# Audit croisé M06 — dimension `niveau_de_vie`

Auditeur M06, session neuve qui n'a pas participé à M05 `niveau_de_vie`, 15 octobre 2026. Branche `m06-niveau_de_vie`, créée depuis `origin/main` au commit `792f1a5`. Les fiches ont été fusionnées par la PR #16. **Rien n'a été modifié** : aucune fiche, aucune règle, aucun tableau, aucun script, aucun catalogue. Ce rapport propose des corrections ; l'agent correcteur ou la session mère les applique. Le déroulé détaillé est dans `docs/cr/M06_niveau_de_vie_journal.md`.

**Documents lus avant l'audit**
- `CLAUDE.md` ;
- la charte, §3.4, §3.6, §4 et §5.1 ;
- le journal des décisions D13 à D36, en particulier D25, D27, D29 P8, D30, D32, D34, D35 et D36 ;
- la fiche M06 ;
- la méthode commune v1.2 (`docs/methodo/33_methode_fiches_M05.md`) ;
- `indicateurs/dimensions.yaml` : contenu et exclusions de `niveau_de_vie`, règles R1 à R8 ;
- les audits `securite`, `liens_bien_etre`, `egalites` et `democratie`.

**Matériau audité**
- les 25 fiches `indicateurs/niveau_de_vie/*.yaml` et `validation_niveau_de_vie.csv` ;
- les règles et les deux tableaux de présélection (140 règles, 11 912 lignes) ;
- le journal, le compte rendu et la liste de maintenance de M05 (`maintenance_catalogues_niveau_de_vie.md`) ;
- la long-list `niveau_de_vie` (11 821 lignes) et toutes les autres long-lists ;
- les catalogues INSEE (BDM, Melodi, y compris les fichiers `*_non`), les catalogues Eurostat (séries, jeux, `*_non`) et le catalogue M04 ;
- les sorties du robot (`docs/sources/series/`) ;
- le croisement des cadres de référence (`30_indicateurs_cadres_reference.csv` et §5 de `30_crosswalk_synthese.md`) ;
- les fiches et présélections des six autres dimensions fichées.

**Contrôles préalables**
- `pytest` : 398 tests réussis.
- `verifier_fiches.py --dimension niveau_de_vie` : 0 erreur, 7 avertissements. M05 en annonçait 5 : les deux nouveaux viennent de la fiche `egalites/ecart_revenu_median_origine`, ajoutée après M05 (§8, I2).

**Code des constats**
- **F** : erreur factuelle (la source et la valeur attendue sont citées).
- **M** : choix contraire à la méthode en vigueur lors de la rédaction (v1.1, §3 et §4).
- **A** : alignement nécessaire sur une décision postérieure (D34, D35, méthode v1.2), sans faute de M05.
- **J** : désaccord de jugement, à trancher par la session mère ou Léo.
- **O** : oubli.

---

## 1. Avis global : `corrections_necessaires` (corrections mineures et ciblées)

Le travail de M05 est solide.

- Toutes les valeurs relues à la source sont exactes : 16 lectures de l'API Eurostat, 4 séries BDM, l'Insee Première n° 2117 et les distributions DREES du robot.
- Les familles INSEE / Eurostat sont presque toutes bien arbitrées.
- Le PIB par habitant est présent comme indicateur ordinaire (A12, R7).
- Les exclusions de D25 et de `dimensions.yaml` sont respectées : la dette publique, l'investissement et le patrimoine national sont écartés, les écarts vont à `egalites`, l'endettement des ménages à `securite`.
- Les trois concepts incontournables du croisement des cadres (pauvreté monétaire relative, revenu disponible, privation matérielle) ont des fiches `retenir`.

**Réduction des comptes nationaux (D30)**

Elle est cohérente et je ne trouve **aucune série importante du niveau de vie des ménages perdue** (§5). Les mesures réelles par habitant d'Eurostat sont toutes gardées, en fiche ou en variante. L'INSEE ne publie dans les catalogues aucun niveau du revenu disponible par unité de consommation : seulement des évolutions (`_PAM_UC`, `_PAA_UC`), ce qui justifie une série principale Eurostat (D35).

**Les corrections à faire, par ordre d'importance**

1. **Choix de la série principale de `privation_alimentaire` (M).** La série Eurostat `ilc_mdes03` (2004-2025, 22 points) est plus longue de 6 ans et plus fraîche d'un an que la série INSEE ODD 2.i1 (2010-2024). Sur 2010-2024, les deux diffèrent au plus de 0,2 point. La méthode (§4, « sauf profondeur ou fraîcheur meilleure ailleurs ») désigne donc Eurostat comme principale. Les ruptures EU-SILC de 2020 et 2022 manquent aussi à la fiche.
2. **Motif d'écart de l'IDH hors méthode (M, J).** « Hors champ de la dimension » et « double compte » ne sont pas des motifs de la méthode (§3). D18 dit au contraire que le double compte des composites se traite au contrôle de redondance. Et `egalites` retient un composite du PNUD de même nature (`coefficient_inegalite_humaine`).
3. **Deux lignes de privation liée au logement rangées en variantes de la privation sévère (F).** `ilc_mdho06q` est la « Severe housing deprivation rate by income quintile » (API Eurostat). Ces lignes vont à `logement_cadre_vie`, comme `ilc_mdho06a`. C'est la vérification que demandait la ligne de maintenance NDV-5.
4. **`pauvrete_ancree_2008` (F).** Les valeurs sont désormais lues : 2008-2025, ruptures (drapeau `b`) en 2020 et 2022. La hausse de 12,5 % à 15,6 % se concentre sur ces deux années de rupture. La phrase « porte la même information que le premier décile » est donc à nuancer.
5. **Baromètre DREES (F, A).** Des ruptures possibles manquent :
   - pour `pauvrete_percue_hausse` (PE01), en 2007 et 2014 ; c'est le même schéma que `egalites/inegalites_percues_hausse` (IN02), déjà corrigée ;
   - pour `pauvrete_ressentie` (PE03), en 2018, comme sur la fiche sœur `securite/risque_pauvrete_ressenti`.

   Le recoupement exigé par D34 reste aussi à documenter.
6. **Lignes orphelines (I1).** Sur les 695 lignes renvoyées à d'autres dimensions, 537 visent des dimensions déjà fichées qui ne les ont pas reprises :
   - `egalites` 165 et `travail` 349 ;
   - `securite` 19, dont **tout l'endettement des ménages** ;
   - `planete` 4.

   La session mère doit trancher (§8).

**Chiffres**
- **25 fiches auditées** : 21 dans l'échantillon réglementaire, plus les 4 restantes relues.
- **18 `conforme`**, dont 5 avec une réserve (valeurs Melodi illisibles par l'outil, aucune n'est citée par la fiche), et **7 `a_corriger`**. Aucune fiche `non_verifiable`.
- **6 corrections transversales**, **5 oublis** (aucun de fond imputable à M05), **9 points de cohérence entre dimensions**, **6 désaccords de jugement**.

La liste ordonnée des corrections est au §10. Aucune correction ne remet en cause les 17 fiches `retenir`.

## 2. Échantillon

