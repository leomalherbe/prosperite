# Fiche source — Eurostat

Rédigée par l'agent de la mission M02 (phase 1), le 2026-10-13 ; complétée en phase 2 le même jour (sections 6 à 10 : pièges constatés par le robot, dossiers du TOC, fixtures réelles, statut des séries des prototypes, **catalogues**). Les informations de phase 1 ont été lues dans la documentation officielle d'Eurostat ou dans des réponses réelles obtenues par l'outil de lecture de page (WebFetch) ; celles de phase 2 proviennent des passages du robot de collecte (GitHub Actions) et de ses journaux (`journaux/`). Ce qui n'a pas pu être vérifié est signalé « non vérifié » ou « non trouvé ».

## 1. Identité de la source

| Élément | Valeur |
|---|---|
| Organisme | Eurostat, office statistique de l'Union européenne (identifiant d'agence SDMX : `ESTAT`) |
| Base de diffusion | Base de données Eurostat (« Eurostat database »), parcourue par le *Data Browser* : `https://ec.europa.eu/eurostat/databrowser/` |
| Racine des API | `https://ec.europa.eu/eurostat/api/dissemination` |
| Jeux Comext / Prodcom (préfixe `DS-`) | `https://ec.europa.eu/eurostat/api/comext/dissemination` — hors périmètre du projet |
| Niveau (charte §3.5) | **Niveau 1** (API) |
| Clé d'API / authentification | **Aucune.** La documentation parle d'un « free of charge programmatic access » sans clé ni compte. L'API Statistics accepte le CORS (appel direct depuis un navigateur possible). |
| Langues | `en`, `fr`, `de` (libellés des jeux, des dimensions et des modalités) |
| Mise à jour | Les jeux sont mis à jour **deux fois par jour, à 11 h 00 et 23 h 00 (heure de Bruxelles)** s'il y a de nouvelles données ou un changement de structure. |
| Historique des versions | **Aucun** : seule la dernière version d'une observation est diffusée (« There is no history available on data »). D'où la nécessité de nos millésimes figés (`donnees/millesimes/`). |
| Documentation | Introduction : `https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-introduction` ; lignes directrices détaillées : `…/api-data-access/api-detailed-guidelines` (sous-pages `api-statistics`, `sdmx2-1/data-query`, `sdmx2-1/structure-queries`, `catalogue-api/toc`, `asynchronous-api`) ; FAQ : `…/api-data-access/api-faq` ; format TSV : `…/api-faq/tsv-format` ; spécification OpenAPI : `https://ec.europa.eu/eurostat/api/dissemination/swagger-ui/sdmx-rest.yaml` ; WADL du catalogue : `https://ec.europa.eu/eurostat/api/dissemination/catalogue/catalogue.wadl` |

### Licence et mention de la source
- Réutilisation libre, y compris commerciale, sans licence écrite, selon la politique de réutilisation de la Commission (décision 2011/833/UE du 12 décembre 2011) ; contenu éditorial sous **Creative Commons Attribution 4.0 International** (page `https://ec.europa.eu/eurostat/help/copyright-notice`).
- **Mention obligatoire** pour un jeu de données : « Source: [DOI du jeu Eurostat], [date d'accès] » ; pour un autre produit : « Source: Eurostat, [titre], [lien], [date d'accès] ». Toute modification des données doit être signalée à l'utilisateur final.
- Exceptions : données de pays hors UE/AELE/candidats et données de tiers (réutilisation non commerciale seulement). Sans incidence pour le projet (France, usage non commercial).
- Le DOI de chaque jeu figure dans l'annotation `DISSEMINATION_DOI_XML` de la réponse JSON-stat (voir §4.4) : le pipeline pourra le recopier dans les fiches indicateurs.

## 2. Les quatre voies d'accès et leur usage dans le projet

| Voie | Point d'entrée | Ce qu'elle donne | Usage dans le projet |
|---|---|---|---|
| **1. Catalogue (TOC)** | `…/catalogue/toc/txt?lang=en` | Liste de tous les dossiers, jeux (`dataset`) et tableaux (`table`) avec dates et hiérarchie | Base du **niveau 1** du catalogue (jeux candidats) |
| **2. API Statistics 1.0** | `…/statistics/1.0/data/{code}?geo=FR&lang=fr&…` | Données filtrées en **JSON-stat 2.0** | Vérification et lecture des **séries** (niveau 2) ; collecte des millésimes |
| **3. SDMX 2.1** | `…/sdmx/2.1/dataflow/…`, `…/datastructure/…`, `…/data/…` | Structure des jeux (dimensions, listes de codes, combinaisons existantes) et données (SDMX-CSV, TSV, JSON-stat) | Description d'un jeu (dimensions et modalités) pour construire les combinaisons par défaut |
| **4. Téléchargement en masse** | `…/sdmx/2.1/data/{CODE}?format=TSV&compressed=true` | Jeu complet, TSV compressé gzip | Jeux volumineux, ou lecture d'un jeu entier en une requête |

### 2.1 Catalogue — table des matières (TOC)

Points d'entrée (WADL du catalogue, vérifié) :
- `https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en` (texte tabulé, une langue par requête : `en`, `fr`, `de`) ;
- `…/catalogue/toc/xml` (XML multilingue, schéma `…/catalogue/toc/TableOfContent.xsd`) ; contient en plus sous-titres, descriptions courtes, liens vers les métadonnées ESMS et liens de téléchargement TSV/SDMX ;
- `…/catalogue/toc/legacy_txt?lang=…` et `…/catalogue/toc/legacy_xml` (anciens formats, non examinés).

