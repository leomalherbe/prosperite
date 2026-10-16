# Audit croisé M06 — dimension `logement_cadre_vie`

Agent auditeur M06 (session neuve, Opus, n'ayant pas participé à M05 `logement_cadre_vie`), 16 octobre 2026. Branche `m06-logement_cadre_vie`, créée depuis `origin/main` au commit `d85ef3a` (fiches fusionnées par la PR #26, puis journal D37 à D40). Matériau audité : les 44 fiches `indicateurs/logement_cadre_vie/*.yaml`, `docs/validation/validation_logement_cadre_vie.csv`, `preselection_logement_cadre_vie.csv`, `preselection_logement_cadre_vie_lignes.csv`, `regles_preselection_logement_cadre_vie.csv`, le journal et le compte rendu M05, les lignes LOG-1 à LOG-11 de `docs/cr/maintenance_catalogues.md`, la long-list `catalogues/longlist_logement_cadre_vie.csv.gz` et les neuf autres, les présélections des neuf autres dimensions, les catalogues INSEE et Eurostat, le crosswalk (`30_indicateurs_cadres_reference.csv`, `30_crosswalk_synthese.md` §5) et les sorties du robot M04 (`docs/sources/series/`, `docs/sources/verif_acces/extraits/`). **Aucune fiche, aucune règle, aucun tableau, aucun script ni aucun catalogue n'a été modifié** : ce rapport propose, l'agent correcteur (ou la session mère) corrige. Déroulé : `docs/cr/M06_logement_cadre_vie_journal.md`.

Contrôle préalable : `python -m pytest -q` → 399 réussis ; `python scripts/verifier_fiches.py --dimension logement_cadre_vie` (sans `--tableau`) → **0 erreur**, 3 avertissements attendus (séries principales hors catalogue des trois fiches hors long-list, avec preuve du robot) ; 44 fiches, 33 familles, 30 `retenir`, 10 `retenir_variante`, 4 `ecarter`, 5 déclaratives, 0 composite, 1 « à vérifier », 3 hors long-list, 16 incontournables, 497 variantes, 146 lignes `autre_dimension`, 0 ligne prise ailleurs.

Nature des constats : **F** = erreur factuelle (source et valeur attendue citées) ; **A** = alignement sur une décision postérieure à M05 (D38, D39) ou sur la méthode, sans faute de M05 ; **C** = complément : réserve déclarée par M05 (valeurs ou drapeaux non lus) levée par l'audit ; **J** = désaccord de jugement (à trancher par la session mère ou Léo) ; **O** = oubli ; **I** = cohérence entre dimensions.

## 0. Avis global : `corrections_necessaires`

Le travail de M05 est solide et honnête sur ses limites. Les thèmes de `dimensions.yaml` ont presque tous une fiche :
- coût du logement : surcharge, taux d'effort, poids dans le revenu, charge ressentie, prix rapportés au revenu, loyers, logement social ;
- qualité du logement : surpeuplement, humidité, sanitaires, éclairement, privation sévère ;
- précarité énergétique, air (quatre polluants), bruit, pollution du quartier, eau du robinet ;
- transports, numérique (accès, haut débit, usage, privation, fibre, administration en ligne), services financiers ;
- sans-abrisme, par une mesure indirecte.

Manquent seulement les espaces verts et l'accès aux services publics de proximité, faute de série éligible (§7). Les arbitrages A3, A7, A14, D33 et la part modale des voyageurs (D39) sont respectés. Les items EU-SILC devenus triennaux sont déjà en `frequence: irreguliere` (anticipation de D38 e). **Toutes les valeurs relues à la source concordent avec les fiches** : 23 jeux Eurostat, 17 séries BDM, le fichier ITDD du SDES, les extraits du robot. Les deux anomalies signalées par M05 sont confirmées : part modale aberrante en 2010-2012, IPCH des loyers arrêté.

Cinq groupes de problèmes doivent être réglés avant la validation de Léo :

1. **Assainissement (A, D39)** : D39 range l'assainissement et le raccordement aux eaux usées dans `planete`. Les deux fiches `conformite_assainissement_collectif` et `raccordement_traitement_eaux_usees` et leurs lignes doivent repartir vers `planete`, qui n'a aujourd'hui aucune fiche de ce concept. Le motif d'écart de `raccordement_traitement_eaux_usees` est par ailleurs fragile : le libellé Eurostat de `WWT_GE2` inclut les traitements « individuels (autonomes) » (§3.1).
2. **Lignes orphelines (A, D38 a ; O1)** : `education` renvoie 28 lignes vers cette dimension (règle 120 `acces_numerique_cadre_vie`), qu'aucune règle de `logement_cadre_vie` ne reprend. Parmi elles, `ilc_mddu03` (personnes n'ayant pas les moyens de posséder un ordinateur) est éligible : 2004-2025, 22 points, 10,5 % en 2004, 3,5 % en 2025. En sens inverse, `education` écarte en bloc (règle 1010) les deux lignes IPCH des loyers, qui sont pourtant la série principale et une variante de `hausse_loyers` (I2).
3. **Incontournables (A, D38 d ; J1)** : sept fiches non principales portent `incontournable: oui` alors que D38 d le réserve à la variante principale. Au niveau des familles, cinq familles sur neuf relèvent de la « pollution de l'air locale ». Avec la règle par défaut du classeur (D37 : `retenir` + principale + incontournable → `retenu_socle`), le socle de la dimension serait composé de :
   - cinq indicateurs d'air sur neuf ;
   - aucun indicateur de coût, de précarité énergétique, de numérique ni de transport.
   Le dioxyde d'azote et l'ozone ne figurent dans aucun cadre de référence (§5).
4. **Séries calculées par le projet (A, D34, D38 b)** : `preoccupation_logement` et `connaissance_personne_sdf` sont `retenir` sans `composantes`, sans `formule` et sans `non_recoupe`. L'audit fournit le recoupement 2025 de la première : 55,35 % publiés par la DREES pour 55,36 % calculés. La seconde n'a encore aucune valeur et son sens est douteux (J3).
5. **Erreurs factuelles sur des variantes et choix de série** :
   - Les séries INSEE « eau distribuée non conforme » ne sont pas le complément des taux de conformité ITDD (F). En microbiologie, l'INSEE donne 0,5 % de non-conformité en 2010, quand le taux ITDD de 98,2 % en implique 1,8 %.
   - La variante OCDE 3_3 de la surcharge n'est pas « le même indicateur » (F) : elle porte sur les ménages des 40 % les plus modestes, à 10,66 % en 2024 contre 7,0 %.
   - Pour les loyers, l'IPC de l'INSEE (011815635, base 2025, 1996-2025) reproduit au dixième près les taux de l'IPCH arrêté. Il devrait devenir la série principale (A, méthode §4 et D32).