| Règle | Fiches |
|---|---|
| `recommandation: ecarter` (2) | `indice_developpement_humain`, `taux_epargne_menages` |
| `incontournable: oui` (6) | `niveau_vie_median`, `privation_materielle_sociale`, `privation_materielle_sociale_severe`, `revenu_disponible_ajuste_habitant`, `taux_pauvrete_50`, `taux_pauvrete_60` |
| `eligibilite_longlist: a_verifier` (2) | `patrimoine_net_median`, `satisfaction_situation_financiere` |
| Signalées au journal M05 : valeurs non lues (1), hors long-list (1), `raccordement: a_etudier` (3 de plus) | `pauvrete_ancree_2008`, `pauvrete_percue_hausse`, `pauvrete_exclusion_arope`, `privation_alimentaire`, `taux_pauvrete_enfants` |
| Point d'attention D30, demandé par la session mère : fiches issues des comptes nationaux (5 de plus) | `pib_habitant` (D25), `revenu_national_habitant`, `consommation_effective_habitant`, `depenses_pre_engagees`, `pouvoir_achat_uc` |
| 20 % des 5 « autres » fiches, soit 1 | `intensite_pauvrete` |

- **Tirage** : `random.Random(20261015).sample(sorted(autres), 1)` avec la **graine 20261015**, parmi `difficulte_joindre_deux_bouts`, `intensite_pauvrete`, `niveau_vie_modestes`, `pauvrete_persistante` et `pauvrete_ressentie`.
- **Total de l'échantillon** : 21 fiches.
- **Fiches hors échantillon** : les 4 restantes ont été relues avec la même exigence, parce que les sources Eurostat et DREES étaient déjà ouvertes. Elles figurent au tableau avec la mention « hors échantillon ».

## 3. Tableau des fiches auditées

Toutes les sources ont été lues le 15/10/2026. Le détail est au §4 et les URL sont en annexe.

