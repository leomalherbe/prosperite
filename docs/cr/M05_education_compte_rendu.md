# Compte rendu — M05, fiches indicateurs de la dimension `education`

Agent de mission M05 (Éducation et compétences), 14 et 15 octobre 2026, branche `m05-education`, pull request « M05 — fiches indicateurs : education ». Mission commencée le 14/10 par un agent interrompu après les règles de présélection, reprise et terminée le 15/10 par un second agent. Méthode commune `docs/methodo/33_methode_fiches_M05.md` (v1.2) appliquée sans modification des scripts communs. Détail dans `docs/cr/M05_education_journal.md`.

**Mise à jour du 16/10/2026 — corrections après l'audit M06** (agent correcteur, branche `m05-education-corr`, PR « M05 — education : corrections après audit ») : audit `docs/validation/audit_education.md` appliqué avec les décisions D41 (socle proposé), D44 (réponses à l'audit) et D46 (lignes renvoyées). Détail dans `docs/cr/M05_education_corrections_journal.md`. Les chiffres et choix ci-dessous sont ceux **après corrections** ; l'état initial de M05 est rappelé quand il a changé.

## 1. Livrables

| Fichier | Contenu |
|---|---|
| `docs/validation/regles_preselection_education.csv` | 110 règles ordonnées (dont 3 concepts hors long-list) ; 104 à la livraison M05 |
| `docs/validation/preselection_education.csv`, `preselection_education_lignes.csv` | 110 groupes ; 4 716 lignes affectées (les 4 503 de la long-list, 0 sans règle, + 96 importées de `travail`, 93 de `logement_cadre_vie` et 24 de `niveau_de_vie`) |
| `indicateurs/education/*.yaml` | 39 fiches (schéma v1.2 + `socle_propose`, D41 ; `socle_v1` vide), 378 variantes |
| `docs/validation/validation_education.csv` | tableau de validation à 18 colonnes, `decision_leo` vide ; `verifier_fiches.py --dimension education` : **0 erreur**, 42 avertissements attendus (39 « champ hors schéma `socle_propose` » tant que le vérificateur ne l'admet pas, 3 séries hors catalogue), 0 ligne prise ailleurs |
| `docs/cr/maintenance_catalogues.md` | lignes 36 à 44 (39 `en_cours`, 41 `fait`, 40, 43 et 44 corrigées le 16/10) |
| `docs/cr/maintenance_catalogues_education.md` | lignes EDU-1 (série des cibles de formation des adultes) et EDU-2 (table de correspondance), 16/10 |

## 2. Chiffres

- **Long-list** : 4 503 lignes (2 844 éligibles, 757 à vérifier, 902 non éligibles) ; Eurostat 4 362, BDM 85, Melodi 39, M04 17. Le gros du volume est hors sujet (étiquettes v0 par mots-clés) : statistiques UOE d'effectifs et de finances, budget des ménages et prix, enquête CVTS sur les entreprises, comptes de capital.
- **Décisions par ligne** (long-list et lignes importées) : 38 en `fiche`, 367 en `variante_de`, 4 084 écartées en bloc (dont les 93 lignes renvoyées par `logement_cadre_vie`), 227 en `autre_dimension` (egalites 137, travail 56, logement_cadre_vie 30, liens_bien_etre 4).
- **39 fiches, 24 familles** : **22 `retenir`**, **14 `retenir_variante`**, **3 `ecarter`** (M05 : 38 fiches, 25 familles, 23 / 13 / 2) ; 36 de résultat, 3 de moyens (D19 : effort et personnel de R&D, dépenses d'éducation).
- 0 déclarative, 0 composite ; 17 à vérifier (séries irrégulières, D17) ; 3 hors long-list (JDC, ICILS, formation par le travail).
- **Incontournables** (§5 du crosswalk, portés par la seule principale, D38 d) : 7 — `sorties_precoces` ; les trois parts d'élèves sous le niveau 2 de PISA et `pisa_eleves_faibles_trois_domaines` ; `piaac_litteratie`, `piaac_numeratie` (M05 : 12, dont 5 fiches non principales).
- **Socle proposé (D41)** : 8 fiches — `sorties_precoces`, `pisa_eleves_difficulte_lecture`, `pisa_eleves_difficulte_mathematiques`, `piaac_litteratie`, `competences_numeriques_base`, `formation_adultes_12_mois`, `accueil_formel_moins_3_ans`, `effort_recherche_pib`.
- Sous-thèmes : compétences des élèves 12 ; diplômes et sorties précoces 8 ; compétences des adultes 5 ; compétences numériques 4 ; formation des adultes 4 ; recherche et innovation 3 ; petite enfance 2 ; moyens 1.

## 3. Choix structurants

1. **Familles par concept substituable (D35).** Sorties précoces (INSEE, principale) et part des 25-34 ans diplômés du secondaire (Eurostat, variante) mesurent le même déficit de qualification ; PISA : une famille par domaine, la part d'élèves sous le niveau 2 (cible européenne < 15 %) principale, le score moyen de l'OCDE en variante ; **mathématiques** : la famille PISA accueille aussi l'évaluation de sixième (variante) et TIMSS en CM1 (écarté), par D44 ; **lecture en fin de primaire** : PIRLS principale, évaluation de sixième en français variante ; PIAAC : littératie seule, numératie avec la part d'adultes faibles en variante ; **formation des adultes** : participation sur douze mois (AES, principale par D44), fenêtre de quatre semaines (EFT annuelle) et formation par le travail des diplômés de l'enseignement professionnel en variantes ; accueil des moins de 3 ans principal, préscolarisation des 3 ans ou plus (100 % chaque année, D34) en variante ; effort de R&D (INSEE, objectif de 3 %) principal, personnel de R&D en variante.
2. **Séries principales corrigées** par rapport aux règles de la veille : `edat_lfse_03` (jeu national) plutôt que l'OCDE 13_1 pour les 25-34 ans diplômés du secondaire (2000-2025 contre 2004-2024) et plutôt que `edat_lfse_04` (jeu régional, D30) pour les adultes peu diplômés.
3. **Sorties précoces : INSEE principale par exception à la méthode §4 (D44).** La série INSEE (2006-2024, indicateur de richesse nationale n° 8) est **rétropolée par la DEPP de 2003 à 2013** (page insee.fr 3281681) sur un champ homogène ; elle atténue la rupture de 2013 d'Eurostat sans l'effacer ; valeurs 2021-2024 provisoires. Eurostat `sdg_04_10` (2000-2025) en variante, raccordement de 2000-2005 en évolution.
4. **Formation des adultes (D44).** L'indicateur des cibles de 2030 (60 % pour l'UE, 65 % pour la France) est une extraction spéciale de l'AES hors formation guidée en situation de travail, absente de la base d'Eurostat (France : 48,4 % en 2016, 49,2 % en 2022, rapport conjoint sur l'emploi) ; la fiche sur douze mois garde `trng_aes_100` (formation guidée incluse, 50,8 % en 2022), plus proche série publiée, avec le drapeau `inclut_formation_guidee` ; `trng_lfs_17` (EFT, biennale depuis 2022, hors formation guidée) en variante.
5. **Séries calculées (D34)** : compétences numériques de base ou plus (somme de deux séries INSEE, recoupée avec `sdg_04_70` en 2021, 2023, 2025) ; enfants de moins de 3 ans en accueil formel (somme de deux durées, recoupée avec `tepsr_sp210` sur six années).
6. **Hors long-list (D32)** : jeunes en difficulté de lecture à la JDC (ITDD, 2022-2024, variante de la lecture PISA) ; élèves de 4e faibles en compétences numériques (ICILS 2018 et 2023, `retenir`) ; formation par le travail des diplômés récents de l'enseignement professionnel (`edat_lfs_9919`, 2021-2025, `retenir_variante`, D44 ; valeurs non lues).
7. **Écartées** : taux de réussite au baccalauréat (sens ambigu : dépend de l'examen) ; dépenses publiques d'éducation en % du PIB (sens ambigu : dépend du PIB, pic de 2020 ; repère UNESCO de 4 à 6 % du PIB, plancher dépassé) ; TIMSS en CM1 (D44 : seuil non documenté, valeur 2023 non comparable selon la NI 24.47 de la DEPP).
8. **Ajout M05** : `pisa_eleves_faibles_trois_domaines` (OCDE 6_1_DEP, 16,8 % en 2022), mesure de privation de l'OCDE sortie des variantes de la lecture.

## 4. Rattachements proposés (à trancher au gel 2)

- **Vers `education`** : 96 lignes de `travail` (parts de diplômés de l'enquête Emploi, formation des salariés), 24 de `niveau_de_vie` (modes de garde, personnel de recherche ODD 9.i4, brevets `sdg_09_40`, dont la série principale de `demandes_brevets`) et 93 de `logement_cadre_vie` (niveau d'éducation et langues par degré d'urbanisation, écartées en bloc) : toutes reprises (D38 a, D46). Spécialistes des TIC et brevets restent en `education` (D44).
- **Hors d'`education`** : `egalites` (parts de femmes dans l'enseignement, les diplômes STEM et les métiers du numérique, ventilations par origine des sorties précoces et des NEET, PISA par statut socio-économique, transmission selon le diplôme des parents) ; `travail` (NEET, insertion des jeunes diplômés ; reprises) ; `logement_cadre_vie` (accès au numérique, A7 ; loyers de l'IPCH, D42) ; `liens_bien_etre` (monuments, musées). Restent à reprendre par les destinataires : `egalites` 75 lignes, `logement_cadre_vie` 28, `liens_bien_etre` 4. Exceptions de la table de correspondance : lignes 43 et EDU-2 de la liste de maintenance.

## 5. Maintenance

ITDD et série longue de la DEPP sur la JDC (36) ; variables DEPP des objectifs européens, dont ICILS (37) ; TIMSS classée « non » contrairement à D28 (38) et valeur 2023 incohérente avec la NI 24.47 (39, `en_cours`) ; jeux Eurostat hors filtre utiles en variantes, dont `trng_lfs_17` **biennal** (40) ; valeurs non relues (41, soldée) ; unité et mesures OCDE 6_x_DEP (42) ; exceptions de la table de correspondance (43) ; sources non cataloguées, dont `edat_lfs_9919` à réintégrer (44) ; série des cibles de formation des adultes (EDU-1) ; rattachements `education` / `logement_cadre_vie` (EDU-2).

## 6. Points à faire vérifier par Léo (priorité au gel 2)

1. **PISA en principale par la part d'élèves faibles** (cible européenne) plutôt que par le score moyen ; la hausse de 2025 est forte (lecture 26,9 % → 32,7 %).
2. **Lecture en fin de primaire** : PIRLS principale (3 points, au plafond à 94 %) devant l'évaluation de sixième (8 points annuels) ; à réexaminer en 2026 quand la sixième atteindra 10 points (la famille des mathématiques a déjà PISA pour principale, D44).
3. **Formation des adultes** : participation sur douze mois principale (D44), mais la série publiée inclut la formation guidée ; les cibles de 60 % et 65 % ne s'y appliquent pas telles quelles (bornes du socle).
4. **Spécialistes des TIC** retenus comme compétences numériques avancées : c'est aussi une structure de l'emploi (non proposé au socle).
5. **Demandes de brevets** retenues comme résultat de la recherche (A5, D44).
6. **Aucune fiche déclarative** : aucune série d'opinion ou de satisfaction sur l'école n'est cataloguée (ligne 44).
7. **Socle proposé** limité à 8 fiches : trois incontournables (sciences PISA, faibles dans les trois domaines, numératie PIAAC) n'y figurent pas.

## 7. Propositions pour la session mère

1. Appliquer D28 sans condition d'étendue dans le filtre de la long-list (cas TIMSS, ligne 38).
2. ~~Confirmer la règle des séries annuelles de moins de 10 points~~ : tranché par D38 f.
3. Corrections après audit (16/10/2026) : questions du journal des corrections, §5 — symétrie de la lecture en fin de primaire avec D44, série principale de la formation des adultes faute de code Eurostat pour l'indicateur des cibles, application de D41 quand les incontournables dépassent la limite de 8, famille d'accueil de la formation par le travail.
