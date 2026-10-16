# Compte rendu — M05, fiches indicateurs de la dimension `logement_cadre_vie`

Mission M05 (Logement et cadre de vie), commencée le 14/10/2026 par un premier agent (règles, 38 fiches, tableau : commit `c451041`), interrompue avant le journal et le compte rendu, reprise et terminée le 15/10/2026. Branche `m05-logement_cadre_vie`, méthode commune `docs/methodo/33_methode_fiches_M05.md` v1.2 sans modification des scripts communs. Détail : `docs/cr/M05_logement_cadre_vie_journal.md`.

## 1. Livrables

| Fichier | Contenu |
|---|---|
| `docs/validation/regles_preselection_logement_cadre_vie.csv` | 142 règles ordonnées (dont 3 `hors_longlist`) |
| `docs/validation/preselection_logement_cadre_vie.csv`, `preselection_logement_cadre_vie_lignes.csv` | 142 groupes ; 1 664 lignes affectées (les 1 527 de la long-list, 0 sans règle, + 137 importées de `democratie`, `education`, `liens_bien_etre`, `niveau_de_vie`, `planete`, `sante`) |
| `indicateurs/logement_cadre_vie/*.yaml` | 44 fiches (schéma étendu, `socle_v1` vide), 497 variantes |
| `docs/validation/validation_logement_cadre_vie.csv` | tableau de validation à 18 colonnes, `decision_leo` vide |
| `docs/cr/maintenance_catalogues.md` | signalements LOG-1 à LOG-11 (`a_faire`), à renuméroter à la fusion (D33) |
| `docs/cr/M05_logement_cadre_vie_journal.md` | méthode reconstituée, reprise, vérifications à la source |

Contrôles : `verifier_fiches.py --dimension logement_cadre_vie` → **0 erreur**, 3 avertissements attendus (séries principales hors catalogue des 3 fiches hors long-list, preuves du robot) ; `pytest` : 398 réussis.

## 2. Chiffres (avant l'audit ; chiffres à jour au §9)

- **Long-list** : 1 527 lignes (1 255 éligibles, 53 à vérifier, 219 non éligibles). Décisions : 35 `fiche`, 452 `variante_de`, 894 `ecarte_en_bloc` (dont 230 croisements de ventilations des enquêtes TIC, 225 usages en ligne sans sens normatif, 70 comptes nationaux du logement), 146 `autre_dimension` (`education` 93, `planete` 23, `sante` 20, `travail` 7, `niveau_de_vie` 2, `egalites` 1). Lignes importées : 137 (6 `fiche`, 25 `variante_de`, 106 `ecarte_en_bloc`), dont les 134 lignes que les présélections déjà faites renvoient ici.
- **44 fiches, 33 familles : 30 `retenir`, 10 `retenir_variante`, 4 `ecarter`** (`sous_occupation`, `logements_commences`, `proprietaires_occupants`, `raccordement_traitement_eaux_usees`, toutes pour sens ambigu).
- **5 déclaratives** (charge ressentie du coût du logement, logement trop sombre, bruit, pollution du quartier, préoccupation pour le logement) ; **0 composite** ; **1 à vérifier** (D17 : `bancarisation`, 5 points) ; **3 hors long-list** (`preoccupation_logement`, `connaissance_personne_sdf`, `duree_trajet_domicile_travail`) ; **3 indicateurs de moyens** (`logements_sociaux`, `couverture_fibre`, `logements_commences`).
- **Incontournables** (crosswalk §5) : surpeuplement et qualité du logement, pollution de l'air locale — **tous présents et retenus** (16 fiches `incontournable: oui` ; principales `surpeuplement`, `logement_humide`, `sans_installations_sanitaires`, `privation_severe_logement`, `exposition_pm25`, `concentration_pm10`, `concentration_no2`, `depassement_norme_ozone`, `pollution_quartier`).
- Sous-thèmes : qualité de l'air 9 fiches ; coût du logement 8 ; surpeuplement et qualité 8 ; numérique 6 ; eau et assainissement 4 ; transports et services 3 ; accès au logement et sans-abrisme 3 ; nuisances 2 ; précarité énergétique 1.

## 3. Travail de la reprise (15/10/2026)

