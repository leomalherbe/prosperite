"""Régénère la long-list commune (M05) sur GitHub Actions, workflow « Collecte ».

Ce script n'interroge aucune API : il relit les catalogues déjà collectés et produit
`catalogues/longlist_<dimension>.csv`, `catalogues/longlist_hors_grille.csv` et
`catalogues/longlist_bilan.json` (voir `src/pipeline/longlist.py` et
`docs/methodo/32_longlist_mode_emploi.md`).

Il existe surtout pour que le workflow, déclenché par un push sur la branche
`m05-longlist`, ait une cible propre (sinon il lancerait tous les scripts de collecte).
Il ne fait **rien** tant que les quatre catalogues d'entrée ne sont pas tous présents
(cas de la branche avant la fusion des catalogues INSEE et Eurostat dans `main`).
Dans la collecte mensuelle de `main` (ordre alphabétique des scripts), il passe après
`collecte_eurostat.py` et `collecte_insee.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from src.pipeline.longlist import CATALOGUES, main, resoudre_chemin  # noqa: E402


def catalogues_absents() -> list[str]:
    return [c.chemin for c in CATALOGUES if resoudre_chemin(RACINE, c.chemin) is None]


if __name__ == "__main__":
    absents = catalogues_absents()
    if absents:
        print("Long-list non régénérée : catalogues absents de la branche : " + ", ".join(absents))
        print("Rien à faire (ils arriveront par la fusion des branches de collecte dans main).")
        sys.exit(0)
    # Exécution finale : sorties compressées (.csv.gz) et bilan, commités par le workflow ;
    # les .csv en clair sont ignorés par git.
    sys.exit(main(["--dimension", "toutes", "--compresser", "--remarque", "régénérée par le robot de collecte"]))
