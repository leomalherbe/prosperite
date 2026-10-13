# Fiche source — Eurostat

Rédigée par l'agent de la mission M02 (phase 1), le 2026-10-13. Toutes les informations ci-dessous ont été lues le 13/10/2026 dans la documentation officielle d'Eurostat ou dans des réponses réelles de l'API obtenues par l'outil de lecture de page (WebFetch). Ce qui n'a pas pu être vérifié est signalé « non vérifié » ou « non trouvé ».

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

Autres services du catalogue (WADL) : `…/catalogue/metabase.txt.gz` (« metabase » : liste compressée des jeux, dimensions et codes — format non vérifié, à examiner en phase 2, pourrait éviter des centaines d'appels `datastructure`) ; `…/catalogue/rss/{langue}/statistics-update.rss` (mises à jour) ; `…/catalogue/dcat/{agence}{/type}` (DCAT-RDF) ; `…/catalogue/jsonld/{agence}/{id}/{version}` ; **`…/catalogue/relations/{agence}/{id}/{version}`** — vérifié : `relations/ESTAT/SDG_08_10/1.0?lang=en` renvoie `{"derived": {}, "source": {"nama_10_pc": "Gross domestic product (GDP) and main components per capita - annual data"}}`, soit le **jeu source** d'une vue SDG.

### 2.2 API Statistics 1.0 (JSON-stat 2.0)

Modèle d'URL : `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{code}?{paramètres}`. Exemple vérifié : `…/statistics/1.0/data/sdg_08_10?geo=FR&lang=fr&time=2022`.

| Paramètre | Valeurs | Remarques (documentation officielle, page « API Statistics ») |
|---|---|---|
| `format` | `JSON` | Seule valeur possible, facultatif |
| `lang` | `EN`, `FR`, `DE` | Défaut `EN`. Le projet utilise `lang=fr` |
| `{dimension}={code}` | ex. `geo=FR`, `unit=PC`, `sex=T`, `age=Y16-64` | Codes et valeurs insensibles à la casse ; ordre libre ; **plusieurs valeurs = paramètre répété** (`sex=M&sex=F`) ; toute dimension du jeu est filtrable |
| `time` (ou `time_period`) | ex. `time=2022` | Période(s) précise(s), répétable |
| `sinceTimePeriod` / `untilTimePeriod` | ex. `sinceTimePeriod=2000` | Bornes inférieure / supérieure ; seule combinaison de paramètres temporels autorisée |
| `lastTimePeriod` | entier N | « a numeric value counting down until the TIME_PERIOD dimension values are included » : les N dernières périodes. La documentation ne dit pas si ce sont les N dernières **avec donnée** pour la sélection filtrée — à tester en phase 2 (non vérifié) |
| `geoLevel` | `aggregate`, `country`, `nuts1`, `nuts2`, `nuts3`, `city` | Incompatible avec `geo` (erreur 400) ; inutile en v1 (France seule) |

Codes d'erreur : `100` aucun résultat (HTTP 400 si résultat vide, 404 si ressource absente) ; `140` erreur de syntaxe (400) ; `150` erreur sémantique, par ex. code de modalité inexistant (400) ; `500` erreur interne. Corps d'erreur JSON du type `{"error":{"status":"400","label":"…"}}`.

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

- Jeu complet via SDMX 2.1 : `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{CODE}?format=TSV&compressed=true` (forme indiquée par la fiche de mission). La documentation des requêtes de structure précise que `compressed=true` renvoie un fichier `.gz` ; celle des requêtes de données dit seulement que les réponses peuvent être obtenues « in .gz compressed format » sans nommer la valeur du paramètre : **à confirmer lors de la première exécution sur GitHub Actions** (non vérifiable avec WebFetch, qui ne décompresse pas).
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

Vérifiée sur `…/sdmx/2.1/datastructure/ESTAT/SDG_08_10` (résumé fidèle : `tests/fixtures/eurostat/datastructure_SDG_08_10_resume.json`). Message SDMX-ML 2.1 (XML) :
- en-tête : `ID`, `Prepared` (horodatage), `Sender id="ESTAT"` ;
- `DataStructure` `id="SDG_08_10"`, `agencyID="ESTAT"`, `version="125.0"`, `isFinal="true"` ;
- `DimensionList` : dimensions **ordonnées** par `position` — `freq` (1, liste `ESTAT:FREQ(3.9)`), `unit` (2, `UNIT(82.0)`), `na_item` (3, `NA_ITEM(30.1)`), `geo` (4, `GEO(28.0)`) ; chaque dimension renvoie à un concept et à une liste de codes **par référence** ;
- `TimeDimension` `TIME_PERIOD` (position 5, type `ObservationalTimePeriod`) ;
- `AttributeList` : `OBS_FLAG` (liste `OBS_FLAG(1.39)`) et `CONF_STATUS` (liste `CONF_STATUS(1.2)`), conditionnels, rattachés à la mesure ;
- `MeasureList` : `PrimaryMeasure` `OBS_VALUE` (type `Double`) ;
- **les listes de codes ne sont pas incluses** : il faut les demander séparément (`…/codelist/ESTAT/UNIT?format=TSV&lang=fr`) ou utiliser `…/dataflow/ESTAT/{CODE}?references=descendants`. La DSD donne toutes les modalités **possibles** de la liste de codes (souvent des milliers pour `geo` ou `unit`) ; les modalités **réellement présentes** dans le jeu sont dans la contrainte de contenu (`…/contentconstraint/ESTAT/{CODE}`) ou, pour la France, dans la réponse JSON-stat filtrée `geo=FR`.

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

## 7. Dossiers prioritaires dans l'arborescence du TOC

*Section complétée à la sous-tâche 3 (voir plus bas).*

## 8. Fixtures enregistrées (`tests/fixtures/eurostat/`)

| Fichier | Origine | Fidélité |
|---|---|---|
| `toc_extrait_en.txt` | 30 premières lignes de `…/catalogue/toc/txt?lang=en` (13/10/2026) | Lignes recopiées à l'identique par WebFetch, en deux morceaux par ligne (titre / reste), puis réassemblées avec de vraies tabulations |
| `toc_extrait_fr.txt` | 8 premières lignes de `…/catalogue/toc/txt?lang=fr` (13/10/2026) | Idem ; pour les lignes de dossiers, le dernier champ `" "` a été restitué par analogie avec le TOC anglais (WebFetch l'avait omis) |
| `sdg_08_10_FR_2022_fr.json` | `…/statistics/1.0/data/sdg_08_10?geo=FR&lang=fr&time=2022` | Reconstitué champ par champ (valeurs exactes) ; `extension.description` et les annotations à titre long (`DISSEMINATION_DOI_XML`, `DISSEMINATION_PRESENTATIONS`, liens `href`) omis |
| `sdg_01_10_FR_fr.json` | `…/statistics/1.0/data/sdg_01_10?geo=FR&lang=fr` (toutes périodes) | Reconstitué champ par champ : `value`, `status`, `id`, `size`, index et libellés des modalités, `positions-with-no-data` exacts ; libellés des dimensions et une partie des annotations omis |
| `sdmx_SDG_08_10_FR_depuis2018.tsv` | `…/sdmx/2.1/data/SDG_08_10/A..B1GQ.FR?format=TSV&startPeriod=2018` | Recopié à l'identique (3 lignes) |
| `datastructure_SDG_08_10_resume.json` | `…/sdmx/2.1/datastructure/ESTAT/SDG_08_10` | **Résumé fidèle** au format JSON (le XML brut n'est pas restituable par WebFetch) |
| `codelist_OBS_FLAG_fr.tsv` | `…/sdmx/2.1/codelist/ESTAT/OBS_FLAG?format=TSV&lang=fr` | 42 lignes recopiées (une éventuelle ligne d'en-tête n'a pas été restituée) |

## 9. Statut des séries des prototypes

*Section complétée à la sous-tâche 2 (voir `docs/sources/eurostat_amorce_prototypes.csv`).*
