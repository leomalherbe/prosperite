# Journal de bord — M05, dimension `securite` (mission pilote)

Agent de mission M05 (dimension Sécurité), branche `m05-securite`, 14 octobre 2026. Mission pilote menée en parallèle de `liens_bien_etre` : les choix de méthode sont écrits ici (§2) pour être repris par les autres dimensions.

## 0. Mise en route

- Branche `m05-securite` créée depuis `origin/main` (`d8a054b`).
- Lus : `CLAUDE.md`, charte (§3.1, §3.4, §3.6, §4, §5.1), journal des décisions (D13–D30), fiche M05 (dont la précision d'échelle du 14/10), `indicateurs/dimensions.yaml`, `_modele_fiche.yaml`, `docs/methodo/32_longlist_mode_emploi.md`, long-list `catalogues/longlist_securite.csv.gz` (928 lignes), `catalogues/longlist_bilan.json`, `30_indicateurs_cadres_reference.csv`, `30_crosswalk_synthese.md`, `docs/sources/autres_sources.md`, `10_indicateurs_candidats_hors_insee_eurostat.csv`, `insee.md`, `eurostat.md`, extraits du robot M04 (`docs/sources/series/ssmsi__…`, `ocde__…`, `drees__…`).
- Tests : `pip install -r requirements.txt && python -m pytest -q` → 372 réussis.
- `scripts/verifier_fiches.py` : absent de `origin/m05-liens_bien_etre` au démarrage, publié par l'agent parallèle en cours de mission (commit `881bc21`) ; **réutilisé tel quel** depuis un fichier temporaire (non copié dans cette branche), y compris pour écrire le tableau de validation (option `--tableau`) : les deux pilotes ont donc le même format de tableau.
- Précaution : aucun fichier sous `scripts/` ni `src/` n'est modifié, pour ne pas déclencher le robot « Collecte » (déclenché par un push sur `mNN-*` touchant ces dossiers). Les scripts de travail (règles de présélection, constructeur des fiches, contrôles) sont restés dans le bac à sable ; leurs règles sont reproduites ci-dessous et dans `docs/validation/preselection_securite.csv` (colonne `motif`).

## 1. Ce que contient la long-list `securite`

928 lignes : 768 éligibles, 19 à vérifier, 141 non éligibles ; Eurostat 823, M04 53, INSEE BDM 29, Melodi 23.

| Bloc | Lignes | Constat |
|---|---|---|
| Accidents aériens (`tran_sf_avia*`, 6 jeux) | 556 (540 éligibles) | 60 % de la long-list : victimes d'accidents survenus en France **ventilées par pays d'immatriculation** (AT, BE, …, UE27, FR), sans total toutes immatriculations |
| Infractions enregistrées Eurostat (`crim_off_cat`, `crim_hom_*` victimes, `crim_thb_*` victimes, `sdg_16_70`, `crim_gen_reg`, `urt_crim_gen`) | 148 | taux pour 100 000 ; jeux régionaux et typologiques non éligibles |
| Justice pénale Eurostat (`crim_just_*`, `crim_pris_*`, `crim_hom_soff` et `crim_thb_sex` hors victimes) | 65 | personnes suspectées, poursuivies, condamnées, détenues ; effectifs de juges, policiers, surveillants |
| Sécurité routière et ferroviaire (`sdg_11_40`, `tran_sf_road*`, `tran_r_acci`, `tran_sf_rail*`, `hsw_ac4`, INSEE ODD 3.i6, OCDE) | 41 | taux, nombres, ventilations par âge, sexe, type de route |
| Sécurité économique (SILC, surendettement, OCDE 1_6, Eurostat expérimental, DREES, soldes Camme) | 39 | |
| Enquêtes de victimation (INSEE ODD 16.i2, 5.i3a, 5.i4a ; ONUDC via OCDE ; CVS en nombre) et homicides hors Eurostat (INSEE, ONUDC, OCDE) | 38 | rupture CVS → VRS |
| SSMSI et ITDD, délinquance enregistrée | 22 | séries en **nombre** depuis 2016 ; ITDD en taux, 9 points |
| Sentiment d'insécurité (SILC, CVS, DREES, OCDE/Gallup) | 19 | |

## 2. Méthode retenue (à reprendre pour les autres dimensions)

### 2.1 Unité de travail : le groupe « concept × décision »
- Chaque ligne de la long-list est affectée à **un seul groupe** par une liste **ordonnée** de règles (prédicats sur `ligne_id`, code de jeu Eurostat, paramètres de requête `iccs`, `leg_stat`, `victim`…), la première règle vraie l'emporte ; contrôle : 100 % des lignes affectées.
- Un groupe porte une décision : `fiche` (une seule ligne : la série principale de la fiche), `variante_de:<id>` (lignes rattachées comme variantes d'une fiche), `ecarte_en_bloc` (motif obligatoire) et, **ajout proposé**, `autre_dimension:<dimension>` (concept relevant d'une autre dimension d'après `dimensions.yaml` : ni retenu ni écarté ici, la session mère tranche, R1). Utilisé une fois (détention provisoire et capacité des prisons → `democratie`).
- Les lignes d'**autres long-lists** qui relèvent du concept sont ajoutées au fichier ligne à ligne avec leur colonne `longlist` (sdg_16_10 de `sante`, deux soldes CVS de `hors_grille`) : la proposition de rattachement est ainsi traçable et vérifiable.
- Sorties : `docs/validation/preselection_securite.csv` (75 groupes : `groupe, decision, fiche, famille, concept, motif, nb_lignes, nb_eligibles, nb_a_verifier, nb_non_eligibles, longlist, sources, exemples_serie_id, regle`) et `docs/validation/preselection_securite_lignes.csv` (932 lignes : 928 de la long-list + 4 d'autres listes ; format aligné sur le pilote `liens_bien_etre`, lu par `verifier_fiches.py`).

### 2.2 Fiche propre ou variante ?
- **Fiche propre** : (a) concept distinct et intelligible pour le public (cambriolages, vols de véhicules, homicides conjugaux…) ; (b) **autre définition** d'un même concept que Léo doit pouvoir arbitrer, en premier lieu **enquête de victimation contre délinquance enregistrée** (même famille, deux fiches) ; (c) concept hors contenu mais visible, pour que l'écart soit arbitrable (sécurité ferroviaire).
- **Variante listée dans une fiche** : ventilations (sexe, âge, ménage, urbanisation, type de route), unités alternatives (nombre, par million, pour 1 000), copies (Melodi de la BDM, `sdg_16_20` de `ilc_mddw03`, jeux santé-handicap), autres relais de la même définition (ONUDC, OCDE, ITDD), séries d'enquête arrêtées, sous-catégories (viols, agressions sexuelles), et séries « non » éligibles du même concept (gardées pour la traçabilité, avec la mention).
- **Écarté en bloc** : sous-séries sans intérêt propre (ventilations par pays d'immatriculation), mesures d'activité des services, moyens administratifs (D28), exclusions de la long-list confirmées.

### 2.3 Choix de la variante principale (ordre appliqué)
1. **Taux** plutôt que nombre (un nombre n'est principal que s'il n'existe aucun taux : SSMSI, surendettement ; la fiche le signale par `qualite: en_nombre_taux_a_calculer`).
2. **Enquête de victimation plutôt que délinquance enregistrée, si l'enquête est vivante** (dernière valeur ≥ 2021). Si l'enquête s'est arrêtée (séries CVS en 2020-2021), la série enregistrée devient principale **à condition que son sens ne soit pas ambigu** (atteintes à fort taux de plainte : homicides, cambriolages, vols de véhicules) ; l'enquête arrêtée devient variante.
3. Puis les critères de la fiche M05 : niveau 1 > 2 ; INSEE > Eurostat à définition égale sauf profondeur ou fraîcheur (Eurostat principal pour les homicides et les tués de la route : taux depuis 2000/2008 quand l'INSEE n'a qu'un nombre depuis 2010) ; série la plus longue ; total avant ventilation.

### 2.4 Drapeau `declaratif`
Règle appliquée : `oui` si la question porte sur une **perception, une opinion ou une évaluation** (sentiment d'insécurité, délinquance perçue dans le quartier, sécurité la nuit, préoccupation, risque de pauvreté ressenti, soldes d'opinion) ; `non` si elle enregistre un **fait ou une capacité déclarés** (victimation, retards de paiement, incapacité à faire face à une dépense imprévue, épargne liquide). Cas limite signalé : la dépense imprévue est une auto-évaluation (classée `non` comme les autres éléments de privation matérielle de SILC). M04 avait classé les victimations `declaratif = oui` : divergence assumée, à harmoniser.

### 2.5 Sens des séries de délinquance enregistrée
- Une série enregistrée reçoit `sens: ambigu` et `recommandation: ecarter` quand **sa tendance contredit l'enquête de victimation** sur la même période (test chiffré, écrit dans le motif) : agressions graves ×2,1 (294 → 613 pour 100 000, 2008-2024) contre victimes de violences physiques stables (2,1 % en 2010 et en 2018) ; violences sexuelles ×4 (35,5 → 140,8, 2010-2024) contre 0,4-0,8 % dans l'enquête ; violences intrafamiliales enregistrées (révélation, M04). Même convention que le pilote `liens_bien_etre` (`sens: ambigu` n'admet que `ecarter`).
- Les séries enregistrées dont l'évolution est plausible et non contredite restent `bas` (homicides, cambriolages, vols de véhicules, vols avec violence).
- Les séries ne contenant que des sauts inexpliqués sont écartées sur ce motif (vols sans violence : +43 % en 2009, -16 % en 2010, +18 % en 2013, sans drapeau de rupture).

### 2.6 Rupture de l'enquête de victimation (2022)
Vérifiée sur la BDM (WebFetch) : les indicateurs ODD 16.i2 ont des valeurs 2010-2018 (CVS) puis 2021-2023 (VRS), **aucune valeur 2019-2020**, et un changement de niveau (ensemble : 2,2-2,7 % puis 1,4-1,7 %). Drapeaux `rupture_enquete_cvs_vrs`, `lacune_2019_2020` ; la note de pertinence demande de ne pas lire la baisse comme une amélioration. Les séries SSMSI de sentiment d'insécurité s'arrêtent en 2021 et la base des séries chronologiques du SSMSI ne contient pas de série VRS (inventaire du robot M04, 3 828 séries).

### 2.7 Incontournables
Un concept est incontournable s'il figure dans au moins trois cadres distincts de `30_indicateurs_cadres_reference.csv` (colonne `cadre`, ODD et objectifs officiels compris), le drapeau étant porté par **toutes les fiches de la famille**. Résultat : homicides (Doughnut, OCDE 10_1, Eurostat QoL) ; tués sur la route (OCDE 10_3, ODD 3.6, objectif UE 2030 — absent du tableau §5 de la synthèse du crosswalk, qui ne compte pas les cibles chiffrées) ; sentiment d'insécurité / délinquance perçue (SSF, OCDE 10_2, Eurostat QoL : familles `insecurite_quartier` et `securite_nuit`) ; sécurité économique — dépense imprévue et épargne liquide (SSF, OCDE 1_6, Eurostat QoL). Les retards de paiement (Eurostat QoL seul) et les violences hors homicides (SSF seul) ne le sont pas.

### 2.8 Sens des recommandations
`retenir` = disponible dans l'outil (variante principale d'une famille) ; `retenir_variante` = proposé comme alternative à l'intérieur de sa famille ; `ecarter` = motif vérifiable (chiffres, dates, décision du journal). La présence dans le socle (`retenu_socle`) reste la décision de Léo. Une série arrêtée sans relais est `ecarter` (elle serait toujours sans donnée récente), même si son concept est central (sentiment d'insécurité CVS) : la fiche existe pour rendre la lacune visible.

### 2.9 Champs des fiches
Schéma charte §5.1 + champs M05, aligné sur le pilote `liens_bien_etre` (0 avertissement de `verifier_fiches.py`) : `ligne_id` (ligne de la long-list de la série principale), `eligibilite_longlist`, `nb_points_depuis_2000` (omis pour les séries mensuelles BDM non comptées), `raccordement` (`oui | non | a_etudier`, suivi de « : note » si besoin), `variantes` (`serie_id, ligne_id, source, nature, eligible, periode`, plus `longlist` pour une ligne d'une autre long-list ou `catalogue` pour une série d'un catalogue « non »), `socle_v1` vide. Vocabulaire `qualite` : `delinquance_enregistree`, `sens_ambigu`, `rupture_enquete_cvs_vrs`, `lacune_AAAA_AAAA`, `serie_arretee_AAAA`, `en_nombre_taux_a_calculer`, `raccordement_AAAA_AAAA`, `rupture_AAAA` (drapeau b d'Eurostat), `provisoire_AAAA`, `irreguliere`, `moyennes_pluriannuelles`, `licence_non_trouvee`, `licence_a_confirmer`, `agregation_annuelle`, `jeu_regional_nuts`, `champ_geo_a_verifier`, `definition_a_corriger`, `faible_precision`, `faibles_effectifs`, `debut_AAAA`.
- URL : `url_api` reprise de la long-list (Eurostat, BDM) ou de l'URL vérifiée par le robot M04 (`docs/sources/verif_acces/series.csv` : SSMSI, OCDE, DREES) ; `url_page` : page de série INSEE (`insee.fr/fr/statistiques/serie/<idbank>`, vérifiée par WebFetch), page du navigateur Eurostat (modèle d'URL ; page en JavaScript, non lisible par WebFetch, le jeu étant vérifié par l'API), pages data.gouv.fr et data.drees vérifiées ; « non trouvé » pour l'OCDE.

### 2.10 Vérifications faites sur les sources (WebFetch, 14/10)
| Série | Constat |
|---|---|
| BDM 010596041, 010596044, 010596045, 010596046 | valeurs 2010-2018 et 2021-2023, aucune en 2019-2020 (rupture CVS/VRS) ; FM |
| BDM 010596040 (homicides, nombre) | 2010-2024, FE, 692 à 887 victimes |
| BDM 010593288 (tués, nombre) | 2010-2024, FM, 3 992 → 3 193 |
| BDM 010594499 (surendettement) | 2010-2024, FM, 218 102 → 108 748 (2020) → 134 807 |
| Eurostat `crim_hom_soff` victimes | 2008-2024, 1,03-1,60 pour 100 000 ; écart avec ONUDC/Banque mondiale ≤ 0,035 point (raccordement 2000-2007) |
| Eurostat `crim_off_cat` ICCS 0501, 05012, 05021, 0502, 0401, 020111, 0301 | valeurs et lacunes 2017-2019 (05012, 05021) relevées, citées dans les motifs |
| Eurostat `crim_hom_vrel` partenaire intime | 2015-2024, 0,15-0,19 |
| Eurostat `sdg_11_40` | 2000-2024, 13,3 → 4,6 ; drapeau b en 2014, p en 2023-2024 |
| Eurostat `tran_r_acci` blessés | 1990-2024, 2 726 (2000) → 990 (2024), sans drapeau |
| Eurostat `ilc_mdes04`, `ilc_mdes05`, `ilc_mddw03` | ruptures b 2020 et 2022 ; `ilc_mddw03` sans valeur 2021-2022 (question devenue triennale) |
| data.drees, jeu 431 (baromètre) | échantillon représentatif de la **France métropolitaine** (et non France entière comme au catalogue M04) |
| data.gouv.fr, base SSMSI | Licence Ouverte 2.0, mise à jour le 15/09/2026 |

## 3. Résultats

- **75 groupes** de présélection pour 932 lignes (928 de la long-list) : 33 `fiche`, 31 `variante_de` (180 lignes), 10 `ecarte_en_bloc` (716 lignes, dont 601 éligibles : aviation 540, activité répressive 50, personnel 8, stupéfiants 1, injures et menaces 2), 1 `autre_dimension:democratie` (3 lignes).
- **33 fiches** dans 25 familles : **20 `retenir`**, 4 `retenir_variante`, 9 `ecarter` ; 9 déclaratives ; 0 composite ; 2 à vérifier (D17 : `pauvrete_actifs_liquides`, `securite_nuit`) ; 8 incontournables (4 concepts) ; 182 variantes.
- Sous-thèmes : atteintes aux personnes 12 fiches, atteintes aux biens 5, sentiment d'insécurité 4, sécurité routière et transports 3, sécurité économique 9 (dont 4 soldes d'opinion, D29 P8).

| Recommandation | Fiches |
|---|---|
| retenir (20) | homicides, homicides_conjugaux, victimes_violences, victimes_violences_physiques, victimes_violences_sexuelles, victimes_violences_conjugales, victimes_vols_violence, cambriolages_logements, vols_vehicules, delinquance_quartier, securite_nuit, tues_route, blesses_route, depense_imprevue, retards_paiement, surendettement, pauvrete_actifs_liquides, risque_pauvrete_ressenti, solde_situation_financiere_passee, solde_capacite_epargne_actuelle |
| retenir_variante (4) | vols_violence_enregistres, preoccupation_insecurite_quartier, solde_situation_financiere_future, solde_capacite_epargne_future |
| ecarter (9) | violences_physiques_enregistrees, violences_sexuelles_enregistrees, violences_intrafamiliales_enregistrees, victimes_traite, vols_sans_violence, escroqueries, destructions_degradations, sentiment_insecurite_quartier, tues_ferroviaire |

## 4. Exclusions abusives, erreurs de catalogue et rattachements à revoir

1. **Table de correspondance, règle 4** : le motif exige « situation financière personnelle » ; les séries CVS 000857196 (situation financière passée) et 000857197 (future) disent « situation financière passée / future » et tombent en `hors_grille` (règle 5) alors que leurs séries brutes sont en `securite` (D29, P8). Correction proposée : motif `situation financi[èe]re (personnelle|pass[ée]e|future)`. Rattachées ici comme variantes.
2. **`sdg_16_10`** (taux standardisé de mortalité par homicide, Eurostat) est en `sante` (étiquette v0 du jeu ODD, règle 9) : à rattacher à `securite` (règle d'exception `sante` + « homicide » → `securite`), proposé comme variante de `homicides`.
3. **Catalogue M04, risque de pauvreté ressenti (DREES PE03)** : la série ne compte que la modalité 1 (« oui, plutôt ») et exclut « je me considère déjà comme pauvre » (7,9 % en 2014, 17,4 % en 2025) : la série baisse de 32,1 % à 16,1 % alors que la somme passe de 40,0 % à 33,5 %. Correction proposée : modalités 1 + 3. Les deux séries DREES ont aussi `geo = FR` au catalogue alors que le baromètre couvre la métropole.
4. **Catalogue INSEE (M01)** : la dépense imprévue et les impayés de SRCV (`DS_SRCV_PMS`, DIF_NON_PREVUE, DIF_PAIE, 2020-2025) sont écartés pour 6 points, alors qu'ils sont raccordables aux séries SILC d'Eurostat depuis 2004 (D16). Pas d'effet ici (Eurostat est principal), mais le même motif écarte le taux de privation matérielle et sociale de l'INSEE (`niveau_de_vie`).
5. **Jeux régionaux NUTS (D30)** : `tran_r_acci` est la **seule** source nationale des blessés de la route ; l'exclusion prévue des jeux NUTS doit l'épargner (exception à prévoir dans M02).
6. **Séries VRS absentes** : la base des séries chronologiques du SSMSI ne contient aucune série de l'enquête Vécu et ressenti en matière de sécurité ; le sentiment d'insécurité, les cambriolages déclarés, les injures et menaces s'arrêtent donc en 2020-2021. À cataloguer par M04 (publications VRS du SSMSI, data.gouv.fr).
7. **Séries SSMSI non cataloguées utiles au raccordement** : vols de véhicules (2016-2025) pour combler la lacune Eurostat 2017-2019 ; homicides « non renseigné » 2008-2015 ; actes de vandalisme (CVS 2006-2020).
8. Aucune exclusion abusive dans la long-list elle-même : les 141 lignes `non` relèvent bien de leur motif (séries depuis 2016 à 9 points, jeux régionaux, séries arrêtées avant 2020, modules ponctuels).
9. Rattachements signalés sans changement : `ilc_mdes07` (retards de factures courantes) est aussi un indicateur de précarité énergétique (`logement_cadre_vie`) ; détention provisoire et capacité des prisons → `democratie` ; corruption et blanchiment enregistrés (non éligibles) → `democratie`.

## 5. Contrôles (tâche 5)

`scripts/verifier_fiches.py` (branche `m05-liens_bien_etre`, commit `881bc21`), lancé depuis un fichier temporaire : `python verifier_fiches.py --dimension securite --racine <worktree> --tableau` →

```
Dimension securite : lignes_longlist 928, fiches 33, familles 25, retenir 20, retenir_variante 4, ecarter 9,
declaratifs 9, composites 0, a_verifier 2, hors_longlist 0, incontournables ['delinquance_quartier',
'depense_imprevue', 'homicides', 'pauvrete_actifs_liquides', 'preoccupation_insecurite_quartier', 'securite_nuit',
'sentiment_insecurite_quartier', 'tues_route'], variantes 182
0 erreur(s), 0 avertissement(s)
```

Contrôles complémentaires (script jetable de l'agent) : identifiants ASCII uniques, égaux au nom de fichier, et sans collision avec les 21 fiches de `origin/m05-liens_bien_etre` ; `socle_v1` vide ; chaque `source_serie_id` et chaque variante présents dans un catalogue INSEE, Eurostat ou M04 (y compris catalogues « non ») ; une variante principale par famille ; `sens: ambigu` ⇒ `ecarter` ; 928 lignes de la long-list affectées, somme des groupes = 932 ; chaque ligne `fiche` ou `variante_de` présente dans une fiche ; tableau de validation = fiches, colonnes de la fiche M05, `decision_leo` et `commentaire_leo` vides → **0 erreur**. Incontournables : les 4 concepts du crosswalk (homicides, sentiment d'insécurité / délinquance perçue, sécurité économique) et les tués sur la route ont une fiche `retenir`. Déclaratifs présents (9).

## 6. Livraison

PR #7 « M05 — fiches indicateurs : securite (pilote) » vers `main` (branche à jour de `main` au moment de l'ouverture) ; compte rendu copié dans le Projet (`claude/cr/M05_securite_compte_rendu.md`) et tableau de validation (`claude/40_validation_securite.csv`).

## 7. Points ouverts

- Léo : licence des séries Gallup relayées par l'OCDE (`securite_nuit`, D26) ; choix du principal pour les vols avec violence (enquête ONUDC jusqu'en 2022 ou série enregistrée jusqu'en 2024) ; maintien des soldes d'opinion Camme (4 fiches, D29 P8).
- Session mère : code de décision `autre_dimension:<dim>` ; convention `declaratif` (§2.4) ; correction de la règle 4 et de `sdg_16_10` ; demande à M04 de cataloguer les séries VRS et de corriger PE03 ; exception `tran_r_acci` à D30.
- Champ géographique du taux de tués (Eurostat et OCDE) : 3 193 tués de métropole pour un taux de 4,6 pour 100 000 impliquent une population d'environ 69 millions (France entière) : numérateur et dénominateur à vérifier auprès de l'ONISR.
