"""Long-list commune des indicateurs candidats (gel 2, charte §3.6 ; fiche M05, « Entrées »).

Le module réunit les catalogues de séries candidates en une seule table, la
rattache à la grille v1 figée (`indicateurs/dimensions.yaml`), applique le filtre
d'éligibilité mécanique de la charte (§3.4, avec les dérogations D16 à D19) et
repère les lignes qui décrivent un même concept. **Aucune ligne n'est supprimée** :
chaque exclusion est motivée, chaque doublon pointe vers la ligne de référence de
son concept. Le jugement (familles, variante principale, recommandation) reste le
travail des fiches M05.

Entrées (chemins relatifs à la racine du dépôt ; `.csv` ou `.csv.gz`) :
- `catalogues/insee_bdm_catalogue.csv`, `catalogues/insee_melodi_catalogue.csv` (M01) ;
- `catalogues/eurostat_series_catalogue.csv` (M02, niveau 2) et, pour le seul repérage
  des raccordements (D16), `catalogues/eurostat_jeux_catalogue.csv` (niveau 1) ;
- `docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv` (M04) ;
- `docs/methodo/31_correspondance_v0_v1.csv` (table de rattachement v0 → v1, gel 1) ;
- `indicateurs/dimensions.yaml` (identifiants des dimensions v1).

Sorties (dans `catalogues/`) :
- `longlist_<dimension>.csv` : une par dimension v1, toutes les lignes rattachées,
  éligibles ou non ;
- `longlist_hors_grille.csv` : lignes `hors_v1`, `hors_grille` et `a_classer` ;
- `longlist_bilan.json` : chiffres par dimension, par source et par motif.
Les CSV sont écrits en clair (sorties de travail, ignorées par git) ou, avec `--compresser`,
en `.csv.gz` (exécution finale : seuls le bilan et les `.csv.gz` sont commités).

Usage :
    python -m src.pipeline.longlist --dimension toutes
    python -m src.pipeline.longlist --dimension sante     # un seul fichier, bilan à l'écran
    python -m src.pipeline.longlist --dimension toutes --compresser   # exécution finale

Mode d'emploi détaillé : `docs/methodo/32_longlist_mode_emploi.md`.
"""

from __future__ import annotations

import argparse
import gzip
import io
import json
import logging
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

VERSION = "1.0"
JOURNAL = logging.getLogger("longlist")

RACINE = Path(__file__).resolve().parents[2]
CHEMIN_TABLE = "docs/methodo/31_correspondance_v0_v1.csv"
CHEMIN_GRILLE = "indicateurs/dimensions.yaml"
CHEMIN_JEUX_EUROSTAT = "catalogues/eurostat_jeux_catalogue.csv"
DOSSIER_SORTIE = "catalogues"

ANNEE_DEBUT = 2000          # charte §2 : 2000 → aujourd'hui
ANNEE_FRAICHEUR = 2020      # charte §3.4 : dernière valeur ≥ 2020
MIN_POINTS = 10             # charte §3.4 : au moins 10 points depuis 2000

HORS_DIMENSIONS = ("hors_v1", "hors_grille", "a_classer")

# Schéma commun demandé par la fiche (ordre des colonnes de sortie, complété plus bas).
COLONNES_COMMUNES = [
    "source", "voie_acces", "serie_id", "libelle", "unite", "frequence", "geo",
    "premiere_periode", "derniere_periode", "nb_points_depuis_2000", "dimension_v0",
    "dimension_v1", "candidat", "ventilation", "declaratif", "composite", "type",
    "url_api", "url_page", "commentaire", "catalogue_origine",
]
COLONNES_SORTIE = [
    "ligne_id", "source", "voie_acces", "niveau_source", "serie_id", "libelle", "unite",
    "frequence", "geo", "premiere_periode", "derniere_periode", "nb_points_depuis_2000",
    "nb_annees_etendue", "dimension_v0", "dimension_v1", "regle_v1", "rattachement_note",
    "candidat", "eligible", "motif_exclusion", "note_eligibilite", "ventilation",
    "declaratif", "composite", "type", "cle_concept", "concept_id", "doublon_de",
    "doublon_de_ligne", "doublon_note", "nb_lignes_concept", "dimensions_concept",
    "url_api", "url_page", "commentaire", "catalogue_origine",
]
MOTIFS = [  # ordre d'écriture dans `motif_exclusion`
    "hors_v1", "hors_grille", "a_classer", "candidat_non", "geo_non_nationale",
    "frequence_non_agregable", "derniere_periode_avant_2020", "moins_de_10_points",
]

# Zones nationales (codes des catalogues ; D15 : gardés distincts, la fiche choisit).
GEO_NATIONALES = {
    "FR", "FX", "FE", "FM", "FR-D976", "FEHM", "FRANCE-F", "FRANCE-FM", "FRANCE-F_X_D976",
    "FM99_FR00", "FM_D99_D978", "FM_H_CORSE_2018", "FR-SPM-WF", "FE_HPBIO", "FR-UE",
}
FREQUENCES_AGREGEABLES = {
    "annuelle", "semestrielle", "trimestrielle", "bimestrielle", "mensuelle",
    "hebdomadaire", "quotidienne",
}

API_EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"


# ---------------------------------------------------------------------------
# Description des catalogues
# ---------------------------------------------------------------------------

@dataclass
class Catalogue:
    """Un catalogue source et la correspondance de ses colonnes avec le schéma commun.

    `colonnes` : colonne commune (ou interne, préfixe « _ ») → colonnes candidates du
    fichier, la première présente est prise. `attendues` : colonnes dont l'absence est
    signalée par un avertissement (les autres sont facultatives par construction,
    ex. `declaratif` n'existe pas dans les catalogues INSEE).
    """

    nom: str
    chemin: str
    prefixe: str
    rang_source: int            # INSEE 0 > Eurostat 1 > autres 2 (choix de la référence)
    voie_acces: str
    colonnes: dict[str, list[str]]
    attendues: list[str] = field(default_factory=list)


_COLONNES_INSEE = {
    "source": ["source"], "serie_id": ["serie_id"], "libelle": ["libelle"],
    "unite": ["unite"], "frequence": ["frequence"], "geo": ["geo"],
    "premiere_periode": ["premiere_periode"], "derniere_periode": ["derniere_periode"],
    "nb_points_depuis_2000": ["nb_points_depuis_2000", "nb_annees_depuis_2000"],
    "dimension_v0": ["dimension_v0"], "candidat": ["candidat"],
    "ventilation": ["ventilation"], "declaratif": ["declaratif"], "composite": ["composite"],
    "type": ["type"], "url_api": ["url_api"], "url_page": ["url_page"],
    "commentaire": ["commentaire"], "_v1_propose": ["dimension_v1_proposee", "dimension_v1"],
    "_agregable": ["agregable"], "_geo_libelle": ["geo_libelle"],
}
_ATTENDUES_INSEE = [
    "source", "serie_id", "libelle", "unite", "frequence", "geo", "premiere_periode",
    "derniere_periode", "nb_points_depuis_2000", "dimension_v0", "candidat", "ventilation",
    "url_api", "commentaire", "_agregable",
]

