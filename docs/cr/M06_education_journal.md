# Journal de bord — M06, audit croisé de la dimension `education`

Agent auditeur M06 (session neuve, Opus), 16 octobre 2026, branche `m06-education` (worktree isolé). L'agent n'a pas participé à M05 `education`. Rapport : `docs/validation/audit_education.md`. Aucune fiche, aucune règle, aucun tableau, aucun script ni aucun catalogue n'a été modifié. Scripts de travail dans `tmp/m06-education/` (ignoré par git).

## 0. Mise en route (09 h 00)

- `git fetch origin && git checkout -B m06-education origin/main` : base `d85ef3a` (journal D37-D40, classeur `democratie`), qui contient la fusion de la PR #22 (fiches `education`, commit `d4deaa3`) et celle de `logement_cadre_vie` (PR #26), postérieure.
- Lus : `CLAUDE.md` ; charte §3.4, §3.6, §4, §5.1 ; journal D13 à D40 (en particulier D17, D25 (A5), D24 (A7, A13), D28, D32, D34, D35, D36, D38 a, d, f, g) ; méthode commune v1.2 (`docs/methodo/33_methode_fiches_M05.md`, en entier) ; fiche M06 ; `indicateurs/dimensions.yaml` (dimension `education`, R1 à R8) ; audits modèles `audit_travail.md` et `audit_planete.md`, journal `M06_travail_journal.md` ; §5 de `30_crosswalk_synthese.md` et lignes « éducation » de `30_indicateurs_cadres_reference.csv`.
- Matériau audité : 38 fiches `indicateurs/education/*.yaml`, `validation_education.csv`, `preselection_education.csv` (104 groupes), `preselection_education_lignes.csv` (4 623 lignes), `regles_preselection_education.csv` (104 règles), journal et compte rendu M05, lignes 36 à 44 de `docs/cr/maintenance_catalogues.md`, `catalogues/longlist_education.csv.gz` et les autres long-lists, catalogues Eurostat (séries et jeux), extraits du robot M04 (`docs/sources/series/` : OCDE How's Life, PNUD, DEPP, SDES ITDD, DREES).
- Contrôles de départ : `pip install -r requirements.txt && python -m pytest -q` → **399 réussis** ; `python scripts/verifier_fiches.py --dimension education` (sans `--tableau`) → **0 erreur, 2 avertissements** (fiches hors long-list `difficultes_lecture_jdc` et `eleves_faibles_competences_numeriques`, attendus) ; compteurs : 4 503 lignes de long-list, 225 `autre_dimension`, 0 ligne prise ailleurs, 38 fiches, 25 familles, 23 `retenir`, 13 `retenir_variante`, 2 `ecarter`, 0 déclarative, 0 composite, 17 « à vérifier », 2 hors long-list, 12 incontournables, 378 variantes.

## 1. Échantillon (09 h 20)

- D'office : 2 `ecarter` (`depense_publique_education`, `taux_reussite_bac`) ; 12 `incontournable: oui` ; 10 éligibilités `a_verifier`/`non` non comptées ailleurs ; 2 hors long-list ; 3 `raccordement: a_etudier` non comptés ailleurs (`formation_adultes_4_semaines`, `prescolarisation_3_ans`, `proportion_bacheliers_generation`) ; la seconde série calculée (`accueil_formel_moins_3_ans`) ; une fiche aux valeurs non relues (`personnel_recherche`) ; deux points soumis à Léo par M05 (`specialistes_tic`, `demandes_brevets`). Total : 33.
- Tirage : 20 % des 24 « autres » fiches (ni `ecarter` ni incontournables) = 4,8, arrondi à 5, tirées parmi les 5 fiches non retenues d'office : `random.Random(20261014).sample(pool, 5)` en Python 3, `pool` = liste triée `['adultes_peu_diplomes', 'diplomes_superieur_25_34', 'duree_moyenne_scolarisation', 'effort_recherche_pib', 'esperance_scolarisation']`, **graine 20261014** (celle des audits précédents) → les 5. **38 fiches sur 38** vérifiées à la source.

## 2. Vérifications à la source (WebFetch, 16/10/2026)

| Source | Lu | Constat |
|---|---|---|
| Eurostat `sdg_04_10` (18-24, T) | 2000-2025 | 13,3 (2000) … 11,8 (2012) → 9,7 (2013, b) → 8,8 (2014, b) … 7,8 (2021, bd), 7,6 (2022, d), 7,6 (2023, d), 7,9 (2024, bd), 7,2 (2025, d) ; b 2003 |
| BDM 010594746 | 2006-2025 | « Taux de sorties précoces du système scolaire des 18-24 ans », FR-D976 ; 11,2 (2006) … 10,8 (2012), 10,1 (2013), 8,6 (2014) … 7,9 (2024) ; **2021-2024 provisoires (OBS_STATUS P)** ; 2025 vide ; MAJ 27/05/2026 |
| insee.fr 3281681 (NIR n° 8) | page | indicateur calculé par Eurostat sur l'enquête Emploi ; champ France métropolitaine et DOM hors Mayotte ; **série rétropolée par la DEPP pour 2003 à 2013** (extension aux DOM en 2014) ; ruptures 2003, 2013, 2021 ; 7,6 % en 2023 (provisoire) |
| Eurostat `edat_lfse_03` (25-34, CITE 3-8 ; 25-64, CITE 0-2) | 1993-2025 | 76,4 (2000) → 89,9 (2025) ; 37,8 (2000) → 15,3 (2025) ; b 2003, 2013, 2014, 2021, 2024 ; 27,6 (2012) → 25,0 (2013) → 23,3 (2014) |
| Eurostat `sdg_04_20` | 2000-2025 | 31,4 → 55,8 ; 47,0 en 2018 ; b 2003, 2013, 2014, 2021, 2024 |
| Eurostat `sdg_04_40` (READ, EF461, SCI) | 2000-2025 | lecture 15,2 … 26,9 (2022), 32,7 (2025), b 2009, 2018 ; maths 16,6 (2003) … 28,8, 35,7 ; sciences 21,2 (2006) … 23,8, 25,8 ; MAJ 08/10/2026 |
| Eurostat `sdg_04_60` (25-64) | 2000-2025 | 2,8 (2000) … 5,7 (2012) → 17,8 (2013, b) … 19,5 (2019), 13,0 (2020), 11,0 (2021, b), 15,5 (2025) ; b 2003, 2013, 2014, 2021, 2024 |
| Eurostat `trng_aes_100` (25-64) | 2007-2022 | FE_NFE 35,1 / 50,5 (b) / 51,3 / 50,8 (b) |
| Eurostat `trng_aes_175` (25-64) | 2007-2022 | NPT_W 10,0 / 13,8 (b) / 11,4 / 11,5 (b) ; NPT_NW 37,5 en 2022 |
| Eurostat `trng_lfs_17` (25-64) | 2022, 2024 | 36,3 ; 37,7 (b) ; note Eurostat `Info_note_TRNG_AL_20240423` : EFT **hors formation guidée en situation de travail**, données **biennales** depuis 2022 ; l'AES diffusé par Eurostat **inclut** cette formation |
| Monitor « Education and Training », boîte à outils « adult learning » | page | indicateur des cibles (47 % en 2025, 60 % en 2030) : AES « excluding guided on-the-job training » ; `trng_aes_100` l'inclut et n'est pas présenté comme mesure de la cible |
| Eurostat `edat_aes_l21` (25-64) | 2007-2022 | aucune langue 41,2 / 41,2 (b) / 39,9 / 22,6 (b) |
| Eurostat `edat_aes_l31` (25-64) | 2007-2022 | « Très bon » 8,7 / 18,7 (b) / 19,9 / 24,5 (b) ; Bon + Élémentaire + Très bon = 99,9 à 100 % en 2011, 2016, 2022 ; 2007 : 22,5 % « sans réponse » |
| Eurostat `ilc_caindformal` (< 3 ans) et `tepsr_sp210` | 2005-2025 | sommes égales au total publié (32,0 ; 39,6 ; 59,3 ; 59,7) ; b 2020, 2022 ; sauts sans drapeau 2007-2008 (27,3 → 39,6) et 2015-2016 (41,7 → 48,9) |
| Eurostat `sdg_04_31`, `educ_uoe_enra10` | 2013-2024 ; 1998-2024 | 100 % sauf 99,3 (2014, b) et 99,6 (2014, b) ; p 2018, 2023, 2024 |
| Eurostat `isoc_sks_itspt` (PC_EMP) | 2004-2025 | 4,0 (2004, e) … 4,1 (2010, e) → 2,7 (2011, be) … 3,0 (2013, b), 3,2 (2014, b) … 4,5 (2021, bd), 4,9 (2025, d) ; e 2004-2012 ; b 2005, 2006 |
| Eurostat `sdg_09_30` | 2003-2024 | 1,24 → 1,72 ; d 2008, 2009 ; b 2010 |
| Eurostat `sdg_09_40` | 2004-2025 | APPL P_MHAB 129,2 → 158,7 (p) ; b 2014 ; p 2021-2025 ; INVT depuis 2011 |
| Eurostat `sdg_09_10` ; BDM 010594852 | 1996-2025 | BDM « Effort de recherche (en % du PIB) », FE : 2,09 (2000), 2,02 (2007), 2,28 (2014, 2020), 2,18 (2024, E) ; Eurostat b 2000, 2004, 2010 |
| Eurostat `educ_uoe_fine06` (ED02-8, PC_GDP) | 2012-2023 | 5,46 → 5,26 (p) ; 5,66 en 2020 ; d 2013 ; p 2019, 2023 |
| Eurostat `sdg_04_70`, `educ_uoe_enra07` | 2021-2025 ; 2013-2024 | 61,96 / 59,67 / 65,74 ; espérance de scolarisation en années entières (16 puis 17) |
| BDM 010594831 à 834 | 2015-2025 | titres, zone FE ; base 30, 28, 28, 26, 31, 29, 31 ; avancées 27, 28, 29, 31, 31, 31, 35 ; « n'ayant pas utilisé internet au cours des trois derniers mois ou sans aucune compétence » 15 … 7 |
| BDM 010594810, 010594813 | 2011-2025 | PIRLS 95, 94, 94 (zone `FMGUADMART16_FHMAY21…`) ; TIMSS 58 (2015), 57 (2019), 36 (2023) (zone `FMGUADMART15_FHMAY19…`) |
| DEPP, NI 24.47 (TIMSS 2023 CM1) | PDF | score moyen 488 (2015), 485 (2019), 484 (2023), « stables » ; 15 % des élèves sous le seuil bas (400) en 2023 ; 3 % au seuil avancé |
| DEPP, page JDC 2024 (NI 25-57) | page | 76 % de lecteurs efficaces, 10 % fragiles, 13 % en difficulté, 6 % en situation d'illettrisme ; champ : 16-18 ans de nationalité française |
| BDM 010594830, 010594736, 010594737 | 2016, 2022 | ODD 4.i2, France métropolitaine : 51 / 51 % |
| Parlement européen, procédure 2021/0293(COD) | résumé | Décennie numérique : ≥ 80 % des 16-74 ans avec des compétences de base ; ≥ 20 millions de spécialistes des TIC dans l'Union en 2030 |
| ISU-UNESCO, fiche « dépenses publiques d'éducation en % du PIB » | PDF | repère du Cadre d'action Éducation 2030 : « au moins 4 à 6 % » du PIB |
| Extraits du robot (dépôt) | — | OCDE How's Life : 6_1/6_2/6_3 (473,85 ; 473,94 ; 487,23 en 2022), 6_1_DEP « Students with low skills in reading, mathematics and science » (16,7966 en 2022), 6_4 (257,223), 6_4_DEP « Adults with low numeracy skills » (22,6255), 6_5 (255,396), pas de 6_5_DEP pour la France ; 13_1 (89,4087 en 2024) ; 15_4 « Investment in R&D » **1,77 % du PIB en 2024** ; PNUD eys 16,0951, mys 11,7657 (2023) ; DEPP : bacheliers 80,7 % (2023, définitif), 80,1 % (2025, provisoire), série « hors DROM » 1970-2009 ; réussite au bac 91,6 % (2025) ; objectifs européens `elet` 7,7 (2024), `dipl_sup` 53,4 (2024), ICILS 42,7 (2023) ; ITDD : 6e 26,9 et 32,2 (2024), JDC 13,32 (2024) |

**Non lus** : PDF des définitions de la base OCDE du bien-être (autorisation non accordée à temps, non relancé) ; note pays PIAAC 2023 de l'OCDE (pages sans chiffres, PDF refusé par robots.txt) ; API Melodi (fermée à l'outil, non tentée).

