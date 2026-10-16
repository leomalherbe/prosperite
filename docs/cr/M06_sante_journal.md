# Journal de bord — M06, audit croisé de la dimension `sante`

Agent auditeur M06 (session neuve, Opus), 16 octobre 2026, branche `m06-sante` (worktree isolé). L'agent n'a pas participé à M05 `sante`. Rapport : `docs/validation/audit_sante.md`. Aucune fiche, aucune règle, aucun tableau, aucun script ni aucun catalogue n'a été modifié ; scripts de lecture de l'auditeur dans `tmp/m06-sante/` (non commités).

## 0. Mise en route (09 h 00)

- `git fetch origin && git checkout -B m06-sante origin/main` : base `d85ef3a` (journal D37-D40, fusions M05 `sante` PR #20, `education` PR #22, `logement_cadre_vie` PR #26, corrections `democratie` PR #23).
- Lus : `CLAUDE.md` ; charte §3.4, §3.6, §4, §5.1 ; journal D13 à D40 (en particulier D31-D40 : D38 b, d ; D39 chutes, items SILC, santé au travail, satisfaction DREES) ; méthode commune v1.2 (`docs/methodo/33_methode_fiches_M05.md`) ; fiche M06 ; `indicateurs/dimensions.yaml` (contenu et exclusions de `sante`, R1 à R8) ; modèles `audit_travail.md`, `audit_planete.md`, `M06_travail_journal.md` ; §5 de `30_crosswalk_synthese.md` et lignes santé de `30_indicateurs_cadres_reference.csv`.
- Matériau audité : 49 fiches `indicateurs/sante/*.yaml`, `validation_sante.csv`, `preselection_sante.csv` (117 groupes), `preselection_sante_lignes.csv` (14 188 lignes), `regles_preselection_sante.csv`, journal et compte rendu M05, SAN-1 à SAN-7 (`maintenance_catalogues.md`), `catalogues/longlist_sante.csv.gz` (14 168 lignes) et les autres long-lists, catalogues Eurostat (séries, jeux), sorties du robot M04 (`docs/sources/series/`).
- Contrôles de départ : `python -m pytest -q` → 399 réussis ; `python scripts/verifier_fiches.py --dimension sante` → **0 erreur, 11 avertissements** (séries hors catalogue avec preuve, attendus) ; compteurs : 49 fiches, 38 familles, 37 `retenir`, 11 `retenir_variante`, 1 `ecarter`, 11 déclaratives, 1 composite, 4 à vérifier, 8 hors long-list, 9 incontournables, 908 variantes, 181 lignes `autre_dimension`, 0 ligne prise ailleurs.

## 1. Échantillon

- D'office : 1 `ecarter` ; 9 `incontournable: oui` ; 4 `a_verifier` ; 12 autres `raccordement: a_etudier` ; 5 hors long-list non encore comptées ; 5 points d'attention (`deces_pollution_air`, `consommation_antibiotiques`, `natalite_adolescentes`, `manque_medecins_percu`, `mortalite_chutes`). Total : 36.
- Tirage : 20 % des 39 fiches ni `ecarter` ni incontournables = 7,8, arrondi à 8, tirées parmi les 13 non retenues d'office. `random.Random(20261014).sample(pool, 8)`, `pool` = liste triée `['consommation_alcool', 'depistage_cancer_colorectal', 'mortalite_cancer', 'mortalite_cardiovasculaire', 'mortalite_diabete', 'mortalite_evitable', 'mortalite_infantile', 'mortalite_maladies_respiratoires', 'mortalite_maternelle', 'mortalite_prematuree', 'morts_desespoir', 'naissances_prematurees', 'vaccination_ror']`, **graine 20261014** → `mortalite_cancer`, `mortalite_evitable`, `mortalite_maladies_respiratoires`, `mortalite_maternelle`, `mortalite_prematuree`, `morts_desespoir`, `naissances_prematurees`, `vaccination_ror`.
- Les 5 restantes vérifiées aussi à la source : **49 fiches sur 49**.

## 2. Vérifications à la source (WebFetch, 16/10/2026)

| Source | Lu | Constat |
|---|---|---|
| Eurostat `demo_mlexpec` Y_LT1 | 1998-2024 | 79,2 (2000) … 82,7 (2019), 82,2 (2020-2022), 82,9 (2023 p), 83,0 (2024 p) ; b 2012, 2014 |
| Eurostat `demo_mlexpec` Y65 | 1998-2024 | 19,1 (1998) … 21,7 (2019), 21,0 (2020), 21,9 (2024 p) ; b 2012, 2014 ; identique à `hlth_hlye` LE_Y65 jusqu'en 2013, puis inférieure de 0,1 à 0,5 an |
| Eurostat `hlth_hlye` LE_Y65, HLY_Y0, HLY_Y65 | 2004-2024 | 20,1 → 22,0 (2019) → 21,2 (2020) → 21,9 ; p 2023 ; HLY_Y0 62,9 … 64,6 (b) 66,2, 64,4 (bp), 63,6 (p) ; HLY_Y65 9,3 … 12,0 (2021), 10,9 (2024 p) |
| Eurostat `sdg_03_20` VG_G, `hlth_silc_10` B_VB | 2005-2025 | 68,8 → 64,7 ; 9,9 → 7,7 (2015) → 10,8 (2023) → 10,2 ; b 2020, 2022 |
| Eurostat `hlth_silc_04`, `hlth_silc_19` | 2008-2025 ; 2004-2025 | 36,7 → 41,7 ; `hlth_silc_19` 33,5 (2007) → 36,5 (2008) sans drapeau |
| Eurostat `hlth_silc_06` SM_SEV, SEV | 2008-2025 | 23,2 … 22,7 (2021) … 26,8 (2023) … 25,8 ; 8,6 … 8,3 (2021) … 10,2 (2023) … 9,8 |
| Eurostat `sdg_03_60`, `hlth_silc_09`, `hlth_silc_08` TXP | 2008-2025 | 2,8 → 1,2 (2015) ; 5,6 → 3,4 (2015), 2,7 → 6,4 (2020 b) ; 2,3 → 0,8 (2015), 1,9 (2025) |
| Eurostat `sdg_03_42` TOTAL, PRVT, TRT | 2011-2023 | 214,83 → 185,97 ; PRVT 125,53 (2019) → 145,24 (2021) ; TRT 67,64 → 58,76, 59,39 en 2022 ; sans drapeau |
| Eurostat `hlth_cd_asdr2` C, I, J, W00-W19, E10-E14 | 2011-2023 | 253,11 → 218,58 ; 224,76 → 163,26 ; 55,28 … 45,41 (2021) … 56,44 ; 9,86 → 13,47 ; 18,26 → 15,18 ; sans drapeau |
| Eurostat `sdg_11_52` + métadonnées ESMS | 2005-2023 | **lue pour la première fois** : 61, 2006 absent, 53 (2013) → 34 (2014) sans drapeau, 22 (2023) ; contrefactuel 5 µg/m³ |
| Eurostat `sdg_03_41`, `sdg_03_70`, `hlth_ps_immu`, `hlth_ps_prev`, `hlth_sha11_hf` HF3, `sdg_02_10` | — | conformes aux fiches ; `sdg_02_10` : 6 années seulement (2008, 2014, 2017, 2019, 2022, 2025) |
| BDM 001641594, 001744911, 010599567, 010593272, 010761075, 010593299, 010593303 | — | titres, zones (FE, FM), unités, valeurs conformes ; VIH au statut E ; tabac ODD 18,2 % en 2024 |
| SPF, page Baromètre santé 2021 (dépression) | — | 13,3 % des 18-75 ans en 2021 (9,8 % en 2017), **France métropolitaine** ; 12,5 % des 18-85 ans |
| SPF, synthèse Baromètre 2024 (dépression) | — | 15,6 % des 18-79 ans en 2024 |
| SPF, page couverture HPV | — | filles nées en 2007 : 44,7 % (schéma complet à 16 ans, au 31/12/2023) = OCDE 45 en 2023 |
| API Odissé (`…/records`) | refusée | autorisation non accordée puis robots.txt : non relancée |

## 3. Lectures dans le dépôt

- Extraits du robot : OCDE ODD 3 (3_1_1, 3_3_*, 3_4_1, 3_4_2, 3_5_2, 3_7_2, 3_8_1, 3_B_1), OCDE How's Life (5_3, 11_3), PNUD (mmr, abr), SPF (dépression, pensées suicidaires, mortinatalité, prématurité, vaccinations du 24e mois, tabac, suicides, chutes) : périodes et dernières valeurs conformes aux fiches.
- Distributions DREES : recalcul des parts de SA05 (3+4), SA07_1 et SA07_2 (1+2), SA09_1 (3) : identiques à M05 ; recalcul D39 (modalité 6 « jamais allé » hors dénominateur) : SA07_1 75,2 % en 2014 et 63,7 % en 2025 ; SA07_2 57,0 % et 44,1 %.
- Catalogue Odissé exporté par le robot (`spf_odisse__catalogue_champs.csv`, 13/10/2026) : jeux `diabete-prevalence-france`, `couvertures-vaccinales-des-adolescents-et-adultes-depuis-2011-france`, éditions 2024 du Baromètre (dépression, conduites suicidaires, tabac), dépistage colorectal, décès attribuables à la chaleur — absents des catalogues et des fiches, et déclarés « non trouvés » par SAN-7 pour les deux premiers.
- Contrôle croisé mécanique (séries principales, composantes, variantes, `ligne_id`) des 49 fiches contre toutes les fiches des autres dimensions : aucun identifiant ni aucune série en commun. Lignes `autre_dimension` : `egalites` 10/10 reprises, `securite` 54/54, `logement_cadre_vie` 1/1 ; **`travail` 0/104 et `niveau_de_vie` 0/12 reprises** ; lignes reçues : 20 `ilc_lvhl01` de `logement_cadre_vie`, toutes importées.

## 4. Résultat

49 fiches auditées : 35 `conforme` (6 avec réserve ou remarque), 14 `a_corriger` (5 F, 9 A, dont 2 avec J), 0 `non_verifiable` ; 7 oublis, 9 points inter-dimensions, 8 désaccords de jugement ; avis `corrections_necessaires`. Liste ordonnée des corrections : §10 du rapport. Rapport copié dans le Projet claude.ai (`claude/cr/M06_sante_audit.md`).
