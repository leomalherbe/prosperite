# Journal de bord — M06, audit croisé de la dimension `travail`

Agent auditeur M06 (session neuve, Opus), 15 octobre 2026, branche `m06-travail` (worktree isolé). L'agent n'a pas participé à M05 `travail`. Rapport : `docs/validation/audit_travail.md`. Aucune fiche, aucune règle, aucun tableau, aucun script ni aucun catalogue n'a été modifié.

## 0. Mise en route (13 h 00)

- `git fetch origin && git checkout -B m06-travail origin/main` : base `792f1a5` (gel 2 : classeurs Excel), qui contient la fusion de la PR #15 (fiches `travail`, commit `dc4393c`) et les corrections `egalites` (PR #19) et `securite` (PR #18).
- Lus : `CLAUDE.md` ; charte §3.4, §3.6, §4, §5.1 ; journal D13 à D36 (en particulier D27, D32, D34, D35, D36) ; méthode commune v1.2 (`docs/methodo/33_methode_fiches_M05.md`) ; fiche M06 ; `indicateurs/dimensions.yaml` (contenu et exclusions de `travail`, R1 à R8) ; audits `securite`, `liens_bien_etre`, `egalites`, `democratie` (structure, exigence, graine) ; §5 de `30_crosswalk_synthese.md` et lignes « travail » de `30_indicateurs_cadres_reference.csv`.
- Matériau audité : 37 fiches `indicateurs/travail/*.yaml`, `validation_travail.csv`, `preselection_travail.csv` (123 groupes), `preselection_travail_lignes.csv` (6 525 lignes), `regles_preselection_travail.csv`, journal et compte rendu M05, `maintenance_catalogues_travail.md` (TRA-1 à TRA-10), `catalogues/longlist_travail.csv.gz` (6 520 lignes) et les autres long-lists, catalogues INSEE, Eurostat (séries, jeux, `*_non`), extraits du robot M04 (`docs/sources/series/`), export du catalogue data.ameli.fr (`docs/sources/verif_acces/extraits/`).
- Contrôles de départ : `python -m pytest -q` → 398 réussis ; `python scripts/verifier_fiches.py --dimension travail` (sans `--tableau`) → 0 erreur, **3** avertissements (les deux fiches DREES hors catalogue, attendus, et un nouveau : `surqualification`, ligne `estat-054299` déjà série principale de `egalites/ecart_surqualification_origine`, créée par la PR #19 après la fusion de `travail`) ; compteurs : 37 fiches, 28 familles, 24 `retenir`, 8 `retenir_variante`, 5 `ecarter`, 3 déclaratives, 0 composite, 3 « à vérifier », 2 hors long-list, 4 incontournables, 1 675 variantes, 652 lignes `autre_dimension`, 1 ligne prise ailleurs.

## 1. Échantillon

- D'office : 5 `ecarter` ; 4 `incontournable: oui` ; 3 `a_verifier` ; 9 fiches des points d'attention de la session mère et des priorités demandées par M05 (§7.5 de son compte rendu) : `taux_chomage`, les deux formules (`taux_chomage_longue_duree`, `part_emploi_temporaire`), les trois mesures `PT_*` de Melodi (`neet`, `halo_chomage`, `taux_sous_emploi`), les deux fiches d'accidents, `satisfaction_travail` ; 5 autres `raccordement: a_etudier` (`emploi_temporaire_subi`, `temps_partiel_subi`, `transitions_temporaire_permanent`, `travail_dimanche`, `travail_nuit`) ; 2 hors long-list (`preoccupation_chomage`, `risque_chomage_percu`). Total d'office : 28.
- Tirage : 20 % des 28 « autres » fiches (ni `ecarter` ni incontournables) = 5,6, arrondi à 6, tirées parmi les 9 qui n'étaient pas déjà retenues d'office. `random.Random(20261014).sample(pool, 6)` en Python 3, `pool` = liste triée `['contrats_tres_courts', 'horaires_atypiques', 'menages_tres_faible_intensite_travail', 'passages_emploi_chomage', 'pauvrete_en_emploi', 'salaire_net_moyen_reel', 'sorties_chomage_emploi', 'sous_utilisation_main_oeuvre', 'surqualification']`, **graine 20261014** (celle des audits précédents) → `horaires_atypiques`, `menages_tres_faible_intensite_travail`, `passages_emploi_chomage`, `salaire_net_moyen_reel`, `sous_utilisation_main_oeuvre`, `surqualification`.
- Les 3 restantes (`contrats_tres_courts`, `pauvrete_en_emploi`, `sorties_chomage_emploi`) ont été vérifiées à la source elles aussi (contrôle complet, pas seulement léger) : **37 fiches sur 37**.

## 2. Vérifications à la source (WebFetch, 15/10/2026)

| Source | Lu | Constat |
|---|---|---|
| Eurostat `lfsa_qoe_3a2` | 2000-2025 | 8,0 (2002) → 13,4 (2003, b) → 9,4 (2025) ; b 2003, 2005, 2006, 2014 ; bd 2021, 2024 ; d 2022, 2023, 2025 ; 11,7 (2020) → 10,0 (2021) |
| Métadonnées `lfsa_qoe_esms` | page | longues heures = « 49 heures ou plus par semaine » ; emploi précaire = « salariés avec un contrat de courte durée de 3 mois au plus » (en % des salariés) |
| Note Eurostat du 9/2/2018 (DDN-20180209-1) | page | emploi précaire : contrat de trois mois au plus, % des salariés ; France 4,8 % en 2016 |
| Eurostat `sdg_08_30` (20-64) | 2009-2025 | 69,8 → 75,4 ; d 2021-2025 |
| Eurostat `lfsi_emp_a` (20-64) | 2003-2025 | 70,0 (2003) … 69,8 (2009) … 75,4 (2025) : identique à `sdg_08_30` de 2009 à 2025 ; d 2021-2025 |
| Eurostat `hsw_exp1` (15-64) | 2007, 2013, 2020 | 49,0 d ; 60,8 d ; 53,5 b |
| Eurostat `hsw_exp2` (15-64) | 2007, 2013, 2020 | 70,0 d ; 81,6 bd ; 74,9 b (exposition physique, long-list `sante`) |
| Eurostat `hsw_pb1` (15-64) | 2007, 2013, 2020 | 48,9 d ; 12,4 ; 8,3 (problèmes de santé liés au travail, long-list `sante`) |
| Eurostat `hsw_n2_02`, `sdg_08_60` | 2008-2024, 2010-2024 | 1,56 → 3,61 ; b 2014, 2017, 2020, 2022 ; identiques depuis 2010 ; 2,74 (2018) → 3,54 (2019) sans drapeau |
| Eurostat `hsw_n2_01` | 2008-2024 | 3 443,59 → 2 303,37 (2009) → 2 621,94 (2024) ; b 2014, 2017, 2020, 2022 |
| Eurostat `lfsa_eppgai` | 1992-2025 | 26,7 (2000), 33,5 (2012) → 38,7 (2013, sans drapeau), 41,5 (2014, b), 36,9 (2020) → 27,2 (2021, b), 20,3 (2025) ; b aussi en 2003, 2005, 2006, 2024 ; aucun « d » |
| Eurostat `lfsa_eetpgar` (NF_PJOB, PC_SAL) | 2003-2025 | unité « pourcentage des salariés » ; 7,3 (2020) → 5,8 (2021, bd) → 3,6 (2025) ; b 2003, 2005, 2006, 2014 ; bd 2024 |
| Eurostat `ilc_lvhl36` | 2008-2025 | 12,0 (2019) → 19,3 (2020, b) ; 27,7 (2023, b) ; 32,5 (2024) ; 28,2 (2025) |
| Eurostat `lfsa_ewpnig`, `lfsa_ewpsun` | 1992-2025 | nuit 7,1 (2012) → 3,7 (2013, sans drapeau), 3,9 (2025) ; dimanche 9,7 → 12,9 (2003, b), 14,6 (2025) ; 2022 et 2024 absents |
| Eurostat `lfsa_esegatyp` | 2011-2025 | 37,9 → 34,2 ; 2022 et 2024 absents ; b 2014, bd 2021, d 2023, 2025 ; pas de dimension sexe |
| Eurostat `ilc_lvhl11` | 2004-2025 | 10,3 → 9,0 ; b 2020, 2022 |
| Eurostat `lfsi_long_a` EMP_UNE, UNE_EMP | 2011-2025 | 3,0 → 2,9 (2021 absent ; b 2014 ; d 2018, 2022-2025 ; bd 2024) ; 36,4 → 33,4 (2020) → 42,3 (2022, d) → 41,3 (2025), 2021 absent |
| Eurostat `lfsa_eoqgan` | 1995-2025 | 18,0 (2000) → 20,4 (2025) ; b 1998, 2003, 2005, 2006, 2013, 2014 ; bd 2021, 2024 |
| Eurostat `ilc_iw01` | 2004-2025 | 5,4 → 8,7 ; b 2008, 2020, 2022 |
| Eurostat `lfsa_qoe_4ax1r2` | 2008-2025 | 4,8 → 3,9 ; b 2014 ; bd 2021, 2024 ; d 2022, 2023, 2025 |
| Eurostat `earn_ses_pub1s` | 2006-2022 | 7,13 / 6,08 / 8,81 / 8,61 / 9,68, sans drapeau |
| Eurostat `lfsi_sla_a` (SLACK, 15-74) | 2014-2025 | 20,0 → 15,0 ; d 2021-2025 |
| BDM 011818634, 011818669, 011818623, 011818639, 011818670, 011818581 | 2003-T1 à 2026-T2 | titres, zone FE, CVS ; valeurs de contrôle pour TRA-3 (§3 du rapport) |
| BDM 010596081 (IRN 1) | 1975-2025 | FR-D976 ; 68,8 % en 2024 ; 2025 sans valeur |
| BDM 010597456 | 1996-T1 à 2026-T2 | demandeurs de catégorie A, France hors Mayotte, CVS-CJO |
| BDM 010752333 | 1996-2024 | salaire net annuel moyen EQTP du privé, zone `FM99_FR00` (France métropolitaine jusqu'en 1999) ; 32 791 € en 2024 |
| insee.fr 8977323, 8977299 | pages | rétropolations 2003, 2011, 2013, 2021, 2024 ; « hypothèses et choix » ; tableaux t302-t310 en xlsx |

**Non lus** : API Melodi (robots.txt, comme pour M05) ; fichiers xlsx d'insee.fr (robots.txt) ; `catalogue-donnees.insee.fr` (JavaScript) ; outil interactif 5369554 (JavaScript) ; data.ameli.fr et API SDMX de l'OCDE (autorisation non accordée à temps, non relancées) ; API Eurostat `lfsa_ewhuis`, `une_ltu_a`, `lfsi_neet_a` (HTTP 429, non relancées conformément à la consigne de l'outil).

Fichiers du dépôt lus (sans saisie de valeur) : `cnam_ameli__sinistralite_naf1.csv`, `ocde__hsl_bien_etre_actuel.csv`, `drees__barometre_2000_2025_distributions.csv`, `drees__barometre_2000_2025_couverture.csv`, dictionnaires DREES 2025, `cnam_ameli__ods_catalogue_export.txt`, fixtures Melodi `DS_SRCV_SATISFACTION`, catalogues Melodi (périodes de `TRAVSATISF`).

## 3. Contrôles par script (bac à sable, non commités)

- Comparaison fiches / long-list (périodes, points, zone, éligibilité, URL) : toutes les périodes et tous les nombres de points des séries principales sont ceux de la long-list ; l'URL d'API de `bas_salaires` n'est pas dans la long-list (construite par M05).
- Recalcul OG04_6 (modalités 1 + 2, NSP au dénominateur) : 90,67 (2000), 88,68 (2010), 63,49 (2025) ; 25 années.
- Contrôle Ameli : 549 614 accidents / 20 799 600 salariés × 1 000 = 26,42 (2024), cohérent avec l'indice de 26,4 ; maladies professionnelles : 50 598 / 20 799 600 × 1 000 = 2,43.
- Inter-dimensions (séries principales, composantes, variantes, lignes de présélection) contre toutes les autres fiches : 1 ligne commune (`estat-054299`) ; lignes envoyées vers `travail` par `niveau_de_vie` et non reprises : 349 ; lignes envoyées par `travail` et non reprises : `securite` 171, `egalites` 307 (dont 305 ventilations par sexe, conformes à D35), `planete` 4 ; recherche des jeux de la dimension dans les autres long-lists (`hsw_*` en `sante`, `sdg_08_20` en `education`, `ilc_lvhl17` en `logement_cadre_vie`).
- Unicité des `serie_id` de variantes (D36) : aucun doublon.

## 4. Rédaction et livraison

- Rapport `docs/validation/audit_travail.md` ; copie dans le Projet (`claude/cr/M06_travail_audit.md`) ; PR **#24** « M06 — audit croisé : travail » ouverte vers `main` par l'API GitHub (`POST /repos/leomalherbe/prosperite/pulls`).
- Aucun fichier sous `scripts/`, `src/`, `indicateurs/`, `catalogues/` modifié ; `.claude/` non commité.
