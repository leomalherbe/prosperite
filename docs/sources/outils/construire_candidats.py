"""Construit docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv (mission M04, tâche T3).

Principe : chaque indicateur candidat est décrit dans candidats_definitions.py (libellé, dimension v0,
sens, déclaratif, type, composite, doublon INSEE/Eurostat, commentaire) et **rattaché à une série
repérée par le robot** (fichiers docs/sources/series/*.csv|txt produits par scripts/collecte_sources.py,
ou extraits de phase 1 dans docs/sources/verif_acces/extraits/). Les années (première, dernière,
nombre de points depuis 2000) sont lues dans ces fichiers, jamais saisies à la main ; une série non
retrouvée fait échouer la construction (aucune ligne « non trouvé » n'est écrite sans le dire).

La dimension v1 proposée est calculée par la table de correspondance v0 → v1 de la mission M03
(copie : correspondance_v0_v1_m03.csv, branche m03-grille, commit 7dd7fcb) : première règle dont la
dimension v0 correspond et dont le motif est trouvé dans le libellé ; une définition peut la forcer
(paramètre dim_v1) en le motivant dans le commentaire.

Ce script est rangé hors de scripts/ pour ne pas déclencher le robot « Collecte » à chaque
modification. Exécution (hors ligne) :
    python docs/sources/outils/construire_candidats.py [--references <dossier>]
où <dossier> contient insee_indicateurs_reperes.csv (branche m01-insee) et eurostat_jeux_catalogue.csv
(branche m02-eurostat) : les identifiants de doublons cités sont alors contrôlés.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parents[3]
SERIES = RACINE / "docs" / "sources" / "series"
EXTRAITS = RACINE / "docs" / "sources" / "verif_acces" / "extraits"
SORTIE = RACINE / "docs" / "sources" / "10_indicateurs_candidats_hors_insee_eurostat.csv"
CORRESPONDANCE = Path(__file__).resolve().parent / "correspondance_v0_v1_m03.csv"

COLONNES = ["indicateur", "dimension_v0", "source", "identifiant_ou_url", "unite", "sens", "declaratif",
            "frequence", "premiere_annee", "derniere_annee", "doublon_insee_eurostat", "commentaire",
            "dimension_v1_proposee", "type", "composite", "geo", "ventilation", "nb_points_depuis_2000",
            "niveau_source", "fiabilite", "preuve"]
DIMENSIONS = {"niveau_de_vie", "travail", "logement_cadre_vie", "sante", "education", "liens_bien_etre",
              "securite_confiance", "democratie", "egalites", "planete"}
DIMENSIONS_V1 = (DIMENSIONS - {"securite_confiance"}) | {"securite", "hors_grille", "a_classer"}

LIGNES: list[dict] = []
_CACHE: dict[str, pd.DataFrame] = {}
_REGLES: list[dict] = []


# --------------------------------------------------------------------------- lecture des preuves


def table(fichier: str) -> pd.DataFrame:
    """Liste de séries produite par le robot (docs/sources/series/<fichier>.csv)."""
    if fichier not in _CACHE:
        chemin = SERIES / f"{fichier}.csv"
        _CACHE[fichier] = pd.read_csv(chemin, dtype=str).fillna("") if chemin.exists() else pd.DataFrame()
    return _CACHE[fichier]


def annees_de(periodes: str, n: int) -> tuple[list[int], bool]:
    """Années couvertes par la chaîne `periodes` du robot, et indicateur « périodes non annuelles ».

    Le robot compresse les années en plages (« 2000-2002,2005 ») ; les autres étiquettes (moyennes
    pluriannuelles « 2009-2011 », campagnes « 2006/2007 ») sont listées telles quelles, élidées par « … »
    au-delà de 12. Pour une étiquette, on retient l'année de fin."""
    jetons = [j.strip() for j in periodes.split(",") if j.strip()]
    elide = "…" in jetons
    jetons = [j for j in jetons if j != "…"]
    if not elide and jetons and all(re.fullmatch(r"\d{4}(-\d{4})?", j) for j in jetons):
        ans: list[int] = []
        for j in jetons:
            m = re.fullmatch(r"(\d{4})-(\d{4})", j)
            ans += list(range(int(m.group(1)), int(m.group(2)) + 1)) if m else [int(j)]
        if n in (0, len(set(ans))):
            return sorted(set(ans)), False
    fins = [int(re.findall(r"\d{4}", j)[-1]) for j in jetons if re.findall(r"\d{4}", j)]
    if elide and fins and fins[-1] - fins[0] + 1 == n:
        fins = list(range(fins[0], fins[-1] + 1))
    return sorted(set(fins)), True


