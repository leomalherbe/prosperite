"""Vérifie les fiches indicateurs d'une dimension (mission M05, tâche 5) et produit le tableau de validation.

Contrôles (erreurs bloquantes, code de sortie 1) :
1. **Schéma** de chaque fiche `indicateurs/<dimension>/<id>.yaml` : champs de la charte §5.1 et de la fiche M05
   (famille, variante_principale, variantes, composite, raccordement, incontournable, recommandation,
   motif_recommandation, note_pertinence, socle_v1 vide), valeurs admises, identifiant ASCII = nom du fichier,
   motif en une phrase, note de pertinence de 2 à 4 phrases, `raccordement` au format
   « oui|non|a_etudier : note courte » (note obligatoire pour oui et a_etudier), `sens: ambigu` → `ecarter`.
2. **Identifiants** uniques dans tout `indicateurs/*/` (aucun indicateur dans deux dimensions).
3. **Familles** : une seule variante principale par famille ; principale → `retenir` ou `ecarter` ;
   autre fiche de la famille → `retenir_variante` ou `ecarter`.
4. **Catalogues** : l'identifiant de la série principale (ou chacune de ses `composantes`) et celui de chaque
   variante figurent dans un catalogue du dépôt (long-lists, catalogues INSEE et Eurostat, y compris les
   séries écartées `*_non`) ; une composante Eurostat peut être une modalité d'un « paquet » catalogué
   (même jeu, mêmes clés, une valeur par clé ; écarts construits, D34). Exception documentée : une fiche
   ou une variante hors catalogue de séries
   (`hors_longlist: oui`, ou variante sans `ligne_id`) dont le jeu Eurostat figure dans le catalogue des jeux,
   ou dont le champ `preuve` désigne un fichier du dépôt (sortie du robot, ex. `docs/sources/series/…`) :
   avertissement, la série est à cataloguer (liste de maintenance, D32).
5. **Couverture** (si `docs/validation/preselection_<dimension>_lignes.csv` existe) : chaque ligne de la
   long-list de la dimension est affectée ; chaque groupe `fiche` a sa fiche ; les variantes des fiches
   correspondent à la présélection (sinon relancer `scripts/preselection.py --maj-fiches`) ; avertissement si
   une ligne utilisée ici (fiche ou variante) est déjà la série principale d'une fiche d'une autre dimension
   (lecture des `docs/validation/preselection_*_lignes.csv`, R1).
6. **Tableau de validation** (si `docs/validation/validation_<dimension>.csv` existe) : une ligne par fiche,
   colonnes attendues, valeurs cohérentes avec les fiches, `decision_leo` vide ou dans la liste admise.
7. **Socle proposé** (D41, méthode 33 v1.3) : `socle_propose: oui|non` obligatoire sur **toute** fiche ;
   `oui` réservé aux variantes principales recommandées `retenir` ; toute variante principale `retenir` et
   `incontournable: oui` est `socle_propose: oui`, sauf dérogation explicite écrite dans la fiche
   (`derogation_socle: <motif>`, ex. décision de Léo) ; 8 fiches `oui` au plus par dimension. Quand la limite
   de 8 est atteinte, un incontournable laissé hors du socle sans dérogation écrite est un avertissement.
   Tant que sa correction n'est pas fusionnée, `logement_cadre_vie` peut ne pas porter le champ
   (avertissement, `DIMENSIONS_SOCLE_TRANSITOIRE`). Avertissement si une fiche non principale porte
   `incontournable: oui` (D38 d).
8. **Identifiants DREES** (D45) : un identifiant du baromètre d'opinion qui cite les deux anciennes pièces jointes
   (`barometre2000_2024_diff_csv` et `barometre2025_diff_csv`) est reconnu comme celui de la pièce jointe unique
   `barometre2000_2025_diff_csv`, avec un avertissement (à aligner).

Avertissements sur les lignes renvoyées (D38 a, D46), à partir des `docs/validation/preselection_*_lignes.csv` :
- toute ligne renvoyée à la dimension par `autre_dimension:<dim>` qu'aucune règle de la dimension ne reprend
  (fiche, variante, écart en bloc ou renvoi motivé vers une troisième dimension) ;
- toute ligne écartée en bloc par la dimension alors qu'une autre dimension la retient (fiche ou variante) ;
  la dimension qui la retient en garde le compte (`lignes_retenues_ecartees_ailleurs`).

Usage :
    python scripts/verifier_fiches.py --dimension liens_bien_etre
    python scripts/verifier_fiches.py --dimension liens_bien_etre --tableau   # (ré)écrit le tableau de validation
    python scripts/verifier_fiches.py --lignes-renvoyees [--limite 20]        # bilan des renvois, par couple
Les décisions de Léo (`decision_leo`, `commentaire_leo`) déjà saisies dans le tableau sont conservées lors de la
réécriture ; la réécriture échoue si elle ferait disparaître une décision (fiche supprimée ou renommée).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import yaml

RACINE = Path(__file__).resolve().parent.parent

OUI_NON = {"oui", "non"}
OBLIGATOIRES = {
    "id": "id", "libelle": "texte", "dimension": "texte", "sous_theme": "texte", "famille": "id",
    "variante_principale": OUI_NON, "definition": "texte", "unite": "texte", "sens": {"haut", "bas", "ambigu"},
    "type": {"resultat", "moyen", "pression"}, "declaratif": OUI_NON, "composite": OUI_NON,
    "source_organisme": "texte", "source_jeu": "texte", "source_serie_id": "texte", "source_niveau": {1, 2},
    "url_api": "url", "url_page": "url",
    "frequence": {"annuelle", "irreguliere", "semestrielle", "trimestrielle", "mensuelle", "ponctuelle"},
    "premiere_annee": "annee", "derniere_annee": "annee", "geo": "texte", "raccordement": "raccordement",
    "incontournable": OUI_NON, "recommandation": {"retenir", "retenir_variante", "ecarter"},
    "motif_recommandation": "phrase", "note_pertinence": "note", "variantes": "liste", "socle_v1": "socle",
    "qualite": "liste", "notes": "texte_vide",
}
FACULTATIFS = {
    "composantes": "liste", "formule": "texte", "nb_points_depuis_2000": "entier",
    "eligibilite_longlist": {"oui", "a_verifier", "non", "hors_longlist"}, "ligne_id": "texte_vide",
    "hors_longlist": OUI_NON, "rattachement_propose": "texte", "preuve": "texte",
    "statut_serie": {"disponible", "a_calculer"}, "annee_reference": {"observation", "edition"},
    # socle_propose est obligatoire (D41) : contrôlé par controler_socle (avertissement en transition)
    "socle_propose": OUI_NON, "derogation_socle": "texte",
}
COLONNES_TABLEAU = ["id", "libelle", "sous_theme", "famille", "variante_principale", "definition_courte", "sens", "unite",
                    "source", "serie_id", "periode", "type", "declaratif", "composite", "incontournable",
                    "socle_propose", "recommandation", "motif", "decision_leo", "commentaire_leo"]
# Format du tableau avant la méthode v1.3 (sans sous_theme ni socle_propose) : admis avec un avertissement
# (tableaux non encore régénérés) ; `--tableau` le remplace par le format v1.3 en gardant les décisions.
COLONNES_TABLEAU_V12 = [c for c in COLONNES_TABLEAU if c not in ("sous_theme", "socle_propose")]
COLONNES_LEO = ["decision_leo", "commentaire_leo"]
DECISIONS_LEO = {"", "retenu", "retenu_socle", "ecarte", "a_discuter"}
SOCLE_MAX = 8                       # D41 : 8 fiches socle_propose: oui au plus par dimension
# D41 : dimensions dont la correction (qui pose socle_propose) n'est pas encore fusionnée ; l'absence du
# champ y est un avertissement. À vider une fois la correction de logement_cadre_vie fusionnée.
DIMENSIONS_SOCLE_TRANSITOIRE = {"logement_cadre_vie"}
# D45 : identifiants du baromètre d'opinion de la DREES, anciennes pièces jointes → pièce jointe unique
DREES_ANCIEN = "pièces jointes barometre2000_2024_diff_csv et barometre2025_diff_csv"
DREES_UNIQUE = "pièce jointe barometre2000_2025_diff_csv"
_RE_ID = re.compile(r"^[a-z][a-z0-9_]*$")
_RE_RACCORDEMENT = re.compile(r"^(oui|non|a_etudier)(?: : (\S.*))?$", re.DOTALL)
_RE_FIN_PHRASE = re.compile(r"[.!?…](?=\s+[A-ZÀÂÉÈÊÎÔÛÇ«])")


@dataclass
class Rapport:
    dimension: str
    erreurs: list[str] = field(default_factory=list)
    avertissements: list[str] = field(default_factory=list)
    compteurs: dict = field(default_factory=dict)

    def erreur(self, fiche: str, message: str) -> None:
        self.erreurs.append(f"{fiche} : {message}")

    def avertir(self, fiche: str, message: str) -> None:
        self.avertissements.append(f"{fiche} : {message}")


def nb_phrases(texte: str) -> int:
    texte = texte.strip()
    if not texte:
        return 0
    return len(_RE_FIN_PHRASE.findall(texte)) + 1


def socle_vide(valeur) -> bool:
    if valeur in (None, {}, ""):
        return True
    return isinstance(valeur, dict) and all(v in (None, "") for v in valeur.values())


def _controle_valeur(nom: str, attendu, valeur) -> str | None:
    """Renvoie un message d'erreur, ou None si la valeur est admise."""
    if isinstance(attendu, set):
        return None if valeur in attendu else f"{nom} = {valeur!r} (attendu : {', '.join(sorted(map(str, attendu)))})"
    if attendu == "id":
        return None if isinstance(valeur, str) and _RE_ID.match(valeur) else f"{nom} doit être un identifiant ASCII"
    if attendu in ("texte", "phrase", "note"):
        if not isinstance(valeur, str) or not valeur.strip():
            return f"{nom} vide"
        if attendu == "phrase" and (nb_phrases(valeur) != 1 or not valeur.rstrip().endswith(".")):
            return f"{nom} doit tenir en une phrase terminée par un point"
        if attendu == "note" and not 2 <= nb_phrases(valeur) <= 4:
            return f"{nom} doit compter de 2 à 4 phrases ({nb_phrases(valeur)})"
        return None
    if attendu == "texte_vide":
        return None if isinstance(valeur, str) else f"{nom} doit être un texte (éventuellement vide)"
    if attendu == "url":
        ok = isinstance(valeur, str) and (valeur.startswith(("http://", "https://")) or valeur == "non trouvé")
        return None if ok else f"{nom} doit être une URL ou « non trouvé »"
    if attendu == "annee":
        ok = (isinstance(valeur, int) and 1700 <= valeur <= 2100) or valeur == "non trouvé"
        return None if ok else f"{nom} doit être une année ou « non trouvé »"
    if attendu == "entier":
        return None if isinstance(valeur, int) and valeur >= 0 else f"{nom} doit être un entier positif"
    if attendu == "liste":
        return None if isinstance(valeur, list) else f"{nom} doit être une liste"
    if attendu == "raccordement":
        m = _RE_RACCORDEMENT.match(valeur) if isinstance(valeur, str) else None
        if not m:
            return f"{nom} doit suivre le format « oui|non|a_etudier : note courte »"
        if m.group(1) != "non" and not m.group(2):
            return f"{nom} = {m.group(1)} : note courte obligatoire après « : »"
        return None
    if attendu == "socle":
        return None if socle_vide(valeur) else f"{nom} doit rester vide au stade M05"
    return f"{nom} : type de contrôle inconnu"