Chiffres : **44 fiches auditées sur 44**, dont **25 `conforme`** (3 avec réserve sur des valeurs Melodi non lues) et **19 `a_corriger`** (3 F, 12 A, 4 C ; 2 J associés). Aucune fiche `non_verifiable`. S'y ajoutent 1 oubli (O1, 28 lignes), 7 points de cohérence inter-dimensions et 7 désaccords de jugement. Liste ordonnée des corrections : §10.

## 1. Échantillon

| Règle (fiche M06 et consigne de la session mère) | Fiches |
|---|---|
| `recommandation: ecarter` (4) | `proprietaires_occupants`, `logements_commences`, `sous_occupation`, `raccordement_traitement_eaux_usees` |
| `incontournable: oui` (16) | `surpeuplement`, `pieces_par_personne`, `logement_humide`, `sans_installations_sanitaires`, `privation_severe_logement`, `logement_inadequat_onu`, `exposition_pm25`, `exposition_pm25_modelisee`, `population_exposee_pm25`, `concentration_pm10`, `depassement_norme_pm10`, `concentration_no2`, `depassement_norme_no2`, `depassement_norme_ozone`, `concentration_ozone`, `pollution_quartier` |
| Signalées au journal M05 (14, hors celles déjà comptées) : éligibilité `a_verifier` (1) ; `raccordement: a_etudier` (3) ; hors long-list (3) ; sens à confirmer (2) ; valeurs non relues (3) ; rattachement à trancher (1) ; périmètre à documenter (1) | `bancarisation` ; `hausse_loyers`, `part_modale_transports_collectifs`, `usage_internet` ; `preoccupation_logement`, `connaissance_personne_sdf`, `duree_trajet_domicile_travail` ; `prix_logements_revenu`, `administration_en_ligne` ; `acces_internet_domicile`, `haut_debit_domicile`, `poids_logement_revenu` ; `conformite_assainissement_collectif` ; `conformite_eau_physicochimique` |
| Tirage : 20 % des 24 « autres » fiches (ni `ecarter` ni incontournables) = 4,8, arrondi à 5, parmi les 10 non retenues d'office | `couverture_fibre`, `incapacite_chauffer`, `nuisances_sonores`, `surcharge_couts_logement`, `taux_effort_logement` |
| Les 5 restantes, vérifiées aussi à la source | `charge_logement_lourde`, `conformite_eau_microbiologique`, `logement_trop_sombre`, `logements_sociaux`, `privation_internet` |

Tirage : `random.Random(20261014).sample(pool, 5)` en Python 3, `pool` = liste triée des 10 fiches non retenues d'office ; **graine 20261014**, la même que pour les audits précédents. **34 fiches d'office + 5 tirées + 5 restantes = 44.**

## 2. Fiches auditées

Sources lues par WebFetch le 16/10/2026 (détail en annexe) ; extraits du robot lus dans le dépôt.