CATALOGUES = [
    Catalogue("insee_bdm", "catalogues/insee_bdm_catalogue.csv", "bdm", 0, "insee_bdm_sdmx",
              _COLONNES_INSEE, _ATTENDUES_INSEE),
    Catalogue("insee_melodi", "catalogues/insee_melodi_catalogue.csv", "melodi", 0, "insee_melodi_api",
              _COLONNES_INSEE, _ATTENDUES_INSEE),
    Catalogue(
        "eurostat_series", "catalogues/eurostat_series_catalogue.csv", "estat", 1,
        "eurostat_api_statistics",
        {
            "source": ["source"], "serie_id": ["serie_id"], "libelle": ["libelle"],
            "unite": ["unite"], "frequence": ["frequence"], "geo": ["geo"],
            "premiere_periode": ["premiere_periode"], "derniere_periode": ["derniere_periode"],
            "nb_points_depuis_2000": ["nb_annees", "nb_points"],
            "dimension_v0": ["dimension_v0"], "candidat": ["candidat"],
            "ventilation": ["ventilation"], "declaratif": ["declaratif"],
            "composite": ["composite"], "type": ["type"], "url_api": ["url_api"],
            "url_page": ["url_page"], "commentaire": ["commentaire"],
            "_v1_propose": ["dimension_v1_proposee", "dimension_v1"],
            "_code_jeu": ["code_jeu"], "_type_ligne": ["type_ligne"],
            "_jeu_source": ["jeu_source"], "_modalites": ["modalites_ventilation"],
        },
        ["source", "serie_id", "libelle", "unite", "frequence", "geo", "premiere_periode",
         "derniere_periode", "nb_points_depuis_2000", "dimension_v0", "candidat",
         "ventilation", "commentaire", "_code_jeu", "_type_ligne", "_jeu_source", "_modalites"],
    ),
    Catalogue(
        "autres_sources_m04", "docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv",
        "m04", 2, "",
        {
            "source": ["source"], "serie_id": ["identifiant_ou_url", "serie_id"],
            "libelle": ["indicateur", "libelle"], "unite": ["unite"],
            "frequence": ["frequence"], "geo": ["geo"],
            "premiere_periode": ["premiere_annee", "premiere_periode"],
            "derniere_periode": ["derniere_annee", "derniere_periode"],
            "nb_points_depuis_2000": ["nb_points_depuis_2000"],
            "dimension_v0": ["dimension_v0"], "candidat": ["candidat"],
            "ventilation": ["ventilation"], "declaratif": ["declaratif"],
            "composite": ["composite"], "type": ["type"], "url_api": ["url_api"],
            "url_page": ["url_page"], "commentaire": ["commentaire"],
            "_v1_propose": ["dimension_v1_proposee", "dimension_v1"],
            "_doublon_m04": ["doublon_insee_eurostat"], "_niveau_source": ["niveau_source"],
            "_preuve": ["preuve"], "_sens": ["sens"],
        },
        ["source", "serie_id", "libelle", "unite", "frequence", "geo", "premiere_periode",
         "derniere_periode", "nb_points_depuis_2000", "dimension_v0", "ventilation",
         "declaratif", "composite", "type", "commentaire", "_v1_propose", "_doublon_m04",
         "_niveau_source"],
    ),
]


# ---------------------------------------------------------------------------
# Lecture tolérante
# ---------------------------------------------------------------------------

def resoudre_chemin(racine: Path, chemin: str) -> Path | None:
    """Renvoie le fichier `chemin` ou sa version `.gz` ; le plus récent si les deux existent."""
    simple = racine / chemin
    compresse = racine / (chemin + ".gz")
    existants = [p for p in (simple, compresse) if p.is_file()]
    if not existants:
        return None
    if len(existants) == 2:
        JOURNAL.warning("%s et %s existent tous deux : le plus récent est lu", simple.name, compresse.name)
        return max(existants, key=lambda p: p.stat().st_mtime)
    return existants[0]


def lire_csv(chemin: Path) -> pd.DataFrame:
    """Lit un CSV (éventuellement compressé) en texte, en UTF-8 puis en Windows-1252."""
    brut = chemin.read_bytes()
    if chemin.suffix == ".gz" or brut[:2] == b"\x1f\x8b":
        brut = gzip.decompress(brut)
    for encodage in ("utf-8-sig", "cp1252"):
        try:
            texte = brut.decode(encodage)
            break
        except UnicodeDecodeError:
            JOURNAL.warning("%s : lecture en %s impossible, essai suivant", chemin.name, encodage)
    else:  # pragma: no cover - cp1252 décode presque tout
        texte = brut.decode("latin-1")
    premiere_ligne = texte.split("\n", 1)[0]
    sep = ";" if premiere_ligne.count(";") > premiere_ligne.count(",") else ","
    return pd.read_csv(io.StringIO(texte), sep=sep, dtype=str, keep_default_na=False)


def charger_catalogue(cat: Catalogue, racine: Path, avertissements: list[str]) -> tuple[pd.DataFrame, dict]:
    """Charge un catalogue dans le schéma commun (colonnes manquantes → valeurs vides)."""
    chemin = resoudre_chemin(racine, cat.chemin)
    info: dict = {"fichier": cat.chemin, "present": chemin is not None}
    if chemin is None:
        message = f"{cat.nom} : catalogue absent ({cat.chemin}[.gz]) — ignoré"
        JOURNAL.warning(message)
        avertissements.append(message)
        return pd.DataFrame(), info
    brut = lire_csv(chemin)
    info.update({"fichier": str(chemin.relative_to(racine)), "lignes": int(len(brut))})
    sortie = pd.DataFrame(index=brut.index)
    manquantes = []
    for cible, candidates in cat.colonnes.items():
        trouvee = next((c for c in candidates if c in brut.columns), None)
        if trouvee is None:
            sortie[cible] = ""
            if cible in cat.attendues:
                manquantes.append(cible)
        else:
            sortie[cible] = brut[trouvee].fillna("").astype(str).str.strip()
    for c in COLONNES_COMMUNES:
        if c not in sortie.columns:
            sortie[c] = ""
    if manquantes:
        message = f"{cat.nom} : colonnes absentes, laissées vides : {', '.join(manquantes)}"
        JOURNAL.warning(message)
        avertissements.append(message)
        info["colonnes_absentes"] = manquantes
    sortie["catalogue_origine"] = cat.nom
    sortie["ligne_id"] = [f"{cat.prefixe}-{i + 1:06d}" for i in range(len(sortie))]
    sortie["_rang_source"] = cat.rang_source
    _completer_par_catalogue(sortie, cat)
    return sortie.reset_index(drop=True), info


def _completer_par_catalogue(df: pd.DataFrame, cat: Catalogue) -> None:
    """Valeurs dérivées propres à chaque catalogue (jamais inventées : lues ou recalculées)."""
    if cat.nom.startswith("insee"):
        df["niveau_source"] = "1"
        df["voie_acces"] = cat.voie_acces
        moyen = df["commentaire"].str.contains(r"type moyen", case=False, regex=True)
        df.loc[(df["type"] == "") & moyen, "type"] = "moyen"
    elif cat.nom == "eurostat_series":
        df["niveau_source"] = "1"
        df["voie_acces"] = cat.voie_acces
        sans_url = (df["url_api"] == "") & (df["serie_id"] != "")
        df.loc[sans_url, "url_api"] = API_EUROSTAT + df.loc[sans_url, "serie_id"]
        _recalculer_ventilations_eurostat(df)
    else:  # M04 et autres catalogues « hors INSEE/Eurostat »
        df["niveau_source"] = df.get("_niveau_source", "")
        df["voie_acces"] = np.where(df["niveau_source"] == "2", "fichier_niveau2",
                                    np.where(df["niveau_source"] == "1", "api_niveau1", ""))
        est_url = df["serie_id"].str.match(r"https?://") & (df["url_api"] == "")
        df.loc[est_url, "url_api"] = df.loc[est_url, "serie_id"]
        preuve = df.get("_preuve", pd.Series("", index=df.index))
        avec_preuve = preuve != ""
        commentaire = df.loc[avec_preuve, "commentaire"]
        prefixe = commentaire.where(commentaire == "", commentaire + " ; ")  # « ; » si non vide
        df.loc[avec_preuve, "commentaire"] = prefixe + "preuve : " + preuve[avec_preuve]
    for c in ("niveau_source", "voie_acces"):
        if c not in df.columns:
            df[c] = ""


