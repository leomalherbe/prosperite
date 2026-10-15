# Journal — M05, fiches indicateurs de la dimension `logement_cadre_vie`

Mission M05 (fiche `docs/missions/M05_fiches_indicateurs.md`), méthode commune `docs/methodo/33_methode_fiches_M05.md` v1.2 (D31 à D36), branche `m05-logement_cadre_vie`. Commencée le 14/10/2026 par un premier agent, interrompue, reprise et terminée le 15/10/2026 par un second agent (ce journal) ; PR #26.

## 0. Reprise

- **État trouvé** (commit `c451041` du 14/10/2026) : règles de présélection (134 groupes), présélection, 38 fiches (28 familles), variantes injectées, tableau de validation ; vérificateur à 0 erreur. **Ni journal, ni compte rendu, ni signalements de maintenance n'avaient été commités** ; les fiches citaient pourtant des lignes « LOG-2 », « LOG-3 » et « LOG-4 ». Ce journal reconstitue la méthode à partir des règles et des fiches, puis consigne la reprise.
- **Mise en route** : `git checkout -B m05-logement_cadre_vie origin/m05-logement_cadre_vie`, fusion de `origin/main` sans conflit (`f8dd61e` : corrections securite et egalites, classeurs Excel du gel 2) ; `pytest` : 398 réussis ; `verifier_fiches.py --dimension logement_cadre_vie` : 0 erreur, 0 avertissement.
- **Sous-dossier de travail** : `tmp/m05_logement_cadre_vie/` (ignoré par git, D36) ; scripts de modification des fiches (`maj_fiches.py`, `nouvelles_fiches.py`, `variantes_manuelles.py`, `assainissement.py`, `prix.py`), tous écrits avec `preselection.texte_yaml`.

## 1. Méthode

### 1.1 Lecture de la long-list (1 527 lignes : 1 255 éligibles, 53 à vérifier, 219 non éligibles)

Lecture par jeu et par mesure (pas ligne à ligne), en partant des concepts du contenu de la dimension (`indicateurs/dimensions.yaml`) : coût et qualité du logement, surpeuplement, sans-abrisme, précarité énergétique, environnement local subi (air, bruit, eau du robinet, espaces verts), accès aux services, transports collectifs, infrastructures et numérique. Exclusions appliquées : aléas climatiques → `planete` (A14) ; compétences numériques → `education` (A7) ; consommation et mix énergétiques → `planete`.

