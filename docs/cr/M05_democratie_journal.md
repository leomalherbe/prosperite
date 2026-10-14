# Journal de bord — M05, dimension `democratie` (Démocratie et institutions)

Agent de mission M05, branche `m05-democratie`, 14 octobre 2026. Méthode commune suivie : `docs/methodo/33_methode_fiches_M05.md` (v1.0), pilotes `liens_bien_etre` et `securite`.

## 0. Mise en route

- Branche `m05-democratie` créée depuis `origin/main` (`48e2381`, fusion du pilote `securite`).
- Lus : `CLAUDE.md`, charte (§3.4, §3.6, §4, §5.1), journal des décisions (D13–D30, en particulier D17, D18, D24 : A8, A10, A11), fiche M05, méthode commune, `indicateurs/dimensions.yaml`, `_modele_fiche.yaml`, fiches et règles des deux pilotes, journal du pilote `securite`, `30_crosswalk_synthese.md` (§5), `30_indicateurs_cadres_reference.csv` (lignes `democratie`), `10_indicateurs_candidats_hors_insee_eurostat.csv`, `autres_sources.md` (§2.10, §3.2, §3.3), `insee.md`, `eurostat.md`, sorties du robot M04 (`docs/sources/series/` : élections, OWID, WGI, OCDE, RSF, Freedom House, WJP).
- Tests : `pip install -r requirements.txt && python -m pytest -q` → 394 réussis.
- Aucun fichier sous `scripts/` ni `src/` n'est modifié (pas de déclenchement du robot « Collecte »). Les scripts de travail de l'agent (écriture des règles et des fiches) sont restés dans le bac à sable ; les fiches sont écrites par `preselection.texte_yaml` comme le demande la méthode.

## 1. Ce que contient la long-list `democratie`

250 lignes : 129 éligibles, 32 à vérifier, 89 non éligibles ; Eurostat 117, autres sources (M04) 101, INSEE BDM 26, Melodi 6 ; 64 lignes marquées composites.

| Bloc (mots-clés du libellé) | Lignes | oui / à vérifier / non | Constat |
|---|---|---|---|
| Administration en ligne (`isoc_ciegi_ac`, `isoc_ciegi_rtx`) | 96 | 20 / 0 / 76 | 38 % de la long-list : usages des sites des pouvoirs publics et motifs de non-usage ; séries 2008-2021, puis nouvelles séries 2022-2025 (rupture), modules 2013 |
| V-Dem (relais OWID) | 31 | 31 / 0 / 0 | indices globaux (libérale, électorale, participative, délibérative, égalitaire), sous-indices et questions d'experts (médias, corruption, polarisation) |
| Justice, prisons et autres | 29 | 24 / 1 / 4 | détention provisoire, occupation carcérale, population écrouée, activité des tribunaux (`crim_crt_*`), dépenses pour les tribunaux, signalement à la police, probité, consultation réglementaire (OCDE 14_4) |
| Participation électorale | 23 | 0 / 21 / 2 | INSEE BDM (2012-2024, champ « France » et métropole) et fichier agrégé du ministère (1999-2026, calcul du robot M04), OCDE 8_2, V-Dem/IDEA, votes blancs |
| Confiance et voix | 21 | 10 / 10 / 1 | INSEE ODD 16.i4 (Cevipof, 5 institutions, BDM et Melodi), OCDE (8_1, 14_2, 14_3), WVS/EVS via OWID |
| WGI | 12 | 12 / 0 / 0 | 6 indicateurs × 2 échelles (estimation, score 0-100) |
| Freedom House | 10 | 10 / 0 / 0 | score global, droits politiques et libertés civiles (OWID), 7 catégories (fichier 2013-2024) |
| WJP | 9 | 9 / 0 / 0 | score global et 8 facteurs |
| Indépendance perçue de la justice (`sdg_16_40`) | 7 | 7 / 0 / 0 | modalités et regroupements |
| RSF | 7 | 1 / 0 / 6 | score annuel 2002-2026 ; relais OWID arrêté en 2021 ; 5 sous-scores 2022-2026 |
| CPI | 3 | 3 / 0 / 0 | Eurostat `sdg_16_50`, OCDE 14_6, OWID |
| Parité politique (`sdg_05_50`) | 2 | 2 / 0 / 0 | relève de `egalites` (A8) |

