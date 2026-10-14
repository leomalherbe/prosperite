# Compte rendu — M05, fiches indicateurs de la dimension `liens_bien_etre` (mission pilote)

Agent de mission M05, 14 octobre 2026 (mis à jour après les décisions de la session mère du même jour, §8). Branche `m05-liens_bien_etre`, pull request « M05 — fiches indicateurs : liens_bien_etre (pilote) ». Méthode détaillée et chiffres : `docs/cr/M05_liens_bien_etre_journal.md`.

## 1. Fait

| Livrable | Fichier |
|---|---|
| Règles de présélection (67 règles ordonnées) | `docs/validation/regles_preselection_liens_bien_etre.csv` |
| Tableau de présélection (une ligne par concept) | `docs/validation/preselection_liens_bien_etre.csv` |
| Affectation ligne à ligne (685 lignes) | `docs/validation/preselection_liens_bien_etre_lignes.csv` |
| 21 fiches YAML | `indicateurs/liens_bien_etre/*.yaml` |
| Tableau de validation (21 lignes, colonnes `sens` et `unite` incluses, `decision_leo` et `commentaire_leo` vides) | `docs/validation/validation_liens_bien_etre.csv` (copie Projet : `claude/40_validation_liens_bien_etre.csv`) |
| Script générique de présélection (règles → présélection, injection des variantes dans les fiches) | `scripts/preselection.py` |
| Vérificateur générique des fiches (schéma, familles, catalogues, couverture, tableau ; écrit le tableau) | `scripts/verifier_fiches.py` |
| Tests hors ligne (22) | `tests/test_verifier_fiches.py` — suite complète : 394 réussis |
| Journal de bord (méthode pilote) | `docs/cr/M05_liens_bien_etre_journal.md` |
| Méthode commune des fiches (adoptée pour les dix dimensions) | `docs/methodo/33_methode_fiches_M05.md` |

## 2. Chiffres

- Long-list : 668 lignes, toutes affectées ; 17 lignes de la long-list `travail` importées (rattachement proposé).
- Présélection : 67 concepts — 21 `fiche`, 34 `variante_de`, 10 `ecarte_en_bloc` (160 lignes, dont 31 non éligibles), 2 `autre_dimension:logement_cadre_vie` (40 lignes non éligibles : satisfaction des domaines « lieu de résidence » et « temps de trajet »).
- Fiches : 21 en 17 familles — **16 `retenir`**, 3 `retenir_variante`, 2 `ecarter`. 14 déclaratives, 0 composite, 7 « à vérifier » (séries irrégulières D17), 1 hors long-list, 2 incontournables présents sur 2 (le troisième concept du crosswalk, le temps libre, est hors v1 : A4).
- `retenir` : satisfaction_vie, bonheur_ressenti, bilan_emotionnel_negatif, optimisme_avenir_personnel, soutien_social, solitude, satisfaction_relations, integration_sociale, cohesion_sociale_percue, confiance_autrui, benevolat, participation_culturelle_sportive, privation_loisirs, privation_sorties_proches, privation_vacances, depart_vacances. `retenir_variante` : satisfaction_vie_faible, situation_personnelle_bonne, optimisme_generations_futures. `ecarter` : evaluation_vie_cantril (dominée par la série INSEE), aidance_personne_agee (sens ambigu, travail non rémunéré A4).

## 3. Non fait

