"""Collecte Eurostat (mission M02) — exécuté par GitHub Actions, workflow « Collecte ».

Script reprenable : l'avancement est conservé dans `catalogues/eurostat_etat_collecte.json`
(commité par le robot avec les résultats). Chaque passage enchaîne les étapes restantes :

  0. echantillons : réponses brutes réelles (TOC, structure SDMX, JSON-stat, erreurs, metabase,
     TSV compressé) écrites dans docs/sources/echantillons_eurostat/ pour servir de fixtures ;
  a. amorce      : statut des 66 séries Eurostat des prototypes
                   → docs/sources/eurostat_amorce_prototypes.csv ;
  b. niveau1     : TOC complet → catalogues/eurostat_jeux_catalogue.csv (+ eurostat_dossiers_toc.csv) ;
  c. niveau2     : pour chaque jeu candidat, structure SDMX puis séries FR vérifiées par l'API
                   → catalogues/eurostat_series_catalogue.csv (écriture incrémentale).

Une étape dont la version (ETAPES ci-dessous) dépasse celle de l'état est refaite.
Le passage s'arrête proprement avant la limite de durée du robot (DUREE_MAX_MINUTES),
le passage suivant reprend où il s'est arrêté (relancer :
`python scripts/actions.py lancer --branche m02-eurostat --cible collecte_eurostat.py`).

Variables d'environnement facultatives :
  EUROSTAT_DUREE_MAX_MINUTES   (défaut 270)
  EUROSTAT_NIVEAU2_MAX_JEUX    nombre maximal de jeux traités au niveau 2 par passage (0 = sans limite)
  EUROSTAT_ETAPES              liste d'étapes à exécuter, ex. "niveau1,niveau2" (défaut : toutes)
"""

from __future__ import annotations

import csv
import io
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

import pandas as pd  # noqa: E402

from src.pipeline import catalogue_eurostat as cat  # noqa: E402
from src.sources import eurostat as es  # noqa: E402

# ------------------------------------------------------------------ paramètres

#: Versions des étapes : augmenter une version fait refaire l'étape au passage suivant.
#: v2 (13/10) : tableaux ODD inclus, racine principale par titre, icd10 en contenu, ind_type en ventilation,
#: colonnes allégées, remplacements vérifiés dans l'amorce.
ETAPES = {"echantillons": 1, "amorce": 2, "niveau1": 2, "niveau2": 2}

DUREE_MAX = float(os.environ.get("EUROSTAT_DUREE_MAX_MINUTES", "270")) * 60
NIVEAU2_MAX_JEUX = int(os.environ.get("EUROSTAT_NIVEAU2_MAX_JEUX", "0") or 0)
TAILLE_MAX_CSV = 90_000_000  # au-delà, le catalogue des séries est compressé (limite GitHub : 100 Mo par fichier)
ETAPES_DEMANDEES = [e.strip() for e in os.environ.get("EUROSTAT_ETAPES", "").split(",") if e.strip()] or list(ETAPES)

CATALOGUES = RACINE / "catalogues"
DOCS_SOURCES = RACINE / "docs" / "sources"
ECHANTILLONS = DOCS_SOURCES / "echantillons_eurostat"
FICHIER_ETAT = CATALOGUES / "eurostat_etat_collecte.json"
FICHIER_BILAN = CATALOGUES / "eurostat_bilan.json"
FICHIER_JEUX = CATALOGUES / "eurostat_jeux_catalogue.csv"
FICHIER_DOSSIERS = CATALOGUES / "eurostat_dossiers_toc.csv"
FICHIER_SERIES = CATALOGUES / "eurostat_series_catalogue.csv"
FICHIER_SERIES_GZ = CATALOGUES / "eurostat_series_catalogue.csv.gz"
FICHIER_AMORCE = DOCS_SOURCES / "eurostat_amorce_prototypes.csv"
FICHIER_PROTOTYPES = RACINE / "docs" / "archives" / "prototypes_indicateurs.csv"

#: Jeux traités en premier au niveau 2 (échantillon varié pour contrôler la logique).
JEUX_ESSAI = [
    "sdg_01_10", "sdg_08_10", "sdg_05_20", "ilc_li02", "ilc_di12", "ilc_mdsd11", "ilc_pw01", "ilc_peps01n",
    "ilc_lvho05a", "lfsa_ergaed", "une_rt_a", "earn_nt_net", "hlth_silc_01", "hlth_cd_asdr2", "demo_mlexpec",
    "edat_lfse_03", "trng_lfse_01", "crim_off_cat", "env_air_gge", "nrg_bal_c", "nama_10_pc", "nasa_10_nf_tr",
    "isoc_ci_ifp_iu", "tran_sf_roadus", "env_wasmun", "hsw_mi08", "cult_pcs_caind", "educ_uoe_enra01",
]

