# Fiche de mission M02 — Moissonnage du catalogue Eurostat pour la France

**Prompt de lancement** (à coller dans une nouvelle session rattachée au Projet « Observatoire de la prospérité ») :

> Tu es un agent du projet « Observatoire de la prospérité ». Lis d'abord dans le Projet la charte `claude/00_charte_projet.md`, puis cette fiche de mission `claude/missions/M02_eurostat.md`. Attache ensuite le dépôt GitHub `leomalherbe/prosperite` (accès en écriture), clone-le et lis son `CLAUDE.md`. Exécute la fiche intégralement, en français, sans modifier la charte ni le journal des décisions, en travaillant sur une branche `m02-eurostat` et en ouvrant une pull request vers `main`. Dépose les livrables documentaires dans le Projet (chemins `claude/…` de la fiche) et dans le dépôt (`docs/…`). Termine par un compte rendu dans `claude/cr/M02_compte_rendu.md` (Projet) et `docs/cr/M02_compte_rendu.md` (dépôt).

**Modèle conseillé** : Opus 5.5. **Durée estimée** : 1 session longue (partie A), 1 session courte (partie B).

## Contexte et contraintes
- Mêmes contraintes que M01 : pas d'appel réseau depuis le bac à sable ; **WebFetch** pour lire une réponse d'API et fabriquer des fixtures ; exécution réelle sur **GitHub Actions**.
- Les deux prototypes existants utilisent déjà ~66 séries Eurostat (jeu SDG). Leur liste figure dans le Projet (`claude/02_diagnostic_prototypes_v11_v6.md`) ; les codes sont dans les prototypes archivés (`90_archives/prototypes/`). Les reprendre comme **amorce**, pas comme limite.
- Tout en français (les libellés Eurostat existent en `lang=fr`).

## Objectif
Produire un **catalogue à deux niveaux** des données Eurostat disponibles pour la France, annuelles, couvrant 2000–aujourd'hui : (1) les **jeux de données** candidats, (2) pour les jeux retenus, les **séries** exactes (combinaisons de modalités) à utiliser, taguées par dimension v0.

## Partie A — Documentaire et code

