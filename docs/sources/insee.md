# Source INSEE — voies d'accès et indicateurs repérés

Fiche documentaire de la mission M01 : phase 1 (tâches A1 et A4), complétée en phase 2 (modules, robot de collecte, catalogue : §2.3, §2.7, §10, §11 et **§12**). Rédigée les 13 et 14 octobre 2026 par les agents de mission M01 ; bilan du passage complet et contrôle qualité des catalogues au §12 (clôture de la phase 2, 14/10).
Branche `m01-insee`.

Conventions : « vérifié » = constaté le 2026-10-13 en lisant la réponse de l'API ; « non trouvé » = information introuvable ; aucune valeur n'est inventée. Les codes de zone (`FE`, `FM`, `FR-D976`, …) sont ceux de l'attribut `REF_AREA` de la BDM (voir §2.6).

---

## 1. Synthèse des voies d'accès

| Voie | URL de base | Authentification aujourd'hui | Formats | Quota | Lister le catalogue | Obtenir une série complète | Fixture réelle |
|---|---|---|---|---|---|---|---|
| **BDM, service web SDMX** | `https://bdm.insee.fr/series/sdmx/` | **Aucune** (vérifié) | SDMX-ML 2.1 (XML) | non documenté (pynsee s'impose 30 appels/min par prudence) ; 400 idbanks par requête, 2 000 séries par requête de dataflow | `/dataflow` puis `/data/<dataflow>?detail=nodata` | `/data/SERIES_BDM/<idbank>` | oui (réponses brutes du robot, §10) |
| BDM via le portail | `https://api.insee.fr/series/BDM/V1/` | incertain : « Restreint », 30 appels/min/IP selon data.gouv.fr ; « pas besoin de jeton » selon le code de pynsee 0.2.5 | SDMX-ML | 30/min | identique | identique | non (api.insee.fr illisible depuis le bac à sable) |
| **Melodi** | `https://api.insee.fr/melodi/` | **Aucune** en mode anonyme (30 appels/min) ; compte facultatif pour un quota plus élevé (non chiffré) | JSON ; fichiers ZIP/CSV et XLSX | 30/min anonyme ; 100 000 lignes max. par appel `/data` | `/catalog/all` | `/data/<jeu>?<DIM>=<code>…` ou fichier complet `/file/<jeu>/<produit>` | oui (enregistrements de l'INSEE, §10) |
| Données locales | `https://api.insee.fr/donnees-locales/` | aucune selon pynsee 0.2.5 | JSON / XML | 30/min | non documenté ici | sans objet (cubes communaux) | **non** (aucune réponse réelle obtenue) |
| Métadonnées | `https://api.insee.fr/metadonnees/` (+ point SPARQL `https://rdf.insee.fr/sparql`) | aucune selon pynsee 0.2.5 ; SPARQL ouvert (vérifié) | JSON / XML ; SPARQL → CSV | 10 000/min affiché, 600/min appliqué par pynsee | `/concepts/definitions`, `/codes/…`, `/geo/…` | sans objet | oui, via SPARQL (§10) |
| Fichiers insee.fr (niveau 2) | `https://www.insee.fr/fr/statistiques/fichier/<page>/<fichier>` | aucune | XLSX, CSV, ZIP | sans objet | pages HTML | téléchargement du fichier | non (robots.txt interdit `*.xlsx|csv|zip` à l'outil de lecture) ; xlsx réel servi par Melodi utilisé à la place |
| Sirene (hors périmètre) | `https://api.insee.fr/api-sirene/3.11/` | **clé obligatoire** (en-tête `X-INSEE-Api-Key-Integration`, souscription au plan « Public ») | JSON | 30/min | — | — | non |

**À retenir.** Depuis le nouveau catalogue des API (mis en service le 17 octobre 2024), **seule l'API Sirene exige une clé**. BDM (`bdm.insee.fr`) et Melodi s'utilisent sans authentification. Pour le projet, il faut deux voies : **BDM SDMX** pour les séries chronologiques (dont les indicateurs ODD et les 10 IRN) et **Melodi** pour les jeux d'enquêtes en séries longues (ERFS, SRCV, enquête Emploi, comptes nationaux base 2020).

Licence et réutilisation : les conditions générales de l'INSEE (page 2381855, mise à jour le 27/05/2019) accordent un droit de réutilisation gratuit, y compris commercial, à condition de **mentionner la source et la date de dernière mise à jour** et de ne pas dénaturer les données. Les fiches data.gouv.fr des API Melodi et BDM affichent la « Licence Ouverte 2.0 » (Etalab) en pied de page. Les fiches indicateurs devront porter la mention « Source : Insee, <jeu>, <date de mise à jour> ».

---

## 2. BDM — service web SDMX

### 2.1 Documentation
- Page de présentation : https://www.insee.fr/fr/information/2862759 (mise à jour le 01/10/2026). Le service est décrit comme gratuit, sans mention de clé ni d'inscription.
- Guide d'utilisation v2.2 (juin 2020) : https://www.insee.fr/fr/statistiques/fichier/2862759/BDM_serviceweb_SDMX_V2_2_guideutilisation.pdf ; kit de démarrage : `…/BDM_serviceweb_SDMX_V2_2_kitdemarrage.pdf`.
- Fichiers d'appui publiés chaque mois sur la même page (noms datés) : liste des regroupements `dataflows_oct26.csv`, correspondance idbank/dimensions `202610_correspondance_idbank_dimension.zip`, codes et libellés `202610_liste_variables_modalites.zip`. Ils n'ont pas pu être lus (robots.txt) ; ils sont utiles au moissonnage de la phase 2.

### 2.2 Points d'entrée (tous en GET, HTTPS)
| Usage | Requête |
|---|---|
| Liste des dataflows | `https://bdm.insee.fr/series/sdmx/dataflow` (ou `/dataflow/FR1/all/latest`) |
| Un dataflow | `https://bdm.insee.fr/series/sdmx/dataflow/FR1/<ID>` |
| Structure (DSD) | `https://bdm.insee.fr/series/sdmx/datastructure/FR1/<ID>` |
| Liste de codes | `https://bdm.insee.fr/series/sdmx/codelist/FR1/<CL_…>` |
| Concepts | `https://bdm.insee.fr/series/sdmx/conceptscheme/` |
| Séries par idbank (1 à 400, séparés par `+`) | `https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/<idbank1>+<idbank2>` |
| Séries d'un dataflow (filtrables par clé) | `https://bdm.insee.fr/series/sdmx/data/<dataflow>/<clé>` |
| Calendrier des mises à jour (30 derniers jours) | `https://bdm.insee.fr/series/sdmx/rss/donnees` |

Paramètres : `startPeriod`, `endPeriod`, `firstNObservations`, `lastNObservations`, `detail` (`full`, `dataonly`, `serieskeysonly`, `nodata`), `includeHistory=true` et `updatedAfter=AAAA-MM-JJThh:mm:ss` (historique des publications, regroupements seulement).
Formats (en-tête `Accept`) : par défaut `application/vnd.sdmx.structurespecificdata+xml;version=2.1` ; `application/vnd.sdmx.genericdata+xml;version=2.1` ; `application/vnd.sdmx.structure+xml` pour les métadonnées ; `Accept-Encoding: gzip` accepté.
Erreurs (guide) : code SDMX 100 → HTTP 404 (aucun résultat), 140 → 400 (syntaxe), 500 → 500, 510 → 413 (réponse trop volumineuse, plus de 2 000 séries).

### 2.3 Comment lister le catalogue
1. `GET /dataflow` : un `str:Dataflow` par regroupement, avec `com:Name` (fr, en), une annotation URL vers la page insee.fr et une annotation « Nombre de séries : N ». **Lue en entier par le robot le 13/10/2026 : 244 dataflows, 374 463 séries annoncées, dont 187 146 pour `SERIES_BDM`** (regroupement technique de toutes les séries, non listé) — fixture `bdm_dataflows_2026-10-13.xml`. En phase 1, l'outil de lecture s'était arrêté après 94 dataflows. L'instantané du paquet R `insee` (août 2024) en compte **199** ; depuis, sont apparus au moins les flux base 2020 (`CNA-2020-*`, `CNT-2020-*`, `CONSO-MENAGES-2020`, `DETTE-TRIM-APU-2020`, `IC-PROD-CONS-2021`). Il n'existe **pas** de `CNA-2020-RDB` (revenu et pouvoir d'achat base 2020) parmi les flux lus.
2. `GET /data/<dataflow>?detail=nodata` : **une ligne par série avec IDBANK, TITLE_FR, TITLE_EN, LAST_UPDATE, REF_AREA, UNIT_MEASURE, sans observations**. C'est la bonne requête pour construire le catalogue.
   **Piège** : `detail=serieskeysonly` (recommandé par la fiche de mission) ne renvoie que les dimensions de la clé, **sans IDBANK ni titre** (vérifié sur `ODD-ERADICATION-PAUVRETE`).
3. Première et dernière période : `GET /data/<dataflow>?firstNObservations=1` et `?lastNObservations=6` (la dernière observation peut être une valeur manquante, voir §2.5).

### 2.4 Comment obtenir une série complète
`GET https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/<idbank>` renvoie toutes les observations, **de la plus récente à la plus ancienne**. Exemple vérifié : `SERIES_BDM/010593281` (satisfaction dans la vie) renvoie 16 observations, de 2025 (`NaN`) à 2010.

### 2.5 Structure de la réponse (StructureSpecificData)
- Racine `message:StructureSpecificData` ; `message:Header` (`ID`, `Test`, `Prepared`, `Sender id="FR1"`, `Structure structureID="FR1_SERIES_BDM_1_0" dimensionAtObservation="TIME_PERIOD"`, `Source`) ; `message:DataSet`.
- `Series` : attributs `IDBANK`, `FREQ` (A, T, M, B, S), `TITLE_FR`, `TITLE_EN`, `LAST_UPDATE` (AAAA-MM-JJ), `UNIT_MEASURE` (code, ex. `POURCENT`, `ANNEES`, `NOTE_MOYENNE_0_10`, `EUROS_HABITANTS`), `UNIT_MULT`, `REF_AREA`, `DECIMALS`. Les requêtes par dataflow ajoutent les dimensions de la clé (ex. `INDICATEUR`, `NATURE`, `CORRECTION`, `AGE`, `SEXE`…).
- `Obs` : `TIME_PERIOD` (`2024`, `2026-Q2`, `2026-09`), `OBS_VALUE` (point décimal ; `NaN` si manquante), `OBS_STATUS` (A définitive, P provisoire, SD semi-définitive, R révisée, E estimée, O manquante), `OBS_QUAL` (DEF, P, SD, E, F), `OBS_TYPE`, `OBS_REV` (présent si révisée).
- **Constat** : les séries des dataflows `ODD-*` se terminent par une observation `NaN` (statut O) pour l'année en cours, parfois deux. La « dernière période » d'une série doit donc être la dernière valeur non manquante.

### 2.6 Codes de zone rencontrés (`REF_AREA`) — ne pas fusionner
| Code | Signification | Exemple |
|---|---|---|
| `FE` | France (selon la série : y compris Mayotte depuis 2014) | espérance de vie 001686961 |
| `FM` | France métropolitaine | satisfaction dans la vie 010593281 |
| `FR-D976` | France hors Mayotte | chômage 001688527, taux d'emploi 010596081 |
| `FM_D99_D978` | périmètre Kyoto (métropole et outre-mer faisant partie de l'UE) | empreinte carbone 010595981 |
| `FR-SPM-WF`, `FE_HPBIO`, `D99`, `DOM`, `DOM-COM`, `PACIFIQUE…` | périmètres particuliers des indicateurs ODD | — |
| `FHREUN15_…`, `FMGUADMART16_…` | champs composites des enquêtes PISA/PIRLS/TIMSS | — |

### 2.7 Limites constatées
- Requêtes par clé de dataflow : **elles fonctionnent** (vérifié par le robot le 13/10). Une clé a une position par dimension du DSD, séparées par des points, codes multiples joints par « + » (ex. `CHOMAGE-TRIM-NATIONAL/T........` → 261 séries). Une clé sans série renvoie **HTTP 404, code SDMX 100** « Aucun résultat ne correspond à cette requête » (c'était la cause de l'« erreur client » de phase 1 : `A........` n'a pas de série dans ce regroupement trimestriel).
- Plus de 2 000 séries : **HTTP 413, code SDMX 510** « La réponse est trop volumineuse » ; le message propose lui-même des clés de découpage (ex. `/data/CNA-2020-ERE/A..IPCH......BRUT.FALSE`). Le module découpe automatiquement par la première dimension libre (fréquence d'abord). Coût : 40 à 65 requêtes et 2 à 3 minutes pour un regroupement de 2 000 à 6 000 séries.
- Le DSD (`/datastructure`) cite les dimensions deux fois : dans `DimensionList` (avec `id` et `position`, TIME_PERIOD en position 1) et dans les relations d'attributs (`<str:Dimension><Ref id="…"/>`, sans `id`). Seules les premières font la clé.
- Le nom de certaines dimensions contient un tiret dans les réponses réelles (`SECT-INST` des comptes base 2020) ; les dataflows ODD n'ont pas de dimension `SERIE_ARRETEE`.
- URL de plus de ~25 idbanks : refusée par le proxy de l'outil (longueur). Sans conséquence pour un script (limite serveur : 400).
- Réponses supérieures à ~60 ko tronquées par l'outil (pas par le serveur).

### 2.8 BDM via `api.insee.fr/series/BDM/V1/`
Ce point d'entrée « portail » existe dans le code de pynsee 0.2.5 (avec repli automatique sur `bdm.insee.fr`). La fiche data.gouv.fr « API BDM » le dit « Restreint » avec 30 appels/min/IP et renvoie vers l'ancien catalogue WSO2 (lien obsolète) ; le commentaire de pynsee dit qu'aucun jeton n'est nécessaire. Non vérifiable depuis le bac à sable. **Recommandation : utiliser `bdm.insee.fr`, ouvert et suffisant.**

---

## 3. Melodi (catalogue des données de l'INSEE)

### 3.1 Documentation et accès
- Catalogue grand public : https://catalogue-donnees.insee.fr (application JavaScript, illisible par l'outil). Fiche de l'API sur le portail : https://portail-api.insee.fr/catalog/api/a890b735-159c-4c91-90b7-35159c7c9126/doc (application JavaScript).
- Fiche data.gouv.fr « API Melodi » : accès « Ouvert avec compte », « hors inscription quota de 30 appels par minute en mode anonyme ».
- Paquet R officiel `melodi` (InseeFrLab, v1.1.2, dépôt mis à jour le 2026-10-09) : « Le package repose sur l'API Melodi, accessible sans authentification ». Ses enregistrements de tests (cassettes vcr, requêtes sans en-tête d'authentification, réponses 200) confirment l'accès anonyme.
- La page insee.fr « Données locales » (3544265) renvoie désormais vers ce catalogue et vers cette API.

### 3.2 Points d'entrée (déduits du paquet `melodi` et de ses enregistrements)
| Usage | Requête |
|---|---|
| Catalogue complet (fr + en) | `GET /melodi/catalog/all` |
| Notice d'un jeu | `GET /melodi/catalog/<jeu>` |
| Données filtrées | `GET /melodi/data/<jeu>?<DIMENSION>=<code>&…&maxResult=<n>&totalCount=TRUE&page=<p>` |
| Valeurs possibles des dimensions (codes et libellés) | `GET /melodi/range/<jeu>` |
| Fichier complet (ZIP de CSV, XLSX) | `GET /melodi/file/<jeu>/<identifiant_produit>` (URL donnée par `product[].accessURL` dans le catalogue) |
| Liste de codes (référentiel RMéS) | `GET /melodi/rmes/listeCode/<CL_…>` |

- `maxResult` jusqu'à **100 000** lignes ; `totalCount=TRUE&maxResult=0` donne le nombre de lignes (`paging.count`) sans les données.
- Filtre géographique : `GEO=<NIVEAU>-<code>` (ex. `GEO=DEP-69`, `GEO=FRANCE-F`) ; dans les réponses, `GEO` vaut `<millésime>-<niveau>-<code>` (ex. `2025-COM-44109`).
- Jeu inexistant : HTTP 500, texte « Le serveur a rencontré une erreur inattendue. » (pas un 404).

### 3.3 Structure des réponses
- `/data` : `{"identifier", "title": {"fr","en"}, "publisher", "observations": [ {"dimensions": {"GEO","FREQ","TIME_PERIOD", …}, "attributes": {"OBS_STATUS", …}, "measures": {"OBS_VALUE_NIVEAU": {"value": 327734.0}} } ], "paging": {"first", "count"}}`. Le nom de la mesure varie selon le jeu (`OBS_VALUE_NIVEAU`, `OBS_VALUE_INDICE_DE_PRIX`).
- `/catalog/all` : liste de notices DCAT (`identifier`, `title`, `subtitle`, `description`, `temporal{startPeriod,endPeriod}`, `accrualPeriodicity`, `spatial`, `spatialResolution`, `theme`, `structure{dsd}`, `product[]` avec `accessURL`, `ordreComposants` = liste des dimensions et attributs, `numSeries`, `modified`, `keyword`).
- `/range` : `{"code","label","range":[{"concept":{"code","label"},"type":"modalites","values":[{"code","label"}]}]}`.

### 3.4 Contenu national utile (catalogue du 2026-01-06 : 96 jeux)
| Jeu | Contenu | Période | Remarque |
|---|---|---|---|
| `DD_CNA_AGREGATS`, `DD_CNA_TEE`, `DD_CNA_CONSO_MENAGES_COICOP`, `DD_CNA_PATRIMOINE`, `DD_CNA_APU` … | comptes nationaux annuels **base 2020** | 1949-2024 | seule voie trouvée pour le RDB, l'épargne et la consommation des ménages en base 2020 |
| `DD_EEC_SERIES` | activité, emploi, chômage (enquête Emploi), séries longues | 1975-2024 | |
| `DS_ERFS_INDIVIDU_SL`, `DS_ERFS_MENAGE_SL`, `DS_ERFS_CHAMP_CONST_SL` | niveau de vie (médiane, moyenne, D1, D9, D9/D1), pauvreté (taux, seuil, intensité) | 1996-2022 (1970-2022 à champ constant) | France métropolitaine |
| `DS_SRCV_SATISFACTION`, `DS_SRCV_CONFIANCE`, `DS_SRCV_PMS` | satisfaction (vie, relations, travail), confiance envers les autres, privation matérielle et sociale | 2010-2024 ; 2020-2024 ; 2020-2024 | déclaratif |
| `DS_MORTALITE`, `DS_FECONDITE`, `DS_ESTIMATION_POPULATION` | espérance de vie, mortalité infantile ; fécondité ; population | 1901-2025 ; 1990-2025 | |
| `DS_TICM_EQUIPEMENT`, `DS_TICM_PRATIQUES` | équipement et usages d'internet | 2009-2025 | |
| `DS_ENQPAT_DET` | patrimoine des ménages | 1998-2021 (triennal) | |
| `DS_DERA_PRIVE_SERIES_LONGUES`, `DS_DERA_PUBLIC_SERIES_LONGUES` | salaires en euros constants | 1951-2024 ; 1995-2023 | |
| `DS_DEVDUR` | indicateurs ODD (609 séries) | 1975-2024 | remplacé semble-t-il par `DS_NAT_SDG` |
| **`DS_NAT_SDG`** | indicateurs nationaux ODD (codes `INDICATOR_SDG`, ex. `3.i4a`) | 2010- | **absent du catalogue de janvier 2026**, cité par les pages ODD publiées le 27/05/2026 |

Le catalogue grandit : `DS_NAT_SDG` et `DS_IPC_PRINC` (IPC base 2025, enregistré le 2026-03-16) n'existaient pas en janvier 2026. La phase 2 devra relire `/catalog/all` en direct.

---

## 4. Données locales (documentation seulement, hors périmètre v1)
- URL : `https://api.insee.fr/donnees-locales/donnees/geo-<croisement>@<jeu>/<niveau>-<code>.<modalités>` ; exemple tiré de pynsee : `geo-SEXE-DIPL_19@GEO2020RP2017/FE-1.all.all`.
- Authentification : aucune selon pynsee 0.2.5 (quota appliqué : 30/min).
- Statut : pynsee 0.2.5 avertit que cette API est « obsolète » et que ses jeux « ne sont plus mis à jour », l'INSEE recommandant Melodi ; la page insee.fr 3544265 présente désormais le catalogue Melodi. Aucune date d'arrêt officielle trouvée.
- **Pas de fixture** : `api.insee.fr` est interdit à l'outil de lecture et aucun enregistrement public n'a été trouvé. Sans conséquence pour le projet (échelle nationale).

## 5. Métadonnées (documentation seulement)
- URL : `https://api.insee.fr/metadonnees/` ; services utilisés par pynsee : `/concepts/definitions`, `/concepts/definition/<id>`, `/codes/cj/n3/<code>`, `/geo/<type>`. Authentification : aucune selon pynsee 0.2.5.
- Même référentiel (RMéS) en données liées : les URI `http://id.insee.fr/concepts/definition/<id>` redirigent vers le point SPARQL **`https://rdf.insee.fr/sparql`**, ouvert et lisible (vérifié). Exemple : concept `c1653` « Pauvreté monétaire » (définitions v1 à v5, modifié le 2025-04-29).
- Melodi expose aussi les listes de codes (`/melodi/rmes/listeCode/CL_AGE`).
- Utilité pour le projet : définitions officielles pour les fiches indicateurs (champ `definition`).

## 6. Fichiers insee.fr à URL stable (niveau 2)
- Forme : `https://www.insee.fr/fr/statistiques/fichier/<identifiant_page>/<nom_fichier>`.
- **Stabilité faible** : les fichiers des 10 « Indicateurs de richesse nationale » changent de nom à chaque édition (ex. `01_Taux_emploi_2024_rapport(version juin 2024).xlsx`, `10-Artificialisation-sols_2024_v20241016-1.xlsx`) ; les séries longues ERFS sont millésimées (`irsocerfs2023_dd0_excel.zip`, page 8731524) ; la liste ODD aussi (`liste_nationale_iODD_2025.xlsx`). Seul candidat apparemment stable repéré : **Chiffres-clés « Niveau de vie et indicateurs d'inégalités »** `…/fichier/2491918/reve-niv-vie-indic-inegalite.xlsx` (page mise à jour le 09/07/2026), utile pour l'**indice de Gini**.
- Le robots.txt d'insee.fr interdit `*.xls`, `*.xlsx`, `*.csv`, `*.zip` aux robots d'exploration : l'outil de lecture ne peut pas les ouvrir. Un script de collecte ponctuel (GitHub Actions, une fois par mois) reste un usage normal de téléchargement, mais c'est un point à valider (§11).
- « Tableau de bord de l'économie française » (outil interactif 5367857) et « France, portrait social » : applications JavaScript ou fichiers annuels renommés ; non recommandés. Leurs données proviennent de la BDM et de Melodi.
- Fixture : aucun fichier insee.fr ; le test du lecteur XLSX pourra utiliser le fichier XLSX réel servi par Melodi (`melodi_file_DS_EC_DECES_…xlsx`, 2 feuilles « Métadonnées » et « France »).

---

## 7. Où se trouvent réellement les indicateurs sociaux annuels
1. **BDM, 17 dataflows `ODD-*`** (« Objectif de développement durable n°… ») : 645 séries vivantes, la plupart mises à jour le 2026-05-27, annuelles et nationales. Ils contiennent **les 10 IRN** et l'essentiel des indicateurs sociaux : pauvreté monétaire et en conditions de vie, inégalités, taux d'effort, satisfaction, espérance de vie (en bonne santé), suicide, tabac, renoncement aux soins, sorties précoces, compétences, écarts femmes-hommes, emploi, sous-emploi, NEET, homicides, violences, confiance dans les institutions, dette, R&D, environnement. Limite : la plupart commencent en **2010** (séries plus longues : emploi 1975, R&D 1996, (100-S80)/S20 1996, empreinte carbone 1995, artificialisation 1982).
2. **BDM, autres dataflows** : `DECES-MORTALITE` (espérance de vie depuis 1946 en métropole), `CNA-2020-PIB` (PIB par habitant depuis 1949), chômage (`CHOMAGE-TRIM-NATIONAL`, trimestriel ; moyenne annuelle dans `TCRED-TRAVAIL-EMPLOI-TCHOMA-SA`), participation électorale (`TCRED-CONDITIONSDEVIE-TXP-CDE`). Plusieurs tableaux `TCRED-*` sont **arrêtés** (revenus Filosofi arrêtés en 2015 ; salaire annuel moyen 001782649 absent aujourd'hui).
3. **Melodi** : séries longues d'enquêtes (ERFS 1996/1970-2022, SRCV, enquête Emploi 1975-2024), comptes nationaux base 2020 (RDB, épargne, consommation), démographie, numérique, patrimoine, salaires ; et depuis mai 2026 `DS_NAT_SDG` (ODD).
4. **Fichiers** : en phase 1, l'indice de Gini du niveau de vie n'avait été trouvé que dans un fichier Chiffres-clés ; le catalogue complet du 13/10 le trouve dans Melodi (`DS_ERFS_RETROPOLE`, 1996-2024 ; `DS_ERFS_NON_RETROPOLE`, 1975-2024), toujours sans idbank BDM (§12.7).
5. **Hors INSEE** : sentiment d'insécurité (SSMSI) ; surpeuplement et taux d'effort annuels (Eurostat, SILC) — l'INSEE ne les publie que par l'enquête Logement (2013, 2020).

## 8. Indicateurs de référence (liste minimale de la fiche)
Détail complet (voies complémentaires, alternatives, commentaires) : `docs/sources/insee_indicateurs_reference.csv`.

| Indicateur | Disponibilité INSEE | Voie | Identifiant exact | Zone | Période (vérifiée) | Dim. v0 |
|---|---|---|---|---|---|---|
| IRN 1 Taux d'emploi (15-64 ans) | API | BDM | 010596081 | FR-D976 | 1975-2024 | travail |
| IRN 2 Effort de recherche (DIRD/PIB) | API | BDM | 010594852 | FE | 1996-2024 | niveau_de_vie |
| IRN 3 Endettement public / ménages / SNF | API | BDM | 010596873 / 010596874 / 010596875 | FE | 2010-2024 | niveau_de_vie |
| IRN 4 Espérance de vie en bonne santé F / H | API | BDM | 010593268 / 010593269 | FE | 2004-2024 | sante |
| IRN 5 Satisfaction dans la vie | API | BDM (+ Melodi `DS_SRCV_SATISFACTION`) | 010593281 | FM | 2010-2024 | liens_bien_etre |
| IRN 6 Inégalités de revenus (100-S80)/S20 | API | BDM | 010594680 | FM | 1996-2023 | egalites |
| IRN 7 Pauvreté en conditions de vie (privation matérielle et sociale) | API | BDM | 010594486 | FM | 2013-2024 | niveau_de_vie |
| IRN 8 Sorties précoces | API | BDM | 010594746 | FR-D976 | 2006-2024 | education |
| IRN 9 Empreinte carbone (par hab. / totale) | API | BDM | 010595988 / 010595981 | FM_D99_D978 | 1995-2024 | planete |
| IRN 10 Artificialisation des sols | API | BDM | 010596134 (+ surface 010596146) | FM | 1982-2023 | planete |
| Taux de pauvreté monétaire 60 % | API | BDM (+ Melodi ERFS pour 1996-2009) | 010594446 | FM | 2010-2023 | niveau_de_vie |
| Niveau de vie médian | API | Melodi | `DS_ERFS_RETROPOLE` (`ERFS_MEASURE=MED_SL`) ; le jeu `DS_ERFS_INDIVIDU_SL` de phase 1 n'existe plus | FRANCE-FM | 1996-2024 | niveau_de_vie |
| Rapport interdécile D9/D1 | API | BDM | 010594681 | FM | 2010-2023 | egalites |
| Indice de Gini (niveau de vie) | API (Melodi, **pas d'idbank BDM**) | Melodi ; fichier Chiffres-clés 2491918 ; alternative Eurostat `ilc_di12` | `DS_ERFS_RETROPOLE` (`ERFS_MEASURE=GI_SL`) | FRANCE-FM | 1996-2024 | egalites |
| Taux de chômage BIT (moyenne annuelle) | API | BDM | 001787717 (FR-D976) ; 001787711 (FM, 1982-) ; 001688527 (trimestriel) | FR-D976 | 2014-2025 | travail |
| Taux d'emploi 15-64 ans | API | BDM | 010596081 | FR-D976 | 1975-2024 | travail |
| Espérance de vie à la naissance F / H | API | BDM | 001686961 / 001686956 | FE | 1994-2025 | sante |
| PIB par habitant en volume | API | BDM | 011779993 (base 2020) | FE | 1949-2025 | niveau_de_vie |
| Dépense de consommation des ménages par habitant | à calculer | Melodi `DD_CNA_AGREGATS` (`EXPENDITURE=CPDEP`, `STO=P31`, `REF_SECTOR=S14`) / population | requête complète dans le CSV | FRANCE-F | 1959-2025 | niveau_de_vie |
| Taux d'épargne des ménages | API (Melodi ; idbank BDM annuel non trouvé) | Melodi `DD_CNA_AGREGATS` (`STO=_TEM`, `REF_SECTOR=S14`) ; alternative Eurostat `nasa_10_ki` | requête complète dans le CSV | FRANCE-F | 1949-2025 | niveau_de_vie |
| Satisfaction dans la vie (SRCV) | API | Melodi `DS_SRCV_SATISFACTION` (`SRCV_MEASURE=VIESATISF`, 16 ans ou plus) / BDM 010593281 | requête complète dans le CSV | FRANCE-FM | 2010-2025 | liens_bien_etre |
| Sentiment d'insécurité (CVS/VRS) | **non disponible à l'INSEE par API** | SSMSI (data.gouv.fr `62029493ff5c2e6d510b42b6` ; enquête VRS depuis 2022) | — | — | — | securite_confiance |
| Part des ménages en surpeuplement | API mais 2 points (2013, 2020) | BDM 010596142 ; alternative Eurostat `ilc_lvho05a` | — | FM | 2013-2020 | logement_cadre_vie |
| Taux d'effort logement | API mais 1 point (2013) | BDM 010594494 ; alternative Eurostat `ilc_lvho07a` | — | FM | 2013 | logement_cadre_vie |

Toutes les valeurs « période » des lignes BDM ont été lues en direct le 2026-10-13 (première observation renvoyée, dernière valeur non manquante). Les lignes Melodi (niveau de vie médian, Gini, consommation, taux d'épargne, satisfaction SRCV) ont été mises à jour le 14/10 d'après le catalogue complet ; contrôle de présence de tous les indicateurs de référence au §12.7.

## 9. Repérage large (`docs/sources/insee_indicateurs_reperes.csv`)
- **1 063 lignes** : 858 séries BDM (645 séries ODD vivantes, 151 autres séries annuelles, 53 séries trimestrielles agrégeables, 6 mensuelles déclaratives, 3 séries des comptes nationaux base 2020), 192 lignes Melodi (34 jeux nationaux, 158 codes `INDICATOR_SDG` de `DS_NAT_SDG`), 13 fichiers insee.fr.
- Colonnes : celles du catalogue (charte §5.3) + `voie_acces` et `url_api`. `candidat` vaut `oui` (600 lignes), `non` (248, raison en commentaire : moyen, zone non nationale, dernière valeur < 2020, série arrêtée…) ou `a_verifier` (215).
- Répartition des `candidat = oui` par dimension v0 : planete 207, niveau_de_vie 93, travail 85, sante 78, liens_bien_etre 42, egalites 28, education 24, democratie 19, securite_confiance 15, logement_cadre_vie 9. Les dimensions **logement**, **sécurité** et **démocratie** sont mal couvertes par l'INSEE : à compléter par Eurostat (M02) et les autres sources (M04).
- Le commentaire `ventilation` signale les déclinaisons par sexe, âge, PCS, quartile (utiles pour la dimension égalités, à ne pas confondre avec l'indicateur d'ensemble).
- Limites : libellés des séries BDM anciennes repris de l'instantané d'août 2024 ; séries hors ODD non vérifiées une à une (marquées) ; codes `INDICATOR_SDG` parfois attribués par inférence (marqués) ; périodes Melodi = couverture du jeu, pas de chaque série.

## 10. Fixtures (`tests/fixtures/insee/`)
Depuis la phase 2, **toutes les fixtures BDM sont des réponses brutes** enregistrées par le robot (décision D21) ; les fixtures reconstituées de phase 1 ont été remplacées. Le robot réenregistre ces échantillons à chaque nouveau cycle dans `docs/sources/echantillons_insee/` (avec `provenance.csv` : URL, statut HTTP, taille, horodatage).

| Fichier | Voie | Provenance |
|---|---|---|
| `bdm/bdm_dataflows_2026-10-13.xml` | BDM | réponse brute du robot : liste complète (244 dataflows) |
| `bdm/bdm_dataflow_ODD-ERADICATION-PAUVRETE_…`, `bdm/bdm_datastructure_CHOMAGE-TRIM-NATIONAL_…`, `bdm/bdm_codelist_CL_PERIODICITE_…` | BDM | réponses brutes du robot (structure) |
| `bdm/bdm_nodata_ODD-ERADICATION-PAUVRETE_…`, `…_CNA-2020-PIB_…`, `…_CHOMAGE-TRIM-NATIONAL_cle_T_…` | BDM | réponses brutes `detail=nodata` (65, 21 et 261 séries) |
| `bdm/bdm_erreur_trop_de_series_CNA-2020-ERE_…`, `bdm/bdm_erreur_cle_sans_resultat_…` | BDM | erreurs réelles 413 (code 510) et 404 (code 100) |
| `bdm/bdm_serie_010593281_…`, `bdm/bdm_serie_001688527_last5_…`, `bdm/bdm_series_010593281+001688527_first1_…` | BDM | séries complètes, dernières et premières observations |
| `bdm/provenance_bdm.csv` | BDM | URL, statut, horodatage de chaque fixture (run 38405848499 du 13/10) |
| `melodi/*_2026-01-06…` à `*_2026-07-17…` (`.json`, `.xlsx`, `.txt`) | Melodi | réponses réelles enregistrées par l'INSEE (cassettes vcr du paquet R `melodi`, dépôt InseeFrLab/melodi) |
| `melodi/*_2026-10-13…` | Melodi | réponses brutes du robot : catalogue d'octobre (145 jeux, `.json.gz`), notice, `/range`, `/data`, comptage et extraits du ZIP de `DS_SRCV_SATISFACTION`, `/range` et `/data` de `DS_NAT_SDG`, `/range` de `DD_CNA_AGREGATS` ; correspondance dans `melodi/provenance_melodi.csv` |
| `metadonnees/rdf_sparql_concept_c1653_2026-10-13.csv` | Métadonnées (RMéS) | réponse SPARQL de `rdf.insee.fr` (lue le 2026-10-13) |
| — | Données locales | aucune (voir §4) |
| — | Fichiers insee.fr | aucune ; XLSX réel de Melodi utilisable pour le lecteur XLSX |

## 11. Points à trancher ou vérifier (état à la clôture de la phase 2, 14/10/2026)
1. **Voies retenues** (D14) : BDM `bdm.insee.fr` + Melodi, sans clé — confirmé par le passage complet (1 976 appels HTTP, 1 030 Mo, aucune authentification, aucun refus de débit, aucune erreur) ; Données locales abandonnée ; le fichier Chiffres-clés du Gini n'est plus nécessaire (Gini dans Melodi, §12.7) : aucun fichier insee.fr n'est moissonné.
2. ~~Fixtures BDM reconstituées~~ : **fait**, remplacées par les réponses brutes (§10).
3. ~~Requêtes par clé de dataflow~~ : **fonctionnent** depuis Actions (§2.7).
4. **Série longue 2000-2009** (D16) : 435 séries candidates portent le motif « raccordement à prévoir » (175 BDM, surtout ODD 2010-… ; 260 Melodi) ; le raccord (ERFS rétropolé 1996-2024, enquête Emploi 1975-2025) reste à faire en M05.
5. **Choix de zone** (D15) : `FM` (métropole) pour les enquêtes ménages, `FR-D976` pour l'enquête Emploi, `FE` pour la démographie et les comptes ; Melodi ajoute `FRANCE-F`, `FRANCE-FM`, `FRANCE-F_X_D976` et, pour les jeux sans dimension géographique, le niveau du jeu (`FE`, `FEHM`) : la colonne `geo` les garde distincts. « France métropolitaine hors Île-de-France » (`FRANCE-FM_X_R11`) est écartée depuis le 14/10.
6. **Comptes nationaux** : les règles de bruit ne gardent que les agrégats ; il reste 2 145 séries Melodi (`DD_CNA_*`) et 128 séries BDM base 2020 candidates (soldes, revenus, consommation, épargne, investissement, patrimoine par grand type d'actif). La correspondance v0 → v1 du gel 1 (A5) écartera l'investissement, la dette publique et le patrimoine national : à relire par la session mère avec M05.
7. **Indicateurs pluriannuels** (D17) : depuis le 14/10, une série courte (moins de 10 points) n'est plus écartée si l'écart moyen entre ses valeurs est d'au moins 1,5 an (PISA, participation électorale, état des masses d'eau, Gini du patrimoine, surpeuplement) : `a_verifier`, motif « série pluriannuelle ou irrégulière (D17) ».

## 12. Catalogue des séries candidates (phase 2, robot de collecte)

### 12.1 Méthode
`scripts/collecte_insee.py`, exécuté par GitHub Actions (workflow « Collecte »), en étapes reprenables d'un passage à l'autre (état dans `catalogues/insee_etat/`) :
1. **BDM** : liste des dataflows et des listes de codes ; pour chaque dataflow (sauf `SERIES_BDM`), toutes les séries par `detail=nodata` avec découpage automatique au-delà de 2 000 séries (§2.7) ; pour les séries nationales de fréquence A/S/T/B/M mises à jour depuis 2020 : lecture complète des séries annuelles (première et dernière valeur non manquante, nombre d'années avec valeur depuis 2000), première et dernière observation des séries infra-annuelles.
2. **Melodi** : catalogue `/catalog/all` ; jeux écartés d'emblée (motif tracé dans `insee_melodi_jeux.csv`) : statistiques d'entreprises, équipements, prénoms, comptes par branche ou par produit, comptes régionaux, jeux sans niveau national, jeux d'**un seul millésime** ou terminés avant 2020 ; pour les autres, `/range` puis extraction du **seul niveau national** (`/data` filtré sur chaque valeur nationale de `GEO`, ou fichier ZIP complet si le jeu est entièrement national et dépasse 100 000 lignes). Une série Melodi = une combinaison de modalités ; son identifiant est la requête qui la relit (`<jeu>?DIM=code&…`).
3. **Échantillons** de réponses brutes (§10), **inventaires** bruts (`catalogues/insee_bdm_inventaire.csv.gz`, `insee_melodi_inventaire.csv.gz`), puis **catalogage hors ligne** (`--catalogage-seul`, exécutable dans le bac à sable sur les inventaires).

Options : `scripts/collecte_insee.options` (`--cycle mois --budget-minutes 255`). Avec `--cycle`, un cycle terminé n'est pas recommencé : un nouveau passage refait seulement le catalogage avec les règles du moment ; le mois suivant (ou un autre identifiant de cycle) relance une collecte complète (§12.9).

### 12.2 Fichiers produits (`catalogues/`)
| Fichier | Contenu |
|---|---|
| `insee_bdm_catalogue.csv`, `insee_melodi_catalogue.csv` | séries **candidates** (`candidat` = `oui` ou `a_verifier`) : colonnes de la charte §5.3 (`source, serie_id, libelle, unite, frequence, geo, premiere_periode, derniere_periode, derniere_maj, theme_source, dimension_v0, candidat, commentaire`) + `agregable, ventilation, geo_libelle, nb_annees_depuis_2000, statut_derniere_valeur, theme_libelle, url_api` |
| `insee_bdm_catalogue_non.csv.gz`, `insee_melodi_catalogue_non.csv.gz` | séries soumises aux règles mais écartées (`candidat = non`), mêmes colonnes, **motif dans `commentaire`** (traçabilité, charte §3.6) |
| `insee_bdm_inventaire.csv.gz`, `insee_melodi_inventaire.csv.gz` | toutes les séries listées (BDM) ou nationales (Melodi), avec leurs dimensions, avant tout filtre (les séries écartées par un filtre dur ne sont que là) |
| `insee_bdm_dataflows.csv`, `insee_melodi_jeux.csv`, `insee_bdm_zones.csv` | traitement par dataflow / jeu (statut, motif d'exclusion, nombre de séries, de candidates) ; codes de zone rencontrés |
| `insee_bilan.json` | chiffres clés (séries listées, exclusions par motif, candidats par dimension, comparaison avec la phase 1, journal des passages) |
| `insee_comparaison_phase1.csv` | sort de chacune des 1 063 lignes du repérage de phase 1 (confirmée, écartée par un filtre et pourquoi, absente) |

Journaux du robot : `journaux/collecte_<AAAA-MM-JJTHHMM>_collecte_insee.py.log` (passage complet : `…2026-10-13T1422…` ; catalogages des 13 et 14/10 : `…T1532…`, `…2026-10-14T0004…`, `…T0010…`, `…T0013…`).

### 12.3 Règles (`src/sources/insee_catalogue.py`, état final du 14/10)
- **Filtres durs** (série absente des catalogues, comptée dans les exclusions du bilan) : fréquence A, S, T, B ou M (Melodi code le trimestre « Q », lu comme T depuis le 14/10) ; zone nationale (FE, FM, FR-D976 et autres périmètres nationaux, gardés distincts — D15 ; périmètres partiels écartés) ; dernière valeur non manquante ≥ 2020 (pour la BDM, une série mise à jour pour la dernière fois avant 2020 ne peut pas l'avoir : ses périodes ne sont pas lues) ; Melodi : combinaisons sans aucune valeur numérique ; comptes trimestriels `DS_CNT_*` (doublon des dataflows BDM `CNT-2020-*`).
- **`candidat = non`** (motif en commentaire) :
  - *hors champ* : statistiques d'entreprises, prix de production, prix agricoles et de détail par produit, indices de prix et déflateurs, coût du travail, conjoncture des entreprises, commerce extérieur, tourisme vu de l'offre, trafic et activité des transports, barèmes (cotisations, indices de traitement, minimum garanti, plafond de la sécurité sociale, indices de taux de salaire), aide publique au développement ; depuis le 14/10 : immatriculations de véhicules neufs (sauf la part de véhicules électriques), réseau routier, effectifs de la fonction publique, nombre d'établissements scolaires, emploi par branche (code NAF dans le libellé, grands secteurs des tableaux « Emploi au 31 décembre »), intentions d'achat de l'enquête de conjoncture auprès des ménages, recensement « dossier complet » de Melodi (trois millésimes de comparaison, sauf la suroccupation des logements) ;
  - *déclinaisons techniques* lues dans les codes de dimensions (sous-secteurs institutionnels et sociétés, contreparties, branches, produits détaillés, COFOG de niveau 2, instruments financiers et actifs détaillés sauf les logements, valorisations et transformations techniques ; dans les comptes nationaux, opérations hors liste des agrégats) ; depuis le 14/10, instruments détaillés de la dette publique (on garde l'ensemble, la dette nette et le total des passifs) ;
  - séries arrêtées ; anciennes bases ; démographie de contexte ; aucune règle de dimension ; série annuelle de moins de 10 points depuis 2000 quand elle commence après 2010.
- **`candidat = a_verifier`** : première période après 2010 mais au moins 10 points possibles (raccordement D16) ; moins de 10 années avec valeur (série irrégulière, D17) ; série courte mais pluriannuelle (écart moyen ≥ 1,5 an, D17, depuis le 14/10) ; dimension déduite du seul regroupement ; zone non renseignée.
- **`candidat = oui`** : les autres ; drapeaux en commentaire : `type moyen (D19)`, `infra-annuelle : agrégation annuelle à prévoir`, `périmètre national particulier`, `ventilation : sexe;age;…` (D21, colonne `ventilation`).
- **Tagging `dimension_v0`** (grille v0 de la charte, conservée dans les catalogues : le passage à la grille v1 figée est fait par la long-list de M05 avec `docs/methodo/31_correspondance_v0_v1.csv`) : règles de mots-clés ordonnées sur le libellé, après retrait des expressions comptables (« Emploi ou débit », « actifs financiers »…) et, depuis le 14/10, des parties de libellé Melodi qui ne sont que des modalités de ventilation (sexe, âge, statut d'activité, PCS, diplôme, décile, versant de la fonction publique…) ; à défaut, dimension du regroupement ODD ou du libellé du regroupement.
- **Validation des règles** (13/10) : application à l'instantané de 158 166 séries BDM du paquet R `insee` (août 2024) et aux inventaires réels de l'essai ; corrections : faux négatif « au cours des … derniers mois », « pour 100 000 habitants » classé en démographie, densité carcérale non classée ; bruit des comptes nationaux et des statistiques d'entreprises. Contrôle sur les catalogues complets (14/10) : §12.5.

### 12.4 Bilan du passage complet
**Collecte** : run **38412716221** (13/10, 14:22 → 15:32 UTC, commit e98381f) — cycle `mois-2026-10` terminé en un seul passage de 69,7 min : 1 976 appels HTTP, 1 029,7 Mo, aucune erreur. Le run **38417739553** (13/10, 15:32 UTC) a refait le catalogage avec les règles du 13/10 au soir ; les runs 38487986391, 38488591925 et 38488913205 (14/10, 00:04 → 00:15 UTC) l'ont refait avec les règles corrigées du §12.5 (catalogage seul, environ 1 min chacun). Chiffres finaux : `catalogues/insee_bilan.json` du 2026-10-14T00:14:39Z.

**BDM**
- 244 dataflows annoncés (374 463 séries, dont 187 146 pour `SERIES_BDM`, non listé) ; 243 listés sans erreur ; **182 082 séries distinctes** dans 226 dataflows (15 dataflows techniques sans libellé ne renvoient qu'une série déjà listée ailleurs ; `IPPI-2005` et `IPPI-2010` ne renvoient aucune série sur 2 571 et 2 493 annoncées : prix de production, hors champ).
- Par fréquence : A 126 772, M 37 098, T 17 044, B 832, S 336 ; par zone : principale (FE, FM, FR-D976) 130 172, autres périmètres nationaux 271, sans objet 1, non nationale 51 638.
- Filtres durs : zone non nationale 51 638 ; dernière mise à jour antérieure à 2020 50 368 ; dernière période antérieure à 2020 492 ; périodes inconnues 99 → **79 485 séries soumises aux règles** : **1 211 `oui`, 297 `a_verifier`** (catalogue de 1 508 séries), 77 977 `non`.

**Melodi**
- 145 jeux au catalogue d'octobre 2026 : 84 écartés d'emblée (dont 39 jeux détaillés du recensement d'un seul millésime), 61 traités ; **66 287 séries nationales** extraites.
- Filtres durs : aucune valeur numérique 9 992 ; dernière période antérieure à 2020 2 196 ; comptes trimestriels doublons de la BDM 1 677 ; fréquence quotidienne (corps électoral, décès quotidiens) 105 ; périmètre partiel (hors Île-de-France) 34 → **52 283 séries soumises aux règles** : **5 413 `oui`, 1 183 `a_verifier`** (catalogue de 6 596 séries), 45 687 `non`.

**Séries candidates par dimension v0** (`oui` + `a_verifier`)

| Dimension v0 | BDM oui | BDM à vérifier | Melodi oui | Melodi à vérifier | Total | dont séries d'ensemble (sans ventilation) |
|---|---:|---:|---:|---:|---:|---:|
| niveau_de_vie | 275 | 16 | 2 418 | 790 | 3 499 | 2 256 |
| travail | 442 | 10 | 1 732 | 219 | 2 403 | 283 |
| logement_cadre_vie | 99 | 11 | 117 | 15 | 242 | 218 |
| sante | 180 | 63 | 173 | 41 | 457 | 100 |
| education | 14 | 70 | 394 | 24 | 502 | 80 |
| liens_bien_etre | 12 | 16 | 405 | 0 | 433 | 17 |
| securite_confiance | 34 | 0 | 12 | 0 | 46 | 34 |
| democratie | 1 | 25 | 1 | 5 | 32 | 32 |
| egalites | 39 | 7 | 28 | 17 | 91 | 32 |
| planete | 115 | 79 | 133 | 72 | 399 | 397 |
| **Total** | **1 211** | **297** | **5 413** | **1 183** | **8 104** | **3 449** |

Lecture : le volume de `niveau_de_vie` vient des comptes nationaux Melodi (2 145 séries `DD_CNA_*`), de l'ERFS (826 séries, dont les ventilations par âge, statut, type de ménage) et des salaires (`DS_DERA_*`, `SALAIRES-ANNUELS`) ; celui de `travail`, de l'enquête Emploi en séries longues (1 673 séries `DD_EEC_SERIES`, ventilations comprises) ; celui de `liens_bien_etre`, de la satisfaction SRCV ventilée (402 séries). Les dimensions sécurité (46), démocratie (32) et égalités (91) restent minces à l'INSEE (sentiment d'insécurité, confiance institutionnelle annuelle, libertés : autres sources, M02 et M04).

**Fréquences des candidates** : BDM annuelle 996, trimestrielle 416, mensuelle 96 (512 séries infra-annuelles à agréger) ; Melodi annuelle 6 594, mensuelle 2.

**Géographies des candidates** : BDM FE 665, FM 515, FR-D976 174, `FM99_FR00` 99 (salaires du secteur privé), `FM_D99_D978` 35 (périmètre Kyoto : empreinte carbone), champs PISA/PIRLS/TIMSS 16, `FM_H_CORSE_2018` 2, `FR-SPM-WF` 1, `FE_HPBIO` 1 (154 séries « périmètre national particulier ») ; Melodi `FRANCE-F` 2 866, `FE` 1 673 (enquête Emploi, jeu sans dimension géographique), `FRANCE-FM` 1 540, `FEHM` 380 (TIC), `FRANCE-F_X_D976` 137.

**Ventilations (D21)** : BDM 679 séries ventilées (âge 441, sexe 429, statut d'activité 35, PCS 35, revenu 9) ; Melodi 3 976 (âge 3 002, statut d'activité 1 764, sexe 1 626, diplôme 735, PCS 632, revenu 430, type de ménage 186, nationalité 21) ; 3 449 séries d'ensemble au total.

**Autres drapeaux** : type moyen (D19) 94 BDM + 457 Melodi ; raccordement (D16) 175 + 260 ; série irrégulière ou pluriannuelle (D17) 117 + 775 ; dimension déduite du regroupement 46 + 166.

**Groupes vérifiés** (soumises aux règles → `oui` / `a_verifier` / `non`)

| Groupe | Soumises | oui | à vérifier | non (motif principal) |
|---|---:|---:|---:|---|
| BDM, 17 dataflows ODD (645 séries listées) | 545 | 307 | 142 | 96 (série annuelle de moins de 10 points 56 ; APD 23 ; arrêtée 16) |
| Melodi `DS_NAT_SDG` | 443 | 247 | 146 | 50 (moins de 10 points 26 ; APD 23) |
| BDM `DECES-MORTALITE` | 176 | 150 | 0 | 26 (séries arrêtées, remplacées) |
| Melodi `DS_DECES_MORTALITE_SERIES` | 150 | 150 | 0 | 0 |
| BDM enquête Emploi (`CHOMAGE-TRIM-NATIONAL`, `EMPLOI-BIT-TRIM`, `TCRED-TRAVAIL-EMPLOI-TCHOMA-SA`) | 453 | 231 | 7 | 215 (séries « France hors Mayotte » arrêtées, remplacées par « France entière ») |
| Melodi `DD_EEC_SERIES` | 1 673 | 1 559 | 114 | 0 |
| Melodi `DS_SRCV_SATISFACTION` | 834 | 417 | 0 | 417 (séries « France hors Mayotte » commencées en 2022) |
| BDM satisfaction dans la vie (ODD 3) | 39 | 12 | 0 | 27 (répartition faible/moyenne/élevée, 2020-2023) |
| Melodi `DS_SRCV_PMS` et `DS_SRCV_CONFIANCE` | 1 992 | 0 | 0 | 1 992 (2020-2025 : moins de 10 points) |
| Melodi `DS_ERFS_RETROPOLE` | 140 | 43 | 0 | 97 (nouvelles ventilations 2023-2024) |
| Melodi `DS_ERFS_NON_RETROPOLE` | 918 | 261 | 522 | 135 (2024 seul) |
| BDM `ODD-ERADICATION-PAUVRETE` | 60 | 49 | 2 | 9 (privation matérielle et sociale par âge et sexe, 2020-2024) |
| BDM `TCRED-CONDITIONSDEVIE-*` | 52 | 0 | 48 | 4 |

La privation matérielle et sociale d'ensemble (IRN 7, BDM 010594486, 2013-2024) et la satisfaction dans la vie (IRN 5) restent candidates ; les jeux SRCV « privations » et « confiance » de Melodi, refondus en 2020, n'ont que 5 ou 6 points.

### 12.5 Contrôle qualité des catalogues complets (14/10) et corrections
**Méthode** : tirage aléatoire de 20 séries candidates par dimension v0 et par source (moins quand la dimension en compte moins : démocratie et sécurité Melodi), sur le catalogue du 13/10 puis de nouveau sur le catalogue corrigé ; tirage de 20 séries écartées par motif d'exclusion (71 motifs : 48 BDM, 23 Melodi, soit environ 1 300 lignes lues) ; examen par regroupement des séries des familles sensibles (ODD, mortalité, enquête Emploi, SRCV, ERFS, comptes nationaux) ; examen des écarts au repérage de phase 1 ; simulation hors ligne (`--catalogage-seul`) avant chaque push, puis catalogage refait par le robot.

**Erreurs systématiques trouvées et corrigées** (tests ajoutés dans `tests/test_insee_catalogue.py` et `tests/test_insee_melodi.py` : 207 tests passent)

| Erreur | Exemple | Correction | Effet |
|---|---|---|---|
| Dimension du regroupement prise sur un mot du libellé du tableau | « Immatriculations de véhicules neufs » → `liens_bien_etre` (« tourisme » dans « Services, tourisme, transports ») | immatriculations (sauf part de véhicules électriques) et réseau routier hors champ | −25 candidates |
| Activité des transports | trafic RATP → `liens_bien_etre` (« voyageurs » lu « voyages ») ; fret, livraisons de carburants → `planete` | dataflow `TRANSPORTS` hors champ ; « voyages » en mot entier | −19 |
| Moyens administratifs pris pour des résultats | effectifs de la fonction publique (44), nombre d'établissements scolaires (26), indice de traitement (8) | hors champ | −78 |
| Emploi par branche | « Emploi salarié en fin de trimestre - Transports et entreposage (A17-HZ) » ; « Emploi au 31 décembre - Agriculture » | code NAF dans le libellé, grands secteurs : hors champ (on garde « Tous secteurs ») | −72 |
| Faux déclenchements de mots-clés | « titres d'OPC **détenus** par les APU » → `democratie` ; « prestations en **espèces** » → `planete` ; « Consommation intérieure de matière », « Productivité matières » → `niveau_de_vie` ; « cultures arables » → `education` | expressions précisées | 5 BDM et 4 Melodi passés en `planete`, 6 en `niveau_de_vie` |
| Consommation des ménages par fonction dispersée | poste « Santé » → `sante`, « Logement » → `logement_cadre_vie` | consommation des ménages → `niveau_de_vie` | 17 BDM, 82 Melodi re-tagués |
| Modalités de ventilation Melodi décidant de la dimension | « Actif occupé ; Ouvriers ; Taux d'utilisation d'un compte bancaire en ligne » → `travail` ; « … ; Fonction Publique Hospitalière ; Salaire… » → `sante` | parties de libellé qui ne sont que des modalités retirées avant le tagging | 60 séries TIC → `education`, 33 salaires → `travail` |
| Intentions d'achat comptées comme sécurité économique | « Intentions d'achats de voitures », « Dépenses d'aménagement du logement » | hors champ (on garde les opinions sur niveau de vie, situation financière, épargne, chômage, prix) | −10 |
| Détail de la dette publique | dépôts, crédits, titres, F6, F8, F12 de `DETTE-TRIM-APU-2020` | déclinaison technique (on garde ensemble, dette nette, total des passifs) | −13 |
| Barèmes | minimum garanti, plafond de la sécurité sociale | hors champ | −6 |
| **Faux négatifs D17** | PISA/PIRLS/TIMSS, participation électorale (présidentielle, législatives, européennes, régionales, départementales, municipales), état des masses d'eau, Gini du patrimoine, surpeuplement, formation des adultes, compétences numériques, habitats naturels | série courte mais pluriannuelle → `a_verifier` (D17) | +81 BDM, +152 Melodi |
| Recensement « dossier complet » | 1 144 décomptes de structure à trois millésimes (2012, 2017, 2023) | hors champ, sauf la suroccupation | +4 (suroccupation) |
| Zone partielle Melodi | « France métropolitaine hors île de France » (`FRANCE-FM_X_R11`, type FRANCE) | exclue à l'extraction et au catalogage | −14 |
| Fréquence trimestrielle Melodi | 1 698 séries « fréquence Q non retenue » | Q lu comme T ; comptes trimestriels `DS_CNT_*` écartés avec le motif « doublon des dataflows BDM CNT-2020-* » | motif corrigé |

Effet global : BDM 1 345 `oui` + 305 `a_verifier` (13/10) → **1 211 + 297** (223 sorties, 81 entrées, 23 dimensions changées) ; Melodi 5 427 + 1 027 → **5 413 + 1 183** (14 sorties, 156 entrées, 184 dimensions changées).

**Vérifications sans anomalie** : les 20 lignes tirées pour chacun des motifs d'exclusion examinés relèvent bien du motif (comptes par branche ou par produit, indices de prix, conjoncture des entreprises, balance des paiements, commerce extérieur, séries arrêtées remplacées par une nouvelle série, anciennes bases, secteurs institutionnels détaillés, COICOP et COFOG détaillés, démographie de contexte…) ; les séries candidates des familles ODD, mortalité, enquête Emploi, satisfaction SRCV et pauvreté ERFS sont candidates, et leurs séries écartées le sont pour un motif fondé (séries arrêtées remplacées, séries annuelles trop courtes, nouvelles ventilations commencées en 2022-2023).

**Points restés en l'état** (signalés, non corrigés) : quelques séries d'entreprises isolées en `a_verifier` (taux d'acceptation des crédits aux TPE, ODD 9) ; dépenses et recettes d'investissement des régions (`TCRED-ECONOMIE-DEP-REC`) ; dépenses des APU par fonction COFOG de premier niveau étiquetées selon la fonction (« Protection de l'environnement » → `planete`) ; dans SRCV, la tranche « 16 ans ou plus » (le total du jeu) est signalée comme ventilation par âge.

### 12.6 Comparaison avec le repérage de phase 1 (`insee_comparaison_phase1.csv`)
Sur les 1 063 lignes du repérage de phase 1 (858 BDM, 192 Melodi, 13 fichiers) :
- **704 séries BDM confirmées** (présentes et soumises aux règles) ; leur statut est le même qu'en phase 1 pour 340 d'entre elles. Les 364 écarts (« candidat différent ») s'expliquent par des règles plus fines qu'en phase 1 : `oui` → `non` 107 (51 séries arrêtées, 56 séries annuelles de moins de 10 points, surtout la satisfaction faible/moyenne/élevée et la privation matérielle par âge, 2020-2024) ; `oui` → `a_verifier` 131 (36 raccordements D16, 90 séries irrégulières ou pluriannuelles D17, 5 dimensions déduites du regroupement) ; `a_verifier` → `non` 40 (séries arrêtées) ; `non` → `a_verifier` 49 (27 raccordements, 12 dimensions déduites, 8 périmètres nationaux particuliers, 2 D17) ; `non` → `oui` 28 (14 indicateurs de moyens admis par D19, 14 séries écartées en phase 1 et retenues par les règles, notamment races locales menacées, exposition des animaux aux antibiotiques, logements vacants, PIB) ; `a_verifier` → `oui` 9 (dont 7 séries infra-annuelles).
- **144 séries BDM écartées par un filtre dur** : dernière valeur antérieure à 2020 (91 : TCRED de revenus Filosofi arrêtés en 2015, taux de pauvreté par âge, personnels de santé…), zone non nationale (32 : déclinaisons ODD des DOM), dernière mise à jour antérieure à 2020 (19), périodes inconnues (2). En phase 1, 85 d'entre elles étaient déjà `a_verifier` et 51 `non`.
- **10 séries BDM absentes** de la BDM d'aujourd'hui : 6 « Salaire annuel moyen - Ensemble/Femmes/Hommes - En EQTP - France/France métropolitaine » (001782649, 001782650, 001782872, 001782873, 001783057, 001783058 : le tableau TCRED correspondant ne les contient plus ; les salaires nets annuels moyens et leurs déciles sont dans `SALAIRES-ANNUELS`, périmètre `FM99_FR00`, candidats, et dans Melodi `DS_DERA_PRIVE_SERIES_LONGUES`) ; 4 taux de mortalité « Ensemble » par cause (maladies infectieuses et parasitaires 001733765, 001733766 ; sida et VIH 001734069, 001734070 : `TCRED-SANTE-CAUSES-DECES` ne contient plus que des séries par sexe, arrêtées en 2022, et de nouveaux taux standardisés depuis 2022 pour six groupes de causes ; pour le VIH, voir les découvertes de séropositivité, ODD 3, 2010-2024).
- **165 lignes Melodi confirmées** (144 codes `INDICATOR_SDG` de `DS_NAT_SDG` et 21 jeux) ; leurs 110 « candidats différents » ne sont pas significatifs : la phase 1 notait un statut par jeu ou par code, le robot un statut par série (plusieurs par code).
- **14 lignes Melodi non retrouvées** (toutes des codes `INDICATOR_SDG`) : 2 codes n'existent pas dans le `/range` de `DS_NAT_SDG` (3.i4b, 11.i2b : correspondances inférées en phase 1) ; 5 codes n'ont aucune série nationale (14.i5a à 14.i5d récifs coralliens, 15.i3b écosystèmes des DROM : outre-mer seulement) ; 7 codes ont une dernière valeur antérieure à 2020 (1.i4 taux d'effort net en logement : 2013 ; 2.i2a et 2.i2b surpoids et obésité des adultes : 2014-2019 ; 8.i5 accidents du travail : 2012-2019 ; 8.i6 intensité du travail : 2013-2019 ; 15.i3a écosystèmes peu anthropisés : 2012-2018 ; 15.i7b espèces les plus envahissantes : 2016).
- **4 jeux Melodi absents** du catalogue d'octobre 2026 : `DS_DEVDUR` (remplacé par `DS_NAT_SDG`), `DS_ERFS_INDIVIDU_SL`, `DS_ERFS_MENAGE_SL`, `DS_ERFS_CHAMP_CONST_SL` (remplacés par `DS_ERFS_RETROPOLE`, 1996-2024, et `DS_ERFS_NON_RETROPOLE`, 1975-2024).
- **9 jeux Melodi sans série au catalogue** : `DD_EEC_ANNUEL`, `DS_ENQPAT_TRANSM`, `DS_FILOSOFI_CC` (un seul millésime) ; `DS_ANTIPOL`, `DS_EACEI` (enquêtes auprès des entreprises) ; `DS_COMPTES_REGIONAUX` (comptes régionaux) ; `DS_FECONDITE`, `DS_MORTALITE` (jeux « dépréciés », sans observation : remplacés par `DS_NAISSANCES_FECONDITE_SERIES` et `DS_DECES_MORTALITE_SERIES`) ; `DS_ELECTORAL` (corps électoral à une date par scrutin, fréquence quotidienne : pas une série).
- **13 fichiers insee.fr** : hors robot (niveau 2) ; aucun n'est plus nécessaire pour les indicateurs de référence.
- **40 dimensions différentes** : 25 lignes d'aide publique au développement (hors champ de toute façon), 6 lignes eau potable et assainissement passées de `planete` à `logement_cadre_vie` (conforme à la règle R2 de la grille v1), 4 lignes Melodi dont la correspondance de code était inférée en phase 1 (le code désigne un autre indicateur), et 5 cas isolés (part des femmes parmi les victimes → `egalites`, auteurs poursuivables → `democratie`, CMU-C → `sante`, comptes bancaires → `niveau_de_vie`).
- **984 séries BDM candidates absentes du repérage de phase 1** (travail 402, niveau de vie 213, santé 177, logement 92, éducation 46, égalités 22, sécurité 17, planète 8, démocratie 7) : séries hors ODD que la phase 1 n'avait pas relevées une à une (enquête Emploi trimestrielle, demandeurs d'emploi, salaires, mortalité par âge, parc et construction de logements, comptes nationaux base 2020).

### 12.7 Indicateurs de référence dans le catalogue complet
Contrôle des 26 lignes de `docs/sources/insee_indicateurs_reference.csv` (les 5 lignes Melodi y ont été mises à jour le 14/10) :

| Indicateur | Identifiant au catalogue complet | Statut |
|---|---|---|
| IRN 1 Taux d'emploi 15-64 ans | BDM 010596081 (FR-D976, 1975-2024) | oui |
| IRN 2 Effort de recherche | BDM 010594852 (FE, 1996-2024) | oui, type moyen (D19) |
| IRN 3 Endettement public / ménages / SNF | BDM 010596873 / 010596874 / 010596875 (FE, 2010-2024) | oui |
| IRN 4 Espérance de vie en bonne santé F / H | BDM 010593268 / 010593269 (FE, 2004-2024) | oui (ventilation sexe) |
| IRN 5 Satisfaction dans la vie | BDM 010593281 (FM, 2010-2024) | oui |
| IRN 6 Inégalités de revenus (100-S80)/S20 | BDM 010594680 (FM, 1996-2023) | oui |
| IRN 7 Privation matérielle et sociale | BDM 010594486 (FM, 2013-2024) | a_verifier (raccordement D16) |
| IRN 8 Sorties précoces | BDM 010594746 (FR-D976, 2006-2024) | oui |
| IRN 9 Empreinte carbone | BDM 010595988 / 010595981 (FM_D99_D978, 1995-2024) | oui (périmètre Kyoto) |
| IRN 10 Artificialisation des sols | BDM 010596134 (FM, 1982-2023) | oui |
| Taux de pauvreté monétaire 60 % | BDM 010594446 (FM, 2010-2023) ; Melodi `DS_ERFS_RETROPOLE?…ERFS_MEASURE=PR_MD60…` (1996-2024) | oui |
| Niveau de vie médian | Melodi `DS_ERFS_RETROPOLE?AGE=_T&EMPSTA_ENQ=_T&ERFS_MEASURE=MED_SL&GEO=FRANCE-FM&MUN_DENSITY_LEVEL=_T&TPH=_T` (1996-2024) | oui |
| Rapport interdécile D9/D1 | BDM 010594681 (FM, 2010-2023) | oui |
| Indice de Gini du niveau de vie | Melodi `DS_ERFS_RETROPOLE?…ERFS_MEASURE=GI_SL…` (1996-2024) ; `DS_ERFS_NON_RETROPOLE` (1975-2024) ; **pas d'idbank BDM** | oui |
| Taux de chômage BIT | BDM 001787711 (FM, 1982-2025) oui ; 001787717 (FR-D976, 2014-2025) a_verifier ; 001688527 (trimestriel) oui | oui |
| Espérance de vie à la naissance F / H | BDM 001686961 / 001686956 (FE, 1994-2025) | oui |
| PIB par habitant en volume | BDM 011779993 (FE, 1949-2025) | oui |
| Dépense de consommation des ménages | Melodi `DD_CNA_AGREGATS` (`EXPENDITURE=CPDEP`, `STO=P31`, `REF_SECTOR=S14`, 1959-2025) ; « par habitant » à calculer | oui |
| Taux d'épargne des ménages | Melodi `DD_CNA_AGREGATS` (`STO=_TEM`, `REF_SECTOR=S14`, 1949-2025) | oui |
| Satisfaction dans la vie (SRCV) | Melodi `DS_SRCV_SATISFACTION` (`SRCV_MEASURE=VIESATISF`, 16 ans ou plus, FRANCE-FM, 2010-2025) | oui |
| Sentiment d'insécurité | hors INSEE (SSMSI, collecté par M04) | sans objet |
| Part des ménages en surpeuplement | BDM 010596142 (FM, 2013 et 2020) ; Melodi recensement, suroccupation (2012, 2017, 2023) | a_verifier (D17) |
| Taux d'effort logement | BDM 010594494 (FM, 2013 seulement) | écarté par filtre dur (dernière valeur 2013) ; alternative Eurostat `ilc_lvho07a` |

Les requêtes Melodi complètes figurent dans le CSV et dans la colonne `serie_id` des catalogues.

### 12.8 Doublons connus avec d'autres sources et entre voies INSEE
- **Indicateurs territoriaux de développement durable (ITDD)**, produit commun INSEE–SDES : aussi collectés par M04 ; à dédoublonner dans la long-list (une ligne, sources alternatives).
- **Indice de Gini du niveau de vie** : dans Melodi (ERFS) seulement, pas d'idbank BDM ; Eurostat publie un Gini EU-SILC (`ilc_di12`) tiré d'une autre enquête (SRCV) : les deux séries diffèrent, la fiche indicateur en retiendra une.
- **Séries SRCV** (satisfaction, privation matérielle et sociale, confiance, surpeuplement, taux d'effort) : la même enquête alimente EU-SILC ; Eurostat les publie en séries harmonisées (`ilc_pw01`, `ilc_lvho05a`, `ilc_lvho07a`, tables de privation matérielle et sociale) : la fiche indicateur dira laquelle est retenue (charte §3.5).
- **Comptes trimestriels** : Melodi `DS_CNT_*` = BDM `CNT-2020-*` (écartés côté Melodi) ; **comptes annuels** : BDM `CNA-2020-*` et Melodi `DD_CNA_*` se recouvrent (mêmes agrégats sous deux identifiants).
- **ODD** : BDM `ODD-*` (idbanks) et Melodi `DS_NAT_SDG` (codes `INDICATOR_SDG`) publient les mêmes indicateurs ; les deux sont au catalogue.
- **Mortalité** : BDM `DECES-MORTALITE` et Melodi `DS_DECES_MORTALITE_SERIES` ; **enquête Emploi** : BDM `CHOMAGE-TRIM-NATIONAL`, `EMPLOI-BIT-TRIM` (trimestriel) et Melodi `DD_EEC_SERIES` (annuel) ; **satisfaction** : BDM 010593281 et Melodi `DS_SRCV_SATISFACTION`.

### 12.9 Exploitation : relance mensuelle, séries écartées
- **Relance mensuelle** : `scripts/collecte_insee.options` contient `--cycle mois --budget-minutes 255`. Le premier passage d'un mois civil (déclenché par le robot mensuel de `main` le 1er à 04:17 UTC une fois la branche fusionnée, ou par un push sur `scripts/`/`src/` d'une branche `m01-*`, ou par `python scripts/actions.py lancer --branche <b> --cible collecte_insee.py`) lance un nouveau cycle `mois-AAAA-MM` complet (environ 70 min) ; s'il est interrompu par le budget, le passage suivant le reprend ; un cycle terminé n'est pas recommencé dans le mois (catalogage seul, environ 1 min). Forcer une collecte : `--nouveau` ou un autre `--cycle` dans le fichier d'options.
- **Séries écartées** : par une règle → `catalogues/insee_*_catalogue_non.csv.gz` (motif dans `commentaire`) ; par un filtre dur (fréquence, zone, dernière période, aucune valeur, doublon trimestriel) → seulement dans les inventaires `insee_*_inventaire.csv.gz`, comptées par motif dans `insee_bilan.json` ; jeux Melodi écartés d'emblée → `insee_melodi_jeux.csv` (colonnes `statut`, `remarque`).
- **Refaire le catalogage hors ligne** : `python scripts/collecte_insee.py --catalogage-seul` (environ 1 min dans le bac à sable) ; ne pas commiter les catalogues ainsi produits si un run « Collecte » est en cours sur la branche.

### 12.10 Limites
- Périodes Melodi : calculées sur les observations nationales extraites (exactes) ; périodes BDM infra-annuelles : première et dernière observation seulement (le nombre d'années avec valeur n'est pas compté).
- Les jeux Melodi d'un seul millésime (recensement détaillé 2023, Filosofi 2023, enquête Emploi annuelle 2025…) ne sont pas extraits : ils ne forment pas de série temporelle.
- Le tagging par mots-clés reste approximatif (exemples restants au §12.5) ; `dimension_v0` est une orientation pour M05, pas un rattachement définitif ; le passage à la grille v1 est fait par la long-list.
- Les ventilations sont gardées (D21) : 4 655 des 8 104 séries candidates sont des déclinaisons (sexe, âge, PCS, diplôme…) ; la long-list devra regrouper chaque famille autour de sa série d'ensemble.
- Les comptes nationaux restent nombreux (2 273 candidates) malgré les règles de bruit.
- Deux dataflows BDM (`IPPI-2005`, `IPPI-2010`, prix de production, hors champ) ne renvoient aucune série au découpage : non examiné plus avant.
- Les séries SRCV de Melodi refondues en 2020 (privations, confiance) et les séries « France hors Mayotte » commencées en 2022 sont écartées faute de 10 points : elles redeviendront candidates d'elles-mêmes au fil des millésimes.

## 13. Sources consultées
- Catalogue des API de l'INSEE : https://www.insee.fr/fr/information/8184146 (mise à jour 12/06/2025)
- Service web SDMX : https://www.insee.fr/fr/information/2862759 ; guide v2.1 et v2.2 (PDF)
- Fiches data.gouv.fr : https://www.data.gouv.fr/fr/dataservices/api-melodi/ ; https://www.data.gouv.fr/dataservices/api-bdm
- Modalités de connexion (Sirene) : https://static.insee.fr/api-sirene/Insee_API_publique_modalites_connexion.pdf
- Paquet R `melodi` : https://github.com/InseeFrLab/melodi ; paquet R `insee` : https://github.com/pyr-opendatafr/R-Insee-Data ; pynsee 0.2.5 (PyPI) et https://github.com/InseeFrLab/pynsee
- Indicateurs de richesse nationale : https://www.insee.fr/fr/statistiques/3281778 et ses 10 sous-pages (3281596 … 3281689)
- Indicateurs ODD : https://www.insee.fr/fr/statistiques/2654964 et ses 17 sous-pages
- Chiffres-clés niveau de vie : https://www.insee.fr/fr/statistiques/2491918 ; séries longues ERFS : https://www.insee.fr/fr/statistiques/8731524
- Conditions de réutilisation : https://www.insee.fr/fr/information/2381855
- SSMSI (sentiment d'insécurité) : https://www.data.gouv.fr/datasets/62029493ff5c2e6d510b42b6
