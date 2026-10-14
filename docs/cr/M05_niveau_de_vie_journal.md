# Journal de bord — M05, dimension `niveau_de_vie` (Niveau de vie)

Agent de mission M05 (dimension Niveau de vie), branche `m05-niveau_de_vie`, 14 octobre 2026. Méthode commune appliquée : `docs/methodo/33_methode_fiches_M05.md` (v1.1), modèles : dimensions `securite`, `liens_bien_etre`, `egalites` (fusionnées) et audits M06.

## 0. Mise en route (14/10, 10 h 00)

- Branche `m05-niveau_de_vie` créée depuis `origin/main` (`1a0697c`, fusion de la PR #12).
- Lus : `CLAUDE.md`, charte (§3.4, §3.6, §4, §5.1), journal des décisions (D01–D33), fiche de mission M05, méthode commune v1.1, `indicateurs/dimensions.yaml` (définition, contenu et exclusions de `niveau_de_vie`, R1–R8), `docs/methodo/31_correspondance_v0_v1.csv`, `32_longlist_mode_emploi.md`, §5 de `30_crosswalk_synthese.md`, lignes `niveau_de_vie` de `30_indicateurs_cadres_reference.csv`, compte rendu et règles d'`egalites`, audits `securite` et `liens_bien_etre`, `docs/cr/maintenance_catalogues.md` (lignes 1 à 35), fiches des quatre dimensions déjà faites (liste des séries principales).
- Tests : `pip install -r requirements.txt && python -m pytest -q` → 397 réussis au départ.
- Outils communs utilisés tels quels (`scripts/preselection.py`, `scripts/verifier_fiches.py`). Aucun fichier sous `scripts/` ni `src/` n'est modifié. Les générateurs de travail (règles, fiches) restent dans le bac à sable (sous-dossier privé : le bac à sable est partagé avec les autres agents M05, dont l'un a écrasé un premier fichier de travail homonyme) ; leur produit est entièrement dans le dépôt.
- Long-list non régénérée (catalogues inchangés depuis le 14/10).

## 1. Ce que contient la long-list `niveau_de_vie`

11 821 lignes : 7 874 éligibles, 3 124 à vérifier, 823 non éligibles ; Eurostat 9 169, Melodi 2 377, BDM 261, M04 14.

Lecture **par jeu et par mesure**, pas ligne à ligne :