Lignes d'autres long-lists traitées : les 3 lignes `securite` signalées `autre_dimension:democratie` par le pilote (règle 1090 : `crim_pris_tri` modalité `TRI_PRE`, `crim_pris_cap` × 2) sont importées ici comme variantes (§3).

## 2. Méthode appliquée et choix propres à la dimension

### 2.1 Règle des composites (D18)
- **Une famille par producteur** (`vdem`, `freedom_house`, `wgi`, `wjp`, `rsf`, `cpi`), une seule variante principale, les sous-indices en `variantes` de la principale. Variante principale = l'indice dont le concept est le plus proche de la dimension : démocratie libérale (V-Dem, proposée par la table des cadres comme version continue de l'indicateur de régime du Doughnut), voix et responsabilité (WGI), score global (Freedom House, WJP, RSF, CPI).
- **Fiches non principales dans une famille de producteur** (`retenir_variante`) : démocratie participative (V-Dem, plus proche du thème participation, alternative à l'indice libéral) ; État de droit et contrôle de la corruption des WGI, gardés en fiches parce qu'ils couvrent 2000-2025 alors que le WJP ne commence qu'en 2012-2013 et le CPI n'est comparable que depuis 2012. Ces deux fiches ne sont pas substituables à « voix et responsabilité » au sens strict de la méthode (§1) : c'est une exception assumée, à trancher par la session mère (questions, §7).
- **Concepts distincts nommés dans le contenu de la dimension** (« libertés d'expression, de la presse, académique ») : liberté d'expression (V-Dem) et liberté académique (V-Dem) forment chacune leur famille (fiche propre admise par la consigne : concept distinct) ; la liberté de la presse est la famille RSF.
- Écartés en bloc : polarisation (V-Dem, question isolée, sens discutable), droits humains de Fariss (arrêté en 2019).

### 2.2 Séries irrégulières (D17)
- Participation électorale : une fiche par type de scrutin, toutes dans la famille `participation_electorale` (substituables : l'utilisateur choisit le scrutin de référence), principale = présidentielle ; `frequence: irreguliere` et `formule` (votants / inscrits de tous les bureaux, report de la valeur du dernier scrutin jusqu'au suivant).
- **Choix de la source principale** : le fichier agrégé du ministère de l'Intérieur (niveau 2, calcul du robot M04) plutôt que la BDM de l'INSEE (niveau 1), parce qu'il remonte à 2002 (présidentielle, législatives), 1999 (européennes), 2004 (régionales), 2008 (municipales) et va jusqu'en 2026, alors que les séries INSEE commencent en 2012-2015 et ne sont plus mises à jour pour les municipales. Le critère « niveau 1 > 2 » de la méthode cède ici à la profondeur (même logique que le pilote `securite` pour Eurostat contre INSEE). Les séries INSEE sont en variantes.
- **Champ** : `geo: FR` (France entière). La valeur 2022 du fichier (73,69 %) est celle de l'OCDE (8_2) ; l'INSEE publie des taux plus élevés de 0,9 à 1,6 point selon le scrutin (champ « France », sans doute sans les Français de l'étranger, à vérifier). Les inscrits du fichier passent de 43,3 à 46,0 millions entre 2007 et 2012 : comparabilité 2002-2007 / 2012-2022 à contrôler (maintenance n° 13).
- Sentiment d'avoir son mot à dire (OCDE 8_1, 2021 et 2023), confiance dans le Parlement et dans l'administration (WVS/EVS, 3 vagues depuis 2000), citoyenneté active (EU-SILC 2015 et 2022) : retenus comme seule mesure de leur concept (précédent `liens_bien_etre/solitude`).

### 2.3 Variante principale hors composites
- Confiance dans les institutions : INSEE BDM (ODD 16.i4, données du baromètre du Cevipof), une famille par institution (justice, police, armée, école, hôpital) ; copies Melodi = doublons techniques ; WVS/EVS et OCDE 14_2 = autres sources.
- Détention provisoire : INSEE BDM 16.i3 (2010-2025) principal ; Eurostat `crim_pris_tri` (2008-2024, valeurs identiques de 2010 à 2019) = partenaire du raccordement 2008-2009 ; ONU 16.3.2 via l'OCDE = variante (moyenne N-2 à N d'après la fiche INSEE).
- Occupation carcérale : INSEE BDM (2012-2024) principal ; rapport des deux séries Eurostat `crim_pris_cap` (2008-2024) = raccordement à étudier (116,8 % contre 116,3 % en 2012).
- CPI : Eurostat `sdg_16_50` (niveau 1) principal, OCDE et OWID = doublons.

### 2.4 Drapeaux
- `declaratif: oui` : confiance (8 fiches), indépendance perçue de la justice, sentiment d'avoir son mot à dire (10 fiches). `non` : participation, citoyenneté active (fait déclaré), signalement à la police (fait déclaré, même règle que le pilote `securite`), composites (évaluations d'experts).
- `sens: ambigu` → `ecarter` : signalement à la police (ODD 16.3.1). Écartés en bloc pour sens ambigu : votes blancs, activité des tribunaux et des parquets, condamnés écroués, atteintes à la probité enregistrées.
- `type: moyen` : dépenses publiques pour les tribunaux (D19), écartées (euros courants, pas de cible officielle).

### 2.5 Incontournables
Méthode §4 : `oui` seulement pour les concepts du §5 de la synthèse du crosswalk. Pour `democratie`, un seul concept y figure : **participation et voix politique** (Doughnut — régimes, V-Dem —, SSF — démocratie et libertés —, OCDE 8_1 et 8_2, Eurostat — participation, citoyenneté active, voix et responsabilité). Portent `incontournable: oui` les fiches qui mesurent ce concept d'après les lignes de la table des cadres : participation (6 fiches de la famille), voix (8_1), citoyenneté active, V-Dem libérale et participative (famille `vdem`), voix et responsabilité (WGI), RSF (proposé pour le thème SSF dans la table des cadres). **Corruption et confiance dans les institutions ne sont présentes que dans deux cadres** (§5, dernier paragraphe) : `incontournable: non`, bien que la consigne de mission les cite comme incontournables ; elles ont toutes une fiche `retenir` (question à la session mère, §7). Dans la famille `wgi`, l'incontournable n'est porté que par la fiche principale (les deux autres fiches mesurent d'autres concepts).

