"""Calcul de l'indice de prospérité — implémentation de référence.

Spécification : charte du projet, §3.2 (docs/00_charte_projet.md).

- Un indicateur est normalisé entre deux bornes fixées par l'utilisateur :
  le *seuil minimal* (score 0) et l'*objectif* (score 100). Le sens est
  implicite : si l'objectif est inférieur au seuil minimal, l'indicateur est
  « bas = mieux » (ex. taux de pauvreté).
- Les scores sont agrégés par une *moyenne généralisée pondérée* d'ordre p,
  aux deux niveaux (indicateurs → dimension, dimensions → indice) :
    p = 1       moyenne arithmétique      (compensation totale)
    p = 0       moyenne géométrique       (compensation limitée)
    p = -inf    minimum pondéré           (compensation nulle, « maillon faible »)
- Les scores sont planchonnés à SCORE_PLANCHER avant agrégation pour p <= 0,
  afin qu'un zéro n'annule pas la moyenne géométrique.
- Les éléments sans score (None) sont ignorés ; la couverture est renvoyée.

Le front reproduira exactement ces formules ; tout changement passe par ici
et par les tests (tests/test_scoring.py).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

SCORE_MIN = 0.0
SCORE_MAX = 100.0
SCORE_PLANCHER = 1.0  # plancher appliqué avant agrégation quand p <= 0

#: Réglages proposés dans l'interface sous le nom « degré de compensation ».
COMPENSATION = {
    "totale": 1.0,          # moyenne arithmétique
    "limitee": 0.0,         # moyenne géométrique
    "nulle": -math.inf,     # minimum pondéré
}


def normaliser(valeur: Optional[float], seuil_minimal: float, objectif: float) -> Optional[float]:
    """Score 0–100 d'une valeur brute entre le seuil minimal (0) et l'objectif (100).

    Le sens est déduit des bornes : objectif > seuil_minimal → « haut = mieux » ;
    objectif < seuil_minimal → « bas = mieux ». Les valeurs au-delà des bornes
    sont écrêtées. Renvoie None si la valeur est absente.
    """
    if valeur is None or (isinstance(valeur, float) and math.isnan(valeur)):
        return None
    if seuil_minimal == objectif:
        raise ValueError("seuil_minimal et objectif doivent être différents")
    fraction = (valeur - seuil_minimal) / (objectif - seuil_minimal)
    fraction = max(0.0, min(1.0, fraction))
    return SCORE_MIN + fraction * (SCORE_MAX - SCORE_MIN)


def moyenne_generalisee(scores: Sequence[float], poids: Sequence[float], p: float = 1.0) -> Optional[float]:
    """Moyenne généralisée pondérée d'ordre p des scores (0–100).

    p = 1 arithmétique ; p = 0 géométrique ; p = -inf minimum ; p = +inf maximum ;
    tout autre p réel : (Σ w s^p / Σ w)^(1/p). Les poids nuls ou négatifs sont ignorés.
    Renvoie None si aucun couple (score, poids > 0) n'est disponible.
    """
    couples = [(float(s), float(w)) for s, w in zip(scores, poids) if s is not None and w is not None and w > 0]
    if not couples:
        return None
    total_poids = sum(w for _, w in couples)
    if p <= 0:
        couples = [(max(s, SCORE_PLANCHER), w) for s, w in couples]
    if math.isinf(p):
        valeurs = [s for s, _ in couples]
        return min(valeurs) if p < 0 else max(valeurs)
    if p == 0:
        return math.exp(sum(w * math.log(s) for s, w in couples) / total_poids)
    if p == 1:
        return sum(w * s for s, w in couples) / total_poids
    return (sum(w * s ** p for s, w in couples) / total_poids) ** (1.0 / p)


@dataclass(frozen=True)
class Agregat:
    """Résultat d'une agrégation : score (None si rien de disponible) et couverture."""

    score: Optional[float]
    disponibles: int
    total: int

    @property
    def couverture(self) -> Optional[float]:
        return None if self.total == 0 else self.disponibles / self.total


def agreger(elements: Iterable[tuple[Optional[float], float]], p: float = 1.0) -> Agregat:
    """Agrège des couples (score ou None, poids) ; sert aux deux niveaux.

    `total` compte les éléments sélectionnés (poids > 0) ; `disponibles` ceux qui ont un score.
    """
    elements = [(s, w) for s, w in elements if w is not None and w > 0]
    scores = [s for s, _ in elements if s is not None]
    poids = [w for s, w in elements if s is not None]
    return Agregat(score=moyenne_generalisee(scores, poids, p), disponibles=len(scores), total=len(elements))


def score_dimension(indicateurs: Iterable[tuple[Optional[float], float]], p_indicateurs: float = 1.0) -> Agregat:
    """Score d'une dimension à partir des (score d'indicateur, poids interne)."""
    return agreger(indicateurs, p_indicateurs)


def indice_global(dimensions: Iterable[tuple[Optional[float], float]], p_dimensions: float = 1.0) -> Agregat:
    """Indice global à partir des (score de dimension, poids de dimension)."""
    return agreger(dimensions, p_dimensions)