## 3. Contrôles transversaux (10 h 30)

- Croisement mécanique (`tmp/m06-education/croise.py`) des séries principales, composantes et variantes des 38 fiches avec toutes les fiches des autres dimensions : **aucun `serie_id` ni `ligne_id` commun** ; aucun identifiant en double.
- Lignes renvoyées (`tmp/m06-education/renvois.py`) : vers `education`, `travail` (96) et `niveau_de_vie` (24) sont reprises ; **`logement_cadre_vie` (93 lignes, groupe `education_urbanisation`) ne l'est pas** (fusion postérieure). Depuis `education`, lignes non reprises par la destination : `egalites` 75, `travail` 56, `logement_cadre_vie` 28, `liens_bien_etre` 4.
- Double affectation : `estat-052758` et `estat-052759` (IPCH, loyers) sont écartées en bloc par `education` (règle 1010) et utilisées par `logement_cadre_vie/hausse_loyers` (règles 190 et 200, `longlist = education`) ; le vérificateur ne le signale pas (il ne contrôle que les lignes utilisées en fiche ou en variante).
- Lignes « éducation » des autres long-lists (`tmp/m06-education/autres_longlists.py`) : toutes affectées, aucune orpheline hors celles ci-dessus.
- Variantes sans `ligne_id` : 11, toutes avec `catalogue` ou `preuve` ; `serie_id` uniques.
- Recherche D36 : `edat_lfs_9919` (formation par le travail des 20-34 ans, 2021-2025) est au catalogue des jeux Eurostat, contrairement à ce que dit la ligne 44 de la liste de maintenance.

## 4. Rédaction (11 h 00)

Rapport `docs/validation/audit_education.md` (même plan que `audit_travail.md`) : 38 fiches auditées, 26 `conforme`, 12 `a_corriger`, 0 `non_verifiable` ; avis global `corrections_necessaires`. Dépôt du rapport dans le Projet (`claude/cr/M06_education_audit.md`), commit, push, pull request.
