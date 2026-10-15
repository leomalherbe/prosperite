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

Usage :
    python scripts/verifier_fiches.py --dimension liens_bien_etre
    python scripts/verifier_fiches.py --dimension liens_bien_etre --tableau   # (ré)écrit le tableau de validation
Les décisions de Léo déjà saisies dans le tableau sont conservées lors de la réécriture.
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
}
COLONNES_TABLEAU = ["id", "libelle", "famille", "variante_principale", "definition_courte", "sens", "unite", "source",
                    "serie_id", "periode", "type", "declaratif", "composite", "incontournable", "recommandation",
                    "motif", "decision_leo", "commentaire_leo"]
DECISIONS_LEO = {"", "retenu", "retenu_socle", "ecarte", "a_discuter"}
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
    jeux: set[str] = set()
    chemin_jeux = dossier / "eurostat_jeux_catalogue.csv"
    if chemin_jeux.exists():
        jeux.update(pd.read_csv(chemin_jeux, dtype=str, keep_default_na=False, usecols=["code_jeu"])["code_jeu"])
    return series, jeux


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
    for serie in principales:
        if serie in series:
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
        if serie in series:
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
        "id": f.get("id"), "libelle": f.get("libelle"), "famille": f.get("famille"),
        "variante_principale": f.get("variante_principale"), "definition_courte": premiere_phrase(f.get("definition", "")),
        "sens": f.get("sens"), "unite": f.get("unite"),
        "source": f"{f.get('source_organisme')} — {f.get('source_jeu')}", "serie_id": f.get("source_serie_id"),
        "periode": periode, "type": f.get("type"), "declaratif": f.get("declaratif"), "composite": f.get("composite"),
        "incontournable": f.get("incontournable"), "recommandation": f.get("recommandation"),
        "motif": f.get("motif_recommandation"), "decision_leo": "", "commentaire_leo": "",
    }


def ecrire_tableau(racine: Path, dimension: str, fiches: list[dict]) -> Path:
    chemin = racine / "docs" / "validation" / f"validation_{dimension}.csv"
    anciennes = {}
    if chemin.exists():
        ancien = pd.read_csv(chemin, dtype=str, keep_default_na=False)
        anciennes = {r["id"]: r for r in ancien.to_dict("records")}
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
    if list(df.columns) != COLONNES_TABLEAU:
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
        for col in COLONNES_TABLEAU[:-2]:
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
    if catalogues:
        series, jeux = index_catalogues(racine)
        paquets = index_paquets(series) if any(f.get("composantes") for f in fiches) else None
        for f in fiches:
            controler_catalogues(f, rapport, series, jeux, racine, paquets)
    controler_couverture(racine, dimension, fiches, rapport)
    controler_lignes_croisees(racine, dimension, rapport)
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dimension", required=True)
    parser.add_argument("--racine", default=str(RACINE))
    parser.add_argument("--tableau", action="store_true", help="(ré)écrire docs/validation/validation_<dim>.csv")
    parser.add_argument("--sans-catalogues", action="store_true", help="ne pas contrôler la présence dans les catalogues")
    args = parser.parse_args(argv)
    racine = Path(args.racine)
    if args.tableau:
        fiches = [f for _, f in lire_fiches(racine, args.dimension)]
        print(f"tableau écrit : {ecrire_tableau(racine, args.dimension, fiches).relative_to(racine)}")
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
