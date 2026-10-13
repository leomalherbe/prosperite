#!/usr/bin/env python3
"""Collecte INSEE (BDM + Melodi) → inventaires bruts → catalogues de séries candidates.

Exécuté par GitHub Actions (workflow « Collecte », cible `collecte_insee.py`, déclenchée par un push
sur `m01-insee` qui modifie scripts/ ou src/, ou à la demande). Le bac à sable des sessions Claude
n'atteint pas les API : seule l'étape `catalogage` (hors ligne) s'y exécute.

Étapes, dans l'ordre (chacune reprend là où le passage précédent s'est arrêté) :
  bdm_flux       liste des dataflows ; listes de codes CL_ZONE_GEO, CL_UNITE, CL_PERIODICITE
  bdm_series     toutes les séries de chaque dataflow (`detail=nodata`, découpage au-delà de 2 000)
  bdm_periodes   première/dernière période des séries nationales mises à jour depuis 2020
                 (annuelles : séries complètes ; infra-annuelles : first/lastNObservations)
  melodi         catalogue, /range, séries nationales de chaque jeu pertinent (/data ou fichier ZIP)
  echantillons   réponses brutes de référence → docs/sources/echantillons_insee/ (futures fixtures)
  consolidation  inventaires bruts : catalogues/insee_{bdm,melodi}_inventaire.csv.gz
  catalogage     filtres, tagging dimension_v0, candidat → catalogues/insee_*_catalogue.csv, bilans,
                 comparaison avec le repérage de phase 1

Reprise : l'état est gardé dans `catalogues/insee_etat/` (commité par le robot). Si le budget de
temps est atteint (240 min par défaut, le robot coupe à 300 min), le script s'arrête proprement ;
le passage suivant reprend. Un cycle terminé est recommencé de zéro au passage suivant.

Options du robot : lancé sans argument, le script lit `scripts/collecte_insee.options` s'il existe
(ex. « --nouveau --budget-minutes 45 ») ; les arguments de la ligne de commande l'emportent.

Usage :
    python scripts/collecte_insee.py                     # collecte complète ou reprise (robot)
    python scripts/collecte_insee.py --catalogage-seul   # hors ligne, depuis les inventaires
    python scripts/collecte_insee.py --nouveau --max-flux 5 --max-jeux 3   # essai réduit
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import re
import shlex
import sys
import time
import traceback
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from src.sources import insee_bdm as bdm  # noqa: E402
from src.sources import insee_catalogue as cat  # noqa: E402
from src.sources import insee_melodi as mel  # noqa: E402
from src.sources.insee_http import ClientHttp, ErreurReseau, Reponse  # noqa: E402

CATALOGUES = RACINE / "catalogues"
ETAT_DIR = CATALOGUES / "insee_etat"
ECHANTILLONS = RACINE / "docs" / "sources" / "echantillons_insee"
PHASE1 = RACINE / "docs" / "sources" / "insee_indicateurs_reperes.csv"

INVENTAIRE_BDM = CATALOGUES / "insee_bdm_inventaire.csv.gz"
INVENTAIRE_MELODI = CATALOGUES / "insee_melodi_inventaire.csv.gz"
CATALOGUE_BDM = CATALOGUES / "insee_bdm_catalogue.csv"
CATALOGUE_MELODI = CATALOGUES / "insee_melodi_catalogue.csv"
FLUX_CSV = CATALOGUES / "insee_bdm_dataflows.csv"
JEUX_CSV = CATALOGUES / "insee_melodi_jeux.csv"
ZONES_CSV = CATALOGUES / "insee_bdm_zones.csv"
COMPARAISON_CSV = CATALOGUES / "insee_comparaison_phase1.csv"
BILAN_JSON = CATALOGUES / "insee_bilan.json"

ETAPES = ["bdm_flux", "echantillons", "bdm_series", "bdm_periodes", "melodi", "consolidation", "catalogage"]

#: Options par défaut du robot (lues seulement si le script est lancé sans argument, comme le fait le
#: workflow « Collecte ») : permet de piloter un passage par un commit (essai réduit, nouveau cycle…).
FICHIER_OPTIONS = RACINE / "scripts" / "collecte_insee.options"

COLONNES_CATALOGUE = [
    "source", "serie_id", "libelle", "unite", "frequence", "geo", "premiere_periode", "derniere_periode", "derniere_maj",
    "theme_source", "dimension_v0", "candidat", "commentaire", "agregable", "ventilation",
    "geo_libelle", "nb_annees_depuis_2000", "statut_derniere_valeur", "theme_libelle", "url_api",
]

COLONNES_INVENTAIRE_BDM = [
    "idbank", "dataflow", "titre_fr", "freq", "ref_area", "zone", "unit_measure", "unit_mult", "last_update", "serie_arretee",
    "premiere_periode", "derniere_periode", "nb_annees_depuis_2000", "statut_derniere_valeur", "periodes", "dimensions",
]

COLONNES_INVENTAIRE_MELODI = [
    "serie_id", "jeu", "libelle", "freq", "geo", "geo_libelle", "unite", "premiere_periode", "derniere_periode",
    "nb_annees_depuis_2000", "nb_valeurs", "statut_derniere_valeur", "derniere_maj", "dimensions",
]

#: Jeux Melodi écartés d'emblée (motif) : statistiques d'entreprises, équipements, prénoms, comptes par branche.
JEUX_HORS_CHAMP: list[tuple[re.Pattern, str]] = [
    (re.compile(p), m) for p, m in [
        (r"^DS_FLORES", "établissements et effectifs salariés par secteur (statistique d'entreprises)"),
        (r"^DS_SIDE", "démographie des entreprises"),
        (r"^DS_BPE", "base permanente des équipements (dénombrements d'équipements)"),
        (r"^DS_PRENOM$", "fichier des prénoms"),
        (r"^DS_TOUR_CAP$", "capacités d'hébergement touristique (offre)"),
        (r"^DS_(TICE|EACEI|ANTIPOL)$", "enquête auprès des entreprises"),
        (r"^DS_ICA$", "indices de chiffre d'affaires (entreprises)"),
        (r"^DD_CNA_(BRANCHES|SUT|REBS|PATRIMOINE_BRANCHES|ECH_EXT|CONSO_MENAGES_PRODUITS)$", "comptes nationaux par branche ou par produit (hors champ, volumineux)"),
        (r"^DS_COMPTES_REGIONAUX$", "comptes régionaux (le niveau France double les comptes nationaux)"),
    ]
]

PLAFOND_MELODI = 3_000_000   # au-delà, le niveau national d'un jeu n'est pas extrait (journalisé)
PERIODICITES = {"annuel": "A", "trimestriel": "T", "mensuel": "M", "semestriel": "S", "bimestriel": "B", "aperiodique": "A", "quotidien": "J"}


# --------------------------------------------------------------------------------------
# Journal, budget, état
# --------------------------------------------------------------------------------------

DEBUT = time.monotonic()


def log(message: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {message}", flush=True)


def maintenant() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class BudgetAtteint(Exception):
    pass


class Budget:
    def __init__(self, minutes: float) -> None:
        self.limite = minutes * 60

    def restant(self) -> float:
        return self.limite - (time.monotonic() - DEBUT)

    def verifier(self) -> None:
        if self.restant() <= 0:
            raise BudgetAtteint()


class Etat:
    """État persistant d'un cycle de collecte (catalogues/insee_etat/etat.json + fichiers JSONL compressés)."""

    def __init__(self, dossier: Path) -> None:
        self.dossier = dossier
        self.fichier = dossier / "etat.json"
        self.d: dict[str, Any] = {}
        if self.fichier.exists():
            try:
                self.d = json.loads(self.fichier.read_text())
            except json.JSONDecodeError:
                self.d = {}

    def nouveau_cycle(self) -> None:
        historique = self.d.get("passages_precedents", [])[-20:]
        if self.d.get("passages"):
            historique.append({"cycle": self.d.get("debut"), "passages": self.d.get("passages"), "termine": self.d.get("termine", False)})
        if self.dossier.exists():
            for f in self.dossier.iterdir():
                if f.is_file() and f.name != "etat.json":
                    f.unlink()
        self.dossier.mkdir(parents=True, exist_ok=True)
        self.d = {"version": 1, "debut": maintenant(), "termine": False, "etapes_terminees": [], "passages": [], "passages_precedents": historique,
                  "bdm_flux_faits": [], "bdm_flux_erreurs": {}, "bdm_flux_stats": {}, "melodi_jeux": {}, "compteurs": {}}
        self.sauver()

    def chemin(self, nom: str) -> Path:
        return self.dossier / nom

    def sauver(self) -> None:
        self.dossier.mkdir(parents=True, exist_ok=True)
        self.d["maj"] = maintenant()
        tmp = self.fichier.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.d, ensure_ascii=False, indent=1))
        tmp.replace(self.fichier)

    def termine(self, etape: str) -> bool:
        return etape in self.d.get("etapes_terminees", [])

    def marquer(self, etape: str) -> None:
        if etape not in self.d["etapes_terminees"]:
            self.d["etapes_terminees"].append(etape)
        self.sauver()