_MODALITE = re.compile(r"([^:;]+):(\d{4})-(\d{4}):(\d+)")


def _recalculer_ventilations_eurostat(df: pd.DataFrame) -> None:
    """Lignes `ventilation` Eurostat : périodes et points recalculés sur les modalités.

    Le `nb_annees` de ces lignes ne décrit pas l'ensemble des modalités ; on retient la
    meilleure modalité (dernière période ≥ 2020 si possible, puis le plus de points),
    lue dans `modalites_ventilation` (« code:première-dernière:nb_années »).
    """
    if "_type_ligne" not in df.columns or "_modalites" not in df.columns:
        return
    masque = (df["_type_ligne"] == "ventilation") & (df["_modalites"] != "")
    for i in df.index[masque]:
        mods = [(int(a), int(b), int(n)) for _, a, b, n in _MODALITE.findall(df.at[i, "_modalites"])]
        if not mods:
            continue
        recentes = [m for m in mods if m[1] >= ANNEE_FRAICHEUR] or mods
        meilleure = max(recentes, key=lambda m: (m[2], m[1]))
        df.at[i, "premiere_periode"] = str(min(m[0] for m in mods))
        df.at[i, "derniere_periode"] = str(max(m[1] for m in mods))
        df.at[i, "nb_points_depuis_2000"] = str(meilleure[2])


# ---------------------------------------------------------------------------
# Normalisation de texte
# ---------------------------------------------------------------------------

def sans_accents(texte: str) -> str:
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


def preparer_libelle(texte: str) -> str:
    """Apostrophes et tirets typographiques ramenés à leur forme simple."""
    return (texte.replace("’", "'").replace("‘", "'").replace("ʼ", "'")
            .replace(" ", " ").replace(" ", " "))


# ---------------------------------------------------------------------------
# Rattachement à la grille v1
# ---------------------------------------------------------------------------

@dataclass
class Regle:
    ordre: int
    dimension_v0: str
    motif: re.Pattern | None
    motif_texte: str
    dimension_v1: str
    regle: str


def charger_table(racine: Path) -> list[Regle]:
    table = lire_csv(racine / CHEMIN_TABLE)
    regles = []
    for _, ligne in table.iterrows():
        motif = ligne["motif_libelle"].strip()
        regles.append(Regle(
            ordre=int(ligne["ordre"]),
            dimension_v0=ligne["dimension_v0"].strip(),
            motif=re.compile(motif, re.IGNORECASE) if motif else None,
            motif_texte=motif,
            dimension_v1=ligne["dimension_v1"].strip(),
            regle=ligne["regle"].strip(),
        ))
    return sorted(regles, key=lambda r: r.ordre)


def charger_dimensions(racine: Path) -> tuple[list[str], dict]:
    grille = yaml.safe_load((racine / CHEMIN_GRILLE).read_text(encoding="utf-8"))
    ids = [d["id"] for d in grille["dimensions"]]
    meta = {k: grille.get(k) for k in ("version", "statut", "date_gel")}
    meta["date_gel"] = str(meta["date_gel"])
    return ids, meta


TOUTES_V0 = "*"  # dimension_v0 d'une règle commune à toutes les dimensions


def appliquer_table(libelle: str, dimension_v0: str, regles: list[Regle]) -> tuple[str, Regle | None]:
    """Première règle dont la `dimension_v0` correspond (ou vaut « * ») et dont le motif se
    trouve dans le libellé.

    Le motif est cherché (insensible à la casse) dans le libellé aux apostrophes simplifiées
    et dans sa version sans accents. Une `dimension_v0` vide vaut `non_classe`. Les règles
    sont parcourues dans l'ordre de la colonne `ordre` : une règle « * » ne s'applique à une
    dimension que si elle précède la règle par défaut (motif vide) de cette dimension.
    """
    v0 = dimension_v0.strip() or "non_classe"
    texte = preparer_libelle(libelle)
    texte_sa = sans_accents(texte)
    for r in regles:
        if r.dimension_v0 not in (v0, TOUTES_V0):
            continue
        if r.motif is None or r.motif.search(texte) or r.motif.search(texte_sa):
            return r.dimension_v1, r
    return "a_classer", None


def rattacher(df: pd.DataFrame, regles: list[Regle], dimensions: list[str]) -> None:
    """Colonnes `dimension_v1`, `regle_v1`, `rattachement_note`.

    Quand le catalogue propose déjà une dimension v1 (M04) : une règle d'**exception** de la
    table (motif non vide) l'emporte sur la proposition ; une règle **par défaut** (motif vide)
    ou l'absence de règle lui cède. Tout écart est noté.
    """
    v1, regle_v1, notes = [], [], []
    for libelle, v0, propose, commentaire in zip(df["libelle"], df["dimension_v0"],
                                                  df["_v1_propose"], df["commentaire"]):
        dim, regle = appliquer_table(libelle, v0, regles)
        note = []
        if regle is None:
            note.append(f"dimension_v0 « {v0} » absente de la table : à classer")
        etiquette = f"{regle.ordre} ({regle.regle})" if regle else ""
        if propose:
            if propose not in dimensions and propose not in HORS_DIMENSIONS:
                note.append(f"dimension v1 proposée par le catalogue inconnue : {propose}")
            exception = regle is not None and regle.motif is not None
            if propose != dim and exception:
                note.append(f"exception de la table prioritaire (règle {etiquette}) : catalogue → {propose}, retenu → {dim}")
            elif propose != dim:
                note.append(f"désaccord : catalogue → {propose} (retenu), table → {dim} (règle {etiquette or 'aucune'})")
            if not exception:
                dim = propose
                etiquette = "catalogue" + (f" ; table : {regle.ordre}" if regle else "")
        if "regroupement" in commentaire and "dimension déduite" in commentaire:
            note.append("dimension_v0 déduite du seul regroupement (catalogue source)")
        v1.append(dim)
        regle_v1.append(etiquette)
        notes.append(" ; ".join(note))
    df["dimension_v1"] = v1
    df["regle_v1"] = regle_v1
    df["rattachement_note"] = notes


# ---------------------------------------------------------------------------
# Drapeaux déduits du libellé (déclaratif)
# ---------------------------------------------------------------------------

# Libellé évoquant une opinion ou un ressenti (« perçu » seul est écarté : « revenus perçus »).
MOTIF_DECLARATIF = (
    r"satisf|sentiment|se sentent|se sentir|se sent |ressenti|opinion|confiance|bonheur|heureu|"
    r"inquiet|crainte|optimis|pessimis|solitude|se disent|se declarent|s'estiment|estiment que|"
    r"jugent|auto-?evalu|subjecti|sante (?:percue|declaree)|etat de sante (?:percu|declare)|"
    r"insecurite percue|difficultes? a joindre les deux bouts|fins de mois difficiles|"
    r"sens de la vie|valent la peine|emotion"
)


