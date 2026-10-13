"""Pilotage des robots GitHub Actions depuis une session Claude (sans `gh`).

Le bac à sable des sessions peut joindre api.github.com (authentification injectée
par le proxy) mais pas les serveurs de journaux de GitHub : les journaux de la
collecte sont donc écrits par le workflow dans `journaux/` et commités sur la
branche ; on les lit ensuite avec `git fetch` + `git show`.

Usage (depuis la racine du dépôt) :
    python scripts/actions.py lancer --branche m01-insee --cible collecte_insee.py
    python scripts/actions.py runs   --branche m01-insee            # derniers runs de la branche
    python scripts/actions.py suivre --run <id>                      # attend la fin, affiche les étapes
    python scripts/actions.py journal --branche m01-insee            # dernier journal de collecte de la branche
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.request

DEPOT = "leomalherbe/prosperite"
API = f"https://api.github.com/repos/{DEPOT}"
WORKFLOW = "collecte.yml"


def _api(chemin: str, methode: str = "GET", corps: dict | None = None) -> dict:
    donnees = json.dumps(corps).encode() if corps is not None else None
    req = urllib.request.Request(API + chemin, data=donnees, method=methode)
    req.add_header("Accept", "application/vnd.github+json")
    if donnees is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as rep:
        contenu = rep.read()
        return json.loads(contenu) if contenu else {}


def lancer(branche: str, cible: str) -> None:
    _api(f"/actions/workflows/{WORKFLOW}/dispatches", "POST", {"ref": branche, "inputs": {"cible": cible}})
    print(f"Collecte demandée sur la branche {branche} (cible : {cible}). Attente de l'apparition du run…")
    for _ in range(12):
        time.sleep(5)
        runs = _api(f"/actions/workflows/{WORKFLOW}/runs?branch={branche}&per_page=1").get("workflow_runs", [])
        if runs and runs[0]["status"] != "completed":
            print(f"Run {runs[0]['id']} : {runs[0]['html_url']}")
            return
    print("Run non encore visible ; utiliser `runs` pour le retrouver.")


def runs(branche: str | None, n: int = 5) -> None:
    filtre = f"&branch={branche}" if branche else ""
    for r in _api(f"/actions/runs?per_page={n}{filtre}").get("workflow_runs", []):
        print(f"{r['id']}  {r['name']:<10} {r['head_branch']:<20} {r['status']:<12} {r['conclusion'] or '-':<10} {r['created_at']}")


def suivre(run_id: int, delai: int = 20, max_minutes: int = 240) -> int:
    debut = time.time()
    while True:
        r = _api(f"/actions/runs/{run_id}")
        print(f"[{int(time.time() - debut)} s] {r['status']} {r['conclusion'] or ''}", flush=True)
        if r["status"] == "completed" or time.time() - debut > max_minutes * 60:
            break
        time.sleep(delai)
    for job in _api(f"/actions/runs/{run_id}/jobs").get("jobs", []):
        print(f"Job {job['name']} : {job['status']} / {job['conclusion']}")
        for etape in job["steps"]:
            print(f"   {etape['number']:>2}. {etape['name']:<40} {etape['status']:<10} {etape['conclusion'] or '-'}")
    return 0 if r.get("conclusion") == "success" else 1


def journal(branche: str) -> None:
    subprocess.run(["git", "fetch", "-q", "origin", branche], check=True)
    fichiers = subprocess.run(["git", "ls-tree", "--name-only", f"origin/{branche}", "journaux/"], capture_output=True, text=True, check=True).stdout.split()
    if not fichiers:
        print("Aucun journal sur cette branche.")
        return
    dernier = sorted(fichiers)[-1]
    print(f"===== {dernier} =====")
    print(subprocess.run(["git", "show", f"origin/{branche}:{dernier}"], capture_output=True, text=True, check=True).stdout)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="commande", required=True)
    a = sp.add_parser("lancer"); a.add_argument("--branche", required=True); a.add_argument("--cible", default="tous")
    b = sp.add_parser("runs"); b.add_argument("--branche"); b.add_argument("-n", type=int, default=5)
    c = sp.add_parser("suivre"); c.add_argument("--run", type=int, required=True)
    d = sp.add_parser("journal"); d.add_argument("--branche", required=True)
    args = p.parse_args()
    if args.commande == "lancer":
        lancer(args.branche, args.cible)
    elif args.commande == "runs":
        runs(args.branche, args.n)
    elif args.commande == "suivre":
        return suivre(args.run)
    elif args.commande == "journal":
        journal(args.branche)
    return 0


if __name__ == "__main__":
    sys.exit(main())
