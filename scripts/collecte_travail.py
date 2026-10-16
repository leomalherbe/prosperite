#!/usr/bin/env python3
"""Collecte ciblée de la dimension `travail` (décision D40) : relecture des séries Melodi.

Exécuté par GitHub Actions (workflow « Collecte », cible `collecte_travail.py`, lancée à la main :
`python scripts/actions.py lancer --branche m05-travail-corr --cible collecte_travail.py`). Le bac à
sable des sessions n'atteint pas les API : seules les fonctions de calcul (`resumer_*`, `controler_*`)
sont testées hors ligne (`tests/test_collecte_travail.py`).

Objet : onze fiches de `travail` ont leur série principale dans Melodi, qu'aucun agent n'a pu lire
(audit M06 `docs/validation/audit_travail.md` §3, TRA-3). Le script lit :

1. **Melodi** `DD_EEC_SERIES` (enquête Emploi, séries longues) mesure par mesure, `DS_SRCV_SATISFACTION`
   (mesure `TRAVSATISF`) et `DS_DERA_PRIVE_SERIES_LONGUES` (salaire net moyen en euros constants), avec
   les libellés exacts des mesures, des unités et des modalités (`/range`) et les notices (`/catalog`) ;
2. **BDM** : les séries trimestrielles de même concept (valeurs de contrôle de l'audit) ;
3. **Eurostat** : les séries que l'audit n'a pas pu relire ou que la correction ajoute (France seule) ;
4. **Assurance maladie** (data.ameli.fr) : décès au travail par secteur et sinistralité (dénominateur).

Sorties (dossier `docs/sources/series/`, commitées par le robot) :
- `melodi_travail_<fiche>.csv` : série(s) principale(s) de chaque fiche, 2000-2025, avec libellés ;
- `melodi_travail_dd_eec_series.csv.gz` : toutes les observations 2000+ de `DD_EEC_SERIES` ;
- `melodi_travail_libelles.csv`, `melodi_travail_notices.txt` : libellés et notices des jeux ;
- `melodi_travail_controles.csv` : lecture taux ou répartition (total, somme des sexes, des âges),
  codes `EMPSTA` par mesure, comparaison aux moyennes annuelles BDM ;
- `bdm_travail_<idbank>.csv` ; `eurostat_travail_<code>.csv` ;
- `cnam_ameli__deces_naf_brut.csv.gz`, `cnam_ameli__sinistralite_naf1_brut.csv.gz`, schémas JSON.

Chaque bloc est indépendant : un échec est journalisé, les autres blocs continuent, le code de sortie
est non nul si au moins un bloc a échoué (le workflow commite tout de même les sorties partielles).
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import sys
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

SORTIES = RACINE / "docs" / "sources" / "series"
ANNEE_MIN, ANNEE_MAX = 2000, 2025

# --------------------------------------------------------------------------------------
# Séries principales des onze fiches (identifiants des fiches à la fusion de l'audit, PR #24)
# --------------------------------------------------------------------------------------

EEC = "DD_EEC_SERIES"
_BASE = {"COMPOHALO": "_T", "EDUC": "_T", "EMPFORM": "_T", "PCS": "_T", "SEX": "_T", "UNDEREMP": "_T",
         "UNEMPDUR": "_T", "WKTIME": "_T"}


def _eec(**dims: str) -> dict[str, str]:
    return {**_BASE, **dims}


#: fiche → liste de (rôle, jeu, dimensions de la série)
FICHES: dict[str, list[tuple[str, str, dict[str, str]]]] = {
    "taux_emploi": [("principale", EEC, _eec(AGE="Y15T64", EEC_MEASURE="EMPRATE", EMPSTA="1", UNIT_MEASURE="PT"))],
    "taux_chomage": [("principale", EEC, _eec(AGE="_T", EEC_MEASURE="UNEMPRATE", EMPSTA="2", UNIT_MEASURE="PT"))],
    "taux_activite": [("principale", EEC, _eec(AGE="Y15T64", EEC_MEASURE="ACTRATE", EMPSTA="1T2", UNIT_MEASURE="PT"))],
    "part_temps_partiel": [("principale", EEC, _eec(AGE="_T", EEC_MEASURE="PT_WKTIME_IN_EMP_BY_SEX_AGE", EMPSTA="1",
                                                    UNIT_MEASURE="PT", WKTIME="PT"))],
    "taux_sous_emploi": [("principale", EEC, _eec(AGE="_T", EEC_MEASURE="PT_UNDEREMP_SEX_AGE_IN_EMP", EMPSTA="1", UNIT_MEASURE="PT"))],
    "neet": [("principale", EEC, _eec(AGE="Y15T29", EEC_MEASURE="PT_SEX_AGE_IN_NEET", EMPSTA="3", UNIT_MEASURE="PT")),
             ("nombre", EEC, _eec(AGE="Y15T29", EEC_MEASURE="NEET", EMPSTA="3", UNIT_MEASURE="PS"))],
    "halo_chomage": [("principale", EEC, _eec(AGE="Y_GE15", EEC_MEASURE="PT_SEX_AGE_IN_HALO", EMPSTA="3", UNIT_MEASURE="PT")),
                     ("nombre", EEC, _eec(AGE="Y_GE15", EEC_MEASURE="HALO", EMPSTA="3", UNIT_MEASURE="PS"))],
    "part_emploi_temporaire": [
        ("composante CDD", EEC, _eec(AGE="_T", EEC_MEASURE="PT_EMPFORM_IN_EMP_BY_SEX_AGE", EMPFORM="22", EMPSTA="1", UNIT_MEASURE="PT")),
        ("composante intérim", EEC, _eec(AGE="_T", EEC_MEASURE="PT_EMPFORM_IN_EMP_BY_SEX_AGE", EMPFORM="26", EMPSTA="1", UNIT_MEASURE="PT"))],
    "taux_chomage_longue_duree": [
        ("composante chômeurs depuis un an ou plus", EEC, _eec(AGE="_T", EEC_MEASURE="UNEMP", EMPSTA="2", UNEMPDUR="LT", UNIT_MEASURE="PS")),
        ("composante population active", EEC, _eec(AGE="_T", EEC_MEASURE="ACTPOP", EMPSTA="1T2", UNIT_MEASURE="PS"))],
    "satisfaction_travail": [("principale", "DS_SRCV_SATISFACTION", {
        "AGE": "Y_GE16", "DECILE_NIVVIE": "_T", "EDUC": "_T", "EMPSTA_ENQ": "_T", "FREQ": "A", "GEO": "FRANCE-FM", "HLTH_GALI": "_T",
        "HLTH_SPH": "_T", "NATIONALITY_TYPE": "_T", "NB_DIFF": "_T", "PCS": "_Z", "SATISFNOTE": "_T", "SEX": "_T",
        "SRCV_MEASURE": "TRAVSATISF", "TPH": "_T", "TSH": "_T"})],
    "salaire_net_moyen_reel": [("principale", "DS_DERA_PRIVE_SERIES_LONGUES", {
        "ACTIVITY": "_T", "AGE": "_T", "DERA_MEASURE": "SALAIRE_NET_EQTP_MENSUEL_MOYEN_EUROS_CONSTANTS", "FREQ": "A",
        "GEO": "FRANCE-F", "NUMBER_EMPL": "_T", "PCS_ESE": "_T", "QUANTILE": "_T", "SEX": "_T", "UNIT_MEASURE": "XDC", "WKTIME": "_T"})],
}

#: Extractions Melodi hors DD_EEC_SERIES (jeu → filtre de l'extraction)
EXTRACTIONS_AUTRES = {
    "DS_SRCV_SATISFACTION": {"SRCV_MEASURE": "TRAVSATISF"},
    "DS_DERA_PRIVE_SERIES_LONGUES": {"DERA_MEASURE": "SALAIRE_NET_EQTP_MENSUEL_MOYEN_EUROS_CONSTANTS"},
}

#: Mesures de DD_EEC_SERIES lues une à une (toutes celles de l'inventaire du 14/10/2026)
MESURES_EEC = [
    "EMPRATE", "UNEMPRATE", "ACTRATE", "EMP", "UNEMP", "ACTPOP", "HALO", "PT_SEX_AGE_IN_HALO", "NEET", "PT_SEX_AGE_IN_NEET",
    "UNDEREMP", "PT_UNDEREMP_SEX_AGE_IN_EMP", "PT_WKTIME_IN_EMP_BY_SEX_AGE", "PT_EMPFORM_IN_EMP_BY_SEX_AGE",
    "PT_UNEMPDUR_IN_UNEMP", "EMPRATE_EDUC", "UNEMPRATE_EDUC", "EMP_EDUC", "UNEMP_EDUC", "PT_EDUC_IN_EMP_BY_SEX_AGE",
    "PT_PCS_IN_EMP_BY_SEX_AGE", "POP_EDUC", "PT_EDUC_IN_POP_BY_SEX_AGE",
]

#: Séries BDM de contrôle (idbank → fiche, libellé court)
BDM = {
    "011818639": ("neet", "NEET 15-29 ans, France entière, CVS"),
    "011818623": ("halo_chomage", "halo 15-64 ans, part dans la population, France entière, CVS"),
    "011818670": ("taux_sous_emploi", "taux de sous-emploi, France entière, CVS"),
    "011818581": ("taux_chomage_longue_duree", "taux de chômage de longue durée, France entière, CVS"),
    "011818676": ("taux_emploi", "taux d'emploi 15-64 ans, France entière, CVS"),
    "010596081": ("taux_emploi", "taux d'emploi (IRN 1), France hors Mayotte, annuel"),
    "011818543": ("taux_chomage", "taux de chômage BIT, France entière, CVS"),
    "001787711": ("taux_chomage", "taux de chômage BIT, moyenne annuelle, France métropolitaine"),
    "011818737": ("taux_activite", "taux d'activité 15-64 ans, France entière, CVS"),
    "011818675": ("part_temps_partiel", "part du temps partiel dans l'emploi, France entière, CVS"),
    "011818697": ("part_emploi_temporaire", "taux d'emploi en CDD ou intérim (part de la population de 15 à 64 ans), CVS"),
    "011818634": ("sous_utilisation_main_oeuvre", "personnes contraintes sur leur offre de travail, 15-64 ans, CVS"),
    "010752333": ("salaire_net_moyen_reel", "salaire net annuel moyen en EQTP, secteur privé, euros courants"),
}

#: Contrôles BDM : (fiche, contrôle, série Melodi ou calcul, idbank BDM)
CONTROLES_BDM = [
    ("neet", "part NEET 15-29 ans (Melodi PT) vs BDM", "neet_pt", "011818639"),
    ("neet", "NEET 15-29 ans recalculé (nombre / population 15-29) vs BDM", "neet_calc", "011818639"),
    ("halo_chomage", "halo 15 ans ou plus (Melodi PT) vs BDM 15-64 ans", "halo_pt", "011818623"),
    ("halo_chomage", "halo 15-64 ans recalculé (nombre / population 15-64) vs BDM", "halo_calc", "011818623"),
    ("taux_sous_emploi", "sous-emploi (Melodi PT) vs BDM", "sous_emploi_pt", "011818670"),
    ("taux_sous_emploi", "sous-emploi recalculé (nombre / emploi) vs BDM", "sous_emploi_calc", "011818670"),
    ("taux_chomage_longue_duree", "chômage de longue durée recalculé vs BDM", "cld_calc", "011818581"),
    ("taux_emploi", "taux d'emploi 15-64 ans (Melodi) vs BDM trimestrielle", "emploi", "011818676"),
    ("taux_emploi", "taux d'emploi 15-64 ans (Melodi) vs IRN 1", "emploi", "010596081"),
    ("taux_chomage", "taux de chômage (Melodi) vs BDM trimestrielle", "chomage", "011818543"),
    ("taux_chomage", "taux de chômage (Melodi) vs moyenne annuelle métropole", "chomage", "001787711"),
    ("taux_activite", "taux d'activité 15-64 ans (Melodi) vs BDM", "activite", "011818737"),
    ("part_temps_partiel", "part du temps partiel (Melodi) vs BDM", "temps_partiel", "011818675"),
    ("part_emploi_temporaire", "(CDD + intérim) x taux d'emploi 15-64 ans / 100 vs taux d'emploi en CDD ou intérim (approché)",
     "temporaire_x_emploi", "011818697"),
]

#: Jeux Eurostat lus pour la France (code → filtres complémentaires)
EUROSTAT = {
    "lfsi_emp_a": {"age": "Y20-64", "indic_em": "EMP_LFS", "sex": "T", "unit": "PC_POP"},
    "sdg_08_30": {"sex": "T"},
    "sdg_08_20": {"sex": "T"},
    "lfsi_neet_a": {"sex": "T", "age": "Y15-29"},
    "hsw_exp1": {},
    "hsw_exp2": {},
    "hsw_pb1": {},
    "une_ltu_a": {"sex": "T"},
    "sdg_08_40": {},
    "lfsa_ewhuis": {"sex": "T"},
    "hsw_n2_02": {},
    "sdg_08_60": {},
    "lfsa_qoe_4ax1r2": {"sex": "T"},
    "lfsa_qoe_3a2": {"sex": "T"},
    "lfsa_eetpgar": {"sex": "T"},
    "lfsa_eppgai": {"sex": "T"},
    "lfsi_long_a": {"sex": "T"},
    "lfsa_ugadra": {"sex": "T"},
}

AMELI = {
    "deces_naf": "deces-par-secteur-d-activite-naf-1-et-naf-5",
    "sinistralite_naf1": "sinistralite-par-secteur-d-activite-concerne-naf-1",
}
URL_AMELI = "https://data.ameli.fr/api/explore/v2.1/catalog/datasets/{jeu}"


def log(message: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {message}", flush=True)


def ecrire_csv(chemin: Path, colonnes: list[str], lignes: Iterable[dict], compresser: bool = False) -> int:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    ouvrir = (lambda p: gzip.open(p, "wt", encoding="utf-8", newline="")) if compresser else (lambda p: open(p, "w", encoding="utf-8", newline=""))
    n = 0
    with ouvrir(chemin) as f:
        w = csv.DictWriter(f, fieldnames=colonnes, extrasaction="ignore")
        w.writeheader()
        for ligne in lignes:
            w.writerow(ligne)
            n += 1
    return n


# --------------------------------------------------------------------------------------
# Fonctions de calcul (testées hors ligne)
# --------------------------------------------------------------------------------------

def annee_de(periode: str) -> Optional[int]:
    try:
        return int(str(periode)[:4])
    except (TypeError, ValueError):
        return None


def cle_dims(dims: dict[str, str]) -> tuple:
    """Clé hachable d'une série (dimensions hors TIME_PERIOD)."""
    return tuple(sorted((k, str(v)) for k, v in dims.items() if k != "TIME_PERIOD"))