def marquer_declaratifs(df: pd.DataFrame) -> None:
    """`declaratif` lu dans le catalogue ; à défaut `presume` si le libellé évoque une opinion
    ou un ressenti (motif `MOTIF_DECLARATIF`), sinon vide (inconnu)."""
    vides = df["declaratif"] == ""
    textes = df.loc[vides, "libelle"].map(lambda t: sans_accents(preparer_libelle(t)).lower())
    touches = textes.str.contains(MOTIF_DECLARATIF, case=False, regex=True)
    df.loc[touches.index[touches], "declaratif"] = "presume"


# ---------------------------------------------------------------------------
# Périodes
# ---------------------------------------------------------------------------

_ANNEE = re.compile(r"(1[89]\d{2}|20\d{2})")


def annee(texte: str, derniere: bool = False) -> int | None:
    annees = [int(a) for a in _ANNEE.findall(texte or "")]
    if not annees:
        return None
    return max(annees) if derniere else min(annees)


def entier(texte: str) -> int | None:
    try:
        return int(float(texte))
    except (TypeError, ValueError):
        return None


def preparer_periodes(df: pd.DataFrame) -> None:
    df["_a_premiere"] = df["premiere_periode"].map(lambda t: annee(t))
    df["_a_derniere"] = df["derniere_periode"].map(lambda t: annee(t, derniere=True))
    df["_nb_points"] = df["nb_points_depuis_2000"].map(entier)
    etendue = []
    for p, d in zip(df["_a_premiere"], df["_a_derniere"]):
        if p is None or d is None or pd.isna(p) or pd.isna(d):
            etendue.append(None)
        else:
            etendue.append(max(0, int(d) - max(int(p), ANNEE_DEBUT) + 1))
    df["_etendue"] = etendue
    df["nb_annees_etendue"] = [("" if e is None else str(e)) for e in etendue]


# ---------------------------------------------------------------------------
# Clé de concept (dédoublonnage)
# ---------------------------------------------------------------------------

_MOTS_VIDES = {"le", "la", "les", "l", "un", "une", "de", "du", "des", "d", "et", "a", "au", "aux", "en"}
_INVARIABLES = {"dans", "sous", "sans", "plus", "moins", "temps", "pays", "prix", "taux", "fois", "corps", "sens",
                "cours", "poids", "mois", "avis", "choix", "voix", "paix", "bois", "repas", "divers",
                "heureux", "malheureux", "nombreux", "deux", "trois", "gaz", "virus", "souris",
                "processus", "recours", "secours", "travers", "vers", "alors", "apres", "tres", "hors",
                "envers", "gens", "parcours", "succes", "acces", "proces", "progres", "permis"}


def singulier(mot: str) -> str:
    """Pluriel simplifié (même traitement des deux côtés : la cohérence compte plus que la grammaire)."""
    if len(mot) <= 3 or mot in _INVARIABLES or mot.isdigit():
        return mot
    if mot.endswith("eaux") or mot.endswith("eux") or mot.endswith("oux"):
        return mot[:-1]
    if mot.endswith("aux") and len(mot) > 4:
        return mot[:-3] + "al"
    if mot.endswith("s") and not mot.endswith("ss"):
        return mot[:-1]
    return mot
_VENTIL = (r"(?:sexe|age|ages|classe d'age|classes d'age|groupe d'age|groupes d'age|tranche d'age|"
           r"tranches d'age|quintile de revenu|quintiles de revenu|quintile|quintiles|decile|deciles|"
           r"niveau d'education atteint|niveau d'etudes atteint|niveau d'instruction atteint|"
           r"niveau d'education|niveau d'etudes|niveau d'etude|niveau de diplome|diplome|"
           r"niveau d'instruction|categorie socioprofessionnelle|pcs|type de menage|"
           r"composition du menage|degre d'urbanisation|nationalite|citoyennete|pays de naissance|"
           r"statut d'activite|statut professionnel|statut d'occupation|activite economique)")
_RE_VENTIL = re.compile(
    r"\b(?:par|selon(?: le| la| l')?)\s*" + _VENTIL
    + r"(?:\s*(?:,|et)\s*(?:le |la |l')?" + _VENTIL + r")*"
)
_SOURCES = (r"insee|eurostat|ocde|oecd|banque mondiale|world bank|drees|dares|sdes|ssmsi|citepa|"
            r"depp|owid|our world in data|pnud|undp|oms|unesco|onudc|unodc|fao|eu-silc|silc|srcv|"
            r"how's life|wid|v-dem|freedom house|world justice project|wjp|rsf")
_RE_SOURCE = re.compile(r"\b(?:source ?: ?|d'apres |selon (?:l'|le |la )?)?(?:" + _SOURCES + r")\b")
_RE_ODD = re.compile(r"\b(?:indicateur )?(?:odd|sdg)(?: \d+(?:\.\d+)*[a-z]?)?\b")
_UNITE = (r"(?:en )?(?:pourcentage(?: du (?:pib|produit interieur brut(?: \(pib\))?))?|pour ?cent|%|"
          r"points?(?: de pourcentage)?|euros?(?: courants| constants| par habitant)?|"
          r"devise nationale(?: \(euros?\))?|(?:milliers?|millions?|milliards?)(?: d'euros| de personnes| de tonnes)?|"
          r"mille tonnes|nombre|nombre moyen|unites?|annees?|ans|jours|heures|tonnes|kilotonnes|"
          r"pour mille|pour 1 ?000(?: habitants| personnes)?|pour 100 ?000(?: habitants| personnes)?|‰|"
          r"terajoules?|gigawattheures?|tonnes equivalent petrole|indice(?: base \d+)?|"
          r"base \d+ ?= ?100|usd|dollars?|usd ppa|ppa|spa|sppa|standard de pouvoir d'achat|"
          r"donnees (?:cvs|cjo|cvs-cjo|brutes?)|cvs|cjo|cvs-cjo|brut|brute|brutes|annuel|annuelle|annee)")
_RE_SEG_UNITE = re.compile(r"^" + _UNITE + r"$")
_RE_SEG_ZONE = re.compile(
    r"^(?:france(?: entiere| metropolitaine| hors mayotte| \(hors mayotte\)| y compris mayotte| \(y compris mayotte\))?"
    r"|metropole|ensemble du territoire|niveau national|national)$")
_RE_SEG_TOTAL = re.compile(
    r"^(?:ensemble|total|tous|toutes|tous ages|tout age|hommes|femmes|homme|femme|hommes et femmes|"
    r"sexe ?: ?\w+|ensemble des .*|(?:de |des )?\d+ (?:a|-) \d+ ans.*|\d+ ?- ?\d+ ans|"
    r"\d+ ans (?:ou plus|et plus)|moins de \d+ ans|plus de \d+ ans)$")
_RE_INLINE_ZONE = re.compile(
    r"\b(?:en )?france(?: entiere| metropolitaine| hors mayotte| y compris mayotte)?\b|"
    r"\b(?:hors|y compris) mayotte\b")
