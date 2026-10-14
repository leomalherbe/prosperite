# Audit croisé M06 — dimension `egalites`

Auditeur M06 (session neuve, n'ayant pas participé à M05 `egalites`), 14 octobre 2026. Branche `m06-egalites`, partie de `origin/main` au commit `1a0697c` (fiches fusionnées par la PR #10). Aucune fiche, aucun tableau M05, aucun script ni catalogue n'a été modifié : ce rapport propose, l'agent correcteur (ou la session mère) corrige. Déroulé détaillé : `docs/cr/M06_egalites_journal.md`.

Lu avant d'agir : `CLAUDE.md` ; charte §3.4, §3.6, §4, §5.1 ; journal D13–D33 ; fiche M06 ; méthode commune v1.1 (`docs/methodo/33_methode_fiches_M05.md`) ; `indicateurs/dimensions.yaml` (contenu d'`egalites`, A8, A9, R1–R8) ; audits `securite` et `liens_bien_etre` et leur commit de corrections ; les 50 fiches, `validation_egalites.csv`, `regles_preselection_egalites.csv`, `preselection_egalites.csv`, `preselection_egalites_lignes.csv` ; journal et compte rendu M05 ; lignes 10-20 de `docs/cr/maintenance_catalogues.md` ; toutes les long-lists ; catalogues INSEE, Eurostat (séries, jeux, `*_non`), M04 ; crosswalk (`30_indicateurs_cadres_reference.csv`, §5 de `30_crosswalk_synthese.md`) ; fiches et présélections `securite`, `liens_bien_etre`, `democratie`. Contrôle préalable : `verifier_fiches.py --dimension egalites` → 0 erreur, 0 avertissement ; `pytest` → 397 réussis.

---

## 1. Avis global : `corrections_necessaires`

Le socle est solide. Les 12 écarts construits sont **licites** : chaque fois, les deux termes viennent du même jeu, ont le même champ et la même unité. Le signe est constant sur toute la période pour les 10 écarts relus sur l'API, la seule exception étant l'écart de chômage entre femmes et hommes, écarté à juste titre ; il n'a été relu qu'en 2025 pour le baccalauréat et pas du tout pour le salaire en EQTP (Melodi). Les valeurs citées dans les motifs et les notes ont été retrouvées à la source pour 21 jeux Eurostat (24 avec les oublis), 1 série BDM, la note de lecture Melodi et les extraits du robot (PNUD, OWID, OCDE, DEPP, DREES). La famille de l'inégalité de revenu (S80/S20 principal) et les incontournables du crosswalk sont bien en place. R3 est respecté : aucune série principale n'est un niveau ou un taux de pauvreté.

Trois problèmes empêchent pourtant de passer à la validation de Léo :

1. **Trois oublis de fond, dus à des affirmations fausses du journal M05 et de la liste de maintenance.**
   - **Écart d'emploi selon la nationalité, 20-64 ans** (`sdg_08_30a`, long-list `travail`, 2000-2025, 26 points). M05 le dit absent du catalogue (« seulement 15 ans ou plus ») alors qu'il y est. C'est l'indicateur d'Eurostat *Quality of life* cité au crosswalk.
   - **Part des femmes dans les conseils des grandes sociétés cotées** (`sdg_05_61`, long-list `education`, 2012-2025, 14 points). La ligne de maintenance n° 19 le dit « non catalogué » alors qu'il l'est. La loi Copé-Zimmermann lui fixe une cible légale de 40 % (crosswalk, objectifs officiels).
   - **Témoins de discriminations liées à l'origine ethnique** (baromètre DREES, CS16_1, 7 vagues 2015-2025, déjà calculées par le robot). C'est la seule mesure directe de l'arbitrage A8. M05 l'a renvoyée en maintenance au lieu d'en faire une fiche hors long-list (D32), et la dimension n'a aujourd'hui **aucune mesure directe des discriminations selon l'origine**.
