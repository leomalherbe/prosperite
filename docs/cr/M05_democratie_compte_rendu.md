# Compte rendu — M05, fiches indicateurs de la dimension `democratie` (Démocratie et institutions)

Agent M05 democratie, 14 octobre 2026, branche `m05-democratie`, PR #11. Méthode commune suivie (`docs/methodo/33_methode_fiches_M05.md`) ; méthode détaillée, vérifications et contrôles : `docs/cr/M05_democratie_journal.md`.

## 1. Fait

| Livrable | Fichier |
|---|---|
| Règles de présélection (86 règles) | `docs/validation/regles_preselection_democratie.csv` |
| Présélection par groupe (86 groupes) et ligne à ligne (250 lignes de la long-list + 3 lignes de `securite`) | `docs/validation/preselection_democratie.csv`, `preselection_democratie_lignes.csv` (écrits par `scripts/preselection.py`) |
| 32 fiches YAML (schéma de la méthode commune, `socle_v1` vide) | `indicateurs/democratie/*.yaml` |
| Tableau de validation (18 colonnes, `decision_leo` vide) | `docs/validation/validation_democratie.csv` (écrit par `scripts/verifier_fiches.py --tableau`) |
| Corrections de catalogues à faire (7 lignes `a_faire`, n° 10 à 16) | `docs/cr/maintenance_catalogues.md` |
| Journal de méthode | `docs/cr/M05_democratie_journal.md` |

Contrôles : `python scripts/verifier_fiches.py --dimension democratie` → **0 erreur**, 1 avertissement attendu (`citoyennete_active`, série hors catalogue de séries, jeu `ilc_scp19` au catalogue des jeux) ; `pytest` : 394 réussis. Aucun fichier de `scripts/` ni de `src/` modifié.

## 2. Chiffres (avant l'audit ; chiffres à jour au §7)