1. **Vérification à la source** de 17 séries principales (API Eurostat, BDM) : valeurs et drapeaux écrits dans les notes ; 5 pages Eurostat refusées par le proxy (HTTP 429), dont 3 lues sur la table ODD de même définition.
2. **Module triennal d'EU-SILC** : depuis 2021, défauts du logement, nuisances et charge ressentie ne sont plus collectés chaque année (valeurs 2004-2020 puis 2023 ; vagues 2023 et 2026) : 7 fiches passent en `frequence: irreguliere` (D17).
3. **Deux anomalies de source** : `tran_hv_psmod` publie 99,1 / 99,2 / 99,1 % de part des transports collectifs en 2010-2012 (remplaçables par la somme des séries INSEE, 16,7 / 17,0 / 16,2) ; `prc_hicp_aind` (loyers) n'est plus mis à jour, remplacé par `prc_hicp_ainr` dont les loyers ne sont pas catalogués.
4. **6 fiches ajoutées** : `preoccupation_logement` (DREES OG04_1, 2014-2025), `connaissance_personne_sdf` (DREES SDPROXIM_3, 2000-2025, valeurs à calculer : seule approche annuelle du sans-abrisme), `duree_trajet_domicile_travail` (ITDD, recensement 2011-2016-2022), `proprietaires_occupants` (écartée, sens ambigu), `conformite_assainissement_collectif` et `raccordement_traitement_eaux_usees` (lignes renvoyées entre `planete` et cette dimension).
5. **12 variantes hors long-list ajoutées** (ITDD, OCDE, catalogues des séries écartées de l'INSEE ; 20 au total avec les 8 séries SDES de l'air du premier agent) ; `pollution_quartier` passe `incontournable: oui` ; correction d'une affirmation fausse (« indice des prix des logements anciens non catalogué » : il est au catalogue des séries écartées, à tort).

## 4. Points délicats et choix faits

1. **Assainissement** : `planete` (fusionné) renvoyait ici ce que la première version de cette présélection lui renvoyait ; le concept n'avait de fiche nulle part. Fiches créées ici, `rattachement_propose` vers `planete` (R2 : pression sur les milieux aquatiques).
2. **Sans-abrisme** : aucune statistique annuelle du nombre de personnes sans domicile n'existe au format admis (D09) ; la seule série est indirecte (part des personnes qui connaissent une personne SDF, baromètre DREES), retenue sous réserve du calcul et avec un sens à confirmer.
3. **EU-SILC d'Eurostat principal** pour les conditions de logement (l'INSEE ne publie pas les niveaux par API, D35) ; les séries INSEE (ODD, SRCV, recensement) sont en variantes.
4. **Familles de la qualité de l'air** par polluant (concentration et dépassement de norme substituables) ; PM2,5 : indicateur réglementaire d'exposition du SDES (2011-2024, objectifs 2020-2030) principal, série modélisée de la Banque mondiale en variante pour 2000-2010.
5. **Rattachements reçus** : administration en ligne (D33), bancarisation (accès aux services, proposé par `niveau_de_vie`), poids du logement dans le revenu, privation sévère liée au logement, pollution du quartier : `rattachement_propose` dans les fiches.

## 5. À faire vérifier par Léo

