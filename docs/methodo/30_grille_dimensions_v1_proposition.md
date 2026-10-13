# Proposition de grille de dimensions v1 (mission M03, tâche T3)

Version 1 — 13 octobre 2026 — agent M03 (phase 2). **Proposition** soumise à la session mère et à Léo pour le **gel 1** (charte §3.6) : rien ici n'est décidé. Le dossier de décision, une page par dimension, est `31_dossier_decision_gel1.md` ; la table de correspondance v0 → v1 lisible par script est `31_correspondance_v0_v1.csv`.

Sources de la proposition : extraction des six cadres (`30_cadres_reference_extraction.md`), crosswalk de 344 lignes (`30_indicateurs_cadres_reference.csv`) et sa synthèse (`30_crosswalk_synthese.md`) ; repérage INSEE de 1 063 séries taguées `dimension_v0` (branche `m01-insee`, `docs/sources/insee_indicateurs_reperes.csv`) ; fiches des sources hors INSEE et Eurostat (branche `m04-sources`, `docs/sources/autres_sources.md` et `10_sources_inventaire.csv`). Le catalogue Eurostat de phase 2 (M02) n'existe pas encore : les séries Eurostat ne sont comptées qu'à travers le crosswalk.

---

## 1. La proposition en bref

**La grille v1 proposée garde les dix domaines de v0 et en redessine les frontières.** Les six cadres valident les dix domaines (341 des 344 lignes du crosswalk s'y rattachent) ; aucun n'impose une onzième dimension faisable. Les changements portent sur ce qui passe d'une dimension à l'autre, fixés par douze règles de partage (§3). Aucune fusion, aucune création, un identifiant renommé (`securite_confiance` → `securite`).

| # | id | Libellé | Type | Cadres (sur 6) | Candidats France estimés : stricts / élargis | Critères du gel 1 |
|---|---|---|---|---|---|---|
| 1 | `niveau_de_vie` | Niveau de vie et économie | plancher | 6 | ≈ 25 / ≈ 30 | remplis |
| 2 | `travail` | Travail et emploi | plancher | 6 | ≈ 18 / ≈ 22 | remplis |
| 3 | `logement_cadre_vie` | Logement et cadre de vie | plancher | 5 | ≈ 14 / ≈ 18 | remplis |
| 4 | `sante` | Santé | plancher | 6 | ≈ 13 / ≈ 18 | remplis |
| 5 | `education` | Éducation et compétences | plancher | 6 | ≈ 8 / ≈ 15 | remplis, faisabilité juste |
| 6 | `liens_bien_etre` | Liens sociaux et bien-être ressenti | plancher | 5 | ≈ 6 / ≈ 13 | faisabilité **sous condition** (séries courtes, D17) |
| 7 | `securite` | Sécurité | plancher | 5 | ≈ 13 / ≈ 16 | remplis |
| 8 | `democratie` | Démocratie et institutions | plancher | 4 | ≈ 3 hors composites / ≈ 16 avec composites | faisabilité **sous condition** (composites, D18) |
| 9 | `egalites` | Égalités | plancher | 6 (comme contenu) ; 1 comme dimension nommée | ≈ 16 / ≈ 20 | remplis ; dimension propre justifiée par la finalité |
| 10 | `planete` | Planète | plafond | 5 | ≥ 40 / ≥ 50 | remplis |

« Stricts » : concepts distincts disposant d'une série France annuelle ou annualisable, d'au moins 10 points depuis 2000 et d'une dernière valeur ≥ 2020 (charte §3.4). « Élargis » : en ajoutant les dérogations actées (D16 raccordement, D17 indicateurs irréguliers, D18 composites, D19 indicateurs de moyens). Méthode de l'estimation : §2.

**Arbitrages** (détail au §5) : satisfaction dans la vie = indicateur de la dimension 6, affichée aussi comme repère à côté de l'indice ; alimentation, énergie et temps répartis selon la nature de l'indicateur ; économie et ressources pour l'avenir = sous-thème de la dimension 1 ; sécurité routière en sécurité ; accès au numérique en cadre de vie, compétences numériques en éducation ; discriminations selon l'origine en égalités ; égalités = dimension propre ; démocratie et sécurité gardées distinctes et enrichies ; confiance partagée entre liens (interpersonnelle) et démocratie (institutionnelle) ; PIB par habitant en repère hors indice.

---

## 2. Méthode

### 2.1 Démarche
1. Point de départ : les dix dimensions de v0 (charte §4).
2. Pour chaque dimension, relevé des **cadres qui la retiennent** (crosswalk remappé en v1 : un cadre la retient s'il y rattache au moins un indicateur ; on précise s'il en fait une dimension nommée).
3. **Indicateurs incontournables** : concepts présents dans au moins trois des cinq cadres de bien-être (Doughnut, SSF, OCDE, Eurostat, INSEE), d'après le §5 de la synthèse du crosswalk, complété en phase 2 (santé mentale : SSF, OCDE, Eurostat).
4. **Règles de partage** (§3) pour que chaque indicateur n'appartienne qu'à une dimension (critère « distincte » du gel 1) ; elles sont traduites en règles automatiques dans `31_correspondance_v0_v1.csv`.
5. **Faisabilité** : estimation du nombre de candidats France (§2.2).
6. **Arbitrages** : au moins deux options, conséquences, recommandation (§5).

### 2.2 Estimation du nombre de candidats
Trois comptages complémentaires, aucun n'étant à lui seul un nombre de « candidats éligibles » (ce sera le travail du gel 2) :
- **Crosswalk** : lignes rattachées à la dimension v1 et disponibilité estimée en phase 1 (`oui`, `probable`, `non`). Une ligne = un indicateur tel qu'un cadre le définit ; un même concept peut compter plusieurs fois (OCDE et Eurostat, par exemple).
- **Repérage INSEE** (M01) : séries hors ventilations et hors `candidat = non`, remappées en v1 par `31_correspondance_v0_v1.csv` ; « strictes » = première et dernière période du repérage compatibles avec la charte (≥ 10 points depuis 2000, dernière ≥ 2020). Le comptage **sous-estime** les séries trimestrielles dont la période n'a pas été relevée (travail) et **surestime** les concepts (doublons BDM/Melodi, France/métropole).
- **Sources M04** : séries vérifiées hors INSEE et Eurostat (OCDE, SSMSI, ONISR, V-Dem, etc.), avec leur profondeur.

L'**estimation finale** (tableau du §1) est un nombre de **concepts distincts** établi à la main à partir de ces trois comptages ; chaque fiche du §4 donne une liste nommée d'au moins huit candidats quand elle existe.

### 2.3 Comptages par dimension v1

| Dimension v1 | Crosswalk : lignes (oui / probable / non) | dont déclaratifs | Lignes par cadre : DN / SSF / OCDE / QoL / NIR / ODD-obj | INSEE : séries (libellés distincts) | INSEE strictes (libellés distincts) |
|---|---|---|---|---|---|
| `niveau_de_vie` | 42 (35 / 6 / 1) | 3 | 3 / 7 / 11 / 9 / 5 / 7 | 61 (57) | 33 (31) |
| `travail` | 42 (28 / 7 / 7) | 4 | 1 / 4 / 11 / 23 / 1 / 2 | 59 (54) | 10 (8) — sous-estimé |
| `logement_cadre_vie` | 38 (26 / 10 / 2) | 7 | 7 / 4 / 11 / 10 / 0 / 6 | 30 (28) | 25 (23) |
| `sante` | 30 (20 / 10 / 0) | 5 | 2 / 3 / 8 / 11 / 2 / 4 | 63 (51) | 17 (15) |
| `education` | 33 (15 / 9 / 9) | 0 | 2 / 2 / 10 / 8 / 1 / 10 | 10 (9) | 9 (8) |
| `liens_bien_etre` | 39 (10 / 17 / 12) | 22 | 1 / 7 / 14 / 16 / 1 / 0 | 6 (6) | 4 (4) |
| `securite` | 14 (11 / 3 / 0) | 3 | 1 / 2 / 4 / 5 / 0 / 2 | 22 (21) | 12 (12) |
| `democratie` | 17 (5 / 3 / 9) | 7 | 2 / 2 / 6 / 7 / 0 / 0 | 21 (14) | 9 (9) |
| `egalites` | 33 (17 / 11 / 5) | 4 | 3 / 6 / 13 / 5 / 2 / 4 | 31 (31) | 23 (23) |
| `planete` | 55 (33 / 15 / 7) | 0 | 13 / 2 / 15 / 0 / 3 / 22 | 192 (162) | 141 (115) |
| hors grille | 1 (levier financier, OCDE 15_8) | 0 | — | — | — |

Total : 344 lignes du crosswalk ; 496 séries INSEE non ventilées et candidates (sur 1 063 repérées). Onze lignes du crosswalk changent de dimension par rapport à la phase 1 (liste au §6.2).

---

## 3. Règles de partage entre dimensions

Ces règles rendent les dimensions **conceptuellement distinctes** (un indicateur n'appartient qu'à une dimension) et servent au rattachement automatique de la long-list (gel 2).

| N° | Règle | Exemple |
|---|---|---|
| R1 | Un indicateur va dans la dimension du **résultat qu'il mesure pour les personnes** (ou pour la planète), pas dans celle de la politique qui l'influence. | Renoncement aux soins pour raisons financières → santé (accès aux soins), pas niveau de vie. |
| R2 | **Planète = pressions exercées** (plafond) ; **cadre de vie = conditions subies localement** (plancher). | Émissions de particules → planète ; exposition aux PM2,5, eau du robinet non conforme, jours de canicule → cadre de vie. |
| R3 | **Égalités = écarts et dispersions** entre personnes ou entre groupes ; les niveaux moyens et les taux de privation vont dans la dimension du domaine. Les ventilations (sexe, âge…) restent des ventilations (D21). | S80/S20, écart salarial femmes-hommes → égalités ; taux de pauvreté, salaire moyen → niveau de vie / travail. |
| R4 | **Confiance envers les autres → liens** ; **confiance dans les institutions → démocratie**. | Confiance interpersonnelle (OCDE 14_1, Eurostat ilc_pw03) → liens ; confiance dans la justice, le gouvernement → démocratie. |
| R5 | **Numérique : accès et usage → cadre de vie** (équipement, haut débit, usage d'internet) ; **compétences et illectronisme → éducation**. | Haut débit à domicile → cadre de vie ; compétences numériques de base → éducation. |
| R6 | **Déclaratif** : l'évaluation d'un domaine va dans ce domaine ; l'évaluation de la vie dans son ensemble (satisfaction, affects, sens) va dans `liens_bien_etre`. | Satisfaction au travail → travail ; santé perçue → santé ; sentiment d'insécurité → sécurité ; satisfaction dans la vie → liens et bien-être ressenti. |
| R7 | **Sécurité** = atteintes aux personnes et aux biens, sécurité routière, **sécurité économique des ménages** (réserves, impayés, surendettement) ; la **sécurité de l'emploi** va en travail ; l'état de santé en santé. | Dépense imprévue, surendettement → sécurité ; transitions emploi → chômage → travail. |
| R8 | **Temps** : temps de travail rémunéré → travail ; temps libre, loisirs, volume de travail non rémunéré → liens ; **répartition** femmes-hommes des tâches → égalités. | Longues durées de travail → travail ; écart femmes-hommes de temps domestique → égalités. |
| R9 | **Alimentation** : accès (insécurité alimentaire, privation) → niveau de vie ; nutrition et corpulence → santé ; production agricole (engrais, pesticides, bio) → planète. | Renoncement à consommer des protéines → niveau de vie ; obésité → santé ; excédent d'azote → planète. |
| R10 | **Énergie** : précarité et accès → logement ; consommation, mix, renouvelables → planète. | Incapacité à chauffer son logement → logement ; part des énergies fossiles → planète. |
| R11 | **Culture et sport** (pratiques) → liens (loisirs) ; connaissances et compétences → éducation. | Non-participation culturelle ou sportive → liens. |
| R12 | **Ressources économiques pour l'avenir** (dette, R&D, investissement, patrimoine national) → sous-thème « économie et ressources pour l'avenir » de `niveau_de_vie`, avec `type: moyen` ou `stock` (D19). | Effort de recherche, dette publique → niveau de vie et économie. |

---

## 4. Les dix dimensions proposées

Chaque fiche suit la même structure : définition, type, question en langage courant, contenu, cadres, incontournables, déclaratifs, candidats, critères du gel 1, changement par rapport à v0.

### 4.1 `niveau_de_vie` — Niveau de vie et économie
- **Définition** : les ressources matérielles dont disposent les ménages (revenus, consommation, patrimoine), la pauvreté et les privations, et les ressources économiques du pays pour l'avenir.
- **Type** : plancher.
- **Question** : « Que doit refléter le niveau de vie ? Est-ce que les gens ont de quoi vivre correctement, combien vivent dans la pauvreté, et l'économie du pays est-elle solide pour la suite ? »
- **Contenu** : (a) revenus et consommation (niveau de vie médian, pouvoir d'achat, consommation effective) ; (b) pauvreté et privations, dont l'**accès à l'alimentation** ; (c) patrimoine des ménages ; (d) **économie et ressources pour l'avenir** : dette publique et privée, effort de recherche, investissement, patrimoine national (indicateurs `type: moyen` ou `stock`, D19).
- **Cadres** (6/6) : Doughnut (revenu et travail : pauvreté sociétale ; alimentation), SSF (niveau de vie matériel ; soutenabilité : stocks), OCDE (revenu et patrimoine ; capital économique), Eurostat (conditions de vie matérielles), INSEE (privation matérielle et sociale ; effort de recherche, endettement), ODD et objectifs (1.1, 1.2, 2.1, AROPE, 3 % de R&D, 60 % de dette).
- **Incontournables** : pauvreté monétaire relative (5 cadres) ; revenu disponible des ménages (3) ; privation matérielle (3).
- **Déclaratifs possibles** : difficulté à joindre les deux bouts (OCDE 1_5, EU-SILC) ; satisfaction à l'égard de la situation financière (modules SILC).
- **Candidats** : crosswalk 42 lignes (35 oui) ; INSEE 61 séries, 33 strictes ; M04 : OCDE 1_5 (2004–2025), DREES (pauvreté avant et après redistribution), BCE (dette des ménages depuis 1999), Banque mondiale (revenu national net ajusté, figé en 2021). Liste nommée (stricts) : niveau de vie médian (ERFS 1996–2023) ; pouvoir d'achat du revenu disponible par unité de consommation (comptes nationaux) ; consommation des ménages ; taux de pauvreté à 60 % et à 50 % (1996–2023) ; intensité de la pauvreté ; privation matérielle et sociale (SRCV 2013–2024) ; renoncement à consommer des protéines pour raisons financières (INSEE, ODD 2) ; difficulté à joindre les deux bouts (OCDE, 2004–2025) ; patrimoine des ménages (comptes de patrimoine) ; effort de recherche (1996–2024) ; dette publique, dette des ménages et des sociétés non financières (2010–2024 dans le tableau ODD, plus longues en comptes nationaux). **≈ 25 stricts, ≈ 30 élargis.**
- **Gel 1** : ≥ 3 cadres : oui (6). Distincte : oui (R3, R7, R9, R12). Faisable : oui. Intelligible : oui.
- **Changement par rapport à v0** : ajout de l'accès à l'alimentation (venant de santé) ; sous-thème « économie et ressources pour l'avenir » rendu explicite ; le **PIB par habitant** quitte le contenu indicatif et devient un repère affiché à côté de l'indice (arbitrage A12) ; la sécurité économique reste en sécurité (comme en v0).

### 4.2 `travail` — Travail et emploi
- **Définition** : l'accès à l'emploi et la qualité des emplois : stabilité, rémunération, conditions et santé au travail, temps de travail, satisfaction.
- **Type** : plancher.
- **Question** : « Que doit refléter le travail ? Est-ce que ceux qui veulent travailler trouvent un emploi, et est-ce que ces emplois sont de bonne qualité ? »
- **Contenu** : quantité d'emploi (emploi, chômage, chômage de longue durée, sous-emploi, halo, NEET) ; qualité et sécurité de l'emploi (contrats temporaires et temps partiel subis, bas salaires, surqualification, transitions vers le chômage) ; conditions et santé au travail (accidents, expositions, tension) ; temps de travail rémunéré (longues durées, horaires atypiques) ; satisfaction au travail.
- **Cadres** (6/6) : Doughnut (NEET), SSF (activités personnelles dont travail), OCDE (travail et qualité de l'emploi), Eurostat (activité productive), INSEE (taux d'emploi), objectifs (taux d'emploi 78 % en 2030, NEET < 9 %).
- **Incontournables** : taux d'emploi (3) ; longues durées de travail (3). Proches du seuil (2 cadres) : NEET, chômage de longue durée, accidents du travail, satisfaction au travail, bas salaires.
- **Déclaratifs possibles** : satisfaction au travail ; surqualification déclarée ; tension au travail.
- **Candidats** : crosswalk 42 lignes (28 oui) ; INSEE 59 séries (le comptage strict, 10, ignore les séries trimestrielles de l'enquête Emploi dont la période n'a pas été relevée) ; Eurostat EFT ; M04 : Assurance maladie (sinistralité depuis 2005), OCDE 2_7 ; DARES non vérifiée (refus du robot). Liste nommée : taux d'emploi 15-64 ans (1975–2024) et 20-64 ans ; taux de chômage ; chômage de longue durée ; sous-emploi ; halo du chômage ; NEET ; temps partiel subi ; contrats temporaires (et subis) ; surqualification ; accidents du travail ; longues durées de travail ; horaires atypiques ; ménages à très faible intensité de travail. **≈ 18 stricts, ≈ 22 élargis.**
- **Gel 1** : oui sur les quatre critères.
- **Changement par rapport à v0** : la sécurité de l'emploi (transitions emploi → chômage, Eurostat) y est rattachée (R7) ; le temps de travail rémunéré y est explicitement rangé (R8).

### 4.3 `logement_cadre_vie` — Logement et cadre de vie
- **Définition** : les conditions de logement (coût, qualité, espace, chauffage) et l'environnement de vie quotidien (air, bruit, eau du robinet, nature, exposition aux aléas, accès aux transports et au numérique).
- **Type** : plancher.
- **Question** : « Que doit refléter le logement et le cadre de vie ? Est-ce que chacun peut se loger correctement à un coût supportable, dans un environnement sain et bien desservi ? »
- **Contenu** : coût du logement ; qualité, surpeuplement ; précarité énergétique ; sans-abrisme ; environnement local (qualité de l'air, bruit, eau du robinet, espaces verts) ; exposition aux aléas climatiques (canicules, inondations) ; **accès aux services, aux transports et au numérique**.
- **Cadres** (5/6) : Doughnut (logement, eau et assainissement, énergie, connectivité), SSF (logement dans les activités personnelles ; environnement présent), OCDE (logement ; qualité de l'environnement), Eurostat (conditions matérielles ; environnement naturel et cadre de vie), ODD et objectifs (6.1, 6.2, 7.1, PM2,5, passoires énergétiques). INSEE NIR : aucun indicateur.
- **Incontournables** : surpeuplement et qualité du logement (3-4) ; pollution de l'air locale (3). Proches : coût du logement, précarité énergétique, accès à internet, espaces verts (2 cadres chacun).
- **Déclaratifs possibles** : satisfaction à l'égard du logement, du cadre de vie, des espaces verts ; bruit et pollution déclarés.
- **Candidats** : crosswalk 38 lignes (26 oui) ; INSEE 30 séries, 25 strictes ; M04 : SDES (exposition aux PM2,5, dépassements des normes), Santé publique France (jours de canicule 2004–2025), BCE (prix immobiliers), Baromètre du numérique (2007–2025), ITDD (logements suroccupés). Liste nommée : surpeuplement ; surcharge des coûts du logement ; problèmes structurels du logement ; incapacité à chauffer son logement (2010–2024) ; exposition aux PM2,5 (Banque mondiale 1995–2023, SDES) ; concentrations de PM10 en fond urbain (2010–2024) ; dépassements des seuils de qualité de l'air ; jours de canicule ; haut débit à domicile (2010–2025) ; usage d'internet ; part modale des transports collectifs (2010–2024) ; bruit déclaré (profondeur à vérifier). **≈ 14 stricts, ≈ 18 élargis** (eau du robinet non conforme 2016–2023, taux d'effort, sans-domicile).
- **Gel 1** : oui sur les quatre critères (≥ 3 cadres : 5).
- **Changement par rapport à v0** : reçoit l'accès au numérique (venant d'éducation), l'exposition aux aléas, l'eau du robinet et l'exposition aux pollutions locales (venant de planète) ; la précarité énergétique y reste.

### 4.4 `sante` — Santé
- **Définition** : l'état de santé de la population — durée de vie, vie en bonne santé, santé physique et mentale — et l'accès aux soins.
- **Type** : plancher.
- **Question** : « Que doit refléter la santé ? Est-ce qu'on vit longtemps et en bonne santé, physique et mentale, et est-ce que chacun peut se soigner ? »
- **Contenu** : longévité et mortalité (espérance de vie, espérance de vie sans incapacité, mortalité infantile, prématurée, évitable) ; santé perçue et morbidité ; santé mentale (dépression, suicide) ; accès aux soins (renoncement, besoins non satisfaits, accessibilité) ; comportements (tabac, alcool, corpulence, activité physique, nutrition).
- **Cadres** (6/6) : Doughnut (santé), SSF, OCDE (santé ; capital humain), Eurostat, INSEE (espérance de vie sans incapacité), ODD (3.1, 3.2, 3.4).
- **Incontournables** : espérance de vie (4) ; santé perçue et morbidité (3-4) ; santé mentale (3 : SSF, OCDE, Eurostat — ajout de la phase 2).
- **Déclaratifs possibles** : santé perçue ; limitations d'activité ; dépression déclarée ; douleur physique (OCDE 11_3).
- **Candidats** : crosswalk 30 lignes (20 oui) ; INSEE 63 séries, 17 strictes ; M04 : Santé publique France (suicides, tabac, santé mentale), DREES (accessibilité potentielle localisée, espérance de vie sans incapacité figée à 2018), OCDE 5_3 (2004–2023), OMS. Liste nommée : espérance de vie à la naissance ; espérance de vie sans incapacité / années de vie en bonne santé ; mortalité infantile ; mortalité prématurée ; suicides (taux standardisé) ; décès par suicide, alcool et drogues ; santé perçue ; maladies chroniques et limitations ; renoncement aux soins pour raisons financières (INSEE) ; besoins de soins non satisfaits ; tabagisme quotidien ; consommation d'alcool. **≈ 13 stricts, ≈ 18 élargis** (obésité, dépression, accessibilité aux médecins, activité physique).
- **Gel 1** : oui sur les quatre critères.
- **Changement par rapport à v0** : la sous-alimentation part en niveau de vie (R9) ; les tués sur la route (tagués santé par M01) partent en sécurité (R7, arbitrage A6).

### 4.5 `education` — Éducation et compétences
- **Définition** : le niveau d'éducation atteint et les compétences des jeunes et des adultes, y compris numériques, et l'accès à la formation tout au long de la vie.
- **Type** : plancher.
- **Question** : « Que doit refléter l'éducation ? Est-ce que les jeunes sortent de l'école avec un diplôme et des compétences solides, et est-ce que les adultes continuent d'apprendre ? »
- **Contenu** : diplômes et sorties précoces ; compétences des élèves ; compétences des adultes ; compétences numériques et illectronisme ; formation des adultes ; accueil de la petite enfance.
- **Cadres** (6/6) : Doughnut (éducation), SSF, OCDE (connaissances et compétences ; capital humain), Eurostat, INSEE (sorties précoces), objectifs (sorties précoces < 9 %, diplômés du supérieur ≥ 45 %, formation des adultes 65 %, compétences numériques 80 %).
- **Incontournables** : diplôme du secondaire / sorties précoces (5) ; compétences mesurées (3).
- **Déclaratifs possibles** : aucun dans les cadres.
- **Candidats** : crosswalk 33 lignes (15 oui, 9 non) ; INSEE 10 séries, 9 strictes ; M04 : DEPP (réussite au baccalauréat selon l'origine sociale depuis 1998), ITDD (jeunes en difficulté de lecture), OCDE (PISA, PIAAC). Liste nommée : sorties précoces (2003-2024) ; diplômés du supérieur parmi les 25-34 ans ; jeunes adultes diplômés du second cycle du secondaire ; formation des adultes ; compétences numériques de base et faibles compétences numériques (2015–2025, rupture en 2021) ; illectronisme ; jeunes en difficulté de lecture (journée défense et citoyenneté, profondeur à vérifier). Élargis (D17) : PISA (lecture, mathématiques, sciences, élèves faibles : 8 vagues 2000–2022), PIAAC (2 vagues). **≈ 8 stricts, ≈ 15 élargis.**
- **Gel 1** : ≥ 3 cadres : oui (6). Distincte : oui (R5, R11). Faisable : **oui, de justesse** au sens strict, confortable avec D17. Intelligible : oui.
- **Changement par rapport à v0** : la culture (pratiques culturelles) part en liens (loisirs, R11) ; l'accès à internet part en cadre de vie (R5) ; libellé raccourci (« et culture » retiré).

### 4.6 `liens_bien_etre` — Liens sociaux et bien-être ressenti
- **Définition** : la qualité des relations (soutien, solitude, confiance envers les autres, engagement), le temps libre et les loisirs, et la manière dont chacun évalue et ressent sa vie.
- **Type** : plancher.
- **Question** : « Que doit refléter cette dimension ? Est-ce que les gens peuvent compter sur d'autres, ont du temps pour eux et des loisirs, et se sentent bien dans leur vie ? »
- **Contenu** : relations et soutien ; solitude ; **confiance envers les autres** ; engagement (bénévolat, vie associative) ; temps libre, loisirs, **pratiques culturelles et sportives**, vacances ; **satisfaction dans la vie**, affects, sens.
- **Cadres** (5/6) : Doughnut (cohésion sociale : soutien social), SSF (liens sociaux ; bien-être subjectif, couche transversale), OCDE (liens sociaux ; bien-être subjectif ; équilibre vie professionnelle-vie privée), Eurostat (loisirs et interactions sociales ; expérience globale de la vie), INSEE (satisfaction dans la vie). Aucune cible ODD ni objectif chiffré.
- **Incontournables** : satisfaction dans la vie (4) ; soutien social (3-4) ; temps libre et emploi du temps (3). Proches : confiance envers les autres, bénévolat (OCDE, Eurostat ; SSF à vérifier).
- **Déclaratifs** : presque tout (22 lignes sur 39).
- **Candidats** : crosswalk 39 lignes (10 oui, 17 probable, 12 non) ; INSEE 6 séries, 4 strictes (toutes sur la satisfaction) ; M04 : OCDE (7_1 soutien social 2006–2025, 11_2 affects négatifs 2006–2025, 14_7 bénévolat 2007–2025 ; séries courtes : 11_1 satisfaction et 14_1 confiance, 7 points ; 7_4 solitude, 2 points), World Happiness Report (2011–2025), Eurostat ilc_pw01 et ilc_pw03 (annuelles récemment), Baromètre de Santé publique France (2024 seulement), baromètre d'opinion de la DREES (microdonnées 2000–2024, contenu à examiner). Liste nommée (stricts) : satisfaction dans la vie (INSEE SRCV 2010–2024) ; évaluation de la vie, échelle de Cantril (WHR 2011–2025) ; soutien social (OCDE 7_1) ; solde d'affects négatifs (OCDE 11_2) ; bénévolat (OCDE 14_7) ; impossibilité de s'offrir une semaine de vacances (SILC, à vérifier ; élément de la privation matérielle : rattachement à trancher au gel 2). Élargis : confiance envers les autres (OCDE 14_1, Eurostat ilc_pw03, INSEE SRCV 2020–2024) ; solitude ; satisfaction des relations et de l'emploi du temps (modules SILC) ; sens de la vie ; licences sportives (INJEP, à vérifier) ; indicateurs à calculer sur le baromètre DREES. **≈ 6 stricts, ≈ 13 élargis.**
- **Gel 1** : ≥ 3 cadres : oui (5). Distincte : oui (R4, R6, R11). Faisable : **sous condition** — huit candidats seulement en admettant les séries courtes ou irrégulières (D17) et les séries Gallup relayées par l'OCDE (origine à confirmer, M04). Intelligible : oui (libellé double assumé).
- **Changement par rapport à v0** : reçoit la confiance envers les autres (venant de `securite_confiance`) et la culture et le sport (venant d'éducation) ; garde la satisfaction dans la vie (arbitrage A1).

### 4.7 `securite` — Sécurité (nouvel identifiant, ex-`securite_confiance`)
- **Définition** : être protégé des atteintes aux personnes et aux biens, des accidents de la route et des coups durs financiers, et se sentir en sécurité.
- **Type** : plancher.
- **Question** : « Que doit refléter la sécurité ? Est-ce qu'on est à l'abri des violences, des vols et des accidents, est-ce qu'on peut faire face à un coup dur financier, et est-ce qu'on se sent en sécurité ? »
- **Contenu** : atteintes aux personnes (homicides, violences physiques et sexuelles, violences intrafamiliales) ; atteintes aux biens (cambriolages, vols) ; sentiment d'insécurité ; **sécurité routière** ; **sécurité économique des ménages** (dépense imprévue, arriérés, surendettement, épargne de précaution).
- **Cadres** (5/6) : Doughnut (paix et justice : homicides), SSF (insécurité physique et économique), OCDE (sécurité ; insécurité financière), Eurostat (sécurité économique et physique), ODD et objectifs (3.6, routes UE 2030). INSEE NIR : aucun.
- **Incontournables** : homicides (3-4) ; sécurité économique (3) ; sentiment d'insécurité (3).
- **Déclaratifs possibles** : sentiment d'insécurité (quartier, domicile, la nuit) ; criminalité perçue dans le quartier (SILC) ; opinion sur sa capacité d'épargne (enquête de conjoncture auprès des ménages).
- **Candidats** : crosswalk 14 lignes (11 oui) ; INSEE 22 séries, 12 strictes ; M04 : SSMSI (base des séries chronologiques, 2006–2023, 159 séries ; sentiment d'insécurité, 15 observations), ONISR (2005–2024), OCDE (10_1, 10_2 2006–2025, 10_3), Banque de France et ITDD (surendettement). Liste nommée : homicides ; violences physiques enregistrées ; violences sexuelles enregistrées ; cambriolages ; victimes de violences déclarées (enquête) ; sentiment d'insécurité dans le quartier ; sentiment de sécurité la nuit (OCDE) ; tués sur la route ; incapacité à faire face à une dépense imprévue ; arriérés de paiement ; situations de surendettement (2010–2024) ; criminalité perçue dans le quartier. **≈ 13 stricts, ≈ 16 élargis.**
- **Gel 1** : oui sur les quatre critères. Point d'attention (gel 2) : la délinquance **enregistrée** a un sens ambigu (elle croît aussi quand la révélation progresse : violences intrafamiliales) ; rupture CVS/VRS en 2022.
- **Changement par rapport à v0** : la confiance part en liens et en démocratie (R4) ; la sécurité routière arrive (A6) ; la sécurité de l'emploi part en travail (R7) ; identifiant renommé.

### 4.8 `democratie` — Démocratie et institutions
- **Définition** : la qualité de la vie démocratique : participation des citoyens, libertés publiques, État de droit et justice, intégrité des institutions et confiance qu'elles inspirent.
- **Type** : plancher.
- **Question** : « Que doit refléter la démocratie ? Est-ce que les citoyens participent et sont entendus, est-ce que les libertés sont respectées et est-ce qu'on peut faire confiance aux institutions ? »
- **Contenu** : participation et voix (participation électorale, avoir son mot à dire) ; libertés (expression, presse, académique) ; État de droit et justice (indépendance, détention provisoire) ; corruption et intégrité ; confiance dans les institutions ; qualité de l'action publique.
- **Cadres** (4/6) : Doughnut (voix politique ; corruption en paix et justice), SSF (voix politique et gouvernance), OCDE (engagement civique ; capital social : confiance, corruption), Eurostat (gouvernance et droits fondamentaux). Ni INSEE NIR, ni cible chiffrée.
- **Incontournables** : participation et voix politique (4). Proches : corruption (Doughnut, OCDE), confiance dans les institutions (OCDE, Eurostat).
- **Déclaratifs possibles** : confiance dans les institutions et le gouvernement ; avoir son mot à dire ; corruption perçue.
- **Composites** (D18) : V-Dem, Freedom House, RSF, indice de perception de la corruption, indicateurs de gouvernance de la Banque mondiale, World Justice Project.
- **Candidats** : crosswalk 17 lignes (5 oui, 9 non) ; INSEE 21 séries, 9 strictes (confiance dans cinq institutions 2013–2024, participation, prévenus) ; M04 : V-Dem via OWID (démocratie électorale et libérale, liberté d'expression, contraintes judiciaires, liberté académique, 2000–2025), Freedom House (droits politiques, libertés civiles, 2002–2025), RSF (2002–2026, ruptures 2013 et 2022), indice de perception de la corruption (2012–2025), Banque mondiale (voix et redevabilité, état de droit, contrôle de la corruption, efficacité de l'action publique, 1996–2025), World Justice Project (2012–2021), participation électorale (1999–2026, irrégulière), OCDE 14_3 (confiance dans le gouvernement 2006–2025). **≈ 3 stricts hors composites** (confiance dans le gouvernement, confiance dans les institutions, part des prévenus parmi les détenus) ; **≈ 16 avec les composites (D18) et la participation (D17).**
- **Gel 1** : ≥ 3 cadres : oui (4). Distincte : oui (R4). Faisable : **sous condition** — dépend des indices composites (D18). Intelligible : oui.
- **Changement par rapport à v0** : la confiance dans les institutions y est explicitement regroupée (R4) ; la parité politique part en égalités (R3).

### 4.9 `egalites` — Égalités
- **Définition** : les écarts de situation entre les personnes et entre les groupes : répartition des revenus et du patrimoine, écarts entre femmes et hommes, selon l'origine, entre territoires et entre générations, et mobilité sociale.
- **Type** : plancher (fondation sociale, comme dans le Doughnut ; les indicateurs sont de sens `bas`).
- **Question** : « Que doit refléter l'égalité ? Les écarts entre les plus aisés et les plus modestes, entre femmes et hommes, selon l'origine ou le lieu de vie, sont-ils acceptables ? »
- **Contenu** : inégalités de revenu et de patrimoine (S80/S20, Gini, Palma, D9/D1, part des 40 % les plus modestes, effet de la redistribution) ; écarts femmes-hommes (salaires, emploi, temps domestique, représentation) ; **écarts selon l'origine et discriminations** ; inégalités territoriales ; écarts entre générations ; mobilité sociale (réussite selon l'origine sociale).
- **Cadres** : comme **contenu**, 6/6 (Doughnut : égalité de genre et raciale, Palma en cohésion sociale ; SSF : couche transversale ; OCDE : variantes `_VER` et écarts entre groupes ; Eurostat : S80/S20, discriminations et égalité des chances ; INSEE : inégalités de revenus ; ODD 10.1, objectifs femmes-hommes) ; comme **dimension nommée**, le seul Doughnut (« Equality »). La dimension propre se justifie par la finalité (§5, A9).
- **Incontournables** : inégalité de revenu (5) ; écarts femmes-hommes (4).
- **Déclaratifs possibles** : discriminations ressenties (enquêtes TeO, Défenseur des droits : non annuelles) ; perception des inégalités (baromètre DREES) ; inégalités de satisfaction (OCDE).
- **Candidats** : crosswalk 33 lignes (17 oui) ; INSEE 31 séries, 23 strictes ; M04 : DREES (redistribution ; baromètre), PNUD (indice d'inégalité de genre 1990–2023), DEPP (réussite au baccalauréat selon l'origine sociale), WID (non vérifié). Liste nommée : S80/S20 (1996–2023) ; indice de Gini ; D9/D1 ; ratio de Palma ; part des 40 % les plus modestes ; S80/S20 avant redistribution ; écart de rémunération femmes-hommes (2010–2023) ; écart de taux d'emploi femmes-hommes (Eurostat) ; femmes parmi les cadres dirigeants de la fonction publique (2010–2023) ; femmes au Parlement (OCDE 14_5) ; indice d'inégalité de genre (PNUD, composite) ; écart de taux d'emploi entre nationaux et ressortissants de pays tiers (Eurostat). **≈ 16 stricts, ≈ 20 élargis** (Gini du patrimoine, part du décile supérieur, écarts territoriaux calculés, discriminations ressenties).
- **Gel 1** : ≥ 3 cadres : oui comme contenu, dimension propre justifiée par la finalité. Distincte : **oui à condition d'appliquer R3** (écarts ici, niveaux ailleurs). Faisable : oui. Intelligible : oui.
- **Changement par rapport à v0** : les discriminations selon l'origine et la parité politique y sont nommées ; les inégalités de satisfaction (variantes `_VER` de l'OCDE) y sont rangées.

### 4.10 `planete` — Planète
- **Définition** : les pressions que le mode de vie et l'économie français exercent sur les grands équilibres naturels — climat, biodiversité, sols, eau, cycles de l'azote et du phosphore, pollutions, ressources, énergie — à maintenir sous des plafonds.
- **Type** : plafond.
- **Question** : « Que doit refléter la planète ? Est-ce que notre façon de vivre reste dans les limites que la nature peut supporter, ici et ailleurs ? »
- **Contenu** : climat (émissions territoriales, empreinte carbone) ; **énergie** (consommation, part des fossiles, renouvelables) ; biodiversité ; sols (artificialisation, forêts) ; eau (prélèvements, état des masses d'eau, nitrates, pesticides) ; azote et phosphore ; pollutions (émissions de polluants, produits chimiques, déchets) ; ressources et circularité.
- **Cadres** (5/6) : Doughnut (9 dimensions du plafond), SSF (soutenabilité environnementale), OCDE (capital naturel), INSEE (empreinte carbone, artificialisation), ODD et objectifs (22 cibles chiffrées). Eurostat QoL : aucun (choix de conception).
- **Incontournables** : émissions de gaz à effet de serre / empreinte carbone (4) ; usage des sols (3).
- **Déclaratifs possibles** : aucun.
- **Candidats** : crosswalk 55 lignes (33 oui) ; INSEE 192 séries, 141 strictes ; M04 : Citepa (1990–2025), SDES, EDGAR, OCDE capital naturel, Hub'Eau. Bornes scientifiques disponibles : limites par habitant du Doughnut pour six empreintes (§1.5 de l'extraction). **≥ 40 stricts.**
- **Gel 1** : oui sur les quatre critères.
- **Changement par rapport à v0** : reçoit explicitement l'énergie (consommation et mix) ; cède au cadre de vie l'exposition aux pollutions locales, l'eau du robinet et les aléas (R2).

---

## 5. Arbitrages

Pour chacun : constat, options, conséquences, recommandation. Les arbitrages A1 à A10 sont ceux de la fiche de mission et de la commande de phase 2 ; A11 à A16 sont révélés par l'analyse.

### A1. Place de la satisfaction globale dans la vie
**Constat** : quatre traitements dans les cadres — absente (Doughnut), couche transversale (SSF, rec. 10), dimension propre (OCDE, Eurostat « +1 »), indicateur parmi dix (INSEE). Charte §3.1 : les déclaratifs sont des indicateurs, pas une dimension, sauf arbitrage.

| Option | Conséquences |
|---|---|
| **A. Dimension propre « Bien-être ressenti »** (satisfaction, affects, sens) | Lisible et cohérente avec la « prospérité subjective » ; précédent du Better Life Index (thème pondérable). Mais **infaisable au sens strict** : ≈ 5 concepts stricts (satisfaction INSEE, Cantril, affects négatifs, douleur, perspectives des ménages), et la dimension « liens sociaux » restante tomberait elle aussi sous 8 (≈ 4 stricts). Il faudrait en plus libérer une place (limite de 10). Double comptage : la satisfaction résume toutes les autres dimensions. |
| **B. Transversale, hors indice** : affichée à côté de l'indice comme repère (« ce que les gens disent ») | Conforme à SSF ; aucun double comptage ; utile pour valider l'indice et pour la phase 7. Mais l'utilisateur ne peut plus la pondérer, et la dimension 6 perd son indicateur le plus long et le plus robuste (faisabilité encore plus fragile). |
| **C. Indicateur de la dimension 6** (v0) | Faisable ; l'utilisateur garde la main (cocher, pondérer) ; cohérent avec l'INSEE et la charte §3.1. Mais la dimension mélange relations et évaluation globale de la vie, et le double comptage subsiste pour qui la coche. |

**Recommandation : C, complétée par l'affichage de B.** La satisfaction dans la vie est un indicateur de `liens_bien_etre` (proposée au socle à l'examen du gel 2), **et** elle est affichée en permanence à côté de l'indice comme repère, sans entrer deux fois dans le calcul. Motifs : seule option faisable sans fusion ailleurs ; préserve le choix de l'utilisateur ; affects et sens suivent le même traitement (indicateurs de la dimension 6).

### A2. Alimentation
**Constat** : Doughnut (sous-alimentation, insécurité alimentaire), Eurostat (fruits et légumes), ODD 2.1 ; en phase 1, partagés entre santé et niveau de vie.

| Option | Conséquences |
|---|---|
| A. Tout en santé | Simple, mais range une privation économique (ne pas pouvoir se payer un repas protéiné) avec la santé. |
| B. Tout en niveau de vie | Range l'obésité avec les revenus : contre-intuitif. |
| C. Dimension propre « Alimentation » | Infaisable (peu de séries : privation alimentaire, aide alimentaire, obésité) et la limite de 10 l'interdit. |
| **D. Répartition selon la nature (R9)** | Accès → niveau de vie ; nutrition → santé ; production agricole → planète. Chaque indicateur trouve une place naturelle ; l'alimentation n'est pas visible comme thème. |

**Recommandation : D.** En France la question alimentaire est surtout une question de pouvoir d'achat (privation) et de santé publique (corpulence) ; les pressions agricoles relèvent du plafond écologique.

### A3. Énergie
**Constat** : Doughnut (accès : électricité, combustibles propres — non pertinents en France), OCDE (incapacité à chauffer ; renouvelables), ODD 7, L100-4, SNBC.

| Option | Conséquences |
|---|---|
| A. Tout en cadre de vie | Mélange la précarité des ménages et la décarbonation. |
| B. Tout en planète | Range la précarité énergétique (privation sociale) dans un plafond écologique : sens incohérent. |
| C. Dimension propre « Transition énergétique » (prototype) | Indicateurs majoritairement de moyens (D19) ; prend une place. |
| **D. Répartition (R10)** | Précarité et accès → logement (plancher) ; consommation, fossiles, renouvelables → planète (plafond). |

**Recommandation : D.** Le sens de l'indicateur (plancher social ou plafond écologique) commande la dimension.

### A4. Temps et travail non rémunéré
**Constat** : dimension propre à l'OCDE (*Work-life balance*) ; SSF (emploi du temps, production domestique) ; Eurostat (travail non rémunéré « à développer »). Sources françaises : enquêtes Emploi du temps de 1999, 2010 et 2025 seulement.

| Option | Conséquences |
|---|---|
| A. Dimension propre « Temps et équilibre de vie » | Infaisable : quasiment aucune série annuelle (OCDE 4_x : une valeur 2009). |
| **B. Répartition (R8)** | Temps de travail rémunéré → travail ; temps libre, loisirs, volume de travail non rémunéré → liens ; répartition femmes-hommes des tâches → égalités. |

**Recommandation : B.** Le libellé de la dimension 6 mentionne le temps libre dans sa définition ; les séries d'emploi du temps seront admises comme irrégulières (D17) si l'enquête 2025 est publiée.

### A5. Innovation, infrastructures et capitaux pour l'avenir (dette, R&D, capital)
**Constat** : SSF (soutenabilité : stocks, à ne pas mêler au bien-être présent), OCDE (capital économique), INSEE NIR (effort de recherche, endettement), objectifs (3 % de R&D, 60 % de dette) ; prototypes : « Prospérité économique », « Innovation et infrastructure ». Aucun cadre ne retient le PIB par habitant. Indicateurs souvent de moyens ou de stocks (D19).

| Option | Conséquences |
|---|---|
| **A. Sous-thème « économie et ressources pour l'avenir » de la dimension 1** (« Niveau de vie et économie », comme v0, mais explicite) | Garde la limite de 10 sans sacrifier une autre dimension ; l'utilisateur choisit d'inclure ou non ces indicateurs ; mais une même dimension mêle niveau de vie présent et ressources futures (critique SSF/OCDE), et le poids de l'économie dans l'indice reste confondu avec celui du niveau de vie. |
| B. Dimension propre « Économie et avenir » | Satisfait ≥ 3 cadres (OCDE, SSF, INSEE) et ≥ 8 candidats ; rend visible la préférence des utilisateurs pour l'économie. Mais exige une fusion ailleurs : soit égalités transversale (A9-B), soit sécurité + démocratie (A10-B). |
| C. Hors indice : tableau de bord « ressources pour l'avenir » affiché à part | Conforme à SSF (rec. 11) ; mais incohérent avec la présence de la planète dans l'indice et avec D19 (l'effort de R&D y est cité comme candidat admis). |
| D. Dispersion (R&D en éducation, dette des ménages en sécurité, dette publique en démocratie…) | Aucune place perdue, mais lecture confuse pour le public. |

**Recommandation : A.** C'est la seule option qui respecte la limite sans retirer une dimension que les cadres valident ; elle suit l'INSEE (domaine « économique » des NIR) ; les indicateurs y portent `type: moyen` ou `stock` et leur entrée au socle se décidera au gel 2. **Infrastructures** : l'accès aux infrastructures (transports, numérique) relève du cadre de vie (R5) ; l'investissement relève de ce sous-thème. Si Léo veut une dimension « économie » visible, l'option B avec A9-B est la variante cohérente (voir « variante économie » ci-dessous).

### A6. Sécurité routière
**Constat** : OCDE 10_3 (sécurité), ODD 3.6 (santé), objectif UE −50 % de tués et blessés graves 2020–2030 ; M01 a tagué les séries en santé.

| Option | Conséquences |
|---|---|
| **A. Sécurité** | Précédent OCDE ; sens commun (« sécurité routière ») ; renforce une dimension peu fournie. |
| B. Santé | Précédent ONU (cause de mortalité) ; la santé est déjà bien fournie. |

**Recommandation : A.** Il s'agit d'un risque d'accident évitable, comme les atteintes aux personnes, plus que d'un état de santé.

### A7. Connectivité numérique
**Constat** : Doughnut (connectivité = transports publics et internet), OCDE (internet à domicile, dans le logement), Eurostat (compétences numériques en éducation), v0 (« numérique » en éducation).

| Option | Conséquences |
|---|---|
| A. Tout en éducation (v0) | Range l'équipement des ménages avec les diplômes. |
| B. Dimension propre « Connectivité » (Doughnut) | Infaisable dans la limite de 10, peu de séries distinctes. |
| **C. Répartition (R5)** | Accès et usage → cadre de vie (avec les transports : « accès aux services ») ; compétences et illectronisme → éducation. |

**Recommandation : C.**

### A8. Discriminations selon l'origine
**Constat** : Doughnut (inégalité raciale, aucune donnée mondiale), Eurostat (discriminations « à développer » ; écart d'emploi nationaux / pays tiers) ; statistique ethnique encadrée en France, mais l'origine migratoire (immigrés, descendants d'immigrés) est mesurée par l'INSEE.

| Option | Conséquences |
|---|---|
| **A. Égalités** (écarts selon l'origine migratoire et la nationalité ; discriminations ressenties en irrégulier, D17) | Cohérent avec R3 et avec le Doughnut ; les écarts d'emploi, de chômage et de pauvreté sont mesurables chaque année. |
| B. Démocratie (droits fondamentaux, comme Eurostat) | Ajouterait du contenu à une dimension peu fournie, mais les indicateurs disponibles sont des écarts de résultats, pas des mesures de droits. |

**Recommandation : A.** Les atteintes à caractère raciste enregistrées (SSMSI) restent en sécurité (R7), avec la même prudence d'interprétation que toute délinquance enregistrée.

### A9. Inégalités : dimension propre ou transversale
**Constat** : transversales dans SSF et l'OCDE ; dimension « Equality » dans le Doughnut ; réparties chez Eurostat ; un indicateur INSEE.

| Option | Conséquences |
|---|---|
| **A. Dimension propre** (v0) | L'utilisateur pondère directement l'égalité (information précieuse pour la finalité 2) ; ≥ 8 candidats annuels ; mais n'est une dimension nommée que dans un cadre, et exige la règle R3 pour rester distincte. |
| B. Transversale : chaque dimension porte ses indicateurs d'écart, et l'interface offre une « lentille équité » (un réglage qui renforce le poids de tous les indicateurs marqués `inegalite`) | Fidèle à SSF et à l'OCDE ; libère une place (pour A5-B ou A1-A). Mais beaucoup d'écarts ne sont pas annuels (gradient social de santé, écarts PISA), la lentille complique l'interface grand public, et la préférence pour l'égalité devient difficile à lire. |

**Recommandation : A.** Valeur forte et partagée dans le débat public français, l'égalité gagne à être un curseur explicite ; la faisabilité est bonne ; la règle R3 suffit à la distinguer.

### A10. Démocratie et sécurité peu fournies : fusion ou enrichissement
**Constat** : 17 lignes chacune dans le crosswalk (phase 1), `democratie` avec 9 séries « non » ; aucune borne chiffrée.

| Option | Conséquences |
|---|---|
| **A. Garder deux dimensions distinctes et les enrichir** : sécurité routière et sécurité économique en sécurité ; composites (D18), confiance institutionnelle et justice en démocratie | Deux préoccupations différentes pour le public (crime, libertés) restent pondérables séparément ; faisabilité obtenue (sécurité ≈ 13 stricts ; démocratie ≈ 16 avec composites). Dépendance aux composites. |
| B. Fusion « Sécurité, justice et institutions » (précédents : ODD 16, « Paix et justice » du Doughnut) | Dimension robuste et libère une place (pour A5-B). Mais mêle cambriolages et liberté de la presse : préférences illisibles ; contraire à SSF, OCDE et Eurostat qui les séparent. |

**Recommandation : A.** Pour le gel 2, prévoir la règle « une famille de composites = une variante principale » (par exemple V-Dem démocratie libérale principale, Freedom House en variante) pour limiter le double comptage (D18).

### A11. Confiance (autres point révélé par la phase 1)
**Constat** : v0 réunit confiance et sécurité ; Eurostat range la confiance interpersonnelle dans les interactions sociales, l'OCDE dans le capital social avec la confiance institutionnelle.
- Options : A. garder `securite_confiance` (v0) ; **B. partager : interpersonnelle → liens, institutionnelle → démocratie (R4)**.
- **Recommandation : B.** Le mot « confiance » couvre deux réalités différentes ; le partage renforce les deux dimensions les plus fragiles (liens, démocratie).

### A12. PIB par habitant
**Constat** : nommé dans le contenu de v0 ; retenu par **aucun** cadre comme indicateur de bien-être (SSF : préférer revenu et consommation des ménages).
- Options : A. indicateur de la dimension 1 ; B. absent ; **C. repère affiché à côté de l'indice (« ce que mesure le PIB »), et indicateur facultatif hors socle**.
- **Recommandation : C.** Pour un indicateur alternatif au PIB, montrer le PIB à côté de l'indice est pédagogique ; le laisser au choix de l'utilisateur respecte la philosophie de l'outil.

### A13. Culture et pratiques sportives
- Options : A. éducation (v0) ; **B. liens, au titre des loisirs (R11 ; Eurostat 5.1, SSF)**.
- **Recommandation : B.** Il s'agit d'usage du temps libre, pas de compétences ; séries surtout irrégulières (D17).

### A14. Adaptation au changement climatique
**Constat** : OCDE 9_3 (exposition aux températures extrêmes), jours de canicule (Santé publique France), catastrophes naturelles (tableau ODD).
- Options : A. planète ; **B. cadre de vie (R2)**.
- **Recommandation : B.** Ce sont des conditions subies par les habitants (plancher) ; la planète mesure les pressions exercées (plafond).

### A15. Sécurité de l'emploi
- Options : A. sécurité (Eurostat : transitions emploi → chômage en sécurité économique) ; **B. travail (OCDE : insécurité du marché du travail en qualité de l'emploi)**.
- **Recommandation : B.** La sécurité économique de la dimension 7 se limite aux réserves et difficultés financières des ménages (R7), ce qui évite deux dimensions concurrentes sur le chômage.

### A16. Stabilité financière (OCDE 15_8, levier des institutions financières)
- **Recommandation : non retenue** (hors bien-être, aucun autre cadre ; illisible pour le public). Seule ligne du crosswalk classée « hors grille ».

### Variantes de grille écartées (pour mémoire)
- **Variante « cadres OCDE et Eurostat »** : bien-être ressenti en dimension propre (A1-A), liens sociaux et temps libre à part, égalités transversales (A9-B). **Écartée** : deux dimensions sous 8 candidats stricts (≈ 5 et ≈ 4).
- **Variante « économie »** : dimension propre « Économie et avenir » (A5-B), égalités transversales avec lentille équité (A9-B), dimension 1 réduite à « Revenus et conditions de vie ». **Faisable** (≥ 3 cadres, ≥ 8 candidats) ; non recommandée pour les raisons données en A9, mais c'est l'alternative cohérente si Léo souhaite une dimension économique visible.

---

## 6. Changements par rapport à v0

### 6.1 Fusions, scissions, renommages
**Aucune fusion ni scission de dimension entière ; aucune création.** Changements :

| Dimension v0 | Dimension v1 | Nature du changement | Justification |
|---|---|---|---|
| `niveau_de_vie` | `niveau_de_vie` (Niveau de vie et économie) | reçoit l'accès à l'alimentation ; sous-thème économie explicite ; PIB par habitant en repère | R9, A5, A12 |
| `travail` | `travail` | reçoit la sécurité de l'emploi | R7, A15 |
| `logement_cadre_vie` | `logement_cadre_vie` | reçoit l'accès au numérique (d'éducation), l'exposition aux pollutions locales, à l'eau non conforme et aux aléas (de planète) | R2, R5, A7, A14 |
| `sante` | `sante` | cède la sous-alimentation (→ niveau de vie) et les tués sur la route (→ sécurité) | R9, A6 |
| `education` | `education` (Éducation et compétences) | cède la culture (→ liens) et l'accès à internet (→ cadre de vie) ; libellé raccourci | R5, R11 |
| `liens_bien_etre` | `liens_bien_etre` (Liens sociaux et bien-être ressenti) | reçoit la confiance interpersonnelle, la culture et le sport ; garde la satisfaction dans la vie | R4, R11, A1 |
| `securite_confiance` | **`securite`** (Sécurité) | **scission de la confiance** (interpersonnelle → liens ; institutionnelle → démocratie) ; reçoit la sécurité routière ; cède la sécurité de l'emploi ; **identifiant renommé** | R4, R7, A6, A11 |
| `democratie` | `democratie` (Démocratie et institutions) | reçoit la confiance institutionnelle ; cède la parité politique (→ égalités) | R3, R4 |
| `egalites` | `egalites` | nomme les discriminations selon l'origine et la parité politique | R3, A8 |
| `planete` | `planete` | nomme l'énergie (consommation, mix) ; cède les conditions subies au cadre de vie | R2, R10 |

### 6.2 Lignes du crosswalk qui changent de dimension
Onze lignes : sous-alimentation (Doughnut) et cible ODD 2.1 → niveau de vie ; absence d'internet (Doughnut) → cadre de vie ; participation culturelle (SSF) et non-participation culturelle ou sportive (Eurostat) → liens ; confiance dans les autres (OCDE 14_1, Eurostat) → liens ; transitions emploi → chômage (Eurostat) → travail ; tableau des stocks de capitaux (SSF) → niveau de vie ; production domestique (SSF) → liens ; levier des institutions financières (OCDE 15_8) → hors grille. La colonne `dimension_v0_proposee` du CSV n'est pas modifiée : la correspondance s'applique par `31_correspondance_v0_v1.csv`.

---

## 7. Limites et points à vérifier
1. **Comptages indicatifs** : le catalogue Eurostat (M02 phase 2) et les catalogues M04 phase 2 ne sont pas encore disponibles ; les estimations seront recalculées sur la long-list (gel 2). Le comptage strict INSEE sous-estime le travail et surestime les concepts (doublons).
2. **Séries Gallup relayées par l'OCDE** (soutien social, affects, sécurité la nuit, confiance dans le gouvernement, bénévolat) : l'origine Gallup est à confirmer (M04) et les conditions de réutilisation de l'OCDE à vérifier ; la faisabilité de la dimension 6 en dépend.
3. **Dimension 6** : rechercher en priorité des séries publiques annuelles (baromètre d'opinion de la DREES 2000–2024 ; modules SRCV ; INJEP ; enquête de conjoncture auprès des ménages).
4. **Dimension 8** : dépendance aux composites (D18) ; ruptures RSF 2013 et 2022 ; Freedom House 2025-2026 sur demande.
5. **Délinquance enregistrée** : sens d'interprétation ambigu ; rupture d'enquête de victimation en 2022.
6. **Arbitrage A5** : si la variante « économie » est retenue, la correspondance de la règle 18 de `31_correspondance_v0_v1.csv` change (sous-thème économie → nouvelle dimension) et `egalites` devient une lentille.
7. **Statut des objectifs** (ZAN, L100-4) : voir la question ouverte Q-F, sans effet sur la grille.
