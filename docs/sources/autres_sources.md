# Sources de données hors INSEE et Eurostat — fiches par source (mission M04, tâche T1)

Version phase 1 — 13 octobre 2026 — agent de mission M04. Document de travail : **à valider par Léo et la session mère** avant la phase 2 (T3, indicateurs candidats).
Tableau récapitulatif : `docs/sources/10_sources_inventaire.csv` (T2). Preuves de vérification : `docs/sources/verif_acces/` (voir §0.3).

---

## 0. Méthode, conventions et preuves

### 0.1 Niveaux (charte §3.5, décision D09)
- **Niveau 1** : API interrogeable par script (avec ou sans clé gratuite ; une clé se range dans les secrets GitHub, jamais dans le code).
- **Niveau 2** : pas d'API, mais **fichier CSV/XLSX (ou ZIP de CSV/XLSX) à URL stable** téléchargeable par script.
- **Exclu** : données lisibles seulement en PDF, en graphique ou en page web ; ou accès soumis à formulaire / inscription nominative sans API ; ou accès impossible à vérifier et sans alternative.

### 0.2 Fiabilité de la voie d'accès
- `verifie` : l'URL a été ouverte le 13/10/2026 et renvoie bien des données (JSON, CSV, XML SDMX, classeur ou archive identifiés).
- `probable` : la voie est documentée par le producteur et un point d'entrée voisin a été vérifié, mais l'accès aux données elles-mêmes n'a pas pu être testé (par exemple clé requise).
- `non_verifie` : l'URL n'a pas pu être ouverte ou n'a pas été trouvée ; la raison est donnée.