class Observations:
    """Observations Melodi indexées par série et par année : {cle_dims: {annee: (valeur, statut)}}."""

    def __init__(self) -> None:
        self.series: dict[tuple, dict[int, tuple[Optional[float], str]]] = defaultdict(dict)

    def ajouter(self, dims: dict[str, str], periode: str, valeur: Optional[float], statut: str = "") -> None:
        a = annee_de(periode)
        if a is None:
            return
        self.series[cle_dims(dims)][a] = (valeur, statut)

    def valeur(self, dims: dict[str, str], annee: int) -> Optional[float]:
        v = self.series.get(cle_dims(dims), {}).get(annee)
        return v[0] if v else None

    def annees(self, dims: dict[str, str]) -> list[int]:
        return sorted(a for a, (v, _) in self.series.get(cle_dims(dims), {}).items() if v is not None)


def moyennes_annuelles(lignes: Iterable[tuple[str, Optional[float]]]) -> dict[int, tuple[float, int]]:
    """(période, valeur) trimestrielles ou annuelles → {année: (moyenne, nombre de valeurs)}."""
    par_annee: dict[int, list[float]] = defaultdict(list)
    for periode, valeur in lignes:
        a = annee_de(periode)
        if a is not None and valeur is not None:
            par_annee[a].append(valeur)
    return {a: (sum(v) / len(v), len(v)) for a, v in par_annee.items()}


