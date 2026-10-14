# Compte rendu — M05, fiches indicateurs de la dimension `securite` (mission pilote)

Agent M05 securite, 14 octobre 2026, branche `m05-securite`, PR #7. Méthode détaillée, vérifications et contrôles : `docs/cr/M05_securite_journal.md`. Version mise en conformité avec la méthode commune (`docs/methodo/33_methode_fiches_M05.md`) après les décisions de la session mère (journal §8).

## 1. Fait

| Livrable | Fichier |
|---|---|
| Règles de présélection (116 règles, méthode commune) | `docs/validation/regles_preselection_securite.csv` |
| Présélection par groupe (116 groupes) et ligne à ligne (928 lignes de la long-list + 4 d'autres long-lists) | `docs/validation/preselection_securite.csv`, `preselection_securite_lignes.csv` (écrits par `scripts/preselection.py`) |
| 33 fiches YAML (schéma de la méthode commune, `socle_v1` vide) | `indicateurs/securite/*.yaml` |
| Tableau de validation (18 colonnes, `decision_leo` vide) | `docs/validation/validation_securite.csv` (écrit par `scripts/verifier_fiches.py --tableau`) |
| Corrections de catalogues à faire (9 lignes `a_faire`) | `docs/cr/maintenance_catalogues.md` |
| Journal de méthode | `docs/cr/M05_securite_journal.md` |

Contrôles : `main` fusionné (`git merge`, sans conflit) ; `python scripts/verifier_fiches.py --dimension securite` → 0 erreur, 0 avertissement ; `pytest` : 394 réussis.

## 2. Chiffres

- Long-list : 928 lignes (768 éligibles, 19 à vérifier). Décisions : 33 lignes `fiche`, 176 `variante_de` (+ 4 lignes importées de `sante` et `hors_grille`), 716 `ecarte_en_bloc` (556 lignes d'accidents aériens ventilées par pays d'immatriculation, 68 lignes non éligibles des jeux régionaux d'infractions, 62 lignes d'activité policière, judiciaire et pénitentiaire ou d'effectifs, etc.), 3 `autre_dimension:democratie`.
- **33 fiches, 25 familles : 20 `retenir`, 4 `retenir_variante`, 9 `ecarter`** ; 9 déclaratives ; 0 composite ; 2 à vérifier (D17) ; 7 fiches incontournables (homicides ; sentiment d'insécurité / délinquance perçue ; dépense imprévue et épargne de précaution) ; 182 variantes.

## 3. Choix structurants (détail : journal §2)

1. Variante principale : taux > nombre ; enquête de victimation > délinquance enregistrée tant que l'enquête est publiée ; sinon série enregistrée si son sens n'est pas ambigu.
2. Délinquance enregistrée dont la tendance contredit l'enquête → `sens: ambigu`, `ecarter`, motif chiffré (agressions graves ×2,1 ; violences sexuelles ×4 ; violences intrafamiliales).
3. `declaratif = oui` pour les perceptions et opinions, `non` pour les faits et capacités déclarés (règle actée).
4. Rupture CVS → VRS documentée sur les données (valeurs 2010-2018 puis 2021-2023, rien en 2019-2020, changement de niveau).
5. `incontournable` selon la méthode commune (§5 du crosswalk) : `tues_route` passe à `non` (trois cadres de la table le citent, mais pas le §5) — à trancher.

## 4. Signalements (consignés dans `docs/cr/maintenance_catalogues.md`, non corrigés)

Règle 4 de la table (soldes CVS 000857196/000857197 hors grille) ; `sdg_16_10` → `securite` ; DREES PE03 (modalités 1 + 3) et champ FM du baromètre ; séries VRS absentes ; séries SSMSI utiles aux raccordements ; exception `tran_r_acci` à l'exclusion des jeux régionaux ; séries SRCV 2020-2025 raccordables (D16) ; champ du taux de tués sur la route.

## 5. À trancher

- Léo : licence Gallup (`securite_nuit`) ; principal des vols avec violence (enquête ONUDC jusqu'en 2022 ou série enregistrée jusqu'en 2024) ; maintien des 4 soldes d'opinion Camme (D29, P8).
- Session mère : statut `incontournable` des tués sur la route.