def serie(fichier: str, **conditions) -> dict:
    """Première ligne de la liste `fichier` satisfaisant toutes les conditions (erreur sinon).

    Conditions : id=<égalité sur serie_id>, id_debut=<préfixe>, id_motif=<regex>, lib_motif=<regex
    sur libelle>, det_motif=<regex sur details>, unite_motif=<regex sur unite>."""
    d = table(fichier)
    if d.empty:
        raise LookupError(f"liste absente : {fichier}")
    m = pd.Series(True, index=d.index)
    for k, v in conditions.items():
        col = {"id": "serie_id", "id_debut": "serie_id", "id_motif": "serie_id", "lib_motif": "libelle",
               "det_motif": "details", "unite_motif": "unite"}[k]
        if k == "id":
            m &= d[col] == v
        elif k == "id_debut":
            m &= d[col].str.startswith(v)
        else:
            m &= d[col].str.contains(v, regex=True)
    x = d[m]
    if x.empty:
        raise LookupError(f"série introuvable dans {fichier} : {conditions}")
    r = x.iloc[0]
    n = int(r.n_periodes or 0)
    ans, etiquettes = annees_de(r.periodes, n)
    return {"annees": ans, "etiquettes": etiquettes, "n": n, "n_distinctes": int(r.n_valeurs_distinctes or 0),
            "derniere_valeur": r.derniere_valeur, "unite_source": r.unite, "libelle_source": r.libelle,
            "serie_id": r.serie_id, "details": r.details, "preuve": f"docs/sources/series/{fichier}.csv"}


def serie_banque_mondiale_phase1(code: str) -> dict:
    """Extrait JSON de phase 1 (docs/sources/verif_acces/extraits/banque_mondiale__<code>.txt)."""
    nom = "banque_mondiale__" + re.sub(r"[^a-z0-9_-]+", "_", code.lower()) + ".txt"
    texte = (EXTRAITS / nom).read_text(encoding="utf-8")
    donnees = json.loads(texte[texte.index("["):])
    obs = {int(o["date"]): o["value"] for o in donnees[1] if o.get("value") is not None}
    if not obs:
        raise LookupError(f"aucune valeur : {code}")
    ans = sorted(obs)
    return {"annees": ans, "etiquettes": False, "n": len(ans), "n_distinctes": len(set(obs.values())),
            "derniere_valeur": obs[ans[-1]], "unite_source": "", "libelle_source": donnees[1][0]["indicator"]["value"],
            "serie_id": code, "details": "", "preuve": f"docs/sources/verif_acces/extraits/{nom}"}


def annees_texte(fichier: str, motif: str, groupe_annee: int = 1) -> dict:
    """Années lues dans une sortie texte du robot (modes lignes/colonne/classeur) : regex à un groupe année."""
    chemin = SERIES / f"{fichier}.txt"
    ans = sorted({int(m.group(groupe_annee)) for m in re.finditer(motif, chemin.read_text(encoding="utf-8"))})
    if not ans:
        raise LookupError(f"motif absent de {fichier}.txt : {motif}")
    return {"annees": ans, "etiquettes": False, "n": len(ans), "n_distinctes": 0, "derniere_valeur": "",
            "unite_source": "", "libelle_source": "", "serie_id": "", "details": "",
            "preuve": f"docs/sources/series/{fichier}.txt"}