## 3. Présélection (`scripts/preselection.py --dimension democratie`)

- Règles : `docs/validation/regles_preselection_democratie.csv` (86 règles) → `preselection_democratie.csv` (86 groupes) et `preselection_democratie_lignes.csv` (253 lignes : 250 de la long-list + 3 de `securite`). **Aucune ligne sans règle.**
- 32 groupes `fiche` (31 lignes ; `citoyennete_active` est une règle `hors_longlist = oui`), 41 groupes `variante_de` (100 lignes), 11 `ecarte_en_bloc` (82 lignes, dont 30 éligibles), 2 `autre_dimension` (40 lignes, dont 10 éligibles).
- Écarts en bloc : votes blancs (1), consultation réglementaire OCDE 14_4 (1), modalités détaillées de `sdg_16_40` (5), condamnés écroués (2), mis en cause poursuivables (2), activité des tribunaux `crim_crt_*` (10), atteintes à la probité (1), polarisation V-Dem (1), Fariss (1), administration en ligne mesurée en 2013 seulement (14), motifs de non-usage `isoc_ciegi_rtx` (44).
- `autre_dimension:egalites` : parité au Parlement et au gouvernement (`sdg_05_50`, 2 lignes, A8). `autre_dimension:logement_cadre_vie` : usage d'internet pour interagir avec les pouvoirs publics (`isoc_ciegi_ac`, 38 lignes, accès numérique aux services, A7).
- Lignes `securite` (règle 1090 du pilote) : `estat-032530` (`crim_pris_tri`, TRI_PRE) → variante de `detention_provisoire` ; `estat-032525`, `estat-032526` (`crim_pris_cap`) → variantes de `occupation_carcerale`. Rattachement à `democratie` proposé (R1).

## 4. Vérifications faites sur les sources (14/10/2026)

