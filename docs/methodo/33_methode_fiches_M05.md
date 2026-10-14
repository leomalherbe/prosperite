# Méthode commune des fiches indicateurs (mission M05) — v1.2

Version 1.1 — 14 octobre 2026. Méthode du pilote `liens_bien_etre` (journal `docs/cr/M05_liens_bien_etre_journal.md`), adoptée par la session mère pour les dix dimensions (D31), complétée par les règles actées au pilote `securite` et par les règles issues des audits M06 (D32, D33 ; §9). Outils : `scripts/preselection.py`, `scripts/verifier_fiches.py` (tests : `tests/test_verifier_fiches.py`). Exemple de fiche complète : `indicateurs/liens_bien_etre/satisfaction_vie.yaml`.

## 1. Vocabulaire

| Terme | Définition opérationnelle |
|---|---|
| Ligne | Une ligne de la long-list (`catalogues/longlist_<dim>.csv.gz`) : une série, ou un paquet de modalités Eurostat. |
| Groupe (concept) | Lignes décrites par une même règle de présélection, avec une seule décision ; une ligne du tableau de présélection. |
| Fiche | Un indicateur distinct et intelligible pour le public : `indicateurs/<dim>/<id>.yaml`. Sa série principale est le groupe `fiche` (une ligne, ou plusieurs `composantes` si l'indicateur est une somme). |
| Variante | Le même indicateur sous une autre forme : ventilation, autre voie d'accès (BDM/Melodi), autre source, autre unité, complément d'une question oui/non, doublon technique. Listée dans `variantes`, pas de fiche propre. |
| Famille | Fiches substituables entre elles (l'utilisateur prendrait l'une **ou** l'autre), avec une seule `variante_principale: oui`. Une fiche sans substitut forme sa famille (`famille` = son `id`). Deux concepts complémentaires (affect positif, affect négatif) sont deux familles. |
| Écart en bloc | Sous-séries sans intérêt propre (classes de fréquence, catégorie intermédiaire, non-réponse, sous-catégorie isolée sans total) ou lignes non éligibles, avec un motif. |

Partage fiche / variante : une autre **statistique** sur la même question devient une fiche si elle se lit autrement pour le public et pour les bornes (part sous un seuil ≠ moyenne) ; une autre **forme** de la même statistique reste une variante.

## 2. Décisions de présélection (colonne `decision` des règles)

| Code | Effet |
|---|---|
| `fiche` | Le groupe porte la série principale de la fiche `<groupe>`. |
| `variante_de:<id>` | Variantes de la fiche `<id>`, injectées dans son champ `variantes`. |
| `ecarte_en_bloc` | Écarté, motif obligatoire. |
| `autre_dimension:<dim>` | La ligne relève d'une autre dimension v1 (rattachement à corriger) ; `<dim>` doit exister dans `indicateurs/dimensions.yaml` ; la session mère tranche. |

Règles (`docs/validation/regles_preselection_<dim>.csv`) : colonnes `ordre, groupe, decision, nature, motif, longlist, catalogue, motif_ligne_id, motif_serie_id, motif_libelle, hors_longlist`. Chaque ligne reçoit la **première** règle dont toutes les conditions non vides sont remplies (expressions régulières en recherche ; libellé insensible à la casse). Ordre : séries principales exactes (`^…$`), doublons et variantes précises, écarts précis, puis règles larges. `longlist = <autre dim>` importe des lignes mal rattachées d'une autre long-list (rattachement proposé) ; `hors_longlist = oui` déclare un concept dont la série n'est dans aucune long-list (vérifiée à la source). Une ligne de la long-list sans règle fait échouer le script : la couverture est exhaustive.

## 3. Recommandations

- `retenir` : variante principale d'une famille, éligible (y compris dérogations D16, D17), sens clair, source publique documentée (licence incertaine signalée dans `qualite`).
- `retenir_variante` : fiche non principale qui apporte ce que la principale n'a pas (autre lecture, années manquantes, objet voisin).
- `ecarter` : sens ambigu, hors champ v1 (A4, R4, R6), dominée (même concept, pas meilleure en profondeur, fraîcheur, fréquence ni licence) ou série arrêtée sans relais (D32 ; si un successeur existe : `raccordement: a_etudier : …`). **Jamais pour la seule brièveté** : une série éligible (D16, D17) est soit `sens: ambigu`, soit retenue, au besoin en variante (D32).
- `motif_recommandation` : **une** phrase vérifiable (années, nombre de points, décision citée) ; `note_pertinence` : 2 à 4 phrases.

## 4. Conventions

- **Identifiants** : ASCII, minuscules, mots français séparés par `_`, sans accent, égaux au nom du fichier (`satisfaction_vie`, `privation_vacances`) ; un identifiant n'existe qu'une fois dans tout `indicateurs/` ; groupes de présélection : même convention (`<fiche>_ventilations`, `<fiche>_eurostat`…).
- **Déclaratif** : `oui` pour les perceptions et opinions (satisfaction, sentiment, confiance, optimisme, jugement sur la société) ; `non` pour les faits ou capacités déclarés (avoir fait du bénévolat, être parti, ne pas avoir les moyens de…).
- **Sens** : `haut` ou `bas` ; `ambigu` implique `recommandation: ecarter`.
- **Raccordement** : `oui|non|a_etudier : note courte` ; la note est obligatoire après `oui` et `a_etudier` (ex. `a_etudier : série INSEE 2020-2025 à raccorder à ilc_pw03 (D16)`).
- **Variante principale** (dans l'ordre) : niveau 1 > 2 ; INSEE > Eurostat > autres à définition égale, sauf profondeur ou fraîcheur meilleure ailleurs ; série la plus longue ; total avant ventilation ; **taux plutôt que nombre** ; **enquête plutôt que série enregistrée** tant que l'enquête est publiée.
- **Incontournable** : `oui` seulement pour les concepts du §5 de `docs/methodo/30_crosswalk_synthese.md` (≥ 3 cadres).
- **Données lues, jamais saisies** : périodes, nombre de points et URL d'API de la série principale viennent de la long-list ; toute valeur citée dans une note est vérifiée (fixture, API lue par WebFetch) ; sinon « non trouvé ».
- **YAML** : écrit par `preselection.texte_yaml` (identifiants d'allure numérique entre guillemets : `'010593281'`).
- **Rattachement** : une ligne d'une autre long-list reprise en fiche porte `rattachement_propose` ; elle reste dans le tableau de validation, la session mère tranche au gel 2. **Avant de commencer**, lire les `docs/validation/preselection_*_lignes.csv` des dimensions déjà traitées et les règles `autre_dimension:*` qui visent la sienne (R1, D32) ; le vérificateur avertit si une ligne utilisée est déjà la série principale d'une fiche d'une autre dimension.
- **Champ mixte** : un taux dont numérateur et dénominateur n'ont pas le même champ (métropole / France entière) est admis s'il est documenté (`qualite: champ_mixte`) ; le pipeline recalculera un taux homogène (D32).

## 5. Schéma de fiche

| Champ | Obligatoire | Valeurs admises |
|---|---|---|
| `id` | oui | identifiant (§4), = nom du fichier |
| `libelle`, `sous_theme`, `definition`, `unite`, `geo` | oui | texte non vide (`geo` : code de zone de la série, D15) |
| `dimension` | oui | la dimension du dossier |
| `famille` | oui | identifiant |
| `variante_principale` | oui | `oui` \| `non` (une seule `oui` par famille) |
| `sens` | oui | `haut` \| `bas` \| `ambigu` (→ `ecarter`) |
| `type` | oui | `resultat` \| `moyen` \| `pression` |
| `declaratif`, `composite`, `incontournable` | oui | `oui` \| `non` |
| `source_organisme`, `source_jeu`, `source_serie_id` | oui | texte ; `source_serie_id` présent dans un catalogue du dépôt |
| `composantes`, `formule` | si somme | liste de `serie_id` du catalogue ; formule en clair (`ALW + MOST`) |
| `source_niveau` | oui | `1` (API) \| `2` (fichier) |
| `url_api`, `url_page` | oui | URL `http(s)://…` ou `non trouvé` |
| `frequence` | oui | `annuelle` \| `irreguliere` \| `semestrielle` \| `trimestrielle` \| `mensuelle` \| `ponctuelle` |
| `premiere_annee`, `derniere_annee` | oui | année de 1700 à 2100 (séries V-Dem, D32) ou `non trouvé` |
| `nb_points_depuis_2000` | conseillé | entier |
| `eligibilite_longlist` | conseillé | `oui` \| `a_verifier` \| `non` \| `hors_longlist` |
| `ligne_id` | conseillé | `ligne_id` de la série principale (vide si hors long-list) |
| `hors_longlist` | conseillé | `oui` \| `non` ; `oui` : jeu Eurostat au catalogue des jeux **ou** `preuve` (§9) |
| `preuve` | si hors catalogue | chemin d'un fichier du dépôt qui atteste la série (sortie du robot, ex. `docs/sources/series/drees__…csv`) |
| `statut_serie` | si hors catalogue | `disponible` (valeurs déjà produites) \| `a_calculer` (à calculer par un robot, ligne de maintenance) |
| `rattachement_propose` | si besoin | origine et dimension proposée |
| `raccordement` | oui | `oui\|non\|a_etudier : note courte` |
| `recommandation` | oui | `retenir` \| `retenir_variante` \| `ecarter` (principale : pas `retenir_variante` ; non principale : pas `retenir`) |
| `motif_recommandation` | oui | une phrase terminée par un point |
| `note_pertinence` | oui | 2 à 4 phrases |
| `variantes` | oui | liste de `{serie_id, source, nature, ligne_id, eligible}` (+ `longlist` si importée) ; entrée sans `ligne_id` = ajout manuel hors long-list, avec `catalogue` |
| `socle_v1` | oui | vide (`seuil_minimal`, `objectif`, `type_justification` nuls, `justification` vide) |
| `qualite` | oui | liste de drapeaux (`rupture_2022`, `serie_irreguliere_D17`, `faible_fiabilite_eurostat_u`…) |
| `notes` | oui | texte (peut être vide) |

## 6. Déroulé pas à pas

```bash
git fetch origin && git checkout -B m05-<dim> origin/main && python -m pytest -q
# 1. Explorer la long-list par jeu / mesure (pas ligne à ligne) et chercher les concepts de la dimension
#    dans les autres long-lists, les catalogues *_non.csv.gz et catalogues/eurostat_jeux_catalogue.csv.
# 2. Écrire docs/validation/regles_preselection_<dim>.csv, puis itérer jusqu'à « 0 ligne sans règle » :
python scripts/preselection.py --dimension <dim>
# 3. Écrire une fiche par groupe « fiche » (indicateurs/<dim>/<id>.yaml), variantes vides.
# 4. Injecter les variantes (les ajouts manuels sans ligne_id sont conservés) :
python scripts/preselection.py --dimension <dim> --maj-fiches
# 5. Tableau de validation, puis contrôles (0 erreur exigé) :
python scripts/verifier_fiches.py --dimension <dim> --tableau
python scripts/verifier_fiches.py --dimension <dim>
```
Sorties : `docs/validation/preselection_<dim>.csv` (une ligne par groupe), `preselection_<dim>_lignes.csv` (une ligne par ligne affectée), `validation_<dim>.csv`. Le vérificateur contrôle : schéma, identifiants uniques dans `indicateurs/`, familles, présence des séries principales et des variantes dans les catalogues, couverture complète de la long-list, cohérence des variantes avec la présélection, cohérence du tableau avec les fiches. Ses compteurs (fiches, `retenir`, déclaratifs, composites, à vérifier, hors long-list, incontournables) vont au journal.

## 7. Tableau de validation

Colonnes, dans l'ordre : `id, libelle, famille, variante_principale, definition_courte, sens, unite, source, serie_id, periode, type, declaratif, composite, incontournable, recommandation, motif, decision_leo, commentaire_leo`. `decision_leo` : vide, `retenu`, `retenu_socle`, `ecarte` ou `a_discuter`. Une réécriture (`--tableau`) conserve les décisions déjà saisies.

## 8. Pièges connus

- Les cellules des règles sont nettoyées des espaces de fin : distinguer `MEASURE=11_1` de `MEASURE=11_1_DEP` par `\b`, pas par une espace.
- Le total d'un jeu Melodi est souvent répété sous chaque mesure de ventilation : une seule ligne en série principale, les autres en doublons techniques.
- Les drapeaux Eurostat (`b` rupture, `u` faible fiabilité) ne sont pas dans la long-list : les lire sur l'API pour les séries principales.
- Ne pas écarter un indicateur parce qu'il recoupe une autre dimension : `autre_dimension:<dim>` ou `rattachement_propose`, la session mère tranche.
- Chercher hors de la long-list les concepts nommés par le contenu de la dimension : sorties du robot M04 (`docs/sources/series/*`, ex. toutes les questions du baromètre DREES), catalogues `*_non.csv.gz`, catalogue des jeux Eurostat (jeux exclus au niveau 1).

## 9. Règles complémentaires (D32, D33)

- **Fiches hors long-list** (D32) : admises si la série est vérifiée à la source ; `hors_longlist: oui`, `eligibilite_longlist: hors_longlist`, `ligne_id` vide, `rattachement_propose` (origine de l'oubli), et soit un jeu Eurostat présent au catalogue des jeux, soit un champ `preuve` vers la sortie du robot ; `statut_serie: a_calculer` si les valeurs ne sont pas encore produites. Une ligne est ajoutée à `docs/cr/maintenance_catalogues.md` (calcul ou réintégration du jeu, numérotation continue). Règle de présélection associée : `hors_longlist = oui`. Les variantes hors long-list (sans `ligne_id`) portent `catalogue` ou `preuve`.
- **Composantes ou fiches** (D32) : la composante d'un concept (une forme de violence, une catégorie de sortie) est une variante de la fiche parente, sauf si elle porte une préoccupation publique propre (ex. violences conjugales) : fiche propre.
- **Opinions sur la société** (D32) : cohésion perçue, optimisme pour les générations futures… sont des fiches de familles distinctes, recommandées comme les autres opinions de la dimension (pas en variante d'une mesure personnelle).
- **Écarts construits** (D32) : un indicateur d'écart calculé par formule (rapport, différence entre deux groupes) est admis en `egalites` avec `formule` et `composantes`, même si ses lignes sources restent des ventilations dans d'autres dimensions.
- **Rattachements tranchés** (D33) : administration en ligne → `logement_cadre_vie` ; parité politique → `egalites` ; prisons et détention provisoire → `democratie` ; adhésion syndicale (DREES SDASSYND_1) → candidat `democratie` ; corruption et confiance dans les institutions : `incontournable: non` (règle des 3 cadres) mais `retenir`. Famille de composites : un concept distinct (ex. WGI « État de droit » et « contrôle de la corruption ») = une famille distincte.
- **Bornes du vérificateur** : `premiere_annee` ≥ 1700 (D32).


## 9. Compléments v1.2 (décisions D34 à D36 du 14/10/2026, issues des audits et des missions niveau_de_vie, planete, travail)

**Familles et variantes (D35)**
- **Famille = concept substituable.** Deux séries sont de la même famille si l'une peut remplacer l'autre pour l'utilisateur (même concept, lectures voisines). Les indices composites qui mesurent le même concept global (qualité de la démocratie : V-Dem libéral, Freedom House, WGI « voix et responsabilité ») forment **une** famille avec une variante principale ; un sous-indice qui mesure un concept distinct (État de droit, contrôle de la corruption, liberté de la presse) forme sa propre famille. Le producteur n'est pas un critère de famille.
- **Total principal, par habitant en variante** quand la cible officielle est exprimée en volume (émissions, SNBC) ; inversement, par habitant principal quand la lecture publique est par tête (empreinte, consommation).
- **Ventilations de second rang** (par produit, par branche, par sous-catégorie) : écartées en bloc par règle motivée quand une variante de premier rang porte déjà l'information.
- **Ventilations par sexe** : renvoyées à `egalites` (`autre_dimension:egalites`) quand l'écart correspondant y existe déjà ; sinon gardées en variantes dans la dimension du concept.
- **Séries trimestrielles ou mensuelles** : variante principale seulement s'il n'existe aucune série annuelle de même définition ; sinon variante.
- **Eurostat principal quand l'INSEE ne publie pas le niveau** (ex. revenu disponible ajusté par habitant) : l'INSEE reste principal à définition égale quand il publie le niveau.

**Écarts construits et séries calculées (D34)**
- Toute fiche calculée par le projet (écart, rapport, taux recalculé, agrégation d'un fichier) porte `composantes` (liste des `serie_id` utilisés, avec leurs modalités) et `formule` (expression normalisée : `A - B`, `A / B * 100`, `somme(…) / somme(…)`), plus la première année lue de **chaque** composante.
- Les écarts dont l'optimum est la parité (femmes-hommes, origine) sont exprimés en **valeur absolue** `|A − B|`, sens `bas`, sauf exception motivée dans la fiche.
- « Série quasi constante » n'est pas un motif d'écart : la fiche est `retenir_variante` ou `sens: ambigu` avec motif.
- **Recoupement obligatoire** : une série calculée par le projet est recoupée avec au moins trois valeurs officielles publiées avant d'être `retenir` ; le champ du fichier source (description du jeu) est lu avant tout calcul ; les points non recoupés sont signalés dans `qualite`.
- **Composites** : champ `annee_reference: observation|edition` obligatoire (année couverte vs année de publication).

**Vérifications (D36)**
- Avant de déclarer une série « non cataloguée », chercher dans **toutes** les long-lists et dans `catalogues/*_non.csv.gz` ; le vérificateur avertit quand une ligne de maintenance cite un jeu présent dans un catalogue.
- Chaque variante porte un `serie_id` unique.
- Quand une décision change une règle, la session mère joint la liste des fiches déjà fusionnées à reprendre.
- Frontière rémunération : salaire moyen réel, bas salaires et pauvreté en emploi → `travail` (qualité de l'emploi) ; revenus et niveau de vie des ménages → `niveau_de_vie`.
- Chaque agent travaille dans un sous-dossier de travail propre (`tmp/<mission>/`, ignoré par git) : le bac à sable est partagé entre agents parallèles.
