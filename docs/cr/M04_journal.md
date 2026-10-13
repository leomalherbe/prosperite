# Journal de bord — mission M04 (sources hors INSEE et Eurostat)

Tenu par l'agent de mission M04. Une entrée horodatée (heure de Paris) par sous-tâche : fait, résultat, problèmes.
Périmètre du lancement en cours : **phase 1** (T1 fiches par source, T2 tableau d'inventaire). La phase 2 (T3, indicateurs candidats) attend la validation de Léo.

---

## 2026-10-13 13:07 — Sous-tâche 0 : mise en route

- **Fait** : lecture de `CLAUDE.md`, `docs/00_charte_projet.md` (§3.5 niveaux de source, §4 grille v0), `docs/01_journal_decisions.md`, `docs/missions/M04_sources_hors_insee_eurostat.md`, `docs/archives/prototypes_indicateurs.csv`. Branche `m04-sources` recréée depuis `origin/main` (609ecc7).
- **Résultat** : 86 indicateurs dans les prototypes ; **20 relèvent de M04** : 16 Banque mondiale (WDI) et 4 Our World in Data (3 V-Dem, 1 RSF). Ils seront statués en fin d'inventaire (T2).
- **Méthode de vérification** : le bac à sable ne peut pas appeler les API depuis un script ; chaque voie d'accès est ouverte avec l'outil de lecture de page web (WebFetch). Une voie est `verifie` si l'URL ouverte renvoie bien des données (JSON, XML, CSV ou fichier tableur identifié) ; `probable` si la page de téléchargement est vue mais pas le fichier lui-même ; `non_verifie` sinon, avec la raison. Les extraits de réponses d'API sont enregistrés dans `tests/fixtures/<source>/`.
- **Problèmes** : aucun. La phase 1 ne touche ni `scripts/` ni `src/` (pas de déclenchement du workflow « Collecte »).
