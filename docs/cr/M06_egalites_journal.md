# Journal de bord — M06, audit croisé de la dimension `egalites`

Agent auditeur M06 (session neuve, n'a pas participé à M05 `egalites`), 14 octobre 2026. Branche `m06-egalites` créée depuis `origin/main` (`1a0697c`, fusion de la PR #12). Rapport : `docs/validation/audit_egalites.md`. Aucune fiche, aucun tableau M05, aucun script ni catalogue n'a été modifié.

## 0. Mise en route

- `git fetch origin && git checkout -B m06-egalites origin/main`.
- Lus : `CLAUDE.md` ; charte §3.4, §3.6, §4, §5.1 ; journal des décisions D13–D33 ; fiche `docs/missions/M06_audit_croise.md` ; méthode commune `docs/methodo/33_methode_fiches_M05.md` (v1.1) ; `indicateurs/dimensions.yaml` (définition, contenu, exclusions d'`egalites`, règles R1–R8) ; audits `docs/validation/audit_securite.md` et `audit_liens_bien_etre.md` (format, niveau d'exigence) et commit de corrections `4d07019` ; compte rendu et journal M05 `egalites` ; `docs/cr/maintenance_catalogues.md` (lignes 10-20).
- Contrôles préalables : `python -m pytest -q` → 397 réussis ; `python scripts/verifier_fiches.py --dimension egalites` → 0 erreur, 0 avertissement (50 fiches, 37 familles, 32 `retenir`, 11 `retenir_variante`, 7 `ecarter`, 5 déclaratives, 5 composites, 4 à vérifier, 0 hors long-list, 11 incontournables, 331 variantes, 0 ligne prise ailleurs).
- Le bac à sable de session est partagé avec d'autres agents : mes scripts de travail sont dans un sous-dossier privé du bac à sable (`m06eg/`), aucun n'est commité.

## 1. Échantillon

Scripts : `echantillon.py` (tirage), `mo.py` (lecture des fiches), `ch.py` (recherche dans catalogues et long-lists), `compare_ll.py` (périodes des fiches contre la long-list), `autres_dims.py` (séries partagées entre dimensions), `ventilations.py` (ventilations par origine dans toutes les long-lists).

| Règle | Nombre | Fiches |
|---|---|---|
| `recommandation: ecarter` | 7 | autonomisation_politique_femmes, ecart_chomage_fh, effet_redistribution, egalite_libertes_groupes_sociaux, indice_developpement_genre, part_femmes_victimes_violences, revenu_relatif_seniors |
| `incontournable: oui` (hors déjà comptées) | 9 | ecart_emploi_fh, ecart_salaire_eqtp_fh, ecart_salaire_fh, gini_niveau_de_vie, indice_inegalite_genre, part_niveau_de_vie_40_modestes, rapport_d9_d1_niveau_de_vie, rapport_s80_s20, ratio_palma |
| `eligibilite_longlist: a_verifier` (journal M05 §3) | 4 | dispersion_scores_pisa, gini_patrimoine, inegalite_satisfaction_vie, part_patrimoine_10_pourcent_riches |
| `raccordement: a_etudier` (hors déjà comptées) | 3 | ecart_temps_partiel_fh, femmes_cadres_dirigeants, femmes_parlement |
| Série « non vérifiée » au journal M05 §2.5 (BDM 010760765) | 1 | femmes_direction_fonction_publique |
| Écarts construits (`formule`), hors déjà comptées | 10 | ecart_besoins_soins_revenu, ecart_chomage_diplome, ecart_chomage_immigres, ecart_neet_immigres, ecart_pauvrete_etrangers, ecart_pauvrete_fh, ecart_pauvrete_jeunes_seniors, ecart_reussite_bac_origine_sociale, ecart_sante_percue_revenu, ecart_sorties_precoces_immigres |
| 20 % des 16 autres, tirage | 4 | ecart_emploi_handicap, inegalite_esperance_vie, part_revenu_1_pourcent_riches, disparites_regionales_chomage |

Tirage : `random.Random(20261014).sample(sorted(autres), 4)` (Python 3), `autres` = les 16 fiches non retenues d'office ; 20 % de 16 = 3,2, arrondi au supérieur comme dans les deux audits précédents. **Graine 20261014.** Total : **38 fiches sur 50**.

« 15 écarts construits » : chiffre du message du commit `456bfb2`. Les fiches en comptent **12** avec `formule` (le journal M05 §6 le rectifie). Les 3 autres fichiers qui mentionnent des « composantes » sont `ecart_emploi_fh` (écart publié par Eurostat, composantes en variantes), `ratio_palma` (Palma EU-SILC recalculé dans la note) et `indice_inegalite_genre` (composite) : tous trois sont dans l'échantillon au titre des incontournables.

## 2. Vérifications à la source (WebFetch, 14/10/2026)

API Eurostat (`…/statistics/1.0/data/<jeu>?…&lang=fr`), une modalité par appel (l'outil ne restitue qu'une modalité quand plusieurs sont demandées) :

| Jeu, modalités | Usage | Résultat |
|---|---|---|
| `ilc_di11i` | effet_redistribution | 2010-2019 : 3,4 à 4,0 ; 2020-2025 : 5,5 à 6,7 ; `b` 2020, 2022 |
| `une_rt_a` F et M, 15-74 ans | ecart_chomage_fh | F−H : +1,5 (2003), −0,1 (2012), +0,1 (2018), −0,2 (2025) ; `d` 2021-2025 |
| `ilc_pnp2` R_MED_I 65+ | revenu_relatif_seniors | 0,90 (2000), 1,01 (2011), 1,04 (2015, 2018), 0,97 (2025) ; `b` 2004, 2008, 2020, 2022 ; série depuis 1995, pas de 2002-2003 |
| `sdg_05_30` (4 modalités) | ecart_emploi_fh, ecart_temps_partiel_fh | EMP 8,0 (2009), 6,0 (2019), 5,7 (2025) ; EMP_PT −25,2 (2009), −17,5 (2025) ; `d` 2021-2025 |
| `lfsa_eppga` F et M, 20-64 ans | définition de l'écart de temps partiel | part du temps partiel dans l'emploi : F 29,7 / H 5,6 (2009) ; F 25,6 / H 8,1 (2025) → H−F = −17,5 en 2025, égal à `sdg_05_30` EMP_PT |
| `sdg_05_20` B-S_X_O | ecart_salaire_fh | 15,4 (2006), 16,0 (2019), 11,8 (2024) ; `p` 2023-2024 |
| `sdg_05_50` PARL_NAT | femmes_parlement | 11,6 (2003, `d`), 26,2 (2016), 36,3 (2017), 37,2 (2025) |
| `ilc_li02` F, M (tous âges) | ecart_pauvrete_fh | F−H : 1,0 (2000-2002, valeurs PCM arrondies à l'unité), 1,5 (2004), −0,2 (2018), 2,0 (2025) ; `b` 2001, 2004, 2020, 2022 |
| `ilc_li02` 18-24 ans, 65+ | ecart_pauvrete_jeunes_seniors | écart 5,2 (2004), 14,9 (2010, maximum), 9,9 (2015), 9,5 (2024), 11,2 (2025) ; 18-24 ans depuis 2004 ; `b` 2004, 2020, 2022 |
| `ilc_li31` FOR, NAT 18+ | ecart_pauvrete_etrangers | 32,8/11,8 (2004) ; 37,8 (2013, 2019) ; 39,7 (2020) ; 34,0/12,8 (2025) ; `b` 2008, 2020, 2022 |
| `lfsa_urgacob` NEU27_2020_FOR, NAT | ecart_chomage_immigres | 19,7/9,4 (2000) ; 13,1/7,0 (2025) ; `b` 2003, 2005, 2006, 2014, `bd` 2021, 2024 |
| `edat_lfse_28` NEU27_2020_FOR, NAT | ecart_neet_immigres | nés hors UE : **aucune valeur en 2004-2005**, 29,8 (2006) … 25,3 (2025) ; nés en France 13,4 (2006), 12,2 (2025) ; `b` 2014, `bd` 2021, 2024 ; aucun `u` |
| `edat_lfse_02` NEU27_2020_FOR, NAT | ecart_sorties_precoces_immigres | 21,4 (2006), 12,7 (2025) ; nés en France 12,0 (2006), 6,7 (2025) ; `b` 2013, 2014, `bd` 2021, 2024 ; aucun `u` |
| `hlth_silc_08` QU1, QU5 (coût, distance, attente) | ecart_besoins_soins_revenu | QU1 4,5 (2008), 6,7 (2014), 3,1 (2015), 5,8 (2025) ; QU5 0,2 (2008), 0,8 (2014), 0,3 (2015), 2,1 (2025) ; `b` 2020, 2022 |
| `hlth_silc_10` QU1, QU5 (bonne ou très bonne) | ecart_sante_percue_revenu | 59,2/75,7 (2005) ; 54,2/75,5 (2025) ; `b` 2020, 2022 |
| `lfsa_urgaed` ED0-2, ED5-8 | ecart_chomage_diplome | écart 9,8 (2000), 6,8 (2008), 12,3 (2016), 9,4 (2025) ; `b` 2003, 2005, 2006, 2013, 2014, `bd` 2021, 2024, `d` 2022-2025 |
| `hlth_dlm200` SM_SEV | ecart_emploi_handicap | 20,4 (2014) … 15,7 (2018) … 24,1 (2021) … 21,6 (2025) ; `b` 2020, 2022 ; le jeu n'a pas de dimension d'âge |
| `lfst_r_lmdur` DISP_NUTS2 | disparites_regionales_chomage | 1999-2025, aucun drapeau ; 28,5 (2000) puis 42,7 (2001) |
| `lfst_r_lmder` DISP_NUTS2 | famille disparites_regionales | 15-64 ans : 6,9 (2000), 8,4 (2001), 5,1 (2025) ; aucun drapeau |
| `ilc_di01` D10, QU1, QU2 | ratio_palma | D10 23,9 / 24,6 ; QU1 8,9 / 8,2 ; QU2 14,0 / 13,4 (2018 / 2025) → Palma 1,04 et 1,14 ; unité « Euro » |
| `ilc_di12`, `ilc_di11` | gini_niveau_de_vie, rapport_s80_s20 | Gini 29,2 (2014), 30,4 (2025) ; S80/S20 EU-SILC `b` 2004, 2008, 2020, 2022 |
| `sdg_08_30a` NAT, NEU27_2020_FOR, 20-64 ans | **oubli** | 68,5/45,5 (2000) ; 71,3/46,8 (2016) ; 76,8/57,5 (2025) ; aucun `u` |
| `sdg_05_61` NEXEC_EXEC | **oubli** | 21,4 (2012), 40,0 (2016), 47,1 (2024), 46,5 (2025) ; aucun drapeau |
| `lfsa_eoqgac` NEU27_2020_FOR, NAT, 15 ans ou plus | **oubli** | 19,3/17,8 (2000) ; 33,9/21,0 (2015) ; 30,5/19,3 (2025) |

Autres lectures :
- BDM `010594728` : « Proportion des femmes cadres dirigeants - Cadres dirigeants dans le privé », FE, 21,5 (2010) … 30,1 (2023), 2024-2025 NaN.
- BDM `010594734` et `010760765` : **refusées à l'outil** (robots.txt), deux essais à 10 s d'intervalle ; titres, zones et périodes lus dans `catalogues/insee_bdm_catalogue.csv`.
- API OCDE : le flux `DSD_HSL@DF_HSL_CWB_INEQ` existe (« Bien-être actuel (inégalité verticale) ») mais porte l'annotation `NonProductionDataflow` ; les séries `_VER` sont aussi dans l'extrait du robot `ocde__hsl_bien_etre_actuel.csv` (flux `DF_HSL_CWB`).
- OWID `incomes-of-the-richest` (France) : 11,33 (2000), 9,55 (2013), 12,1 (2022).
- Refusés ou non lus : `api.insee.fr/melodi` (non tenté, refusé à M05 et aux audits précédents) ; `data.education.gouv.fr` (robots.txt) ; métadonnées Eurostat `hlth_dlm_esms` (erreur) ; page de données `hlth_dlm200` (vide) ; **`sdg_05_61` modalité NEXEC : limite de débit (HTTP 429), page non relue**.

Extraits du robot (dépôt) : `pnud__hdr25_series_composites_france.csv` (GII 0,034, rang 11 ; GDI 0,993, 11 valeurs distinctes sur 34 ; coefficient 8,97 ; `ineq_le` 3,71, 2010-2023, 14 points) ; `owid__*` (V-Dem : autonomisation 1851 puis 1900-2025, 52 valeurs distinctes, 0,929 ; égalité des libertés 1789-2025, 14 valeurs distinctes, 1,042 ; WID 1910, 1915-2022 ; Palma WID 2,64) ; `ocde__hsl_inegalites_verticales.csv` (11_1_VER 2,08 en 2024, 6 périodes ; 6_2_VER 1,68 ; 1_3_VER 49,9 en 2020) ; `depp__fr-en-reussite-au-baccalaureat-origine-sociale.csv` (97,1 / 87,5 en 2025 ; par série : général 98,3/93,1, technologique 95/87,9, professionnel 90,4/82,2) ; DREES distributions et dictionnaires (CS09, CS16_1 à CS16_5, IN01, IN02).

Métadonnées Melodi (`docs/sources/echantillons_insee/melodi_catalog_all_2026-10-13.json.gz`) : `DS_ERFS_RETROPOLE` (S80S20_SL = 4,62 en 2024, note de lecture ; mesures `_BR` = avant redistribution ; champ des ménages ordinaires à revenu positif ou nul dont la personne de référence n'est pas étudiante ; « pas de rupture de série ») ; `DS_DERA_PRIVE_SERIES_LONGUES` (France depuis 2000, métropole avant).

## 3. Complétude et cohérence (dépôt)

- Long-list `egalites` : les 330 lignes sont affectées ; écarts en bloc (27) et renvois (88) relus, motifs acceptés.
- Recherche dans toutes les long-lists des ventilations par origine (`c_birth`, `citizen`) : 143 couples (dimension, jeu) ; utilisés par `egalites` : 12 (`edat_lfse_01`, `edat_lfse_02`, `edat_lfse_23`, `edat_lfse_28`, `ilc_li31` à `ilc_li34`, `lfsa_ergacob`, `lfsa_ergan`, `lfsa_urgacob`, `lfsa_urgan`). Découverte de `sdg_08_30a` (taux d'emploi 20-64 ans par nationalité, long-list `travail`, éligible), contraire à l'affirmation du journal M05 §2.3 et de la ligne de maintenance n° 16.
- Recherche « femmes » hors long-list `egalites` : `sdg_05_61` (conseils des grandes sociétés cotées) dans la long-list `education` (lignes `estat-002069`, `estat-002070`, éligibles), contraire à la ligne de maintenance n° 19.
- DREES : CS16_1 à CS16_5 déjà calculées par le robot (7 vagues 2015-2025).
- Jeux Eurostat de mobilité intergénérationnelle `ilc_igtp01`, `ilc_igtp03` : 2019 et 2023, hors filtre au catalogue des jeux.
- Présélections des autres dimensions : `democratie` envoie `sdg_05_50` à `egalites` (règle 900), cohérent ; `securite` écarte les atteintes racistes et anti-LGBT enregistrées (règle 1160, « rattachement à egalites à examiner ») ; aucune ligne `autre_dimension:egalites` en `liens_bien_etre`. Aucun identifiant ni aucune série (principale, composante, variante) commun entre `egalites` et les trois autres dimensions fichées.
- R3 : aucune série principale n'est un niveau ou un taux de pauvreté ; huit séries de niveau par sexe (INSEE, long-list `travail`) et quatre de niveau par nationalité (`ilc_li32` à `ilc_li34`) sont en `variante_de` d'écarts.

## 4. Résultat

38 fiches auditées : **27 conformes**, **10 à corriger**, **1 non vérifiable**. Avis : `corrections_necessaires`. Détail et corrections ordonnées : `docs/validation/audit_egalites.md`.