def controler_schema(fiche: dict, chemin: Path, dimension: str, rapport: Rapport) -> None:
    nom = chemin.stem
    for cle, attendu in OBLIGATOIRES.items():
        if cle not in fiche:
            rapport.erreur(nom, f"champ obligatoire absent : {cle}")
            continue
        message = _controle_valeur(cle, attendu, fiche[cle])
        if message:
            rapport.erreur(nom, message)
    for cle, attendu in FACULTATIFS.items():
        if cle in fiche:
            message = _controle_valeur(cle, attendu, fiche[cle])
            if message:
                rapport.erreur(nom, message)
    inconnus = set(fiche) - set(OBLIGATOIRES) - set(FACULTATIFS)
    if inconnus:
        rapport.avertir(nom, f"champs hors schéma : {', '.join(sorted(inconnus))}")
    if fiche.get("id") != nom:
        rapport.erreur(nom, f"id ({fiche.get('id')}) différent du nom de fichier")
    if fiche.get("dimension") != dimension:
        rapport.erreur(nom, f"dimension = {fiche.get('dimension')!r}, attendu {dimension}")
    if fiche.get("sens") == "ambigu" and fiche.get("recommandation") != "ecarter":
        rapport.erreur(nom, "sens ambigu : seule la recommandation « ecarter » est admise (charte §3.4)")
    pa, da = fiche.get("premiere_annee"), fiche.get("derniere_annee")
    if isinstance(pa, int) and isinstance(da, int) and pa > da:
        rapport.erreur(nom, "premiere_annee postérieure à derniere_annee")
    for i, v in enumerate(fiche.get("variantes") or []):
        if not isinstance(v, dict) or not all(isinstance(v.get(k), str) and v.get(k) for k in ("serie_id", "source", "nature")):
            rapport.erreur(nom, f"variante n° {i + 1} : serie_id, source et nature sont obligatoires")