- Long-list : 250 lignes (129 éligibles, 32 à vérifier, 89 non ; 64 composites). Décisions : 31 lignes `fiche` (+ 1 fiche hors long-list), 100 lignes `variante_de` (dont 3 importées de `securite`), 82 `ecarte_en_bloc` (dont 58 lignes d'administration en ligne non éligibles ou sans intérêt propre, 10 d'activité des tribunaux), 40 `autre_dimension` (38 `logement_cadre_vie`, 2 `egalites`).
- **32 fiches, 24 familles : 22 `retenir`, 7 `retenir_variante`, 3 `ecarter`** ; 10 déclaratives (confiance, indépendance perçue de la justice, voix) ; 11 composites ; 12 irrégulières (D17), dont 10 « à vérifier » dans la long-list ; 1 hors long-list ; 12 incontournables ; 100 variantes.
- Composites par famille de producteur (D18) : V-Dem (démocratie libérale principale, participative en variante ; liberté d'expression et liberté académique en familles de concept), WGI (voix et responsabilité principale ; État de droit et contrôle de la corruption en variantes), Freedom House, WJP, RSF, CPI (une fiche principale chacun ; sous-indices en `variantes`).

## 3. Choix structurants (détail : journal §2)

1. **Participation électorale** : une fiche par scrutin dans une famille (principale : présidentielle) ; source principale = fichier agrégé du ministère de l'Intérieur (niveau 2, 1999-2026) plutôt que la BDM de l'INSEE (niveau 1, 2012-2024), pour la profondeur ; `frequence: irreguliere` et `formule` (report de la dernière valeur) ; champ France entière, inscrits de 2002-2007 à vérifier ; départementales écartées (rupture de champ en 2015, cantonales par moitié).
2. **Composites** : une famille par producteur, une variante principale (concept le plus proche de la dimension), sous-indices en variantes ; exceptions motivées : liberté d'expression et liberté académique (concepts nommés dans la dimension) en familles propres, État de droit et contrôle de la corruption WGI en fiches non principales (séries depuis 1996 quand le WJP et le CPI commencent en 2012-2013).
3. **Confiance dans les institutions** : INSEE ODD 16.i4 (baromètre du Cevipof, vérifié dans la fiche de métadonnées), une famille par institution ; gouvernement (OCDE/Gallup), Parlement et administration (WVS/EVS, 3 vagues) retenus comme seules mesures (précédent `solitude`).
4. **Justice et État de droit hors composites** : détention provisoire (ODD 16.3.2, raccordement 2008-2009 par Eurostat), occupation carcérale (raccordement 2008-2011 à étudier), indépendance perçue de la justice (Eurobaromètre) retenues ; dépenses pour les tribunaux (moyen en euros courants) et signalement à la police (sens ambigu) écartés.
5. **Incontournables** (méthode §4) : seul le concept « participation et voix politique » est au §5 du crosswalk ; corruption et confiance dans les institutions (deux cadres) restent à `non` mais ont toutes une fiche `retenir`.

## 4. Signalements (consignés dans `docs/cr/maintenance_catalogues.md`, non corrigés)

10 — OCDE 8_2 libellé « législatives » alors qu'il s'agit de la présidentielle ; 11 — fréquence `annuelle` des séries de participation INSEE (municipales 001785274/75 classées « non » à tort) ; 12 — `ilc_scp19` (citoyenneté active) hors catalogue ; 13 — champ des inscrits 2002-2007 et scrutins 1995-2001 absents du fichier des élections ; 14 — confiance dans le gouvernement et les partis (WVS/EVS) non cataloguée ; 15 — table de correspondance : administration en ligne → `logement_cadre_vie`, `sdg_05_50` → `egalites`, `crim_pris_*` → `democratie` ; 16 — sens « ambigu » de RSF à remplacer par `haut` + ruptures. Aucune autre exclusion abusive : les 89 lignes « non » relèvent de leur motif (séries de 2013 seulement ou depuis 2022, sous-scores RSF depuis 2022, Fariss arrêté en 2019, OCDE 14_2 à un point, probité à 8 points).

## 5. Propositions

- `scripts/verifier_fiches.py` : élargir la borne de `premiere_annee` (1900) ou documenter l'usage : trois séries V-Dem commencent en 1789 et ont été ramenées à 1900 (note dans chaque fiche).
- Méthode §1 : préciser le statut des fiches non principales d'une famille de producteur (D18) qui ne sont pas substituables à la principale (`etat_de_droit_wgi`, `controle_corruption_wgi`) : garder `retenir_variante` ou en faire des familles de concept.
- Fichier de maintenance : prévoir une numérotation par dimension (ex. `DEM-1`) pour éviter les conflits entre agents M05 parallèles.

## 6. À trancher

- **Léo** : source principale de la participation (ministère plutôt qu'INSEE) et nombre de fiches de participation (6) ; maintien de Freedom House (7 valeurs distinctes depuis 2002, licence non trouvée) ; RSF lisible seulement depuis 2013 ; citoyenneté active (24,8 % en 2015, 11,9 % en 2022 : comparabilité à vérifier) ; confiance dans l'armée dans cette dimension.
- **Session mère** : incontournables corruption et confiance (consigne de mission contre méthode §4) ; fiches non principales WGI ; rattachements `autre_dimension` (administration en ligne, parité) et confiance dans l'école et l'hôpital gardées ici (R5) ; lignes `crim_pris_*` de `securite` rattachées ici.

## 7. Corrections après audit (M06, D32-D36) — branche `m05-democratie-corr`, PR #23

Audit : `docs/validation/audit_democratie.md` (29 fiches auditées : 18 conformes, 10 à corriger, 1 non vérifiable ; 4 oublis ; 8 désaccords de jugement ; 9 corrections au §10). Les neuf corrections et les oublis O1 à O3 sont appliqués (O4 : piste de source, DEM-7) ; détail horodaté, fichiers et limites : `docs/cr/M05_democratie_corrections_journal.md`.

| Fiche | Correction |
|---|---|
| `participation_presidentielle`, `_legislatives`, `_europeennes`, `_municipales`, `_regionales`, `_departementales` | recalcul sur un **champ homogène métropole + DROM** (champ « France » de l'INSEE) à partir de la vague 9 du robot (agrégat par scrutin et par département), le fichier ne contenant les Français de l'étranger et les collectivités d'outre-mer qu'à partir de 2009-2012 ; recoupé avec les archives du ministère (présidentielles 2002 et 2007 : 72,11 % et 84,73 % ; régionales 2010 : 46,33 %) et l'INSEE 2012-2024 (identique à l'arrondi) ; présidentielle : 72,11 / 84,73 / 80,67 / 79,02 / 75,28 % ; municipales depuis 2014 (2008 limité aux communes de plus de 3 500 habitants) ; régionales depuis 2010 (2004 mal codé : Manche absente, bureaux rattachés au mauvais département, DEM-1) ; départementales en `retenir_variante` sur 2015-2021 (J3) ; `composantes`, `formule`, `preuve`, `geo: FE` (D34) |
| `libertes_freedom_house` | années OWID = années couvertes (`annee_couverte`) ; édition 2026 ; baisse de 93-96 à 89 ; famille `qualite_democratique` |
| composites (D33, D35, J1, J5, J6) | familles de concept : `qualite_democratique` (V-Dem libéral principal ; V-Dem participatif, Freedom House, WGI voix et responsabilité en variantes), `etat_de_droit` (WGI principal, WJP en variante), `corruption` (WGI principal, CPI en variante), `liberte_presse_rsf`, `liberte_expression_vdem`, `liberte_academique_vdem` ; WGI en score 0-100 (documentation lue) ; sous-indices V-Dem d'État de droit et de corruption rattachés à leur famille, autres sous-indices WGI écartés en bloc ; `annee_reference` sur les 11 composites |
| `democratie_liberale_vdem`, `democratie_participative_vdem`, `liberte_expression_vdem` | `premiere_annee: 1789` (D32) ; `faible_variation` sur l'indice libéral |
| `adhesion_syndicale` (nouvelle, O1, D33) | SDASSYND_1 du baromètre DREES calculée par la vague 10 du robot : 8,06 % (2000) → 5,49 % (2019) → 6,81 % (2025), 25 points ; `retenir`, sans valeur officielle publiée pour la recouper |
| `participation_en_ligne` (nouvelle, O2) | `I_IUVOTE` d'Eurostat importé de la long-list `logement_cadre_vie` : 6,96 % (2011) à 8,74 % (2025), 10 points ; `retenir`, incontournable |
| `taux_detention` (nouvelle, O3, I2) | 14 lignes `crim_pris_*` renvoyées par `securite` : détenus pour 100 000 habitants (97,26 en 2008, 117,47 en 2024), `sens: ambigu`, `ecarter` ; ventilations en variantes, détenus par infraction écartés en bloc |
| `voix_pouvoirs_publics` | source primaire « à vérifier (PIAAC ou enquête Confiance) », `source_a_verifier` |
| `perception_corruption_cpi`, `voix_responsabilite_wgi`, `detention_provisoire`, `liberte_expression_vdem` | motif CPI (71 → 66, maximum 72) ; trajectoire de voix et responsabilité depuis 2000 et volatilité 2003-2005 ; raccordement de 2019 `a_etudier` (J4) ; incontournables motivés (J7) |

Chiffres après corrections : **35 fiches, 25 familles : 22 `retenir`, 10 `retenir_variante`, 3 `ecarter`** ; 10 déclaratives ; 11 composites ; 2 hors long-list ; 13 incontournables ; 102 variantes. Présélection : 93 groupes (35 `fiche`, 44 `variante_de`, 12 `ecarte_en_bloc`, 2 `autre_dimension`) ; 269 lignes, dont 19 importées (17 de `securite`, 2 de `logement_cadre_vie`). Vérificateur : 0 erreur, 2 avertissements attendus (`adhesion_syndicale`, `citoyennete_active` : séries hors catalogue). Tests : 399 réussis.

Liste de maintenance : ligne 24 précisée dans `docs/cr/maintenance_catalogues.md` ; nouveaux signalements DEM-1 à DEM-7 dans `docs/cr/maintenance_catalogues_democratie.md` (régionales 2004 mal codées, catalogage de SDASSYND_1, identifiants WJP et des lignes de participation (D36), champ homogène au catalogue, table de correspondance pour `I_IUVOTE` et `crim_pris_*`, extraits complets des scores WGI, sources à rechercher).

À trancher : **session mère** — `adhesion_syndicale` en `retenir` sans recoupement possible (D34) ; V-Dem libéral (niveau 2) plutôt que WGI voix et responsabilité (niveau 1) en principale de `qualite_democratique` (concept le plus large, dérogation à la méthode §4) ; rattachement de `I_IUVOTE` et des 17 lignes `crim_pris_*` ; mesures `I_IUPOL*` laissées à `logement_cadre_vie`. **Léo** — un seul indice par famille de composites ; WGI en principale pour l'État de droit et la corruption, le WJP et le CPI, plus connus mais plus courts, en variantes ; régionales et municipales réduites à 3 points, départementales à 2.