def controler_repartition(obs: Observations, dims: dict[str, str], annee: int, ages: list[str]) -> dict[str, Any]:
    """Lecture taux ou répartition d'une mesure `PT_*` pour une année.

    - total : valeur de la série (sexes réunis) ;
    - somme des sexes : F + M ; si elle vaut le total (≈ 100), la mesure est une répartition par sexe ;
      si le total est compris entre F et M, c'est un taux (moyenne pondérée des taux par sexe) ;
    - somme des âges : somme des valeurs des classes d'âge `ages` (sexes réunis), ≈ 100 si répartition.
    """
    total = obs.valeur(dims, annee)
    f = obs.valeur({**dims, "SEX": "F"}, annee)
    m = obs.valeur({**dims, "SEX": "M"}, annee)
    valeurs_ages = [obs.valeur({**dims, "AGE": a}, annee) for a in ages]
    somme_ages = sum(v for v in valeurs_ages if v is not None) if any(v is not None for v in valeurs_ages) else None
    lecture = "indéterminée"
    if total is not None and f is not None and m is not None:
        somme = f + m
        if abs(somme - 100) < 1.0 and abs(total - 100) < 1.0:
            lecture = "répartition (F + M = total = 100)"
        elif abs(somme - 100) < 1.0:
            lecture = "répartition par sexe (F + M = 100)"
        elif min(f, m) - 0.05 <= total <= max(f, m) + 0.05:
            lecture = "taux (total compris entre les taux des femmes et des hommes)"
        else:
            lecture = "ni taux ni répartition par sexe : à examiner"
    return {"total": total, "femmes": f, "hommes": m, "somme_sexes": (f + m) if f is not None and m is not None else None,
            "somme_ages": somme_ages, "ages": ";".join(ages), "lecture": lecture}