_RE_INLINE_UNITE = re.compile(
    r"\b(?:en|exprime en) (?:%|pourcentage|euros?(?: constants| courants)?|milliers|millions|milliards|"
    r"nombre|points?)\b|"
    r"\bpour (?:100|1 ?000|10 ?000|100 ?000) (?:habitants|personnes|naissances vivantes)\b|\bpour mille\b|‰|"
    r"\bdonnees (?:cvs|cjo|cvs-cjo|brutes?)\b|\b(?:cvs-cjo|cvs|cjo)\b|%")
_RE_ANNEES = re.compile(r"\b(?:base|ref(?:erence)?|millesime|edition) (?:1[89]|20)\d{2}\b|\b(?:1[89]|20)\d{2}\b")
_RE_SEPARATEURS = re.compile(r"\s+[—–-]\s+|\s*;\s*|\s*\|\s*|\s*—\s*")
_RE_PARENTHESES = re.compile(r"\(([^()]*)\)")


_RE_PAR_ZONE = re.compile(r"mayotte|corse|metropol|outre-mer|\bdrom?\b|\bdom-com\b|perimetre|hexagon")


def _parenthese_inutile(contenu: str) -> bool:
    c = contenu.strip()
    if not c:
        return True
    if _RE_SEG_UNITE.match(c) or _RE_SEG_ZONE.match(c) or _RE_PAR_ZONE.search(c):
        return True
    if re.fullmatch(r"[\d\s\-–/]+", c):  # années ou plages d'années
        return True
    if re.fullmatch(r"(?:source ?: ?)?(?:" + _SOURCES + r")(?:[ ,/]+(?:" + _SOURCES + r"))*", c):
        return True
    return bool(re.fullmatch(r"(?:en |exprime en )?(?:usd|dollars?|ppa|usd ppa|euros?|%|pourcentage)[^)]*", c))


@lru_cache(maxsize=None)
def cle_concept(libelle: str) -> str:
    """Clé de concept : libellé en minuscules, sans accents, sans mentions de source, d'unité,
    de zone et d'année, sans les segments « total / sexe / âge », pluriels simplifiés.

    Le libellé est découpé en segments (séparateurs « — », « - » entouré d'espaces, « ; »),
    les segments qui ne sont qu'une unité, une zone ou une modalité de total, de sexe ou
    d'âge sont retirés, puis les mentions de ventilation (« par sexe et âge »), de source,
    d'unité, de zone et d'année sont retirées du reste. Renvoie "" si rien ne subsiste.
    """
    texte = sans_accents(preparer_libelle(libelle)).lower().strip()
    if not texte:
        return ""
    texte = _RE_PARENTHESES.sub(lambda m: " " if _parenthese_inutile(m.group(1)) else m.group(0), texte)
    segments = []
    for seg in _RE_SEPARATEURS.split(texte):
        seg = seg.strip(" ,.:")
        if not seg or _RE_SEG_UNITE.match(seg) or _RE_SEG_ZONE.match(seg) or _RE_SEG_TOTAL.match(seg):
            continue
        seg = _RE_VENTIL.sub(" ", seg)
        seg = _RE_ODD.sub(" ", seg)
        seg = _RE_SOURCE.sub(" ", seg)
        seg = _RE_INLINE_ZONE.sub(" ", seg)
        seg = _RE_INLINE_UNITE.sub(" ", seg)
        seg = _RE_ANNEES.sub(" ", seg)
        mots = [singulier(mot) for mot in re.findall(r"[a-z0-9]+", seg) if mot not in _MOTS_VIDES]
        if mots:
            segments.append(" ".join(mots))
    return " | ".join(segments)


# ---------------------------------------------------------------------------
# Concepts : groupes de lignes de même clé, liens « doublon » de M04
# ---------------------------------------------------------------------------

_RE_DOUBLON_M04 = re.compile(r"doublon\s*:\s*([^;]+)", re.IGNORECASE)
_RE_REF_INSEE = re.compile(r"INSEE\s+(\d{9,10})")
_RE_REF_EUROSTAT = re.compile(r"Eurostat\s+([a-z][a-z0-9_]+)", re.IGNORECASE)


def _references_m04(commentaire: str) -> tuple[list[str], list[str]]:
    m = _RE_DOUBLON_M04.search(commentaire or "")
    if not m:
        return [], []
    texte = m.group(1)
    return _RE_REF_INSEE.findall(texte), [c.lower() for c in _RE_REF_EUROSTAT.findall(texte)]


def construire_concepts(df: pd.DataFrame) -> None:
    """Calcule `cle_concept` et un identifiant de groupe interne `_groupe`.

    Deux lignes sont du même concept si elles ont la même clé non vide, ou si M04 déclare
    l'une doublon strict (`doublon_insee_eurostat = oui`) d'une série INSEE (idbank) présente
    dans la long-list. Les doublons partiels et les doublons cités par un code de jeu
    Eurostat sont seulement notés dans `doublon_note`.
    """
    df["cle_concept"] = df["libelle"].map(cle_concept)
    cles = df["cle_concept"].where(df["cle_concept"] != "", "∅" + df["ligne_id"])
    groupe = pd.factorize(cles)[0].astype(np.int64)
    df["doublon_note"] = ""
    df["_lien_m04"] = ""

    bdm = df.index[df["catalogue_origine"] == "insee_bdm"]
    index_insee = dict(zip(df.loc[bdm, "serie_id"], bdm))
    estat = df[(df["catalogue_origine"] == "eurostat_series") & (df["_type_ligne"] != "ventilation")]
    index_jeux = estat.groupby("_code_jeu").groups if len(estat) else {}

    doublons = df.index[df["_doublon_m04"].isin(["oui", "partiel"])]
    for i in doublons:
        insee, eurostat = _references_m04(df.at[i, "commentaire"])
        cites = [f"INSEE {x}" for x in insee] + [f"Eurostat {x}" for x in eurostat]
        nature = df.at[i, "_doublon_m04"]
        if nature == "partiel":
            df.at[i, "doublon_note"] = ("doublon partiel signalé par M04 (même famille, autre définition)"
                                        + (f" : {', '.join(cites)}" if cites else ""))
            continue
        # Seul un idbank INSEE désigne une série précise ; un code de jeu Eurostat désigne un
        # jeu entier (âge, unité, seuil… non précisés) : on le note sans fusionner les concepts.
        cible = next((index_insee[idb] for idb in insee if idb in index_insee), None)
        if cible is None:
            probables = []
            for code in eurostat:
                lignes = list(index_jeux.get(code, []))
                if len(lignes) == 1:
                    probables.append(df.at[lignes[0], "serie_id"])
            note = ("doublon strict signalé par M04, série non identifiée dans la long-list"
                    + (f" : {', '.join(cites)}" if cites else ""))
            if probables:
                note += f" ; série Eurostat probable (seule série par défaut du jeu, à vérifier) : {', '.join(probables)}"
            df.at[i, "doublon_note"] = note
            continue
        ancien, nouveau = groupe[i], groupe[cible]
        groupe[groupe == ancien] = nouveau
        df.at[i, "_lien_m04"] = df.at[cible, "ligne_id"]
        df.at[i, "doublon_note"] = f"doublon strict signalé par M04 : {', '.join(cites)}"
    df["_groupe"] = groupe


