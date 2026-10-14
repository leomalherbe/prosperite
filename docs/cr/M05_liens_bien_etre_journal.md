# Journal de bord — M05, dimension `liens_bien_etre` (mission pilote)

Agent de mission M05, 14 octobre 2026, branche `m05-liens_bien_etre` (partie de `origin/main` au commit `d8a054b`). Dimension : **Liens sociaux et bien-être ressenti** (grille v1 figée, `indicateurs/dimensions.yaml`). Mission pilote : la méthode ci-dessous est écrite pour être reprise telle quelle par les neuf autres dimensions.

Lu avant d'agir : `CLAUDE.md` ; charte §3.1, §3.4, §3.6, §4, §5.1 ; journal D13–D30 ; fiche M05 (dont la précision d'échelle du 14/10) ; `indicateurs/dimensions.yaml` (définition, contenu, exclusions, R1–R8) ; `indicateurs/_modele_fiche.yaml` ; `docs/methodo/32_longlist_mode_emploi.md` ; long-list `catalogues/longlist_liens_bien_etre.csv.gz` (668 lignes : 389 éligibles, 208 à vérifier, 71 non éligibles) et bilan ; `docs/methodo/30_indicateurs_cadres_reference.csv` (34 lignes `liens_bien_etre`) et `30_crosswalk_synthese.md` ; `docs/sources/autres_sources.md` (§2.2, §2.11, §3.1, §3.4, §7), `insee.md`, `eurostat.md`. Tests initiaux : 372 réussis.

---

## 1. Méthode (à reprendre pour les autres dimensions)

### 1.1 Chaîne de travail et outils

| Étape | Outil | Sortie |
|---|---|---|
| 1. Lire la long-list par jeu et par mesure (pas ligne à ligne) | pandas, regroupement par code de jeu / mesure | — |
| 2. Écrire les **règles de présélection** | `docs/validation/regles_preselection_<dim>.csv` | règles ordonnées |
| 3. Appliquer les règles | `python scripts/preselection.py --dimension <dim>` | `preselection_<dim>.csv` (une ligne par groupe) et `preselection_<dim>_lignes.csv` (une ligne par ligne de long-list) |
| 4. Rédiger une fiche par groupe `fiche` | YAML dans `indicateurs/<dim>/<id>.yaml` | fiches sans variantes |
| 5. Injecter les variantes | `python scripts/preselection.py --dimension <dim> --maj-fiches` | champ `variantes` rempli depuis la présélection |
| 6. Ajouter à la main les variantes hors long-list | édition YAML (entrées **sans** `ligne_id`, avec `catalogue`) | conservées par `--maj-fiches` |
| 7. Tableau de validation | `python scripts/verifier_fiches.py --dimension <dim> --tableau` | `docs/validation/validation_<dim>.csv` |
| 8. Contrôles | `python scripts/verifier_fiches.py --dimension <dim>` | 0 erreur exigé ; compteurs pour le journal |

Les deux scripts sont génériques (aucune référence à la dimension pilote) et testés hors ligne (`tests/test_verifier_fiches.py`, mini-dépôt construit dans un dossier temporaire, plus un test sur les fiches réelles de `liens_bien_etre`).

### 1.2 Vocabulaire opérationnel (échelle du 14/10)

