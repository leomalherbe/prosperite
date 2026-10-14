"""Présélection d'une dimension (mission M05, tâche 1) : long-list → concepts → fiches.

Le script applique un fichier de règles ordonnées (`docs/validation/regles_preselection_<dimension>.csv`)
aux lignes de la long-list de la dimension (`catalogues/longlist_<dimension>.csv.gz`) : chaque ligne reçoit
la **première** règle qui la décrit. Une règle définit un **groupe** de lignes et sa décision :

- `fiche` : le groupe porte la série principale d'une fiche indicateur (`fiche` = identifiant de la fiche) ;
- `variante_de:<id>` : le groupe réunit des variantes de la fiche `<id>` (ventilations, autre source,
  autre unité, complément…) ; elles seront listées dans le champ `variantes` de la fiche ;
- `ecarte_en_bloc` : sous-séries sans intérêt propre ou non éligibles, écartées avec un motif.

Colonnes du fichier de règles (CSV UTF-8, virgule) :
    ordre, groupe, decision, nature, motif, longlist, catalogue, motif_ligne_id, motif_serie_id,
    motif_libelle, hors_longlist
- `motif_*` et `catalogue` sont des expressions régulières (recherche, pas égalité ; vide = toute ligne) ;
  `motif_libelle` est insensible à la casse ; toutes les conditions non vides doivent être remplies.
- `longlist` vide = la dimension traitée ; sinon une autre dimension : la règle **importe** de sa long-list
  les lignes qu'elle décrit (rattachement proposé, à trancher par la session mère).
- `hors_longlist = oui` : concept sans ligne dans les long-lists (série vérifiée à la source) ; la règle ne
  s'applique à aucune ligne mais produit une ligne de présélection (0 ligne regroupée).

Sorties (dans `docs/validation/`) :
- `preselection_<dimension>.csv` : une ligne par groupe (décision, motif, nombre de lignes, exemples) ;
- `preselection_<dimension>_lignes.csv` : une ligne par ligne de long-list (groupe, décision, fiche).
Toute ligne de la long-list de la dimension sans règle fait échouer le script (code 1).

Option `--maj-fiches` : réécrit le champ `variantes` des fiches `indicateurs/<dimension>/*.yaml` à partir
de la présélection (les entrées sans `ligne_id`, ajoutées à la main pour des séries hors long-list, sont
conservées).

Usage :
    python scripts/preselection.py --dimension liens_bien_etre
    python scripts/preselection.py --dimension liens_bien_etre --maj-fiches
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd
import yaml

RACINE = Path(__file__).resolve().parent.parent
COLONNES_REGLES = ["ordre", "groupe", "decision", "nature", "motif", "longlist", "catalogue",
                   "motif_ligne_id", "motif_serie_id", "motif_libelle", "hors_longlist"]
COLONNES_PRESELECTION = ["groupe", "decision", "fiche", "nature", "motif", "nb_lignes", "nb_eligibles",
                         "nb_a_verifier", "nb_non_eligibles", "longlist", "catalogues", "exemples_serie_id",
                         "regle"]
COLONNES_LIGNES = ["ligne_id", "longlist", "groupe", "decision", "fiche", "nature", "serie_id", "source",
                   "catalogue_origine", "libelle", "eligible", "motif_exclusion", "regle"]
_RE_DECISION = re.compile(r"^(fiche|ecarte_en_bloc|variante_de:[a-z0-9_]+)$")
_RE_ID = re.compile(r"^[a-z][a-z0-9_]*$")


class ErreurRegles(ValueError):
    """Fichier de règles invalide."""


def lire_longlist(racine: Path, dimension: str) -> pd.DataFrame:
    """Lit `catalogues/longlist_<dimension>.csv.gz` (à défaut le `.csv` en clair)."""
    for nom in (f"longlist_{dimension}.csv.gz", f"longlist_{dimension}.csv"):
        chemin = racine / "catalogues" / nom
        if chemin.exists():
            df = pd.read_csv(chemin, dtype=str, keep_default_na=False)
            df["longlist"] = dimension
            return df
    raise FileNotFoundError(f"long-list introuvable pour la dimension {dimension}")


def lire_regles(chemin: Path) -> list[dict]:
    df = pd.read_csv(chemin, dtype=str, keep_default_na=False)
    manquantes = [c for c in COLONNES_REGLES if c not in df.columns]
    if manquantes:
        raise ErreurRegles(f"colonnes absentes du fichier de règles : {', '.join(manquantes)}")
    regles = []
    vus = set()
    for r in df.to_dict("records"):
        r = {k: (v or "").strip() for k, v in r.items()}
        if not r["ordre"].isdigit():
            raise ErreurRegles(f"ordre non entier : {r['ordre']!r} (groupe {r['groupe']})")
        r["ordre"] = int(r["ordre"])
        if not _RE_ID.match(r["groupe"]):
            raise ErreurRegles(f"identifiant de groupe invalide : {r['groupe']!r}")
        if r["groupe"] in vus:
            raise ErreurRegles(f"groupe en double : {r['groupe']}")
        vus.add(r["groupe"])
        if not _RE_DECISION.match(r["decision"]):
            raise ErreurRegles(f"décision invalide pour {r['groupe']} : {r['decision']!r}")
        if not r["motif"]:
            raise ErreurRegles(f"motif vide pour le groupe {r['groupe']}")
        if r["hors_longlist"] not in ("", "oui", "non"):
            raise ErreurRegles(f"hors_longlist doit valoir oui ou non ({r['groupe']})")
        for champ in ("catalogue", "motif_ligne_id", "motif_serie_id", "motif_libelle"):
            if r[champ]:
                try:
                    re.compile(r[champ])
                except re.error as exc:
                    raise ErreurRegles(f"expression invalide ({r['groupe']}, {champ}) : {exc}") from exc
        regles.append(r)
    regles.sort(key=lambda r: r["ordre"])
    fiches = {r["groupe"] for r in regles if r["decision"] == "fiche"}
    for r in regles:
        if r["decision"].startswith("variante_de:") and r["decision"].split(":", 1)[1] not in fiches:
            raise ErreurRegles(f"{r['groupe']} : variante d'une fiche inconnue ({r['decision']})")
    return regles


def fiche_de(regle: dict) -> str:
    if regle["decision"] == "fiche":
        return regle["groupe"]
    if regle["decision"].startswith("variante_de:"):
        return regle["decision"].split(":", 1)[1]
    return ""


def _decrit(regle: dict, ligne: dict) -> bool:
    if regle["hors_longlist"] == "oui":
        return False
    conditions = (("catalogue", "catalogue_origine", 0), ("motif_ligne_id", "ligne_id", 0),
                  ("motif_serie_id", "serie_id", 0), ("motif_libelle", "libelle", re.IGNORECASE))
    for champ, colonne, drapeaux in conditions:
        if regle[champ] and not re.search(regle[champ], ligne.get(colonne, ""), drapeaux):
            return False
    return True


def affecter(racine: Path, dimension: str, regles: list[dict]) -> tuple[pd.DataFrame, list[str]]:
    """Affecte chaque ligne à sa première règle. Renvoie (lignes affectées, lignes sans règle)."""
    sorties, orphelines = [], []
    par_longlist: dict[str, list[dict]] = {}
    for r in regles:
        par_longlist.setdefault(r["longlist"] or dimension, []).append(r)
    for nom, regles_ll in par_longlist.items():
        lignes = lire_longlist(racine, nom).to_dict("records")
        for ligne in lignes:
            regle = next((r for r in regles_ll if _decrit(r, ligne)), None)
            if regle is None:
                if nom == dimension:
                    orphelines.append(ligne["ligne_id"])
                continue
            sorties.append({
                "ligne_id": ligne["ligne_id"], "longlist": nom, "groupe": regle["groupe"],
                "decision": regle["decision"], "fiche": fiche_de(regle), "nature": regle["nature"],
                "serie_id": ligne["serie_id"], "source": ligne["source"],
                "catalogue_origine": ligne["catalogue_origine"], "libelle": ligne["libelle"],
                "eligible": ligne["eligible"], "motif_exclusion": ligne["motif_exclusion"],
                "regle": regle["ordre"],
            })
    return pd.DataFrame(sorties, columns=COLONNES_LIGNES), orphelines


def synthese(regles: list[dict], lignes: pd.DataFrame, dimension: str) -> pd.DataFrame:
    rangs = []
    for r in regles:
        sel = lignes[lignes["groupe"] == r["groupe"]]
        exemples = " | ".join(sel["serie_id"].head(3))
        rangs.append({
            "groupe": r["groupe"], "decision": r["decision"], "fiche": fiche_de(r), "nature": r["nature"],
            "motif": r["motif"], "nb_lignes": len(sel), "nb_eligibles": int((sel["eligible"] == "oui").sum()),
            "nb_a_verifier": int((sel["eligible"] == "a_verifier").sum()),
            "nb_non_eligibles": int((sel["eligible"] == "non").sum()),
            "longlist": r["longlist"] or dimension, "catalogues": " ; ".join(sorted(set(sel["catalogue_origine"]))),
            "exemples_serie_id": exemples, "regle": r["ordre"],
        })
    return pd.DataFrame(rangs, columns=COLONNES_PRESELECTION)


def variantes_depuis_lignes(lignes: pd.DataFrame, fiche: str, dimension: str) -> list[dict]:
    sel = lignes[(lignes["fiche"] == fiche) & lignes["decision"].str.startswith("variante_de:")]
    variantes = []
    for r in sel.to_dict("records"):
        entree = {"serie_id": r["serie_id"], "source": r["source"], "nature": r["nature"],
                  "ligne_id": r["ligne_id"], "eligible": r["eligible"]}
        if r["longlist"] != dimension:
            entree["longlist"] = r["longlist"]
        variantes.append(entree)
    return variantes


class _Dumper(yaml.SafeDumper):
    """Met entre guillemets les chaînes d'allure numérique (idbank « 010593281 ») : un lecteur YAML 1.2
    (JavaScript, ruamel) les lirait sinon comme des nombres et perdrait le zéro initial."""


def _representer_texte(dumper: yaml.SafeDumper, texte: str):
    style = "'" if re.fullmatch(r"[0-9+\-.][0-9_.:+\-eE]*", texte) else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", texte, style=style)


_Dumper.add_representer(str, _representer_texte)


def texte_yaml(donnees: dict) -> str:
    return yaml.dump(donnees, Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=110,
                     default_flow_style=False)


def ecrire_yaml(chemin: Path, donnees: dict) -> None:
    chemin.write_text(texte_yaml(donnees), encoding="utf-8")


def maj_fiches(racine: Path, dimension: str, lignes: pd.DataFrame) -> list[str]:
    """Réécrit `variantes` dans chaque fiche de la dimension. Renvoie les fiches modifiées."""
    modifiees = []
    for chemin in sorted((racine / "indicateurs" / dimension).glob("*.yaml")):
        if chemin.name.startswith("_"):
            continue
        fiche = yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}
        manuelles = [v for v in (fiche.get("variantes") or []) if not v.get("ligne_id")]
        nouvelles = variantes_depuis_lignes(lignes, fiche.get("id", chemin.stem), dimension) + manuelles
        fiche["variantes"] = nouvelles
        if texte_yaml(fiche) != chemin.read_text(encoding="utf-8"):
            ecrire_yaml(chemin, fiche)
            modifiees.append(chemin.name)
    return modifiees


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dimension", required=True)
    parser.add_argument("--regles", help="fichier de règles (défaut : docs/validation/regles_preselection_<dim>.csv)")
    parser.add_argument("--racine", default=str(RACINE))
    parser.add_argument("--maj-fiches", action="store_true", help="réécrire le champ variantes des fiches")
    args = parser.parse_args(argv)

    racine = Path(args.racine)
    dossier = racine / "docs" / "validation"
    chemin_regles = Path(args.regles) if args.regles else dossier / f"regles_preselection_{args.dimension}.csv"
    regles = lire_regles(chemin_regles)
    lignes, orphelines = affecter(racine, args.dimension, regles)
    if orphelines:
        print(f"{len(orphelines)} ligne(s) de la long-list sans règle : {', '.join(orphelines[:20])}"
              + (" …" if len(orphelines) > 20 else ""), file=sys.stderr)
        return 1
    vides = [r["groupe"] for r in regles if r["hors_longlist"] != "oui" and not (lignes["groupe"] == r["groupe"]).any()]
    for groupe in vides:
        print(f"avertissement : la règle {groupe} ne décrit aucune ligne", file=sys.stderr)

    dossier.mkdir(parents=True, exist_ok=True)
    pre = synthese(regles, lignes, args.dimension)
    pre.to_csv(dossier / f"preselection_{args.dimension}.csv", index=False, lineterminator="\n")
    lignes.to_csv(dossier / f"preselection_{args.dimension}_lignes.csv", index=False, lineterminator="\n")

    importees = int((lignes["longlist"] != args.dimension).sum())
    print(f"{len(lignes)} lignes affectées ({importees} importées d'autres long-lists), {len(pre)} groupes : "
          + ", ".join(f"{k} {v}" for k, v in pre["decision"].str.split(":").str[0].value_counts().items()))
    if args.maj_fiches:
        modifiees = maj_fiches(racine, args.dimension, lignes)
        print(f"variantes réécrites dans {len(modifiees)} fiche(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