| Source (WebFetch) | Constat |
|---|---|
| BDM 010596050 à 010596054 (confiance, 16.i4) | 2013-2024, FE ; justice 44-48 %, police 66-78 %, armée 72-83 %, école 65-74 %, hôpital 76-83 % ; 2024 révisée pour la justice |
| Fiche de métadonnées INSEE 16.i4 (PDF) | source : baromètre de la confiance politique du Cevipof (lancé en 2009), environ 3 500 inscrits sur les listes électorales, 18 ans ou plus, « très » + « plutôt » confiance (Q25) |
| BDM 010596049 et fiche de métadonnées INSEE 16.i3 | 2010-2025 (24,7 % à 29,0 %) ; rupture 2019 (condamnés-prévenus comptés parmi les condamnés) ; 2025 au 30 août ; identique à l'ODD 16.3.2 (base mondiale : moyenne N-2 à N) |
| BDM 001779317 | occupation carcérale 2012-2024 : 116,3 % → 103,4 % (2020) → 129,5 % (2024) |
| BDM 001778320, 001778322, 001778442, 001778185 | participation INSEE : présidentielle 80,7 / 79,0 / 75,3 % (2012/2017/2022, FE), législatives 58,2 / 49,6 / 48,4 / 67,9 %, européennes 43,4 / 51,3 / 53,0 % |
| Eurostat `sdg_16_40` (VG_FG) et métadonnées | 2016-2025 (54 % → 59 % en 2019 → 51 % en 2025), sans drapeau ; source : Flash Eurobaromètre (DG Justice), hors système statistique européen |
| Eurostat `sdg_16_50` | CPI 2012-2025 : 71 → 72 (2018, 2022) → 66 (2025), sans drapeau |
| Eurostat `sdg_16_30` | 54,3 € (2000) → 120,6 € par habitant (2024, provisoire) |
| Eurostat `crim_pris_tri` (TRI_PRE), `crim_pris_cap` | 2008-2024 sans drapeau ; détention provisoire identique à l'INSEE de 2010 à 2019 (écart ≤ 0,3 point ensuite) ; rapport détenus / capacité = 116,8 % (2012), 129,3 % (2024) |
| Eurostat `ilc_scp19` | citoyenneté active (AC43A) 24,8 % (2015), 11,9 % (2022) ; bénévolat formel 23,0 / 15,6 %, informel 23,3 / 11,1 % |
| API Banque mondiale `GOV_WGI_VA.EST` et `.SC` | 1996-2025 sans 1997, 1999, 2001 ; 0,95 (2000), 1,48 (2005), 1,16 (2025) ; score 0-100 : 75,2 → 79,0 |
| Page OWID `liberal-democracy-index` | source V-Dem v16 ; dernière valeur France 0,8 (2025) ; données tierces sous licence du fournisseur |
| Sorties du robot M04 (lues dans le dépôt) | participation par scrutin 1999-2026 ; RSF 2002-2026 (3,25 en 2002, 78,4 en 2013, 78,53 en 2022, 76,68 en 2026) ; Freedom House 2013-2024 (90 puis 89 depuis 2022) ; WJP 0,764 (2012-2013) → 0,724 (2025) ; OCDE 8_1 (26,3 % en 2023), 14_3 (37,3 % en 2025) ; WVS/EVS (Parlement 33,1 %, administration 52,6 % en 2022) |

Non lus (accès refusé à l'outil de lecture ou absence de métadonnées) : documentation des WGI, schéma du fichier des élections (champ des Français de l'étranger), page des résultats du ministère de l'Intérieur, codebook V-Dem. Les définitions concernées le signalent (« non lu », « à vérifier »).

## 5. Résultats