| Bloc | Lignes | Constat |
|---|---|---|
| Comptes nationaux INSEE (Melodi `DD_CNA_*`, BDM comptes annuels et trimestriels) | ≈ 1 400 | agrégats par secteur institutionnel, opération, produit, prix courants ou chaînés, niveau ou évolution ; une douzaine de mesures intelligibles (PIB et RNB par habitant, pouvoir d'achat par UC, taux d'épargne, dépenses pré-engagées, patrimoine net) |
| Comptes nationaux Eurostat (`nasa_10_*`, `nama_10_*`, `naida_10_gdp`, `naidsa_10_f_bs`, `gov_10*`) | ≈ 3 400 | dont 1 838 lignes de comptes financiers par instrument et 410 de comptes des administrations ; les mesures par habitant en termes réels sont dans `nasa_10_nf_tr` (B6G_R_HAB, B7G_R_HAB, P4_R_HAB), `nasa_10_ki` et `nama_10_pc` |
| Parités de pouvoir d'achat (`prc_ppp_ind`, `prc_ppp_ind_1`) | 1 639 | indices de niveau des prix par produit ; seules les dépenses réelles par habitant du PIB et de la consommation individuelle effective servent (variantes) |
| Budget de famille (`hbs_*`), consommation par fonction (COICOP) | ≈ 2 800 | structure de la dépense, quinquennale pour `hbs` |
| EU-SILC (`ilc_*`, `sdg_01_*`, `hlth_d*`, `icw_*`) | ≈ 2 200 | pauvreté (seuils 40 à 70 %, ventilations), privations, AROPE, pauvreté subjective, satisfaction financière, structure des ménages, modes de garde |
| INSEE ERFS (`DS_ERFS_RETROPOLE`, `DS_ERFS_NON_RETROPOLE`) | 800 | dont 510 valeurs de rupture (BWA, BWB) qui ne sont pas des séries (maintenance n° 20) |
| INSEE ODD (BDM et `DS_NAT_SDG`), salaires (`DS_DERA_*`, SMIC), patrimoine (`DS_ENQPAT_DET`) | ≈ 700 | |
| M04 (OCDE How's Life, DREES, PNUD, Banque mondiale, BCE) | 14 | |

Recherche hors de la long-list (méthode §8, R1) : présélections des quatre dimensions déjà faites (104 lignes de `niveau_de_vie` reprises par `egalites`, 86 lignes d'`egalites` renvoyées ici) ; autres long-lists (`ilc_mdes03` et `hlth_dm030` dans `planete`, maintenance n° 35) ; catalogue `insee_melodi_catalogue_non.csv.gz` (SRCV `DS_SRCV_PMS` 2020-2025, maintenance n° 8) ; catalogue des jeux Eurostat (`ilc_li22` ancré 2019, `sdg_10_20` sans donnée France) ; sorties du robot M04 (baromètre DREES : PE01, PE02, PE03, OG04_3, PE07, CS27).

## 2. Présélection (10 h 20 – 10 h 35)

- `docs/validation/regles_preselection_niveau_de_vie.csv` : **140 règles** (ordre : lignes déjà reprises par `egalites`, séries principales exactes, variantes par jeu et par mesure, imports d'autres long-lists, renvois `autre_dimension`, puis écarts en bloc par jeu). Expressions régulières sur `serie_id` (paramètres Melodi `STO=`, `REF_SECTOR=`, `ERFS_MEASURE=` ; paramètres Eurostat `na_item=`, `statinfo=`, `rskpovth=`) et sur `ligne_id` pour la BDM (identifiants consécutifs par tableau).
- `python scripts/preselection.py --dimension niveau_de_vie` → **11 912 lignes affectées** (les 11 821 de la long-list, aucune sans règle, aucune règle vide ; 91 importées : `egalites` 86, `planete` 5), **140 groupes** : 25 `fiche` (24 lignes + 1 hors long-list), 57 `variante_de` (1 271 lignes propres + 11 importées), 43 `ecarte_en_bloc` (9 831 lignes propres + 80 importées), 15 `autre_dimension` (695 lignes : `travail` 354, `egalites` 249, `logement_cadre_vie` 45, `education` 24, `securite` 19, `planete` 4).
- Première exécution : 3 lignes sans règle (`nama_10_pc` P31_S13, P32_S13, P3_S13 : consommation des administrations par habitant) → ajoutées aux comptes des administrations (A5).

### 2.1 Comptes nationaux (D30) : traitement par jeu et par mesure

| Bloc | Lignes | Décision |
|---|---|---|
| Consommation par produit (COICOP), coefficients budgétaires, Budget de famille, dépense culturelle, consommation mensuelle de biens | 2 574 | écart en bloc : détail par produit, la consommation totale par habitant porte le concept |
| Patrimoine et comptes financiers par actif (`DD_CNA_PATRIMOINE`, `DD_CNA_TEE` hors valeur nette, `nasa_10_f_*`, `naidsa_10_f_bs`, droits à pension) | 2 204 | écart en bloc : composantes techniques ; la valeur nette des ménages est une variante de `patrimoine_net_median` |
| Parités de pouvoir d'achat et niveaux de prix par produit | 1 606 | écart en bloc ; les dépenses réelles par habitant du PIB et de la consommation individuelle effective sont des variantes |
| Administrations publiques (`DD_CNA_APU`, secteur S13, `gov_10*`, BDM) | 634 | écart en bloc (A5, R6) |
| Opérations des ménages (valeur ajoutée, excédent, revenu mixte, revenus primaires, salaires, cotisations, impôts, prestations, transferts en nature, CCF, capacité de financement ; `nasa_10_nf_tr`, `nama_10r_2hhinc`) | 381 | écart en bloc : composantes du revenu disponible sans lecture propre |
| ISBLSM, total des secteurs résidents, économie totale hors PIB et revenu national, parts dans le PIB, comptes trimestriels | 453 | écart en bloc (D29 P6 ; conjoncture) |
| Mesures retenues | 241 variantes et 9 fiches | revenu disponible ajusté réel par habitant (Eurostat), pouvoir d'achat par UC, PIB par habitant, revenu national réel par habitant, consommation individuelle effective par habitant, dépenses pré-engagées, taux d'épargne (écarté, sens ambigu), patrimoine (valeur nette des ménages en variante) |

Le niveau réel par habitant du revenu disponible n'existe qu'à Eurostat (`nasa_10_nf_tr`, B7G_R_HAB et B6G_R_HAB) : l'INSEE ne publie dans les catalogues que des évolutions (`_PAM_UC`) et des montants totaux en euros courants. D'où une famille `revenu_disponible_menages` à principale Eurostat (niveau) et variante de fiche INSEE (évolution, la mesure du débat public). Même logique pour la consommation : niveau par habitant chez Eurostat (`nama_10_pc` P41), totaux seulement à l'INSEE.

### 2.2 Familles INSEE / Eurostat (même définition)

| Concept | Principale | Variante(s) Eurostat ou autre | Motif |
|---|---|---|---|
| Taux de pauvreté à 60 % | INSEE ERFS rétropolée (1996-2024, sans rupture) | EU-SILC `ilc_li02`, `sdg_01_20` (2000-2025, ruptures 2008, 2020, 2022) ; ODD BDM 2010-2023 | INSEE > Eurostat à définition égale, série sans rupture |
| Taux de pauvreté à 50 % | INSEE ERFS rétropolée | EU-SILC, OCDE 1_4 | idem |
| Intensité de la pauvreté | INSEE ERFS rétropolée | `ilc_li11`, `sdg_10_30` | idem |
| Niveau de vie médian | INSEE ERFS rétropolée | `ilc_di03`, `ilc_di18` | idem |
| Privation matérielle et sociale | INSEE BDM ODD 1.i2 (2013-2024) | `ilc_mdsd07` (2014-2025), SRCV Melodi 2020-2025 (`_non`) | Eurostat plus frais d'un an mais moins profond d'un an : INSEE gardé |
| Privation alimentaire | INSEE BDM ODD 2.i1 (2010-2024) | `ilc_mdes03` (2004-2025, long-list `planete`) | INSEE ; raccordement 2004-2009 à étudier |
| PIB par habitant | INSEE BDM 011779993 (1949-2025) | `sdg_08_10`, `nama_10_pc` | INSEE |
| Privation sévère, AROPE, pauvreté persistante, ancrée, subjective, satisfaction financière | Eurostat | — | pas d'équivalent INSEE au catalogue |

### 2.3 Lignes reprises par d'autres dimensions (R1)

- 84 lignes de mesures de dispersion déjà reprises par `egalites` (S80/S20, parts de niveau de vie, S90/S50, parts du patrimoine) → `autre_dimension:egalites`.
- 16 lignes composantes d'écarts construits d'`egalites` (`ilc_li02` par sexe et par âge, `ilc_li31` à `ilc_li34` par nationalité) gardées en ventilations de `taux_pauvrete_60` selon D32 (« les lignes sources restent des ventilations ») : 4 avertissements R1 attendus du vérificateur.
- 4 lignes de salaires par sexe reprises par `egalites/ecart_salaire_eqtp_fh` → `autre_dimension:travail` avec l'ensemble des salaires.
- Les 86 lignes d'`egalites` renvoyées ici par M05 `egalites` (maintenance n° 11) sont importées, et elles seules : 6 en variantes (`ilc_di04`, seuils D1 et D5 d'`ilc_di01`, `statinfo = TC`), 80 écartées en bloc (seuils des autres quantiles, revenu par intensité de travail, revenus avant transferts). Une première version des règles importait aussi les parts `ilc_di01` `statinfo = SHARE` qu'`egalites` garde : corrigé (règles limitées à `statinfo = TC`).

## 3. Fiches (10 h 35 – 11 h 05)

25 fiches écrites par un générateur de travail (bac à sable), variantes injectées par `python scripts/preselection.py --dimension niveau_de_vie --maj-fiches` (1 282 variantes de la long-list + 3 ajouts manuels du catalogue `insee_melodi_catalogue_non`).

Vérifications à la source (WebFetch, 14/10/2026) :
- API Eurostat : `nasa_10_nf_tr` B7G_R_HAB et B6G_R_HAB, `nama_10_pc` P41, `sdg_01_10`, `ilc_mdsd11`, `ilc_mdsd07`, `ilc_li21`, `ilc_sbjp01`, `ilc_mdes09` (GRT et DIF : leur somme égale `ilc_sbjp01` à l'arrondi près sur 2010-2025), `ilc_pw01b` (FIN), `nasa_10_ki` SRG_S14_S15.
- **Non lus** : `ilc_li22b` (l'API Eurostat a renvoyé une erreur 429, « trop de requêtes », et l'outil a demandé de ne plus réessayer : la fiche `pauvrete_ancree_2008` porte `valeurs_non_lues`) ; la BDM et Melodi de l'INSEE (robots.txt) ; l'API de la Banque mondiale pour l'insécurité alimentaire (erreur du serveur).
- Page insee.fr de l'Insee Première n° 2117 (niveau de vie et pauvreté en 2024) : médiane, taux et seuil de pauvreté, intensité, premier décile, nombre de pauvres.
- Sorties du robot M04 dans le dépôt : baromètre DREES (PE01, PE03 : distributions, couverture, dictionnaire 2025), PNUD (IDH).

## 4. Contrôles

- `python scripts/verifier_fiches.py --dimension niveau_de_vie --tableau` puis sans option : **0 erreur, 5 avertissements** (1 série principale hors catalogue avec preuve : `pauvrete_percue_hausse` ; 4 lignes déjà séries principales d'écarts construits d'`egalites`, attendues, §2.3).
- Compteurs : 11 821 lignes de long-list, 695 renvoyées à d'autres dimensions, **25 fiches, 19 familles, 17 `retenir`, 6 `retenir_variante`, 2 `ecarter`**, 4 déclaratives, 2 composites, 2 à vérifier (D17), 1 hors long-list, 6 incontournables, 1 285 variantes.
- `python -m pytest -q` : 397 réussis (aucun fichier de code modifié).

## 5. Incidents

- **Bac à sable partagé** : le dossier de travail est commun aux agents M05 parallèles ; un premier générateur de règles de cet agent (`gen_regles.py`) a été écrasé par celui de l'agent `travail`. Travail repris dans un sous-dossier privé ; aucun effet sur le dépôt (proposition au compte rendu, §7.5).
- **API Eurostat** : réponse 429 (« trop de requêtes ») sur `ilc_li22b` après une dizaine de lectures ; consigne de l'outil : ne pas réessayer. Valeurs de `pauvrete_ancree_2008` non lues (drapeau `valeurs_non_lues`).
- **INSEE BDM et Melodi** : lecture refusée (robots.txt) ; valeurs INSEE citées d'après la page insee.fr de l'Insee Première n° 2117 et les métadonnées Melodi présentes dans le dépôt, sinon « non lues ».

## 6. Pull request (11 h 20)

- PR **#16** « M05 — fiches indicateurs : niveau_de_vie » ouverte vers `main` par l'API GitHub (`POST /repos/leomalherbe/prosperite/pulls`) : https://github.com/leomalherbe/prosperite/pull/16.
- Compte rendu copié dans le Projet claude.ai (`claude/cr/M05_niveau_de_vie_compte_rendu.md`) avec le tableau de validation (`claude/40_validation_niveau_de_vie.csv`).