### A1. Fiche source
`docs/sources/eurostat.md` : les quatre voies d'accès et leur usage dans le projet :
- **Catalogue TOC** : `https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en` (tabulé : titre, code, type, dernière mise à jour, début/fin des données, hiérarchie de dossiers) — base du niveau 1 du catalogue.
- **API statistics 1.0 (JSON-stat 2.0)** : `…/statistics/1.0/data/{code}?geo=FR&lang=fr&…` — lecture d'une série filtrée ; documenter les paramètres (`time`, `sinceTimePeriod`, `lastTimePeriod`, filtres par dimension).
- **SDMX 2.1** : `…/sdmx/2.1/dataflow/ESTAT/all`, `…/sdmx/2.1/datastructure/ESTAT/{code}` (dimensions et codelists d'un jeu), `…/sdmx/2.1/data/{code}/…`.
- **Téléchargement en masse** (TSV compressé) : `…/sdmx/2.1/data/{code}?format=TSV&compressed=true` — pour les jeux volumineux.
Préciser : pas de clé, licence (réutilisation libre avec mention), quotas (requêtes asynchrones au-delà d'une certaine taille), fréquence de mise à jour.

### A2. Modules Python
- `src/sources/eurostat.py` : `lire_toc()` → DataFrame ; `decrire_jeu(code)` → dimensions et modalités (via datastructure) ; `obtenir_donnees(code, filtres)` → lignes `serie_id, geo, periode, valeur, statut` (analyse JSON-stat 2.0 : `id`, `size`, `dimension.*.category.index`, `value` clairsemé, `status`).
- `tests/test_eurostat.py` + `tests/fixtures/eurostat/` (TOC tronqué, une réponse JSON-stat réelle — par exemple `sdg_08_10?geo=FR&lang=fr` —, une datastructure).

### A3. Script de moissonnage — niveau 1 (jeux de données)
`scripts/moissonner_catalogue_eurostat.py`, étape 1 : lire le TOC, garder `type = dataset`, `dataEnd ≥ 2020`, `dataStart ≤ 2010`. Conserver la hiérarchie de dossiers comme `theme_source`. Tagging `dimension_v0` par mots-clés sur titre et dossier ; `candidat = oui` par règle. Dossiers prioritaires (à inclure même sans match de mots-clés) : *Sustainable development indicators* (`sdg_*`), *Quality of life* (`qol`, `ilc_pw*`), *Income and living conditions* (`ilc_*`), *Labour market* (`lfs*`, `une_*`, `earn_*`), *Health* (`hlth_*`), *Education and training* (`educ_*`, `trng_*`), *Crime* (`crim_*`), *Environment* (`env_*`), *Energy* (`nrg_*`), *National accounts* (`nama_10_pc`, `nasa_10_*`), *Population* (`demo_*`), *Digital economy and society* (`isoc_*`), *Culture* (`cult_*`), *Transport safety* (`tran_sf_*`). Sortie : `catalogues/eurostat_jeux_catalogue.csv`.

### A4. Script de moissonnage — niveau 2 (séries)
Étape 2, pour chaque jeu `candidat = oui` : interroger la datastructure, construire la (les) combinaison(s) de modalités **par défaut** (totaux : `sex=T`, `age=TOTAL` ou classe la plus large, `unit` principale, `geo=FR`), vérifier via l'API JSON-stat que la série existe pour FR avec ≥ 10 points depuis 2000, enregistrer `premiere_periode`, `derniere_periode`, nombre de points, unité. Conserver aussi, en lignes séparées, les ventilations utiles pour l'axe égalités (par sexe, par quintile, par âge) lorsque le jeu les propose, avec `candidat = ventilation`. Sortie : `catalogues/eurostat_series_catalogue.csv`.

## Partie B — Exécution
- Branche `m02-eurostat`, job dans `.github/workflows/collecte.yml`, commit des CSV. Prévoir un délai entre requêtes (0,2 s) et une reprise sur erreur ; le niveau 2 peut prendre du temps : journaliser l'avancement.
- Donner dans le compte rendu : nombre de jeux dans le TOC, après filtres, candidats ; nombre de séries FR validées.

## Livrables
- `docs/sources/eurostat.md` ; `src/sources/eurostat.py` ; `tests/test_eurostat.py` + fixtures ; `scripts/moissonner_catalogue_eurostat.py`.
- `catalogues/eurostat_jeux_catalogue.csv`, `catalogues/eurostat_series_catalogue.csv` (partie B).
- `docs/sources/eurostat_amorce_prototypes.csv` : les ~66 séries des prototypes, avec leur statut (toujours disponible / code changé / à remplacer).
- `claude/cr/M02_compte_rendu.md`.

## Critères d'acceptation
- Les tests passent avec des fixtures réelles.
- Le catalogue niveau 1 conserve la hiérarchie de dossiers et le tag de dimension ; aucun jeu des dossiers prioritaires n'est perdu par les filtres sans justification.
- Le catalogue niveau 2 ne contient que des séries **vérifiées** pour FR (pas de combinaison théorique non testée).
- Les 66 séries des prototypes sont toutes statuées.

## Pièges connus
- JSON-stat renvoie `value` comme dictionnaire clairsemé indexé par position linéaire : respecter l'ordre des dimensions de `id` et les tailles de `size`.
- `geo=FR` désigne la France entière (y compris DROM selon les jeux) ; certains jeux n'ont que `FX` (métropole) ou aucune donnée France : le dire.
- Les codes `sdg_*` sont des vues recalculées de jeux sources ; noter le jeu source quand il est identifiable (plus riche en ventilations).
- Les jeux EU-SILC (`ilc_*`) ont des ruptures de série (2020, changement de méthodologie) : conserver le `statut` (drapeaux `b`, `e`, `p`, `u`) dans les sorties.

## Compte rendu attendu
Fait / non fait ; chiffres clés ; liste des 20 jeux les plus prometteurs par dimension v0 selon toi (avec codes) ; problèmes ; propositions.
