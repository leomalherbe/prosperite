# Compte rendu — mission M03 (cadres de référence, crosswalk, grille v1)

13 octobre 2026 — agent M03 (phase 2 ; la phase 1 a été conduite par un autre agent). Branche `m03-grille`, pull request #3. Détail horodaté : `docs/cr/M03_journal.md`.

## 1. Fait
| Tâche | Livrable (dépôt) | Projet claude.ai |
|---|---|---|
| T1 extraction des six cadres (phase 1) ; section Doughnut contre-vérifiée (phase 2, §1.7) | `docs/methodo/30_cadres_reference_extraction.md` | `claude/30_cadres_reference_extraction.md` (mis à jour) |
| T2 crosswalk, 344 lignes (phase 1) ; 35 lignes Doughnut corrigées (phase 2) | `docs/methodo/30_indicateurs_cadres_reference.csv` | `claude/30_indicateurs_cadres_reference.csv` (mis à jour) |
| T2 synthèse (phase 1) | `docs/methodo/30_crosswalk_synthese.md` | `claude/30_crosswalk_synthese.md` |
| T3 proposition de grille v1 | `docs/methodo/30_grille_dimensions_v1_proposition.md` | `claude/30_grille_dimensions_v1_proposition.md` |
| Dossier de décision du gel 1 | `docs/methodo/31_dossier_decision_gel1.md` | `claude/31_dossier_decision_gel1.md` |
| Correspondance v0 → v1 lisible par script | `docs/methodo/31_correspondance_v0_v1.csv` | — |
| Preuves de la contre-vérification du Doughnut | `journaux/m03_doughnut_supplementaire/` (8 extraits du dépôt Zenodo des auteurs) | — |

## 2. Non fait
- Lecture des **tableaux supplémentaires 1 et 2** du Doughnut (sources par indicateur) : inaccessibles (ORA protégé par Cloudflare, Europe PMC interrompu, Nature et PMC refusés). Les fournisseurs primaires des indicateurs sociaux restent « à vérifier ».
- Comptage des candidats sur les **catalogues de phase 2** (M01, M02, M04) : pas encore produits ; estimations faites sur le crosswalk, le repérage INSEE et les fiches M04.

## 3. Problèmes rencontrés
- Bac à sable sans accès aux archives des éditeurs : contourné par un script ponctuel du robot « Collecte » (`scripts/collecte_grille.py`, retiré après usage), qui a obtenu le dépôt Zenodo des auteurs.
- Écart non résolu sur l'eau bleue 2021-22 (article 18,2 %, dépôt 18,60 %).
- Licence du dépôt Zenodo non relevée : les extraits conservés comme preuves sont à retirer si elle l'interdit.

## 4. Propositions à la session mère (charte et journal non modifiés)
1. **Journal** : après la décision de Léo, consigner le gel 1 (grille v1, une ligne par arbitrage A1 à A16) et clore la question ouverte **Q-B**.
2. **Charte §4** : remplacer la grille v0 par la grille v1 décidée ; ajouter les **règles de partage R1 à R12** (§3 de la proposition), qui conditionnent le critère « distincte » du gel 1 et le rattachement automatique de la long-list.
3. **`indicateurs/dimensions.yaml`** v1 : renommer `securite_confiance` en `securite` et mettre à jour les contenus (statut `figee` après décision).
4. **Missions de phase 2** : priorité aux séries publiques annuelles pour `liens_bien_etre` (baromètre d'opinion DREES 2000–2024, modules SRCV, INJEP) ; confirmer l'origine Gallup et les conditions de réutilisation des séries OCDE de bien-être (M04) ; utiliser `31_correspondance_v0_v1.csv` dans le script de long-list.
5. **Gel 2** : règle « une famille de composites = une variante principale » pour la démocratie (D18) ; documenter le sens des séries de délinquance enregistrée ; trancher le rattachement de « ne pas pouvoir partir une semaine en vacances » (privation matérielle ou loisirs).
6. **Socle des bornes** : les limites par habitant du Doughnut pour six empreintes (§1.5 de l'extraction) sont des bornes « scientifiques » directement utilisables pour la dimension planète.