def population_par_age(obs: Observations, ages: list[str], annee: int) -> Optional[float]:
    """Population d'une classe d'âge = Σ actifs / taux d'activité × 100 (mesures ACTPOP et ACTRATE)."""
    total = 0.0
    for a in ages:
        actifs = obs.valeur(_eec(AGE=a, EEC_MEASURE="ACTPOP", EMPSTA="1T2", UNIT_MEASURE="PS"), annee)
        taux = obs.valeur(_eec(AGE=a, EEC_MEASURE="ACTRATE", EMPSTA="1T2", UNIT_MEASURE="PT"), annee)
        if actifs is None or not taux:
            return None
        total += actifs / taux * 100
    return total


def calculer(obs: Observations, nom: str, annee: int) -> Optional[float]:
    """Valeurs Melodi comparées à la BDM (séries lues ou recalculées sur les nombres)."""
    v = obs.valeur
    if nom == "neet_pt":
        return v(FICHES["neet"][0][2], annee)
    if nom == "neet_calc":
        nombre = v(FICHES["neet"][1][2], annee)
        pop = population_par_age(obs, ["Y15T19", "Y20T24", "Y25T29"], annee)
        return nombre / pop * 100 if nombre is not None and pop else None
    if nom == "halo_pt":
        return v(FICHES["halo_chomage"][0][2], annee)
    if nom == "halo_calc":
        nombres = [v(_eec(AGE=a, EEC_MEASURE="HALO", EMPSTA="3", UNIT_MEASURE="PS"), annee) for a in ("Y15T24", "Y25T49", "Y50T64")]
        pop = population_par_age(obs, ["Y15T64"], annee)
        return sum(nombres) / pop * 100 if None not in nombres and pop else None
    if nom == "sous_emploi_pt":
        return v(FICHES["taux_sous_emploi"][0][2], annee)
    if nom == "sous_emploi_calc":
        sous = v(_eec(AGE="_T", EEC_MEASURE="UNDEREMP", EMPSTA="1", UNIT_MEASURE="PS"), annee)
        emploi = v(_eec(AGE="_T", EEC_MEASURE="EMP", EMPSTA="1", UNIT_MEASURE="PS"), annee)
        return sous / emploi * 100 if sous is not None and emploi else None
    if nom == "cld_calc":
        a, b = (v(d, annee) for _, _, d in FICHES["taux_chomage_longue_duree"])
        return a / b * 100 if a is not None and b else None
    if nom == "emploi":
        return v(FICHES["taux_emploi"][0][2], annee)
    if nom == "chomage":
        return v(FICHES["taux_chomage"][0][2], annee)
    if nom == "activite":
        return v(FICHES["taux_activite"][0][2], annee)
    if nom == "temps_partiel":
        return v(FICHES["part_temps_partiel"][0][2], annee)
    if nom == "temporaire":
        a, b = (v(d, annee) for _, _, d in FICHES["part_emploi_temporaire"])
        return a + b if a is not None and b is not None else None
    if nom == "temporaire_x_emploi":
        t, e = calculer(obs, "temporaire", annee), calculer(obs, "emploi", annee)
        return t * e / 100 if t is not None and e is not None else None
    raise KeyError(nom)


