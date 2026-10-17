# Point de reprise — session mère

Mis à jour le 2026-10-17 à 14 h 05 (Paris). Ce document permet à toute session (mère ou reprise après redémarrage) de reprendre le pilotage sans relire l'historique de conversation. Il est réécrit à chaque étape importante.

## État du projet
- **Phase 0** cadrage : fait (charte v1.2, journal D01–D47).
- **Gel 1** (dimensions) : fait le 13/10 (`indicateurs/dimensions.yaml` v1 figée).
- **M01–M04, M05-prep** : terminées et fusionnées (PR #1–#5).
- **M05 fiches indicateurs** : faites pour les 10 dimensions ; **M06 audits croisés** : faits pour les 10 ; **corrections après audit** : faites et fusionnées pour les 10 (dernière : logement_cadre_vie, PR #35, avec transfert de l'assainissement vers planète). Méthode commune : `docs/methodo/33_methode_fiches_M05.md` (v1.3 en cours sur la branche transversale).
- **Gel 2** : `democratie`, `liens_bien_etre`, `egalites`, `securite` **figées par Léo** (D47–D49 ; décisions dans `docs/validation/validation_<dim>.csv`, classeurs retournés archivés dans `docs/validation/classeurs/retours/`). Grille **v1.1** (D49 : sécurité économique des ménages → niveau_de_vie, transfert exécuté, PR #37). Transversal fusionné (PR #36 : socle proposé par sous-thème sur les 10 dimensions, 606 lignes renvoyées reprises, vérificateur et classeur v1.3, méthode 33 v1.3). Les **6 classeurs restants** (niveau_de_vie 39 fiches, travail 40, logement_cadre_vie 43, sante 50, education 39, planete 79) sont déposés dans le dossier OneDrive `30_dimensions_indicateurs/validation/` le 17/10 ; Léo les remplit à son rythme.
- Aucun agent en cours.

## Prochaines étapes (dans l'ordre)
1. À chaque classeur retourné (Léo enregistre sur place dans le dossier OneDrive, ou le joint dans la conversation) : `python scripts/classeur_validation.py importer --dimension <dim> --fichier <xlsx>` ; archiver le retour dans `docs/validation/classeurs/retours/` ; consigner au journal (D48…) ; traiter les `a_discuter` par questions cliquables en session.
2. Quand les 10 sont figées : **base d'indicateurs v1.0** (`statut: fige` sur les fiches, journal des modifications, versionnement sémantique, charte §3.6), puis **M07 socle des bornes v1** (seuil minimal / objectif par indicateur retenu, hiérarchie officiel > scientifique > historique > européen > expert ; vérifier Q-F ZAN et énergie-climat), **M08 pipeline de données et millésimes**, **M09 front** (3 modes + jeu), **phase 7 collecte** (Supabase UE).

## Décisions en attente de Léo
- Remplir les 8 classeurs restants (validation par exception) quand ils seront déposés.
- Questions ouvertes au journal : Q-C (seuil de bascule vers les bornes émergentes), Q-D (cadre institutionnel), Q-E (répondants), Q-F (statut des objectifs ZAN et énergie-climat).

## Conventions de reprise
- Lire `docs/00_charte_projet.md`, `docs/01_journal_decisions.md`, `docs/methodo/33_methode_fiches_M05.md`, puis ce document (copies dans le Projet claude.ai sous `claude/`).
- Dépôt : `leomalherbe/prosperite` (attacher avec accès en écriture ; `gh` ne fonctionne pas dans le bac à sable ; `python scripts/actions.py` pilote GitHub Actions ; branches de mission `mNN-*`).
- Dossier OneDrive de Léo « Prosperity x Claude » : copies des documents de pilotage et livrables (déposer via l'outil de fichiers de l'ordinateur lié).
- Les agents de mission tournent en Opus (D13), en worktree, avec journal de bord et arrêt-rapport ; Léo valide par exception, avec choix cliquables en session quand une décision lui revient.