def ajouter_jsonl(chemin: Path, objets: Iterable[dict]) -> int:
    n = 0
    with gzip.open(chemin, "at", encoding="utf-8") as f:
        for o in objets:
            f.write(json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "\n")
            n += 1
    return n


def lire_jsonl(chemin: Path) -> Iterable[dict]:
    if not chemin.exists():
        return
    with gzip.open(chemin, "rt", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if ligne:
                try:
                    yield json.loads(ligne)
                except json.JSONDecodeError:
                    continue  # ligne tronquée par une interruption


# --------------------------------------------------------------------------------------
# Étape bdm_flux
# --------------------------------------------------------------------------------------

def etape_bdm_flux(etat: Etat, client, echantillons: bool) -> None:
    rep = client.get(bdm.url_dataflows())
    if not rep.ok:
        raise RuntimeError(f"liste des dataflows : HTTP {rep.statut} {rep.extrait()}")
    flux = bdm.analyser_dataflows(rep.contenu)
    if echantillons:
        sauver_echantillon("bdm_dataflows.xml", rep)
    etat.chemin("bdm_flux.json").write_text(json.dumps([f.__dict__ for f in flux], ensure_ascii=False, indent=0))
    codelists: dict[str, dict[str, str]] = {}
    for cl in ("CL_ZONE_GEO", "CL_UNITE", "CL_PERIODICITE"):
        try:
            codelists[cl] = bdm.obtenir_codelist(cl, client)
        except Exception as exc:  # une liste de codes manquante n'empêche pas la collecte
            log(f"  liste de codes {cl} illisible : {exc}")
            codelists[cl] = {}
    etat.chemin("bdm_codelists.json").write_text(json.dumps(codelists, ensure_ascii=False))
    total = sum(f.nb_series or 0 for f in flux)
    log(f"BDM : {len(flux)} dataflows, {total} séries annoncées ; zones {len(codelists['CL_ZONE_GEO'])} codes, unités {len(codelists['CL_UNITE'])} codes")
    etat.d["compteurs"]["bdm_dataflows"] = len(flux)
    etat.d["compteurs"]["bdm_series_annoncees"] = total
    etat.marquer("bdm_flux")


def charger_flux(etat: Etat) -> list[bdm.Dataflow]:
    return [bdm.Dataflow(**d) for d in json.loads(etat.chemin("bdm_flux.json").read_text())]


def charger_codelists(etat: Optional[Etat]) -> dict[str, dict[str, str]]:
    if etat is None:
        return {}
    chemin = etat.chemin("bdm_codelists.json")
    return json.loads(chemin.read_text()) if chemin.exists() else {}


# --------------------------------------------------------------------------------------
# Étape bdm_series
# --------------------------------------------------------------------------------------

def etape_bdm_series(etat: Etat, client, budget: Budget, max_flux: Optional[int]) -> None:
    flux = charger_flux(etat)
    if max_flux:
        flux = flux[:max_flux]
    faits = set(etat.d["bdm_flux_faits"])
    cache_codelists: dict[str, dict[str, str]] = {}
    a_faire = [f for f in flux if f.id not in faits and f.id != "SERIES_BDM"]
    log(f"BDM séries : {len(a_faire)} dataflows à lister ({len(faits)} déjà faits)")
    for i, f in enumerate(a_faire, 1):
        budget.verifier()
        t0 = time.monotonic()
        try:
            res = bdm.lister_series(f.id, client, nb_annonce=f.nb_series, codelists=cache_codelists)
        except ErreurReseau as exc:
            etat.d["bdm_flux_erreurs"][f.id] = [f"réseau : {exc}"]
            log(f"  [{i}/{len(a_faire)}] {f.id} : ÉCHEC réseau {str(exc)[:160]}")
            etat.d["bdm_flux_faits"].append(f.id)
            etat.sauver()
            continue
        except Exception as exc:
            etat.d["bdm_flux_erreurs"][f.id] = [f"{type(exc).__name__} : {exc}"[:500]]
            log(f"  [{i}/{len(a_faire)}] {f.id} : ERREUR {type(exc).__name__} {str(exc)[:200]}")
            etat.d["bdm_flux_faits"].append(f.id)
            etat.sauver()
            continue
        ajouter_jsonl(etat.chemin("bdm_series.jsonl.gz"), ({"df": f.id, "a": s} for s in res.series))
        etat.d["bdm_flux_faits"].append(f.id)
        etat.d["bdm_flux_stats"][f.id] = {"series": len(res.series), "requetes": res.requetes, "decoupages": res.decoupages, "erreurs": len(res.erreurs)}
        if res.erreurs:
            etat.d["bdm_flux_erreurs"][f.id] = res.erreurs[:20]
        etat.sauver()
        ecart = "" if f.nb_series in (None, len(res.series)) else f" (annoncées {f.nb_series})"
        log(f"  [{i}/{len(a_faire)}] {f.id} : {len(res.series)} séries{ecart}, {res.requetes} requêtes, {res.decoupages} découpages, "
            f"{len(res.erreurs)} erreurs, {time.monotonic() - t0:.0f} s")
        for e in res.erreurs[:3]:
            log(f"      ! {e[:220]}")
    etat.marquer("bdm_series")


def charger_series_bdm(etat: Etat) -> dict[str, dict]:
    series: dict[str, dict] = {}
    for o in lire_jsonl(etat.chemin("bdm_series.jsonl.gz")):
        a = o.get("a") or {}
        idb = a.get("IDBANK")
        if idb and idb not in series:
            a["_df"] = o.get("df", "")
            series[idb] = a
    return series


# --------------------------------------------------------------------------------------
# Étape bdm_periodes
# --------------------------------------------------------------------------------------

def a_lire_periodes(a: dict, zones: dict[str, str]) -> bool:
    if a.get("FREQ") not in cat.FREQUENCES_RETENUES:
        return False
    if cat.classer_zone(a.get("REF_AREA", ""), zones.get(a.get("REF_AREA", ""), "")) == "hors_nationale":
        return False
    maj = a.get("LAST_UPDATE", "")
    return not maj or maj >= f"{cat.ANNEE_DERNIERE_MIN}-01-01"


def etape_bdm_periodes(etat: Etat, client, budget: Budget) -> None:
    series = charger_series_bdm(etat)
    zones = charger_codelists(etat).get("CL_ZONE_GEO", {})
    deja = {o["i"] for o in lire_jsonl(etat.chemin("bdm_periodes.jsonl.gz")) if "i" in o}
    cibles = [idb for idb, a in series.items() if a_lire_periodes(a, zones) and idb not in deja]
    annuelles = sorted(i for i in cibles if series[i].get("FREQ") == "A")
    infra = sorted(i for i in cibles if series[i].get("FREQ") != "A")
    log(f"BDM périodes : {len(series)} séries listées ; à lire : {len(annuelles)} annuelles (séries complètes), "
        f"{len(infra)} infra-annuelles (première/dernière observation) ; {len(deja)} déjà lues")
    erreurs: list[str] = []
    chemin = etat.chemin("bdm_periodes.jsonl.gz")

    lots_a = bdm.lots(annuelles, 200)
    for k, lot in enumerate(lots_a, 1):
        budget.verifier()
        recues = {s.idbank: s for s in bdm.obtenir_series(lot, client, taille_lot=200, erreurs=erreurs)}
        sortie = []
        for idb in lot:
            s = recues.get(idb)
            if s is None:
                sortie.append({"i": idb, "m": "absente"})
                continue
            r = s.resume()
            sortie.append({"i": idb, "p": r.premiere, "d": r.derniere, "n": r.nb_annees_depuis, "nv": r.nb_valeurs, "s": r.statut_derniere, "m": "complete"})
        ajouter_jsonl(chemin, sortie)
        if k % 20 == 0 or k == len(lots_a):
            log(f"  annuelles : lot {k}/{len(lots_a)} ({client.nb_appels} appels, {client.nb_octets / 1e6:.0f} Mo, {len(erreurs)} erreurs)")

    lots_i = bdm.lots(infra, 400)
    for k, lot in enumerate(lots_i, 1):
        budget.verifier()
        periodes = bdm.periodes_par_idbank(lot, client, erreurs=erreurs)
        sortie = []
        for idb in lot:
            r = periodes.get(idb)
            if r is None:
                sortie.append({"i": idb, "m": "absente"})
            else:
                sortie.append({"i": idb, "p": r.premiere, "d": r.derniere, "s": r.statut_derniere, "m": "premiere_derniere"})
        ajouter_jsonl(chemin, sortie)
        if k % 20 == 0 or k == len(lots_i):
            log(f"  infra-annuelles : lot {k}/{len(lots_i)} ({client.nb_appels} appels, {client.nb_octets / 1e6:.0f} Mo, {len(erreurs)} erreurs)")
    if erreurs:
        etat.d["bdm_periodes_erreurs"] = (etat.d.get("bdm_periodes_erreurs", []) + erreurs)[:200]
        for e in erreurs[:10]:
            log(f"      ! {e[:220]}")
    etat.marquer("bdm_periodes")


# --------------------------------------------------------------------------------------
# Étape melodi
# --------------------------------------------------------------------------------------

def motif_jeu_hors_champ(jeu: mel.JeuMelodi) -> Optional[str]:
    for motif, explication in JEUX_HORS_CHAMP:
        if motif.search(jeu.id):
            return explication
    if jeu.niveaux_geo and not jeu.niveau_national:
        return f"pas de niveau national dans le catalogue ({';'.join(jeu.niveaux_geo)})"
    return None


def freq_de(dims: dict[str, str], periode: str, jeu: mel.JeuMelodi) -> str:
    if dims.get("FREQ"):
        return str(dims["FREQ"])
    if re.fullmatch(r"\d{4}", periode or ""):
        return "A"
    if re.fullmatch(r"\d{4}-Q\d", periode or ""):
        return "T"
    if re.fullmatch(r"\d{4}-S\d", periode or ""):
        return "S"
    if re.fullmatch(r"\d{4}-\d{2}", periode or ""):
        return "M"
    return PERIODICITES.get(cat.normaliser(jeu.periodicite).replace("-", ""), "")


class AgregatMelodi:
    """Regroupe les observations d'un jeu en séries et résume leurs périodes."""

    def __init__(self, jeu: mel.JeuMelodi) -> None:
        self.jeu = jeu
        self.series: dict[tuple[str, str], dict] = {}
        self.mesures: set[str] = set()
        self.valeurs_dims: dict[str, set[str]] = defaultdict(set)
        self.nb_obs = 0

    def ajouter(self, obs: dict) -> None:
        self.nb_obs += 1
        dims = {k: str(v) for k, v in (obs.get("dimensions") or {}).items()}
        periode = dims.pop("TIME_PERIOD", "")
        if "GEO" in dims:
            dims["GEO"] = mel.normaliser_geo(dims["GEO"])
        mesure, valeur = mel.mesure_et_valeur(obs)
        self.mesures.add(mesure)
        cle = (mel.identifiant_serie(self.jeu.id, dims), mesure)
        s = self.series.get(cle)
        if s is None:
            s = self.series[cle] = {"dims": dims, "p": "", "d": "", "nv": 0, "annees": set(), "s": "", "freq": ""}
            for k, v in dims.items():
                self.valeurs_dims[k].add(v)
        if valeur is None:
            return
        s["nv"] += 1
        if not s["p"] or periode < s["p"]:
            s["p"] = periode
        if not s["d"] or periode >= s["d"]:
            s["d"] = periode
            s["s"] = str((obs.get("attributes") or {}).get("OBS_STATUS") or "")
        a = cat.annee_de(periode)
        if a is not None and a >= cat.ANNEE_DEBUT_PROJET:
            s["annees"].add(a)
        if not s["freq"]:
            s["freq"] = freq_de(dims, periode, self.jeu)

    def sorties(self, plage: dict[str, mel.Concept]) -> list[dict]:
        plusieurs = len(self.mesures) > 1
        ordre = [c for c in self.jeu.composants if c in self.valeurs_dims] + sorted(k for k in self.valeurs_dims if k not in self.jeu.composants)
        variables = [k for k in ordre if len(self.valeurs_dims[k]) > 1]
        geo_concept = plage.get("GEO")
        lignes = []
        for (sid, mesure), s in sorted(self.series.items()):
            dims = s["dims"]
            parties = []
            for k in variables:
                v = dims.get(k, "")
                concept = plage.get(k)
                parties.append((concept.valeurs.get(v) if concept else "") or v)
            libelle = self.jeu.titre + (" — " + " ; ".join(parties) if parties else "")
            unite = ""
            if "UNIT_MEASURE" in dims:
                c = plage.get("UNIT_MEASURE")
                unite = (c.valeurs.get(dims["UNIT_MEASURE"]) if c else "") or dims["UNIT_MEASURE"]
            geo = dims.get("GEO", "") or self.jeu.spatial
            geo_lib = (geo_concept.valeurs.get(geo, "") if geo_concept else "") or ("" if dims.get("GEO") else "niveau du jeu : " + self.jeu.spatial)
            lignes.append({
                "jeu": self.jeu.id, "sid": sid + (f"#{mesure}" if plusieurs else ""), "lib": libelle, "freq": s["freq"], "geo": geo, "geo_lib": geo_lib,
                "unite": unite, "p": s["p"], "d": s["d"], "n": len(s["annees"]), "nv": s["nv"], "s": s["s"], "maj": self.jeu.modifie,
                "dims": dims,
            })
        return lignes


def extraire_jeu(jeu: mel.JeuMelodi, client, budget: Budget) -> tuple[list[dict], dict]:
    info: dict[str, Any] = {"statut": "traité", "methode": "", "remarque": "", "nb_obs": 0, "nb_series": 0}
    plage = mel.obtenir_plage(jeu.id, client)
    nationales = mel.valeurs_geo_nationales(plage)
    geo = plage.get("GEO")
    if geo is not None and not nationales:
        info.update(statut="écarté", remarque="aucune valeur géographique nationale dans /range")
        return [], info
    toutes_nationales = geo is None or len(nationales) == len(geo.types)
    filtres: list[Optional[dict[str, str]]] = [None] if toutes_nationales else [{"GEO": cle} for cle, _ in nationales]
    info["geo_nationales"] = ";".join(cle for cle, _ in nationales) if nationales else f"(pas de dimension GEO ; jeu {jeu.spatial})"
    agregat = AgregatMelodi(jeu)
    methodes = []
    for filtre in filtres:
        budget.verifier()
        total = mel.compter(jeu.id, filtre, client)
        if total == 0:
            continue
        if total > PLAFOND_MELODI:
            info["remarque"] += f" volume national {total} > {PLAFOND_MELODI} : non extrait ;"
            info["statut"] = "partiel"
            continue
        produit = jeu.produit_csv()
        if total > mel.LIMITE_RESULTATS and toutes_nationales and produit:
            contenu = mel.telecharger_fichier(produit["accessURL"], client)
            _, lignes, _ = mel.lire_zip_csv(contenu)
            for ligne in lignes:
                agregat.ajouter(mel.ligne_csv_en_observation(ligne))
            methodes.append(f"fichier ZIP ({len(contenu) / 1e6:.1f} Mo)")
        else:
            ext = mel.Extraction()
            for obs in mel.iterer_observations(jeu.id, filtre, client, total=total, extraction=ext):
                agregat.ajouter(obs)
            methodes.append(f"/data {ext.pages} page(s)" + ("" if not filtre else f" {filtre['GEO']}"))
            if not ext.complete:
                info["statut"] = "partiel"
                info["remarque"] += f" {ext.remarque} ;"
    info["methode"] = ", ".join(methodes)
    info["nb_obs"] = agregat.nb_obs
    sorties = agregat.sorties(plage)
    info["nb_series"] = len(sorties)
    return sorties, info


def etape_melodi(etat: Etat, client, budget: Budget, max_jeux: Optional[int], echantillons: bool) -> None:
    chemin_cat = etat.chemin("melodi_catalogue.json")
    if not chemin_cat.exists():
        rep = client.get(f"{mel.URL_BASE}/catalog/all")
        if not rep.ok:
            raise RuntimeError(f"catalogue Melodi : HTTP {rep.statut} {rep.extrait()}")
        chemin_cat.write_bytes(rep.contenu)
        if echantillons:
            sauver_echantillon("melodi_catalog_all.json.gz", rep, compresser=True)
    jeux = mel.analyser_catalogue(chemin_cat.read_bytes())
    log(f"Melodi : {len(jeux)} jeux au catalogue")
    etat.d["compteurs"]["melodi_jeux"] = len(jeux)
    if max_jeux:
        jeux = jeux[:max_jeux]
    statuts = etat.d["melodi_jeux"]
    for i, jeu in enumerate(jeux, 1):
        if jeu.id in statuts:
            continue
        budget.verifier()
        motif = motif_jeu_hors_champ(jeu)
        if motif:
            statuts[jeu.id] = {"statut": "écarté", "remarque": motif}
            etat.sauver()
            continue
        t0 = time.monotonic()
        try:
            sorties, info = extraire_jeu(jeu, client, budget)
        except BudgetAtteint:
            raise
        except Exception as exc:
            statuts[jeu.id] = {"statut": "erreur", "remarque": f"{type(exc).__name__} : {exc}"[:400]}
            etat.sauver()
            log(f"  [{i}/{len(jeux)}] {jeu.id} : ERREUR {type(exc).__name__} {str(exc)[:200]}")
            continue
        ajouter_jsonl(etat.chemin("melodi_series.jsonl.gz"), sorties)
        statuts[jeu.id] = info
        etat.sauver()
        log(f"  [{i}/{len(jeux)}] {jeu.id} : {info['statut']}, {info['nb_series']} séries nationales, {info['nb_obs']} obs., "
            f"{info.get('methode', '')} {info.get('remarque', '')} ({time.monotonic() - t0:.0f} s)")
    etat.marquer("melodi")


# --------------------------------------------------------------------------------------
# Étape echantillons (futures fixtures, décision D21)
# --------------------------------------------------------------------------------------

PROVENANCE: list[dict] = []


def sauver_echantillon(nom: str, rep: Reponse, compresser: bool = False, limite: int = 400_000) -> None:
    ECHANTILLONS.mkdir(parents=True, exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base, _, ext = nom.partition(".")
    fichier = ECHANTILLONS / f"{base}_{date}.{ext}"
    contenu = rep.contenu
    tronque = ""
    if compresser:
        contenu = gzip.compress(contenu)
    elif len(contenu) > limite:
        contenu = contenu[:limite]
        tronque = f"tronqué à {limite} octets sur {len(rep.contenu)}"
    fichier.write_bytes(contenu)
    PROVENANCE.append({"fichier": fichier.name, "url": rep.url, "statut_http": rep.statut,
                       "content_type": rep.entetes.get("Content-Type", rep.entetes.get("content-type", "")),
                       "octets": len(rep.contenu), "enregistre_le": maintenant(), "remarque": tronque})


def etape_echantillons(etat: Etat, client) -> None:
    b = bdm.URL_BASE
    demandes = [
        ("bdm_dataflow_ODD-ERADICATION-PAUVRETE.xml", f"{b}/dataflow/FR1/ODD-ERADICATION-PAUVRETE", None),
        ("bdm_datastructure_CHOMAGE-TRIM-NATIONAL.xml", f"{b}/datastructure/FR1/CHOMAGE-TRIM-NATIONAL", None),
        ("bdm_codelist_CL_PERIODICITE.xml", f"{b}/codelist/FR1/CL_PERIODICITE", None),
        ("bdm_nodata_ODD-ERADICATION-PAUVRETE.xml", f"{b}/data/ODD-ERADICATION-PAUVRETE", {"detail": "nodata"}),
        ("bdm_nodata_CNA-2020-PIB.xml", f"{b}/data/CNA-2020-PIB", {"detail": "nodata"}),
        ("bdm_nodata_CHOMAGE-TRIM-NATIONAL_cle_T.xml", f"{b}/data/CHOMAGE-TRIM-NATIONAL/T........", {"detail": "nodata"}),
        ("bdm_erreur_cle_sans_resultat.xml", f"{b}/data/CHOMAGE-TRIM-NATIONAL/A........", {"detail": "nodata"}),
        ("bdm_erreur_trop_de_series_CNA-2020-ERE.xml", f"{b}/data/CNA-2020-ERE", {"detail": "nodata"}),
        ("bdm_serie_010593281.xml", f"{b}/data/SERIES_BDM/010593281", None),
        ("bdm_serie_001688527_last5.xml", f"{b}/data/SERIES_BDM/001688527", {"lastNObservations": "5"}),
        ("bdm_series_010593281+001688527_first1.xml", f"{b}/data/SERIES_BDM/010593281+001688527", {"firstNObservations": "1"}),
        ("melodi_range_DS_SRCV_SATISFACTION.json", f"{mel.URL_BASE}/range/DS_SRCV_SATISFACTION", None),
        ("melodi_data_DS_SRCV_SATISFACTION_extrait.json", f"{mel.URL_BASE}/data/DS_SRCV_SATISFACTION", {"maxResult": "40"}),
        ("melodi_data_DS_SRCV_SATISFACTION_page2.json", f"{mel.URL_BASE}/data/DS_SRCV_SATISFACTION", {"maxResult": "40", "page": "2"}),
        ("melodi_data_DS_SRCV_SATISFACTION_totalCount.json", f"{mel.URL_BASE}/data/DS_SRCV_SATISFACTION", {"totalCount": "TRUE", "maxResult": "0"}),
        ("melodi_range_DS_NAT_SDG.json", f"{mel.URL_BASE}/range/DS_NAT_SDG", None),
        ("melodi_data_DS_NAT_SDG_extrait.json", f"{mel.URL_BASE}/data/DS_NAT_SDG", {"maxResult": "40"}),
        ("melodi_range_DD_CNA_AGREGATS.json", f"{mel.URL_BASE}/range/DD_CNA_AGREGATS", None),
    ]
    for nom, url, params in demandes:
        try:
            rep = client.get(url, params=params)
        except ErreurReseau as exc:
            log(f"  échantillon {nom} : échec réseau {exc}")
            continue
        sauver_echantillon(nom, rep)
        log(f"  échantillon {nom} : HTTP {rep.statut}, {len(rep.contenu)} octets")
    # fichier ZIP complet d'un petit jeu : extraits des CSV de données et de métadonnées
    try:
        rep_notice = client.get(f"{mel.URL_BASE}/catalog/DS_SRCV_SATISFACTION")
        sauver_echantillon("melodi_catalog_DS_SRCV_SATISFACTION.json", rep_notice)
        notice = mel.analyser_catalogue(rep_notice.contenu)[0] if rep_notice.ok else None
        produit = notice.produit_csv() if notice else None
        if produit:
            rep = client.get(produit["accessURL"])
            if rep.ok:
                archive = zipfile.ZipFile(io.BytesIO(rep.contenu))
                for membre in archive.namelist():
                    lignes = archive.read(membre).decode("utf-8-sig", errors="replace").splitlines()[:60]
                    faux = Reponse(rep.statut, ("\n".join(lignes) + "\n").encode(), f"{rep.url} [{membre}, 60 premières lignes]", rep.entetes)
                    sauver_echantillon(f"melodi_file_DS_SRCV_SATISFACTION_{Path(membre).stem}_extrait.csv", faux)
                log(f"  échantillon ZIP DS_SRCV_SATISFACTION : {', '.join(archive.namelist())}")
    except Exception as exc:
        log(f"  échantillon ZIP : {type(exc).__name__} {exc}")
    ecrire_provenance()
    etat.marquer("echantillons")


def ecrire_provenance() -> None:
    if not PROVENANCE:
        return
    ECHANTILLONS.mkdir(parents=True, exist_ok=True)
    chemin = ECHANTILLONS / "provenance.csv"
    anciennes = []
    if chemin.exists():
        noms = {p["fichier"] for p in PROVENANCE}
        anciennes = [r for r in csv.DictReader(open(chemin, encoding="utf-8")) if r["fichier"] not in noms]
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["fichier", "url", "statut_http", "content_type", "octets", "enregistre_le", "remarque"])
        w.writeheader()
        w.writerows(anciennes + PROVENANCE)
    PROVENANCE.clear()


# --------------------------------------------------------------------------------------
# Étape consolidation : inventaires bruts
# --------------------------------------------------------------------------------------

def ecrire_csv(chemin: Path, colonnes: list[str], lignes: Iterable[dict], compresser: bool = False) -> int:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    tmp = chemin.with_name(chemin.name + ".tmp")
    ouvrir = (lambda p: gzip.open(p, "wt", encoding="utf-8", newline="")) if compresser else (lambda p: open(p, "w", encoding="utf-8", newline=""))
    n = 0
    with ouvrir(tmp) as f:
        w = csv.DictWriter(f, fieldnames=colonnes, extrasaction="ignore")
        w.writeheader()
        for ligne in lignes:
            w.writerow(ligne)
            n += 1
    tmp.replace(chemin)
    return n


def lire_csv(chemin: Path) -> list[dict]:
    ouvrir = gzip.open if chemin.suffix == ".gz" else open
    with ouvrir(chemin, "rt", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def etape_consolidation(etat: Etat) -> None:
    series = charger_series_bdm(etat)
    zones = charger_codelists(etat).get("CL_ZONE_GEO", {})
    periodes = {o["i"]: o for o in lire_jsonl(etat.chemin("bdm_periodes.jsonl.gz")) if "i" in o}
    flux = {f.id: f for f in charger_flux(etat)}
    lignes = []
    for idb, a in series.items():
        p = periodes.get(idb, {})
        dims = {k: v for k, v in a.items() if k not in bdm.ATTRIBUTS_SERIE and not k.startswith("_") and k not in ("TITLE_EN", "SERIE_ARRETEE")}
        if not p:
            methode = "non lues (fréquence, zone ou dernière mise à jour < 2020)" if not a_lire_periodes(a, zones) else "non lues (interruption)"
        else:
            methode = {"complete": "série complète", "premiere_derniere": "première et dernière observations", "absente": "absente de la réponse SERIES_BDM"}.get(p.get("m"), p.get("m", ""))
        lignes.append({
            "idbank": idb, "dataflow": a.get("_df", ""), "titre_fr": a.get("TITLE_FR", ""), "freq": a.get("FREQ", ""),
            "ref_area": a.get("REF_AREA", ""), "zone": cat.classer_zone(a.get("REF_AREA", ""), zones.get(a.get("REF_AREA", ""), "")),
            "unit_measure": a.get("UNIT_MEASURE", ""), "unit_mult": a.get("UNIT_MULT", ""), "last_update": a.get("LAST_UPDATE", ""),
            "serie_arretee": a.get("SERIE_ARRETEE", ""), "premiere_periode": p.get("p", ""), "derniere_periode": p.get("d", ""),
            "nb_annees_depuis_2000": p.get("n", ""), "statut_derniere_valeur": p.get("s", ""), "periodes": methode,
            "dimensions": ";".join(f"{k}={v}" for k, v in sorted(dims.items())),
        })
    lignes.sort(key=lambda l: (l["dataflow"], l["idbank"]))
    n = ecrire_csv(INVENTAIRE_BDM, COLONNES_INVENTAIRE_BDM, lignes, compresser=True)
    log(f"Inventaire BDM : {n} séries → {INVENTAIRE_BDM.relative_to(RACINE)}")

    # tableau des dataflows (statut de traitement)
    stats = etat.d.get("bdm_flux_stats", {})
    erreurs = etat.d.get("bdm_flux_erreurs", {})
    lignes_flux = []
    for fid, f in flux.items():
        st = stats.get(fid, {})
        lignes_flux.append({"dataflow": fid, "nom_fr": f.nom_fr, "url_page": f.url_page, "nb_series_annoncees": f.nb_series or "",
                            "nb_series_listees": st.get("series", ""), "requetes": st.get("requetes", ""), "decoupages": st.get("decoupages", ""),
                            "erreurs": " | ".join(erreurs.get(fid, []))[:500]})
    etat.chemin("bdm_flux_traitement.json").write_text(json.dumps(lignes_flux, ensure_ascii=False))

    mlignes = []
    for o in lire_jsonl(etat.chemin("melodi_series.jsonl.gz")):
        mlignes.append({"serie_id": o["sid"], "jeu": o["jeu"], "libelle": o["lib"], "freq": o["freq"], "geo": o["geo"], "geo_libelle": o["geo_lib"],
                        "unite": o["unite"], "premiere_periode": o["p"], "derniere_periode": o["d"], "nb_annees_depuis_2000": o["n"],
                        "nb_valeurs": o["nv"], "statut_derniere_valeur": o["s"], "derniere_maj": o["maj"],
                        "dimensions": ";".join(f"{k}={v}" for k, v in sorted(o["dims"].items()))})
    n = ecrire_csv(INVENTAIRE_MELODI, COLONNES_INVENTAIRE_MELODI, mlignes, compresser=True)
    log(f"Inventaire Melodi : {n} séries nationales → {INVENTAIRE_MELODI.relative_to(RACINE)}")

    # tableau des jeux Melodi (statut de traitement)
    jeux = {j.id: j for j in mel.analyser_catalogue(etat.chemin("melodi_catalogue.json").read_bytes())} if etat.chemin("melodi_catalogue.json").exists() else {}
    lignes_jeux = []
    for jid, j in jeux.items():
        st = etat.d.get("melodi_jeux", {}).get(jid, {"statut": "non traité"})
        lignes_jeux.append({"jeu": jid, "titre": j.titre, "sous_titre": j.sous_titre, "periodicite": j.periodicite, "debut": j.debut[:4], "fin": j.fin[:4],
                            "spatial": j.spatial, "niveaux_geo": ";".join(j.niveaux_geo), "nb_observations_catalogue": j.nb_observations or "",
                            "modifie": j.modifie, "themes": ";".join(j.themes)[:300], "statut": st.get("statut", ""), "remarque": (st.get("remarque") or "").strip(),
                            "methode": st.get("methode", ""), "geo_nationales": st.get("geo_nationales", ""), "nb_obs_nationales": st.get("nb_obs", ""),
                            "nb_series_nationales": st.get("nb_series", "")})
    etat.chemin("melodi_jeux_traitement.json").write_text(json.dumps(lignes_jeux, ensure_ascii=False))
    etat.marquer("consolidation")


# --------------------------------------------------------------------------------------
# Étape catalogage (hors ligne)
# --------------------------------------------------------------------------------------

def frequence_libelle(code: str) -> str:
    return cat.FREQUENCES_RETENUES.get(code, code)


def unite_libelle(code: str, mult: str, unites: dict[str, str]) -> str:
    lib = unites.get(code, "") or code
    if mult and mult not in ("0", ""):
        lib += f" (×10^{mult})"
    return lib


def motif_exclusion_bdm(l: dict) -> Optional[str]:
    if l["freq"] not in cat.FREQUENCES_RETENUES:
        return f"fréquence {l['freq'] or '?'} non retenue"
    if l["zone"] == "hors_nationale":
        return f"zone non nationale ({l['ref_area']})"
    if not l["derniere_periode"]:
        if l["periodes"].startswith("non lues"):
            return f"dernière mise à jour {l['last_update'] or '?'} antérieure à {cat.ANNEE_DERNIERE_MIN}"
        return f"périodes inconnues ({l['periodes']})"
    a = cat.annee_de(l["derniere_periode"])
    if a is None or a < cat.ANNEE_DERNIERE_MIN:
        return f"dernière période {l['derniere_periode']} < {cat.ANNEE_DERNIERE_MIN}"
    return None


def etape_catalogage(etat: Optional[Etat]) -> dict:
    if not INVENTAIRE_BDM.exists():
        log("Catalogage : inventaire BDM absent, rien à faire (la collecte n'a pas encore abouti)")
        return {}
    inventaire = lire_csv(INVENTAIRE_BDM)
    codelists = charger_codelists(etat) if etat and etat.chemin("bdm_codelists.json").exists() else {}
    unites = codelists.get("CL_UNITE", {})
    zones_lib = codelists.get("CL_ZONE_GEO", {})
    flux_info = {}
    chemin_flux = (etat.chemin("bdm_flux_traitement.json") if etat else None)
    if chemin_flux and chemin_flux.exists():
        flux_info = {f["dataflow"]: f for f in json.loads(chemin_flux.read_text())}
    elif FLUX_CSV.exists():
        flux_info = {f["dataflow"]: f for f in lire_csv(FLUX_CSV)}
    anciens = cat.flux_anciennes_bases(set(flux_info) | {l["dataflow"] for l in inventaire})

    catalogue, exclusions, par_flux = [], Counter(), defaultdict(Counter)
    for l in inventaire:
        df = l["dataflow"]
        par_flux[df]["listees"] += 1
        motif = motif_exclusion_bdm(l)
        if motif:
            exclusions[re.sub(r"\(.*?\)|\d{4}(-\S+)?", "…", motif)] += 1
            continue
        nb = int(l["nb_annees_depuis_2000"]) if l["nb_annees_depuis_2000"] not in ("", None) else None
        dims = dict(kv.split("=", 1) for kv in l["dimensions"].split(";") if "=" in kv)
        d = cat.decider(
            libelle=l["titre_fr"], theme=df, theme_libelle=flux_info.get(df, {}).get("nom_fr", ""), frequence=l["freq"], zone=l["zone"],
            premiere=l["premiere_periode"], derniere=l["derniere_periode"], nb_annees_depuis_2000=nb,
            serie_arretee=l["serie_arretee"].upper() == "TRUE" or "serie arretee" in cat.normaliser(l["titre_fr"]),
            ancienne_base=anciens.get(df), dimensions={k: v for k, v in dims.items() if k == "SEXE"},
        )
        par_flux[df]["catalogue"] += 1
        par_flux[df][d.candidat] += 1
        catalogue.append({
            "source": "INSEE BDM", "serie_id": l["idbank"], "libelle": l["titre_fr"], "unite": unite_libelle(l["unit_measure"], l["unit_mult"], unites),
            "frequence": frequence_libelle(l["freq"]), "geo": l["ref_area"], "premiere_periode": l["premiere_periode"], "derniere_periode": l["derniere_periode"],
            "derniere_maj": l["last_update"], "theme_source": df, "dimension_v0": d.dimension_v0, "candidat": d.candidat, "commentaire": d.commentaire,
            "agregable": "sans_objet" if l["freq"] == "A" else "oui", "ventilation": d.ventilation,
            "geo_libelle": zones_lib.get(l["ref_area"], cat.ZONE_LIBELLE.get(l["ref_area"], "")), "nb_annees_depuis_2000": l["nb_annees_depuis_2000"],
            "statut_derniere_valeur": l["statut_derniere_valeur"], "theme_libelle": flux_info.get(df, {}).get("nom_fr", ""),
            "url_api": f"{bdm.URL_BASE}/data/SERIES_BDM/{l['idbank']}",
        })
    catalogue.sort(key=lambda r: (r["theme_source"], r["serie_id"]))
    ecrire_csv(CATALOGUE_BDM, COLONNES_CATALOGUE, catalogue)

    # dataflows
    lignes_flux = []
    for df in sorted(set(flux_info) | set(par_flux)):
        f = flux_info.get(df, {})
        c = par_flux.get(df, Counter())
        lignes_flux.append({**{k: f.get(k, "") for k in ("dataflow", "nom_fr", "url_page", "nb_series_annoncees", "nb_series_listees", "requetes", "decoupages", "erreurs")},
                            "dataflow": df, "ancienne_base": anciens.get(df, ""), "nb_catalogue": c["catalogue"], "nb_oui": c["oui"],
                            "nb_a_verifier": c["a_verifier"], "nb_non": c["non"]})
    ecrire_csv(FLUX_CSV, ["dataflow", "nom_fr", "nb_series_annoncees", "nb_series_listees", "nb_catalogue", "nb_oui", "nb_a_verifier", "nb_non",
                          "ancienne_base", "requetes", "decoupages", "erreurs", "url_page"], lignes_flux)

    # zones rencontrées
    zones = Counter((l["ref_area"], l["zone"]) for l in inventaire)
    ecrire_csv(ZONES_CSV, ["ref_area", "libelle", "classe", "nb_series"],
               ({"ref_area": z, "libelle": zones_lib.get(z, ""), "classe": c, "nb_series": n} for (z, c), n in zones.most_common()))

    # Melodi
    mcatalogue, mexclusions = [], Counter()
    jeux_info = {}
    if etat and etat.chemin("melodi_jeux_traitement.json").exists():
        jeux_info = {j["jeu"]: j for j in json.loads(etat.chemin("melodi_jeux_traitement.json").read_text())}
    elif JEUX_CSV.exists():
        jeux_info = {j["jeu"]: j for j in lire_csv(JEUX_CSV)}
    par_jeu = defaultdict(Counter)
    if INVENTAIRE_MELODI.exists():
        for l in lire_csv(INVENTAIRE_MELODI):
            par_jeu[l["jeu"]]["nationales"] += 1
            freq = l["freq"]
            a = cat.annee_de(l["derniere_periode"])
            if freq not in cat.FREQUENCES_RETENUES:
                mexclusions[f"fréquence {freq or '?'} non retenue"] += 1
                continue
            if a is None or a < cat.ANNEE_DERNIERE_MIN:
                mexclusions[f"dernière période < {cat.ANNEE_DERNIERE_MIN} ou inconnue"] += 1
                continue
            dims = dict(kv.split("=", 1) for kv in l["dimensions"].split(";") if "=" in kv)
            nb = int(l["nb_annees_depuis_2000"]) if l["nb_annees_depuis_2000"] else None
            jeu = jeux_info.get(l["jeu"], {})
            zone = "principale" if l["geo"] in ("FRANCE-F", "FRANCE-FM", "FRANCE-FE", "FRANCE-FEHM", "FE", "FM", "FEHM") else "nationale"
            d = cat.decider(libelle=l["libelle"], theme=l["jeu"], theme_libelle=f"{jeu.get('titre', '')} {jeu.get('themes', '')}", frequence=freq, zone=zone,
                            premiere=l["premiere_periode"], derniere=l["derniere_periode"], nb_annees_depuis_2000=nb, dimensions=dims)
            par_jeu[l["jeu"]]["catalogue"] += 1
            par_jeu[l["jeu"]][d.candidat] += 1
            requete = l["serie_id"].split("#", 1)[0]
            mcatalogue.append({
                "source": "INSEE Melodi", "serie_id": l["serie_id"], "libelle": l["libelle"], "unite": l["unite"], "frequence": frequence_libelle(freq),
                "geo": l["geo"], "premiere_periode": l["premiere_periode"], "derniere_periode": l["derniere_periode"], "derniere_maj": l["derniere_maj"],
                "theme_source": l["jeu"], "dimension_v0": d.dimension_v0, "candidat": d.candidat, "commentaire": d.commentaire,
                "agregable": "sans_objet" if freq == "A" else "oui", "ventilation": d.ventilation, "geo_libelle": l["geo_libelle"],
                "nb_annees_depuis_2000": l["nb_annees_depuis_2000"], "statut_derniere_valeur": l["statut_derniere_valeur"],
                "theme_libelle": jeu.get("titre", ""), "url_api": f"{mel.URL_BASE}/data/{requete}",
            })
    mcatalogue.sort(key=lambda r: r["serie_id"])
    ecrire_csv(CATALOGUE_MELODI, COLONNES_CATALOGUE, mcatalogue)
    if jeux_info:
        lignes_jeux = []
        for jid, j in sorted(jeux_info.items()):
            c = par_jeu.get(jid, Counter())
            lignes_jeux.append({**j, "nb_catalogue": c["catalogue"], "nb_oui": c["oui"], "nb_a_verifier": c["a_verifier"], "nb_non": c["non"]})
        ecrire_csv(JEUX_CSV, ["jeu", "titre", "statut", "remarque", "nb_series_nationales", "nb_catalogue", "nb_oui", "nb_a_verifier", "nb_non",
                              "periodicite", "debut", "fin", "spatial", "niveaux_geo", "geo_nationales", "nb_observations_catalogue", "nb_obs_nationales",
                              "methode", "modifie", "sous_titre", "themes"], lignes_jeux)

    comparaison = comparer_phase1(inventaire, catalogue, mcatalogue, jeux_info)
    bilan = faire_bilan(inventaire, catalogue, exclusions, mcatalogue, mexclusions, jeux_info, comparaison, etat)
    BILAN_JSON.write_text(json.dumps(bilan, ensure_ascii=False, indent=1))
    log("Bilan : " + json.dumps({k: bilan[k] for k in ("bdm", "melodi")}, ensure_ascii=False)[:1500])
    log("Comparaison phase 1 : " + json.dumps(bilan.get("comparaison_phase1", {}), ensure_ascii=False)[:1200])
    return bilan


def comparer_phase1(inventaire: list[dict], catalogue: list[dict], mcatalogue: list[dict], jeux_info: dict) -> dict:
    if not PHASE1.exists():
        return {}
    phase1 = lire_csv(PHASE1)
    inv = {l["idbank"]: l for l in inventaire}
    cat_bdm = {r["serie_id"]: r for r in catalogue}
    cat_mel_par_jeu = defaultdict(list)
    for r in mcatalogue:
        cat_mel_par_jeu[r["theme_source"]].append(r)
    lignes, resume = [], Counter()
    for r in phase1:
        voie, sid = r.get("voie_acces", ""), r.get("serie_id", "")
        statut, motif, robot_dim, robot_cand = "", "", "", ""
        if voie.startswith("BDM"):
            if sid in cat_bdm:
                c = cat_bdm[sid]
                statut = "confirmee"
                robot_dim, robot_cand = c["dimension_v0"], c["candidat"]
                motif = c["commentaire"]
            elif sid in inv:
                statut = "ecartee_par_filtre"
                motif = motif_exclusion_bdm(inv[sid]) or ""
            else:
                statut = "absente_de_la_bdm"
                motif = "idbank non renvoyé par la liste des séries des dataflows"
        elif voie.startswith("Melodi"):
            jeu, _, requete = sid.partition("?")
            series = cat_mel_par_jeu.get(jeu, [])
            if requete:
                filtres = dict(kv.split("=", 1) for kv in requete.split("&") if "=" in kv)
                trouvees = [s for s in series if all(f"{k}={v}" in s["serie_id"].split("?", 1)[-1].split("#")[0].split("&") for k, v in filtres.items())]
                if trouvees:
                    statut = "confirmee"
                    robot_dim = ";".join(sorted({s["dimension_v0"] for s in trouvees}))
                    robot_cand = ";".join(sorted({s["candidat"] for s in trouvees}))
                    motif = f"{len(trouvees)} série(s) du catalogue correspondent"
                else:
                    statut = "non_retrouvee" if jeu in jeux_info else "jeu_absent"
                    motif = (jeux_info.get(jeu, {}).get("statut", "") + " " + jeux_info.get(jeu, {}).get("remarque", "")).strip() or "jeu absent du catalogue Melodi"
            else:
                if jeu in jeux_info:
                    statut = "confirmee" if series else "jeu_sans_serie_au_catalogue"
                    robot_cand = ";".join(f"{k}={v}" for k, v in sorted(Counter(s["candidat"] for s in series).items()))
                    motif = f"{len(series)} séries au catalogue ; jeu : {jeux_info[jeu].get('statut', '')} {jeux_info[jeu].get('remarque', '')}".strip()
                else:
                    statut, motif = "jeu_absent", "jeu absent du catalogue Melodi actuel"
        else:
            statut, motif = "hors_robot", "fichier insee.fr (niveau 2) : non moissonné par le robot"
        resume[f"{voie.split(' ')[0]}:{statut}"] += 1
        if statut == "confirmee" and robot_dim and r.get("dimension_v0") and robot_dim != r.get("dimension_v0"):
            resume["dimension_differente"] += 1
        if statut == "confirmee" and robot_cand and r.get("candidat") and robot_cand != r.get("candidat"):
            resume["candidat_different"] += 1
        lignes.append({"voie_acces": voie, "serie_id": sid, "libelle": r.get("libelle", ""), "dimension_phase1": r.get("dimension_v0", ""),
                       "candidat_phase1": r.get("candidat", ""), "statut_robot": statut, "dimension_robot": robot_dim, "candidat_robot": robot_cand,
                       "motif": motif})
    ecrire_csv(COMPARAISON_CSV, ["voie_acces", "serie_id", "libelle", "statut_robot", "motif", "dimension_phase1", "dimension_robot",
                                 "candidat_phase1", "candidat_robot"], lignes)
    ids_phase1 = {r.get("serie_id", "") for r in phase1}
    nouvelles = [c for c in catalogue if c["serie_id"] not in ids_phase1 and c["candidat"] in ("oui", "a_verifier")]
    resume_nouvelles = Counter(c["dimension_v0"] for c in nouvelles)
    return {"phase1": len(phase1), "statuts": dict(sorted(resume.items())), "bdm_nouvelles_oui_ou_a_verifier": len(nouvelles),
            "bdm_nouvelles_par_dimension": dict(resume_nouvelles.most_common())}


def faire_bilan(inventaire, catalogue, exclusions, mcatalogue, mexclusions, jeux_info, comparaison, etat) -> dict:
    def repartition(lignes, cle):
        return dict(Counter(l[cle] for l in lignes).most_common())

    def par_dimension(lignes):
        d = defaultdict(Counter)
        for l in lignes:
            d[l["dimension_v0"] or "(aucune)"][l["candidat"]] += 1
        return {k: dict(v) for k, v in sorted(d.items())}

    return {
        "date": maintenant(),
        "bdm": {
            "dataflows": len({l["dataflow"] for l in inventaire}),
            "series_listees": len(inventaire),
            "par_frequence": repartition(inventaire, "freq"),
            "par_zone": repartition(inventaire, "zone"),
            "catalogue": len(catalogue),
            "exclusions": dict(exclusions.most_common()),
            "candidat": repartition(catalogue, "candidat"),
            "catalogue_par_frequence": repartition(catalogue, "frequence"),
            "catalogue_par_geo": dict(Counter(c["geo"] for c in catalogue).most_common(15)),
        },
        "bdm_par_dimension": par_dimension(catalogue),
        "melodi": {
            "jeux": len(jeux_info),
            "jeux_par_statut": dict(Counter(j.get("statut", "") for j in jeux_info.values()).most_common()),
            "series_nationales": sum(int(j.get("nb_series_nationales") or 0) for j in jeux_info.values()),
            "catalogue": len(mcatalogue),
            "exclusions": dict(mexclusions.most_common()),
            "candidat": repartition(mcatalogue, "candidat"),
        },
        "melodi_par_dimension": par_dimension(mcatalogue),
        "comparaison_phase1": comparaison,
        "collecte": {k: (etat.d.get(k) if etat else None) for k in ("debut", "maj", "termine", "passages")},
    }


# --------------------------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--etapes", default=",".join(ETAPES), help="étapes à exécuter, séparées par des virgules")
    p.add_argument("--budget-minutes", type=float, default=240.0)
    p.add_argument("--nouveau", action="store_true", help="ignorer l'état existant et commencer un nouveau cycle")
    p.add_argument("--catalogage-seul", action="store_true", help="hors ligne : catalogage depuis les inventaires")
    p.add_argument("--max-flux", type=int, default=None, help="(essai) nombre maximal de dataflows")
    p.add_argument("--max-jeux", type=int, default=None, help="(essai) nombre maximal de jeux Melodi")
    p.add_argument("--intervalle-bdm", type=float, default=0.5, help="secondes minimales entre deux appels à bdm.insee.fr")
    argv = sys.argv[1:]
    if not argv and FICHIER_OPTIONS.exists():
        argv = shlex.split(FICHIER_OPTIONS.read_text(encoding="utf-8"), comments=True)
        log(f"Options lues dans {FICHIER_OPTIONS.name} : {' '.join(argv) or '(aucune)'}")
    args = p.parse_args(argv)

    if args.catalogage_seul:
        etat = Etat(ETAT_DIR) if ETAT_DIR.exists() else None
        etape_catalogage(etat)
        return 0

    etapes = [e for e in args.etapes.split(",") if e]
    budget = Budget(args.budget_minutes)
    etat = Etat(ETAT_DIR)
    if args.nouveau or not etat.d or etat.d.get("termine"):
        log("Nouveau cycle de collecte" + (" (le précédent était terminé)" if etat.d.get("termine") else ""))
        etat.nouveau_cycle()
    else:
        log(f"Reprise du cycle commencé le {etat.d.get('debut')} ; étapes déjà terminées : {', '.join(etat.d.get('etapes_terminees', [])) or 'aucune'}")
    passage = {"debut": maintenant(), "fin": None, "issue": None}
    etat.d["passages"].append(passage)
    etat.sauver()

    client = ClientHttp(intervalles={"bdm.insee.fr": args.intervalle_bdm, mel.HOTE: mel.INTERVALLE_MIN}, essais=3, journal=log)
    echantillons = "echantillons" in etapes and not etat.termine("echantillons")
    code = 0
    try:
        for etape in ETAPES:
            if etape not in etapes or etat.termine(etape):
                continue
            log(f"=== Étape {etape} (budget restant {budget.restant() / 60:.0f} min) ===")
            if etape == "bdm_flux":
                etape_bdm_flux(etat, client, echantillons)
            elif etape == "bdm_series":
                etape_bdm_series(etat, client, budget, args.max_flux)
            elif etape == "bdm_periodes":
                etape_bdm_periodes(etat, client, budget)
            elif etape == "melodi":
                etape_melodi(etat, client, budget, args.max_jeux, echantillons)
            elif etape == "echantillons":
                etape_echantillons(etat, client)
            elif etape == "consolidation":
                etape_consolidation(etat)
            elif etape == "catalogage":
                etape_catalogage(etat)
                etat.marquer("catalogage")
        termine = all(etat.termine(e) for e in ETAPES if e in etapes)
        passage["issue"] = "cycle terminé" if termine else "étapes demandées terminées"
        if termine and set(ETAPES) <= set(etapes):
            etat.d["termine"] = True
            for f in ("bdm_series.jsonl.gz", "bdm_periodes.jsonl.gz", "melodi_series.jsonl.gz", "melodi_catalogue.json"):
                if etat.chemin(f).exists():
                    etat.chemin(f).unlink()
            log("Cycle terminé : fichiers d'état intermédiaires supprimés (les inventaires gardent tout).")
    except BudgetAtteint:
        passage["issue"] = "budget de temps atteint : reprise au prochain passage"
        log(f"BUDGET ATTEINT ({args.budget_minutes:.0f} min) : état sauvegardé, le prochain passage reprendra.")
    except Exception as exc:
        passage["issue"] = f"erreur : {type(exc).__name__} {exc}"[:400]
        log(f"ERREUR FATALE : {type(exc).__name__} {exc}")
        traceback.print_exc()
        code = 1
    finally:
        ecrire_provenance()
        passage["fin"] = maintenant()
        passage["appels"] = getattr(client, "nb_appels", 0)
        passage["mo"] = round(getattr(client, "nb_octets", 0) / 1e6, 1)
        etat.sauver()
        log(f"Fin du passage : {passage['issue']} ; {passage['appels']} appels HTTP, {passage['mo']} Mo, {(time.monotonic() - DEBUT) / 60:.1f} min")
    return code


if __name__ == "__main__":
    sys.exit(main())
