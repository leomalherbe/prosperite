# Compte rendu de fin de mission — M01 INSEE

Mission M01 « Inventaire et moissonnage des API de l'INSEE ». Phases 1 (13/10/2026) et 2 (13-14/10/2026), agents de mission successifs ; clôture le 14/10/2026. Branche `m01-insee`, PR #1. Détail des sous-tâches : `docs/cr/M01_journal.md` ; fiche source : `docs/sources/insee.md`.

## 1. Fait

| Tâche de la fiche | Livrable | État |
|---|---|---|
| A1 Cartographie des voies d'accès | `docs/sources/insee.md` §1-§6 | fait : BDM SDMX (`bdm.insee.fr`) et Melodi sans clé ; Données locales (obsolète, hors v1) et Métadonnées documentées ; fichiers insee.fr (niveau 2) examinés |
| A2 Modules Python | `src/sources/insee_http.py`, `insee_bdm.py`, `insee_melodi.py`, `insee_fichiers.py`, `insee_catalogue.py` | fait |
| A2 Tests et fixtures | `tests/test_insee_*.py`, `tests/test_collecte_insee.py`, `tests/fixtures/insee/` | fait : 207 tests passent (`python -m pytest -q`) ; fixtures BDM = réponses brutes du robot ; Melodi = enregistrements de l'INSEE et réponses du robot ; Métadonnées = SPARQL |
| A3 Script de moissonnage | `scripts/collecte_insee.py` (au lieu de `moissonner_catalogue_insee.py`, convention `collecte_<source>.py` du `CLAUDE.md`) | fait : collecte reprenable par étapes, budget de temps, cycle mensuel, catalogage hors ligne |
| A4 Repérage large et indicateurs de référence | `docs/sources/insee_indicateurs_reperes.csv` (1 063 lignes), `docs/sources/insee_indicateurs_reference.csv` (26 lignes) | fait ; 5 lignes de référence mises à jour le 14/10 d'après le catalogue complet |
| B Exécution sur GitHub Actions | `catalogues/insee_*` | fait : passage complet terminé (run 38412716221), catalogage refait avec les règles finales (runs du 14/10) |
| Contrôle qualité des catalogues complets | `docs/sources/insee.md` §12.5 | fait : échantillons par dimension et par motif, 13 familles d'erreurs corrigées |
| Comparaison avec la phase 1 | `catalogues/insee_comparaison_phase1.csv`, `docs/sources/insee.md` §12.6 | fait : tous les statuts expliqués |

Critères d'acceptation de la fiche :
- chaque voie d'accès a une fixture réelle et un test, **sauf Données locales** (aucune réponse réelle obtenue ; voie obsolète, hors v1) et les fichiers insee.fr (robots.txt ; lecteur testé sur le XLSX réel servi par Melodi) ;
- le catalogue contient les séries annuelles nationales des comptes nationaux (BDM `CNA-2020-*`, Melodi `DD_CNA_*`), de l'emploi et du chômage (BDM, Melodi `DD_EEC_SERIES`), des niveaux de vie et de la pauvreté (BDM ODD, Melodi ERFS), de la démographie (mortalité, espérance de vie ; population en contexte) et du logement (parc, construction, loyers ; surpeuplement et taux d'effort seulement en 2013/2020 à l'INSEE) ;
- les 26 indicateurs de référence sont localisés (identifiant et voie, §12.7 de la fiche source), sauf le sentiment d'insécurité (hors INSEE : SSMSI) ; le taux d'effort logement n'existe qu'en 2013 (alternative Eurostat) ;
- aucune valeur inventée ; informations introuvables marquées « non trouvé ».