- Aucune correction de catalogue ni de règle de rattachement (hors mandat de la branche) : propositions au §5.
- Pas de bornes (`socle_v1` vide, conformément à la fiche M05).
- Valeurs Melodi non relues (api.insee.fr refuse l'outil de lecture) : identité Melodi / BDM de la satisfaction dans la vie à contrôler au premier passage du robot.

## 4. Problèmes rencontrés

- **Workflow « Collecte »** : avant sa correction sur `main` (fusionnée dans la branche), un push touchant `scripts/` sans `collecte_<dimension>.py` lançait la cible « tous » ; contourné par `[skip ci]` sur trois commits. Plus nécessaire.
- Exclusions en amont qui privaient la dimension de concepts nommés dans son contenu (vacances, bénévolat public, rencontres avec les proches) : voir §5.
- Licences non établies : données Gallup relayées par l'OCDE (3 fiches `retenir`), World Happiness Report, baromètre DREES.

## 5. Propositions (pour la session mère)

1. **Rattachements** (table de correspondance, règles d'exception) : `Incapacité à se payer une semaine de vacances` (Eurostat `ilc_mdes02`, v0 `travail`) → `liens_bien_etre` (A13, R3) ; répartition de la satisfaction dans la vie par statut d'activité (`PT_NOTE_IN_VIESATISF_BY_EMPSTA`, v0 `travail`) → `liens_bien_etre` (R4) ; satisfaction des domaines « lieu de résidence » et « temps de trajet » (`ilc_pw01b`, `ilc_pw02b`, `ilc_pw05b`) → `logement_cadre_vie` (R4) ; hors dimension : `ilc_mdes03` (repas avec viande ou poisson, aujourd'hui `planete`) → `niveau_de_vie` (A2).
2. **Catalogue Eurostat (M02)** : admettre les jeux `tour_dem_to*` (participation des personnes au tourisme : ce sont des résultats pour les ménages, pas une statistique sectorielle) ; appliquer D28 aux modules EU-SILC exclus au niveau 1 pour « début > 2010 » (`ilc_scp09`-`ilc_scp12`, `ilc_scp19`, `ilc_scp20`…).
3. **Long-list** : harmoniser la dérogation D17 de `longlist.py` (étendue ≥ 10 ans) avec D28 (écart moyen ≥ 1,5 an) ; ne pas signaler « statistiques d'entreprises » les ventilations par PCS (« chefs d'entreprise »).
4. **Modèle de fiche** (charte §5.1, `indicateurs/_modele_fiche.yaml`) : ajouter les champs M05 utilisés ici (`famille`, `variante_principale`, `variantes`, `composite`, `raccordement`, `incontournable`, `recommandation`, `motif_recommandation`, `note_pertinence`) et les champs techniques `composantes`, `formule`, `nb_points_depuis_2000`, `eligibilite_longlist`, `ligne_id`, `hors_longlist`, `rattachement_propose` ; admettre `sens: ambigu` pour les seules fiches écartées.
5. **Workflow « Collecte »** : sur un push de branche de mission sans script `collecte_<sujet>.py`, ne rien lancer plutôt que « tous ». — fait sur `main` (`cbf1a60`).
6. **M04** : rechercher un taux de licences sportives toutes fédérations (INJEP) et des séries de pratiques culturelles et sportives (DEPS, INJEP).

## 6. Points à faire vérifier par Léo

1. Trois fiches `retenir` reposent sur des données Gallup relayées par l'OCDE (soutien social — incontournable —, bilan émotionnel négatif, bénévolat), dont la réutilisation n'est pas confirmée.
2. Deux fiches mesurent une opinion sur la société plutôt que le bien-être de la personne : `cohesion_sociale_percue` (`retenir`) et `optimisme_generations_futures` (`retenir_variante`).
3. Les items de privation (loisirs, sorties avec les proches, vacances) sont placés ici par domaine (R3) plutôt qu'en niveau de vie.
4. Séries très courtes retenues par la dérogation D17 : `solitude` (2 points), `bonheur_ressenti` et `participation_culturelle_sportive` (3 points chacune).
5. `confiance_autrui` : toutes les valeurs Eurostat portent le drapeau de faible fiabilité « u » ; la série INSEE annuelle (2020-2025) pourrait devenir principale.
6. `depart_vacances` est proposé hors long-list (jeu Eurostat exclu à tort), avec un décrochage 2016-2017 à éclaircir.

## 7. Questions pour la session mère (répondues le 14/10 : oui aux trois, voir §8)

- Le vocabulaire (groupe / fiche / variante / famille), les définitions de `retenir`, `retenir_variante` et `ecarter`, le schéma étendu et les deux scripts conviennent-ils pour être imposés aux neuf autres dimensions ?
- Les fiches proposées pour des lignes d'une autre long-list (`privation_vacances`) ou hors long-list (`depart_vacances`) sont-elles admises dans le tableau de validation avant la décision de rattachement ?
- Faut-il ajouter `sens` et `unite` au tableau de validation (colonnes utiles pour juger une recommandation) ?

## 8. Décisions de la session mère du 14/10/2026 (appliquées)

- Méthode, schéma et scripts adoptés pour les neuf autres dimensions : `docs/methodo/33_methode_fiches_M05.md`, avec les règles du pilote `securite` (code `autre_dimension:<dim>`, `declaratif` = perception ou opinion, `sens: ambigu` ⇒ `ecarter`, `raccordement` au format « oui|non|a_etudier : note courte », variante principale : taux plutôt que nombre, enquête plutôt que série enregistrée). Conséquences ici : `benevolat` passe à `declaratif: non` ; `confiance_autrui` a `raccordement: a_etudier : …` ; deux groupes de présélection passent en `autre_dimension:logement_cadre_vie`.
- Tableau de validation régénéré avec `sens` et `unite` (18 colonnes).
- **`privation_vacances`** (ligne de la long-list `travail`, rattachement proposé à `liens_bien_etre`) et **`depart_vacances`** (hors long-list, jeu Eurostat `tour_dem_totot` à réintégrer) restent au tableau avec `rattachement_propose` renseigné ; la session mère tranche au gel 2.
- `origin/main` fusionné (workflow Collecte corrigé) ; plus de `[skip ci]`.
