# Journal de bord — M06, audit croisé de la dimension `liens_bien_etre`

Auditeur M06, 14 octobre 2026, branche `m06-liens_bien_etre` (partie de `origin/main` au commit `48e2381`). Session neuve, sans participation à M05. Livrable : `docs/validation/audit_liens_bien_etre.md` (copie Projet : `claude/cr/M06_liens_bien_etre_audit.md`). Aucune fiche, aucun script, aucun catalogue modifié.

## 1. Déroulé

1. Mise en route : `git checkout -B m06-liens_bien_etre origin/main`. Lecture de `CLAUDE.md`, charte (§3.1, §3.4, §3.6, §4, §5.1), journal D13–D30, fiche M06, méthode `33_methode_fiches_M05.md`, `dimensions.yaml`, des 21 fiches, du tableau de validation, des règles et tableaux de présélection, du journal et du compte rendu M05.
2. Contrôle préalable : `python scripts/verifier_fiches.py --dimension liens_bien_etre` → 0 erreur, 1 avertissement (identique au journal M05). Long-list : 668 lignes toutes affectées (croisement long-list × présélection refait avec pandas : 20 séries principales, 448 variantes, 160 écarts, 40 autre dimension).
3. Échantillon (§2 du rapport) : 2 `ecarter`, 2 incontournables, 7 « à vérifier » du journal M05, 2 rattachements proposés, 1 point ouvert du journal (§7), 2 fiches tirées parmi les 9 autres avec `random.Random(20261014).sample(sorted(autres), 2)` → `optimisme_avenir_personnel`, `situation_personnelle_bonne`. Total 15.
4. Vérifications à la source (WebFetch, une requête à la fois) :
   - Eurostat (API JSON) : `ilc_mdes02`, `tour_dem_totot`, `ilc_pw08`, `ilc_pw03`, `ilc_scp01`, `ilc_mdes11a`, `ilc_mdes10a`, `ilc_pw06`, `ilc_pw01b` ; métadonnées `tour_dem_esms` et `tour_dem_esmsdm_fr`.
   - OCDE (SDMX, `format=jsondata`) : `FRA.7_1.PT_POP_Y_GE15._T._T._T.`, `FRA.7_1......` (clé des fiches, acceptée), `FRA.7_4.PT_POP_Y_GE16._T._T._T.`. Le format `csvfilewithlabels` des fiches est renvoyé en binaire à l'outil (non lisible, pas une erreur de l'API).
   - INSEE : BDM `010593281` (lue) ; Melodi refusé (robots.txt).
   - DREES : page du jeu 431 (champ « France métropolitaine », licence non indiquée) ; liste des pièces jointes refusée (robots.txt), relue dans l'extrait du robot.
   - WHR : page `data-sharing` (aucune licence).
   - Extraits du robot commités : distributions, couverture et dictionnaires du baromètre DREES ; extraits OCDE *How's Life* ; extrait WHR 2026.
5. Complétude : recherche par mots-clés dans les dix long-lists, les catalogues INSEE (retenus et écartés), le catalogue des jeux Eurostat, le catalogue M04 et les dictionnaires DREES ; comparaison au crosswalk (§5 et lignes `liens_bien_etre`).
6. Cohérence inter-dimensions : comparaison mécanique des séries (principales, composantes, variantes) des fiches `liens_bien_etre` et `securite`, puis des jeux et mesures ; relecture des fiches DREES de `securite`.
7. Rapport, journal, commit, push, pull request, dépôt dans le Projet.

## 2. Résultats chiffrés

- Fiches auditées : 15 / 21 — conformes 9, à corriger 6 (`aidance_personne_agee`, `solitude`, `privation_vacances`, `depart_vacances`, `optimisme_avenir_personnel`, `situation_personnelle_bonne`), non vérifiables 0 (réserves partielles : valeur Melodi 2025 de `satisfaction_vie`, poursuite de `satisfaction_relations`).
- Hors échantillon, corrections transversales : 5 fiches (3 DREES pour `geo`, `cohesion_sociale_percue` pour la rupture 2018, `privation_loisirs`/`privation_sorties_proches` pour le champ d'âge).
- Oublis : 6 (dont 2 de fond : solitude DREES CS12, adhésion associative DREES SDASSYND_2).
- Incohérences inter-dimensions : 6 (aucun identifiant ni série en double avec `securite`).
- Avis global : `corrections_necessaires`.

## 3. Constats marquants

- Toutes les valeurs citées dans les notes des fiches et relues à la source sont exactes (bonheur 62,1 / 67,8 / 66,4 % ; confiance 5,9 → 4,5 et drapeaux « u » ; vacances 33,4 → 22,0 % ; départs 63,06 → 57,35 % ; soutien social 87,6 % ; solitude 10,8 % ; participation 80,6 → 59,1 % ; satisfaction 6,8 à 7,5).
- Erreur répétée : `geo: FR` sur les 6 fiches DREES (enquête métropolitaine ; `securite` a `FM`).
- `depart_vacances` : la fiche nationale Eurostat documente une rupture en 2020 (reprise de l'enquête SDT par l'INSEE), un champ 15 ans ou plus et un panel non aléatoire ; le décrochage 2017 reste inexpliqué.
- Le baromètre DREES contient deux questions de la dimension non exploitées : CS12 (se sentir seul, 7 vagues 2014-2025) et SDASSYND_2 (membre d'une association, 2000-2025).

## 4. Difficultés

- `api.insee.fr` (Melodi) et l'API des pièces jointes DREES refusent l'outil de lecture (robots.txt) : valeurs Melodi non relues ; pièces jointes DREES relues dans l'extrait du robot du 13/10.
- Page OCDE *How's Life* en erreur : `url_page` « non trouvé » confirmé.
- La distribution de SDASSYND_2 n'a pas été calculée par le robot M04 : valeurs « non trouvé » (couverture seule).

## 5. Propositions (pour la session mère, non appliquées)

Voir §9 et §10 du rapport : corrections ordonnées pour M05 ; calcul des deux séries DREES par le robot M04 ; règle de famille pour les opinions sur la société ; consigne à M05 `travail` sur les 20 lignes de sa long-list utilisées ou à utiliser ici ; candidat `democratie` (adhésion syndicale DREES).
