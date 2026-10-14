"""Fichiers insee.fr à URL stable (niveau 2 de la charte, décision D14).

Téléchargement d'un fichier XLSX/CSV (ou d'un ZIP qui en contient) avec un User-Agent qui identifie
le projet, à débit modéré (le client impose un intervalle minimal entre deux appels), puis lecture
d'une feuille en `pandas.DataFrame`.

Exemple (sur GitHub Actions seulement : le bac à sable n'atteint pas insee.fr) :

    from src.sources.insee_http import ClientHttp
    from src.sources import insee_fichiers as f
    client = ClientHttp(intervalle_defaut=5.0)
    contenu = f.telecharger("https://www.insee.fr/fr/statistiques/fichier/2491918/reve-niv-vie-indic-inegalite.xlsx", client)
    print(f.lister_feuilles(contenu))
    tableau = f.lire_feuille(contenu, feuille=0, entete=None)
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Optional, Union

from .insee_http import AGENT, Reponse

#: Intervalle conseillé entre deux téléchargements sur www.insee.fr (débit modéré).
INTERVALLE_CONSEILLE = 5.0

Source = Union[bytes, str, Path]


class ErreurFichier(RuntimeError):
    def __init__(self, reponse: Reponse):
        super().__init__(f"HTTP {reponse.statut} sur {reponse.url} : {reponse.extrait()}")
        self.reponse = reponse


def telecharger(url: str, client, destination: Optional[Path] = None) -> bytes:
    """Télécharge un fichier ; l'écrit dans `destination` si fourni ; renvoie son contenu."""
    rep = client.get(url, entetes={"User-Agent": AGENT})
    if not rep.ok:
        raise ErreurFichier(rep)
    if destination is not None:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(rep.contenu)
    return rep.contenu


def _octets(source: Source) -> bytes:
    if isinstance(source, (bytes, bytearray)):
        return bytes(source)
    return Path(source).read_bytes()


def type_fichier(contenu: bytes, nom: str = "") -> str:
    """'xlsx', 'xls', 'zip' ou 'csv', d'après la signature puis l'extension."""
    if contenu[:4] == b"PK\x03\x04":
        try:
            noms = zipfile.ZipFile(io.BytesIO(contenu)).namelist()
        except zipfile.BadZipFile:
            return "zip"
        return "xlsx" if any(n.startswith("xl/") for n in noms) else "zip"
    if contenu[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return "xls"
    suffixe = Path(nom).suffix.lower().lstrip(".")
    return suffixe if suffixe in {"xlsx", "xls", "zip", "csv"} else "csv"


def extraire_du_zip(contenu: bytes, motif: str = "") -> tuple[str, bytes]:
    """Premier fichier XLSX/XLS/CSV d'une archive (dont le nom contient `motif`, si fourni)."""
    archive = zipfile.ZipFile(io.BytesIO(contenu))
    candidats = [n for n in archive.namelist() if n.lower().endswith((".xlsx", ".xls", ".csv")) and motif.lower() in n.lower()]
    if not candidats:
        raise ValueError(f"aucun fichier tabulaire{' contenant ' + motif if motif else ''} dans l'archive")
    return candidats[0], archive.read(candidats[0])


def lister_feuilles(source: Source) -> list[str]:
    import pandas as pd

    contenu = _octets(source)
    if type_fichier(contenu) not in {"xlsx", "xls"}:
        return []
    return list(pd.ExcelFile(io.BytesIO(contenu)).sheet_names)


def lire_feuille(source: Source, feuille: Union[int, str] = 0, entete: Optional[int] = 0, nom: str = "", **options):
    """Lit une feuille d'un XLSX/XLS (ou un CSV) en DataFrame.

    `entete=None` lit tout sans ligne d'en-tête (utile pour les tableaux insee.fr dont l'en-tête est
    précédé d'un titre et de notes). Les options supplémentaires sont transmises à pandas.
    """
    import pandas as pd

    contenu = _octets(source)
    genre = type_fichier(contenu, nom or (str(source) if not isinstance(source, (bytes, bytearray)) else ""))
    if genre == "zip":
        nom, contenu = extraire_du_zip(contenu, options.pop("motif", ""))
        genre = type_fichier(contenu, nom)
    if genre in {"xlsx", "xls"}:
        return pd.read_excel(io.BytesIO(contenu), sheet_name=feuille, header=entete, **options)
    texte = contenu.decode("utf-8-sig", errors="replace")
    separateur = ";" if texte[:2000].count(";") > texte[:2000].count(",") else ","
    return pd.read_csv(io.StringIO(texte), sep=separateur, header=entete, **options)
