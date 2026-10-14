# Fiche de mission M05 — Long-list, éligibilité et fiches indicateurs par dimension

**Prérequis** : grille v1 figée (gel 1, charte §3.6) ; catalogues de phase 2 fusionnés dans `main` (M01, M02, M04) ; long-list régénérée (`catalogues/longlist_<dimension>.csv.gz`, bilan du 14/10/2026). **Remplis.**

**Échelle du travail (précision du 14/10)** : la long-list compte 64 719 lignes (47 367 éligibles) parce qu'elle contient toutes les séries des jeux Eurostat et INSEE (une ligne par unité, par modalité, par ventilation). Le travail des fiches se fait au niveau du **concept** : une fiche par indicateur distinct et intelligible pour le public, les ventilations, unités alternatives, autres sources et sous-séries détaillées (par produit, par branche, par tranche d'âge…) étant rattachées comme **variantes** à la fiche de leur concept, et les sous-séries sans intérêt propre écartées **en bloc** par une règle motivée (ex. « séries par produit du jeu X : écartées, la variante principale est l'agrégat »). Pas de plafond a priori, mais l'ordre de grandeur attendu est de quelques dizaines de fiches par dimension, pas des milliers.

**Prompt de lancement** (une session par dimension, ou par groupe de dimensions ; Opus) :

> Tu es un agent du projet « Observatoire de la prospérité ». Lis dans le Projet la charte `claude/00_charte_projet.md` (§3.4, §3.6, §5.1), le journal des décisions, puis cette fiche `claude/missions/M05_fiches_indicateurs.md`. Attache le dépôt `leomalherbe/prosperite`, clone-le, lis `CLAUDE.md`. Travaille sur la branche `m05-<dimension>` et ouvre une pull request. Dimension(s) à traiter : `<id>`. Termine par un compte rendu `claude/cr/M05_<dimension>_compte_rendu.md` et `docs/cr/`.

## Objectif
Pour une dimension figée, produire la liste **complète** des indicateurs éligibles avec une fiche YAML par indicateur, regroupés en familles, chacun avec une recommandation motivée — la matière du classeur de validation de Léo (gel 2).

## Entrées
- `indicateurs/dimensions.yaml` (v1 figée) ; `catalogues/*.csv` (INSEE BDM/Melodi, Eurostat jeux et séries, autres sources) ; `docs/methodo/30_indicateurs_cadres_reference.csv` (incontournables et seuils) ; `docs/sources/*.md` (voies d'accès).
- Script commun `src/pipeline/longlist.py` (fourni par la session mère avant le lancement) : union des catalogues, rattachement à la grille v1, dédoublonnage par concept, filtre d'éligibilité, sortie `catalogues/longlist_<dimension>.csv` avec colonne `eligible` et `motif_exclusion`.

## Tâches
1. **Lire la long-list** de la dimension (`catalogues/longlist_<dimension>.csv.gz`, déjà produite ; relancer `python -m src.pipeline.longlist --dimension <id>` seulement si les catalogues ont changé) et relire les exclusions : signaler toute exclusion abusive (ex. série annuelle mal détectée) dans le journal, corriger le catalogue source si c'est une erreur de collecte (PR séparée). Produire d'abord un **tableau de présélection** `docs/validation/preselection_<dimension>.csv` : une ligne par concept (groupe de lignes de la long-list), avec le nombre de lignes regroupées, la décision de présélection (`fiche` | `variante_de:<id>` | `ecarte_en_bloc`) et le motif.
2. **Dédoublonnage et familles** : regrouper les lignes éligibles par concept (`famille`), désigner la **variante principale** (critères : source niveau 1 > 2 ; INSEE > Eurostat à définition égale, sauf profondeur ou fraîcheur meilleure ailleurs ; série la plus longue ; total avant ventilation) et lister les variantes (seuils alternatifs, ventilations, autre source).
3. **Fiches** : un fichier `indicateurs/<dimension>/<id>.yaml` par indicateur éligible (schéma charte §5.1 ; champs supplémentaires : `famille`, `variante_principale: oui|non`, `composite`, `raccordement`, `recommandation: retenir|retenir_variante|ecarter`, `motif_recommandation`, `note_pertinence` de 2 à 4 phrases, `incontournable: oui|non` (présent dans ≥ 3 cadres de référence)). Pas de bornes à ce stade (`socle_v1` vide).
4. **Tableau de validation** : `docs/validation/validation_<dimension>.csv` — une ligne par fiche : id, libellé, famille, variante principale, définition courte, source, période, type, déclaratif, composite, incontournable, recommandation, motif, `decision_leo` (vide), `commentaire_leo` (vide). La session mère le convertit en classeur Excel avec listes déroulantes.
5. **Contrôles** : aucun id en double ; chaque fiche a une source et un identifiant de série vérifiés dans les catalogues ; le nombre de `retenir` par dimension est noté dans le journal ; les indicateurs `declaratif: oui` sont présents s'ils existent.
6. Journal de bord `docs/cr/M05_<dimension>_journal.md`, commits fréquents, PR.

## Critères d'acceptation
- Toutes les lignes éligibles de la long-list ont une fiche ou un motif d'exclusion.
- Les incontournables du crosswalk pour la dimension sont tous présents (ou leur absence est expliquée : non disponible pour la France).
- Les recommandations sont motivées en une phrase vérifiable (pas d'appréciation vague).

## Pièges
- Deux indicateurs qui mesurent le même concept avec des définitions différentes (INSEE vs Eurostat) ne sont pas des doublons stricts : même famille, variantes.
- Un indicateur de pression (émissions) et un indicateur d'état (concentration) ne sont pas la même famille.
- Ne pas écarter un indicateur parce qu'il est « redondant » avec une autre dimension : signaler, la session mère tranche le rattachement.
