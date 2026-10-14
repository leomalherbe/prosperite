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
