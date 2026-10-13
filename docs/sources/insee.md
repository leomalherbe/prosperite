# Source INSEE — voies d'accès et indicateurs repérés

Fiche documentaire de la mission M01, phase 1 (tâches A1 et A4). Rédigée le 13 octobre 2026 par l'agent de mission M01.
Branche `m01-insee`. À valider par la session mère avant la phase 2 (modules Python, moissonnage, GitHub Actions).

Conventions : « vérifié » = constaté le 2026-10-13 en lisant la réponse de l'API ; « non trouvé » = information introuvable ; aucune valeur n'est inventée. Les codes de zone (`FE`, `FM`, `FR-D976`, …) sont ceux de l'attribut `REF_AREA` de la BDM (voir §2.6).

---

## 1. Synthèse des voies d'accès

| Voie | URL de base | Authentification aujourd'hui | Formats | Quota | Lister le catalogue | Obtenir une série complète | Fixture réelle |
|---|---|---|---|---|---|---|---|
| **BDM, service web SDMX** | `https://bdm.insee.fr/series/sdmx/` | **Aucune** (vérifié) | SDMX-ML 2.1 (XML) | non documenté (pynsee s'impose 30 appels/min par prudence) ; 400 idbanks par requête, 2 000 séries par requête de dataflow | `/dataflow` puis `/data/<dataflow>?detail=nodata` | `/data/SERIES_BDM/<idbank>` | oui (reconstituée, §10) |
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
1. `GET /dataflow` : un `str:Dataflow` par regroupement, avec `com:Name` (fr, en), une annotation URL vers la page insee.fr et une annotation « Nombre de séries : N ». La réponse complète n'a pas pu être lue (outil tronqué après 94 dataflows, de `BALANCE-PAIEMENTS` à `ICA-2010-IND-CONS`). L'instantané du paquet R `insee` (août 2024) en compte **199** ; depuis, sont apparus au moins les flux base 2020 (`CNA-2020-*`, `CNT-2020-*`, `CONSO-MENAGES-2020`, `DETTE-TRIM-APU-2020`, `IC-PROD-CONS-2021`). Il n'existe **pas** de `CNA-2020-RDB` (revenu et pouvoir d'achat base 2020) parmi les flux lus.
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
- Requêtes par clé de dataflow (`/data/CNA-2020-CSI/A..S14.......`, `/data/CNA-2014-CSI/<clé complète>`) : **erreur client** via l'outil de lecture ; cause non élucidée (404 SDMX ou refus de l'outil). À tester depuis GitHub Actions en phase 2.
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
| Fichier | Voie | Provenance |
|---|---|---|
| `bdm/bdm_serie_001688527_last5_2026-10-13.xml` | BDM | **reconstituée** : réponse lue le 2026-10-13, attributs extraits un à un (l'outil ne recopie pas le XML brut) |
| `bdm/bdm_serie_010593281_2026-10-13.xml` | BDM | reconstituée, série complète, valeurs recoupées par une 2e requête |
| `bdm/bdm_dataflow_ODD-ERADICATION-PAUVRETE_2026-10-13.xml` | BDM | reconstituée (message de structure) |
| `bdm/bdm_nodata_ODD-ERADICATION-PAUVRETE_2026-10-13.csv` | BDM | extraction CSV de la réponse `detail=nodata` (65 séries) |
| `bdm/bdm_dataflows_extrait_2026-10-13.csv` | BDM | 93 premiers dataflows de la liste vivante |
| `melodi/*.json`, `melodi/*.xlsx`, `melodi/*.txt` | Melodi | **réponses réelles** enregistrées par l'INSEE (cassettes vcr du paquet R `melodi`, dépôt InseeFrLab/melodi, 2026-01-06 à 2026-07-17) ; correspondance URI ↔ fichier dans `melodi/provenance_melodi.csv` |
| `metadonnees/rdf_sparql_concept_c1653_2026-10-13.csv` | Métadonnées (RMéS) | réponse SPARQL de `rdf.insee.fr` (lue le 2026-10-13) |
| — | Données locales | aucune (voir §4) |
| — | Fichiers insee.fr | aucune ; XLSX réel de Melodi utilisable pour le lecteur XLSX |

## 11. Points à trancher ou vérifier avant la phase 2
1. **Voies retenues** : BDM `bdm.insee.fr` (sans clé) + Melodi (sans clé) ; Données locales abandonnée ; fichiers insee.fr limités au fichier Chiffres-clés du Gini (robots.txt : à valider).
2. **Fixtures BDM reconstituées** : les remplacer par de vraies réponses enregistrées lors du premier passage sur GitHub Actions.
3. **Requêtes par clé de dataflow** à tester depuis Actions (échec via l'outil).
4. **Série longue 2000-2009** : beaucoup de séries ODD commencent en 2010 ; prévoir le raccord avec Melodi (ERFS, EEC) ou des séries BDM longues.
5. **Choix de zone** : `FM` (métropole) pour les enquêtes ménages, `FR-D976` pour l'enquête Emploi, `FE` pour la démographie et les comptes : il faudra accepter des champs différents selon les indicateurs (champ `geo` de la fiche).

## 12. Sources consultées
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
