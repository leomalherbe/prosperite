"""Construit docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv (mission M04, tâche T3).

Principe : chaque indicateur candidat est décrit ici (libellé, dimension v0, sens, déclaratif,
type, composite, doublon INSEE/Eurostat, commentaire) et **rattaché à une série repérée par le
robot** (fichiers docs/sources/series/*.csv|txt produits par scripts/collecte_sources.py, ou
extraits de phase 1 dans docs/sources/verif_acces/extraits/). Les années (première, dernière,
nombre de points depuis 2000) sont lues dans ces fichiers, jamais saisies à la main : si la série
n'est pas trouvée, la ligne est marquée `non_verifie` avec la raison.

Ce script est rangé hors de scripts/ pour ne pas déclencher le robot « Collecte » à chaque
modification. Exécution (hors ligne) : python docs/sources/outils/construire_candidats.py
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

COLONNES = ["indicateur", "dimension_v0", "source", "identifiant_ou_url", "unite", "sens", "declaratif",
            "frequence", "premiere_annee", "derniere_annee", "doublon_insee_eurostat", "commentaire",
            "composite", "type", "geo", "niveau_source", "fiabilite"]
DIMENSIONS = {"niveau_de_vie", "travail", "logement_cadre_vie", "sante", "education", "liens_bien_etre",
              "securite_confiance", "democratie", "egalites", "planete"}

LIGNES: list[dict] = []
_CACHE: dict[str, pd.DataFrame] = {}


# --------------------------------------------------------------------------- lecture des preuves


def table(fichier: str) -> pd.DataFrame:
    """Liste de séries produite par le robot (docs/sources/series/<fichier>.csv)."""
    if fichier not in _CACHE:
        chemin = SERIES / f"{fichier}.csv"
        _CACHE[fichier] = pd.read_csv(chemin, dtype=str).fillna("") if chemin.exists() else pd.DataFrame()
    return _CACHE[fichier]


def annees_de(periodes: str, n: int) -> list[int]:
    """Développe « 2000-2002,2005 » ; pour une période unique non annuelle (« 2015-2017 »), renvoie sa fin."""
    jetons = [j for j in periodes.split(",") if j and j != "…"]
    ans: list[int] = []
    for j in jetons:
        m = re.fullmatch(r"(\d{4})-(\d{4})", j)
        if m and n != 1:
            ans += list(range(int(m.group(1)), int(m.group(2)) + 1))
        elif re.fullmatch(r"\d{4}", j):
            ans.append(int(j))
        else:
            m = re.findall(r"(\d{4})", j)
            if m:
                ans.append(int(m[-1]))
    return sorted(set(ans))


def serie(fichier: str, **conditions) -> dict | None:
    """Première ligne de la liste `fichier` satisfaisant toutes les conditions.

    Conditions : id=<égalité sur serie_id>, id_debut=<préfixe>, id_motif=<regex>, lib_motif=<regex
    sur libelle>, det_motif=<regex sur details>, unite_motif=<regex sur unite>."""
    d = table(fichier)
    if d.empty:
        return None
    m = pd.Series(True, index=d.index)
    for k, v in conditions.items():
        if k == "id":
            m &= d.serie_id == v
        elif k == "id_debut":
            m &= d.serie_id.str.startswith(v)
        elif k == "id_motif":
            m &= d.serie_id.str.contains(v, regex=True)
        elif k == "lib_motif":
            m &= d.libelle.str.contains(v, regex=True)
        elif k == "det_motif":
            m &= d.details.str.contains(v, regex=True)
        elif k == "unite_motif":
            m &= d.unite.str.contains(v, regex=True)
    x = d[m]
    if x.empty:
        return None
    r = x.iloc[0]
    n = int(r.n_periodes or 0)
    return {"annees": annees_de(r.periodes, n), "n": n, "n_distinctes": int(r.n_valeurs_distinctes or 0),
            "derniere_valeur": r.derniere_valeur, "unite_source": r.unite, "libelle_source": r.libelle,
            "serie_id": r.serie_id, "preuve": f"docs/sources/series/{fichier}.csv"}


def serie_banque_mondiale_phase1(code: str) -> dict | None:
    """Extrait JSON de phase 1 (docs/sources/verif_acces/extraits/banque_mondiale__<code>.txt)."""
    nom = "banque_mondiale__" + re.sub(r"[^a-z0-9_-]+", "_", code.lower()) + ".txt"
    chemin = EXTRAITS / nom
    if not chemin.exists():
        return None
    texte = chemin.read_text(encoding="utf-8")
    try:
        donnees = json.loads(texte[texte.index("["):])
    except ValueError:
        return None
    if len(donnees) < 2 or not donnees[1]:
        return None
    obs = {int(o["date"]): o["value"] for o in donnees[1] if o.get("value") is not None}
    if not obs:
        return None
    ans = sorted(obs)
    return {"annees": ans, "n": len(ans), "n_distinctes": len(set(obs.values())), "derniere_valeur": obs[ans[-1]],
            "unite_source": "", "libelle_source": donnees[1][0]["indicator"]["value"], "serie_id": code,
            "preuve": f"docs/sources/verif_acces/extraits/{nom}"}


def annees_texte(fichier: str, motif: str, groupe_annee: int = 1) -> dict | None:
    """Années lues dans une sortie texte du robot (mode lignes/colonne) : motif regex à un groupe année."""
    chemin = SERIES / f"{fichier}.txt"
    if not chemin.exists():
        return None
    ans = sorted({int(m.group(groupe_annee)) for m in re.finditer(motif, chemin.read_text(encoding="utf-8"))})
    if not ans:
        return None
    return {"annees": ans, "n": len(ans), "n_distinctes": 0, "derniere_valeur": "", "unite_source": "",
            "libelle_source": "", "serie_id": "", "preuve": f"docs/sources/series/{fichier}.txt"}


# --------------------------------------------------------------------------- construction des lignes


def frequence_de(ans: list[int]) -> str:
    if len(ans) <= 1:
        return "ponctuelle"
    pas = {b - a for a, b in zip(ans, ans[1:])}
    if pas == {1}:
        return "annuelle"
    return "irreguliere"


def ajouter(indicateur: str, dimension: str, source: str, identifiant: str, unite: str, sens: str,
            declaratif: str, type_: str, composite: str, doublon: str, commentaire: str, s: dict | None,
            geo: str = "FR", niveau: str = "1", frequence: str | None = None, raison_absence: str = "",
            fiabilite: str | None = None) -> None:
    assert dimension in DIMENSIONS, dimension
    assert sens in ("haut", "bas", "ambigu"), sens
    assert declaratif in ("oui", "non") and composite in ("oui", "non"), indicateur
    assert type_ in ("resultat", "moyen", "pression"), type_
    assert doublon in ("oui", "non", "partiel"), doublon
    com = commentaire.strip()
    if s is None:
        fiab = fiabilite or "non_verifie"
        prem = der = "non trouvé"
        freq = frequence or "non trouvé"
        com = (com + " " if com else "") + f"Non vérifié : {raison_absence or 'série absente des réponses du robot'}."
    else:
        ans = s["annees"]
        depuis_2000 = [a for a in ans if a >= 2000]
        prem, der = (ans[0], ans[-1]) if ans else ("non trouvé", "non trouvé")
        freq = frequence or frequence_de(ans)
        notes = [f"{len(depuis_2000)} points depuis 2000"]
        if s.get("n_distinctes") and len(ans) >= 6 and s["n_distinctes"] <= len(ans) / 2:
            notes.append(f"seulement {s['n_distinctes']} valeurs distinctes (valeurs répétées)")
        com = (com + " " if com else "") + " ; ".join(notes) + f". Preuve : {s['preuve']}."
        fiab = fiabilite or "verifie"
    LIGNES.append({"indicateur": indicateur, "dimension_v0": dimension, "source": source,
                   "identifiant_ou_url": identifiant, "unite": unite, "sens": sens, "declaratif": declaratif,
                   "frequence": freq, "premiere_annee": prem, "derniere_annee": der,
                   "doublon_insee_eurostat": doublon, "commentaire": com, "composite": composite, "type": type_,
                   "geo": geo, "niveau_source": niveau, "fiabilite": fiab})


def ecrire() -> None:
    vus = set()
    for l in LIGNES:
        cle = (l["indicateur"], l["source"], l["identifiant_ou_url"])
        assert cle not in vus, f"doublon de ligne : {cle}"
        vus.add(cle)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES)
        w.writeheader()
        w.writerows(LIGNES)
    print(f"{len(LIGNES)} indicateurs candidats écrits dans {SORTIE.relative_to(RACINE)}")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import construire_candidats as cc  # module importé (et non __main__) : celui qu'utilisent les définitions
    import candidats_definitions  # noqa: F401  (remplit cc.LIGNES via ajouter())

    cc.ecrire()
