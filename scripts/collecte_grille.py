"""Mission M03 (phase 2) — contre-vérification du Doughnut 3.0 : documents supplémentaires.

Script **ponctuel** exécuté par le robot « Collecte » (le bac à sable des sessions ne peut
pas télécharger l'archive). Il récupère l'archive des documents supplémentaires de
Fanning & Raworth (2025, Nature 646, 47-56), déposée sur ORA (Oxford University Research
Archive, licence CC BY 4.0), et en extrait le texte (PDF, DOCX) et le début des feuilles
(XLSX, CSV) dans `journaux/m03_doughnut_supplementaire/`, pour lecture par l'agent M03.

Aucune donnée n'est écrite dans `catalogues/` ni `donnees/`. Le script est retiré de la
branche après exécution (il n'a pas vocation à tourner chaque mois sur `main`).
"""

from __future__ import annotations

import io
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import requests

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "journaux" / "m03_doughnut_supplementaire"
URL_ORA_ZIP = "https://ora.ox.ac.uk/objects/uuid:cb7f2af6-96de-4744-9b44-185ce77c6b14/files/r6h440v46z"
ENTETES = {"User-Agent": "observatoire-prosperite/0.1 (projet de recherche ; github.com/leomalherbe/prosperite)"}
MAX_LIGNES_FEUILLE = 400


def _pypdf():
    try:
        import pypdf  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pypdf>=4"], check=True)
    import pypdf

    return pypdf


def _nom_sur(nom: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", nom)[:120]


def extraire_pdf(contenu: bytes) -> str:
    pypdf = _pypdf()
    lecteur = pypdf.PdfReader(io.BytesIO(contenu))
    morceaux = []
    for i, page in enumerate(lecteur.pages, start=1):
        morceaux.append(f"\n\n=== page {i} ===\n")
        morceaux.append(page.extract_text() or "")
    return "".join(morceaux)


def extraire_docx(contenu: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(contenu)) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"</w:tc>", " | ", xml)
    return re.sub(r"<[^>]+>", "", xml)


def extraire_xlsx(contenu: bytes) -> str:
    import openpyxl

    classeur = openpyxl.load_workbook(io.BytesIO(contenu), read_only=True, data_only=True)
    morceaux = []
    for feuille in classeur.worksheets:
        morceaux.append(f"\n\n=== feuille « {feuille.title} » (dimensions déclarées : {feuille.max_row} lignes x {feuille.max_column} colonnes) ===\n")
        for n, ligne in enumerate(feuille.iter_rows(values_only=True), start=1):
            if n > MAX_LIGNES_FEUILLE:
                morceaux.append(f"[… tronqué après {MAX_LIGNES_FEUILLE} lignes]\n")
                break
            morceaux.append(" | ".join("" if v is None else str(v) for v in ligne) + "\n")
    return "".join(morceaux)


def traiter(nom: str, contenu: bytes) -> str | None:
    bas = nom.lower()
    if bas.endswith(".pdf"):
        return extraire_pdf(contenu)
    if bas.endswith(".docx"):
        return extraire_docx(contenu)
    if bas.endswith((".xlsx", ".xlsm")):
        return extraire_xlsx(contenu)
    if bas.endswith((".csv", ".txt", ".md", ".r", ".json")):
        texte = contenu.decode("utf-8", errors="replace")
        lignes = texte.splitlines()
        if len(lignes) > MAX_LIGNES_FEUILLE:
            texte = "\n".join(lignes[:MAX_LIGNES_FEUILLE]) + f"\n[… tronqué après {MAX_LIGNES_FEUILLE} lignes sur {len(lignes)}]"
        return texte
    return None


def parcourir_zip(contenu: bytes, prefixe: str, inventaire: list[str]) -> None:
    with zipfile.ZipFile(io.BytesIO(contenu)) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            nom = f"{prefixe}{info.filename}"
            inventaire.append(f"{nom}\t{info.file_size} octets")
            donnees = z.read(info)
            if info.filename.lower().endswith(".zip"):
                parcourir_zip(donnees, nom + "/", inventaire)
                continue
            try:
                texte = traiter(info.filename, donnees)
            except Exception as exc:  # on continue : un fichier illisible ne doit pas tout bloquer
                texte = f"[erreur d'extraction : {exc!r}]"
            if texte is not None:
                (SORTIE / (_nom_sur(nom) + ".txt")).write_text(texte, encoding="utf-8")
                print(f"  extrait : {nom} -> {len(texte)} caractères")