def lire_fiches(racine: Path, dimension: str) -> list[tuple[Path, dict]]:
    fiches = []
    for chemin in sorted((racine / "indicateurs" / dimension).glob("*.yaml")):
        if not chemin.name.startswith("_"):
            fiches.append((chemin, yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}))
    return fiches


def ids_toutes_dimensions(racine: Path) -> Counter:
    compte = Counter()
    for chemin in (racine / "indicateurs").glob("*/*.yaml"):
        if not chemin.name.startswith("_"):
            donnees = yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}
            compte[donnees.get("id", chemin.stem)] += 1
    return compte


def index_catalogues(racine: Path) -> tuple[set[str], set[str]]:
    """Identifiants de séries de tous les catalogues du dépôt, et codes des jeux Eurostat."""
    series: set[str] = set()
    dossier = racine / "catalogues"
    motifs = ["longlist_*.csv.gz", "longlist_*.csv", "insee_*_catalogue.csv", "insee_*_catalogue_non.csv.gz",
              "eurostat_series_catalogue*.csv.gz", "eurostat_series_catalogue*.csv"]
    for motif in motifs:
        for chemin in dossier.glob(motif):
            try:
                df = pd.read_csv(chemin, dtype=str, keep_default_na=False, usecols=["serie_id"])
            except ValueError:
                continue
            series.update(df["serie_id"])
    series.update({normaliser_id(s) for s in series if DREES_ANCIEN in s})
    jeux: set[str] = set()
    chemin_jeux = dossier / "eurostat_jeux_catalogue.csv"
    if chemin_jeux.exists():
        jeux.update(pd.read_csv(chemin_jeux, dtype=str, keep_default_na=False, usecols=["code_jeu"])["code_jeu"])
    return series, jeux


def normaliser_id(serie: str) -> str:
    """Identifiant DREES aligné sur la pièce jointe unique du baromètre d'opinion (D45)."""
    return serie.replace(DREES_ANCIEN, DREES_UNIQUE) if isinstance(serie, str) else serie


def _au_catalogue(serie: str, series: set[str]) -> bool:
    return serie in series or normaliser_id(serie) in series


def _preuve(racine: Path | None, element: dict) -> str | None:
    """Chemin de preuve (fichier du dépôt) déclaré par une fiche ou une variante, s'il existe."""
    chemin = element.get("preuve")
    if racine is not None and isinstance(chemin, str) and chemin and (racine / chemin).is_file():
        return chemin
    return None


def _cle_requete(serie: str) -> tuple[str, list[tuple[str, str]]]:
    """Découpe un identifiant Eurostat `jeu?k1=v1&k2=v2…` en (jeu, paires clé-valeur)."""
    jeu, _, requete = serie.partition("?")
    paires = [tuple(p.split("=", 1)) for p in requete.split("&") if "=" in p] if requete else []
    return jeu, paires


def index_paquets(series: set[str]) -> dict[str, list[dict[str, set[str]]]]:
    """Paquets de modalités du catalogue (`jeu?…&sex=M&sex=F…`), par jeu : clé → valeurs admises."""
    index: dict[str, list[dict[str, set[str]]]] = defaultdict(list)
    for serie in series:
        jeu, paires = _cle_requete(serie)
        if paires:
            cles: dict[str, set[str]] = defaultdict(set)
            for k, v in paires:
                cles[k].add(v)
            index[jeu].append(dict(cles))
    return index


