# Journal de bord — M06, audit croisé de la dimension `logement_cadre_vie`

Agent auditeur M06 (session neuve, Opus), 16 octobre 2026, branche `m06-logement_cadre_vie` (worktree isolé). L'agent n'a pas participé à M05 `logement_cadre_vie`. Rapport : `docs/validation/audit_logement_cadre_vie.md`. Aucune fiche, aucune règle, aucun tableau, aucun script ni aucun catalogue n'a été modifié.

## 0. Mise en route

- `git fetch origin && git checkout -B m06-logement_cadre_vie origin/main` : base `d85ef3a` (journal D37 à D40). Elle contient la fusion de la PR #26 (fiches `logement_cadre_vie`, `b252eae`), celle de la PR #22 (`education`, `d4deaa3`) et celle de la PR #20 (`sante`).
- Lus :
  - `CLAUDE.md` ;
  - charte §3.4, §3.6, §4, §5.1 ;
  - journal D13 à D40, en particulier D32, D34, D35, D38 et D39 ;
  - méthode commune v1.2 (`docs/methodo/33_methode_fiches_M05.md`) en entier ;
  - `indicateurs/dimensions.yaml` (contenu et exclusions de la dimension, R1 à R8) ;
  - fiche M06 ;
  - modèles `audit_travail.md` et `audit_planete.md`, journal `M06_travail_journal.md` ;
  - §5 de `30_crosswalk_synthese.md` et les 37 lignes « logement » de `30_indicateurs_cadres_reference.csv`.
- Matériau audité :
  - les 44 fiches, `validation_logement_cadre_vie.csv` ;
  - `preselection_logement_cadre_vie.csv` (142 groupes) et `preselection_logement_cadre_vie_lignes.csv` (1 664 lignes) ;
  - `regles_preselection_logement_cadre_vie.csv` ;
  - journal et compte rendu M05 ;
  - LOG-1 à LOG-11 de `maintenance_catalogues.md`.
- Contrôles de départ :
  - `pip install -r requirements.txt && python -m pytest -q` → **399 réussis** ;
  - `python scripts/verifier_fiches.py --dimension logement_cadre_vie` → **0 erreur, 3 avertissements** (séries principales hors catalogue de `connaissance_personne_sdf`, `duree_trajet_domicile_travail` et `preoccupation_logement`, attendus) ;
  - compteurs : 44 fiches, 33 familles, 30 `retenir`, 10 `retenir_variante`, 4 `ecarter`, 5 déclaratives, 0 composite, 1 « à vérifier », 3 hors long-list, 16 incontournables, 497 variantes, 146 lignes `autre_dimension`, 0 ligne prise ailleurs.
- Scripts de contrôle écrits dans le répertoire de travail de la session, hors dépôt : lecture des long-lists, renvois croisés, recouvrement inter-dimensions, comparaison fiches et long-list, lignes éligibles des groupes écartés.

## 1. Échantillon

- D'office (34) :
  - 4 `ecarter` ;
  - 16 `incontournable: oui` ;
  - 14 fiches signalées au journal M05 :
    - éligibilité `a_verifier` : `bancarisation` ;
    - `raccordement: a_etudier` : `hausse_loyers`, `part_modale_transports_collectifs`, `usage_internet` (et `exposition_pm25`, déjà comptée) ;
    - hors long-list : `preoccupation_logement`, `connaissance_personne_sdf`, `duree_trajet_domicile_travail` ;
    - sens à confirmer : `prix_logements_revenu`, `administration_en_ligne` ;
    - valeurs non relues : `acces_internet_domicile`, `haut_debit_domicile`, `poids_logement_revenu` (et `pollution_quartier`, déjà comptée) ;
    - rattachement à trancher : `conformite_assainissement_collectif` ;
    - périmètre à documenter : `conformite_eau_physicochimique`.
- Tirage : 20 % des 24 « autres » fiches (ni `ecarter` ni incontournables) = 4,8, arrondi à 5, tirées parmi les 10 qui n'étaient pas retenues d'office. `random.Random(20261014).sample(pool, 5)`, `pool` = liste triée `['charge_logement_lourde', 'conformite_eau_microbiologique', 'couverture_fibre', 'incapacite_chauffer', 'logement_trop_sombre', 'logements_sociaux', 'nuisances_sonores', 'privation_internet', 'surcharge_couts_logement', 'taux_effort_logement']`, **graine 20261014**. Fiches tirées : `couverture_fibre`, `incapacite_chauffer`, `nuisances_sonores`, `surcharge_couts_logement`, `taux_effort_logement`.
- Les 5 restantes ont été vérifiées à la source elles aussi : **44 fiches sur 44**.

