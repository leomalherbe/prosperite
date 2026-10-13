# Fiche de mission M01 — Inventaire et moissonnage des API de l'INSEE

**Prompt de lancement** (à coller dans une nouvelle session rattachée au Projet « Observatoire de la prospérité ») :

> Tu es un agent du projet « Observatoire de la prospérité ». Lis d'abord dans le Projet la charte `claude/00_charte_projet.md`, puis cette fiche de mission `claude/missions/M01_insee.md`. Attache ensuite le dépôt GitHub `leomalherbe/prosperite` (accès en écriture), clone-le et lis son `CLAUDE.md`. Exécute la fiche intégralement, en français, sans modifier la charte ni le journal des décisions, en travaillant sur une branche `m01-insee` et en ouvrant une pull request vers `main`. Dépose les livrables documentaires dans le Projet (chemins `claude/…` de la fiche) et dans le dépôt (`docs/…`). Termine par un compte rendu dans `claude/cr/M01_compte_rendu.md` (Projet) et `docs/cr/M01_compte_rendu.md` (dépôt).

**Modèle conseillé** : Opus 5.5 (code + connaissance des API). **Durée estimée** : 1 session longue (partie A), puis 1 session courte (partie B, après création du dépôt GitHub).

## Contexte et contraintes
- Le bac à sable de ta session **ne peut pas exécuter d'appels réseau vers les API** (seuls GitHub et les dépôts de paquets sont joignables). Pour **voir** une réponse d'API, utilise l'outil de lecture de page web (WebFetch) sur l'URL de l'API : il te rend la structure et des valeurs. Enregistre ces réponses comme **fixtures** pour les tests.
- L'exécution réelle des scripts se fait sur **GitHub Actions** (partie B). Si le dépôt n'est pas encore attaché à ta session, fais la partie A et livre les fichiers en pièces jointes dans la conversation ; dis-le dans le compte rendu.
- Tout en français. Python 3.12, `requests`, `pandas`, `pydantic`, `pytest`. Pas de clé d'API en dur dans le code (variables d'environnement).

## Objectif
Produire (1) la cartographie complète des voies d'accès aux données de l'INSEE, (2) des modules Python testés pour les interroger, (3) un **catalogue des séries annuelles nationales candidates** pour l'indicateur de prospérité, tagué par dimension v0.

## Partie A — Documentaire et code (faisable sans le dépôt)

