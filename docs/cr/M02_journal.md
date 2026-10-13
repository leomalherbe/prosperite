# Journal de bord — mission M02 (Eurostat)

Tenu par l'agent de mission M02. Une entrée horodatée (heure de Paris) par sous-tâche : fait, résultat, problèmes.
Périmètre du lancement en cours : **phase 1** (A1 fiche source + statut des séries des prototypes + repérage des dossiers prioritaires du TOC).

---

## 2026-10-13 13:05 — Sous-tâche 0 : mise en route

- **Fait** : lecture de `CLAUDE.md`, `docs/00_charte_projet.md`, `docs/01_journal_decisions.md`, `docs/missions/M02_eurostat.md`, `docs/archives/README.md`, `docs/archives/prototypes_indicateurs.csv`. Branche `m02-eurostat` recréée depuis `origin/main` (609ecc7).
- **Résultat** : 86 indicateurs dans les prototypes, dont **66 d'origine Eurostat** (62 codes `sdg_*`, plus `ilc_lvho05a`, `ilc_lvho03`, `cei_pc031`, `env_wasmun`) ; 16 Banque mondiale et 4 OWID hors périmètre (M04). *(Corrigé à 13 h 25 : 62 et non 63 codes `sdg_*`.)*
- **Problèmes** : aucun. Note : le workflow « Collecte » se déclenche sur push d'une branche `mNN-*` modifiant `scripts/` ou `src/` ; la phase 1 ne touche ni l'un ni l'autre (pas de déclenchement attendu).

## 2026-10-13 13:26 — Sous-tâche 1 : fiche source A1 et fixtures

- **Fait** : lecture de la documentation officielle (introduction API, API Statistics, SDMX 2.1 données et structure, catalogue/TOC, API asynchrone, FAQ, format TSV, licence, WADL du catalogue) ; requêtes réelles par WebFetch sur le TOC (`en` et `fr`), l'API Statistics (`sdg_08_10`, `sdg_01_10`), SDMX 2.1 (datastructure `SDG_08_10`, données TSV, liste de codes `OBS_FLAG`), le service `catalogue/relations` et les schémas de catégories `popul`, `envir`, `cc`, `tb_eu`.
- **Résultat** : `docs/sources/eurostat.md` (sections 1 à 6 et 8 ; sections 7 et 9 complétées aux sous-tâches suivantes) ; 7 fixtures dans `tests/fixtures/eurostat/` (extraits du TOC en/fr, 2 réponses JSON-stat, 1 TSV SDMX, résumé de DSD, liste des drapeaux).
- **Problèmes** :
  - WebFetch résume au lieu de citer (citations ≤ 125 caractères) : fixtures **reconstituées champ par champ** en demandant les valeurs exactes chemin par chemin ; provenance et omissions documentées (§8 de la fiche).
  - WebFetch tronque à ~78 000 caractères : **le TOC complet n'est pas lisible** depuis la session (seul son début l'est) ; idem pour les schémas de catégories volumineux.
  - Limite de débit du proxy WebFetch (HTTP 429) à deux reprises ; pages non lues et non redemandées : `sdmx/2.1/categoryscheme/ESTAT/sdg`, `sdmx/2.1/categoryscheme/ESTAT/economy`, `sdmx/2.1/dataflow/ESTAT/ILC_LI02?references=parents`. Rythme ralenti ensuite (pauses de 45 à 70 s).
  - `dataflow/ESTAT/ILC_LI02?references=categorisation` refusé (erreur client) : la recherche du chemin d'un jeu par ses catégorisations n'est pas possible ainsi.
  - Constat : TOC `lang=fr` en retard sur `lang=en` (dates de mise à jour différentes pour un même jeu).

---

# Phase 2 (A2, A3, A4, B) — nouvel agent (session neuve, décision D13)

## 2026-10-13 15:05 — Sous-tâche 2.0 : reprise et mise en place

- **Fait** : branche `m02-eurostat` recréée depuis `origin/m02-eurostat` (995af17) et fusion de `origin/main` (charte v1.1, journal D13–D22, fiches M05/M06) ; lecture de `CLAUDE.md`, charte, journal des décisions (D13 à D22, notamment D21 sur les ventilations), fiche M02, livrables de phase 1 (ce journal, `docs/sources/eurostat.md`, `docs/sources/eurostat_amorce_prototypes.csv`, fixtures), `docs/archives/prototypes_indicateurs.csv`, `scripts/lancer_collecte.py`, `scripts/actions.py`, `.github/workflows/collecte.yml`, `src/scoring/calcul.py`.
- **Résultat** : état de départ = fiche source complète (sections 7 et 9 encore à remplir), 7 fixtures reconstituées par WebFetch, **27 séries d'amorce statuées sur 66** (25 disponibles, 1 sans donnée FR, 2 non vérifiées). Tests existants : 14 passent.
- **Plan** : (1) module `src/sources/eurostat.py` + logique de catalogue `src/pipeline/catalogue_eurostat.py` + tests hors ligne ; (2) script reprenable `scripts/collecte_eurostat.py` (étapes : échantillons réels pour les fixtures, amorce des 66 séries, niveau 1 sur le TOC complet, niveau 2 par jeu candidat) avec fichier d'état `catalogues/eurostat_etat_collecte.json` ; (3) premier passage du robot en mode essai (niveau 2 limité), remplacement des fixtures reconstituées par les réponses réelles, corrections, puis passages complets.
- **Problèmes** : aucun.