# --------------------------------------------------------------------------------------
# Blocs de collecte (réseau : GitHub Actions seulement)
# --------------------------------------------------------------------------------------

def libelles_series(jeu: str, dims: dict[str, str], plage: dict) -> dict[str, str]:
    def lib(concept: str, code: str) -> str:
        c = plage.get(concept)
        return (c.valeurs.get(code, "") if c else "") or ""
    mesure = dims.get("EEC_MEASURE") or dims.get("SRCV_MEASURE") or dims.get("DERA_MEASURE") or ""
    concept_mesure = "EEC_MEASURE" if "EEC_MEASURE" in dims else ("SRCV_MEASURE" if "SRCV_MEASURE" in dims else "DERA_MEASURE")
    autres = [f"{k}={c} ({lib(k, c)})" for k, c in sorted(dims.items()) if k not in (concept_mesure, "UNIT_MEASURE")]
    return {"mesure_code": mesure, "mesure_libelle": lib(concept_mesure, mesure), "unite_code": dims.get("UNIT_MEASURE", ""),
            "unite_libelle": lib("UNIT_MEASURE", dims.get("UNIT_MEASURE", "")), "modalites": " ; ".join(autres)}


def bloc_melodi(etat: dict) -> None:
    from src.sources import insee_melodi as mel

    client = mel.client_melodi(journal=log)
    plages: dict[str, dict] = {}
    notices: list[str] = []
    libelles: list[dict] = []
    for jeu in [EEC, *EXTRACTIONS_AUTRES]:
        notice, plage = mel.decrire_jeu(jeu, client)
        plages[jeu] = plage
        if notice:
            notices.append(f"===== {jeu} =====\nTitre : {notice.titre}\nSous-titre : {notice.sous_titre}\nPériodicité : {notice.periodicite}\n"
                           f"Couverture : {notice.debut} - {notice.fin} ; spatial : {notice.spatial} ; niveaux : {';'.join(notice.niveaux_geo)}\n"
                           f"Mise à jour : {notice.modifie}\nDescription :\n{notice.description}\n")
        for code_concept, concept in plage.items():
            for code, lib in concept.valeurs.items():
                libelles.append({"jeu": jeu, "concept": code_concept, "concept_libelle": concept.libelle, "code": code, "libelle": lib})
        log(f"Melodi {jeu} : notice {'lue' if notice else 'absente'}, {len(plage)} concepts")
    (SORTIES / "melodi_travail_notices.txt").write_text("\n".join(notices), encoding="utf-8")
    ecrire_csv(SORTIES / "melodi_travail_libelles.csv", ["jeu", "concept", "concept_libelle", "code", "libelle"], libelles)

    obs_par_jeu: dict[str, Observations] = defaultdict(Observations)
    brutes: list[dict] = []
    extractions = [(EEC, {"EEC_MEASURE": m}) for m in MESURES_EEC] + list(EXTRACTIONS_AUTRES.items())
    for jeu, filtre in extractions:
        try:
            n = 0
            for o in mel.iterer_observations(jeu, filtre, client, total=mel.compter(jeu, filtre, client)):
                dims = {k: (mel.normaliser_geo(v) if k == "GEO" else str(v)) for k, v in (o.get("dimensions") or {}).items()}
                periode = dims.pop("TIME_PERIOD", "")
                _, valeur = mel.mesure_et_valeur(o)
                attributs = o.get("attributes") or {}
                statut = str(attributs.get("OBS_STATUS") or "")
                obs_par_jeu[jeu].ajouter(dims, periode, valeur, statut)
                a = annee_de(periode)
                if a is not None and a >= ANNEE_MIN:
                    brutes.append({"jeu": jeu, "serie_id": mel.identifiant_serie(jeu, dims), "periode": periode, "valeur": valeur,
                                   "statut": statut, "attributs": json.dumps(attributs, ensure_ascii=False, sort_keys=True)})
                n += 1
            log(f"Melodi {jeu} {filtre} : {n} observations")
        except Exception as exc:  # une mesure absente n'arrête pas la collecte
            etat["erreurs"].append(f"Melodi {jeu} {filtre} : {type(exc).__name__} {str(exc)[:300]}")
            log(f"  ERREUR {etat['erreurs'][-1]}")
    ecrire_csv(SORTIES / "melodi_travail_dd_eec_series.csv.gz", ["jeu", "serie_id", "periode", "valeur", "statut", "attributs"],
               [b for b in brutes if b["jeu"] == EEC], compresser=True)

    # Une sortie par fiche
    for fiche, series in FICHES.items():
        lignes = []
        for role, jeu, dims in series:
            libs = libelles_series(jeu, dims, plages.get(jeu, {}))
            sid = mel.identifiant_serie(jeu, dims)
            donnees = obs_par_jeu[jeu].series.get(cle_dims(dims), {})
            if not donnees:
                etat["erreurs"].append(f"{fiche} : série {sid} absente de l'extraction")
            for a in sorted(donnees):
                if ANNEE_MIN <= a <= ANNEE_MAX:
                    valeur, statut = donnees[a]
                    lignes.append({"fiche": fiche, "role": role, "jeu": jeu, "serie_id": sid, **libs, "annee": a,
                                   "valeur": valeur, "statut": statut})
        n = ecrire_csv(SORTIES / f"melodi_travail_{fiche}.csv",
                       ["fiche", "role", "jeu", "serie_id", "mesure_code", "mesure_libelle", "unite_code", "unite_libelle", "modalites",
                        "annee", "valeur", "statut"], lignes)
        log(f"Sortie {fiche} : {n} lignes")
    etat["melodi"] = obs_par_jeu
    etat["plages"] = plages