def annees_fichiers(motif_fichier: str, motif_ligne: str) -> dict:
    """Une année par fichier texte du robot (ex. RSF : un fichier par édition) dont une ligne contient le motif."""
    ans, preuves = [], []
    for chemin in sorted(SERIES.glob("*.txt")):
        m = re.fullmatch(motif_fichier, chemin.name)
        if m and re.search(motif_ligne, chemin.read_text(encoding="utf-8"), flags=re.M):
            ans.append(int(m.group(1)))
            preuves.append(chemin.name)
    if not ans:
        raise LookupError(f"aucun fichier {motif_fichier} ne contient {motif_ligne}")
    return {"annees": sorted(set(ans)), "etiquettes": False, "n": len(set(ans)), "n_distinctes": 0,
            "derniere_valeur": "", "unite_source": "", "libelle_source": "", "serie_id": "", "details": "",
            "preuve": f"docs/sources/series/{preuves[0]} … {preuves[-1]} ({len(preuves)} fichiers)"}


def annees_liste(annees: list[int], preuve: str, n_distinctes: int = 0) -> dict:
    """Années établies par une fonction de lecture dédiée (DREES, élections) à partir d'une sortie du robot."""
    if not annees:
        raise LookupError(f"aucune année : {preuve}")
    return {"annees": sorted(set(annees)), "etiquettes": False, "n": len(set(annees)), "n_distinctes": n_distinctes,
            "derniere_valeur": "", "unite_source": "", "libelle_source": "", "serie_id": "", "details": "",
            "preuve": preuve}


# --------------------------------------------------------------------------- dimension v1


def dimension_v1(dim_v0: str, libelle: str) -> tuple[str, str]:
    if not _REGLES:
        with CORRESPONDANCE.open(encoding="utf-8") as f:
            _REGLES.extend(sorted(csv.DictReader(f), key=lambda r: int(r["ordre"])))
    for r in _REGLES:
        if r["dimension_v0"] != dim_v0:
            continue
        if not r["motif_libelle"] or re.search(r["motif_libelle"], libelle, flags=re.I):
            return r["dimension_v1"], r["regle"]
    return "a_classer", "—"


# --------------------------------------------------------------------------- construction des lignes


def lacunes(ans: list[int]) -> list[int]:
    return [a for a in range(ans[0], ans[-1] + 1) if a not in set(ans)] if ans else []


def frequence_de(ans: list[int]) -> str:
    """annuelle (au plus deux années isolées manquantes, signalées en commentaire) | irreguliere | ponctuelle."""
    if len(ans) <= 1:
        return "ponctuelle"
    pas = {b - a for a, b in zip(ans, ans[1:])}
    return "annuelle" if max(pas) <= 2 and len(lacunes(ans)) <= 2 else "irreguliere"