### A1. Cartographie des voies d'accès
Pour chacune des voies suivantes, établir : URL de base, authentification (clé ? compte sur portail-api.insee.fr ?), formats (SDMX-ML, JSON, CSV), quotas, moyen de **lister le catalogue**, moyen d'obtenir **une série complète**, licence, exemple de requête et exemple de réponse (fixture).
1. **BDM — service web SDMX** (`https://bdm.insee.fr/series/sdmx/…`) : dataflows, structures, codelists, données par idbank (`/data/SERIES_BDM/{idbank}`) ou par dataflow et clé.
2. **Melodi** (`https://api.insee.fr/melodi/…`) : catalogue des jeux de données, structure d'un jeu, extraction filtrée, format JSON.
3. **Données locales** (cubes communaux) : documenter seulement (hors périmètre v1).
4. **Métadonnées** (concepts, nomenclatures, indicateurs) : documenter seulement.
5. **Fichiers insee.fr à URL stable** (xlsx/csv des pages « Indicateurs de richesse nationale », « Tableau de bord de l'économie française », « France, portrait social », SRCV) : niveau 2 selon la charte.
Sources à lire : `https://www.insee.fr/fr/information/8184146` (catalogue des API), `https://portail-api.insee.fr/catalog/all`, guide BDM SDMX (PDF sur insee.fr), documentation des paquets R `insee` et `melodi` et du paquet Python `pynsee` (ils révèlent les points d'entrée réels).
Livrable : `docs/sources/insee.md`.

### A2. Modules Python
- `src/sources/insee_bdm.py` : `lister_dataflows()`, `lister_series(dataflow)` (clés + attributs : IDBANK, TITLE_FR, FREQ, UNIT_MEASURE, REF_AREA, LAST_UPDATE, première/dernière période), `obtenir_serie(idbank)` → lignes `serie_id, geo, periode, valeur, statut`. Analyse SDMX-ML 2.1 (StructureSpecificData).
- `src/sources/insee_melodi.py` : `lister_jeux()`, `decrire_jeu(id)`, `obtenir_donnees(id, filtres)` → même format de sortie.
- `src/sources/insee_fichiers.py` : téléchargement d'un xlsx/csv à URL stable et lecture d'une feuille (niveau 2).
- `tests/` avec fixtures enregistrées (une réponse réelle par point d'entrée, obtenue via WebFetch ou via la documentation).

### A3. Script de moissonnage
`scripts/moissonner_catalogue_insee.py` : produit `catalogues/insee_bdm_catalogue.csv` et `catalogues/insee_melodi_catalogue.csv` (colonnes de la charte §5.3). Filtres : fréquence annuelle (ou trimestrielle/mensuelle agrégable, drapeau `agregable`), couverture France (métropole / France entière / hors Mayotte — garder les trois, colonne `geo` explicite), dernière période ≥ 2020, première période ≤ 2010. Tagging `dimension_v0` par règles de mots-clés sur le libellé (grille v0 de la charte §4) ; `candidat = oui` si une règle a matché et que le libellé décrit un **résultat** pour la population (pas un indice de prix sectoriel, pas une série d'entreprise).

### A4. Liste de contrôle des indicateurs de référence
Vérifier et documenter (id exact, fréquence, période couverte, voie d'accès) la disponibilité INSEE des indicateurs suivants : les **10 indicateurs de richesse nationale** (taux d'emploi, effort de recherche, endettement, espérance de vie en bonne santé, satisfaction dans la vie, inégalités de revenus, pauvreté en conditions de vie, sorties précoces du système scolaire, empreinte carbone, artificialisation des sols) ; taux de pauvreté monétaire (60 %) ; niveau de vie médian ; rapport interdécile ; indice de Gini ; taux de chômage BIT ; taux d'emploi 15–64 ; espérance de vie à la naissance ; PIB par habitant en volume ; dépense de consommation des ménages par habitant ; taux d'épargne ; satisfaction dans la vie (SRCV) ; sentiment d'insécurité (enquête CVS/VRS) ; part des ménages en surpeuplement ; taux d'effort logement.
Livrable : tableau dans `docs/sources/insee.md` (section « Indicateurs de référence »).

## Partie B — Exécution (quand le dépôt GitHub est attaché)
- Pousser les fichiers sur une branche `m01-insee`, ajouter un job au workflow `.github/workflows/collecte.yml` (ou en créer un) qui exécute `scripts/moissonner_catalogue_insee.py` et commite les CSV dans `catalogues/`.
- Lire le journal d'exécution, corriger jusqu'à réussite. Indiquer le nombre de lignes obtenues par catalogue et le nombre de `candidat = oui`.

## Livrables (chemins exacts)
- `docs/sources/insee.md` — fiche source complète (A1 + A4).
- `src/sources/insee_bdm.py`, `src/sources/insee_melodi.py`, `src/sources/insee_fichiers.py`, `tests/test_insee_*.py`, `tests/fixtures/insee/*`.
- `scripts/moissonner_catalogue_insee.py`.
- `catalogues/insee_bdm_catalogue.csv`, `catalogues/insee_melodi_catalogue.csv` (partie B).
- `claude/cr/M01_compte_rendu.md` dans le Projet.

## Critères d'acceptation
- Chaque voie d'accès a une fixture réelle et un test qui passe (`pytest`).
- Le catalogue BDM contient au moins les séries annuelles nationales de : comptes nationaux, emploi-chômage, niveaux de vie/pauvreté, démographie, logement — ou le compte rendu explique pourquoi certaines ne sont pas dans BDM (et où elles sont : Melodi, fichiers).
- Les 24 indicateurs de référence sont chacun soit localisés (id + voie), soit déclarés « non disponibles à l'INSEE par API » avec la voie alternative connue (Eurostat, fichier).
- Aucune valeur inventée : une information non trouvée est marquée « non trouvé ».

## Pièges connus
- BDM contient surtout des séries conjoncturelles mensuelles/trimestrielles ; beaucoup d'indicateurs sociaux annuels sont dans Melodi ou seulement en fichiers.
- Les codes de zone (REF_AREA) varient selon les séries (France métropolitaine, France entière, France hors Mayotte) : ne pas fusionner, documenter.
- Le portail API de l'INSEE a changé le 17 octobre 2024 : vérifier quelles API demandent une clé **aujourd'hui**, ne pas se fier à des tutoriels antérieurs.
- Les réponses SDMX-ML sont volumineuses : utiliser `detail=serieskeysonly` ou équivalent pour lister sans télécharger les observations.

## Compte rendu attendu (`claude/cr/M01_compte_rendu.md`)
Fait / non fait ; chiffres clés (nombre de dataflows, de séries, de candidats) ; problèmes rencontrés ; propositions pour la session mère (ex. indicateurs INSEE à privilégier par rapport à Eurostat, et pourquoi).
