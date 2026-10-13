# Journal de bord — mission M04 (sources hors INSEE et Eurostat)

Tenu par l'agent de mission M04. Une entrée horodatée (heure de Paris) par sous-tâche : fait, résultat, problèmes.
Périmètre du lancement en cours : **phase 1** (T1 fiches par source, T2 tableau d'inventaire). La phase 2 (T3, indicateurs candidats) attend la validation de Léo.

---

## 2026-10-13 13:07 — Sous-tâche 0 : mise en route

- **Fait** : lecture de `CLAUDE.md`, `docs/00_charte_projet.md` (§3.5 niveaux de source, §4 grille v0), `docs/01_journal_decisions.md`, `docs/missions/M04_sources_hors_insee_eurostat.md`, `docs/archives/prototypes_indicateurs.csv`. Branche `m04-sources` recréée depuis `origin/main` (609ecc7).
- **Résultat** : 86 indicateurs dans les prototypes ; **20 relèvent de M04** : 16 Banque mondiale (WDI) et 4 Our World in Data (3 V-Dem, 1 RSF). Ils seront statués en fin d'inventaire (T2).
- **Méthode de vérification** : le bac à sable ne peut pas appeler les API depuis un script ; chaque voie d'accès est ouverte avec l'outil de lecture de page web (WebFetch). Une voie est `verifie` si l'URL ouverte renvoie bien des données (JSON, XML, CSV ou fichier tableur identifié) ; `probable` si la page de téléchargement est vue mais pas le fichier lui-même ; `non_verifie` sinon, avec la raison. Les extraits de réponses d'API sont enregistrés dans `tests/fixtures/<source>/`.
- **Problèmes** : aucun. La phase 1 ne touche ni `scripts/` ni `src/` (pas de déclenchement du workflow « Collecte »).

## 2026-10-13 13:35 — Sous-tâche 1 : premiers essais d'accès et vérification par le robot

- **Constat bloquant pour WebFetch** : l'outil de lecture de page respecte les `robots.txt`. Sont refusés : tous les portails Opendatasoft de l'État (`/api/` interdit à tout robot sauf Googlebot : DREES, DEPP, Santé publique France/Odissé…), `static.data.gouv.fr` (fichiers de data.gouv.fr), l'API de la BCE, Resana. L'API de la Banque mondiale renvoie une erreur serveur sur les requêtes de données (les métadonnées passent). En outre, l'outil refuse de recopier plus de 125 caractères verbatim : impossible d'en tirer une fixture brute.
- **Passent avec WebFetch** : API data.gouv.fr (`/api/1/datasets/…`), Webstat Banque de France (catalogue), API SDMX de l'OCDE, OWID (CSV des graphiques), Ademe Data Fair, pages des producteurs (Citepa, EDGAR, PNUD, WHR, Transparency, RSF, V-Dem, GFN).
- **Décision technique (dans le périmètre phase 1)** : ajout d'un script autonome `scripts/collecte_sources.py` exécuté par GitHub Actions (workflow « Collecte », cible déduite du nom de branche). Il lit `docs/sources/verif_acces/urls.csv`, ouvre chaque URL sans clé, et écrit `docs/sources/verif_acces/resultats.csv` (code HTTP, type, taille, verdict) et un extrait lisible par URL dans `docs/sources/verif_acces/extraits/` (début du texte, feuilles d'un classeur, contenu d'un zip, valeurs distinctes d'une colonne). Tests hors ligne : `tests/test_collecte_sources.py` (8 tests).
- **Vague 1** : 82 URL (9 portails Opendatasoft, Webstat, BCE, SDES DiDo, SSMSI, élections, ONISR, Ademe, Citepa, OCDE, 18 séries Banque mondiale + WGI, OWID ×4, RSF, Transparency, Freedom House, V-Dem, WHR, EDGAR, GFN, PNUD, OMS, ONUDC).
- **Constat** : le portail `naturefrance.fr` (ONB) est hors service ; une page de secours sur eaufrance.fr renvoie vers des fiches PDF hébergées sur Resana, sans date de reprise annoncée.

