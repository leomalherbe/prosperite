# Journal de bord — M06, audit croisé de la dimension `securite`

Agent auditeur M06, 14 octobre 2026, branche `m06-securite` (worktree isolé). L'agent n'a pas participé à M05 `securite`. Rapport : `docs/validation/audit_securite.md`.

## 0. Mise en route

- `git fetch origin && git checkout -B m06-securite origin/main` : base `48e2381` (fusion de la PR #7, fiches `securite`).
- Lus : `CLAUDE.md` ; charte §3.1, §3.4, §3.6, §4, §5.1 ; journal des décisions D13-D30 ; fiche M06 ; `docs/methodo/33_methode_fiches_M05.md` ; `indicateurs/dimensions.yaml` (définition et exclusions de `securite` : A6, A11, A15 ; D29 P8) ; `docs/methodo/30_crosswalk_synthese.md` §5 et `30_indicateurs_cadres_reference.csv` (lignes sécurité) ; journal et compte rendu M05 `securite` ; `docs/cr/maintenance_catalogues.md` ; `docs/sources/autres_sources.md` §2.2 et §2.4.
- Matériau audité : 33 fiches, `validation_securite.csv`, `preselection_securite.csv` (116 groupes), `preselection_securite_lignes.csv`, `regles_preselection_securite.csv`, `catalogues/longlist_securite.csv.gz` (928 lignes).
- Contrôle de départ : `python scripts/verifier_fiches.py --dimension securite` (sans `--tableau`, donc sans écriture) → 0 erreur, 0 avertissement ; `git status` propre ensuite.

## 1. Échantillon

- D'office : 9 `ecarter` ; 7 `incontournable: oui` (dont `sentiment_insecurite_quartier`, déjà comptée) ; `a_verifier` (`pauvrete_actifs_liquides`, `securite_nuit`) ; `a_etudier` (`sentiment_insecurite_quartier`, `surendettement`, `vols_vehicules`) ; `tues_route` (consigne de la session mère). Cela fait 18 fiches distinctes.
- Tirage aléatoire de 20 % des 18 « autres » fiches (ni `ecarter` ni incontournables), arrondi à 4, parmi les 15 qui n'étaient pas déjà retenues d'office : `random.seed(20261014)`, `random.sample(sorted(pool), 4)` → `homicides_conjugaux`, `solde_situation_financiere_passee`, `victimes_violences_conjugales`, `victimes_violences_physiques`.
- Total : 22 fiches.

## 2. Vérifications à la source (WebFetch, 14/10/2026)

| Source | Lu | Constat |
|---|---|---|
| Eurostat `sdg_11_40` (TOTAL, RT, FR) | 2000-2024 | 13,3 → 4,6 ; `b` 2014, `p` 2023-2024 ; jeux sources DEMO_GIND et TRAN_SF_ROADRO ; organisme : DG MOVE |
| Eurostat `tran_sf_roadro` (NR, FR) | 2018-2024 | 3 246, 3 238, 2 538, 2 931, 3 260, 3 154, 3 181 |
| BDM 010593288 (tués, FM) | 2010-2024 | 3 248 (2018) … 3 193 (2024) : 2 à 13 de plus qu'Eurostat chaque année |
| Eurostat `demo_gind` (AVG, FR) | 2018-2025 | 68 775 952 en 2024 ; 3 181 / 68 775 952 = 4,63 (publié 4,6) ; formule exacte pour 2018, 2020, 2021, 2022 |
| BDM 000067671 (population moyenne FM) | 2018-2025 | 66 479 199 en 2024 → taux FM 4,80 |
| Eurostat `crim_off_cat` ICCS020111, 0301, 0502, 0401, 05021, 05012 | 2008-2024 | valeurs des motifs retrouvées ; lacunes 2017-2019 pour 05021 et 05012 ; aucun drapeau |
| Eurostat `crim_hom_soff` (victimes), `crim_hom_vrel` (IPTN) | 2008-2024, 2015-2024 | 1,03-1,60 ; 0,15-0,19 |
| Banque mondiale `VC.IHR.PSRC.P5` | 2000-2023 | écart avec Eurostat de 0,009 à 0,035 (2008-2023), toujours positif |
| Eurostat `sdg_16_70`, `tran_sf_railvi` | 2008-2024, 2006-2024 | 16 valeurs (aucune en 2015) ; 19 valeurs |
| Eurostat `ilc_mddw03`, `ilc_mdes04`, `tran_r_acci` (INJ) | séries complètes | valeurs, drapeaux et lacunes conformes aux fiches |
| BDM 010596041, 010596044, 010596045, 010596046 | 2010-2025 | CVS 2010-2018, VRS 2021-2023, rien en 2019-2020 ; FM |
| BDM 010594499, 000857184 | 2010-2024 ; depuis 1970 | surendettement FM ; solde brut FM, mensuel depuis 1970-01 |
| data.gouv.fr, jeu CVS `62029493ff5c2e6d510b42b6` | métadonnées | CVS 2007-2021 ; collecte 2021 à 99 % par téléphone, comparaison déconseillée ; VRS depuis 2022 |
| insee.fr 2526402 | page | VRS 2022-2024, sentiment d'insécurité par sexe et âge (xlsx), 18 ans ou plus, FM et 3 DROM, sans total d'ensemble |
| insee.fr 2526026 | page | CVS 2007-2019 ; taux de plainte en 2019 : cambriolage ou tentative 44,6 %, vol ou tentative de vol de voiture 47,2 %, destruction ou dégradation de la voiture 16,3 % |
| API data.gouv.fr (recherche) | 3 requêtes | aucun jeu VRS ; aucun jeu sur les morts violentes au sein du couple |
| `statistiques.interieur.gouv.fr` (page VRS) | — | accès refusé dans le bac à sable : non lu |

Fichiers du dépôt lus (extraits des robots) : inventaire SSMSI (`ssmsi__series_chronologiques.csv`, 3 828 séries : périodes des séries enregistrées et taux de dépôt de plainte), OCDE (`ocde__hsl_bien_etre_actuel.csv` pour 10_2, 10_3 et 1_6 ; `ocde__odd_16.csv`), DREES (distributions d'og04_4 et de pe03, dictionnaires).

Limites : le fichier SSMSI (24,6 Mo) n'est pas lisible par WebFetch, donc seules les périodes et les dernières valeurs des séries SSMSI ont été contrôlées ; l'âge minimal du baromètre DREES n'a pas été vérifié.

## 3. Complétude et cohérence (scripts jetables, gardés dans le bac à sable)

- Recherche par expression régulière, dans les dix long-lists, des concepts de sécurité rattachés ailleurs. Trouvés : les causes de décès « homicides » et « accidents de transport » dans `sante` (`hlth_cd_asdr2`, `acdr2`, `ysdr2`) ; les taux de dépôt de plainte dans `democratie` ; l'incarcération dans `democratie` ; `ilc_mdes09` dans `niveau_de_vie` ; les parts de femmes victimes dans `egalites`.
- Croisement des fiches `securite` et `liens_bien_etre` (séries principales et variantes) et des deux présélections ligne à ligne : aucune série ni ligne commune ; aucun identifiant en double.
- Tous les codes `crim_off_cat` pour la France du catalogue Eurostat sont traités par la présélection.

## 4. Résultat

22 fiches auditées : 16 `conforme`, 6 `a_corriger` (`tues_route`, `vols_vehicules`, `sentiment_insecurite_quartier`, `escroqueries`, `destructions_degradations`, `vols_sans_violence`), 0 `non_verifiable`. Avis global : `corrections_necessaires` (mineures), 10 corrections ordonnées. Hors échantillon : `risque_pauvrete_ressenti` (définition incohérente), `cambriolages_logements` (même argument de plainte que `vols_vehicules`).

## 5. Livraison

- Fichiers créés : `docs/validation/audit_securite.md` et ce journal. Aucune fiche, aucun script ni aucun catalogue n'a été modifié.
- Commit sur `m06-securite`, push, PR vers `main` ouverte par l'API GitHub (« M06 — audit croisé : securite ») ; rapport déposé dans le Projet sous `claude/cr/M06_securite_audit.md`.
