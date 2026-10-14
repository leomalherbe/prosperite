# Journal de bord — M05, dimension `travail` (Travail et emploi)

Agent de mission M05 (dimension Travail et emploi), branche `m05-travail`, 14 octobre 2026. Méthode commune appliquée : `docs/methodo/33_methode_fiches_M05.md` (v1.1), modèles `securite`, `liens_bien_etre`, `egalites`, `democratie`.

## 0. Mise en route (08:20 UTC)

- Branche `m05-travail` créée depuis `origin/main` (`1a0697c`, fusion de la PR #12).
- Lus : `CLAUDE.md`, charte (§3.4, §3.6, §4, §5.1), journal des décisions (D13–D33), fiche M05, méthode commune v1.1, `indicateurs/dimensions.yaml` (définition, contenu et exclusions de `travail`, R1–R8), `31_correspondance_v0_v1.csv`, fiches et règles des dimensions faites, `M05_egalites_compte_rendu.md`, rapports d'audit `audit_securite.md` et `audit_liens_bien_etre.md`, §5 de `30_crosswalk_synthese.md`, lignes `travail` de `30_indicateurs_cadres_reference.csv`, `docs/sources/insee.md` (§3.4, §12), extraits du robot M04 (OCDE, Ameli, DREES).
- Tests : `python -m pytest -q` → 397 réussis au départ.
- Rattachements croisés lus avant de commencer (R1, D32) : `preselection_egalites_lignes.csv` utilise **51 lignes** de la long-list `travail` (composantes et variantes des écarts femmes-hommes, selon l'origine et selon le diplôme, parts des hauts salaires) ; `preselection_liens_bien_etre_lignes.csv` en utilise **20** (`ilc_mdes02` ×2, `hlth_dm020` ×3, 15 lignes Melodi de satisfaction dans la vie par statut d'activité ; consigne I4 de l'audit M06). `securite` et `democratie` n'en utilisent aucune.
- Incohérence relevée dans `indicateurs/dimensions.yaml` : l'exclusion de `travail` cite encore « thème temps (longues durées de travail, horaires atypiques, équilibre des temps) non traité en v1 », alors que le contenu et D27 gardent les longues durées et les horaires atypiques dans `travail`. J'applique D27 (proposition de correction au compte rendu).

## 1. Long-list et présélection (09:40 UTC)

Long-list `travail` : **6 520 lignes** (5 327 éligibles, 253 à vérifier, 940 non éligibles) ; Eurostat 4 040, Melodi 2 014 (dont `DD_EEC_SERIES` 1 673), BDM 452, M04 14 (OCDE 9, Assurance maladie 3, PNUD 2).

Constats d'exploration (par jeu et par mesure) :
- **`DD_EEC_SERIES`** (enquête Emploi, séries longues) : 23 mesures croisées par sexe, âge, diplôme, PCS, forme d'emploi, temps de travail, composante du sous-emploi et du halo. La page INSEE des séries longues (`insee.fr/fr/statistiques/8977323`, lue par WebFetch) indique des séries **rétropolées** : rupture de 2003 (enquête en continu), de 2013 (questionnaire) et de 2021 (rénovation) corrigées, champ France entière y compris Mayotte. C'est l'argument central pour en faire la variante principale (INSEE > Eurostat, et Eurostat porte le drapeau « d » depuis 2021 : vérifié sur `une_ltu_a`, `lfsi_sla_a`, `lfsa_qoe_3a2`, `lfsa_eoqgan`).
- Les mesures `PT_*` de Melodi ont des libellés ambigus (« Part du sexe et de l'âge dans le nombre de jeunes NEET ») ; les tableaux INSEE correspondants (t309, t310, t401) les décrivent comme des parts de la population ou de l'emploi du groupe. L'API Melodi est refusée à WebFetch (robots.txt) : unité à confirmer au premier passage du robot (drapeau `libelle_melodi_ambigu`).
- **BDM** : séries trimestrielles CVS de l'enquête Emploi (chômage, halo, sous-emploi, taux d'emploi en EQTP, NEET), demandeurs d'emploi France Travail (120 lignes), salaires du privé (FM99_FR00), comptes nationaux, indicateurs ODD et IRN 1.
- **Eurostat** : 300 jeux environ, dont une majorité de structures (profession, branche, NUTS, typologies) et de jeux d'entreprises (coût de la main-d'œuvre, vacances d'emploi). Les jeux de qualité de l'emploi du cadre Qualité de vie sont présents (`lfsa_eppgai`, `lfsa_eoqgan`, `lfsa_qoe_3a2`, `lfsa_esegatyp`, `lfsa_ewpnig`, `lfsi_long_a`, `hsw_*`).
- Aucune exclusion abusive repérée : les non-éligibles sont des séries arrêtées (OCDE 2_5, 2_6, jeux `_h` arrêtés en 2020), des modules ad hoc à un point (2020) ou l'enquête sur la structure des salaires (4 ou 5 points, à vérifier D17).

Règle sur les séries trimestrielles (consigne de la session mère) : retenues comme principales seulement faute de série annuelle de même définition (taux d'emploi en EQTP, part des personnes contraintes sur leur offre de travail). Le taux de chômage de longue durée, publié par l'INSEE seulement en trimestriel, est **calculé** sur les séries longues annuelles (chômeurs depuis un an ou plus / actifs), plutôt que pris chez Eurostat (drapeau « d » depuis 2021).

Rattachements : 51 lignes reprises par `egalites` et 20 par `liens_bien_etre` → `autre_dimension` (règles 10 et 20). Ventilations par sexe des taux d'emploi, de chômage et de la part du temps partiel (écarts déjà au catalogue d'`egalites`) → `autre_dimension:egalites` (305 lignes) ; ventilations par sexe des autres mesures (NEET, sous-emploi, halo, contrats temporaires, accidents…) gardées en variantes ici, faute d'écart au catalogue d'`egalites`.

`python scripts/preselection.py --dimension travail` → **6 525 lignes affectées** (6 520 + 5 importées de `niveau_de_vie`), **0 sans règle**, aucune règle vide, **123 groupes** : 37 `fiche` (dont 2 hors long-list), 49 `variante_de`, 26 `ecarte_en_bloc`, 11 `autre_dimension`.

Répartition des 6 520 lignes de la long-list : 36 en `fiche` (séries principales, dont 2 composantes pour chacune des deux formules), 1 671 en `variante_de`, 4 161 en `ecarte_en_bloc` (3 131 éligibles, 185 à vérifier, 845 non éligibles), 652 en `autre_dimension` (`egalites` 361, `securite` 171, `education` 96, `liens_bien_etre` 20, `planete` 4). Cinq lignes importées de `niveau_de_vie` (salaire moyen réel et trois variantes, `sdg_01_41`).

## 2. Fiches (10:30 UTC)

Outil de travail (bac à sable, non commité) : un générateur de règles et un générateur de fiches qui écrivent par `preselection.texte_yaml` ; périodes, nombre de points, URL d'API et zone lus dans la long-list. Puis `python scripts/preselection.py --dimension travail --maj-fiches` (variantes injectées dans 33 fiches) et `python scripts/verifier_fiches.py --dimension travail --tableau`.

**37 fiches, 28 familles** : 24 `retenir`, 8 `retenir_variante`, 5 `ecarter` ; 3 déclaratives (préoccupation pour le chômage, risque de chômage perçu, satisfaction au travail) ; 0 composite ; 3 à vérifier (D17 : bas salaires OCDE et SES, risques psychosociaux) ; 2 hors long-list (baromètre DREES) ; 4 fiches incontournables (familles taux d'emploi et longues durées de travail, §5 du crosswalk) ; 1 675 variantes.

Choix structurants :
- **Une famille par concept, INSEE en principale** : taux d'emploi, chômage, NEET, sous-emploi, contrats temporaires, temps partiel et activité prennent la série longue rétropolée `DD_EEC_SERIES` ; Eurostat (EFT) et la BDM trimestrielle sont des variantes. Exceptions motivées : fiches variantes Eurostat quand la lecture diffère (taux d'emploi des 20-64 ans de la cible de 78 %, temps partiel involontaire rapporté au temps partiel, emploi temporaire subi, contrats très courts).
- **Formules** : taux de chômage de longue durée (chômeurs depuis un an ou plus / actifs) et part des CDD et de l'intérim (somme de deux parts), toutes deux sur les séries longues de l'INSEE (maintenance TRA-2).
- **Trimestrielles en principale** (faute de série annuelle de même définition) : taux d'emploi en EQTP et part des personnes contraintes sur leur offre de travail (sous-utilisation, OCDE 13_2).
- **Accidents du travail : deux familles** (`accidents_travail` avec arrêt, Assurance maladie 2005-2024 ; `accidents_travail_mortels`, Eurostat `hsw_n2_02` 2008-2024). Motifs : un décès n'est pas substituable à un accident avec arrêt (méthode §1, concepts complémentaires) et les accidents mortels portent une préoccupation publique propre (§9, D32). Principale non mortelle nationale (Assurance maladie) plutôt qu'ESAW : plus longue, et la série ESAW varie de 3 443,59 (2008) à 2 303,37 (2009) avec quatre ruptures.
- **Écartées** (sens ambigu ou dominée) : taux d'activité, part du temps partiel, durée hebdomadaire moyenne, maladies professionnelles reconnues (en nombre, dépend de la reconnaissance), demandeurs d'emploi (série administrative en nombre, dominée par le chômage BIT).
- **Rémunération** : `salaire_net_moyen_reel` (INSEE, euros constants, 1996-2024) importé de la long-list `niveau_de_vie` avec `rattachement_propose` ; bas salaires (OCDE 2_8_DEP principal, SES Eurostat en variante) ; pauvreté des personnes en emploi (EU-SILC), à la frontière de `niveau_de_vie`.
- **Sécurité de l'emploi ressentie** (A15) : deux questions du baromètre DREES hors long-list (OG04_6 « préoccupé par le chômage », 2000-2025, valeurs recalculées sur les distributions du robot : 90,7 % en 2000, 63,5 % en 2025 ; SDRICHOM « risque de chômage pour soi ou un proche », 2010-2025, à calculer).

Vérifications à la source (API Eurostat par WebFetch, 14/10/2026) : `une_ltu_a`, `lfsa_qoe_3a2`, `lfsa_esegatyp`, `hsw_exp1`, `hsw_n2_02`, `sdg_08_60`, `hsw_n2_01`, `lfsa_eppgai`, `lfsi_long_a` (EMP_UNE), `lfsi_sla_a`, `lfsa_eoqgan`, `ilc_iw01`, `sdg_08_30`, `ilc_lvhl11`, `lfsa_eetpgar`, `lfsa_qoe_4ax1r2`, `ilc_lvhl36`, `earn_ses_pub1s`, `lfsa_ewpnig`, `lfsa_ewpsun`, `lfsa_ewhuis` ; page INSEE des séries longues (8977323 et 8977299). Refusés : API Melodi (robots.txt) ; `lfsi_long_e09` et `lfsi_long_a` UNE_EMP (HTTP 429, non relus ensuite, conformément à la consigne de l'outil). Extraits du robot lus : OCDE (`ocde__hsl_bien_etre_*`), Assurance maladie (`cnam_ameli__sinistralite_naf1`), DREES (couverture, distributions, dictionnaires).

Ruptures constatées (drapeaux lus) : Eurostat EFT « d » ou « bd » depuis 2021 sur toutes les séries lues (2021 : rénovation de l'enquête Emploi) ; sauts de 2003 (passage à l'enquête en continu) sur les longues durées (8,0 % → 13,4 %) et le travail du dimanche (9,7 % → 12,9 %) ; **chute non signalée de 2013** du travail de nuit (7,1 % → 3,7 %, nouveau questionnaire) ; rupture de 2020 de `ilc_lvhl36` (12,0 % → 19,3 %) ; temps partiel involontaire 36,9 % → 27,2 % en 2021 ; emploi temporaire subi 7,3 % → 5,8 % en 2021. Les séries longues de l'INSEE corrigent 2003, 2013 et 2021 : c'est la raison de leur choix en principale.

`python scripts/verifier_fiches.py --dimension travail` → **0 erreur**, 2 avertissements (les deux fiches DREES hors catalogue, avec preuve) ; `lignes_prises_ailleurs 0`. `python -m pytest -q` → 397 réussis.

## 3. Maintenance

`docs/cr/maintenance_catalogues_travail.md` : 10 lignes `TRA-1` à `TRA-10` (DREES OG04_6 et SDRICHOM, formules du pipeline, unité des mesures `PT_*` de Melodi, rattachements de la table v0→v1, salaires, pauvreté en emploi, Assurance maladie, conditions de travail DARES, métadonnées Eurostat, chute de 2013 du travail de nuit). Le fichier partagé `maintenance_catalogues.md` n'est pas modifié.