| Fiche | Motif d'inclusion | Source consultée | Verdict | Nature | Constat, correction attendue (détail aux §3 à §8) |
|---|---|---|---|---|---|
| `proprietaires_occupants` | ecarter | BDM 001791247 | conforme | — | 55,7 (2000), 56,9 (2005), 57,7 (2010-2013), 57,5 (2017-2023), 57,4 (2024-2025, `P`), 57,3 (2026, `P`) : exact. Sens ambigu recevable. |
| `logements_commences` | ecarter | BDM 001718270 | conforme | — | Cumul sur douze mois, mensuel, zone `FR-D976`, 263 000 en décembre 2025. Le motif « sans série annuelle publiée » est à nuancer : le cumul de décembre est un total annuel, ce que la note dit déjà. |
| `sous_occupation` | ecarter | API `ilc_lvho50a` | **a_corriger** | C (mineur) | 37,8 (2004) → 44,2 (2013) → 40,4 (2025), 22 points : exact. Ruptures `b` en 2020 et 2022 absentes de `qualite` (vide) : ajouter `rupture_2020`, `rupture_2022`. |
| `raccordement_traitement_eaux_usees` | ecarter | API `sdg_06_20` | **a_corriger** | A, J | Valeurs exactes (77,30 en 2001, 80,00 en 2024, 19 valeurs, aucune de 2005 à 2009, aucun drapeau). D39 : concept → `planete`. Le libellé Eurostat de `WWT_GE2` inclut les traitements « individuels (autonomes) » : le motif d'ambiguïté est à revoir (§3.1, J4). |
| `conformite_assainissement_collectif` | rattachement à trancher | BDM 010595400, 010595405 | **a_corriger** | A | Valeurs exactes (80,0 en 2010 ; 98,6 en 2018 ; 91,9 en 2022 ; non collectif 40,8 → 64,5) ; D39 : fiche et variantes → `planete` (§3.1). |
| `exposition_pm25` | incontournable | extrait du robot et fixture du fichier DiDo d237b4e4 | conforme | — | 17,33 (2009-2011) → 8,89 (2022-2024), 14 périodes triennales, objectifs 14,7 (2020), 11,2 (2025) et 10 (2030) : exact. |
| `exposition_pm25_modelisee` | incontournable | extrait de l'API Banque mondiale | **a_corriger** | A | Valeurs exactes (17,88 en 2000 ; 8,23 en 2023 ; 1995-2023). Non principale : `incontournable: non` (D38 d). |
| `population_exposee_pm25` | incontournable | extrait OCDE How's Life 9_2 | **a_corriger** | A, (J6) | 99,70 % (2020), 2004-2020 : exact ; seuil toujours non lu (PDF de l'OCDE refusé par robots.txt). `incontournable: non` (D38 d). |
| `concentration_no2` | incontournable | extrait SDES (fichier 9db8c875) | conforme | (J1) | 11,97 µg/m³ (2024), 21,86 près du trafic, indice 42,64 : exact. |
| `depassement_norme_no2` | incontournable | extrait SDES (a956734e) | **a_corriger** | A | 1,21 % (2024) et 3,10 % des stations des grandes agglomérations : exact. `incontournable: non` (D38 d). |
| `concentration_pm10` | incontournable | extrait SDES ; BDM 010596141, 010596140 | conforme | — | SDES 13,26 µg/m³ (2024) ; INSEE fond urbain 13,3 (2024, série 2010-2024) et trafic 17,3 : même mesure, choix du SDES (2007) justifié. |
| `depassement_norme_pm10` | incontournable | extrait SDES ; BDM 010596138 | **a_corriger** | A | 1,80 % (2024) : exact. `incontournable: non` (D38 d). |
| `depassement_norme_ozone` | incontournable | extrait SDES | conforme | (J1) | 9,88 % (2024) ; variante triennale 9,39 % (2022-2024) ; indice d'ozone 98,96 : exact. |
| `concentration_ozone` | incontournable | extrait SDES (b10a6294) | **a_corriger** | A | 98,96 (2024), 2000-2024 : exact. `incontournable: non` (D38 d). |
| `pollution_quartier` | incontournable, non relue | API `ilc_mddw02` | **a_corriger** | C | 20,1 (2004), 11,3 (2012), 14,9 (2019), 18,6 (2020, `b`), 16,0 (2023) ; 18 points ; rien en 2021, 2022, 2024 ni 2025. Remplacer `drapeaux_non_lus` par `rupture_2020` et la phrase « valeurs non relues ». |
| `logement_humide` | incontournable | API `ilc_mdho01` | conforme | — | 15,0 (2004), 10,9 (2011), 11,5 (2019), 18,0 (2020, `b`), 21,1 (2023) : exact. |
| `privation_severe_logement` | incontournable | API `ilc_mdho06a` | conforme | — | 3,4 (2004), 2,1 (2013, 2017), 3,8 (2020, `b`), 4,6 (2023) : exact. Le drapeau `valeurs_lues_sur_table_odd` peut être retiré (mineur). |
| `logement_inadequat_onu` | incontournable | extrait OCDE ODD 11 | **a_corriger** | A | 7 % (2024), 13 valeurs distinctes, 2021 absente : exact. `incontournable: non` (D38 d). |
| `sans_installations_sanitaires` | incontournable | API `ilc_mdho05` | conforme | — | Libellé : « ni baignoire ni douche ni toilettes » ; 0,6 (2004) → 0,2 (2019), 0,4 (2020, `b`), 0,7 (2023) : exact. Le drapeau `valeurs_lues_sur_table_odd` peut être retiré (mineur). |
| `surpeuplement` | incontournable | API `ilc_lvho05a` ; BDM 010596142 | conforme | — | 10,3 (2004) → 7,1 (2014) → 10,8 (2025), `b` 2020 et 2022, 22 points ; INSEE : deux points seulement (8,4 en 2013, 8,1 en 2020), ce qui confirme le motif. |
| `pieces_par_personne` | incontournable | API `ilc_lvho03` | **a_corriger** | A | 1,7 à 1,9, `b` 2020 et 2022 : exact. `incontournable: non` (D38 d). |
| `bancarisation` | a_verifier | BDM 010596094 | conforme | (J5) | 97,0 / 96,6 / 94,0 / 99,2 / 99,2 (2011, 2014, 2017, 2021, 2024), France entière : exact ; D28 applicable (écart moyen 3,25 ans). Source primaire toujours non trouvée (métadonnées INSEE 8.i7 : erreur serveur). |
| `hausse_loyers` | a_etudier | API `prc_hicp_aind` ; BDM 011815635 | **a_corriger** | A, (J2) | Valeurs exactes ; l'API confirme « n'est plus actualisé, remplacé par prc_hicp_ainr ». L'IPC INSEE des loyers (base 2025) reproduit les taux de l'IPCH : il devrait devenir la série principale (§4). |
| `part_modale_transports_collectifs` | a_etudier | API `tran_hv_psmod` ; BDM 010751584, 010751585 | conforme | — | 99,1 (2010, `e`), 99,2 (2011, `e`), 99,1 (2012) puis 15,6 (2013, `b`) confirmés ; sommes INSEE 16,7 / 17,0 / 16,2 / 16,1 / 12,2 / 17,3 (2010-2013, 2020, 2024) exactes. Rattachement confirmé par D39. |
| `usage_internet` | a_etudier | API `isoc_ci_ifp_iu` | conforme | — | 46,87 (2006) → 94,98 (2025), 2020 absente, aucun drapeau : exact. |
| `preoccupation_logement` | hors long-list | distributions et tableaux publiés DREES 2025 du robot | **a_corriger** | A | Recalcul exact : 66,23 (2014), 54,01 (2020), 55,36 (2025) ; minimum 53,86 % en 2022. D34 et D38 b : `composantes`, `formule`, `non_recoupe_2014_2024`, recoupement 2025 (§6). |
| `connaissance_personne_sdf` | hors long-list | couverture et dictionnaires DREES 2025 | **a_corriger** | A, J3 | 25 années (2000-2002, 2004-2025), modalités 1 à 8 et NSP : exact ; aucune valeur calculée ; absente des tableaux publiés 2025. `composantes`, `formule`, D38 b ; sens à trancher (§6). |
| `duree_trajet_domicile_travail` | hors long-list | fichier ITDD France entière (DiDo 305ea0e3) | **a_corriger** | C | Valeurs désormais lues : actifs 12, 12, 13 min ; navetteurs 18, 19, 19 min (2011, 2016, 2022) ; distances 7,5, 7,9, 8,4 km et 14,2, 14,6, 14,9 km. Sous-champs : « actifs » et « navetteurs » (§8). |
| `prix_logements_revenu` | sens à confirmer | API `tipsho60` | conforme | — | 70,20 (2000), 112,33 (2007), 95,48 (2024), 25 points, aucun drapeau : exact ; sens « bas » défendable, à soumettre à Léo comme le propose M05. |
| `administration_en_ligne` | sens à confirmer, non relue | catalogue Melodi ; API `isoc_ciegi_ac` (I_IUGOV12) | conforme (réserve) | — | Mesure `EGOV_12MOIS` : « Taux de personnes ayant eu recours aux services de l'administration en ligne dans les 12 mois », `FEHM`, 2009-2025, 16 points. Eurostat « jusqu'en 2021 » confirmé : 48,10 (2008) → 80,66 (2021). Valeurs Melodi non lues. |
| `acces_internet_domicile` | non relue | API `isoc_ci_in_h` | **a_corriger** | C | 23,04 (2002) → 94,43 (2025), 2005 et 2020 absentes, aucun drapeau, 22 points. Retirer `drapeaux_non_lus`, ajouter `annees_manquantes_2005_2020`, citer la série principale plutôt que l'OCDE (88,11 % en 2021). |
| `haut_debit_domicile` | non relue, champ à vérifier | catalogue Melodi ; BDM 010594684 | conforme (réserve) | — | Mesure `HAUT_DEBIT` : « Haut débit fixe ou mobile à domicile », `FEHM`, 2009-2025. L'indicateur ODD de même enquête donne 64,4 (2010) → 89,9 % (2025), 2020 absente ; titre « Part des individus disposant du haut débit à leur domicile » (le champ « individus » est confirmé). Valeurs Melodi non lues. |
| `poids_logement_revenu` | non relue | catalogue Melodi | conforme (réserve) | — | Libellé du catalogue : « Part de la dépense liée au logement dans le revenu disponible brut ; Pourcentage », 1959-2025, statut `P` : conforme à la fiche. Valeurs non lues. |
| `conformite_eau_physicochimique` | périmètre à documenter | ITDD (DiDo) ; BDM 010600312 | **a_corriger** | F, C | ITDD : 98,7 (2008), 98,5 (2023), puis 95,3 (2024), une chute à documenter. La variante INSEE n'est pas le complément du taux ITDD (§5). |
| `couverture_fibre` | tirage | API `isoc_cbt` | conforme | — | 10,5 (2013) → 91,7 (2025), 13 points sans lacune ni drapeau : exact. |
| `incapacite_chauffer` | tirage | API `ilc_mdes01` ; BDM 010596095 | conforme | — | 5,9 (2004) … 6,0 (2021), 10,7 (2022, `b`), 12,1 (2023), 11,5 (2025) : exact ; INSEE 2010-2024, France métropolitaine. |
| `nuisances_sonores` | tirage | API `ilc_mddw01` | conforme | — | Lue directement (et non plus sur la table ODD) : 23,5 (2004), 16,2 (2013), 20,7 (2020, `b`), 21,1 (2023) : exact. Le drapeau `valeurs_lues_sur_table_odd` peut être retiré (mineur). |
| `surcharge_couts_logement` | tirage | API `ilc_lvho07a` ; How's Life 2020 (définitions) ; extrait OCDE | **a_corriger** | F (mineur) | Valeurs exactes (5,4 ; 4,0 ; 7,0 ; 6,4 ; 2021 absente). La variante OCDE 3_3 n'est pas « le même indicateur » (§5). |
| `taux_effort_logement` | tirage | API `ilc_lvho08a` | conforme | — | 12,3 (2004), 13,3 (2006), 11,1 (2020, `b`), 12,2 (2025), 2021 absente : exact. |
| `charge_logement_lourde` | contrôle | API `ilc_mded04` | conforme | — | 20,2 (2004), 29,6 (2013), 23,2 (2019), 26,4 (2020, `b`), 31,4 (2023) : exact. |
| `conformite_eau_microbiologique` | contrôle | ITDD (DiDo) ; BDM 010600314 | **a_corriger** | F, C | ITDD : 99 (2008) … 96,9 (2016) … 97,9 (2024), 9 valeurs distinctes. La variante INSEE n'est pas le complément (§5). |
| `logement_trop_sombre` | contrôle | API `ilc_mdho04` | conforme | — | 9,0 (2004), 6,9 (2017-2018), 9,7 (2020, `b`), 10,6 (2023) : exact. |
| `logements_sociaux` | contrôle | BDM 001779870 | conforme | — | 699 (2012) → 787 (2025), France entière ; l'écart avec l'ITDD (795,1) est déjà signalé en LOG-5. |
| `privation_internet` | contrôle | API `ilc_mddu07a` | conforme | — | 2,7 (2014) → 1,6 (2025), `b` 2020 et 2022, 12 points : exact. |