- **Ligne** : une ligne de long-list (une série, ou un paquet de modalités Eurostat).
- **Groupe** (= « concept » de la fiche M05, une ligne du tableau de présélection) : ensemble de lignes décrit par une règle, avec **une** décision : `fiche`, `variante_de:<id>` ou `ecarte_en_bloc`.
- **Fiche** : un indicateur distinct et intelligible pour le public. Sa série principale est le groupe `fiche` (une ligne, ou plusieurs **composantes** si l'indicateur est une somme, cf. `bonheur_ressenti`).
- **Variante** (`variantes` de la fiche) : même indicateur sous une autre forme — ventilation (sexe, âge, diplôme, revenu…), autre voie d'accès (BDM/Melodi), autre source (Eurostat, OCDE), autre unité (part élevée), complément (part « non » d'une question oui/non), doublon technique. Pas de fiche propre.
- **Famille** : fiches substituables entre elles (l'utilisateur choisirait l'une **ou** l'autre), avec une seule `variante_principale: oui`. Une fiche sans substitut forme sa propre famille (`famille` = son `id`). Deux concepts complémentaires (affect positif, affect négatif) sont deux familles, pas deux variantes.
- **Écart en bloc** : sous-séries sans intérêt propre (classes de fréquence, catégorie intermédiaire « moyen », non-réponse, fédérations sportives isolées sans total) ou lignes non éligibles, avec un motif.

Règle de partage fiche / variante appliquée : une autre **statistique** sur la même question devient une fiche si elle se lit autrement pour le public et pour les bornes (part sous un seuil ≠ moyenne : `satisfaction_vie_faible`) ; une autre **forme** de la même statistique reste une variante (part des notes 9-10, complément, ventilations).

### 1.3 Format des règles

Colonnes : `ordre, groupe, decision, nature, motif, longlist, catalogue, motif_ligne_id, motif_serie_id, motif_libelle, hors_longlist`.
- Chaque ligne de long-list reçoit la **première** règle dont toutes les conditions non vides sont remplies (expressions régulières en recherche ; `motif_libelle` insensible à la casse). Ordre conseillé : série principale exacte (ancrée `^…$`), puis doublons et variantes précises, puis écarts en bloc précis, puis règles larges (ventilations d'un jeu).
- Une ligne de la long-list de la dimension sans règle fait échouer le script : **la couverture est exhaustive par construction**.
- `longlist = <autre dimension>` importe des lignes mal rattachées d'une autre long-list (17 lignes de `travail` ici) : elles restent dans leur long-list, la présélection et la fiche le signalent (`rattachement_propose`), la session mère tranche (R1).
- `hors_longlist = oui` : concept dont la série n'est dans aucune long-list (exclue en amont à tort), vérifiée à la source ; la fiche porte `hors_longlist: oui`.
- Piège rencontré : `lire_regles` retire les espaces de fin de cellule ; pour distinguer `MEASURE=11_1` de `MEASURE=11_1_DEP`, utiliser `\b` et non une espace finale.

### 1.4 Choix de la variante principale (critères M05, appliqués dans cet ordre)

1. Niveau 1 > niveau 2 ; INSEE > Eurostat > autres **à définition égale** ; 2. sauf profondeur ou fraîcheur meilleure ailleurs ; 3. série la plus longue ; 4. total avant ventilation.
Cas tranchés : `satisfaction_vie` — Melodi plutôt que la BDM (même enquête, Melodi va jusqu'en 2025, BDM jusqu'en 2024) ; `soutien_social` — OCDE (Gallup, 2006-2025) plutôt qu'EU-SILC (3 vagues), malgré la licence à confirmer, avec la variante publique désignée comme repli ; `confiance_autrui` — Eurostat (7 vagues depuis 2013) plutôt que l'INSEE (annuel depuis 2020 seulement), avec mention que la série INSEE pourrait la remplacer (faible fiabilité Eurostat).

### 1.5 Recommandations : définitions opérationnelles

- `retenir` : variante principale d'une famille, éligible (y compris dérogations D16/D17), sens clair, source publique documentée (licence incertaine signalée en `qualite`).
- `retenir_variante` : fiche non principale qui apporte ce que la principale n'a pas (autre lecture — seuil plutôt que moyenne —, couverture d'années manquantes, autre objet proche).
- `ecarter` : sens ambigu (charte §3.4 ; `sens: ambigu` n'est admis par le vérificateur qu'avec cette recommandation), hors champ v1 (A4, R4, R6) ou **dominée** (même concept, pas meilleure sur la profondeur, la fraîcheur, la fréquence ni la licence).
- `motif_recommandation` : une phrase, vérifiable (chiffres, années, décisions citées) ; `note_pertinence` : 2 à 4 phrases. Les deux sont contrôlés par le vérificateur (nombre de phrases).
- `incontournable: oui` seulement pour les concepts du §5 de `30_crosswalk_synthese.md` (≥ 3 cadres) : ici satisfaction dans la vie (4) et soutien social (3-4) ; le troisième concept de la dimension v0 dans ce tableau, « temps libre / emploi du temps » (3), est hors v1 (A4, D27).

### 1.6 Schéma de fiche utilisé

Charte §5.1 + champs M05, dans cet ordre : `id, libelle, dimension, sous_theme, famille, variante_principale, definition, unite, sens, type, declaratif, composite, source_organisme, source_jeu, source_serie_id, [composantes, formule], source_niveau, url_api, url_page, frequence, premiere_annee, derniere_annee, nb_points_depuis_2000, geo, eligibilite_longlist, ligne_id, hors_longlist, [rattachement_propose], raccordement, incontournable, recommandation, motif_recommandation, note_pertinence, variantes, socle_v1 (vide), qualite, notes`. Modèle conseillé : copier `indicateurs/liens_bien_etre/satisfaction_vie.yaml`.

Ajouts au modèle de la charte (à valider par la session mère) : `composantes` et `formule` (indicateur somme de plusieurs séries), `nb_points_depuis_2000`, `eligibilite_longlist` (`oui | a_verifier | non | hors_longlist`), `ligne_id` (lien vers la long-list), `hors_longlist`, `rattachement_propose`, `sens: ambigu` (réservé à `ecarter`). Chaque variante : `serie_id, source, nature, ligne_id, eligible` (+ `longlist` si importée, `catalogue` si hors long-list).
Les périodes, nombres de points et URL d'API de la série principale sont **lus dans la long-list** par le script d'écriture, jamais saisis. Les identifiants d'allure numérique (idbank) sont écrits entre guillemets (`'010593281'`) pour qu'un lecteur YAML 1.2 (JavaScript) ne les convertisse pas en nombre (`preselection.texte_yaml`).

### 1.7 Vérifications à la source (WebFetch, 14/10/2026)

API Eurostat (lecture JSON) : `ilc_pw08` (années 2013, 2018, 2022 ; valeurs par fréquence ; aucun drapeau), `ilc_pw03` (2013, 2018, 2021-2025 ; **drapeau « u » sur toutes les valeurs**, ruptures 2018 et 2022), `ilc_pw06` (2013, 2018, 2022), `ilc_scp01` (2006, 2015, 2022), `ilc_mdes02`, `ilc_mdes10a`, `ilc_mdes11a` (ruptures 2020 et 2022), `tour_dem_totot` (2012-2025, sans drapeau). Pages : sommaire INSEE des indicateurs de richesse nationale (sous-page 3281675 « Satisfaction globale de la vie »), page du baromètre DREES (existe ; licence non indiquée), Data Browser Eurostat et catalogue Melodi (existent, rendus en JavaScript : contenu non lisible). Refusés à l'outil : `api.insee.fr/melodi` (robots.txt), pages OCDE (erreur) : `url_page` OCDE = « non trouvé ». Libellés des questions DREES lus dans `docs/sources/series/drees__barometre_dico_*_2025.txt` ; définitions Gallup lues dans `docs/sources/series/ocde__hsl_definitions_pdf.txt`.

### 1.8 Contraintes techniques rencontrées

- **Workflow « Collecte »** : avant sa correction sur `main` (commit `cbf1a60`, fusionné dans la branche), un push sur `mNN-*` touchant `scripts/` sans `scripts/collecte_<sujet>.py` lançait la cible « tous » ; les trois premiers commits de la branche portent donc `[skip ci]`. Depuis la correction, un tel push ne lance plus rien : `[skip ci]` n'est plus nécessaire.
- La long-list commitée (`.csv.gz`) est lue telle quelle ; aucune régénération n'a été nécessaire (catalogues inchangés depuis l'exécution finale du 14/10).

