# Compte rendu — M05, fiches indicateurs de la dimension `democratie` (Démocratie et institutions)

Agent M05 democratie, 14 octobre 2026, branche `m05-democratie`. Méthode commune suivie (`docs/methodo/33_methode_fiches_M05.md`) ; méthode détaillée, vérifications et contrôles : `docs/cr/M05_democratie_journal.md`.

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

## 2. Chiffres

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