2. **Des erreurs factuelles sur des fiches**, les plus nettes étant :
   - la période de `ecart_neet_immigres` (la modalité « nés hors UE » commence en 2006, pas en 2004) ;
   - la définition de `ecart_temps_partiel_fh` (c'est un écart de parts du temps partiel dans l'emploi, pas de taux d'emploi) ;
   - les premières années des deux séries V-Dem (1851 et 1789), toujours ramenées à 1900 alors que D32 admet désormais ces années ;
   - des drapeaux de rupture Eurostat absents de plusieurs écarts construits.
3. **Deux écarts motivés hors de la méthode** : `autonomisation_politique_femmes` est dite « dominée » alors qu'elle est plus longue et plus fraîche que l'indice du PNUD, et `egalite_libertes_groupes_sociaux` est écartée parce qu'elle est « presque constante ». Ni l'un ni l'autre n'est un motif d'écart prévu par la méthode (§3).

Chiffres : **38 fiches auditées** sur 50, avec **27 conformes**, **10 à corriger** et **1 non vérifiable** (valeurs BDM refusées à l'outil). S'y ajoutent **5 corrections transversales** hors échantillon, **8 oublis** (dont 3 importants) et **7 points de cohérence inter-dimensions**. Liste ordonnée des corrections : §10.

## 2. Échantillon

| Règle | Fiches |
|---|---|
| `recommandation: ecarter` (7) | autonomisation_politique_femmes, ecart_chomage_fh, effet_redistribution, egalite_libertes_groupes_sociaux, indice_developpement_genre, part_femmes_victimes_violences, revenu_relatif_seniors |
| `incontournable: oui` (11, dont 2 déjà comptées) | ecart_emploi_fh, ecart_salaire_fh, ecart_salaire_eqtp_fh, gini_niveau_de_vie, indice_inegalite_genre, part_niveau_de_vie_40_modestes, rapport_d9_d1_niveau_de_vie, rapport_s80_s20, ratio_palma (+ autonomisation_politique_femmes, indice_developpement_genre) |
| Signalées au journal M05 : `a_verifier` (4), `raccordement: a_etudier` (3 de plus), série « non vérifiée » (1) | dispersion_scores_pisa, gini_patrimoine, inegalite_satisfaction_vie, part_patrimoine_10_pourcent_riches ; ecart_temps_partiel_fh, femmes_cadres_dirigeants, femmes_parlement ; femmes_direction_fonction_publique |
| Écarts construits (12 avec `formule`, dont 2 déjà comptés) | ecart_besoins_soins_revenu, ecart_chomage_diplome, ecart_chomage_immigres, ecart_neet_immigres, ecart_pauvrete_etrangers, ecart_pauvrete_fh, ecart_pauvrete_jeunes_seniors, ecart_reussite_bac_origine_sociale, ecart_sante_percue_revenu, ecart_sorties_precoces_immigres (+ ecart_chomage_fh, ecart_salaire_eqtp_fh) |
| 20 % des 16 autres, tirage (4) | ecart_emploi_handicap, inegalite_esperance_vie, part_revenu_1_pourcent_riches, disparites_regionales_chomage |

Tirage : `random.Random(20261014).sample(sorted(autres), 4)`. **Graine 20261014.** 20 % de 16 = 3,2, arrondi à 4 comme dans les audits précédents. Total : **38 fiches**.

« 15 écarts construits » vient du message du commit M05 `456bfb2`. Les fiches n'en comptent que **12** avec `formule`, et le journal M05 §6 le reconnaît. Les 3 autres fichiers qui parlent de « composantes » sont `ecart_emploi_fh`, `ratio_palma` et `indice_inegalite_genre` : ils sont audités au titre des incontournables, et leur construction est examinée au §5.

## 3. Tableau des fiches auditées

Nature : **F** = erreur factuelle ; **M** = motif ou champ non conforme à la méthode ; **J** = désaccord de jugement ; **O** = oubli. Sources lues le 14/10/2026 (détail §4 et annexe).

| Fiche | Motif d'échantillon | Source consultée | Verdict | Nature | Correction attendue (résumé ; détail §4) |
|---|---|---|---|---|---|
| `effet_redistribution` | ecarter | API `ilc_di11i` | conforme | — | — |
| `ecart_chomage_fh` | ecarter, formule | API `une_rt_a` F, M | conforme | (J1) | — |
| `indice_developpement_genre` | ecarter, incontournable | extrait PNUD | conforme | (J2) | — |
| `autonomisation_politique_femmes` | ecarter, incontournable | extrait OWID | **a_corriger** | F, M, (J2) | `premiere_annee: 1851` ; motif « dominé » à remplacer : `retenir_variante` ou motif de la méthode |
| `part_femmes_victimes_violences` | ecarter | catalogue BDM (API refusée) | **a_corriger** (mineur) | F | Nature des variantes (`melodi-005417` = copie de 5.i3b) ; rupture à formuler « passage de CVS à VRS, deux années sans valeur » |
| `egalite_libertes_groupes_sociaux` | ecarter | extrait OWID ; distributions DREES | **a_corriger** | F, M | `premiere_annee: 1789` ; motif hors méthode ; note fausse (« aucune série mesurée ») |
| `revenu_relatif_seniors` | ecarter | API `ilc_pnp2` | conforme | — | Remarque : `b` 2004 et 2008 absents de `qualite` (§6) |
| `ecart_emploi_fh` | incontournable | API `sdg_05_30` | conforme | — | — |
| `ecart_salaire_fh` | incontournable | API `sdg_05_20` | conforme | — | — |
| `ecart_salaire_eqtp_fh` | incontournable, formule | catalogue et métadonnées Melodi | conforme | — | Valeurs non lues (Melodi fermé à l'outil), aucune n'est citée |
| `gini_niveau_de_vie` | incontournable | catalogue Melodi ; API `ilc_di12` | conforme | — | — |
| `indice_inegalite_genre` | incontournable | extrait PNUD ; crosswalk | conforme | — | — |
| `part_niveau_de_vie_40_modestes` | incontournable | catalogues Melodi et BDM | conforme | — | — |
| `rapport_d9_d1_niveau_de_vie` | incontournable | catalogues Melodi et BDM | conforme | — | — |
| `rapport_s80_s20` | incontournable | métadonnées Melodi (note de lecture) ; API `ilc_di11` | conforme | — | — |
| `ratio_palma` | incontournable | API `ilc_di01` ; extrait WID ; catalogue Melodi | conforme | — | — |
| `gini_patrimoine` | a_verifier | catalogue Melodi | conforme | — | Réserve : valeurs Melodi non relues |
| `part_patrimoine_10_pourcent_riches` | a_verifier | catalogue Melodi ; extrait OCDE | conforme | — | Réserve : unité (« masse détenue ») à confirmer par le robot |
| `dispersion_scores_pisa` | a_verifier, a_etudier | extrait OCDE ; API OCDE (flux) | conforme | — | Remarque : `url_api` sur un flux OCDE « non production » (§6) |
| `inegalite_satisfaction_vie` | a_verifier, a_etudier | extrait OCDE | conforme | — | Même remarque |
| `ecart_temps_partiel_fh` | a_etudier | API `sdg_05_30`, `lfsa_eppga` | **a_corriger** | F | Définition, libellé, unité : écart de **part du temps partiel dans l'emploi** (H − F) |
| `femmes_cadres_dirigeants` | a_etudier | BDM `010594728` | conforme | — | — |
| `femmes_parlement` | a_etudier | API `sdg_05_50` | conforme | — | Remarque : drapeau `d` 2003 (§6) |
| `femmes_direction_fonction_publique` | non vérifiée (M05) | catalogue BDM (API refusée deux fois) | **non_verifiable** | — | Identifiant, titre, zone, période conformes au catalogue ; valeurs non lues |
| `ecart_besoins_soins_revenu` | formule | API `hlth_silc_08` QU1, QU5 | **a_corriger** (mineur) | F | `rupture_2020`, `rupture_2022` ; chute 2014-2015 à signaler |
| `ecart_chomage_diplome` | formule | API `lfsa_urgaed` | **a_corriger** (mineur) | F, (J3) | Drapeaux de rupture et `definition_differente_2021` absents |
| `ecart_chomage_immigres` | formule | API `lfsa_urgacob` | conforme | (J5) | Famille à revoir après l'oubli O1 |
| `ecart_neet_immigres` | formule | API `edat_lfse_28` | **a_corriger** | F | `premiere_annee: 2006`, `nb_points_depuis_2000: 20` ; ruptures ; `faible_precision` sans drapeau `u` |
| `ecart_pauvrete_etrangers` | formule | API `ilc_li31` | conforme | — | Remarque : `b` 2008 (§6) |
| `ecart_pauvrete_fh` | formule | API `ilc_li02` F, M | **a_corriger** (mineur) | F, (J1) | Motif « 2004-2025 » contre `premiere_annee: 2000` ; 2000-2002 PCM arrondies ; ruptures 2001, 2004 |
| `ecart_pauvrete_jeunes_seniors` | formule | API `ilc_li02` 18-24, 65+ | **a_corriger** (mineur) | F | « croissante » faux (maximum 14,9 en 2010) ; `rupture_2004` |
| `ecart_reussite_bac_origine_sociale` | formule | extrait DEPP (API refusée) | conforme | — | Réserve : valeur 2020 (épreuves remplacées par le contrôle continu) non relue |
| `ecart_sante_percue_revenu` | formule | API `hlth_silc_10` QU1, QU5 | conforme | — | — |
| `ecart_sorties_precoces_immigres` | formule | API `edat_lfse_02` | conforme | — | Remarque : `rupture_2014` (§6) |
| `ecart_emploi_handicap` | tirage | API `hlth_dlm200` | conforme | — | Tranche d'âge non vérifiable (déjà signalée) |
| `inegalite_esperance_vie` | tirage | extrait PNUD | conforme | — | — |
| `part_revenu_1_pourcent_riches` | tirage | OWID (CSV France) ; extrait | conforme | — | — |
| `disparites_regionales_chomage` | tirage | API `lfst_r_lmdur`, `lfst_r_lmder` | **a_corriger** (mineur) | F | Saut 2000-2001 sans drapeau (28,5 → 42,7) à signaler pour la famille |

## 4. Détail des vérifications par fiche

Valeurs entre parenthèses : lues à la source le 14/10/2026 (API par WebFetch) ou dans les extraits du robot commités sous `docs/sources/series/`.

### 4.1 Fiches écartées

**`effet_redistribution`** — `ilc_di11i` « Effet des impôts et des transferts sociaux sur le ratio des parts de quintile S80/S20 dans le revenu » : 4,0 (2010) ; 3,4 à 4,0 jusqu'en 2019 ; 5,9 (2020, `b`) ; 6,7 (2022, `b`) ; 5,9 (2025). Le motif est exact. `type: moyen` (D19) et `sens: ambigu` sont défendables : l'effet grandit avec les inégalités primaires, et le couple « avant / après redistribution » porte l'information. Conforme.

**`ecart_chomage_fh`** — `une_rt_a`, 15-74 ans. F − H vaut +1,5 en 2003 (9,3 contre 7,8), −0,1 en 2012 (9,7 contre 9,8), +0,1 en 2018 (9,1 contre 9,0) et −0,2 en 2025 (7,6 contre 7,8) ; drapeau `d` de 2021 à 2025. L'écart oscille autour de 0 depuis 2012 : le motif est exact et l'écart est cohérent avec la méthode. Construction licite (même jeu, deux modalités de sexe). Conforme ; voir J1.

**`indice_developpement_genre`** — extrait PNUD : 1990-2023, 34 périodes, 11 valeurs distinctes, 0,993 en 2023. L'optimum est à 1, d'où `sens: ambigu` et l'écart. Conforme ; `incontournable: oui` relève de J2.

**`autonomisation_politique_femmes`** — extrait OWID : 1851, puis 1900-2025 (127 périodes), 52 valeurs distinctes, 0,929 en 2025, valeurs exactes. Deux erreurs :
1. **F** : `premiere_annee: 1900` et la note « ramenée à 1900 » sont obsolètes. D32 et le vérificateur v1.1 admettent désormais une année ≥ 1700 : il faut `premiere_annee: 1851` et retirer la note.
2. **M** : le motif « Dominé » ne répond pas à la définition de la méthode (§3 : même concept, pas meilleure en profondeur, fraîcheur, fréquence ni licence). Dans la famille `indice_composite_genre`, la série V-Dem est plus profonde (1851/1900 contre 1990) et plus fraîche (2025 contre 2023) que l'indice du PNUD, dont la licence est par ailleurs « à confirmer ». « Proche du plafond » et « fondé sur des experts » ne sont pas des motifs d'écart. Correction attendue : `recommandation: retenir_variante`, ou un motif de la méthode explicitement cité.

**`part_femmes_victimes_violences`** — catalogue BDM `010594734` : « Part des femmes parmi les victimes physiques et/ou sexuelles intrafamiliales », FM, 2010-2023, 12 points. La définition est conforme, et `sens: ambigu` (une part, pas un taux) est défendable. Erreurs mineures (**F**) :
1. La nature commune des 3 variantes (« indicateur ODD 5.i4b… », motif « autre champ de violences ») est fausse pour `melodi-005417`, qui est la copie Melodi de 5.i3b, c'est-à-dire un doublon technique de la série principale.
2. « La rupture de l'enquête de victimation de 2022 » est imprécis : 12 points sur 2010-2023 signifie qu'il manque deux années. Pour la série voisine BDM `010596046`, issue des mêmes enquêtes, l'audit `securite` lit 2010-2018 puis 2021-2023, sans valeur en 2019-2020 ; les valeurs de `010594734` n'ont pas pu être relues (BDM refusée à l'outil). À reformuler : « passage de l'enquête CVS à l'enquête VRS, deux années sans valeur (à lire sur la série) ».

**`egalite_libertes_groupes_sociaux`** — extrait OWID : 1789-2025, 237 périodes, 14 valeurs distinctes, 1,042 en 2025, valeurs exactes. Trois corrections :
1. **F** : `premiere_annee: 1789` (D32), note sur la borne de 1900 à retirer.
2. **M** : « presque constant, sans borne fixe » n'est pas un motif d'écart de la méthode. Soit la session mère ajoute ce motif à la méthode (proposition P3, §11), soit la fiche passe à `retenir`, ou à `retenir_variante` si une fiche CS16_1 devient principale d'une famille « discriminations selon l'origine » (O2).
3. **F** : la note affirme qu'« aucune série annuelle mesurée n'est au catalogue ». Or CS16_1 est déjà calculée par le robot (`drees__barometre_2000_2025_distributions.csv` : 23,80 % en 2015, 20,46 % en 2025, 7 vagues) et peut faire l'objet d'une fiche hors long-list avec `preuve` (D32). Par ailleurs, les atteintes à caractère raciste enregistrées (SSMSI, `m04-000282`) sont au catalogue et ont été écartées par `securite` (§8, I3).

**`revenu_relatif_seniors`** — `ilc_pnp2` : 0,90 (2000) ; 1,01 (2011) ; 1,04 (2015 et 2018) ; 0,97 (2025) ; pas de valeur en 2002-2003. Le rapport passe bien par la parité, et `sens: ambigu` est fondé. `premiere_annee: 2000` suit la long-list (la série commence en 1995). Conforme ; les drapeaux `b` de 2004 et 2008 manquent (§6, T1).

### 4.2 Incontournables

**`ecart_emploi_fh`** — `sdg_05_30` EMP : 8,0 (2009), 6,0 (2019), 5,7 (2025), `d` 2021-2025. La cible européenne (diviser par deux l'écart de 2019) donne bien 3,0 points. Conforme.

**`ecart_salaire_fh`** — `sdg_05_20` « Écart des rémunérations entre hommes et femmes (non corrigé) », champ B-S_X_O : 15,4 (2006), 16,0 (2019), 11,8 (2024), `p` en 2023-2024 ; aucune valeur avant 2006 pour la France. La dérogation (Eurostat principal plutôt que l'INSEE en EQTP) est motivée par l'indicateur ODD national 5.i1 et le cadre QoL. Conforme.

**`ecart_salaire_eqtp_fh`** — Les composantes M et F de `DS_DERA_PRIVE_SERIES_LONGUES` (salaire net EQTP mensuel moyen en euros constants, `WKTIME=_T`) existent au catalogue, 1996-2024. La construction est licite : même jeu, même mesure, même champ (privé, « France depuis 2000, métropole jusqu'en 1999 », d'après les métadonnées Melodi), et l'euro constant n'affecte pas un rapport. `formule`, `composantes`, `champ_geo_1999_2000` et la note documentent tout cela. Conforme ; valeurs non relues (Melodi fermé à l'outil), aucune n'est citée.

**`gini_niveau_de_vie`, `rapport_d9_d1_niveau_de_vie`, `part_niveau_de_vie_40_modestes`, `ratio_palma`, `rapport_s80_s20`** — Les cinq mesures rétropolées existent au catalogue Melodi (1996-2024, 25 points, FRANCE-FM). Les libellés confirment que `S90S40_SL` est bien le ratio de Palma (« niveau de vie cumulé des 10 % les plus riches / 40 % les plus pauvres ») et `S80S20_SL` le rapport des masses. Les métadonnées Melodi donnent S80/S20 = 4,62 en 2024 (note de lecture) et l'absence de rupture (« données rétropolées »). EU-SILC :
- Gini 29,2 (2014), 30,4 (2025), `b` 2020, 2022 ;
- S80/S20 `b` 2004, 2008, 2020, 2022 ;
- Palma recalculé (D10 / (QU1 + QU2)) : 23,9 / 22,9 = 1,04 (2018) et 24,6 / 21,6 = 1,14 (2025) ;
- Palma WID avant impôt : 2,64 (2022, extrait).

Les codes ODD cités (10.i1, 10.i2a, 10.i2b) correspondent au catalogue, et le seuil Palma = 2 du Doughnut figure au crosswalk. Une famille unique avec le S80/S20 principal est cohérente avec la méthode (statistiques substituables). Conforme.

**`indice_inegalite_genre`** — Extrait PNUD : 0,034 en 2023, rang 11, 1990-2023 (34 périodes). L'indicateur du Doughnut pour l'égalité femmes-hommes est bien l'IIG (crosswalk). Conforme.

### 4.3 Fiches signalées au journal M05

**`gini_patrimoine`** — Catalogue : `GINI_PATBRUT_HR`, FRANCE-FM, 2010-2024, 5 points. Le libellé « patrimoine net hors reste (en euros constants) » contredit le code, comme la fiche le signale (maintenance n° 13). Admission par D17/D28 (écart moyen de 3,5 ans) exacte. Conforme ; valeurs non relues.

**`part_patrimoine_10_pourcent_riches`** — Catalogue : `MASSE_PATBRUT`, `QUANTILE=D9TD10`, France hors Mayotte, 2015-2024, 4 points ; libellé « Masse détenue de patrimoine total », unité vide. L'unité de la fiche (« % du patrimoine brut total ») est plausible, mais ni le catalogue ni une API lisible ne la confirment : à vérifier par le robot. OCDE 1_3_VER : 49,9 en 2020 (extrait) ✓. Conforme (réserve).

**`dispersion_scores_pisa`** — Extrait OCDE 6_2_VER : 2018, 2022 ; 1,68 en 2022 ✓. Retenir une série de deux valeurs est conforme à D32 (jamais d'écart pour la seule brièveté). Remarque : `url_api` vise le flux `DSD_HSL@DF_HSL_CWB_INEQ`, qui existe mais porte l'annotation `NonProductionDataflow`, alors que `source_serie_id` et l'extrait du robot utilisent `DF_HSL_CWB` (§6, T5). Conforme.

**`inegalite_satisfaction_vie`** — Extrait OCDE 11_1_VER : 2013, 2018, 2021-2024 (6 périodes), 2,08 en 2024 ✓. `declaratif: oui` est cohérent (dispersion d'une évaluation). Même remarque sur `url_api`. Conforme.

**`ecart_temps_partiel_fh`** — `sdg_05_30` EMP_PT : −25,2 (2009), −17,5 (2025), `d` 2021-2025 ✓. **F** : la fiche définit l'indicateur comme la « différence entre le taux d'emploi à temps partiel des hommes et celui des femmes ». Or `lfsa_eppga` (« Personnes en emploi à temps partiel - % de l'emploi total », 20-64 ans) donne en 2025 H 8,1 − F 25,6 = **−17,5**, exactement la valeur publiée. Un écart de taux d'emploi à temps partiel (rapporté à la population) serait nettement plus petit en valeur absolue. En 2009, l'écart des parts vaut −24,1 contre −25,2 publié : l'écart d'un point vient sans doute de révisions, et les métadonnées `sdg_05_30` lues ne détaillent pas la modalité. Correction : libellé, définition et unité en « écart de part du temps partiel dans l'emploi (hommes − femmes, 20-64 ans) », à confirmer dans les métadonnées. Les variantes INSEE (« part du temps partiel dans l'emploi ») et le raccordement deviennent alors cohérents.

**`femmes_cadres_dirigeants`** — BDM `010594728` « Proportion des femmes cadres dirigeants - Cadres dirigeants dans le privé », FE : 21,5 (2010), 30,1 (2023), NaN en 2024-2025 ✓. La loi du 24 décembre 2021 (n° 2021-1774) figure au crosswalk (30 % puis 40 %). Conforme.

**`femmes_parlement`** — `sdg_05_50` PARL_NAT : 11,6 (2003, `d`), 26,2 (2016), 36,3 (2017), 37,2 (2025) ✓. Le rattachement (A8, D33) est cohérent avec la règle 900 de `democratie`. Conforme ; drapeau `d` 2003 à ajouter (§6).

**`femmes_direction_fonction_publique`** — L'API BDM a été refusée à l'outil (robots.txt, deux essais). Le catalogue donne « Part des femmes parmi l'encadrement supérieur et de direction dans la fonction publique - Total », FR-D976, 2012-2023, statut P : identifiant, zone et période sont conformes. **Non vérifiable** pour les valeurs (la fiche n'en cite pas).

### 4.4 Écarts construits

**`ecart_besoins_soins_revenu`** — `hlth_silc_08` (raison « trop cher, trop loin ou liste d'attente », 16 ans ou plus). QU1 − QU5 vaut 4,3 (2008), 5,9 (2014), 2,8 (2015), 1,9 (2017), 4,5 (2020), 3,7 (2025) : signe constant. Construction licite. **F** (mineur) : `b` en 2020 et en 2022 sur les deux composantes, absents de `qualite`. La chute de 2014 à 2015 (QU1 6,7 → 3,1 ; QU5 0,8 → 0,3), sans drapeau, est à signaler comme rupture possible. Attendu : `rupture_2020`, `rupture_2022`, `rupture_possible_2015` et une phrase dans la note.

**`ecart_chomage_diplome`** — `lfsa_urgaed`, 15-74 ans. CITE 0-2 − CITE 5-8 vaut 9,8 (2000), 6,8 (2008), 12,3 (2016), 9,4 (2025) : signe constant. Construction licite. **F** (mineur) : aucun drapeau dans `qualite` alors que la source porte `b` en 2003, 2005, 2006, 2013 et 2014, `bd` en 2021 et 2024, `d` de 2021 à 2025. Attendu : `rupture_2003` … `rupture_2024`, `definition_differente_2021`. J3 : le sous-thème « origine sociale et mobilité » ne convient pas à un écart selon le diplôme de la personne elle-même.

**`ecart_chomage_immigres`** — `lfsa_urgacob` : 19,7 / 9,4 (2000) ; 13,1 / 7,0 (2025) ; ruptures 2003, 2005, 2006, 2014, 2021, 2024. Tout est exact. Conforme ; la famille est à revoir après O1 (J5).

**`ecart_neet_immigres`** — **F** : la modalité « nés hors UE » d'`edat_lfse_28` n'a **aucune valeur en 2004 et 2005**. La série va de 2006 (29,8 %) à 2025 (25,3 %), soit 20 points, et non 2004-2025 (22 points) comme l'écrivent la fiche, son motif et le tableau. M05 a corrigé ce point pour `edat_lfse_02`, pas pour ce jeu. Écart : 16,4 (2006), 13,1 (2025), signe constant. Autres corrections : la source porte `b` 2014, `bd` 2021 et 2024, `d` 2021-2025, absents de `qualite`. Aucun drapeau `u` n'existe, alors que la note demande de « lire les drapeaux de fiabilité » : `faible_precision` est donc à justifier autrement (effectifs) ou à retirer. Attendu :
- `premiere_annee: 2006`, `nb_points_depuis_2000: 20`, motif réécrit ;
- `qualite` complétée ;
- note « valeurs lues sur l'API » comme pour `ecart_sorties_precoces_immigres` ;
- `edat_lfse_28` à ajouter à la ligne de maintenance n° 17.

**`ecart_pauvrete_etrangers`** — `ilc_li31` (18 ans ou plus) : 32,8 / 11,8 (2004) ; 37,8 (2013 et 2019) ; 39,7 (2020) ; 34,0 / 12,8 (2025) ✓. Les composantes sont explicites (seul écart construit avec `composantes` complètes). Conforme ; `b` 2008 à ajouter (§6).

**`ecart_pauvrete_fh`** — `ilc_li02` : F − H vaut 1,5 (2004), −0,2 (2018), 2,0 (2025) ✓. **F** (mineur) : le motif dit « 2004 à 2025 », mais la fiche porte `premiere_annee: 2000` et 25 points. La source a bien des valeurs en 2000-2002, mais ce sont des valeurs PCM arrondies à l'unité (16 et 15 %, puis 13 et 12 %), avec `b` en 2001 puis en 2004, et rien en 2003. Attendu : `rupture_2001`, `rupture_2004` et une phrase sur les valeurs entières de 2000-2002 ; à défaut, aligner le motif sur 2000. La valeur 65 ans ou plus de la note (13,1 contre 9,8) n'a pas été relue. J1 sur le traitement du changement de signe.

**`ecart_pauvrete_jeunes_seniors`** — `ilc_li02` : 5,2 (2004), 9,9 (2015), 11,2 (2025) ✓ ; 18-24 ans depuis 2004 ✓. **F** (mineur) : le motif dit « croissante », or l'écart culmine à **14,9 en 2010** (24,3 − 9,4) et vaut 9,6 en 2022 et 9,5 en 2024. Attendu : « de signe constant, maximum de 14,9 points en 2010 » et `rupture_2004` dans `qualite` (la note cite déjà la rupture).

**`ecart_reussite_bac_origine_sociale`** — Extrait DEPP : 97,1 (cadres) et 87,5 (ouvriers) en 2025, 1997-2025 ✓. Construction licite, même jeu. Comme la fiche l'indique, l'écart « toutes séries » mêle un effet de composition : par série, il ne vaut que 5,2 points en général, 7,1 en technologique et 8,2 en professionnel. Réserve : en 2020, les épreuves ont été remplacées par le contrôle continu, et la valeur de cette année n'a pas pu être relue (`data.education.gouv.fr` refusé à l'outil). Si elle saute, ajouter `rupture_2020`. Conforme.

**`ecart_sante_percue_revenu`** — `hlth_silc_10` (« très bonne ou bonne », 16 ans ou plus) : 75,7 − 59,2 = 16,5 (2005) et 75,5 − 54,2 = 21,3 (2025) ✓ ; `b` 2020 et 2022 ✓. Conforme.

**`ecart_sorties_precoces_immigres`** — `edat_lfse_02` : nés hors UE 21,4 (2006), 12,7 (2025) ✓ ; écart 9,4 puis 6,0, signe constant. Conforme ; `rupture_2014` manque (`b` en 2013 et en 2014 ; la note cite bien 2014) et aucun drapeau `u` ne justifie `faible_precision` (§6).

### 4.5 Tirage

**`ecart_emploi_handicap`** — `hlth_dlm200` SM_SEV : 20,4 (2014), 15,7 (2018, minimum), 24,1 (2021, maximum), 21,6 (2025), `b` 2020 et 2022 ✓. Le jeu n'a pas de dimension d'âge : la tranche d'âge reste à confirmer dans les métadonnées (déjà signalé par `champ_age_a_verifier`). Rattachement à `egalites` (écart entre groupes, R3) cohérent. Conforme.

**`inegalite_esperance_vie`** — Extrait PNUD `ineq_le` : 2010-2023, 14 périodes, 3,71 en 2023 ✓. Conforme.

**`part_revenu_1_pourcent_riches`** — OWID (France) : 11,33 (2000), 9,55 (2013), 12,1 (2022) ✓ ; 1910, 1915-2022 ✓. La dérogation au niveau 1 est motivée. Conforme.

**`disparites_regionales_chomage`** — `lfst_r_lmdur` DISP_NUTS2 : 1999-2025, aucun drapeau. La valeur passe de 28,5 (2000) à **42,7 (2001)**, le plus fort mouvement de la série. La dispersion de l'emploi, principale de la famille, saute au même moment (6,9 → 8,4). **F** (mineur) : ce saut simultané, non documenté, évoque un changement de couverture des régions NUTS 2 (hypothèse non vérifiée). Attendu : `rupture_possible_2001` et une note sur les trois fiches de la famille `disparites_regionales`, à confirmer par les métadonnées régionales de l'enquête Forces de travail.

## 5. Écarts construits : licéité et documentation

Les 12 fiches à `formule` combinent **deux modalités d'un même jeu**, donc d'une même source, d'un même champ et d'une même unité :
- `une_rt_a`, `ilc_li02` (deux fois), `lfsa_urgacob`, `ilc_li31`, `edat_lfse_28`, `edat_lfse_02`, `lfsa_urgaed`, `hlth_silc_08`, `hlth_silc_10` ;
- Melodi `DS_DERA_PRIVE_SERIES_LONGUES` (même mesure) ;
- DEPP (même jeu, même variable).

Le sens « bas = mieux » est correct partout : l'ordre des termes est choisi pour que l'écart soit positif quand le groupe défavorisé l'est (QU1 − QU5 pour les besoins non satisfaits, QU5 − QU1 pour la bonne santé). Le signe a été vérifié sur toute la période pour les 10 écarts relus sur l'API Eurostat. Pour le baccalauréat, il ne l'a été qu'en 2025 (extrait du robot, sans série annuelle) ; pour le salaire en EQTP, pas du tout (Melodi). Seul le chômage femmes-hommes a un signe alterné, et il est écarté.

Les trois « autres » fichiers comptés dans les 15 :
- `ecart_emploi_fh` est un écart publié par Eurostat ; ses composantes, des taux par sexe, sont en variantes ;
- `ratio_palma` repose sur une mesure INSEE publiée ; le Palma EU-SILC n'est qu'un calcul d'appoint, documenté dans `notes` avec les valeurs lues ;
- `indice_inegalite_genre` est un composite publié.

Rien à corriger sur leur construction.

Documentation : **9 des 12** écarts construits ne portent pas de champ `composantes`. Leur `source_serie_id` est un « paquet » de modalités de la long-list, et la formule désigne les modalités en clair (`c_birth=NEU27_2020_FOR`). C'est licite au sens de D32, mais le pipeline devra analyser un texte libre : voir la proposition P1 (§11).

## 6. Contrôles hors échantillon et corrections transversales

| # | Fiches | Constat | Source | Correction |
|---|---|---|---|---|
| T1 | `revenu_relatif_seniors` (2004, 2008) ; `ecart_pauvrete_etrangers` (2008) ; `ecart_sorties_precoces_immigres` (2014) ; `femmes_parlement` (`d` 2003) | Drapeaux Eurostat absents de `qualite` | API (§4) | Compléter `qualite`. |
| T2 | `discriminations_femmes_temoins`, `societe_juste_percue`, `inegalites_percues_hausse` | `geo: FM` déjà juste, mais `qualite: champ_geo_a_corriger` et note « geo FR à corriger » obsolètes ; `source_serie_id` cite deux pièces jointes (`2000_2024` + `2025`) alors que `url_api` vise `barometre2000_2025_diff_csv` | fiches `liens_bien_etre` corrigées après audit | `enquete_metropole` à la place de `champ_geo_a_corriger`, note retirée, `source_serie_id` aligné sur la pièce jointe unique (comme en `liens_bien_etre`). |
| T3 | `societe_juste_percue` (IN01), `inegalites_percues_hausse` (IN02) | IN01 : non-réponses (au dénominateur) de 1,3 % (2017) à 2,9 % (2018), puis 2,5 à 3,3 %, le saut déjà signalé en `liens_bien_etre` et `securite`. IN02 : la modalité 3 « (Sont restées stables) » passe de 13 à 22 % (2000-2006) à 5-9 % (2007-2025), avec un pic isolé à 16,6 % en 2014 ; la modalité 1 retenue (« ont plutôt augmenté ») en est affectée (76,1 % en 2014 contre 86,7 % en 2013) | distributions et dictionnaire DREES du robot | `rupture_possible_2018` (IN01) ; pour IN02, `rupture_possible_2007` et `anomalie_2014` dans `qualite`, avec une note (modalité « stable » proposée ou spontanée selon les années, à vérifier dans les questionnaires). |
| T4 | `disparites_regionales_emploi`, `_chomage`, `_neet` | Saut de 2001 commun aux dispersions régionales | API `lfst_r_lmder`, `lfst_r_lmdur` | `rupture_possible_2001` (§4.5). |
| T5 | `dispersion_scores_pisa`, `inegalite_satisfaction_vie` | `url_api` sur `DF_HSL_CWB_INEQ` (flux « non production ») ; `source_serie_id` et le robot sur `DF_HSL_CWB` | API OCDE (structure du flux) ; extrait `ocde__hsl_bien_etre_actuel.csv` | Aligner `url_api` sur `DF_HSL_CWB` (flux de production, déjà lu par le robot). |

Fiches hors échantillon relues sans constat : `coefficient_inegalite_humaine` (8,97 en 2023 ✓), `ecart_pension_fh`, `ecart_pauvrete_enfants_education_parents`, `femmes_filieres_scientifiques`, `femmes_postes_encadrement`, `rapport_d9_d1_salaires`, `rapport_s80_s20_avant_redistribution` (mesure `S80S20_SL_BR` au catalogue ✓), `disparites_regionales_neet`.

## 7. Complétude : oublis

Long-list `egalites` : les 330 lignes sont affectées ; je ne conteste aucun des 6 écarts en bloc (27 lignes) ni des 3 renvois (88 lignes). Les oublis sont dans **d'autres long-lists** ou dans les **sorties du robot** :

| # | Oubli | Données (lues) | Importance | Proposition |
|---|---|---|---|---|
| O1 | **Écart de taux d'emploi entre nationaux et ressortissants de pays hors UE, 20-64 ans** : `sdg_08_30a`, long-list `travail` (`estat-053141` NAT, `estat-053142` NEU27_2020_FOR), éligibles, 2000-2025, 26 points | 68,5 / 45,5 (2000) ; 71,3 / 46,8 (2016) ; 76,8 / 57,5 (2025), soit un écart de 23,0, 24,5 puis 19,3 points, de signe constant ; `b` 2003, 2005, 2006, 2014, `bd` 2021 et 2024 ; aucun `u` | **forte** : indicateur Eurostat *Quality of life* du crosswalk ; seul écart d'emploi selon l'origine sans biais d'âge | Écart construit (`formule` NAT − NEU27_2020_FOR, deux `composantes`), famille `ecart_emploi_origine`, variante principale à trancher avec `ecart_chomage_immigres` (J5). Corriger le journal M05 §2.3, le motif de `ecart_chomage_immigres_emploi` et la ligne de maintenance n° 16 (pour la nationalité, la série 20-64 ans **est** au catalogue). |
| O2 | **Témoins de discriminations liées à l'origine ethnique** : baromètre DREES CS16_1 « Au cours des 12 derniers mois, avez-vous été le·la témoin de discriminations liées à l'origine ethnique ? » | 2015, 2017, 2019-2021, 2023, 2025 (7 vagues, écart moyen 1,7 an ≥ 1,5, D28) ; « oui » 23,80 (2015) → 20,46 % (2025), d'après les distributions du robot (non-réponses au dénominateur) | **forte** : seule mesure directe de A8 | Fiche hors long-list (D32 : `hors_longlist: oui`, `preuve: docs/sources/series/drees__barometre_2000_2025_distributions.csv`, `geo: FM`, `declaratif: oui`, `frequence: irreguliere`), `retenir`. CS16_4 (religion) en variante ou famille voisine ; CS16_2 (orientation sexuelle), CS16_3 (âge) et CS16_5 (handicap) en variantes ou écartées avec un motif. La ligne de maintenance n° 14 devient « catalogage ». |
| O3 | **Part des femmes dans les conseils des plus grandes sociétés cotées** : `sdg_05_61`, long-list `education` (`estat-002070` NEXEC_EXEC, `estat-002069` NEXEC), éligibles, 2012-2025, 14 points | NEXEC_EXEC : 21,4 (2012), 40,0 (2016), 47,1 (2024), 46,5 (2025), sans drapeau (NEXEC non relu : limite de débit) | **forte** : « représentation économique » (contenu explicite) ; cible légale de 40 % (loi n° 2011-103, crosswalk « objectifs officiels ») | Fiche importée de la long-list `education` (rattachement proposé), famille `femmes_postes_direction` ou famille propre, `sens: haut` jusqu'à la parité ; corriger la ligne de maintenance n° 19 (« aucun n'est au catalogue » est faux pour cet indicateur). |
| O4 | Écart de **taux de surqualification** selon le pays de naissance : `lfsa_eoqgac`, long-list `travail` (`estat-054299`), 2000-2025 | nés hors UE 19,3 / 33,9 / 30,5 contre nés en France 17,8 / 21,0 / 19,3 (2000 / 2015 / 2025), soit un écart de 1,5, 12,9 puis 11,2 points | moyenne : le « déclassement » des immigrés diplômés, souvent rapproché des discriminations | Écart construit, famille d'origine, `retenir_variante` ou fiche propre. |
| O5 | Écart de **revenu médian** selon le pays de naissance ou la nationalité : `ilc_di16`, `ilc_di15`, long-list `niveau_de_vie` (FOR et NAT 2004-2025) ; autres écarts selon l'origine possibles : privation (`ilc_mdsd04/05`), surpeuplement (`ilc_lvho15/16`), santé perçue (`hlth_silc_23/24`) | valeurs non relues | moyenne à faible | Au moins une phrase au journal ; le rapport des médianes est le candidat le plus lisible. |
| O6 | **Mobilité intergénérationnelle** : `ilc_igtp01` (niveau d'éducation des enfants adultes selon celui des parents), `ilc_igtp03` (pauvreté selon le diplôme des parents) ; jeux hors filtre (début 2019) | 2019 et 2023 (catalogue des jeux) | moyenne : « mobilité sociale » est un contenu explicite ; la dimension n'a que des mesures indirectes | Fiche hors long-list (jeu au catalogue des jeux, D32), à recommander comme `dispersion_scores_pisa` (2 valeurs) ; sinon motiver l'absence au journal. |
| O7 | **Atteintes à caractère raciste, xénophobe ou antireligieux enregistrées** (SSMSI, `m04-000282`) et atteintes anti-LGBT+ (`m04-000283`), long-list `securite`, écartées par la règle 1160 de `securite` (« rattachement à egalites à examiner ») | 2016-2023 (8 points) | faible (série enregistrée, `sens` discutable) | Les citer dans le journal `egalites` (A8) et laisser la session mère trancher le rattachement (I3). |
| O8 | Part des femmes parmi les spécialistes du numérique (`isoc_sks_itsps`) et diplômés par domaine et sexe (`educ_uoe_grad10`), long-list `education` | non relues | faible | Variantes possibles de `femmes_filieres_scientifiques`, à mentionner. |

Autres contenus de la dimension :
- **Territoires** : présents (3 fiches NUTS 2) ; l'absence d'écart urbain/rural (`ilc_li43`, signe non univoque) est motivée au journal M05.
- **Générations** : présentes (1 fiche retenue, 1 écartée).
- **Écarts femmes-hommes** : présents (16 fiches).
- **Incontournables du crosswalk** (§5) : inégalité de revenu (5 cadres) et écarts femmes-hommes (4 cadres) ont des fiches `retenir` marquées `incontournable: oui`.
- **Concepts à deux cadres** : patrimoine (SSF, OCDE) présent ; « discriminations » (Eurostat QoL, « à développer ») absent tant que O2 n'est pas traité.

## 8. Cohérence inter-dimensions

Contrôle mécanique sur les 137 fiches de `egalites` (50), `securite` (33), `liens_bien_etre` (22) et `democratie` (32) (séries principales, composantes, variantes) : **aucun identifiant commun, aucune série commune**. Le vérificateur compte 0 ligne déjà prise ailleurs. Les dimensions `travail`, `niveau_de_vie`, `sante` et `education` n'étant pas fichées, le contrôle R1 complet reste à faire quand elles le seront.

| # | Constat | Correction ou décision |
|---|---|---|
| I1 | `sdg_05_50` : `democratie` le renvoie à `egalites` (règle 900), `egalites` l'importe en fiche et en variante | Cohérent (A8, D33). |
| I2 | R3 : aucune série principale n'est un niveau ou un taux de pauvreté. Mais **12 séries de niveau** sont en `variante_de` d'écarts : 8 séries INSEE par sexe issues de la long-list `travail` (chômage `001688533/535`, `011818546/547` ; emploi `011818672/695` ; temps partiel `011818641/656`) et 4 séries `ilc_li32` à `ilc_li34` de `niveau_de_vie`. Ce sont des composantes, pas des variantes du même indicateur (méthode §1) | Les marquer « composante » (nature) et prévoir que `travail` et `niveau_de_vie` les gardent comme niveaux (D32 « composantes partagées ») ; sinon le vérificateur v1.1 signalera une double prise quand ces dimensions seront fichées. |
| I3 | Atteintes racistes et anti-LGBT+ enregistrées : écartées en `securite` avec « rattachement à egalites à examiner », ignorées en `egalites` | Trancher le rattachement (A8 place les discriminations selon l'origine en `egalites`) ; à défaut, la mention de O7. |
| I4 | Baromètre DREES : drapeau `champ_geo_a_corriger` ici, `enquete_metropole` en `liens_bien_etre` et `securite` ; rupture possible de 2018 signalée là-bas, pas ici | T2, T3. |
| I5 | Lignes des long-lists `travail`, `education`, `sante`, `niveau_de_vie` utilisées par `egalites` (169, dont 18 en série principale) | Consigne aux futurs agents M05 de ces dimensions : règles `autre_dimension:egalites` pour les lignes d'écart publiées (`earn_gr_gpgr2*`, `hlth_dlm200`, parts ERFS…) et maintien des ventilations comme niveaux (R1, R3). |
| I6 | Voisinages sans doublon : `egalite_libertes_groupes_sociaux` (V-Dem) et l'indice de démocratie égalitaire V-Dem, variante de `democratie/democratie_liberale_vdem` ; `part_femmes_victimes_violences` (ODD 5.i3b, part) et `securite/victimes_violences_conjugales` (variante ODD 5.i3a, nombre) ; `inegalite_satisfaction_vie` et `liens_bien_etre/satisfaction_vie` | Aucune correction ; à noter pour le contrôle de redondance du gel 2. |
| I7 | `ecart_chomage_diplome` et `ecart_chomage_immigres` construits sur des ventilations de la long-list `travail` ; O1 et O4 aussi | Même consigne qu'I5. |

## 9. Synthèse par nature

**Erreurs factuelles**, de la plus grave à la moins grave :
1. Journal M05 §2.3, motif de `ecart_chomage_immigres_emploi` et ligne de maintenance n° 16 : « taux d'emploi selon l'origine seulement 15 ans ou plus au catalogue ». C'est faux pour la nationalité : `sdg_08_30a`, 20-64 ans, est au catalogue et dans la long-list `travail`. Conséquence : oubli O1.
2. Ligne de maintenance n° 19 et compte rendu M05 §4 : « femmes dans les conseils d'administration … aucun n'est au catalogue ». C'est faux : `sdg_05_61` est au catalogue et dans la long-list `education`. Conséquence : oubli O3.
3. Compte rendu M05 §5.4 et note d'`egalite_libertes_groupes_sociaux` : « aucune mesure directe des discriminations au catalogue ». C'est inexact : CS16_1 a été calculée par le robot (preuve disponible, D32), et les atteintes racistes enregistrées sont au catalogue (écartées en `securite`). Conséquence : oubli O2.
4. `ecart_neet_immigres` : période 2006-2025 et 20 points, au lieu de 2004-2025 et 22 points.
5. `ecart_temps_partiel_fh` : écart de parts du temps partiel dans l'emploi, pas de taux d'emploi à temps partiel.
6. `autonomisation_politique_femmes` (1851) et `egalite_libertes_groupes_sociaux` (1789) : `premiere_annee` et notes obsolètes depuis D32.
7. Drapeaux de rupture : aucun pour `ecart_chomage_diplome` ni pour `ecart_neet_immigres`, partiels ailleurs (§4.4, T1).
8. Mots ou périodes inexacts dans les motifs : « croissante » (`ecart_pauvrete_jeunes_seniors`), « 2004-2025 » (`ecart_pauvrete_fh`).
9. Saut de 2001 non signalé (`disparites_regionales_*`) ; chute de 2015 non signalée (`ecart_besoins_soins_revenu`) ; IN02 (2007, 2014) et IN01 (2018) (T3).
10. Nature erronée d'une variante de `part_femmes_victimes_violences`.

**Motifs ou champs non conformes à la méthode** : écarts de `autonomisation_politique_femmes` (« dominé » au sens non méthodique) et de `egalite_libertes_groupes_sociaux` (« presque constant »).

**Désaccords de jugement**, à trancher par la session mère ou Léo (je ne les compte pas comme erreurs) :
- **J1** — Écarts qui changent de signe. `ecart_chomage_fh` est écarté pour un signe alterné, `ecart_pauvrete_fh` retenu malgré une valeur négative (2018). Les deux décisions se défendent, mais une règle commune manque. On pourrait par exemple admettre l'écart absolu \|F − H\| avec `sens: bas` quand l'optimum est la parité ; cela rendrait aussi utilisables le revenu relatif des seniors et l'indice de développement de genre (P2).
- **J2** — `incontournable: oui` porté par toute la famille `indice_composite_genre`, y compris la série V-Dem et l'IDG, qui ne sont pas le concept du crosswalk (l'IIG). Réserver le drapeau aux fiches qui mesurent le concept, ou écrire la règle « par famille » dans la méthode.
- **J3** — `ecart_chomage_diplome` est rangé en « origine sociale et mobilité » : un écart selon le diplôme de la personne n'est pas un écart selon l'origine sociale. Sous-thème à renommer (« diplôme ») ou fiche à justifier.
- **J4** — « Quasi constant » comme motif d'écart (P3).
- **J5** — Famille `ecart_emploi_origine` : avec O1, la variante principale est à réexaminer. L'écart d'emploi des 20-64 ans selon la nationalité est l'indicateur QoL ; l'écart de chômage selon le pays de naissance couvre les immigrés naturalisés.
- **J6** — `effet_redistribution` est écarté alors que le contenu de la dimension le cite. C'est défendable et déjà posé à Léo par M05 ; rien à ajouter.

**Oublis** : O1 à O8 (§7), dont trois de fond (O1, O2, O3).

## 10. Corrections ordonnées pour l'agent correcteur

1. **O1** — Règles de présélection `longlist = travail` pour `estat-053141` et `estat-053142` (`sdg_08_30a`). Nouvelle fiche d'écart construit (NAT − NEU27_2020_FOR, `composantes`, `formule`, `rattachement_propose`), famille `ecart_emploi_origine`, principale à trancher (J5). Corriger le journal M05 §2.3, le motif du groupe `ecart_chomage_immigres_emploi` et la ligne de maintenance n° 16.
2. **O3** — Règle `longlist = education` pour `estat-002070` (fiche) et `estat-002069` (variante). Nouvelle fiche « femmes dans les conseils des grandes sociétés cotées » (`sens: haut`, cible légale à citer au socle des bornes). Corriger la ligne de maintenance n° 19.
3. **O2** — Fiche hors long-list CS16_1, avec preuve et `statut_serie: disponible` (valeurs déjà calculées). Décision sur CS16_2 à CS16_5. Ligne de maintenance n° 14 réécrite (catalogage). Puis revoir la note et la recommandation d'`egalite_libertes_groupes_sociaux` (§4.1).
4. **`ecart_neet_immigres`** : `premiere_annee: 2006`, `nb_points_depuis_2000: 20`, motif ; `qualite` (`rupture_2014`, `rupture_2021`, `rupture_2024`, `definition_differente_2021`), justification ou retrait de `faible_precision` ; note « lu sur l'API » ; `edat_lfse_28` dans la ligne de maintenance n° 17.
5. **`ecart_temps_partiel_fh`** : libellé, définition et unité « écart de part du temps partiel dans l'emploi, hommes − femmes, 20-64 ans » (à confirmer dans les métadonnées `sdg_05_30`).
6. **`autonomisation_politique_femmes`** : `premiere_annee: 1851`, note retirée ; recommandation conforme à la méthode (`retenir_variante` ou motif cité).
7. **`egalite_libertes_groupes_sociaux`** : `premiere_annee: 1789`, note retirée et corrigée ; recommandation selon la décision sur P3 et O2.
8. **Ruptures et mentions** : `ecart_chomage_diplome`, `ecart_besoins_soins_revenu` (§4.4) ; `ecart_pauvrete_fh` ; `ecart_pauvrete_jeunes_seniors` (« croissante ») ; T1 ; `disparites_regionales_*` (T4) ; DREES (T2, T3).
9. **`part_femmes_victimes_violences`** : nature des variantes (`melodi-005417` en doublon technique), formulation de la rupture CVS/VRS.
10. **T5** : `url_api` OCDE sur `DF_HSL_CWB`.
11. Si la session mère les accepte : O4, O6 (fiches) ; O5, O7, O8 (mentions au journal) ; J2, J3 (drapeau et sous-thème).
12. Puis `python scripts/preselection.py --dimension egalites --maj-fiches`, `verifier_fiches.py --dimension egalites --tableau`, `verifier_fiches.py --dimension egalites` (0 erreur) et `pytest`.

## 11. Questions pour la session mère et propositions pour la méthode commune

1. **P1 — Écarts construits lisibles par machine.** Exiger `composantes` (une `serie_id` complète par terme, comme `ecart_pauvrete_etrangers`) et une `formule` normalisée (`A - B`, `(A - B) / A`). Aujourd'hui, 9 fiches sur 12 désignent les modalités dans un texte libre.
2. **P2 — Écarts à optimum de parité** (J1). Admettre l'écart absolu \|A − B\| (`sens: bas`) ou un indicateur de « désavantage » tronqué, plutôt que `sens: ambigu ⇒ ecarter`, pour les écarts entre groupes et les rapports dont l'optimum est 1 (chômage femmes-hommes, revenu relatif des seniors, IDG) ; en faire une règle de la méthode.
3. **P3 — Séries quasi constantes** (J4). Ajouter ou refuser explicitement un motif d'écart « série quasi constante sur 2000-aujourd'hui (moins de *k* valeurs distinctes) ». Deux fiches V-Dem en dépendent ici, et des fiches V-Dem de `democratie` sont concernées.
4. **P4 — Recherche des oublis.** Avant de déclarer une série « non cataloguée », chercher dans **toutes** les long-lists et dans `eurostat_series_catalogue.csv.gz` par jeu, pas seulement par libellé. Deux affirmations « absent du catalogue » se sont révélées fausses (O1, O3). Ajouter au vérificateur un avertissement quand une ligne de maintenance cite un jeu déjà présent dans une long-list.
5. **P5 — Périodes des paquets** (maintenance n° 17). Tant que le catalogue n'a pas de période par modalité, la méthode devrait imposer la lecture sur l'API de la première année de la modalité utilisée par toute formule. L'oubli de `ecart_neet_immigres` vient de là.
6. **Drapeau `incontournable`** (J2) : par concept (fiche) ou par famille ?
7. **Rattachements** (I2, I3, I5, I7) : statut des séries de niveau tenues en variantes d'écarts ; rattachement des atteintes racistes enregistrées ; consigne aux agents M05 `travail`, `niveau_de_vie`, `sante` et `education`.

## Annexe — sources consultées

| Source | Usage |
|---|---|
| `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<jeu>?…&lang=fr`, avec `ilc_di11i`, `une_rt_a` (F, M), `ilc_pnp2`, `sdg_05_30`, `lfsa_eppga` (F, M), `sdg_05_20`, `sdg_05_50`, `ilc_li02` (F, M, 18-24, 65+), `ilc_li31` (FOR, NAT), `lfsa_urgacob` (NEU27_2020_FOR, NAT), `edat_lfse_28`, `edat_lfse_02` (idem), `hlth_silc_08` (QU1, QU5), `hlth_silc_10` (QU1, QU5), `lfsa_urgaed` (ED0-2, ED5-8), `hlth_dlm200`, `lfst_r_lmdur`, `lfst_r_lmder`, `ilc_di01` (D10, QU1, QU2), `ilc_di12`, `ilc_di11`, `sdg_08_30a` (NAT, NEU27_2020_FOR), `sdg_05_61` (NEXEC_EXEC), `lfsa_eoqgac` (NEU27_2020_FOR, NAT) | §4, §7 |
| `https://ec.europa.eu/eurostat/cache/metadata/en/sdg_05_30_esmsip2.htm` | définition de l'écart d'emploi (ne détaille pas EMP_PT) |
| `https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/010594728` | `femmes_cadres_dirigeants` |
| `https://sdmx.oecd.org/public/rest/dataflow/OECD.WISE.WDP/DSD_HSL@DF_HSL_CWB_INEQ/1.1` | existence et statut du flux (T5) |
| `https://ourworldindata.org/grapher/incomes-of-the-richest.csv?v=1&csvType=full&useColumnShortNames=true&country=~FRA` | `part_revenu_1_pourcent_riches` |
| Refusés ou non lus : BDM `010594734` et `010760765` (robots.txt, deux essais) ; `data.education.gouv.fr` (robots.txt) ; `api.insee.fr/melodi` (refusé aux audits précédents, non retenté) ; métadonnées `hlth_dlm_esms` (erreur) ; `sdg_05_61` NEXEC (HTTP 429) | — |
| Dépôt : `catalogues/*` (Melodi, BDM, Eurostat séries et jeux, `*_non`, long-lists) ; `docs/sources/echantillons_insee/melodi_catalog_all_2026-10-13.json.gz` ; `docs/sources/series/` (`pnud__hdr25_series_composites_france.csv`, `owid__*`, `ocde__hsl_inegalites_verticales.csv`, `ocde__hsl_bien_etre_actuel.csv`, `depp__fr-en-reussite-au-baccalaureat-origine-sociale.csv`, `drees__barometre_2000_2025_distributions.csv`, `drees__barometre_2000_2025_couverture.csv`, dictionnaires DREES 2025) ; `docs/methodo/30_indicateurs_cadres_reference.csv` | §4 à §8 |