def choisir_references(df: pd.DataFrame) -> None:
    """Ligne de référence de chaque concept et colonnes `concept_id`, `doublon_de`.

    Ordre de préférence : éligible (oui, puis a_verifier, puis non) ; INSEE > Eurostat >
    autres ; série la plus longue (points depuis 2000, à défaut étendue) ; total avant
    ventilation ; dernière période la plus récente ; identifiant de ligne.
    """
    rang_elig = df["eligible"].map({"oui": 0, "a_verifier": 1, "non": 2}).fillna(3)
    longueur = df["_nb_points"].where(df["_nb_points"].notna(), df["_etendue"]).fillna(-1).astype(float)
    tri = pd.DataFrame({
        "g": df["_groupe"], "e": rang_elig, "s": df["_rang_source"], "l": -longueur,
        "v": (df["ventilation"] != "").astype(int),
        "d": -pd.to_numeric(df["_a_derniere"], errors="coerce").fillna(0),
        "id": df["ligne_id"],
    }).sort_values(["g", "e", "s", "l", "v", "d", "id"])
    premiers = tri.groupby("g", sort=False).head(1)
    ref_par_groupe = dict(zip(premiers["g"], premiers.index))
    ref = df["_groupe"].map(ref_par_groupe)
    df["concept_id"] = df.loc[ref.values, "ligne_id"].values
    est_ref = df.index == ref.values
    df["doublon_de"] = np.where(est_ref, "", df.loc[ref.values, "serie_id"].values)
    df["doublon_de_ligne"] = np.where(est_ref, "", df["concept_id"])
    taille = df.groupby("_groupe")["ligne_id"].transform("size")
    df["nb_lignes_concept"] = taille.astype(str)
    dims = df.groupby("_groupe")["dimension_v1"].agg(lambda s: " ; ".join(sorted(set(s))) if s.nunique() > 1 else "")
    df["dimensions_concept"] = df["_groupe"].map(dims)
    cle_ref = df.loc[ref.values, "cle_concept"].values
    meme_cle = (~est_ref) & (df["cle_concept"].values == cle_ref) & (df["_lien_m04"] == "")
    notes = df.loc[meme_cle, "doublon_note"]
    df.loc[meme_cle, "doublon_note"] = ("même clé de concept ; " + notes).where(notes != "", "même clé de concept")
    relie = (~est_ref) & (df["cle_concept"].values != cle_ref) & (df["doublon_note"] == "")
    df.loc[relie, "doublon_note"] = "concept relié par un doublon strict signalé par M04"


# ---------------------------------------------------------------------------
# Éligibilité (charte §3.4, D16 à D19)
# ---------------------------------------------------------------------------

def charger_jeux_eurostat(racine: Path) -> dict[str, tuple[int | None, int | None]]:
    """Périodes (toutes zones) des jeux Eurostat, pour repérer un raccordement possible (D16)."""
    chemin = resoudre_chemin(racine, CHEMIN_JEUX_EUROSTAT)
    if chemin is None:
        JOURNAL.info("catalogue des jeux Eurostat absent : raccordement par jeu source non évalué")
        return {}
    jeux = lire_csv(chemin)
    if not {"serie_id", "premiere_periode", "derniere_periode"} <= set(jeux.columns):
        JOURNAL.warning("catalogue des jeux Eurostat : colonnes de périodes absentes")
        return {}
    code = jeux["code_jeu"] if "code_jeu" in jeux.columns else jeux["serie_id"]
    return {c.lower(): (annee(p), annee(d, derniere=True))
            for c, p, d in zip(code, jeux["premiere_periode"], jeux["derniere_periode"])}


def _norm_freq(texte: str) -> str:
    return sans_accents(texte or "").strip().lower()


GEO_USUELLES = {"FR", "FE", "FM", "FR-D976", "FRANCE-F", "FRANCE-FM", "FRANCE-F_X_D976", "FEHM"}

# Signalement non bloquant : libellés de statistiques d'entreprises ou d'échanges extérieurs,
# que la fiche source des catalogues range en principe hors périmètre (note seulement).
MOTIF_CHAMP_ENTREPRISES = re.compile(
    r"\bNACE\b|\bentreprises?\b|commerce international|balance des paiements", re.IGNORECASE)
NOTE_CHAMP_ENTREPRISES = "champ à vérifier : statistiques d'entreprises ou d'échanges extérieurs"


def _opt_int(valeur) -> int | None:
    if valeur is None:
        return None
    try:
        if pd.isna(valeur):
            return None
    except (TypeError, ValueError):
        pass
    return int(valeur)