def bloc_bdm(etat: dict) -> None:
    from src.sources import insee_bdm as bdm
    from src.sources.insee_http import ClientHttp

    client = ClientHttp(intervalles={"bdm.insee.fr": 0.6}, journal=log)
    erreurs: list[str] = []
    series = bdm.obtenir_series(list(BDM), client, erreurs=erreurs)
    etat["erreurs"] += erreurs
    etat["bdm"] = {}
    for s in series:
        lignes = bdm.series_en_lignes([s])
        etat["bdm"][s.idbank] = lignes
        titre = s.attributs.get("TITLE_FR", "")
        ecrire_csv(SORTIES / f"bdm_travail_{s.idbank}.csv", ["idbank", "titre", "zone", "periode", "valeur", "statut"],
                   ({"idbank": s.idbank, "titre": titre, "zone": l.geo, "periode": l.periode, "valeur": l.valeur, "statut": l.statut} for l in lignes))
        log(f"BDM {s.idbank} : {len(lignes)} observations ({titre[:90]})")


def bloc_controles(etat: dict) -> None:
    obs: Optional[Observations] = (etat.get("melodi") or {}).get(EEC)
    if obs is None:
        raise RuntimeError("pas d'observations DD_EEC_SERIES : contrôles impossibles")
    lignes: list[dict] = []
    # 1. taux ou répartition des mesures PT_*
    repartitions = [
        ("neet", FICHES["neet"][0][2], ["Y15T19", "Y20T24", "Y25T29"]),
        ("halo_chomage", FICHES["halo_chomage"][0][2], ["Y15T24", "Y25T49", "Y50T64", "Y_GE65"]),
        ("taux_sous_emploi", FICHES["taux_sous_emploi"][0][2], ["Y15T24", "Y25T49", "Y_GE50"]),
        ("part_temps_partiel", FICHES["part_temps_partiel"][0][2], ["Y15T24", "Y25T49", "Y_GE50"]),
        ("part_emploi_temporaire", FICHES["part_emploi_temporaire"][0][2], ["Y15T24", "Y25T49", "Y_GE50"]),
    ]
    for fiche, dims, ages in repartitions:
        for annee in (2003, 2010, 2014, 2020, 2024, 2025):
            r = controler_repartition(obs, dims, annee, ages)
            lignes.append({"fiche": fiche, "controle": "taux ou répartition", "annee": annee, "valeur_melodi": r["total"],
                           "detail": f"F={r['femmes']} ; M={r['hommes']} ; F+M={r['somme_sexes']} ; somme des âges ({r['ages']})={r['somme_ages']}",
                           "lecture": r["lecture"]})
    # 2. codes EMPSTA présents par mesure
    par_mesure: dict[str, set[str]] = defaultdict(set)
    for cle in obs.series:
        d = dict(cle)
        par_mesure[d.get("EEC_MEASURE", "")].add(d.get("EMPSTA", ""))
    for mesure in sorted(par_mesure):
        lignes.append({"fiche": "", "controle": f"codes EMPSTA de la mesure {mesure}", "annee": "", "valeur_melodi": "",
                       "detail": ";".join(sorted(par_mesure[mesure])), "lecture": ""})
    # 3. comparaison aux moyennes annuelles BDM
    bdm_series = etat.get("bdm") or {}
    for fiche, controle, nom, idbank in CONTROLES_BDM:
        moyennes = moyennes_annuelles((l.periode, l.valeur) for l in bdm_series.get(idbank, []))
        for annee in range(ANNEE_MIN, ANNEE_MAX + 1):
            m = calculer(obs, nom, annee)
            b = moyennes.get(annee)
            if m is None and b is None:
                continue
            lignes.append({"fiche": fiche, "controle": controle, "annee": annee, "valeur_melodi": None if m is None else round(m, 3),
                           "valeur_bdm": None if b is None else round(b[0], 3), "idbank_bdm": idbank, "n_valeurs_bdm": "" if b is None else b[1],
                           "ecart": None if (m is None or b is None) else round(m - b[0], 3), "detail": "", "lecture": ""})
    ecrire_csv(SORTIES / "melodi_travail_controles.csv",
               ["fiche", "controle", "annee", "valeur_melodi", "valeur_bdm", "idbank_bdm", "n_valeurs_bdm", "ecart", "detail", "lecture"], lignes)
    log(f"Contrôles : {len(lignes)} lignes")