def selection_de_paquet(serie: str, paquets: dict[str, list[dict[str, set[str]]]]) -> bool:
    """Vrai si `serie` (une valeur par clé) est une modalité d'un paquet catalogué du même jeu, avec les mêmes
    clés : composante d'un écart construit (méthode 33 §9, D34), ex. `une_rt_a?…&sex=F…` dans `…&sex=M&sex=F…`."""
    jeu, paires = _cle_requete(serie)
    cles = [k for k, _ in paires]
    if not paires or len(cles) != len(set(cles)):
        return False
    return any(set(p) == set(cles) and all(v in p[k] for k, v in paires) for p in paquets.get(jeu, []))


def controler_catalogues(fiche: dict, rapport: Rapport, series: set[str], jeux: set[str],
                         racine: Path | None = None, paquets: dict | None = None) -> None:
    nom = fiche.get("id", "?")
    hors = fiche.get("hors_longlist") == "oui"
    principales = fiche.get("composantes") or [fiche.get("source_serie_id", "")]
    identifiants = [fiche.get("source_serie_id", "")] + list(principales) + [
        v.get("serie_id", "") for v in fiche.get("variantes") or [] if isinstance(v, dict)]
    anciens = sum(isinstance(s, str) and DREES_ANCIEN in s for s in identifiants)
    if anciens:
        rapport.avertir(nom, f"{anciens} identifiant(s) DREES citant les deux anciennes pièces jointes : aligner sur "
                             f"la « {DREES_UNIQUE} » (D45)")
    for serie in principales:
        if _au_catalogue(serie, series):
            continue
        if fiche.get("composantes"):
            if paquets is None:
                paquets = index_paquets(series)
            if selection_de_paquet(serie, paquets):
                continue
        if hors and serie.split("?")[0] in jeux:
            rapport.avertir(nom, f"série principale hors catalogue de séries (jeu {serie.split('?')[0]} au catalogue "
                                 "des jeux) : à réintégrer au catalogue")
            continue
        if hors and _preuve(racine, fiche):
            etat = " ; valeurs à calculer" if fiche.get("statut_serie") == "a_calculer" else ""
            rapport.avertir(nom, f"série principale hors catalogue (preuve : {_preuve(racine, fiche)}){etat} : "
                                 "à cataloguer")
            continue
        rapport.erreur(nom, f"série principale absente des catalogues : {serie}")
    for v in fiche.get("variantes") or []:
        serie = v.get("serie_id", "")
        if _au_catalogue(serie, series):
            continue
        if not v.get("ligne_id") and serie.split("?")[0] in jeux and "vérifi" in v.get("catalogue", ""):
            continue
        if not v.get("ligne_id") and _preuve(racine, v):
            continue
        rapport.erreur(nom, f"variante absente des catalogues : {serie}")


def controler_lignes_croisees(racine: Path, dimension: str, rapport: Rapport) -> None:
    """Avertit si une ligne utilisée par la dimension (fiche ou variante) est la série principale d'une fiche
    d'une autre dimension (rattachements croisés, R1, D32)."""
    dossier = racine / "docs" / "validation"
    propre = dossier / f"preselection_{dimension}_lignes.csv"
    if not propre.exists():
        return
    lignes = pd.read_csv(propre, dtype=str, keep_default_na=False)
    utilisees = lignes[(lignes["decision"] == "fiche") | lignes["decision"].str.startswith("variante_de:")]
    prises = {}
    for chemin in sorted(dossier.glob("preselection_*_lignes.csv")):
        autre = chemin.name[len("preselection_"):-len("_lignes.csv")]
        if autre == dimension:
            continue
        df = pd.read_csv(chemin, dtype=str, keep_default_na=False)
        for r in df[df["decision"] == "fiche"].to_dict("records"):
            prises.setdefault(r["ligne_id"], (autre, r["groupe"]))
    n = 0
    for r in utilisees.to_dict("records"):
        if r["ligne_id"] in prises:
            autre, groupe = prises[r["ligne_id"]]
            rapport.avertir(r["fiche"], f"ligne {r['ligne_id']} déjà série principale de {autre}/{groupe} (R1)")
            n += 1
    rapport.compteurs["lignes_prises_ailleurs"] = n


def lire_preselections(racine: Path) -> dict[str, pd.DataFrame]:
    """Les `docs/validation/preselection_<dim>_lignes.csv` du dépôt, par dimension."""
    dossier = racine / "docs" / "validation"
    return {chemin.name[len("preselection_"):-len("_lignes.csv")]: pd.read_csv(chemin, dtype=str, keep_default_na=False)
            for chemin in sorted(dossier.glob("preselection_*_lignes.csv"))}


def _statut_reprise(decisions: list[str], origine: str) -> str:
    """Traitement, par la dimension destinataire, d'une ligne qui lui est renvoyée (D38 a, D46)."""
    if "fiche" in decisions:
        return "fiche"
    if any(d.startswith("variante_de:") for d in decisions):
        return "variante"
    if "ecarte_en_bloc" in decisions:
        return "ecartee"
    relais = sorted({d.split(":", 1)[1] for d in decisions if d.startswith("autre_dimension:")} - {origine})
    if relais:
        return "relayee:" + relais[0]
    return "orpheline"


