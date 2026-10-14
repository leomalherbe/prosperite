# Journal de bord — M05, dimension `egalites` (Égalités)

Agent de mission M05 (dimension Égalités), branche `m05-egalites`, 14 octobre 2026. Méthode commune appliquée : `docs/methodo/33_methode_fiches_M05.md` (v1.0), pilotes `liens_bien_etre` et `securite`.

## 0. Mise en route

- Branche `m05-egalites` créée depuis `origin/main` (`48e2381`, fusion du pilote `securite`).
- Lus : `CLAUDE.md`, charte (§3.4, §3.6, §4, §5.1), journal des décisions (D13–D30), fiche M05, méthode commune `33_methode_fiches_M05.md`, `indicateurs/dimensions.yaml` (définition, contenu, exclusions d'`egalites` ; A8, A9, R3), `_modele_fiche.yaml`, fiches et règles des pilotes (`indicateurs/securite/*.yaml`, `indicateurs/liens_bien_etre/*.yaml`, `regles_preselection_securite.csv`), `docs/cr/M05_securite_journal.md`, `docs/cr/maintenance_catalogues.md`, `30_indicateurs_cadres_reference.csv`, §5 de `30_crosswalk_synthese.md`, `10_indicateurs_candidats_hors_insee_eurostat.csv`, extraits du robot M04 (`docs/sources/series/` : OWID, PNUD, DREES, DEPP, OCDE), métadonnées du catalogue Melodi (`docs/sources/echantillons_insee/melodi_catalog_all_2026-10-13.json.gz`).
- Tests : `pip install -r requirements.txt && python -m pytest -q` → 394 réussis (au départ et à la fin).
- Outils communs utilisés tels quels : `scripts/preselection.py` (`--maj-fiches`), `scripts/verifier_fiches.py` (`--tableau`). Aucun fichier sous `scripts/` ni `src/` n'est modifié (pas de déclenchement du robot « Collecte »). Les deux générateurs de travail (règles, fiches) sont restés dans le bac à sable ; leur produit est entièrement dans le dépôt (règles CSV, fiches YAML).

## 1. Ce que contient la long-list `egalites`

330 lignes : 289 éligibles, 31 à vérifier, 10 non éligibles ; Eurostat 198, INSEE BDM 46, Melodi 45, M04 41 (OCDE 17, OWID 10, PNUD 7, DREES 3, DEPP 2, Banque mondiale 2).

Répartition des 330 lignes après présélection (sous-thème de la fiche de rattachement) :

| Bloc | Lignes | Constat |
|---|---|---|
| Inégalités de revenu (INSEE ERFS rétropolé et non rétropolé, ODD 10, Eurostat `ilc_di11*`, `ilc_di12*`, `sdg_10_41`, `sdg_10_50`, parts `ilc_di01`, OCDE, Banque mondiale, WID, PNUD) | 90 | S80/S20, Gini, Palma, D9/D1, S40, avant redistribution, effet de la redistribution, part du 1 % |
| Niveaux de revenu EU-SILC (`ilc_di01` seuils, `ilc_di04`, `ilc_di07`, `ilc_di13b`, `ilc_di14b`) | 86 | des **niveaux**, pas des écarts : renvoyés à `niveau_de_vie` (R3) |
| Écarts femmes-hommes (ODD 5 INSEE, `sdg_05_20`, `sdg_05_30`, pensions `ilc_pnp*`, OCDE, OIT, PNUD, V-Dem, DREES) | 57 | |
| Écartés en bloc | 27 | parts détaillées des quantiles (16), femmes enseignantes (4), asile (2), Gini expérimental de la dépense et de l'épargne (2), temps non rémunéré 2009 (2), droits LGBT+ arrêtés en 2019 (1) |
| Salaires (BDM D9/D1, D9/D5, D5/D1 en EQTP et à temps complet, OCDE) | 19 | |
| Disparités régionales (`lfst_r_*`, `DISP_NUTS2/3`) | 17 | valeurs nationales de dispersion issues de jeux régionaux |
| Origine sociale (DEPP, `ilc_li60*`, PISA, PIAAC), patrimoine, perceptions, générations, multidimensionnel, discriminations, santé | 32 | |
| Renvoyées à `securite` (`ilc_li70b`) | 2 | prestations des chômeurs |

Les **écarts selon l'origine, le diplôme, le revenu, l'âge et le handicap** ne sont presque pas dans la long-list `egalites` : ils sont dans les **ventilations** des long-lists `travail`, `niveau_de_vie`, `education` et `sante` (colonnes `ventilation` : `citizen`, `c_birth`, `isced11`, `quant_inc`, `age`, `sex`). Ils ont été repérés par une recherche sur ces colonnes, puis construits (§2.3).

## 2. Méthode appliquée

### 2.1 Présélection
- `docs/validation/regles_preselection_egalites.csv` : **136 règles** (ordre : séries principales exactes, variantes par sous-groupe, imports d'autres long-lists, puis écarts en bloc et `autre_dimension` par expression sur `serie_id`).
- `python scripts/preselection.py --dimension egalites` → **499 lignes affectées** (330 de la long-list, aucune sans règle, aucune règle vide ; 169 importées : `niveau_de_vie` 104, `travail` 51, `sante` 10, `education` 2, `democratie` 2), **136 groupes** : 50 `fiche` (53 lignes), 77 `variante_de` (331 lignes), 6 `ecarte_en_bloc` (27 lignes), 3 `autre_dimension` (88 lignes : 86 vers `niveau_de_vie`, 2 vers `securite`).
- Lignes de la long-list `egalites` : 35 en `fiche`, 180 en `variante_de`, 27 écartées, 88 renvoyées à une autre dimension.

### 2.2 Familles et variante principale
- Une famille réunit les fiches **substituables** : les cinq statistiques d'inégalité du niveau de vie après redistribution (S80/S20, Gini, Palma, D9/D1, part des 40 % les plus modestes) forment **une seule famille** (`inegalite_revenu`) : elles sont très corrélées et l'utilisateur doit en choisir une. Les inégalités avant redistribution, la concentration au sommet (1 %), le patrimoine, les salaires sont des familles distinctes.
- Principale `inegalite_revenu` : **S80/S20 ERFS rétropolé** (Melodi `S80S20_SL`, 1996-2024), indicateur de richesse nationale n° 6 et concept des cinq cadres ; la version BDM (ODD 10.i2a) s'arrête en 2023. Cette série est dans la long-list `niveau_de_vie` (étiquette v0 du jeu) alors que le Gini, le Palma et le D9/D1 du **même jeu** sont en `egalites` : rattachement proposé (maintenance n° 10).
- Dérogations à l'ordre de la méthode, motivées dans les fiches : (a) **écart de salaire** : principale = écart non corrigé d'Eurostat (`sdg_05_20`, 2006-2024), indicateur ODD national 5.i1 retenu par l'INSEE elle-même et cadre Eurostat QoL, plutôt que l'écart INSEE en EQTP plus long (1996-2024, construit), proposé en `retenir_variante` ; (b) **part du 1 %** : principale = WID (niveau 2, sources fiscales) plutôt que la part du dernier centile EU-SILC (niveau 1), l'enquête saisissant mal le sommet.

### 2.3 Écarts construits (champ `formule`)
Douze fiches portent un écart **calculé** à partir de séries du catalogue ; leurs lignes sources sont importées en décision `fiche` depuis leur long-list (les niveaux y restent, R3 ; `rattachement_propose` le dit). Le signe de chaque écart a été **vérifié sur l'API Eurostat** (WebFetch) avant de fixer le sens :

| Fiche | Formule | Source | Vérification (14/10) | Sens |
|---|---|---|---|---|
| `ecart_chomage_fh` | F − H | `une_rt_a` (travail) | F 9,3/H 7,8 (2003) ; 9,7/9,8 (2012) ; 7,6/7,8 (2025) : **change de signe en 2012** | ambigu → écarter |
| `ecart_pauvrete_fh` | F − H | `ilc_li02` (niveau_de_vie) | +1,5 (2004), −0,2 (2018), +2,0 (2025) | bas |
| `ecart_salaire_eqtp_fh` | (H − F)/H | Melodi `DS_DERA_PRIVE_SERIES_LONGUES` (niveau_de_vie) | non lu (API Melodi fermée à l'outil) | bas |
| `ecart_chomage_immigres` | nés hors UE − nés en France | `lfsa_urgacob` (travail) | 19,7/9,4 (2000) ; 13,1/7,0 (2025) | bas |
| `ecart_pauvrete_etrangers` | étrangers − Français | `ilc_li31` (niveau_de_vie) | 32,8/11,8 (2004) ; 34,0/12,8 (2025) | bas |
| `ecart_neet_immigres` | nés hors UE − nés en France | `edat_lfse_28` (travail) | non lu | bas |
| `ecart_sorties_precoces_immigres` | nés hors UE − nés en France | `edat_lfse_02` (education) | nés hors UE 21,4 (2006) → 12,7 (2025), **modalité depuis 2006** | bas |
| `ecart_reussite_bac_origine_sociale` | cadres − ouvriers | DEPP (egalites) | 97,1/87,5 (2025, extrait du robot M04) | bas |
| `ecart_chomage_diplome` | CITE 0-2 − CITE 5-8 | `lfsa_urgaed` (travail) | non lu | bas |
| `ecart_sante_percue_revenu` | QU5 − QU1 (bonne santé) | `hlth_silc_10` (sante) | 16,5 (2005), 21,3 (2025) | bas |
| `ecart_besoins_soins_revenu` | QU1 − QU5 (besoins non satisfaits) | `hlth_silc_08` (sante) | non lu | bas |
| `ecart_pauvrete_jeunes_seniors` | 18-24 ans − 65 ans ou plus | `ilc_li02` (niveau_de_vie) | 5,2 (2004), 9,9 (2015), 11,2 (2025), **18-24 ans depuis 2004** | bas |

Écarts **publiés directement** (sans formule) : `ecart_emploi_fh` et `ecart_temps_partiel_fh` (`sdg_05_30`), `ecart_salaire_fh` (`sdg_05_20`), `ecart_pension_fh` (`ilc_pnp13`), `ecart_pauvrete_enfants_education_parents` (`ilc_li60a`), `ecart_emploi_handicap` (`hlth_dlm200`, importé de `sante`), dispersions régionales `lfst_r_*`.

Écarts non construits faute de série adaptée au catalogue : écart de **taux d'emploi** selon l'origine ou le diplôme (paquets publiés seulement pour les 15 ans ou plus : biais de structure par âge ; listés en variantes, maintenance n° 16) ; écart d'**espérance de vie** selon le diplôme ou le niveau de vie (non catalogué, n° 19) ; écarts de pauvreté villes/zones rurales (`ilc_li43`, non retenu : le sens d'un écart urbain/rural n'est pas univoque).

### 2.4 Sens, déclaratif, composites, incontournables
- `sens: ambigu` (→ `ecarter`) pour 5 fiches : écart de chômage F/H (changement de signe), effet de la redistribution (grandit quand les inégalités primaires augmentent ; rupture 2020 : 3,4-4,0 puis 5,5-6,7), revenu relatif des seniors (0,90 → 1,04 → 0,97 : passe par la parité), indice de développement de genre (optimum à 1), part des femmes parmi les victimes de violences (part, pas taux).
- Écart publié négatif (`ecart_temps_partiel_fh`, hommes − femmes : −25,2 en 2009, −17,5 en 2025) : `sens: haut`, expliqué dans la définition.
- Part des femmes dans les filières scientifiques : le total ODD 5.i2 a dépassé 50 % en 2023 (50,6 %, BDM 010594718) ; la principale est le champ « formations scientifiques, ingénieurs compris » (39,0 % → 46,4 %), encore sous la parité.
- `declaratif: oui` : 5 fiches (perceptions DREES ×3, santé perçue, inégalité de satisfaction) ; règle du pilote (perceptions et jugements = oui ; faits déclarés = non).
- `composite: oui` : 5 (indice d'inégalité de genre et de développement de genre du PNUD, coefficient d'inégalité humaine, deux indices V-Dem), admis par D18.
- `incontournable: oui` (§5 du crosswalk, porté par toute la famille) : familles `inegalite_revenu` (5 fiches), `ecart_emploi_fh` (1), `ecart_salaire_fh` (2), `indice_composite_genre` (3) = **11 fiches**. Les écarts de temps partiel, de pension, de pauvreté et la parité politique (un seul cadre) sont à `non`.

### 2.5 Vérifications à la source (WebFetch, 14/10/2026)
| Source | Constat |
|---|---|
| Eurostat `sdg_05_30` EMP / EMP_PT | 8,0 → 5,7 points (2009-2025) ; −25,2 → −17,5 ; drapeau d 2021-2025 |
| Eurostat `une_rt_a` F, M | changement de signe de l'écart en 2012 (voir §2.3) |
| Eurostat `ilc_li02` F, M (tous âges, 65+), 18-24, 65+ | voir §2.3 ; 65+ en 2025 : F 13,1, H 9,8 |
| Eurostat `ilc_pnp12` | « Gender differences in AROP », unité « nombre » : −7,40 à −0,20 (65+), ne correspond pas à F − H (maintenance n° 18) |
| Eurostat `ilc_di11i`, `ilc_pnp2`, `ilc_di12`, `ilc_pnp13`, `hlth_dlm200`, `ilc_li60a`, `lfst_r_lmder`, `sdg_05_20`, `sdg_05_50`, `lfsa_urgacob`, `ilc_li31`, `edat_lfse_02`, `hlth_silc_10` | valeurs citées dans les motifs des fiches |
| Eurostat `ilc_di01` (D10, QU1, QU2) | Palma EU-SILC calculé : 1,04 (2018), 1,14 (2025) ; unité « Euro » au catalogue alors que la statistique est une part (maintenance n° 12) |
| INSEE BDM 010594718, 010594719, 010594728, 010752357, 010776367 | valeurs citées ; 010594728 sans valeur 2024-2025 ; 010776367 sans valeur 2023-2024 |
| INSEE BDM 010760765 | erreur serveur à la lecture : non vérifiée |
| Melodi (API `api.insee.fr/melodi`) | refusée à l'outil de lecture (robots.txt) ; S80/S20 2024 = 4,62 lu dans les métadonnées du catalogue Melodi (note de lecture de `DS_ERFS_RETROPOLE`) |
| OWID (WID) | top 1 % : 11,33 (2000), 9,55 (2013), 12,10 (2022) ; Palma avant impôt 2,50 → 2,64 ; V-Dem France non lisible (fichier tronqué) |
| Extraits du robot M04 | PNUD (GII 0,034, 11e rang ; GDI 0,993 ; coefficient 8,97 ; Atkinson revenu 17,89, durée de vie 3,71, éducation 5,30, en 2023) ; OCDE (11_1_VER 2,08 en 2024 ; 1_3_VER 49,9 en 2020 ; 2_8_VER 2,78 ; PISA D9/D1 maths 1,68) ; DREES (IN01 26,5 → 18,7 ; IN02 69,0 → 85,7 ; CS09 17,3 → 15,7 ; CS16_1 23,8 → 20,5) ; DEPP |

## 3. Résultats

- **50 fiches**, **37 familles** : **32 `retenir`**, **11 `retenir_variante`**, **7 `ecarter`** ; 5 déclaratives ; 5 composites ; 4 à vérifier (D17 : `gini_patrimoine`, `part_patrimoine_10_pourcent_riches`, `dispersion_scores_pisa`, `inegalite_satisfaction_vie`) ; 0 hors long-list ; 11 incontournables (4 familles) ; **331 variantes** ; **12 écarts construits** ; 16 fiches avec `rattachement_propose` (série principale ou composantes dans une autre long-list) ; 9 raccordements `a_etudier`.
- Sous-thèmes : écarts femmes-hommes 16 ; inégalités de revenu 8 ; écarts selon l'origine 4 et discriminations 2 ; origine sociale et mobilité 4 ; santé 3 et handicap 1 ; territoires 3 ; générations 2 ; patrimoine 2 ; salaires 1 ; perceptions 3 ; multidimensionnel 1.

| Recommandation | Fiches |
|---|---|
| retenir (32) | rapport_s80_s20, rapport_s80_s20_avant_redistribution, part_revenu_1_pourcent_riches, gini_patrimoine, rapport_d9_d1_salaires, ecart_emploi_fh, ecart_temps_partiel_fh, ecart_salaire_fh, ecart_pension_fh, ecart_pauvrete_fh, femmes_parlement, femmes_cadres_dirigeants, femmes_filieres_scientifiques, indice_inegalite_genre, discriminations_femmes_temoins, ecart_chomage_immigres, ecart_pauvrete_etrangers, ecart_neet_immigres, ecart_sorties_precoces_immigres, ecart_reussite_bac_origine_sociale, ecart_pauvrete_enfants_education_parents, ecart_chomage_diplome, dispersion_scores_pisa, ecart_sante_percue_revenu, ecart_besoins_soins_revenu, inegalite_esperance_vie, ecart_emploi_handicap, disparites_regionales_emploi, ecart_pauvrete_jeunes_seniors, societe_juste_percue, inegalite_satisfaction_vie, coefficient_inegalite_humaine |
| retenir_variante (11) | gini_niveau_de_vie, ratio_palma, rapport_d9_d1_niveau_de_vie, part_niveau_de_vie_40_modestes, part_patrimoine_10_pourcent_riches, ecart_salaire_eqtp_fh, femmes_postes_encadrement, femmes_direction_fonction_publique, disparites_regionales_chomage, disparites_regionales_neet, inegalites_percues_hausse |
| ecarter (7) | effet_redistribution, ecart_chomage_fh, indice_developpement_genre, autonomisation_politique_femmes, part_femmes_victimes_violences, egalite_libertes_groupes_sociaux, revenu_relatif_seniors |

Écarts en bloc (27 lignes) : parts détaillées des quantiles `ilc_di01` (16), part des femmes enseignantes (4), demandes d'asile (2), Gini expérimental de la dépense et de l'épargne (2), temps non rémunéré OCDE 2009 (A4, 2), indice des droits LGBT+ arrêté en 2019 (1). Lignes importées (169) : revenu 56, écarts femmes-hommes 46, patrimoine 28, origine 22, handicap 6, santé 4, salaires 4, origine sociale 2, générations 1.

## 4. Exclusions, erreurs de catalogue et rattachements

Consignés dans `docs/cr/maintenance_catalogues.md`, lignes **10 à 20** (statut `a_faire`), non corrigés par l'agent :
- n° 10-11 : rattachements de la table de correspondance (mesures de dispersion ERFS, patrimoine et salaires en `niveau_de_vie`/`travail` ; `earn_gr_gpgr2*`, `sdg_05_50`, `hlth_dlm200` ; renvoi des niveaux de revenu `ilc_di04/07/13b/14b` et seuils `ilc_di01` vers `niveau_de_vie`, `ilc_li70b` vers `securite`) ;
- n° 12 : unité « Euro » des parts `ilc_di01` ; n° 13 : libellé incohérent de `GINI_PATBRUT_HR` (Melodi) ; n° 17 : périodes des paquets de modalités ; n° 18 : définition d'`ilc_pnp12` ; n° 20 : lignes ERFS `COMPARE_TIME=BWA/BWB` (valeurs de rupture, pas des séries) ;
- n° 14, 16, 19 : séries à cataloguer (DREES CS16_1-5 sur les discriminations ; taux d'emploi 20-64 ans par origine et 25-64 ans par diplôme ; PISA selon le statut social, espérance de vie par niveau de vie, TeO, Défenseur des droits, femmes dans les conseils d'administration) ;
- n° 15 : épargner les indicateurs nationaux de dispersion `lfst_r_*` lors de l'exclusion des jeux NUTS (D30).

Exclusions de la long-list relues : les 10 lignes `non` relèvent bien de leur motif (séries arrêtées avant 2020, une ou trois valeurs) ; aucune exclusion abusive. Les 31 `a_verifier` sont des séries pluriannuelles (D17, D28) ou les valeurs de rupture ERFS (n° 20).

## 5. Contrôles

```
python scripts/verifier_fiches.py --dimension egalites --tableau
Dimension egalites : lignes_longlist 330, lignes_autre_dimension 88, fiches 50, familles 37, retenir 32,
retenir_variante 11, ecarter 7, declaratifs 5, composites 5, a_verifier 4, hors_longlist 0, incontournables
[11 fiches], variantes 331
0 erreur(s), 0 avertissement(s)
```
Identifiants ASCII uniques dans `indicateurs/` (aucune collision avec `liens_bien_etre` et `securite`) ; `socle_v1` vide ; chaque série principale, composante et variante présente dans un catalogue ; une variante principale par famille ; `sens: ambigu` ⇒ `ecarter` ; tableau de validation à 18 colonnes, `decision_leo` vide. `pytest` : 394 réussis.

Contrainte rencontrée : le vérificateur commun refuse une `premiere_annee` antérieure à 1900 ; les deux séries V-Dem (1789, 1851) portent 1900 avec une note (proposition : élargir la borne).

## 6. Livraison

Commits sur `m05-egalites`, PR « M05 — fiches indicateurs : egalites » vers `main` ; compte rendu `docs/cr/M05_egalites_compte_rendu.md`, copié dans le Projet (`claude/cr/M05_egalites_compte_rendu.md`) avec le tableau de validation (`claude/40_validation_egalites.csv`). Le message du deuxième commit annonce « 15 écarts construits » : le décompte exact est **12** (fiches avec `formule`).