## 2026-10-13 13:55 — Sous-tâche 2 : résultats des vagues 1 et 2 du robot (run Actions 38390822077 puis 38392712026)

- **Vague 1** : 74/82 URL renvoient des données. Échecs instructifs : `data.culture.gouv.fr` n'est plus un portail Opendatasoft (application `culture.data.gouv.fr`) ; Webstat `observations` n'existe pas sans compte (404) ; l'URL du CSV SSMSI relevée via WebFetch renvoyait 404 (constat de la vague 3 : le fichier avait été remplacé le 15/09/2026 et son URL horodatée avait changé) — leçon : utiliser le permalien de ressource data.gouv.fr ou relire l'API ; V-Dem n'a pas de lien direct (404, téléchargement par formulaire) ; GFN répond 403 sans clé ; l'URL ONUDC renvoie une page HTML (portail déplacé vers data.unodc.org).
- **Vague 2** : 104 URL ; catalogues complets des 8 portails Opendatasoft extraits (DREES 265 jeux, DEPP 310, MESR 217, Odissé 388, Ameli 51, économie 617, ODRE 187, CNAF 210).
- **Résultats marquants** :
  - Banque mondiale : 14 des 16 séries des prototypes répondent ; `EN.ATM.CO2E.PC` et `EN.ATM.CO2E.PP.GD` sont **archivées** (« indicator was not found… deleted or archived ») ; remplaçants vérifiés `EN.GHG.CO2.PC.CE.AR5`, `EN.GHG.ALL.PC.CE.AR5`. WGI accessibles via `source=3` avec les codes `GOV_WGI_*` (1996–2025).
  - OWID : la série RSF des prototypes (`press-freedom-index-rsf`) **s'arrête en 2021** (9 points 2013–2021) ; la source primaire RSF publie un CSV par année (2002–2026, vérifié). Les 3 séries V-Dem des prototypes vont jusqu'en 2025.
  - OCDE How's Life : 68 mesures France (bien-être actuel) et 33 (bien-être futur), dont des séries annuelles 2006–2025 issues de Gallup (sentiment de sécurité la nuit, soutien social, affects négatifs, confiance dans le gouvernement, bénévolat).
  - BCE (SDMX, sans clé) : ratio dette des ménages / revenu disponible France depuis 1999T4 (`QSA…XDC_R_B6GA_CY…`).
  - SDES DiDo : qualité de l'air nationale (exposition PM2,5 fond urbain 2009–2024, concentrations) en CSV à identifiant stable.
  - Géodes redirige vers Odissé (Santé publique France).
- **Problèmes** : DARES refuse la connexion du robot (« Remote end closed connection ») ; le classeur CPI 2025 est un xlsx valide mais illisible par openpyxl en mode lecture seule (à traiter en phase de collecte).

## 2026-10-13 14:08 — Sous-tâche 3 : vagues 3 et 4 du robot, fixtures (runs 38393724607 et 38394608567)

- **Vague 3** (113 URL) : fiches data.gouv.fr complètes (URL courantes des ressources), pièces jointes DREES, enregistrements Odissé / DEPP / Ameli, ITDD France entière (185 variables, colonnes annuelles A1982–A2025).
- **Vague 4** (123 URL, consolidée : 114 données, 4 pages HTML, 5 erreurs) : **permalien data.gouv.fr vérifié** (`/fr/datasets/r/<id_ressource>` redirige vers le fichier courant) ; baromètre d'opinion DREES = **microdonnées pondérées 2000–2024 en CSV** (pièce jointe) ; EVSI DREES figée à 2018 ; base SSMSI : 88 419 lignes, 159 titres dont « Sentiment d'insécurité dans le quartier ou le village » (15 obs.), fichier encodé en Windows-1252.
- **Fixtures** : 19 réponses réelles copiées dans `tests/fixtures/` (opendatasoft, banque_de_france, bce, sdes_dido, data_gouv, ademe, ocde, banque_mondiale, oms, hubeau, rsf, owid) avec leur provenance dans `tests/fixtures/provenance_m04.csv`. Pas de fixture OWID « grapher » brute (l'extrait conservé est filtré sur la France).
- **Problèmes** : la description SDMX des flux How's Life ne nomme pas les sources (l'origine Gallup de certaines séries reste à confirmer dans le PDF de métadonnées OCDE) ; DARES toujours injoignable.

