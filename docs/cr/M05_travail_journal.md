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

Rattachements : 51 lignes reprises par `egalites` et 20 par `liens_bien_etre` → `autre_dimension` (règles 10 et 20). Ventilations par sexe des taux d'emploi, de chômage et de la part du temps partiel (écarts déjà au catalogue d'`egalites`) → `autre_dimension:egalites` (289 lignes) ; ventilations par sexe des autres mesures (NEET, sous-emploi, halo, contrats temporaires, accidents…) gardées en variantes ici, faute d'écart au catalogue d'`egalites`.

`python scripts/preselection.py --dimension travail` → **6 525 lignes affectées** (6 520 + 5 importées de `niveau_de_vie`), **0 sans règle**, aucune règle vide, **123 groupes** : 37 `fiche` (dont 2 hors long-list), 49 `variante_de`, 26 `ecarte_en_bloc`, 11 `autre_dimension`.
