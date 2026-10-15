"""Tests hors ligne des fonctions de calcul de scripts/collecte_travail.py (collecte ciblée D40)."""

import importlib.util
from pathlib import Path

import pytest

CHEMIN = Path(__file__).resolve().parent.parent / "scripts" / "collecte_travail.py"
spec = importlib.util.spec_from_file_location("collecte_travail", CHEMIN)
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)


def _obs_neet(total: float, f: float, m: float, ages: dict[str, float]) -> "ct.Observations":
    obs = ct.Observations()
    dims = ct.FICHES["neet"][0][2]
    obs.ajouter(dims, "2025", total)
    obs.ajouter({**dims, "SEX": "F"}, "2025", f)
    obs.ajouter({**dims, "SEX": "M"}, "2025", m)
    for age, v in ages.items():
        obs.ajouter({**dims, "AGE": age}, "2025", v)
    return obs


def test_lecture_taux():
    obs = _obs_neet(12.9, 13.2, 12.6, {"Y15T19": 6.0, "Y20T24": 16.0, "Y25T29": 16.5})
    r = ct.controler_repartition(obs, ct.FICHES["neet"][0][2], 2025, ["Y15T19", "Y20T24", "Y25T29"])
    assert r["lecture"].startswith("taux")
    assert r["somme_ages"] == pytest.approx(38.5)


def test_lecture_repartition():
    obs = _obs_neet(100.0, 48.0, 52.0, {"Y15T19": 20.0, "Y20T24": 38.0, "Y25T29": 42.0})
    r = ct.controler_repartition(obs, ct.FICHES["neet"][0][2], 2025, ["Y15T19", "Y20T24", "Y25T29"])
    assert r["lecture"].startswith("répartition")
    assert r["somme_ages"] == pytest.approx(100.0)


def test_moyennes_annuelles_et_calculs():
    moy = ct.moyennes_annuelles([("2025-Q1", 12.9), ("2025-Q2", 13.0), ("2025-Q3", 12.8), ("2025-Q4", 13.1), ("2024-Q4", None)])
    assert moy[2025] == (pytest.approx(12.95), 4)
    assert 2024 not in moy
    obs = ct.Observations()
    a, b = (d for _, _, d in ct.FICHES["taux_chomage_longue_duree"])
    obs.ajouter(a, "2024", 550.0)
    obs.ajouter(b, "2024", 31000.0)
    assert ct.calculer(obs, "cld_calc", 2024) == pytest.approx(550 / 31000 * 100)
    assert ct.calculer(obs, "cld_calc", 2023) is None
    # population 15-29 reconstituée par actifs / taux d'activité
    for age, actifs, taux in (("Y15T19", 600.0, 15.0), ("Y20T24", 2400.0, 60.0), ("Y25T29", 3200.0, 80.0)):
        obs.ajouter(ct._eec(AGE=age, EEC_MEASURE="ACTPOP", EMPSTA="1T2", UNIT_MEASURE="PS"), "2024", actifs)
        obs.ajouter(ct._eec(AGE=age, EEC_MEASURE="ACTRATE", EMPSTA="1T2", UNIT_MEASURE="PT"), "2024", taux)
    obs.ajouter(ct.FICHES["neet"][1][2], "2024", 1500.0)
    assert ct.calculer(obs, "neet_calc", 2024) == pytest.approx(1500 / 12000 * 100)


def test_fiches_couvertes():
    # les onze fiches de l'audit (§3) sont toutes lues
    attendues = {"taux_emploi", "taux_chomage", "taux_activite", "part_temps_partiel", "taux_sous_emploi", "neet", "halo_chomage",
                 "part_emploi_temporaire", "taux_chomage_longue_duree", "satisfaction_travail", "salaire_net_moyen_reel"}
    assert set(ct.FICHES) == attendues
    for series in ct.FICHES.values():
        for _, jeu, dims in series:
            assert jeu == ct.EEC or jeu in ct.EXTRACTIONS_AUTRES
            if jeu == ct.EEC:
                assert dims["EEC_MEASURE"] in ct.MESURES_EEC
