# Journal — M05 transversal, préparation du gel 2

Agent transversal (session lancée par la session mère), 17 octobre 2026. Branche `m05-transversal-gel2`, reprise d'un agent précédent interrompu (16/10) puis fusionnée avec `main` (corrections `logement_cadre_vie`, PR #35 ; journal D47). Décisions appliquées : D38, D41 à D47 ; méthode `docs/methodo/33_methode_fiches_M05.md` passée en v1.3 sur cette branche.

## 1. Mise en route

- `git checkout -B m05-transversal-gel2 origin/m05-transversal-gel2 && git merge origin/main` : conflit sur `docs/validation/validation_planete.csv` (main y avait les deux fiches d'assainissement transférées par `logement_cadre_vie`, au format v1.2). Résolu en partant de la version de la branche (aucune décision de Léo des deux côtés) puis en régénérant le tableau avec `python scripts/verifier_fiches.py --dimension planete --tableau` (78 fiches) ; commit `f9f895c`. Second `git merge origin/main` (journal D47, point de reprise du 17/10) sans conflit : `a263eae`. Troisième fusion en fin de travail (`d7e821a`) : `egalites` figée par Léo (D48, 9 décisions importées dans le tableau v1.2 de main) ; conflit sur `validation_egalites.csv` résolu en partant de la version de main puis en régénérant le tableau (décisions conservées), et D48 appliquée aux fiches (§3 bis).
- État de départ : `python -m pytest -q` → 431 tests réussis ; vérificateur à **0 erreur** sur les 10 dimensions ; `--lignes-renvoyees` → **606 lignes orphelines** (`egalites` 572, `securite` 21, `democratie` 9, `liens_bien_etre` 4) ; deux renvois **hors long-list** de `sante` (règles 1020 et 1030, sans ligne) que le rapport ne suivait pas ; trois tableaux encore au format v1.2 (`logement_cadre_vie`, `sante`, `education`) ; six incontournables hors du socle sans dérogation écrite (avertissements) ; trois identifiants DREES de `sante` à l'ancienne forme (D45).

## 2. Ce qui était fait par l'agent précédent (d'après `git log origin/main..HEAD`)

| Commit | Contenu |
|---|---|
| `5ca5c42` | Vérificateur et classeur v1.3 : `socle_propose` obligatoire avec `derogation_socle` (D41), plafond de 8, incontournable sur la seule principale (D38 d) ; rapport `--lignes-renvoyees` par couple, avertissements des lignes orphelines et des lignes retenues et écartées (D46) ; reconnaissance des anciens identifiants DREES (D45) ; tableau à 20 colonnes, réécriture qui conserve les décisions de Léo et refuse d'en perdre ; classeur : défaut `retenu_socle` = `socle_propose: oui`, feuille « Synthèse » par sous-thème, reprise d'un classeur non importé. Tests `tests/test_verifier_fiches.py` et `tests/test_classeur_validation.py`. |
| `25bf088` | D45 : 17 identifiants DREES du catalogue M04 et des long-lists alignés sur la pièce jointe unique `barometre2000_2025_diff_csv`. |
| `075b3ed` | `socle_propose` posé sur les 7 dimensions corrigées en premier ; `democratie` et `liens_bien_etre` : socle validé par Léo, dérogations écrites (`citoyennete_active`, `democratie_liberale_vdem`, `participation_en_ligne`) ; D38 c (`coefficient_inegalite_humaine` en `retenir_variante`) ; D38 d ; D42 (`delinquance_quartier` irrégulière) ; D43 (GALI déclaratif) ; D45 (fiches DREES, variante Eurostat 2008-2014 des accidents mortels du travail, `lfsa_ugadra` écarté) ; tableaux régénérés. |
| `fe68d93`, `92092e4` | Premier essai antérieur aux décisions de Léo et aux fusions `sante` et `education`, remplacé (fusion « ours », aucun fichier repris). |

La méthode 33 n'avait pas été passée en v1.3 : fait ici (§5).

## 3. Socle proposé par dimension (D41, contrôle D)

Toutes les fiches des 10 dimensions portent `socle_propose` ; `oui` seulement sur des principales `retenir` ; au plus 8 par dimension ; aucun `incontournable: oui` hors d'une principale ; `democratie` et `liens_bien_etre` : socle = exactement le socle validé par Léo (D47).

| Dimension | Fiche au socle | Motif (une ligne) |
|---|---|---|
| niveau_de_vie | `niveau_vie_median` | incontournable ; revenus et pouvoir d'achat |
| | `revenu_disponible_ajuste_habitant` | incontournable ; revenus (comptes nationaux) |
| | `taux_pauvrete_60` | incontournable ; pauvreté monétaire |
| | `privation_materielle_sociale` | incontournable ; privations |
| | `privation_alimentaire` | accès à l'alimentation (A2) |
| | `patrimoine_net_median` | patrimoine des ménages |
| travail | `taux_emploi` | incontournable ; emploi et chômage |
| | `longues_durees_travail` | incontournable ; conditions et santé au travail (D27) |
| | `bas_salaires` | qualité et sécurité de l'emploi (rémunération, D36) |
| | `satisfaction_travail` | satisfaction au travail |
| logement_cadre_vie | `surpeuplement`, `logement_humide` | incontournables ; qualité et surpeuplement |
| | `exposition_pm25`, `pollution_quartier` | incontournables ; environnement local subi (D42) |
| | `surcharge_couts_logement` | coût du logement |
| | `incapacite_chauffer` | précarité énergétique (A3) |
| | `part_modale_transports_collectifs` | transports et services |
| | `acces_internet_domicile` | numérique (A7) |
| sante | `esperance_vie_naissance`, `esperance_vie_sans_incapacite` | incontournables ; espérance de vie |
| | `sante_percue_bonne`, `maladie_chronique`, `limitations_activite` | incontournables ; santé perçue, chronicité, limitations |
| | `episodes_depressifs` | incontournable (D43) ; santé mentale |
| | `besoins_soins_non_satisfaits` | accès aux soins |
| | `tabagisme_quotidien` | comportements (13 vagues, premier facteur de risque) |
| education | `sorties_precoces` | incontournable ; diplômes et sorties précoces (D44) |
| | `pisa_eleves_difficulte_lecture`, `pisa_eleves_difficulte_mathematiques` | incontournables ; compétences des élèves |
| | `piaac_litteratie` | incontournable ; compétences des adultes |
| | `competences_numeriques_base` | compétences numériques (A7) |
| | `formation_adultes_12_mois` | formation des adultes (D44) |
| | `accueil_formel_moins_3_ans` | petite enfance |
| | `effort_recherche_pib` | recherche (A5) |
| liens_bien_etre | `satisfaction_vie`, `soutien_social`, `cohesion_sociale_percue`, `optimisme_avenir_personnel` | socle validé par Léo (D47) |
| securite | `homicides` | incontournable ; atteintes aux personnes et aux biens |
| | `delinquance_quartier`, `securite_nuit` | incontournables ; sentiment d'insécurité |
| | `depense_imprevue`, `pauvrete_actifs_liquides` | incontournables ; sécurité économique |
| | `tues_route` | sécurité routière (A6) |
| democratie | `confiance_justice`, `confiance_police`, `etat_de_droit_wgi`, `liberte_presse_rsf`, `participation_presidentielle`, `voix_pouvoirs_publics` | socle validé par Léo (D47) |
| egalites | `gini_niveau_de_vie`, `ecart_salaire_eqtp_fh`, `ecart_revenu_median_origine`, `inegalite_esperance_vie`, `gini_patrimoine` | socle validé par Léo (D48 ; avant : `rapport_s80_s20`, `ecart_emploi_fh`, `ecart_salaire_fh`, `indice_inegalite_genre`, `ecart_emploi_nationalite`, `ecart_reussite_bac_origine_sociale`) |
| planete | `emissions_ges_territoire`, `empreinte_carbone_par_habitant` | incontournables ; climat |
| | `part_energies_renouvelables` | énergie |
| | `artificialisation_sols`, `part_espaces_naturels`, `taux_boisement` | incontournables ; biodiversité, sols, forêts |
| | `taux_recyclage_dechets_municipaux` | pollutions, déchets, matières |

**Dérogations écrites ici** (`derogation_socle`, limite de 8 atteinte, motifs repris des journaux de corrections) : `logement_cadre_vie/concentration_pm10`, `privation_severe_logement`, `sans_installations_sanitaires` ; `education/piaac_numeratie`, `pisa_eleves_difficulte_sciences`, `pisa_eleves_faibles_trois_domaines`. Les avertissements « incontournable hors du socle » disparaissent ; la question posée par les deux correcteurs (appliquer `retenu_socle` à tous les incontournables ?) reste ouverte (§7).

### 3 bis. Application de D48 (`egalites` figée)

- Les trois fiches `retenir_variante` placées au socle par Léo deviennent principales de leur famille (`retenir`) et les anciennes principales passent en `retenir_variante` : `inegalite_revenu` (`gini_niveau_de_vie` ← `rapport_s80_s20`), `ecart_salaire_fh` (`ecart_salaire_eqtp_fh` ← `ecart_salaire_fh`), `ecart_pauvrete_origine` (`ecart_revenu_median_origine` ← `ecart_pauvrete_etrangers`) ; l'incontournable suit la principale (D38 d : `gini_niveau_de_vie`, `ecart_salaire_eqtp_fh`) ; motifs réécrits en citant D48, deux phrases de note corrigées (« principal de la famille »).
- `socle_propose: oui` = exactement les 5 fiches du socle de Léo ; `derogation_socle` (« Décision de Léo au gel 2, classeur retourné le 17/10/2026… ») sur `ecart_emploi_fh` et `indice_inegalite_genre`, incontournables retirés du socle ; `ecart_emploi_nationalite` et `ecart_reussite_bac_origine_sociale` passent en `non`. Contrôle : pour les trois dimensions figées, la décision par défaut du classeur v1.3 coïncide avec chaque décision de Léo et le socle effectif est celui du journal (D47, D48).
- Dimension figée : les deux fiches créées par la reprise des lignes renvoyées (`ecart_pisa_origine_sociale`, `tolerance_minorites_percue`) sont retirées et leurs lignes deviennent des **variantes** (`ecart_reussite_bac_origine_sociale` : 8 lignes PISA par statut socio-économique ; `discriminations_origine_temoins` : série OCDE 10.3.1). Pour une v1.1 d'`egalites` : une fiche d'écart PISA selon l'origine sociale (D34, TRV-1) et une fiche de tolérance perçue envers les minorités (17 points annuels 2007-2023, TRV-2).

Autres contrôles D : `delinquance_quartier` en `frequence: irreguliere` (D42) ; `coefficient_inegalite_humaine` en `retenir_variante`, `composite: oui`, hors socle (D38 c) ; `travail/accidents_travail_mortels_eurostat` : variante 2008-2024 servant à couvrir 2008-2014, `raccordement: a_etudier` vers la série Ameli (D45) ; `lfsa_ugadra` : toutes les lignes en `ecarte_en_bloc` (groupe `travail/chomeurs_indemnisation`, D45) ; GALI `declaratif: oui` partout, `egalites/ecart_emploi_handicap` compris (D43).

## 4. Lignes renvoyées traitées (D46, tâche C)

Les règles de reprise listent les `ligne_id` exacts (aucune ligne affectée ailleurs n'est capturée) et citent le groupe d'origine ; générateur : `tmp/gel2/regles_egalites.py`, `tmp/gel2/ajout_regles.py` (non commités, dossier de travail).

| Origine → destination | Orphelines | Fiche | Variante | Écartées | Règles de la destination |
|---|---|---|---|---|---|
| travail → egalites | 323 | 0 | 43 | 280 | composantes par sexe de `ecart_emploi_fh` (18), `ecart_chomage_fh` (14), `ecart_temps_partiel_fh` (5), `ecart_salaire_eqtp_fh` (4 niveaux de salaire) ; `sdg_05_40` en variante de `ecart_emploi_fh` (2, D39, A4) ; second rang écarté (268 : sexe croisé avec l'âge, le diplôme, la PCS, le temps de travail, D35) ; évolutions et indices de salaire par sexe écartés (12) |
| niveau_de_vie → egalites | 173 | 0 | 8 | 165 | taux de pauvreté par sexe → `ecart_pauvrete_fh` (6), nombres écartés (2) ; `ilc_pnp3` → `revenu_relatif_seniors` (2) ; tranches de revenu `ilc_di20`, `di27`, `di31` (46), ventilations de l'impact des transferts `ilc_li80*` (45) et seuils de quantiles du patrimoine (72) écartés |
| education → egalites | 75 | 0 | 24 | 51 | parts PISA par statut socio-économique (8) → `ecart_reussite_bac_origine_sociale` (dimension figée, D48) ; NEET (5) et sorties précoces (3) par origine → composantes des écarts existants ; très faible intensité de travail des enfants selon le diplôme des parents → `ecart_pauvrete_enfants_education_parents` (6), par âge écartée (6) ; étudiantes en sciences et TIC (supérieur) → `femmes_filieres_scientifiques` (2), autres niveaux écartés (4) ; enseignantes (9), cheffes d'établissement (5), rapport F/H des diplômés (5), PISA BDM non éligibles (8), `ilc_di23` (14) écartés |
| logement_cadre_vie → egalites | 1 | 0 | 1 | 0 | série OCDE 10.3.1 (tolérance perçue envers les minorités) → `discriminations_origine_temoins` (dimension figée, D48) |
| niveau_de_vie → securite | 19 | 2 | 15 | 2 | fiches `charge_remboursement_dettes_lourde` (+5 variantes) et `endettement_menages` (+10 variantes) ; actifs financiers nets des comptes nationaux écartés (2) |
| egalites → securite | 2 | 0 | 0 | 2 | `ilc_li70b` (indemnisation des chômeurs) écarté, comme `lfsa_ugadra` en travail (D39, D45) |
| logement_cadre_vie → democratie | 9 | 0 | 2 | 7 | I_IUCPP (participation civique ou politique en ligne) en variantes de `participation_en_ligne` ; ventilations et séries I_IUPOL non éligibles écartées |
| education → liens_bien_etre | 4 | 0 | 0 | 4 | nombres de monuments et de musées écartés (moyens, non éligibles) |
| **Total** | **606** | **2** | **93** | **511** | |

Renvois **hors long-list** (nouveau suivi du vérificateur) : `sante/deces_chaleur_planete` → fiche `planete/deces_chaleur` (règle 2220) ; `sante/confiance_medecins_democratie` → deux variantes de `democratie/confiance_hopital` (SA13_AB_1, SA13_CD_1 ; règle 209). Signalement TRA-14 de la correction `travail` (OG04_9, sans règle) → fiche `niveau_de_vie/preoccupation_pouvoir_achat` (règle 1410).

Dimensions déjà sans orpheline au départ (rien à reprendre) : `planete` (27 lignes de `logement_cadre_vie`, assainissement compris), `travail` (56 d'`education`, 104 `hsw_*` de `sante`), `niveau_de_vie` (12 `hlth_dm*` de `sante`), `securite` (54 de `sante`), `logement_cadre_vie`, `sante`, `education`.

**Fiches créées** (4 ; deux fiches `egalites` créées d'abord ont été ramenées en variantes après D48, §3 bis) : `securite/charge_remboursement_dettes_lourde` (`retenir`, déclaratif, comme `charge_logement_lourde`) ; `securite/endettement_menages` (`retenir`, type pression, `sens_a_confirmer`) ; `planete/deces_chaleur` (`retenir`, hors long-list, preuve robot vague 13) ; `niveau_de_vie/preoccupation_pouvoir_achat` (`retenir_variante`, D38 b, famille `pauvrete_subjective`).

**Dimensions figées** : `democratie` et `liens_bien_etre` n'ont reçu que des variantes (`participation_en_ligne`, `confiance_hopital`) et des écarts en bloc ; tableaux identiques ligne à ligne, décisions de Léo intactes ; `egalites` (figée en fin de travail) : variantes et écarts en bloc seulement, plus l'application de D48 (§3 bis). Pour une v1.1 de `democratie` : I_IUCPP (participation civique ou politique en ligne, 2013-2025, 9 points, à vérifier) pourrait devenir une fiche ; SA13_AB_4 (confiance dans ce que disent les hommes et femmes politiques en cas de crise sanitaire, 8 vagues 2015-2025, non renvoyée) pourrait compléter la confiance dans les institutions ; I_IUPOL1 (2013-2019) et I_IUPOL2 (2021-2025) seraient à raccorder pour former une série d'expression politique en ligne. Rien pour `liens_bien_etre`.

## 5. Outils et méthode

- **Vérificateur** : `DIMENSIONS_SOCLE_TRANSITOIRE` vidé (logement_cadre_vie fusionnée) ; suivi des **renvois hors long-list** (règle `autre_dimension` + `hors_longlist = oui`) : repris si une règle de la destination cite `<origine>/<groupe>` dans son motif ; avertissement par dimension, section et compteur dans `--lignes-renvoyees`, dernière ligne « N ligne(s) orpheline(s), M renvoi(s) hors long-list non repris, K ligne(s) retenue(s) et écartée(s) ». Tests : `test_renvoi_hors_longlist_repris_par_citation`, transition du socle testée avec `monkeypatch`.
- **Méthode 33 v1.3** : §10 (socle proposé et dimensions figées, lignes renvoyées et renvois hors long-list, règles communes D38 et D42 à D45), schéma (`socle_propose`, `derogation_socle`, `annee_reference`), tableau à 20 colonnes, déroulé (rapport des renvois, classeur), historique des versions (§11).
- **Classeur** : inchangé (v1.3 de l'agent précédent) ; classeurs Excel non générés (session mère).

## 6. Alignements et contrôles finaux

- D45 : identifiants DREES de `sante/limitations_activite`, `sante_percue_bonne` (variantes, présélection `sante` relancée) et `manque_medecins_percu` (série principale et composante) alignés sur la pièce jointe unique ; aucune autre ancienne forme dans `indicateurs/`.
- Tableaux de validation des 10 dimensions régénérés au format v1.3 (`--tableau`) ; `democratie` et `liens_bien_etre` identiques à l'avant, `egalites` porteur des 9 décisions de Léo de main (décisions et commentaires conservés).
- `python -m pytest -q` : **432 réussis**. Vérificateur : **0 erreur** sur les 10 dimensions ; avertissements restants : séries hors catalogue avec preuve ou jeu au catalogue des jeux (« à cataloguer ») et 5 lignes de `niveau_de_vie` déjà séries principales d'écarts d'`egalites` (variantes de `taux_pauvrete_60` et `niveau_vie_median`, R1, antérieures). `--lignes-renvoyees` : **0 orpheline, 0 renvoi hors long-list non repris, 0 ligne retenue et écartée**. `tmp/gel2/controles.py` : aucune série principale (ni composante) partagée entre deux dimensions, aucune ligne « fiche » dans deux dimensions.

| Dimension | Fiches | Familles | retenir | retenir_variante | ecarter | Socle proposé |
|---|---|---|---|---|---|---|
| niveau_de_vie | 28 | 18 | 17 | 10 | 1 | 6 |
| travail | 40 | 31 | 27 | 8 | 5 | 4 |
| logement_cadre_vie | 43 | 32 | 29 | 11 | 3 | 8 |
| sante | 50 | 39 | 38 | 11 | 1 | 8 |
| education | 39 | 24 | 22 | 14 | 3 | 8 |
| liens_bien_etre | 22 | 19 | 18 | 2 | 2 | 4 |
| securite | 35 | 27 | 22 | 4 | 9 | 6 |
| democratie | 35 | 25 | 22 | 10 | 3 | 6 |
| egalites | 57 | 39 | 37 | 17 | 3 | 5 |
| planete | 79 | 67 | 63 | 10 | 6 | 7 |

Maintenance : `docs/cr/maintenance_catalogues_transversal.md` (TRV-1 valeurs PISA par statut socio-économique ; TRV-2 origine et licence de la série OCDE 10.3.1 ; TRV-3 dénominateur d'`ilc_mded05` ; TRV-4 suivi de SAN-10, SAN-11, TRA-14).

## 7. Questions pour la session mère

1. Incontournables hors socle (`logement_cadre_vie` 3, `education` 3, dérogations écrites) : garder la limite de 8, ou appliquer `retenu_socle` à tous les incontournables ?
2. `planete` : le sous-thème « aléas et adaptation » n'a pas de fiche au socle (7 sur 8) ; proposer `deces_chaleur` (ou `jours_canicule`) comme huitième ?
3. `travail` : socle de 4 fiches, le taux de chômage (`retenir`, non incontournable) n'y est pas ; l'ajouter ?
4. `securite/endettement_menages` : sens « bas » (OCDE, vulnérabilité) retenu avec `sens_a_confirmer` ; un endettement plus élevé accompagne aussi l'accès à la propriété : le garder au gel 2 ou le passer en `sens: ambigu` ?
5. `sdg_05_40` (inactivité pour responsabilités familiales) gardé en variante de `ecart_emploi_fh` (A4 : conciliation des temps hors v1) plutôt qu'en fiche : à confirmer.
6. Dépôt dans le Projet claude.ai (`claude/cr/M05_transversal_gel2_journal.md`, `claude/40_validation_<dim>.csv` pour les 10 dimensions, toutes au format v1.3) : l'outil Projects n'est pas disponible dans cette session d'agent ; à faire par la session mère.
7. D48 appliquée aux fiches `egalites` sur cette branche (échange de trois principales, incontournable reporté, socle de Léo, deux dérogations, deux fiches nouvelles ramenées en variantes, §3 bis) : à confirmer avant fusion.