def lignes_renvoyees(preselections: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Une ligne par renvoi `autre_dimension:<destination>` : origine, destination, ligne et statut de reprise
    (`fiche`, `variante`, `ecartee`, `relayee:<dim>` = renvoyée plus loin par une règle motivée, `orpheline`)."""
    decisions: dict[str, dict[str, list[str]]] = {}
    for dim, df in preselections.items():
        par_ligne: dict[str, list[str]] = defaultdict(list)
        for lid, dec in zip(df["ligne_id"], df["decision"]):
            par_ligne[lid].append(dec)
        decisions[dim] = par_ligne
    rangs = []
    for origine, df in preselections.items():
        renvois = df[df["decision"].str.startswith("autre_dimension:")]
        for r in renvois.to_dict("records"):
            destination = r["decision"].split(":", 1)[1]
            statut = _statut_reprise(decisions.get(destination, {}).get(r["ligne_id"], []), origine)
            rangs.append({"origine": origine, "destination": destination, "ligne_id": r["ligne_id"],
                          "longlist": r["longlist"], "groupe": r["groupe"], "serie_id": r["serie_id"],
                          "libelle": r["libelle"], "statut": statut})
    colonnes = ["origine", "destination", "ligne_id", "longlist", "groupe", "serie_id", "libelle", "statut"]
    return pd.DataFrame(rangs, columns=colonnes)


def lignes_retenues_et_ecartees(preselections: dict[str, pd.DataFrame]) -> list[dict]:
    """Lignes retenues (fiche ou variante) dans une dimension et écartées en bloc dans une autre (D46)."""
    usages: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for dim, df in preselections.items():
        for lid, dec, groupe in zip(df["ligne_id"], df["decision"], df["groupe"]):
            usages[lid].append((dim, dec, groupe))
    conflits = []
    for lid, us in usages.items():
        retenues = [u for u in us if u[1] == "fiche" or u[1].startswith("variante_de:")]
        ecartees = [u for u in us if u[1] == "ecarte_en_bloc"]
        for dim_r, _, groupe_r in retenues:
            for dim_e, _, groupe_e in ecartees:
                if dim_r != dim_e:
                    conflits.append({"ligne_id": lid, "retenue_dans": dim_r, "groupe_retenu": groupe_r,
                                     "ecartee_dans": dim_e, "groupe_ecarte": groupe_e})
    return conflits


def controler_lignes_renvoyees(dimension: str, rapport: Rapport, preselections: dict[str, pd.DataFrame]) -> None:
    """D46 : avertit pour chaque groupe de lignes renvoyées à la dimension et non reprises, et pour chaque ligne
    écartée en bloc ici alors qu'une autre dimension la retient (fiche ou variante). La dimension qui retient la
    ligne n'est pas avertie (l'écart est à motiver ou à corriger là où il est écrit) ; elle en garde le compte."""
    renvois = lignes_renvoyees(preselections)
    recues = renvois[renvois["destination"] == dimension]
    orphelines = recues[recues["statut"] == "orpheline"]
    for (origine, groupe), sel in orphelines.groupby(["origine", "groupe"], sort=True):
        exemples = ", ".join(sel["ligne_id"].head(5)) + (" …" if len(sel) > 5 else "")
        rapport.avertir("lignes renvoyées", f"{len(sel)} ligne(s) renvoyée(s) par {origine} (groupe {groupe}) non "
                                            f"reprises (D46) : {exemples}")
    rapport.compteurs["lignes_recues"] = len(recues)
    rapport.compteurs["lignes_recues_orphelines"] = len(orphelines)
    ecartees_ici, retenues_ici = 0, 0
    for c in lignes_retenues_et_ecartees(preselections):
        if c["ecartee_dans"] == dimension:
            rapport.avertir(c["groupe_ecarte"], f"ligne {c['ligne_id']} écartée ici et retenue par "
                                                f"{c['retenue_dans']}/{c['groupe_retenu']} (D46)")
            ecartees_ici += 1
        elif c["retenue_dans"] == dimension:
            retenues_ici += 1
    rapport.compteurs["lignes_ecartees_retenues_ailleurs"] = ecartees_ici
    rapport.compteurs["lignes_retenues_ecartees_ailleurs"] = retenues_ici


def controler_socle(fiches: list[dict], dimension: str, rapport: Rapport) -> None:
    """D41 : socle proposé (incontournables et une fiche principale par sous-thème, 8 au plus) ; D38 d.

    - `socle_propose` obligatoire sur toute fiche (avertissement dans une dimension de transition) ;
    - `oui` réservé aux variantes principales recommandées `retenir` ; 8 `oui` au plus ;
    - variante principale `retenir` et incontournable → `oui`, sauf `derogation_socle: <motif>` écrite dans la fiche ;
      sans dérogation, erreur, ou avertissement si la limite de 8 est déjà atteinte."""
    for f in fiches:
        if f.get("incontournable") == "oui" and f.get("variante_principale") != "oui":
            rapport.avertir(f.get("id"), "incontournable: oui sur une fiche non principale (D38 d : porté par la "
                                         "variante principale seulement)")
    transition = dimension in DIMENSIONS_SOCLE_TRANSITOIRE
    sans_champ = sorted(f.get("id") for f in fiches if "socle_propose" not in f)
    if sans_champ:
        if transition:
            rapport.avertir("socle", f"champ socle_propose absent de {len(sans_champ)} fiche(s) (D41) : admis tant "
                                     "que la correction de la dimension n'est pas fusionnée")
        else:
            for fid in sans_champ:
                rapport.erreur(fid, "champ socle_propose obligatoire (D41, méthode 33 v1.3)")
    socle = sorted(f.get("id") for f in fiches if f.get("socle_propose") == "oui")
    plein = len(socle) >= SOCLE_MAX
    derogations = []
    for f in fiches:
        if "socle_propose" not in f:
            continue
        principale = f.get("variante_principale") == "oui"
        valeur = f.get("socle_propose")
        if valeur == "oui" and not principale:
            rapport.erreur(f.get("id"), "socle_propose: oui réservé aux variantes principales (D41)")
        elif valeur == "oui" and f.get("recommandation") != "retenir":
            rapport.erreur(f.get("id"), "socle_propose: oui exige la recommandation « retenir » (D41)")
        hors_socle = (principale and f.get("incontournable") == "oui" and f.get("recommandation") == "retenir"
                      and valeur != "oui")
        derogation = f.get("derogation_socle")
        if hors_socle and derogation:
            derogations.append(f.get("id"))
        elif hors_socle and plein:
            rapport.avertir(f.get("id"), f"incontournable hors du socle proposé, limite de {SOCLE_MAX} atteinte : "
                                         "écrire la dérogation dans la fiche (derogation_socle, D41)")
        elif hors_socle:
            rapport.erreur(f.get("id"), "variante principale incontournable : socle_propose: oui attendu, ou "
                                        "dérogation écrite dans la fiche (derogation_socle, D41)")
        elif derogation:
            rapport.avertir(f.get("id"), "derogation_socle sans objet (fiche au socle, non principale, non "
                                         "incontournable ou non retenue)")
    if len(socle) > SOCLE_MAX:
        rapport.erreur("socle", f"{len(socle)} fiches socle_propose: oui ({SOCLE_MAX} au plus par dimension, D41)")
    rapport.compteurs["socle_propose"] = socle
    if derogations:
        rapport.compteurs["derogations_socle"] = sorted(derogations)


def controler_familles(fiches: list[dict], rapport: Rapport) -> None:
    familles = defaultdict(list)
    for f in fiches:
        familles[f.get("famille")].append(f)
    for famille, membres in familles.items():
        principales = [f for f in membres if f.get("variante_principale") == "oui"]
        if len(principales) != 1:
            rapport.erreur(f"famille {famille}", f"{len(principales)} variante(s) principale(s) (une attendue)")
        for f in membres:
            reco = f.get("recommandation")
            if f.get("variante_principale") == "oui" and reco == "retenir_variante":
                rapport.erreur(f.get("id"), "variante principale recommandée « retenir_variante »")
            if f.get("variante_principale") == "non" and reco == "retenir":
                rapport.erreur(f.get("id"), "variante non principale recommandée « retenir » (attendu retenir_variante)")


def controler_couverture(racine: Path, dimension: str, fiches: list[dict], rapport: Rapport) -> None:
    chemin = racine / "docs" / "validation" / f"preselection_{dimension}_lignes.csv"
    if not chemin.exists():
        rapport.avertir("présélection", f"{chemin.name} absent : couverture non contrôlée")
        return
    lignes = pd.read_csv(chemin, dtype=str, keep_default_na=False)
    longlist = None
    for nom in (f"longlist_{dimension}.csv.gz", f"longlist_{dimension}.csv"):
        if (racine / "catalogues" / nom).exists():
            longlist = pd.read_csv(racine / "catalogues" / nom, dtype=str, keep_default_na=False, usecols=["ligne_id"])
            break
    if longlist is not None:
        propres = set(lignes.loc[lignes["longlist"] == dimension, "ligne_id"])
        manquantes = sorted(set(longlist["ligne_id"]) - propres)
        if manquantes:
            rapport.erreur("présélection", f"{len(manquantes)} ligne(s) de la long-list non affectée(s) : "
                                           f"{', '.join(manquantes[:10])}")
        rapport.compteurs["lignes_longlist"] = len(longlist)
    decisions = lignes["decision"].str.split(":").str[0]
    rapport.compteurs["lignes_autre_dimension"] = int((decisions == "autre_dimension").sum())
    par_id = {f.get("id"): f for f in fiches}
    groupes_fiche = set(lignes.loc[lignes["decision"] == "fiche", "groupe"])
    for groupe in sorted(groupes_fiche - set(par_id)):
        rapport.erreur("présélection", f"groupe « fiche » sans fiche : {groupe}")
    for fid, f in par_id.items():
        if f.get("hors_longlist") != "oui" and fid not in groupes_fiche:
            rapport.erreur(fid, "aucune ligne de présélection en décision « fiche » pour cette fiche")
        attendues = set(lignes.loc[(lignes["fiche"] == fid) & lignes["decision"].str.startswith("variante_de:"),
                                   "ligne_id"])
        presentes = {v.get("ligne_id") for v in f.get("variantes") or [] if v.get("ligne_id")}
        if attendues != presentes:
            rapport.erreur(fid, f"variantes différentes de la présélection ({len(presentes)} contre {len(attendues)}) : "
                                "relancer scripts/preselection.py --maj-fiches")


def premiere_phrase(texte: str, limite: int = 220) -> str:
    texte = " ".join(texte.split())
    coupe = _RE_FIN_PHRASE.search(texte)
    phrase = texte[:coupe.end()] if coupe else texte
    if len(phrase) > limite:
        phrase = phrase[:limite].rsplit(" ", 1)[0] + " …"
    return phrase


def ligne_tableau(f: dict) -> dict:
    nb = f.get("nb_points_depuis_2000")
    periode = f"{f.get('premiere_annee')}-{f.get('derniere_annee')}"
    periode += f" ({nb} points, {f.get('frequence')})" if nb is not None else f" ({f.get('frequence')})"
    return {
        "id": f.get("id"), "libelle": f.get("libelle"), "sous_theme": f.get("sous_theme"), "famille": f.get("famille"),
        "variante_principale": f.get("variante_principale"), "definition_courte": premiere_phrase(f.get("definition", "")),
        "sens": f.get("sens"), "unite": f.get("unite"),
        "source": f"{f.get('source_organisme')} — {f.get('source_jeu')}", "serie_id": f.get("source_serie_id"),
        "periode": periode, "type": f.get("type"), "declaratif": f.get("declaratif"), "composite": f.get("composite"),
        "incontournable": f.get("incontournable"), "socle_propose": f.get("socle_propose", ""),
        "recommandation": f.get("recommandation"), "motif": f.get("motif_recommandation"),
        "decision_leo": "", "commentaire_leo": "",
    }


class DecisionsPerdues(ValueError):
    """La réécriture du tableau ferait disparaître des décisions de Léo."""


def ecrire_tableau(racine: Path, dimension: str, fiches: list[dict]) -> Path:
    """(Ré)écrit le tableau de validation au format v1.3. Les colonnes `decision_leo` et `commentaire_leo` déjà
    saisies sont reportées par identifiant ; si une ligne qui porte une décision ou un commentaire n'a plus de fiche
    (fiche supprimée ou renommée), rien n'est écrit (`DecisionsPerdues`)."""
    chemin = racine / "docs" / "validation" / f"validation_{dimension}.csv"
    anciennes = {}
    if chemin.exists():
        ancien = pd.read_csv(chemin, dtype=str, keep_default_na=False)
        anciennes = {r["id"]: r for r in ancien.to_dict("records")}
    ids = {f.get("id") for f in fiches}
    perdues = sorted(i for i, r in anciennes.items()
                     if i not in ids and any((r.get(c) or "").strip() for c in COLONNES_LEO))
    if perdues:
        raise DecisionsPerdues(f"{chemin.name} : décision(s) de Léo sans fiche correspondante ({', '.join(perdues)}) ; "
                               "reporter la décision sur la nouvelle fiche avant de réécrire le tableau")
    rangs = []
    cle = lambda f: (f.get("sous_theme", ""), f.get("famille", ""), f.get("variante_principale") != "oui", f.get("id"))
    for f in sorted(fiches, key=cle):
        rang = ligne_tableau(f)
        if rang["id"] in anciennes:
            rang["decision_leo"] = anciennes[rang["id"]].get("decision_leo", "")
            rang["commentaire_leo"] = anciennes[rang["id"]].get("commentaire_leo", "")
        rangs.append(rang)
    df = pd.DataFrame(rangs, columns=COLONNES_TABLEAU)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(chemin, index=False, lineterminator="\n")
    return chemin