def evaluer_eligibilite(df: pd.DataFrame, jeux_eurostat: dict) -> None:
    """Colonnes `eligible` (oui | non | a_verifier), `motif_exclusion`, `note_eligibilite`.

    Motifs bloquants : hors_v1, hors_grille, a_classer, candidat_non, geo_non_nationale,
    frequence_non_agregable, derniere_periode_avant_2020, moins_de_10_points. Le dernier
    devient « à vérifier » (motif conservé) si la série est irrégulière (D17) ou si
    10 points sont atteignables par raccordement (D16). Jamais d'exclusion pour redondance.
    """
    col = {c: df[c].tolist() for c in ("dimension_v1", "geo", "frequence", "_agregable", "commentaire",
                                       "candidat", "composite", "type", "serie_id", "_jeu_source", "_groupe",
                                       "ventilation", "cle_concept", "ligne_id", "_lien_m04")}
    rangs = df["_rang_source"].tolist()
    champ_entreprises = df["libelle"].str.contains(MOTIF_CHAMP_ENTREPRISES).tolist()
    premieres = [_opt_int(v) for v in df["_a_premiere"]]
    dernieres = [_opt_int(v) for v in df["_a_derniere"]]
    nbs = [_opt_int(v) for v in df["_nb_points"]]
    etendues = [_opt_int(v) for v in df["_etendue"]]
    groupes: dict[int, np.ndarray] = df.groupby("_groupe").indices
    ordre_motifs = {m: k for k, m in enumerate(MOTIFS)}

    def raccordement(i: int) -> str | None:
        """Raison pour laquelle 10 points sont atteignables par raccordement (D16), ou None."""
        premiere, derniere = premieres[i], dernieres[i]
        if premiere is None or derniere is None:
            return None
        # 1. une autre ligne du même concept et de même ventilation couvre les années
        #    antérieures, sans trou ; préférence : même clé, puis INSEE > Eurostat > autres,
        #    puis la plus ancienne
        partenaires = []
        for j in groupes.get(col["_groupe"][i], []):
            pj, dj = premieres[j], dernieres[j]
            if j == i or pj is None or dj is None:
                continue
            lien = col["_lien_m04"][i] == col["ligne_id"][j] or col["_lien_m04"][j] == col["ligne_id"][i]
            if col["ventilation"][j] != col["ventilation"][i] and not lien:
                continue
            if pj < premiere and dj >= premiere - 1 and derniere - max(pj, ANNEE_DEBUT) + 1 >= MIN_POINTS:
                partenaires.append((not lien, col["cle_concept"][j] != col["cle_concept"][i], rangs[j], pj, j))
        if partenaires:
            *_, pj, j = min(partenaires)
            return f"raccordement possible avec {col['serie_id'][j]} (même concept, depuis {pj}) (D16)"
        # 2. Eurostat : le jeu source d'un indicateur ODD est plus long (périodes toutes zones)
        for code in re.split(r"\s*;\s*", col["_jeu_source"][i]):
            p, d = jeux_eurostat.get(code.lower(), (None, None)) if code else (None, None)
            if p is not None and d is not None and p < premiere and derniere - max(p, ANNEE_DEBUT) + 1 >= MIN_POINTS:
                return f"raccordement possible avec le jeu source {code} ({p}-{d}, toutes zones) (D16)"
        # 3. le catalogue source annonce un raccordement (M01)
        if "raccordement" in col["commentaire"][i]:
            return "raccordement à prévoir selon le catalogue source (D16)"
        return None

    eligible, motifs_col, notes_col = [], [], []
    for i in range(len(df)):
        motifs: list[tuple[str, bool]] = []  # (motif, bloquant)
        a_verifier: list[str] = []
        infos: list[str] = []
        if col["dimension_v1"][i] in HORS_DIMENSIONS:
            motifs.append((col["dimension_v1"][i], True))

        geo = col["geo"][i].strip()
        if not geo:
            a_verifier.append("zone non renseignée")
        elif geo not in GEO_NATIONALES:
            motifs.append(("geo_non_nationale", True))
        elif geo == "FX":
            infos.append("France métropolitaine (FX, FR absent)")
        elif geo not in GEO_USUELLES:
            infos.append(f"périmètre national particulier ({geo})")

        freq = _norm_freq(col["frequence"][i])
        irreguliere = freq == "irreguliere"
        if not freq:
            a_verifier.append("fréquence inconnue")
        elif freq in FREQUENCES_AGREGEABLES:
            if freq != "annuelle":
                if col["_agregable"][i].strip().lower() == "non":
                    motifs.append(("frequence_non_agregable", True))
                else:
                    infos.append(f"{freq} : agrégation annuelle à prévoir")
        elif irreguliere:
            if nbs[i] is None or nbs[i] >= MIN_POINTS:
                infos.append("série irrégulière admise (D17, report de la dernière valeur)")
        elif freq != "ponctuelle":
            motifs.append(("frequence_non_agregable", True))

        derniere = dernieres[i]
        if derniere is None:
            a_verifier.append("dernière période inconnue")
        elif derniere < ANNEE_FRAICHEUR:
            motifs.append(("derniere_periode_avant_2020", True))

        nb, etendue = nbs[i], etendues[i]
        if nb is None:
            if etendue is None:
                a_verifier.append("nombre de points inconnu")
            elif etendue >= MIN_POINTS:
                infos.append(f"points non comptés : étendue de {etendue} années depuis {ANNEE_DEBUT}")
            else:
                nb = etendue  # borne supérieure du nombre de points
        if nb is not None and nb < MIN_POINTS:
            if irreguliere or (etendue is not None and etendue >= MIN_POINTS and nb < etendue):
                sur = f" sur {etendue} années" if etendue is not None else ""
                souple = f"série irrégulière : {nb} points{sur} (D17)"
            else:
                souple = raccordement(i)
            motifs.append(("moins_de_10_points", not souple))
            if souple:
                a_verifier.append(souple)
        elif "raccordement" in col["commentaire"][i]:
            infos.append("raccordement souhaitable pour couvrir 2000-2009 (D16, catalogue source)")

        # Refus du catalogue source sans motif recalculable ici (sinon le motif recalculé,
        # avec ses dérogations D16/D17, prévaut : ex. « < 10 années » d'Eurostat).
        if col["candidat"][i].strip().lower() == "non" and not motifs:
            motifs.append(("candidat_non", True))
        if col["composite"][i] == "oui":
            infos.append("composite admis (D18)")
        if col["type"][i] == "moyen":
            infos.append("indicateur de moyens admis (D19)")
        if champ_entreprises[i]:
            infos.append(NOTE_CHAMP_ENTREPRISES)

        if any(b for _, b in motifs):
            eligible.append("non")
        elif a_verifier:
            eligible.append("a_verifier")
        else:
            eligible.append("oui")
        noms = sorted({m for m, _ in motifs}, key=lambda m: ordre_motifs.get(m, 99))
        motifs_col.append(" ; ".join(noms))
        notes_col.append(" ; ".join([f"à vérifier : {a}" for a in a_verifier] + infos))
    df["eligible"] = eligible
    df["motif_exclusion"] = motifs_col
    df["note_eligibilite"] = notes_col


# ---------------------------------------------------------------------------
# Assemblage
# ---------------------------------------------------------------------------

@dataclass
class Resultat:
    table: pd.DataFrame
    catalogues: dict
    avertissements: list[str]
    dimensions: list[str]
    grille: dict
    nb_regles: int


def construire_longlist(racine: Path = RACINE, catalogues: list[Catalogue] | None = None) -> Resultat:
    """Union, rattachement, éligibilité et concepts ; renvoie la table complète."""
    racine = Path(racine)
    avertissements: list[str] = []
    dimensions, grille = charger_dimensions(racine)
    regles = charger_table(racine)
    infos, morceaux = {}, []
    for cat in catalogues or CATALOGUES:
        df, info = charger_catalogue(cat, racine, avertissements)
        infos[cat.nom] = info
        if len(df):
            morceaux.append(df)
            JOURNAL.info("%s : %d lignes", cat.nom, len(df))
    if not morceaux:
        raise SystemExit("Aucun catalogue trouvé : rien à faire.")
    table = pd.concat(morceaux, ignore_index=True, sort=False)
    for c in table.columns:
        if c != "_rang_source":
            table[c] = table[c].fillna("")
    for c in ("_v1_propose", "_agregable", "_doublon_m04", "_type_ligne", "_code_jeu", "_jeu_source"):
        if c not in table.columns:
            table[c] = ""

    JOURNAL.info("rattachement v1 (%d règles)", len(regles))
    rattacher(table, regles, dimensions)
    marquer_declaratifs(table)
    preparer_periodes(table)
    JOURNAL.info("clés de concept")
    construire_concepts(table)
    JOURNAL.info("éligibilité")
    evaluer_eligibilite(table, charger_jeux_eurostat(racine))
    choisir_references(table)
    return Resultat(table, infos, avertissements, dimensions, grille, len(regles))


# ---------------------------------------------------------------------------
# Bilan et écriture
# ---------------------------------------------------------------------------

def _compter(series: pd.Series) -> dict:
    return {str(k): int(v) for k, v in series.value_counts().items() if str(k) != ""}


def bilan_partie(t: pd.DataFrame) -> dict:
    motifs: dict[str, dict[str, int]] = {}
    for statut, texte in zip(t["eligible"], t["motif_exclusion"]):
        for m in filter(None, texte.split(" ; ")):
            motifs.setdefault(m, {"non": 0, "a_verifier": 0, "oui": 0})[statut] += 1
    par_source = {}
    for nom, s in t.groupby("catalogue_origine"):
        par_source[nom] = {"lignes": int(len(s)), "eligibles": int((s["eligible"] == "oui").sum()),
                           "a_verifier": int((s["eligible"] == "a_verifier").sum())}
    return {
        "lignes": int(len(t)),
        "eligibles": int((t["eligible"] == "oui").sum()),
        "a_verifier": int((t["eligible"] == "a_verifier").sum()),
        "non_eligibles": int((t["eligible"] == "non").sum()),
        "motifs": dict(sorted(motifs.items(), key=lambda kv: MOTIFS.index(kv[0]) if kv[0] in MOTIFS else 99)),
        "declaratifs": {"oui": int((t["declaratif"] == "oui").sum()),
                        "presume": int((t["declaratif"] == "presume").sum())},
        "declaratifs_eligibles_ou_a_verifier": int(
            (t["declaratif"].isin(["oui", "presume"]) & (t["eligible"] != "non")).sum()),
        "composites": int((t["composite"] == "oui").sum()),
        "ventilations": int((t["ventilation"] != "").sum()),
        "statistiques_entreprises_signalees": {
            "lignes": int(t["note_eligibilite"].str.contains(NOTE_CHAMP_ENTREPRISES, regex=False).sum()),
            "eligibles": int((t["note_eligibilite"].str.contains(NOTE_CHAMP_ENTREPRISES, regex=False)
                              & (t["eligible"] == "oui")).sum()),
        },
        "concepts_distincts": int(t["concept_id"].nunique()),
        "concepts_distincts_eligibles": int(t.loc[t["eligible"] == "oui", "concept_id"].nunique()),
        "concepts_distincts_eligibles_ou_a_verifier": int(t.loc[t["eligible"] != "non", "concept_id"].nunique()),
        "lignes_de_reference": int((t["doublon_de_ligne"] == "").sum()),
        "par_source": par_source,
        "rattachement": {
            "par_regle": _compter(t["regle_v1"].str.extract(r"^(\d+|catalogue)", expand=False).fillna("aucune")),
            "desaccords_catalogue_retenu": int(t["rattachement_note"].str.contains("désaccord").sum()),
            "exceptions_table_prioritaires": int(t["rattachement_note"].str.contains("exception de la table").sum()),
        },
    }


