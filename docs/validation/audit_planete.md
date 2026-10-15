# Audit croisé M06 — dimension `planete`

Agent auditeur M06 (session neuve, n'ayant pas participé à M05 `planete`), 15 octobre 2026. Branche `m06-planete`, créée depuis `origin/main` au commit `792f1a5` (fiches fusionnées par la PR #17, puis méthode v1.2 et décisions D34-D36). Matériau audité : les 75 fiches `indicateurs/planete/*.yaml`, `docs/validation/validation_planete.csv`, `preselection_planete.csv`, `preselection_planete_lignes.csv`, `regles_preselection_planete.csv`, le journal et le compte rendu M05 `planete`, `docs/cr/maintenance_catalogues_planete.md`, la long-list `catalogues/longlist_planete.csv.gz`, les catalogues INSEE et Eurostat, le crosswalk (`30_indicateurs_cadres_reference.csv`, `30_crosswalk_synthese.md`, `30_cadres_reference_extraction.md`) et les sorties du robot M04 (`docs/sources/series/`). **Aucune fiche, aucun tableau, aucun script ni aucun catalogue n'a été modifié** : ce rapport propose, un agent correcteur (ou la session mère) corrige. Le déroulé est dans `docs/cr/M06_planete_journal.md`.

Contrôle préalable : `python -m pytest -q` → 398 réussis ; `python scripts/verifier_fiches.py --dimension planete` (vérificateur v1.2, sans `--tableau`) → 0 erreur, 2 avertissements attendus (`intensite_exploitation_forets`, `preoccupation_environnement`, séries hors catalogue avec preuve) ; 75 fiches, **65 familles** (le chiffre de 64 date du premier commit M05, avant l'ajout des deux fiches hors long-list), 61 `retenir`, 9 `retenir_variante`, 5 `ecarter`, 1 déclarative, 2 composites, 3 « à vérifier », 2 hors long-list, 7 incontournables, 697 variantes, 0 ligne prise par une autre dimension.

Nature des constats : **F** = erreur factuelle (source et valeur attendue citées) ; **A** = alignement sur une décision postérieure à M05 (D34, D35), sans faute de M05 ; **C** = complément : réserve déclarée par M05 (drapeaux ou périmètre non lus) levée par l'audit ; **J** = désaccord de jugement (à trancher par la session mère ou Léo) ; **O** = oubli ; **I** = cohérence inter-dimensions.

## 0. Avis global : `corrections_necessaires`

Le travail de M05 est solide sur l'essentiel. Les concepts nommés par `dimensions.yaml` ont tous une fiche ; seuls manquent les feux de forêt, aléa climatique qui relève d'A14. Les arbitrages D24-D25 sont respectés : énergie et agriculture ici, aléas subis ici (A14), air local, eau du robinet, bruit et précarité énergétique renvoyés à `logement_cadre_vie`. L'empreinte et les émissions territoriales forment deux familles, et les ventilations fines sont écartées par des règles motivées. Sur les 42 fiches relues à la source, les valeurs numériques citées sont exactes, y compris les valeurs INSEE que M05 n'avait pas pu lire (la BDM répond à l'outil le 15/10) ; seules deux comparaisons sont fausses (§3.3, `prelevements_eau`). Six groupes de problèmes doivent pourtant être réglés avant la validation de Léo :

1. **`part_espaces_naturels` repose sur une série INSEE mal étiquetée** (F, incontournable). La BDM 010776377, présentée comme une « proportion » en %, contient des hectares (21 950 459 en 2000). La série en % est 010776378, étiquetée « milliers d'hectares », et elle est arrondie à l'unité : elle vaut 40 de 2000 à 2022. L'inversion vaut aussi pour les terres agricoles (010776375/376) ; 010596146 (« milliers d'hectares ») est en hectares (§3.1).
2. **Polluants atmosphériques : champ et rupture du « total pour l'évaluation de conformité »** (F et C, 6 fiches). Le code Eurostat `NFR_TOT_NAT_C` suit la directive (UE) 2016/2284, qui exclut les DOM (art. 2 §2) : le champ est l'hexagone, et le drapeau `perimetre_geo_a_verifier` peut être remplacé par `champ_metropole`. Surtout, la série des COVNM chute de 40 % en 2020 (1 171 700 t → 706 010 t) et présente un creux isolé en 2005 (1 339 890 t entre 1 827 710 et 1 703 750). C'est l'ordre de grandeur des COVNM agricoles (403,6 kt en 2025 chez le Citepa), probablement exclus du total de conformité pour l'année de référence et à partir de 2020. La comparaison de la fiche avec le Citepa (1 027,5 kt en 2025) porte donc sur deux champs différents (§3.3).
3. **`gaspillage_alimentaire` cumule deux méthodes non comparables** (F). D'après les métadonnées INSEE de l'indicateur 12.i3, les valeurs depuis 2020 « ne sont pas comparables » à celle de 2015 (étude ADEME). Il reste 4 points annuels comparables (2020-2023) : la souplesse D28, pensée pour les séries pluriannuelles, ne s'applique plus, et la recommandation `retenir` doit être revue (§3.2).
4. **Décision D35 non encore appliquée** (A) : la méthode v1.2 cite l'empreinte comme cas où le **par habitant est principal**. La famille `empreinte_carbone` doit être inversée (`empreinte_carbone_par_habitant` principale), ou la session mère doit confirmer l'exception (fourchettes SNBC 3 en Mt). Il manque aussi `annee_reference` aux deux composites (D34) et `composantes`/`formule` à la série DREES recalculée.
5. **Compléments de M05 levés par l'audit** (C) : drapeaux Eurostat lus pour les nitrates (série lissée, quasi constante), l'eutrophisation marine (aucun drapeau, mais un champ limité à la ZEE métropolitaine et une valeur annuelle arrondie à 0,00 % quatre années sur dix), la circularité (2024 imputée). Valeur provisoire pour les habitats (2024).
6. **Rattachements croisés non repris** (I) : 8 lignes renvoyées vers `planete` par `niveau_de_vie` (règle 1180) et `travail` (règle 960) n'ont aucune affectation dans la présélection `planete`. La part modale du fret est ici, celle des voyageurs (même indicateur ODD 9.i1) dans la long-list `logement_cadre_vie`.

Chiffres : **42 fiches auditées sur 75** (les 33 autres ont reçu un contrôle transversal), soit **23 `conforme`**, **18 `a_corriger`** (7 F, 5 A, 6 C) et **1 `non_verifiable`** (définition OCDE de `intensite_exploitation_forets`). S'y ajoutent 3 oublis (plus les 3 sources déjà signalées en PLA-4), 6 points de cohérence inter-dimensions et 9 désaccords de jugement. Liste ordonnée des corrections : §9.

## 1. Échantillon

| Règle (fiche M06 et consigne de la session mère) | Fiches |
|---|---|
| `recommandation: ecarter` (5) | `captures_peche`, `communes_ppr`, `prelevements_bois`, `preoccupation_environnement`, `races_locales_menacees` |
| `incontournable: oui` (7) | `emissions_ges_territoire`, `emissions_ges_par_habitant`, `empreinte_carbone`, `empreinte_carbone_par_habitant`, `artificialisation_sols`, `part_espaces_naturels`, `taux_boisement` |
| « À vérifier » au journal M05 (20, dont 1 déjà comptée) : éligibilité `a_verifier` (3), éligibilité `non` retenue selon D28 (3), hors long-list (2), raccordement `a_etudier` (5), rattachement proposé (1), drapeaux Eurostat non lus (6) | `erosion_sols`, `especes_exotiques_envahissantes`, `etat_conservation_habitats` ; `etat_ecologique_eaux_surface`, `etat_chimique_eaux_souterraines`, `gaspillage_alimentaire` ; `intensite_exploitation_forets` ; `consommation_interieure_matieres`, `emissions_co2_voitures_neuves`, `excedent_azote`, `excedent_phosphore`, `oiseaux_communs_specialistes` ; `exposition_chaleur_extreme` ; `emissions_cov_non_methaniques`, `emissions_dioxyde_soufre`, `emissions_metaux_lourds`, `eutrophisation_eaux_marines`, `nitrates_eaux_souterraines`, `taux_utilisation_circulaire_matieres` |
| Composites (2) | `empreinte_consommation_ue`, `empreinte_ecologique` |
| 20 % des 42 « autres » fiches, soit 8,4 arrondi à 9 | `prelevements_eau`, `emissions_dioxines`, `eaux_baignade_excellentes`, `part_vehicules_electriques_neufs`, `puits_carbone_utcatf`, `pesticides_rivieres`, `indice_exploitation_eau`, `indice_liste_rouge`, `flux_phosphore_mer` |

Tirage : `random.Random(20261014).sample(pool, 9)` en Python 3, `pool` étant la liste triée des 42 fiches non retenues d'office, **graine 20261014** (même graine que les quatre audits précédents). Total : **33 fiches d'office + 9 tirées = 42**. Les 33 autres ont reçu un contrôle transversal (type, sens, famille, unité, zone, cohérence avec D19 et D35) ; `consommation_energie_finale` et `consommation_energie_primaire` ont aussi été relues à la source (API `nrg_ind_eff` : 2005-2024, sans drapeau).

## 2. Fiches auditées

Sources lues par WebFetch le 15/10/2026 (détail en annexe) ; extraits du robot lus dans le dépôt.

| Fiche | Motif | Source consultée | Verdict | Nature | Constat et correction attendue (détail aux §3 à §6) |
|---|---|---|---|---|---|
| `captures_peche` | ecarter | API `fish_ca_main` | conforme | — | 691 942 t (2000), 442 800 t (2025), 2018-2021 provisoires (`p`) : exact ; sens ambigu recevable. |
| `communes_ppr` | ecarter | BDM 010595980 | conforme | — | 8 959 (2013) → 12 493 (2025), 13 points ; moyen administratif à double lecture : écart recevable. |
| `prelevements_bois` | ecarter | API `for_remov` | **a_corriger** | F (mineur) | 77 136 (2000) et 57 220 (2023) milliers de m³ exacts ; 2022 est aussi estimée (`e`) : drapeau `valeurs_estimees_2019_2021_2022_2023`. |
| `preoccupation_environnement` | ecarter, hors long-list | extrait DREES du robot (OG05_1) | **a_corriger** | A | 86,8 % (2000), 87,5 % (2019), 76,7 % (2025) recalculés à l'identique ; série calculée par le projet sans `composantes` ni `formule` (D34). |
| `races_locales_menacees` | ecarter | BDM 010594440, 010594442, 010594444 | **a_corriger** | F (mineur) | Valeurs **0 en 2012 et 2013** pour les classes « à risque » et « non à risque » (240 races classées « inconnu ») : anomalie à signaler (`valeurs_nulles_2012_2013`), 14 points utiles et non 16. La hausse 38 → 122 vient surtout du reclassement des races « à risque inconnu » (182 → 107), ce qui conforte le sens ambigu. |
| `artificialisation_sols` | incontournable | BDM 010596134, 010596146 | **a_corriger** | F (mineur), J | 7,4 % (2000) → 9,5 % (2023), révisions 1995-1996 et 2007-2015 (`OBS_REV`) : exact ; la variante 010596146 est en **hectares** (4 090 161 en 2000), non en milliers d'hectares comme l'étiquette INSEE ; famille `usage_sols` à scinder (J1). |
| `part_espaces_naturels` | incontournable | BDM 010776375 à 010776378 | **a_corriger** | F, J | Série principale en hectares, % publié arrondi à l'entier (§3.1). |
| `taux_boisement` | incontournable | BDM 010596289 | conforme | — | 29,9 % (2010) → 32,0 % (2022), unité `POURCENT_MOY5`, zone FM. |
| `emissions_ges_territoire` | incontournable | BDM 010596008 ; extrait Citepa | conforme | — | 551 Mt (2000), 369 Mt (2024, estimée `E`), 1990-2024 ; Citepa 359,4 Mt (2025, hors UTCATF) exact. |
| `emissions_ges_par_habitant` | incontournable | API `sdg_13_10` ; BDM 010595993 | conforme | — | 9,4 t (1990), 9,1 (2000), 5,3 (2024), sans drapeau ; INSEE 5,5 t (2023) et 5,4 t (2024, `E`) concordants. |
| `empreinte_carbone` | incontournable | BDM 010595981 | **a_corriger** | A, C | 692 Mt (2000), 563 Mt (2024, `E`) ; D35 : le par habitant devient principal (§4.1) ; remplacer la note « Valeurs BDM non relues ». |
| `empreinte_carbone_par_habitant` | incontournable | BDM 010595988 | **a_corriger** | A | 11,4 t (2000), 8,2 t (2024, `E`) : exact ; `variante_principale: oui`, `recommandation: retenir` (§4.1). |
| `consommation_interieure_matieres` | raccordement `a_etudier` | API `env_ac_mfa` | conforme | — | 14,561 t (2000, `b`), 10,597 t (2025, `i`), ruptures `b` en 2000, 2004 et 2009 : exact. |
| `emissions_co2_voitures_neuves` | raccordement `a_etudier` | API `sdg_13_31` | conforme | — | 109,8 g/km (2016) → 133,8 (2017, `be`), 2018-2019 `e`, 89,1 (2025, `p`) : exact. |
| `emissions_cov_non_methaniques` | drapeaux non lus | API `env_air_emis` ; extrait Citepa ; directive 2016/2284 | **a_corriger** | F, C | Rupture du total de conformité en 2005 et 2020 ; comparaison au Citepa inexacte ; champ hexagonal (§3.3). |
| `emissions_dioxyde_soufre` | drapeaux non lus | idem | **a_corriger** | C | 640 600 t (2000), 70 690 t (2024), aucun drapeau ; champ hexagonal (§3.3). |
| `emissions_metaux_lourds` | drapeaux non lus | idem | **a_corriger** | C | Plomb 280 t (2000), 90 t (2024), aucun drapeau ; niveau concordant avec le Citepa « France hexagonale » (92,1 t en 2025) : champ hexagonal probable (§3.3). |
| `erosion_sols` | a_verifier | API `sdg_15_50` | conforme | — | 4,14 % (2000), 3,39 (2010), 3,27 (2016), 3,08 (2023, `p`) : exact. |
| `especes_exotiques_envahissantes` | a_verifier | BDM 010596532 | conforme | (réserve) | 37,5 (2014) et 54,3 (2024), unité `MOYENNE_10`, titre « Nombre moyen d'espèces exotiques envahissantes en métropole » ; le mode de comptage reste « non trouvé » (la fiche le dit). |
| `etat_conservation_habitats` | a_verifier | BDM 010596301 à 010596304 | **a_corriger** | C | 22 % (2012), 20 (2018), 16 (2024, **provisoire `P`**) ; les quatre classes somment à 100 ; ajouter `derniere_valeur_provisoire`. |
| `etat_ecologique_eaux_surface` | éligibilité `non` (D28) | BDM 010595385, 010595386 | conforme | — | Très bon + bon : 43,4 (2013), 44,2 (2015), 43,1 (2019), 43,6 (2021) ; D28 applicable (écart moyen de 2,7 ans) ; `composantes` et `formule` présentes. |
| `etat_chimique_eaux_souterraines` | éligibilité `non` (D28) | BDM 010595394 | conforme | — | 67,0 ; 69,1 ; 70,7 ; 67,9 (2013, 2015, 2019, 2021). |
| `gaspillage_alimentaire` | éligibilité `non` (D28) | BDM 010596198 ; métadonnées INSEE 12.i3 | **a_corriger** | F | Rupture 2015/2020 non documentée, D28 inapplicable (§3.2). |
| `eutrophisation_eaux_marines` | drapeaux non lus | API `sdg_14_60` | **a_corriger** | C, J | Valeurs lues, aucun drapeau ; champ = ZEE métropolitaine ; valeur annuelle très instable (§3.4, J3). |
| `nitrates_eaux_souterraines` | drapeaux non lus | API `sdg_06_40` ; extrait ITDD | **a_corriger** | C | 17,85 mg/l (2007) → 17,49 (2023), sans drapeau ; série lissée (minimum 17,26 en 2018) : `faible_variation`, note « valeurs non relues » à remplacer ; variante ITDD 3,87 % (2022) exacte. |
| `taux_utilisation_circulaire_matieres` | drapeaux non lus | API `sdg_12_41` | **a_corriger** | C | 17,6 % (2010) → 17,8 % (2024, **imputée `i`**) ; creux 2019-2021 (16,2 ; 15,4 ; 15,4) ; drapeau `derniere_valeur_imputee`. |
| `excedent_azote` | raccordement `a_etudier` | API `aei_pr_gnb` | conforme | (J2) | 40,0 kg/ha (2000), 18,3 (2023), rupture `b` en 2010 : exact. |
| `excedent_phosphore` | raccordement `a_etudier` | API `aei_pr_gnb` | conforme | — | 8,4 kg/ha (2000), −1,1 (2023), rupture `b` en 2010 : exact. |
| `oiseaux_communs_specialistes` | raccordement `a_etudier` | BDM 010596708 | conforme | — | 84 (2010) → 63 (2024), base 100 en 1989, FM. |
| `exposition_chaleur_extreme` | rattachement proposé | extrait OCDE How's Life (9_3) | conforme | (réserve), O2 | 1,03 % (2024), 21 valeurs 2004-2024 : exact ; définition absente aussi de l'extrait des définitions OCDE ; base documentée possible chez Santé publique France (O2). |
| `intensite_exploitation_forets` | hors long-list | extrait OCDE ODD 15 ; API `for_vol_efa` | **non_verifiable** | O3 | 0,66 (2023), 18 points, 14 valeurs distinctes : exact. Définition et unité non lues (API OCDE non autorisée à l'outil). Recoupement : prélèvements sur accroissement net d'Eurostat = 0,677 en 2023 (§6, O3). |
| `empreinte_ecologique` | composite | extrait Footprint 2026 du robot | **a_corriger** | A | 6,0 gha (2000), 4,45 (2025), 2024-2025 estimés (`E`) : exact ; `annee_reference` manquant (D34). |
| `empreinte_consommation_ue` | composite | API `sdg_12_31` | **a_corriger** | A | 3,27 (2010), 3,17 (2024), sans drapeau : exact ; `annee_reference` manquant (D34). |
| `prelevements_eau` | tirage | API `env_wat_abs` ; extrait ITDD | **a_corriger** | F (mineur) | 538,42 m³ (2000), 341,21 m³ (2023), sans drapeau : exact. La note attribue « 34,1 milliards de m³ » aux eaux de surface : c'est le total toutes origines, eaux saumâtres comprises (ITDD `vol_prelev.total`, 2022) ; le refroidissement en eau de surface (13,3 milliards) est exact. |
| `emissions_dioxines` | tirage | extrait Citepa | conforme | — | 115,7 g I-TEQ (2025), 1990-2025, France hexagonale. |
| `eaux_baignade_excellentes` | tirage | API `sdg_14_40` | conforme | (J5) | 65,3 % (2011), 66,4 (2012), 75,6 (2013), 76,4 (2025) ; intérieures 71,0 (2025) : exact ; saut de 2013 toujours sans explication à la source. |
| `part_vehicules_electriques_neufs` | tirage | BDM 010775965 | conforme | (réserve) | 0,5 % (2013) → 16,8 % (2024), FE ; prise en compte des hybrides rechargeables toujours non trouvée. |
| `puits_carbone_utcatf` | tirage | API `env_air_gge` CRF4 ; décret SNBC 3 | conforme | — | −34,07 Mt (2000), −60,98 (2004), −33,94 (2017), −41,18 (2024), sans drapeau ; décret n° 2026-636 du 16/07/2026 existant. |
| `pesticides_rivieres` | tirage | API `sdg_06_70` | conforme | — | 17,4 % (2022) à 35,2 % (2023), 29,7 % (2017), sans drapeau. |
| `indice_exploitation_eau` | tirage | API `sdg_06_60` | conforme | — | 2,19 % (2013) à 5,35 % (2005), 2023 estimée (`e`). |
| `indice_liste_rouge` | tirage | extraits OCDE ODD 15 et How's Life ; OWID | conforme | (J4) | 0,83 (2024), 25 points, 13 valeurs distinctes ; How's Life 0,8426 (2025). |
| `flux_phosphore_mer` | tirage | BDM 010596782 à 010596785 | conforme | — | 15,0 kt (2010) … 15,9 (2021) ; Manche et Atlantique jusqu'en 2023, Méditerranée jusqu'en 2021 : exact. |

Contrôles transversaux de l'échantillon : `declaratif` (`oui` pour la seule opinion DREES) et `composite` (2) conformes à la méthode §4 et à D18 ; `frequence: irreguliere` justifiée pour les masses d'eau, les habitats, les espèces exotiques, l'érosion et les déchets (biennale), **pas pour le gaspillage** (§3.2). Les types sont justes (§5.1), sauf la famille mixte `usage_sols` (J1).

## 3. Erreurs factuelles et compléments (détail)

### 3.1 `part_espaces_naturels` : étiquettes INSEE inversées (F)

| BDM | Titre INSEE | Unité INSEE | 2000 | 2010 | 2020 | 2022 |
|---|---|---|---|---|---|---|
| 010776377 (série de la fiche) | Proportion de zones boisées, naturelles, humides ou en eau | `POURCENT` | 21 950 459 | 22 012 523 | 22 006 230 | 22 003 139 |
| 010776378 (variante) | Surface de zones boisées, naturelles, humides ou en eau | `MILLIERS_HECTARES` | 40 | 40 | 40 | 40 |
| 010776375 (variante) | Proportion de terres agricoles | `POURCENT` | 28 909 967 | 28 282 190 | 27 775 143 | 27 700 994 |
| 010776376 (variante) | Surface de terres agricoles | `MILLIERS_HECTARES` | 53 | 51 | 51 | 50 |
| 010596146 (variante d'`artificialisation_sols`) | Surface des sols artificialisés | `MILLIERS_HECTARES` | 4 090 161 | 4 653 742 | 5 136 984 | 5 214 224 |

Les « proportions » sont des surfaces en hectares, les « surfaces » des pourcentages arrondis à l'unité, et 010596146 est en hectares. Recoupement : la somme des trois surfaces (54 950 587 ha en 2000, 54 918 357 ha en 2022) est la superficie de la métropole. On en déduit une part d'espaces naturels de 39,95 % (2000), 40,06 % (2010) et 40,07 % (2020 et 2022), et une part artificialisée de 7,44 % (2000) et 9,49 % (2022), identique à la série publiée 010596134 (7,4 et 9,5). **Corrections** :
- série principale calculée selon D34 : `formule: 010776377 / (010596146 + 010776375 + 010776377) * 100`, avec `composantes`, recoupement avec 010776378 (40) et 010596134, première année 1982 pour chaque composante ;
- ou bien 010776378, avec les drapeaux `etiquettes_inversees_insee` et `arrondi_entier` : la série publiée ne bouge pas de 2000 à 2022 et serait inutilisable pour des bornes ;
- corriger l'unité de la variante 010596146 (hectares) dans `artificialisation_sols` ;
- ajouter une ligne de maintenance M01 (unités des séries Teruti 010596146 et 010776375 à 010776378).

La part calculée est quasi constante (39,95 % à 40,07 %), ce qui n'est pas un motif d'écart (D34) ; voir J1 pour la famille.

### 3.2 `gaspillage_alimentaire` : rupture 2015/2020 (F)

Les métadonnées de l'indicateur ODD 12.i3 (INSEE, fiche lue le 15/10) indiquent :
- 2015 : étude de l'ADEME publiée en 2016 ;
- depuis 2020 : champ et méthode des décisions (UE) 2019/1597 et 2019/2000 (pertes de récolte exclues, parties non comestibles comprises), avec des sources INRAE, INSEE et ADEME ;
- les chiffres depuis 2020 « ne sont pas comparables à celles calculées en 2015 par l'Ademe » ;
- 2020 a été révisé en 2023, 2022 en 2025.

La BDM donne 150 kg par habitant (2015), puis 129, 129, 137 et 142 (2020-2023). La fiche présente ces 5 points comme une série pluriannuelle continue : `frequence: irreguliere`, admise par D28 pour un écart moyen de 2 ans. **Corrections** :
- `frequence: annuelle` ;
- `raccordement: a_etudier : 2015 (ADEME) non comparable à 2020-2023 (méthode UE)` et `qualite: rupture_2020` ;
- motif et note réécrits : l'objectif AGEC (−50 % par rapport à 2015) ne peut pas être suivi sur cette série seule.

Avec 4 points annuels comparables, la série n'est plus éligible (charte §3.4 : 10 points) et D28 ne s'applique pas. La recommandation doit être revue : `ecarter` (motif : série comparable trop courte, à réexaminer quand elle atteindra 10 points) ou dérogation explicite décidée par la session mère au titre de la cible ODD 12.3 (question 3, §10). La règle de présélection `gaspillage_alimentaire` et la ligne PLA-1 (qui cite ce cas comme exemple de D28) sont à corriger en conséquence.

### 3.3 Polluants atmosphériques : champ et rupture du total de conformité (F, C)

**Champ.** Les six fiches de polluants issues d'`env_air_emis` (`emissions_ammoniac`, `emissions_oxydes_azote`, `emissions_particules_fines` hors échantillon, `emissions_cov_non_methaniques`, `emissions_dioxyde_soufre`, `emissions_metaux_lourds`) prennent le code `NFR_TOT_NAT_C` (« Total national pour l'évaluation de conformité »). Or la directive (UE) 2016/2284 « ne couvre pas les émissions … des départements français d'outre-mer » (article 2 §2, lu sur legislation.gov.uk). Le champ des cinq polluants visés par la directive est donc l'hexagone, comme l'avait pressenti M05 en comparant au Citepa (ammoniac : 574 390 t en 2024 chez Eurostat, 568,3 kt en 2025 chez le Citepa « France hexagonale »). Pour le plomb, non visé par la directive, la concordance avec le Citepa hexagonal (90 t en 2024, 92,1 t en 2025) rend le même champ probable. Le total « pour tout l'ensemble du territoire » (`NFR_TOT_NAT`) est déjà en variante de chaque fiche. **Corrections** :
- `qualite` : remplacer `perimetre_geo_a_verifier` par `champ_metropole` (garder `geo: FR`, code de la série, D15, ou passer en `FM` : question 2) et retirer `drapeaux_eurostat_non_lus` (API lue le 15/10, mise à jour du 07/09/2026 : aucun drapeau de 2000 à 2024 sur les 16 polluants) ;
- remplacer la note commune « Périmètre géographique … à confirmer » par la référence à l'article 2 §2 de la directive.

**Rupture des COVNM** (F). Série `NFR_TOT_NAT_C` lue de 1990 à 2024 :

| Année | 2003 | 2004 | **2005** | 2006 | 2018 | 2019 | **2020** | 2021 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| COVNM (t) | 1 917 650 | 1 827 710 | **1 339 890** | 1 703 750 | 1 206 970 | 1 171 700 | **706 010** | 709 410 | 635 090 |

L'année 2005 est isolée et la série baisse de 40 % en 2020. L'écart (≈ 400 à 490 kt) a l'ordre de grandeur des COVNM du secteur « agriculture / sylviculture » chez le Citepa (403,6 kt en 2025 sur 1 027,5 kt). Explication probable, non vérifiée (article 4 de la directive non lu, accès refusé) : le total de conformité exclut les COVNM des effluents d'élevage et des sols agricoles pour l'année de référence 2005 et pour les années d'engagement à partir de 2020. La série principale n'est donc pas homogène, et le motif compare deux champs différents (« 1 027,5 kt en 2025 selon le Citepa », agriculture comprise ; le Citepa hors agriculture et sylviculture donne 623,9 kt). **Corrections** :
- choisir une série homogène : `NFR_TOT_NAT` (variante, à relire : refus HTTP 429 le 15/10), ou le Citepa hexagonal 1990-2025 (niveau 2), ou le total de conformité limité à 2020-2024 ;
- `raccordement: a_etudier` et `qualite: rupture_2005_2020` tant que la série n'est pas remplacée ;
- motif corrigé ;
- vérifier sur 2019-2020 si le total de conformité des oxydes d'azote, que la même disposition viserait aussi (hypothèse), présente la même rupture (non lu : 1 050 190 t en 2015, 754 770 t en 2020).

### 3.4 `eutrophisation_eaux_marines` (C, J3)

L'API `sdg_14_60` (mise à jour du 28/04/2026) donne :
- aucun drapeau ;
- en km² et en %, un rapport constant de **≈ 348 500 km²** (22 725 km² = 6,52 % en 2007 ; 16 782 km² = 4,82 % en 2024) : c'est la ZEE métropolitaine, le champ n'est donc pas la France entière ;
- en valeur annuelle (`VAL_A`) : 0,00 % en 2016, 2017, 2023 et 2025, 6,52 % en 2007, 4,82 % en 2024 ;
- en moyenne sur quatre ans (`AVG_4Y`) : 0,02 % (2017) à 2,35 % (2010), 1,23 % en 2025.

Un « avis important » accompagne le jeu (non lu). **Corrections** : `qualite` (`champ_metropole`, `forte_variabilite_annuelle`, retrait de `drapeaux_eurostat_non_lus`), définition (« part de la ZEE métropolitaine… ») et note (les valeurs sont désormais lues). La méthode reste à lire avant les bornes. Voir J3 pour la série principale.

### 3.5 Autres points factuels et compléments

- `races_locales_menacees`, `prelevements_bois`, `prelevements_eau`, `artificialisation_sols` : voir le tableau du §2.
- `nitrates_eaux_souterraines` : série lissée (17,85 → 17,26 → 17,49 mg/l), probablement une moyenne sur stations constantes ; signaler `faible_variation` pour les bornes, sans écart (D34).
- `especes_exotiques_envahissantes` : la fiche peut maintenant citer 37,5 (2014) et 54,3 (2024).
- `risque_pesticides_hri1` (hors échantillon, saut signalé par M05) : le communiqué interministériel de 2019, cité par Terre-net, attribue la hausse des ventes de 2018 à « une anticipation des achats en fin d'année 2018 en prévision de l'augmentation de la RPD » (redevance pour pollutions diffuses). Le NODU confirme ce pic (120,8 en 2018, 75,8 en 2019, BDM 010594432). Remplacer `saut_2019_a_expliquer` par `pic_2018_anticipation_rpd`.

## 4. Alignements sur les décisions postérieures à M05 (D34, D35)

1. **Empreinte carbone, D35** (A). La méthode v1.2 (§9) dit : « par habitant principal quand la lecture publique est par tête (empreinte, consommation) ». Il faut donc `empreinte_carbone_par_habitant` → `variante_principale: oui`, `recommandation: retenir`, et `empreinte_carbone` → `retenir_variante`, avec les motifs et le tableau de validation régénérés. La SNBC 3 fixe des fourchettes en Mt (516-531 Mt en 2024-2028) et un repère 2050 par habitant (2,3 ou 3,1 t) : si la session mère préfère garder le total, l'exception est à écrire dans D35 (question 1). Les autres familles sont conformes à D35 : émissions territoriales en Mt (budgets carbone), énergie en Mtep (cibles en volume), polluants et engrais en tonnes (cibles en % d'un volume), matières, déchets, eau et gaspillage par habitant.
2. **Composites, D34** (A) : `annee_reference` manque à `empreinte_ecologique` (`observation` : les comptes de 2026 couvrent 1961-2025, les deux dernières années étant estimées) et à `empreinte_consommation_ue` (`observation`, à confirmer dans la métadonnée Eurostat).
3. **Séries calculées, D34** (A) : `preoccupation_environnement` (OG05_1, modalités 1 + 2, non-réponses au dénominateur) doit porter `composantes` et `formule`. La part d'espaces naturels recalculée (§3.1) devra suivre la même règle.
4. **D36** : aucune variante sans `serie_id` unique (contrôle mécanique : 0 doublon) ; les deux séries hors long-list sont absentes de toutes les long-lists et des catalogues `*_non.csv.gz` (vérifié).

## 5. Points d'attention de la consigne

### 5.1 Pressions et états

Répartition des 75 fiches : 38 pressions, 25 résultats (états des milieux et aléas subis), 12 moyens (D19, tous physiques et adossés à une cible ou à un levier, aucun moyen budgétaire). Classement relu sur l'échantillon et contrôlé sur le reste :

| Catégorie | Constat |
|---|---|
| Pressions exercées | Émissions, empreintes, artificialisation, prélèvements d'eau et de bois, excédents et engrais, pesticides (HRI1, NODU), matières, déchets, polluants, flux d'azote et de phosphore à la mer, espèces exotiques, antibiotiques : `pression`, conforme. |
| États des milieux | Concentrations (nitrates, phosphates, pesticides des rivières), masses d'eau, baignade, eutrophisation, oiseaux, Liste rouge, habitats, érosion, ozone pour la végétation, boisement, espaces naturels, puits de carbone : `resultat`, conforme. |
| Familles | Dix familles regroupent plusieurs fiches : une seule mêle pression et état, `usage_sols` (artificialisation `pression`, espaces naturels `resultat`) → J1. Flux à la mer (pressions) et concentrations (états) sont bien dans des familles distinctes. |

### 5.2 Empreinte carbone et émissions territoriales

Deux familles distinctes, conformément à la méthode :
- empreinte : INSEE-SDES, 010595981 et 010595988 ;
- émissions territoriales : inventaire du Citepa relayé par l'INSEE, 010596008 et Eurostat `sdg_13_10`.

Les valeurs sont exactes et la zone est identique (`FM_D99_D978`, périmètre de Kyoto ; écart BDM/Melodi déjà en PLA-8). Les empreintes Eurostat (FIGARO), OCDE et Global Carbon Project sont en variantes, avec l'avertissement qu'elles reposent sur d'autres tableaux entrées-sorties. Le recouvrement entre empreinte carbone, empreinte écologique (part carbone prépondérante) et empreinte de consommation de l'UE relève du contrôle de redondance (M05 l'a noté). Seul l'ordre total / par habitant est à revoir (§4.1).

### 5.3 Unités

Les unités déclarées par les fiches de l'échantillon correspondent aux sources, sauf quatre unités fausses à la source, relevées dans les fiches ou leurs variantes :
- BDM 010776377 et 010596146 (§3.1) ;
- OCDE 12_8, déclarée en kg mais publiée en tonnes (PLA-7, la nature de la variante d'`emissions_ges_par_habitant` reprend « kg ») ;
- OCDE 15_2_1, déclarée en « points de pourcentage » pour un rapport de 0,66 (signalé par la fiche).

Le mélange de totaux et de séries par habitant dans la dimension suit D35.

### 5.4 Séries pluriannuelles (D17, D28)

| Fiche | Points | Écart moyen | Constat |
|---|---|---|---|
| `etat_ecologique_eaux_surface`, `etat_chimique_eaux_souterraines` | 4 (2013-2021) | 2,7 ans | D28 applicable ; PLA-1 justifiée |
| `etat_conservation_habitats` | 3 (2012, 2018, 2024) | 6 ans | rapportage sexennal, conforme |
| `especes_exotiques_envahissantes` | 2 (2014, 2024) | 10 ans | conforme à D28 ; comparaison de deux décennies seulement |
| `erosion_sols` | 4 (2000-2023) | 7,7 ans | modèle, conforme |
| `production_dechets` (hors échantillon) | 10, biennale | 2 ans | conforme |
| `gaspillage_alimentaire` | 5 dont 4 annuels | — | **non pluriannuelle : rupture 2015/2020** (§3.2) |

### 5.5 Périmètre géographique

Zones des 75 séries principales : `FR` 46, `FE` 14, `FM` 11, `FM_D99_D978` 3, `FE_HPBIO` 1. Les zones déclarées sont exactes dans l'échantillon, mais le code Eurostat `FR` recouvre parfois un champ métropolitain non documenté : les six polluants du total de conformité (§3.3) et l'eutrophisation marine (§3.4). Les autres champs métropolitains sont signalés par `champ_metropole` (Teruti, boisement, oiseaux, habitats, espèces exotiques, flux à la mer, Citepa hexagonal). `jours_canicule` (hors échantillon, `geo: FR`) mérite la même vérification, le système d'alerte canicule étant départemental.

## 6. Désaccords de jugement

- **J1. Famille `usage_sols`.** L'artificialisation (pression) et la part d'espaces naturels (état) ne sont pas substituables. Les trois parts (artificialisé, agricole, naturel) somment à 100 % : l'artificialisation progresse surtout aux dépens des terres agricoles (52,61 % → 50,44 % de 2000 à 2022), tandis que les espaces naturels restent stables (≈ 40 %). La part d'espaces naturels est plus proche du taux de boisement, qu'elle contient. Proposition : deux familles (`usage_sols` = artificialisation ; `espaces_naturels` = part d'espaces naturels, `retenir`), toutes deux incontournables.
- **J2. Azote et phosphore : excédent ou engrais en principale ?** Les engrais minéraux portent la cible officielle (SNBC 3 : −30 % en 2030 par rapport à 2020) et la forme de la limite du Doughnut (azote et phosphore appliqués comme engrais). La charte §3.3 place les objectifs officiels au premier rang des bornes. L'excédent, lui, n'a pas de cible et varie avec les rendements (61,8 kg/ha en 2003, 18,3 en 2023). Les deux mesurent des choses différentes (apport minéral contre surplus du bilan) : deux familles, ou les engrais en principale.
- **J3. Eutrophisation : moyenne sur quatre ans en principale.** Avec quatre années à 0,00 % sur les dix dernières et un pic à 4,82 % en 2024 suivi de 0,00 %, la valeur annuelle donnerait un score erratique ; la moyenne sur quatre ans (`AVG_4Y`, déjà en variante) se lit mieux.
- **J4. Liste rouge : série plus fine.** Les « paliers » relevés par la fiche (`valeurs_par_paliers`) tiennent à l'arrondi à deux décimales de la base ODD de l'OCDE (13 valeurs distinctes sur 25 ans) et d'OWID (0,84). How's Life 12_7 publie le même indice à quatre décimales (0,8426 en 2025, 22 valeurs distinctes sur 22 ans) et une année de plus. Proposition : How's Life en principale (2004-2025, 22 points), ou la fiche actuelle avec une note sur l'arrondi.
- **J5. Eaux de baignade : rester en `planete`.** L'indicateur est un état des eaux littorales (ODD 14), pas une condition subie au quotidien comme l'eau du robinet (R2). L'accord avec M05 est à acter par la session mère.
- **J6. Rattachements à confirmer** (soulevés par M05) : le rendement des réseaux d'eau potable est un service d'infrastructure (`logement_cadre_vie`, A5) autant qu'une pression ; l'exposition des animaux aux antibiotiques relève de l'agriculture (A2) mais aussi de la santé (antibiorésistance). L'auditeur garde les deux en `planete`, faute de concept équivalent ailleurs.
- **J7. Protection forte.** Elle porte une cible légale propre (10 % du territoire) distincte des 30 % d'aires protégées. D32 (« composante … sauf préoccupation publique propre ») permettrait une famille propre ; la variante de M05 reste défendable.
- **J8. Gaspillage** : écart ou dérogation (§3.2, question 3).
- **J9. Intensité d'exploitation forestière : préférer une série du catalogue.** La série OCDE est hors catalogue et sa définition n'est pas lue. Les volumes Eurostat `for_vol_efa` (unité `THS_M3`, forêts disponibles pour l'approvisionnement en bois) donnent :
  - accroissement net annuel 2012-2023 (rupture `b` en 2018) : 93,2 → 73,9 millions de m³ ;
  - quantités enlevées 2000-2023, imputées (`i`) avant 2012 ;
  - rapport : 0,458 (2012), 0,617 (2018), 0,686 (2021), 0,666 (2022), 0,677 (2023), concordant avec l'OCDE (0,66).

  Une série calculée (D34) de niveau 1, 2012-2023 (12 points), pourrait devenir principale ou recouper l'OCDE (O3). Elle montre une pression qui s'accroît : l'accroissement baisse et les prélèvements montent.

## 7. Complétude

**Long-list** : les 21 533 lignes et la ligne importée de `logement_cadre_vie` sont toutes affectées (vérificateur). Les lignes éligibles écartées en bloc ont été regroupées par jeu et relues :
- bilans énergétiques, comptes physiques, détail des inventaires et tableaux de passage : matière première des agrégats retenus ;
- moyens budgétaires : charte §3.4 ;
- échanges de déchets, filière bio, activité « verte » : sens ambigu ou détail.

Les motifs sont recevables. Une exception : les comptes forestiers en volume (O3). Les 16 lignes renvoyées ailleurs sont conformes à R2 et A2.

**Indicateurs du Doughnut** (13 limites, `30_cadres_reference_extraction.md` §1.4) :

| Limite | Indicateur mondial | Mesure nationale disponible | Fiche `planete` |
|---|---|---|---|
| Changement climatique | concentration de CO2, forçage radiatif | non (variables mondiales) ; proxy : empreinte de consommation (limite de 0,95 t de CO2 par habitant en 2017) | `empreinte_carbone(_par_habitant)`, `emissions_ges_*` (incontournables) |
| Acidification des océans | saturation en aragonite | non | — |
| Pollution chimique | production de produits chimiques dangereux | non (jeu Eurostat « par classe de dangerosité » sans donnée France) | proxies : `risque_pesticides_hri1`, `emissions_dioxines`, `emissions_metaux_lourds` |
| Nutriments | phosphore, azote appliqués comme engrais | oui (`aei_fm_usefert`) | `engrais_phosphates_mineraux`, `engrais_azotes_mineraux` (`retenir_variante`, J2) |
| Pollution de l'air | aérosols (AOD) | non ; proxy : émissions de particules | `emissions_particules_fines` |
| Eau douce | eau bleue / eau verte | partiel (prélèvements, WEI+) / non | `prelevements_eau`, `indice_exploitation_eau` |
| Conversion des terres | surface forestière | oui | `taux_boisement` |
| Biodiversité | taux d'extinction ; HANPP | proxy Liste rouge / non | `indice_liste_rouge` |
| Ozone stratosphérique | unités Dobson | non (aucune série de substances appauvrissant l'ozone au catalogue) | — |

Les indicateurs du Doughnut mesurables pour la France ont tous une fiche. Les empreintes azote, phosphore, eau bleue, perte d'espèces et HANPP de Tian et al. (2024) n'ont pas de série nationale annuelle.

**Incontournables du crosswalk** (§5) : « émissions de GES / empreinte carbone » (4 cadres) et « usage des sols » (3 cadres) sont couverts par 7 fiches, toutes `retenir` ou `retenir_variante` ; aucune autre fiche ne relève de ces concepts. Les 15 indicateurs « capital naturel » de l'OCDE sont présents en fiche ou en variante, sauf 12_4 (paysages forestiers intacts, non disponible).

**Oublis** :

| # | Oubli | Données (lues) | Importance | Proposition |
|---|---|---|---|---|
| O1 | **Feux de forêt** (surface brûlée), aléa climatique subi qui relève d'A14 (« canicules, inondations, aléas climatiques → planete ») | absents des dix long-lists, des catalogues `*_non.csv.gz` et des candidats M04 ; seuls figurent les polluants émis par les incendies (`NFR11B`) | moyenne | Ligne de maintenance : rechercher une source annuelle nationale (base BDIFF des incendies de forêt, système européen EFFIS) ; fiche hors long-list si vérifiée (D32). |
| O2 | **Population concernée par une canicule** et **sévérité des canicules** (Santé publique France, jeux `canicules-taille-de-la-population-concernee-par-une-canicule-france` et `canicules-severite-france`) | 22 enregistrements chacun (2004-2025), champs `pop_exposee` et `severite` d'après `docs/sources/series/spf_odisse__catalogue_champs.csv` ; valeurs non lues (API Odissé non autorisée à l'outil) | moyenne | Cataloguer comme variantes de `chaleur_extreme` ; la population exposée de SPF, documentée, pourrait remplacer l'OCDE 9_3 dont la définition est introuvable. |
| O3 | **Volumes forestiers d'Eurostat en m³** (`for_vol_efa`, `indic_fo=FAWS`, `unit=THS_M3` : accroissement net, quantités enlevées) | le catalogue M02 ne garde que l'unité `MIO_EUR` pour les forêts exploitables (28 lignes `for_vol_efa`, dont seulement deux en m³ et sur les forêts non exploitables) ; valeurs lues (J9) | moyenne | Maintenance M02 (préférer l'unité physique aux valeurs monétaires quand les deux existent) ; série calculée prélèvements / accroissement (D34). |

Déjà signalés par M05 et non repris comme oublis : consommation d'espaces naturels, agricoles et forestiers, haies, stocks halieutiques (PLA-4). Vérifiés sans résultat : pesticides dans les eaux souterraines (ITDD, 2020-2022, non éligible), substances appauvrissant l'ozone, HANPP, papillons des prairies (agrégat UE seulement).

## 8. Cohérence inter-dimensions

Contrôle mécanique des séries principales, des composantes, des variantes et des lignes des 75 fiches `planete`, contre les 206 fiches des six autres dimensions : **aucun identifiant commun, aucune série commune, aucune ligne commune**.

| # | Point | Proposition |
|---|---|---|
| I1 | **8 lignes renvoyées vers `planete` sans affectation** : `niveau_de_vie` règle 1180 (`sdg_02_20` revenu agricole par UTA, `sdg_17_50` taxes environnementales, `tran_hv_frtra` et `tran_hv_pstra` volumes de transport rapportés au PIB) ; `travail` règle 960 (`melodi-005582` à `005585`, emploi de l'économie circulaire par pilier, ODD 12.i6b) | Règles `longlist = niveau_de_vie` et `longlist = travail` dans la présélection `planete` : emploi circulaire et taxes → écarts en bloc existants (sens ambigu, moyens) ; volumes de transport rapportés au PIB → variantes de `part_modale_fret_routier` ou fiche de découplage ; revenu agricole → écart motivé, ou renvoi à `niveau_de_vie`. Proposer au vérificateur un avertissement quand une ligne `autre_dimension:<dim>` n'est pas reprise par `<dim>`. |
| I2 | **Part modale** : le fret (ODD 9.i1b, BDM 010751587) est ici, les voyageurs (ODD 9.i1a 010751584/585, Eurostat `tran_hv_psmod`) sont dans la long-list `logement_cadre_vie` | À trancher : les deux en `planete` (pression des transports), ou les voyageurs en `logement_cadre_vie` (accès aux transports collectifs) avec un motif. |
| I3 | Environnement local déclaré (`ilc_mddw02`, `ilc_mddw05`, `hlth_dhc120`) et assainissement → `logement_cadre_vie` | Conforme à R2 ; à reprendre par M05 `logement_cadre_vie` (pas encore traité). L'exposition aux PM2,5 (OCDE 9_2) y figure déjà, les décès dus aux PM2,5 (`sdg_11_52`) sont en `sante` : cohérent. |
| I4 | OCDE 9_3 (chaleur extrême), importée de la long-list `logement_cadre_vie` | M05 `logement_cadre_vie` devra poser `autre_dimension:planete` (A14). |
| I5 | Privation alimentaire (5 lignes) | Reprise par `niveau_de_vie` en variantes de `privation_alimentaire` : cohérent (A2). |
| I6 | Rendement des réseaux d'eau, antibiotiques, eaux de baignade | J5 et J6. |

## 9. Liste ordonnée des corrections (à faire par l'agent correcteur ou la session mère)

1. **`part_espaces_naturels`** (§3.1) : série principale recalculée en % à partir des hectares (D34) ou 010776378 avec drapeaux ; définition et unité ; unité de la variante 010596146 dans `artificialisation_sols` ; ligne de maintenance M01 sur les étiquettes INSEE.
2. **`emissions_cov_non_methaniques`** (§3.3) : série homogène (relire `NFR_TOT_NAT` ou prendre le Citepa), drapeau de rupture 2005/2020, motif corrigé ; vérifier la même rupture pour les oxydes d'azote.
3. **Champ des polluants** (§3.3) : `champ_metropole` à la place de `perimetre_geo_a_verifier` et retrait de `drapeaux_eurostat_non_lus` dans les six fiches `env_air_emis` ; note commune réécrite.
4. **`gaspillage_alimentaire`** (§3.2) : fréquence annuelle, rupture 2015/2020, motif ; recommandation selon la réponse à la question 3 ; règle de présélection et PLA-1.
5. **Empreinte, D35** (§4.1) : inverser la variante principale de la famille `empreinte_carbone` (ou exception écrite par la session mère) ; remplacer la note « valeurs BDM non relues ».
6. **D34** (§4.2-4.3) : `annee_reference` des deux composites ; `composantes` et `formule` de `preoccupation_environnement`.
7. **`eutrophisation_eaux_marines`** (§3.4) : champ ZEE métropolitaine, `forte_variabilite_annuelle`, retrait du drapeau, note ; série principale selon J3.
8. **Compléments** : `nitrates_eaux_souterraines` (`faible_variation`, note), `taux_utilisation_circulaire_matieres` (`derniere_valeur_imputee`), `etat_conservation_habitats` (`derniere_valeur_provisoire`), `races_locales_menacees` (`valeurs_nulles_2012_2013`, 14 points utiles), `prelevements_bois` (2022 estimée), `risque_pesticides_hri1` (pic 2018 expliqué).
9. **I1** : importer les 8 lignes renvoyées par `niveau_de_vie` et `travail` (écarts ou variantes motivés).
10. **O1-O3** : lignes de maintenance (feux de forêt ; jeux canicule de Santé publique France ; `for_vol_efa` en m³), puis variantes ou fiches selon J9.
11. **J1, J2, J3, J4, J7** : décisions de la session mère, puis familles et variantes principales mises à jour.
12. **Mineurs** : note de `prelevements_eau` (34,1 milliards de m³ = total toutes origines) ; valeurs à citer dans `especes_exotiques_envahissantes` ; nature « kg » de la variante OCDE 12_8 (PLA-7) ; vérifier le champ de `jours_canicule`.
13. **I2** : rattachement de la part modale des voyageurs à trancher avec M05 `logement_cadre_vie`.
14. Puis `python scripts/preselection.py --dimension planete --maj-fiches`, `python scripts/verifier_fiches.py --dimension planete --tableau` et `python scripts/verifier_fiches.py --dimension planete` (0 erreur), et mise à jour du compte rendu M05.

## 10. Questions pour la session mère

1. D35 et l'empreinte : le par habitant devient-il principal, comme le dit la méthode v1.2, alors que les fourchettes SNBC 3 sont en Mt ?
2. Polluants du total de conformité : garder `geo: FR` (code de la série) avec `champ_metropole`, ou passer la série principale au total « tout le territoire » (`NFR_TOT_NAT`, déjà en variante), s'il est homogène dans le temps ?
3. Gaspillage alimentaire : écart (4 points comparables) ou dérogation au titre de la cible ODD 12.3 et de la loi AGEC ?
4. Familles : scinder `usage_sols` (J1) ? Engrais minéraux ou excédent en principale pour l'azote et le phosphore (J2) ?
5. Rattachements : baignade, rendement des réseaux, antibiotiques (J5, J6) ; part modale des voyageurs (I2).

## 11. Propositions pour la méthode commune

1. **Contrôle d'ordre de grandeur des unités** : le vérificateur pourrait signaler une série principale en % dont les valeurs dépassent 100, ou une série en « milliers » dont les valeurs dépassent un million (cas des séries Teruti de la BDM).
2. **Totaux ajustés ou de conformité** : avant de retenir un total « pour l'évaluation de conformité » (NEC, inventaires ajustés), comparer ses années de référence et d'engagement avec le total national ; une exclusion réglementaire peut créer une rupture.
3. **Indicateurs annuels erratiques** : quand une série annuelle a des valeurs nulles ou des pics isolés (eutrophisation, aléas), la moyenne pluriannuelle publiée par le producteur est un meilleur candidat de série principale.
4. **Catalogue Eurostat** : préférer l'unité physique à l'unité monétaire quand un jeu publie les deux (`for_vol_efa`).
5. **Renvois croisés** : le vérificateur devrait avertir quand une ligne `autre_dimension:<dim>` d'une présélection n'est reprise par aucune règle de `<dim>` (8 lignes ici).
6. **Métadonnées INSEE ODD** : lire la fiche de métadonnées (`metadonnees-<indicateur>.pdf`) de chaque série principale INSEE ODD ; elle signale les ruptures (gaspillage) que la série ne montre pas.

## Annexe — sources consultées (15/10/2026)

| Source | Usage |
|---|---|
| `https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/<idbank>` (requêtes groupées) : 010596008, 010595981, 010595988, 010595993, 010600316, 010596134, 010596146, 010776375 à 010776378, 010596289, 010596532, 010596301 à 010596304, 010594440, 010594442, 010594444, 010596198, 010595385, 010595386, 010595394, 010596708, 010595980, 010596782 à 010596785, 010596774, 010775965, 010761992, 010594432, 010595977, 010751587 | valeurs, unités, zones, statuts |
| `https://www.insee.fr/fr/statistiques/fichier/4997335/metadonnees-12.i3.pdf` | rupture 2015/2020 du gaspillage alimentaire |
| API Eurostat (`https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/…`) : `sdg_13_10`, `env_air_emis` (`NFR_TOT_NAT_C` : 16 polluants ; COVNM 1990-2024), `env_air_gge` CRF4, `sdg_15_50`, `sdg_13_31`, `env_ac_mfa`, `sdg_06_40`, `sdg_14_60`, `sdg_12_41`, `aei_pr_gnb`, `sdg_12_31`, `env_wat_abs`, `sdg_06_60`, `sdg_06_70`, `sdg_14_40`, `nrg_ind_eff`, `for_remov`, `for_vol_efa` (`THS_M3`, `FAWS`), `fish_ca_main` | valeurs et drapeaux |
| `https://www.legislation.gov.uk/eudr/2016/2284/article/2/data.html` | champ de la directive (UE) 2016/2284 (DOM exclus) |
| `https://www.terre-net.fr/actualite-agricole/economie-social/article/la-vente-de-produits-phytos-en-hausse-conjoncturelle-de-8-en-2018-202-165402.html` | explication du pic des ventes de pesticides en 2018 |
| Recherche web (actu-environnement.com, « décret du 16/07/2026 2026-636 ») | existence du décret SNBC 3 cité par `puits_carbone_utcatf` |
| Extraits du robot (dépôt) : `citepa__secten_series.csv`, `citepa__secten_totaux_hors_utcatf.csv`, `ocde__odd_15.csv`, `ocde__hsl_bien_etre_actuel.csv`, `ocde__hsl_bien_etre_futur.csv`, `ocde__hsl_definitions_pdf.txt`, `owid__red-list-index.csv`, `drees__barometre_2000_2025_distributions.csv`, `drees__barometre_dico_*`, `gfn_fodafo__nfba2026_france.txt`, `sdes__itdd_france_entiere.csv`, `spf_odisse__catalogue_champs.csv`, `spf_odisse__canicules-nombres-de-jours-de-canicule-france.csv` | valeurs et couvertures |
| **Non lus** : EUR-Lex (directive 2016/2284) et article 4 de la directive sur legislation.gov.uk (autorisation non accordée) ; API OCDE `DSD_FOREST@DF_FOREST` (idem) ; API Odissé « population concernée par une canicule » (idem) ; API Eurostat `env_air_emis` COVNM `NFR_TOT_NAT` (**HTTP 429**, aucune lecture Eurostat ensuite) ; « avis importants » de `sdg_14_60` et `sdg_06_70` | — |
