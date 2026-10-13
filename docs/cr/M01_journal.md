# Journal de bord — M01 INSEE (agent de mission)

Une entrée horodatée par sous-tâche : fait, résultat, problèmes. Heure de Paris.

## 2026-10-13 13:04 — Démarrage, phase 1 (A1 + A4)
- Fait : lecture de `CLAUDE.md`, de la charte, du journal des décisions, de la fiche M01 et de `docs/archives/prototypes_indicateurs.csv` (86 indicateurs des prototypes : aucun n'est sourcé à l'INSEE, tous Eurostat / Banque mondiale / OWID).
- Branche `m01-insee` recréée depuis `origin/main` (609ecc7).
- Périmètre de ce lancement : phase 1 seulement (A1 cartographie des voies d'accès, A4 repérage des indicateurs). Pas de modules Python ni de script de moissonnage (phase 2).
- Contrainte : aucun appel d'API depuis un script ; les réponses sont lues par l'outil de lecture de page web et enregistrées comme fixtures dans `tests/fixtures/insee/`.

## 2026-10-13 13:40 — A1, première passe : accès réels et fixtures
- Fait : lecture du catalogue des API (insee.fr/fr/information/8184146), des pages BDM (2411675, 2862759), du guide SDMX v2.2, des fiches data.gouv « API Melodi » et « API BDM », du code de pynsee 0.2.5 et du paquet R `melodi` 1.1.2 (dépôt InseeFrLab/melodi, commit du 2026-10-09).
- Résultats :
  - `bdm.insee.fr` répond sans authentification (lu aujourd'hui) ; `detail=nodata` liste les séries AVEC IDBANK/TITLE_FR/LAST_UPDATE, alors que `detail=serieskeysonly` ne rend que les dimensions (pas d'IDBANK) : à retenir pour la phase 2.
  - `api.insee.fr` (Melodi, Données locales, Métadonnées, BDM via portail) est **interdit à l'outil de lecture de page web par le robots.txt** : aucune réponse lisible depuis le bac à sable. Idem pour les fichiers `*.xlsx|*.csv|*.zip` de insee.fr (robots.txt).
  - Contournement pour Melodi : cassettes vcr (réponses réelles enregistrées par l'INSEE, 2026-01 à 2026-07) du paquet R `melodi`, extraites dans `tests/fixtures/insee/melodi/` avec un fichier de provenance.
  - Contournement pour Métadonnées : point SPARQL public `rdf.insee.fr/sparql` (même référentiel RMéS) lisible ; fixture du concept c1653 « Pauvreté monétaire ».
  - Données locales : aucune réponse réelle obtenue (pas d'enregistrement public trouvé) ; pynsee signale que cette API n'est plus mise à jour et renvoie vers Melodi.
  - Instantané hors ligne du catalogue BDM (paquet R `insee`, août 2024 : 199 dataflows, 158 166 idbanks avec titres, fréquence, zone) exploité pour le repérage ; à revalider sur le catalogue vivant en phase 2.
- Fixtures BDM reconstituées (l'outil ne recopie pas le XML brut ; attributs extraits un à un puis réassemblés, signalé dans chaque fichier) : série 001688527 (5 dernières obs.), série 010593281 (satisfaction dans la vie, complète), dataflow ODD-ERADICATION-PAUVRETE, liste `nodata` des 65 séries de ce dataflow (CSV), extrait de la liste vivante des dataflows (93 premiers, la réponse complète est tronquée par l'outil).
- Problèmes : liste complète des dataflows illisible (troncature) ; CSV `dataflows_oct26.csv` d'insee.fr bloqué (robots) ; portail `portail-api.insee.fr` est une application JavaScript illisible.

## 2026-10-13 14:45 — A4, inventaire des indicateurs ODD et IRN (en cours)
- Fait : lecture des 10 pages « Indicateurs de richesse nationale » (édition 17/07/2026), de la page des indicateurs ODD (2654964, 27/05/2026) et des 17 sous-pages par objectif (codes `INDICATOR_SDG` du jeu Melodi **DS_NAT_SDG**, absent du catalogue Melodi de janvier 2026, donc créé depuis) ; interrogation des 17 dataflows BDM `ODD-*` (première observation, date de mise à jour, zone, unité de chaque série) : 645 séries vivantes (contre 450 nationales annuelles dans l'instantané d'août 2024), mises à jour le 2026-05-27 pour la plupart.
- Résultats : les 10 IRN sont tous dans BDM (dataflows ODD) avec un idbank annuel national ; vérification en direct des premières et dernières années pour les séries de référence.
- Constats (suite plus bas) : les séries ODD de BDM se terminent par une observation `NaN` (statut O) pour l'année en cours : la « dernière période » doit être la dernière valeur non manquante ; les fichiers xlsx des IRN changent de nom chaque année (pas d'URL stable) ; la requête BDM par clé de dataflow (`/data/<flux>/<clé>`) a échoué via l'outil de lecture (erreur client), à tester en phase 2.

## 2026-10-13 16:10 — A4, livrables CSV
- Fait : `docs/sources/insee_indicateurs_reperes.csv` (1 063 lignes : 858 séries BDM dont les 645 séries ODD vivantes, 192 lignes Melodi dont 158 codes `INDICATOR_SDG` du jeu DS_NAT_SDG, 13 fichiers insee.fr) et `docs/sources/insee_indicateurs_reference.csv` (26 lignes couvrant la liste minimale de la fiche : les 10 IRN sur 12 lignes, l'endettement étant détaillé en 3, + 14 compléments).
- Méthode : dernière période = dernière valeur non manquante lue le 2026-10-13 (requêtes `lastNObservations=6` par dataflow ODD) ; première période = première observation renvoyée ; tag `dimension_v0` par règles de mots-clés ; `candidat` = oui / non / a_verifier avec la raison en commentaire. Les séries hors ODD viennent de l'instantané d'août 2024 et sont marquées « à vérifier en phase 2 » sauf une vingtaine vérifiées en direct.
- Résultats : 600 lignes `candidat = oui` (550 BDM, 49 Melodi, 1 fichier). Les 10 IRN ont tous un idbank BDM annuel national vivant. Non disponibles à l'INSEE par API : indice de Gini du niveau de vie (fichier Chiffres-clés seulement), sentiment d'insécurité (SSMSI). Disponibles mais insuffisants (< 10 points) : surpeuplement, taux d'effort logement. Taux d'épargne des ménages : idbank non trouvé.
- Problèmes : séries TCRED de revenus (Filosofi) arrêtées en 2015 ; série 001782649 (salaire annuel moyen) absente de BDM aujourd'hui ; plusieurs codes `INDICATOR_SDG` attribués par inférence (ordre des liens sur la page) : signalé en commentaire.

## 2026-10-13 16:40 — A1 + A4, fiche source `docs/sources/insee.md`
- Fait : rédaction de la fiche documentaire (synthèse des 6 voies d'accès, détail BDM / Melodi / Données locales / Métadonnées / fichiers, localisation des indicateurs sociaux annuels, tableau des indicateurs de référence, résumé du repérage, liste des fixtures, points à trancher, sources).
- Vérification : `python -m pytest -q` → 14 tests passent (aucun code ajouté en phase 1).
- Reste : dépôt de la fiche dans le Projet claude.ai (`claude/10_source_insee.md`).

## 2026-10-13 16:45 — Dépôt Projet et clôture de la phase 1
- Fait : `docs/sources/insee.md` déposé dans le Projet claude.ai sous `claude/10_source_insee.md`.
- Phase 1 terminée ; arrêt avant la phase 2 (modules Python, script de moissonnage, GitHub Actions), conformément à la consigne. Aucun fichier sous `scripts/` ou `src/` modifié : le workflow « Collecte » n'a pas été déclenché.

## 2026-10-13 15:10 — Démarrage de la phase 2 (A2, A3, B)
- Fait : branche `m01-insee` reprise depuis `origin/m01-insee` et fusion de `origin/main` (charte v1.1, journal D13–D22, fiches M05/M06). Relecture de `CLAUDE.md`, de la charte, du journal (D14, D15, D16, D21), de la fiche M01, des livrables de phase 1, de `scripts/lancer_collecte.py`, `scripts/actions.py`, du workflow « Collecte » et de `src/scoring/calcul.py`.
- Vérifications préalables (outil de lecture de page) : `detail=nodata` sur un regroupement de 21 séries (`CNA-2020-PIB`) renvoie IDBANK, titres, LAST_UPDATE et **toutes les dimensions de la clé, dont `SERIE_ARRETEE`** ; sur un regroupement de 3 140 séries (`CNA-2020-ERE`) la même requête échoue (limite de 2 000 séries par requête) ; une requête par clé partielle fonctionne (`/data/CHOMAGE-TRIM-NATIONAL/T........?detail=nodata` : 147+ séries ; `A........` : aucun résultat, d'où l'erreur de phase 1) ; `SERIES_BDM/<id1>+<id2>?firstNObservations=1` renvoie la première observation de chaque série ; la structure (DSD) donne l'ordre des dimensions (FREQ en premier) et la liste de codes `CL_ZONE_GEO` (239 codes) permet de classer les zones nationales.
- Plan : modules `insee_http` (client commun : identification, débit, reprises), `insee_bdm`, `insee_melodi`, `insee_fichiers`, `insee_catalogue` (filtres, tagging, candidat) ; script `scripts/collecte_insee.py` en deux temps (collecte réseau reprenable → inventaires bruts ; catalogage hors ligne → catalogues), avec échantillons de réponses brutes dans `docs/sources/echantillons_insee/`.

## 2026-10-13 15:45 — A2 : modules d'accès et tests hors ligne
- Fait : `src/sources/insee_http.py` (client commun : User-Agent du projet, intervalle minimal par hôte, reprises sur 429/5xx/coupures avec `Retry-After`, faux client `ClientFixtures` pour les tests, type `Ligne`), `src/sources/insee_bdm.py` (dataflows, DSD, listes de codes, `lister_series` par `detail=nodata` avec **découpage automatique** de la clé quand la réponse dépasse 2 000 séries — FREQ d'abord, puis les dimensions suivantes, codes groupés par « + » —, `obtenir_series` par lots de 400 idbanks avec coupure en deux d'un lot en échec, `periodes_par_idbank` (first/lastNObservations, relecture complète si NaN), `obtenir_serie` → lignes sans les NaN de début et de fin), `src/sources/insee_melodi.py` (catalogue, `/range`, détection des niveaux géographiques nationaux, `/data` avec comptage et pagination contrôlée, identifiant de série = requête `<jeu>?DIM=code&…`, lecture du ZIP de CSV), `src/sources/insee_fichiers.py` (téléchargement identifié, XLSX/CSV/ZIP → DataFrame).
- Fixtures ajoutées (reconstituées, à remplacer par les réponses brutes du robot) : DSD `CHOMAGE-TRIM-NATIONAL`, liste de codes `CL_PERIODICITE` (5 codes : A, B, M, S, T).
- Tests : `tests/test_insee_bdm.py`, `tests/test_insee_melodi.py`, `tests/test_insee_fichiers.py` ; `python -m pytest -q` → 52 tests passent.

## 2026-10-13 16:35 — A3 : script de collecte reprenable et règles de catalogage
- Fait : `scripts/collecte_insee.py` (étapes `bdm_flux`, `echantillons`, `bdm_series`, `bdm_periodes`, `melodi`, `consolidation`, `catalogage` ; état dans `catalogues/insee_etat/` avec fichiers JSONL compressés écrits au fil de l'eau ; budget de temps (240 min par défaut) puis arrêt propre et reprise au passage suivant ; journalisation horodatée ; échantillons de réponses brutes dans `docs/sources/echantillons_insee/` avec `provenance.csv` ; mode `--catalogage-seul` hors ligne sur les inventaires). Options du robot pilotables par commit dans `scripts/collecte_insee.options` (lu seulement sans argument).
- `src/sources/insee_catalogue.py` : zones (FE, FM, FR-D976 gardés distincts, D15 ; autres périmètres nationaux ; « SO »), filtres durs (fréquence A/S/T/B/M, zone nationale, dernière période ≥ 2020), filtre souple « première ≤ 2010 » (`a_verifier` si ≥ 10 points possibles — raccordement D16 —, `non` sinon), règles de tagging ordonnées (reprises de la phase 1 et corrigées : 93 % d'accord avec les 1 063 lignes de phase 1, écarts restants dus surtout à des libellés résumés en phase 1 ou à l'APD classée hors champ), hors champ (entreprises, prix de production, conjoncture des entreprises, commerce extérieur…), anciennes bases, séries arrêtées, moyens (D19), séries irrégulières (D17), ventilations (D21).
- Tests : `tests/test_insee_catalogue.py`, `tests/test_collecte_insee.py` (circuit complet hors ligne avec faux client, dont reprise après arrêt pour budget) ; 91 tests passent.
- Premier passage du robot : essai réduit (20 dataflows, 20 jeux Melodi, 45 min) pour valider les appels réels avant la collecte complète.
