# Charte du projet — Observatoire de la prospérité

Version 1.1 — 13 octobre 2026 (§3.6 et feuille de route mis à jour après la phase 1) — rédigée par la session mère, validée par Léo Malherbe.
Document de référence pour toutes les sessions et tous les agents du projet. **À lire avant toute mission.**

---

## 1. Objet

Construire un **indicateur synthétique multidimensionnel de prospérité subjective pour la France**, et l'outil (observatoire) qui permet à chacun de le paramétrer.

Deux finalités à terme :
1. Proposer un indicateur de prospérité **alternatif au PIB**, fondé sur ce qui compte réellement aux yeux des gens.
2. Utiliser l'outil pour **collecter les préférences** (poids, choix d'indicateurs, seuils) d'un grand nombre d'utilisateurs, afin de produire un **indicateur intersubjectif** : l'indice calculé avec la pondération et le calibrage moyens (ou médians) des utilisateurs.

## 2. Périmètre de la version 1

| Élément | Décision |
|---|---|
| Territoire | **France, échelle nationale uniquement.** Le modèle de données prévoit une clé géographique (`geo`) pour une extension territoriale ultérieure, non exploitée en v1. |
| Période | **2000 → aujourd'hui**, trajectoire annuelle. |
| Langue | **Tout en français** (interface, documentation, identifiants d'indicateurs en français sans accents, ex. `taux_pauvrete_60`). |
| Public v1 | Les trois niveaux d'usage (rapide / avancé / expert) sont conservés ; le **jeu grand public** prime pour l'ergonomie. |
| Comparaisons internationales | Hors périmètre v1. Les séries étrangères ne servent qu'au calibrage des bornes (référence européenne). |

## 3. Principes méthodologiques actés

### 3.1 Deux sens de « subjectif », distingués explicitement
- **Subjectivité du paramétrage** : chaque utilisateur choisit dimensions, poids, indicateurs, seuils, règle d'agrégation. C'est le cœur de l'outil.
- **Données déclaratives** : les indicateurs de bien-être ressenti (satisfaction dans la vie, santé perçue, confiance, sentiment d'insécurité…) sont admis **comme indicateurs** dans les dimensions, signalés par un drapeau `declaratif = oui`. Ils ne constituent pas une dimension à part (sauf arbitrage en mission M03).

### 3.2 Un seul indice, mais des règles d'agrégation au choix
- Sortie principale : **un indice unique 0–100**, plus les scores par dimension, la trajectoire et la couverture.
- Normalisation d'un indicateur : deux bornes fixées par l'utilisateur, **seuil minimal** (score 0, « niveau minimal acceptable », aussi appelé plancher) et **objectif** (score 100, « niveau souhaitable », aussi appelé plafond). Linéaire entre les deux, borné à [0,100]. Le sens (haut/bas) est porté par la fiche indicateur ; pour un indicateur « bas » (ex. taux de pauvreté), le seuil minimal est numériquement supérieur à l'objectif.
- **Règle d'agrégation choisie par l'utilisateur**, aux deux niveaux (indicateurs → dimension, dimensions → indice), via une **moyenne généralisée pondérée** d'ordre p :
  - p = 1 : moyenne arithmétique (compensation totale, défaut actuel) ;
  - p → 0 : moyenne géométrique (compensation limitée, type IDH) ;
  - p → −∞ : minimum pondéré (« maillon faible », aucune compensation).
  Dans l'interface, un seul réglage « degré de compensation » avec trois positions (totale / limitée / nulle). Les scores sont planchonnés à 1 pour éviter l'annulation par un zéro avec p ≤ 0.
- Les indicateurs sans donnée sont ignorés dans la moyenne et la **couverture** (n disponibles / n sélectionnés) est toujours affichée.

### 3.3 Bornes initiales puis bornes émergentes
- Pour **chaque indicateur retenu**, une borne minimale et un objectif **initiaux** sont fixés par le projet, avec justification documentée, selon la hiérarchie : (1) objectif légal ou officiel France/UE (lois, SNBC, objectifs 2030…) ; (2) seuil scientifique (Doughnut, limites planétaires) ; (3) référence historique France 2000–aujourd'hui ; (4) référence européenne (meilleur/pire pays UE) ; (5) dire d'expert.
- Une fois un **volume suffisant de réponses** obtenu (seuil à définir en phase 7), les bornes par défaut basculent vers les bornes **émergentes** (médianes des utilisateurs). Le socle est versionné : `socle_v1_expert`, `socle_v2_emergent`, etc.

### 3.4 Dimensions et indicateurs
- **Au plus 10 dimensions**, et **beaucoup d'indicateurs** dans chacune (large choix pour l'utilisateur).
- Construction des dimensions par la **voie A (top-down conceptuelle)** : grille a priori issue du croisement des cadres de référence (Doughnut 3.0, Stiglitz-Sen-Fitoussi, OCDE *How's Life*, cadre « qualité de vie » Eurostat, indicateurs de richesse nationale INSEE). Les analyses statistiques ne servent qu'à détecter la redondance à l'intérieur d'une dimension.
- Critères d'éligibilité d'un indicateur : résultat (pas un moyen budgétaire) ; couverture nationale ; annuel ou agrégable en annuel ; au moins 10 points depuis 2000, dernière valeur ≥ 2020 ; sens d'interprétation non ambigu ; source publique documentée ; pas de doublon strict d'un autre indicateur retenu.

### 3.5 Sources de données
- **Niveau 1** : accessible par API (INSEE BDM/Melodi, Eurostat, OCDE, Banque mondiale, Banque de France, data.gouv…).
- **Niveau 2** : pas d'API mais **téléchargement direct d'un CSV/XLSX à URL stable**, automatisable par script.
- **Exclu** : données lisibles seulement dans un PDF ou un graphique.
- Priorité INSEE, puis Eurostat (souvent les mêmes données SRCV/SILC harmonisées : la fiche indicateur indique la version retenue et pourquoi), puis les autres.

### 3.6 Validation et gel des dimensions et des indicateurs (décision D20)
Deux gels successifs, chacun avec des critères explicites, un dossier de décision préparé par la session mère, une décision de Léo et une trace au journal. Principe : **validation par exception** — chaque élément arrive avec une recommandation argumentée ; Léo ne se prononce que là où il diverge ou hésite, le reste suit la recommandation.

**Gel 1 — dimensions** (après la proposition de grille v1 de M03)
1. Dossier de décision, une page par dimension : définition en une phrase, type plancher/plafond, question en langage courant, cadres qui la retiennent, nombre de candidats disponibles d'après les catalogues, options d'arbitrage et recommandation.
2. Critères : présente dans au moins trois cadres de référence ou justifiée par la finalité du projet ; conceptuellement distincte (un indicateur n'appartient qu'à une dimension) ; faisable (≥ 8 candidats éligibles, annuels, depuis 2000) ; intelligible par le grand public.
3. Décision de Léo, dimension par dimension ; consignation au journal ; `indicateurs/dimensions.yaml` v1 avec `statut: figee` et date.
4. Une dimension figée ne change que par une nouvelle décision au journal et un changement de version.

**Gel 2 — indicateurs par dimension** (après les catalogues de phase 2 et la mission M05)
1. Long-list automatique : union des catalogues (INSEE, Eurostat, autres), rattachée à la grille v1, dédoublonnée (un concept = une ligne avec ses sources alternatives).
2. Filtre d'éligibilité mécanique (§3.4), par script, exclusions motivées et traçables.
3. Fiches indicateurs (M05) : définition, source, sens, type, déclaratif, qualité, note de pertinence ; regroupement en **familles** de variantes avec une variante principale ; recommandation `retenir` / `retenir comme variante` / `écarter` motivée. **Audit croisé** (M06) par un agent n'ayant pas vu le travail du rédacteur, sur un échantillon et les cas douteux.
4. Validation de Léo, dimension par dimension, dans un classeur `30_dimensions_indicateurs/validation/validation_<dimension>.xlsx` (dossier OneDrive) : colonne `decision_leo` à liste déroulante (`retenu` = disponible dans l'outil ; `retenu_socle` = coché par défaut dans la configuration de référence ; `ecarte` ; `a_discuter`) et colonne de commentaire ; seules les lignes où Léo diverge sont remplies ; réintégration automatique.
5. Contrôles avant gel : aucun indicateur dans deux dimensions ; nombre suffisant d'indicateurs par dimension, mélange objectif/déclaratif et résultat/pression ; test à blanc du calcul de l'indice sur données collectées ; relecture par Léo des dix fiches les plus sensibles.
6. Gel : `indicateurs/*.yaml` en `statut: fige`, **base d'indicateurs v1.0** avec journal des modifications. Versionnement sémantique : ajout = version mineure ; retrait ou redéfinition = version majeure (comparabilité des réponses). La base ne bouge pas pendant une vague de collecte ; chaque réponse enregistre la version utilisée.

**Ensuite** : socle des bornes v1 (même mécanique, classeur par dimension) ; puis boucle intersubjective sur la structure (dimensions jamais activées, indicateurs toujours décochés → arguments pour une v2).

## 4. Grille de dimensions v0 (provisoire, à consolider en mission M03)

Sert à orienter le moissonnage et le tagging. Chaque dimension est de type **plancher social** (on vise au-dessus d'un minimum) ou **plafond écologique** (on vise en dessous d'un maximum).

| # | Dimension (id) | Contenu indicatif | Type |
|---|---|---|---|
| 1 | Niveau de vie et économie (`niveau_de_vie`) | Revenu disponible, consommation, pauvreté monétaire et en conditions de vie, patrimoine, PIB/hab., investissement, dette | plancher |
| 2 | Travail et emploi (`travail`) | Taux d'emploi, chômage et chômage de longue durée, NEET, qualité et sécurité de l'emploi, accidents, temps de travail, satisfaction au travail | plancher |
| 3 | Logement et cadre de vie (`logement_cadre_vie`) | Coût et qualité du logement, surpeuplement, précarité énergétique, qualité de l'air locale, bruit, accès à la nature, mobilité | plancher |
| 4 | Santé (`sante`) | Espérance de vie (en bonne santé), mortalité évitable, santé perçue, accès aux soins, santé mentale, comportements | plancher |
| 5 | Éducation, compétences et culture (`education`) | Sorties précoces, diplômes, compétences (PISA, PIAAC), formation des adultes, numérique, pratiques culturelles | plancher |
| 6 | Vie personnelle, liens sociaux et bien-être ressenti (`liens_bien_etre`) | Soutien social, isolement, temps libre, équilibre vie pro/perso, satisfaction dans la vie, sens, affects | plancher |
| 7 | Sécurité et confiance (`securite_confiance`) | Homicides, violences, sentiment d'insécurité, sécurité économique (épargne de précaution, impayés), confiance interpersonnelle | plancher |
| 8 | Démocratie, droits et institutions (`democratie`) | Participation électorale, confiance dans les institutions, libertés (presse, expression, académique), corruption perçue, indépendance de la justice, voix politique | plancher |
| 9 | Égalités (`egalites`) | Inégalités de revenu et de patrimoine, écarts femmes-hommes, inégalités territoriales, intergénérationnelles, mobilité sociale | plancher |
| 10 | Planète (`planete`) | Émissions et empreinte carbone, biodiversité, artificialisation des sols, ressources et circularité, eau, azote, pollutions | plafond |

Points à arbitrer en M03 : place de la satisfaction globale (dimension 6 ou transversale) ; alimentation (1 ou 4) ; énergie (3 ou 10) ; innovation/infrastructures (1 ou dimension propre, sachant la limite de 10).

## 5. Modèle de données

### 5.1 Fiche indicateur (`indicateurs/<id>.yaml`, une par indicateur)
```
id: taux_pauvrete_60
libelle: Taux de pauvreté monétaire (seuil à 60 % du niveau de vie médian)
dimension: niveau_de_vie
sous_theme: pauvreté
definition: >
  Part des personnes dont le niveau de vie est inférieur à 60 % du niveau de vie médian…
unite: "%"
sens: bas                      # haut = plus c'est élevé, mieux c'est ; bas = l'inverse
type: resultat                 # resultat | moyen | pression
declaratif: non                # oui si donnée d'enquête d'opinion/ressenti
source_organisme: INSEE
source_jeu: SRCV / ERFS
source_serie_id: "001234567"   # idbank, code Eurostat, etc.
source_niveau: 1               # 1 = API ; 2 = téléchargement CSV/XLSX
url_api: https://…
url_page: https://…
frequence: annuelle
premiere_annee: 1996
derniere_annee: 2023
geo: FR                        # clé géographique, FR en v1
socle_v1:
  seuil_minimal: 16.0          # score 0
  objectif: 8.0                # score 100
  justification: "Historique France (pire 2000–2023 = 14,5 %) élargi ; objectif = moitié du niveau 2000, cohérent ODD 1.2"
  type_justification: historique   # officiel | scientifique | historique | europeen | expert
qualite: [rupture_2010, revision_frequente]
notes: ""
```

### 5.2 Séries de données (`donnees/millesimes/<AAAA-MM-JJ>/series.csv`)
Colonnes : `indicateur_id, geo, annee, valeur, statut, source_version, date_collecte`. Un **millésime** = une collecte complète figée et datée ; le front utilise le dernier millésime validé. Les millésimes antérieurs sont conservés (reproductibilité).

### 5.3 Catalogues de séries candidates (`catalogues/<source>_catalogue.csv`)
Colonnes minimales : `source, serie_id, libelle, unite, frequence, geo, premiere_periode, derniere_periode, derniere_maj, theme_source, dimension_v0, candidat, commentaire`.

### 5.4 Configuration utilisateur et réponses (phase 7)
`configurations` : id, horodatage, profil (facultatif : âge, région, statut), `dimensions_actives`, `poids_dimensions`, `indicateurs_selectionnes`, `poids_indicateurs`, `bornes` (par indicateur), `regle_agregation` (p aux deux niveaux), `indice_obtenu`, `version_socle`, `version_base_indicateurs`. Anonyme par défaut ; consentement explicite ; aucune donnée directement identifiante.

## 6. Architecture technique cible (décision à confirmer, voir §6.3)

### 6.1 Contrainte de départ
Les sessions Claude (bac à sable cloud) **ne peuvent pas appeler les API statistiques depuis un script** (réseau restreint à GitHub et aux dépôts de paquets). Elles peuvent **lire** une réponse d'API via la lecture de page (pour comprendre une structure ou vérifier une valeur), et elles peuvent lire et écrire sur GitHub. Donc : **le code est écrit dans les sessions, exécuté sur GitHub Actions.**

### 6.2 Pile recommandée (coût 0 €, aucune administration de serveur)
| Brique | Rôle | Pourquoi |
|---|---|---|
| **Dépôt GitHub** `observatoire-prosperite` | Code, fiches indicateurs, catalogues, millésimes de données, documentation | Vous avez déjà un compte ; historique complet ; les agents y déposent directement |
| **GitHub Actions** | Robot qui exécute la collecte (catalogues, séries), les tests et la fabrication des millésimes, à la demande ou chaque mois | Internet ouvert, gratuit, journal d'exécution lisible par les agents |
| **GitHub Pages** | Hébergement du site (outil 3 modes + jeu) en pages statiques | Gratuit, URL publique, aucun serveur |
| **Python 3.12** (pandas, requests, pydantic, pytest) | Langage unique du pipeline | Meilleur compromis pour des agents ; bibliothèques INSEE/Eurostat existantes |
| **Front** : HTML/CSS/JS sans serveur (framework léger à décider en phase 6) | Interface | Le front lit un JSON statique produit par le pipeline |
| **Supabase** (région UE) — phase 7 | Base pour enregistrer les réponses des utilisateurs | Gratuit au départ, tableau de bord sans code, export CSV, hébergement européen (RGPD) |

### 6.3 Décisions attendues de Léo
- Dépôt **public** (recommandé : transparence scientifique, Actions et Pages sans limite) ou privé.
- Nom du dépôt (proposition : `observatoire-prosperite`).
- Connexion de GitHub à claude.ai (Paramètres → Connecteurs) pour que les sessions puissent pousser du code.

### 6.4 Arborescence du dépôt (à créer en M00)
```
observatoire-prosperite/
  README.md
  docs/                 charte, journal des décisions, fiches de mission, comptes rendus
  src/sources/          un module par source (insee_bdm.py, insee_melodi.py, eurostat.py, …)
  src/pipeline/         collecte, nettoyage, millésimes, export JSON pour le front
  src/scoring/          normalisation, moyenne généralisée, calcul d'indice (référence unique, réutilisée par le front)
  scripts/              points d'entrée exécutés par Actions
  tests/                tests unitaires avec fixtures (réponses d'API enregistrées)
  catalogues/           catalogues de séries candidates (CSV)
  indicateurs/          une fiche YAML par indicateur + dimensions.yaml
  donnees/millesimes/   collectes figées et datées
  site/                 application web (front)
  .github/workflows/    collecte.yml, tests.yml, pages.yml
```

## 7. Organisation du travail

### 7.1 Rôles
- **Session mère** (modèle le plus avancé, effort élevé) : cadrage, décisions, rédaction des fiches de mission, intégration, contrôle qualité, journal des décisions.
- **Agents de mission** (modèles plus légers, sessions séparées rattachées au même Projet) : exécutent une fiche de mission, déposent les livrables, rédigent un compte rendu.
- **Léo** : décisions de fond, validation des arbitrages méthodologiques, actions nécessitant un compte (GitHub, Supabase), relecture.

### 7.2 Cycle d'une mission
1. La session mère publie `claude/missions/Mxx_<titre>.md` dans le Projet (et une copie dans `00_pilotage/fiches_mission/`).
2. Léo ouvre une nouvelle session rattachée au Projet et colle le **prompt de lancement** indiqué dans la fiche.
3. L'agent lit la charte puis la fiche, exécute, dépose les livrables (Projet, dépôt GitHub une fois relié, fichiers envoyés dans la conversation sinon).
4. L'agent termine par un compte rendu `claude/cr/Mxx_compte_rendu.md` : fait / non fait / problèmes / propositions.
5. La session mère contrôle, intègre, met à jour le journal des décisions et la charte si nécessaire.

### 7.3 Conventions
- Tout en français ; identifiants ASCII en français ; dates ISO (AAAA-MM-JJ) ; CSV UTF-8 séparateur virgule ; nombres avec point décimal.
- Nommage des docs Projet : `claude/00_…` pilotage, `claude/missions/…`, `claude/cr/…`, `claude/30_…` méthodologie, `claude/40_…` données.
- Un agent **ne modifie jamais** la charte ni le journal : il propose dans son compte rendu.
- Un agent qui bloque (accès impossible, ambiguïté) le dit dans le compte rendu plutôt que d'inventer.

## 8. Feuille de route

| Phase | Contenu | Statut |
|---|---|---|
| 0 | Cadrage : charte, journal, arborescence, architecture, dépôt `leomalherbe/prosperite` (public), robots Tests et Collecte | **Fait (13/10/2026)** |
| 1 | Inventaire des sources et API (M01 INSEE, M02 Eurostat, M04 autres sources) | **Phase 1 faite (13/10/2026)** : PR #1, #2, #4 |
| 2 | Moissonnage des catalogues (M01/M02 phase 2, M04 phase 2, exécution GitHub Actions) | En cours |
| 3 | Crosswalk des cadres (M03 phase 1, PR #3) **fait** ; grille v1 (M03 phase 2) puis **gel 1** | En cours |
| 4 | Fiches indicateurs (M05), audit croisé (M06), validation par classeurs, **gel 2** ; puis socle v1 des bornes | Fiches M05/M06 publiées |
| 5 | Pipeline de données et millésimes | À venir |
| 6 | Front refondu (3 modes + jeu) | À venir |
| 7 | Collecte des réponses, indice intersubjectif | À venir (recrutement des répondants à traiter plus tard) |
| 8 | Validation, publication | À venir |

## 9. Références de cadrage
- Fanning A.L., Raworth K. (2025), « Doughnut of social and planetary boundaries monitors a world out of balance », *Nature* 646, 47–56 — 21 dimensions, 35 indicateurs, tendances 2000–2022.
- Stiglitz, Sen, Fitoussi (2009), rapport de la Commission sur la mesure des performances économiques et du progrès social — 8 dimensions.
- OCDE, *How's Life?* / Better Life Index — 11 dimensions de bien-être actuel + 4 capitaux.
- Eurostat, cadre « Quality of life » — 8 dimensions + 1 (expérience globale de la vie).
- INSEE, *Les nouveaux indicateurs de richesse* (loi du 13 avril 2015) — 10 indicateurs, rapport annuel.
- CEPREMAP, Observatoire du bien-être — baromètre trimestriel du bien-être des Français.
