import math

import pytest

from src.scoring.calcul import (
    COMPENSATION,
    SCORE_PLANCHER,
    agreger,
    indice_global,
    moyenne_generalisee,
    normaliser,
    score_dimension,
)


# --- normalisation -----------------------------------------------------------

def test_normaliser_sens_haut():
    # espérance de vie : seuil 75 (score 0), objectif 85 (score 100)
    assert normaliser(75, 75, 85) == 0
    assert normaliser(85, 75, 85) == 100
    assert normaliser(80, 75, 85) == pytest.approx(50)


def test_normaliser_sens_bas():
    # taux de pauvreté : seuil minimal 16 % (score 0), objectif 8 % (score 100)
    assert normaliser(16, 16, 8) == 0
    assert normaliser(8, 16, 8) == 100
    assert normaliser(12, 16, 8) == pytest.approx(50)


def test_normaliser_ecretage_et_absence():
    assert normaliser(200, 75, 85) == 100
    assert normaliser(0, 75, 85) == 0
    assert normaliser(20, 16, 8) == 0
    assert normaliser(None, 75, 85) is None
    assert normaliser(float("nan"), 75, 85) is None


def test_normaliser_bornes_egales():
    with pytest.raises(ValueError):
        normaliser(10, 5, 5)


# --- moyenne généralisée -----------------------------------------------------

def test_arithmetique():
    assert moyenne_generalisee([20, 80], [1, 1], 1) == pytest.approx(50)
    assert moyenne_generalisee([20, 80], [3, 1], 1) == pytest.approx(35)


def test_geometrique():
    assert moyenne_generalisee([25, 100], [1, 1], 0) == pytest.approx(50)


def test_minimum_et_maximum():
    assert moyenne_generalisee([20, 80, 50], [1, 1, 1], -math.inf) == 20
    assert moyenne_generalisee([20, 80, 50], [1, 1, 1], math.inf) == 80


def test_ordre_quelconque():
    # p = -1 : moyenne harmonique
    assert moyenne_generalisee([50, 100], [1, 1], -1) == pytest.approx(200 / 3)


def test_plancher_pour_p_non_positif():
    # un score nul n'annule pas la moyenne géométrique : il est remplacé par SCORE_PLANCHER
    assert moyenne_generalisee([0, 100], [1, 1], 0) == pytest.approx(math.sqrt(SCORE_PLANCHER * 100))
    assert moyenne_generalisee([0, 100], [1, 1], -math.inf) == SCORE_PLANCHER
    # mais pas pour la moyenne arithmétique
    assert moyenne_generalisee([0, 100], [1, 1], 1) == 50


def test_poids_nuls_et_vide():
    assert moyenne_generalisee([20, 80], [0, 1], 1) == 80
    assert moyenne_generalisee([], [], 1) is None
    assert moyenne_generalisee([20], [0], 1) is None


def test_reglages_compensation():
    scores, poids = [10, 90], [1, 1]
    totale = moyenne_generalisee(scores, poids, COMPENSATION["totale"])
    limitee = moyenne_generalisee(scores, poids, COMPENSATION["limitee"])
    nulle = moyenne_generalisee(scores, poids, COMPENSATION["nulle"])
    assert totale == 50 and limitee == pytest.approx(30) and nulle == 10
    assert nulle < limitee < totale


# --- agrégation et couverture -----------------------------------------------

def test_agreger_ignore_les_absents_et_compte_la_couverture():
    a = agreger([(80, 1), (None, 1), (40, 2)], 1)
    assert a.score == pytest.approx((80 + 80) / 3)
    assert (a.disponibles, a.total) == (2, 3)
    assert a.couverture == pytest.approx(2 / 3)


def test_agreger_rien_de_disponible():
    a = agreger([(None, 1), (None, 1)], 1)
    assert a.score is None and a.disponibles == 0 and a.total == 2
    assert agreger([], 1).couverture is None


def test_deux_niveaux():
    sante = score_dimension([(normaliser(82, 75, 85), 1), (normaliser(12, 16, 8), 1)], 1)
    planete = score_dimension([(normaliser(5.0, 8.0, 2.0), 1)], 1)  # tCO2e/hab, bas = mieux
    assert sante.score == pytest.approx((70 + 50) / 2)
    assert planete.score == pytest.approx(50)
    global_ = indice_global([(sante.score, 2), (planete.score, 1)], COMPENSATION["totale"])
    assert global_.score == pytest.approx((60 * 2 + 50) / 3)
    assert indice_global([(sante.score, 2), (planete.score, 1)], COMPENSATION["nulle"]).score == 50
