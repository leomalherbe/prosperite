# Journal de bord — M06, audit croisé de la dimension `niveau_de_vie`

Agent auditeur M06, 15 octobre 2026, branche `m06-niveau_de_vie` (worktree isolé). L'agent n'a pas participé à M05 `niveau_de_vie`. Rapport : `docs/validation/audit_niveau_de_vie.md`.

## 0. Mise en route

- `git fetch origin && git checkout -B m06-niveau_de_vie origin/main` : base `792f1a5` (après les corrections `securite` et `egalites` et les classeurs du gel 2).
- Lus : `CLAUDE.md` ; charte §3.4, §3.6, §4, §5.1 ; journal des décisions D13-D36 (D25, D27, D29 P8, D30, D32, D34-D36 en particulier) ; méthode commune v1.2 ; fiche M06 ; `indicateurs/dimensions.yaml` ; audits `securite`, `liens_bien_etre`, `egalites`, `democratie` (format et niveau d'exigence) ; compte rendu, journal et liste de maintenance de M05 `niveau_de_vie` ; §5 de `30_crosswalk_synthese.md` et lignes utiles de `30_indicateurs_cadres_reference.csv`.
- Contrôles : `pip install -r requirements.txt && python -m pytest -q` → 398 réussis ; `python scripts/verifier_fiches.py --dimension niveau_de_vie` → 0 erreur, 7 avertissements (1 série hors catalogue avec preuve, 6 lignes déjà séries principales d'écarts d'`egalites`, dont 2 apparues avec `egalites/ecart_revenu_median_origine`, postérieure à M05).
- Travail dans `tmp/m06-niveau_de_vie/` (ignoré par git) : tables pandas de la long-list, des présélections des 7 dimensions et des séries de toutes les fiches.

## 1. Échantillon

- D'office : 2 `ecarter`, 6 incontournables, 2 `a_verifier`, 5 signalées au journal M05 (valeurs non lues, hors long-list, `raccordement: a_etudier`), 5 fiches de comptes nationaux (point d'attention D30 de la session mère, dont le PIB par habitant, D25) : 20 fiches.
- « Autres » : 5 fiches ; 20 % = 1 ; `random.Random(20261015).sample(sorted(autres), 1)` → `intensite_pauvrete`. Total 21.
- Les 4 restantes (`difficulte_joindre_deux_bouts`, `niveau_vie_modestes`, `pauvrete_persistante`, `pauvrete_ressentie`) ont été relues avec la même exigence.

## 2. Vérifications à la source (15/10/2026)

| Source | Lu | Constat |
|---|---|---|
| API Eurostat `nasa_10_nf_tr` B7G_R_HAB S14_S15 | 1975-2024 | valeurs de la fiche exactes ; unité étiquetée CP_MNAC par Eurostat |
| Métadonnées `nasa_10_nf_tr_esms` | — | déflateur implicite de la consommation finale effective S14_S15 ; base 2010 pour l'indice |
| API `nama_10_pc` P41 | 1995-2025 | exactes, `p` 2024-2025 |
| API `ilc_mdsd07`, `ilc_mdsd11`, `sdg_01_10`, `ilc_li21`, `ilc_sbjp01`, `ilc_pw01b`, `nasa_10_ki` | séries complètes | exactes ; `b` 2020 et 2022 sur EU-SILC |
| API `ilc_li22b` (non lu par M05) | 2008-2025 | 12,5 → 15,6 ; `b` 2020 (+2,1) et 2022 (+1,6) ; jeu mis à jour le 05/10/2026 |
| API `ilc_mdes09` GRT et DIF | 2004-2025 | somme = `ilc_sbjp01` à 0,1 près sur 2010-2025 ; GRT 2004 atypique (6,1 puis 3,1) |
| API `ilc_mdes03` | 2004-2025 | identique à l'INSEE 2.i1 à 0,2 près sur 2010-2024 ; plus longue et plus fraîche |
| API `ilc_li02` B_60 | 1995-2025 | `b` 2001, 2004, 2020, 2022 ; pas de rupture en 2008 |
| API `ilc_mdho06q` | 2004-2023 | « Severe housing deprivation rate by income quintile » : libellé du catalogue faux, lignes mal rangées |
| API `sdg_10_20` | — | coefficient de variation entre pays (CVA), aucune zone : NDV-10 à clore |
| BDM 011779993, 010594486, 010594393, 010594449 | séries complètes | exactes ; la BDM répond à l'outil (contrairement aux audits précédents) |
| Insee Première n° 2117 (9/07/2026) | 2024 | médiane, D1, taux et seuil de pauvreté, intensité : exacts |
| Sorties du robot : distributions, couverture, dictionnaires et tableaux croisés 2025 DREES ; PNUD | PE01, PE02, PE03, SDSITFIN, IDH | 2025 recoupé (92,08 % et 17,41 %) ; modalité spontanée de PE01 (2007, 2014) ; non-réponses PE03 en 2018 |

Refus : API Melodi (robots.txt, une tentative) ; API Banque mondiale `SN.ITK.MSFI.ZS` (autorisation non accordée à temps, non réessayée) ; une page de définition insee.fr dont l'adresse supposée était fausse (sans usage). 16 lectures Eurostat réussies sans réponse 429.

## 3. Complétude et cohérence (dépôt)

- Long-list : 11 821 lignes affectées ; 7 874 éligibles = 22 fiches, 1 161 variantes, 549 renvois, 6 142 écarts en bloc. Groupes d'écart relus un à un : un seul motif contesté (règle 740, `ilc_mdho06q`).
- Comptes nationaux (D30) : tout `DD_CNA_AGREGATS` relu par code STO × secteur, tous les `na_item` Eurostat des jeux de comptes de la long-list : aucune série de niveau de vie des ménages perdue ; l'INSEE n'a au catalogue que des évolutions par UC.
- Catalogues INSEE (`*_non` compris) : `DS_SRCV_SATISFACTION` sans domaine financier ; `DS_SRCV_PMS` seulement 2020-2025 ; aucune « pauvreté en conditions de vie » ni insécurité alimentaire ; M04 : aucune série FIES.
- Toutes les long-lists, mots-clés du niveau de vie : opinions de conjoncture sur le niveau de vie en France en `hors_grille` (D29 P8) ; très faible intensité de travail en `travail` ; rien d'autre à rapatrier.
- Renvois `autre_dimension` : `egalites` reprend 84/249, `travail` 5/354, `securite` 0/19, `planete` 0/4 → 537 lignes orphelines dans des dimensions déjà fichées.
- Séries communes avec les 6 autres dimensions fichées : seulement les composantes des écarts d'`egalites` (D32).

## 4. Résultat

25 fiches auditées : **18 conformes** (5 avec réserve Melodi), **7 à corriger**, 0 non vérifiable. 6 corrections transversales, 5 oublis, 9 points inter-dimensions, 6 désaccords de jugement. Avis : `corrections_necessaires` (mineures et ciblées). Détail et corrections ordonnées : `docs/validation/audit_niveau_de_vie.md`.