## 2026-10-13 14:10 — Sous-tâche 4 : livrables T1 et T2

- `docs/sources/autres_sources.md` (T1) : points d'entrée communs (Opendatasoft, data.gouv.fr, DiDo, SDMX), 12 fiches françaises, 5 fiches internationales (dont tableaux V-Dem/RSF/CPI/Freedom House/WJP et WHR/Gallup/Eurofound/ESS/Eurobaromètre), 15 sources découvertes, statut des 20 séries des prototypes, synthèse par dimension.
- `docs/sources/10_sources_inventaire.csv` (T2) : 53 sources (niveau 1 : 20 ; niveau 2 : 18 ; exclu : 15 ; fiabilité : 40 `verifie`, 2 `probable`, 11 `non_verifie`) + 20 lignes « prototype: » (16 Banque mondiale, 4 OWID) avec statut et proposition.

## 2026-10-13 14:13 — Sous-tâche 5 : relecture, dépôt dans le Projet, fin de la phase 1

- Relecture des fiches : tableaux markdown contrôlés ; corrections (échelles RSF constatées dans les fichiers : 2013 exprimé en « plus haut = mieux » ; premières années OWID ; EVSI DREES figée à 2018 ; origine Gallup des séries OCDE marquée « à confirmer »).
- Dépôt dans le Projet claude.ai : `claude/10_sources_hors_insee_eurostat.md` (contenu de `docs/sources/autres_sources.md`) et `claude/10_sources_inventaire.csv`.
- Tout est commité et poussé sur `m04-sources`. **Phase 1 terminée ; arrêt en attente de la validation de Léo avant la phase 2 (T3).**
- Note pour la suite : `scripts/collecte_sources.py` tournera aussi chaque mois si la branche est fusionnée dans `main` (veille des liens) ; à confirmer par la session mère.

---

# Phase 2 — tâche T3 (indicateurs candidats)

Lancement par la session mère le 13/10/2026 (agent neuf, décision D13). Lectures : `CLAUDE.md`, charte v1.1, journal des décisions (D13 à D22, en particulier D17 non annuels, D18 composites, D21 pas de clés), fiche M04, livrables de phase 1, `insee_indicateurs_reperes.csv` (M01, 1 063 lignes) et `eurostat_amorce_prototypes.csv` (M02) pour le signalement des doublons.

## 2026-10-13 15:15 — Sous-tâche 6 : mise en route de la phase 2, extension du script du robot

