# Audit croisé M06 — dimension `democratie`

Agent auditeur M06 (session neuve, n'ayant pas participé à M05 `democratie`), 14 octobre 2026. Branche `m06-democratie`, créée depuis `origin/main` au commit `1a0697c` (fiches fusionnées par la PR #11, puis D31-D33 et vérificateur v1.1). Matériau audité : les 32 fiches `indicateurs/democratie/*.yaml`, `docs/validation/validation_democratie.csv`, `preselection_democratie.csv`, `preselection_democratie_lignes.csv`, `regles_preselection_democratie.csv`, le journal et le compte rendu M05 `democratie`, la long-list `catalogues/longlist_democratie.csv.gz` et les sorties du robot M04 (`docs/sources/series/`). **Aucune fiche, aucun tableau, aucun script ni aucun catalogue n'a été modifié** : ce rapport propose, un agent correcteur (ou la session mère) corrige. Le déroulé est dans `docs/cr/M06_democratie_journal.md`.

Contrôle préalable : `python scripts/verifier_fiches.py --dimension democratie` (vérificateur v1.1, sans `--tableau`) → 0 erreur, 1 avertissement attendu (`citoyennete_active`, jeu `ilc_scp19` hors catalogue des séries) ; 32 fiches, 24 familles, 22 `retenir`, 7 `retenir_variante`, 3 `ecarter`, 10 déclaratives, 11 composites, 10 « à vérifier », 12 incontournables, 100 variantes, 0 ligne prise par une autre dimension.

Nature des constats : **F** = erreur factuelle (source et valeur attendue citées) ; **A** = alignement sur une décision postérieure à M05 (D32, D33), sans faute de M05 ; **J** = désaccord de jugement (à trancher par la session mère ou Léo) ; **O** = oubli.

## 0. Avis global : `corrections_necessaires`

La structure de M05 tient : les concepts nommés par `dimensions.yaml` ont tous une fiche, la règle des composites (D18) est appliquée avec une variante principale par famille et des exceptions motivées, les rattachements A8 (parité → `egalites`) et A7 (administration en ligne → `logement_cadre_vie`) sont respectés, et toutes les valeurs relues pour les séries INSEE, Eurostat, Banque mondiale, OCDE, V-Dem, RSF et WJP sont exactes. Mais quatre groupes de problèmes doivent être réglés avant la validation de Léo :

1. **La participation électorale recalculée par le robot est fausse avant 2012** (F, le plus grave) : le recoupement avec les résultats officiels montre une surestimation de 0,51 point en 2002 et de 0,96 point en 2007 pour la présidentielle (inscrits incomplets), une sous-estimation de 7,6 points pour les municipales de 2008 (fichier limité aux communes de plus de 3 500 habitants) et un écart inexpliqué de −1,45 point pour les régionales de 2004. Pour les législatives, l'entrée des Français de l'étranger en 2012 crée une rupture de champ que la fiche ne documente pas. Les scrutins de 2012 à 2026 recoupés sont exacts.
2. **Freedom House** (F) : la fiche affirme que les années du relais OWID sont celles des éditions du rapport ; elles sont en réalité les années couvertes (édition = année + 1).
3. **Décisions D32 et D33 non encore appliquées** (A) : `premiere_annee` des trois séries V-Dem ramenée à 1900 au lieu de 1789 ; fiches WGI « État de droit » et « contrôle de la corruption » toujours dans la famille de producteur `wgi` ; adhésion syndicale (SDASSYND_1) sans fiche ; lignes de prisons de la long-list `securite` encore écartées là-bas.
4. **Un oubli à trancher** (O) : la participation en ligne à des consultations ou votes sur des sujets civiques ou politiques (Eurostat `isoc_ci_ac_i`, `I_IUVOTE`, 2011-2025, 10 points, éligible) est dans la long-list `logement_cadre_vie` alors qu'elle relève du contenu « participation » de `democratie`.

Chiffres : **29 fiches auditées sur 32** (les 3 autres ont reçu un contrôle léger) — **18 `conforme`, 10 `a_corriger`** (5 F, 5 A), **1 `non_verifiable`** (source primaire de `voix_pouvoirs_publics`). 4 oublis, 7 points de cohérence inter-dimensions, 8 désaccords de jugement. Liste ordonnée des corrections : §10.

## 1. Échantillon

| Règle (fiche M06 et consigne de la session mère) | Fiches |
|---|---|
| `recommandation: ecarter` (3) | `depenses_tribunaux`, `signalement_police`, `participation_departementales` |
| `incontournable: oui` (12, dont 1 déjà comptée) | `citoyennete_active`, `democratie_liberale_vdem`, `democratie_participative_vdem`, `liberte_presse_rsf`, `voix_pouvoirs_publics`, `voix_responsabilite_wgi`, `participation_presidentielle`, `_legislatives`, `_europeennes`, `_municipales`, `_regionales` (+ `_departementales`) |
| « À vérifier » au journal M05 (éligibilité `a_verifier` : 10, dont 7 déjà comptées ; raccordement `a_etudier` : 1 nouvelle) | `confiance_gouvernement`, `confiance_parlement`, `confiance_administration` ; `occupation_carcerale` |
| Toutes les composites (11, dont 4 déjà comptées) | `controle_corruption_wgi`, `etat_de_droit_wgi`, `etat_de_droit_wjp`, `liberte_academique_vdem`, `liberte_expression_vdem`, `libertes_freedom_house`, `perception_corruption_cpi` |
| Participation électorale (6) | déjà comptées (incontournables) |
| 20 % des 18 « autres » fiches (ni `ecarter` ni incontournables), soit 3,6 arrondi à 4, tirées parmi les 7 non retenues d'office | `detention_provisoire`, `confiance_police`, `confiance_ecole`, `independance_justice_percue` |

Tirage : `random.Random(20261014).sample(pool, 4)` en Python 3, `pool` = liste triée `['confiance_armee', 'confiance_ecole', 'confiance_hopital', 'confiance_justice', 'confiance_police', 'detention_provisoire', 'independance_justice_percue']`, **graine 20261014** (même graine que les audits `securite` et `liens_bien_etre`). Total : **25 fiches d'office + 4 tirées = 29**. Contrôle léger (valeurs BDM relues, définition) des 3 restantes : `confiance_armee`, `confiance_justice`, `confiance_hopital`, sans constat.

## 2. Fiches auditées

Sources lues par WebFetch le 14/10/2026 (détail en annexe) ; extraits du robot lus dans le dépôt.

| Fiche | Motif | Source consultée | Verdict | Nature | Correction attendue (détail aux §3 à §7) |
|---|---|---|---|---|---|
| `participation_presidentielle` | incontournable, à vérifier | sortie du robot ; archives des résultats du ministère (2002, 2007) ; Conseil constitutionnel (2012, 2022) | **a_corriger** | F | Valeurs 2002 et 2007 fausses (72,11 et 84,73 % contre 71,60 et 83,77 % officiels) : champ des inscrits incomplet ; rupture de champ en 2012 (§3). |
| `participation_legislatives` | incontournable, à vérifier | sortie du robot ; création des circonscriptions des Français de l'étranger (premières élections en juin 2012) | **a_corriger** | F | Documenter la rupture de champ de 2012 (Français de l'étranger) au lieu de « inclusion avant 2012 à vérifier » ; 2002 et 2007 non recoupés (pages officielles non lisibles) (§3). |
| `participation_europeennes` | incontournable, à vérifier | sortie du robot | conforme | — | Réserve : 1999-2009 non recoupés (pages des archives en erreur à l'outil). |
| `participation_municipales` | incontournable, à vérifier | sortie du robot ; Maire-info (chiffre définitif du ministère, 11/03/2008) ; data.gouv.fr (description du jeu) ; communiqué du ministère (2026) | **a_corriger** | F | 2008 : 58,86 % sur les seules communes de plus de 3 500 habitants contre 66,5 % officiels (France entière) ; retirer 2008 ou le marquer non comparable (§3). |
| `participation_regionales` | incontournable, à vérifier | sortie du robot ; archives du ministère (2004) | **a_corriger** | F | 2004 : 59,39 % contre 60,84 % officiels (−1,45 point, 724 000 votants manquants) ; cause à trouver avant usage (§3). |
| `participation_departementales` | ecarter, incontournable | sortie du robot | conforme | (J) | Chiffres exacts (19,6-21,4 millions d'inscrits aux cantonales, 42,7 millions en 2015) ; motif hors liste de la méthode (§7, J3). |
| `voix_pouvoirs_publics` | incontournable, à vérifier | extrait OCDE du robot ; OCDE *How's Life? 2020* (définition) | **non_verifiable** | — | Valeurs exactes (26,27 % et 57,62 % en 2023) ; la source primaire déclarée (enquête Confiance de l'OCDE) n'a pas pu être confirmée : l'OCDE définit l'indicateur sur PIAAC (16-65 ans), unité que porte la base (§5.3). |
| `citoyennete_active` | incontournable, hors long-list | API Eurostat `ilc_scp19` | conforme | — | 24,8 % (2015), 11,9 % (2022), sans drapeau ; libellé français de AC43A : « Initiatives citoyennes ». |
| `democratie_liberale_vdem` | incontournable, composite | métadonnées OWID ; CSV OWID filtré France ; sortie du robot | **a_corriger** | A | `premiere_annee: 1789` (et non 1900, borne levée par D32) ; ajouter `faible_variation` (0,789 à 0,822 depuis 2000) par cohérence. |
| `democratie_participative_vdem` | incontournable, composite | CSV OWID filtré France ; sortie du robot | **a_corriger** | A | `premiere_annee: 1789`. |
| `liberte_expression_vdem` | composite | sortie du robot | **a_corriger** | A | `premiere_annee: 1789`. |
| `liberte_academique_vdem` | composite | sortie du robot | conforme | — | 1900-2025, 27 valeurs distinctes, 0,8 en 2025 : exact (la série commence bien en 1900). |
| `liberte_presse_rsf` | incontournable, composite | extraits RSF du robot (2002-2026) | conforme | (J) | Valeurs exactes (3,25 en 2002 au rang 11 ; 78,4 en 2013 ; 77,4 en 2021 ; 78,53 en 2022 ; 76,68 en 2026 au rang 25) ; année = année du classement (§7, J6). |
| `libertes_freedom_house` | composite | CSV OWID filtré France ; métadonnées OWID ; extrait Freedom House 2013-2024 | **a_corriger** | F | Années OWID = années couvertes (édition = année + 1), pas années d'édition ; « OWID relaie l'édition 2025 » → édition 2026 ; décrire la baisse de 95-96 à 89 (§4.2). |
| `voix_responsabilite_wgi` | incontournable, composite | API Banque mondiale `GOV_WGI_VA.EST` et `.SC` ; documentation WGI | conforme | (J) | Valeurs exactes ; documentation désormais lue ; note de tendance à reformuler (§7, J5). |
| `etat_de_droit_wgi` | composite | API Banque mondiale `GOV_WGI_RL.EST` | **a_corriger** | A | 0,97 en 2025 exact ; famille de concept propre (D33) au lieu de `wgi` (§4.1). |
| `controle_corruption_wgi` | composite | API Banque mondiale `GOV_WGI_CC.EST` | **a_corriger** | A | Idem (D33). |
| `etat_de_droit_wjp` | composite | extrait WJP 2025 du robot | conforme | — | 12 éditions, 0,764 (2012-2013) → 0,724 (2025) : exact. |
| `perception_corruption_cpi` | composite | CSV OWID filtré France (2012-2024) ; extrait OCDE 14_6 (2025) ; API Eurostat `sdg_16_50` **refusée (HTTP 429)** | conforme | — | 71 (2012), 72 (2018, 2022), 67 (2024), 66 (2025) exacts ; motif « de 72 à 66 » à lire « de 71 (2012) à 66 (2025) » (mineur). Absence de drapeau Eurostat non revérifiée. |
| `confiance_gouvernement` | à vérifier | extrait OCDE du robot ; définitions OCDE (extrait du robot, p. 37) | conforme | — | 37,33 % (2025), 7 points (moyennes Gallup 2006-2007 puis triennales), 15 ans ou plus : exact. |
| `confiance_parlement` | à vérifier | extrait OWID du robot | conforme | — | 33,08 % (2022), vagues 1984, 1993, 2004, 2010, 2022. |
| `confiance_administration` | à vérifier | extrait OWID du robot | conforme | — | 52,56 % (2022), mêmes vagues. |
| `occupation_carcerale` | raccordement `a_etudier` | BDM 001779317 | conforme | — | 116,3 (2012), 103,4 (2020), 129,5 (2024) : exact ; « places opérationnelles » non relu (la fiche le dit). |
| `depenses_tribunaux` | ecarter | API Eurostat `sdg_16_30` | conforme | — | 54,3 € (2000), 94,0 € (2020), 120,6 € (2024, `p`) ; aucune valeur 2025 ; écart conforme à la charte §3.4 (moyen budgétaire). |
| `signalement_police` | ecarter | extrait OCDE ODD 16 du robot | conforme | — | 2010-2019 et 2021-2022 (12 points), dernière valeur 22 % ; sens ambigu et série arrêtée (D32) cohérents. |
| `detention_provisoire` | tirage | BDM 010596049 ; métadonnées INSEE 16.i3 | conforme | (J) | 24,7 % (2012) à 29,0 % (2018), 26,7 % (2025, provisoire, au 30 août) ; rupture 2019 confirmée par l'INSEE (§7, J4). |
| `confiance_police` | tirage | BDM 010596051 ; métadonnées INSEE 16.i4 | conforme | — | 66 (2013, 2020), 75 (2016), 78 (2017), 71 (2024). |
| `confiance_ecole` | tirage | BDM 010596053 | conforme | — | 73 (2013), 65 (2018), 74 (2022), 68 (2024). |
| `independance_justice_percue` | tirage | API Eurostat `sdg_16_40` | conforme | — | 54 (2016), 59 (2019), 56 (2022), 51 (2025), sans drapeau. |

Contrôles transversaux de l'échantillon : `type` (`resultat`, sauf `depenses_tribunaux` en `moyen`), `declaratif` (`oui` pour la confiance, l'indépendance perçue et la voix ; `non` pour la participation, la citoyenneté active, le signalement et les composites d'experts) et `frequence: irreguliere` (12 fiches) sont conformes à la méthode §4 et à D17. Les 12 incontournables correspondent au seul concept « participation et voix politique » du §5 du crosswalk ; corruption et confiance restent `non` et `retenir` (D33).

## 3. Recoupement de la participation électorale (robot M04 contre résultats officiels)

| Scrutin (1er tour) | Robot = fiche | Officiel | Écart | Inscrits robot / officiels | Source officielle |
|---|---|---|---|---|---|
| Présidentielle 2002 | 72,11 % | **71,60 %** (29 497 888 / 41 197 964) | **+0,51** | 40 467 855 / 41 197 964 (−730 109) | archives des résultats du ministère, page « France entière » |
| Présidentielle 2007 | 84,73 % | **83,77 %** (37 254 242 / 44 472 834) | **+0,96** | 43 319 652 / 44 472 834 (−1 153 182) | idem |
| Présidentielle 2012 | 79,48 % | 79,48 % (36 584 399 / 46 028 542) | 0 | 46 028 571 / 46 028 542 | Conseil constitutionnel, décision 2012-152 PDR |
| Présidentielle 2022 | 73,69 % | 73,69 % (35 923 707 / 48 747 876) | 0 | identiques | Conseil constitutionnel, décision 2022-195 PDR |
| Régionales 2004 | 59,39 % | **60,84 %** (25 453 092 / 41 835 232) | **−1,45** | 41 638 437 / 41 835 232 (−196 795 ; votants −723 982) | archives du ministère, « France entière » |
| Municipales 2008 | 58,86 % | **66,5 %** (chiffre définitif, France entière) | **−7,6** | 26 252 771 inscrits seulement | ministère, 11/03/2008, cité par Maire-info |
| Municipales 2026 | 57,12 % | 57,1 % (48,7 millions d'électeurs) | ≈ 0 | 48 690 084 | communiqué du ministère |

Le second tour de la présidentielle 2002 est aussi décalé (80,28 % contre 79,71 %). Constats :

1. **Présidentielle** : de 2012 à 2022 le calcul est exact ; en 2002 et 2007 le fichier agrégé compte 0,73 et 1,15 million d'inscrits de moins que les résultats officiels, ce qui surestime la participation d'un demi-point à un point (les inscrits manquants votent moins, hypothèse compatible avec l'absence des Français de l'étranger, non vérifiée). La baisse 2007 → 2012 est donc exagérée : −5,25 points dans la fiche contre −4,29 points officiels. La valeur INSEE « France » (BDM 001778320 : 80,7 % en 2012, 79,0 % en 2017, 75,3 % en 2022), plus élevée de 1,2 à 1,6 point, est compatible avec un champ hors Français de l'étranger (hypothèse).
2. **Législatives** : les Français de l'étranger n'élisent des députés que depuis juin 2012 (onze circonscriptions créées après la révision constitutionnelle de 2008). Le saut des inscrits du fichier (43,57 millions en 2007, 46,08 millions en 2012) traduit donc une **rupture de champ réelle**, que la fiche présente comme « à vérifier ». Les valeurs officielles de 2002 et 2007 n'ont pas pu être lues (seul le second tour 2007 est en ligne aux archives).
3. **Municipales 2008** : le jeu data.gouv.fr « Données des élections agrégées » précise que les municipales de 2008 ne couvrent que les communes de plus de 3 500 habitants. La valeur de la fiche (58,86 %) n'est pas la participation nationale (66,5 %) et fait croire à une hausse en 2014 (63,55 %) alors que la participation a baissé.
4. **Régionales 2004** : écart de −1,45 point, avec 724 000 votants manquants pour 197 000 inscrits manquants ; cause non trouvée.
5. **Européennes 1999-2009, législatives 2002-2007** : non recoupés (pages des archives en erreur à l'outil). Les scrutins de 2012-2026 recoupés (présidentielles 2012 et 2022, municipales 2026) sont exacts à l'arrondi près.

**Corrections attendues** : (a) recalculer toute la famille sur un champ homogène — le plus simple est d'exclure, pour tous les scrutins, les bureaux des Français de l'étranger (champ « France hors étranger », comparable à l'INSEE) si le fichier les identifie, puis de vérifier que 2002 et 2007 retombent sur ce champ ; à défaut, couper la présidentielle et les législatives à 2012 ou documenter la rupture de 2012 avec `raccordement: a_etudier` ; (b) retirer 2008 de `participation_municipales` (`premiere_annee: 2014`, 3 points) ou le marquer non comparable ; (c) marquer 2004 de `participation_regionales` `a_recouper` tant que l'écart n'est pas expliqué ; (d) corriger les notes et motifs qui citent ces valeurs ; (e) compléter la ligne 24 de `docs/cr/maintenance_catalogues.md` avec ces chiffres.

## 4. Règle des composites (D18, D33)

### 4.1 Application

| Famille | Variante principale | Fiches non principales | Sous-indices en `variantes` | Constat |
|---|---|---|---|---|
| `vdem` | `democratie_liberale_vdem` | `democratie_participative_vdem` (`retenir_variante`) | 21 (indices électoral, délibératif, égalitaire ; libertés, État de droit, contraintes sur l'exécutif ; société civile ; 7 indices de corruption) | conforme D18 |
| `liberte_expression_vdem`, `liberte_academique_vdem` | elles-mêmes | — | 5 questions médias ; 0 | exception motivée (concepts nommés par la dimension) |
| `wgi` | `voix_responsabilite_wgi` | `etat_de_droit_wgi`, `controle_corruption_wgi` (`retenir_variante`) | 7 (score 0-100, efficacité, réglementation, stabilité politique) | **contraire à D33** : ces deux fiches deviennent des familles de concept distinctes |
| `freedom_house` | `libertes_freedom_house` | — | 9 (droits politiques, libertés civiles, catégories A-G) | conforme |
| `wjp` | `etat_de_droit_wjp` | — | 8 facteurs | conforme ; les 8 variantes portent le même `serie_id` (URL du fichier), sans le facteur : identifiant à préciser |
| `rsf` | `liberte_presse_rsf` | — | 6 (relais OWID, 5 sous-scores) | conforme |
| `cpi` | `perception_corruption_cpi` | — | 2 doublons (OCDE, OWID) | conforme |

Correction (A) : `etat_de_droit_wgi` et `controle_corruption_wgi` → familles propres (`famille` = leur `id`), `variante_principale: oui`, `recommandation: retenir`, retrait de la phrase « Exception à la règle des familles », tableau régénéré. Si la session mère lit D33 comme « une famille par concept tous producteurs confondus », les familles seraient `etat_de_droit` (WJP + WGI) et `corruption` (CPI + WGI) avec une seule principale : voir J1.

### 4.2 Freedom House : convention d'années (F)

Le CSV OWID filtré sur la France donne 95 (2002-2004), 93 (2005), 94 (2006), 93 (2007), 96 (2008-2009), 95 (2010-2014), **91 (2015)**, 90 (2016-2020), **89 (2021-2025)**. Le fichier Freedom House « All_data_FIW_2013-2024 » (extrait du robot) donne, par **édition** : 95 (2013-2015), **91 (2016)**, 90 (2017-2021), **89 (2022-2024)**. L'année OWID vaut donc édition − 1 : c'est l'année couverte. Les métadonnées OWID citent « Freedom House (2026) », période 2002-2025, mise à jour du 23/03/2026. **Corrections** : `definition` (« années = éditions du rapport » → « années couvertes ; l'édition du rapport est l'année suivante ») ; `qualite` (`annee_edition` → `annee_couverte`) ; `notes` (préciser que « 90, puis 89 en 2022-2024 » sont des éditions, soit 2021-2023 en années OWID) ; `note_pertinence` (« OWID relaie l'édition 2025 » → édition 2026, données 2025 ; le score « varie très peu » depuis 2016 mais a perdu 6 à 7 points depuis 2002-2014).

## 5. Erreurs factuelles et points non vérifiables (détail)

1. **Participation électorale** (4 fiches) : §3.
2. **Freedom House** : §4.2.
3. **`voix_pouvoirs_publics`, source primaire** (non vérifiable) : la fiche attribue la mesure 8_1 à l'enquête de l'OCDE sur les déterminants de la confiance (vagues 2021 et 2023). *How's Life? 2020* définit « Having a say in government » à partir de l'enquête PIAAC (16-65 ans, question « People like me don't have any say in what the government does », désaccord = avoir son mot à dire) ; la base porte l'unité `PT_POP_Y16T65`, propre à PIAAC, alors que les années 2021 et 2023 évoquent l'enquête Confiance. Le PDF de définitions de l'OCDE est refusé à l'outil (robots.txt). **Attendu** : écrire « source primaire à vérifier (PIAAC ou enquête Confiance de l'OCDE) » et ajouter `source_a_verifier` tant que la comparabilité 2021/2023 n'est pas établie.

## 6. Alignements sur les décisions postérieures à M05 (D32, D33)

1. **V-Dem, `premiere_annee`** : D32 admet une première année ≥ 1700. Les métadonnées OWID (« Date range 1789-2025 », V-Dem v16, mise à jour du 17/03/2026) et la sortie du robot donnent 1789 pour `democratie_liberale_vdem`, `democratie_participative_vdem` et `liberte_expression_vdem` : remettre 1789 et supprimer la phrase « premiere_annee ramenée à 1900 » des notes (« données lues, jamais saisies », méthode §4). `liberte_academique_vdem` commence bien en 1900.
2. **WGI** : §4.1.
3. **Adhésion syndicale** (D33) : voir O1.
4. **Lignes de prisons** (D33 : « lignes prisons et détention provisoire → democratie ») : voir I2.

## 7. Désaccords de jugement

- **J1. Familles de composites : producteur ou concept ?** D18 (dans `dimensions.yaml`) raisonne par producteur ; la méthode §1 définit la famille par la substituabilité ; D33 commence à raisonner par concept (WGI). Trois indices globaux de qualité démocratique — V-Dem libérale, Freedom House, WGI voix et responsabilité — sont substituables mais forment trois familles, toutes `retenir` ; de même la liberté de la presse (RSF et l'indice V-Dem d'expression, qui inclut les médias), l'État de droit (WJP, WGI, et l'indice V-Dem d'État de droit en variante) et la corruption (CPI, WGI, et sept indices V-Dem en variantes). Si D33 vaut « une famille par concept », l'ordre de la méthode (niveau 1 > 2, série la plus longue) désignerait les WGI comme principales pour l'État de droit (1996-2025, API) et la corruption (25 points contre 14 pour le CPI), à l'inverse du choix de M05 (WJP et CPI, plus spécialisés). À trancher ; dans tous les cas, le tableau de validation devrait signaler à Léo les groupes « l'un ou l'autre ». Les autres sous-indices WGI (efficacité, réglementation, stabilité politique) ne sont pas « le même indicateur sous une autre forme » (méthode §1) : un écart en bloc motivé serait plus juste qu'un rang de variante.
- **J2. Source principale de la participation** : garder le fichier du ministère (profondeur) reste justifié, à condition d'homogénéiser le champ (§3). L'INSEE (niveau 1) ne couvre que 2012-2024.
- **J3. `participation_departementales`** : « champ rompu en 2015 » n'est pas un motif de la méthode §3. La partie 2015-2021 (2 points) est éligible au sens de D17 et D28 ; par cohérence avec D32 (jamais d'écart pour la seule brièveté) et avec les municipales et régionales retenues en variante, soit la garder en `retenir_variante` sur 2015-2021, soit motiver l'écart autrement.
- **J4. `detention_provisoire`, rupture 2019** : la fiche de métadonnées INSEE 16.i3 confirme une rupture (« revu à la baisse ») au passage à Genésis ; `raccordement: oui` ne couvre que 2008-2009. Comme pour les ruptures CVS/VRS de `securite`, proposer `a_etudier` pour 2019, sinon l'indice affichera une amélioration artificielle (29,0 % en 2018, 25,9 % en 2019).
- **J5. WGI, échelle et lecture** : la documentation WGI (lue) indique que l'estimation suit une loi normale de moyenne proche de zéro et que les scores 0-100 sont produits « pour faciliter les comparaisons entre pays et dans le temps », avec intervalles de confiance à 90 %. Envisager le score 0-100 (`.SC`) comme série principale. La note « la France recule de 1,48 (2005) à 1,16 (2025) » part du pic : la valeur était de 0,95 en 2000 et de 0,91 en 2003 ; écrire la trajectoire complète et signaler la volatilité de 2003-2005.
- **J6. Conventions d'années des composites** : V-Dem et Freedom House (OWID) datent l'année observée ; RSF et le WJP datent l'édition (classement 2026 publié en 2026 sur l'année 2025). Documenter la convention dans chaque fiche, voire décaler RSF et WJP d'un an.
- **J7. Incontournables** : `liberte_presse_rsf` est `oui` (proxy SSF), mais `liberte_expression_vdem` et `libertes_freedom_house` sont `non` alors que la table des cadres cite aussi « indices V-Dem » pour la même ligne SSF. C'est défendable, à expliciter dans le motif.
- **J8. Confiance par vagues espacées** (`confiance_parlement`, `confiance_administration` : 3 vagues depuis 2000, la dernière en 2022) : `retenir` conforme à D17 et au précédent `solitude`. Il reste à rappeler à Léo que la valeur reportée vieillit vite (la fiche le dit).

## 8. Complétude

**Long-list** : les 250 lignes et les 3 lignes importées de `securite` sont toutes affectées (vérificateur). Les 30 lignes éligibles écartées en bloc (activité des tribunaux 8, motifs de non-usage de l'administration en ligne 12, classes de `sdg_16_40` 5, condamnés écroués 2, mis en cause 2, polarisation 1) ont des motifs recevables ; la valeur citée pour l'activité pénale (6 439 affaires reçues pour 1 021 résolues pour 100 000 habitants en 2022) est exacte (API `crim_crt_case`), et la série présente un saut de définition en 2016 (1 513 puis 7 492 affaires reçues). Les 2 lignes « à vérifier » écartées (votes blancs, consultation réglementaire) le sont pour sens ambigu ou mesure de moyen.

**Séries non composites demandées par la consigne** :

| Concept | Constat |
|---|---|
| Confiance dans les institutions INSEE ODD 16.i4 | Les 5 institutions (armée, police, justice, école, hôpital) ont leur fiche ; copies Melodi en doublons ; valeurs relues. EU-SILC (système politique, justice, police) : jeu `ilc_pw03b`, 2013 seulement (API), non éligible ; `ilc_pw03` ne porte plus que la confiance envers autrui. Confiance dans les institutions de l'UE (`sdg_16_60`) : jeu interrompu (« DISCONTINUED »), pas un oubli. |
| Votes blancs | Écartés en bloc pour sens ambigu : conforme. |
| Détention provisoire | Fiche `retenir`, raccordée à Eurostat ; voir J4. |
| Adhésion syndicale (D33) | **Oubli** (O1). |
| Atteintes à la probité | Inventaire SSMSI : 2016-2023, 8 points, non éligible ; écart conforme. |
| Taux de signalement | Fiche `signalement_police` (écartée) avec trois variantes (ODD 16.3.1 vols avec violence, taux de dépôt de plainte CVS) : conforme. |

**Oublis** :

| # | Oubli | Données (lues) | Importance | Proposition |
|---|---|---|---|---|
| O1 | **Adhésion à un syndicat** (DREES, SDASSYND_1 : « Vous personnellement, êtes-vous membre d'une organisation syndicale ? ») | couverture 2000-2002 et 2004-2025 (25 années), taux de réponse 2025 = 1,000 (`drees__barometre_2000_2025_couverture.csv`) ; valeurs non calculées par le robot | forte (D33) | Fiche hors long-list `adhesion_syndicale` sur le modèle de `liens_bien_etre/vie_associative` : `geo: FM`, `declaratif: non`, `statut_serie: a_calculer`, `preuve` vers la sortie « couverture », ligne de maintenance pour le calcul (modalité 1, non-réponses au dénominateur). Sens `haut` à motiver (engagement dans la représentation collective). |
| O2 | **Participation en ligne à des consultations ou votes sur des sujets civiques ou politiques** (Eurostat `isoc_ci_ac_i`, `I_IUVOTE`) | 2011-2025, 10 points, éligible, ligne `estat-005592` de la long-list `logement_cadre_vie` ; les mesures voisines `I_IUPOL`, `I_IUPOL1`, `I_IUPOL2` (exprimer des opinions politiques en ligne) ont 1 à 5 points | moyenne | Ce n'est pas de l'administration en ligne (D33) mais de la participation citoyenne : règle `longlist = logement_cadre_vie` dans la présélection `democratie` (fiche ou variante de `citoyennete_active`, à trancher), et règle `autre_dimension:democratie` pour M05 `logement_cadre_vie`. |
| O3 | Lignes de prisons restées en `securite` (`crim_pris_age`, `crim_pris_ctz`, `crim_pris_off`, `crim_pris_tri` `TRI_SPSD`, règle 1100 « activité répressive ») | 2008-2024, éligibles | faible (l'écart resterait probable : taux d'incarcération au sens ambigu) | Appliquer D33 : les importer dans la présélection `democratie` (écart en bloc motivé ici, ou fiche `taux_detention` en `sens: ambigu`). |
| O4 | Non-inscription sur les listes électorales | aucune série trouvée dans les catalogues INSEE (BDM, Melodi) | faible | Piste pour M04 (répertoire électoral unique de l'INSEE). |

Déjà signalés par M05 et non repris comme oublis : confiance dans le gouvernement et les partis (WVS/EVS, maintenance n° 25), citoyenneté active hors catalogue (n° 23). Vérifié sans résultat : la question DREES OG04_10 (préoccupation pour la situation politique) n'a été posée qu'en 2025.

**Incontournables du crosswalk** (§5) : « participation et voix politique » (Doughnut, SSF, OCDE, Eurostat) est couvert par 12 fiches, dont 11 `retenir` ou `retenir_variante` (seule `participation_departementales` est écartée). Corruption et confiance dans les institutions (deux cadres) ont des fiches `retenir` (D33). Les indicateurs Eurostat QoL de confiance dans le système judiciaire, le système politique et la police n'existent qu'en 2013 (`ilc_pw03b`) : leur absence est justifiée.

## 9. Cohérence inter-dimensions

Contrôle mécanique (séries principales, composantes et variantes ; lignes) des 32 fiches `democratie` contre les 105 fiches de `egalites`, `liens_bien_etre` et `securite` : **aucun identifiant commun, aucune série commune, aucune ligne commune**. Jeux partagés avec des mesures distinctes : `DS_NAT_SDG` (16.i3 et 16.i4 ici ; autres ODD ailleurs) et la base ODD 16 de l'OCDE (16.3.1 et 16.3.2 ici ; homicides et victimation en `securite`).

| # | Point | Proposition |
|---|---|---|
| I1 | Parité politique : `sdg_05_50` est en `egalites` (`femmes_parlement`), comme le veut A8 | Rien à corriger. |
| I2 | D33 « lignes prisons → democratie » appliqué aux 3 lignes `crim_pris_tri` `TRI_PRE` et `crim_pris_cap`, pas aux autres lignes `crim_pris_*` (règle 1100 de `securite`) | O3. |
| I3 | Taux de dépôt de plainte SSMSI (`m04-000297`, `m04-000298`) : variantes de `signalement_police` ici, référence pour documenter le sens des séries enregistrées de `securite` (audit M06 `securite`, §3) | Garder une seule affectation (ici) et les citer depuis `securite`. |
| I4 | Confiance dans l'école et l'hôpital : `democratie` par R5 ; ces lignes INSEE 16.i4 pourraient être reprises par M05 `education` et `sante` | Consigne `autre_dimension:democratie` pour ces dimensions. |
| I5 | Baromètre DREES : SDASSYND_2 (association) en `liens_bien_etre`, SDASSYND_1 (syndicat) attendu ici (D33) | O1, avec `geo: FM` et la même URL de pièce jointe (`barometre2000_2025_diff_csv`). |
| I6 | `ilc_scp19` : AC43A (citoyenneté active) ici, AC41A et AC42A (bénévolat) en `liens_bien_etre` (maintenance n° 31-32) | Cohérent. |
| I7 | `isoc_ci_ac_i` `I_IUVOTE` dans la long-list `logement_cadre_vie` | O2. |

## 10. Liste ordonnée des corrections (à faire par l'agent correcteur ou la session mère)

1. **Participation électorale** (§3) : recalculer la famille sur un champ homogène (hors Français de l'étranger, si le fichier les identifie) ou couper à 2012 ; documenter la rupture 2012 des législatives ; retirer ou marquer 2008 des municipales (champ ≥ 3 500 habitants) ; marquer 2004 des régionales `a_recouper` ; corriger les valeurs citées dans les motifs et notes (présidentielle 2002 : 71,60 % officiel ; 2007 : 83,77 %) ; compléter la ligne 24 de la maintenance.
2. **`libertes_freedom_house`** (§4.2) : convention d'années (année couverte), drapeau `annee_couverte`, notes et note de pertinence (édition 2026 ; baisse de 95-96 à 89).
3. **WGI, D33** (§4.1) : `etat_de_droit_wgi` et `controle_corruption_wgi` en familles propres, `variante_principale: oui`, `recommandation: retenir` (ou familles de concept selon J1).
4. **V-Dem, D32** (§6.1) : `premiere_annee: 1789` pour `democratie_liberale_vdem`, `democratie_participative_vdem`, `liberte_expression_vdem` ; notes corrigées ; `faible_variation` sur l'indice libéral.
5. **O1** : fiche hors long-list `adhesion_syndicale` (SDASSYND_1, `a_calculer`) et ligne de maintenance pour le calcul par le robot.
6. **O2** : rattachement de `I_IUVOTE` (`estat-005592`) à trancher, puis règle de présélection (`longlist = logement_cadre_vie`).
7. **O3 / I2** : importer les autres lignes `crim_pris_*` de `securite` dans la présélection `democratie` (écart en bloc motivé) et retirer `crim_pris_*` de la règle 1100 de `securite`.
8. **`voix_pouvoirs_publics`** (§5.3) : source primaire « à vérifier (PIAAC ou enquête Confiance) », drapeau `source_a_verifier`.
9. **Mineurs** : motif de `perception_corruption_cpi` (« de 71 en 2012 à 66 en 2025, maximum 72 ») ; `url_page` des WGI (page de documentation de la Banque mondiale) et mention « documentation lue » ; `serie_id` des 8 facteurs WJP à distinguer ; note de `voix_responsabilite_wgi` (trajectoire depuis 2000, J5) ; raccordement 2019 de `detention_provisoire` (J4).
10. Puis `python scripts/preselection.py --dimension democratie --maj-fiches`, `python scripts/verifier_fiches.py --dimension democratie --tableau` et `python scripts/verifier_fiches.py --dimension democratie` (0 erreur).

## 11. Questions pour la session mère

1. D33 pour les composites : « famille de concept » signifie-t-il une famille par sous-indice WGI (lecture minimale), ou une famille par concept tous producteurs confondus (État de droit : WJP + WGI ; corruption : CPI + WGI ; qualité démocratique globale : V-Dem + Freedom House + WGI) ? Dans le second cas, quelle variante principale (J1) ?
2. Participation : faut-il imposer le champ « hors Français de l'étranger » (comparable à l'INSEE et homogène depuis 2002) ou le champ France entière tronqué à 2012 ?
3. La participation en ligne (`I_IUVOTE`) relève-t-elle de `democratie` (participation) ou de `logement_cadre_vie` (numérique) ?
4. Les ruptures internes d'une série principale (détention provisoire 2019, comme CVS/VRS en `securite`) doivent-elles toujours porter `raccordement: a_etudier` ?
5. Faut-il harmoniser la convention d'année des composites (année observée plutôt qu'année d'édition) ?

## 12. Propositions pour la méthode commune

1. **Recoupement obligatoire des séries calculées par le projet** : toute série « calcul du projet » (fichier agrégé, microdonnées) doit être recoupée sur au moins trois points avec une valeur officielle publiée avant la recommandation `retenir`, recoupement cité dans `notes`. Le robot M04 pourrait produire un contrôle « somme des inscrits par scrutin contre total officiel ».
2. **Champ d'un fichier agrégé** : lire la description du jeu (data.gouv.fr) avant de calculer ; la limitation des municipales 2008 y était écrite.
3. **Convention d'année** : ajouter à la fiche un champ `annee_reference` (`observation` ou `edition`) pour les composites et les enquêtes publiées l'année suivante.
4. **Familles de composites** : écrire dans la méthode §1 la règle issue de D33 (famille = concept substituable, quel que soit le producteur) et ce qui va en variante (même indicateur sous une autre forme) ou en écart en bloc (autres sous-indices du producteur).
5. **Identifiants de variantes** : un `serie_id` doit désigner une seule série ; pour les fichiers à plusieurs colonnes ou feuilles, inclure la colonne ou le facteur (cas WJP).
6. **Décisions postérieures** : quand une décision (D32, D33) change une règle, la session mère joint la liste des fiches déjà fusionnées à reprendre (ici 5 fiches et 2 nouvelles lignes de présélection).

## Annexe — sources consultées (14/10/2026)

| Source | Usage |
|---|---|
| `https://www.archives-resultats-elections.interieur.gouv.fr/resultats/presidentielle_2002/FE.php`, `…/presidentielle_2007/FE.php`, `…/regionales_2004/FE.php` | résultats officiels « France entière » |
| `https://www.conseil-constitutionnel.fr/decision/2012/2012152PDR.htm` ; décision 2022-195 PDR (reprise par `blog.landot-avocats.net`, 13/04/2022) | présidentielles 2012 et 2022 |
| `https://www.maire-info.com/335-dabstention-au-premier-tour-des-elections-municipales-chiffre-definitif-article2-9465` | municipales 2008 (66,5 %, ministère) |
| `https://www.interieur.gouv.fr/actualites/communiques-de-presse/elections-municipales-et-communautaires-2026-bilan-chiffre-du-premier-et-du-second-tour` | municipales 2026 (57,1 %) |
| `https://www.data.gouv.fr/fr/datasets/6481e741d4cf002ec0efec9d/` | champ du fichier agrégé (municipales 2008 : communes de plus de 3 500 habitants ; 2001 absentes) |
| `https://alliancesolidaire.org/2022/05/19/les-deputes-des-francais-de-letranger/` | premières législatives des Français de l'étranger (juin 2012) |
| `https://api.worldbank.org/v2/country/FRA/indicator/GOV_WGI_{VA,RL,CC}.EST?source=3&format=json` ; `GOV_WGI_VA.SC` ; `https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation` | WGI |
| `https://ourworldindata.org/grapher/{liberal-democracy-index,participatory-democracy-index,freedom-score-fh,ti-corruption-perception-index}.csv?…&csvType=filtered&country=~FRA&time=…` ; métadonnées `….metadata.json` | V-Dem, Freedom House, CPI |
| API Eurostat : `sdg_16_30`, `sdg_16_40`, `ilc_scp19`, `ilc_pw03`, `ilc_pw03b`, `crim_crt_case` | dépenses, indépendance perçue, citoyenneté active, confiance EU-SILC, activité des tribunaux |
| BDM INSEE : 010596049 à 010596054, 001779317, 001778320 | détention provisoire, confiance, occupation carcérale, participation INSEE |
| `https://www.insee.fr/fr/statistiques/fichier/4997354/metadonnees-16.i3.pdf`, `…/metadonnees-16.i4.pdf` | définitions, rupture 2019, échantillon Cevipof |
| `https://www.oecd.org/en/publications/how-s-life/volume-/issue-_9870c393-en/full-report/component-15` | définition de « Having a say in government » (PIAAC) et de la participation électorale (présidentielle pour la France) |
| Extraits du robot (dépôt) : `interieur_elections__participation_par_scrutin.csv`, `owid__*`, `ocde__hsl_*`, `ocde__odd_16.csv`, `rsf__classement_*.txt`, `freedom_house__fiw_2013_2024_france.txt`, `wjp__historique_2025_essai_c.txt`, `drees__barometre_*`, `ssmsi__series_chronologiques.csv` | valeurs et couvertures |
| **Non lus** : API Eurostat `sdg_16_50` (HTTP 429, refus de l'outil après limitation de débit) ; `sdg_16_60` (erreur) ; pages des archives pour les présidentielles 2012, européennes 1999 et 2004, municipales 2008, législatives 2002 et premier tour 2007 (erreur ou contenu absent) ; PDF de définitions de l'OCDE (robots.txt) | — |