### 1.9 Mode d'emploi pour une nouvelle dimension

```bash
python -m pytest -q
# 1. explorer : python -c "import pandas as pd; d=pd.read_csv('catalogues/longlist_<dim>.csv.gz', dtype=str); ..."
# 2. écrire docs/validation/regles_preselection_<dim>.csv, puis itérer jusqu'à 0 ligne sans règle :
python scripts/preselection.py --dimension <dim>
# 3. écrire indicateurs/<dim>/<id>.yaml (une par groupe « fiche »), puis :
python scripts/preselection.py --dimension <dim> --maj-fiches
python scripts/verifier_fiches.py --dimension <dim> --tableau
python scripts/verifier_fiches.py --dimension <dim>      # 0 erreur
```
Relire aussi les long-lists voisines (recherche par mots-clés du contenu de la dimension) : ici, 17 lignes de `travail` relevaient de `liens_bien_etre`.

---

## 2. Déroulé

1. Lecture des entrées ; inventaire de la long-list par catalogue et par jeu : INSEE BDM 28 lignes (satisfaction dans la vie, licences sportives de 8 fédérations), Melodi 342 (satisfaction SRCV : vie, relations sociales, répartitions 0-5 / 6-8 / 9-10 ventilées), Eurostat 262 (modules bien-être `ilc_pw*`, participation `ilc_scp01/03`, privations `ilc_mdes10/11`), M04 36 (OCDE How's Life, baromètre DREES, WHR, OWID).
2. Recherche des concepts de la dimension dans les autres long-lists, les catalogues d'exclusion (`*_non.csv.gz`) et le catalogue des jeux Eurostat (§4).
3. Règles (66), présélection, fiches (21), variantes, vérificateur, tableau de validation ; vérifications à la source (§1.7).

## 3. Résultats chiffrés

- **Présélection** : 67 groupes — 21 `fiche`, 34 `variante_de`, 10 `ecarte_en_bloc`, 2 `autre_dimension:logement_cadre_vie` (40 lignes, satisfaction des domaines « lieu de résidence » et « temps de trajet », non éligibles) ; 685 lignes affectées = les 668 de la long-list + 17 importées de `travail`.
  - Lignes de la long-list : 20 en série principale (12 éligibles, 8 à vérifier), 448 en variantes (296 éligibles, 152 à vérifier), 160 écartées en bloc (81 éligibles : 65 catégories « moyen » 6-8 de Melodi et 16 licences par fédération ; 48 à vérifier : catégories « moyen » Eurostat, non-réponses, classes de fréquence ; 31 non éligibles), 40 renvoyées à `logement_cadre_vie` (non éligibles).
  - Importées de `travail` : 1 série principale (`ilc_mdes02`), 11 variantes, 5 écartées (catégorie 6-8).
- **Fiches : 21** (17 familles) — **16 `retenir`**, 3 `retenir_variante` (`satisfaction_vie_faible`, `situation_personnelle_bonne`, `optimisme_generations_futures`), 2 `ecarter` (`evaluation_vie_cantril` : dominée ; `aidance_personne_agee` : sens ambigu et A4).
- Déclaratives : 14 (`benevolat` passé à `non` : fait déclaré) ; composites : 0 ; séries « à vérifier » (D17) : 7 (`bonheur_ressenti`, `bilan_emotionnel_negatif`, `soutien_social`, `solitude`, `confiance_autrui`, `benevolat`, `participation_culturelle_sportive`) ; hors long-list : 1 (`depart_vacances`) ; rattachement proposé depuis `travail` : 1 fiche (`privation_vacances`) et 2 groupes de variantes ; incontournables : 2 sur 2 présents.
- Variantes listées dans les fiches : 465 (dont 6 ajoutées à la main hors long-list : INSEE `DS_SRCV_CONFIANCE`, 3 items `DS_SRCV_PMS`, 2 durées `tour_dem_totot`).
- Sources des 21 séries principales : INSEE 3, Eurostat 7, OCDE 4 (dont 3 Gallup), DREES 6, WHR 1. Niveau 2 (fichiers) : 7.

## 4. Relecture des exclusions et erreurs de catalogue

**Exclusions de la long-list (`eligible = non`, 71 lignes)** : toutes fondées — modules EU-SILC à une seule vague 2013 (« sens de la vie », « lieu de résidence », « temps de trajet » : 60 lignes), séries OCDE de l'enquête Emploi du temps (2009), Eurobaromètre via OWID (arrêté en 2016), classes de fréquence `ilc_scp03` AC52A (2 points 2015-2022).

**Exclusions abusives ou erreurs en amont** (corrections proposées, non faites : hors mandat de cette branche) :
1. **Tourisme des personnes exclu par M02** : `tour_dem_tosex`, `…toage`, `…totot`, etc. (« Personnes participant au tourisme pour des motifs personnels », 2012-2025) sont classés « domaine hors périmètre (tourisme) : statistique sectorielle » ; ce sont des résultats pour les personnes (départ en vacances, contenu A13). Fiche `depart_vacances` créée hors long-list ; à réintégrer au catalogue Eurostat (M02).
2. **Modules EU-SILC exclus au niveau 1 par M02** (« début des données > 2010 ») : `ilc_scp19`/`ilc_scp20` (bénévolat formel et informel, 2015 et 2022), `ilc_scp09`-`ilc_scp12` (rencontres et contacts avec famille et amis, 2015 et 2022), `ilc_scp05`/`ilc_scp07`. Avec D28 (écart moyen ≥ 1,5 an), ils seraient candidats « à vérifier », comme `ilc_scp01` (2006, 2015, 2022) qui est dans la long-list. Variantes publiques attendues de `benevolat` et nouvelles fiches possibles (rencontres avec les proches).
3. **Rattachements à corriger** : `ilc_mdes02` (vacances, 22 points) est dans la long-list `travail` (étiquette v0 du jeu Eurostat) → `liens_bien_etre` (A13, R3) ; `PT_NOTE_IN_VIESATISF_BY_EMPSTA` (répartition de la satisfaction dans la vie par statut d'activité, 15 lignes) est dans `travail` (règle par défaut de M01) → `liens_bien_etre` (R4). Hors de ma dimension mais repéré : `ilc_mdes03` (repas avec viande ou poisson) est dans `planete` → `niveau_de_vie` (accès à l'alimentation, A2).
4. **Règle D17 appliquée différemment selon l'étiquette de fréquence** : une série Eurostat de 2 points espacés de 7 ans sur une étendue < 10 ans est `non` dans la long-list (§4.3 : étendue ≥ 10 ans exigée), une série M04 étiquetée `irreguliere` de 2 points sur 5 ans (`solitude`) est `a_verifier`, et D28 (catalogues) admet tout écart moyen ≥ 1,5 an. À harmoniser (proposition : appliquer le critère D28 dans `longlist.py`).
5. **Faux positif « statistiques d'entreprises »** : 5 lignes Melodi de satisfaction ventilées par PCS (« Agriculteurs, artisans, commerçants, chefs d'entreprise ») portent la note « champ à vérifier » (mot « entreprise ») ; sans conséquence, motif à affiner dans `longlist.py`.
6. **Lacunes de catalogue** : pas de taux de licences sportives toutes fédérations (la BDM n'a que 8 fédérations, `TCRED-CONDITIONSDEVIE-LICENCES-SPORTIVES`) ; pas de série de pratique sportive ni de pratiques culturelles annuelles (enquêtes du ministère de la Culture, INJEP) ; « sens de la vie » mesuré en 2013 seulement. À rechercher par M04 (INJEP, DEPS).

## 5. Incontournables du crosswalk

| Concept (§5 du crosswalk) | Cadres | Fiche |
|---|---|---|
| Satisfaction dans la vie | SSF, OCDE, Eurostat, INSEE (4) | `satisfaction_vie` (retenir) |
| Soutien social | Doughnut, OCDE, Eurostat (3-4) | `soutien_social` (retenir) |
| Temps libre / emploi du temps | SSF, OCDE, Eurostat (3) | absent : thème hors v1 (A4, D27) ; seule série (OCDE 4_1) de 2009, non éligible |

Concepts à deux cadres présents : confiance dans les autres (`confiance_autrui`), satisfaction des relations personnelles (`satisfaction_relations`), bénévolat (`benevolat`), affects (`bonheur_ressenti`, `bilan_emotionnel_negatif`), solitude (`solitude`). Absents faute de données France éligibles : sens de la vie (2013), fréquence des rencontres avec les amis (exclue en amont, §4.2), avoir quelqu'un à qui parler de sujets personnels (`ilc_scp17`, 2013-2015).

## 6. Contrôles (sortie de `verifier_fiches.py`)

```
Dimension liens_bien_etre : lignes_longlist 668, lignes_autre_dimension 40, fiches 21, familles 17, retenir 16, retenir_variante 3, ecarter 2,
declaratifs 14, composites 0, a_verifier 7, hors_longlist 1, incontournables ['satisfaction_vie', 'soutien_social'], variantes 465
avertissement — depart_vacances : série principale hors catalogue de séries (jeu tour_dem_totot au catalogue des jeux) : à réintégrer au catalogue
0 erreur(s), 1 avertissement(s)
```
Aucun identifiant en double dans `indicateurs/` ; chaque série principale et chaque variante est présente dans un catalogue du dépôt (sauf `depart_vacances`, jeu présent au catalogue des jeux, série vérifiée à la source) ; toutes les lignes de la long-list sont affectées ; tableau de validation cohérent avec les fiches. Tests : 394 réussis (22 nouveaux).

## 7. Points ouverts

- Identité des valeurs Melodi `VIESATISF` et BDM 010593281 non contrôlée (api.insee.fr fermé à l'outil) : à vérifier au premier passage du robot.
- Réutilisation des données Gallup relayées par l'OCDE (3 fiches `retenir` : `soutien_social`, `bilan_emotionnel_negatif`, `benevolat`) : courriel à l'OCDE proposé en D26, toujours en attente.
- `confiance_autrui` : faible fiabilité Eurostat sur toutes les années ; la série INSEE annuelle 2020-2025 pourrait devenir principale (raccordement D16 à étudier).
- `satisfaction_relations` : série métropolitaine arrêtée en 2022 dans le catalogue ; poursuite à vérifier.
- `depart_vacances` : décrochage 2016-2017 sans drapeau ; champ d'âge à vérifier.
- Baromètre DREES (6 fiches) : stabilité des codes de modalités 2000-2025, champ géographique et licence à confirmer.

## 8. Décisions de la session mère (14/10/2026) et mises à jour

1. Méthode adoptée pour les neuf autres dimensions ; rédigée dans `docs/methodo/33_methode_fiches_M05.md` (vocabulaire, schéma complet, déroulé, conventions), avec les règles du pilote `securite` : code `autre_dimension:<dim>` (ajouté à `preselection.py`, contrôlé contre `dimensions.yaml`) ; `declaratif = oui` pour les perceptions et opinions, `non` pour les faits ou capacités déclarés (`benevolat` passe à `non`) ; `sens: ambigu` ⇒ `ecarter` ; `raccordement` au format « oui|non|a_etudier : note courte » (contrôlé par le vérificateur ; `confiance_autrui` = `a_etudier`, `satisfaction_vie` = `non : …`, autres fiches `non`) ; variante principale : taux plutôt que nombre, enquête plutôt que série enregistrée (aucune fiche concernée ici).
2. Tableau de validation : colonnes `sens` et `unite` ajoutées après `definition_courte` ; tableau régénéré.
3. `privation_vacances` et `depart_vacances` restent au tableau avec `rattachement_propose` ; décision au gel 2.
4. `origin/main` fusionné (correction du workflow Collecte) ; plus de `[skip ci]`.
5. Présélection : la satisfaction des domaines « lieu de résidence » et « temps de trajet » passe d'un écart en bloc à `autre_dimension:logement_cadre_vie`.