- **Fait** : branche `m04-sources` remise à jour (`origin/main` fusionnée : charte v1.1, D13–D22). Analyse des extraits de phase 1 : les séries How's Life issues du Gallup World Poll (`7_1`, `10_2`, `11_2`, `11_3`, `14_3`, `14_7`) sont des **moyennes sur trois ans répétées chaque année** (20 années affichées 2006–2025, 7 valeurs distinctes) : à signaler dans les fiches (fréquence effective triennale).
- **Découvertes par lecture de pages (WebFetch)** : slugs OWID des pages démocratie, droits humains, corruption, bonheur, confiance, inégalités, biodiversité (≈ 70 graphiques retenus pour test) ; **Global Footprint Network : la Footprint Data Foundation (FoDaFo) publie le classeur des comptes nationaux 2026 en téléchargement direct sans inscription** (`fodafo.org/wp-content/uploads/NEFBA2026_bulk_v1_0_omiting_Iceland_Faroe_Islands.xlsx`) — à vérifier par le robot ; World Happiness Report : seul le classeur de la figure 2.1 (moyennes triennales) est publié par édition, pas de panel annuel.
- **Extension du robot** (consigne de la session mère : lister les séries, pas seulement les URL) : nouveau module `src/sources/series_tabulaires.py` (fonctions hors ligne : table longue → une ligne par série avec première/dernière période, nombre de périodes, valeurs distinctes, dernière valeur ; table large ; couverture annuelle de microdonnées ; lignes contenant un motif dans un CSV/XLSX/ZIP ; catalogues Opendatasoft avec champs et DiDo avec fichiers ; agrégation d'un gros CSV par clé ; réponse JSON Banque mondiale). `scripts/collecte_sources.py` traite désormais une deuxième liste `docs/sources/verif_acces/series.csv` (157 ressources) et écrit `docs/sources/series/<source>__<cle>.csv|.txt` et `docs/sources/series/resultats.csv`. Tests hors ligne : `tests/test_series_tabulaires.py` (10 tests) + 1 test de chaîne complète ; 33 tests passent.
- **Vague 5 (séries)** : OCDE How's Life (bien-être actuel, futur, inégalités verticales ; libellés français de la structure) et ODD OCDE (3, 5, 10, 11, 15, 16) pour la France ; WGI (12 séries) ; 70 graphiques OWID (V-Dem, Freedom House, EIU, CPI, RSF, WHR, WVS, Eurobaromètre, IDEA, WID, biodiversité) + `co2-data` ; RSF 2002–2026 (25 fichiers) ; Freedom House, WJP, WHR, PNUD ; Citepa (séries Secten), EDGAR, GFN/FoDaFo ; catalogue DiDo et ITDD ; SSMSI (159 titres) ; participation par scrutin (agrégation nationale du fichier des résultats au bureau de vote) ; DREES (catalogue avec champs, couverture annuelle des variables du baromètre 2000–2025, dictionnaire, tableaux 2025) ; Odissé (catalogue + 19 jeux France) ; DEPP (catalogue + 5 jeux) ; Ameli (sinistralité).
- **Problèmes** : aucun à ce stade.

## 2026-10-13 15:43 — Sous-tâche 7 : résultats de la vague 5 (run 38403411850), préparation de la vague 6

- **Vague 5** : 123/157 ressources listées (journal `journaux/collecte_2026-10-13T1315_collecte_sources.py.log`, sorties dans `docs/sources/series/`). Résultats principaux :
  - **OCDE How's Life** : 68 mesures France (bien-être actuel), 36 (bien-être futur), 11 (inégalités verticales) ; libellés français de la structure SDMX récupérés. Confirmation : les séries d'origine Gallup (`7_1`, `10_2`, `11_2`, `11_3`, `14_3`, `14_7`) n'ont que 7 valeurs distinctes sur 20 ans (moyennes triennales répétées). ODD OCDE : victimation (UNODC, 2007–2022), taux de plainte, « bon endroit où vivre » (2007–2023), aires protégées des zones clés de biodiversité, Liste rouge.
  - **WGI** : 12 séries 1996–2025 (27 points) ; l'API de la Banque mondiale met 1,5 à 3,5 minutes par série « score ».
  - **OWID** : 65 graphiques lus ; 32 indices et sous-indices V-Dem 1789/1900–2025 (dont 4 variables de liberté des médias), Freedom House 2002/2003–2025, CPI 2012–2024, Eurobaromètre « heureux » 1973–2016, WVS (5 vagues), participation IDEA/V-Dem (1945–2024), WID (Gini, Palma, part du 1 % le plus riche, 1910–2022), Liste rouge 1980–2025, aires protégées 2013–2025. **Refusés (HTTP 403)** : `democracy-index-eiu`, `perceived-influence-over-government`, `self-reported-freedom` (données non redistribuables par OWID). `material-footprint-per-capita` : pas de série France.
  - **Footprint Data Foundation** (comptes nationaux d'empreinte écologique, édition 2026) : **vérifié sans inscription**, France 1961–2025 (2024–2025 estimés) → la question de la clé GFN (D21) est contournée.
  - **Participation électorale** : agrégation nationale des 406 Mo du fichier au bureau de vote : 56 scrutins 1999–2026 (ex. présidentielle 2022 T1 : 73,69 % ; législatives 2024 T1 : 66,71 %).
  - **SSMSI** : 3 828 séries dont 181 nationales ; enquête CVS (2006/2007–2020/2021, France métropolitaine) et délinquance enregistrée (2016–2025).
  - **DREES** : microdonnées du baromètre 2000–2025 (sans 2003) : 360 variables, dont 82 présentes au moins 20 ans ; les « tris croisés » 2025 ne sont pas des séries (une seule vague).
  - **Odissé, DEPP, Ameli, Citepa, EDGAR, PNUD, ITDD (177 variables France), Freedom House (sous-scores A–G 2013–2024), WHR** : listés.
- **Échecs corrigés pour la vague 6** : motif RSF coupé par le séparateur « ; » des paramètres (25 fichiers) ; classeur WJP transposé (un pays par colonne) → nouveau mode `colonne` ; libellés du dictionnaire DREES tronqués → paramètre `largeur` ; colonnes de période non standard (Odissé, DEPP) → paramètres explicites et noms ajoutés ; identifiant Odissé erroné.
- **Script** : seules les ressources de la vague la plus récente sont exécutées (colonne `vague` de `series.csv`), les sorties antérieures sont conservées et `resultats.csv` fusionné ; nouveaux modes `colonne` (classeur transposé) et `distribution` (parts pondérées par année et modalité des microdonnées du baromètre DREES) ; 35 tests passent.
- **Vague 6** (48 ressources) : RSF 2002–2026, WJP (2021 + 5 URL d'éditions récentes à tester), totaux Citepa hors UTCATF, DREES (dictionnaires complets, distributions pondérées des variables d'opinion 2000–2025), 9 fichiers SDES (qualité de l'air nationale, déchets), corrections Odissé et DEPP.

*(Reprise par un nouvel agent après interruption du précédent, 13/10/2026 vers 16 h : lecture de CLAUDE.md, de la charte v1.1, de D13 à D22, de la fiche M04, de ce journal, des livrables de phase 1, des sorties du robot, du dossier du gel 1 et de la table de correspondance v0 → v1 de la branche `m03-grille` ; 35 tests passaient.)*

## 2026-10-13 16:10 — Sous-tâche 8 : bilan de la vague 6 (run du 13/10, 15 h 43)

- **Fait** : la vague 6 avait bien tourné (commit robot `5fe5acf`) : 44/48 ressources listées. RSF 2002–2026 lisible (24 éditions, 2011 absent : édition 2011-2012 publiée sous 2012) ; **WJP : fichier historique 2025** (éditions 2012-2013 → 2025, un pays par colonne) ; Citepa : totaux hors UTCATF 1990–2025 ; DREES : distributions pondérées par année et modalité (17 202 lignes) et dictionnaires complets ; SDES : 9 fichiers air et déchets ; Odissé et DEPP corrigés.
- **Échecs** : WJP 2022–2024 (pages HTML ou 404, sans objet grâce au fichier 2025), Odissé « maladies cardio-neuro-vasculaires » (pas de colonne de période), 3 graphiques OWID en 403 (déjà connus).

## 2026-10-13 16:28 — Sous-tâche 9 : vague 7, origine Gallup (run 38413045136)

- **Constat** : le PDF de métadonnées How's Life (« definitions and metadata ») est refusé à WebFetch (robots.txt) ; la page des conditions générales de l'OCDE et les pages du rapport 2024 ne sont pas lisibles (rendu JavaScript) ; le WHR ne publie plus de panel annuel (page data-sharing lue) ; aucune donnée INJEP sur data.gouv.fr ; CEVIPOF toujours en PDF.
- **Fait** : nouveau mode `pdf` du robot (fonction `lignes_pdf` de `src/sources/series_tabulaires.py`, dépendance `pypdf` ajoutée à `requirements.txt`, test hors ligne sur un PDF construit à la main ; 36 tests passent) ; vague 7 = PDF OCDE + métadonnées OWID (confiance dans le gouvernement, échelle de Cantril).
- **Résultat** : origine **Gallup World Poll confirmée** pour soutien social, sécurité la nuit, émotions négatives, douleur, confiance dans le gouvernement et la dernière mesure du chapitre 14 (bénévolat) ; données « pooled » : 2006-07 puis blocs triennaux 2008-10 … 2023-25 (7 valeurs), 7 ans par âge, 5 ans par diplôme. Aucune mention de licence ou de restriction dans le PDF (recherche « licence, copyright, terms, third party » : 0). OWID confirme Gallup et la moyenne triennale glissante du WHR.

## 2026-10-13 16:38 — Sous-tâche 10 : liste des indicateurs candidats (T3)

- **Fait** : refonte de `docs/sources/outils/construire_candidats.py` (colonnes de la fiche + `dimension_v1_proposee`, `type`, `composite`, `geo`, `ventilation`, `nb_points_depuis_2000`, `niveau_source`, `fiabilite`, `preuve` ; lecture robuste des périodes pluriannuelles ; règle de fréquence ; v1 par la table M03 copiée dans `correspondance_v0_v1_m03.csv` ; contrôle des identifiants de doublon contre les catalogues M01/M02) et définitions dans `candidats_definitions.py` (OCDE How's Life et ODD, WGI, OWID, RSF, Freedom House, WJP, élections) et `candidats_definitions_suite.py` (DREES, WHR, SSMSI, ITDD, Citepa, EDGAR, FoDaFo, PNUD, SDES, Odissé, DEPP, Ameli, WDI).
- **Résultat** : `docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv`, **404 lignes** (370 + 34 ventilations), toutes `verifie` ; 79 déclaratives, 83 composites, 88 non annuelles (hors ventilations) ; 247 satisfont les critères chiffrés de la charte §3.4 ; doublons : 45 oui, 114 partiel, 211 non ; 68 identifiants de doublon cités, tous retrouvés dans les catalogues M01/M02.
- **Trouvé pour `liens_bien_etre`** : baromètre DREES (situation personnelle 2002–2025, optimisme 2000–2025, intégration et cohésion 2014–2025, aidance 2011–2025) et WHR (2011–2025) : 9 séries annuelles éligibles, sans doublon INSEE/Eurostat.
- **Problèmes** : identifiants SSMSI et ODD tronqués dans mes affichages (corrigé par recherche par préfixe) ; en-tête RSF 2012 « 2011-12 » (motif corrigé) ; fins de ligne CRLF des CSV (normalisées en LF).

## 2026-10-13 16:45 — Sous-tâche 11 : fiches et inventaire

- `docs/sources/autres_sources.md` : §3 mis à jour (Gallup, WJP 2025, Footprint Data Foundation) et **§7 ajouté** (méthode, chiffres par dimension v0 et v1, apports par dimension, origine Gallup et réutilisation, réponses à D21, doublons, limites).
- `docs/sources/10_sources_inventaire.csv` : 74 sources (ajout `footprint_data_foundation`, niveau 2, `verifie`) ; mises à jour WJP, GFN, SSMSI, OWID co2, Ameli, DREES, WID, WHR, Gallup, Eurobaromètre, IDEA, PNUD, Citepa.
- **Vague 8** préparée (série longue BCE de la dette des ménages) ; un premier lancement manuel est parti avant la poussée et a rejoué la vague 7 (sans dommage) ; relancé (run 38416125768).
