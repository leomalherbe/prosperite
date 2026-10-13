"""Tests hors ligne du module BDM (src/sources/insee_bdm.py) sur les fixtures de tests/fixtures/insee/bdm/."""

from pathlib import Path

import pytest

from src.sources import insee_bdm as bdm
from src.sources.insee_http import ClientFixtures, Reponse

FIX = Path(__file__).parent / "fixtures" / "insee" / "bdm"


def fixture(motif: str) -> bytes:
    fichiers = sorted(FIX.glob(motif))
    assert fichiers, f"fixture introuvable : {motif}"
    return fichiers[-1].read_bytes()


def rep(contenu: bytes, statut: int = 200) -> Reponse:
    return Reponse(statut=statut, contenu=contenu, url="")


# --- structures ----------------------------------------------------------------------------

def test_analyser_dataflows():
    flux = bdm.analyser_dataflows(fixture("bdm_dataflow_ODD-ERADICATION-PAUVRETE_*.xml"))
    assert len(flux) == 1
    df = flux[0]
    assert df.id == "ODD-ERADICATION-PAUVRETE"
    assert df.nom_fr.startswith("Objectif de développement durable n°1")
    assert df.nom_en.startswith("Sustainable Development Goal")
    assert df.nb_series == 65
    assert df.url_page.startswith("https://www.insee.fr/")


def test_analyser_structure_ordre_de_la_cle():
    dims = bdm.analyser_structure(fixture("bdm_datastructure_CHOMAGE-TRIM-NATIONAL_*.xml"))
    assert [d.id for d in dims][:3] == ["FREQ", "INDICATEUR", "NATURE"]
    assert "TIME_PERIOD" not in [d.id for d in dims]
    assert dims[0].codelist == "CL_PERIODICITE"
    assert len(dims) == 9
    assert bdm.construire_cle(dims, {"FREQ": ["T"]}) == "T........"
    assert bdm.construire_cle(dims, {"FREQ": ["A", "T"], "SEXE": ["1"]}) == "A+T....1...."


def test_analyser_codelist():
    codes = bdm.analyser_codelist(fixture("bdm_codelist_CL_PERIODICITE_*.xml"))
    assert codes["A"] == "Annuelle"
    assert set(codes) == {"A", "B", "M", "S", "T"}


# --- données -------------------------------------------------------------------------------

def test_analyser_donnees_serie_annuelle_avec_nan_final():
    series = bdm.analyser_donnees(fixture("bdm_serie_010593281_*.xml"))
    assert len(series) == 1
    s = series[0]
    assert s.idbank == "010593281"
    assert s.freq == "A"
    assert s.geo == "FM"
    assert s.attributs["UNIT_MEASURE"] == "NOTE_MOYENNE_0_10"
    assert len(s.observations) == 16
    r = s.resume()
    assert (r.premiere, r.derniere) == ("2010", "2024")
    assert r.manquantes_fin == 1          # 2025 = NaN
    assert r.nb_valeurs == 15
    assert r.nb_annees_depuis == 15
    assert r.statut_derniere == "A"


def test_series_en_lignes_ignore_les_manquantes_de_fin():
    lignes = bdm.series_en_lignes(bdm.analyser_donnees(fixture("bdm_serie_010593281_*.xml")))
    assert len(lignes) == 15
    assert lignes[0].periode == "2010" and lignes[-1].periode == "2024"
    assert all(l.valeur is not None for l in lignes)
    assert lignes[-1] == ("010593281", "FM", "2024", 7.2, "A")


def test_serie_trimestrielle():
    s = bdm.analyser_donnees(fixture("bdm_serie_001688527_*.xml"))[0]
    assert s.freq == "T" and s.geo == "FR-D976"
    r = s.resume()
    assert (r.premiere, r.derniere) == ("2025-Q2", "2026-Q2")


def test_resumer_observations_lacunes_et_debut_manquant():
    obs = [
        {"TIME_PERIOD": "2019", "OBS_VALUE": "NaN", "OBS_STATUS": "O"},
        {"TIME_PERIOD": "2020", "OBS_VALUE": "1.5", "OBS_STATUS": "A"},
        {"TIME_PERIOD": "2022", "OBS_VALUE": "2", "OBS_STATUS": "P"},
        {"TIME_PERIOD": "2023", "OBS_VALUE": "NaN", "OBS_STATUS": "O"},
    ]
    r = bdm.resumer_observations(obs)
    assert (r.premiere, r.derniere, r.nb_valeurs) == ("2020", "2022", 2)
    assert (r.manquantes_debut, r.manquantes_fin) == (1, 1)
    assert r.statut_derniere == "P"


# --- appels (faux client) -----------------------------------------------------------------

