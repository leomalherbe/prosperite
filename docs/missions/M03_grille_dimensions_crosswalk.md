# Fiche de mission M03 — Cadres de référence, crosswalk et grille de dimensions v1

**Prompt de lancement** (à coller dans une nouvelle session rattachée au Projet « Observatoire de la prospérité ») :

> Tu es un agent du projet « Observatoire de la prospérité ». Lis d'abord dans le Projet la charte `claude/00_charte_projet.md`, puis cette fiche de mission `claude/missions/M03_grille_dimensions_crosswalk.md`. Exécute-la intégralement, en français, sans modifier la charte ni le journal des décisions. Termine par un compte rendu dans `claude/cr/M03_compte_rendu.md`.

**Modèle conseillé** : Sonnet 5.5 (travail documentaire, pas de code). **Peut démarrer immédiatement** (aucune dépendance technique). **Durée estimée** : 1 session longue.

## Contexte
La charte (§3.4, D02) retient la voie **top-down conceptuelle** : les dimensions de l'indicateur sont construites en croisant les cadres de référence existants, pas par clustering statistique. La grille v0 (charte §4) est une hypothèse de travail de 10 dimensions. Cette mission la met à l'épreuve des cadres et prépare le socle des bornes (les seuils et cibles que ces cadres définissent).

## Objectif
1. Extraire **dimensions, indicateurs, définitions et seuils/cibles** de six cadres de référence.
2. Construire le **crosswalk** cadre → grille v0.
3. Proposer une **grille v1 (≤ 10 dimensions)** argumentée, avec les arbitrages des questions ouvertes.

## Tâches

### T1. Extraction des cadres (une section par cadre, même structure)
Pour chaque cadre : liste des dimensions ; liste des indicateurs par dimension (libellé, définition courte, unité, sens, seuil minimal ou cible s'il existe, source de données citée) ; principe d'agrégation ; remarques sur la pertinence pour la France.
1. **Doughnut 3.0** — Fanning & Raworth, *Nature* 646 (2025), 47–56, `https://www.nature.com/articles/s41586-025-09385-1` : 12 dimensions sociales, 9 plafonds écologiques, 35 indicateurs ; lire les tableaux 1 et 2 et, si accessibles, les tableaux supplémentaires (seuils). Compléter par `https://doughnuteconomics.org/news/doughnut-3-0-is-here` et l'explorateur de données du site.
2. **Rapport Stiglitz-Sen-Fitoussi (2009)** : 8 dimensions du bien-être et recommandations (dont la place du subjectif et la soutenabilité).
3. **OCDE, *How's Life?* (édition la plus récente) et Better Life Index** : 11 dimensions du bien-être actuel, 4 capitaux (ressources pour le futur), indicateurs et, pour la France, valeurs récentes si disponibles.
4. **Eurostat, cadre « Quality of life »** : 8 dimensions + 1 (expérience globale de la vie), indicateurs et codes de jeux de données.
5. **INSEE, *Les nouveaux indicateurs de richesse* (loi du 13 avril 2015)**, rapport 2025 : `https://www.insee.fr/fr/statistiques/fichier/3281778/NIR2025.pdf` — 10 indicateurs, définitions, séries.
6. **ODD / UN SDG indicators** (uniquement les cibles chiffrées pour 2030 utiles au socle des bornes : pauvreté, NEET, mortalité, énergies renouvelables, etc.) et **objectifs officiels français** (SNBC, zéro artificialisation nette, objectifs de la loi énergie-climat, objectif de taux d'emploi, etc.) : relever les cibles chiffrées avec leur référence.

### T2. Crosswalk
Tableau CSV `30_indicateurs_cadres_reference.csv`, une ligne par indicateur de cadre : `cadre, dimension_cadre, indicateur, definition, unite, sens, seuil_ou_cible, type_seuil (minimum|cible|limite), reference_seuil, source_donnees_citee, dimension_v0_proposee, disponibilite_france_estimee (oui|probable|non|inconnue), commentaire`.
Puis une matrice de synthèse (markdown) : cadres en colonnes, dimensions v0 en lignes, nombre d'indicateurs rattachés dans chaque case ; cases vides = dimensions v0 non couvertes ; indicateurs non rattachables = besoins non couverts par v0.

### T3. Proposition de grille v1
Document `30_grille_dimensions_v1_proposition.md` : pour chaque dimension (≤ 10) : id, libellé, définition en une phrase, type (plancher/plafond), contenu, indicateurs « incontournables » (ceux présents dans ≥ 3 cadres), indicateurs déclaratifs possibles. Traiter explicitement les arbitrages ouverts de la charte (journal, Q-B) : place de la satisfaction globale dans la vie ; alimentation ; énergie ; innovation/infrastructures ; et tout point que l'analyse révèle (ex. « temps » comme dimension à part ? « soutenabilité économique » — dette, capital — où ?). Donner pour chaque arbitrage deux options et une recommandation.

## Livrables (docs Projet)
- `claude/30_cadres_reference_extraction.md` (T1).
- `claude/30_indicateurs_cadres_reference.csv` (T2 ; le CSV est déposé comme doc Projet et envoyé en pièce jointe dans la conversation).
- `claude/30_crosswalk_synthese.md` (T2, matrice).
- `claude/30_grille_dimensions_v1_proposition.md` (T3).
- `claude/cr/M03_compte_rendu.md`.

## Critères d'acceptation
- Chaque indicateur de cadre porte une source précise (page, tableau) ; les seuils/cibles ont une référence vérifiable ; aucun chiffre n'est reconstitué de mémoire sans mention « à vérifier ».
- Les 35 indicateurs du Doughnut 3.0 et les 10 indicateurs INSEE sont tous présents dans le CSV.
- La grille v1 respecte la limite de 10 dimensions et justifie chaque fusion ou scission par rapport à v0.

## Pièges connus
- Le texte du *Nature* accessible en ligne peut être tronqué avant les tableaux : chercher les Supplementary Information et la page méthodologique du site Doughnut.
- Ne pas confondre les dimensions du Doughnut global avec celles des « portraits de ville » (Doughnut Unrolled), qui mêlent local/global : ne retenir que le cadre global 3.0, et signaler les adaptations locales en remarque.
- Les 11 dimensions OCDE et les 8+1 Eurostat se recoupent largement : le crosswalk doit rendre visibles les différences de découpage (ex. « sécurité » séparée ou non de « conditions matérielles »).
