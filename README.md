# Observatoire de la prospérité

Construction d'un **indicateur synthétique multidimensionnel de prospérité subjective pour la France**, et de l'outil qui permet à chacun de le paramétrer : choix et pondération des dimensions, choix des indicateurs, seuils minimaux et objectifs, règle d'agrégation. À terme, les paramétrages collectés produisent un **indicateur intersubjectif** (pondération et calibrage moyens des utilisateurs).

Ce dépôt contient le code (collecte des données publiques, calcul de l'indice, application web), les fiches d'indicateurs, les catalogues de séries et les données figées par millésime.

## Organisation
- `docs/` — charte du projet (fait foi), journal des décisions, fiches de mission, comptes rendus, fiches par source de données.
- `src/sources/` — un module par source (INSEE, Eurostat, …) ; `src/scoring/calcul.py` — calcul de référence de l'indice ; `src/pipeline/` — collecte, nettoyage, millésimes.
- `scripts/` — scripts de collecte exécutés par GitHub Actions (`scripts/collecte_*.py`).
- `catalogues/` — séries candidates (CSV) ; `indicateurs/` — fiches YAML et grille de dimensions ; `donnees/millesimes/` — données figées et datées.
- `site/` — application web (modes rapide / avancé / expert, jeu collectif).

## Fonctionnement
- **Tests** : à chaque push (`.github/workflows/tests.yml`).
- **Collecte** : workflow « Collecte » (`.github/workflows/collecte.yml`), lancé à la main depuis l'onglet *Actions* ou chaque mois ; il exécute les scripts de collecte et commite les résultats.
- Les sessions Claude écrivent le code et les documents ; GitHub Actions exécute la collecte ; GitHub Pages hébergera le site.

## Méthode (résumé)
Chaque indicateur est normalisé entre un **seuil minimal** (score 0) et un **objectif** (score 100). Les scores sont agrégés par une **moyenne généralisée pondérée** dont l'ordre règle le degré de compensation entre indicateurs puis entre dimensions (totale / limitée / nulle). Voir `docs/00_charte_projet.md`.

Licence des données : celle de chaque source (mentionnée dans les fiches). Code : à définir.
