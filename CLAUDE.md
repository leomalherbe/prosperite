# Consignes pour les sessions Claude travaillant dans ce dépôt

Projet : **Observatoire de la prospérité** — indicateur synthétique multidimensionnel de prospérité subjective pour la France. Tout est en français.

## À lire avant d'agir
1. `docs/00_charte_projet.md` — finalités, décisions, grille de dimensions v0, schémas de données, architecture, conventions. **Fait foi.**
2. `docs/01_journal_decisions.md` — décisions actées et questions ouvertes.
3. Ta fiche de mission dans `docs/missions/Mxx_*.md` (la même existe dans le Projet claude.ai).

## Règles
- Un agent **ne modifie jamais** la charte ni le journal des décisions : il propose dans son compte rendu (`docs/cr/Mxx_compte_rendu.md`, copié aussi dans le Projet claude.ai sous `claude/cr/`).
- Travailler sur une branche `mNN-<sujet>` (ex. `m01-insee`), commits en français, puis ouvrir une pull request vers `main`. Avant de pousser : `git fetch origin main` et rebaser si nécessaire.
- Aucune clé d'API ni secret dans le code (variables d'environnement, secrets GitHub).
- Aucune valeur inventée : une information introuvable est marquée « non trouvé ».

## Contrainte réseau (importante)
Le bac à sable des sessions **ne peut pas appeler les API statistiques** depuis un script (réseau limité à GitHub et aux dépôts de paquets). En conséquence :
- Pour **voir** la réponse d'une API (structure, exemple de valeurs), utiliser l'outil de lecture de page web (WebFetch) sur l'URL de l'API et enregistrer la réponse comme fixture dans `tests/fixtures/<source>/`.
- Le code doit être **testé hors ligne** (`python -m pytest -q`) sur ces fixtures.
- L'exécution réelle se fait sur **GitHub Actions**, workflow « Collecte » : chaque script de collecte est un fichier autonome `scripts/collecte_<source>.py` qui écrit dans `catalogues/` ou `donnees/`. Lancer : `gh workflow run collecte.yml --ref <branche> -f cible=collecte_<source>.py`, puis suivre : `gh run list --workflow=collecte.yml --limit 3`, `gh run watch <id>`, `gh run view <id> --log`. Les résultats sont commités automatiquement sur la branche.

## Où mettre quoi
| Contenu | Emplacement |
|---|---|
| Module d'accès à une source | `src/sources/<source>.py` (fonctions : lister le catalogue, obtenir une série → lignes `serie_id, geo, periode, valeur, statut`) |
| Script de collecte exécuté par Actions | `scripts/collecte_<source>.py` |
| Tests et fixtures | `tests/test_<source>.py`, `tests/fixtures/<source>/` |
| Fiche documentaire d'une source | `docs/sources/<source>.md` |
| Catalogues de séries candidates (CSV, colonnes charte §5.3) | `catalogues/<source>_catalogue.csv` |
| Fiches indicateurs (YAML, schéma charte §5.1) et grille de dimensions | `indicateurs/` |
| Données figées et datées | `donnees/millesimes/<AAAA-MM-JJ>/` |
| Calcul de l'indice (référence unique) | `src/scoring/calcul.py` — ne pas dupliquer la logique ailleurs |
| Application web | `site/` |

## Commandes
- Tests : `pip install -r requirements.txt && python -m pytest -q`
- Collecte locale (ne fonctionne que sur GitHub Actions) : `python scripts/lancer_collecte.py --cible collecte_<source>.py`
