# Audit croisé M06 — dimension `sante`

Agent auditeur M06 (session neuve, n'ayant pas participé à M05 `sante`), 16 octobre 2026. Branche `m06-sante`, créée depuis `origin/main` au commit `d85ef3a` (fiches `sante` fusionnées par la PR #20, puis décisions D37 à D40). Matériau audité : les 49 fiches `indicateurs/sante/*.yaml`, `docs/validation/validation_sante.csv`, `preselection_sante.csv`, `preselection_sante_lignes.csv`, `regles_preselection_sante.csv`, le journal et le compte rendu M05, les lignes SAN-1 à SAN-7 de `docs/cr/maintenance_catalogues.md`, la long-list `catalogues/longlist_sante.csv.gz` et les autres long-lists, les catalogues Eurostat, les sorties du robot M04 (`docs/sources/series/`). **Aucune fiche, aucune règle, aucun tableau, aucun script ni aucun catalogue n'a été modifié** : ce rapport propose, l'agent correcteur (ou la session mère) corrige. Déroulé : `docs/cr/M06_sante_journal.md`.

Contrôle préalable : `python -m pytest -q` → 399 réussis ; `python scripts/verifier_fiches.py --dimension sante` (sans `--tableau`) → **0 erreur, 11 avertissements**, tous « série principale hors catalogue avec preuve » (8 fiches hors long-list, une alerte par composante pour les séries DREES), attendus ; compteurs : 49 fiches, 38 familles, 37 `retenir`, 11 `retenir_variante`, 1 `ecarter`, 11 déclaratives, 1 composite, 4 « à vérifier », 8 hors long-list, 9 incontournables, 908 variantes, 181 lignes `autre_dimension`, 0 ligne prise ailleurs.

Nature des constats : **F** = erreur factuelle (source et valeur attendue citées) ; **A** = alignement sur une décision postérieure à M05 (D38, D39 du 15/10), sans faute de M05 ; **J** = désaccord de jugement (à trancher par la session mère ou Léo) ; **O** = oubli ; **I** = incohérence entre dimensions.

## 0. Avis global : `corrections_necessaires`

Le travail de M05 est de bonne qualité. Les 38 familles couvrent les cinq thèmes de `dimensions.yaml` (espérance de vie et mortalité, santé perçue et limitations, santé mentale, accès aux soins, comportements et nutrition). Les choix structurants sont fondés : Eurostat principal pour les séries EU-SILC (l'INSEE ne publie pas ces niveaux, D35), taux standardisés `hlth_cd_asdr2` pour les causes de décès, mortinatalité spontanée plutôt que totale, tués sur la route et homicides renvoyés à `securite` (A6), santé au travail renvoyée à `travail` (confirmé par D39). **Toutes les valeurs Eurostat et BDM citées ont été retrouvées à la source** (27 requêtes sur 19 jeux Eurostat, 7 séries BDM, sorties du robot pour l'OCDE, le PNUD, Santé publique France et la DREES), drapeaux compris ; les ruptures SRCV de 2020 et 2022 et les chutes non signalées de 2008 (`hlth_silc_19`) et de 2015 (besoins non satisfaits) sont exactes.

Quatre groupes de problèmes doivent être réglés avant la validation de Léo :

1. **Alignements sur D38 et D39** (A) : la satisfaction envers les hôpitaux publics et les urgences (DREES) doit être recalculée hors répondants « jamais allé » (D39), ce qui relève la série de 2 à 4 points depuis 2014 (§3) ; quatre fiches variantes portent `incontournable: oui` alors que D38 (d) le réserve à la variante principale ; les quatre séries DREES calculées par le projet doivent porter `non_recoupe` (D38 b) ; la note de `mortalite_chutes` doit citer D39.
2. **Erreurs factuelles** (F) : `deces_pollution_air` peut maintenant être lue (18 valeurs, de 61 à 22 décès pour 100 000) et montre un saut non expliqué de 2013 à 2014 (53 → 34) ; les épisodes dépressifs et les pensées suicidaires du Baromètre santé portent sur la **France métropolitaine** (`geo: FR` à corriger en `FM`) ; l'obésité n'a que 6 vagues irrégulières mais porte `frequence: annuelle` ; la population cible de la vaccination HPV est identifiable (filles, schéma complet à 16 ans).
3. **Oublis** (O) dans les sorties du robot, contrairement à SAN-7 (« non trouvé ») : **prévalence du diabète traité** (Santé publique France, jeu `diabete-prevalence-france`) ; **couvertures vaccinales HPV et grippe** de Santé publique France 2011-2025 ; **édition 2024 du Baromètre de Santé publique France** pour la dépression (15,6 % des 18-79 ans), les conduites suicidaires et le tabac ; participation au dépistage colorectal de Santé publique France ; décès attribuables à la chaleur (rattachement à trancher).
4. **Jugements à trancher** (J) : espérance de vie à 65 ans (la série `demo_mlexpec`, 1998-2024, cohérente avec la fiche principale, s'écarte de `hlth_hlye` à partir de 2014) ; santé mentale incontournable ou non ; drapeau `declaratif` de l'indicateur GALI (oui ici, non en `egalites`).

Chiffres : **49 fiches auditées sur 49** — **35 `conforme`** (dont 6 avec réserve ou remarque mineure), **14 `a_corriger`** (5 F, 9 A ; 2 portent aussi un J), **0 `non_verifiable`** (les valeurs de Santé publique France non lisibles à l'API sont celles que les fiches déclarent déjà non lues). 7 oublis, 9 points de cohérence inter-dimensions, 8 désaccords de jugement. Liste ordonnée des corrections : §10.

## 1. Échantillon

| Règle (fiche M06 et consigne de la session mère) | Fiches |
|---|---|
| `recommandation: ecarter` (1) | `decouvertes_vih` |
| `incontournable: oui` (9) | `esperance_vie_naissance`, `esperance_vie_65`, `esperance_vie_sans_incapacite`, `esperance_vie_sans_incapacite_65`, `sante_percue_bonne`, `sante_percue_mauvaise`, `maladie_chronique`, `limitations_activite`, `limitations_activite_fortes` |
| Éligibilité `a_verifier` (journal M05) (4) | `douleur_physique`, `episodes_depressifs`, `pensees_suicidaires`, `obesite` |
| Autres `raccordement: a_etudier` (journal M05) (12) | `besoins_soins_non_satisfaits`, `besoins_soins_dentaires_non_satisfaits`, `renoncement_soins_financier`, `densite_medecins_generalistes`, `reste_a_charge_menages`, `mortalite_maladies_infectieuses`, `mortinatalite`, `suicide`, `tabagisme_quotidien`, `vaccination_grippe_seniors`, `satisfaction_soins_hopital`, `satisfaction_urgences` |
| Hors long-list non encore comptées (5) | `couverture_sanitaire_universelle`, `mortalite_prematuree_mnt`, `mortalite_traitable`, `sante_francais_percue_degradee`, `vaccination_hpv` |
| Points d'attention (compte rendu M05 §6 ; D39) (5) | `deces_pollution_air` (valeurs non lues), `consommation_antibiotiques` et `natalite_adolescentes` (`hors_contenu_cite`), `manque_medecins_percu` (DREES), `mortalite_chutes` (D39) |
| 20 % des 39 fiches « autres » (ni `ecarter` ni incontournables), soit 7,8 arrondi à 8, tirées parmi les 13 non retenues d'office | `mortalite_cancer`, `mortalite_evitable`, `mortalite_maladies_respiratoires`, `mortalite_maternelle`, `mortalite_prematuree`, `morts_desespoir`, `naissances_prematurees`, `vaccination_ror` |
| Les 5 restantes, vérifiées aussi à la source | `consommation_alcool`, `depistage_cancer_colorectal`, `mortalite_cardiovasculaire`, `mortalite_diabete`, `mortalite_infantile` |

Tirage : `random.Random(20261014).sample(pool, 8)` en Python 3, `pool` = liste triée des 13 fiches non retenues d'office ; **graine 20261014**, celle des audits précédents. **36 fiches d'office + 8 tirées + 5 restantes = 49.**

## 2. Fiches auditées

Sources lues par WebFetch le 16/10/2026 (détail en annexe) ; extraits du robot lus dans le dépôt ; parts DREES recalculées sur `docs/sources/series/drees__barometre_2000_2025_distributions.csv`.

| Fiche | Motif d'inclusion | Source consultée | Verdict | Nature | Constat, correction attendue (détail aux §3 à §7) |
|---|---|---|---|---|---|
| `decouvertes_vih` | ecarter | BDM 010593272 | conforme | — | 6 110 (2010) … 4 848 (2020) … 5 850 (2024), toutes au statut `E` (estimations) ; sens ambigu fondé (dépistage). Remarque : signaler le statut `E` dans `qualite`. |
| `esperance_vie_naissance` | incontournable | API `demo_mlexpec` (Y_LT1) | conforme | — | 1998-2024 ; 79,2 (2000), 82,7 (2019), 82,2 (2020-2022), 83,0 (2024) ; `b` 2012 et 2014, `p` 2023-2024. Les séries BDM sont intitulées « France (inclus Mayotte à partir de 2014) », ce qui appuie l'hypothèse de la note sur la rupture de 2014. |
| `esperance_vie_65` | incontournable | API `hlth_hlye` (LE_Y65) et `demo_mlexpec` (Y65) | **a_corriger** | A, J | Valeurs exactes (20,1 en 2004 ; 22,0 en 2019 ; 21,2 en 2020 ; 21,9 en 2024 ; `p` 2023) ; `incontournable: non` (D38 d). J1 : `demo_mlexpec` Y65 couvre 1998-2024 et diffère de `hlth_hlye` à partir de 2014 (§5). |
| `esperance_vie_sans_incapacite` | incontournable | API `hlth_hlye` (HLY_Y0) | conforme | — | 62,9 (2004) … 64,6 (2020, `b`), 66,2 (2021), 64,4 (2022, `bp`), 63,6 (2024, `p`). |
| `esperance_vie_sans_incapacite_65` | incontournable | API `hlth_hlye` (HLY_Y65) | **a_corriger** | A | Valeurs exactes (9,3 ; 11,0 en 2019 ; 12,0 en 2021 ; 10,9 en 2024) ; `incontournable: non` (D38 d). |
| `sante_percue_bonne` | incontournable | API `sdg_03_20` (VG_G) | conforme | — | 68,8 (2005) → 64,7 (2025) ; `b` 2020 et 2022 seulement. |
| `sante_percue_mauvaise` | incontournable | API `hlth_silc_10` (B_VB) | **a_corriger** | A | Valeurs exactes (9,9 ; 7,7 en 2015 ; 10,8 en 2023 ; 10,2 en 2025) ; `incontournable: non` (D38 d). |
| `maladie_chronique` | incontournable | API `hlth_silc_04`, `hlth_silc_19` | conforme | (J6) | 36,7 (2008) → 41,7 (2025), `b` 2020 et 2022 ; `hlth_silc_19` saute bien de 33,5 (2007) à 36,5 (2008) sans drapeau : choix de la principale fondé. |
| `limitations_activite` | incontournable | API `hlth_silc_06` (SM_SEV) | conforme | (J5) | 23,2 (2008), 22,7 (2021), 26,8 (2023), 25,8 (2025). |
| `limitations_activite_fortes` | incontournable | API `hlth_silc_06` (SEV) | **a_corriger** | A | Valeurs exactes (8,6 ; 8,3 en 2021 ; 10,2 en 2023 ; 9,8 en 2025) ; `incontournable: non` (D38 d). |
| `douleur_physique` | a_verifier | extrait OCDE `11_3` du robot | conforme | — | 20 périodes 2006-2025, 7 valeurs distinctes (moyennes groupées), 32,96 % ; D17 et D28 respectés ; licence Gallup signalée (D26). |
| `episodes_depressifs` | a_verifier | extrait SPF du robot ; page SPF « Baromètre santé 2021 » ; synthèse SPF 2024 | **a_corriger** | F, O | 13,27 % en 2021 confirmé (« 13,3 % » des 18-75 ans, contre 9,8 % en 2017), **en France métropolitaine** : `geo: FM`, définition et `qualite` à corriger ; vague 2024 disponible (15,6 % des 18-79 ans, O3). |
| `pensees_suicidaires` | a_verifier | extrait SPF du robot | **a_corriger** | F, O | 4,21 % en 2021 ; même Baromètre santé, donc France métropolitaine (`geo: FM`) ; vague 2024 disponible (jeu `conduites-sucidaires-indicateurs-du-barometre-2024`, O3) ; anomalie d'intervalle confirmée dans l'extrait (SAN-6). |
| `obesite` | a_verifier | API `sdg_02_10` (BMI_GE30) | **a_corriger** | F | 12,2 (2008), 15,3 (2014), 15,1 (2017), 15,0 (2019), 15,2 (2022), 16,3 (2025), aucune autre année : `frequence: irreguliere` (D17), au lieu d'`annuelle` (fiche et tableau). |
| `besoins_soins_non_satisfaits` | a_etudier | API `sdg_03_60` | conforme | — | 1,9 (2008), 2,8 (2014) → 1,2 (2015) sans drapeau, 2,7 (2020, `b`), 4,1 (2024), 3,7 (2025). |
| `besoins_soins_dentaires_non_satisfaits` | a_etudier | API `hlth_silc_09` | conforme | — | 4,2 (2008), 5,6 → 3,4 (2015), 2,7 (2019) → 6,4 (2020, `b`), 7,0 (2024), 6,5 (2025). |
| `renoncement_soins_financier` | a_etudier | API `hlth_silc_08` (TXP) ; BDM 010593299 | conforme | — | Valeurs identiques de 2010 à 2023 (1,7 … 0,8 en 2015 … 1,8), BDM en `FM`, sans valeur en 2024-2025 : choix d'Eurostat fondé. |
| `densite_medecins_generalistes` | a_etudier | BDM 010761075 | conforme (remarque) | — | 155 (2012) → 145 (2024) → 146 (2025) : « baisse continue » à nuancer (hausse d'un point en 2025). |
| `reste_a_charge_menages` | a_etudier | API `hlth_sha11_hf` (HF3, PC_CHE) | conforme | (J7) | 9,36 (2006), 10,17 (2009) → 11,96 (2010, `b`), 10,17 à 10,38 de 2021 à 2025, `p` 2025. |
| `mortalite_maladies_infectieuses` | a_etudier | API `sdg_03_41` | conforme | — | 5,80 (2001) … 2,90 (2010), 2,73 (2011) … 1,01 (2023), sans drapeau, 2000 vide. |
| `mortinatalite` | a_etudier, hors long-list | extrait SPF du robot | conforme (réserve) | — | 11 périodes 2014-2024 ; 2024 : 9,208 = 5,627 spontanée + 3,581 induite (6 094 = 3 724 + 2 370) ; valeurs 2014-2023, dénominateur et seuil de terme non lisibles (API Odissé refusée), comme la fiche le déclare. |
| `suicide` | a_etudier | BDM 010599567 ; extraits OCDE et SPF | conforme | — | 16,9 (2011), 15,8 (2012), 14,2 (2022), 13,0 (2023), 2024-2025 vides ; SPF 13,0 en 2023 ; OCDE 3_4_2 13,1 en 2022 contre 14,2 à la BDM : la note « standardisation à vérifier » est justifiée. |
| `tabagisme_quotidien` | a_etudier | extrait SPF ; BDM 010593303 | conforme (réserve) | (O3) | SPF : 13 vagues 2000-2023, 23,12 % ; BDM (`FM`) : 29,7 (2010), 28,5 (2014), 29,4 (2016) … 25,3 (2021), 18,2 (2024), rien en 2022-2023. Vague 2024 de Santé publique France à intégrer (O3). |
| `vaccination_grippe_seniors` | a_etudier | API `hlth_ps_immu` | conforme | (O2) | 53,0 (2000) → 65,0 (2001) ; `b` 2005 ; 63,9 (2010) → 48,5 (2015) → 59,9 (2021) → 53,7 (2025). |
| `satisfaction_soins_hopital` | a_etudier, hors long-list | distributions DREES (recalcul) ; dictionnaire 2025 | **a_corriger** | A | Recalcul exact selon la convention de M05 (69,2 ; 73,1 ; 58,4 ; 61,3) ; D39 impose d'exclure la modalité 6 « jamais allé » : 75,2 (2014), 63,7 (2025)… (§3) ; `rupture_2014`, `non_recoupe`. |
| `satisfaction_urgences` | a_etudier, hors long-list | distributions DREES (recalcul) | **a_corriger** | A | Idem : 57,0 (2014), 45,3 (2019), 42,8 (2022), 44,1 (2025) hors « jamais allé » (§3). |
| `couverture_sanitaire_universelle` | hors long-list | extrait OCDE 3_8_1 | conforme | (J8) | 7 périodes 2000-2021, 5 valeurs distinctes, 85 en 2021. |
| `mortalite_prematuree_mnt` | hors long-list | extrait OCDE 3_4_1 | conforme | — | 7 périodes (2000, 2005, 2010, 2015, 2019-2021), 10,2 en 2021. |
| `mortalite_traitable` | hors long-list | API `sdg_03_42` (TRT) | conforme (remarque) | — | 67,64 (2011) → 58,76 (2023) ; 58,82 (2021) → 59,39 (2022) : « baisse continûment » à nuancer. TOTAL = PRVT + TRT vérifié. |
| `sante_francais_percue_degradee` | hors long-list | distributions DREES (recalcul) ; dictionnaire 2025 | **a_corriger** | A | Recalcul exact : 26,9 (2000), 40,3 (2019), 53,6 (2020), 61,2 (2025) ; 25 vagues (pas de 2003) ; `non_recoupe` à ajouter (D38 b). |
| `vaccination_hpv` | hors long-list | extrait OCDE 3_B_1 ; page SPF des couvertures HPV | **a_corriger** | F, J | 13 périodes 2011-2023, 45 en 2023 = 44,7 % des **filles** nées en 2007, schéma complet à 16 ans (SPF, données au 31/12/2023) : définition à préciser ; série nationale SPF 2011-2025 disponible (J3, O2). |
| `deces_pollution_air` | valeurs non lues | API `sdg_11_52` ; métadonnées `sdg_11_52_esmsip2` | **a_corriger** | F | Lue : 61 (2005), 2006 absent, 53 (2013) → 34 (2014) sans drapeau, 22 (2023) ; contrefactuel 5 µg/m³ (lignes directrices OMS 2021) ; retirer `valeurs_non_lues`, `raccordement: a_etudier` (§4). |
| `consommation_antibiotiques` | hors contenu cité | API `sdg_03_70` | conforme | (J4) | 25,9 (2013), 20,3 (2020), 26,5 (2024), sans drapeau. |
| `natalite_adolescentes` | hors contenu cité | extrait PNUD ; extrait OCDE 3_7_2 | conforme | (J4) | 34 périodes 1990-2023, 3,507 en 2023 ; l'OCDE (3_7_2) donne 6,36 en 2021 : estimations divergentes, à signaler dans `qualite`. |
| `manque_medecins_percu` | DREES | distributions DREES (recalcul) | **a_corriger** | A | Recalcul exact (20,7 ; 28,3 ; 36,3 ; 49,6 ; 57,8 ; 55,8) ; 11 vagues ; `non_recoupe` à ajouter (D38 b). |
| `mortalite_chutes` | D39 | API `hlth_cd_asdr2` (W00-W19) ; extrait SPF | **a_corriger** | A | 9,86 (2011) → 13,47 (2023), +37 %, saut 2021-2022 (11,85 → 13,34) déjà signalé (`certification_a_verifier`) ; rattachement tranché par D39 : réécrire la note. |
| `mortalite_cancer` | tirage | API `hlth_cd_asdr2` (C) | conforme | — | 253,11 → 218,58 (−14 %), sans drapeau. |
| `mortalite_evitable` | tirage | API `sdg_03_42` (TOTAL, PRVT, TRT) | conforme | — | 214,83 ; 185,84 (2019) ; 204,06 (2021) ; 185,97 (2023) ; PRVT 125,53 → 145,24. |
| `mortalite_maladies_respiratoires` | tirage | API `hlth_cd_asdr2` (J) | conforme | — | 55,28 ; 51,93 (2014) ; 60,47 (2015) ; 48,51 (2020) ; 45,41 (2021) ; 56,44 (2023). |
| `mortalite_maternelle` | tirage | extraits PNUD et OCDE 3_1_1 | conforme | — | 34 périodes 1990-2023, 7,909 en 2023 ; OCDE 2000-2018, 8,2. |
| `mortalite_prematuree` | tirage | BDM 001744911 | conforme | — | « Taux de mortalité standardisé - 0-64 ans (prématuré) - France (inclus Mayotte à partir de 2014) », ‰ ; 2,2 (1998-2001) → 1,7 (2023-2025, provisoires). |
| `morts_desespoir` | tirage | extrait OCDE `5_3` | conforme | — | 20 périodes 2004-2023, 18,70 en 2023. |
| `naissances_prematurees` | tirage | extrait SPF | conforme | — | 13 périodes 2012-2024, 6,688 % ; faible poids 7,447 %. |
| `vaccination_ror` | tirage | extrait SPF | conforme | — | `cs24_ror2` : 15 périodes 2010-2024, 92,7 % ; DTP 96,4 %. |
| `consommation_alcool` | contrôle | extrait OCDE 3_5_2 | conforme | — | 24 périodes 2000-2023, 10,4 litres. |
| `depistage_cancer_colorectal` | contrôle | API `hlth_ps_prev` | conforme | (O4) | 28,20 (2011) … 24,90 (2020), `m` 2015-2016, `b` 2017, 29,60 (2024). |
| `mortalite_cardiovasculaire` | contrôle | API `hlth_cd_asdr2` (I) | conforme | — | 224,76 → 163,26 (−27 %). |
| `mortalite_diabete` | contrôle | API `hlth_cd_asdr2` (E10-E14) | conforme | (O1) | 18,26 → 15,18 (−17 %). |
| `mortalite_infantile` | contrôle | BDM 001641594 | conforme | — | 4,5 (2000), 3,5 (2011, 2012, 2014), 4,1 (2024), 4,0 (2025, `P`), champ FE. |

Contrôles transversaux : `sens` (tous `haut`/`bas` sauf `decouvertes_vih`), `type` (40 résultats, 6 moyens au titre de D19, 3 pressions) et `declaratif` (`oui` pour la santé perçue, l'indicateur GALI et les opinions DREES ; `non` pour la maladie chronique, les besoins non satisfaits et les états mesurés par questionnaire standardisé) sont conformes à la méthode §4, sous réserve de J5. Les variantes principales suivent la méthode (Eurostat principal quand l'INSEE ne publie pas le niveau, enquête plutôt que série enregistrée), sauf J1 et J3.

## 3. Satisfaction envers les soins (DREES) : recalcul imposé par D39 (A)

Le dictionnaire 2025 (`drees__barometre_dico_libelles_2025.txt`) donne pour SA07_* : 1 « Très satisfait.e », 2 « Plutôt satisfait.e », 3 « Ni satisfait.e ni insatisfait.e », 4 « Plutôt insatisfait.e », 5 « Très insatisfait.e », 6 « (Je n'y suis jamais allé.e / je ne connais pas) », 999999999 « (NSP) ». La modalité 6 n'existe qu'à partir de 2014. M05 garde les modalités 6 et NSP au dénominateur (convention du tableau officiel) ; D39 (15/10, postérieure à M05) impose d'exclure la modalité 6 et de signaler la rupture de 2014.

Parts recalculées par l'audit sur les distributions du robot, modalités 1 + 2, **modalité 6 exclue du dénominateur, NSP conservé** (les années antérieures à 2014 ne changent pas) :

| Année | SA07_1 hôpitaux publics (convention M05 → attendu D39) | SA07_2 urgences (convention M05 → attendu D39) |
|---|---|---|
| 2010 | 69,2 → 69,2 | 63,0 → 63,0 |
| 2013 | 66,8 → 66,8 | 52,7 → 52,7 |
| 2014 | 73,1 → **75,2** | 54,3 → **57,0** |
| 2018 | 62,5 → **65,0** | 42,1 → **45,6** |
| 2019 | 65,3 → **68,5** | 41,4 → **45,3** |
| 2021 | 68,6 → **71,4** | 51,0 → **55,4** |
| 2022 | pas de question | 38,6 → **42,8** |
| 2023 | 58,4 → **60,8** | 38,3 → **41,3** |
| 2025 | 61,3 → **63,7** | 41,1 → **44,1** |

**Correction attendue** (fiches `satisfaction_soins_hopital`, `satisfaction_urgences`, et leurs variantes SA07_5 et SA07_3) : définition « parmi les personnes qui ont un avis sur ce prestataire (modalité « jamais allé.e / ne connais pas » exclue à partir de 2014) » ; formule `(M1 + M2) / (100 − M6) * 100` ; motif et note avec les valeurs ci-dessus ; `qualite` : `rupture_2014` (avant 2014, les non-usagers ne peuvent pas être distingués), `non_recoupe` (D38 b) ; le contrôle de plausibilité reste la valeur officielle 2025 (61,29 %) reproduite avec la convention du tableau officiel. Même ajout de `non_recoupe` pour `sante_francais_percue_degradee` et `manque_medecins_percu`, dont les recalculs de l'audit sont identiques à ceux de M05.

## 4. Décès attribuables aux particules fines (F)

L'API Eurostat, refusée deux fois à M05 (HTTP 429), a répondu le 16/10/2026 : `sdg_11_52` (PM2_5, PMD, RT, FR) donne **61 (2005), 51 (2007), 54, 61, 62, 61, 55, 53 (2013), 34 (2014), 42, 36, 34, 34, 27, 24 (2020), 29, 30, 22 (2023)** décès prématurés pour 100 000 habitants, **2006 absent**, aucun drapeau. Les métadonnées (`sdg_11_52_esmsip2`, mises à jour le 21/05/2026) précisent : seul l'impact au-delà de **5 µg/m³** (ligne directrice OMS 2021) est compté, risque relatif de 8 % par 10 µg/m³, même approche pour toutes les années ; 2006 manque faute de cartes interpolées ; aucune rupture n'est documentée.

**Correction attendue** : retirer `valeurs_non_lues` ; définition complétée (contrefactuel 5 µg/m³) ; motif chiffré (61 en 2005, 22 en 2023) ; `raccordement: a_etudier : chute de 53 à 34 décès pour 100 000 de 2013 à 2014 (−36 %), sans drapeau ni explication dans les métadonnées` ; `qualite` : ajouter `pas_de_valeur_2006`, `saut_2014_non_signale`. Le rattachement à `sante` (résultat de santé ; l'exposition reste en `logement_cadre_vie`, les émissions en `planete`) est cohérent avec R2 : la session mère le confirme au gel 2 (I3).

## 5. Espérance de vie à 65 ans (A, J1)

`esperance_vie_65` porte `incontournable: oui` alors qu'elle n'est pas variante principale : D38 (d) le réserve à la principale (même correction pour `esperance_vie_sans_incapacite_65`, `limitations_activite_fortes`, `sante_percue_mauvaise`).

Sur le fond (J1) : la série principale de la fiche est la modalité LE_Y65 du jeu des années de vie en bonne santé (`hlth_hlye`, 2004-2024). Le jeu démographique d'Eurostat, qui porte la fiche principale de la famille (`demo_mlexpec`), publie aussi l'espérance de vie à 65 ans (`age=Y65`) **de 1998 à 2024**, avec les mêmes drapeaux que la naissance (`b` 2012 et 2014, `p` 2023-2024). Les deux séries sont **identiques de 2004 à 2013**, puis divergent : 21,5 contre 22,0 (2014), 21,7 contre 22,0 (2019), 21,0 contre 21,2 (2020), 21,2 contre 21,3 (2022), 21,9 dans les deux cas en 2024. La méthode (§4 : même source que la principale, série la plus longue) désigne `demo_mlexpec` Y65 ; l'argument contraire est la cohérence avec les années de vie en bonne santé à 65 ans, calculées sur LE_Y65 de `hlth_hlye`. **Proposition** : principale = `demo_mlexpec?freq=A&unit=YR&sex=T&age=Y65&geo=FR` (jeu au catalogue des jeux, modalité à cataloguer : O6), `hlth_hlye` LE_Y65 en variante avec la divergence de 2014 notée ; à défaut, garder `hlth_hlye` et documenter l'écart.

## 6. Santé mentale et Baromètre de Santé publique France (F, O)

- **Champ** : la page de Santé publique France sur le Baromètre santé 2021 indique « 12,5 % des personnes âgées de 18-85 ans » et, pour la comparaison avec 2017, **13,3 % des 18-75 ans en 2021 contre 9,8 % en 2017**, « en France métropolitaine ». La valeur de la fiche (13,2688 %) est donc celle des 18-75 ans en métropole : `geo: FM`, `qualite` `enquete_metropole` (au lieu de `enquete_metropole_a_verifier`), définition « 18-75 ans résidant en France métropolitaine ». Même enquête, même champ pour `pensees_suicidaires`.
- **Vague 2024 (O3)** : la synthèse de Santé publique France (édition 2024 du Baromètre) donne **15,6 % des 18-79 ans** ayant vécu un épisode dépressif caractérisé, avec des résultats régionaux incluant La Réunion. Le catalogue Odissé exporté par le robot le 13/10 (`docs/sources/series/spf_odisse__catalogue_champs.csv`) contient `episodes-depressif-indicateurs-du-barometre-2024` (104 enregistrements), `conduites-sucidaires-indicateurs-du-barometre-2024` (231) et `tabagisme-indicateurs-du-barometre-2024` (194). Ces jeux d'une seule édition prolongent les trois séries de M05 jusqu'en 2024, au prix d'une rupture (âges 18-79, protocole et champ différents) : `derniere_annee: 2024`, `raccordement: a_etudier : édition 2024 (18-79 ans, nouveau protocole, DROM inclus) non comparable aux vagues 2005-2021`. Pour le tabac, la valeur 2024 de l'INSEE (18,2 %, ODD 3.i8) en est vraisemblablement la copie.
- **Incontournable (J2)** : le §5 du crosswalk ne liste pas la santé mentale, mais `30_indicateurs_cadres_reference.csv` la donne dans trois cadres (SSF « Santé mentale » ; OCDE 5_3 et 5_4 ; Eurostat Qualité de vie « Santé mentale déclarée »). Si la session mère applique la règle des trois cadres au CSV, `episodes_depressifs` (principale de `sante_mentale`) et `suicide` deviennent `incontournable: oui`.

## 7. Autres erreurs factuelles et remarques (détail)

1. **F1 — `obesite`** : `sdg_02_10` n'a que 2008, 2014, 2017, 2019, 2022 et 2025 ; `frequence: irreguliere` (D17) dans la fiche et le tableau (« 6 points, annuelle »). L'attribution des vagues 2017 et 2022 aux modules d'EU-SILC reste à vérifier, comme la note le dit.
2. **F2 — `vaccination_hpv`** : la page de Santé publique France « Données de couverture vaccinale HPV par groupe d'âge » (mise à jour le 25/04/2025, données au 31/12/2023, SNIIRAM-DCIR) donne 44,7 % de schéma complet à 16 ans pour les filles nées en 2007, valeur arrondie à 45 par l'OMS et l'OCDE pour 2023. Attendu : définition « part des filles de 16 ans ayant reçu un schéma vaccinal complet », retrait de `population_cible_a_verifier`. Voir J3 pour la source principale.
3. **F3 — `episodes_depressifs`, `pensees_suicidaires`** : §6.
4. **F4 — `deces_pollution_air`** : §4.
5. **Remarques mineures (fiches conformes)** : `densite_medecins_generalistes` (146 en 2025 après 145 en 2024 : pas de « baisse continue ») ; `mortalite_traitable` (59,39 en 2022 après 58,82 en 2021 : pas de baisse « continue ») ; `decouvertes_vih` (statut `E` de toutes les valeurs BDM, à porter dans `qualite`) ; `esperance_vie_naissance` (l'inclusion de Mayotte en 2014 est attestée par les titres des séries BDM 001686956 et 001641594, pour l'INSEE) ; `natalite_adolescentes` (PNUD 3,5 ‰ en 2023 contre OCDE 6,36 ‰ en 2021 : écart d'estimation à signaler) ; fiches EU-SILC (`geo: FR`, code Eurostat) : l'indicateur national ODD 3.i7a, de mêmes valeurs que `hlth_silc_08` de 2010 à 2023, est publié par l'INSEE en `FM` ; le champ réel de SRCV mériterait une phrase dans les notes (D15), comme dans les autres dimensions qui utilisent EU-SILC.

## 8. Désaccords de jugement

- **J1. Espérance de vie à 65 ans** : §5.
- **J2. Santé mentale incontournable** : §6.
- **J3. Vaccination HPV : source nationale.** Santé publique France publie la série nationale (jeu `couvertures-vaccinales-des-adolescents-et-adultes-depuis-2011-france`, 15 enregistrements depuis 2011, mis à jour le 08/10/2026 : `hpv1_f`, `hpv2_f`, `hpv1_g`, `hpv2_g`, `grip_65plus`…), producteur de la donnée que l'OMS reprend. À définition égale, la méthode (§4 : fraîcheur, profondeur) et la lisibilité (filles et garçons) plaident pour la série SPF en principale (`hpv2_f`), l'OCDE en variante. Valeurs non lues (API Odissé refusée par robots.txt) : ligne de maintenance d'abord.
- **J4. Fiches hors du contenu cité** (`consommation_antibiotiques`, `natalite_adolescentes`) : M05 les soumet à Léo ; l'audit n'y voit pas d'obstacle de principe (comportements de soins ; santé reproductive, cible ODD 3.7), mais suggère de chercher pour la natalité des adolescentes une source d'état civil (taux de fécondité des 15-19 ans) plutôt que deux estimations internationales divergentes.
- **J5. Drapeau `declaratif` de l'indicateur GALI** : `oui` en `sante` (limitations, années de vie en bonne santé : « self-perceived » chez Eurostat), `non` pour `egalites/ecart_emploi_handicap`, fondé sur la même question. À harmoniser ; l'audit suit `sante` (limitation perçue).
- **J6. Maladie chronique, sens `bas`** : la fiche reconnaît que la hausse (36,7 → 41,7 %) tient aussi au vieillissement et au diagnostic, sans standardisation par âge ; le sens reste défendable (indicateur de morbidité des cadres SSF, OCDE, Eurostat), mais Léo doit le savoir pour les bornes.
- **J7. Reste à charge, type** : `moyen` (D19) ; la part des paiements directs mesure plutôt la protection financière des ménages (résultat du système d'assurance). Sans effet sur la recommandation.
- **J8. Couverture sanitaire universelle dans la famille des besoins non satisfaits** : un indice composite de couverture des services essentiels n'est pas vraiment substituable à une mesure déclarée d'accès ; la fiche resterait `retenir_variante` si elle formait sa propre famille… ce qui n'est pas permis par la méthode (une principale ne peut pas être `retenir_variante`). L'audit accepte le choix de M05.

## 9. Complétude et cohérence inter-dimensions

**Long-list** : les 14 168 lignes et les 20 lignes importées de `logement_cadre_vie` sont affectées (vérificateur). Les 21 groupes écartés en bloc ont été relus : activité hospitalière (8 184 lignes, mesures d'activité), causes de décès en nombre, en taux brut ou en moyennes triennales régionales, causes détaillées (D35), dépenses et ressources de santé (moyens budgétaires, charte §3.4), recours aux soins (sens ambigu), catégories détaillées de la santé perçue. **Aucune exclusion abusive repérée.**

**Contenu de `dimensions.yaml`** (sous-thèmes des fiches) : espérance de vie (4), mortalité (6), causes de décès (6) et maladies infectieuses (1) ; santé perçue, maladie chronique et limitations (6) ; santé mentale (4) ; accès aux soins (7) ; comportements et prévention, dont tabac, alcool et corpulence (8) ; périnatalité (4) ; perceptions (3) : tous les thèmes sont couverts. Manquent, faute de série annuelle, l'activité physique et la consommation de fruits et légumes (EHIS 2014 et 2019, Baromètre 2024 seul) : absence justifiée.

**Crosswalk** : espérance de vie, santé perçue, morbidité et limitations, années de vie en bonne santé : fiches `retenir`, incontournables à juste titre (à reporter sur les seules principales, D38 d) ; mortalité des moins de 5 ans (variante OCDE 3.2.1 de la mortalité infantile), couverture sanitaire universelle, mortalité maternelle, mortalité prématurée par maladies non transmissibles (cible ODD 3.4), besoins non satisfaits, tabac, obésité, alcool (ventes ; l'alcool à risque n'existe qu'en vagues EHIS), dépression, morts de désespoir, douleur, mortalité prématurée : tous présents. Santé mentale : voir J2.

**Oublis** :

| # | Oubli | Données (lues) | Importance | Proposition |
|---|---|---|---|---|
| O1 | **Prévalence du diabète traité** | Catalogue Odissé du robot : `diabete-prevalence-france` (« Diabète : Prévalence (France) », 42 enregistrements, champs `annee`, `sexe`, `diabete_tx_std`, `diabete_tx_brut`, mis à jour le 01/04/2026) ; valeurs non lues (robots.txt) | forte : maladie chronique liée à la nutrition et à la corpulence (A2), que SAN-7 déclare « non trouvée » à tort | Ligne de maintenance (catalogage, taux standardisé ensemble) ; puis fiche `prevalence_diabete` (famille propre ; sens à discuter : la prévalence traitée dépend aussi du dépistage) ; corriger SAN-7. |
| O2 | **Couvertures vaccinales nationales adolescents et adultes** (HPV filles et garçons, grippe des 65 ans ou plus, rappels) | `couvertures-vaccinales-des-adolescents-et-adultes-depuis-2011-france` (15 enregistrements, 08/10/2026) | moyenne | Principale de `vaccination_hpv` (J3), variante SPF de `vaccination_grippe_seniors` ; corriger SAN-7 (« HPV par cohorte : à rechercher »). |
| O3 | **Édition 2024 du Baromètre de Santé publique France** (dépression, conduites suicidaires, tabac) | 3 jeux Odissé listés au §6 ; 15,6 % d'épisodes dépressifs chez les 18-79 ans (synthèse SPF) | moyenne : seule mise à jour possible de la santé mentale déclarée (dernière vague 2021) | Ajouter le point 2024 avec raccordement `a_etudier` (§6) ; ligne de maintenance. |
| O4 | **Participation au dépistage organisé du cancer colorectal (SPF)** | `cancer-participation-au-depistage-organise-du-cancer-du-colon-rectum-france-copie` (39 enregistrements, couverture 2010-2025, taux standardisés de participation) | faible | Variante nationale de `depistage_cancer_colorectal`, ou principale si elle comble 2015-2016 sans rupture. |
| O5 | **Décès attribuables à la chaleur** | `canicules-deces-attribuables-a-la-chaleur-pendant-lete-et-pendant-les-vagues-de-chaleur-france` (24 enregistrements) et `canicules-exces-de-deces-pendant-les-vagues-de-chaleur-france` (18) ; M05 les croyait en PDF seulement | moyenne | Rattachement à trancher : `planete` (A14, à côté de `jours_canicule`) ou `sante` (par symétrie avec `deces_pollution_air`). |
| O6 | **Espérance de vie à 65 ans `demo_mlexpec`** | API, 1998-2024 ; seules les modalités Y_LT1, Y_GE85 et Y_GE95 sont au catalogue | moyenne (J1) | Maintenance M02 : cataloguer `age=Y65`. |
| O7 | **Confiance dans ce que disent les médecins** (DREES SA13) | signalée par M05, reprise nulle part | faible | Signaler à `democratie` (R5) ou écarter explicitement. |

**Cohérence inter-dimensions** — contrôle mécanique des séries principales, composantes, variantes et lignes de présélection des 49 fiches contre toutes les autres fiches : aucun identifiant ni aucune série en commun.

| # | Point | Proposition |
|---|---|---|
| I1 | 104 lignes `hsw_*` (santé au travail) envoyées à `travail` (`sante_travail`), rattachement confirmé par D39, **reprises nulle part** | Correction `travail` (D38 a ; O1 et I4 de l'audit `travail`). |
| I2 | 12 lignes `hlth_dm070`, `hlth_dm080`, `hlth_dm100`, `hlth_dm110` (privations par niveau de limitation) envoyées à `niveau_de_vie`, **reprises nulle part** (`niveau_de_vie` reprend `hlth_dm030` depuis `planete`) | Correction `niveau_de_vie` : variantes ou écart en bloc motivé (D38 a). |
| I3 | `deces_pollution_air` (`sante`) / `exposition_pm25`, `population_exposee_pm25` (`logement_cadre_vie`) / `emissions_particules_fines` (`planete`) : même chaîne causale, séries distinctes | Conforme à R2 ; confirmer au gel 2 et au contrôle de redondance. |
| I4 | `satisfaction_soins_hopital` (DREES SA07_1) / `democratie/confiance_hopital` (INSEE, ODD 16.i4) | Questions distinctes (satisfaction, R4 ; confiance, R5) : contrôle de redondance seulement. |
| I5 | 54 lignes de causes de décès (homicides, transports) envoyées à `securite` | Toutes reprises (`tues_route`, `homicides`) ; la mortalité infantile par accident de transport reste en `sante` (SEC-1) : conforme. |
| I6 | 10 lignes envoyées à `egalites` | Toutes reprises par les écarts construits : conforme. `egalites/inegalite_esperance_vie` (dispersion) ne double pas `esperance_vie_naissance` (niveau). |
| I7 | 20 lignes `ilc_lvhl01` reçues de `logement_cadre_vie` ; 1 ligne (ODD 7.i1) envoyée à `logement_cadre_vie` | Importées dans les deux sens : conforme à D38 (a) et D39. |
| I8 | Drapeau `declaratif` du GALI | J5. |
| I9 | `niveau_de_vie/indice_developpement_humain` inclut l'espérance de vie | Composite multidimensionnel au plus `retenir_variante` (D38 c) : rien à faire en `sante`. |

## 10. Liste ordonnée des corrections (à faire par l'agent correcteur ou la session mère)

1. **D39, satisfaction DREES** (§3) : recalculer `satisfaction_soins_hopital`, `satisfaction_urgences` et leurs variantes SA07_5 et SA07_3 hors modalité 6, formule, définition, motif, `rupture_2014`, `non_recoupe`.
2. **`deces_pollution_air`** (§4) : valeurs lues, contrefactuel 5 µg/m³, saut 2013-2014 en `raccordement: a_etudier`, 2006 absent.
3. **Oublis SPF** (O1, O2, O3) : lignes de maintenance pour `diabete-prevalence-france`, `couvertures-vaccinales-des-adolescents-et-adultes-depuis-2011-france` et les trois jeux du Baromètre 2024 ; corriger SAN-7 ; fiche `prevalence_diabete` une fois la série lue ; point 2024 et raccordement pour `episodes_depressifs`, `pensees_suicidaires`, `tabagisme_quotidien`.
4. **Champs et fréquences** : `geo: FM` et définitions de `episodes_depressifs` et `pensees_suicidaires` (§6) ; `frequence: irreguliere` pour `obesite` (F1) ; définition de `vaccination_hpv` (F2).
5. **D38 (d)** : `incontournable: non` pour `esperance_vie_65`, `esperance_vie_sans_incapacite_65`, `limitations_activite_fortes`, `sante_percue_mauvaise`.
6. **Espérance de vie à 65 ans** (J1, O6) : décision de la session mère, puis principale `demo_mlexpec` Y65 (ou divergence documentée).
7. **D38 (b) et D39** : `non_recoupe` pour `sante_francais_percue_degradee` et `manque_medecins_percu` ; note de rattachement de `mortalite_chutes` citant D39 ; SAN-4 : `ilc_lvhl01` réglé par D39.
8. **Lignes orphelines** (I1, I2) : à reprendre par `travail` (104) et `niveau_de_vie` (12) ; O5 (chaleur) et O7 (SA13) à trancher.
9. **Mineurs** : O4 (dépistage SPF) ; remarques du §7.5 ; J2, J3, J5 selon les décisions.
10. Puis `python scripts/preselection.py --dimension sante --maj-fiches`, `python scripts/verifier_fiches.py --dimension sante --tableau` et `python scripts/verifier_fiches.py --dimension sante` (0 erreur).

## 11. Questions pour la session mère

1. **Espérance de vie à 65 ans** : `demo_mlexpec` (1998-2024, même source que la principale) ou `hlth_hlye` (cohérente avec les années de vie en bonne santé à 65 ans) ? Les deux séries s'écartent de 0,1 à 0,5 an depuis 2014.
2. **Santé mentale incontournable ?** Trois cadres dans `30_indicateurs_cadres_reference.csv`, absente du §5 de la synthèse.
3. **Baromètre de Santé publique France 2024** : prolonger les séries 2005-2021 (dépression, pensées suicidaires) et 2000-2023 (tabac) par un point 2024 non comparable, avec raccordement `a_etudier`, ou ouvrir de nouvelles séries ?
4. **Décès attribuables à la chaleur** : `planete` (A14) ou `sante` (comme les décès attribuables aux PM2,5) ?
5. **Indicateur GALI** : `declaratif` oui ou non, dans toutes les dimensions ?
6. **Prévalence du diabète traité** : fiche `retenir` avec sens `bas` malgré l'effet du dépistage, ou `retenir_variante` ?

## Annexe — sources consultées (16/10/2026)

| Source | Usage |
|---|---|
| API Eurostat (`…/statistics/1.0/data/<code>?…&geo=FR&lang=fr`) : `demo_mlexpec` (Y_LT1, Y65), `hlth_hlye` (LE_Y65, HLY_Y0, HLY_Y65), `sdg_03_20`, `hlth_silc_10`, `hlth_silc_04`, `hlth_silc_19`, `hlth_silc_06` (SM_SEV, SEV), `sdg_03_60`, `hlth_silc_09`, `hlth_silc_08`, `sdg_03_42` (TOTAL, PRVT, TRT), `hlth_cd_asdr2` (C, I, J, W00-W19, E10-E14), `sdg_11_52`, `sdg_03_41`, `sdg_03_70`, `hlth_ps_immu`, `hlth_ps_prev`, `hlth_sha11_hf`, `sdg_02_10` | valeurs, drapeaux, libellés |
| `https://ec.europa.eu/eurostat/cache/metadata/en/sdg_11_52_esmsip2.htm` | méthode des décès attribuables aux PM2,5 (5 µg/m³, 2006 absent) |
| BDM INSEE (`bdm.insee.fr/series/sdmx/data/SERIES_BDM/<idbank>`) : 001641594, 001744911, 010599567, 010593272, 010761075, 010593299, 010593303 | titres, zones, unités, valeurs, statuts |
| `https://www.santepubliquefrance.fr/sante-mentale/depression-et-anxiete/article/prevalence-des-episodes-depressifs-en-france-chez-les-18-85-ans-resultats-du-barometre-sante-2021` | 13,3 % des 18-75 ans en 2021 (9,8 % en 2017), France métropolitaine |
| `https://www.santepubliquefrance.fr/sante-mentale/depression-et-anxiete/rapportsynthese/episodes-depressifs-prevalence-et-recours-aux-soins-barometre-de-sante-publique-france-resultats-de` | 15,6 % des 18-79 ans en 2024 |
| `https://www.santepubliquefrance.fr/vaccination-1/donnees-de-couverture-vaccinale-papillomavirus-humains-hpv-par-groupe-dage` | HPV : 44,7 % des filles nées en 2007, schéma complet à 16 ans |
| Recherches web : Baromètre santé 2021 et 2024 (dépression), couverture vaccinale HPV | pages SPF ci-dessus |
| Extraits du robot (dépôt) : `ocde__odd_3.csv`, `ocde__hsl_bien_etre_actuel.csv`, `pnud__hdr25_series_composites_france.csv`, `spf_odisse__*.csv` (dépression, pensées suicidaires, mortinatalité, prématurité, vaccinations, tabac, suicides, chutes), `spf_odisse__catalogue_champs.csv`, `drees__barometre_2000_2025_distributions.csv`, `drees__barometre_dico_*_2025.txt` | valeurs, couvertures, jeux disponibles, recalculs |
| **Non lus** : API Odissé de Santé publique France (`…/records`, robots.txt et autorisation refusée) : valeurs de `diabete-prevalence-france`, des couvertures adolescents-adultes, du Baromètre 2024 et du dépistage colorectal | — |
