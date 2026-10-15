# Compte rendu — M05, fiches indicateurs de la dimension `education`

Agent de mission M05 (Éducation et compétences), 14 et 15 octobre 2026, branche `m05-education`, pull request « M05 — fiches indicateurs : education ». Mission commencée le 14/10 par un agent interrompu après les règles de présélection, reprise et terminée le 15/10 par un second agent. Méthode commune `docs/methodo/33_methode_fiches_M05.md` (v1.2) appliquée sans modification des scripts communs. Détail dans `docs/cr/M05_education_journal.md`.

## 1. Livrables

| Fichier | Contenu |
|---|---|
| `docs/validation/regles_preselection_education.csv` | 104 règles ordonnées (dont 2 concepts hors long-list) |
| `docs/validation/preselection_education.csv`, `preselection_education_lignes.csv` | 104 groupes ; 4 623 lignes affectées (les 4 503 de la long-list, 0 sans règle, + 96 importées de `travail` et 24 de `niveau_de_vie`) |
| `indicateurs/education/*.yaml` | 38 fiches (schéma v1.2, `socle_v1` vide), 378 variantes |
| `docs/validation/validation_education.csv` | tableau de validation à 18 colonnes, `decision_leo` vide ; `verifier_fiches.py --dimension education` : **0 erreur**, 2 avertissements (fiches hors long-list avec preuve), 0 ligne déjà prise ailleurs |
| `docs/cr/maintenance_catalogues.md` | lignes 36 à 44 (`a_faire`) |

## 2. Chiffres

