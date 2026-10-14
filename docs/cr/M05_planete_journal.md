# Journal de bord — M05, dimension `planete` (Planète)

Agent de mission M05 (dimension Planète, type plafond), branche `m05-planete`, 14 octobre 2026. Méthode commune appliquée : `docs/methodo/33_methode_fiches_M05.md` (v1.1), modèles `securite`, `liens_bien_etre`, `egalites`, `democratie` et audits M06.

## 0. Mise en route (10 h 05)

- Branche `m05-planete` créée depuis `origin/main` (`1a0697c`, fusion de la PR #12).
- Lus : `CLAUDE.md` ; charte §3.1 à §3.6, §4, §5.1 ; journal des décisions D13 à D33 (en particulier D15, D16, D17, D18, D19, D23 à D28, D32, D33) ; fiche M05 ; méthode commune v1.1 ; `indicateurs/dimensions.yaml` (définition, contenu, exclusions de `planete`, R1 à R8) ; fiches et règles des dimensions faites ; compte rendu `egalites` ; audits M06 `securite` et `liens_bien_etre` ; §5 et §8 de `30_crosswalk_synthese.md` ; lignes `planete` de `30_indicateurs_cadres_reference.csv` ; `10_indicateurs_candidats_hors_insee_eurostat.csv` ; `docs/sources/autres_sources.md` ; extraits du robot M04 (`docs/sources/series/` : Citepa, OCDE, OWID, SPF, SDES, Footprint Data Foundation, PNUD).
- Tests au départ : `python -m pytest -q` → 397 réussis.
- Outils communs utilisés tels quels (`scripts/preselection.py`, `scripts/verifier_fiches.py`) ; aucun fichier de `scripts/` ni de `src/` modifié (pas de déclenchement du robot « Collecte »). Les générateurs de travail (règles, fiches) restent dans le bac à sable ; leur produit est entièrement dans le dépôt.
- Présélections des autres dimensions relues (R1, D32) : aucune ligne de la long-list `planete` n'y est utilisée, aucune règle `autre_dimension:planete` ; la règle `crim_off_cat_non_eligibles` de `securite` mentionne les infractions environnementales (non éligibles), sans renvoi.

## 1. Ce que contient la long-list `planete` (10 h 15)

21 533 lignes : 15 945 éligibles, 559 à vérifier, 5 029 non éligibles. Eurostat 21 063 (229 jeux), INSEE BDM 194, Melodi 205, sources M04 71 (Citepa 21, OCDE 19, SDES 11, OWID 9, PNUD 3, Banque mondiale 3, Footprint Data Foundation 3, EDGAR 1, Santé publique France 1).

| Bloc | Lignes | Constat |
|---|---|---|
| Bilans énergétiques Eurostat (`nrg_cb_*`, `nrg_bal_*`, stocks, échanges, capacités, pompes à chaleur) | ≈ 11 000 | matière première des indicateurs agrégés, aucune lecture propre |
| Pesticides par culture et par substance (`aei_pestuse`) | 3 067 | 2 points par culture (2011, 2021) |
| Dépenses, subventions, taxes et investissements de protection de l'environnement (`env_epea_*`, `env_esst_*`, `env_ac_ep*`, `env_ac_pep*`, `env_ac_tax*`) | ≈ 2 270 | moyens budgétaires (charte §3.4) |
| Inventaires détaillés GES (`env_air_gge`, 811) et polluants (`env_air_emis`, 911), comptes d'émissions (`env_ac_ai*`) | ≈ 2 100 | sous-catégories CRF/NFR, tableaux de passage |
| Déchets (échanges, installations, emballages, DEEE, VHU, traitement) | ≈ 1 200 | détails techniques |
| Indicateurs ODD nationaux INSEE (BDM et Melodi `DS_NAT_SDG`, doublons l'un de l'autre) | ≈ 350 | cœur de la dimension (climat, énergie, eau, biodiversité, sols, déchets, agriculture) |
| Comptes de patrimoine (ressources naturelles en valeur, `DD_CNA_*`) | 49 | patrimoine national (A5) |
| Sources M04 (Citepa, OCDE How's Life « capital naturel », OWID, SDES ITDD, SPF, Footprint, PNUD, Banque mondiale) | 71 | |

Lignes à signaler : les masses d'eau (ODD 6.i2, 14.i1 : 4 points 2013-2021) et le gaspillage alimentaire (ODD 12.i3 : 5 points 2015-2023) sont **non éligibles** dans la long-list alors que D28 les rend candidates (écart moyen ≥ 1,5 an) : la règle de `src/pipeline/longlist.py` n'admet la souplesse D17 que si l'étendue atteint 10 ans (maintenance PLA-1).

## 2. Présélection (10 h 30)

- `docs/validation/regles_preselection_planete.csv` écrit par un générateur (bac à sable) : séries principales exactes (`ligne_id`), variantes précises, un import (`logement_cadre_vie`), écarts en bloc par expression sur `serie_id`, renvois.
- `python scripts/preselection.py --dimension planete` → **21 534 lignes affectées** (21 533 de la long-list, aucune sans règle, aucune règle vide ; 1 importée : OCDE 9_3 « population exposée à des températures extrêmes » de `logement_cadre_vie`, rattachement proposé au titre d'A14), **219 groupes** : 73 `fiche`, 120 `variante_de`, 23 `ecarte_en_bloc`, 3 `autre_dimension`.
- Après ajout des deux concepts hors long-list (§3.3) : **221 groupes** (75 `fiche`, 120 `variante_de`, 23 `ecarte_en_bloc`, 3 `autre_dimension`).
- Lignes de la long-list `planete` : **73 en `fiche`** (72 fiches, dont une somme de deux classes), **697 en `variante_de`**, **20 747 écartées en bloc** (15 261 éligibles, 524 à vérifier, 4 962 non éligibles), **16 renvoyées** à une autre dimension.
- Variantes regroupées par concept : les ventilations très fines (sous-catégories CRF/NFR, croisements gaz × secteur, secteur × origine de l'eau, composantes du bilan nutritif, détail des déchets par matériau et opération) sont écartées en bloc pour garder des listes de variantes lisibles ; les totaux par gaz, par grand secteur, par polluant, par usage et par mode de traitement restent en variantes.

| Écart en bloc | Lignes | Motif |
|---|---|---|
| `energie_bilans_detail` | 11 059 | bilans par produit et par flux, stocks, échanges, capacités, pompes à chaleur : matière première des agrégats |
| `pesticides_par_culture` | 3 067 | 2 points par culture, détail sans lecture propre (HRI1 et ventes retenus) |
| `moyens_budgetaires_environnement` | 2 268 | dépenses, subventions, taxes, investissements (charte §3.4, D19) |
| `dechets_echanges_installations` | 1 118 | commerce de déchets, installations, détail des emballages, VHU, DEEE, piles, traitement |
| `polluants_inventaire_detail` | 881 | NFR fins, monoxyde de carbone (hors plafonds NEC) |
| `ges_inventaire_detail` | 769 | CRF fins, gaz × secteur, soutes internationales |
| `activite_economique_verte` (+ INSEE) | 486 | biens et services environnementaux, emploi circulaire : sens ambigu |
| `comptes_emissions_passerelles` | 421 | tableaux de passage inventaire/comptes, équivalents acides |
| `energie_comptes_physiques` | 166 | comptes PEFA hors totaux |
| `bio_filiere_detail` | 163 | cheptel, productions, opérateurs bio |
| `eaux_usees_boues` | 129 | eaux usées (non éligibles) et boues |
| autres (11 groupes) | 220 | patrimoine (A5), dépendance aux importations (hors définition), indice mixte du PNUD (R1), forêts en valeur, composantes du bilan nutritif, de la circularité, de l'eau, moyens administratifs marins (D28) |

## 3. Familles, variantes principales et choix (10 h 40)

### 3.1 Règles appliquées
- **Émissions du territoire et empreinte : deux familles** (méthode §8, inventaire territorial contre consommation). Dans chacune, la série **en millions de tonnes** est principale (grandeur des budgets carbone, de l'objectif −50 % 2030/1990 et des fourchettes indicatives de la SNBC 3) et la série **par habitant** est une fiche `retenir_variante` (autre lecture, repères par personne). Les émissions nettes (UTCATF inclus) sont une variante ; le **puits de carbone** (UTCATF) forme une famille propre.
- **Énergie** : consommation **finale** et **primaire** en familles distinctes (consigne) ; principale Eurostat `nrg_ind_eff` (définition EED, 2005-2024) plutôt que l'INSEE (2011-2024, plus court) ; renouvelables (Eurostat `sdg_07_40`, 2004-2025), part des fossiles (`nrg_ind_ffgae`, 2000-2024) et productivité énergétique (`sdg_07_30`) en familles propres ; dépendance aux importations écartée en bloc (sécurité d'approvisionnement, hors définition).
- **Eau** : famille `pression_eau` (prélèvements par habitant, principale ; WEI+ en `retenir_variante`) ; qualité en familles d'**état** distinctes (état écologique des eaux de surface, état chimique des nappes, nitrates, phosphates, pesticides, baignade, eutrophisation marine) ; flux d'azote et de phosphore à la mer en familles de **pression**.
- **Azote et phosphore** : deux familles (`pression_azote_agricole`, `pression_phosphore_agricole`) avec l'excédent du bilan en principale et la consommation d'engrais minéraux (forme de la limite planétaire du Doughnut, cible SNBC 3) en `retenir_variante` ; l'ammoniac en famille propre.
- **Biodiversité** : oiseaux communs spécialistes (INSEE), indice Liste rouge (OCDE ODD 15.5.1), aires protégées terrestres (OCDE, cible de 30 %) avec la protection forte INSEE (cible de 10 %) en `retenir_variante`, aires marines, état des habitats (D17), espèces exotiques envahissantes (D17).
- **Ordre de la méthode §4** respecté : Eurostat préféré à l'INSEE quand il est plus long (énergie, renouvelables, matières, déchets municipaux, recyclage, prélèvements d'eau), OCDE quand il est plus long (aires marines) ; ITDD (produit commun SDES-INSEE) préféré à Eurostat pour l'agriculture biologique (même profondeur, valeurs Eurostat 2020-2024 estimées) et pour le rendement des réseaux (un an de plus que la BDM).
- **D15** : zones conservées telles que publiées (`FM_D99_D978` pour les séries INSEE d'émissions et d'empreinte, `FM` pour Teruti, les oiseaux, les flux à la mer, `FE` pour la protection forte, `FR` pour Eurostat) ; variantes métropole/France entière gardées en variantes.

### 3.2 Sens et type (D19)
- 38 pressions, 25 résultats (états et aléas subis), 12 moyens (renouvelables, aires protégées, agriculture biologique, recyclage, circularité, véhicules électriques, report modal, productivité énergétique, rendement des réseaux, PPR).
- `haut` : renouvelables, aires protégées, bio, recyclage, circularité, oiseaux, Liste rouge, habitats, espaces naturels, boisement, masses d'eau, baignade, diversité des cultures, productivité énergétique, véhicules électriques, rendement des réseaux. Les autres sont `bas`, sauf cinq `ambigu` (→ `ecarter`) : communes couvertes par un PPR, races locales menacées, captures de pêche, prélèvements de bois en volume, préoccupation pour l'environnement.

### 3.3 Hors long-list (D32)
- `intensite_exploitation_forets` : OCDE ODD « Intensity of use of forest resources » (2002-2023, 18 points), extraite par le robot (`ocde__odd_15.csv`) mais absente des catalogues ; principale de la famille `exploitation_forets` (les prélèvements en volume, au sens ambigu, sont écartés). Maintenance PLA-2.
- `preoccupation_environnement` : baromètre DREES OG05_1 (2000-2025), **seule mesure déclarative** de la dimension, écartée pour sens ambigu ; valeurs recalculées sur les distributions du robot (modalités 1+2 : 86,8 % en 2000, 76,7 % en 2025). Maintenance PLA-3.

### 3.4 Rattachements proposés
- **Vers `planete`** : OCDE How's Life 9_3 (population exposée à des températures extrêmes, ligne `m04-000063` de `logement_cadre_vie`) en `retenir_variante` de la famille `chaleur_extreme` (A14).
- **Hors de `planete`** : 8 lignes d'environnement local déclaré (`ilc_mddw02`, `ilc_mddw05`, `hlth_dhc120`) et 3 lignes d'assainissement (`sdg_06_20`, `env_ww_con`, ITDD conformité des stations) → `logement_cadre_vie` ; 5 lignes de privation alimentaire (`ilc_mdes03`, `hlth_dm030`) → `niveau_de_vie` (A2).

## 4. Vérifications à la source (10 h 20 – 10 h 45)

Lues sur l'API Eurostat (WebFetch, 14/10/2026), valeurs et drapeaux des séries principales : `sdg_13_10`, `env_air_gge` CRF 4, `sdg_12_31`, `sdg_13_40`, `sdg_15_42`, `nrg_ind_eff`, `sdg_07_40`, `nrg_ind_ffgae`, `sdg_07_30`, `sdg_13_31` (rupture `b` en 2017, NEDC → WLTP), `fish_ca_main`, `for_remov`, `sdg_15_50`, `env_wat_abs`, `sdg_06_60`, `sdg_06_50`, `sdg_06_70` (définition lue : part des masses d'eau déclarées dépassant des seuils fondés sur les NQE), `env_air_emis` (NH3, NOx, PM2,5), `aei_pr_gnb` (rupture `b` en 2010), `aei_fm_usefert`, `aei_hri`, `sdg_02_40` (2020-2024 estimés), `env_wasmun` (estimations, saut 2015-2016 sans drapeau), `sdg_11_60`, `sdg_12_21` (2024-2025 imputés), `env_ac_mfa` (ruptures 2000, 2004, 2009), `sdg_12_51`, `sdg_14_40`.

**Non lus** : `sdg_06_40` et `sdg_14_60` (refus 429 du proxy de lecture, à ne pas relancer), `env_air_emis` SOx, COVNM et plomb, `sdg_12_41` (pour limiter les appels) : drapeau `drapeaux_eurostat_non_lus` dans les fiches. **BDM INSEE** : lecture refusée (robots.txt) ; aucune valeur INSEE n'est citée dans les fiches, seules les périodes de la long-list. Valeurs des sources M04 lues dans les extraits du robot (`docs/sources/series/` : Citepa, OCDE, ITDD, SPF, SDES ozone, DREES).

## 5. Fiches et contrôles (10 h 50)

- Fiches écrites par un générateur (bac à sable) : textes rédigés, périodes, points, zones, identifiants et URL d'API lus dans la long-list ; `python scripts/preselection.py --dimension planete --maj-fiches` → variantes injectées ; `python scripts/verifier_fiches.py --dimension planete --tableau` puis sans option → **0 erreur, 2 avertissements** (les deux séries hors catalogue, attendus).
- Compteurs du vérificateur : **75 fiches, 65 familles, 61 `retenir`, 9 `retenir_variante`, 5 `ecarter`**, 1 déclarative, 2 composites (empreinte écologique, empreinte de consommation de l'UE), 3 `a_verifier` (érosion, espèces exotiques, habitats), 2 hors long-list, **7 incontournables** (émissions du territoire et par habitant, empreinte carbone et par habitant, artificialisation, espaces naturels, taux de boisement), 697 variantes, 0 ligne déjà prise par une autre dimension.
- Séries irrégulières (D17) : 7 (habitats, espèces exotiques, érosion, état des eaux de surface et des nappes, gaspillage alimentaire, déchets toutes activités).
- Tests : 397 réussis ; vérificateur des quatre autres dimensions inchangé.
- Maintenance : `docs/cr/maintenance_catalogues_planete.md`, lignes PLA-1 à PLA-8 (statut `a_faire`).

## 6. Clôture (11 h 00)

- PR **#17** « M05 — fiches indicateurs : planete » ouverte vers `main` par l'API GitHub (`gh` indisponible) : https://github.com/leomalherbe/prosperite/pull/17.
- Compte rendu `docs/cr/M05_planete_compte_rendu.md`, copié dans le Projet claude.ai (`claude/cr/M05_planete_compte_rendu.md`) avec le tableau de validation (`claude/40_validation_planete.csv`).
- Avant chaque poussée : `git fetch origin main` (aucun nouveau commit sur `main` pendant la mission, pas de rebasage nécessaire).