def ajouter(indicateur: str, dimension: str, source: str, identifiant: str, unite: str, sens: str,
            declaratif: str, type_: str, composite: str, doublon: str, commentaire: str, s: dict,
            geo: str = "FR", niveau: str = "1", frequence: str | None = None, ventilation: str = "",
            dim_v1: str | None = None, fiabilite: str = "verifie", ref_doublon: str = "",
            points_effectifs: int | None = None) -> None:
    """Ajoute un indicateur candidat ; `s` est la preuve (dictionnaire renvoyé par serie(), annees_*()).

    `points_effectifs` remplace le nombre de points depuis 2000 quand les valeurs annuelles publiées
    répètent des moyennes pluriannuelles (cas des séries Gallup relayées par l'OCDE)."""
    assert dimension in DIMENSIONS, dimension
    assert sens in ("haut", "bas", "ambigu"), sens
    assert declaratif in ("oui", "non") and composite in ("oui", "non"), indicateur
    assert type_ in ("resultat", "moyen", "pression"), type_
    assert doublon in ("oui", "non", "partiel"), doublon
    assert fiabilite in ("verifie", "probable"), fiabilite
    assert doublon == "non" or ref_doublon or "doublon" in commentaire.lower() or commentaire, indicateur
    ans = s["annees"]
    depuis_2000 = [a for a in ans if a >= 2000]
    freq = frequence or frequence_de(depuis_2000 or ans)  # fréquence jugée sur la période utile (2000 → )
    notes = []
    if freq == "annuelle" and lacunes(depuis_2000 or ans):
        notes.append("années manquantes : " + ", ".join(map(str, lacunes(depuis_2000 or ans))))
    if s.get("etiquettes"):
        notes.append("périodes pluriannuelles (année de fin retenue)")
    if s.get("n_distinctes") and len(ans) >= 6 and s["n_distinctes"] <= len(ans) / 2:
        notes.append(f"seulement {s['n_distinctes']} valeurs distinctes sur {len(ans)} (valeurs répétées)")
    if depuis_2000 and depuis_2000[-1] < 2020:
        notes.append(f"dernière valeur {depuis_2000[-1]} (< 2020)")
    if ref_doublon:
        notes.append(f"doublon : {ref_doublon}")
    v1, regle = dimension_v1(dimension, indicateur)
    if dim_v1:
        assert dim_v1 in DIMENSIONS_V1, dim_v1
        if dim_v1 != v1:
            notes.append(f"dimension v1 forcée ({v1} par la table M03)")
        v1 = dim_v1
    elif regle not in ("—", ""):
        notes.append(f"v1 : règle {regle}")
    com = " ; ".join([commentaire.strip()] + notes if commentaire.strip() else notes)
    LIGNES.append({"indicateur": indicateur, "dimension_v0": dimension, "source": source,
                   "identifiant_ou_url": identifiant, "unite": unite, "sens": sens, "declaratif": declaratif,
                   "frequence": freq, "premiere_annee": ans[0], "derniere_annee": ans[-1],
                   "doublon_insee_eurostat": doublon, "commentaire": com, "dimension_v1_proposee": v1,
                   "type": type_, "composite": composite, "geo": geo, "ventilation": ventilation,
                   "nb_points_depuis_2000": len(depuis_2000) if points_effectifs is None else points_effectifs,
                   "niveau_source": niveau, "fiabilite": fiabilite,
                   "preuve": s["preuve"], "_ref": ref_doublon})


def controler_references(dossier: Path) -> list[str]:
    """Vérifie que chaque identifiant de doublon cité existe dans les catalogues INSEE (M01) / Eurostat (M02)."""
    insee = set(pd.read_csv(dossier / "insee_indicateurs_reperes.csv", dtype=str).serie_id)
    jeux = set(pd.read_csv(dossier / "eurostat_jeux_catalogue.csv", dtype=str).code_jeu)
    absents = []
    for l in LIGNES:
        for ref in [r.strip() for r in l["_ref"].split("+") if r.strip()]:
            org, _, code = ref.partition(" ")
            if org == "INSEE" and code not in insee or org == "Eurostat" and code not in jeux:
                absents.append(f"{l['indicateur']} → {ref}")
    return absents


def ecrire() -> None:
    vus = set()
    for l in LIGNES:
        cle = (l["indicateur"], l["source"], l["identifiant_ou_url"], l["ventilation"])
        assert cle not in vus, f"doublon de ligne : {cle}"
        vus.add(cle)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(LIGNES)
    print(f"{len(LIGNES)} indicateurs candidats écrits dans {SORTIE.relative_to(RACINE)}")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import construire_candidats as cc  # module importé (et non __main__) : celui qu'utilisent les définitions
    import candidats_definitions  # noqa: F401  (remplit cc.LIGNES via ajouter())

    cc.ecrire()
    if "--references" in sys.argv:
        absents = cc.controler_references(Path(sys.argv[sys.argv.index("--references") + 1]))
        print(f"Références de doublons absentes des catalogues : {len(absents)}")
        for a in absents:
            print("  ", a)