| Fiche | Motif d'échantillon | Source consultée | Verdict | Nature | Correction attendue (résumé) |
|---|---|---|---|---|---|
| `indice_developpement_humain` | ecarter | extrait PNUD du robot | **a_corriger** | M, A, (J1) | Motif conforme à la méthode, ou recommandation revue ; `annee_reference: observation` |
| `taux_epargne_menages` | ecarter | API `nasa_10_ki` SRG_S14_S15 | conforme | — | Remarque : le motif cite des valeurs Eurostat (ménages et ISBLSM) pour une principale INSEE (ménages) |
| `niveau_vie_median` | incontournable | Insee Première n° 2117 ; catalogue Melodi | conforme | (J2) | — |
| `privation_materielle_sociale` | incontournable | BDM 010594486 ; API `ilc_mdsd07` | **a_corriger** (mineur) | F | Citer les valeurs de la principale INSEE ; documenter l'écart avec EU-SILC (jusqu'à 1,2 point avant 2020) |
| `privation_materielle_sociale_severe` | incontournable | API `ilc_mdsd11`, `ilc_mdho06q` | **a_corriger** (mineur) | F | Retirer les 2 variantes `ilc_mdho06q` (privation liée au logement) |
| `revenu_disponible_ajuste_habitant` | incontournable | API `nasa_10_nf_tr` ; métadonnées | conforme | — | Remarque : déflateur = prix de la consommation finale effective des ménages et ISBLSM (métadonnées) |
| `taux_pauvrete_50` | incontournable | catalogue Melodi ; croisement des cadres | conforme | — | — |
| `taux_pauvrete_60` | incontournable | Insee Première n° 2117 ; API `ilc_li02` | conforme | (A) | Ventilation par sexe à renvoyer à `egalites` (D35, T2) |
| `patrimoine_net_median` | a_verifier | catalogue Melodi | conforme | — | Réserve : valeurs non lues (aucune n'est citée) |
| `satisfaction_situation_financiere` | a_verifier | API `ilc_pw01b` ; catalogue `DS_SRCV_SATISFACTION` | conforme | — | — |
| `pauvrete_ancree_2008` | valeurs non lues | API `ilc_li22b` | **a_corriger** | F, (J4) | `rupture_2020`, `rupture_2022`, retirer `valeurs_non_lues` ; nuancer « même information » ; raccordement (série toujours publiée) |
| `pauvrete_percue_hausse` | hors long-list | distributions et tableaux 2025 de la DREES | **a_corriger** (mineur) | F, A | `rupture_possible_2007`, `anomalie_2014`, `non_recoupe_2000_2024` (D34) |
| `pauvrete_exclusion_arope` | a_etudier | API `sdg_01_10` ; croisement des cadres (cible) | conforme | (A) | `annee_reference` (T1) |
| `privation_alimentaire` | a_etudier | BDM 010594393 ; API `ilc_mdes03` | **a_corriger** | M, F | Série principale Eurostat `ilc_mdes03` (méthode §4), INSEE en variante ; `rupture_2020`, `rupture_2022` |
| `taux_pauvrete_enfants` | a_etudier | catalogue Melodi ; BDM 010594449 | conforme | (O4) | Réserve : valeurs ERFS non lues (aucune n'est citée) |
| `pib_habitant` | D30, D25 | BDM 011779993 | conforme | — | — |
| `revenu_national_habitant` | D30 | catalogue Melodi | conforme | — | Réserve : valeurs non lues ; métadonnées contradictoires « prix courants » et « termes réels » (T6) |
| `consommation_effective_habitant` | D30 | API `nama_10_pc` P41 | conforme | — | — |
| `depenses_pre_engagees` | D30 | catalogue Melodi | conforme | — | Réserve : valeurs non lues (aucune n'est citée) |
| `pouvoir_achat_uc` | D30 | catalogue Melodi | conforme | — | Réserve : idem |
| `intensite_pauvrete` | tirage | Insee Première n° 2117 ; catalogue Melodi | conforme | — | — |
| `difficulte_joindre_deux_bouts` | hors échantillon | API `ilc_sbjp01`, `ilc_mdes09` (GRT, DIF) | conforme | — | Remarque : valeur 2004 atypique (raccordement) |
| `niveau_vie_modestes` | hors échantillon | Insee Première n° 2117 | conforme | — | — |
| `pauvrete_persistante` | hors échantillon | API `ilc_li21` | conforme | — | — |
| `pauvrete_ressentie` | hors échantillon | distributions et tableaux 2025 de la DREES | **a_corriger** (mineur) | F, A | `rupture_possible_2018`, `non_recoupe_2014_2023` ; `source_serie_id` et `url_api` alignés sur la fiche sœur de `securite` ; note NDV-4 périmée |

## 4. Détail des vérifications par fiche

Les valeurs entre parenthèses ont été lues à la source le 15/10/2026 : API Eurostat ou BDM par l'outil de lecture, Insee Première, sorties du robot dans `docs/sources/series/`. L'API Melodi est refusée à l'outil (robots.txt) : pour les séries Melodi, l'identifiant, le libellé, la zone et la période sont vérifiés dans le catalogue Melodi, qui est produit par le robot depuis l'API.

### 4.1 Fiches écartées

**`indice_developpement_humain`** — Extrait du robot `pnud__hdr25_series_composites_france.csv` : `hdi` couvre 1990-2023 (34 périodes, dont 24 depuis 2000), avec 0,92 en 2023 ✓. L'identifiant, la période et l'unité sont exacts. Trois problèmes :

1. **M.** Le motif d'écart (« hors champ de la dimension […] (D18, double compte) ») ne figure pas parmi les motifs de la méthode (§3) : sens ambigu, hors champ **v1** (A4, R4, R6), série dominée, série arrêtée. Il contredit aussi D18 : « indices composites admis avec drapeau `composite: oui` ; **le double comptage se traite au contrôle de redondance** ». Enfin, `egalites` retient `coefficient_inegalite_humaine`, un composite multidomaine du même rapport du PNUD, « composite admis par D18 ».
2. **A.** Il manque `annee_reference: observation` (D34, méthode v1.2) : `hdi_2023` est l'année observée dans l'édition 2025.
3. **Remarque.** La note dit que « l'indice ajusté aux inégalités n'est pas au catalogue ». C'est exact pour le catalogue, mais l'IDHI (`ihdi`, 2010-2023, 0,836 en 2023) figure déjà dans la sortie du robot et pourrait être une variante avec `preuve`.

Correction attendue :
- soit `recommandation: retenir` (famille propre `indice_developpement_humain`, `composite: oui`), la redondance étant laissée au contrôle du gel 2, comme pour le coefficient d'inégalité humaine ;
- soit un motif de la méthode, ou une règle nouvelle de la session mère (« composite multidimensionnel qui recouvre plusieurs dimensions de la grille → repère externe »), voir J1.

**`taux_epargne_menages`** — `nasa_10_ki` SRG_S14_S15 vaut 13,07 (2000), 15,73 (2009), 14,24 (2019), 20,03 (2020), 18,67 (2021) et 17,93 (2024, provisoire) ✓. `sens: ambigu` et l'écart qui en découle sont conformes à la méthode (§3). Remarque : le motif et la note citent la série Eurostat des ménages **et ISBLSM**, alors que la principale est la mesure INSEE des ménages seuls (`REF_SECTOR=S14`). Il faut le dire ou citer l'INSEE. Conforme.

### 4.2 Incontournables

**`revenu_disponible_ajuste_habitant`** — `nasa_10_nf_tr`, B7G_R_HAB, S14_S15, RECV : 21 496 (2000), 26 280 (2019), 25 849 (2020), 27 882 (2024) ✓, sans drapeau.
- L'API étiquette bien l'unité « Current prices, million units of national currency », alors que la grandeur est en euros réels par habitant : l'incohérence vient d'Eurostat, et NDV-1 la signale à juste titre.
- Les métadonnées de `nasa_10_nf_tr` donnent le déflateur : « implicit deflator […] household and NPISH actual final consumption (S.14_S.15_P4) ». La définition de la fiche est donc exacte. L'année de référence des prix n'est donnée que pour l'indice (2010 = 100), d'où le drapeau `annee_de_reference_des_prix_non_trouvee`, justifié.
- La série existe depuis 1975 ; `premiere_annee: 2000` suit la long-list, comme le veut la méthode (§4).
- Concept du croisement des cadres (SSF, OCDE 1_1, Eurostat) ✓ ; D35 (Eurostat principal quand l'INSEE ne publie pas le niveau) ✓.

Conforme.

**`niveau_vie_median`, `taux_pauvrete_60`, `taux_pauvrete_50`** (et `niveau_vie_modestes`, `intensite_pauvrete`, §4.6)
- L'Insee Première n° 2117 (9 juillet 2026, page `https://www.insee.fr/fr/statistiques/9019316`) donne pour 2024 :
  - une médiane de 26 740 € par UC et par an, soit 2 228 € par mois (+1,8 % en euros constants) ✓ ;
  - un premier décile de 13 970 € (+1,7 %) ✓ ;
  - un taux de pauvreté de 15,4 %, soit 9,8 millions de personnes, pour un seuil de 1 337 € par mois ✓ ;
  - une intensité de 19,7 % (+0,5 point) ✓.
- Le champ (France métropolitaine, logements ordinaires, personne de référence non étudiante) et la rétropolation jusqu'en 1996, « malgré des ruptures en 2010, 2012 et 2020 », confirment `raccordement: non` et `qualite: champ_metropole_menages_ordinaires`.
- Les mesures `MED_SL`, `PR_MD60`, `PR_MD50`, `D1_SL` et `PI_MD60` figurent bien au catalogue Melodi (1996-2024, 25 points depuis 2000).
- Les seuils de 50 % de l'OCDE (1_4) et du Doughnut (pauvreté sociétale) sont au croisement des cadres ✓.
- EU-SILC `ilc_li02` (B_60, total) : drapeaux `b` en **2001, 2004, 2020 et 2022**, aucun en 2008 (§6, T5). La fiche n'en cite correctement que 2020 et 2022.

Les trois fiches sont conformes. Pour `taux_pauvrete_60`, voir T2 (D35).

**`privation_materielle_sociale`** — La BDM 010594486 (FM, mise à jour du 27/05/2026) donne : 11,7 (2013), 12,9 (2014), 11,8 (2015), 12,1 (2016), 11,4 (2017), 11,9 (2018), 12,4 (2019), 12,3 (2020), 10,5 (2021), 12,9 (2022), 13,1 (2023), 12,7 (2024), 2025 sans valeur. La période 2013-2024 (12 points) et la zone FM sont donc exactes ✓.

**F (mineur)** : la note cite les valeurs d'EU-SILC (`ilc_mdsd07` : 14,1 en 2014, 10,5 en 2021, 13,3 en 2025, drapeau `b` en 2020 et 2022 ✓) comme celles de « la même mesure ». Or les deux séries diffèrent de 0,7 à 1,2 point de 2014 à 2019 (12,9 contre 14,1 en 2014, 12,4 contre 13,1 en 2019), puis de 0 à 0,4 point à partir de 2020. Par ailleurs, les ventilations BDM par sexe et par âge ne commencent qu'en 2020. Tout cela suggère que l'INSEE a rétropolé la série totale 2013-2019 lors de la rénovation de SRCV en 2020, mais cette hypothèse n'est pas vérifiée. Correction attendue :
- citer les valeurs de la principale INSEE ;
- remplacer « Eurostat publie la même mesure » par « même concept, valeurs différentes avant 2020 » ;
- vérifier dans la documentation de l'INSEE si la série est rétropolée. Si c'est le cas, le drapeau `rupture_eu_silc_2020_2022` ne s'applique pas à la principale.

Le choix de l'INSEE (un an de profondeur contre un an de fraîcheur) reste défendable.

**`privation_materielle_sociale_severe`** — `ilc_mdsd11` : 6,8 (2015), 7,3 (2019), 6,4 (2020, `b`), 5,5 (2021), 7,0 (2022, `b`), 7,0 (2025) ✓. La période (2015-2025, 11 points) est exacte, et la variante de raccordement `ilc_mddd11` (2004-2020) est bien au catalogue.

**F** : la règle 740 range en variantes les 2 lignes `ilc_mdho06q` (`estat-031859`, `estat-031860`) sous le libellé erroné du catalogue (« Taux de privation matérielle sévère par quintile de revenu »). Or l'API donne « **Severe housing deprivation rate by income quintile** » : 3,4 % en 2004, 2,3 % en 2019, 3,8 % en 2020 (`b`), 4,6 % en 2023, sans valeur en 2021-2022. C'est de la privation liée au logement. Correction attendue :
- retirer `ilc_mdho06q` de la règle 740 et l'ajouter à la règle 760 (`privation_logement`, `autre_dimension:logement_cadre_vie`) ;
- retirer les 2 variantes de la fiche ;
- clore NDV-5 en « vérifié : libellé du catalogue à corriger ».

### 4.3 Fiches « à vérifier » et signalées au journal M05

**`patrimoine_net_median`** — Catalogue Melodi : `DS_ENQPAT_DET`, « Montant de patrimoine net hors reste (en euros constants) ; Decile_5 », FRANCE-FM, 2010-2024, 5 points ✓. D5 seul, sans tranche, désigne bien la médiane. L'écart moyen de (2024 − 2010) / 4 = 3,5 ans remplit la condition de D17 et D28 ✓. Conforme, avec une réserve : valeurs non lues, mais la fiche n'en cite aucune.

**`satisfaction_situation_financiere`** — `ilc_pw01b` FIN, moyenne, 16 ans ou plus : 6,4 (2013), 6,6 (2018), 6,4 (2022) ✓, sans drapeau. Le catalogue confirme que `DS_SRCV_SATISFACTION` ne contient que `VIESATISF`, `RELSATISF` et `TRAVSATISF` ✓. R4, D17 (écart moyen de 4,5 ans) et `declaratif: oui` sont corrects. Conforme.

**`pauvrete_ancree_2008`** — M05 n'avait pas pu lire `ilc_li22b` (réponse 429). Valeurs lues, pour le total des deux sexes et des âges :

| Années | Valeurs |
|---|---|
| 2008-2012 | 12,5 · 12,5 · 12,3 · 13,7 · 13,8 |
| 2013-2017 | 13,4 · 12,9 · 13,0 · 12,3 · 11,8 |
| 2018-2022 | 11,9 · 12,1 · **14,2 `b`** · 13,4 · **15,0 `b`** |
| 2023-2025 | 15,1 · 15,8 · 15,6 |

La période (2008-2025, 18 points) est exacte, et le jeu a été mis à jour le 05/10/2026 : **la série est toujours publiée**. Corrections (**F**) :
1. `qualite` : remplacer `valeurs_non_lues` et `rupture_eu_silc_2020_2022_a_verifier` par `rupture_2020` et `rupture_2022`.
2. Note : la hausse totale de 2008 à 2025 (+3,1 points) se concentre sur les deux années de rupture (+2,1 en 2020, +1,6 en 2022). Hors ruptures, la série baisse de 0,6 point. La phrase « porte la même information que le premier décile en euros constants » est à remplacer par une formulation qui signale cette dépendance aux ruptures. Voir aussi J4.
3. `raccordement` : la série n'est pas arrêtée. « `ilc_li22` pourrait lui succéder » devient « autre ancrage (2019) disponible » ; NDV-6 est résolu.

**`pauvrete_percue_hausse`** (PE01, hors long-list, `preuve` présente)

Valeurs de la modalité 2, d'après les distributions du robot :

| Année | 2000 | 2006 | 2007 | 2013 | 2014 | 2015 | 2025 |
|---|---|---|---|---|---|---|---|
| Valeur (%) | 73,22 | 84,81 | 83,41 | 92,45 | 88,53 | 90,86 | 92,08 |

- Couverture : 2000-2002 et 2004-2025 ✓.
- Recoupement : la valeur 2025 (92,08 %) est identique au tableau croisé publié par la DREES pour 2025 (`drees__barometre_tc_simplifies_2025.txt`). Dans ce tableau, la modalité « (Sont restées stables) » est entre parenthèses, donc **spontanée**.
- Cette modalité vaut de 8,5 à 18,9 % de 2000 à 2006, chute à 4,8 % en 2007, puis reste entre 2,5 et 5,4 %, sauf en 2014 (7,67 %), année où la modalité 2 recule de 4 points.

C'est exactement le schéma relevé sur IN02 par l'audit `egalites` (T3) et corrigé dans `egalites/inegalites_percues_hausse` (`rupture_possible_2007`, `anomalie_2014`). Corrections :
- **F** : ajouter `rupture_possible_2007` et `anomalie_2014` à `qualite`, avec une phrase dans la note ;
- **A** : D34 exige un recoupement avec au moins 3 valeurs officielles avant `retenir`, et 1 seule est recoupée. Il faut ajouter `non_recoupe_2000_2024`, comme `securite/risque_pauvrete_ressenti`, et recouper deux valeurs de plus avec les publications de la DREES, ou bien la session mère accepte l'alignement sur `securite` (Q3) ;
- **A** : ajouter `licence_a_confirmer`, par alignement sur les fiches DREES de `securite` et `travail`.

**`pauvrete_exclusion_arope`** — `sdg_01_10` : 18,4 (2015) ; 19,0 (2020, `b`) ; 20,7 (2022, `b`) ; 20,8 (2025) ✓. La période (2015-2025, 11 points) est exacte. La cible française (−1,1 million de personnes en 2030 par rapport à 2019) est au croisement des cadres ✓. La variante de raccordement `ilc_peps01` (2004-2020) figure à la long-list. Conforme ; `annee_reference` manque pour un composite (T1).

**`privation_alimentaire`** — Comparaison des deux séries, d'après la BDM 010594393 (INSEE ODD 2.i1, FM) et l'API Eurostat `ilc_mdes03` (total) :

| Année | INSEE (%) | Eurostat (%) |
|---|---|---|
| 2004 | — | 6,7 |
| 2010 | 6,9 | 6,9 |
| 2019 | 7,6 | 7,5 |
| 2020 | 7,3 | 7,2 `b` |
| 2021 | 6,3 | 6,3 |
| 2022 | 9,4 | 9,5 `b` |
| 2023 | 12,3 | 12,2 |
| 2024 | 10,0 | 10,2 |
| 2025 | — (sans valeur) | 11,2 |

Sur les 15 années communes, l'écart ne dépasse jamais 0,2 point.

1. **M** : la méthode (§4) dit « INSEE > Eurostat > autres à définition égale, **sauf profondeur ou fraîcheur meilleure ailleurs** ». La série Eurostat est plus profonde de 6 ans et plus fraîche d'un an, pour des valeurs identiques à 0,2 point près. Correction attendue : série principale `ilc_mdes03` (`estat-031704`, long-list `planete`, avec `rattachement_propose` déjà rédigé, maintenance n° 35), l'INSEE 2.i1 et sa copie Melodi en variantes, `raccordement: non`. À défaut, motiver explicitement la dérogation.
2. **F** : la principale actuelle reprend les valeurs EU-SILC, ruptures comprises (2021 → 2022 : +3,1 points). Il faut ajouter `rupture_2020` et `rupture_2022`.

Le choix d'une fiche distincte de la privation matérielle et sociale (D32, préoccupation publique propre) est approuvé.

**`taux_pauvrete_enfants`**
- Le catalogue Melodi confirme `DS_ERFS_NON_RETROPOLE`, AGE=Y_LT18, `COMPARE_TIME=NB`, 1996-2024, 22 points depuis 2000 : les 3 valeurs manquantes sont celles des années de rupture 2010, 2012 et 2020, publiées en BWA et BWB.
- La variante ODD (BDM 010594449, FM) donne 19,3 (2010), 20,3 (2012), 19,6 (2020), 21,9 (2023, révisée), 2024 sans valeur.
- Les ruptures de `qualite` sont exactes et le motif (D32, cible européenne relative aux enfants) est fondé.

Conforme, avec une réserve : valeurs ERFS non lues, mais aucune n'est citée. Voir O4 sur les variantes EU-SILC des enfants.

### 4.4 Fiches issues des comptes nationaux (D30)

**`pib_habitant`** — BDM 011779993 : « Produit intérieur brut par habitant […] Prix chaîné année de base », EUROS_HABITANTS, zone FE. Valeurs : 6 742 (1949), 32 028 (2000), 37 163 (2019), 34 235 (2020), 38 176 (2024, statut SD), 38 360 (2025, statut P) ✓. La période 1949-2025, l'unité (euros de 2020 chaînés par habitant) et la zone FE sont exactes. Le rattachement A12 et R7 est respecté, et l'INSEE est principal à définition égale ✓. Conforme. Remarque : `valeurs_provisoires_2025` pourrait être ajouté, comme pour la consommation.

**`consommation_effective_habitant`** — `nama_10_pc` P41, CLV20_EUR_HAB : 21 150 (2000), 25 660 (2019), 23 920 (2020), 26 190 (2024, `p`), 26 250 (2025, `p`) ✓. Conforme.

**`revenu_national_habitant`** — Catalogue Melodi : `_RNB_REEL_HABITANT`, « Revenu national brut en termes réels par habitant », 1949-2025 ✓. Les métadonnées de la ligne sont contradictoires : `PRICES=V` (« en valeur aux prix courants ») et « Devise nationale (Euros) », alors que le nom de la mesure dit « termes réels ». Conforme, avec une réserve (valeurs non lues) ; ajouter `annee_de_reference_des_prix_non_trouvee` (T6).

**`depenses_pre_engagees`, `pouvoir_achat_uc`** — Catalogue Melodi : `_DEP_REVENU` (« Part de la dépense pré-engagée dans le revenu disponible brut », Territoire national, 1959-2025) et `_PAM_UC` (« Pouvoir d'achat du rdb par unité de consommation ; Croissance annuelle », 1960-2025) ✓. La famille `revenu_disponible_menages` (niveau Eurostat principal, évolution INSEE en fiche distincte) respecte la méthode (§1) : une autre statistique, lue autrement et avec d'autres bornes, devient une fiche. Conformes, avec une réserve : valeurs non lues, mais aucune n'est citée.

### 4.5 Tirage

**`intensite_pauvrete`** — Insee Première n° 2117 : 19,7 % en 2024, +0,5 point ✓. La mesure `PI_MD60` (1996-2024) est au catalogue. Indicateur ODD 1.i3 : les variantes BDM 010594492 et 010594493 (2010-2023) sont au catalogue ✓. Conforme.

### 4.6 Fiches hors échantillon relues

**`difficulte_joindre_deux_bouts`** — `ilc_sbjp01` : 20,2 (2010), 18,1 (2017), 16,9 (2019), 18,5 (2020), 16,5 (2021), 21,7 (2022), 22,2 (2023), 21,8 (2024 et 2025) ✓.

| `ilc_mdes09` | 2004 | 2005 | 2013 | 2021 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| « Grande difficulté » (GRT) | 6,1 | 3,1 | — | — | 8,3 | 8,0 |
| « Difficulté » (DIF) | 11,6 | — | 16,1 | 11,0 | — | — |

Les deux modalités portent le drapeau `b` en 2020 et 2022. **La somme GRT + DIF égale `ilc_sbjp01` à 0,1 point près sur les 16 années 2010-2025** : le raccordement « oui » est vérifié. `declaratif: oui` est motivé et cohérent avec l'OCDE (1_5). Conforme. Remarque : la valeur GRT de 2004 (6,1, puis 3,1 en 2005) est atypique, et la première vague française d'EU-SILC mérite un drapeau `anomalie_2004_possible` si le raccordement est utilisé.

**`niveau_vie_modestes`** — 13 970 € et +1,7 % en 2024 ✓ (Insee Première n° 2117). Conforme. Remarque : « seule mesure absolue du bas de la distribution » serait plus exact en « seule mesure en euros constants », puisque le taux ancré est aussi absolu.

**`pauvrete_persistante`** — `ilc_li21` : 6,4 (2007, `b`), lacune 2008-2010, 7,1 (2011), 8,5 (2015), 9,3 (2022), 7,1 (2023), 10,4 (2024), 10,3 (2025, `b`) ✓. Conforme.

**`pauvrete_ressentie`** (PE03, modalité 3) — Valeurs de la modalité 3 : 7,87 (2014), 12,38 (2015), 17,12 (2018), 18,71 (2022), 19,24 (2023), 17,41 (2025) ✓. La valeur 2025 est recoupée avec le tableau croisé publié (17,41 %). Pas de vague en 2024 ✓. Corrections :
- **F** : les non-réponses passent de 1,35 % (2017) à **6,08 %** (2018) et restent entre 6,2 et 7,8 % ensuite. Au même moment, la modalité 3 passe de 12,65 à 17,12 %. La fiche sœur `securite/risque_pauvrete_ressenti`, corrigée, porte `rupture_possible_2018` pour la même question : il faut l'ajouter ici.
- **A** : `non_recoupe_2014_2023` et `licence_a_confirmer` (D34, alignement sur `securite`).
- **F (forme)** : `source_serie_id` cite deux pièces jointes et `url_api` vaut « non trouvé », alors que `pauvrete_percue_hausse` et la fiche sœur visent la pièce jointe unique `barometre2000_2025_diff_csv`, dont l'URL est connue. Il faut aligner `url_api` ; pour `source_serie_id`, voir la contrainte du vérificateur (Q6).
- La note sur la maintenance n° 3 est périmée : SEC-2 a abandonné la somme des modalités 1 et 3. Elle est à réécrire.

## 5. Réduction des comptes nationaux (D30) : contrôle

**Couverture.** Les règles 1200 à 1310 traitent par jeu et par mesure environ 7 900 lignes : Melodi `DD_CNA_*`, BDM, Eurostat `nasa_*`, `nama_*`, `naida_*`, `gov_*` et `prc_ppp_*`. J'ai relu mesure par mesure tout `DD_CNA_AGREGATS` (codes STO × secteur) et tous les `na_item` de `nasa_10_nf_tr`, `nasa_10_ki`, `nama_10_pc` et `naida_10_gdp` présents dans la long-list.

**Ce qui est gardé**
- Les trois mesures réelles par habitant d'Eurostat :
  - B7G_R_HAB, en série principale ;
  - B6G_R_HAB et P4_R_HAB, en variantes ;
  - leurs indices et taux de croissance (`nasa_10_ki`, en variantes).
- Le PIB et la consommation par habitant (`nama_10_pc`, `sdg_08_10`, `prc_ppp_ind`).
- Le revenu national, brut et net, et le revenu disponible de la nation (`naida_10_gdp`, INSEE, Banque mondiale).
- Toutes les mesures INSEE par UC, qui ne sont que des évolutions : `_PAM_UC`, `_PAA_UC`, `_PAM_MENAGE`, `_PAM_PERSONNE`…
- Le taux d'épargne et le taux d'épargne financière, les dépenses pré-engagées, et la valeur nette du patrimoine des ménages.

**Ce qui est écarté**
- Les comptes des administrations publiques (A5).
- Les secteurs autres que les ménages (D29 P6).
- Les opérations techniques des ménages (B1 à B5, D1 à D9, P5…).
- Le patrimoine par actif.
- La consommation par produit et les niveaux de prix.
- Les comptes trimestriels.

Les motifs sont exacts. **Je ne trouve aucune série perdue qui mesure le niveau de vie des ménages.** Le constat de M05 se vérifie : l'INSEE ne publie aux catalogues aucun niveau du revenu disponible par UC ou par habitant (NDV-9).

**Familles.** Cinq familles sont issues des comptes nationaux : `revenu_disponible_menages`, `pib_habitant`, `consommation_menages`, `depenses_pre_engagees` et `taux_epargne_menages`. Elles sont cohérentes avec D35 : famille = concept substituable, Eurostat principal quand l'INSEE ne publie pas le niveau. Deux remarques mineures :
- **(a)** Les valeurs nationales des jeux régionaux (`nama_10r_2gdp`, `nama_10r_2hhinc`) sont gardées en variantes. D30 prévoit de les exclure au niveau 1 lors de la prochaine maintenance de M02 ; elles disparaîtront alors des fiches.
- **(b)** Les agrégats INSEE totaux (en millions d'euros) sont des variantes de séries principales par habitant. C'est admis (une « autre unité »), mais ces variantes n'apportent rien de lisible au gel 2 ; la question 4 de M05 (alléger les variantes) s'applique.

## 6. Corrections transversales

| # | Fiches ou fichiers | Constat | Source | Correction |
|---|---|---|---|---|
| T1 | `indice_developpement_humain`, `pauvrete_exclusion_arope` | Composites sans `annee_reference` (D34, méthode v1.2) | méthode §9 | `annee_reference: observation`. Pour l'AROPE, préciser dans la note que la composante monétaire porte sur les revenus de l'année N − 1 |
| T2 | `taux_pauvrete_60` (`estat-000033`, `ilc_li02` par sexe) | D35 : la ventilation par sexe est renvoyée à `egalites` quand l'écart y existe déjà (`ecart_pauvrete_fh`) | méthode §9 (D35) | Règle `autre_dimension:egalites` pour `estat-000033` ; un avertissement R1 de moins. Les lignes par âge et par nationalité restent des variantes (D32) |
| T3 | `niveau_vie_median` (5 variantes), `niveau_vie_modestes` (1) | Variantes importées de la long-list `egalites` sans `rattachement_propose`, alors que `privation_alimentaire` en porte un pour ses imports de `planete` | méthode §4 | Ajouter `rattachement_propose` (lignes renvoyées par `egalites`, maintenance n° 11), ou écrire dans la méthode qu'il n'est exigé que pour la série principale |
| T4 | `docs/cr/maintenance_catalogues_niveau_de_vie.md` | NDV-5 vérifié (privation liée au logement) ; NDV-6 résolu (`ilc_li22b` publié jusqu'en 2025) ; **NDV-10 à clore** ; NDV-4 périmé (SEC-2) ; NDV-1 : déflateur trouvé dans les métadonnées | API Eurostat, métadonnées `nasa_10_nf_tr` | Mettre à jour les statuts lors de la consolidation de la liste partagée. NDV-10 : `sdg_10_20` est devenu « Disparities in adjusted gross disposable income of households per capita », en coefficient de variation entre pays (unité CVA), sans aucune zone nationale. Le catalogue (`sans_donnee_fr`) a raison et le niveau français est déjà lu dans `nasa_10_nf_tr` |
| T5 | Compte rendu M05 §3.2, journal M05 §2.2 | « EU-SILC […] ruptures en 2008, 2020 et 2022 » | API `ilc_li02` (B_60, total) | Ruptures en 2001, 2004, 2020 et 2022 ; aucune en 2008 pour ce jeu |
| T6 | `revenu_national_habitant` | Unité « termes réels » alors que la ligne porte `PRICES=V` et « Devise nationale » ; année de référence des prix inconnue | catalogue Melodi | `qualite: annee_de_reference_des_prix_non_trouvee`, une phrase dans la note |

## 7. Complétude : oublis

La couverture de la long-list est exhaustive : 11 821 lignes, aucune sans règle. Sur les 7 874 lignes éligibles :

| Décision | Lignes |
|---|---|
| Série principale d'une fiche | 22 |
| Variante | 1 161 |
| Renvoyée à une autre dimension | 549 |
| Écartée en bloc | 6 142 |

Les écarts en bloc ont été relus groupe par groupe (§5 et règles 270 à 1400). Je ne conteste aucun motif, sauf la règle 740 (`ilc_mdho06q`, §4.2).

| # | Oubli | Données lues | Importance | Proposition |
|---|---|---|---|---|
| O1 | **Opinion sur le niveau de vie en France**, évolution passée et perspectives : enquête de conjoncture auprès des ménages, BDM 000857176, 000857177, 000857188, 000857189 (mensuelles, 1970-2026, éligibles mais classées `hors_grille`) | catalogue BDM | moyenne | Pas une faute de M05 : D29 P8 classe ces soldes hors grille, et M05 a posé la question (§7.3 de son compte rendu). Mais D32 (opinions sur la société, fiches de familles distinctes) a conduit à retenir PE01, de même nature : la session mère tranche (Q1). En cas d'admission, retenir une série par horizon (passé, perspectives) après lecture des titres complets des quatre séries (traitement saisonnier), en moyenne annuelle |
| O2 | **Insécurité alimentaire modérée ou grave** (échelle FIES, ODD 2.1.2, Doughnut ; croisement des cadres : « FAO publie l'ODD 2.1.2 pour la France (à vérifier) ») | Aucune ligne dans les catalogues (INSEE, Eurostat, M04 recherchés). API Banque mondiale `SN.ITK.MSFI.ZS` **non lue** : la demande d'autorisation est restée sans réponse | moyenne (A2) | Garder NDV-7 ; vérifier l'API de la FAO ou de la Banque mondiale depuis le robot. Si la série existe, fiche hors long-list `retenir_variante` dans une famille `acces_alimentation` avec la privation alimentaire |
| O3 | **Perception de l'évolution future de la pauvreté** (DREES PE02, 25 vagues 2000-2025, modalité « vont plutôt augmenter » de 64,95 % en 2000 à 91,54 % en 2025) | distributions du robot | faible | La note de `pauvrete_percue_hausse` l'écarte sans motif de la méthode (« même construction »). En faire une variante ou une famille distincte (D32), comme `securite` le fait pour les soldes passé et futur de la situation financière |
| O4 | Pauvreté des enfants dans EU-SILC (`ilc_li02` Y_LT18, 2004-2025, dans un paquet de la ligne `estat-000034`) et AROPE des enfants (`sdg_01_10a`) : pas en variantes de `taux_pauvrete_enfants` | long-list | faible | Mention dans la note : la série EU-SILC, sans trou aux années de rupture, est un relais possible des valeurs BWA et BWB |
| O5 | IDH ajusté aux inégalités (`ihdi`, PNUD, 2010-2023) | extrait du robot | faible | Variante avec `preuve` si l'IDH est retenu (§4.1) |

**Comparaison avec le croisement des cadres (§5).** Les concepts présents dans au moins trois cadres ont tous des fiches `retenir` marquées `incontournable: oui` : pauvreté monétaire relative (5 cadres), revenu disponible des ménages (3), privation matérielle (3). Les autres indicateurs des cadres sont couverts :
- **SSF** : revenu, consommation, patrimoine, pauvreté, revenu national ;
- **OCDE** : 1_1, 1_3, 1_4, 1_5 en fiches ou en variantes, 1_6 en `securite` ;
- **Eurostat QoL** : médiane, taux de pauvreté, taux ancré, satisfaction financière, consommation effective, joindre les deux bouts, privation sévère ;
- **INSEE NIR** : n° 7 et taux de pauvreté ;
- **objectif officiel** : AROPE.

Le seul concept du Doughnut sans mesure est l'insécurité alimentaire (O2).

Les déclaratifs demandés par la session mère sont présents : difficulté à joindre les deux bouts, pauvreté ressentie, satisfaction financière, perception de la hausse de la pauvreté. Dans le baromètre DREES, j'ai écarté les autres questions candidates :
- SDSITFIN (« situation financière du foyer », 2021-2025) : 5 vagues annuelles ne remplissent pas la condition de D17 et D28 ;
- CS27 (renoncements de dépenses) : 2025 seulement ;
- OG04_3 et PE07 : écartées par M05 pour sens ambigu, motif accepté.

## 8. Cohérence inter-dimensions

Contrôle mécanique sur les 7 dimensions fichées (25 + 37 + 75 + 22 + 33 + 32 + 57 fiches ; séries principales, composantes et variantes) : **aucun identifiant commun**. Les seules séries communes sont celles des écarts construits d'`egalites` (I2).

| # | Constat | Correction ou décision |
|---|---|---|
| I1 | **Lignes orphelines.** Les 695 lignes renvoyées par `niveau_de_vie` ne sont reprises que partiellement : `egalites` en reprend 84 sur 249, `travail` 5 sur 354, `securite` 0 sur 19, `planete` 0 sur 4 (`logement_cadre_vie` 45 et `education` 24 : dimensions pas encore fichées). Restent sans fiche : **19 lignes d'endettement des ménages** (INSEE ODD 17.i4a, `nasa_10_ki` DIR et NFW, OCDE 15_6, BCE QSA, endettement moyen de l'enquête Patrimoine, `ilc_mded05`) ; 165 lignes pour `egalites` (impact des transferts `ilc_li80*` 45, tranches de revenu `ilc_di20/27/31` 46, quantiles du patrimoine 72, taux de remplacement `ilc_pnp3` 2) ; 349 lignes de salaires et de pauvreté en emploi pour `travail` ; 4 pour `planete` (intensité du transport, taxes environnementales, revenu agricole) | Session mère (Q2) : rattacher par importation dans la dimension cible (fiche, variante ou écart en bloc motivé) ou laisser explicitement hors fiche. L'endettement des ménages est un indicateur de richesse nationale de l'INSEE (n° 3) et un indicateur OCDE (15_6) : `securite` n'a qu'une fiche de surendettement |
| I2 | Avertissements R1 : 6 lignes de `niveau_de_vie` sont séries principales d'écarts d'`egalites` (`ilc_li02` par sexe et par âge, `ilc_li31` FOR et NAT, et `ilc_di16` FOR et NAT ajoutées par la correction d'`egalites`) | Convention D32 respectée. Avec D35, la ligne par sexe passe à `autre_dimension:egalites` (T2) |
| I3 | PE03 : modalité 1 en `securite`, modalité 3 ici. Cohérent depuis SEC-2, mais les drapeaux divergent (`rupture_possible_2018`, `non_recoupe`, `licence_a_confirmer`, `url_api`) | Aligner `pauvrete_ressentie` (§4.6) |
| I4 | PE01 (ici) et IN02 (`egalites`) : même structure et même anomalie de la modalité spontanée, mais les drapeaux ne sont posés qu'en `egalites` | Aligner `pauvrete_percue_hausse` (§4.3) |
| I5 | Composites multidomaines du PNUD : l'IDH est écarté ici pour double compte, le coefficient d'inégalité humaine est retenu en `egalites` au titre de D18 | Règle commune (J1, Q4) |
| I6 | « Double risque de pauvreté » (`icw_pov_10` à `12`) : variantes de `taux_pauvrete_60` ici, écartées en bloc par `securite` (autres lignes des mêmes jeux) | Harmoniser au gel 2 ; aucune urgence |
| I7 | Éléments de la privation matérielle et sociale qui ont une fiche ailleurs : vacances et loisirs en `liens_bien_etre`, dépense imprévue et retards de paiement en `securite`, chauffage et internet à venir en `logement_cadre_vie` ; composante « très faible intensité de travail » de l'AROPE en `travail` | Signalé par les fiches ; contrôle de redondance du gel 2 |
| I8 | `depenses_pre_engagees` (loyers imputés compris) et le futur coût du logement de `logement_cadre_vie` (`_DEP_LOGT_REVENU` lui est déjà renvoyé) | À surveiller quand `logement_cadre_vie` sera fiché |
| I9 | `taux_epargne_menages` : la note propose un rattachement possible à `securite` (épargne de précaution) | Session mère ; l'écart pour sens ambigu suffit en `niveau_de_vie` |

## 9. Synthèse par nature

**Erreurs factuelles**, de la plus grave à la moins grave :
1. `ilc_mdho06q` (privation liée au logement) en variantes de la privation sévère ; libellé du catalogue faux (§4.2).
2. `pauvrete_ancree_2008` : drapeaux de rupture absents, `valeurs_non_lues` périmé, « même information que le premier décile » contredit par les données, raccordement vers une série dite successeur alors que la série est toujours publiée.
3. `privation_alimentaire` : ruptures 2020 et 2022 absentes.
4. `pauvrete_percue_hausse` (2007, 2014) et `pauvrete_ressentie` (2018) : ruptures possibles non signalées.
5. `privation_materielle_sociale` : valeurs EU-SILC présentées comme celles de la principale INSEE.
6. Ruptures EU-SILC « 2008 » dans le compte rendu et le journal (T5) ; prémisse fausse de NDV-10 (T4).
7. Forme : `pauvrete_ressentie` (`url_api` « non trouvé ») ; `revenu_national_habitant` (unité, T6).

**Choix contraires à la méthode** :
- série principale de `privation_alimentaire` (§4 : profondeur et fraîcheur) ;
- motif d'écart de l'IDH (§3 et D18).

**Alignements sur des décisions postérieures** (D34, D35) : `annee_reference` (T1) ; recoupement et `licence_a_confirmer` des séries DREES ; ventilation par sexe (T2).

**Désaccords de jugement**, à trancher par la session mère ou Léo ; je ne les compte pas comme des erreurs :
- **J1** — IDH : le retenir (D18, comme le coefficient d'inégalité humaine) ou créer une règle explicite « composite qui recouvre plusieurs dimensions de la grille → repère externe ».
- **J2** — Revenu des ménages en deux familles (`revenu_disponible_menages` et `niveau_vie_median`), toutes deux incontournables. Je suis d'accord avec M05 : la médiane d'enquête et la moyenne des comptes nationaux ajustée des services publics ne répondent pas à la même question. Léo tranche (question 1 de M05).
- **J3** — `incontournable` à l'intérieur d'une famille : `pouvoir_achat_uc` vaut `non` alors que la principale de sa famille vaut `oui`, mais `taux_pauvrete_50` et la privation sévère valent `oui`. Même question que J2 de l'audit `egalites` (par concept ou par famille).
- **J4** — `pauvrete_ancree_2008` dans la famille du premier décile : défendable (lecture « absolue » du bas de la distribution), mais avec des ruptures qui expliquent toute la hausse. Une famille propre, ou une place dans `pauvrete_monetaire`, se discute aussi.
- **J5** — Opinions de conjoncture sur le niveau de vie en France : D29 P8 face à D32 (O1).
- **J6** — Taux d'épargne écarté plutôt que rattaché à `securite` : j'approuve l'écart.

**Oublis** : O1 à O5 (§7). Aucun n'est un oubli de fond imputable à M05 : O1 relève d'une décision de la session mère, O2 d'une source absente des catalogues.

## 10. Corrections ordonnées pour l'agent correcteur

1. **`privation_alimentaire`** : principale `ilc_mdes03` (`estat-031704`, importée de `planete` avec `rattachement_propose`), INSEE 2.i1 (BDM 010594393) et sa copie Melodi en variantes, `raccordement: non`, `premiere_annee: 2004`, `derniere_annee: 2025`, `nb_points_depuis_2000: 22`, `qualite: rupture_2020, rupture_2022`. Motif réécrit (série la plus longue et la plus fraîche, valeurs identiques à l'INSEE à 0,2 point près). À défaut, garder l'INSEE en motivant la dérogation et ajouter les drapeaux de rupture.
2. **Règles 740 et 760** : déplacer `ilc_mdho06q` vers `privation_logement` (`autre_dimension:logement_cadre_vie`). Puis `--maj-fiches` (2 variantes de moins pour la privation sévère) ; NDV-5 clos.
3. **`indice_developpement_humain`** : après la décision sur J1, recommandation conforme à la méthode et à D18 (`retenir`, famille propre) ou motif cité d'une règle nouvelle ; `annee_reference: observation` ; IDHI en variante avec `preuve` si la fiche est retenue.
4. **`pauvrete_ancree_2008`** : `qualite: rupture_2020, rupture_2022` (sans `valeurs_non_lues`) ; note avec les valeurs lues (12,5 en 2008, 12,1 en 2019, 14,2 en 2020, 15,0 en 2022, 15,6 en 2025) et la dépendance aux ruptures ; raccordement « non : série publiée jusqu'en 2025 ; ancrage 2019 (`ilc_li22`) disponible ».
5. **`pauvrete_percue_hausse`** : `rupture_possible_2007`, `anomalie_2014`, `non_recoupe_2000_2024`, `licence_a_confirmer` ; recoupement de la valeur 2025 cité dans la note ; décision sur O3 (PE02).
6. **`pauvrete_ressentie`** : `rupture_possible_2018`, `non_recoupe_2014_2023`, `licence_a_confirmer` ; `url_api` vers la pièce jointe unique (comme la fiche sœur) ; note sur NDV-4 et SEC-2 réécrite.
7. **`privation_materielle_sociale`** : citer les valeurs de la BDM (11,7 en 2013, 12,9 en 2014, 10,5 en 2021, 12,7 en 2024) ; nuancer « même mesure » ; vérifier la rétropolation INSEE avant de garder `rupture_eu_silc_2020_2022`.
8. **Transversales** : T1 (`annee_reference`), T2 (`estat-000033` → `autre_dimension:egalites`), T3 (`rattachement_propose`), T6 (`revenu_national_habitant`) ; remarques de forme (`taux_epargne_menages` : source des valeurs du motif ; `pib_habitant` : `valeurs_provisoires_2025` ; `niveau_vie_modestes` : « seule mesure en euros constants » ; `difficulte_joindre_deux_bouts` : anomalie possible en 2004).
9. **Liste de maintenance** (T4) : NDV-1 (déflateur trouvé), NDV-4 (périmé), NDV-5 (vérifié), NDV-6 (résolu), NDV-10 (à clore). **Compte rendu et journal M05** : ruptures EU-SILC (T5).
10. Selon les décisions de la session mère : O1 (opinions de conjoncture), O3 (PE02), O4 et O5 (variantes) ; I1 (lignes orphelines, endettement des ménages en premier).
11. Puis `python scripts/preselection.py --dimension niveau_de_vie --maj-fiches`, `python scripts/verifier_fiches.py --dimension niveau_de_vie --tableau`, `python scripts/verifier_fiches.py --dimension niveau_de_vie` (0 erreur) et `python -m pytest -q`.

## 11. Questions pour la session mère

1. **Q1 (O1, J5)** — Les soldes d'opinion sur le niveau de vie **en France** (enquête de conjoncture) restent-ils hors grille (D29 P8) alors que D32 fait des opinions sur la société des fiches à part entière ? Si oui, dire pourquoi PE01 est admise et eux non.
2. **Q2 (I1)** — Que faire des 537 lignes renvoyées par `niveau_de_vie` à des dimensions déjà fichées qui ne les ont pas reprises ? En priorité : l'**endettement des ménages** (19 lignes ; `dimensions.yaml` : « réserves financières des ménages et surendettement → securite ») revient-il à `securite` comme fiche, ou est-il hors v1 (A16) ? Faut-il une règle générale : toute dimension fichée après une autre importe ou écarte explicitement les lignes qui lui sont renvoyées ?
3. **Q3 (D34)** — Pour les séries du baromètre DREES calculées sur microdonnées, le drapeau `non_recoupe_…` suffit-il pour `retenir` (pratique de `securite`), ou faut-il recouper trois vagues avant de valider ? La pratique diffère aujourd'hui entre `securite` et les autres dimensions.
4. **Q4 (J1, I5)** — Règle commune pour les composites multidomaines (IDH, coefficient d'inégalité humaine) : fiche retenue ou repère externe ?
5. **Q5 (J3)** — `incontournable` : par fiche, selon le concept exact du croisement des cadres, ou par famille ?
6. **Q6** — Les fiches DREES issues de la long-list (`m04-…`) gardent un `source_serie_id` qui cite deux pièces jointes (celui du catalogue M04, exigé par le vérificateur), alors que les fiches hors long-list et les `url_api` des autres fiches DREES visent la pièce jointe unique `barometre2000_2025_diff_csv`. Faut-il mettre à jour le catalogue M04 pour aligner les deux ?

## Annexe — sources consultées

| Source | Usage |
|---|---|
| `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<jeu>?…` avec `nasa_10_nf_tr` (B7G_R_HAB), `nama_10_pc` (P41), `sdg_01_10`, `ilc_li21`, `ilc_li22b`, `ilc_sbjp01`, `ilc_mdes09` (GRT, DIF), `ilc_pw01b` (FIN), `nasa_10_ki` (SRG_S14_S15), `ilc_mdsd07`, `ilc_mdsd11`, `ilc_mdes03`, `ilc_li02` (B_60), `ilc_mdho06q`, `sdg_10_20` | §4, §6 |
| `https://ec.europa.eu/eurostat/cache/metadata/en/nasa_10_nf_tr_esms.htm` | déflateur des mesures réelles par habitant |
| `https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/<idbank>` avec 011779993, 010594486, 010594393, 010594449 | §4 |
| `https://www.insee.fr/fr/statistiques/9019316` (Insee Première n° 2117, 9 juillet 2026) | valeurs 2024 de l'ERFS, champ, rétropolation |
| Dépôt : `docs/sources/series/drees__barometre_2000_2025_distributions.csv`, `_couverture.csv`, `drees__barometre_dico_*_2025.txt`, `drees__barometre_tc_simplifies_2025.txt`, `pnud__hdr25_series_composites_france.csv` | DREES, PNUD |
| Dépôt : `catalogues/` (Melodi, BDM, Eurostat séries et jeux, `*_non`, toutes les long-lists), `docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv`, `docs/methodo/30_indicateurs_cadres_reference.csv`, présélections des 7 dimensions fichées | §5, §7, §8 |
| **Refusés ou non lus** : API Melodi (`api.insee.fr/melodi`, robots.txt) ; API Banque mondiale `SN.ITK.MSFI.ZS` (permission non accordée à temps, non réessayée) ; une page de définition insee.fr dont l'adresse supposée renvoyait à une autre définition (aucun usage) | — |
