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

## 2. Chiffres (avant l'audit ; chiffres à jour au §6)

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

## 6. Corrections après audit (M06, D32-D36) — branche `m05-securite-corr`

Audit : `docs/validation/audit_securite.md` (22 fiches auditées, 16 conformes, 6 à corriger, 10 corrections au §9). Les dix corrections sont appliquées ; détail, fichiers et limites : `docs/cr/M05_securite_corrections_journal.md`.

| Fiche | Correction |
|---|---|
| `tues_route` | champ mixte documenté (`qualite: champ_mixte`, D32) : tués de métropole rapportés à la population de la France entière, taux sous-estimé d'environ 3 % (4,6 publié contre 4,8 en métropole en 2024) ; source DG Mobilité et transports (API) ; taux homogène à recalculer par le pipeline (010593288 / 000067671 × 100 000) ; proposé à Léo en `retenu_socle` (motif) ; maintenance n° 9 close |
| `escroqueries`, `destructions_degradations` | motif « série courte » remplacé par `sens: ambigu` (D32) : taux de plainte de 12,8 % (escroqueries bancaires), 16,3 % (dégradations de la voiture) et 9,0 % (vandalisme contre le logement) ; taux pour 100 000 habitants avec `composantes` et `formule` |
| `vols_sans_violence` | `sens: ambigu` ; sauts « sans drapeau ni explication publiée » ; taux de plainte de 26,9 % |
| `risque_pauvrete_ressenti` | modalité 1 seule (NDV-4 : la modalité 3 est en `niveau_de_vie`) : définition, motif et `qualite` alignés, la baisse se retrouvant parmi les répondants qui ne se disent pas déjà pauvres (34,9 % puis 19,5 %) ; recoupé sur la publication DREES 2025 ; maintenance n° 3 à abandonner (SEC-2) |
| `vols_vehicules`, `cambriolages_logements` | taux de plainte mesurés (47,2 % et 44,6 % en 2019, INSEE ; 51 % et 52,7 % en 2020, SSMSI) à la place de l'argument de l'assurance ; sens `bas` gardé comme hypothèse (`sens_hypothese_plainte_stable`) ; pièces détachées (ICCS 05021) ; raccordement des cambriolages `a_etudier` |
| `victimes_violences`, `_physiques`, `_sexuelles`, `_conjugales`, `victimes_vols_violence` | raccordement `a_etudier` avec l'ampleur de la rupture CVS/VRS (ensemble -44 %, physiques -52 %, conjugales -60 %, sexuelles sans baisse visible) |
| `sentiment_insecurite_quartier` | suite VRS de l'INSEE (2022-2024) citée, non comparable ; drapeau `collecte_telephonique_2021` ; `ecarter` maintenu (D32) ; maintenance n° 5 précisée |
| `violences_physiques_enregistrees`, `violences_sexuelles_enregistrees`, `violences_intrafamiliales_enregistrees`, `victimes_traite` | motifs sur périodes alignées (agressions graves +26 % sur 2010-2018 contre 2,1 % → 2,1 % dans l'enquête) et taux de plainte ou de signalement (29,7 %, 22 %, 17,4 %, 6 %) ; `lacune_2015` pour la traite |
| `homicides`, `tues_route` (présélection) | 52 lignes `hlth_cd_*` de la long-list `sante` reprises (homicides X85-Y09, accidents de transport) : 34 variantes, 18 moyennes triennales écartées en bloc (SEC-1) |
| familles imbriquées | motifs de `victimes_violences` et de ses trois composantes, de `homicides` et `homicides_conjugaux` : « à ne pas cumuler au socle » |

Autres changements : toutes les lignes `crim_pris_*` (17) passent en `autre_dimension:democratie` (D33) ; règles v1.2 (`composantes` et `formule` pour 9 fiches, formule seule pour `sentiment_insecurite_quartier`) ; `surendettement` gardé en nombre (indicateur ODD 1.i5 publié, taux non recoupable, D34) ; `vols_violence_enregistres` (taux de signalement de 30 %) et `blesses_route` (blessés graves) précisés.

Chiffres après corrections : **33 fiches, 25 familles : 20 `retenir`, 4 `retenir_variante`, 9 `ecarter`** (dont 7 en `sens: ambigu`) ; 9 déclaratives ; 0 composite ; 7 incontournables ; 216 variantes. Présélection : 119 groupes (33 `fiche`, 74 `variante_de`, 11 `ecarte_en_bloc`, 1 `autre_dimension`) ; 984 lignes, dont 56 importées (54 de `sante`, 2 de `hors_grille`) ; 17 lignes `autre_dimension:democratie`. Vérificateur : 0 erreur, 0 avertissement. Tests : 397 réussis.

Liste de maintenance : n° 5 précisée et n° 9 close dans `docs/cr/maintenance_catalogues.md` ; nouveaux signalements SEC-1 à SEC-5 dans `docs/cr/maintenance_catalogues_securite.md` (table de correspondance des causes de décès, abandon de la n° 3, taux de dépôt de plainte SSMSI et taux de signalement OCDE comme séries de contexte, population de 14 ans ou plus).

À trancher : Léo — `tues_route` en `retenu_socle` ; ensemble **ou** composantes pour les violences et les homicides ; sens `bas` des cambriolages et vols de véhicules tant que la stabilité du taux de plainte n'est pas vérifiée. Session mère — `surendettement` en nombre ; import des lignes `crim_pris_*` par `democratie` ; lignes envoyées vers `securite` par `egalites`, `travail` et `niveau_de_vie` (prestations des chômeurs, endettement), non reprises.