### 0.3 Comment la vérification a été faite (important pour relire ce document)
1. **Outil de lecture de page web (WebFetch)** : utilisé pour les pages des producteurs et les API qui l'acceptent (data.gouv.fr, Webstat, OCDE, OWID, Ademe, Banque mondiale pour les métadonnées). Il **respecte les `robots.txt`** : il est refusé par tous les portails Opendatasoft de l'État (`/api/` interdit à tout robot sauf Googlebot), par `static.data.gouv.fr`, par l'API de la BCE, par la DARES et par Resana. Il refuse aussi de recopier plus de 125 caractères verbatim (pas de fixture brute possible par ce biais).
2. **Robot GitHub Actions** : le script `scripts/collecte_sources.py` (cible `collecte_sources.py` du workflow « Collecte ») ouvre sans clé chaque URL de `docs/sources/verif_acces/urls.csv` et écrit :
   - `docs/sources/verif_acces/resultats.csv` : code HTTP, type de contenu, taille, nature détectée, verdict (`donnees`, `page_html`, `pdf`, `erreur`) ;
   - `docs/sources/verif_acces/extraits/<source>__<cle>.txt` : extrait lisible (début du texte, feuilles et premières lignes d'un classeur, contenu d'une archive, valeurs distinctes d'une colonne).
   Trois vagues ont été exécutées le 13/10/2026 ; **les colonnes `fiabilite_acces` du CSV d'inventaire renvoient à ces résultats**. Le script peut être relancé à tout moment (veille des liens) : `python scripts/actions.py lancer --branche m04-sources --cible collecte_sources.py`.
3. **Fixtures** : des réponses d'API réelles (issues du robot) sont copiées dans `tests/fixtures/<source>/` pour les tests hors ligne des futurs modules.

### 0.4 Points d'attention transversaux
- **Indices composites** (CPI, Freedom House, V-Dem, WGI, World Happiness, IDH…) : ce sont des **indicateurs agrégés** ; les retenir pose une question de double comptage avec les indicateurs élémentaires d'une même dimension. Ils sont signalés comme tels dans chaque fiche.
- **Source primaire ou relais** : quand OWID, l'OCDE ou la Banque mondiale redistribuent une série d'un autre producteur (V-Dem, RSF, Gallup, ONUDC…), la source primaire est indiquée ; le relais est souvent la voie la plus simple, mais il peut être en retard (cas RSF via OWID, arrêtée en 2021).
- **URL horodatées** : beaucoup de fichiers (data.gouv.fr, Citepa, SDES, Freedom House) changent d'URL à chaque édition. La voie stable est alors **l'API ou la page catalogue qui liste le fichier**, pas l'URL du fichier ; le script de collecte devra relire l'URL courante avant de télécharger.

---

## 1. Points d'entrée communs (documentés une fois)

### 1.1 Opendatasoft — API Explore v2.1 (nombreux portails publics français)
| Élément | Valeur |
|---|---|
| Portails vérifiés (robot, 13/10/2026) | `data.drees.solidarites-sante.gouv.fr` (265 jeux), `data.education.gouv.fr` (DEPP, 310), `data.enseignementsup-recherche.gouv.fr` (217), `odisse.santepubliquefrance.fr` (388), `data.ameli.fr` (51), `data.economie.gouv.fr` (617), `odre.opendatasoft.com` (187), `data.caf.fr` (210), `webstat.banque-france.fr` (catalogue seulement, voir §2.8) |
| Catalogue (JSON) | `GET https://<portail>/api/explore/v2.1/catalog/datasets?limit=<n>&where=<ODSQL>` → `total_count`, `results[]` (`dataset_id`, `metas.default.title`, `metas.default.modified`, `metas.default.records_count`, `attachments`, …) |
| Catalogue complet (CSV) | `GET https://<portail>/api/explore/v2.1/catalog/exports/csv?delimiter=%3B` → colonnes `datasetid`, `default.title`, `default.modified`, `default.records_count`, `default.publisher`, `default.license`, `default.theme`… |
| Enregistrements d'un jeu | `GET …/catalog/datasets/<dataset_id>/records?limit=100&where=…&select=…&order_by=…` (JSON paginé) |
| Export complet d'un jeu | `GET …/catalog/datasets/<dataset_id>/exports/csv?delimiter=%3B` (aussi `json`, `xlsx`, `parquet`) — vérifié sur Odissé |
| Pièces jointes | Un jeu à `records_count = 0` ne contient pas de table mais des **fichiers joints** (souvent XLSX) listés dans `attachments` ; c'est fréquent à la DREES (voir §2.2) → niveau 2 |
| Authentification | Aucune pour les jeux publics ; en-tête `Authorization: Apikey <clé>` pour les jeux restreints |
| Format | JSON, CSV, XLSX, Parquet |
| Remarque | Le `robots.txt` standard d'Opendatasoft interdit `/api/` aux robots : WebFetch est refusé, un script (Actions) passe sans difficulté. Le portail `data.culture.gouv.fr` n'est **plus** sous Opendatasoft (application `culture.data.gouv.fr`) : non vérifié. |

### 1.2 data.gouv.fr — API du catalogue national
| Élément | Valeur |
|---|---|
| Fiche d'un jeu | `GET https://www.data.gouv.fr/api/1/datasets/<id ou slug>/` → titre, organisation, licence, fréquence, couverture temporelle, `resources[]` (titre, format, `url`, `last_modified`, taille) — vérifié |
| Recherche | `GET https://www.data.gouv.fr/api/2/datasets/search/?q=<mots>&organization=<id>&page_size=<n>` — vérifié |
| Ressources d'un jeu | `GET https://www.data.gouv.fr/api/2/datasets/<id>/resources/?page=1&page_size=50` — vérifié |
| Fichiers | Hébergés sur `static.data.gouv.fr/resources/<slug>/<horodatage>/<fichier>` (l'horodatage change à chaque mise à jour) ou chez le producteur (Opendatasoft, DiDo, S3). **Toujours relire l'URL dans l'API avant de télécharger.** |
| Authentification | Aucune |
| Licence | Indiquée par jeu (`license` : `lov2` = Licence Ouverte 2.0, `odc-odbl`…) |
| Remarque | Une URL de fichier recopiée par WebFetch s'est révélée fausse (404) : ne prendre les URL que dans la réponse brute de l'API. |

### 1.3 SDES — plateforme DiDo (Diffusion des données)
| Élément | Valeur |
|---|---|
| URL de base | `https://data.statistiques.developpement-durable.gouv.fr/dido/api/v1/` ; documentation Swagger : `…/dido/api/v1/apidoc.html` |
| Liste des jeux | `GET …/datasets?page=1&pageSize=<10|20|50|100|all>` (toute autre valeur de `pageSize` → erreur 400, vérifié) |
| Fichier de données | `GET …/datafiles/<rid>/csv` → CSV `;` (vérifié) ; les `rid` sont stables et repris dans les fiches data.gouv.fr du SDES (organisation `681a1272bfa84b075f9531e1`) |
| Authentification | Aucune |
| Formats | CSV, XLSX, JSON, GeoJSON (selon la page du SDES) |

### 1.4 SDMX REST (OCDE, BCE)
| Élément | OCDE | BCE |
|---|---|---|
| URL de base | `https://sdmx.oecd.org/public/rest/` | `https://data-api.ecb.europa.eu/service/` |
| Liste des flux | `dataflow/all` (1 547 flux le 13/10/2026) | `dataflow/ECB` |
| Données | `data/<agence>,<DSD>@<DF>,<version>/<clé>?startPeriod=AAAA&format=csvfilewithlabels` | `data/<flux>/<clé>?format=csvdata` |
| Authentification | Aucune | Aucune |
| Vérification | `verifie` (WebFetch et robot) | `verifie` (robot ; WebFetch refusé par robots.txt) |

---

## 2. Fiches des sources françaises

### 2.1 SDES — Service des données et études statistiques (ministère de la Transition écologique)
| Champ | Valeur |
|---|---|
| Organisme | SDES (service statistique ministériel environnement, énergie, logement, transports) |
| Périmètre | Environnement (air, eau, déchets, pesticides, risques), émissions et empreinte carbone, énergie, logement et construction, transports |
| Voie d'accès | (a) **API DiDo** (§1.3) pour les jeux diffusés sur DiDo ; (b) **fichiers XLSX des publications** (`https://www.statistiques.developpement-durable.gouv.fr/media/<n>/download?inline`) pour les séries de synthèse (empreinte carbone, bilans) |
| Authentification | Aucune |
| Format | CSV (`;`), XLSX |
| Niveau | **1** (DiDo) ; **2** (XLSX des publications, URL changeant à chaque édition) |
| Fiabilité | `verifie` (DiDo : 4 fichiers ouverts ; XLSX empreinte carbone ouvert) |
| Licence | Non vérifiée jeu par jeu (champ `license` des fiches data.gouv.fr du SDES) |
| Fréquence | Annuelle pour les indicateurs nationaux ; mensuelle pour l'énergie et la construction |
| Profondeur | Variable : empreinte carbone 1990–2024 ; air (exposition PM2,5) moyennes triennales 2009-2011 → 2022-2024 |
| Couverture géographique | France (métropole et/ou entière selon l'indicateur), régions, départements, communes (ITDD) |

**Exemples d'indicateurs (identifiants vérifiés)**
- Exposition moyenne aux PM2,5 en fond urbain (moyenne triennale, µg/m³, avec objectifs 2020/2030) — DiDo `rid d237b4e4-c1ce-431f-8716-4297be69f261` (`…/datafiles/d237b4e4-c1ce-431f-8716-4297be69f261/csv`) ; dernière période renseignée 2022-2024 = 8,89.
- Concentrations annuelles SO2, NO2, PM10, PM2,5 et O3 (indice base 100) — `rid b10a6294-7f55-47be-b2e7-2ea2a856e564`.
- Concentrations annuelles SO2, NO2, PM10, PM2,5 en µg/m³ — `rid 9db8c875-10d8-49b3-ac30-1e6f358ab6b0`.
- Dépassements des normes de protection de la santé (NO2, O3, PM10, PM2,5), % d'agglomérations — `rid a956734e-0f63-4629-821e-669f477d5f53`.
- Dépassements de la norme O3 de protection de la végétation — `rid 6bcf0cf8-c721-4de9-a964-f040cb2798ab`.
- Empreinte carbone de la France 1990–2024 (t CO2e/hab ; 8,2 en 2024, provisoire, selon la page de publication) — XLSX `https://www.statistiques.developpement-durable.gouv.fr/media/8724/download?inline`.
- Indicateurs territoriaux de développement durable (ODD), fichier « France entière » — `rid 305ea0e3-269b-47ee-bab5-7553fec6f010`.
- Jeux SDES repérés sur data.gouv.fr (titres vérifiés, identifiants à relever en phase 2) : « Achats et ventes de produits phytosanitaires à l'échelle départementale », « Production et traitement des déchets », « Gaz à effet de serre et polluants atmosphériques au format AEA », « Exposition des logements et des individus au risque d'inondation… », « Exposition des maisons individuelles au retrait-gonflement des argiles », « Parc de véhicules routiers ».

**Limites** : les séries de synthèse les plus utiles (empreinte carbone, artificialisation, bilan énergétique) sont dans des XLSX de publication dont l'URL change à chaque édition ; le moissonnage devra repartir de la page de publication. Beaucoup de jeux DiDo sont locaux (communes, IRIS) et non des séries nationales. L'empreinte carbone figure aussi dans les tableaux INSEE (M01) et l'exposition aux PM2,5 chez Eurostat (M02) : à arbitrer (doublon partiel).

### 2.2 DREES — Direction de la recherche, des études, de l'évaluation et des statistiques
| Champ | Valeur |
|---|---|
| Organisme | DREES (service statistique ministériel santé et solidarités) |
| Périmètre | Santé (espérance de vie sans incapacité, accès aux soins, santé mentale), protection sociale, minima sociaux, pauvreté et redistribution, handicap, retraite, opinion (baromètre d'opinion depuis 2000) |
| Voie d'accès | Portail Opendatasoft `data.drees.solidarites-sante.gouv.fr` (§1.1) : tables interrogeables (niveau 1) **ou** jeux sans table dont les données sont des fichiers joints XLSX (niveau 2) |
| Authentification | Aucune |
| Format | JSON/CSV (tables) ; XLSX (pièces jointes) |
| Niveau | **1** (jeux à enregistrements) / **2** (jeux à pièces jointes) |
| Fiabilité | `verifie` (catalogue complet ouvert : 265 jeux) |
| Licence | Licence Ouverte (à confirmer par jeu, champ `default.license`) |
| Fréquence | Annuelle en général |
| Profondeur | Baromètre d'opinion : depuis 2000 (page DREES) ; autres : variable |
| Couverture | France, régions, départements |

**Exemples de jeux (identifiants `dataset_id` vérifiés dans le catalogue)**
- `431_le-barometre-d-opinion` — Le baromètre d'opinion (opinions sur santé, protection sociale, inégalités, cohésion sociale ; résultats agrégés rétrospectifs selon la page DREES).
- `3457_esperance-de-vie-sans-incapacite` — Espérance de vie sans incapacité.
- `530_l-accessibilite-potentielle-localisee-apl` — Accessibilité potentielle localisée aux professionnels de santé.
- `4230_indicateurs-de-pauvrete-avant-et-apres-redistribution-de-niveau-de-vie-et-d` — Pauvreté avant et après redistribution.
- `336_minima-sociaux-rsa-et-prime-d-activite` — Minima sociaux, RSA et prime d'activité.
- `631_insertion-sociale-et-minima-sociaux` — ISD : insertion sociale et minima sociaux (27 395 enregistrements).
- `indicateurs-atlas-sante-mentale` — Indicateurs de l'atlas santé mentale.
- `graphique-er-suicide-complet` — données de l'Observatoire du suicide (graphique, 10 enregistrements).

**Limites** : environ la moitié des jeux sont des « coquilles » à pièces jointes (records_count = 0) dont le contenu et l'identifiant de pièce jointe sont à relire avant chaque collecte ; les tableaux ne sont pas homogènes d'un jeu à l'autre. Plusieurs séries recoupent l'INSEE (pauvreté) ou Eurostat (espérance de vie en bonne santé, SILC) : doublons partiels à arbitrer.

### 2.3 Santé publique France — Odissé (ex-Géodes)
| Champ | Valeur |
|---|---|
| Organisme | Santé publique France |
| Périmètre | Mortalité par cause (suicide, maladies chroniques), santé mentale, comportements (tabac, alcool, sédentarité, corpulence), périnatalité, environnement et santé (canicules, pollution de l'air), indicateurs des Baromètres de Santé publique France |
| Voie d'accès | Portail Opendatasoft `odisse.santepubliquefrance.fr` (§1.1). L'ancienne adresse `geodes.santepubliquefrance.fr` affiche désormais Odissé (vérifié). |
| Authentification | Aucune |
| Format | JSON, CSV, XLSX |
| Niveau | **1** |
| Fiabilité | `verifie` (catalogue complet : 388 jeux ; enregistrements d'un jeu, voir §0.3) |
| Licence | Non vérifiée (champ `default.license` à lire) |
| Fréquence | Annuelle (mortalité, canicules) ; ponctuelle (Baromètre : éditions 2024 seulement pour plusieurs jeux) |
| Profondeur | Variable ; par exemple jours de canicule France : 22 enregistrements |
| Couverture | France, régions, départements, infra-départemental |

**Exemples de jeux (`dataset_id` vérifiés)**
- `suicides-deces-france` — Suicides : décès (France), 135 enregistrements.
- `canicules-nombres-de-jours-de-canicule-france` — Nombre de jours de canicule (France), 22 enregistrements ; `canicules-severite-france`.
- `tabagisme-prevalence-selon-le-sexe` — Tabac : prévalence selon le sexe (39) ; `tabagisme-prevalence-selon-le-revenu` (36).
- `sante-mentale-episodes-depressifs-caracterises-dans-les-12-derniers-mo` (France, 12) ; `sante-mentale-pensees-suicidaires-et-tentatives-de-suicide_fra` (12).
- `bien-etre-indicateurs-du-barometre-2024` — Bien-être, Baromètre de Santé publique France 2024 (104) ; `trouble-anxieux-generalise-indicateurs-du-barometre-2024`.
- `corpulence-surpoids-et-obesite-fra` (2 enregistrements) ; `mortalite-infantile-et-mortinatalite-france` (13).
- `pollution-de-l-air-impact-du-no2-et-des-pm2-5_mortalite_fra` — mortalité attribuable à la pollution de l'air (1 enregistrement).

**Limites** : nombreux jeux à une seule édition (Baromètre 2024) ou à faible profondeur : beaucoup ne satisferont pas le critère « 10 points depuis 2000 ». Les décès par suicide existent aussi chez Eurostat (causes de décès) : doublon partiel.

### 2.4 SSMSI — Service statistique ministériel de la sécurité intérieure (Interstats)
| Champ | Valeur |
|---|---|
| Organisme | Ministère de l'Intérieur, SSMSI |
| Périmètre | Délinquance enregistrée (homicides, violences, cambriolages, escroqueries…), victimation et sentiment d'insécurité (enquêtes Cadre de vie et sécurité puis Vécu et ressenti en matière de sécurité), atteintes à la probité |
| Voie d'accès | Fichiers publiés sur data.gouv.fr (§1.2) : **base des séries chronologiques** (jeu `62b02e970a264df3467b6c42`, CSV ~24,6 Mo et Parquet) ; bases communales/départementales (jeu `621df2954fa5a3b5a023e23c`) ; ancien « état 4001 » mensuel départemental depuis 1996 (jeu `5617ad4dc751df6211cdbb49`, XLSX) |
| Authentification | Aucune |
| Format | CSV, Parquet, XLSX |
| Niveau | **2** |
| Fiabilité | `verifie` (fiche API et fichiers ouverts par le robot, voir résultats vague 3) |
| Licence | Licence Ouverte 2.0 (`lov2`, fiche data.gouv.fr de la base des séries chronologiques) |
| Fréquence | Mensuelle, trimestrielle ou annuelle selon l'indicateur ; base mise à jour en août 2026 |
| Profondeur | Base des séries chronologiques : couverture déclarée 2006–2023 dans les métadonnées (à recouper avec le fichier) ; état 4001 : depuis janvier 1996 (fichier non mis à jour depuis 2022) |
| Couverture | France, départements |

**Exemples d'indicateurs** (périmètres listés dans la description officielle de la base ; libellés exacts des séries à relever en phase 2) : homicides et tentatives ; coups et blessures volontaires ; violences sexuelles ; cambriolages de logements ; escroqueries et fraudes aux moyens de paiement ; atteintes à caractère raciste, xénophobe ou antireligieux ; atteintes anti-LGBT ; outrages sexistes ; dépôt de plainte (taux de plainte) ; **sentiment d'insécurité** (enquêtes de victimation).

**Limites** : délinquance **enregistrée** = activité des services autant que délinquance réelle (sens d'interprétation ambigu pour certaines infractions, par exemple violences intrafamiliales dont la hausse reflète aussi une meilleure révélation). Rupture entre l'enquête CVS (2007–2021) et VRS (depuis 2022). Homicides également disponibles via OCDE (How's Life 10_1) et Banque mondiale (ONUDC).

### 2.5 DEPP — Direction de l'évaluation, de la prospective et de la performance (Éducation nationale)
| Champ | Valeur |
|---|---|
| Organisme | DEPP (service statistique ministériel de l'éducation) ; SIES pour l'enseignement supérieur (`data.enseignementsup-recherche.gouv.fr`) |
| Périmètre | Réussite aux examens (baccalauréat, brevet), évaluations nationales des élèves (CP → seconde), valeur ajoutée des établissements, insertion des diplômés (InserJeunes, InserSup), origine sociale des bacheliers |
| Voie d'accès | Portail Opendatasoft `data.education.gouv.fr` (§1.1) ; idem SIES |
| Authentification | Aucune |
| Format | JSON, CSV, XLSX |
| Niveau | **1** |
| Fiabilité | `verifie` (catalogues DEPP 310 jeux et SIES 217 jeux ouverts) |
| Licence | Licence Ouverte (à confirmer par jeu) |
| Fréquence | Annuelle |
| Profondeur | Courte pour les évaluations nationales (dispositif récent) ; à mesurer jeu par jeu pour le baccalauréat |
| Couverture | France, académies, départements, établissements |

**Exemples de jeux (`dataset_id` vérifiés)** : `fr-en-reussite-au-baccalaureat-origine-sociale` (348 enregistrements) ; `fr-en-baccalaureat-par-academie` (43 217) ; `fr-en-dnb-par-sexe-et-par-serie` ; `fr-en-evaluations_nationales_6eme_academie` (et CE1, CM1, CM2, 4e, 2de) ; `fr-en-indicateurs-valeur-ajoutee-colleges` ; SIES : `fr-esr-insersup` (insertion professionnelle des diplômés du supérieur), `fr-esr-taux-poursuite-enseignement-superieur-par-academie`.

**Compétences internationales (PISA, PIAAC)** : non publiées par la DEPP en données ouvertes ; disponibles via l'OCDE (How's Life, mesures `6_1` à `6_5`, §3.1) : PISA 2006–2022 (6 points), PIAAC 2012 et 2023.

**Limites** : les publications de référence (« Repères et références statistiques », « L'état de l'École ») sont diffusées hors du portail (XLSX sur education.gouv.fr) : non vérifié. Les sorties précoces et diplômes sont chez Eurostat/INSEE (M01/M02).

### 2.6 OFB / Observatoire national de la biodiversité (ONB) — `naturefrance.fr`
| Champ | Valeur |
|---|---|
| Organisme | Office français de la biodiversité (OFB) et partenaires de l'ONB |
| Périmètre | Environ 120 indicateurs d'état, de pression et de réponse sur la biodiversité |
| Voie d'accès | **Aucune voie automatisable trouvée** : le portail `naturefrance.fr` est hors service (« services temporairement interrompus », vérifié le 13/10/2026) ; la page de secours `https://www.eaufrance.fr/lobservatoire-national-de-la-biodiversite-onb` renvoie vers des fiches et visuels hébergés sur Resana (non ouvrables par script, refus robots.txt) |
| Niveau | **Exclu (temporairement)** |
| Fiabilité | `non_verifie` — portail interrompu, pas de date de reprise annoncée |
| Licence | Etalab 2.0 pour les visuels (page eaufrance) |

**Alternatives vérifiées pour la biodiversité** : OCDE How's Life, bien-être futur (`12_7` indice Liste rouge 2004–2025 ; `12_5`/`12_6` aires protégées terrestres et marines 2004–2024 ; `12_1` couverture naturelle et semi-naturelle) ; Hub'Eau (qualité des eaux, §3.9) ; SDES (pesticides) ; INSEE (indicateurs ODD, dont l'indice d'abondance des oiseaux communs, mission M01) ; Eurostat (mission M02).

### 2.7 Ademe et Citepa
**Ademe — portail Data Fair `data.ademe.fr`**
| Champ | Valeur |
|---|---|
| Voie d'accès | API Data Fair : `GET https://data.ademe.fr/data-fair/api/v1/datasets?size=<n>&q=<mot>&select=id,title,updatedAt,count` ; lignes d'un jeu : `…/datasets/<id>/lines` |
| Authentification / format | Aucune / JSON, CSV |
| Niveau / fiabilité | **1** / `verifie` (1 018 jeux) |
| Licence | Non vérifiée |
| Exemples | `meg-83tjwtg8dyz4vv7h1dqe` DPE logements existants depuis juillet 2021 (15,6 M lignes) ; `dpe-france` DPE avant juillet 2021 ; `empreintes-t1` à `empreintes-g8` (empreinte carbone et matières 2015 et scénarios 2050) ; `base-carboner` (facteurs d'émission) |
| Limites | Peu de **séries nationales annuelles** : surtout des microdonnées (DPE, non représentatives du parc) et des scénarios prospectifs. La part de logements par étiquette DPE représentative du parc relève du SDES/ONRE (à vérifier en phase 2). |

**Citepa — inventaire national des émissions (format Secten)**
| Champ | Valeur |
|---|---|
| Voie d'accès | Fichiers de la page `https://www.citepa.org/donnees-air-climat/donnees-gaz-a-effet-de-serre/secten/` : XLSX « série longue » `https://www.citepa.org/wp-content/uploads/2026/06/serie_longue_Citepa_Secten_ed_2026-d.xlsx` (feuille `BDD_Secten`, 51 112 lignes : format, édition, famille, secteur niv. 1-3, périmètre, substance, unité, année, émission) ; ZIP GES `…/2026/06/Citepa2026_gaz_a_effet_de_serre.zip` (4 classeurs) ; ZIP polluants, ZIP par secteur |
| Authentification / format | Aucune / XLSX, ZIP de XLSX |
| Niveau / fiabilité | **2** / `verifie` |
| Licence | **Non trouvée** (la page mentionne seulement le label « statistique d'intérêt général » obtenu le 17/07/2025) |
| Fréquence / profondeur | Annuelle (édition de juin) / 1990–2025 (GES, NOx, PM2,5 selon la page) |
| Exemples | Émissions totales de GES hors UTCATF ; par secteur (transports, bâtiments, agriculture, industrie) ; méthane, protoxyde d'azote ; polluants (NOx, PM2,5, NH3) |
| Limites | URL changeant chaque année (`wp-content/uploads/AAAA/MM/…`, suffixe de version) ; licence à clarifier avant redistribution. Doublon partiel avec Eurostat/INSEE (inventaire CCNUCC) et EDGAR. |

### 2.8 Banque de France — Webstat (et BCE en complément)
| Champ | Valeur |
|---|---|
| Organisme | Banque de France (plus de 40 000 séries, y compris BCE/FMI) |
| Périmètre | Comptes financiers des ménages (endettement, épargne), crédits et taux, surendettement (dépôts de dossiers par département), entreprises |
| Voie d'accès | Nouveau Webstat sous Opendatasoft : **catalogue des séries** `https://webstat.banque-france.fr/api/explore/v2.1/catalog/datasets?where=search("…")` (un « jeu » par série, métadonnées `metas.custom.series_key`, dates de première et dernière observation, deux dernières valeurs) ; **observations** : API réservée aux comptes (« ouvert avec compte », 10 000 appels/jour selon data.gouv.fr ; portail développeur `https://developer.webstat.banque-france.fr`) |
| Authentification | Catalogue : aucune (vérifié) ; observations : compte gratuit et clé (non testé) |
| Format | JSON, CSV, XLSX (selon data.gouv.fr) |
| Niveau | **1** |
| Fiabilité | `probable` — catalogue vérifié ; le point `datasets/observations` répond 404 sans compte |
| Licence | Licence Ouverte 2.0 indiquée pour le contenu du site (selon la fiche data.gouv.fr du service) |
| Exemples (identifiants vérifiés) | `cnfsi-q-s-fr-w0-s1m-s1-n-l-f-f401-t-_z-xdc-_t-s-v-n-_t` (flux d'endettement des ménages auprès des institutions financières, trimestriel CVS, 1995T4–2026T1) ; `cnfsi-a-n-fr-w0-s1m-s1-n-l-f-f401-t-_z-xdc-_t-s-v-n-_t` (annuel 1996–2025) ; `cnfsi-q-y-fr-w0-s1m-s1-n-b-b8g-_z-_z-_z-xdc_r_b6g_s1m-_t-s-v-n-_t` (épargne brute / revenu disponible des ménages) ; `ifi-m-d<dep>-suren-depot` (dépôts de dossiers de surendettement, mensuel, par département) |

**Alternative sans clé, vérifiée : BCE Data Portal (SDMX, §1.4)** — ratio des crédits aux ménages au revenu disponible brut ajusté, France, depuis 1999T4 : `QSA/Q.N.FR.W0.S1M.S1.N.L.LE.F4.T._Z.XDC_R_B6GA_CY._T.S.V.N._T`. Flux utiles : `QSA` (comptes financiers trimestriels), `RPP` (prix de l'immobilier résidentiel), `SHI` (indicateurs structurels du logement), `HICP`, `MIR`, `BSI`. Niveau 1, `verifie`, aucune clé.

### 2.9 data.gouv.fr — catalogue national
Voie d'accès documentée au §1.2 (niveau 1, `verifie`). Jeux « résultats » utiles repérés et ouverts :
- **Données des élections agrégées** (`6481e741d4cf002ec0efec9d`, organisation data.gouv.fr, Licence Ouverte 2.0) — voir §2.10.
- **Bases annuelles des accidents corporels de la circulation routière 2005–2024** (`53698f4ca3a729239d2036df`, Ministère de l'Intérieur / ONISR) — fichiers annuels `caract-`, `lieux-`, `vehicules-`, `usagers-<année>.csv` ; la gravité (`grav`) permet de compter tués et blessés hospitalisés. Niveau 2, `verifie`.
- **Baromètre du numérique 2007–2025** (Arcep/Arcom/CGE/ANCT ; terrain Crédoc jusqu'en 2019) : jeux `5838300988ee386317c65bb3` (Arcep) et `67dde5bb8b979e2f5c9d869d` (Arcom), microdonnées CSV pondérées (`IDENT, ANNEE, POND, …`) et dictionnaire XLSX, licence ODbL. Niveau 2, `verifie`. Indicateurs calculables : usage d'internet, équipement, difficultés numériques (illectronisme).
- **SSMSI** : voir §2.4. **SDES** : voir §2.1.

### 2.10 Ministère de l'Intérieur (résultats électoraux) et CEVIPOF (confiance politique)
**Résultats électoraux**
| Champ | Valeur |
|---|---|
| Voie d'accès | Jeu data.gouv.fr « Données des élections agrégées » : `https://data-pipeline-open.s3.sbg.io.cloud.ovh.net/elections/general_results.csv` (≈ 406 Mo) ou `…/general_results.parquet` (≈ 71 Mo) ; schéma `…/schema-general-results.json` |
| Format | CSV `;` au bureau de vote : `id_election` (ex. `2022_pres_t1`), `inscrits`, `abstentions`, `votants`, `blancs`, `nuls`, `exprimes` et ratios |
| Niveau / fiabilité | **2** / `verifie` |
| Licence | Licence Ouverte 2.0 |
| Profondeur | 1999 → 2026 (municipales 2026 présentes dans le fichier) |
| Indicateurs | Taux de participation (votants / inscrits) à chaque scrutin national : présidentielles (2002, 2007, 2012, 2017, 2022), législatives, européennes, régionales, municipales ; part des votes blancs et nuls |
| Limites | Fréquence **irrégulière** (pas annuelle) : il faudra définir une règle (dernier scrutin national connu, moyenne glissante). Très gros fichier : préférer le Parquet et agréger par `id_election`. |

**CEVIPOF — Baromètre de la confiance politique (Sciences Po / OpinionWay)**
| Champ | Valeur |
|---|---|
| Voie d'accès | Rapports **PDF** par vague (vague 1 janvier 2010 → vague 17 février 2026) sur `https://www.sciencespo.fr/cevipof/fr/etudes-enquetes/barometre-confiance-politique/` ; aucun fichier de données ni lien vers des microdonnées trouvé |
| Niveau / fiabilité | **Exclu** (PDF seulement) / `verifie` (absence de données constatée) |
| Remarque | L'INSEE cite ce baromètre comme source de son indicateur ODD 16.i4 « Confiance de la population dans les institutions » : **à vérifier en M01** (si l'INSEE publie la série en tableau, c'est la voie d'accès). Alternatives vérifiées : OCDE `14_3` confiance dans le gouvernement (2006–2025, Gallup) ; Eurostat (confiance dans les institutions de l'UE, M02). |

### 2.11 CEPREMAP — Observatoire du bien-être
| Champ | Valeur |
|---|---|
| Périmètre | Baromètre trimestriel du bien-être des Français (satisfaction dans la vie, sens, bonheur et anxiété la veille, solitude, relations, perspectives), adossé à l'enquête de conjoncture auprès des ménages (CAMME) de l'INSEE |
| Voie d'accès | Tableau de bord HTML (`https://www.cepremap.fr/Tableau_de_Bord_Bien-Etre.html`), notes et rapports **PDF** ; aucun fichier CSV/XLSX trouvé (pages et code de la page examinés, voir extrait robot) |
| Niveau / fiabilité | **Exclu** / `verifie` (absence de données téléchargeables constatée) |
| Remarque | La source primaire est l'INSEE (module bien-être de l'enquête CAMME) : microdonnées diffusées aux chercheurs (réseau Quetelet), non automatisables ; **à poser à M01** : l'INSEE publie-t-il des séries agrégées du module ? Alternative vérifiée : OCDE How's Life `11_1` (satisfaction dans la vie, 2013–2025, 7 points), WHR (§3.5). |

### 2.12 Crédoc et Observatoire des inégalités
- **Crédoc — enquête « Conditions de vie et aspirations »** : diffusion en rapports et notes (site `credoc.fr`, environ 600 études téléchargeables) ; aucun fichier de données trouvé. **Exclu**, `verifie` (absence constatée). Seule exception utile : le **Baromètre du numérique** (terrain Crédoc jusqu'en 2019), désormais publié en microdonnées par l'Arcep/Arcom (§2.9, niveau 2).
- **Observatoire des inégalités** (`inegalites.fr`) : source **secondaire** (reprend l'INSEE, la DREES, Eurostat) ; pages web et rapports ; page de données ouverte par WebFetch en erreur. **Exclu** (utiliser les sources primaires) ; `non_verifie` pour d'éventuels fichiers.

---

## 3. Fiches des sources internationales

### 3.1 OCDE — OECD Data Explorer (SDMX)
| Champ | Valeur |
|---|---|
| Voie d'accès | API SDMX REST (§1.4) : `https://sdmx.oecd.org/public/rest/data/<agence>,<DSD@DF>,<version>/<clé>?…` |
| Authentification / format | Aucune / CSV (avec libellés), XML et JSON SDMX |
| Niveau / fiabilité | **1** / `verifie` |
| Licence | À vérifier (conditions d'utilisation de l'OCDE ; page non lisible par WebFetch) |
| Fréquence / profondeur | Annuelle ; How's Life : 2004 → 2025 selon les mesures |
| Couverture | Pays de l'OCDE (France = `FRA`) ; certaines bases régionales |

**Base How's Life (bien-être), flux vérifiés pour la France**
- Bien-être actuel `OECD.WISE.WDP,DSD_HSL@DF_HSL_CWB,1.1` (clé `FRA.......`) : 68 mesures France. Séries longues utiles : `10_2` se sentir en sécurité la nuit (2006–2025, 20 points) ; `7_1` soutien social (2006–2025) ; `11_2` affects négatifs (2006–2025) ; `11_3` douleur physique ; `1_5` difficulté à boucler les fins de mois (2004–2025) ; `3_5` incapacité à chauffer son logement ; `5_2` santé perçue positive ; `5_3` décès par suicide, alcool, drogues (2004–2023) ; `10_1` homicides (2004–2022) ; `10_3` décès sur la route (2004–2024) ; `2_7` longues heures de travail ; `9_3` exposition aux températures extrêmes. Séries courtes : `11_1` satisfaction dans la vie (2013–2025, 7 points) ; `7_4` solitude (2018, 2022) ; `8_1` avoir son mot à dire (2021, 2023) ; `8_2` participation électorale (4 scrutins).
- Bien-être futur `OECD.WISE.WDP,DSD_HSL@DF_HSL_FWB,1.1` : 33 mesures, dont `14_1` confiance dans les autres (2013–2025, 7 points), `14_3` confiance dans le gouvernement (2006–2025), `14_6` corruption (CPI, 2012–2025), `14_7` bénévolat (2007–2025), `14_5` parité en politique, `12_7` indice Liste rouge (2004–2025), `12_5`/`12_6` aires protégées, `12_14` empreinte matières, `12_15` taux de recyclage, `12_9` empreinte carbone, `12_11` bilan des nutriments du sol, `13_3` mortalité prématurée, `13_4` tabagisme, `15_6` dette des ménages.
- **Remarque** : plusieurs séries annuelles (sécurité la nuit, soutien social, affects, confiance dans le gouvernement, bénévolat) proviennent du **Gallup World Poll** : l'OCDE est donc une voie d'accès ouverte à une partie des données Gallup (fermées par ailleurs).

**Autres flux utiles repérés dans la liste des 1 547 flux (non interrogés pour la France à ce stade)** : `OECD.WISE.INE` `DSD_WISE_IDD@DF_IDD` (distribution des revenus), `DSD_WEALTH@DF_WEALTH` (patrimoine), `DSD_TIME_USE@DF_TIME_USE` (emploi du temps) ; `OECD.ELS.HD` `DSD_HEALTH_STAT@DF_AM` (mortalité évitable), `@DF_LE`, `@DF_PHS` (santé perçue), `DSD_HEALTH_LVNG@DF_HEALTH_LVNG_AC` / `_TC` (alcool, tabac) ; `OECD.ELS.SAE` `DSD_HW@DF_AVG_ANN_HRS_WKD` (heures travaillées), `DSD_EARNINGS@GENDER_WAGE_GAP` ; `OECD.GOV.GIP` `DSD_GOV_INT@DF_GOV_TDG_2025` (confiance, sécurité et dignité) ; `OECD.ENV.EPI` `DSD_AIR_POL@DF_AIR_POLL`, `DSD_WILD_LIFE@DF_WILD_LIFE` (espèces menacées), `DSD_PA@DF_PROT_AREA`, `DSD_LAND@DF_LAND_COVER`, `DSD_MATERIAL_RESOURCES@DF_MATERIAL_RESOURCES`, `DSD_MUNW@DF_MUNW` ; `OECD.WISE.RSB` `DSD_SDG@DF_SDG_G_16` (ODD 16).

**Limites** : versions de flux (`1.1`, `2.0`…) qui évoluent ; certaines mesures sont reprises d'Eurostat (EU-SILC, LFS) : doublons à signaler.

### 3.2 Banque mondiale — API v2 (WDI, WGI)
| Champ | Valeur |
|---|---|
| Voie d'accès | `https://api.worldbank.org/v2/country/FRA/indicator/<code>?format=json&per_page=100&date=AAAA:AAAA` ; WGI : ajouter `source=3` |
| Authentification / format | Aucune / JSON (aussi XML) |
| Niveau / fiabilité | **1** / `verifie` (20 séries WDI et 6 WGI ouvertes) |
| Licence | CC BY 4.0 (conditions générales de la Banque mondiale ; non revérifiée ici) |
| Fréquence / profondeur | Annuelle ; jusqu'en 2024–2025 selon les séries (mise à jour du 08/10/2026) |
| Catalogue | 1 498 indicateurs WDI (`source=2`) ; 36 indicateurs WGI (`source=3`) — listes extraites |
| Exemples | WGI 1996–2025 : `GOV_WGI_VA.EST` (voix et redevabilité), `GOV_WGI_RL.EST` (état de droit), `GOV_WGI_CC.EST` (contrôle de la corruption), `GOV_WGI_GE.EST` (efficacité de l'action publique), `GOV_WGI_PV.EST` (stabilité politique) — **indices composites** ; WDI : `EN.GHG.CO2.PC.CE.AR5`, `EN.GHG.ALL.PC.CE.AR5` (émissions par habitant, 1995–2024), `VC.IHR.PSRC.P5` (homicides, source ONUDC), `EN.ATM.PM25.MC.M3` (exposition PM2,5, jusqu'en 2023) |
| Limites | Pour la France, la Banque mondiale reprend souvent Eurostat/INSEE/OCDE (doublons) et convertit en dollars ; deux codes des prototypes sont archivés (voir §5). |

### 3.3 Our World in Data, V-Dem, RSF, Transparency International, Freedom House
**Our World in Data (relais)**
| Champ | Valeur |
|---|---|
| Voie d'accès | CSV des graphiques : `https://ourworldindata.org/grapher/<slug>.csv?v=1&csvType=full&useColumnShortNames=true` (tous pays, toutes années) ; métadonnées `…/<slug>.metadata.json`. **Attention** : `csvType=filtered&time=earliest..latest` ne renvoie que les deux extrémités. Données CO2 complètes : `https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv` |
| Authentification / format | Aucune / CSV, JSON |
| Niveau / fiabilité | **2** / `verifie` (11 graphiques + co2-data ouverts) |
| Licence | CC BY 4.0 pour les contenus OWID ; licence de la source primaire pour les données (V-Dem : CC BY-SA 4.0) |
| Séries France vérifiées | `freedom-of-expression-index`, `judicial-constraints-on-the-executive-index`, `electoral-democracy-index`, `liberal-democracy-index` (V-Dem, 1789–2025) ; `academic-freedom-index` (V-Dem, 2000–2025) ; `political-rights-score-fh` (2002–2025), `civil-liberties-score-fh` (2003–2025) (Freedom House) ; `ti-corruption-perception-index` (2012–2024) ; `happiness-cantril-ladder` (WHR, 2011–2025, 14 points) ; `press-freedom-index-rsf` (**2013–2021 seulement**) ; `self-reported-trust-attitudes` (WVS/EVS, 5 vagues dont 2004 et 2022) |
| Limites | Relais pouvant être en retard ou arrêté (RSF) ; slugs susceptibles de changer. |

**Sources primaires**
| Source | Voie d'accès vérifiée | Niveau | Fiabilité | Licence | Remarques |
|---|---|---|---|---|---|
| **V-Dem** (Varieties of Democracy, v16, mars 2026) | Téléchargement **par formulaire** (courriel obligatoire) sur `https://v-dem.net/data/the-v-dem-dataset/` ; pas de lien direct (essai d'URL directe : 404) ; paquet R `vdemdata` sur GitHub | **Exclu** en direct → passer par OWID (niveau 2) | `verifie` (formulaire constaté) | CC BY-SA 4.0 | Indices composites (démocratie électorale, libérale…) et sous-indices |
| **RSF** — Classement mondial de la liberté de la presse | `https://rsf.org/sites/default/files/import_classement/<année>.csv` (vérifié pour 2002, 2013, 2026) | **2** | `verifie` | Non trouvée | Score France 2026 : 76,68 (rang 25). **Ruptures** : 2002–2012 échelle « plus bas = mieux » non bornée ; 2013–2021 échelle 0–100 « plus bas = mieux » ; depuis 2022 nouvelle méthode « plus haut = mieux » avec 5 sous-scores. CSV `;`, virgule décimale, encodage variable selon l'année. |
| **Transparency International** — CPI | `https://images.transparencycdn.org/images/CPI2025_Results.xlsx` (classeur à 6 feuilles) | **2** | `verifie` | CC BY-ND 4.0 (page CPI) | Indice composite de corruption perçue ; méthode comparable depuis 2012 ; URL nouvelle chaque année ; classeur illisible par openpyxl en lecture seule (prévoir un autre lecteur) |
| **Freedom House** — Freedom in the World | `https://freedomhouse.org/sites/default/files/2024-02/All_data_FIW_2013-2024.xlsx` ; `…/Country_and_Territory_Ratings_and_Statuses_FIW_1973-2024.xlsx` (vérifiés) | **2** | `verifie` (édition 2024) | Non trouvée | Éditions 2025-2026 : données sur demande (« FIW Data Request ») selon la page du rapport ; OWID relaie jusqu'en 2025. Indice composite. |
| **World Justice Project** — Rule of Law Index | `https://worldjusticeproject.org/sites/default/files/documents/FINAL_2021_wjp_rule_of_law_index_HISTORICAL_DATA_FILE.xlsx` (2012–2021, une feuille par édition) | **2** | `verifie` (fichier 2021) ; éditions postérieures `non_verifie` (fichier non trouvé) | Non trouvée | Indice composite ; scores antérieurs à 2015 non strictement comparables |

### 3.4 Bien-être ressenti : World Happiness Report, Gallup, Eurofound, ESS, Eurobaromètre
| Source | Voie d'accès | Niveau | Fiabilité | Licence | Remarques |
|---|---|---|---|---|---|
| **World Happiness Report** | `https://files.worldhappiness.report/WHR26_Data_Figure_2.1.xlsx` (feuille « Data for Figure 2.1 (2011–2025) » : année, rang, pays, évaluation de la vie en moyenne triennale, intervalles, contributions des 6 facteurs) ; éditions antérieures en `.xls`/`.xlsx` sur `https://worldhappiness.report/data-sharing/` ; relais OWID `happiness-cantril-ladder` | **2** | `verifie` | Non précisée (« disponibles gratuitement ») | Données Gallup (échelle de Cantril) ; nom de fichier nouveau chaque année ; moyenne sur 3 ans |
| **Gallup World Poll** | Abonnement (Gallup Analytics) | **Exclu** | — | Propriétaire | Une partie des séries est **relayée par l'OCDE** (How's Life, §3.1) et par le WHR |
| **Eurofound** (EQLS 2003, 2007, 2011, 2016 ; enquêtes « Living, working and COVID-19 ») | Microdonnées via le UK Data Service (inscription) ; site Eurofound non lisible par WebFetch | **Exclu** | `non_verifie` (site en erreur pour l'outil) | — | Trop peu de vagues pour une série annuelle |
| **European Social Survey** | Portail `ess.sikt.no` : téléchargement CSV/SPSS/Stata **après connexion** ; API en version bêta (`https://api.ess.sikt.no/docs`, page ouverte) | **Exclu** en v1 (inscription) ; niveau 1 possible si l'API bêta accepte une clé | `probable` (documentation API ouverte, données non testées) | CC BY 4.0 (fiche data.norge.no) | Biennale depuis 2002 ; satisfaction dans la vie, confiance interpersonnelle et institutionnelle, sentiment de sécurité ; nombre de vagues françaises à vérifier |
| **Eurobaromètre** | Microdonnées GESIS (DOI par vague, connexion) ; fichier de tendances `https://www.gesis.org/fileadmin/upload/dienstleistung/daten/umfragedaten/eurobarometer/eb_trends/eb_trend_trust_in_institutions.xls` (inventaire des questions, pas des valeurs) | **Exclu** en v1 | `non_verifie` (téléchargement non testé) | Conditions GESIS | La confiance dans les institutions de l'UE est diffusée par Eurostat (M02) ; la confiance dans le gouvernement et le parlement nationaux n'a pas de voie ouverte trouvée |

### 3.5 Planète : Global Footprint Network, EDGAR, Copernicus
| Source | Voie d'accès | Niveau | Fiabilité | Licence | Remarques |
|---|---|---|---|---|---|
| **Global Footprint Network** | API `https://api.footprintnetwork.org/v1/data/FR/all/EFCpc` (403 sans clé, vérifié) ; paquet public par **formulaire** (courriel, ZIP) | **1** sous réserve d'obtenir une clé gratuite ; sinon exclu | `non_verifie` (clé non disponible) | CC BY-SA 4.0 (paquet public) | Empreinte écologique et biocapacité 1961–2025 (édition 2026). Alternative vérifiée : OCDE `12_14` empreinte matières |
| **EDGAR** (Commission européenne, JRC) | `https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/EDGAR/datasets/EDGAR_2025_GHG/EDGAR_AR5_GHG_1970_2024.zip` (contient `EDGAR_AR5_GHG_1970_2024.xlsx`) ; aussi CO2, CH4, N2O, gaz fluorés, NOx, PM2,5 | **2** | `verifie` | CC BY 4.0 (IEA-EDGAR CO2 : CC BY-NC-ND 4.0) | 1970–2024 ; utile surtout pour le calibrage européen (doublon partiel Citepa/Eurostat) ; dossier `EDGAR_<édition>_GHG` nouveau chaque année |
| **Copernicus CAMS** (qualité de l'air) | Catalogue STAC `https://ads.atmosphere.copernicus.eu/api/catalogue/v1/collections` (ouvert, vérifié) ; téléchargement des données avec compte et clé ; grilles NetCDF | **Exclu** en v1 (pas d'indicateur national prêt à l'emploi) | `verifie` (catalogue) | Licence Copernicus | Utiliser SDES (§2.1), Banque mondiale `EN.ATM.PM25.MC.M3` ou OCDE `9_2` |

---

## 4. Sources découvertes en route

| Source | Voie d'accès | Niveau | Fiabilité | Intérêt / exemples |
|---|---|---|---|---|
| **BCE — ECB Data Portal** | SDMX `https://data-api.ecb.europa.eu/service/` (§1.4) | 1 | `verifie` | Dette des ménages / revenu (QSA) depuis 1999T4 ; prix immobiliers (RPP) ; logement (SHI) |
| **PNUD — Rapport sur le développement humain** | `https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv` (1990–2023) ; tableaux XLSX | 2 | `verifie` | IDH, IDH ajusté aux inégalités, indice d'inégalité de genre, IDH ajusté aux pressions planétaires — **indices composites** ; URL par édition |
| **OMS — Global Health Observatory** | API OData `https://ghoapi.azureedge.net/api/<code>?$filter=SpatialDim eq 'FRA'` | 1 | `verifie` (`MH_12`, taux de suicide) | Suicide, alcool, couverture sanitaire ; doublons fréquents avec Eurostat/OCDE ; licence non vérifiée |
| **Hub'Eau** (OFB/BRGM, eaufrance) | API `https://hubeau.eaufrance.fr/api/v1/qualite_nappes/analyses?code_param=1340` (nitrates, 885 036 analyses) | 1 | `verifie` | Qualité des eaux souterraines et de surface ; **données brutes par station** : un indicateur national demanderait une méthode d'agrégation |
| **ODRE** (Open Data Réseaux Énergies) | Opendatasoft `odre.opendatasoft.com` (§1.1) | 1 | `verifie` | `consommation-annuelle-brute` (électricité), `pic-annuel-conso-brute` (2001–2025), éCO2mix |
| **Assurance maladie — data.ameli.fr** | Opendatasoft (§1.1) | 1 | `verifie` | Risques professionnels : `sinistralite-par-secteur-d-activite-concerne-naf-1`, `deces-par-secteur-d-activite-naf-1-et-naf-5`, `maladies-professionnelles-psychiques-par-secteur-d-activite-naf-1-et-n` ; accès aux soins : `patients-longueduree-annuelle` (patients en ALD sans médecin traitant) |
| **CNAF — data.caf.fr** | Opendatasoft (§1.1) | 1 | `verifie` | Surtout des effectifs d'allocataires (indicateurs de **moyens**, peu éligibles) ; `nbpla_pe_nat_hist` (places d'accueil petite enfance 2017–2022) |
| **Ministère de l'Économie — data.economie.gouv.fr** | Opendatasoft (§1.1) | 1 | `verifie` | Baromètre des réclamations DGCCRF depuis 2008 (marginal) |
| **ONISR** (sécurité routière) | data.gouv.fr (§2.9) | 2 | `verifie` | Tués et blessés de la route (microdonnées BAAC 2005–2024) ; série nationale aussi à l'OCDE `10_3` |
| **Arcep / Arcom — Baromètre du numérique** | data.gouv.fr (§2.9) | 2 | `verifie` | Usages et difficultés numériques 2007–2025 (microdonnées pondérées) |
| **Global Carbon Project via OWID (co2-data)** | GitHub `owid/co2-data` (§3.3) | 2 | `verifie` | Émissions de CO2 fondées sur la consommation, par habitant |
| **DARES** (travail) | Site `dares.travail-emploi.gouv.fr` | — | `non_verifie` | Connexion refusée au robot et refus robots.txt pour WebFetch ; séries attendues : conditions de travail, durée du travail, accidents ; **à vérifier manuellement par Léo** |
| **ONUDC** (criminalité) | Portail déplacé vers `https://data.unodc.org/` ; pas de fichier direct trouvé | — | `non_verifie` | Homicides accessibles via Banque mondiale `VC.IHR.PSRC.P5` et OCDE `10_1` (vérifiés) |
| **International IDEA** (participation électorale) | Base « Voter Turnout » sans export direct trouvé | — | `non_verifie` | Participation calculable à partir des résultats officiels (§2.10) |
| **World Inequality Database (WID)** | API utilisée par le paquet R `widr` (point d'accès AWS) ; non testée | — | `non_verifie` | Parts de revenu et de patrimoine des plus aisés ; à étudier en phase 2 (OWID en relaie une partie) |

---

## 5. Statut des séries des prototypes hors INSEE/Eurostat (20 séries)

Vérification du 13/10/2026 (robot, extraits `banque_mondiale__*.txt` et `owid__*.txt`). « n ≥ 2000 » = nombre d'années renseignées depuis 2000.

| id_prototype | Code | Statut | Période France | Dernière valeur | Proposition |
|---|---|---|---|---|---|
| labprod | `SL.GDP.PCAP.EM.KD` | Actif | 1995–2025 (n ≥ 2000 : 26) | 2025 : 128 587 $ PPA 2021 | Conserver comme candidat ; doublon partiel Eurostat/OCDE (productivité) |
| hhcons | `NE.CON.PRVT.PC.KD` | Actif | 1995–2025 (26) | 2025 : 21 276 $ 2015 | Préférer INSEE (consommation par UC, euros) ; doublon |
| adjnni | `NY.ADJ.NNTY.PC.KD` | Actif mais figé | 1995–2021 (22) | 2021 | Dernière année < 2022 : fragile ; à remplacer si l'OCDE `1_1` convient |
| adjsav | `NY.ADJ.SVNG.GN.ZS` | Actif mais figé | 1995–2021 (22) | 2021 : 9,21 % | Série plus mise à jour depuis 2021 (« épargne nette ajustée ») : à abandonner ou à suivre |
| gini | `SI.POV.GINI` | Actif | 1996–2023 (24) | 2023 : 31,8 | Doublon INSEE/Eurostat (Gini du niveau de vie) : préférer la source nationale |
| bottom20 | `SI.DST.FRST.20` | Actif | 1996–2023 (24) | 2023 : 7,7 % | Idem (doublon) |
| lifeexp | `SP.DYN.LE00.IN` | Actif | 1995–2024 (25) | 2024 : 82,98 ans | Doublon INSEE : préférer l'INSEE |
| physicians | `SH.MED.PHYS.ZS` | Actif | 1995–2022 (23) | 2022 : 3,28 ‰ | Indicateur de **moyen** (pas de résultat) : non éligible selon la charte §3.4 ; préférer un indicateur d'accès (APL DREES, patients sans médecin traitant) |
| preprimary | `SE.PRE.ENRR` | Actif mais figé | 1995–2020 (21) | 2020 : 106,7 % | Taux brut > 100 % peu interprétable ; à abandonner |
| lfprratio | `SL.TLF.CACT.FM.ZS` | Actif (modélisé OIT) | 1995–2025 (26) | 2025 : 86,4 % | Doublon Eurostat (taux d'activité par sexe) : préférer Eurostat |
| railpass | `IS.RRS.PASG.KM` | Actif mais figé | 1995–2021 (22) | 2021 | Indicateur de volume, sens ambigu ; préférer SDES/Eurostat (part modale) |
| internet | `IT.NET.USER.ZS` | Actif | 1995–2024 (25) | 2024 : 88,7 % | Doublon Eurostat ; alternative Baromètre du numérique |
| hitechexports | `TX.VAL.TECH.MF.ZS` | Actif | 2007–2024 (18) | 2024 : 23,1 % | Indicateur de compétitivité, lien faible avec la prospérité ressentie |
| pmexposure | `EN.ATM.PM25.MC.M3` | Actif | 1995–2023 (24) | 2023 : 8,23 µg/m³ | Candidat ; alternative nationale SDES (exposition PM2,5 fond urbain) |
| co2pc | `EN.ATM.CO2E.PC` | **Archivé** (« indicator was not found… deleted or archived ») | — | — | Remplacer par `EN.GHG.CO2.PC.CE.AR5` (vérifié, 1995–2024, 2024 : 4,00 t) ou mieux Citepa/INSEE ; envisager l'empreinte carbone SDES |
| co2intensity | `EN.ATM.CO2E.PP.GD` | **Archivé** | — | — | Remplaçant probable `EN.GHG.CO2.RT.GDP.PP.KD` (résultat de la vague 3) ; indicateur d'intensité, à discuter |
| freexpression | OWID `freedom-of-expression-index` (V-Dem) | Actif | 1789–2025 (26 depuis 2000) | 2025 : 0,959 | Conserver (indice composite V-Dem ; voie OWID) |
| pressfreedom | OWID `press-freedom-index-rsf` | **Arrêté en 2021** sur OWID | 2013–2021 (9) | 2021 : 22,6 (ancienne échelle) | Remplacer par la source primaire RSF (CSV annuel 2002–2026) en traitant les ruptures 2013 et 2022 |
| judicialchecks | OWID `judicial-constraints-on-the-executive-index` (V-Dem) | Actif | 2000–2025 (26) | 2025 : 0,945 | Conserver (composite V-Dem) |
| academicfreedom | OWID `academic-freedom-index` (V-Dem) | Actif | 2000–2025 (26) | 2025 : 0,800 | Conserver (composite V-Dem) |

---

## 6. Synthèse : apport par dimension v0 (charte §4)

| Dimension | Sources les plus riches hors INSEE/Eurostat (vérifiées) |
|---|---|
| `niveau_de_vie` | OCDE How's Life (`1_5` difficulté à boucler les fins de mois 2004–2025) ; DREES (pauvreté après redistribution) ; BCE/Banque de France (dette, épargne des ménages) |
| `travail` | OCDE (`2_7` longues heures, `2_5` insécurité, `2_9` satisfaction au travail — courte) ; Assurance maladie (accidents du travail, maladies professionnelles) ; DARES non vérifiée |
| `logement_cadre_vie` | SDES (qualité de l'air, risques d'inondation) ; OCDE (`3_5` chauffage, `9_2`, `9_3`) ; BCE (prix immobiliers) ; Odissé (jours de canicule) |
| `sante` | Odissé (suicides, tabac, santé mentale) ; DREES (EVSI, accès aux soins) ; OCDE (`5_3` décès par suicide/alcool/drogues, mortalité évitable) ; OMS |
| `education` | DEPP (examens, évaluations — séries courtes) ; OCDE (PISA, PIAAC via How's Life) ; Baromètre du numérique |
| `liens_bien_etre` | OCDE (`7_1` soutien social, `11_2` affects négatifs 2006–2025 ; `11_1` satisfaction, `7_4` solitude — courtes) ; WHR (2011–2025) ; Odissé (Baromètre 2024) ; CEPREMAP exclu |
| `securite_confiance` | SSMSI (délinquance enregistrée, sentiment d'insécurité) ; OCDE (`10_2` sécurité la nuit 2006–2025, `10_1`, `10_3`, `14_1` confiance dans les autres) ; ONISR |
| `democratie` | V-Dem via OWID (2000–2025), Freedom House, RSF (2002–2026), CPI (2012–2025), WGI (1996–2025), WJP (2012–2021) ; Intérieur (participation électorale 1999–2026) ; OCDE (`14_3` confiance dans le gouvernement 2006–2025, `14_5` parité, `14_7` bénévolat) ; CEVIPOF exclu |
| `egalites` | DREES (redistribution) ; PNUD (IDH ajusté, inégalités de genre) ; OCDE (IDD, patrimoine) ; WID non vérifié |
| `planete` | SDES (empreinte carbone, air) ; Citepa (inventaire 1990–2025) ; EDGAR ; OCDE bien-être futur (Liste rouge, aires protégées, empreinte matières, recyclage, nutriments) ; Hub'Eau ; GFN non vérifié ; ONB indisponible |
