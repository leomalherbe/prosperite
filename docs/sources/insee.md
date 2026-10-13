# Source INSEE — voies d'accès et indicateurs repérés

Fiche documentaire de la mission M01 : phase 1 (tâches A1 et A4), complétée en phase 2 (modules, robot de collecte, catalogue : §2.3, §2.7, §10, §11 et **§12**). Rédigée le 13 octobre 2026 par les agents de mission M01.
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
4. **Fichiers** : l'indice de Gini du niveau de vie n'est que dans un fichier Chiffres-clés.
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
| Niveau de vie médian | API (code de mesure à lire) | Melodi | `DS_ERFS_INDIVIDU_SL` | FM | 1996-2022 | niveau_de_vie |
| Rapport interdécile D9/D1 | API | BDM | 010594681 | FM | 2010-2023 | egalites |
| Indice de Gini (niveau de vie) | **non disponible par API** | fichier Chiffres-clés 2491918 ; alternative Eurostat `ilc_di12` | URL du fichier | FM | jusqu'en 2024 | egalites |
| Taux de chômage BIT (moyenne annuelle) | API | BDM | 001787717 (FR-D976) ; 001787711 (FM, 1982-) ; 001688527 (trimestriel) | FR-D976 | 2014-2025 | travail |
| Taux d'emploi 15-64 ans | API | BDM | 010596081 | FR-D976 | 1975-2024 | travail |
| Espérance de vie à la naissance F / H | API | BDM | 001686961 / 001686956 | FE | 1994-2025 | sante |
| PIB par habitant en volume | API | BDM | 011779993 (base 2020) | FE | 1949-2025 | niveau_de_vie |
| Dépense de consommation des ménages par habitant | à calculer | Melodi `DD_CNA_CONSO_MENAGES_COICOP` / population | — | FE | 1949-2024 | niveau_de_vie |
| Taux d'épargne des ménages | **non trouvé** dans BDM ; Melodi `DD_CNA_TEE` à confirmer ; alternative Eurostat `nasa_10_ki` | — | — | FE | — | niveau_de_vie |
| Satisfaction dans la vie (SRCV) | API | Melodi `DS_SRCV_SATISFACTION` / BDM 010593281 | — | FM | 2010-2024 | liens_bien_etre |
| Sentiment d'insécurité (CVS/VRS) | **non disponible à l'INSEE par API** | SSMSI (data.gouv.fr `62029493ff5c2e6d510b42b6` ; enquête VRS depuis 2022) | — | — | — | securite_confiance |
| Part des ménages en surpeuplement | API mais 2 points (2013, 2020) | BDM 010596142 ; alternative Eurostat `ilc_lvho05a` | — | FM | 2013-2020 | logement_cadre_vie |
| Taux d'effort logement | API mais 1 point (2013) | BDM 010594494 ; alternative Eurostat `ilc_lvho07a` | — | FM | 2013 | logement_cadre_vie |

Toutes les valeurs « période » des lignes BDM ont été lues en direct le 2026-10-13 (première observation renvoyée, dernière valeur non manquante).

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