def bloc_eurostat(etat: dict) -> None:
    from src.sources import eurostat as es

    client = es.ClientEurostat(journal=log)
    for code, filtres in EUROSTAT.items():
        try:
            jeu = es.obtenir_jeu(code, {"geo": "FR", **filtres}, lang="fr", client=client)
        except Exception as exc:
            etat["erreurs"].append(f"Eurostat {code} : {type(exc).__name__} {str(exc)[:200]}")
            log(f"  ERREUR {etat['erreurs'][-1]}")
            continue
        dims = jeu.dimensions_hors_temps
        lignes = []
        for codes, periode, valeur, drapeau in jeu.observations:
            modalites = " ; ".join(f"{d.id}={c} ({d.libelles.get(c, c)})" for d, c in zip(dims, codes))
            lignes.append({"code": code, "serie_id": jeu.serie_id(codes), "modalites": modalites, "periode": periode,
                           "valeur": valeur, "drapeau": drapeau})
        lignes.sort(key=lambda l: (l["serie_id"], l["periode"]))
        ecrire_csv(SORTIES / f"eurostat_travail_{code}.csv", ["code", "serie_id", "modalites", "periode", "valeur", "drapeau"], lignes)
        log(f"Eurostat {code} : {len(lignes)} observations ({jeu.libelle[:80]}, mise à jour {jeu.mise_a_jour})")