- **32 fiches** dans **24 familles** : **22 `retenir`**, 7 `retenir_variante`, 3 `ecarter` ; 10 déclaratives ; 11 composites ; 10 à vérifier (D17) ; 1 hors long-list (`citoyennete_active`) ; 12 incontournables ; 100 variantes.
- Composites par famille : V-Dem 2 fiches (libérale `retenir`, participative `retenir_variante`) + 2 familles de concept V-Dem (liberté d'expression, liberté académique : `retenir`) ; WGI 3 fiches (voix et responsabilité `retenir`, État de droit et contrôle de la corruption `retenir_variante`) ; Freedom House, WJP, RSF, CPI : 1 fiche `retenir` chacune.
- Irréguliers : 6 participation, voix, citoyenneté active, confiance dans le gouvernement, le Parlement, l'administration, WJP (12 fiches `frequence: irreguliere`).

| Sous-thème | retenir | retenir_variante | ecarter |
|---|---|---|---|
| participation électorale | participation_presidentielle | participation_legislatives, participation_europeennes, participation_municipales, participation_regionales | participation_departementales |
| voix et participation citoyenne | voix_pouvoirs_publics, citoyennete_active | | |
| confiance dans les institutions | confiance_justice, confiance_police, confiance_armee, confiance_ecole, confiance_hopital, confiance_gouvernement, confiance_parlement, confiance_administration | | |
| justice et État de droit | independance_justice_percue, detention_provisoire, occupation_carcerale, etat_de_droit_wjp | etat_de_droit_wgi | depenses_tribunaux, signalement_police |
| libertés | liberte_expression_vdem, liberte_academique_vdem, libertes_freedom_house, liberte_presse_rsf | | |
| qualité démocratique (composites) | democratie_liberale_vdem, voix_responsabilite_wgi | democratie_participative_vdem | |
| corruption et intégrité | perception_corruption_cpi | controle_corruption_wgi | |

**Nombre de `retenir` : 22.**

## 6. Contrôles (tâche 5)

`python scripts/verifier_fiches.py --dimension democratie --tableau` :

```
Dimension democratie : lignes_longlist 250, lignes_autre_dimension 40, fiches 32, familles 24, retenir 22,
retenir_variante 7, ecarter 3, declaratifs 10, composites 11, a_verifier 10, hors_longlist 1,
incontournables [citoyennete_active, democratie_liberale_vdem, democratie_participative_vdem, liberte_presse_rsf,
participation_departementales, participation_europeennes, participation_legislatives, participation_municipales,
participation_presidentielle, participation_regionales, voix_pouvoirs_publics, voix_responsabilite_wgi], variantes 100
avertissement — citoyennete_active : série principale hors catalogue de séries (jeu ilc_scp19 au catalogue des jeux) : à réintégrer au catalogue
0 erreur(s), 1 avertissement(s)
```

- L'avertissement est attendu (fiche hors long-list, réintégration demandée : maintenance n° 12).
- `premiere_annee` : le vérificateur n'admet que 1900-2100 ; les séries V-Dem libérale, participative et liberté d'expression commencent en 1789 dans le relais OWID : `premiere_annee` ramenée à 1900 et signalée dans les notes de chaque fiche (proposition de modification du script au compte rendu).
- Identifiants uniques dans `indicateurs/` (contrôle du vérificateur) ; pas de collision avec `liens_bien_etre` ni `securite`.

## 7. Points ouverts

- **Session mère** : (1) incontournables — corruption et confiance dans les institutions (deux cadres seulement) laissés à `non` malgré la consigne ; (2) fiches non principales `etat_de_droit_wgi` et `controle_corruption_wgi` dans la famille de producteur `wgi` (non substituables à la principale) ; (3) rattachements proposés : administration en ligne → `logement_cadre_vie`, parité politique → `egalites`, prisons (`crim_pris_*`) → `democratie`, confiance dans l'école et l'hôpital gardées ici (R5) ; (4) borne 1900 de `premiere_annee` dans `verifier_fiches.py`.
- **Léo** : source principale de la participation (fichier du ministère, niveau 2, plutôt que l'INSEE) ; nombre de fiches de participation (6) ; maintien de Freedom House (7 valeurs distinctes depuis 2002) ; RSF lisible seulement depuis 2013 ; citoyenneté active (division par deux entre 2015 et 2022, comparabilité à vérifier) ; confiance dans l'armée dans une dimension « démocratie ».
- Manques constatés : aucune série publique annuelle de confiance dans le gouvernement ou le Parlement (Cevipof en PDF, D9) ; pas de délai de jugement ni de taux de résolution des affaires publié au catalogue ; pas de confiance dans les institutions européennes (`sdg_16_60` absent du catalogue Eurostat).
- Corrections de catalogues : `docs/cr/maintenance_catalogues.md`, lignes 10 à 16 (`a_faire`).

## 8. Livraison

Commits sur `m05-democratie`, PR « M05 — fiches indicateurs : democratie » vers `main` ; compte rendu `docs/cr/M05_democratie_compte_rendu.md`, copié dans le Projet (`claude/cr/M05_democratie_compte_rendu.md`) avec le tableau de validation (`claude/40_validation_democratie.csv`).