def controler_tableau(racine: Path, dimension: str, fiches: list[dict], rapport: Rapport) -> None:
    chemin = racine / "docs" / "validation" / f"validation_{dimension}.csv"
    if not chemin.exists():
        rapport.avertir("tableau", f"{chemin.name} absent (option --tableau pour le produire)")
        return
    df = pd.read_csv(chemin, dtype=str, keep_default_na=False)
    colonnes = COLONNES_TABLEAU
    if list(df.columns) == COLONNES_TABLEAU_V12:
        rapport.avertir("tableau", "format antérieur à la méthode v1.3 (sans sous_theme ni socle_propose) : "
                                   "relancer avec --tableau (les décisions de Léo sont conservées)")
        colonnes = COLONNES_TABLEAU_V12
    elif list(df.columns) != COLONNES_TABLEAU:
        rapport.erreur("tableau", f"colonnes inattendues : {list(df.columns)}")
        return
    if df["id"].duplicated().any():
        rapport.erreur("tableau", "identifiants en double")
    par_id = {f.get("id"): f for f in fiches}
    if set(df["id"]) != set(par_id):
        rapport.erreur("tableau", "les lignes du tableau ne correspondent pas aux fiches")
    for r in df.to_dict("records"):
        f = par_id.get(r["id"])
        if f is None:
            continue
        attendu = ligne_tableau(f)
        for col in colonnes[:-2]:
            if str(attendu[col]) != r[col]:
                rapport.erreur(r["id"], f"tableau de validation : colonne {col} différente de la fiche "
                                        "(relancer avec --tableau)")
                break
        if r["decision_leo"] not in DECISIONS_LEO:
            rapport.erreur(r["id"], f"decision_leo non admise : {r['decision_leo']!r}")