def bloc_ameli(etat: dict) -> None:
    from src.sources.insee_http import ClientHttp

    client = ClientHttp(intervalles={"data.ameli.fr": 1.0}, journal=log)
    for nom, jeu in AMELI.items():
        url = URL_AMELI.format(jeu=jeu)
        notice = client.get(url)
        if notice.ok:
            (SORTIES / f"cnam_ameli__{nom}_schema.json").write_bytes(notice.contenu)
        else:
            etat["erreurs"].append(f"Ameli {jeu} (notice) : HTTP {notice.statut} {notice.extrait(150)}")
        rep = client.get(f"{url}/exports/csv", params={"delimiter": ";"})
        if not rep.ok:
            etat["erreurs"].append(f"Ameli {jeu} (export) : HTTP {rep.statut} {rep.extrait(150)}")
            log(f"  ERREUR {etat['erreurs'][-1]}")
            continue
        (SORTIES / f"cnam_ameli__{nom}_brut.csv.gz").write_bytes(gzip.compress(rep.contenu))
        texte = rep.contenu.decode("utf-8-sig", errors="replace")
        lecteur = csv.reader(io.StringIO(texte), delimiter=";")
        entete = next(lecteur, [])
        n = sum(1 for _ in lecteur)
        log(f"Ameli {jeu} : {n} lignes, colonnes {entete}")


def main() -> int:
    SORTIES.mkdir(parents=True, exist_ok=True)
    etat: dict[str, Any] = {"erreurs": []}
    blocs = [("melodi", bloc_melodi), ("bdm", bloc_bdm), ("controles", bloc_controles), ("eurostat", bloc_eurostat), ("ameli", bloc_ameli)]
    echecs = []
    for nom, bloc in blocs:
        log(f"===== bloc {nom} =====")
        try:
            bloc(etat)
        except Exception as exc:
            echecs.append(nom)
            etat["erreurs"].append(f"bloc {nom} : {type(exc).__name__} {exc}")
            traceback.print_exc()
    bilan = {"date": datetime.now(timezone.utc).isoformat(timespec="seconds"), "blocs_en_echec": echecs, "erreurs": etat["erreurs"]}
    (SORTIES / "melodi_travail_bilan.json").write_text(json.dumps(bilan, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"Bilan : {len(echecs)} bloc(s) en échec, {len(etat['erreurs'])} erreur(s)")
    for e in etat["erreurs"]:
        log(f"  - {e}")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