**Format TXT** (vérifié sur des lignes réelles, voir fixture `tests/fixtures/eurostat/toc_extrait_en.txt`) :
- séparateur tabulation ; champs texte entre guillemets doubles ; le champ `values` (nombre de valeurs) est un entier **sans** guillemets ;
- en-tête (identique en `lang=fr`, non traduit) : `"title"  "code"  "type"  "last update of data"  "last table structure change"  "data start"  "data end"  "values"` ;
- **hiérarchie = indentation de 4 espaces par niveau en tête du titre** (à l'intérieur des guillemets) : niveau 0 `"Database by themes"`, niveau 1 `"    General and regional statistics"`, etc. ;
- `type` ∈ `folder` (dossier), `dataset` (jeu de données complet), `table` (tableau prédéfini) ;
- pour un dossier, les champs de date et `values` valent `" "` (un espace entre guillemets) ;
- dates de mise à jour au format `JJ.MM.AAAA` (ex. `02.10.2026`) ; début/fin des données au format de la fréquence (`1991`, `1991-Q1`, `1991-01`) ;
- un **tableau peut être rangé sous un jeu** (ex. `teibs020` indenté sous le jeu `ei_bssi_m_r2`) : la hiérarchie mêle dossiers et jeux ;
- un même code peut apparaître à **plusieurs endroits** de l'arborescence (documentation : « can be classified at different places ») : dédoublonner par `code` en conservant tous les chemins.

Exemple réel (13/10/2026) :
```
"Database by themes"	"data"	"folder"	" "	" "	" "	" "	" "
"    General and regional statistics"	"general"	"folder"	" "	" "	" "	" "	" "
"                    Economic sentiment and confidence indicators by sector - monthly data"	"ei_bssi_m_r2"	"dataset"	"29.09.2026"	"29.09.2026"	"1980-01"	"2026-09"	142312
```

Autres services du catalogue (WADL) : `…/catalogue/metabase.txt.gz` (« metabase » : liste compressée des jeux, dimensions et codes ; **vérifié en phase 2** : gzip de 4,1 Mo, 34,1 Mo décompressé, 1 344 860 lignes tabulées `jeu⇥dimension⇥modalité` couvrant 7 600 jeux, sans libellés ni indication des pays renseignés — extrait en fixture `metabase_extrait.txt` ; le robot ne s'en sert pas, la structure de chaque jeu candidat étant lue par `dataflow…referencepartial`, qui ne garde que les modalités présentes) ; `…/catalogue/rss/{langue}/statistics-update.rss` (mises à jour) ; `…/catalogue/dcat/{agence}{/type}` (DCAT-RDF) ; `…/catalogue/jsonld/{agence}/{id}/{version}` ; **`…/catalogue/relations/{agence}/{id}/{version}`** — vérifié : `relations/ESTAT/SDG_08_10/1.0?lang=en` renvoie `{"derived": {}, "source": {"nama_10_pc": "Gross domestic product (GDP) and main components per capita - annual data"}}`, soit le **jeu source** d'une vue SDG.

### 2.2 API Statistics 1.0 (JSON-stat 2.0)

Modèle d'URL : `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{code}?{paramètres}`. Exemple vérifié : `…/statistics/1.0/data/sdg_08_10?geo=FR&lang=fr&time=2022`.

| Paramètre | Valeurs | Remarques (documentation officielle, page « API Statistics ») |
|---|---|---|
| `format` | `JSON` | Seule valeur possible, facultatif |
| `lang` | `EN`, `FR`, `DE` | Défaut `EN`. Le projet utilise `lang=fr` |
| `{dimension}={code}` | ex. `geo=FR`, `unit=PC`, `sex=T`, `age=Y16-64` | Codes et valeurs insensibles à la casse ; ordre libre ; **plusieurs valeurs = paramètre répété** (`sex=M&sex=F`) ; toute dimension du jeu est filtrable |
| `time` (ou `time_period`) | ex. `time=2022` | Période(s) précise(s), répétable |
| `sinceTimePeriod` / `untilTimePeriod` | ex. `sinceTimePeriod=2000` | Bornes inférieure / supérieure ; seule combinaison de paramètres temporels autorisée |
| `lastTimePeriod` | entier N | « a numeric value counting down until the TIME_PERIOD dimension values are included » : les N dernières périodes. Vérifié en phase 2 (fixture `sdg_01_10_FR_lastTimePeriod3_fr.json`) : `lastTimePeriod=3` sur `sdg_01_10?geo=FR` renvoie 2023, 2024, 2025, toutes renseignées ; le cas d'une dernière période vide pour la sélection n'a pas été testé |
| `geoLevel` | `aggregate`, `country`, `nuts1`, `nuts2`, `nuts3`, `city` | Incompatible avec `geo` (erreur 400) ; inutile en v1 (France seule) |

Codes d'erreur (documentation) : `100` aucun résultat (HTTP 400 si résultat vide, 404 si ressource absente) ; `140` erreur de syntaxe (400) ; `150` erreur sémantique, par ex. code de modalité inexistant (400) ; `500` erreur interne. Corps d'erreur JSON du type `{"error":{"status":"400","label":"…"}}`.

**Constaté en phase 2 (réponses réelles du robot)** : un **jeu inexistant** renvoie HTTP 404 avec une **liste** `{"error":[{"status":404,"id":100,"label":"ERR_NOT_FOUND_4: … is not available for dissemination."}]}` (fixture `erreur_jeu_inexistant.json`) ; une **modalité inexistante** (`unit=XXX`) ne renvoie **pas** d'erreur mais HTTP 200 avec un cube vide (`size` contenant un 0, `value` vide ; fixture `erreur_modalite_inexistante.json`). Le module traite les deux formes d'erreur et le cube vide (`AucuneDonnee`).

Traitement asynchrone : pour une extraction trop lourde, la réponse contient un objet `warning` de statut 413 et de libellé « ASYNCHRONOUS_RESPONSE. Your request will be treated asynchronously. Please try again later. » Aucune notification : **renvoyer la même requête plus tard** (FAQ : « waiting a few minutes and recalling the same URL should be enough »).

### 2.3 SDMX 2.1 (structure et données)

Racine : `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/`. Les codes de jeux s'écrivent en **majuscules** côté SDMX (`SDG_08_10`), en minuscules dans le TOC et l'API Statistics (`sdg_08_10`) ; les deux casses sont acceptées par l'API Statistics.

**Requêtes de structure** — modèle `…/{type}/{agence}/{id}/{version}?detail=…&references=…&compressed=…` :

| Requête | Exemple | Utilité |
|---|---|---|
| Liste de tous les jeux | `…/dataflow/ESTAT/all` (ou `…/dataflow/all/all/latest`) | Catalogue SDMX (sans hiérarchie de dossiers) |
| Un jeu | `…/dataflow/ESTAT/NAMA_10_GDP` ; `?references=descendants` ajoute DSD, listes de codes et concepts | Nom, structure associée |
| Structure (DSD) | `…/datastructure/ESTAT/SDG_08_10` | **Ordre des dimensions** et listes de codes associées (voir §5) |
| Liste de codes | `…/codelist/ESTAT/GEO` ; formats `JSON` ou `TSV` et `lang=fr` acceptés pour les listes de codes | Libellés des modalités ; ex. vérifié : `…/codelist/ESTAT/OBS_FLAG?format=TSV&lang=fr` |
| Contrainte de contenu | `…/contentconstraint/ESTAT/NAMA_10_GDP` | **Combinaisons de modalités réellement présentes** dans le jeu (évite de tester des combinaisons théoriques) |
| Schéma de catégories | `…/categoryscheme/ESTAT/{thème}` (ex. `popul`, `envir`, `cc`, `tb_eu`) | **Arborescence des dossiers** du TOC (identifiants = codes de dossiers du TOC) — voir §7 |

Paramètre `detail` : `full` (défaut), `allstubs`, `referencestubs`, `allcompletestubs`, `referencecompletestubs`, `referencepartial` (seulement avec `references=children|descendants` sur un dataflow). Paramètre `references` : `none` (défaut), `children`, `descendants`. Une seule ressource par requête (pas de valeurs multiples). Les jeux de données sont toujours en version `1.0` ; DSD, listes de codes et concepts sont versionnés.

**Requêtes de données** — modèle `…/data/{CODE}/{clé}?startPeriod=…&endPeriod=…&format=…` :
- la **clé** liste les modalités dans **l'ordre des dimensions de la DSD**, séparées par des points ; position vide = toutes les modalités ; `+` = OU. Ex. documenté : `…/data/NAMA_10_GDP/A.CP_MEUR..LU` ; `…/data/DEMO_GIND/A.NATT+POPTRT.FR+FX/?format=TSV&startPeriod=2012&endPeriod=2021` ;
- `format` : SDMX-ML 2.1 générique (défaut), `SDMX_2.1_STRUCTURED`, `SDMX-CSV`, `JSON` (JSON-stat), `TSV` ;
- `startPeriod`, `endPeriod`, `firstNObservations`, `lastNObservations` (N premières/dernières observations **par série**) ; `detail` = `dataonly` | `serieskeysonly` | `nodata` | `full` ; `returnData=ALL` (TSV et SDMX-CSV) conserve les séries sans donnée ;
- vérifié : `…/sdmx/2.1/data/SDG_08_10/A..B1GQ.FR?format=TSV&startPeriod=2018` (fixture `sdmx_SDG_08_10_FR_depuis2018.tsv`).

SDMX 3.0 existe aussi (`…/sdmx/3.0/…`, formats SDMX-CSV 2.0, JSON-stat, TSV, SDMX-ML) : non utilisé par le projet.

### 2.4 Téléchargement en masse (TSV compressé)

- Jeu complet via SDMX 2.1 : `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{CODE}?format=TSV&compressed=true` (forme indiquée par la fiche de mission). **Vérifié en phase 2** : `…/data/SDG_08_10/A..B1GQ.FR?format=TSV&compressed=true&startPeriod=2018` renvoie HTTP 200, `Content-Type: text/tab-separated-values`, **corps gzip** (180 octets, 236 une fois décompressé), sans en-tête `Content-Encoding` : il faut décompresser soi-même (`decompresser_si_gzip`).
- Interface manuelle équivalente : `https://ec.europa.eu/eurostat/databrowser/bulk?lang=en` (jeux complets en TSV gzip, SDMX-CSV, SDMX 2.1). L'ancien service `BulkDownloadListing` n'est plus mentionné par la documentation actuelle (« non trouvé »).
- **Format TSV** (page FAQ « TSV format », vérifié sur une réponse réelle) :
  - une ligne d'en-tête puis une ligne par série ; 1re colonne = codes des dimensions séparés par des virgules puis `\TIME_PERIOD` (ex. `freq,unit,na_item,geo\TIME_PERIOD`), colonnes suivantes = périodes en ordre croissant ;
  - cellule = `valeur␣drapeau` ; **une espace finale est conservée quand il n'y a pas de drapeau** (`36570 `), `38180 p` sinon ; observé : les libellés de périodes de l'en-tête portent aussi une espace finale (`2018 `) ;
  - `:` = valeur absente ; les séries entièrement vides sont omises (sauf `returnData=ALL`) ; lignes triées par clé ;
  - jeux multi-fréquences : une ligne par fréquence.

### 2.5 API asynchrone

- Une requête devient asynchrone quand l'un de ces critères dépasse un seuil (valeurs **non publiées**) : nombre de requêtes d'extraction simultanées ; nombre de requêtes par jour, sur 7 jours, sur 30 jours ; « coût d'extraction » cumulé par jour, 7 jours, 30 jours.
- Réponse de soumission (XML) avec un identifiant ; suivi : `https://ec.europa.eu/eurostat/api/dissemination/1.0/async/status/{id}` ; récupération : `…/1.0/async/data/{id}` quand le statut vaut `AVAILABLE`. Statuts : `SUBMITTED`, `PROCESSING`, `AVAILABLE`, `EXPIRED` (après « quelques jours » ou mise à jour du jeu), `UNKNOWN_REQUEST`, `ERROR`.
- Requête trop volumineuse : erreur `413 EXTRACTION_TOO_BIG` indiquant le nombre de lignes estimé et le maximum (exemple de la documentation : 5 000 000 lignes) → ajouter des filtres.
- **Recommandations Eurostat** : une extraction à la fois, **pas de parallélisation** dans les scripts, téléchargement en masse quand c'est possible.

## 3. Quotas et bonnes pratiques pour la collecte (GitHub Actions)

- Aucun quota chiffré n'est publié (ni requêtes par minute, ni taille maximale) ; seuls existent le passage forcé en asynchrone (§2.5) et la limite de longueur d'URL (« network appliance » : éviter de répéter des dizaines de `&geo=`).
- Constat de la mission : l'outil WebFetch (proxy de la session) a reçu des **HTTP 429** après environ 7 requêtes en 4 minutes vers `ec.europa.eu`. Il s'agit peut-être d'une limite du proxy et non d'Eurostat, mais le script de phase 2 doit l'anticiper.
- Règles proposées pour les scripts : requêtes **séquentielles**, pause ≥ 0,2 s (fiche de mission) et reprise avec attente croissante sur 429/5xx ; détection du `warning` 413 asynchrone (nouvel essai après quelques minutes) ; filtrer systématiquement `geo=FR` (et `sinceTimePeriod=2000` si utile) pour garder des réponses petites ; journaliser chaque requête.

## 4. Structure d'une réponse JSON-stat 2.0 (API Statistics)

Vérifiée sur deux réponses réelles : `sdg_08_10?geo=FR&lang=fr&time=2022` et `sdg_01_10?geo=FR&lang=fr` (fixtures `tests/fixtures/eurostat/sdg_08_10_FR_2022_fr.json` et `sdg_01_10_FR_fr.json`).

### 4.1 Clés de premier niveau
`version` (`"2.0"`), `class` (`"dataset"`), `label` (titre du jeu dans la langue demandée), `source` (`"ESTAT"`), `updated` (horodatage ISO de la dernière mise à jour, ex. `"2026-10-09T23:00:00+0200"`), `value`, `status` (**absente** s'il n'y a aucun drapeau dans la sélection), `id`, `size`, `dimension`, `extension`. Pas de clé `role` ni `note`.

### 4.2 Dimensions : `id`, `size`, `dimension.*`
- `id` : **liste ordonnée** des dimensions, ex. `["freq","age","unit","geo","time"]` ; l'ordre est celui de la structure du jeu, `time` toujours en dernier.
- `size` : nombre de modalités **présentes dans la réponse** pour chaque dimension, dans le même ordre, ex. `[1,2,2,1,12]`.
- `dimension.<dim>.label` : libellé de la dimension (ex. `"Unité de mesure"`).
- `dimension.<dim>.category.index` : `{code: position}`, ex. `{"PC":0,"THS_PER":1}`.
- `dimension.<dim>.category.label` : `{code: libellé}`, ex. `{"PC":"Pourcentage","THS_PER":"Milliers de personnes"}`.
- **La dimension `time` contient aussi des périodes sans aucune donnée pour la sélection** (ex. `2014` pour `sdg_01_10` en France), signalées dans `extension.positions-with-no-data`.

### 4.3 Valeurs : `value` clairsemé et `status`
- `value` est un **objet clairsemé** `{"position linéaire": valeur}` ; une position absente = pas de donnée. La position linéaire se calcule en ordre « ligne » (la dernière dimension, `time`, varie le plus vite) :
  `position = Σ_k pos_k × Π_{j>k} size_j`.
  Exemple `sdg_01_10` (`size = [1,2,2,1,12]`) : (age=`TOTAL`→0, unit=`PC`→0, time=`2015`→1) → position 1 → 18.4 ; (age=`Y_LT18`→1, unit=`PC`→0, time=`2015`→1) → 1×(2×1×12) + 0 + 1 = 25 → 22.4.
- `status` est un objet clairsemé de même indexation `{"position": "drapeau"}`, ex. `{"6":"b","8":"b"}` : rupture de série en 2020 et 2022 pour le taux AROPE France.
- Liste officielle des drapeaux (`…/sdmx/2.1/codelist/ESTAT/OBS_FLAG?format=TSV&lang=fr`, fixture `codelist_OBS_FLAG_fr.tsv`, 42 codes) : codes simples `b` rupture de série, `d` définition différente, `e` estimé, `f` prévision, `i` valeur imputée, `m` valeur manquante (ne peut exister), `n` non significatif, `p` provisoire, `u` peu fiable, et leurs combinaisons (`bp`, `ep`, `bdu`…). La confidentialité relève d'un attribut distinct (`CONF_STATUS`).

### 4.4 `extension`
- `lang` (`"FR"`), `id` (code en majuscules, ex. `"SDG_08_10"`), `agencyId` (`"ESTAT"`), `version` (`"1.0"`), `datastructure` (`{"id":"SDG_08_10","agencyId":"ESTAT","version":"125.0"}`).
- `positions-with-no-data` : `{dimension: [positions sans aucune donnée]}`, ex. `{"freq":[],"age":[],"unit":[],"geo":[],"time":[0]}`. Permet de calculer **la première et la dernière période réellement renseignées** sans parcourir `value`.
- `annotation` : liste d'objets `{type, title?, date?, href?}`. Annotations utiles relevées sur `sdg_08_10` :

| `type` | Contenu | Usage |
|---|---|---|
| `DISSEMINATION_SOURCE_DATASET` | `title` = code du **jeu source**, ex. `NAMA_10_PC` (pour `sdg_08_10`), `ILC_PECS01` (pour `sdg_01_10`) | Retrouver le jeu source d'une vue SDG, plus riche en ventilations |
| `OBS_PERIOD_OVERALL_OLDEST` / `OBS_PERIOD_OVERALL_LATEST` | première / dernière période du jeu **tous pays confondus** | Filtrage rapide (ne vaut pas pour la France seule) |
| `OBS_COUNT` | nombre d'observations du jeu (tous pays) | Taille du jeu |
| `UPDATE_DATA`, `UPDATE_STRUCTURE`, `CREATED`, `DISSEMINATION_TIMESTAMP_*` | dates | `derniere_maj` du catalogue |
| `DISSEMINATION_DOI_XML` | DOI du jeu (titre XML long) | Mention de la source (licence) |
| `ESMS_HTML`, `ESMS_SDMX`, `DISSEMINATION_EXPLANATORY_LINK` | liens vers les métadonnées de référence | `url_page` des fiches indicateurs |
| `DISSEMINATION_OBJECT_TYPE` | `DATASET` | — |

`extension.description` contient le texte de présentation du jeu (description méthodologique) ; non relevé en entier.

## 5. Structure d'une datastructure SDMX (DSD)

Vérifiée en phase 1 sur `…/sdmx/2.1/datastructure/ESTAT/SDG_08_10` (lecture WebFetch) ; en phase 2, réponses brutes enregistrées : `datastructure_SDG_01_10.xml` et `dataflow_{SDG_01_10,ILC_LI02}_referencepartial.xml` (voir §8). Message SDMX-ML 2.1 (XML) :
- en-tête : `ID`, `Prepared` (horodatage), `Sender id="ESTAT"` ;
- `DataStructure` `id="SDG_08_10"`, `agencyID="ESTAT"`, `version="125.0"`, `isFinal="true"` ;
- `DimensionList` : dimensions **ordonnées** par `position` — `freq` (1, liste `ESTAT:FREQ(3.9)`), `unit` (2, `UNIT(82.0)`), `na_item` (3, `NA_ITEM(30.1)`), `geo` (4, `GEO(28.0)`) ; chaque dimension renvoie à un concept et à une liste de codes **par référence** ;
- `TimeDimension` `TIME_PERIOD` (position 5, type `ObservationalTimePeriod`) ;
- `AttributeList` : `OBS_FLAG` (liste `OBS_FLAG(1.39)`) et `CONF_STATUS` (liste `CONF_STATUS(1.2)`), conditionnels, rattachés à la mesure ;
- `MeasureList` : `PrimaryMeasure` `OBS_VALUE` (type `Double`) ;
- **les listes de codes ne sont pas incluses** : il faut les demander séparément (`…/codelist/ESTAT/UNIT?format=TSV&lang=fr`) ou utiliser `…/dataflow/ESTAT/{CODE}?references=descendants`. La DSD donne toutes les modalités **possibles** de la liste de codes (souvent des milliers pour `geo` ou `unit`) ; les modalités **réellement présentes** dans le jeu sont dans la contrainte de contenu (`…/contentconstraint/ESTAT/{CODE}`) ou, pour la France, dans la réponse JSON-stat filtrée `geo=FR`.
- **Choix de phase 2** : le robot lit la structure par `…/dataflow/ESTAT/{CODE}?references=descendants&detail=referencepartial` (une requête : DSD + listes de codes **réduites aux modalités présentes dans le jeu**, tous pays confondus, libellés en/fr/de), avec repli sur `…/datastructure/ESTAT/{CODE}?references=children`. La présence de `FR` (ou à défaut `FX`) dans la liste `GEO` réduite décide de l'interrogation des données.

## 6. Pièges constatés (phase 1)

1. **WebFetch ne restitue pas les réponses brutes** (citations limitées à 125 caractères, réponses résumées) et **tronque les documents longs** (le TOC complet n'est lu qu'à hauteur de ses 77 684 premiers caractères, soit le début du thème « General and regional statistics » ; les schémas de catégories `popul`, `cc`, `tb_eu` sont tronqués vers 100 000 caractères). Les fixtures ont donc été **reconstituées champ par champ** (voir §8). Le TOC complet ne peut être lu que par un script exécuté sur GitHub Actions (phase 2).
2. **Limite de débit** : HTTP 429 du proxy WebFetch après quelques requêtes rapprochées ; trois pages non lues pour cette raison (`categoryscheme/ESTAT/sdg`, `categoryscheme/ESTAT/economy`, `dataflow/ESTAT/ILC_LI02?references=parents`).
3. **Le TOC `lang=fr` semble en retard sur le TOC `lang=en`** : le 13/10/2026, `ei_bpm6ca_q` affichait une dernière mise à jour au `02.10.2026` (données jusqu'à `2026-Q2`, 314 724 valeurs) en anglais, mais au `08.07.2026` (jusqu'à `2026-Q1`, 311 618 valeurs) en français. Recommandation : lire les dates et la hiérarchie dans le TOC `en`, ne prendre au TOC `fr` que les titres français (ou prendre le `label` de la réponse JSON-stat `lang=fr`).
4. L'en-tête du TOC n'est pas traduit (`"title"`, `"code"`… dans toutes les langues).
5. `time` contient des périodes vides pour la France ; `OBS_PERIOD_OVERALL_*` vaut pour tous les pays : **toujours calculer première et dernière période sur la sélection `geo=FR`**.
6. `status` est absent quand la sélection n'a aucun drapeau : le code doit tolérer l'absence de la clé.
7. Les vues `sdg_*` cachent souvent des ventilations du jeu source (annotation `DISSEMINATION_SOURCE_DATASET` ou service `catalogue/relations`) : par ex. `sdg_08_10` ← `nama_10_pc`, `sdg_01_10` ← `ilc_pecs01`.
8. Ruptures EU-SILC : le taux AROPE France porte un drapeau `b` en 2020 **et** en 2022 ; la série `sdg_01_10` ne commence qu'en 2015 pour la France (période 2014 présente mais vide ; 2014 est la première période tous pays). Il s'agit de la définition de l'AROPE retenue pour les objectifs 2030 ; pour couvrir 2000–2014, il faudra chercher dans les jeux `ilc_*` une série de l'ancienne définition (à vérifier en phase 2).
9. Casse des codes : minuscules dans le TOC et l'API Statistics, majuscules en SDMX.

### Pièges constatés en phase 2 (passages du robot)

10. **Les indicateurs ODD `sdg_*` sont typés `table` dans le TOC** (seuls 33 codes `sdg_*` y sont des `dataset`), alors que l'API les sert comme des jeux : le filtre strict `type = dataset` de la fiche aurait perdu l'essentiel du dossier ODD. Ils sont donc inclus au niveau 1 (exception motivée) ; les autres tableaux restent non candidats (vues prédéfinies d'un jeu, souvent rangées sous ce jeu dans le TOC).
11. **Deux racines portent le code `data`** : « Database by themes » et « Cross cutting topics » (titre français « Thèmes transversaux ») ; un même dossier ou jeu peut figurer dans les deux arborescences. Le chemin principal d'un jeu est celui de « Database by themes » ; les autres sont dans `autres_chemins`.
12. Les lignes de dossiers du TOC se terminent par un champ vide (et non `" "`) ; le TOC complet compte 12 235 lignes (≈ 2 Mo en anglais, 2,2 Mo en français).
13. Une **modalité inexistante** renvoie HTTP 200 avec un cube vide, sans erreur ; un **jeu inexistant** renvoie 404 avec `{"error":[…]}` (liste) en JSON et une enveloppe SOAP `Fault` en SDMX (voir §2.2).
14. Certains codes ODD ne contiennent que des **agrégats UE** (`sdg_13_11`, `sdg_15_60`, `sdg_15_61`) ou n'ont pas de valeur France (`sdg_10_20` : `FR` absent de la liste des zones ; `sdg_06_30` : aucune observation France depuis 2000) ; d'autres ont disparu (`sdg_05_60`, `sdg_15_10`) : voir §9.
15. Le TOC contient des **jeux sans France par construction** (pays du voisinage et candidats : préfixes `enps_`, `enpe_`, `enpr_`, `cpc_`, `med_`, `enlr_`, dossier « Non EU countries », 176 jeux) et des **projections** jusqu'en 2100 (`proj_*`…), qui passent les filtres de dates de la fiche : ils sont exclus avec motif.
16. **Faux amis des mots-clés** (titres en et fr lus ensemble) : « cultures » (récoltes) ≠ culture ; « fertility » (fécondité) ≠ « fertiliser » ; « relatives » (proches) lu dans « décisions relatives à » ; « politique » (policy) lu dans « Politique de sécurité » ; « water » dans « waterways » ; « accommodation » (tourisme) ≠ logement ; « road traffic » (trafic) ≠ accidents. Les mots-clés trouvés **seulement dans le chemin des dossiers** rattachaient tout le thème « Agriculture, forestry and fisheries » à `planete` : depuis la v4 ils donnent l'étiquette mais plus la candidature (§10.2).

## 7. Dossiers prioritaires dans l'arborescence du TOC

Les dossiers prioritaires de la fiche M02 (A3) sont repérés **par le préfixe du code du jeu** (prioritaire sur l'emplacement) puis **par le titre d'un des dossiers de ses chemins** (anglais, normalisé). Emplacements dans le TOC du 13/10/2026 (`catalogues/eurostat_dossiers_toc.csv`, colonne `chemin`) :

| Dossier prioritaire (`dossier_prioritaire`) | Préfixes de code | Code et chemin du dossier principal dans le TOC |
|---|---|---|
| `sdg` — Sustainable development indicators | `sdg_` | `sdg` : Cross cutting topics > EU policies > Sustainable development indicators (sous-dossiers `sdg_01` … `sdg_17`, « Goal NN – … ») |
| `qualite_de_vie` — Quality of life | `qol`, `ilc_pw` | `qol` : Cross cutting topics > Cross cutting topics > Quality of life |
| `revenus_conditions_de_vie` — Income and living conditions | `ilc_` | `ilc` : Database by themes > Population and social conditions > Living conditions and welfare > Income and living conditions (aussi `dsb_ilc` sous Disability et `eq_ilc` sous Equality and non-discrimination) |
| `marche_du_travail` — Labour market | `lfs`, `une_`, `earn_` | `labour` : Database by themes > Population and social conditions > Labour market |
| `sante` — Health | `hlth_` | `hlth` : Database by themes > Population and social conditions > Health (aussi `qol_hlt`, `eq_hlth`, `degurb_hlth`) |
| `education_formation` — Education and training | `educ_`, `trng_`, `edat_` | `educ` : Database by themes > Population and social conditions > Education and training |
| `criminalite` — Crime and criminal justice | `crim_` | `crim` : Database by themes > Population and social conditions > Crime and criminal justice |
| `environnement` — Environment | `env_` | `env` : Database by themes > Environment and energy > Environment |
| `energie` — Energy | `nrg_` | `nrg` : Database by themes > Environment and energy > Energy |
| `comptes_nationaux` — National accounts | `nama_10_pc`, `nasa_10_` | `na10` / `nama10` : Database by themes > Economy and finance > National accounts (ESA 2010) > Annual national accounts (par code seulement : le dossier entier n'est pas prioritaire) |
| `population` — Population | `demo_` | `demo` : Database by themes > Population and social conditions > Demography, population stock and balance (par code seulement) |
| `numerique` — Digital economy and society | `isoc_` | `isoc` : Database by themes > Science, technology, digital society > Digital economy and society |
| `culture` — Culture | `cult_` | `cult` : Database by themes > Population and social conditions > Culture |
| `securite_transports` — Transport safety | `tran_sf_` | `tran_sf` : Database by themes > Transport > Transport safety |

Remarques : les titres « Labour market », « Health », « Energy », « Environment » désignent aussi des sous-dossiers d'autres thèmes (« Degree of urbanisation > Labour market », « Euro indicators / PEEIs > Labour market », « Climate change > Drivers > Energy », dossiers des pays du voisinage…) : leurs jeux sont traités comme prioritaires (les jeux du voisinage sont ensuite exclus, §6 n° 15 ; les jeux mensuels des indicateurs conjoncturels sont non candidats car infra-annuels). Le nombre de jeux, de jeux retenus par les filtres et de candidats sous chaque emplacement de dossier est dans `catalogues/eurostat_dossiers_toc.csv` (§10.1).

## 8. Fixtures enregistrées (`tests/fixtures/eurostat/`)

Depuis le premier passage du robot (13/10/2026, étape `echantillons`), les fixtures sont des **réponses brutes réelles** enregistrées par le script de collecte sur GitHub Actions (URL, statut HTTP, type, taille, date de chaque requête : `echantillons_info.json`). Les fixtures reconstituées par WebFetch en phase 1 ont été remplacées, sauf la liste des drapeaux.

| Fichier | Requête (13/10/2026) | Origine |
|---|---|---|
| `toc_extrait_en.txt`, `toc_extrait_fr.txt` | `…/catalogue/toc/txt?lang=en` / `fr` | Robot : en-tête, 12 premières lignes, puis lignes de 10 codes témoins (`sdg_01_10`, `sdg_08_10`, `ilc_li02`, `ilc_pw01`, `une_rt_a`, `lfsq_egais`, `tps00001`, `hlth_silc_10`, `ilc_lvho05a`, `nama_10_pc`) et de tous leurs dossiers ancêtres, recopiées sans modification |
| `dataflow_SDG_01_10_referencepartial.xml`, `dataflow_ILC_LI02_referencepartial.xml` | `…/sdmx/2.1/dataflow/ESTAT/{CODE}?references=descendants&detail=referencepartial` | Robot (brut) : structure + listes de codes réduites aux modalités présentes |
| `datastructure_SDG_01_10.xml` | `…/sdmx/2.1/datastructure/ESTAT/SDG_01_10` | Robot (brut) |
| `sdg_01_10_FR_fr.json`, `sdg_08_10_FR_2022_fr.json`, `ilc_li02_FR_T_PC_depuis2015_fr.json`, `sdg_10_20_FR_fr.json`, `sdg_01_10_FR_lastTimePeriod3_fr.json` | `…/statistics/1.0/data/{code}?geo=FR&lang=fr&…` | Robot (brut, JSON-stat 2.0) |
| `erreur_modalite_inexistante.json`, `erreur_jeu_inexistant.json`, `erreur_structure_inexistante.xml` | `sdg_08_10?unit=XXX`, `zzz_inexistant`, `dataflow/ESTAT/ZZZ_INEXISTANT` | Robot (brut) : cube vide HTTP 200, erreur JSON 404, enveloppe SOAP 404 |
| `sdmx_SDG_08_10_FR_depuis2018.tsv` | `…/sdmx/2.1/data/SDG_08_10/A..B1GQ.FR?format=TSV&compressed=true&startPeriod=2018` | Robot : réponse gzip décompressée (236 octets) |
| `metabase_extrait.txt` | `…/catalogue/metabase.txt.gz` | Robot : 80 premières lignes de la metabase décompressée |
| `echantillons_info.json` | — | Robot : métadonnées de chaque requête ci-dessus |
| `codelist_OBS_FLAG_fr.tsv` | `…/sdmx/2.1/codelist/ESTAT/OBS_FLAG?format=TSV&lang=fr` | Phase 1 (WebFetch) : 42 lignes recopiées |

## 9. Statut des séries des prototypes

Fichier `docs/sources/eurostat_amorce_prototypes.csv` : une ligne par série Eurostat des prototypes (`docs/archives/prototypes_indicateurs.csv`, 66 séries d'origine Eurostat), **vérifiée par le robot** (requête JSON-stat `geo=FR`, toutes périodes) à l'étape `amorce` du script. Colonnes : identifiant et libellé du prototype, `code_eurostat`, `statut`, `nouveau_code`, libellé Eurostat (fr), première et dernière période et nombre de périodes pour la France (série par défaut), unité par défaut et unités disponibles, dimensions du jeu, ventilations disponibles dans la vue, jeu source (annotation `DISSEMINATION_SOURCE_DATASET`), date de mise à jour, drapeaux, date de vérification, commentaire (partie manuelle de phase 1 puis ` || robot : …`).

Statuts : `disponible` (série France ≥ 10 années depuis 2000 et dernière ≥ 2020) ; `disponible (série courte)` (série France présente mais critère §3.4 non rempli) ; `code changé` (code disparu, successeur vérifié) ; `à remplacer` (le code ne fournit pas la France ; remplaçant vérifié) ; `sans donnée FR`. Bilan au 13/10/2026 : voir §10.4.

## 10. Catalogues Eurostat (phase 2)

### 10.1 Fichiers produits par le robot

| Fichier | Contenu |
|---|---|
| `catalogues/eurostat_jeux_catalogue.csv` | **Niveau 1** : un code du TOC par ligne (jeux `dataset` et tableaux `table`, dédoublonnés par code). Colonnes de la charte §5.3 (`source`, `serie_id` = code du jeu, `libelle` (fr), `unite` (vide au niveau 1), `frequence`, `geo` (vide), `premiere_periode`, `derniere_periode`, `derniere_maj`, `theme_source` (chemin principal des dossiers), `dimension_v0`, `candidat`, `commentaire` (= motif)) puis : `code_jeu`, `libelle_en`, `type`, `nb_valeurs`, `derniere_modif_structure`, `theme_codes`, `autres_chemins` (autres emplacements dans le TOC), `dossier_prioritaire`, `dimensions_v0_secondaires`, `methode_etiquette` (`mots-clés`, `objectif ODD NN`, `dossier …`, `aucun mot-clé`), `filtre_toc` (`retenu` / `exclu : …` / `hors filtre : …`), `motif_candidat`, et le résultat du niveau 2 : `statut_niveau2` (`ok`, `sans_donnee_fr`, `sans_dimension_geo`, `structure_introuvable`, erreurs), `nb_series_fr`, `nb_series_candidates`, `structure_fr` (rôle de chaque dimension, ex. `unit (2) [unité] ; sex→T (3) [ventilation] ; icd10 (80) [contenu]`). |
| `catalogues/eurostat_series_catalogue.csv` | **Niveau 2** : une ligne par série France **lue dans une réponse de l'API** (aucune combinaison théorique). Colonnes §5.3 (`serie_id` = code du jeu + filtres de l'API Statistics, directement réutilisable : `sdg_01_10?freq=A&age=TOTAL&unit=PC&geo=FR`) puis `code_jeu`, `type_ligne` (`defaut` ou `ventilation`), `ventilation` (dimension ventilée), `libelles_modalites`, `unite_code`, `unites_disponibles`, `nb_points`, `nb_annees`, `derniere_valeur`, `drapeaux` (drapeaux Eurostat et nombre d'occurrences depuis 2000, ex. `b:2 ; p:1`), `modalites_ventilation` (ligne de ventilation : `modalité:première-dernière:nb_années` pour chaque modalité), `jeu_source`, `date_verification`. `candidat` vaut `oui` / `non` (éligibilité §3.4, motif dans `commentaire`) pour une ligne `defaut`, `ventilation` pour une ligne de ventilation (D21). Compressé automatiquement en `.csv.gz` au-delà de 90 Mo (limite GitHub de 100 Mo par fichier). |
| `catalogues/eurostat_dossiers_toc.csv` | Une ligne par **emplacement** de dossier du TOC (un même code peut figurer à plusieurs endroits ; les deux racines portent le code `data`) : `code_dossier`, `titre_en`, `titre_fr`, `profondeur`, `chemin`, `chemin_codes`, `nb_jeux` (codes de jeux et de tableaux rangés dessous, toutes profondeurs), `nb_jeux_filtres` (dont retenus par les filtres de dates), `nb_candidats`. |
| `catalogues/eurostat_bilan.json` | Volumes du dernier passage (TOC, filtres, candidats par dimension et par dossier, statuts du niveau 2, séries par dimension). |
| `catalogues/eurostat_etat_collecte.json` | État du script reprenable : version et date de chaque étape, statut et durée de chaque jeu traité au niveau 2, historique des passages (requêtes, nouveaux essais, octets). |
| `docs/sources/eurostat_amorce_prototypes.csv` | Statut des 66 séries des prototypes (§9). |
| `journaux/collecte_<horodatage>_collecte_eurostat.py.log` | Journal d'exécution de chaque passage (une ligne par jeu au niveau 2). |

### 10.2 Niveau 1 : filtres, étiquetage, candidature

Source : TOC anglais (dates et hiérarchie, §6 n° 3) et TOC français (titres). Logique : `src/pipeline/catalogue_eurostat.py` (`construire_catalogue_jeux`, `etiqueter`, `bilan_dossiers`).

1. **Filtres de dates** (fiche M02) : `filtre_toc = retenu` si fin des données ≥ 2020 et début ≤ 2010 ; `exclu` si fin < 2020 ou dates absentes ; `hors filtre` si début > 2010.
2. **Dossier prioritaire** (§7) : préfixe du code, puis titre d'un dossier de l'un des chemins.
3. **Étiquette `dimension_v0`** par mots-clés anglais et français (liste `MOTS_CLES`, frontières de mots, sans accents) : score 2 par dimension trouvée dans la **partie principale du titre** (avant « by » / « par »), 0,5 dans la partie « by … » (ventilations), 1 dans le chemin principal des dossiers ; la meilleure dimension est retenue (égalités départagées du plus spécifique au plus général : égalités, sécurité, démocratie, liens, logement, santé, éducation, travail, niveau de vie, planète) ; les autres dimensions de score ≥ 1 vont dans `dimensions_v0_secondaires`. Sans aucun mot-clé : repli sur l'objectif ODD (`sdg_NN` ou dossier « Goal NN »), puis sur le dossier prioritaire (ex. `revenus_conditions_de_vie` → `niveau_de_vie`, `numerique` et `culture` → `education`) ; les jeux `demo_*` sans mot-clé restent sans étiquette. **L'étiquette est une orientation pour le moissonnage, pas un classement** : la grille v1 (M03) et les fiches indicateurs (M05) la reprendront.
4. **Candidature** (`candidat`, motif dans `motif_candidat`), dans cet ordre :
   - `non` : jeux sans France par construction (§6 n° 15) ;
   - `non` : **domaines hors périmètre**, hors dossiers prioritaires — statistiques sectorielles qui ne décrivent ni la situation de la population ni l'environnement : production, prix et comptes agricoles, structure des exploitations, viticulture, pêche et aquaculture, produits de la sylviculture, transports fluvial, maritime, aérien, ferroviaire (hors sécurité) et par oléoduc, parc et trafic routiers, transport intermodal de marchandises, tourisme, investissements directs étrangers, commerce extérieur, statistiques d'entreprises, titres de séjour (liste `PREFIXES_HORS_PERIMETRE`) ; exceptions : surface boisée (`for_area*`), véhicules à émission nulle (`road_eq*_zev`) ;
   - `non` : projections (fin des données > 2027) ;
   - `non` : tableaux (`table`), sauf les indicateurs ODD `sdg_*` (§6 n° 10) ;
   - `non` : jeux infra-annuels (une version annuelle existe en général) ;
   - `oui` : jeu retenu par les filtres et rangé dans un dossier prioritaire ;
   - `oui` : jeu retenu par les filtres dont **un mot-clé figure dans la partie principale du titre** (un mot-clé trouvé seulement dans le chemin ou dans la ventilation donne l'étiquette, pas la candidature) ;
   - `oui` par **rattrapage** : jeu « hors filtre » (début > 2010) pouvant encore avoir ≥ 10 années jusqu'à sa fin (charte §3.4) et pertinent (dossier prioritaire ou mot-clé du titre) — sans quoi l'AROPE 2021 (`sdg_01_10`, `ilc_pecs01`) et de nombreux indicateurs ODD seraient perdus ;
   - `non` sinon (motif : filtre de dates, ou aucun mot-clé ni dossier prioritaire).
5. Historique des règles : v1 (premier passage, essai) ; v2 (tableaux ODD inclus, racine principale repérée par son titre) ; v3 (jeux hors France et projections exclus, mots-clés affinés) ; **v4** (candidature par mot-clé du titre principal, domaines hors périmètre, bilan des dossiers par emplacement).

### 10.3 Niveau 2 : séries France vérifiées

Pour chaque jeu candidat (ordre : échantillon de contrôle, puis indicateurs ODD, puis le reste) :

1. **Structure** : `dataflow/ESTAT/{CODE}?references=descendants&detail=referencepartial` (§5). Sans dimension `geo` : `sans_dimension_geo`. `FR` présent → `geo=FR` ; sinon `FX` (métropole, signalé dans le commentaire de chaque série) ; sinon `sans_donnee_fr` (sans requête de données).
2. **Plan de requêtes** JSON-stat (`lang=fr`, `sinceTimePeriod=2000`, `geo` et `freq=A` fixés) : si le cube majoré (modalités × périodes) dépasse 300 000 cellules, les dimensions ayant un code total (hors unité et ventilations) sont fixées à ce total, puis la plus grande dimension restante est découpée en paquets (≤ 40 codes par requête, ≤ 60 requêtes) ; sur `413 EXTRACTION_TOO_BIG`, nouveau plan plus fin (50 000 cellules, ≤ 120 requêtes) ; réponse asynchrone : jusqu'à 3 nouvelles tentatives espacées de 60 s. Requêtes séquentielles, pause de 0,2 s, nouvel essai avec attente croissante (10 s, 30 s, 90 s…) sur 429, 5xx ou coupure, en-tête `Retry-After` respecté.
3. **Rôle des dimensions** (réponse France) : `freq` et `geo` fixés ; `unit` choisie série par série (préférence : pourcentages et taux, puis par habitant, années et ratios, autres, indices, niveaux absolus, variations en dernier) ; `age` fixé à `TOTAL` ou à la classe la plus large (à la naissance pour une espérance de vie) ; une dimension ayant un code total (`TOTAL`, `T`, `_T`, `TOT`, `ALL`, `TOTAL_HH`, `POP` pour `wstatus`, `IND_TOTAL` pour `ind_type`) est fixée à ce total ; une dimension à une seule modalité est fixée ; les autres sont du **contenu** (chaque modalité = un indicateur distinct ; `icd10`, causes de décès, est toujours du contenu).
4. **Lignes** : une ligne `defaut` par combinaison des dimensions de contenu (autres dimensions à leur défaut, unité préférée parmi celles qui ont des données) ; **ventilations conservées (D21)** : pour chaque dimension de ventilation (`sex`, `age` hors âges détaillés année par année, `quantile`, `quant_inc`, `incgrp`, `quant_expn`, `hhtyp`, `hhcomp`, `deg_urb`, `ind_type`, `isced*`), une ligne `ventilation` listant les modalités hors défaut ayant des données, avec la couverture de chacune (`modalites_ventilation`) ; son `serie_id` répète le paramètre ventilé (`sex=M&sex=F`).
5. **Éligibilité** (charte §3.4) : `candidat = oui` si ≥ 10 années renseignées depuis 2000 **et** dernière période ≥ 2020, sinon `non` avec motif ; les drapeaux (`b` rupture, `p` provisoire, `e` estimé, `u` peu fiable…) sont comptés dans `drapeaux`.

### 10.4 Volumes au 13/10/2026

**État au 13/10/2026, 16 h 55** : le passage complet n° 2 du robot (run 38405905176, règles v2, niveau 2 sans limite, lancé à 15 h 33) n'était pas terminé ; le passage n° 3 (règles v4, run 38412944475) attend derrière lui. Les chiffres ci-dessous sont ceux du passage n° 1 (essai) et, pour les règles v4, une **estimation hors ligne** (règles appliquées à un pseudo-TOC reconstruit depuis le catalogue du passage 1, qui reproduit exactement les volumes v3 annoncés ; tableaux ODD non compris). `catalogues/eurostat_bilan.json` donne les chiffres réels du dernier passage commité.

| Élément | Valeur | Source |
|---|---|---|
| Entrées du TOC (anglais) | 12 234 (6 649 jeux, 911 tableaux, 1 878 codes de dossiers) | passage 1 |
| Jeux retenus par les filtres de dates (fin ≥ 2020, début ≤ 2010) | 2 715 (exclus 2 223 ; hors filtre 1 711) | passage 1 |
| Jeux candidats, règles v1 / v3 / **v4** (hors tableaux ODD) | 2 413 / 2 143 / **1 820** (dont 401 par rattrapage en v4) | passage 1 ; estimations hors ligne |
| Candidats v4 par dimension v0 | éducation 420, travail 420, niveau de vie 288, planète 230, santé 186, logement 107, sécurité 55, égalités 41, liens et bien-être 17, démocratie 7, sans étiquette (`demo_*`) 49 | estimation hors ligne |
| Candidats v4 par dossier prioritaire | revenus et conditions de vie 338, éducation 300, marché du travail 300, santé 191, environnement 109, numérique 92, population 70, énergie 62, ODD (jeux) 40, criminalité 24, culture 24, sécurité des transports 18, qualité de vie 16, comptes nationaux 10 ; hors dossiers (mots-clés du titre) 226 | estimation hors ligne |
| Non candidats v4 par motif principal | fin < 2020 ou dates absentes 1 704 ; domaine hors périmètre 1 357 ; début > 2010 sans rattrapage 942 ; infra-annuels 349 ; aucun mot-clé ni dossier 210 ; pays hors UE 176 ; mot-clé seulement dans le chemin ou la ventilation 50 ; projections 41 | estimation hors ligne |
| Niveau 2, passage 1 (40 jeux de contrôle) | 38 jeux avec séries FR, 2 sans donnée FR (`sdg_06_30`, `sdg_10_20`) ; 3 259 séries par défaut dont 2 780 éligibles, 129 lignes de ventilation ; 100 % `geo=FR` ; 0 série éligible hors critères (contrôle) | passage 1 |
| Amorce (66 séries des prototypes) | toutes vérifiées par le robot : 55 disponibles, 6 séries courtes (`sdg_03_30`, `sdg_04_40`, `sdg_04_70`, `sdg_17_60`, `sdg_15_50`, `sdg_11_32`), 3 sans donnée FR (`sdg_10_20`, `sdg_13_11`, `sdg_15_60`), 2 codes disparus (`sdg_05_60`, `sdg_15_10`) ; la version 2 (passage 2) vérifie les remplaçants `sdg_05_61`, `sdg_15_11`, `sdg_13_10`, `env_bio3` | passage 1 |

À compléter à la fin des passages 2 et 3 : nombre de jeux candidats réels (tableaux ODD compris), statuts du niveau 2, séries France vérifiées et éligibles par dimension v0, lignes de ventilation.

### 10.5 Limites connues

- **Étiquetage par mots-clés** : une dimension principale par jeu, déterminée surtout par le titre ; les jeux multi-thèmes (ex. santé par niveau de revenu) n'ont qu'une étiquette principale (les autres dans `dimensions_v0_secondaires`) ; la même étiquette est recopiée sur toutes les séries du jeu, y compris quand une modalité de contenu relèverait d'une autre dimension.
- **Jeux à beaucoup de séries de contenu** : certains jeux énumèrent des centaines de combinaisons (émissions par polluant × secteur, comptes par secteur × opération, usages d'internet par type d'individu…) ; elles sont toutes gardées (aucune limite a priori) et devront être regroupées par concept en M05.
- **Dimensions sans code total reconnu** (ex. `nace_r2` dont le total s'appelle `B-S_X_O`, `indic_*`) : énumérées comme contenu.
- **Choix de l'unité** : heuristique (taux et parts d'abord) ; les autres unités disponibles figurent dans `unites_disponibles`. Défaut constaté : les indices relatifs à la moyenne UE commençant par `PC_` (ex. `PC_EU27_2020_HAB_MEUR_CP` pour `nama_10_pc`) passent avant les niveaux par habitant en volume (`CLV20_EUR_HAB`) ; à corriger à la prochaine version du niveau 2 (rang plus faible pour les unités relatives à l'UE).
- **Découpage limité** à 60 (puis 120) requêtes par jeu : pour les jeux les plus volumineux, des modalités peuvent ne pas avoir été lues (signalé dans le message du jeu, colonne `structure_fr` et état de collecte).
- **Jeux infra-annuels et tableaux non candidats** (sauf ODD) : à réexaminer si un indicateur n'existe qu'en trimestriel ou en tableau.
- **France métropolitaine** (`FX`) prise seulement quand `FR` est absent.
- **Pas de raccordement** des séries ODD courtes à leurs jeux sources plus longs (D16) : le `jeu_source` est noté pour le faire en M05.
- **Mise à jour** : le script est reprenable et ne refait une étape que si sa version augmente (`ETAPES` dans `scripts/collecte_eurostat.py`) ou si elle n'est pas terminée ; le passage mensuel automatique sur `main` ne refera donc **rien** tant que l'état commité est complet (voir §10.6).

### 10.6 Relancer la collecte

- **Automatiquement** : tout push sur la branche `m02-eurostat` qui modifie `scripts/` ou `src/` relance le workflow « Collecte » (cible `collecte_eurostat.py`) ; les résultats, l'état et le journal sont commités sur la branche par le robot (`git pull --rebase origin m02-eurostat` pour les récupérer).
- **À la demande** : `python scripts/actions.py lancer --branche m02-eurostat --cible collecte_eurostat.py`, puis `python scripts/actions.py suivre --run <id>` et `python scripts/actions.py journal --branche m02-eurostat`.
- **Refaire une étape** : augmenter sa version dans `ETAPES` (ex. `"niveau1": 5`) ; refaire le niveau 1 rouvre le niveau 2 (retrait des jeux qui ne sont plus candidats, traitement des seuls nouveaux). **Tout refaire** : augmenter la version de `niveau2` (repart de zéro) ou supprimer `catalogues/eurostat_etat_collecte.json`.
- **Variables d'environnement** : `EUROSTAT_DUREE_MAX_MINUTES` (défaut 270 ; arrêt propre et reprise au passage suivant), `EUROSTAT_NIVEAU2_MAX_JEUX` (0 = sans limite), `EUROSTAT_ETAPES` (ex. `niveau1,niveau2`).
