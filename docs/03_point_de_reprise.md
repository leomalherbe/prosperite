# Point de reprise — session mère

Mis à jour le 2026-10-14 à 10 h 05 (Paris), juste avant une pause (coupure internet annoncée par Léo). Ce document permet à toute session (mère ou reprise après redémarrage) de reprendre le pilotage sans relire l'historique de conversation. Il est réécrit à chaque étape importante.

## État du projet
- **Phase 0** cadrage : fait (charte v1.2, journal D01–D33).
- **Gel 1** (dimensions) : fait le 13/10 — `indicateurs/dimensions.yaml` v1 `statut: figee` (D23–D25, D27).
- **M01 INSEE, M02 Eurostat, M03 cadres, M04 autres sources** : terminées et fusionnées dans `main` (PR #1 à #4). Catalogues complets dans `catalogues/` ; règles de catalogage actées D28–D30.
- **M05-prep** (long-list `src/pipeline/longlist.py`, 47 367 lignes, 42 concepts présents sur plusieurs dimensions) : fusionnée (PR #5), régénérée par le robot (`collecte_longlist.py`).
- **Méthode commune des fiches M05** : `docs/methodo/33_methode_fiches_M05.md` (D31), règles complémentaires des audits (D32), rattachements tranchés (D33).
- **M05 fiches indicateurs** — faites et fusionnées pour **4 dimensions sur 10** : `liens_bien_etre` (21 fiches, PR #6), `securite` (33, PR #7), `egalites` (50, PR #10), `democratie` (32, PR #11). Tableaux de validation : `docs/validation/validation_<dimension>.csv`.
- **M06 audits croisés** — faits et fusionnés pour `liens_bien_etre` (PR #8) et `securite` (PR #9) ; rapports `docs/validation/audit_<dimension>.md`.
- **PR #12 ouverte** : `m05-liens_bien_etre-corr` — corrections de `liens_bien_etre` après audit (à relire et fusionner).
- Aucun robot en cours, aucun agent actif au moment de la pause.

## Prochaines étapes (dans l'ordre)
1. Fusionner la PR #12 (corrections liens_bien_etre) après relecture.
2. Lancer **M05** pour les **6 dimensions restantes** : `niveau_de_vie`, `travail`, `logement_cadre_vie`, `sante`, `education`, `planete` (fiche `docs/missions/M05_fiches_indicateurs.md` + méthode commune 33 ; agents Opus en worktree, une dimension par agent, 2 à 3 en parallèle au plus pour éviter les conflits git ; `niveau_de_vie` et `planete` sont les plus volumineuses : comptes nationaux à réduire en familles, D30).
3. Lancer **M06** (audit croisé) pour `egalites`, `democratie`, puis chaque nouvelle dimension ; appliquer les corrections (branche `m05-<dim>-corr`).
4. Convertir les `docs/validation/validation_<dimension>.csv` en **classeurs Excel** avec listes déroulantes (`decision_leo` : retenu / retenu_socle / ecarte / a_discuter) déposés dans le dossier OneDrive `30_dimensions_indicateurs/validation/` → **gel 2** par Léo (validation par exception, dimension par dimension ; possibilité de choix cliquables en session pour les familles où l'agent hésite).
5. Après le gel 2 : socle des bornes v1 (M07), pipeline de données et millésimes (M08), front (M09), collecte (phase 7).

## Décisions en attente de Léo
- Aucune bloquante. Le gel 2 commence dès que les classeurs d'une dimension sont prêts (les 4 premières dimensions peuvent être validées sans attendre les 6 autres).
- Questions ouvertes au journal : Q-C (seuil de bascule vers les bornes émergentes), Q-D (cadre institutionnel), Q-E (répondants), Q-F (statut des objectifs ZAN et énergie-climat, à vérifier avant le socle des bornes).

## Conventions de reprise
- Lire `docs/00_charte_projet.md`, `docs/01_journal_decisions.md`, `docs/methodo/33_methode_fiches_M05.md`, puis ce document (copies dans le Projet claude.ai sous `claude/`).
- Dépôt : `leomalherbe/prosperite` (attacher avec accès en écriture ; `gh` ne fonctionne pas dans le bac à sable ; `python scripts/actions.py` pilote GitHub Actions ; branches de mission `mNN-*`).
- Dossier OneDrive de Léo « Prosperity x Claude » : copies des documents de pilotage et livrables (déposer via l'outil de fichiers de l'ordinateur lié).
- Les agents de mission tournent en Opus (D13), en worktree, avec journal de bord et arrêt-rapport ; Léo valide par exception, avec choix cliquables en session quand une décision lui revient.