## 2. Vérifications à la source (WebFetch, 16/10/2026)

Aucun refus HTTP 429 d'Eurostat pendant la session (requêtes espacées, intercalées avec la BDM).

| Source | Lu | Constat |
|---|---|---|
| BDM 001791247, 010595400, 010595405, 010596094, 001779870 | séries complètes | propriétaires 50,6 (1982) … 57,3 (2026, `P`) ; assainissement collectif 80,0 (2010) … 91,9 (2022), rien après 2022 ; non collectif 40,8 … 64,5 (2023) ; bancarisation 5 points ; logements sociaux 699 → 787 |
| Eurostat `ilc_lvho50a` | 2004-2025 | 37,8 → 40,4 ; `b` 2020 et 2022 |
| BDM 010751584, 010751585, 010596142, 010600314, 010600312, 010596095 | séries complètes | parts modales INSEE (FM) ; surpeuplement INSEE : 2013 et 2020 seulement ; eau non conforme (unité `POURCENT_PRELEVT`) ; chauffage INSEE 2010-2024 |
| Eurostat `sdg_06_20` | 2001-2024 | 19 valeurs, rien de 2005 à 2009 ; libellé de `WWT_GE2` : « urbaines, individuelles (autonomes) et autres - avec au moins un traitement secondaire » |
| BDM 010596140, 010596141, 010594684, 011815635, 010596138 | séries complètes | PM10 INSEE ; haut débit ODD 64,4 → 89,9 ; IPC des loyers base 2025, 1996-2025 |
| Eurostat `ilc_mddw02` | 2004-2023 | 18 points ; `b` 2020 ; 16,0 (2023) |
| BDM 001718270 (depuis 2024-01) | mensuel | cumul sur douze mois, `FR-D976`, 263 000 en décembre 2025 |
| Eurostat `ilc_mdho01`, `ilc_mdho06a`, `ilc_mdho05`, `ilc_mdho04`, `ilc_mddw01`, `ilc_mded04` | 2004-2023 | 18 points chacun, `b` 2020, rien en 2021-2022 et 2024-2025 : module triennal confirmé |
| DiDo SDES, ITDD France entière (305ea0e3, CSV) | variables demandées | `med_dist_min_hp` actifs 12/12/13, navetteurs 18/19/19 ; `med_dist_km` 7,5/7,9/8,4 et 14,2/14,6/14,9 (2011, 2016, 2022) ; conformité microbiologique 99 (2008) … 97,9 (2024) ; physico-chimique 98,7 (2008) … 95,3 (2024) |
| Eurostat `ilc_lvho05a`, `ilc_lvho07a`, `ilc_lvho08a`, `ilc_lvho03`, `ilc_mdes01`, `ilc_mddu07a` | 2004-2025 (2014-2025) | valeurs des fiches exactes ; 2021 absente pour la surcharge et le taux d'effort ; `b` 2020 et 2022 |
| OCDE *How's Life? 2020*, chapitre 6 (après recherche web) | page | surcharge : « households in the bottom 40% … more than 40% » ; accès à internet : haut débit d'au moins 256 kbit/s |
| Eurostat `isoc_ci_in_h`, `isoc_ci_ifp_iu`, `isoc_cbt`, `isoc_ciegi_ac` (I_IUGOV12) | séries complètes | aucun drapeau ; accès 2005 et 2020 absentes ; usage 2020 absente ; fibre 2013-2025 complète ; administration en ligne « jusqu'en 2021 » (80,66 %) |
| Eurostat `tran_hv_psmod` | 1990-2024 | 99,1 (2010, `e`), 99,2 (2011, `e`), 99,1 (2012), 15,6 (2013, `b`) |
| Eurostat `sdg_11_50` | — | erreur client. DB.nomics (après recherche web) : dernière mise à jour le 8/2/2021, données jusqu'en 2019 : non éligible |
| Eurostat `tipsho60`, `prc_hicp_aind` (CP041), `ilc_mddu03` | séries complètes | prix sur revenu exact ; IPCH « n'est plus actualisé, remplacé par prc_hicp_ainr » ; privation d'ordinateur 10,5 (2004) → 3,5 (2025), `b` 2020 et 2022 |

**Non lus** :
- PDF des définitions de How's Life (robots.txt) ;
- métadonnées INSEE ODD 8.i7 (erreur serveur) ;
- Melodi (non tenté : refusé par robots.txt selon M05 et M06 `travail`) ;
- API SDMX de l'OCDE (non tentée).