Sources de la long-list : Eurostat (858 lignes, dont l'essentiel d'EU-SILC `ilc_*`, des enquêtes TIC `isoc_*`, des transports `tran_*`), INSEE Melodi (523, enquêtes TIC et ODD), INSEE BDM (121 : parc, construction, loyers, logement social, ODD), M04 (25 : SDES qualité de l'air, ITDD, OCDE, Banque mondiale).

### 1.2 Règles (142 groupes au final, ordre croissant, première règle applicable)

| Thème | Groupes `fiche` | Principales décisions d'écart en bloc |
|---|---|---|
| Coût du logement | `surcharge_couts_logement`, `taux_effort_logement`, `poids_logement_revenu`, `charge_logement_lourde`, `prix_logements_revenu`, `hausse_loyers`, `logements_sociaux`, `logements_commences` | croisements seuil × ventilation de `ilc_lvho28` à `30` (44 lignes) et nationalité × âge × sexe (32) : second rang (D35) ; classes de taux d'effort `hlth_dhc050` ; montants (`ilc_mded03`, loyer moyen du parc social) ; séries techniques des indices de prix (pondérations, ventes) ; construction par type et surfaces (42) |
| Structure du parc | `proprietaires_occupants` (reprise) | parc BDM et Melodi (nombre de logements, vacants, résidences secondaires, autres statuts d'occupation) et distributions `ilc_lvho01`, `ilc_lvho02` : grandeurs de contexte sans sens normatif |
| Surpeuplement et qualité | `surpeuplement`, `pieces_par_personne`, `sous_occupation`, `logement_humide`, `sans_installations_sanitaires`, `logement_trop_sombre`, `privation_severe_logement`, `logement_inadequat_onu` | distribution de la privation liée au logement par nombre d'items (33 lignes de `niveau_de_vie`) |
| Précarité énergétique | `incapacite_chauffer` | degrés-jours de chauffage (variable climatique) ; degrés-jours de refroidissement → `planete` |
| Qualité de l'air | `exposition_pm25`, `exposition_pm25_modelisee`, `population_exposee_pm25`, `concentration_pm10`, `depassement_norme_pm10`, `concentration_no2`, `depassement_norme_no2`, `depassement_norme_ozone`, `concentration_ozone` | — |
| Nuisances | `pollution_quartier` (lignes de `planete`), `nuisances_sonores` | — |
| Eau et assainissement | `conformite_eau_microbiologique`, `conformite_eau_physicochimique`, `conformite_assainissement_collectif` et `raccordement_traitement_eaux_usees` (reprise, §2.9) | — |
| Transports et services | `part_modale_transports_collectifs`, `bancarisation` (ligne de `niveau_de_vie`), `duree_trajet_domicile_travail` (reprise, hors long-list) | volume de transport par autobus ; fret, véhicules électriques → `planete` |
| Numérique | `acces_internet_domicile`, `haut_debit_domicile`, `privation_internet`, `usage_internet`, `administration_en_ligne`, `couverture_fibre` | croisements de deux ventilations des enquêtes TIC (230 lignes) ; usages en ligne particuliers sans sens normatif (225) ; technologies de connexion arrêtées (12) ; couverture par technologie de second rang (13) ; trafic et prix (3) ; détail des démarches administratives en ligne (33 lignes de `democratie`) |
| Autres | `preoccupation_logement`, `connaissance_personne_sdf` (reprise, hors long-list) | satisfaction du logement, du cadre de vie et des espaces verts (module EU-SILC 2013 seul, 40 + 40 lignes) ; espaces verts OCDE 9_1 (2 points, 2012 et 2018) ; comptes nationaux du logement (70 : investissement et patrimoine, A5) ; dépenses publiques (8 : moyens) ; population par degré d'urbanisation (16 : contexte) |

### 1.3 Lignes reçues d'autres dimensions (`autre_dimension:logement_cadre_vie`) et importées

Contrôle de la reprise : toutes les lignes que les présélections déjà faites renvoient à `logement_cadre_vie` sont reprises (134 sur 134) : `democratie` 38 (administration en ligne, D33 : 5 variantes, 33 écartées en bloc), `liens_bien_etre` 40 (satisfaction du lieu de résidence et du temps de trajet, module 2013 : écartées, non éligibles), `niveau_de_vie` 45 (coût et privation liés au logement, bancarisation), `planete` 11 (pollution du quartier, assainissement). Importées en plus : 2 lignes de `education` (IPCH des loyers, rattachement par défaut erroné) et 1 de `sante` (ODD 7 de l'INSEE, incapacité à chauffer). Total : 137 lignes importées (6 `fiche`, 25 `variante_de`, 106 `ecarte_en_bloc`).

Lignes envoyées ailleurs (146) : `education` 93 (niveau d'éducation par degré d'urbanisation), `planete` 23 (degrés-jours de refroidissement, fret, véhicules de transport collectif électriques, températures extrêmes OCDE 9_3), `sante` 20 (santé perçue par degré d'urbanisation), `travail` 7, `niveau_de_vie` 2 (pauvreté après coûts du logement `ilc_li48`), `egalites` 1 (OCDE 10.3.1, bon endroit où vivre pour les minorités).

### 1.4 Recherche hors long-list (D32, D36)

Mots-clés du contenu cherchés dans toutes les long-lists, dans `catalogues/*_non.csv.gz`, dans le catalogue des jeux Eurostat et dans les sorties du robot M04 (`docs/sources/series/` : baromètre DREES, OCDE How's Life et ODD, SDES qualité de l'air et ITDD).

| Trouvé | Décision |
|---|---|
| DREES OG04_1, préoccupation pour le logement (2014-2025, distributions déjà calculées) | fiche `preoccupation_logement` |
| DREES SDPROXIM_3, connaître quelqu'un de SDF (2000-2025, distribution non calculée) | fiche `connaissance_personne_sdf` (`statut_serie: a_calculer`) |
| ITDD `med_dist_min_hp`, `med_dist_km` (navettes domicile-travail, 2011, 2016, 2022) | fiche `duree_trajet_domicile_travail` + 3 variantes |
| ITDD `part_depl_dom_trav`, `taux_lgmt_suroccupes`, `log_hlm_phab`, `part_pls`, `locaux_raccor`, `couv4g` ; OCDE ODD 11.1.1 bidonvilles | variantes hors long-list (preuve du robot) |
| INSEE BDM 011815635 (IPC des loyers base 2025), 010567058 (prix des logements anciens) au catalogue des séries écartées | variantes de `hausse_loyers` et `prix_logements_revenu` |
| DREES LO11 (conditions de logement jugées satisfaisantes, 2024-2025), LO10 (nombre de pièces, 5 vagues 2020-2025), LO01 et LO02 (statut d'occupation, prêt) ; HA04 (évolution de l'accessibilité du quartier aux personnes handicapées, 6 vagues, opinion d'évolution) | non retenus (non éligibles ou structure) ; HA04 relève plutôt d'`egalites` (handicap), signalé ici seulement |
| DREES SA09 (médecins à proximité), long-list `sante` m04-000270 ; Eurostat `sdg_11_52` (décès prématurés dus aux PM2,5, long-list `sante`) | laissés à `sante` (accès aux soins ; mortalité) |

Recherches sans résultat (aucune série nationale à URL stable au catalogue ni trouvée) : nombre de personnes sans domicile et hébergement d'urgence (enquête Sans-domicile de l'INSEE ponctuelle, 2001 et 2012 d'après M03) ; précarité énergétique ONPE et Médiateur national de l'énergie (synthèses PDF seulement, recherche web du 15/10/2026) ; expulsions locatives (PDF seulement) ; demandes de logement social (SNE) ; parc par étiquette DPE (SDES-ONRE) ; accessibilité des services et des transports publics (ODD 11.2.1 : une seule année, 2020 ; modules EU-SILC ponctuels) ; satisfaction du logement (EU-SILC 2013 seulement ; aucune mesure `LOGSATISF` dans `DS_SRCV_SATISFACTION`, qui ne porte que la vie, le travail et les relations). Signalements : LOG-11.

## 2. Choix structurants

1. **EU-SILC d'Eurostat en série principale** quand l'INSEE ne publie pas le niveau par API (D35) : surcharge des coûts, taux d'effort, surpeuplement, défauts du logement, incapacité à chauffer, nuisances. Les séries INSEE (ODD, SRCV, recensement) sont en variantes.
2. **Coût du logement** : une famille `surcharge_couts_logement` (principale : taux de surcharge, 40 % du revenu ; variantes-fiches : taux d'effort médian, poids du logement dans le revenu des comptes nationaux) ; familles propres pour la charge ressentie, les prix d'achat rapportés au revenu, la hausse des loyers, le logement social.
3. **Qualité de l'air** : une famille par polluant (PM2,5, PM10, NO2, ozone), la concentration et le dépassement de norme d'un même polluant étant substituables ; principale PM2,5 = indicateur réglementaire d'exposition du SDES (objectifs 2020, 2025, 2030), la série modélisée de la Banque mondiale couvrant 2000-2010 en `retenir_variante`.
4. **Module triennal d'EU-SILC** (reprise) : les défauts du logement, l'environnement du logement et la charge ressentie du coût du logement n'ont plus de valeur annuelle depuis 2021 (valeurs 2004-2020, puis 2023 ; module « conditions de travail et de logement », vagues 2023 et 2026, page des modules d'Eurostat lue le 15/10/2026). Sept fiches passent en `frequence: irreguliere` (D17) avec le drapeau `module_triennal_depuis_2021` : `logement_humide`, `logement_trop_sombre`, `sans_installations_sanitaires`, `privation_severe_logement`, `nuisances_sonores`, `pollution_quartier`, `charge_logement_lourde`. Les fiches annuelles (surpeuplement, surcharge, taux d'effort, pièces par personne, incapacité à chauffer, privation d'internet) gardent `annuelle`.
5. **Sens ambigu → `ecarter`** : `sous_occupation`, `logements_commences` (offre mais aussi artificialisation), `proprietaires_occupants` (reprise : concept public, structure du parc), `raccordement_traitement_eaux_usees` (reprise : la population non raccordée relève surtout de l'assainissement non collectif). Sont gardés en `sens` signalé à confirmer : `prix_logements_revenu` (bas = accessibilité), `administration_en_ligne` (haut, mais une hausse peut traduire la fermeture des guichets), `connaissance_personne_sdf` (bas, indicateur indirect).
6. **Indicateurs de moyens** (D19, `type: moyen`) : `logements_sociaux`, `couverture_fibre`, `logements_commences`.
7. **`declaratif`** (méthode §4) : `oui` pour la charge ressentie, le logement jugé trop sombre, le bruit et la pollution ressentis, la préoccupation pour le logement (5 fiches) ; `non` pour les capacités financières déclarées (chauffer, internet) et les faits déclarés (connaître une personne SDF).
8. **Hors long-list** (reprise) : trois fiches (§1.4), sur le modèle des fiches DREES de `travail` et `niveau_de_vie` (`geo: FM`, pièce jointe `barometre2000_2025_diff_csv`, non-réponses au dénominateur).
9. **Assainissement** (reprise) : la première version renvoyait à `planete` les lignes d'assainissement (conformité des ouvrages collectifs et non collectifs, raccordement à un traitement secondaire), tandis que `planete` (fusionné, PR #17, maintenance PLA-6) les renvoyait ici : sans fiche, le concept disparaissait des deux tableaux. Deux fiches sont créées ici dans une même famille, avec `rattachement_propose` vers `planete` (R2 : pression sur les milieux aquatiques) : la session mère tranche.
10. **Incontournables** (crosswalk §5) : « surpeuplement et qualité du logement » (SSF, OCDE, Eurostat, + Doughnut) et « pollution de l'air locale » (SSF, OCDE, Eurostat). 16 fiches portent `incontournable: oui` ; la reprise ajoute `pollution_quartier`, indicateur phare de la sous-dimension 8.1 « Pollution » d'Eurostat. Chaque concept a au moins une fiche `retenir` (`surpeuplement`, `logement_humide`, `sans_installations_sanitaires`, `privation_severe_logement` ; `exposition_pm25`, `concentration_pm10`, `concentration_no2`, `depassement_norme_ozone`, `pollution_quartier`).

## 3. Vérifications à la source (15/10/2026)

API Eurostat par l'outil de lecture, une requête toutes les 60 à 100 secondes (le proxy renvoie HTTP 429 au-delà). **Refusées (429), non relues** : `ilc_mdho05`, `ilc_mdho06a`, `ilc_mddw01`, `ilc_mddw02`, `isoc_ci_in_h` ; pour les trois premières, la table ODD de même définition a été lue (`sdg_06_10`, `sdg_11_11`, `sdg_11_20`). Lecture du fichier ITDD (DiDo) : autorisation non accordée à l'outil. Melodi : fermé à l'outil (robots.txt).

| Fiche | Série lue | Constat | Effet |
|---|---|---|---|
| `logement_trop_sombre` | `ilc_mdho04` | 9,0 (2004) … 7,3 (2019), 9,7 (2020, b), 10,6 (2023) ; rien en 2021, 2022, 2024, 2025 | module triennal, valeurs dans la note |
| `charge_logement_lourde` | `ilc_mded04` (HVY) | 20,2 (2004), 29,6 (2013), 23,2 (2019), 26,4 (2020, b), 31,4 (2023) ; rien en 2021-2022 | module triennal ; la poursuite « à vérifier » est levée |
| `sans_installations_sanitaires` | `sdg_06_10` | 0,6 (2004), 0,2 (2019), 0,4 (2020, b), 0,7 (2023) | idem |
| `privation_severe_logement` | `sdg_11_11` | 3,4 (2004), 2,1 (2013), 3,8 (2020, b), 4,6 (2023) | idem |
| `nuisances_sonores` | `sdg_11_20` | 23,5 (2004), 16,2 (2013), 20,7 (2020, b), 21,1 (2023) | idem |
| `taux_effort_logement` | `ilc_lvho08a` | 12,3 (2004), 11,1 (2020, b), 11,4 (2022, b), 12,2 (2025) ; rien en 2021 | ruptures 2020 et 2022 |
| `pieces_par_personne` | `ilc_lvho03` | 1,7 à 1,9 de 2004 à 2025 ; b en 2020 et 2022 | `faible_variabilite` |
| `privation_internet` | `ilc_mddu07a` | 2,7 (2014), 1,4 (2024), 1,6 (2025) ; b en 2020 et 2022 | `faible_niveau` |
| `usage_internet` | `isoc_ci_ifp_iu` | 46,87 (2006), 94,98 (2025), rien en 2020, aucun drapeau | `annee_manquante_2020` |
| `couverture_fibre` | `isoc_cbt` (FTTP) | 10,5 (2013), 91,7 (2025), aucun drapeau | `proche_de_la_saturation` |
| `hausse_loyers` | `prc_hicp_aind` (CP041) | -0,1 (2000), 3,6 (2005), 2,3 (2025) ; **jeu plus mis à jour, remplacé par `prc_hicp_ainr`** (ECOICOP v2) | `raccordement: a_etudier`, variante IPC INSEE base 2025, LOG-6 |
| `part_modale_transports_collectifs` | `tran_hv_psmod` ; BDM 010751584, 010751585 | **valeurs aberrantes 99,1 / 99,2 / 99,1 en 2010-2012** (e en 2010-2011), b en 2013 ; somme INSEE 16,7 / 17,0 / 16,2, écart de -0,1 à +0,7 point avec Eurostat sur 2013-2024 | `raccordement: a_etudier`, LOG-7 |
| `bancarisation` | BDM 010596094 | 97,0 (2011), 96,6 (2014), 94,0 (2017), 99,2 (2021 et 2024) | valeurs dans la note ; source primaire (Global Findex probable) à vérifier |
| `logements_sociaux` | BDM 001779870 | 699 (2012) à 787 (2025) ; ITDD 795,1 en 2025 | écart signalé (LOG-5) |
| `proprietaires_occupants` | BDM 001791247 | 55,7 (2000), 57,7 (2010-2013), 57,3 (2026, provisoire) | — |
| `conformite_assainissement_collectif` | BDM 010595400, 010595405 | 80,0 (2010), 98,6 (2018), 91,9 (2022) ; non collectif 40,8 (2010) → 64,5 (2023), saut 2012-2013 | — |
| `raccordement_traitement_eaux_usees` | `sdg_06_20` | 77,30 à 80,46 %, rien de 2005 à 2009 | `sens: ambigu` |

Fiches non relues à la source (valeurs tirées des extraits du robot ou non citées) : `acces_internet_domicile` (429), `pollution_quartier` (429), `administration_en_ligne`, `haut_debit_domicile`, `poids_logement_revenu` (Melodi), fiches SDES et OCDE (extraits du robot déjà cités par le premier agent).

## 4. Contrôles

- `python scripts/preselection.py --dimension logement_cadre_vie --maj-fiches` : 1 664 lignes affectées (1 527 de la long-list, 0 sans règle, + 137 importées), 142 groupes (44 `fiche`, 61 `variante_de`, 27 `ecarte_en_bloc`, 10 `autre_dimension`).
- `python scripts/verifier_fiches.py --dimension logement_cadre_vie --tableau` : **0 erreur**, 3 avertissements attendus (séries principales hors catalogue des trois fiches hors long-list, preuves du robot).
- Compteurs : **44 fiches, 33 familles ; 30 `retenir`, 10 `retenir_variante`, 4 `ecarter`** ; 5 déclaratives ; 0 composite ; 1 « à vérifier » (D17 : `bancarisation`) ; 3 hors long-list ; 16 incontournables ; 497 variantes ; 0 ligne déjà série principale d'une autre dimension.
- `python -m pytest -q` : 398 réussis. Aucun fichier de `scripts/` ni de `src/` modifié.

## 5. Points ouverts

1. **R1 avec les dimensions en cours** (`education`, `sante`, traitées en parallèle) : `hausse_loyers` utilise deux lignes de la long-list `education` (IPCH `prc_hicp_aind` CP041 et CP0411) et `incapacite_chauffer` une ligne de `sante` (melodi-005545, ODD 7.i1) : leurs présélections devraient les marquer `autre_dimension:logement_cadre_vie`.
2. **Assainissement** : rattachement à trancher entre `planete` et `logement_cadre_vie` (§2.9).
3. **Redondances à surveiller au contrôle de redondance** : `privation_severe_logement` et ses composantes (`surpeuplement`, `logement_humide`, `sans_installations_sanitaires`, `logement_trop_sombre`) ; `privation_internet` et la privation matérielle et sociale (`niveau_de_vie`) ; `poids_logement_revenu` et `niveau_de_vie/depenses_pre_engagees` ; `incapacite_chauffer` et `securite/retards_paiement` (dont les factures courantes, `ilc_mdes07`, troisième indicateur européen de précarité énergétique, reste en `securite`).
4. **Valeurs à relire au premier passage du robot** : séries refusées par le proxy (§3) et séries Melodi.
