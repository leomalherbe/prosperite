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