## 11. Points à trancher ou vérifier (état après la phase 2)
1. **Voies retenues** (D14) : BDM `bdm.insee.fr` + Melodi, sans clé — confirmé par le robot (aucune authentification, aucun refus de débit pendant l'essai) ; Données locales abandonnée ; fichiers insee.fr limités au fichier Chiffres-clés du Gini (non moissonné par le robot).
2. ~~Fixtures BDM reconstituées~~ : **fait**, remplacées par les réponses brutes (§10).
3. ~~Requêtes par clé de dataflow~~ : **fonctionnent** depuis Actions (§2.7).
4. **Série longue 2000-2009** (D16) : beaucoup de séries ODD commencent en 2010 ; elles sont `a_verifier` au catalogue quand elles commencent après 2010, avec le motif « raccordement à prévoir » ; le raccord avec Melodi (ERFS, EEC) reste à faire en M05.
5. **Choix de zone** (D15) : `FM` (métropole) pour les enquêtes ménages, `FR-D976` pour l'enquête Emploi, `FE` pour la démographie et les comptes ; Melodi ajoute `FRANCE-F`, `FRANCE-FM`, `FRANCE-F_X_D976` : la colonne `geo` du catalogue les garde distincts.
6. **Comptes nationaux** : les règles de bruit (§12.3) ne gardent que les agrégats (économie totale, APU, ménages, ISBLSM ; premier niveau des nomenclatures). À relire par la session mère : la liste des opérations gardées et le traitement des dépenses publiques par fonction (gardées au 1er niveau COFOG, `type moyen`, D19).

## 12. Catalogue des séries candidates (phase 2, robot de collecte)

### 12.1 Méthode
`scripts/collecte_insee.py`, exécuté par GitHub Actions (workflow « Collecte »), en étapes reprenables d'un passage à l'autre (état dans `catalogues/insee_etat/`) :
1. **BDM** : liste des dataflows et des listes de codes ; pour chaque dataflow (sauf `SERIES_BDM`), toutes les séries par `detail=nodata` avec découpage automatique au-delà de 2 000 séries (§2.7) ; pour les séries nationales de fréquence A/S/T/B/M mises à jour depuis 2020 : lecture complète des séries annuelles (première et dernière valeur non manquante, nombre d'années avec valeur depuis 2000), première et dernière observation des séries infra-annuelles.
2. **Melodi** : catalogue `/catalog/all` ; jeux écartés d'emblée (motif tracé dans `insee_melodi_jeux.csv`) : statistiques d'entreprises, équipements, prénoms, comptes par branche ou par produit, comptes régionaux, jeux sans niveau national, jeux d'**un seul millésime** ou terminés avant 2020 ; pour les autres, `/range` puis extraction du **seul niveau national** (`/data` filtré sur chaque valeur nationale de `GEO`, ou fichier ZIP complet si le jeu est entièrement national et dépasse 100 000 lignes). Une série Melodi = une combinaison de modalités ; son identifiant est la requête qui la relit (`<jeu>?DIM=code&…`).
3. **Échantillons** de réponses brutes (§10), **inventaires** bruts (`catalogues/insee_bdm_inventaire.csv.gz`, `insee_melodi_inventaire.csv.gz`), puis **catalogage hors ligne** (`--catalogage-seul`, exécutable dans le bac à sable sur les inventaires).

Options : `scripts/collecte_insee.options` (`--cycle mois --budget-minutes 255`). Avec `--cycle`, un cycle terminé n'est pas recommencé : un nouveau passage refait seulement le catalogage avec les règles du moment ; le mois suivant (ou un autre identifiant de cycle) relance une collecte complète.

### 12.2 Fichiers produits (`catalogues/`)
| Fichier | Contenu |
|---|---|
| `insee_bdm_catalogue.csv`, `insee_melodi_catalogue.csv` | séries **candidates** (`candidat` = `oui` ou `a_verifier`) : colonnes de la charte §5.3 (`source, serie_id, libelle, unite, frequence, geo, premiere_periode, derniere_periode, derniere_maj, theme_source, dimension_v0, candidat, commentaire`) + `agregable, ventilation, geo_libelle, nb_annees_depuis_2000, statut_derniere_valeur, theme_libelle, url_api` |
| `insee_bdm_catalogue_non.csv.gz`, `insee_melodi_catalogue_non.csv.gz` | séries écartées par une règle (`candidat = non`), même colonnes, **motif dans `commentaire`** (traçabilité, charte §3.6) |
| `insee_bdm_inventaire.csv.gz`, `insee_melodi_inventaire.csv.gz` | toutes les séries listées (BDM) ou nationales (Melodi), avec leurs dimensions, avant tout filtre |
| `insee_bdm_dataflows.csv`, `insee_melodi_jeux.csv`, `insee_bdm_zones.csv` | traitement par dataflow / jeu (statut, motif d'exclusion, nombre de séries, de candidates) ; codes de zone rencontrés |
| `insee_bilan.json` | chiffres clés (séries listées, exclusions par motif, candidats par dimension) |
| `insee_comparaison_phase1.csv` | sort de chacune des 1 063 lignes du repérage de phase 1 (confirmée, écartée par un filtre et pourquoi, absente) |

### 12.3 Règles (`src/sources/insee_catalogue.py`)
- **Filtres durs** (série absente des catalogues, comptée dans les exclusions du bilan) : fréquence A, S, T, B ou M ; zone nationale (FE, FM, FR-D976 et autres périmètres nationaux, gardés distincts — D15) ; dernière valeur non manquante ≥ 2020 (pour la BDM, une série mise à jour pour la dernière fois avant 2020 ne peut pas l'avoir : ses périodes ne sont pas lues).
- **`candidat = non`** (motif en commentaire) : hors champ (statistiques d'entreprises, prix de production, prix agricoles et de détail par produit, indices de prix et déflateurs, coût du travail, conjoncture des entreprises, commerce extérieur, tourisme vu de l'offre, trafic de voyageurs, barèmes, aide publique au développement) ; **déclinaisons techniques** lues dans les codes de dimensions (sous-secteurs institutionnels et sociétés, contreparties, branches, produits détaillés, COFOG de niveau 2, instruments financiers et actifs détaillés sauf les logements, valorisations et transformations techniques ; dans les comptes nationaux, opérations hors liste des agrégats) ; séries arrêtées ; anciennes bases ; démographie de contexte ; aucune règle de dimension ; moins de 10 points depuis 2000 quand la série commence après 2010.
- **`candidat = a_verifier`** : première période après 2010 mais au moins 10 points possibles (raccordement D16) ; moins de 10 années avec valeur (série irrégulière, D17) ; dimension déduite du seul regroupement ; zone non renseignée.
- **`candidat = oui`** : les autres ; drapeaux en commentaire : `type moyen (D19)`, `infra-annuelle : agrégation annuelle à prévoir`, `ventilation : sexe;age;…` (D21, colonne `ventilation`).
- **Tagging `dimension_v0`** : règles de mots-clés ordonnées sur le libellé (grille v0, charte §4), après retrait des expressions comptables (« Emploi ou débit », « actifs financiers »…) ; à défaut, dimension du regroupement ODD.
- **Validation des règles** (phase 2) : application à l'instantané de 158 166 séries BDM du paquet R `insee` (août 2024 ; 110 302 séries nationales A/S/T/B/M) et aux inventaires réels de l'essai ; examen par regroupement des séries qui changent de statut. Corrections : faux négatif « au cours des … derniers mois » (indicateurs ODD d'usage d'internet écartés comme « cours de bourse »), « pour 100 000 habitants » classé en démographie, densité carcérale non classée ; bruit : 8 699 comptes détaillés des APU et 16 398 séries d'un seul millésime de l'enquête Emploi annuelle étaient `oui` dans l'essai Melodi. Sur l'instantané 2024, `oui` passe de 20 584 à 2 489 sans qu'aucune série des regroupements ODD, mortalité, enquête Emploi ou conditions de vie ne change de statut à tort.

### 12.4 Chiffres
- **Essai réduit** (run 38405848499, 13/10, 20 premiers dataflows et 20 premiers jeux Melodi, règles de l'époque) : 31 888 séries BDM listées (comptes en base 2010 et 2014, balance des paiements, chômage trimestriel), 4 030 au catalogue, 104 `oui` (chômage) ; 9 jeux Melodi traités, 61 909 séries nationales. Ces chiffres ne sont pas représentatifs : l'ordre alphabétique faisait passer d'abord les anciennes bases des comptes nationaux.
- **Passage complet** : run **38412716221** lancé le 13/10 à 14:22 UTC (tous les dataflows, tous les jeux Melodi, 255 min) ; un run en attente (38415610569) le reprendra s'il n'a pas fini, ou refera le catalogage avec les règles finales. **Les chiffres du passage complet (séries listées, retenues, candidates par dimension) sont dans `catalogues/insee_bilan.json` une fois ces runs terminés** ; ils seront reportés ici et dans le compte rendu de mission.

### 12.5 Limites
- Périodes Melodi : calculées sur les observations nationales extraites (exactes) ; périodes BDM infra-annuelles : première et dernière observation seulement (le nombre d'années avec valeur n'est pas compté).
- Les jeux Melodi d'un seul millésime (recensement détaillé 2023, Filosofi 2023, enquête Emploi annuelle 2025…) ne sont pas extraits : ils ne forment pas de série temporelle.
- Le tagging par mots-clés reste approximatif sur les libellés composés de Melodi (concaténation des modalités) ; `dimension_v0` est une orientation pour M03/M05, pas un rattachement définitif.
- Les ventilations sont gardées (D21) : l'enquête Emploi en séries longues compte à elle seule environ 1 700 séries candidates (sexe × âge × PCS × diplôme).

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