1. Sens de `prix_logements_revenu` (bas = accessibilité de l'achat), de `administration_en_ligne` (haut) et de `connaissance_personne_sdf` (bas, indicateur indirect).
2. Écarts pour sens ambigu : `proprietaires_occupants`, `sous_occupation`, `logements_commences`, `raccordement_traitement_eaux_usees`.
3. Indicateurs presque saturés ou presque constants gardés (D34) : `sans_installations_sanitaires`, `bancarisation`, `usage_internet`, `couverture_fibre`, `pieces_par_personne`, `population_exposee_pm25`.
4. Choix du socle : `privation_severe_logement` **ou** ses composantes (redondance).

## 6. Signalements (`docs/cr/maintenance_catalogues.md`, LOG-1 à LOG-11)

DREES OG04_1 et SDPROXIM_3 à cataloguer et calculer (LOG-1) ; séries SDES de l'air extraites mais non cataloguées (LOG-2) ; seuil de l'indicateur OCDE 9_2 (LOG-3) ; indices des prix des logements INSEE écartés à tort et série BCE RPP (LOG-4) ; variables ITDD et OCDE ODD 11 (LOG-5) ; relais de `prc_hicp_aind` (LOG-6) ; valeurs aberrantes de `tran_hv_psmod` (LOG-7) ; fréquence des items du module triennal EU-SILC (LOG-8) ; exceptions de la table de correspondance (LOG-9) ; libellé tronqué de m04-000126 (LOG-10) ; sources non cataloguées du logement (LOG-11).

## 7. Questions pour la session mère

1. Trancher le rattachement de l'**assainissement** (`planete` ou `logement_cadre_vie`) : les deux présélections se le renvoyaient.
2. Consigne aux agents `education` et `sante` en cours : marquer `autre_dimension:logement_cadre_vie` les lignes IPCH des loyers (`prc_hicp_aind` CP041, CP0411) et ODD 7.i1 (melodi-005545), utilisées ici.
3. Faire calculer par le robot M04 SDPROXIM_3 (LOG-1) avant le gel 2, faute de quoi la seule mesure du sans-abrisme reste sans valeurs.
4. Valider le passage en `frequence: irreguliere` des items EU-SILC du module triennal (et l'appliquer aux fiches des autres dimensions qui en utilisent, par exemple `securite/delinquance_quartier`, `ilc_mddw03`).

## 8. Pull request

PR #26 vers `main` « M05 — fiches indicateurs : logement_cadre_vie » (https://github.com/leomalherbe/prosperite/pull/26), ouverte le 15/10/2026 par l'API GitHub ; à ne pas fusionner pendant un run du robot (D26).

## 9. Corrections après audit (M06, D38-D46) — branche `m05-logement_cadre_vie-corr`, PR #PR_NUM

Audit : `docs/validation/audit_logement_cadre_vie.md` (44 fiches auditées : 25 conformes, 19 à corriger ; 1 oubli de 28 lignes ; 7 points de cohérence ; 7 désaccords de jugement ; 11 corrections au §12), réponses de la session mère en D42. Toutes les corrections F, A et C sont appliquées ; J3 et J5 suivent D42 ; J6 et J7, non tranchés, restent en question. Deux collectes ciblées du robot (vagues 15 et 16, 16/10/2026) ont calculé la distribution de SDPROXIM_3 et lu les trois séries Melodi. Détail, fichiers et limites : `docs/cr/M05_logement_cadre_vie_corrections_journal.md`.

| Fiche | Correction |
|---|---|
| `conformite_assainissement_collectif`, `raccordement_traitement_eaux_usees` (D39, D42) | **transférées dans `planete`** (fiches créées dans `indicateurs/planete/`, règles et tableau de `planete` mis à jour, `socle_propose: non`) ; sens ambigu du raccordement confirmé par `env_ww_con` (part collectée fixée à 82 %, assainissement individuel jamais compté) |
| `privation_ordinateur` (nouvelle, O1) | `ilc_mddu03` (2004-2025 : 10,5 % → 2,2 % en 2015 → 3,5 % en 2025), `retenir_variante` dans la famille `privation_internet`, 15 ventilations en variantes (lignes renvoyées par `education`) |
| `hausse_loyers` (D42) | IPC des loyers de l'INSEE (BDM 011815635, 1996-2025) en principale, taux nominal calculé (`composantes`, `formule`), recoupé sur neuf années avec l'IPCH, passé en variante |
| `preoccupation_logement`, `connaissance_personne_sdf` (D34, D38 b, D42) | `composantes`, `formule`, `non_recoupe` ; préoccupation recoupée en 2025 (55,35 %) ; connaître une personne SDF : valeurs calculées (9,18 % en 2000, 15,97 % en 2008, 9,33 % en 2025), famille propre, `retenir`, déclaratif, plausibilité contre l'enquête Sans-domicile de l'INSEE |
| 9 fiches de l'air et de la qualité du logement (D38 d, D42) | `incontournable: non` sur les 7 non principales et sur les familles NO2 et ozone : 7 incontournables, tous principaux |
| eau du robinet, surcharge (F1, F2) | variantes INSEE « autre statistique, définition à documenter » ; creux de 2016, chute de 2024 ; OCDE 3_3 = 40 % les plus modestes |
| `pollution_quartier`, `acces_internet_domicile`, `duree_trajet_domicile_travail`, `sous_occupation`, 3 fiches EU-SILC (C) | valeurs, drapeaux et sous-champs lus ; drapeaux « non lus » retirés |
| `administration_en_ligne`, `haut_debit_domicile`, `poids_logement_revenu` | valeurs Melodi lues par le robot (vague 16) |
| `privation_severe_logement`, `haut_debit_domicile`, `hausse_loyers` | lignes renvoyées en variantes (`ilc_mdho06q`, `isoc_r_broad_h`, IPCH) |

Lignes renvoyées (D38 a, D46) : les 164 lignes reçues sont toutes reprises (dont les 28 d'`education` sur l'accès au numérique, les 2 lignes IPCH des loyers, les 2 lignes `ilc_mdho06q` de `niveau_de_vie`, la ligne ODD 7.i1 de `sante`) ; les lignes envoyées portent un motif et sont reprises par `planete` (27), `sante` (20), `education` (93, écartées), `travail` (7), `niveau_de_vie` (2) ; restent à reprendre : 1 ligne par `egalites` (OCDE 10_3_1) et 9 lignes par `democratie` (participation et expression politiques en ligne, nouvelle règle 1475, D39, qui corrige aussi la contradiction sur les deux lignes `I_IUVOTE` retenues par `democratie` et écartées ici).

Socle proposé (D41, `socle_propose: oui`, 8 fiches) : `surcharge_couts_logement` (coût), `surpeuplement` et `logement_humide` (qualité et surpeuplement), `incapacite_chauffer` (précarité énergétique), `exposition_pm25` et `pollution_quartier` (environnement local subi), `part_modale_transports_collectifs` (services et transports), `acces_internet_domicile` (numérique). Trois incontournables restent hors du socle proposé (`concentration_pm10`, `privation_severe_logement`, `sans_installations_sanitaires`) : question à la session mère.

Chiffres après corrections : **43 fiches, 32 familles : 29 `retenir`, 11 `retenir_variante`, 3 `ecarter`** (`sous_occupation`, `logements_commences`, `proprietaires_occupants`) ; 6 déclaratives ; 0 composite ; 1 « à vérifier » ; 4 hors long-list ; 7 incontournables ; 510 variantes ; 40 résultats, 3 moyens. Présélection : 144 groupes (43 `fiche`, 61 `variante_de`, 28 `ecarte_en_bloc`, 12 `autre_dimension`) ; 1 691 lignes, dont 164 importées ; 161 lignes renvoyées. `planete` : 78 fiches, 66 familles. Vérificateur : 0 erreur pour les deux dimensions, avertissements attendus (`socle_propose` hors schéma tant que le vérificateur v1.3 n'est pas fusionné ; séries hors catalogue avec preuve) ; `pytest` : 403 réussis. Classeur Excel non généré (session mère).

Liste de maintenance : LOG-1, LOG-5, LOG-6, LOG-9 mises à jour (`docs/cr/maintenance_catalogues.md`) ; LOG-12 (`env_ww_con` : libellé, traitement tertiaire), LOG-13 (libellé de `ilc_mdho06q`), LOG-14 (définition de l'OCDE 3_3) dans `docs/cr/maintenance_catalogues_logement_cadre_vie.md`.

Réponses aux questions du §7 : 1. assainissement → `planete` (D39, D42) ; 2. loyers renvoyés par `education` (règle 1005) et ODD 7.i1 par `sante` ; 3. SDPROXIM_3 calculé (vague 15) ; 4. module triennal en `irreguliere` (D38 e), à appliquer par `securite` à `delinquance_quartier` (D42).

À trancher : **session mère** — incontournables hors du socle proposé (conflit avec le vérificateur v1.3) ; privation d'ordinateur en variante ou en famille propre ; J6 (`population_exposee_pm25`) et J7 (type de `logements_commences`) ; reprise des 9 lignes de participation politique en ligne par `democratie` ; numéros des vagues 15 et 16 du robot. **Léo** — « connaître une personne SDF » comme seul indicateur du sans-abrisme (D42) ; sens de `prix_logements_revenu` et d'`administration_en_ligne` ; hausse des loyers en taux nominal (bornes à indexer sur l'inflation) ; chute de 2024 de la conformité physico-chimique de l'eau ; choix entre `privation_severe_logement` et ses composantes au socle.
