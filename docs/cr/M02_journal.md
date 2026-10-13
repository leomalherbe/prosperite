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
