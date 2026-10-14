"""Tests hors ligne du module fichiers insee.fr (src/sources/insee_fichiers.py).

Le fichier XLSX utilisé est une réponse réelle de Melodi (`/melodi/file/DS_EC_DECES/…`), même format
que les fichiers XLSX d'insee.fr (aucun fichier insee.fr n'est lisible depuis le bac à sable).
"""

import io
import zipfile
from pathlib import Path

import pytest

from src.sources import insee_fichiers as fic
from src.sources.insee_http import AGENT, ClientFixtures, Reponse

XLSX = sorted((Path(__file__).parent / "fixtures" / "insee" / "melodi").glob("melodi_file_DS_EC_DECES_*.xlsx"))[-1]


def test_type_fichier():
    contenu = XLSX.read_bytes()
    assert fic.type_fichier(contenu) == "xlsx"
    assert fic.type_fichier(b"a;b\n1;2\n", "x.csv") == "csv"


def test_lister_et_lire_feuille():
    feuilles = fic.lister_feuilles(XLSX)
    assert len(feuilles) == 2
    tableau = fic.lire_feuille(XLSX, feuille=feuilles[-1], entete=None)
    assert tableau.shape[0] > 5 and tableau.shape[1] >= 2


def test_lire_feuille_dans_un_zip():
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as z:
        z.writestr("lisezmoi.txt", "x")
        z.writestr("donnees/tableau.xlsx", XLSX.read_bytes())
    tableau = fic.lire_feuille(tampon.getvalue(), feuille=0, entete=None)
    assert tableau.shape[0] > 0


def test_lire_csv_point_virgule():
    tableau = fic.lire_feuille("a;b\n1;2\n3;4\n".encode(), nom="t.csv")
    assert list(tableau.columns) == ["a", "b"] and len(tableau) == 2


def test_telecharger_identifie_le_projet(tmp_path):
    client = ClientFixtures([(lambda u: u.endswith(".xlsx"), Reponse(200, XLSX.read_bytes(), ""))])
    dest = tmp_path / "f.xlsx"
    contenu = fic.telecharger("https://www.insee.fr/fr/statistiques/fichier/1/f.xlsx", client, destination=dest)
    assert dest.read_bytes() == contenu
    assert "ObservatoireProsperite" in AGENT


def test_telecharger_erreur():
    with pytest.raises(fic.ErreurFichier):
        fic.telecharger("https://www.insee.fr/absent.xlsx", ClientFixtures([]))
