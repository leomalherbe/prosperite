# Point de reprise — session mère

Mis à jour le 2026-10-17 à 12 h 15 (Paris). Ce document permet à toute session (mère ou reprise après redémarrage) de reprendre le pilotage sans relire l'historique de conversation. Il est réécrit à chaque étape importante.

## État du projet
- **Phase 0** cadrage : fait (charte v1.2, journal D01–D47).
- **Gel 1** (dimensions) : fait le 13/10 (`indicateurs/dimensions.yaml` v1 figée).
- **M01–M04, M05-prep** : terminées et fusionnées (PR #1–#5).
- **M05 fiches indicateurs** : faites pour les 10 dimensions ; **M06 audits croisés** : faits pour les 10 ; **corrections après audit** : faites et fusionnées pour les 10 (dernière : logement_cadre_vie, PR #35, avec transfert de l'assainissement vers planète). Méthode commune : `docs/methodo/33_methode_fiches_M05.md` (v1.3 en cours sur la branche transversale).
- **Gel 2** : `democratie` et `liens_bien_etre` **figées par Léo** (D47 ; décisions dans `docs/validation/validation_<dim>.csv`, classeurs retournés archivés dans `docs/validation/classeurs/retours/`). Les 8 autres dimensions attendent leurs classeurs.
- **En cours** : branche `m05-transversal-gel2` (agent lancé le 17/10 à 12 h 10) — socle proposé par sous-thème (D41) sur les 10 dimensions, lignes renvoyées non reprises (D46), vérificateur et classeur v1.3, tableaux de validation régénérés → PR à fusionner.

## Prochaines étapes (dans l'ordre)
1. Fusionner la PR transversale ; `python -m pytest -q` ; vérificateur à 0 erreur sur les 10 dimensions ; `--lignes-renvoyees` sans orpheline.
2. Générer les **8 classeurs** restants (`python scripts/classeur_validation.py exporter --toutes`, v1.3 : défaut `retenu_socle` = `socle_propose: oui`) et les déposer dans le dossier OneDrive `30_dimensions_indicateurs/validation/` (ne pas écraser les deux classeurs validés) ; prévenir Léo.
3. À chaque classeur retourné : `python scripts/classeur_validation.py importer --dimension <dim> --fichier <xlsx>` ; archiver le retour dans `docs/validation/classeurs/retours/` ; consigner au journal (D48…) ; traiter les `a_discuter` par questions cliquables en session.
4. Quand les 10 sont figées : **base d'indicateurs v1.0** (`statut: fige` sur les fiches, journal des modifications, versionnement sémantique, charte §3.6), puis **M07 socle des bornes v1** (seuil minimal / objectif par indicateur retenu, hiérarchie officiel > scientifique > historique > européen > expert ; vérifier Q-F ZAN et énergie-climat), **M08 pipeline de données et millésimes**, **M09 front** (3 modes + jeu), **phase 7 collecte** (Supabase UE).

## Décisions en attente de Léo
- Remplir les 8 classeurs restants (validation par exception) quand ils seront déposés.
- Questions ouvertes au journal : Q-C (seuil de bascule vers les bornes émergentes), Q-D (cadre institutionnel), Q-E (répondants), Q-F (statut des objectifs ZAN et énergie-climat).

## Conventions de reprise
- Lire `docs/00_charte_projet.md`, `docs/01_journal_decisions.md`, `docs/methodo/33_methode_fiches_M05.md`, puis ce document (copies dans le Projet claude.ai sous `claude/`).
- Dépôt : `leomalherbe/prosperite` (attacher avec accès en écriture ; `gh` ne fonctionne pas dans le bac à sable ; `python scripts/actions.py` pilote GitHub Actions ; branches de mission `mNN-*`).
- Dossier OneDrive de Léo « Prosperity x Claude » : copies des documents de pilotage et livrables (déposer via l'outil de fichiers de l'ordinateur lié).
- Les agents de mission tournent en Opus (D13), en worktree, avec journal de bord et arrêt-rapport ; Léo valide par exception, avec choix cliquables en session quand une décision lui revient.
