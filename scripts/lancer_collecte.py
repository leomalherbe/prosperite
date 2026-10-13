"""Lance les scripts de collecte (exécuté par GitHub Actions, workflow « Collecte »).

Chaque script de collecte est un fichier autonome `scripts/collecte_<source>.py`
(ex. collecte_insee.py, collecte_eurostat.py) qui écrit ses résultats dans
`catalogues/` ou `donnees/`. Ce lanceur les exécute un par un, journalise, et
continue en cas d'échec ; il renvoie un code de sortie non nul si au moins un
script a échoué (le commit des résultats partiels est fait par le workflow).

Usage :
    python scripts/lancer_collecte.py                 # tous les scripts
    python scripts/lancer_collecte.py --cible collecte_insee.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "scripts"


def scripts_disponibles() -> list[Path]:
    return sorted(p for p in DOSSIER.glob("collecte_*.py") if p.is_file())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cible", default="tous", help="nom d'un script collecte_*.py, ou 'tous'")
    args = parser.parse_args()

    scripts = scripts_disponibles()
    if args.cible != "tous":
        scripts = [p for p in scripts if p.name == args.cible]
        if not scripts:
            print(f"Aucun script nommé {args.cible} dans {DOSSIER}", file=sys.stderr)
            return 2
    if not scripts:
        print("Aucun script de collecte (scripts/collecte_*.py) : rien à faire.")
        return 0

    echecs = []
    for script in scripts:
        print(f"\n===== {script.name} =====", flush=True)
        debut = time.time()
        resultat = subprocess.run([sys.executable, str(script)], cwd=RACINE)
        duree = time.time() - debut
        etat = "OK" if resultat.returncode == 0 else f"ÉCHEC (code {resultat.returncode})"
        print(f"----- {script.name} : {etat} en {duree:.0f} s", flush=True)
        if resultat.returncode != 0:
            echecs.append(script.name)

    print("\nBilan :", "tous les scripts ont réussi" if not echecs else f"échecs : {', '.join(echecs)}")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
