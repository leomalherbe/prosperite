# Fiche source — Eurostat

Rédigée par l'agent de la mission M02 (phase 1), le 2026-10-13 ; complétée en phase 2 le même jour (sections 6 à 10 : pièges constatés par le robot, dossiers du TOC, fixtures réelles, statut des séries des prototypes, **catalogues**) ; **clôture de la phase 2 le 2026-10-14** (règles v5, bilan final §10.4, rafraîchissement §10.6). Les informations de phase 1 ont été lues dans la documentation officielle d'Eurostat ou dans des réponses réelles obtenues par l'outil de lecture de page (WebFetch) ; celles de phase 2 proviennent des passages du robot de collecte (GitHub Actions) et de ses journaux (`journaux/`). Ce qui n'a pas pu être vérifié est signalé « non vérifié » ou « non trouvé ».

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
16. **Faux amis des mots-clés** (titres en et fr lus ensemble) : « cultures » (récoltes) ≠ culture ; « fertility » (fécondité) ≠ « fertiliser » ; « relatives » (proches) lu dans « décisions relatives à » ; « politique » (policy) lu dans « Politique de sécurité » ; « water » dans « waterways » ; « accommodation » (tourisme) ≠ logement ; « road traffic » (trafic) ≠ accidents. Les mots-clés trouvés **seulement dans le chemin des dossiers** rattachaient tout le thème « Agriculture, forestry and fisheries » à `planete` : depuis la v4 ils donnent l'étiquette mais plus la candidature (§10.2). Contrôle qualité du 14/10 (v5) : « **Tableaux des emplois** » (titre français des *use tables* entrées-sorties) lu comme « emploi » ; « besoins de soins **non satisfaits** » lu comme satisfaction ; « **sages-femmes** » lu comme écart femmes-hommes.
17. **Cube vide d'un jeu sans la France** (bogue des passages 2 et 3, 13/10) : `env_bio3` n'a que l'agrégat UE ; `geo=FR` renvoie HTTP 200 avec une dimension `geo` **de taille 0**, et le rôle des dimensions levait `IndexError` (liste de modalités vide) dans la vérification des remplaçants de l'amorce. Corrigé en v5 : un cube vide donne « aucune valeur pour la France » et une réponse de forme inattendue « structure inattendue », sans arrêter l'étape (tests de non-régression sur les fixtures réelles `sdg_10_20_FR_fr.json` et `erreur_modalite_inexistante.json`).
18. **Dossiers prioritaires mêlés de statistiques d'entreprises** : « Digital economy and society » contient les enquêtes TIC auprès des entreprises (`isoc_ci_*_en2`, `isoc_ec_*`, `isoc_eb_*`…) et la démographie des entreprises (`bd_*`), « Culture » des statistiques structurelles d'entreprises (`sbs_*`), « Labour market » l'enquête sur le coût de la main-d'œuvre (`lc_n*`, `lc_r*`) : la règle du dossier prioritaire les rendait candidats (≈ 102 000 lignes de séries au 13/10). Exclus en v5, même dans un dossier prioritaire (§10.2).
19. **Codes « total » propres à certaines dimensions** : partenaire `WORLD` ou `WRL_X_REP` (monde hors pays déclarant, mobilité étudiante), espèces `F00` (tous organismes aquatiques), zone de pêche `0` (toutes zones) ou la grande zone du jeu (`27` pour ses sous-zones `27_8_A`…) ; non reconnus avant la v5, ils faisaient énumérer chaque pays partenaire ou espèce (jusqu'à 12 904 séries pour `fish_ca_atl27`).

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

Statuts : `disponible` (série France ≥ 10 années depuis 2000 et dernière ≥ 2020) ; `disponible (série courte)` (série France présente mais critère §3.4 non rempli) ; `code changé` (code disparu, successeur vérifié) ; `à remplacer` (le code ne fournit pas la France ; remplaçant vérifié) ; `sans donnée FR` ; `structure inattendue` (réponse de forme non prévue ; aucun cas au 14/10).

**Bilan final (amorce v3, 14/10/2026, 66 statuts)** : 55 `disponible` ; 6 `disponible (série courte)` (`sdg_03_30` tabagisme 7 années, `sdg_04_40` PISA 9, `sdg_04_70` compétences numériques 3, `sdg_17_60` très haut débit 7, `sdg_15_50` érosion 4, `sdg_11_32` imperméabilisation 6 : enquêtes non annuelles ou récentes, D17) ; 2 `code changé` (`sdg_05_60` → `sdg_05_61`, femmes cadres dirigeantes, 2012–2025 ; `sdg_15_10` → `sdg_15_11`, surface forestière, 2015–2023, série longue `for_area`) ; 2 `à remplacer` (`sdg_13_11` → `sdg_13_10`, émissions nettes de GES, 1990–2024 ; `sdg_15_60` → `env_bio2`, indice des oiseaux communs **des milieux agricoles**, 1990–2021 : `env_bio3` n'a que l'agrégat UE, et l'indice de tous les oiseaux communs relève d'une source nationale) ; 1 `sans donnée FR` (`sdg_10_20`, dispersion régionale du revenu, à recalculer depuis `nama_10r_2hhinc` si l'indicateur est gardé).

## 10. Catalogues Eurostat (phase 2)

### 10.1 Fichiers produits par le robot

| Fichier | Contenu |
|---|---|
| `catalogues/eurostat_jeux_catalogue.csv` | **Niveau 1** : un code du TOC par ligne (jeux `dataset` et tableaux `table`, dédoublonnés par code). Colonnes de la charte §5.3 (`source`, `serie_id` = code du jeu, `libelle` (fr), `unite` (vide au niveau 1), `frequence`, `geo` (vide), `premiere_periode`, `derniere_periode`, `derniere_maj`, `theme_source` (chemin principal des dossiers), `dimension_v0`, `candidat`, `commentaire` (= motif)) puis : `code_jeu`, `libelle_en`, `type`, `nb_valeurs`, `derniere_modif_structure`, `theme_codes`, `autres_chemins` (autres emplacements dans le TOC), `dossier_prioritaire`, `dimensions_v0_secondaires`, `methode_etiquette` (`mots-clés`, `objectif ODD NN`, `dossier …`, `aucun mot-clé`), `filtre_toc` (`retenu` / `exclu : …` / `hors filtre : …`), `motif_candidat`, et le résultat du niveau 2 : `statut_niveau2` (`ok`, `sans_donnee_fr`, `sans_dimension_geo`, `structure_introuvable`, erreurs), `nb_series_fr`, `nb_series_candidates`, `structure_fr` (rôle de chaque dimension, ex. `unit (2) [unité] ; sex→T (3) [ventilation] ; icd10 (80) [contenu]`). |
| `catalogues/eurostat_series_catalogue.csv` | **Niveau 2** : une ligne par série France **lue dans une réponse de l'API** (aucune combinaison théorique). Colonnes §5.3 (`serie_id` = code du jeu + filtres de l'API Statistics, directement réutilisable : `sdg_01_10?freq=A&age=TOTAL&unit=PC&geo=FR`) puis `code_jeu`, `type_ligne` (`defaut` ou `ventilation`), `ventilation` (dimension ventilée), `libelles_modalites`, `unite_code`, `unites_disponibles`, `nb_points`, `nb_annees`, `derniere_valeur`, `drapeaux` (drapeaux Eurostat et nombre d'occurrences depuis 2000, ex. `b:2 ; p:1`), `modalites_ventilation` (ligne de ventilation : `modalité:première-dernière:nb_années` pour chaque modalité), `jeu_source`, `date_verification`. `candidat` vaut `oui` / `non` (éligibilité §3.4, motif dans `commentaire`) pour une ligne `defaut`, `ventilation` pour une ligne de ventilation (D21). **Toujours compressé** : `eurostat_series_catalogue.csv.gz` (1,6 Mo au 14/10 ; lisible directement par pandas). |
| `catalogues/eurostat_series_catalogue_non.csv.gz` | **Séries écartées par une règle de périmètre** (D26 : catalogues scindés candidats / écartés) : mêmes colonnes, `candidat = non`, motif en tête de `commentaire` (v5 : `secteur_hors_menages : secteur S11 (ni l'ensemble de l'économie S1, ni les ménages S14/S14_S15)`). Les jeux écartés au niveau 1 gardent leur motif dans le catalogue des jeux (`motif_candidat`) ; les séries non éligibles au §3.4 (moins de 10 années…) restent dans le catalogue principal, car D17 admet les indicateurs non annuels. |
| `catalogues/eurostat_dossiers_toc.csv` | Une ligne par **emplacement** de dossier du TOC (un même code peut figurer à plusieurs endroits ; les deux racines portent le code `data`) : `code_dossier`, `titre_en`, `titre_fr`, `profondeur`, `chemin`, `chemin_codes`, `nb_jeux` (codes de jeux et de tableaux rangés dessous, toutes profondeurs), `nb_jeux_filtres` (dont retenus par les filtres de dates), `nb_candidats`. |
| `catalogues/eurostat_bilan.json` | Volumes du dernier passage (TOC, filtres, candidats par dimension et par dossier, statuts du niveau 2, séries par dimension). |
| `catalogues/eurostat_etat_collecte.json` | État du script reprenable : version et date de chaque étape, statut et durée de chaque jeu traité au niveau 2, historique des passages (requêtes, nouveaux essais, octets). |
| `docs/sources/eurostat_amorce_prototypes.csv` | Statut des 66 séries des prototypes (§9). |
| `journaux/collecte_<horodatage>_collecte_eurostat.py.log` | Journal d'exécution de chaque passage (une ligne par jeu au niveau 2). |

### 10.2 Niveau 1 : filtres, étiquetage, candidature

Source : TOC anglais (dates et hiérarchie, §6 n° 3) et TOC français (titres). Logique : `src/pipeline/catalogue_eurostat.py` (`construire_catalogue_jeux`, `etiqueter`, `bilan_dossiers`).

1. **Filtres de dates** (fiche M02) : `filtre_toc = retenu` si fin des données ≥ 2020 et début ≤ 2010 ; `exclu` si fin < 2020 ou dates absentes ; `hors filtre` si début > 2010.
2. **Dossier prioritaire** (§7) : préfixe du code, puis titre d'un dossier de l'un des chemins.
3. **Étiquette `dimension_v0`** par mots-clés anglais et français (liste `MOTS_CLES`, frontières de mots, sans accents) : score 2 par dimension trouvée dans la **partie principale du titre** (avant « by » / « par »), 0,5 dans la partie « by … » (ventilations), 1 dans le chemin principal des dossiers ; la meilleure dimension est retenue (égalités départagées du plus spécifique au plus général : égalités, sécurité, démocratie, liens, logement, santé, éducation, travail, niveau de vie, planète) ; les autres dimensions de score ≥ 1 vont dans `dimensions_v0_secondaires`. Sans aucun mot-clé : repli sur l'objectif ODD (`sdg_NN` ou dossier « Goal NN »), puis sur le dossier prioritaire (ex. `revenus_conditions_de_vie` → `niveau_de_vie`, `numerique` et `culture` → `education`) ; depuis la v5, les jeux de population sans mot-clé (effectifs, structure par âge, naissances, fécondité, mariages, divorces : 47 jeux candidats) sont étiquetés **`contexte`** (dénominateurs et séries de contexte ; la table `docs/methodo/31_correspondance_v0_v1.csv` range `contexte` hors grille). Mots-clés R-D ajoutés en v5 (`R&D`, `GERD`, `research and development`, `DIRD`) avec l'étiquette `education` (gel 1, A5). **L'étiquette est une orientation pour le moissonnage, pas un classement** : la grille v1 (M03) et les fiches indicateurs (M05) la reprendront.
4. **Candidature** (`candidat`, motif dans `motif_candidat`), dans cet ordre :
   - `non` : jeux sans France par construction (§6 n° 15) ;
   - `non` (v5, D26) : **statistiques d'entreprises et d'échanges extérieurs, même dans un dossier prioritaire** (liste `PREFIXES_ENTREPRISES_ECHANGES`, motif « entreprises ou échanges extérieurs (…) ») : démographie des entreprises (`bd_*`, `met_bd*`, `urt_bd*`), statistiques structurelles d'entreprises (`sbs_*`), filiales étrangères (`fats_*`), balance des paiements et position extérieure (`bop_*`, dont `bop_its6_det`, `bop_rem6`), commerce extérieur (`ext_*`, biens culturels `cult_trd*`), enquête sur le coût de la main-d'œuvre par activité ou région (`lc_n*`, `lc_r*`) et pondérations de l'indice du coût du travail (`lc_lci_r2_cow`, `lc_lci_r2_itw`), enquêtes TIC auprès des entreprises et secteur des TIC (`isoc_ci_in_e*`, `isoc_ci_cm_p*`, `isoc_ci_it_e*`, `isoc_ci_ra*`, `isoc_cimob*`, `isoc_ec_e*`, `isoc_eb_*`, `isoc_ske_*`, `isoc_cisce*`, `isoc_cicce*`, `isoc_ciweb*`, `isoc_cism*`, `isoc_e_dii*`, `isoc_bde15*`, `isoc_ic_bi*`, `isoc_env_ict*`, `isoc_it_ict*`, et tout autre `isoc_*` dont le titre anglais contient « enterprise », « NACE », « ICT sector » ou « international trade »), secteurs de haute technologie (`htec_*`), groupes multinationaux (`egi_*`), R-D des entreprises par activité ou taille (`rd_p_bemp*`, `rd_p_perssize`), tableaux entrées-sorties (`naio_*` : « Tableaux des emplois », emploi lié aux exportations). Les jeux `isoc_*` des particuliers et des ménages restent candidats ;
   - `non` : **domaines hors périmètre**, hors dossiers prioritaires — statistiques sectorielles qui ne décrivent ni la situation de la population ni l'environnement : production, prix et comptes agricoles, structure des exploitations, viticulture, pêche (débarquements, flotte, aquaculture), produits, échanges et comptes de la sylviculture, transports fluvial, maritime, aérien, ferroviaire (hors sécurité) et par oléoduc, parc et trafic routiers, transport intermodal de marchandises, tourisme, titres de séjour (liste `PREFIXES_HORS_PERIMETRE`) ; exception : véhicules à émission nulle (`road_eq*_zev`) ;
   - `oui` (v5, D26) : **pêche et sylviculture réintégrées** en `planete` (liste `REINTEGRES_PLANETE`, motif « pêche et sylviculture réintégrées (D26) : … ») si les filtres de dates le permettent : captures par zone de pêche (`fish_ca_*`), surfaces boisées (`for_area*`), volume de bois sur pied (`for_vol*`, stock), prélèvements de bois rond (`for_remov`, `for_owner`) ; la production (aquaculture, débarquements, produits du bois), les prix et les comptes restent exclus ;
   - `non` : projections (fin des données > 2027) ;
   - `non` : tableaux (`table`), sauf les indicateurs ODD `sdg_*` (§6 n° 10) ;
   - `non` : jeux infra-annuels (une version annuelle existe en général) ;
   - `oui` : jeu retenu par les filtres et rangé dans un dossier prioritaire ;
   - `oui` : jeu retenu par les filtres dont **un mot-clé figure dans la partie principale du titre** (un mot-clé trouvé seulement dans le chemin ou dans la ventilation donne l'étiquette, pas la candidature) ;
   - `oui` par **rattrapage** : jeu « hors filtre » (début > 2010) pouvant encore avoir ≥ 10 années jusqu'à sa fin (charte §3.4) et pertinent (dossier prioritaire ou mot-clé du titre) — sans quoi l'AROPE 2021 (`sdg_01_10`, `ilc_pecs01`) et de nombreux indicateurs ODD seraient perdus ;
   - `non` sinon (motif : filtre de dates, ou aucun mot-clé ni dossier prioritaire).
5. Historique des règles : v1 (premier passage, essai) ; v2 (tableaux ODD inclus, racine principale repérée par son titre) ; v3 (jeux hors France et projections exclus, mots-clés affinés) ; v4 (candidature par mot-clé du titre principal, domaines hors périmètre, bilan des dossiers par emplacement) ; **v5** (14/10, D26 et contrôle qualité : entreprises et échanges extérieurs exclus même dans les dossiers prioritaires, pêche et sylviculture réintégrées, `contexte` pour la population, mots-clés R-D, faux amis « Tableaux des emplois », « non satisfaits », « sages-femmes » ; version de l'étape `niveau1` = 6 dans le script).

### 10.3 Niveau 2 : séries France vérifiées

Pour chaque jeu candidat (ordre : échantillon de contrôle, puis indicateurs ODD, puis le reste) :

1. **Structure** : `dataflow/ESTAT/{CODE}?references=descendants&detail=referencepartial` (§5). Sans dimension `geo` : `sans_dimension_geo`. `FR` présent → `geo=FR` ; sinon `FX` (métropole, signalé dans le commentaire de chaque série) ; sinon `sans_donnee_fr` (sans requête de données).
2. **Plan de requêtes** JSON-stat (`lang=fr`, `sinceTimePeriod=2000`, `geo` et `freq=A` fixés) : si le cube majoré (modalités × périodes) dépasse 300 000 cellules, les dimensions ayant un code total (hors unité et ventilations) sont fixées à ce total, puis la plus grande dimension restante est découpée en paquets (≤ 40 codes par requête, ≤ 60 requêtes) ; sur `413 EXTRACTION_TOO_BIG`, nouveau plan plus fin (50 000 cellules, ≤ 120 requêtes) ; réponse asynchrone : jusqu'à 3 nouvelles tentatives espacées de 60 s. Requêtes séquentielles, pause de 0,2 s, nouvel essai avec attente croissante (10 s, 30 s, 90 s…) sur 429, 5xx ou coupure, en-tête `Retry-After` respecté.
3. **Rôle des dimensions** (réponse France) : `freq` et `geo` fixés ; `unit` choisie série par série (préférence, v5 : pourcentages et taux, puis par habitant, années et ratios, autres niveaux (euros, volumes…), indices simples, niveaux en milliers ou millions ; puis **indices relatifs à l'UE ou base 100 d'une année** — `PC_EU27_2020…`, `EUR_HAB_EU27_2020`, `PPS_HAB_EU27_2020`, `I15`, `I20`, `CLV_I10`, `INX…` — qui ne sont retenus que si aucune unité absolue n'existe ; variations (`PCH…`) en dernier ; à rang égal, l'année de référence la plus récente : `CLV20` avant `CLV15`) ; `age` fixé à `TOTAL` ou à la classe la plus large (à la naissance pour une espérance de vie) ; une dimension ayant un code total (`TOTAL`, `T`, `_T`, `TOT`, `ALL`, `TOTAL_HH`, `POP` pour `wstatus`, `IND_TOTAL` pour `ind_type`, et depuis la v5 `WORLD` / `WRL_X_REP` pour `partner`, `F00` pour `species`, `0` ou la grande zone du jeu pour `fishreg`) est fixée à ce total ; une dimension à une seule modalité est fixée ; une dimension sans aucune modalité (cube vide) n'a pas de rôle et ne produit aucune série ; les autres sont du **contenu** (chaque modalité = un indicateur distinct ; `icd10`, causes de décès, est toujours du contenu).
4. **Lignes** : une ligne `defaut` par combinaison des dimensions de contenu (autres dimensions à leur défaut, unité préférée parmi celles qui ont des données) ; **ventilations conservées (D21)** : pour chaque dimension de ventilation (`sex`, `age` hors âges détaillés année par année, `quantile`, `quant_inc`, `incgrp`, `quant_expn`, `hhtyp`, `hhcomp`, `deg_urb`, `ind_type`, `isced*`, et depuis la v5 **`citizen` (nationalité) et `c_birth` (pays de naissance)** pour les écarts selon l'origine, gel 1 A8), une ligne `ventilation` listant les modalités hors défaut ayant des données, avec la couverture de chacune (`modalites_ventilation`) ; son `serie_id` répète le paramètre ventilé (`sex=M&sex=F`).
5. **Éligibilité** (charte §3.4) : `candidat = oui` si ≥ 10 années renseignées depuis 2000 **et** dernière période ≥ 2020, sinon `non` avec motif ; les drapeaux (`b` rupture, `p` provisoire, `e` estimé, `u` peu fiable…) sont comptés dans `drapeaux`.
6. **Règles appliquées au catalogue écrit, sans requête** (v5, à chaque passage) : (a) une seule vérification par jeu (la plus récente, cas des jeux rafraîchis) ; (b) retrait des jeux qui ne sont plus candidats ; (c) étiquette `dimension_v0` et chemin `theme_source` **resynchronisés** sur le niveau 1 (avant la v5, les séries gardaient l'étiquette de leur premier traitement : 2 832 lignes de 82 jeux étaient en décalage) ; (d) **comptes par secteur institutionnel** (`nasa_10_f_*`, `naidsa_10_f_*`, `nasa_10_nf_tr`, `nasa_10_ki`) : seuls l'ensemble de l'économie (`S1`) et les ménages (`S14`, `S14_S15`) sont gardés, y compris pour le secteur de contrepartie (`sector2` de `nasa_10_f_cp`) ; les autres secteurs vont au fichier des séries écartées, motif `secteur_hors_menages`.
7. **Recalcul ciblé** (v5) : une révision des règles du niveau 2 (`REGLES_NIVEAU2` dans le script) ne refait que les jeux concernés, repérés dans le catalogue écrit : jeux dont l'unité retenue change avec la règle actuelle (`jeux_a_refaire_unites`, 16 jeux le 14/10 : `nama_10_pc`, `nama_10_gdp`, `prc_hicp_aind`…), jeux dont une série porte une dimension au traitement révisé (`jeux_a_refaire_dimensions` : partenaire, nationalité, pays de naissance, espèces et zones de pêche, 176 puis 24 jeux).

### 10.4 Bilan final (14/10/2026, règles v5)

**Passages du robot** (workflow « Collecte », branche `m02-eurostat`) : n° 1 essai (13/10, run 38404425489, 40 jeux) ; n° 2 complet (13/10, run 38405905176, règles v2 : 2 490 jeux en 220 min, 5 185 requêtes) ; n° 3 (13/10, run 38412944475, niveau 1 v4) ; n° 2 et 3 en échec sur l'amorce (§6 n° 17) ; **n° 4** (14/10, run 38487815549 : amorce v3, niveau 1 v5, révision des unités, 39 jeux, 279 requêtes, 2,9 min) ; **n° 5** (run 38488281026 : niveau 1 v6, partenaire et origine, 174 jeux, 350 requêtes, 3,8 min) ; **n° 6** (run 38488832255 : partenaire `WRL_X_REP`, 24 jeux, 48 requêtes, 0,7 min). Aucun nouvel essai réseau, aucune erreur. Chiffres ci-dessous : `catalogues/eurostat_bilan.json` du passage n° 6.

| Élément | Valeur |
|---|---|
| TOC (anglais) | 12 234 entrées : 6 649 jeux, 911 tableaux, 1 878 codes de dossiers ; 7 560 codes au catalogue des jeux |
| Retenus par les filtres de dates (fin ≥ 2020, début ≤ 2010) | 3 053 (tableaux compris) |
| **Jeux candidats (niveau 1 v5)** | **1 816** (1 739 jeux et 77 tableaux ODD ; 381 par rattrapage) — 1 897 en v4 |
| Candidats par dimension v0 | travail 387, éducation 381, niveau de vie 301, planète 264, santé 197, logement et cadre de vie 113, sécurité et confiance 57, `contexte` 47, égalités 44, liens et bien-être 17, démocratie 8 |
| Candidats par dossier prioritaire | revenus et conditions de vie 338, éducation 300, marché du travail 286, santé 191, ODD 117, environnement 109, population 70, énergie 62, numérique 27 (92 en v4), criminalité 24, culture 19, sécurité des transports 18, qualité de vie 16, comptes nationaux 10 ; hors dossiers (mot-clé du titre) 229 |
| Non candidats par motif | fin < 2020 ou dates absentes 1 663 ; domaine hors périmètre 1 126 ; début > 2010 sans rattrapage 895 ; tableaux 830 ; **entreprises ou échanges extérieurs 460** (dont 155 dans un dossier prioritaire : statistiques structurelles 107, tableaux entrées-sorties 50, démographie des entreprises 45, commerce extérieur 35, haute technologie 31, balance des paiements 27, coût de la main-d'œuvre 41, TIC des entreprises 90…) ; infra-annuels 346 ; pays hors UE 176 ; aucun mot-clé ni dossier 150 ; mot-clé seulement dans le chemin ou la ventilation 57 ; projections 41 |
| Réintégrés (pêche et sylviculture, D26) | 14 jeux : `fish_ca_main`, `fish_ca_atl21`, `fish_ca_atl27`, `fish_ca_atl34`, `fish_ca_atl37`, `fish_ca_atl41`, `fish_ca_atl47`, `fish_ca_ind51`, `for_area`, `for_area_efa`, `for_vol`, `for_vol_efa`, `for_remov`, `for_owner` ; 33 séries par défaut dont 21 éligibles (ex. captures françaises toutes zones `fish_ca_main?…species=F00&fishreg=0…`, 2000–2025, tonnes poids vif) |
| Statuts du niveau 2 (1 816 jeux) | `ok` 1 722 ; `sans_dimension_geo` 58 (villes `urb_*`, régions métropolitaines `met_*`, empreintes `env_ac_*fp`, bassins `sdg_14_*`…) ; `sans_donnee_fr` 36 (agrégats UE seulement : `env_bio3`, `sdg_13_11`, `sdg_15_60`, `sdg_15_61`… ; régions sans niveau national) ; restants 0 |
| **Catalogue des séries** | 56 210 lignes (1,6 Mo compressé) : **42 538 séries par défaut, dont 31 375 éligibles** (§3.4), et **13 672 lignes de ventilation** ; 1 720 jeux avec séries ; 100 % `geo=FR` ; aucun `serie_id` en double |
| Séries par défaut / éligibles par dimension v0 | planète 21 057 / 15 567 ; niveau de vie 9 233 / 6 054 ; santé 5 944 / 5 308 ; éducation 3 006 / 1 913 ; travail 1 704 / 1 223 ; sécurité et confiance 737 / 629 ; logement et cadre de vie 312 / 291 ; `contexte` 277 / 241 ; égalités 121 / 116 ; liens et bien-être 78 / 4 ; démocratie 69 / 29 |
| Jeux ayant au moins une série éligible | travail 331, niveau de vie 248, éducation 228, planète 191, santé 154, logement 101, sécurité 45, égalités 41, `contexte` 38, démocratie 8, liens et bien-être 4 |
| Lignes de ventilation (D21) par dimension ventilée | âge 7 390, sexe 5 156, `isced11` 255, composition du ménage 203, degré d'urbanisation 150, type d'individus 130, `iscedf13` 124, quintile de revenu 110, **nationalité 72, pays de naissance 71** (nouveau, A8), type de ménage 10, quantile 1 |
| Séries écartées (`eurostat_series_catalogue_non.csv.gz`) | 20 114, motif `secteur_hors_menages` : `nasa_10_f_cp` 3 745, `nasa_10_f_bs` 3 255, `nasa_10_f_tr` 3 241, `nasa_10_f_gl` 3 192, `nasa_10_f_oc` 3 192, `naidsa_10_f_bs` 2 858, `nasa_10_nf_tr` 624, `nasa_10_ki` 7 |
| Unités | 0 série dont l'unité changerait avec la règle v5 ; 180 séries gardent un indice (`I20`, `I15`, `INX`…) faute d'unité absolue (seules des variations `PCH` existent : `lc_lci_r2_a`, `nama_10_lp_a21`, `nrg_ind_difec`…) |
| Amorce (66 séries des prototypes) | 55 disponibles, 6 séries courtes, 2 codes changés, 2 à remplacer, 1 sans donnée FR (détail §9) |

**Effet des corrections du 14/10** (catalogue des séries) : 191 707 lignes au 13/10 → 56 210 (−135 497) ; séries éligibles 95 836 → 31 375. Principales réductions : statistiques d'entreprises et d'échanges extérieurs (102 836 lignes retirées au passage n° 4 avec les jeux devenus non candidats et les 16 jeux refaits pour l'unité ; dont `bop_its6_det` 27 705 et `bd_9fh_sz_cl_r2` 13 509), comptes par secteur hors ménages (20 114 lignes déplacées vers le fichier des écartées), tableaux entrées-sorties (≈ 1 100 séries), pays d'origine des étudiants mobiles et pays partenaires (≈ 6 000 séries par défaut remplacées par le total), espèces et sous-zones de pêche (20 753 séries au passage n° 4 ramenées à 8 au passage n° 5). Gains : 12 jeux de pêche et de sylviculture (les surfaces boisées `for_area*` étaient déjà candidates), 11 jeux de R-D (`rd_e_*`, `rd_p_persocc`, `rd_p_persqual11`, `rd_p_perssci`, `gba_tncoor`), 143 lignes de ventilation par origine.

**Contrôle qualité du niveau 2** (14/10, tirage fixe de 20 séries éligibles et 20 écartées par dimension v0, script hors ligne) : les séries écartées le sont toutes pour une raison juste (moins de 10 années, dernière période < 2020 : enquêtes quinquennales, séries historiques arrêtées, modules ponctuels EU-SILC) ; toutes les séries sont `geo=FR` ; les libellés et périodes sont cohérents. Erreurs systématiques trouvées et corrigées : tableaux entrées-sorties étiquetés `travail` (« Tableaux des emplois »), pays d'origine et pays partenaires énumérés, espèces de poissons énumérées, comptes financiers ventilés par secteur de contrepartie, besoins de soins non satisfaits étiquetés `liens_bien_etre`, personnel infirmier et sages-femmes étiqueté `egalites`. Restent des volumes importants mais légitimes (bilans énergétiques `nrg_cb_*`, pesticides par culture `aei_pestuse`, causes de décès `hlth_cd_*`), à regrouper par concept en M05.

### 10.5 Limites connues

- **Étiquetage par mots-clés** : une dimension principale par jeu, déterminée surtout par le titre ; la même étiquette est recopiée sur toutes les séries du jeu, y compris quand une modalité de contenu relèverait d'une autre dimension (ex. `sdg_16_10`, homicides, et `sdg_11_40`, tués sur la route, étiquetés `sante` ; la table v0→v1 corrige le second). Les catalogues restent en **dimension v0** ; le passage en v1 est fait par la long-list (M05).
- **Liens et bien-être** : 4 séries éligibles seulement ; les modules EU-SILC de bien-être (`ilc_pw*` : satisfaction, confiance, bonheur) n'ont que 1 à 7 années pour la France (2013, 2018, 2021–2025) et sont marqués non éligibles : ils relèvent de D17 (indicateurs non annuels), que la long-list applique.
- **Jeux à beaucoup de séries de contenu** (bilans énergétiques, émissions par polluant × secteur, causes de décès…) : toutes gardées (aucune limite a priori), à regrouper par concept en M05.
- **Dimensions sans code total reconnu** (ex. `nace_r2` dont le total s'appelle `B-S_X_O`, `indic_*`, `c_regis` des accidents aériens) : énumérées comme contenu.
- **Choix de l'unité** : heuristique ; les autres unités disponibles figurent dans `unites_disponibles`. Défaut repéré au contrôle qualité, non corrigé : à rang égal, un niveau monétaire peut passer avant une grandeur physique (`for_area_efa` : `MIO_EUR` plutôt que `THS_HA` pour une surface boisée).
- **Découpage limité** à 60 (puis 120) requêtes par jeu : pour les jeux les plus volumineux, des modalités peuvent ne pas avoir été lues (signalé dans le message du jeu et dans `structure_fr`).
- **Jeux infra-annuels et tableaux non candidats** (sauf ODD) : à réexaminer si un indicateur n'existe qu'en trimestriel ou en tableau.
- **France métropolitaine** (`FX`) prise seulement quand `FR` est absent.
- **Pas de raccordement** des séries ODD courtes à leurs jeux sources plus longs (D16) : le `jeu_source` est noté pour le faire en M05.

### 10.6 Relancer la collecte, rafraîchissement

- **Automatiquement** : tout push sur la branche `m02-eurostat` qui modifie `scripts/` ou `src/` relance le workflow « Collecte » (cible `collecte_eurostat.py`) ; une fois la branche fusionnée, le passage **mensuel** du 1er du mois sur `main` exécute le script. Les résultats, l'état et le journal sont commités par le robot (`git pull --rebase origin <branche>` pour les récupérer).
- **Rafraîchissement (péremption, v5)** : le niveau 1 (TOC) et l'amorce sont refaits s'ils datent de plus de **30 jours** (le passage mensuel reprend donc les nouveaux jeux, les retraits et les changements de titres) ; un jeu du niveau 2 vérifié il y a plus de **90 jours** est revérifié, au plus **600 jeux par passage**, les plus anciens d'abord (≈ 5 s par jeu, soit ≈ 50 min ; les 1 816 jeux vérifiés le 13 et le 14/10 seront donc rafraîchis sur les passages de janvier à avril 2027). Les nouvelles séries d'un jeu remplacent les anciennes (on ne garde que la vérification la plus récente de chaque jeu) ; si la revérification échoue (erreur réseau), la vérification précédente est gardée et l'échec noté dans l'état (`rafraichissement_echoue`).
- **À la demande** : `python scripts/actions.py lancer --branche m02-eurostat --cible collecte_eurostat.py`, puis `python scripts/actions.py suivre --run <id>` et `python scripts/actions.py journal --branche m02-eurostat`.
- **Refaire une étape** : augmenter sa version dans `ETAPES` (ex. `"niveau1": 7`) ; refaire le niveau 1 rouvre le niveau 2 (retrait des jeux qui ne sont plus candidats, traitement des seuls nouveaux). **Changer une règle du niveau 2 sans tout refaire** : augmenter `REGLES_NIVEAU2` et, si la règle porte sur une dimension, l'ajouter à `REVISIONS_DIMENSIONS` (les jeux concernés sont repérés dans le catalogue écrit et refaits seuls) ; une règle d'unité est détectée automatiquement. **Tout refaire** : augmenter la version de `niveau2` (repart de zéro, ≈ 4 h) ou supprimer `catalogues/eurostat_etat_collecte.json`.
- **Variables d'environnement** : `EUROSTAT_DUREE_MAX_MINUTES` (défaut 270 ; arrêt propre et reprise au passage suivant), `EUROSTAT_NIVEAU2_MAX_JEUX` (0 = sans limite), `EUROSTAT_ETAPES` (ex. `niveau1,niveau2`), `EUROSTAT_PEREMPTION_NIVEAU1_JOURS` (30), `EUROSTAT_PEREMPTION_JOURS` (90, niveau 2), `EUROSTAT_RAFRAICHIR_MAX_JEUX` (600).
