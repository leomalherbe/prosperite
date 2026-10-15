# Audit croisé M06 — dimension `travail`

Agent auditeur M06 (session neuve, n'ayant pas participé à M05 `travail`), 15 octobre 2026. Branche `m06-travail`, créée depuis `origin/main` au commit `792f1a5` (fiches fusionnées par la PR #15, puis D34-D36, méthode v1.2 et corrections `egalites`/`securite`). Matériau audité : les 37 fiches `indicateurs/travail/*.yaml`, `docs/validation/validation_travail.csv`, `preselection_travail.csv`, `preselection_travail_lignes.csv`, `regles_preselection_travail.csv`, le journal et le compte rendu M05, `docs/cr/maintenance_catalogues_travail.md` (TRA-1 à TRA-10), la long-list `catalogues/longlist_travail.csv.gz` et les autres long-lists, les catalogues INSEE et Eurostat, les sorties du robot M04. **Aucune fiche, aucune règle, aucun tableau, aucun script ni aucun catalogue n'a été modifié** : ce rapport propose, l'agent correcteur (ou la session mère) corrige. Déroulé : `docs/cr/M06_travail_journal.md`.

Contrôle préalable : `python -m pytest -q` → 398 réussis ; `python scripts/verifier_fiches.py --dimension travail` (sans `--tableau`) → 0 erreur, **3 avertissements** : les deux fiches DREES hors catalogue (attendus) et un nouveau, `surqualification` (ligne `estat-054299` devenue série principale de `egalites/ecart_surqualification_origine` par la PR #19, après la fusion de `travail`) ; 37 fiches, 28 familles, 24 `retenir`, 8 `retenir_variante`, 5 `ecarter`, 3 déclaratives, 0 composite, 3 « à vérifier », 2 hors long-list, 4 incontournables, 1 675 variantes.

Nature des constats : **F** = erreur factuelle (source et valeur attendue citées) ; **A** = alignement sur une décision ou une fusion postérieure à M05 (D34, PR #16, PR #19), sans faute de M05 ; **J** = désaccord de jugement (à trancher par la session mère ou Léo) ; **O** = oubli ; **I** = incohérence entre dimensions.

## 0. Avis global : `corrections_necessaires`

La structure de M05 est solide. Les 28 familles couvrent tout le contenu de `dimensions.yaml` (emploi, chômage, longue durée, sous-emploi, halo, NEET ; contrats courts, temps partiel subi, bas salaires, surqualification, passages au chômage ; accidents, expositions, longues durées, horaires atypiques ; satisfaction). Les décisions D27 (durées et horaires dans `travail`, temps libre et conciliation hors v1), A15 (sécurité de l'emploi ici) et D36 (salaire réel, bas salaires et pauvreté en emploi ici) sont appliquées. Les deux incontournables du crosswalk (taux d'emploi, longues durées) ont des fiches `retenir`. Les cinq écarts sont motivés selon la méthode. **Toutes les valeurs Eurostat, BDM, OCDE, Ameli et DREES citées dans les motifs et les notes ont été retrouvées à la source** (22 jeux Eurostat, 9 séries BDM, 4 extraits du robot), à une année près dans un motif.

Quatre groupes de problèmes doivent être réglés avant la validation de Léo :

1. **Onze fiches, dont neuf sur l'enquête Emploi, ont leur série principale dans Melodi, qu'aucun agent n'a pu lire** (robots.txt). Pour trois d'entre elles (`neet`, `halo_chomage`, `taux_sous_emploi`), le libellé de la mesure (« Part du sexe et de l'âge dans… ») laisse ouverte une lecture en *répartition* plutôt qu'en *taux*, et toutes les lignes NEET de Melodi sont codées `EMPSTA=3` « Inactif ». M05 l'a signalé (TRA-3) mais a retenu ces séries en principales. L'audit fournit les valeurs de contrôle BDM (§3) ; le contrôle doit être fait **avant le gel 2**, sinon les séries BDM, dont le libellé est sans ambiguïté, doivent passer en principales. Pour le halo, la série BDM est de toute façon plus longue (J1).
2. **Erreurs factuelles** (F) : la série principale du taux d'emploi des 20-64 ans (`sdg_08_30`, 2009-2025) a une jumelle de même valeur couvrant 2003-2025 (`lfsi_emp_a`), alors que la fiche dit que celle-ci « couvre 2003-2008 » ; la définition et l'unité des contrats très courts (contrat de trois mois au plus, en % des **salariés**) ; le seuil des longues heures (49 heures ou plus) donné pour « non trouvé » ; les dénominateurs de l'emploi temporaire subi et du temps partiel subi ; une année erronée et des drapeaux manquants dans quatre fiches.
3. **Rattachements non soldés** (I, A) : `niveau_de_vie` renvoie **349 lignes** vers `travail` (séries longues de salaires, SMIC, pauvreté en emploi par handicap) que la présélection `travail` n'a pas reprises ; une variante de `surqualification` est devenue série principale d'`egalites` ; les lignes de santé au travail (`hsw_exp2`, `hsw_pb*`) et le NEET de l'ODD (`sdg_08_20`) sont dans les long-lists `sante` et `education` sans signalement.
4. **Oublis** (O) : l'exposition aux risques pour la santé **physique** et les problèmes de santé liés au travail (cadre Qualité de vie), alors que le pendant **mental** est retenu avec la même qualité de données ; les décès au travail de l'Assurance maladie (jeu `deces-par-secteur-d-activite-naf-1-et-naf-5`, déjà repéré par M04), qui répondent à la question laissée ouverte par TRA-7.

Chiffres : **37 fiches auditées sur 37** — **23 `conforme`, 12 `a_corriger`** (7 F, 4 A, 1 J), **2 `non_verifiable`** (`neet`, `taux_sous_emploi` : valeurs Melodi illisibles et unité ambiguë). 4 oublis, 7 points de cohérence inter-dimensions, 7 désaccords de jugement. Liste ordonnée des corrections : §12.

## 1. Échantillon

| Règle (fiche M06 et consigne de la session mère) | Fiches |
|---|---|
| `recommandation: ecarter` (5) | `demandeurs_emploi`, `duree_hebdomadaire_travail`, `maladies_professionnelles`, `taux_activite`, `part_temps_partiel` |
| `incontournable: oui` (4) | `taux_emploi`, `taux_emploi_20_64`, `taux_emploi_eqtp`, `longues_durees_travail` |
| Éligibilité `a_verifier` (3) | `bas_salaires`, `bas_salaires_ses`, `exposition_risques_sante_mentale` |
| Points d'attention de la session mère et priorités demandées par M05 (compte rendu §7.5) (9) | `taux_chomage` ; formules : `taux_chomage_longue_duree`, `part_emploi_temporaire` ; mesures `PT_*` (TRA-3) : `neet`, `halo_chomage`, `taux_sous_emploi` ; accidents : `accidents_travail`, `accidents_travail_mortels` ; déclaratif : `satisfaction_travail` |
| Autres `raccordement: a_etudier` (5) | `emploi_temporaire_subi`, `temps_partiel_subi`, `transitions_temporaire_permanent`, `travail_dimanche`, `travail_nuit` |
| Hors long-list (2) | `preoccupation_chomage`, `risque_chomage_percu` |
| 20 % des 28 « autres » fiches (ni `ecarter` ni incontournables), soit 5,6 arrondi à 6, tirées parmi les 9 non retenues d'office | `horaires_atypiques`, `menages_tres_faible_intensite_travail`, `passages_emploi_chomage`, `salaire_net_moyen_reel`, `sous_utilisation_main_oeuvre`, `surqualification` |
| Les 3 restantes, vérifiées aussi à la source | `contrats_tres_courts`, `pauvrete_en_emploi`, `sorties_chomage_emploi` |

Tirage : `random.Random(20261014).sample(pool, 6)` en Python 3, `pool` = liste triée des 9 fiches non retenues d'office ; **graine 20261014**, la même que pour les audits précédents. **28 fiches d'office + 6 tirées + 3 restantes = 37.**

## 2. Fiches auditées

Sources lues par WebFetch le 15/10/2026 (détail en annexe) ; extraits du robot lus dans le dépôt.

| Fiche | Motif d'inclusion | Source consultée | Verdict | Nature | Constat, correction attendue (détail aux §3 à §9) |
|---|---|---|---|---|---|
| `demandeurs_emploi` | ecarter | BDM 010597456 | conforme | — | Catégorie A, France hors Mayotte, CVS-CJO, 1996-T1 à 2026-T2 (3 325 600 puis 3 323 000) ; « dominée » au sens de la méthode §4 (enquête plutôt que série enregistrée). |
| `duree_hebdomadaire_travail` | ecarter | long-list `estat-026047` ; API `lfsa_ewhuis` **refusée (HTTP 429)** | conforme (réserve) | (J6) | Sens ambigu fondé ; valeurs 37,2 et 36,8 non relues. |
| `maladies_professionnelles` | ecarter | extrait Ameli du robot ; export du catalogue data.ameli.fr | conforme | — | 50 598 en 2024, 20 années. Un taux est calculable dès maintenant (50 598 / 20 799 600 salariés × 1 000 = 2,43 ‰), mais le sens reste ambigu. |
| `taux_activite` | ecarter | long-list ; page INSEE 8977323 | conforme | — | Sens ambigu fondé. |
| `part_temps_partiel` | ecarter | long-list ; page INSEE 8977323 | conforme | — | Sens ambigu fondé ; la part subie est portée par la famille `sous_emploi`. |
| `taux_emploi` | incontournable | page INSEE 8977323 ; BDM 010596081 (IRN 1) | conforme (réserve) | — | IRN 1 : France hors Mayotte, 1975-2024, 68,8 % en 2024, 2025 vide (comme le dit la note) ; rétropolations 2003, 2011, 2013, 2021, 2024 confirmées ; valeurs Melodi non lues (§3). |
| `taux_emploi_20_64` | incontournable | API `sdg_08_30` et `lfsi_emp_a` | **a_corriger** | F | `lfsi_emp_a` (20-64 ans) couvre **2003-2025** avec des valeurs identiques à `sdg_08_30` de 2009 à 2025 : elle doit être la série principale (§4). |
| `taux_emploi_eqtp` | incontournable | BDM 011818669 | conforme | — | France entière, CVS, 2003-T1 à 2026-T2 ; 64,6 % en moyenne 2025. |
| `longues_durees_travail` | incontournable | API `lfsa_qoe_3a2` ; métadonnées `lfsa_qoe_esms` | **a_corriger** | F | Valeurs et drapeaux exacts ; le seuil est connu : « 49 heures ou plus par semaine » ; mentionner aussi la baisse de 2021 (11,7 → 10,0, `bd`) (§7, F3). |
| `bas_salaires` | a_verifier | extrait OCDE du robot ; API OCDE **non lue** (autorisation) | conforme | — | 7 périodes (2006, 2010, 2014, 2018, 2022-2024), 5,83 % en 2024 ; écart moyen de 3 ans ≥ 1,5 (D28) ; l'`url_api` a été construite par M05 (absente de la long-list), à vérifier ou à remplacer par « non trouvé ». |
| `bas_salaires_ses` | a_verifier | API `earn_ses_pub1s` | conforme | — | 7,13 / 6,08 / 8,81 / 8,61 / 9,68 %, sans drapeau. |
| `exposition_risques_sante_mentale` | a_verifier | API `hsw_exp1` | conforme | (J2) | 49,0 `d` ; 60,8 `d` ; 53,5 `b`. Le pendant physique (`hsw_exp2`) manque (O1). |
| `taux_chomage` | point d'attention | page INSEE 8977323 ; long-list | conforme (réserve) | — | Mesure `UNEMPRATE` sans ambiguïté ; valeurs Melodi non lues (§3). |
| `taux_chomage_longue_duree` | formule | BDM 011818581 ; extrait OCDE 2_3 ; API `une_ltu_a` **refusée (429)** | **a_corriger** | A | Recoupement D34 (≥ 3 valeurs officielles) à faire avant `retenir` : moyennes BDM 2,3 (2003), 3,2 (2015), 1,8 (2024) ; OCDE 1,76 (2025). Formule à normaliser : `A / B * 100`. |
| `part_emploi_temporaire` | formule | long-list ; catalogue BDM | **a_corriger** | A | Recoupement D34 à faire ; formule `A + B` ; unité des mesures `PT_EMPFORM_*` non lue (§3). |
| `neet` | TRA-3 | long-list ; BDM 011818639 | **non_verifiable** | — | Valeurs Melodi illisibles ; libellé ambigu **et** lignes NEET toutes codées `EMPSTA=3` « Inactif » (§3). Valeur de contrôle : BDM 12,95 % en moyenne 2025. |
| `halo_chomage` | TRA-3, a_etudier | long-list ; BDM 011818623 | **a_corriger** | J | La série BDM (15-64 ans, « part dans la population », 2003-T1 à 2026-T2) est plus longue que la série Melodi (15 ans ou plus, 2014-2025) et sans ambiguïté d'unité : elle devrait être principale (§3, J1). |
| `taux_sous_emploi` | TRA-3 | long-list ; BDM 011818670 | **non_verifiable** | — | Valeurs Melodi illisibles ; contrôle BDM : 4,4 % en moyenne 2025, 15,6 % au 2020-T2. |
| `accidents_travail` | point d'attention | extrait Ameli du robot ; API `hsw_n2_01` ; data.ameli.fr **non lu** (autorisation) | conforme | — | 26,4 en 2024 = 549 614 / 20 799 600 × 1 000 ; 2020 absent ; choix national justifié (§5). |
| `accidents_travail_mortels` | point d'attention | API `hsw_n2_02`, `sdg_08_60` | **a_corriger** | F | Motif « série 2008-2025 » : la série s'arrête en 2024 ; hausse de 2018 à 2019 (2,74 → 3,54, +29 %) sans drapeau, cause non documentée ; voir O2. |
| `satisfaction_travail` | déclaratif | catalogues Melodi ; extrait OCDE | conforme (réserve) | — | `declaratif: oui`, R4 ; 12 années sur 2010-2023 (`FRANCE-FM`) ; OCDE 7,08 en 2023 ; préciser « personnes en emploi » dans la définition (mineur). |
| `emploi_temporaire_subi` | a_etudier | API `lfsa_eetpgar` | **a_corriger** | F | Unité « pourcentage des salariés » : c'est une part de **l'ensemble** des salariés, pas des salariés temporaires (la définition prête à confusion) ; ruptures de 2005, 2006 et 2024 absentes de `qualite` ; la baisse se poursuit après 2021 (5,8 → 3,6). |
| `temps_partiel_subi` | a_etudier | API `lfsa_eppgai` | **a_corriger** | F | Libellé et motif disent « salariés » : le dénominateur est l'ensemble des personnes à temps partiel ; ruptures de 2005 et 2006 absentes ; saut non signalé de 2013 (33,5 → 38,7). |
| `transitions_temporaire_permanent` | a_etudier | API `ilc_lvhl36` | conforme | — | 12,0 → 19,3 (2020, `b`), `b` 2023, 32,5 (2024). |
| `travail_dimanche` | a_etudier | API `lfsa_ewpsun` | conforme | — | 9,7 → 12,9 (2003, `b`) ; 14,6 (2025) ; 2022 et 2024 absents. |
| `travail_nuit` | a_etudier | API `lfsa_ewpnig` | conforme | — | 7,1 (2012) → 3,7 (2013) sans drapeau ; 3,9 (2025). |
| `preoccupation_chomage` | hors long-list | distributions DREES du robot ; dictionnaires 2025 | **a_corriger** | A | Valeurs exactes (90,67 ; 88,68 ; 63,49), libellé exact ; série calculée par le projet : recoupement D34 ou drapeau `non_recoupe` (§6). |
| `risque_chomage_percu` | hors long-list | couverture et dictionnaires DREES | conforme | — | SDRICHOM : 16 années 2010-2025, modalités Oui / Non / NSP ; `declaratif: oui` justifié. |
| `horaires_atypiques` | tirage | API `lfsa_esegatyp` | conforme | — | 37,9 → 34,2 ; 13 valeurs ; pas de dimension sexe. |
| `menages_tres_faible_intensite_travail` | tirage | API `ilc_lvhl11` | conforme | (J4) | 10,3 → 9,0 ; `b` 2020 et 2022. |
| `passages_emploi_chomage` | tirage | API `lfsi_long_a` | conforme | — | 3,0 → 2,9 ; 2021 absent ; drapeaux conformes à `qualite`. |
| `salaire_net_moyen_reel` | tirage | BDM 010752333 ; table des zones BDM | conforme (réserve) | (J5) | La série BDM jumelle couvre 1996-2024, zone `FM99_FR00` (« France métropolitaine jusqu'en 1999 ») ; série Melodi non lue. |
| `sous_utilisation_main_oeuvre` | tirage | BDM 011818634 ; API `lfsi_sla_a` | conforme | (J4) | 2003-T1 à 2026-T2, FE ; `lfsi_sla_a` : 20,0 (2014) → 15,0 (2025), `d` depuis 2021. |
| `surqualification` | tirage | API `lfsa_eoqgan` | **a_corriger** | A | Valeurs exactes (18,0 → 20,4) ; la variante `estat-054299` est devenue principale d'`egalites` : la renvoyer (`autre_dimension:egalites`) (I1). |
| `contrats_tres_courts` | contrôle | API `lfsa_qoe_4ax1r2` ; métadonnées `lfsa_qoe_esms` ; note Eurostat du 9/2/2018 | **a_corriger** | F | Emploi précaire = contrat de **trois mois au plus**, en **% des salariés** (et non « % de l'emploi total ») ; valeurs exactes (4,8 → 3,9). |
| `pauvrete_en_emploi` | contrôle | API `ilc_iw01` | conforme | — | 5,4 → 8,7 ; `b` 2008, 2020, 2022 ; « activité la plus fréquente » à préciser (mineur). |
| `sorties_chomage_emploi` | contrôle | API `lfsi_long_a` (UNE_EMP) | **a_corriger** | F | Drapeaux désormais lus : `b` 2014, `d` 2022-2025, `bd` 2024, 2021 absent ; saut 33,4 (2020) → 42,3 (2022) au changement de définition : `raccordement: a_etudier`. |

Contrôles transversaux : `type` (tous `resultat`) et `declaratif` (`oui` pour la satisfaction et les deux questions DREES ; `non` pour les faits déclarés : expositions, contrats subis) sont conformes à la méthode §4. Les `incontournable: oui` portent sur le seul concept « taux d'emploi » (3 fiches de la famille) et sur les longues durées ; le taux de chômage reste `non` à juste titre (Eurostat seul au §5 du crosswalk ; l'OCDE n'a que le chômage de longue durée).

## 3. Enquête Emploi : séries longues de l'INSEE (Melodi) contre EFT d'Eurostat

**Le choix de M05 est fondé.** La page INSEE des séries longues (8977323, Insee Résultats du 2 juillet 2026) confirme les rétropolations de 2003 (enquête en continu), 2011 (âge et stagiaires), 2013 (questionnaire), 2021 (rénovation) et 2024 (France entière y compris Mayotte), « toujours basées sur des hypothèses et des choix ». Côté Eurostat, la plupart des séries EFT portent `d` depuis 2021 (vérifié sur `lfsa_qoe_3a2`, `sdg_08_30`, `lfsi_emp_a`, `lfsa_eoqgan`, `lfsa_eetpgar`, `lfsi_long_a`, `lfsi_sla_a`), mais pas toutes : `lfsa_eppgai` n'a que des `b`, et `lfsa_ewpnig` chute en 2013 sans drapeau.

**Mais aucune valeur des séries Melodi n'a été lue**, ni par M05 ni par l'audit (API refusée par robots.txt ; fichiers xlsx d'insee.fr refusés ; catalogue et outils interactifs en JavaScript). Onze fiches sont concernées : neuf sur l'enquête Emploi (`taux_emploi`, `taux_chomage`, `taux_activite`, `part_temps_partiel`, `taux_sous_emploi`, `neet`, `halo_chomage`, et les composantes de `part_emploi_temporaire` et de `taux_chomage_longue_duree`), plus `satisfaction_travail` (SRCV) et `salaire_net_moyen_reel` (DERA). Pour les mesures `EMPRATE`, `UNEMPRATE`, `ACTRATE`, `UNEMP`, `ACTPOP`, le libellé ne laisse pas de doute. Pour les mesures `PT_*`, deux formes coexistent :

- « Part du type de contrat dans l'emploi par sexe et âge » (`PT_EMPFORM_*`), « Part du temps de travail dans l'emploi… » (`PT_WKTIME_*`), « Part du sous-emploi, du sexe et de l'âge dans l'emploi total » (`PT_UNDEREMP_*`) : une lecture en taux est naturelle ;
- « Part du sexe et de l'âge dans le nombre de jeunes NEET » (`PT_SEX_AGE_IN_NEET`) et « … dans les personnes dans le halo » (`PT_SEX_AGE_IN_HALO`) : la lecture naturelle est une **répartition** (part d'un groupe d'âge et de sexe parmi les NEET), qui vaudrait 100 % pour le total. M05 s'appuie sur les tableaux t309 et t310 de l'INSEE pour une lecture en taux, ce qui est plausible mais non vérifié.

**Constat supplémentaire de l'audit** : les 24 lignes NEET de Melodi (nombres et parts) sont toutes codées `EMPSTA=3`, libellé « Inactif » ; il n'existe aucune ligne `EMPSTA=2` (chômeur). Si ce code n'est pas un artefact, la série principale de `neet` ne compterait que les NEET inactifs, alors que la définition (et la cible de 9 %) inclut les chômeurs.

**Valeurs de contrôle pour TRA-3** (BDM, lues le 15/10/2026, moyennes des quatre trimestres de 2025) : NEET 15-29 ans 011818639 = 12,95 % (12,9 ; 13,0 ; 12,8 ; 13,1) ; halo 15-64 ans en part de la population 011818623 = 4,475 % (4,4 ; 4,5 ; 4,5 ; 4,5) ; sous-emploi 011818670 = 4,4 % (4,3 ; 4,5 ; 4,4 ; 4,4) ; taux d'emploi IRN 1 010596081 = 68,8 % en 2024 (France hors Mayotte) ; chômage de longue durée 011818581 = 1,775 % en 2024.

**Correction attendue** : faire lire par le robot, avant le gel 2, les séries `DD_EEC_SERIES` des fiches concernées (une collecte ciblée suffit) et comparer aux valeurs ci-dessus ; si une série `PT_*` vaut 100 % pour le total ou s'écarte nettement de la BDM, passer la série BDM correspondante en principale. En attendant, garder `unite_a_confirmer` et ajouter pour `neet` un drapeau `champ_empsta_a_verifier`.

## 4. Taux d'emploi des 20-64 ans (F)

`lfsi_emp_a` (`indic_em=EMP_LFS`, 20-64 ans) donne 70,0 (2003), 69,8 (2004), 69,7 (2005, 2006), 70,2 (2007), 70,7 (2008), puis **exactement** les valeurs de `sdg_08_30` de 2009 à 2025 (69,8 … 75,4), avec `d` de 2021 à 2025. C'est donc la même série, sur **23 points au lieu de 17**. La note de raccordement (« `lfsi_emp_a` couvre 2003-2008 ») est fausse, et un raccordement est inutile. **Correction** : série principale = modalité 20-64 ans de la ligne `estat-025131` (`lfsi_emp_a`, 2003-2025), `url_api` avec `age=Y20-64` ; `sdg_08_30` en variante (doublon technique, indicateur de la cible de 78 %) ; `raccordement: non`, `premiere_annee: 2003`, `nb_points_depuis_2000: 23` ; motif et note réécrits. La fiche garde la cible de 78 % comme borne officielle.

## 5. Accidents du travail et maladies professionnelles

- **Niveau de source** : l'Assurance maladie publie par l'API Opendatasoft de data.ameli.fr ; la long-list et la fiche portent `source_niveau: 1`, ce qui est exact (pas niveau 2). Le portail a refusé l'outil de lecture (autorisation non accordée à temps) : valeurs prises dans l'extrait du robot.
- **`accidents_travail`** : 26,4 accidents pour 1 000 salariés en 2024, cohérent avec 549 614 accidents pour 20,80 millions de salariés (26,42) ; 19 périodes (2005-2019, 2021-2024). La série européenne non mortelle (`hsw_n2_01`) passe de 3 443,59 (2008) à 2 303,37 (2009), soit −33 % en un an, avec des ruptures en 2014, 2017, 2020 et 2022 : le choix de la source nationale est justifié.
- **`accidents_travail_mortels`** : valeurs exactes (1,56 en 2008 ; 3,61 en 2024 ; `sdg_08_60` identique depuis 2010). Le motif dit « 2008-2025 » : lire **2008-2024**. La hausse de 2018 à 2019 (2,74 → 3,54) n'a pas de drapeau : écrire « cause non documentée » plutôt que « les ruptures expliquent sans doute une partie de la hausse ».
- **Source nationale des décès (O2)** : l'export du catalogue data.ameli.fr du robot M04 (`docs/sources/verif_acces/extraits/cnam_ameli__ods_catalogue_export.txt`, ligne 39) et `docs/sources/autres_sources.md` (ligne 374) citent le jeu **`deces-par-secteur-d-activite-naf-1-et-naf-5`** (« décès au travail par secteur d'activité »). TRA-7 (« vérifier si le jeu publie le nombre d'accidents mortels ») a donc déjà sa réponse : le jeu existe, il reste à le cataloguer et à calculer un taux pour 100 000 salariés (même dénominateur que l'indice de fréquence). Il pourrait servir de variante nationale, voire de principale, à `accidents_travail_mortels`. Le même catalogue contient les maladies professionnelles psychiques (ligne 46) et les troubles musculosquelettiques (lignes 29 et 36), utiles pour documenter les risques psychosociaux et physiques.

## 6. Satisfaction et insécurité de l'emploi ressentie (déclaratifs)

- **`satisfaction_travail`** : R4 respecté, `declaratif: oui`. Le catalogue Melodi confirme 12 années sur 2010-2023 pour `TRAVSATISF` en France métropolitaine. Il existe aussi une série France hors Mayotte limitée à 2023 (catalogue des non-candidates), à suivre comme successeur possible. L'OCDE (7,08 en 2023) et EU-SILC (`ilc_pw01b`, 2013 et 2018 seulement) sont bien des variantes plus pauvres. La définition devrait dire « personnes **en emploi** de 16 ans ou plus », puisque la question ne porte que sur l'emploi principal.
- **`preoccupation_chomage`** : recalcul exact sur les distributions du robot (modalités 1 + 2, NSP au dénominateur) : 90,67 % (2000), 88,68 % (2010), 63,49 % (2025) ; 25 années, pas d'enquête en 2003. Libellé exact : « Êtes-vous personnellement préoccupé(e) par… le chômage ? ». C'est une série calculée par le projet : D34 demande un recoupement avec au moins trois valeurs publiées par la DREES (synthèses du baromètre), ou à défaut un drapeau `non_recoupe` et `retenir_variante` jusqu'au recoupement. C'est un alignement sur D34, pas une faute de M05.
- **`risque_chomage_percu`** : conforme ; la fiche signale à juste titre qu'elle pourrait devenir principale une fois calculée.

## 7. Erreurs factuelles (détail)

1. **F1 — `taux_emploi_20_64`** : §4.
2. **F2 — `contrats_tres_courts`** : les métadonnées Eurostat du jeu de qualité de l'emploi (`lfsa_qoe_esms`) définissent l'emploi précaire comme le « pourcentage des **salariés** ayant un contrat de courte durée de **3 mois au plus** » ; la note Eurostat du 9 février 2018 donne 4,8 % pour la France en 2016, valeur de l'API pour 2016. **Attendu** : `definition` (« Part des salariés de 15 ans ou plus dont le contrat de travail ne dépasse pas trois mois »), `unite: '% des salariés'`, suppression de `definition_a_verifier`, note de pertinence sans « non trouvé » ; la règle 190 de la présélection disait déjà « trois mois au plus ».
3. **F3 — `longues_durees_travail`** : seuil = « 49 heures ou plus par semaine » (`lfsa_qoe_esms`), à écrire dans `definition` et `note_pertinence` ; supprimer `seuil_horaire_a_verifier` ; compléter le raccordement avec la baisse de 2021 (11,7 % en 2020, 10,0 % en 2021, `bd`), du même ordre que le saut de 2003. TRA-9 est soldé sur ce point et sur F2.
4. **F4 — `emploi_temporaire_subi`** : unité `PC_SAL` = « pourcentage des salariés » (ensemble) ; écrire « Part, parmi l'ensemble des salariés de 15 ans ou plus, de ceux qui occupent un emploi temporaire faute d'avoir trouvé un emploi permanent ». Le cadre Qualité de vie rapporte aux seuls salariés temporaires : c'est une autre statistique, à signaler. Ajouter `rupture_2005`, `rupture_2006`, `rupture_2024` ; le motif « divisé par deux après la rupture de 2021 » mêle rupture et tendance (5,8 % en 2021, 3,6 % en 2025).
5. **F5 — `temps_partiel_subi`** : `lfsa_eppgai` rapporte à **toutes les personnes à temps partiel** (pas de dimension de statut) ; corriger le libellé « (part des salariés à temps partiel) » et le motif « rapporté aux seuls salariés à temps partiel ». Ajouter `rupture_2005`, `rupture_2006` et signaler le saut non marqué de 2013 (33,5 → 38,7), contemporain du nouveau questionnaire.
6. **F6 — `accidents_travail_mortels`** : motif « 2008-2025 » → « 2008-2024 » ; cause des sauts non documentée (§5).
7. **F7 — `sorties_chomage_emploi`** : remplacer `drapeaux_non_lus` et `pas_de_valeur_2021_a_verifier` par `pas_de_valeur_2021`, `rupture_2014`, `rupture_2024`, `definition_differente_2022_2025` ; `raccordement: a_etudier : saut de 33,4 % (2020) à 42,3 % (2022) au changement de définition`.

## 8. Alignements (A)

1. **D34, séries calculées** : `taux_chomage_longue_duree`, `part_emploi_temporaire` et `preoccupation_chomage` sont `retenir` sans recoupement. Attendu : recoupement avec ≥ 3 valeurs officielles (pour le chômage de longue durée : moyennes annuelles BDM 011818581, 2,3 % en 2003, 3,2 % en 2015, 1,8 % en 2024 ; OCDE 2_3, 1,76 % en 2025 ; pour les CDD et l'intérim : publication INSEE de la part des emplois à durée limitée ; pour la DREES : synthèses du baromètre), formules normalisées (`A / B * 100`, `A + B`), points non recoupés signalés dans `qualite`.
2. **R1 après la PR #19** : `estat-054299` (`lfsa_eoqgac`, surqualification par pays de naissance) est variante de `surqualification` et principale d'`egalites/ecart_surqualification_origine`. Attendu : ajouter la ligne à la règle 10 (`lignes_reprises_egalites`) ; l'avertissement du vérificateur disparaîtra.
3. **D36, frontière rémunération** : voir I2 (349 lignes de `niveau_de_vie`).

## 9. Désaccords de jugement

- **J1. Halo autour du chômage : BDM en principale.** L'ordre de la méthode (§4 : niveau 1, INSEE, puis « série la plus longue ») désigne la série BDM 011818623 (15-64 ans, part dans la population, 2003-2026, 24 années) plutôt que Melodi (15 ans ou plus, 2014-2025, 12 points). D35 ne s'y oppose pas : il n'existe pas de série annuelle **de même définition** (l'âge diffère). La BDM lève en outre l'ambiguïté d'unité (§3) et rend inutile le raccordement 2003-2013. Même classe d'âge que `sous_utilisation_main_oeuvre`.
- **J2. Risques psychosociaux : trois points non comparables.** `exposition_risques_sante_mentale` est `retenir` avec 49,0 % (`d`), 60,8 % (`d`), 53,5 % (`b`) : D17 l'admet, mais la trajectoire n'a pas de sens. M05 pose la question à Léo ; l'audit propose `raccordement: non : vagues non comparables` et, pour le socle, une lecture en niveau 2020 seulement. Même traitement pour le pendant physique s'il est ajouté (O1).
- **J3. Accidents mortels** : choisir entre la série européenne (tous travailleurs, ruptures) et la série nationale de l'Assurance maladie (régime général) une fois celle-ci cataloguée (O2).
- **J4. Familles imbriquées** : `sous_utilisation_main_oeuvre` = chômage + halo + sous-emploi (trois familles `retenir`) ; `menages_tres_faible_intensite_travail` est une composante de l'AROPE de `niveau_de_vie`. Comme pour `securite`, le signaler à Léo pour le socle (ensemble **ou** composantes) et au contrôle de redondance.
- **J5. Salaire réel, champ** : la série BDM jumelle (010752333) est en France métropolitaine jusqu'en 1999 puis en France y compris DOM (`FM99_FR00`). Vérifier sur la série Melodi au premier passage du robot et, si c'est le même champ, ajouter un drapeau `champ_metropole_avant_2000` (sans effet sur 2000-2024).
- **J6. Durée hebdomadaire** : le crosswalk donne le sens `bas` (cadre Qualité de vie) ; M05 la juge ambiguë. L'audit suit M05 (le surtravail et le sous-emploi sont mesurés à part), mais le motif devrait citer le choix contraire du cadre Eurostat.
- **J7. Préoccupation pour le chômage** : la fiche la rapproche d'une « opinion sur la société » (D32). Par D32, une opinion sur la société forme sa propre famille ; ici elle est principale de la famille `insecurite_emploi_percue` avec une question personnelle (SDRICHOM) en variante. Si la session mère la lit comme opinion sur la société, deux familles distinctes seraient plus justes.

## 10. Complétude

**Long-list** : les 6 520 lignes et les 5 lignes importées de `niveau_de_vie` sont toutes affectées (vérificateur). Les 26 groupes écartés en bloc (4 161 lignes) ont des motifs recevables, relus groupe par groupe (structures, effectifs, comptes nationaux, statistiques d'entreprises, fiscalité, territoires, conciliation des temps hors v1 par A4, séries OCDE 2_5 et 2_6 arrêtées par D32). Aucune exclusion abusive repérée.

**Crosswalk** (lignes « travail » des cinq cadres et des objectifs officiels) : taux d'emploi (3 fiches) et longues durées, incontournables, sont `retenir` ; NEET (cible de 9 %), chômage et chômage de longue durée, intensité de travail, temps partiel subi, bas salaires, contrats temporaires et contrats subis, surqualification, accidents mortels, personnes déclarant un accident (variante `hsw_ac1`), exposition mentale, durée hebdomadaire (écartée), horaires atypiques, satisfaction au travail, passages de l'emploi au chômage, sous-utilisation (OCDE 13_2), emploi non standard (SSF) : tous présents. Absences justifiées : flexibilité des horaires (`lfso_19*`, 2019 seulement), insécurité du marché du travail et tension au travail de l'OCDE (arrêtées), surqualification déclarée (non trouvée). Absences non justifiées : O1.

**Oublis** :

| # | Oubli | Données (lues) | Importance | Proposition |
|---|---|---|---|---|
| O1 | **Exposition aux risques pour la santé physique** (`hsw_exp2`, `estat-026548`) et **problèmes de santé liés au travail** (`hsw_pb1`, `estat-021751`), indicateurs du cadre Qualité de vie | API : `hsw_exp2` 70,0 `d` (2007), 81,6 `bd` (2013), 74,9 `b` (2020) ; `hsw_pb1` 48,9 `d`, 12,4, 8,3 ; long-list `sante`, `a_verifier` (3 points), comme `hsw_exp1` | forte : le contenu de `travail` nomme « conditions et santé au travail : accidents, expositions », et le pendant mental est `retenir` avec les mêmes données | Règles `longlist = sante` dans la présélection `travail` : fiche `exposition_risques_sante_physique` (famille propre) et fiche ou écart motivé pour `hsw_pb1` (rupture 2007-2013 évidente) ; à défaut, `autre_dimension:travail` dans la future présélection `sante`. |
| O2 | **Décès au travail** (Assurance maladie, `deces-par-secteur-d-activite-naf-1-et-naf-5`) ; maladies professionnelles psychiques ; troubles musculosquelettiques | jeux listés dans l'export du catalogue data.ameli.fr du robot ; valeurs non lues (portail refusé à l'outil) | moyenne | Ligne de maintenance (catalogage par le robot M04, taux pour 100 000 salariés) ; reformuler TRA-7 : le jeu existe. |
| O3 | **NEET de l'ODD européen** (`sdg_08_20`, `estat-002088`, 15-29 ans, 2003-2025, 23 points, éligible) | long-list `education` | faible (même concept que `neet`, variante) mais risque R1 | Règle `longlist = education` → `variante_de:neet` ; `sdg_08_20a` (par nationalité) → `autre_dimension:egalites`. |
| O4 | Préoccupation pour « le niveau des salaires et du pouvoir d'achat » (DREES OG04_9, 12 années 2014-2025) | couverture du robot ; utilisée nulle part | faible | À trancher entre `travail` (rémunération) et `niveau_de_vie` ; pas de fiche nécessaire si la session mère juge la question trop proche du pouvoir d'achat. |

Déjà signalés par M05 et non repris comme oublis : source nationale des conditions de travail de la DARES (TRA-8, non trouvée ; M04 la classe `non_verifie`, accès refusé) ; métadonnées des horaires atypiques (TRA-9, toujours non trouvées).

## 11. Cohérence inter-dimensions

Contrôle mécanique (séries principales, composantes, variantes, lignes de présélection) des 37 fiches contre toutes les fiches des autres dimensions : aucun identifiant commun ; **une** ligne commune (`estat-054299`).

| # | Point | Proposition |
|---|---|---|
| I1 | `estat-054299` : variante de `surqualification`, principale d'`egalites` (PR #19) | A2 (§8). |
| I2 | `niveau_de_vie` renvoie 354 lignes vers `travail` (règles `salaires_travail` 268, `salaires_travail_bdm` 72, `pauvrete_travail` 9 + 5 déjà importées) ; **349 ne sont reprises nulle part** : séries longues DERA (salaire EQTP en euros constants, indices, évolutions), BDM (salaires annuels par sexe et PCS, déciles, SMIC et ses indices, pouvoir d'achat des postes à temps complet), `hlth_dpe050` (pauvreté en emploi selon le handicap) | D36 confirme le rattachement : règles `longlist = niveau_de_vie` dans la présélection `travail` (variantes de `salaire_net_moyen_reel` et de `pauvrete_en_emploi`, déciles → `autre_dimension:egalites`, SMIC → écart en bloc comme paramètre de politique, à l'image de la règle 1060). |
| I3 | Lignes envoyées par `travail` et non reprises : `securite` 171 (`lfsa_ugadra`, chômeurs selon l'inscription et l'indemnisation ; le journal des corrections `securite` le note) ; `egalites` 2 (`sdg_05_40`, inactivité pour responsabilités familiales) ; `planete` 4 (emploi de l'économie circulaire) ; `education` 96 (dimension non traitée) | Session mère : pour `sdg_05_40`, A4 (conciliation hors v1) plaide pour un écart en bloc plutôt qu'un renvoi ; pour `lfsa_ugadra`, trancher entre `securite` (sécurité économique) et un écart en bloc. Les 305 ventilations par sexe renvoyées à `egalites` sont conformes à D35. |
| I4 | Long-list `sante` : `hsw_exp2`, `hsw_exp4`, `hsw_exp10`, `hsw_pb1` à `hsw_pb13` (santé au travail) | O1 ; consigne pour M05 `sante`. |
| I5 | Long-list `education` : `sdg_08_20` (NEET) et `sdg_08_20a` | O3 ; consigne pour M05 `education`. |
| I6 | Long-list `logement_cadre_vie` : `ilc_lvhl17`, `ilc_lvhl17n` (très faible intensité de travail selon le statut d'occupation) | Ventilation de `menages_tres_faible_intensite_travail` : consigne `autre_dimension:travail` ou écart en bloc pour M05 `logement_cadre_vie`. |
| I7 | `niveau_de_vie/pauvrete_exclusion_arope` inclut la très faible intensité de travail ; `pauvrete_en_emploi` est une ventilation du taux de pauvreté | J4 ; frontière tranchée par D36 pour la pauvreté en emploi. |

## 12. Liste ordonnée des corrections (à faire par l'agent correcteur ou la session mère)

1. **TRA-3, bloquant pour le gel 2** (§3) : faire lire par le robot les séries `DD_EEC_SERIES` des fiches `neet`, `halo_chomage`, `taux_sous_emploi`, `part_temps_partiel`, `part_emploi_temporaire` (et, au passage, `taux_emploi`, `taux_chomage`, `taux_activite`, les composantes de `taux_chomage_longue_duree`), comparer aux valeurs BDM de contrôle, vérifier le code `EMPSTA=3` des lignes NEET ; passer en principale la série BDM de toute mesure non confirmée.
2. **`taux_emploi_20_64`** (§4) : principale = `lfsi_emp_a` 20-64 ans (2003-2025), `sdg_08_30` en variante, raccordement et note corrigés.
3. **`contrats_tres_courts`** (F2) : définition (trois mois au plus), unité (% des salariés).
4. **`halo_chomage`** (J1) : principale = BDM 011818623 (15-64 ans, 2003-2026), Melodi en variante.
5. **I2** : reprendre les 349 lignes de `niveau_de_vie` (règles `longlist = niveau_de_vie`) ; **A2/I1** : `estat-054299` → `autre_dimension:egalites`.
6. **O1** : importer `hsw_exp2` (et décider de `hsw_pb1`) depuis la long-list `sante` ; **O3** : `sdg_08_20` en variante de `neet` ; **O2** : ligne de maintenance pour le jeu Ameli des décès (et reformulation de TRA-7).
7. **D34** (A1) : recoupements et formules normalisées pour `taux_chomage_longue_duree`, `part_emploi_temporaire`, `preoccupation_chomage`.
8. **`longues_durees_travail`** (F3) : seuil de 49 heures, raccordement 2021 ; clore la partie correspondante de TRA-9.
9. **Mineurs** : F4 (`emploi_temporaire_subi`), F5 (`temps_partiel_subi`), F6 (`accidents_travail_mortels`), F7 (`sorties_chomage_emploi`), « personnes en emploi » pour `satisfaction_travail`, « activité la plus fréquente » pour `pauvrete_en_emploi`, `url_api` de `bas_salaires` vérifiée ou « non trouvé », J5 (champ du salaire avant 2000), J2 (raccordement des risques psychosociaux).
10. Puis `python scripts/preselection.py --dimension travail --maj-fiches`, `python scripts/verifier_fiches.py --dimension travail --tableau` et `python scripts/verifier_fiches.py --dimension travail` (0 erreur, plus d'avertissement R1).

## 13. Questions pour la session mère

1. **Séries longues Melodi non lues** : accepte-t-on de geler des séries principales dont aucune valeur n'a été lue, ou faut-il une collecte ciblée du robot sur `DD_EEC_SERIES` avant le gel 2 (règle générale : « unité confirmée sur les valeurs avant `retenir` ») ?
2. **Santé au travail** : les lignes `hsw_exp*` et `hsw_pb*` (aujourd'hui dans la long-list `sante`) relèvent-elles de `travail` (« conditions et santé au travail ») ou de `sante` ?
3. **349 lignes de salaires** renvoyées par `niveau_de_vie` : confirmer qu'elles reviennent à `travail` (D36) et que la correction de `travail` doit les reprendre.
4. **Lignes orphelines** : `lfsa_ugadra` (171, vers `securite`), `sdg_05_40` (2, vers `egalites` ou hors v1 par A4), emploi de l'économie circulaire (4, vers `planete`) : qui les reprend ?
5. **D34 et microdonnées** : une part recalculée par le projet sur les distributions du baromètre DREES doit-elle être recoupée avec les publications de la DREES (même règle que les écarts construits), y compris pour les fiches déjà validées d'autres dimensions (`securite/preoccupation_insecurite_quartier`, `niveau_de_vie`, `planete`) ?
6. **Accidents mortels** : une fois le jeu Ameli des décès catalogué, série nationale (régime général, sans rupture connue) ou européenne (tous travailleurs, quatre ruptures) en principale ?

## Annexe — sources consultées (15/10/2026)

| Source | Usage |
|---|---|
| API Eurostat (`…/statistics/1.0/data/<code>?…&lang=fr`) : `lfsa_qoe_3a2`, `sdg_08_30`, `lfsi_emp_a`, `hsw_exp1`, `hsw_exp2`, `hsw_pb1`, `hsw_n2_01`, `hsw_n2_02`, `sdg_08_60`, `lfsa_eppgai`, `lfsa_eetpgar`, `ilc_lvhl36`, `lfsa_ewpnig`, `lfsa_ewpsun`, `lfsa_esegatyp`, `ilc_lvhl11`, `lfsi_long_a` (EMP_UNE, UNE_EMP), `lfsa_eoqgan`, `ilc_iw01`, `lfsa_qoe_4ax1r2`, `earn_ses_pub1s`, `lfsi_sla_a` | valeurs, drapeaux, libellés |
| `https://ec.europa.eu/eurostat/cache/metadata/en/lfsa_qoe_esms.htm` | définitions : longues heures (49 h ou plus), emploi précaire (contrat de 3 mois au plus, % des salariés) |
| `https://ec.europa.eu/eurostat/web/products-eurostat-news/-/DDN-20180209-1` | emploi précaire : trois mois au plus, salariés ; France 4,8 % en 2016 |
| BDM INSEE (`bdm.insee.fr/series/sdmx/data/SERIES_BDM/<idbank>`) : 011818634, 011818669, 011818623, 011818639, 011818670, 011818581, 010596081, 010597456, 010752333 | titres, zones, périodes, valeurs de contrôle |
| `https://www.insee.fr/fr/statistiques/8977323`, `…/8977299` | rétropolations des séries longues, tableaux t302-t310 |
| Recherches web : définition de l'emploi précaire et des longues heures (Eurostat) | pages Eurostat ci-dessus |
| Extraits du robot (dépôt) : `cnam_ameli__sinistralite_naf1.csv`, `ocde__hsl_bien_etre_actuel.csv`, `drees__barometre_2000_2025_distributions.csv`, `drees__barometre_2000_2025_couverture.csv`, `drees__barometre_dico_*_2025.txt`, `docs/sources/verif_acces/extraits/cnam_ameli__ods_catalogue_export.txt` ; catalogues Melodi (`TRAVSATISF`), table des zones BDM | valeurs, couvertures, jeux disponibles |
| **Non lus** : API Melodi et fichiers xlsx d'insee.fr (robots.txt) ; `catalogue-donnees.insee.fr` et outil interactif 5369554 (JavaScript) ; data.ameli.fr (`sinistralite-par-secteur-d-activite-concerne-naf-1`) et API SDMX de l'OCDE (`FRA.2_8_DEP…`) (autorisation non accordée à temps) ; API Eurostat `lfsa_ewhuis`, `une_ltu_a`, `lfsi_neet_a` (HTTP 429, non relancées) ; métadonnées des horaires atypiques (non trouvées) | — |