## 2. Non fait, ou fait autrement
- **Données locales** : pas de fixture (aucune réponse réelle publique ; l'API est signalée obsolète au profit de Melodi).
- **Fichiers insee.fr** (niveau 2) : non moissonnés par le robot. Le seul utile repéré en phase 1 (indice de Gini, Chiffres-clés) n'est plus nécessaire : le Gini est dans Melodi.
- **Raccordement 2000-2009** (D16) des séries commencées après 2010 : signalé (`a_verifier`, 435 séries), non fait (M05).
- **Agrégation annuelle** des 512 séries infra-annuelles candidates : signalée, non faite (pipeline).
- **Dimension v1** : les catalogues restent tagués en `dimension_v0` (consigne) ; le passage v0 → v1 est fait par la long-list de M05.

## 3. Chiffres clés (catalogues finaux du 14/10/2026, `catalogues/insee_bilan.json`)
- **Collecte** (run 38412716221, 13/10, 69,7 min) : 1 976 appels HTTP, 1 030 Mo, aucune erreur, aucune clé.
- **BDM** : 244 dataflows (374 463 séries annoncées, dont 187 146 dans `SERIES_BDM`, non listé) ; **182 082 séries listées** ; 79 485 après filtres durs (fréquence, zone nationale, dernière valeur ≥ 2020) ; **1 211 `oui` + 297 `a_verifier` = 1 508 candidates**.
- **Melodi** : 145 jeux (61 traités, 84 écartés d'emblée) ; **66 287 séries nationales** ; 52 283 après filtres durs ; **5 413 `oui` + 1 183 `a_verifier` = 6 596 candidates**.
- **Candidates par dimension v0** (BDM + Melodi) : niveau de vie 3 499 ; travail 2 403 ; santé 457 ; éducation 502 ; liens et bien-être 433 ; planète 399 ; logement et cadre de vie 242 ; égalités 91 ; sécurité 46 ; démocratie 32 — **8 104** au total, dont **3 449 séries d'ensemble** et 4 655 ventilations (âge, sexe, statut d'activité, PCS, diplôme, revenu…, D21).
- **Fréquences** : 7 590 annuelles, 416 trimestrielles, 98 mensuelles. **Géographies** : BDM FE 665, FM 515, FR-D976 174, autres périmètres nationaux 154 ; Melodi `FRANCE-F` 2 866, `FE` 1 673, `FRANCE-FM` 1 540, `FEHM` 380, `FRANCE-F_X_D976` 137.
- **Drapeaux** : type moyen (D19) 551 ; raccordement (D16) 435 ; série irrégulière ou pluriannuelle (D17) 892 ; dimension déduite du regroupement 212.
- **Indicateurs ODD** : BDM 545 séries soumises (307 `oui`, 142 `a_verifier`) ; Melodi `DS_NAT_SDG` 443 (247, 146).
- **Comparaison avec la phase 1** (1 063 lignes) : 704 séries BDM confirmées, 144 écartées par un filtre dur, 10 absentes de la BDM ; 165 lignes Melodi confirmées, 14 codes non retrouvés, 4 jeux disparus, 9 jeux sans série ; 13 fichiers hors robot ; 984 séries BDM candidates nouvelles par rapport au repérage.

## 4. Problèmes rencontrés
1. **Réseau du bac à sable** : aucune API statistique joignable ; `api.insee.fr` et les fichiers d'insee.fr interdits à l'outil de lecture (robots.txt). Contournements : enregistrements de l'INSEE (paquet R `melodi`), point SPARQL, puis réponses brutes du robot comme fixtures.
2. **Volumétrie** : regroupements BDM de plus de 2 000 séries (erreur 413, découpage automatique par clé) ; catalogue Melodi de l'essai à 48 Mo pour 9 jeux (risque de dépasser la limite de 100 Mo de GitHub) : catalogues scindés candidates / écartées compressées.
3. **Qualité du tagging par mots-clés** : 13 familles d'erreurs systématiques trouvées sur les catalogues complets et corrigées (fiche source §12.5), dont des faux négatifs D17 (PISA, participation électorale) et des étiquetages absurdes (immatriculations de véhicules en « liens et bien-être »).
4. **Changements du catalogue INSEE depuis la phase 1** : jeux ERFS refondus (`DS_ERFS_INDIVIDU_SL` et voisins remplacés), jeux « dépréciés » vides (`DS_FECONDITE`, `DS_MORTALITE`), séries TCRED supprimées (salaire annuel moyen, mortalité par cause « Ensemble »), séries « France hors Mayotte » arrêtées et remplacées par « France entière » dans l'enquête Emploi.
5. **Incident git** (14/10) : un `git pull --rebase` a linéarisé le commit de fusion de `main` ; historique rétabli aussitôt par `--force-with-lease` sur la branche de mission, arbre identique vérifié, aucun run perdu. Précaution pour les sessions suivantes : après une fusion de `main`, utiliser `git pull --rebase=merges` (ou `git fetch` puis vérifier) plutôt que `git pull --rebase`.

## 5. Propositions pour la session mère
1. **INSEE plutôt qu'Eurostat** pour : niveau de vie, pauvreté et inégalités de revenu (ERFS rétropolé 1996-2024, Gini compris : enquête de référence de l'INSEE sur les revenus, appariée aux données fiscales), emploi et chômage (enquête Emploi 1975-2025, trimestriel), espérance de vie et mortalité (séries depuis 1946/1962), les 10 indicateurs de richesse nationale (BDM ODD), le taux d'épargne et la consommation des ménages (comptes base 2020). **Eurostat** pour les indicateurs SILC que l'INSEE ne publie pas en série annuelle (surpeuplement, taux d'effort) et, si ses séries sont plus longues, pour les indicateurs SRCV refondus en 2020 (privations détaillées, confiance envers les autres) : à vérifier par M02.
2. **Long-list M05** : regrouper chaque famille autour de sa série d'ensemble (57 % des candidates sont des ventilations) et dédoublonner les voies INSEE (BDM ODD / Melodi `DS_NAT_SDG`, `CNA-2020-*` / `DD_CNA_*`, mortalité, enquête Emploi) ainsi que les ITDD collectés aussi par M04 et les séries SRCV/SILC d'Eurostat (fiche source §12.8).
3. **Comptes nationaux** : n'en retenir qu'une poignée (PIB par habitant, revenu disponible et pouvoir d'achat par unité de consommation, consommation par habitant, taux d'épargne) ; les 2 273 candidates restantes sont pour l'essentiel hors v1 après la correspondance A5 (investissement, dette publique, patrimoine national).
4. **Proposer au journal** : (a) la règle D17 opérationnelle « série courte admise en `a_verifier` si l'écart moyen entre valeurs est d'au moins 1,5 an » ; (b) le recensement « dossier complet » de Melodi hors champ (trois millésimes de comparaison), sauf la suroccupation ; (c) les jeux SRCV refondus en 2020 (privations, confiance) laissés hors catalogue jusqu'à 10 points, Eurostat servant de série longue.
5. **Fusion de la PR #1** : aucun run « Collecte » n'est en cours sur la branche au moment de la clôture ; une fois fusionnée, la collecte INSEE tournera le 1er de chaque mois sur `main` (cycle `mois-AAAA-MM`, environ 70 min, catalogues commités sur `main`).