## 2026-10-13 15:23 — Sous-tâche 2.1 : modules A2, script A3/A4, tests hors ligne

- **Fait** :
  - `src/sources/eurostat.py` : `ClientEurostat` (requêtes séquentielles, pause 0,2 s, nouveaux essais avec attente ×3 sur 429/5xx/coupure, respect de `Retry-After`) ; `lire_toc()` / `analyser_toc()` (TOC tabulé → DataFrame, profondeur par indentation, `theme_source` = chemin des dossiers, `theme_codes`, `parent`, dates ISO) ; `decrire_jeu()` / `analyser_structure()` (SDMX-ML 2.1 indépendant des préfixes : `dataflow?references=descendants&detail=referencepartial`, repli `datastructure?references=children`) ; `obtenir_donnees()` / `obtenir_jeu()` / `analyser_jsonstat()` (ordre `id`/`size`, `value` et `status` clairsemés ou en liste, `status` absent toléré, erreurs → `AucuneDonnee`, `ReponseAsynchrone`, `ExtractionTropVolumineuse`, `ErreurEurostat`). Identifiant de série = code du jeu + filtres de l'API Statistics (`sdg_01_10?freq=A&age=TOTAL&unit=PC&geo=FR`), directement réutilisable.
  - `src/pipeline/catalogue_eurostat.py` : niveau 1 (dossiers prioritaires par code et par titre de dossier, étiquette `dimension_v0` par mots-clés en/fr pondérés titre principal 2 / partie « by… » 0,5 / chemin 1, repli ODD puis dossier ; filtres de dates ; règle `candidat` motivée) ; niveau 2 (rôle des dimensions : contenu énuméré, totaux fixés, ventilations sexe/âge/quantile/type de ménage/éducation/degré d'urbanisation, unité principale choisie par série ; séries `defaut` + une ligne `ventilation` par dimension avec la couverture de chaque modalité ; éligibilité ≥ 10 années depuis 2000 et fin ≥ 2020) ; planification des requêtes (fixation des totaux puis découpage pour les jeux volumineux) ; lignes de l'amorce.
  - `scripts/collecte_eurostat.py` : quatre étapes reprenables (échantillons réels, amorce, niveau 1, niveau 2), état `catalogues/eurostat_etat_collecte.json`, bilan `catalogues/eurostat_bilan.json`, arrêt propre à 270 min, niveau 2 limité à 40 jeux pour ce premier passage (contrôle de la logique sur un échantillon varié).
  - `tests/test_eurostat.py` : 58 tests (72 au total avec le calcul) ; simulation complète du script hors ligne (réponses servies depuis les fixtures) concluante.
- **Choix à faire valider** (repris dans le compte rendu) : (1) jeux infra-annuels non candidats (une version annuelle existe en général) ; (2) **rattrapage** des jeux pertinents commençant après 2010 mais pouvant avoir ≥ 10 années (sinon l'AROPE 2021, `sdg_01_10`, `ilc_pecs01`… seraient perdus par le filtre `dataStart ≤ 2010`) ; (3) ventilations en **une ligne par dimension** (couverture de chaque modalité dans `modalites_ventilation`) plutôt qu'une ligne par modalité, pour garder un catalogue de taille maniable.
- **Problèmes** : aucun. Prochaine étape : pousser (déclenche le robot), lire le journal, remplacer les fixtures reconstituées par les échantillons réels.

## 2026-10-13 15:42 — Sous-tâche 2.2 : premier passage du robot (essai), fixtures réelles, corrections

- **Fait** : passage 1 du robot (run 38404425489, 2 min 24 s au total, 160 requêtes, 0 nouvel essai) : échantillons réels, amorce des 66 séries, niveau 1 complet, niveau 2 limité à 40 jeux. Lecture du journal `journaux/collecte_2026-10-13T1322_collecte_eurostat.py.log` et des sorties.
- **Résultats** :
  - TOC : 12 234 entrées, 6 649 jeux, 911 tableaux, 1 878 dossiers ; metabase : 1 344 860 lignes (jeu, dimension, modalité) pour 7 600 jeux (4 Mo compressés).
  - Amorce : le robot retrouve exactement les valeurs de phase 1 pour les 25 séries déjà vérifiées (seules différences : présentation de `jeu_source`, et `edu_outc_pisa` de phase 1 corrigé en `educ_outc_pisa` d'après l'annotation). Nouveaux statuts : 55 disponibles, 6 séries courtes, 3 sans donnée FR, 2 codes disparus (`sdg_05_60`, `sdg_15_10`).
  - Niveau 2 (40 jeux) : environ 1 s par jeu (2 requêtes) ; rôles des dimensions corrects dans l'ensemble.
- **Pièges découverts** (ajoutés à la fiche source) : (1) les **indicateurs ODD `sdg_*` sont typés « table »** dans le TOC (seuls 33 codes `sdg_*` sont des « dataset ») : le filtre strict `type = dataset` aurait perdu l'essentiel du dossier ODD ; (2) la racine « Cross cutting topics » porte **aussi le code `data`** ; (3) les lignes de dossiers se terminent par un champ vide (et non `" "`) ; (4) une modalité inexistante renvoie HTTP 200 avec un cube vide (taille 0), sans erreur ; (5) un jeu inexistant renvoie 404 `{"error":[{…"id":100…}]}` (liste) et, en SDMX, une enveloppe SOAP `Fault` ; (6) `lastTimePeriod=N` = les N dernières périodes ; (7) `sdg_13_11`, `sdg_15_60`, `sdg_15_61` sont des agrégats UE seulement.
- **Corrections** (versions d'étapes portées à 2 : amorce, niveau 1 et niveau 2 refaits) : tableaux inclus au niveau 1, `sdg_*` candidats (exception motivée), autres tableaux non candidats ; racine principale repérée par son titre ; préfixe de code prioritaire sur l'emplacement pour le dossier prioritaire ; repli ODD par le dossier « Goal NN » ; `icd10` (causes de décès) toujours énumérée ; `ind_type` (isoc) en ventilation (total `IND_TOTAL`) ; colonnes du catalogue des séries allégées (≈ 930 octets par ligne au passage 1) et compression automatique au-delà de 90 Mo ; remplacements de l'amorce vérifiés par le robot (`sdg_05_61`, `sdg_15_11`, `sdg_13_10`, `env_bio3`) ; prise en charge de l'erreur SOAP.
- **Fixtures** : les fixtures reconstituées de phase 1 sont remplacées par les réponses brutes du robot (TOC en/fr, JSON-stat `sdg_01_10` et `sdg_08_10`, TSV) ou complétées (structures SDMX réelles `dataflow…referencepartial` et `datastructure`, `ilc_li02`, `lastTimePeriod`, cube vide, erreurs 404 JSON et SOAP, extrait de metabase, `echantillons_info.json`) ; le résumé de DSD reconstitué est supprimé ; seule `codelist_OBS_FLAG_fr.tsv` reste de phase 1. 84 tests passent.
- **Problèmes** : aucun bloquant. Prochaine étape : passage complet (niveau 2 sans limite).

## 2026-10-13 15:55 — Sous-tâche 2.3 : passage complet lancé, affinage du niveau 1

- **Fait** : passage 2 lancé automatiquement par le push (run 38405905176, 13 h 33 UTC) : amorce v2, niveau 1 v2, niveau 2 complet. Pendant ce temps, contrôle de l'étiquetage sur un échantillon aléatoire de candidats par dimension (pseudo-TOC reconstruit depuis le catalogue du passage 1).
- **Constats** : étiquettes justes dans les dossiers prioritaires ; bruit hors de ces dossiers : jeux des pays du voisinage et candidats (`enps_*`, `enpe_*`, dossier « Non EU countries » : 176 jeux sans France), tourisme (« accommodation » → logement), trafic aérien par aéroport (« passenger transport »), « cultures » français (= récoltes) → culture, « fertility » → engrais, « government »/« seats » nus → démocratie, et 41 jeux de **projections** jusqu'en 2100 repêchés par la règle de rattrapage.
- **Corrections** (niveau 1 v3, poussées pendant le passage 2 : le robot les exécutera au passage suivant, mis en file d'attente) : exclusion motivée des jeux hors France et des projections (fin > 2027) ; mots-clés affinés ; plus de repli « population → santé » ; un recalcul du niveau 1 rouvre le niveau 2 (retrait des jeux qui ne sont plus candidats, traitement des nouveaux). Effet mesuré hors ligne sur les jeux : 2 143 candidats au lieu de 2 413 (hors tableaux ODD). 86 tests passent.
- **Problèmes** : aucun.
