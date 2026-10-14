# Journal de bord — M06, audit croisé de la dimension `democratie`

Agent auditeur M06, 14 octobre 2026, branche `m06-democratie` (worktree isolé). L'agent n'a pas participé à M05 `democratie`. Rapport : `docs/validation/audit_democratie.md`.

## 0. Mise en route

- `git fetch origin && git checkout -B m06-democratie origin/main` : base `1a0697c` (après les PR #11 `democratie` et #12 corrections `liens_bien_etre`, vérificateur v1.1, D31-D33).
- Lus : `CLAUDE.md` ; charte §3.1, §3.4, §3.6, §4, §5.1 ; journal des décisions D01-D33 (en particulier D17, D18, D28, D32, D33) ; fiche M06 ; `docs/methodo/33_methode_fiches_M05.md` v1.1 ; `indicateurs/dimensions.yaml` (définition, contenu, exclusions de `democratie`, R1-R8) ; `30_crosswalk_synthese.md` §5 et lignes `democratie` de `30_indicateurs_cadres_reference.csv` ; audits M06 `securite` et `liens_bien_etre` (format, exigence) ; journal et compte rendu M05 `democratie` ; `docs/cr/maintenance_catalogues.md`.
- Matériau audité : 32 fiches, `validation_democratie.csv`, `preselection_democratie.csv` (86 groupes), `preselection_democratie_lignes.csv` (253 lignes), `regles_preselection_democratie.csv`, long-list `democratie` (250 lignes), sorties du robot M04.
- Contrôle de départ : `python scripts/verifier_fiches.py --dimension democratie` (sans `--tableau`) → 0 erreur, 1 avertissement attendu (`citoyennete_active`) ; `git status` propre ensuite.

## 1. Échantillon

- D'office : 3 `ecarter` ; 12 incontournables (dont `participation_departementales`, déjà comptée) ; « à vérifier » au journal M05 (éligibilité `a_verifier` : 3 nouvelles ; raccordement `a_etudier` : `occupation_carcerale`) ; toutes les composites (7 nouvelles) ; participation électorale (déjà comptée). Soit 25 fiches.
- « Autres » fiches (ni `ecarter` ni incontournables) : 18 ; 20 % = 3,6, arrondi à 4 comme dans les audits précédents ; tirage parmi les 7 non retenues d'office : `random.Random(20261014).sample(sorted(pool), 4)` → `detention_provisoire`, `confiance_police`, `confiance_ecole`, `independance_justice_percue`.
- Total : 29 fiches ; contrôle léger des 3 restantes (`confiance_armee`, `confiance_justice`, `confiance_hopital` : valeurs BDM relues, motifs exacts).

## 2. Vérifications à la source (WebFetch, 14/10/2026)

| Source | Lu | Constat |
|---|---|---|
| Archives des résultats du ministère, présidentielle 2002 et 2007 (« France entière ») | 1er et 2d tours | 71,60 % (29 497 888 / 41 197 964) et 83,77 % (37 254 242 / 44 472 834) contre 72,11 % et 84,73 % au robot |
| Conseil constitutionnel 2012-152 PDR ; 2022-195 PDR (via blog Landot) | 1er tour | 2012 et 2022 identiques au robot |
| Archives du ministère, régionales 2004 | 1er tour | 60,84 % (25 453 092 / 41 835 232) contre 59,39 % |
| Maire-info (chiffre définitif du ministère, 11/03/2008) | municipales 2008 | 66,5 % France entière contre 58,86 % |
| data.gouv.fr, « Données des élections agrégées » | description | municipales 2008 : communes de plus de 3 500 habitants seulement ; municipales 2001 absentes |
| Communiqué du ministère, municipales 2026 | 1er tour | 57,1 % (robot 57,12 %) |
| Alliance solidaire (2022) | législatives | premières élections des députés des Français de l'étranger en juin 2012 |
| API Banque mondiale VA.EST, VA.SC, RL.EST, CC.EST ; documentation WGI | 1996-2025 | valeurs des fiches exactes ; scores 0-100 « pour faciliter les comparaisons dans le temps » |
| OWID, CSV filtrés France et métadonnées (V-Dem libérale et participative, Freedom House, CPI) | 1999-2025 | V-Dem v16, 1789-2025 ; Freedom House : années OWID = édition − 1 ; CPI 2012-2024 exact |
| API Eurostat `sdg_16_30`, `sdg_16_40`, `ilc_scp19`, `ilc_pw03`, `ilc_pw03b`, `crim_crt_case` | séries complètes | valeurs des fiches exactes ; `ilc_pw03b` (confiance institutionnelle EU-SILC) : 2013 seulement |
| BDM 010596049 à 010596054, 001779317, 001778320 | séries complètes | exactes |
| Métadonnées INSEE 16.i3 et 16.i4 (PDF) | — | rupture 2019 de la détention provisoire confirmée ; Cevipof, 3 500 inscrits, 18 ans ou plus |
| OCDE *How's Life? 2020*, chapitre engagement civique | — | « Having a say » défini sur PIAAC (16-65 ans) ; participation de la France = présidentielle |

Refus et erreurs : API Eurostat `sdg_16_50` (HTTP 429, limitation de débit ; page non relue, valeurs CPI vérifiées par OWID et l'extrait OCDE) ; `sdg_16_60` (erreur ; jeu « DISCONTINUED » d'après la recherche) ; archives des présidentielles 2012, européennes 1999 et 2004, municipales 2008, législatives 2002 et premier tour 2007 (erreur ou contenu absent) ; PDF des définitions de l'OCDE (robots.txt). Aucun outil d'accès à l'ordinateur de Léo, aucun navigateur, aucun appel d'API depuis un script.

Fichiers du dépôt lus : `interieur_elections__participation_par_scrutin.csv`, extraits OWID, OCDE (`hsl_bien_etre_actuel`, `hsl_bien_etre_futur`, `odd_16`, `hsl_definitions_pdf`), RSF 2002-2026, Freedom House 2013-2024, WJP 2025, DREES (couverture, dictionnaires), SSMSI (inventaire).

## 3. Complétude et cohérence (scripts jetables, gardés dans le bac à sable)

- Bilan des 253 lignes de présélection par décision et éligibilité ; 30 lignes éligibles écartées en bloc, motifs relus.
- Recherche par expressions régulières, dans les neuf autres long-lists, des concepts de la dimension (vote, élection, syndicat, confiance, justice, prison, corruption, liberté, citoyenneté) : trouvés `isoc_ci_ac_i` `I_IUVOTE` (participation en ligne) en `logement_cadre_vie`, lignes `crim_pris_*` et `crim_just_*` en `securite`, `sdg_05_50` et ODD 5.5.1 en `egalites`, `ilc_pw03` (confiance envers autrui) en `liens_bien_etre`.
- Croisement des 32 fiches avec les 105 fiches des autres dimensions (séries, composantes, variantes, lignes) : aucun identifiant, aucune série ni aucune ligne commune.
- Recherches sans résultat : non-inscription électorale dans les catalogues INSEE ; confiance institutionnelle EU-SILC après 2013 ; DREES OG04_10 (2025 seulement).

## 4. Résultat

29 fiches auditées : 18 `conforme`, 10 `a_corriger` (participation présidentielle, législatives, municipales, régionales et Freedom House pour erreur factuelle ; trois V-Dem et deux WGI pour alignement sur D32 et D33), 1 `non_verifiable` (`voix_pouvoirs_publics`, source primaire). 4 oublis (adhésion syndicale, participation en ligne, lignes de prisons restées en `securite`, non-inscription), 7 points inter-dimensions, 8 désaccords de jugement. Avis global : `corrections_necessaires`, 10 corrections ordonnées.

## 5. Livraison

- Fichiers créés : `docs/validation/audit_democratie.md` et ce journal. Aucune fiche, aucun tableau, aucun script ni aucun catalogue n'a été modifié ; ni la charte, ni le journal des décisions, ni `CLAUDE.md`, ni les fiches de mission.
- Commits sur `m06-democratie`, push, PR #14 vers `main` ouverte par l'API GitHub (« M06 — audit croisé : democratie ») ; rapport déposé dans le Projet sous `claude/cr/M06_democratie_audit.md`.
