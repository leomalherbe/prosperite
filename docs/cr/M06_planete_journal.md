# Journal de bord — M06, audit croisé de la dimension `planete`

Agent auditeur M06, 15 octobre 2026, branche `m06-planete` (worktree isolé). L'agent n'a pas participé à M05 `planete`. Rapport : `docs/validation/audit_planete.md`.

## 0. Mise en route

- `git fetch origin && git checkout -B m06-planete origin/main` : base `792f1a5` (après la fusion des fiches `planete` par la PR #17, la méthode v1.2 et les décisions D34-D36, les corrections `securite` et `egalites`).
- Lus : `CLAUDE.md` ; charte §3.1 à §3.6, §4, §5.1 ; journal des décisions D01-D36 (en particulier D15-D19, D24, D25, D28, D32, D34-D36) ; fiche M06 ; `docs/methodo/33_methode_fiches_M05.md` v1.2 ; `indicateurs/dimensions.yaml` (définition, contenu, exclusions de `planete`, R1-R8, type plafond) ; audits M06 `securite`, `liens_bien_etre`, `egalites`, `democratie` (format, exigence) ; compte rendu et journal M05 `planete` ; `docs/cr/maintenance_catalogues_planete.md` (PLA-1 à PLA-8) ; `30_crosswalk_synthese.md` (§5, §8) ; `30_cadres_reference_extraction.md` (§1.4 à §1.7 : les 13 limites du Doughnut et les limites par habitant 2017) ; lignes `planete` de `30_indicateurs_cadres_reference.csv`.
- Matériau audité : 75 fiches `indicateurs/planete/*.yaml`, `validation_planete.csv`, `preselection_planete.csv` (221 groupes), `preselection_planete_lignes.csv` (21 534 lignes), `regles_preselection_planete.csv`, long-list `planete` (21 533 lignes), catalogues INSEE et Eurostat (dont `*_non.csv.gz`), sorties du robot M04 (`docs/sources/series/`).
- Contrôles de départ : `python -m pytest -q` → 398 réussis ; `python scripts/verifier_fiches.py --dimension planete` → 0 erreur, 2 avertissements attendus (`intensite_exploitation_forets`, `preoccupation_environnement` hors catalogue) ; 75 fiches, **65 familles** (et non 64 : le commit `dfba460` en comptait 64 pour 74 fiches avant l'ajout des deux fiches hors long-list), 61 `retenir`, 9 `retenir_variante`, 5 `ecarter`, 1 déclarative, 2 composites, 3 « à vérifier », 2 hors long-list, 7 incontournables, 697 variantes, 0 ligne prise par une autre dimension. `git status` propre ensuite (sous-dossier de travail `tmp/m06_planete/`, ignoré par git).

## 1. Échantillon

- D'office : 5 `ecarter` ; 7 incontournables ; « à vérifier » au sens du journal M05 : éligibilité `a_verifier` (3), éligibilité `non` retenue selon D28 (3), hors long-list (2, dont 1 déjà comptée), raccordement `a_etudier` (5), rattachement proposé (1), drapeaux Eurostat non lus (6) ; composites (2). Soit 33 fiches.
- « Autres » fiches : 42 ; 20 % = 8,4, arrondi à 9 comme dans les audits précédents ; `random.Random(20261014).sample(sorted(pool), 9)` → `prelevements_eau`, `emissions_dioxines`, `eaux_baignade_excellentes`, `part_vehicules_electriques_neufs`, `puits_carbone_utcatf`, `pesticides_rivieres`, `indice_exploitation_eau`, `indice_liste_rouge`, `flux_phosphore_mer`.
- Total : **42 fiches**. Contrôle transversal (type, sens, famille, unité, zone) des 33 autres, sans lecture à la source sauf `consommation_energie_finale` et `consommation_energie_primaire` (API `nrg_ind_eff` : 2005-2024, exact).

## 2. Vérifications à la source (WebFetch, 15/10/2026)

| Source | Lu | Constat |
|---|---|---|
| BDM 010596008, 010595981, 010595988, 010595993, 010600316 | séries complètes | émissions 551 Mt (2000), 369 (2024, E) ; empreinte 692 / 563 Mt (E) ; 11,4 / 8,2 t par habitant (E) ; zone `FM_D99_D978` : exact |
| BDM 010596134, 010596146, 010776375 à 010776378, 010596289 | séries complètes | artificialisation 7,4 % (2000) → 9,5 % (2023) ; **010776377 « Proportion … » contient des hectares (21 950 459 en 2000) et 010776378 « Surface … milliers d'hectares » des pourcentages entiers (40)** ; même inversion pour les terres agricoles ; 010596146 (« milliers d'hectares ») est en hectares ; boisement 29,9 → 32,0 % |
| BDM 010596532, 010596301 à 010596304, 010594440, 010594442, 010594444 | séries complètes | espèces exotiques 37,5 (2014), 54,3 (2024) ; habitats favorables 22, 20, 16 (2024 provisoire) ; races à risque 38 (2010) → 122 (2025) avec **0 en 2012 et 2013** |
| BDM 010596198, 010595385, 010595386, 010595394, 010596708, 010595980, 010596782, 010775965 | séries complètes | gaspillage 150 (2015), 129-142 (2020-2023) ; masses d'eau 2013, 2015, 2019, 2021 ; oiseaux 84 → 63 ; PPR 8 959 → 12 493 ; flux de phosphore 2010-2021 ; voitures électriques 0,5 → 16,8 % |
| BDM 010596774, 010596783 à 010596785, 010761992, 010594432, 010595977, 010751587 | séries complètes | façades Manche et Atlantique jusqu'en 2023 ; protection forte 5,15 → 6,43 % ; NODU 2010-2021 (2021 provisoire) |
| Métadonnées INSEE ODD 12.i3 (PDF) | — | **les valeurs depuis 2020 « ne sont pas comparables » à celle de 2015 (ADEME)** ; champ des décisions UE 2019/1597 et 2019/2000 |
| API Eurostat `sdg_13_10`, `env_air_gge` CRF4, `sdg_12_31`, `sdg_15_50`, `sdg_13_31`, `env_ac_mfa`, `aei_pr_gnb`, `env_wat_abs`, `sdg_06_60`, `sdg_06_70`, `sdg_14_40`, `nrg_ind_eff`, `for_remov`, `fish_ca_main` | séries complètes | valeurs citées par les fiches exactes |
| API Eurostat `sdg_06_40`, `sdg_14_60`, `sdg_12_41` (non lues par M05) | séries complètes | nitrates 17,85 → 17,49 mg/l, série lissée sans drapeau ; eutrophisation annuelle de 0,00 à 6,52 %, ZEE de ≈ 348 500 km² (métropole) ; circularité 2024 imputée (`i`) |
| API Eurostat `env_air_emis` (`NFR_TOT_NAT_C`, 16 polluants ; COVNM 1990-2024) | séries | aucun drapeau ; **COVNM : creux isolé en 2005 (1 339 890 t contre 1 827 710 en 2004) et chute de 40 % en 2020 (706 010 t contre 1 171 700 en 2019)** |
| API Eurostat `for_vol_efa` (`THS_M3`, `FAWS`) | 2000-2023 | accroissement net 2012-2023 (rupture `b` 2018) ; prélèvements / accroissement : 0,458 (2012) → 0,677 (2023) |
| Directive (UE) 2016/2284, article 2 (legislation.gov.uk) | — | « ne couvre pas les émissions … des départements français d'outre-mer » |
| Terre-net (communiqué interministériel de 2019) | — | hausse des ventes de 2018 « liée à une anticipation des achats … en prévision de l'augmentation de la RPD » |
| Actu-environnement (recherche) | — | décret n° 2026-636 du 16/07/2026 (SNBC 3) existe |

Fichiers du dépôt lus : extraits Citepa (`citepa__secten_*`), OCDE (`ocde__odd_15.csv`, `ocde__hsl_bien_etre_*`), DREES (`drees__barometre_*`), Footprint (`gfn_fodafo__nfba2026_france.txt`), SDES ITDD, Santé publique France (`spf_odisse__*`), OWID.

**Refus et erreurs** : EUR-Lex (directive 2016/2284, demande d'autorisation sans réponse) ; legislation.gov.uk article 4 de la directive (idem) ; API OCDE `DSD_FOREST@DF_FOREST` (idem) ; API Odissé « population concernée par une canicule » (idem) ; métadonnées INSEE 12.i3 (première adresse en erreur, seconde lue) ; `fish_ca_main` (deux erreurs serveur, troisième lecture réussie) ; **API Eurostat `env_air_emis` COVNM `NFR_TOT_NAT` refusée (HTTP 429)**, aucune lecture Eurostat ensuite. Aucun outil d'accès à l'ordinateur de Léo, aucun navigateur, aucun appel d'API depuis un script.

## 3. Complétude et cohérence (scripts jetables dans `tmp/m06_planete/`)

- Présélection : 221 groupes relus ; lignes éligibles écartées en bloc regroupées par jeu (hors bilans énergétiques et moyens budgétaires) : motifs recevables, sauf la question des comptes forestiers (le catalogue Eurostat ne garde que l'unité `MIO_EUR` des volumes `for_vol_efa` sur les forêts exploitables).
- Recherche, dans les dix long-lists et les catalogues `*_non.csv.gz`, des concepts de la dimension : feux de forêt (absents partout), stocks halieutiques, haies, consommation d'ENAF (absents, déjà PLA-4), substances appauvrissant l'ozone et HANPP (absents), produits chimiques dangereux (jeu Eurostat sans donnée France), part modale des voyageurs (long-list `logement_cadre_vie`), pesticides dans les nappes (ITDD 2020-2022, non éligible), séries hors long-list des fiches (`15_2_1_OECD`, `OG05_1` : absentes de tous les catalogues, conforme à D36).
- Croisement des 75 fiches avec les 206 fiches des six autres dimensions (séries principales, composantes, variantes, lignes) : aucun identifiant, aucune série ni aucune ligne commune. Lignes renvoyées vers `planete` par d'autres présélections : 4 de `niveau_de_vie` (règle 1180) et 4 de `travail` (règle 960), **non reprises** dans la présélection `planete`.
- Familles : une seule mêle pression et état (`usage_sols`).

## 4. Résultat

42 fiches auditées : 23 `conforme`, 18 `a_corriger` (7 erreurs factuelles, 5 alignements sur D34-D35, 6 compléments levant une réserve de M05), 1 `non_verifiable` (`intensite_exploitation_forets`, définition OCDE). 3 oublis (plus les 3 sources de PLA-4), 6 points inter-dimensions, 9 désaccords de jugement. Avis global : `corrections_necessaires`, 14 corrections ordonnées.

## 5. Livraison

- Fichiers créés : `docs/validation/audit_planete.md` et ce journal. Aucune fiche, aucun tableau, aucun script ni aucun catalogue n'a été modifié ; ni la charte, ni le journal des décisions, ni `CLAUDE.md`, ni les fiches de mission.
- Commits sur `m06-planete`, push, PR #25 vers `main` ouverte par l'API GitHub (« M06 — audit croisé : planete ») ; rapport déposé dans le Projet sous `claude/cr/M06_planete_audit.md`.
