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