def etat_des_sources(racine: Path) -> dict:
    """État des collectes d'après les bilans des catalogues (complet ou partiel)."""
    etat = {}
    chemin = resoudre_chemin(racine, "catalogues/insee_bilan.json")
    if chemin:
        b = json.loads(chemin.read_text(encoding="utf-8"))
        collecte = b.get("collecte", {})
        etat["insee"] = {"date": b.get("date"), "collecte_terminee": collecte.get("termine")}
    chemin = resoudre_chemin(racine, "catalogues/eurostat_bilan.json")
    if chemin:
        b = json.loads(chemin.read_text(encoding="utf-8"))
        n2 = b.get("etapes", {}).get("niveau2", {})
        etat["eurostat"] = {"date": b.get("date"), "niveau2_termine": n2.get("termine"),
                            "niveau2_jeux_restants": n2.get("restants"),
                            "niveau2_statuts": b.get("niveau2_statuts")}
    return etat


def construire_bilan(res: Resultat, racine: Path, remarque: str = "") -> dict:
    t = res.table
    bilan = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "script": f"src/pipeline/longlist.py v{VERSION}",
        "grille": res.grille,
        "table_correspondance": {"fichier": CHEMIN_TABLE, "regles": res.nb_regles},
        "remarque": remarque,
        "catalogues": res.catalogues,
        "etat_des_collectes": etat_des_sources(racine),
        "avertissements": res.avertissements,
        "total": bilan_partie(t),
        "par_dimension": {d: bilan_partie(t[t["dimension_v1"] == d]) for d in res.dimensions},
        "hors_grille": bilan_partie(t[t["dimension_v1"].isin(HORS_DIMENSIONS)]),
        "hors_grille_par_statut": _compter(t.loc[t["dimension_v1"].isin(HORS_DIMENSIONS), "dimension_v1"]),
        "concepts_sur_plusieurs_dimensions": int(t.loc[t["dimensions_concept"] != "", "concept_id"].nunique()),
    }
    return bilan


def ecrire_csv(t: pd.DataFrame, chemin: Path, compresser: bool = False) -> Path:
    """Écrit le CSV (UTF-8, virgule, LF), en clair ou compressé (`.csv.gz`).

    En clair : sortie de travail, ignorée par git (`.gitignore`) ; un `.csv.gz` existant
    (commité) n'est pas touché. Compressé : sortie d'une exécution finale, à commiter ;
    le `.csv` en clair du même nom, devenu périmé, est supprimé.
    """
    donnees = t[COLONNES_SORTIE].to_csv(index=False, lineterminator="\n").encode("utf-8")
    if compresser:
        compresse = chemin.with_name(chemin.name + ".gz")
        compresse.write_bytes(gzip.compress(donnees, mtime=0))
        chemin.unlink(missing_ok=True)
        return compresse
    chemin.write_bytes(donnees)
    return chemin


def trier_pour_sortie(t: pd.DataFrame) -> pd.DataFrame:
    """Lignes d'un même concept regroupées, référence en tête ; concepts dont la référence
    est éligible d'abord, puis à vérifier, puis non éligibles."""
    rang = t["eligible"].map({"oui": 0, "a_verifier": 1, "non": 2})
    rang_ref = t["concept_id"].map(dict(zip(t["ligne_id"], rang)))
    rang_ref = rang_ref.fillna(rang)  # référence hors de cette partie : rang de la ligne
    cles = t.assign(_r=rang_ref, _d=(t["doublon_de_ligne"] != "").astype(int))
    return cles.sort_values(["_r", "concept_id", "_d", "ligne_id"]).drop(columns=["_r", "_d"])


def ecrire_sorties(res: Resultat, racine: Path, dimension: str = "toutes", remarque: str = "",
                   compresser: bool = False) -> list[Path]:
    sortie = racine / DOSSIER_SORTIE
    sortie.mkdir(parents=True, exist_ok=True)
    t = res.table
    ecrits = []
    cibles = res.dimensions + ["hors_grille"] if dimension == "toutes" else [dimension]
    for d in cibles:
        partie = t[t["dimension_v1"].isin(HORS_DIMENSIONS)] if d == "hors_grille" else t[t["dimension_v1"] == d]
        chemin = ecrire_csv(trier_pour_sortie(partie), sortie / f"longlist_{d}.csv", compresser)
        ecrits.append(chemin)
        JOURNAL.info("%s : %d lignes (%d éligibles, %d à vérifier)", chemin.name, len(partie),
                     (partie["eligible"] == "oui").sum(), (partie["eligible"] == "a_verifier").sum())
    if dimension == "toutes":
        bilan = construire_bilan(res, racine, remarque)
        chemin = sortie / "longlist_bilan.json"
        chemin.write_text(json.dumps(bilan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        ecrits.append(chemin)
    return ecrits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Long-list commune des indicateurs candidats (M05).")
    parser.add_argument("--dimension", default="toutes",
                        help="identifiant d'une dimension v1, « hors_grille » ou « toutes » (défaut)")
    parser.add_argument("--racine", default=str(RACINE), help="racine du dépôt (défaut : celle du module)")
    parser.add_argument("--remarque", default="", help="texte libre recopié dans le bilan (provenance des catalogues…)")
    parser.add_argument("--compresser", action="store_true",
                        help="écrire les sorties en .csv.gz (exécution finale, à commiter) ; défaut : .csv en clair, "
                             "ignorés par git")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", stream=sys.stdout)
    racine = Path(args.racine)
    dimensions, _ = charger_dimensions(racine)
    if args.dimension not in dimensions + ["hors_grille", "toutes"]:
        parser.error(f"dimension inconnue : {args.dimension} (attendu : {', '.join(dimensions)}, hors_grille, toutes)")
    res = construire_longlist(racine)
    ecrits = ecrire_sorties(res, racine, args.dimension, args.remarque, args.compresser)
    for p in ecrits:
        print(f"écrit : {p.relative_to(racine)} ({p.stat().st_size / 1e6:.1f} Mo)")
    if args.dimension != "toutes":
        t = res.table
        partie = t[t["dimension_v1"].isin(HORS_DIMENSIONS)] if args.dimension == "hors_grille" \
            else t[t["dimension_v1"] == args.dimension]
        print(json.dumps(bilan_partie(partie), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