URL_EUROPEPMC_SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12488500/supplementaryFiles"
URL_ZENODO = "https://zenodo.org/api/records/15688961"
URL_NATURE = "https://www.nature.com/articles/s41586-025-09385-1"
TAILLE_MAX = 60_000_000


def telecharger(url: str) -> requests.Response | None:
    try:
        rep = requests.get(url, headers=ENTETES, timeout=300, allow_redirects=True)
    except requests.RequestException as exc:
        print(f"  {url} : erreur réseau {exc!r}")
        return None
    print(f"  {url} : HTTP {rep.status_code} ; {rep.headers.get('Content-Type')} ; {len(rep.content)} octets")
    return rep


def deposer(nom: str, contenu: bytes, inventaire: list[str]) -> None:
    """Traite un fichier téléchargé (archive ou document isolé)."""
    inventaire.append(f"{nom}\t{len(contenu)} octets")
    if contenu.startswith(b"PK") and not nom.lower().endswith((".xlsx", ".xlsm", ".docx")):
        parcourir_zip(contenu, nom + "/", inventaire)
        return
    try:
        texte = traiter(nom, contenu)
    except Exception as exc:
        texte = f"[erreur d'extraction : {exc!r}]"
    if texte is not None:
        (SORTIE / (_nom_sur(nom) + ".txt")).write_text(texte, encoding="utf-8")
        print(f"  extrait : {nom} -> {len(texte)} caractères")


def main() -> int:
    SORTIE.mkdir(parents=True, exist_ok=True)
    inventaire: list[str] = []
    obtenu = False

    print("1. ORA (archive des documents supplémentaires)")
    rep = telecharger(URL_ORA_ZIP)
    if rep is not None and rep.status_code == 200 and rep.content.startswith(b"PK"):
        deposer("ora_supplementary.zip", rep.content, inventaire)
        obtenu = True

    print("2. Europe PMC (fichiers supplémentaires de PMC12488500)")
    rep = telecharger(URL_EUROPEPMC_SUPP)
    if rep is not None and rep.status_code == 200 and rep.content.startswith(b"PK"):
        deposer("europepmc_supplementary.zip", rep.content, inventaire)
        obtenu = True

    print("3. Zenodo (données et code, DOI 10.5281/zenodo.15688961)")
    rep = telecharger(URL_ZENODO)
    if rep is not None and rep.status_code == 200:
        try:
            fiche = rep.json()
        except ValueError:
            fiche = {}
        (SORTIE / "zenodo_fiche.txt").write_text(
            f"titre : {fiche.get('metadata', {}).get('title')}\nversion : {fiche.get('metadata', {}).get('version')}\n"
            f"description : {fiche.get('metadata', {}).get('description')}\n", encoding="utf-8"
        )
        for f in fiche.get("files", []):
            nom, taille = f.get("key", "?"), f.get("size", 0)
            lien = f.get("links", {}).get("self")
            print(f"  fichier Zenodo : {nom} ({taille} octets)")
            if lien and taille and taille < TAILLE_MAX:
                r2 = telecharger(lien)
                if r2 is not None and r2.status_code == 200:
                    deposer("zenodo_" + nom, r2.content, inventaire)
                    obtenu = True

    print("4. Nature (liens des documents supplémentaires dans la page de l'article)")
    rep = telecharger(URL_NATURE)
    if rep is not None and rep.status_code == 200:
        liens = sorted(set(re.findall(r'https://static-content\.springer\.com/esm/[^"\']+', rep.text)))
        for lien in liens:
            print(f"  lien supplémentaire : {lien}")
            r2 = telecharger(lien)
            if r2 is not None and r2.status_code == 200:
                deposer("nature_" + lien.rsplit("/", 1)[-1], r2.content, inventaire)
                obtenu = True

    (SORTIE / "00_inventaire.txt").write_text(
        "Sources tentées : ORA, Europe PMC, Zenodo, Nature (voir le journal d'exécution)\n" + "\n".join(inventaire) + "\n",
        encoding="utf-8",
    )
    print("Inventaire :")
    for ligne in inventaire:
        print("  " + ligne)
    return 0 if obtenu else 1


if __name__ == "__main__":
    sys.exit(main())
