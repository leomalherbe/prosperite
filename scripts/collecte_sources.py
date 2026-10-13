"""Vérification des voies d'accès aux sources hors INSEE/Eurostat (mission M04).

Exécuté par GitHub Actions (workflow « Collecte », cible collecte_sources.py) :
le bac à sable des sessions Claude ne peut pas appeler les API ni télécharger
de fichiers, et l'outil de lecture de page web est refusé par le robots.txt de
nombreux portails publics (Opendatasoft, static.data.gouv.fr, API de la BCE…).

Entrée  : docs/sources/verif_acces/urls.csv
          colonnes : source, cle, url, octets_max, mode
          - octets_max : nombre d'octets lus au plus (défaut 300 000) ;
          - mode : vide (extrait brut des premiers octets), « complet » (le
            texte lu est conservé jusqu'à octets_max, pour un catalogue),
            « colonne:<nom> » (CSV lu en entier, valeurs distinctes de <nom>),
            « colonnes:<a>|<b>|… » (CSV lu en entier, combinaisons distinctes
            de ces colonnes) ou « regex:<motif> » (texte lu en entier, toutes
            les correspondances du motif, une par ligne).
Sorties : docs/sources/verif_acces/resultats.csv (une ligne par URL) ;
          docs/sources/verif_acces/extraits/<source>__<cle>.txt (extrait lisible :
          début du texte, feuilles et premières lignes d'un classeur, contenu
          d'une archive zip, valeurs distinctes d'une colonne).

Aucune clé d'API n'est utilisée : une source qui en exige une est signalée
par son code HTTP (401/403). Le script ne lève pas d'erreur si une URL échoue :
l'échec est le résultat de la vérification.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "docs" / "sources" / "verif_acces"
ENTREE = DOSSIER / "urls.csv"
SORTIE = DOSSIER / "resultats.csv"
EXTRAITS = DOSSIER / "extraits"

OCTETS_MAX_DEFAUT = 300_000
OCTETS_MAX_ABSOLU = 80_000_000
TAILLE_EXTRAIT = 6_000
ENTETES = {
    "User-Agent": "observatoire-prosperite/0.1 (verification d'acces ; https://github.com/leomalherbe/prosperite)",
    "Accept": "*/*",
}
COLONNES_SORTIE = [
    "source", "cle", "url", "date_verification", "statut_http", "url_finale",
    "content_type", "taille_annoncee", "octets_lus", "nature", "verdict", "message", "extrait",
]


def deviner_nature(content_type: str, debut: bytes, url: str = "") -> str:
    """Nature du contenu reçu, d'après les premiers octets puis l'en-tête Content-Type."""
    ct = (content_type or "").lower()
    tete = debut[:8]
    if tete.startswith(b"PK\x03\x04"):
        if "spreadsheet" in ct or "excel" in ct or url.lower().split("?")[0].endswith((".xlsx", ".xlsm")):
            return "xlsx"
        return "zip"
    if tete.startswith(b"\xd0\xcf\x11\xe0"):
        return "xls"
    if tete.startswith(b"%PDF"):
        return "pdf"
    if tete.startswith(b"PAR1"):
        return "parquet"
    if tete.startswith(b"\x1f\x8b"):
        return "gzip"
    texte = debut[:2000].decode("utf-8", errors="replace").lstrip("﻿ \r\n\t").lower()
    if texte.startswith(("<!doctype html", "<html")) or "text/html" in ct:
        return "html"
    if texte.startswith(("{", "[")) or "json" in ct:
        return "json"
    if texte.startswith("<?xml") or texte.startswith("<message:") or "xml" in ct:
        return "xml"
    if "csv" in ct or "text/plain" in ct or re.match(r'^[^\n]{1,2000}[,;\t][^\n]*\n', texte):
        return "csv"
    if "spreadsheet" in ct or "excel" in ct:
        return "xlsx"
    return "autre"


def verdict(statut: int | None, nature: str) -> str:
    """donnees | page_html | pdf | erreur."""
    if statut is None or statut >= 400:
        return "erreur"
    if nature == "html":
        return "page_html"
    if nature == "pdf":
        return "pdf"
    return "donnees"


def nom_extrait(source: str, cle: str) -> str:
    propre = lambda s: re.sub(r"[^a-z0-9_-]+", "_", s.lower()).strip("_")
    return f"{propre(source)}__{propre(cle)}.txt"


def decrire_classeur(contenu: bytes, lignes: int = 12, feuilles_max: int = 12) -> str:
    import openpyxl

    wb = openpyxl.load_workbook(io.BytesIO(contenu), read_only=True, data_only=True)
    if not wb.sheetnames:  # certains classeurs ne s'ouvrent pas en lecture seule
        wb = openpyxl.load_workbook(io.BytesIO(contenu), read_only=False, data_only=True)
    if not wb.sheetnames:
        return "Classeur sans feuille lisible par openpyxl. " + decrire_zip(contenu)
    sortie = [f"Feuilles ({len(wb.sheetnames)}) : {wb.sheetnames}"]
    for nom in wb.sheetnames[:feuilles_max]:
        ws = wb[nom]
        sortie.append(f"\n=== Feuille « {nom} » (dimensions {ws.max_row} x {ws.max_column}) ===")
        for i, ligne in enumerate(ws.iter_rows(values_only=True)):
            if i >= lignes:
                break
            cellules = ["" if v is None else str(v)[:40] for v in ligne[:25]]
            while cellules and cellules[-1] == "":
                cellules.pop()
            sortie.append(" | ".join(cellules))
    return "\n".join(sortie)


def decrire_zip(contenu: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(contenu)) as z:
        infos = z.infolist()
        return "Archive zip :\n" + "\n".join(f"{i.filename}  ({i.file_size} octets)" for i in infos[:200])


def valeurs_distinctes(contenu: bytes, colonne: str, max_valeurs: int = 3000) -> str:
    df = lire_csv(contenu)
    if colonne not in df.columns:
        return f"Colonne « {colonne} » absente. Colonnes : {list(df.columns)}"
    vals = df[colonne].dropna().value_counts()
    lignes = [f"Colonnes : {list(df.columns)}", f"{len(df)} lignes ; {len(vals)} valeurs distinctes de « {colonne} » (effectif) :"]
    lignes += [f"{v}\t{n}" for v, n in vals.head(max_valeurs).items()]
    return "\n".join(lignes)


def lire_csv(contenu: bytes):
    import pandas as pd

    texte = contenu.decode("utf-8", errors="replace").lstrip("﻿")
    premiere = texte.split("\n", 1)[0]
    sep = max([",", ";", "\t", "|"], key=premiere.count)
    return pd.read_csv(io.StringIO(texte), sep=sep, dtype=str, low_memory=False, on_bad_lines="skip")


def combinaisons_distinctes(contenu: bytes, colonnes: list[str], max_lignes: int = 5000) -> str:
    df = lire_csv(contenu)
    absentes = [c for c in colonnes if c not in df.columns]
    if absentes:
        return f"Colonnes absentes : {absentes}. Colonnes : {list(df.columns)}"
    d = df[colonnes].drop_duplicates()
    lignes = [f"Colonnes : {list(df.columns)}", f"{len(df)} lignes ; {len(d)} combinaisons distinctes de {colonnes} :",
              "\t".join(colonnes)]
    lignes += ["\t".join("" if v != v else str(v) for v in rangee) for rangee in d.head(max_lignes).itertuples(index=False)]
    return "\n".join(lignes)


def correspondances(contenu: bytes, motif: str, max_lignes: int = 20000) -> str:
    texte = contenu.decode("utf-8", errors="replace")
    trouves = re.findall(motif, texte)
    vus, sortie = set(), []
    for t in trouves:
        ligne = "\t".join(t) if isinstance(t, tuple) else t
        if ligne not in vus:
            vus.add(ligne)
            sortie.append(ligne)
    return f"{len(sortie)} correspondances distinctes du motif {motif!r} :\n" + "\n".join(sortie[:max_lignes])


def verifier(source: str, cle: str, url: str, octets_max: int, mode: str) -> dict:
    import requests

    res = {"source": source, "cle": cle, "url": url,
           "date_verification": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "statut_http": "", "url_finale": "", "content_type": "", "taille_annoncee": "",
           "octets_lus": 0, "nature": "", "verdict": "erreur", "message": "", "extrait": ""}
    if mode.startswith(("colonne:", "colonnes:", "regex:")) or mode == "complet":
        octets_max = max(octets_max, OCTETS_MAX_DEFAUT)
    octets_max = min(octets_max, OCTETS_MAX_ABSOLU)
    try:
        with requests.get(url, headers=ENTETES, timeout=(20, 120), stream=True, allow_redirects=True) as r:
            res["statut_http"] = r.status_code
            res["url_finale"] = r.url if r.url != url else ""
            res["content_type"] = r.headers.get("Content-Type", "")
            res["taille_annoncee"] = r.headers.get("Content-Length", "")
            morceaux, total = [], 0
            for bloc in r.iter_content(chunk_size=65536):
                morceaux.append(bloc)
                total += len(bloc)
                if total >= octets_max:
                    break
            contenu = b"".join(morceaux)[:octets_max]
    except Exception as exc:  # l'échec fait partie du résultat
        res["message"] = f"{type(exc).__name__}: {exc}"[:300]
        return res

    res["octets_lus"] = len(contenu)
    nature = deviner_nature(res["content_type"], contenu, url)
    res["nature"] = nature
    res["verdict"] = verdict(res["statut_http"], nature)

    try:
        complet = not res["taille_annoncee"] or len(contenu) >= int(res["taille_annoncee"] or 0)
        if nature == "xlsx" and complet:
            description = decrire_classeur(contenu)
        elif nature == "xlsx":
            description = f"Classeur tronqué à {len(contenu)} octets (taille {res['taille_annoncee']}) : augmenter octets_max."
        elif nature == "zip" and complet:
            description = decrire_zip(contenu)
        elif mode.startswith("colonne:") and nature == "csv":
            description = valeurs_distinctes(contenu, mode.split(":", 1)[1])
        elif mode.startswith("colonnes:") and nature == "csv":
            description = combinaisons_distinctes(contenu, mode.split(":", 1)[1].split("|"))
        elif mode.startswith("regex:") and res["verdict"] == "donnees":
            description = correspondances(contenu, mode.split(":", 1)[1])
        elif nature in ("json", "xml", "csv", "html", "autre"):
            texte = contenu.decode("utf-8", errors="replace")
            if nature == "json" and len(contenu) < octets_max:
                try:
                    texte = json.dumps(json.loads(texte), ensure_ascii=False, indent=1)
                except ValueError:
                    pass
            description = texte if mode == "complet" else texte[:TAILLE_EXTRAIT]
        else:
            description = f"Contenu binaire ({nature}), début : {contenu[:16]!r}"
    except Exception as exc:
        description = f"Lecture impossible : {type(exc).__name__}: {exc}"
        res["message"] = description[:300]

    nom = nom_extrait(source, cle)
    entete = (f"# {source} / {cle}\n# URL : {url}\n# Vérifié le {res['date_verification']} — HTTP {res['statut_http']}"
              f" — {res['content_type']} — {res['octets_lus']} octets lus (taille annoncée : {res['taille_annoncee'] or 'inconnue'})\n\n")
    (EXTRAITS / nom).write_text(entete + description, encoding="utf-8")
    res["extrait"] = f"extraits/{nom}"
    return res


def main() -> int:
    if not ENTREE.exists():
        print(f"Pas de liste d'URL ({ENTREE}) : rien à vérifier.")
        return 0
    EXTRAITS.mkdir(parents=True, exist_ok=True)
    for ancien in EXTRAITS.glob("*.txt"):  # chaque exécution produit un instantané complet
        ancien.unlink()
    with ENTREE.open(encoding="utf-8") as f:
        lignes = [l for l in csv.DictReader(f) if (l.get("url") or "").strip()]
    resultats = []
    for i, l in enumerate(lignes, 1):
        octets = int(l.get("octets_max") or OCTETS_MAX_DEFAUT)
        r = verifier(l["source"].strip(), l["cle"].strip(), l["url"].strip(), octets, (l.get("mode") or "").strip())
        print(f"[{i}/{len(lignes)}] {r['verdict']:<9} HTTP {r['statut_http'] or '---'} {r['nature']:<7} {l['source']} / {l['cle']}", flush=True)
        resultats.append(r)
        time.sleep(0.5)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES_SORTIE)
        w.writeheader()
        w.writerows(resultats)
    n_ok = sum(r["verdict"] == "donnees" for r in resultats)
    print(f"\nBilan : {n_ok}/{len(resultats)} URL renvoient des données ; détail dans {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