#: Modalités par défaut des séries des prototypes (relevées en phase 1 ou imposées par l'indicateur).
DEFAUTS_AMORCE = {
    "sdg_08_10": {"unit": "CLV20_EUR_HAB"},
    "sdg_08_11": {"indic": "INV_TOT"},
    "sdg_08_30": {"age": "Y20-64", "indic_em": "EMP_LFS"},
    "sdg_08_20": {"age": "Y15-29"},
    "sdg_01_41": {"wstatus": "EMP", "age": "Y_GE18"},
    "sdg_08_60": {"nace_r2": "TOTAL", "severity": "FAT"},
    "sdg_01_20": {"rskpovth": "B_60"},
    "sdg_03_12": {"hlth_hle": "HE_Y0"},
    "sdg_03_60": {"reason": "TXP_TFAR_WLIST", "age": "Y_GE16"},
    "sdg_03_20": {"levels": "VG_G", "age": "Y_GE16"},
    "sdg_03_30": {"age": "Y_GE15"},
    "sdg_04_10": {"age": "Y18-24", "wstatus": "POP"},
    "sdg_04_20": {"isced11": "ED5-8", "age": "Y25-34"},
    "sdg_04_40": {"field": "READ"},
    "sdg_04_60": {"age": "Y25-64"},
    "sdg_04_70": {"indic_is": "I_DSK2_BAB", "ind_type": "IND_TOTAL"},
    "sdg_05_20": {"nace_r2": "B-S_X_O"},
    "sdg_05_30": {"wstatus": "EMP", "age": "Y20-64"},
}

#: Remplacements des séries de prototypes disparues ou sans donnée France (repérés dans le TOC
#: au premier passage du 13/10/2026) : code → (nouveau code, statut, note). Le robot vérifie le
#: nouveau code pour la France et ajoute sa couverture au commentaire.
REMPLACEMENTS_AMORCE = {
    "sdg_05_60": ("sdg_05_61", "code changé", "sdg_05_60 n'est plus diffusé ; successeur : sdg_05_61 « Positions held by women in senior management »"),
    "sdg_15_10": ("sdg_15_11", "code changé", "sdg_15_10 n'est plus diffusé ; successeur : sdg_15_11 « Forest area » (depuis 2015) ; série longue possible : for_area (FAO, 1990–2025)"),
    "sdg_13_11": ("sdg_13_10", "à remplacer", "sdg_13_11 = émissions nettes de l'UE (agrégat UE seulement) ; pour la France : sdg_13_10 « Domestic net greenhouse gas emissions »"),
    "sdg_15_60": ("env_bio3", "à remplacer", "sdg_15_60 = indice UE agrégé (code typé « table », absent des jeux) ; indices nationaux : env_bio3 « Common bird indices by type of estimate »"),
    "sdg_10_20": ("", "sans donnée FR", "aucune valeur France (dispersion des régions NUTS 2 non publiée pour FR) ; à recalculer à partir de nama_10r_2hhinc si l'indicateur est conservé"),
}

DEBUT = time.monotonic()
CLIENT = es.ClientEurostat(pause=0.2)
_CACHE_TOC: dict[str, str] = {}


def journal(message: str) -> None:
    horodatage = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{horodatage}] {message}", flush=True)


CLIENT.journal = journal


def maintenant() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def aujourdhui() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def temps_restant() -> float:
    return DUREE_MAX - (time.monotonic() - DEBUT)


# ------------------------------------------------------------------ état

def lire_etat() -> dict:
    if FICHIER_ETAT.exists():
        return json.loads(FICHIER_ETAT.read_text(encoding="utf-8"))
    return {"etapes": {}, "passages": []}