Contrôles transversaux :
- **Long-list (comparaison mécanique)** : les périodes, les points, les zones, l'éligibilité et l'URL d'API des 41 séries principales issues d'une long-list sont identiques à la long-list.
- **Unicité (D36)** : aucun `serie_id` de variante en double.
- **Types** : `type: moyen` pour le logement social, la fibre et les logements commencés (D19), `resultat` partout ailleurs. Aucune famille ne mêle pression et état (D38 i).
- **Déclaratif** : `oui` pour les cinq jugements et perceptions (charge ressentie, logement trop sombre, bruit, pollution, préoccupation) ; `non` pour les capacités et les faits déclarés (chauffer, internet, connaître une personne SDF). C'est conforme à la méthode §4 et cohérent avec `securite/delinquance_quartier` (même module EU-SILC, `declaratif: oui`).
- **Fréquence** : les sept items du module triennal EU-SILC (2004-2020 puis 2023, confirmé sur l'API pour les sept) sont `irreguliere`, ce qui anticipe D38 e.

## 3. Rattachements tranchés après M05 (D38, D39)

### 3.1 Assainissement → `planete` (A)

D39 : « assainissement et raccordement aux eaux usées → `planete` (le défaut d'équipement sanitaire du logement reste en `logement_cadre_vie`) ». **Correction** :
- passer en `autre_dimension:planete` les groupes `conformite_assainissement_collectif`, `conformite_assainissement_collectif_variantes`, `raccordement_traitement_eaux_usees`, `raccordement_traitement_eaux_usees_variantes` et `conformite_stations_itdd` ;
- les lignes concernées sont `bdm-000767`, `bdm-000768`, `melodi-005726`, `melodi-005727`, `estat-002071`, `estat-041327` et `m04-000315` ;
- supprimer les deux fiches ;
- `planete` les reprend (D38 a), avec les valeurs déjà lues.

`sans_installations_sanitaires` reste ici.

**Point de fond pour `planete` (J4)** : le libellé de la modalité `WWT_GE2` de `sdg_06_20` est « Traitement des eaux usées urbaines, individuelles (autonomes) et autres - avec au moins un traitement secondaire » (API lue le 16/10/2026). Le motif « la part non raccordée relève surtout de l'assainissement non collectif » ne s'appuie sur aucune source, et le champ de l'indicateur inclut en principe les systèmes individuels. Dans `planete`, l'indicateur se lit d'abord comme une pression évitée sur les milieux (sens `haut`). Le sens ambigu n'est pas démontré : la question est à réexaminer avant d'écarter.

### 3.2 Lignes reçues (D38 a)

| Dimension d'origine | Lignes renvoyées vers `logement_cadre_vie` | Reprises | Constat |
|---|---|---|---|
| `democratie` | 38 | 38 | conforme |
| `liens_bien_etre` | 40 | 40 | conforme |
| `niveau_de_vie` | 45 | 45 | conforme |
| `planete` | 11 | 11 | conforme (mais voir §3.1) |
| `sante` | 1 | 1 | conforme (`melodi-005545`, ODD 7.i1) |
| **`education`** | **28** | **0** | **orphelines** : règle 120 `acces_numerique_cadre_vie` (`ilc_mddu03`, `ilc_mddu03a` à `f`, `hlth_dm090`, `isoc_r_broad_h`) ; voir O1 |

`education` a été fusionnée quelques minutes avant `logement_cadre_vie` (PR #22, puis #26) : c'est un alignement, pas une faute de M05.

### 3.3 Part modale (D39)

D39 confirme le choix de M05 : les voyageurs sont ici et le fret est dans `planete`.

## 4. Coût du logement : loyers (A, J2)

L'API confirme que `prc_hicp_aind` « n'est plus actualisé » et qu'il est remplacé par `prc_hicp_ainr`. La série INSEE `011815635` (IPC annuel, base 2025, France, COICOP 04.1, loyers effectivement payés, 1996-2025) est au catalogue des séries écartées par M01 (« indice de prix »). Elle reproduit les taux de l'IPCH :

| Année | IPCH CP041 (taux, %) | IPC INSEE 011815635 (indice) | Taux recalculé (%) |
|---|---|---|---|
| 2000 | −0,1 | 67,38 (1999 : 67,46) | −0,12 |
| 2005 | 3,6 | 75,90 (2004 : 73,26) | 3,60 |
| 2010 | 1,6 | 85,82 (2009 : 84,47) | 1,60 |
| 2018 | −0,3 | 91,36 (2017 : 91,61) | −0,27 |
| 2023 | 2,1 | 95,50 (2022 : 93,51) | 2,13 |
| 2025 | 2,3 | 100,00 (2024 : 97,73) | 2,32 |

**Correction** :
- série principale = 011815635 (niveau 1, INSEE, toujours mise à jour), avec `composantes: ['011815635']` et `formule: 011815635[t] / 011815635[t-1] * 100 - 100` ;
- recoupement D34 fait sur six années (tableau ci-dessus) ;
- `raccordement: non` ; IPCH en variante ;
- réintégration de la série au catalogue INSEE (LOG-6, volet INSEE).

À défaut, si la session mère préfère ne pas recalculer, garder l'IPCH avec `raccordement: a_etudier` (D32), comme l'a fait M05.

**J2 (sens)** : un taux nominal de hausse des loyers dépend de l'inflation générale (−0,3 % en 2018, 3,6 % en 2005). Des bornes fixes pénaliseraient les années de forte inflation sans que la charge relative des locataires ait changé. Proposition : l'écart entre la hausse des loyers et l'inflation d'ensemble (formule simple sur deux séries de l'IPC), ou le maintien du taux nominal avec des bornes indexées.

## 5. Variantes mal qualifiées (F)

1. **Eau du robinet (F1)**. Les séries BDM 010600314 (« Eau distribuée non conforme pour la micro-biologie ») et 010600312 (physico-chimie), en `POURCENT_PRELEVT`, sont décrites comme « complément de la même statistique » que les taux de conformité ITDD. Ce n'est pas le cas :

| Année | ITDD microbiologie (conformité) | 100 − ITDD | INSEE 010600314 (non conforme) | ITDD physico-chimie | 100 − ITDD | INSEE 010600312 |
|---|---|---|---|---|---|---|
| 2010 | 98,2 | 1,8 | 0,5 | 98,2 | 1,8 | 1,1 |
| 2015 | 98,2 | 1,8 | 0,6 | 98,0 | 2,0 | 1,3 |
| 2016 | 96,9 | 3,1 | 1,7 | 97,9 | 2,1 | 1,8 |
| 2021 | 98,5 | 1,5 | 1,5 | 96,7 | 3,3 | 3,3 |
| 2023 | 98,3 | 1,7 | 1,5 | 98,5 | 1,5 | 1,3 |

**Correction** :
- nature des variantes : « autre statistique du contrôle sanitaire (INSEE, ODD 6.1), définition différente à documenter » ;
- notes : signaler le saut de la série INSEE en microbiologie de 2015 à 2016 (0,6 → 1,7) ;
- `qualite` de `conformite_eau_microbiologique` : creux de 2016 (96,9) ;
- `qualite` de `conformite_eau_physicochimique` : chute de 2024 (98,5 → 95,3, `baisse_2024_a_documenter`), dont la cause n'est pas documentée à la source. Hypothèse non vérifiée : extension de la liste des paramètres contrôlés.
2. **Surcharge des coûts (F2)**. La variante OCDE How's Life 3_3 (groupe `surcharge_couts_logement_ocde`, nature « Même indicateur relayé par l'OCDE ») vaut 10,66 % en 2024 (extrait du robot), contre 7,0 % pour `ilc_lvho07a`. D'après How's Life 2020 (chapitre 6, lu le 16/10/2026), l'OCDE mesure « the share of households in the bottom 40% of the income distribution spending more than 40% of their disposable income on housing costs ». Les coûts retenus sont les loyers et les remboursements d'emprunt, sans loyers imputés. L'unité de l'édition 2024 extraite par le robot est « Percentage of population » : la définition de 2024 n'a pas été lue (PDF refusé). **Correction** : nature « autre statistique : ménages (ou personnes) des 40 % les plus modestes ; définition 2024 à confirmer ».

## 6. Séries calculées par le projet : baromètre DREES (A, J3)

- **`preoccupation_logement`** : la somme des modalités 1 et 2 de OG04_1, non-réponses au dénominateur, donne 66,23 % (2014), 62,10 (2015), 59,89 (2018), 54,01 (2020), 53,86 (2022), 56,77 (2023) et 55,36 (2025). Les tableaux croisés simplifiés publiés par la DREES pour 2025 (feuille 5 de `drees__barometre_tc_simplifies_2025.txt`) donnent « S/T Oui » = 55,35 % (beaucoup 19,16 ; assez 36,20). C'est identique au calcul du robot. **Correction (D34, D38 b)** :
  - `composantes` (variable OG04_1, modalités 1 et 2) ;
  - `formule` : part pondérée des modalités 1 + 2 parmi l'ensemble des répondants, NSP compris ;
  - `qualite: non_recoupe_2014_2024`, avec la note du recoupement 2025 ;
  - le motif peut mentionner le minimum de 2022 (53,86 %).
  - C'est la même mise en forme que `securite/risque_pauvrete_ressenti`.
- **`connaissance_personne_sdf`** : la couverture (25 années) et les modalités (1 « non », 2 à 8 « oui » sous diverses formes, NSP) sont exactes. Aucune valeur n'est calculée, et la question n'est pas dans les tableaux publiés de 2025 : aucun recoupement n'est possible. **Correction (D34, D38 b)** : `composantes` et `formule` (modalités 2 à 8), `non_recoupe`, et une recommandation qui ne devient `retenir` qu'après le calcul (LOG-1) et un contrôle de plausibilité documenté. **J3** : voir §9.

## 7. Incontournables (A, J1)

**A (D38 d)** : l'incontournable « se porte sur la variante principale seulement ». Sept fiches non principales sont à passer en `incontournable: non` : `pieces_par_personne`, `logement_inadequat_onu`, `exposition_pm25_modelisee`, `population_exposee_pm25`, `depassement_norme_pm10`, `depassement_norme_no2`, `concentration_ozone`.

**J1 (familles)** : le §5 du crosswalk retient deux concepts pour cette dimension.
- « Surpeuplement et qualité du logement » : M05 en fait 4 familles (surpeuplement, humidité, sanitaires, privation sévère), ce qui correspond aux indicateurs nommés par SSF, l'OCDE, le cadre Qualité de vie d'Eurostat et le Doughnut.
- « Pollution de l'air locale » : M05 en fait 5 familles, alors que les cadres ne nomment que :
  - les particules PM2,5 (OCDE 9_2, ODD de l'UE) ;
  - les particules PM10 et PM2,5 (indicateur phare du cadre Qualité de vie d'Eurostat) ;
  - la pollution déclarée autour du logement (Eurostat 8.1, SSF).

  Le dioxyde d'azote et l'ozone n'y figurent pas.

**Proposition** : `incontournable: non` pour les familles `concentration_no2` et `depassement_norme_ozone`, qui restent `retenir`. L'incontournable est conservé pour `exposition_pm25`, `concentration_pm10` et `pollution_quartier`.

Conséquence pour le classeur (règle par défaut de D37) : le socle passe de 9 à 7 indicateurs. Il ne contient alors toujours aucun indicateur de coût, de précarité énergétique, de numérique ni de transport (question 1, §11).

## 8. Compléments levés par l'audit (C)

- **`pollution_quartier`** : valeurs et drapeaux lus (§2). `qualite` : remplacer `drapeaux_non_lus` par `rupture_2020`. Note : remplacer « valeurs non relues » par les valeurs.
- **`acces_internet_domicile`** : valeurs lues, aucun drapeau, 2005 et 2020 absentes. `qualite` : retirer `drapeaux_non_lus`, ajouter `annees_manquantes_2005_2020`. Note : citer 94,4 % (2024-2025, Eurostat) plutôt que l'OCDE (88,11 % en 2021).
- **`duree_trajet_domicile_travail`** : le fichier DiDo ITDD (lu le 16/10/2026 ; la lecture avait été refusée à M05) donne les valeurs suivantes.

| Variable | Sous-champ | 2011 | 2016 | 2022 |
|---|---|---|---|---|
| `med_dist_min_hp` (min) | actifs | 12 | 12 | 13 |
| `med_dist_min_hp` (min) | navetteurs | 18 | 19 | 19 |
| `med_dist_km` (km) | actifs | 7,5 | 7,9 | 8,4 |
| `med_dist_km` (km) | navetteurs | 14,2 | 14,6 | 14,9 |

  `LIBELLE_SOUS_CHAMP` = « actifs » et « navetteurs ». **Correction** :
  - remplacer « non trouvé » par ces valeurs ;
  - retirer `sous_champs_a_verifier` ;
  - garder `methode_a_verifier`, puisque le suffixe `hp` désigne une durée à l'heure de pointe, probablement estimée par distancier (non vérifié).
- **`sous_occupation`** : ruptures de 2020 et 2022 (§2).
- **Drapeau cosmétique** : `valeurs_lues_sur_table_odd` peut être retiré de `nuisances_sonores`, `sans_installations_sanitaires` et `privation_severe_logement`, puisque les jeux primaires ont été lus et concordent.
- **Séries Melodi non lues** (`administration_en_ligne`, `haut_debit_domicile`, `poids_logement_revenu`) : comme pour `travail` (D40), une collecte ciblée du robot avant le gel 2. Valeurs de contrôle :
  - BDM 010594684 : 89,9 % en 2025 ;
  - Eurostat I_IUGOV12 : 80,66 % en 2021 ;
  - OCDE 3_2 : 79,84 % du revenu ajusté restant après le logement en 2024.

## 9. Désaccords de jugement

- **J1. Incontournables de l'air** : §7.
- **J2. Loyers en nominal** : §4.
- **J3. Personnes connaissant une personne SDF : sens.** La part des personnes qui connaissent une personne SDF dépend aussi de la taille des réseaux, de la visibilité du phénomène et de l'évolution des modalités (« vous-même » à vérifier). M05 le reconnaît et laisse le sens « à confirmer ». Selon la méthode (§3, §4), un sens ambigu entraîne `ecarter`.

  L'audit propose de ne pas la `retenir` avant le calcul et le contrôle de plausibilité (D38 b), et de demander à Léo s'il accepte ce proxy faute de mieux. Le contenu « sans-abrisme » resterait sinon sans indicateur ; LOG-11 suit la recherche d'une source DIHAL, SI-SIAO ou ES-DS.
- **J4. Raccordement aux eaux usées** : §3.1. À réexaminer dans `planete`, sens `haut` probable.
- **J5. Bancarisation** : M05 accepte le renvoi de `niveau_de_vie` au titre de l'« accès aux services ». L'auditeur ne s'y oppose pas, mais ce rattachement n'est pas tranché au journal. Il touche aussi `niveau_de_vie` (inclusion financière) et `securite` (sécurité économique) : à acter.
- **J6. Population exposée aux PM2,5 (OCDE 9_2)** :
  - la série s'arrête en 2020 dans l'édition consultée ;
  - elle vaut 99,70 % et ne distingue presque plus les années ;
  - son seuil n'est pas documenté (PDF de l'OCDE refusé par robots.txt) ;
  - la famille a déjà une principale et une variante longue.

  `ecarter` (D32 : série arrêtée, relais présent dans la famille) serait plus simple que `retenir_variante`.
- **J7. Logements commencés, `type: moyen`** : la construction neuve est une activité, pas un moyen budgétaire au sens de D19. Le point est sans effet puisque la fiche est écartée pour sens ambigu, mais le type devrait plutôt être `resultat`.

## 10. Complétude

**Long-list** : les 1 527 lignes et les 137 lignes importées sont toutes affectées (vérificateur). Les 27 groupes écartés en bloc ont été relus par groupe, y compris les lignes éligibles une à une pour les groupes de structure du parc, d'usages en ligne, de population, de montants et de couverture par technologie. Les motifs sont recevables :
- ventilations de second rang (D35), structure du parc, montants nominaux ;
- moyens budgétaires (charte §3.4), comptes nationaux (A5) ;
- usages en ligne sans sens normatif, technologies arrêtées.

Aucune exclusion abusive n'a été repérée.

**Crosswalk** (`30_indicateurs_cadres_reference.csv`, 37 lignes rattachées au cadre de vie) :

| Indicateurs des cadres | Fiche |
|---|---|
| Surpeuplement (OCDE 3_1, Eurostat 1.3), problèmes structurels (Eurostat), équipements sanitaires et pièces par personne (BLI), bidonvilles et logement inadéquat (Doughnut, ODD 11.1.1) | présents |
| Surcharge (OCDE 3_3), accessibilité financière (OCDE 3_2), internet (OCDE 3_4), chauffage (OCDE 3_5, Doughnut énergie) | présents, en fiches ou en variantes |
| Air : OCDE 9_2, Eurostat PM10 et PM2,5, objectifs UE et valeur guide OMS | présents |
| Pollution, saleté et bruit déclarés (Eurostat 8.1, SSF) | présents |
| Eau potable et assainissement (Doughnut, ODD 6) | présents (assainissement → `planete`, D39) |
| Temps de trajet (SSF) | `duree_trajet_domicile_travail` |
| Sans-abrisme (SSF) | proxy indirect (J3) |
| Chaleur extrême (OCDE 9_3) | renvoyé à `planete` (A14) |

Absences justifiées, toutes faute de série éligible :
- sous-occupation (sens ambigu) ;
- satisfaction du logement, des espaces verts et du cadre de vie (EU-SILC 2013 seulement, 1 point à la long-list ; DREES LO11 : 2024-2025) ;
- accès aux espaces verts (OCDE 9_1 : 2012 et 2018) ;
- accès aux transports publics (ODD 11.2.1 : 2020 seulement ; EU-SILC `ilc_hcmp06` : 2012 ; `ilc_atst*` : 2024) ;
- passoires énergétiques (parc par étiquette DPE non catalogué, LOG-11) ;
- `sdg_11_50` (exposition aux particules, Eurostat d'après l'AEE) : absent des catalogues mais non éligible, dernière mise à jour en février 2021 et données jusqu'en 2019 (DB.nomics).

**Indicateurs déclaratifs disponibles** :

| Source | Constat |
|---|---|
| Baromètre DREES | OG04_1 retenu ; SDPROXIM_3 retenu (J3) ; LO11 (2 vagues) et LO10 (5 vagues, structure) non éligibles ; HA04 (accessibilité du quartier aux personnes handicapées, 6 vagues, opinion d'évolution) à rattacher à `egalites` comme le note M05 |
| EU-SILC `ilc_pw*` | seuls le logement et les espaces verts (2013) relèvent de la dimension : 1 point |
| OCDE How's Life | aucun item déclaratif sur le logement |
| Eurostat (ressenti) | bruit, pollution, logement sombre, charge ressentie : retenus |

**Thèmes de `dimensions.yaml`** : tous couverts sauf les espaces verts et l'accès aux services publics de proximité, pour lesquels aucune série éligible n'existe dans les catalogues. Ces deux lacunes sont à signaler à Léo comme limites de la dimension, pas comme oublis.

**Oublis** :

| # | Oubli | Données (lues) | Importance | Proposition |
|---|---|---|---|---|
| O1 | **Personnes n'ayant pas les moyens de posséder un ordinateur** (`ilc_mddu03`, `estat-031765`, long-list `education`), avec ses ventilations (`ilc_mddu03a` à `f`), la table handicap (`hlth_dm090`) et la table régionale du haut débit (`isoc_r_broad_h`, 2006-2021) : 28 lignes renvoyées par `education` (règle 120) et orphelines | API `ilc_mddu03` : 10,5 (2004), 4,0 (2010), 2,2 (2015), 2,5 (2020, `b`), 3,3 (2022, `b`), 3,5 (2025) ; 22 points | moyenne : privation numérique pour raisons financières, qui remonte depuis 2015 alors que la privation d'internet baisse | Règles `longlist = education` : fiche `privation_ordinateur` (`retenir_variante` dans la famille `privation_internet`, ou famille propre si la session mère juge les deux équipements non substituables), ventilations en variantes ; `isoc_r_broad_h` → `variante_de:haut_debit_domicile`. |

Pistes non comptées comme oublis (non lues, à confier à la maintenance) :
- exposition au bruit mesurée selon la directive européenne sur le bruit dans l'environnement (cartes stratégiques quinquennales, données de l'Agence européenne pour l'environnement) : existence d'une série nationale à URL stable non vérifiée ;
- sources de LOG-11 (sans-abrisme, expulsions, demandes de logement social, étiquettes DPE).

## 11. Cohérence inter-dimensions

Contrôle mécanique des séries principales, des composantes, des variantes et des lignes des 44 fiches contre les 371 fiches des neuf autres dimensions : **aucun identifiant commun, aucune série commune, aucune ligne commune**.

| # | Point | Proposition |
|---|---|---|
| I1 | 28 lignes de `education` orphelines (D38 a) | O1. |
| I2 | `education` règle 1010 `budget_menages_prix` : `prc_hicp_aind` et `prc_hicp_ainr` écartés en bloc, y compris `estat-052758` (CP041) et `estat-052759` (CP0411), qui sont la série principale et une variante de `hausse_loyers`. La même ligne reçoit donc deux décisions contraires, et la consigne du compte rendu M05 (question 2) n'a pas été appliquée par `education` | Règle `education` placée avant la règle 1010 : `autre_dimension:logement_cadre_vie` pour `prc_hicp_aind` CP041 et CP0411. Le vérificateur pourrait signaler une ligne affectée en `fiche` ou `variante_de` dans une dimension et en `ecarte_en_bloc` dans une autre. |
| I3 | Assainissement : D39 → `planete`, qui n'a aucune fiche | §3.1. |
| I4 | Lignes envoyées par `logement_cadre_vie` et non reprises (D38 a) :<br>• `planete` 22 : fret 18, degrés-jours de refroidissement 2, véhicules électriques de transport collectif 2 ; seule la chaleur extrême (OCDE 9_3) est reprise ;<br>• `education` 93 : niveau d'éducation par degré d'urbanisation ;<br>• `travail` 7 : `ilc_lvhl17`, `ilc_lvhl17n`, `hrst_fl_mob*` ;<br>• `niveau_de_vie` 2 : `ilc_li48` ;<br>• `egalites` 1 : OCDE 10_3_1 | À reprendre par les dimensions destinataires lors de leurs corrections. Pour le fret, `planete` a déjà la fiche `part_modale_fret_routier` (variantes). Pour `ilc_li48`, `niveau_de_vie` a `ilc_li45` en variante de `taux_pauvrete_60`. |
| I5 | `securite/delinquance_quartier` (`ilc_mddw03`, même module triennal EU-SILC) reste `frequence: annuelle`, alors que ses sept homologues sont `irreguliere` | D38 e : `frequence: irreguliere` dans `securite`. |
| I6 | Redondances à surveiller, déjà notées par M05 :<br>• `poids_logement_revenu` / `niveau_de_vie/depenses_pre_engagees` ;<br>• `privation_internet` / `niveau_de_vie/privation_materielle_sociale` (l'item internet en fait partie) ;<br>• `incapacite_chauffer` / `securite/retards_paiement` (factures) ;<br>• `privation_severe_logement` et ses composantes | Contrôle de redondance du gel 2. |
| I7 | Frontières vérifiées et conformes :<br>• `planete` : émissions de polluants (pressions) ici contre concentrations subies (R2) ; `ozone_vegetation` contre `depassement_norme_ozone` ; `exposition_chaleur_extreme`, `jours_canicule` (A14) ; `rendement_reseaux_eau`, `eaux_baignade_excellentes` (D39) ;<br>• `sante` : `deces_pollution_air` (`sdg_11_52`), `manque_medecins_percu` (accès aux soins) ;<br>• `education` : `illectronisme`, `competences_numeriques_base` (A7) ;<br>• `securite` : `delinquance_quartier`, `retards_paiement` ;<br>• `democratie` : `participation_en_ligne` (D39) | — |

## 12. Liste ordonnée des corrections (à faire par l'agent correcteur ou la session mère)

1. **Assainissement (D39, §3.1)** : groupes `conformite_assainissement_collectif*`, `raccordement_traitement_eaux_usees*` et `conformite_stations_itdd` → `autre_dimension:planete` ; suppression des deux fiches ; reprise par `planete` avec réexamen du sens de `sdg_06_20` (J4).
2. **Lignes orphelines (D38 a, O1, I2)** : importer les 28 lignes de `education` (fiche `privation_ordinateur` et variantes ; `isoc_r_broad_h` en variante de `haut_debit_domicile`). Demander à `education` la règle `autre_dimension:logement_cadre_vie` pour les lignes IPCH des loyers.
3. **Incontournables (D38 d, J1, §7)** : `incontournable: non` sur les 7 fiches non principales. Selon la décision J1, `non` aussi pour les familles `concentration_no2` et `depassement_norme_ozone`.
4. **Séries DREES (D34, D38 b, §6)** :
   - `preoccupation_logement` : `composantes`, `formule`, `non_recoupe_2014_2024`, recoupement 2025 (55,35 %) ;
   - `connaissance_personne_sdf` : `composantes`, `formule`, `non_recoupe`, recommandation selon J3.
5. **`hausse_loyers` (§4)** : IPC INSEE 011815635 en principale (formule de taux, recoupement fait), IPCH en variante, `raccordement: non`, réintégration au catalogue INSEE (LOG-6) ; puis décision J2.
6. **F1 et F2 (§5)** : nature des variantes INSEE de l'eau du robinet et de la variante OCDE 3_3 ; drapeaux de l'eau (creux de 2016, chute de 2024, saut INSEE 2015-2016).
7. **Compléments (§8)** :
   - `pollution_quartier`, `acces_internet_domicile` : drapeaux et notes ;
   - `duree_trajet_domicile_travail` : valeurs 2011 et 2016, sous-champs ;
   - `sous_occupation` : ruptures ;
   - drapeau `valeurs_lues_sur_table_odd` retiré.
8. **Séries Melodi** (`administration_en_ligne`, `haut_debit_domicile`, `poids_logement_revenu`) : collecte ciblée du robot avant le gel 2, comparaison aux valeurs de contrôle du §8.
9. **Décisions J3, J5, J6, J7** puis familles, recommandations et types mis à jour.
10. **Signalements aux autres dimensions** : I4 (lignes non reprises) et I5 (`securite/delinquance_quartier`).
11. Puis `python scripts/preselection.py --dimension logement_cadre_vie --maj-fiches`, `python scripts/verifier_fiches.py --dimension logement_cadre_vie --tableau` et `python scripts/verifier_fiches.py --dimension logement_cadre_vie` (0 erreur), et mise à jour du compte rendu M05.

## 13. Questions pour la session mère

1. **Socle par défaut** : avec la règle de D37 et le seul critère des « 3 cadres », le socle de la dimension ne contient que la qualité du logement et l'air, soit 7 indicateurs après J1. Faut-il, pour chaque sous-thème de `dimensions.yaml` (coût, précarité énergétique, numérique, transports), désigner une principale au socle même hors crosswalk ? Les candidats naturels sont `surcharge_couts_logement`, `incapacite_chauffer`, `acces_internet_domicile` ou `usage_internet`, et `part_modale_transports_collectifs`. Faut-il aussi choisir entre `privation_severe_logement` et ses composantes (redondance) ?
2. **Incontournables de l'air (J1)** : limiter l'incontournable aux PM2,5, aux PM10 et à la pollution déclarée ?
3. **Loyers** : IPC INSEE en principale (recalcul de taux selon D34) ? Taux nominal ou écart à l'inflation (J2) ?
4. **Sans-abrisme (J3)** : accepter « connaître une personne SDF » comme seul proxy, une fois calculé, ou laisser le thème sans indicateur jusqu'à LOG-11 ?
5. **Rattachements** : bancarisation (J5) ; consigne aux dimensions destinataires pour les lignes non reprises (I4) et à `education` pour les loyers (I2) ; la privation d'ordinateur (O1) est-elle une variante de `privation_internet` ou une famille propre ?
6. **Vérificateur** : ajouter deux avertissements, l'un pour une ligne `autre_dimension:<dim>` non reprise par `<dim>` (proposé aussi par l'audit `planete`), l'autre pour une ligne affectée en `fiche` ou `variante_de` dans une dimension et en `ecarte_en_bloc` dans une autre (I2) ?

## Annexe — sources consultées (16/10/2026)

| Source | Usage |
|---|---|
| API Eurostat (`https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<code>?…&geo=FR&lang=fr`) : `ilc_lvho50a`, `sdg_06_20`, `ilc_mddw02`, `ilc_mdho01`, `ilc_mdho06a`, `ilc_mdho05`, `ilc_lvho05a`, `ilc_lvho07a`, `isoc_ci_in_h`, `isoc_ci_ifp_iu`, `isoc_cbt`, `tran_hv_psmod`, `ilc_mdes01`, `ilc_mddw01`, `ilc_lvho08a`, `ilc_mded04`, `ilc_mdho04`, `ilc_mddu07a`, `tipsho60`, `ilc_mddu03`, `prc_hicp_aind`, `ilc_lvho03`, `isoc_ciegi_ac` (I_IUGOV12) | valeurs, drapeaux, libellés, mention d'arrêt de `prc_hicp_aind` |
| BDM INSEE (`https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/<idbanks>`, requêtes groupées) : 001791247, 010595400, 010595405, 010596094, 001779870 ; 010751584, 010751585, 010596142, 010600314, 010600312, 010596095 ; 010596140, 010596141, 010594684, 011815635, 010596138 ; 001718270 | titres, unités, zones, valeurs, statuts |
| DiDo SDES, fichier ITDD France entière (`https://data.statistiques.developpement-durable.gouv.fr/dido/api/v1/datafiles/305ea0e3-269b-47ee-bab5-7553fec6f010/csv`) | durée et distance des navettes 2011-2022, conformité de l'eau distribuée 2008-2024 |
| OCDE, *How's Life? 2020*, chapitre 6 (`https://www.oecd.org/en/publications/2020/03/how-s-life-2020_b547d82c/full-report/component-6.html`), trouvé par recherche web | définitions de la surcharge (40 % les plus modestes) et de l'accès à internet |
| DB.nomics, `https://db.nomics.world/Eurostat/sdg_11_50?offset=10`, trouvé par recherche web | `sdg_11_50` : dernière mise à jour le 8/2/2021, données jusqu'en 2019 |
| Extraits du robot (dépôt) : `sdes__air_*.csv`, `verif_acces/extraits/sdes__air_expo_pm25_fond_urbain_csv.txt`, fixture `tests/fixtures/sdes_dido/datafile_expo_pm25_fond_urbain.csv`, `verif_acces/extraits/banque_mondiale__en_atm_pm25_mc_m3.txt`, `ocde__odd_11.csv`, `ocde__hsl_bien_etre_actuel.csv`, `ocde__hsl_structure_libelles_fr.txt` et `_en.txt`, `drees__barometre_2000_2025_distributions.csv`, `drees__barometre_2000_2025_couverture.csv`, `drees__barometre_dico_variables_2025.txt`, `drees__barometre_dico_libelles_2025.txt`, `drees__barometre_tc_simplifies_2025.txt`, `sdes__itdd_france_entiere.csv`, `sdes__dido_catalogue.csv` | valeurs, couvertures, modalités, recoupement DREES 2025 |
| Catalogues du dépôt : `insee_melodi_catalogue.csv`, `insee_bdm_catalogue_non.csv.gz`, `eurostat_jeux_catalogue.csv`, les dix long-lists, les dix présélections | libellés Melodi, exclusions M01, jeux EU-SILC modulaires, renvois croisés |
| **Non lus** :<br>• PDF des définitions de How's Life (oecd.org, refusé par robots.txt) ;<br>• métadonnées INSEE de l'indicateur ODD 8.i7 (erreur serveur) ;<br>• API Melodi (non tentée, refusée par robots.txt selon M05 et M06 `travail`) ;<br>• API SDMX de l'OCDE (non tentée) ;<br>• API Eurostat `sdg_11_50` (erreur client ; jeu arrêté d'après DB.nomics) | — |
