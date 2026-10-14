# Compte rendu — mission M02 (Eurostat), phases 1 et 2

Agents M02 (phase 1 le 13/10 ; phase 2 les 13 et 14/10, trois sessions successives, décision D13). Branche `m02-eurostat`, PR #2. Journal détaillé : `docs/cr/M02_journal.md`. Fiche source : `docs/sources/eurostat.md` (§10 pour les catalogues).

## 1. Fait

- **A1** — fiche source `docs/sources/eurostat.md` : quatre voies d'accès (TOC, API Statistics JSON-stat, SDMX 2.1, TSV en masse), licence, quotas, structure JSON-stat et SDMX, 19 pièges constatés, dossiers prioritaires dans le TOC, fixtures, catalogues.
- **A2** — `src/sources/eurostat.py` (TOC, structure SDMX, JSON-stat 2.0, erreurs, client avec nouveaux essais) ; `src/pipeline/catalogue_eurostat.py` (logique des deux niveaux et de l'amorce) ; `tests/test_eurostat.py` : **118 tests** passent hors ligne sur des **réponses réelles** enregistrées par le robot.
- **A3/A4/B** — `scripts/collecte_eurostat.py`, script reprenable exécuté par GitHub Actions (six passages) : `catalogues/eurostat_jeux_catalogue.csv` (niveau 1), `catalogues/eurostat_series_catalogue.csv.gz` (niveau 2, séries France vérifiées), `catalogues/eurostat_series_catalogue_non.csv.gz` (séries écartées avec motif, D26), `catalogues/eurostat_dossiers_toc.csv`, `catalogues/eurostat_bilan.json`, `catalogues/eurostat_etat_collecte.json`, journaux `journaux/collecte_*_collecte_eurostat.py.log`.
- **Amorce** — `docs/sources/eurostat_amorce_prototypes.csv` : les **66** séries Eurostat des prototypes statuées par le robot.
- **Clôture (14/10)** — bogue de l'amorce corrigé ; nettoyage du niveau 1 (D26) ; pêche et sylviculture réintégrées ; unités absolues préférées (recalcul ciblé) ; secteurs hors ménages écartés ; contrôle qualité du niveau 2 et corrections ; rafraîchissement automatique (péremption).

Note : le script s'appelle `scripts/collecte_eurostat.py` (convention du dépôt, `CLAUDE.md`) et non `scripts/moissonner_catalogue_eurostat.py` comme l'indiquait la fiche ; le catalogue des séries est compressé (`.csv.gz`).

## 2. Chiffres clés (14/10/2026, règles v5)

| | |
|---|---|
| TOC | 12 234 entrées : 6 649 jeux, 911 tableaux, 1 878 dossiers |
| Retenus par les filtres de dates (fin ≥ 2020, début ≤ 2010) | 3 053 |
| **Jeux candidats** | **1 816** (dont 77 indicateurs ODD typés « table » et 381 par rattrapage) ; niveau 2 : 1 722 avec séries France, 58 sans dimension `geo`, 36 sans donnée France |
| **Séries France vérifiées** | **42 538 séries par défaut, dont 31 375 éligibles** (≥ 10 années depuis 2000, fin ≥ 2020) ; 13 672 lignes de ventilation ; 100 % `geo=FR` |
| Séries éligibles par dimension v0 | planète 15 567 ; niveau de vie 6 054 ; santé 5 308 ; éducation 1 913 ; travail 1 223 ; sécurité et confiance 629 ; logement et cadre de vie 291 ; `contexte` 241 ; égalités 116 ; démocratie 29 ; liens et bien-être 4 |
| Jeux avec au moins une série éligible | travail 331, niveau de vie 248, éducation 228, planète 191, santé 154, logement 101, sécurité 45, égalités 41, `contexte` 38, démocratie 8, liens et bien-être 4 |
| Ventilations (D21) | âge 7 390, sexe 5 156, niveau d'éducation 379, composition et type de ménage 213, degré d'urbanisation 150, type d'individus 130, quintile 111, **nationalité 72, pays de naissance 71** |
| Séries écartées (`_non`) | 20 114, motif `secteur_hors_menages` |
| Amorce (66) | 55 disponibles, 6 séries courtes, 2 codes changés (`sdg_05_61`, `sdg_15_11`), 2 à remplacer (`sdg_13_10`, `env_bio2`), 1 sans donnée France (`sdg_10_20`) |

## 3. Corrections du 14/10 et effets

1. **Bogue de l'amorce** (passages 2 et 3 en échec) : `env_bio3`, remplaçant prévu de `sdg_15_60`, n'a que l'agrégat UE ; la réponse France est un cube vide (dimension `geo` de taille 0) et le rôle des dimensions lisait le premier élément d'une liste vide. Corrigé (cube vide = « aucune valeur pour la France », réponse inattendue = « structure inattendue », sans arrêter l'étape), test de non-régression ; remplaçant corrigé : `env_bio2` (oiseaux des milieux agricoles, 1990–2021). Le niveau 2 n'a pas été relancé en entier.
2. **Bruit au niveau 1** (D26, constats de M05-prep) : 460 jeux d'entreprises et d'échanges extérieurs exclus, dont 155 rangés dans des dossiers prioritaires (numérique, culture, marché du travail) ; plus, après contrôle qualité, tableaux entrées-sorties `naio_*` et commerce de biens culturels. Comptes par secteur : seuls l'ensemble de l'économie et les ménages restent (20 114 séries écartées). Catalogue des séries : 191 707 → 56 210 lignes ; séries éligibles 95 836 → 31 375 (éducation 34 108 → 1 913, niveau de vie 25 792 → 6 054, travail 13 192 → 1 223).
3. **Unités (D26)** : indices relatifs à l'UE et base 100 relégués quand une unité absolue existe ; 16 jeux refaits seuls (`nama_10_pc` passe de `PC_EU27_2020_HAB_MEUR_CP` à `CLV20_EUR_HAB`, `nama_10_gdp` de `PC_EU27_2020_MEUR_CP` à `PC_GDP`, `prc_hicp_aind` de l'indice au taux de variation annuel moyen…) ; aucune série restante ne changerait d'unité ; 180 séries gardent un indice faute d'unité absolue.
4. **Pêche et sylviculture** : 12 jeux réintégrés en `planete` (captures `fish_ca_*` au total des espèces, par grande zone ; stock sur pied `for_vol*` ; prélèvements `for_remov`, `for_owner`), production et prix agricoles toujours exclus ; ex. captures françaises toutes zones 2000–2025.
5. **Contrôle qualité** (20 séries éligibles et 20 écartées par dimension v0) : écartées à juste titre ; erreurs systématiques corrigées (pays partenaires et pays d'origine énumérés, espèces énumérées, faux amis « Tableaux des emplois », « non satisfaits », « sages-femmes ») ; étiquettes des séries resynchronisées sur le niveau 1 ; ventilations conformes à D21 ; ventilations par origine ajoutées (A8). **Population sans étiquette** : 47 jeux `demo_*` étiquetés `contexte` (la table v0→v1 les range hors grille).

## 4. Jeux les plus prometteurs par dimension v0 (codes ; liste non limitative)

- **Niveau de vie** : `sdg_01_10`/`ilc_pecs01` (AROPE), `sdg_01_20`, `ilc_li02` (pauvreté par seuil), `sdg_01_31` (privation matérielle et sociale sévère), `sdg_01_41`, `ilc_di03` (revenu médian et moyen), `sdg_08_10`/`nama_10_pc` (PIB et consommation par habitant en volume), `nasa_10_ki` (revenu disponible et épargne des ménages), `sdg_10_10`, `ilc_mdes*` (difficultés financières).
- **Travail** : `sdg_08_30` (taux d'emploi), `une_rt_a`, `sdg_08_40` (chômage de longue durée), `sdg_08_20` (NEET, étiqueté `education`), `sdg_08_60` (accidents mortels du travail), `hsw_mi01`–`hsw_mi05`, `lfsa_ewpsun`/`lfsa_ehomp` (horaires atypiques, D27), `earn_nt_netft`, `ilc_lvhl32` (transitions par contrat).
- **Logement et cadre de vie** : `ilc_lvho05a` (surpeuplement), `sdg_01_50`/`ilc_lvho07a` (surcharge du coût du logement), `ilc_mdho06*` (privation liée au logement), `sdg_07_60` (impossibilité de chauffer), `sdg_11_20` (bruit), `sdg_09_50`/`tran_hv_psmod` (répartition modale), `sdg_06_10` (assainissement).
- **Santé** : `sdg_03_11`/`demo_mlexpec` (espérance de vie), `sdg_03_12`/`hlth_hlye` (années de vie en bonne santé), `sdg_03_20` (santé perçue), `sdg_03_42`, `hlth_cd_asdr2` (mortalité standardisée par cause, 88 séries), `sdg_03_60` (besoins de soins non satisfaits), `sdg_03_41`, `hlth_dh*`, `hlth_silc_*`.
- **Éducation** : `sdg_04_10` (sorties précoces), `sdg_04_20` (diplômés du supérieur), `sdg_04_60` (formation des adultes), `edat_lfse_03`/`edat_lfse_04`, `sdg_04_31` (petite enfance), `sdg_09_10`/`rd_e_gerdtot` (effort de R-D, A5), `sdg_04_70` (compétences numériques, 2021–2025, série courte).
- **Liens et bien-être** : peu de séries éligibles ; `ilc_pw01`–`ilc_pw09` (satisfaction, bonheur, confiance : 2013, 2018, 2021–2025, D17), `ilc_mdes10*`/`ilc_mdes11*` (moyens de voir ses proches, de loisirs), `ilc_scp01`/`ilc_scp03` (participation sociale : années isolées, D17).
- **Sécurité** : `sdg_16_20` (criminalité, violence ou vandalisme dans le quartier), `sdg_16_10` (homicides, étiqueté `sante`)/`crim_hom_*`, `crim_off_cat`, `sdg_11_40` (étiqueté `sante`)/`tran_sf_roadus` (tués sur la route), `ilc_mdes04`–`08` (arriérés, dépenses imprévues : sécurité économique).
- **Démocratie** : `sdg_16_40` (indépendance perçue de la justice), `sdg_16_50` (corruption perçue), `sdg_05_50` (sièges détenus par des femmes), `sdg_16_30`, `crim_crt_*` ; Eurostat est pauvre ici (sources M04).
- **Égalités** : `sdg_10_41` (S80/S20), `sdg_10_50`, `ilc_di11*`/`ilc_di12` (Gini), `sdg_05_20` (écart de salaire), `sdg_05_30` (écart d'emploi), `ilc_pnp13` (écart de pension), ventilations par sexe, âge, quintile, origine.
- **Planète** : `sdg_13_10`/`env_air_gge` (GES), `sdg_13_21`, `env_ac_ghgfp` (empreinte : sans dimension `geo`, à voir), `sdg_12_21` (empreinte matières), `sdg_07_40` (renouvelables), `sdg_07_10`/`sdg_07_11`, `sdg_11_60`/`env_wasmun`, `sdg_12_41` (circularité), `env_bio2` (oiseaux), `sdg_15_42`, `aei_fm_usefert`/`aei_pr_gnb` (azote, phosphore), `fish_ca_main`, `for_remov`.

## 5. Problèmes et limites

- Étiquetage v0 par mots-clés : orientation, pas classement (ex. homicides `sdg_16_10` en santé) ; les catalogues restent en v0, le passage en v1 est fait par la long-list.
- Liens et bien-être : 4 séries éligibles ; les modules de bien-être d'EU-SILC sont irréguliers (D17).
- À rang égal, une unité monétaire peut passer avant une grandeur physique (`for_area_efa`) ; dimensions sans total reconnu (`nace_r2`, `c_regis`) énumérées.
- **Historique de la branche** : un `git pull --rebase` a aplati la fusion de `main` du 14/10 (les 55 commits de `main` y sont recopiés au lieu d'une fusion). Contenu identique à `main` pour ces fichiers ; voir la proposition 1.

## 6. Propositions (à acter par la session mère)

1. **Fusion de la PR #2** en « squash » (ou fusion après rétablissement d'une vraie fusion de `main` par l'agent, sur demande), pour ne pas dupliquer les commits de `main` dans l'historique.
2. Journal : acter les règles v5 (exclusion des statistiques d'entreprises même dans les dossiers prioritaires ; catalogue des séries écartées `_non` réservé aux exclusions de périmètre, les séries non éligibles au §3.4 restant au catalogue principal à cause de D17 ; étiquette `contexte` pour la population ; ventilations par origine ; péremption 30/90 jours).
3. M05 : appliquer D17 aux séries `ilc_pw*` et `hlth_silc_*` non annuelles ; regrouper par concept les jeux volumineux (bilans énergétiques, causes de décès, pesticides).
4. M04 : indice national de tous les oiseaux communs (Vigie-Nature / ONB), absent d'Eurostat.

## 7. Questions pour la session mère

1. Garder les R-D (`rd_e_*`, `rd_p_*`) étiquetés `education` en v0 (cohérent avec A5) ?
2. Faut-il aussi restreindre les comptes des administrations publiques (`gov_10a_*`, dette et dépenses, hors v1 selon A5) au niveau 2, ou laisser la table v0→v1 les ranger hors v1 ?
3. Les jeux régionaux NUTS 2/3 (`demo_r_*`, `hlth_cd_y*`) donnent la valeur nationale avec `geo=FR` : les garder (doublons des jeux nationaux) ou les exclure ?