Les années du fichier ITDD ont été attribuées par position de colonne (colonnes `A2025` à `A1982`). Les nombres de valeurs distinctes concordent avec l'extrait du robot : 9 en microbiologie, 14 en physico-chimie et 2 pour les durées, ce qui valide l'attribution.

Fichiers du dépôt lus (aucune valeur saisie) :
- `sdes__air_*.csv` et extrait/fixture DiDo de l'exposition aux PM2,5 ;
- extrait Banque mondiale `EN.ATM.PM25.MC.M3` (valeurs 1995-2023 relues) ;
- `ocde__odd_11.csv`, `ocde__hsl_bien_etre_actuel.csv`, libellés How's Life FR/EN ;
- distributions, couverture, dictionnaires et tableaux simplifiés 2025 du baromètre DREES ;
- `sdes__itdd_france_entiere.csv`, `sdes__dido_catalogue.csv` ;
- `insee_melodi_catalogue.csv` (libellés de `EGOV_12MOIS`, `HAUT_DEBIT`, `_DEP_LOGT_REVENU`) ;
- `insee_bdm_catalogue_non.csv.gz` (motifs d'exclusion de 011815635 et 010567058) ;
- `eurostat_jeux_catalogue.csv` (jeux EU-SILC modulaires `ilc_hcm*`, `ilc_ats*`, `ilc_lvhe*`, `ilc_lvho31`).

## 3. Contrôles par script (hors dépôt)

- **Fiches et long-list** (périodes, points, zone, éligibilité, URL d'API des 41 séries principales issues d'une long-list) : aucun écart.
- **Unicité des `serie_id` de variantes (D36)** : aucun doublon.
- **Recalcul DREES OG04_1** (modalités 1 + 2, NSP au dénominateur) : 66,23 (2014), 62,10 (2015), 59,89 (2018), 54,01 (2020), 53,86 (2022), 56,77 (2023), 55,36 (2025). Les tableaux publiés de 2025 donnent 55,35 % : recoupement exact. SDPROXIM_3 est absent des tableaux publiés et des distributions.
- **IPC INSEE 011815635** : taux recalculés −0,12 (2000), 3,60 (2005), 1,60 (2010), −0,27 (2018), 2,13 (2023), 2,32 (2025), identiques à l'IPCH au dixième.
- **Renvois croisés (D38 a)** :
  - lignes reçues : 38, 40, 45, 11 et 1 reprises (`democratie`, `liens_bien_etre`, `niveau_de_vie`, `planete`, `sante`) ; **28 orphelines** de `education` (règle 120) ;
  - lignes envoyées et non reprises : `planete` 22 sur 23, `education` 93, `travail` 7, `niveau_de_vie` 2, `egalites` 1 ; `sante` 20 sur 20 reprises ;
  - **double décision** : `estat-052758` et `estat-052759` sont `fiche` ou `variante_de` ici et `ecarte_en_bloc` dans `education` (règle 1010).
- **Recouvrement inter-dimensions** (identifiants, séries principales, composantes, variantes, lignes) contre 371 fiches : aucun.
- **Groupes écartés en bloc** : les lignes éligibles des groupes de structure du parc, d'usages en ligne, de population, de montants et de couverture par technologie ont été relues ; aucune exclusion abusive.
- **Recherche d'oublis** :
  - `ilc_pw01b`, `ilc_pw05b` (logement, espaces verts : 2013 seulement) ;
  - `ilc_hcmp03`, `ilc_hcmp06`, `ilc_hcmh02` (2012) ; `ilc_lvho31` et `ilc_lvhe*` (2023) ; `ilc_atst*` (2024) ;
  - `sdg_11_50` (arrêté) ;
  - variables ITDD (rien d'autre d'éligible) ;
  - questions du baromètre DREES (OG04_1, SDPROXIM_3, LO10, LO11, HA04, SA09).
  
  Seul O1 (`ilc_mddu03`, renvoyé par `education`) est retenu.

## 4. Bilan

- 44 fiches auditées : 25 `conforme`, dont 3 avec réserve (séries Melodi non lues), et 19 `a_corriger` : 3 F, 12 A, 4 C, avec 2 J associés. Aucune `non_verifiable`.
- 1 oubli (O1 : 28 lignes orphelines), 7 points de cohérence inter-dimensions, 7 désaccords de jugement.
- Avis : `corrections_necessaires`. Les corrections bloquantes sont l'assainissement (D39), les lignes orphelines (D38 a), les incontournables (D38 d) et les séries DREES (D34, D38 b). Le changement de série principale des loyers est recommandé.
- Rapport copié dans le Projet claude.ai : `claude/cr/M06_logement_cadre_vie_audit.md`.