def test_obtenir_serie():
    client = ClientFixtures([(lambda u: "SERIES_BDM/010593281" in u, rep(fixture("bdm_serie_010593281_*.xml")))])
    lignes = bdm.obtenir_serie("010593281", client)
    assert len(lignes) == 15
    assert client.appels == ["https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/010593281"]


def test_obtenir_serie_erreur():
    client = ClientFixtures([])
    with pytest.raises(bdm.ErreurBdm):
        bdm.obtenir_serie("000000000", client)


def test_lister_series_decoupe_quand_la_reponse_est_trop_volumineuse():
    """Requête globale refusée (413) → structure → liste des fréquences → une requête par fréquence."""
    annuelle = fixture("bdm_serie_010593281_*.xml")
    trimestrielle = fixture("bdm_serie_001688527_*.xml")
    routes = [
        (lambda u: u.endswith("/data/FLUX?detail=nodata"), rep(b"<Error code=\"510\"/>", 413)),
        (lambda u: "/datastructure/FR1/FLUX" in u, rep(fixture("bdm_datastructure_CHOMAGE-TRIM-NATIONAL_*.xml"))),
        (lambda u: "/codelist/FR1/CL_PERIODICITE" in u, rep(fixture("bdm_codelist_CL_PERIODICITE_*.xml"))),
        (lambda u: "/data/FLUX/A........?" in u, rep(annuelle)),
        (lambda u: "/data/FLUX/T........?" in u, rep(trimestrielle)),
    ]
    client = ClientFixtures(routes)
    res = bdm.lister_series("FLUX", client)
    assert sorted(s["IDBANK"] for s in res.series) == ["001688527", "010593281"]
    assert res.decoupages == 1
    assert not res.erreurs
    # 1 globale + 1 DSD + 1 liste de codes + 5 fréquences
    assert res.requetes == 8


def test_lister_series_decoupage_d_emblee_si_plus_de_2000_series():
    routes = [
        (lambda u: "/datastructure/FR1/FLUX" in u, rep(fixture("bdm_datastructure_CHOMAGE-TRIM-NATIONAL_*.xml"))),
        (lambda u: "/codelist/FR1/CL_PERIODICITE" in u, rep(fixture("bdm_codelist_CL_PERIODICITE_*.xml"))),
        (lambda u: "/data/FLUX/A........?" in u, rep(fixture("bdm_serie_010593281_*.xml"))),
    ]
    client = ClientFixtures(routes)
    res = bdm.lister_series("FLUX", client, nb_annonce=3140)
    assert [s["IDBANK"] for s in res.series] == ["010593281"]
    assert not any(u.endswith("/data/FLUX?detail=nodata") for u in client.appels)


def test_obtenir_series_coupe_un_lot_en_echec():
    annuelle = fixture("bdm_serie_010593281_*.xml")

    def route(u: str) -> bool:
        return "SERIES_BDM/010593281?" in u or u.endswith("SERIES_BDM/010593281")

    client = ClientFixtures([(lambda u: "+" in u, rep(b"erreur", 400)), (route, rep(annuelle))])
    erreurs: list[str] = []
    series = bdm.obtenir_series(["010593281", "999999999"], client, erreurs=erreurs)
    assert [s.idbank for s in series] == ["010593281"]
    assert len(erreurs) == 1 and "999999999" in erreurs[0]


def test_periodes_par_idbank_relit_en_entier_si_fin_manquante():
    """lastNObservations=3 ne contient que des NaN → relecture complète de la série."""
    complete = fixture("bdm_serie_010593281_*.xml")
    texte = complete.decode()
    # réponse « lastNObservations » simulée : on ne garde que l'observation NaN de 2025
    debut, fin = texte.split("<Obs", 1)[0], texte.rsplit("</Series>", 1)[1]
    seule_nan = texte.split("<Obs", 2)[1]
    derniere = (debut + "<Obs" + seule_nan.split("/>", 1)[0] + "/>\n    </Series>" + fin).encode()
    routes = [
        (lambda u: "lastNObservations" in u, rep(derniere)),
        (lambda u: "SERIES_BDM/010593281" in u, rep(complete)),
    ]
    client = ClientFixtures(routes)
    p = bdm.periodes_par_idbank(["010593281"], client)
    assert (p["010593281"].premiere, p["010593281"].derniere) == ("2010", "2024")


def test_est_trop_volumineuse():
    assert bdm.est_trop_volumineuse(rep(b"", 413))
    assert bdm.est_trop_volumineuse(rep(b'<mes:ErrorMessage code="510">', 400))
    assert not bdm.est_trop_volumineuse(rep(b"", 404))
    assert not bdm.est_trop_volumineuse(rep(b"<ok/>", 200))
