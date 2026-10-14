# Compte rendu — M05, fiches indicateurs de la dimension `securite` (mission pilote)

Agent M05 securite, 14 octobre 2026, branche `m05-securite`. Méthode détaillée, vérifications et contrôles : `docs/cr/M05_securite_journal.md`.

## 1. Fait

| Livrable | Fichier |
|---|---|
| Présélection par concept (75 groupes) | `docs/validation/preselection_securite.csv` |
| Présélection ligne à ligne (928 lignes de la long-list + 4 d'autres long-lists) | `docs/validation/preselection_securite_lignes.csv` |
| 33 fiches YAML (schéma charte §5.1 + champs M05, `socle_v1` vide) | `indicateurs/securite/*.yaml` |
| Tableau de validation (colonnes de la fiche M05, `decision_leo` vide) | `docs/validation/validation_securite.csv` |
| Journal de méthode | `docs/cr/M05_securite_journal.md` |

Contrôles : `scripts/verifier_fiches.py` du pilote `liens_bien_etre` réutilisé tel quel (0 erreur, 0 avertissement ; il a aussi écrit le tableau, même format que l'autre pilote) et contrôles complémentaires de l'agent (0 erreur).

## 2. Chiffres

- Long-list : 928 lignes (768 éligibles, 19 à vérifier). Décisions : 33 lignes `fiche`, 176 `variante_de` (+ 4 lignes d'autres long-lists), 716 `ecarte_en_bloc` (dont 556 lignes d'accidents aériens ventilées par pays d'immatriculation, 68 lignes non éligibles des jeux régionaux d'infractions et 62 lignes d'activité policière, judiciaire et pénitentiaire ou d'effectifs), 3 `autre_dimension:democratie`.
- **33 fiches, 25 familles : 20 `retenir`, 4 `retenir_variante`, 9 `ecarter`** ; 9 déclaratives ; 0 composite ; 2 à vérifier (D17) ; 182 variantes rattachées.
- Incontournables (≥ 3 cadres) : homicides, tués sur la route, sentiment d'insécurité / délinquance perçue (2 familles), dépense imprévue et épargne de précaution — tous présents avec une fiche `retenir`.

## 3. Choix structurants (détail : journal §2)

1. Groupe « concept × décision », règles ordonnées, 100 % des lignes affectées ; nouveau code `autre_dimension:<dim>` pour les concepts d'une autre dimension (proposition).
2. Variante principale : taux > nombre ; enquête de victimation > délinquance enregistrée **si l'enquête est vivante** ; sinon série enregistrée si son sens n'est pas ambigu.
3. Délinquance enregistrée dont la tendance contredit l'enquête → `sens: ambigu`, `ecarter`, motif chiffré (agressions graves ×2,1 ; violences sexuelles ×4 ; violences intrafamiliales).
4. `declaratif = oui` pour les perceptions et opinions, `non` pour les faits et capacités déclarés (victimation, impayés, dépense imprévue).
5. Rupture CVS → VRS documentée sur les données (valeurs 2010-2018 puis 2021-2023, rien en 2019-2020, changement de niveau).

## 4. Problèmes et erreurs trouvées

1. Table de correspondance, règle 4 : les soldes CVS « situation financière passée / future » (000857196, 000857197) tombent hors grille ; motif à élargir.
2. `sdg_16_10` (mortalité par homicide) rattaché à `sante` : à rattacher à `securite`.
3. Catalogue M04 : risque de pauvreté ressenti (DREES PE03) limité à la modalité « oui, plutôt », sans « déjà pauvre » (7,9 % → 17,4 %) : série trompeuse, correction 1 + 3 proposée ; séries DREES en `geo = FR` au lieu de FM.
4. Aucune série de l'enquête VRS (2022 et suivantes) dans les catalogues : sentiment d'insécurité, cambriolages déclarés, injures et menaces s'arrêtent en 2020-2021.
5. D30 (exclusion des jeux régionaux NUTS) supprimerait `tran_r_acci`, seule source nationale des blessés de la route.
6. Champ du taux de tués (Eurostat, OCDE) : 3 193 tués de métropole pour 4,6 pour 100 000 impliquent la population de la France entière (à vérifier, ONISR).

## 5. Propositions (journal et table : non modifiés)

- Journal : acter le code `autre_dimension:<dim>`, la règle `declaratif` (§2.4 du journal), `sens: ambigu` ⇒ `ecarter`, le critère « enquête vivante » ; corriger la règle 4 et ajouter une exception `sante` + « homicide » → `securite`.
- M04 (maintenance) : cataloguer les séries VRS du SSMSI, les vols de véhicules SSMSI (comblent 2017-2019) et la série homicides 2008-2015 ; corriger PE03 (modalités 1 + 3, `geo` FM).
- M02 : garder `tran_r_acci` au niveau national lors de l'exclusion des jeux NUTS.
- Léo : licence Gallup (`securite_nuit`) ; principal des vols avec violence (enquête ONUDC jusqu'en 2022 ou série enregistrée jusqu'en 2024) ; maintien des 4 soldes d'opinion Camme (D29, P8).