def ecrire_etat(etat: dict) -> None:
    CATALOGUES.mkdir(parents=True, exist_ok=True)
    tmp = FICHIER_ETAT.with_suffix(".tmp")
    tmp.write_text(json.dumps(etat, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    tmp.replace(FICHIER_ETAT)


def etape_a_faire(etat: dict, nom: str) -> bool:
    info = etat["etapes"].get(nom, {})
    return info.get("version", 0) < ETAPES[nom] or not info.get("termine", False)


def toc(lang: str) -> str:
    if lang not in _CACHE_TOC:
        journal(f"Téléchargement du TOC ({lang})…")
        _CACHE_TOC[lang] = es.telecharger_toc(lang, CLIENT)
        journal(f"TOC {lang} : {len(_CACHE_TOC[lang]):,} caractères, {_CACHE_TOC[lang].count(chr(10)):,} lignes")
    return _CACHE_TOC[lang]


# ------------------------------------------------------------------ étape 0 : échantillons

def _enregistrer(nom: str, contenu: bytes, info: dict, maximum: int = 3_000_000) -> None:
    ECHANTILLONS.mkdir(parents=True, exist_ok=True)
    if len(contenu) > maximum:
        info["tronque_a_octets"] = maximum
        contenu = contenu[:maximum]
    (ECHANTILLONS / nom).write_bytes(contenu)


def _extraire_toc(texte: str, codes: set[str], premieres: int = 12) -> str:
    """Lignes du TOC : en-tête, `premieres` lignes, puis les lignes des codes demandés et de leurs ancêtres."""
    lignes = texte.splitlines()
    garder = set(range(min(premieres + 1, len(lignes))))
    pile: list[tuple[int, int]] = []  # (profondeur, rang de ligne)
    for i, ligne in enumerate(lignes[1:], start=1):
        champs = ligne.split("\t")
        titre = champs[0].strip('"')
        profondeur = (len(titre) - len(titre.lstrip(" "))) // 4
        while pile and pile[-1][0] >= profondeur:
            pile.pop()
        code = champs[1].strip('"') if len(champs) > 1 else ""
        if code in codes:
            garder.update(r for _, r in pile)
            garder.add(i)
        pile.append((profondeur, i))
    return "\n".join(lignes[i] for i in sorted(garder)) + "\n"


def etape_echantillons(etat: dict) -> None:
    journal("=== Étape 0 : échantillons de réponses réelles ===")
    infos = {}

    def requete(nom: str, url: str, params=None, gz: bool = False) -> bytes:
        t0 = time.monotonic()
        rep = CLIENT.get(url, params or [])
        contenu = rep.content
        info = {
            "url": rep.url, "statut_http": rep.status_code, "content_type": rep.headers.get("Content-Type", ""),
            "content_encoding": rep.headers.get("Content-Encoding", ""), "octets": len(contenu),
            "duree_s": round(time.monotonic() - t0, 2), "gzip": contenu[:2] == b"\x1f\x8b", "date": maintenant(),
        }
        if gz and info["gzip"]:
            contenu = es.decompresser_si_gzip(contenu)
            info["octets_decompresses"] = len(contenu)
        infos[nom] = info
        journal(f"  {nom} : HTTP {rep.status_code}, {len(contenu):,} octets, {info['duree_s']} s")
        return contenu

    codes = {"sdg_01_10", "sdg_08_10", "ilc_li02", "ilc_pw01", "une_rt_a", "lfsq_egais", "tps00001", "hlth_silc_10", "ilc_lvho05a", "nama_10_pc"}
    for lang in ("en", "fr"):
        texte = toc(lang)
        extrait = _extraire_toc(texte, codes)
        infos[f"toc_{lang}_extrait.txt"] = {"url": f"{es.URL_TOC}?lang={lang}", "lignes_toc_complet": texte.count("\n"), "octets_toc_complet": len(texte.encode()), "date": maintenant()}
        _enregistrer(f"toc_{lang}_extrait.txt", extrait.encode("utf-8"), infos[f"toc_{lang}_extrait.txt"])

    essais = [
        ("dataflow_SDG_01_10_referencepartial.xml", es.URL_DATAFLOW.format(code="SDG_01_10"), [("references", "descendants"), ("detail", "referencepartial")], False),
        ("dataflow_ILC_LI02_referencepartial.xml", es.URL_DATAFLOW.format(code="ILC_LI02"), [("references", "descendants"), ("detail", "referencepartial")], False),
        ("datastructure_SDG_01_10.xml", es.URL_DATASTRUCTURE.format(code="SDG_01_10"), [], False),
        ("sdg_01_10_FR_fr.json", es.URL_STATISTIQUES.format(code="sdg_01_10"), [("geo", "FR"), ("lang", "fr")], False),
        ("sdg_08_10_FR_2022_fr.json", es.URL_STATISTIQUES.format(code="sdg_08_10"), [("geo", "FR"), ("lang", "fr"), ("time", "2022")], False),
        ("ilc_li02_FR_T_PC_depuis2015_fr.json", es.URL_STATISTIQUES.format(code="ilc_li02"), [("geo", "FR"), ("sex", "T"), ("unit", "PC"), ("sinceTimePeriod", "2015"), ("lang", "fr")], False),
        ("sdg_01_10_FR_lastTimePeriod3_fr.json", es.URL_STATISTIQUES.format(code="sdg_01_10"), [("geo", "FR"), ("lastTimePeriod", "3"), ("lang", "fr")], False),
        ("sdg_10_20_FR_fr.json", es.URL_STATISTIQUES.format(code="sdg_10_20"), [("geo", "FR"), ("lang", "fr")], False),
        ("erreur_modalite_inexistante.json", es.URL_STATISTIQUES.format(code="sdg_08_10"), [("geo", "FR"), ("unit", "XXX"), ("lang", "fr")], False),
        ("erreur_jeu_inexistant.json", es.URL_STATISTIQUES.format(code="zzz_inexistant"), [("geo", "FR"), ("lang", "fr")], False),
        ("erreur_structure_inexistante.xml", es.URL_DATAFLOW.format(code="ZZZ_INEXISTANT"), [("references", "descendants"), ("detail", "referencepartial")], False),
        ("sdmx_SDG_08_10_FR_tsv_compresse.tsv", es.RACINE_API + "/sdmx/2.1/data/SDG_08_10/A..B1GQ.FR", [("format", "TSV"), ("compressed", "true"), ("startPeriod", "2018")], True),
    ]
    for nom, url, params, gz in essais:
        try:
            _enregistrer(nom, requete(nom, url, params, gz), infos[nom])
        except Exception as exc:  # un échantillon manquant ne doit pas bloquer la collecte
            infos[nom] = {"url": url, "erreur": repr(exc)}
            journal(f"  {nom} : ÉCHEC {exc!r}")
    # metabase : liste compressée des jeux, dimensions et modalités (on ne garde qu'un extrait)
    try:
        contenu = requete("metabase_extrait.txt", es.RACINE_API + "/catalogue/metabase.txt.gz", [], True)
        texte = contenu.decode("utf-8", errors="replace")
        lignes = texte.splitlines()
        infos["metabase_extrait.txt"].update({"lignes": len(lignes), "jeux_distincts": len({l.split("\t")[0] for l in lignes if l})})
        _enregistrer("metabase_extrait.txt", ("\n".join(lignes[:80]) + "\n").encode("utf-8"), infos["metabase_extrait.txt"])
    except Exception as exc:
        infos["metabase_extrait.txt"] = {"erreur": repr(exc)}
        journal(f"  metabase : ÉCHEC {exc!r}")
    (ECHANTILLONS / "echantillons_info.json").write_text(json.dumps(infos, ensure_ascii=False, indent=1), encoding="utf-8")
    etat["etapes"]["echantillons"] = {"version": ETAPES["echantillons"], "termine": True, "date": maintenant(), "nb_fichiers": len(infos)}
    ecrire_etat(etat)


# ------------------------------------------------------------------ étape a : amorce

def _commentaires_manuels() -> dict[str, str]:
    """Partie manuelle des commentaires de l'amorce existante (phase 1 ou relecture humaine)."""
    if not FICHIER_AMORCE.exists():
        return {}
    manuels = {}
    for ligne in csv.DictReader(FICHIER_AMORCE.open(encoding="utf-8")):
        commentaire = ligne.get("commentaire", "") or ""
        if "non vérifié" in (ligne.get("statut") or ""):
            continue  # commentaire de phase 1 devenu caduc (requête refusée par WebFetch)
        if commentaire.startswith("robot : "):
            continue
        manuels[ligne["id_prototype"]] = commentaire.split(cat.SEPARATEUR_ROBOT)[0].strip()
    return manuels


def _verifier_remplacement(code: str) -> str:
    """Couverture France de la série par défaut d'un code de remplacement (texte pour le commentaire)."""
    try:
        jeu = es.obtenir_jeu(code, {"geo": "FR"}, "fr", CLIENT)
    except es.ErreurEurostat as exc:
        return f"{code} non vérifiable ({type(exc).__name__})"
    lignes, _ = cat.construire_series(jeu, annee_min=0)
    defaut = [l for l in lignes if l["type_ligne"] == "defaut"]
    if not defaut:
        return f"{code} : aucune valeur pour la France"
    d = max(defaut, key=lambda l: l["nb_annees"])
    filtres = d["serie_id"].split("?", 1)[1]
    return (f"{code} vérifié pour la France : {d['premiere_periode']}–{d['derniere_periode']} ({d['nb_annees']} années, "
            f"{len(defaut)} série(s) par défaut ; la plus longue : {filtres}, unité {d['unite_code'] or '-'})")


def etape_amorce(etat: dict) -> None:
    journal("=== Étape a : amorce (séries Eurostat des prototypes) ===")
    protos = [l for l in csv.DictReader(FICHIER_PROTOTYPES.open(encoding="utf-8")) if l["origine"] == "Eurostat"]
    manuels = _commentaires_manuels()
    codes_toc = set(es.analyser_toc(toc("en"))["code"])
    lignes = []
    for proto in protos:
        proto = dict(proto, commentaire_manuel=manuels.get(proto["id_prototype"], ""))
        code = proto["code_source"]
        jeu, erreur = None, ""
        try:
            jeu = es.obtenir_jeu(code, {"geo": "FR"}, "fr", CLIENT)
            if not jeu.observations:
                jeu, erreur = None, "réponse sans aucune valeur pour la France"
        except es.ErreurEurostat as exc:
            erreur = f"{type(exc).__name__} : {exc}"
        ligne = cat.ligne_amorce(proto, jeu, erreur, DEFAUTS_AMORCE.get(code), aujourdhui(), code in codes_toc)
        if code in REMPLACEMENTS_AMORCE and ligne["statut"] not in ("disponible",):
            nouveau, statut, note = REMPLACEMENTS_AMORCE[code]
            ligne["statut"], ligne["nouveau_code"] = statut, nouveau
            if nouveau:
                note += " ; " + _verifier_remplacement(nouveau)
            ligne["commentaire"] += " ; " + note
        lignes.append(ligne)
        journal(f"  {proto['id_prototype']:<20} {code:<12} {ligne['statut']:<26} {ligne['premiere_periode_fr']}–{ligne['derniere_periode_fr']} ({ligne['nb_periodes_fr']})")
    pd.DataFrame(lignes, columns=cat.COLONNES_AMORCE).to_csv(FICHIER_AMORCE, index=False, lineterminator="\n")
    bilan = pd.Series([l["statut"] for l in lignes]).value_counts().to_dict()
    journal(f"  Bilan amorce : {bilan}")
    etat["etapes"]["amorce"] = {"version": ETAPES["amorce"], "termine": True, "date": maintenant(), "bilan": bilan, "nb": len(lignes)}
    ecrire_etat(etat)


# ------------------------------------------------------------------ étape b : niveau 1

def etape_niveau1(etat: dict) -> None:
    journal("=== Étape b : niveau 1 (jeux du TOC) ===")
    toc_en = es.analyser_toc(toc("en"))
    toc_fr = es.analyser_toc(toc("fr"))
    catalogue = cat.construire_catalogue_jeux(toc_en, toc_fr)
    ancien = pd.read_csv(FICHIER_JEUX, dtype=str, keep_default_na=False) if FICHIER_JEUX.exists() else None
    if ancien is not None:  # conserver les colonnes remplies par le niveau 2
        report = ancien.set_index("code_jeu")[["statut_niveau2", "nb_series_fr", "nb_series_candidates", "structure_fr"]]
        for col in report.columns:
            catalogue[col] = catalogue["code_jeu"].map(report[col]).fillna("")
    CATALOGUES.mkdir(parents=True, exist_ok=True)
    catalogue.to_csv(FICHIER_JEUX, index=False, lineterminator="\n")
    dossiers = cat.bilan_dossiers(toc_en, catalogue, toc_fr)
    dossiers.to_csv(FICHIER_DOSSIERS, index=False, lineterminator="\n")
    types = toc_en.drop_duplicates("code")["type"].value_counts().to_dict()
    bilan = {
        "entrees_toc": int(len(toc_en)),
        "codes_distincts_par_type": {k: int(v) for k, v in types.items()},
        "jeux": int(len(catalogue)),
        "jeux_par_filtre": {k: int(v) for k, v in catalogue["filtre_toc"].str.split(" :").str[0].value_counts().items()},
        "jeux_retenus_par_filtres": int((catalogue["filtre_toc"] == "retenu").sum()),
        "jeux_infra_annuels": int(catalogue["motif_candidat"].str.startswith("infra-annuel").sum()),
        "candidats": int((catalogue["candidat"] == "oui").sum()),
        "candidats_par_rattrapage": int(catalogue["motif_candidat"].str.startswith("rattrapage").sum()),
        "candidats_par_dimension": {k: int(v) for k, v in catalogue[catalogue["candidat"] == "oui"]["dimension_v0"].value_counts().items()},
        "candidats_par_dossier": {k or "(mots-clés)": int(v) for k, v in catalogue[catalogue["candidat"] == "oui"]["dossier_prioritaire"].value_counts().items()},
        "jeux_prioritaires_non_candidats_par_motif": {k: int(v) for k, v in catalogue[(catalogue["dossier_prioritaire"] != "") & (catalogue["candidat"] != "oui")]["motif_candidat"].str.split(" :").str[0].value_counts().items()},
    }
    journal("  " + json.dumps(bilan, ensure_ascii=False))
    etat["etapes"]["niveau1"] = {"version": ETAPES["niveau1"], "termine": True, "date": maintenant(), "bilan": bilan}
    ecrire_etat(etat)


# ------------------------------------------------------------------ étape c : niveau 2

def _preparer_fichier_series() -> None:
    """Si le catalogue des séries a été compressé au passage précédent, le décompresser pour continuer."""
    if FICHIER_SERIES_GZ.exists() and not FICHIER_SERIES.exists():
        import gzip
        FICHIER_SERIES.write_bytes(gzip.decompress(FICHIER_SERIES_GZ.read_bytes()))
    if FICHIER_SERIES_GZ.exists():
        FICHIER_SERIES_GZ.unlink()


def _finaliser_fichier_series() -> None:
    """Compresse le catalogue des séries s'il dépasse TAILLE_MAX_CSV (sinon le push du robot échouerait)."""
    if FICHIER_SERIES.exists() and FICHIER_SERIES.stat().st_size > TAILLE_MAX_CSV:
        import gzip
        FICHIER_SERIES_GZ.write_bytes(gzip.compress(FICHIER_SERIES.read_bytes(), compresslevel=9))
        FICHIER_SERIES.unlink()
        journal(f"  Catalogue des séries compressé : {FICHIER_SERIES_GZ.name} ({FICHIER_SERIES_GZ.stat().st_size / 1e6:.1f} Mo)")


def _ecrire_series(lignes: list[dict]) -> None:
    nouveau = not FICHIER_SERIES.exists()
    with FICHIER_SERIES.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cat.COLONNES_SERIES, lineterminator="\n", extrasaction="ignore")
        if nouveau:
            w.writeheader()
        w.writerows(lignes)


def _nettoyer_series(gardes: set[str]) -> None:
    """Retire du catalogue des séries les jeux non (ou plus) marqués comme traités."""
    if not FICHIER_SERIES.exists():
        return
    df = pd.read_csv(FICHIER_SERIES, dtype=str, keep_default_na=False)
    avant = len(df)
    df = df[df["code_jeu"].isin(gardes)]
    if len(df) != avant:
        df.to_csv(FICHIER_SERIES, index=False, lineterminator="\n")
        journal(f"  {avant - len(df)} lignes retirées (jeux à refaire ou non candidats)")


def _interroger(code: str, filtres: dict) -> "es.JeuJsonStat | None":
    """Une requête JSON-stat avec attente sur réponse asynchrone ; None si aucune donnée."""
    for essai in range(4):
        try:
            return es.obtenir_jeu(code, dict(filtres, sinceTimePeriod=cat.ANNEE_MIN), "fr", CLIENT)
        except es.AucuneDonnee:
            return None
        except es.ReponseAsynchrone:
            if essai == 3:
                raise
            journal(f"    réponse asynchrone pour {code}, nouvel essai dans 60 s")
            time.sleep(60)
    return None


STATUTS_FINALS = {"ok", "sans_donnee_fr", "sans_dimension_geo", "structure_introuvable"}


def traiter_jeu(ligne_jeu: dict) -> tuple[dict, list[dict]]:
    """Structure + séries FR d'un jeu candidat. Renvoie (état du jeu, lignes du catalogue)."""
    code = ligne_jeu["code_jeu"]
    n0, t0 = CLIENT.nb_requetes, time.monotonic()
    info = {"date": maintenant()}

    def fin(statut: str, message: str = "", lignes=None, **autres):
        info.update(statut=statut, message=message, requetes=CLIENT.nb_requetes - n0, duree_s=round(time.monotonic() - t0, 1), **autres)
        return info, lignes or []

    try:
        structure = es.decrire_jeu(code, CLIENT)
    except es.AucuneDonnee as exc:
        return fin("structure_introuvable", str(exc))
    except es.ErreurEurostat as exc:
        return fin("erreur_structure", str(exc))
    geo_dim = structure.dimension("geo")
    if geo_dim is None:
        return fin("sans_dimension_geo", "pas de dimension geo")
    if "FR" in geo_dim.modalites or not structure.partielle:
        geo = "FR"
    elif "FX" in geo_dim.modalites:
        geo = "FX"
    else:
        return fin("sans_donnee_fr", f"ni FR ni FX parmi {len(geo_dim.modalites)} zones")
    freq_dim = structure.dimension("freq")
    frequence = None
    if freq_dim is not None and len(freq_dim.modalites) > 0:
        frequence = "A" if "A" in freq_dim.modalites else None
    a_fin = cat.annee(ligne_jeu.get("derniere_periode")) or 2026
    a_debut = max(cat.annee(ligne_jeu.get("premiere_periode")) or cat.ANNEE_MIN, cat.ANNEE_MIN)
    nb_periodes = max(a_fin - a_debut + 1, 1) * (1 if frequence == "A" else cat.PERIODES_PAR_AN.get(ligne_jeu.get("frequence", ""), 1))
    plan, note = cat.planifier_requetes(structure, geo, frequence, nb_periodes)
    reponses = []
    try:
        for filtres in plan:
            if temps_restant() < 60:
                return fin("interrompu", "durée maximale du passage atteinte")
            try:
                reponses.append(_interroger(code, filtres))
            except es.ExtractionTropVolumineuse:
                plan2, note2 = cat.planifier_requetes(structure, geo, frequence, nb_periodes, seuil=50_000, max_requetes=120)
                note += f" ; extraction trop volumineuse, nouveau plan : {note2}"
                reponses = [_interroger(code, f) for f in plan2]
                break
    except es.ReponseAsynchrone as exc:
        return fin("asynchrone", str(exc))
    except es.ErreurEurostat as exc:
        return fin("erreur_donnees", str(exc))
    jeu = cat.fusionner_jeux([r for r in reponses if r is not None])
    if jeu is None or not jeu.observations:
        return fin("sans_donnee_fr", f"aucune observation pour {geo} depuis {cat.ANNEE_MIN}", geo=geo)
    contexte = cat.ContexteJeu(ligne_jeu.get("theme_source", ""), ligne_jeu.get("dimension_v0", ""), aujourdhui())
    lignes, roles = cat.construire_series(jeu, contexte)
    nb_def = sum(1 for l in lignes if l["type_ligne"] == "defaut")
    nb_ok = sum(1 for l in lignes if l["candidat"] == "oui")
    nb_v = sum(1 for l in lignes if l["type_ligne"] == "ventilation")
    if geo == "FX":
        for l in lignes:
            l["commentaire"] = ("France métropolitaine seulement (FX) ; " + l["commentaire"]).strip(" ;")
    return fin("ok", note, lignes, geo=geo, nb_series=nb_def, nb_candidates=nb_ok, nb_ventilations=nb_v,
               nb_observations=len(jeu.observations), structure_fr=roles.description(jeu), jeu_source=jeu.jeu_source)


def _ordre_traitement(candidats: pd.DataFrame) -> list[dict]:
    lignes = candidats.to_dict("records")
    rang_essai = {c: i for i, c in enumerate(JEUX_ESSAI)}
    return sorted(lignes, key=lambda l: (rang_essai.get(l["code_jeu"], len(rang_essai)), 0 if l["code_jeu"].startswith("sdg_") else 1))


def mettre_a_jour_catalogue_jeux(etat: dict) -> None:
    if not FICHIER_JEUX.exists():
        return
    jeux = pd.read_csv(FICHIER_JEUX, dtype=str, keep_default_na=False)
    suivi = etat["etapes"].get("niveau2", {}).get("jeux", {})
    jeux["statut_niveau2"] = jeux["code_jeu"].map(lambda c: suivi.get(c, {}).get("statut", "")).fillna("")
    jeux["nb_series_fr"] = jeux["code_jeu"].map(lambda c: str(suivi.get(c, {}).get("nb_series", "")) if c in suivi else "")
    jeux["nb_series_candidates"] = jeux["code_jeu"].map(lambda c: str(suivi.get(c, {}).get("nb_candidates", "")) if c in suivi else "")
    jeux["structure_fr"] = jeux["code_jeu"].map(lambda c: suivi.get(c, {}).get("structure_fr", "") or suivi.get(c, {}).get("message", "") if c in suivi else "")
    jeux.to_csv(FICHIER_JEUX, index=False, lineterminator="\n")


def etape_niveau2(etat: dict) -> None:
    journal("=== Étape c : niveau 2 (séries FR des jeux candidats) ===")
    info = etat["etapes"].get("niveau2", {})
    if info.get("version", 0) < ETAPES["niveau2"]:
        journal("  Nouvelle version de l'étape : reprise de zéro")
        info = {"version": ETAPES["niveau2"], "termine": False, "debut": maintenant(), "jeux": {}}
        for f in (FICHIER_SERIES, FICHIER_SERIES_GZ):
            if f.exists():
                f.unlink()
    etat["etapes"]["niveau2"] = info
    _preparer_fichier_series()
    jeux = pd.read_csv(FICHIER_JEUX, dtype=str, keep_default_na=False)
    candidats = jeux[jeux["candidat"] == "oui"]
    codes_candidats = set(candidats["code_jeu"])
    suivi: dict = info["jeux"]
    for code in [c for c in suivi if c not in codes_candidats]:
        del suivi[code]
    _nettoyer_series({c for c, s in suivi.items() if s.get("statut") == "ok"})
    a_faire = [l for l in _ordre_traitement(candidats)
               if suivi.get(l["code_jeu"], {}).get("statut") not in STATUTS_FINALS and suivi.get(l["code_jeu"], {}).get("essais", 0) < 3]
    journal(f"  {len(candidats)} jeux candidats ; {len(codes_candidats) - len(a_faire)} déjà traités ; {len(a_faire)} à traiter"
            + (f" (au plus {NIVEAU2_MAX_JEUX} dans ce passage)" if NIVEAU2_MAX_JEUX else ""))
    traites = 0
    for i, ligne_jeu in enumerate(a_faire, start=1):
        if NIVEAU2_MAX_JEUX and traites >= NIVEAU2_MAX_JEUX:
            journal(f"  Limite de {NIVEAU2_MAX_JEUX} jeux par passage atteinte")
            break
        if temps_restant() < 120:
            journal("  Durée maximale du passage bientôt atteinte : arrêt propre, reprise au prochain passage")
            break
        code = ligne_jeu["code_jeu"]
        precedent = suivi.get(code, {})
        try:
            etat_jeu, lignes = traiter_jeu(ligne_jeu)
        except Exception as exc:  # erreur inattendue : on journalise et on continue
            etat_jeu, lignes = {"statut": "erreur_inattendue", "message": repr(exc)[:500], "date": maintenant()}, []
        if etat_jeu["statut"] == "interrompu":
            journal(f"  {code} interrompu (durée) : repris au prochain passage")
            break
        etat_jeu["essais"] = precedent.get("essais", 0) + (0 if etat_jeu["statut"] in STATUTS_FINALS else 1)
        if lignes:
            _ecrire_series(lignes)
        suivi[code] = etat_jeu
        traites += 1
        journal(f"  [{i}/{len(a_faire)}] {code:<22} {etat_jeu['statut']:<18} séries {etat_jeu.get('nb_series', 0):>5} "
                f"(éligibles {etat_jeu.get('nb_candidates', 0)}, ventilations {etat_jeu.get('nb_ventilations', 0)}) "
                f"{etat_jeu.get('requetes', 0)} req. {etat_jeu.get('duree_s', 0)} s {etat_jeu.get('message', '')[:120]}")
        if traites % 10 == 0:
            ecrire_etat(etat)
    restants = [c for c in codes_candidats
                if suivi.get(c, {}).get("statut") not in STATUTS_FINALS and suivi.get(c, {}).get("essais", 0) < 3]
    info["termine"] = not restants
    info["restants"] = len(restants)
    if info["termine"]:
        info["fin"] = maintenant()
    ecrire_etat(etat)
    mettre_a_jour_catalogue_jeux(etat)
    _finaliser_fichier_series()
    journal(f"  Passage terminé : {traites} jeux traités, {len(restants)} restants")


# ------------------------------------------------------------------ bilan

def ecrire_bilan(etat: dict) -> None:
    bilan = {"date": maintenant(), "etapes": {k: {kk: vv for kk, vv in v.items() if kk != "jeux"} for k, v in etat["etapes"].items()}}
    suivi = etat["etapes"].get("niveau2", {}).get("jeux", {})
    if suivi:
        bilan["niveau2_statuts"] = pd.Series([s.get("statut") for s in suivi.values()]).value_counts().to_dict()
    fichier = FICHIER_SERIES if FICHIER_SERIES.exists() else FICHIER_SERIES_GZ
    if fichier.exists():
        series = pd.read_csv(fichier, dtype=str, keep_default_na=False)
        taille = fichier.stat().st_size
        defaut = series[series["type_ligne"] == "defaut"]
        bilan["series"] = {
            "fichier": fichier.name,
            "octets": int(taille),
            "lignes": int(len(series)),
            "series_defaut": int(len(defaut)),
            "series_eligibles": int((defaut["candidat"] == "oui").sum()),
            "lignes_ventilation": int((series["type_ligne"] == "ventilation").sum()),
            "jeux_avec_series": int(series["code_jeu"].nunique()),
            "series_defaut_par_dimension": defaut["dimension_v0"].value_counts().to_dict(),
            "series_eligibles_par_dimension": defaut[defaut["candidat"] == "oui"]["dimension_v0"].value_counts().to_dict(),
            "jeux_avec_serie_eligible_par_dimension": defaut[defaut["candidat"] == "oui"].groupby("dimension_v0")["code_jeu"].nunique().to_dict(),
        }
    FICHIER_BILAN.write_text(json.dumps(bilan, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    journal("Bilan : " + json.dumps(bilan.get("series", {}), ensure_ascii=False, default=str))


def main() -> int:
    journal(f"Collecte Eurostat — étapes demandées : {', '.join(ETAPES_DEMANDEES)} ; durée max {DUREE_MAX / 60:.0f} min ; "
            f"niveau 2 : {NIVEAU2_MAX_JEUX or 'sans limite'} jeux par passage")
    etat = lire_etat()
    passage = {"debut": maintenant(), "etapes": []}
    etat.setdefault("passages", []).append(passage)
    code_retour = 0
    for nom, fonction in (("echantillons", etape_echantillons), ("amorce", etape_amorce), ("niveau1", etape_niveau1), ("niveau2", etape_niveau2)):
        if nom not in ETAPES_DEMANDEES or not etape_a_faire(etat, nom):
            continue
        if temps_restant() < 300:
            journal(f"Plus assez de temps pour l'étape {nom}")
            break
        try:
            fonction(etat)
            passage["etapes"].append(nom)
        except Exception as exc:
            journal(f"ÉCHEC de l'étape {nom} : {exc!r}")
            import traceback
            traceback.print_exc()
            passage["etapes"].append(f"{nom} (échec)")
            code_retour = 1
            if nom in ("niveau1",):
                break
    passage.update(fin=maintenant(), requetes=CLIENT.nb_requetes, nouveaux_essais=CLIENT.nb_nouveaux_essais, octets=CLIENT.octets)
    etat["passages"] = etat["passages"][-30:]
    ecrire_etat(etat)
    ecrire_bilan(etat)
    journal(f"Fin : {CLIENT.nb_requetes} requêtes ({CLIENT.nb_nouveaux_essais} nouveaux essais), {CLIENT.octets / 1e6:.1f} Mo, "
            f"{(time.monotonic() - DEBUT) / 60:.1f} min")
    return code_retour


if __name__ == "__main__":
    sys.exit(main())