def verifier_dimension(racine: Path, dimension: str, catalogues: bool = True) -> Rapport:
    rapport = Rapport(dimension)
    lues = lire_fiches(racine, dimension)
    if not lues:
        rapport.erreur(dimension, f"aucune fiche dans indicateurs/{dimension}/")
        return rapport
    for chemin, fiche in lues:
        controler_schema(fiche, chemin, dimension, rapport)
    fiches = [f for _, f in lues]
    for fid, n in ids_toutes_dimensions(racine).items():
        if n > 1 and fid in {f.get("id") for f in fiches}:
            rapport.erreur(fid, f"identifiant présent {n} fois dans indicateurs/")
    controler_familles(fiches, rapport)
    controler_socle(fiches, dimension, rapport)
    if catalogues:
        series, jeux = index_catalogues(racine)
        paquets = index_paquets(series) if any(f.get("composantes") for f in fiches) else None
        for f in fiches:
            controler_catalogues(f, rapport, series, jeux, racine, paquets)
    controler_couverture(racine, dimension, fiches, rapport)
    controler_lignes_croisees(racine, dimension, rapport)
    controler_lignes_renvoyees(dimension, rapport, lire_preselections(racine))
    controler_tableau(racine, dimension, fiches, rapport)
    reco = Counter(f.get("recommandation") for f in fiches)
    rapport.compteurs.update({
        "fiches": len(fiches), "familles": len({f.get("famille") for f in fiches}),
        "retenir": reco.get("retenir", 0), "retenir_variante": reco.get("retenir_variante", 0),
        "ecarter": reco.get("ecarter", 0),
        "declaratifs": sum(f.get("declaratif") == "oui" for f in fiches),
        "composites": sum(f.get("composite") == "oui" for f in fiches),
        "a_verifier": sum(f.get("eligibilite_longlist") == "a_verifier" for f in fiches),
        "hors_longlist": sum(f.get("hors_longlist") == "oui" for f in fiches),
        "incontournables": sorted(f.get("id") for f in fiches if f.get("incontournable") == "oui"),
        "variantes": sum(len(f.get("variantes") or []) for f in fiches),
    })
    return rapport