- **Long-list** : 4 503 lignes (2 844 éligibles, 757 à vérifier, 902 non éligibles) ; Eurostat 4 362, BDM 85, Melodi 39, M04 17. Le gros du volume est hors sujet (étiquettes v0 par mots-clés) : statistiques UOE d'effectifs et de finances, budget des ménages et prix, enquête CVTS sur les entreprises, comptes de capital.
- **Décisions par ligne** : 37 en `fiche`, 307 en `variante_de`, 3 934 écartées en bloc (dont 2 404 éligibles : effectifs et finances de l'éducation, budget des ménages, personnels enseignants, comptes de capital, structures par niveau d'études), 225 en `autre_dimension` (egalites 137, travail 56, logement_cadre_vie 28, liens_bien_etre 4).
- **38 fiches, 25 familles** : **23 `retenir`**, **13 `retenir_variante`**, **2 `ecarter`** ; 35 de résultat, 3 de moyens (D19 : effort et personnel de R&D, dépenses d'éducation).
- 0 déclarative, 0 composite ; 17 à vérifier (séries irrégulières, D17) ; 2 hors long-list (JDC, ICILS).
- **Incontournables** (§5 du crosswalk) : « diplôme du secondaire / sorties précoces » (`sorties_precoces`, `jeunes_diplomes_secondaire`) et « compétences mesurées (PISA, PIAAC) » (7 fiches PISA, 3 fiches PIAAC) ; tous présents, chaque famille ayant sa principale `retenir`.
- Sous-thèmes : compétences des élèves 12 ; diplômes et sorties précoces 8 ; compétences des adultes 5 ; compétences numériques 4 ; formation des adultes 3 ; recherche et innovation 3 ; petite enfance 2 ; moyens 1.

## 3. Choix structurants

1. **Familles par concept substituable (D35).** Sorties précoces (INSEE, principale) et part des 25-34 ans diplômés du secondaire (Eurostat, variante) mesurent le même déficit de qualification ; PISA : une famille par domaine, la part d'élèves sous le niveau 2 (cible européenne < 15 %) principale, le score moyen de l'OCDE en variante ; PIRLS et TIMSS (CM1, D17) principales, évaluations nationales de sixième (8 points annuels, sous le seuil de 10) en variantes ; PIAAC : littératie seule, numératie avec la part d'adultes faibles en variante ; formation des adultes : série annuelle sur 4 semaines principale, participation sur 12 mois (cibles européenne de 60 % et française de 65 % en 2030, enquête quinquennale) en variante ; accueil des moins de 3 ans principal, préscolarisation des 3 ans ou plus (100 % chaque année, D34) en variante ; effort de R&D (INSEE, objectif de 3 %) principal, personnel de R&D en variante.
2. **Séries principales corrigées** par rapport aux règles de la veille : `edat_lfse_03` (jeu national) plutôt que l'OCDE 13_1 pour les 25-34 ans diplômés du secondaire (2000-2025 contre 2004-2024) et plutôt que `edat_lfse_04` (jeu régional, D30) pour les adultes peu diplômés.
3. **Sorties précoces : INSEE principale malgré une série Eurostat plus longue.** La série INSEE (2006-2024) est l'indicateur de richesse nationale n° 8 ; elle reste sous Eurostat avant 2013 et ne montre pas la rupture de 2013 d'Eurostat (11,8 % → 9,7 %), ce qui suggère une rétropolation (à confirmer). Eurostat `sdg_04_10` couvre 2000-2005 et 2025 (raccordement `a_etudier`).
4. **Séries calculées (D34)** : compétences numériques de base ou plus (somme de deux séries INSEE, recoupée avec `sdg_04_70` en 2021, 2023, 2025) ; enfants de moins de 3 ans en accueil formel (somme de deux durées, recoupée avec `tepsr_sp210` sur six années).
5. **Hors long-list (D32)** : jeunes en difficulté de lecture à la JDC (ITDD, 2022-2024, 3 points, variante de la lecture PISA) et élèves de 4e faibles en compétences numériques (ICILS 2018 et 2023, cible européenne < 15 %, `retenir`), avec preuve du robot.
6. **Écartées** (sens ambigu) : taux de réussite au baccalauréat (dépend de l'examen), dépenses publiques d'éducation en % du PIB (moyen sans cible, sensible à la démographie scolaire).
7. **Ajout** : `pisa_eleves_faibles_trois_domaines` (OCDE 6_1_DEP, 16,8 % en 2022), mesure de privation de l'OCDE sortie des variantes de la lecture.

## 4. Rattachements proposés (à trancher au gel 2)

- **Vers `education`** : 96 lignes de `travail` (parts de diplômés de l'enquête Emploi, formation des salariés) et 24 de `niveau_de_vie` (modes de garde, personnel de recherche ODD 9.i4, brevets `sdg_09_40`, dont la série principale de `demandes_brevets`) ; signalés aussi par TRA-4 et NDV-2.
- **Hors d'`education`** : `egalites` (parts de femmes dans l'enseignement, les diplômes STEM et les métiers du numérique, ventilations par origine des sorties précoces et des NEET, PISA par statut socio-économique, transmission selon le diplôme des parents) ; `travail` (NEET, insertion des jeunes diplômés) ; `logement_cadre_vie` (accès au numérique, A7) ; `liens_bien_etre` (monuments, musées). Proposition d'exceptions de la table de correspondance : ligne 43 de la liste de maintenance.

## 5. Maintenance (lignes 36 à 44)

ITDD et série longue de la DEPP sur la JDC (36) ; variables DEPP des objectifs européens, dont ICILS (37) ; TIMSS classée « non » contrairement à D28 (38) et chute de 2023 à vérifier (39) ; jeux Eurostat hors filtre utiles en variantes (`sdg_04_70`, `tepsr_sp210`, `trng_lfs_17`, 40) ; valeurs non relues par refus du proxy (`edat_aes_l31`, `sdg_09_30`, `educ_uoe_fine06`, 41) ; unité et mesures OCDE 6_x_DEP (42) ; exceptions de la table de correspondance (43) ; sources non cataloguées : satisfaction à l'égard du système éducatif, dépense intérieure d'éducation, illettrisme des adultes, formation par le travail (44). Aucune exclusion abusive de la long-list en dehors de la ligne 38.

## 6. Points à faire vérifier par Léo (priorité au gel 2)

1. **PISA en principale par la part d'élèves faibles** (cible européenne) plutôt que par le score moyen ; la hausse de 2025 est forte (lecture 26,9 % → 32,7 %).
2. **PIRLS et TIMSS principales** (3 points chacune, PIRLS au plafond à 94 %) faute d'éligibilité des évaluations de sixième (8 points annuels, plus informatives) : à inverser en 2026 quand la sixième atteindra 10 points ? TIMSS 2023 (36 %) est à vérifier.
3. **Formation des adultes** : principale annuelle sur 4 semaines (rupture de 2013 qui triple le niveau) ou participation sur 12 mois porteuse des cibles (4 points) ?
4. **Spécialistes des TIC** retenus comme compétences numériques avancées : c'est aussi une structure de l'emploi.
5. **Demandes de brevets** retenues comme résultat de la recherche alors que le contenu de la dimension ne cite que l'effort de R&D (A5).
6. **Aucune fiche déclarative** : aucune série d'opinion ou de satisfaction sur l'école n'est cataloguée (ligne 44).

## 7. Propositions pour la session mère

1. Appliquer D28 sans condition d'étendue dans le filtre de la long-list (cas TIMSS, ligne 38).
2. Confirmer la règle suivie pour les séries annuelles de moins de 10 points qui sont la seule mesure fréquente d'un concept (sixième, JDC) : variante d'une fiche éligible de la même famille plutôt qu'écart.
3. Faire relire en priorité par l'audit M06 : la famille des sorties précoces (choix INSEE contre Eurostat), les deux séries calculées, la valeur TIMSS 2023 et les deux fiches hors long-list.