def rapport_lignes_renvoyees(racine: Path, limite: int = 0) -> list[str]:
    """Bilan des renvois `autre_dimension:<dim>` par couple (origine → destination) : reprises par la destination
    (fiche, variante, écart en bloc, renvoi plus loin) et lignes orphelines (D46), puis lignes retenues dans une
    dimension et écartées dans une autre. `limite` > 0 : nombre maximal de lignes orphelines listées par couple."""
    preselections = lire_preselections(racine)
    renvois = lignes_renvoyees(preselections)
    sorties = ["Lignes renvoyées (autre_dimension:<dim>) — origine → destination : renvoyées ; fiche, variante, "
               "écartées, relayées ; orphelines"]
    total = 0
    for (origine, destination), sel in renvois.groupby(["origine", "destination"], sort=True):
        statuts = sel["statut"].str.split(":").str[0].value_counts()
        n_orph = int(statuts.get("orpheline", 0))
        total += n_orph
        sorties.append(f"{origine} → {destination} : {len(sel)} ; {int(statuts.get('fiche', 0))}, "
                       f"{int(statuts.get('variante', 0))}, {int(statuts.get('ecartee', 0))}, "
                       f"{int(statuts.get('relayee', 0))} ; {n_orph}")
    for (origine, destination), sel in renvois[renvois["statut"] == "orpheline"].groupby(["origine", "destination"],
                                                                                          sort=True):
        sorties.append("")
        sorties.append(f"Orphelines {origine} → {destination} ({len(sel)}) :")
        for r in (sel.head(limite) if limite > 0 else sel).to_dict("records"):
            sorties.append(f"  {r['ligne_id']} [{r['groupe']}] {r['serie_id'][:80]} — {r['libelle'][:90]}")
        if 0 < limite < len(sel):
            sorties.append(f"  … {len(sel) - limite} autre(s)")
    par_destination = renvois[renvois["statut"] == "orpheline"].groupby("destination").size()
    if len(par_destination):
        sorties.append("")
        sorties.append("Orphelines par destination : " + ", ".join(f"{d} {n}" for d, n in par_destination.items()))
    conflits = lignes_retenues_et_ecartees(preselections)
    sorties.append("")
    sorties.append(f"Lignes retenues dans une dimension et écartées dans une autre : {len(conflits)}")
    for c in conflits:
        sorties.append(f"  {c['ligne_id']} : retenue par {c['retenue_dans']}/{c['groupe_retenu']}, écartée par "
                       f"{c['ecartee_dans']}/{c['groupe_ecarte']}")
    sorties.append("")
    sorties.append(f"{total} ligne(s) orpheline(s), {len(conflits)} ligne(s) retenue(s) et écartée(s)")
    return sorties


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dimension")
    parser.add_argument("--racine", default=str(RACINE))
    parser.add_argument("--tableau", action="store_true", help="(ré)écrire docs/validation/validation_<dim>.csv")
    parser.add_argument("--sans-catalogues", action="store_true", help="ne pas contrôler la présence dans les catalogues")
    parser.add_argument("--lignes-renvoyees", action="store_true",
                        help="bilan des lignes renvoyées par couple de dimensions et des lignes orphelines (D46)")
    parser.add_argument("--limite", type=int, default=0,
                        help="avec --lignes-renvoyees : nombre maximal de lignes orphelines listées par couple")
    parser.add_argument("--sortie", help="avec --lignes-renvoyees : écrit le détail des renvois (une ligne par "
                                         "renvoi, avec son statut) dans ce fichier CSV")
    args = parser.parse_args(argv)
    racine = Path(args.racine)
    if args.lignes_renvoyees:
        print("\n".join(rapport_lignes_renvoyees(racine, args.limite)))
        if args.sortie:
            lignes_renvoyees(lire_preselections(racine)).to_csv(args.sortie, index=False, lineterminator="\n")
            print(f"détail écrit : {args.sortie}")
        if not args.dimension:
            return 0
    if not args.dimension:
        parser.error("--dimension est obligatoire (sauf avec --lignes-renvoyees)")
    if args.tableau:
        fiches = [f for _, f in lire_fiches(racine, args.dimension)]
        try:
            print(f"tableau écrit : {ecrire_tableau(racine, args.dimension, fiches).relative_to(racine)}")
        except DecisionsPerdues as exc:
            print(f"ERREUR — {exc}", file=sys.stderr)
            return 1
    rapport = verifier_dimension(racine, args.dimension, catalogues=not args.sans_catalogues)
    print(f"Dimension {args.dimension} : " + ", ".join(f"{k} {v}" for k, v in rapport.compteurs.items()))
    for message in rapport.avertissements:
        print(f"avertissement — {message}")
    for message in rapport.erreurs:
        print(f"ERREUR — {message}", file=sys.stderr)
    print(f"{len(rapport.erreurs)} erreur(s), {len(rapport.avertissements)} avertissement(s)")
    return 1 if rapport.erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
