# Dossier de décision — gel 1 des dimensions (grille v1)

Préparé par l'agent M03 (phase 2) pour la session mère et Léo Malherbe — 13 octobre 2026.
Procédure : charte §3.6, gel 1 (décision D20). **Validation par exception** : chaque page porte une recommandation ; Léo ne répond que là où il diverge ou hésite, et la recommandation est suivie ailleurs. La décision est ensuite consignée au journal et `indicateurs/dimensions.yaml` passe en v1 (`statut: figee`).

Argumentaire complet : `30_grille_dimensions_v1_proposition.md`. Table de correspondance pour le script de long-list : annexe en fin de dossier et `31_correspondance_v0_v1.csv`.

**Comment répondre** : sur chaque page, remplir la ligne « Décision » (valider / modifier, en précisant / refuser) ; pour les arbitrages, « suivre la recommandation » ou l'option choisie.

---

## Résumé

**La grille v1 garde les dix domaines de v0 et en redessine les frontières.** Les six cadres de référence valident les dix domaines (341 indicateurs de cadre sur 344 s'y rattachent) ; aucune onzième dimension n'est à la fois justifiée et faisable. Aucune fusion, aucune création ; un identifiant renommé.

| # | id | Libellé | Type | Cadres (sur 6) | Candidats France (stricts / élargis) | Critères du gel 1 | Recommandation |
|---|---|---|---|---|---|---|---|
| 1 | `niveau_de_vie` | Niveau de vie et économie | plancher | 6 | ≈ 25 / ≈ 30 | remplis | valider |
| 2 | `travail` | Travail et emploi | plancher | 6 | ≈ 18 / ≈ 22 | remplis | valider |
| 3 | `logement_cadre_vie` | Logement et cadre de vie | plancher | 5 | ≈ 14 / ≈ 18 | remplis | valider |
| 4 | `sante` | Santé | plancher | 6 | ≈ 13 / ≈ 18 | remplis | valider |
| 5 | `education` | Éducation et compétences | plancher | 6 | ≈ 8 / ≈ 15 | remplis (faisabilité juste) | valider |
| 6 | `liens_bien_etre` | Liens sociaux et bien-être ressenti | plancher | 5 | ≈ 6 / ≈ 13 | faisabilité sous condition | valider sous condition |
| 7 | `securite` | Sécurité | plancher | 5 | ≈ 13 / ≈ 16 | remplis | valider |
| 8 | `democratie` | Démocratie et institutions | plancher | 4 | ≈ 3 hors composites / ≈ 16 | faisabilité sous condition | valider sous condition |
| 9 | `egalites` | Égalités | plancher | 6 (contenu) | ≈ 16 / ≈ 20 | remplis (dimension justifiée par la finalité) | valider |
| 10 | `planete` | Planète | plafond | 5 | ≥ 40 / ≥ 50 | remplis | valider |

« Stricts » : concepts distincts avec une série France annuelle, ≥ 10 points depuis 2000, dernière valeur ≥ 2020 (charte §3.4). « Élargis » : avec les dérogations actées (D16 raccordement, D17 irréguliers, D18 composites, D19 moyens). Estimations indicatives, établies sur le crosswalk, le repérage INSEE (1 063 séries) et les sources M04 ; elles seront recalculées sur la long-list du gel 2.

**Changements par rapport à v0**
- `securite_confiance` devient **`securite`** : la confiance envers les autres passe en liens, la confiance dans les institutions en démocratie ; la sécurité routière arrive ; la sécurité de l'emploi part en travail.
- **Cadre de vie** reçoit l'accès au numérique (d'éducation) et les conditions subies venant de planète (pollution locale, eau du robinet, canicules et inondations).
- **Niveau de vie** reçoit l'accès à l'alimentation (de santé) ; le sous-thème « économie et ressources pour l'avenir » est rendu explicite ; le PIB par habitant devient un repère affiché hors indice.
- **Éducation** cède la culture (→ liens) ; **santé** cède la sous-alimentation et les tués sur la route.
- **Planète** nomme l'énergie (consommation et mix) ; **égalités** nomme les discriminations selon l'origine et la parité politique.

**Arbitrages** (options détaillées dans les pages indiquées)

| N° | Question | Recommandation | Page |
|---|---|---|---|
| A1 | Satisfaction globale dans la vie : dimension propre, transversale ou indicateur ? | Indicateur de la dimension 6, **et** affichée à côté de l'indice comme repère | 6 |
| A2 | Alimentation | Répartie : accès → niveau de vie ; nutrition → santé ; agriculture → planète | 1 |
| A3 | Énergie | Répartie : précarité → logement ; consommation et mix → planète | 3, 10 |
| A4 | Temps et travail non rémunéré | Réparti : travail rémunéré → travail ; temps libre → liens ; répartition femmes-hommes → égalités | 6 |
| A5 | Innovation, infrastructures, capitaux pour l'avenir | Sous-thème « économie et ressources pour l'avenir » de la dimension 1 | 1 |
| A6 | Sécurité routière | Sécurité | 7 |
| A7 | Connectivité numérique | Accès → cadre de vie ; compétences → éducation | 3, 5 |
| A8 | Discriminations selon l'origine | Égalités | 9 |
| A9 | Inégalités : dimension propre ou transversale ? | Dimension propre | 9 |
| A10 | Démocratie et sécurité peu fournies : fusion ? | Non : garder distinctes et enrichir | 7, 8 |
| A11 | Confiance | Interpersonnelle → liens ; institutionnelle → démocratie | 6, 8 |
| A12 | PIB par habitant | Repère affiché hors indice ; indicateur facultatif hors socle | 1 |
| A13 | Culture et sport | Liens (loisirs) | 5, 6 |
| A14 | Adaptation au changement climatique | Cadre de vie | 3 |
| A15 | Sécurité de l'emploi | Travail | 2 |
| A16 | Stabilité financière | Non retenue | 1 |

**Variante possible** (non recommandée, mais cohérente) : si Léo veut une dimension « Économie et avenir » visible, la seule variante faisable est de la créer en rendant les égalités transversales (une « lentille équité » dans l'interface) : voir pages 1 et 9.

---

## Page 1 — `niveau_de_vie` · Niveau de vie et économie

**En une phrase** : les ressources matérielles dont disposent les ménages (revenus, consommation, patrimoine), la pauvreté et les privations, et les ressources économiques du pays pour l'avenir.

| Type | Plancher (on vise au-dessus d'un minimum) |
|---|---|
| Question posée à l'utilisateur | « Que doit refléter le niveau de vie ? Est-ce que les gens ont de quoi vivre correctement, combien vivent dans la pauvreté, et l'économie du pays est-elle solide pour la suite ? » |

**Contenu** : revenus et consommation ; pauvreté et privations, dont l'accès à l'alimentation ; patrimoine des ménages ; économie et ressources pour l'avenir (dette publique et privée, effort de recherche, investissement, patrimoine national — indicateurs de moyens ou de stocks, D19).

**Par rapport à v0** : même dimension ; reçoit l'accès à l'alimentation ; sous-thème économique explicite ; le PIB par habitant sort du contenu (repère hors indice).

**Cadres qui la retiennent : 6 sur 6** — Doughnut (pauvreté sociétale, alimentation), Stiglitz-Sen-Fitoussi (niveau de vie matériel ; stocks pour la soutenabilité), OCDE (revenu et patrimoine ; capital économique), Eurostat (conditions de vie matérielles), INSEE (privation matérielle et sociale ; effort de recherche ; endettement), ODD et objectifs (pauvreté ÷ 2, AROPE, 3 % de R&D, 60 % de dette).

**Indicateurs incontournables** (≥ 3 cadres de bien-être) : taux de pauvreté monétaire ; revenu disponible des ménages ; privation matérielle.

**Candidats France : ≈ 25 stricts, ≈ 30 élargis.** Crosswalk : 42 lignes (35 disponibles). INSEE : 61 séries, dont 33 conformes à la charte. Autres : OCDE (difficulté à joindre les deux bouts, 2004–2025), DREES, BCE (dette des ménages depuis 1999). Exemples : niveau de vie médian (1996–2023) ; pouvoir d'achat par unité de consommation ; consommation des ménages ; taux de pauvreté à 60 % et à 50 % ; intensité de la pauvreté ; privation matérielle et sociale (2013–2024) ; renoncement à des repas protéinés faute d'argent ; difficulté à joindre les deux bouts ; patrimoine des ménages ; effort de recherche (1996–2024) ; dette publique ; dette des ménages.

**Critères du gel 1**

| Critère | Verdict |
|---|---|
| ≥ 3 cadres ou finalité | oui (6 cadres) |
| Distincte | oui : écarts de revenus en égalités, réserves financières en sécurité, nutrition en santé (règles R3, R7, R9) |
| Faisable (≥ 8 candidats) | oui |
| Intelligible | oui |

**Arbitrages touchant cette page**
- **A5 — Innovation et capitaux pour l'avenir.** (A) sous-thème de cette dimension ; (B) dimension propre « Économie et avenir », possible seulement si une autre dimension disparaît (égalités transversales) ; (C) tableau de bord hors indice ; (D) dispersion dans plusieurs dimensions. **Recommandé : A** (limite de 10 respectée, comme le domaine « économique » des indicateurs INSEE ; entrée au socle décidée au gel 2). Infrastructures : l'accès (transports, numérique) va en cadre de vie, l'investissement ici.
- **A12 — PIB par habitant** : (A) indicateur ; (B) absent ; (C) repère affiché à côté de l'indice et indicateur facultatif hors socle. **Recommandé : C** (aucun cadre ne le retient comme mesure du bien-être ; le montrer à côté d'un indicateur alternatif au PIB est pédagogique).
- **A2 — Alimentation** : (A) tout en santé ; (B) tout ici ; (C) dimension propre (infaisable) ; (D) répartition. **Recommandé : D** — accès (insécurité alimentaire, privation) ici ; nutrition en santé ; agriculture en planète.
- **A16 — Stabilité financière** (levier bancaire, OCDE) : **non retenue**.

**Recommandation** : valider.

**Décision attendue : valider / modifier (préciser) / refuser**
Décision de Léo : …  Arbitrages A2, A5, A12, A16 : suivre la recommandation / autre option : …

---

## Page 2 — `travail` · Travail et emploi

**En une phrase** : l'accès à l'emploi et la qualité des emplois : stabilité, rémunération, conditions et santé au travail, temps de travail, satisfaction.

| Type | Plancher |
|---|---|
| Question posée à l'utilisateur | « Que doit refléter le travail ? Est-ce que ceux qui veulent travailler trouvent un emploi, et est-ce que ces emplois sont de bonne qualité ? » |

**Contenu** : emploi, chômage, chômage de longue durée, sous-emploi, jeunes ni en emploi ni en formation (NEET) ; qualité et sécurité de l'emploi (contrats courts et temps partiel subis, bas salaires, surqualification, passages de l'emploi au chômage) ; conditions et santé au travail (accidents, expositions) ; temps de travail rémunéré (longues durées, horaires atypiques) ; satisfaction au travail.

**Par rapport à v0** : inchangée ; y sont rangés explicitement la sécurité de l'emploi et le temps de travail rémunéré.

**Cadres qui la retiennent : 6 sur 6** — Doughnut (NEET), Stiglitz-Sen-Fitoussi (activités personnelles dont le travail), OCDE (travail et qualité de l'emploi), Eurostat (activité productive), INSEE (taux d'emploi), objectifs (taux d'emploi de 78 % en 2030 ; NEET < 9 %).

**Indicateurs incontournables** : taux d'emploi ; longues durées de travail. Présents dans deux cadres : NEET, chômage de longue durée, accidents du travail, satisfaction au travail, bas salaires.

**Candidats France : ≈ 18 stricts, ≈ 22 élargis.** Crosswalk : 42 lignes (28 disponibles). INSEE : 59 séries (enquête Emploi). Autres : Eurostat (enquête sur les forces de travail), Assurance maladie (accidents du travail depuis 2005), OCDE. Exemples : taux d'emploi 15-64 ans (depuis 1975) et 20-64 ans ; taux de chômage ; chômage de longue durée ; sous-emploi ; halo du chômage ; NEET ; temps partiel subi ; contrats temporaires subis ; surqualification ; accidents du travail ; longues durées de travail ; horaires atypiques.

**Critères du gel 1**

| Critère | Verdict |
|---|---|
| ≥ 3 cadres ou finalité | oui (6) |
| Distincte | oui (réserves financières des ménages en sécurité, écarts femmes-hommes en égalités) |
| Faisable | oui |
| Intelligible | oui |

**Arbitrages touchant cette page**
- **A15 — Sécurité de l'emploi** : (A) en sécurité, comme Eurostat ; (B) ici, comme l'OCDE. **Recommandé : B** (évite deux dimensions concurrentes sur le chômage).
- **A4 — Temps** : le temps de travail rémunéré est ici (voir page 6).

**Recommandation** : valider.

**Décision attendue : valider / modifier (préciser) / refuser**
Décision de Léo : …  Arbitrage A15 : suivre la recommandation / autre option : …

---

## Page 3 — `logement_cadre_vie` · Logement et cadre de vie

**En une phrase** : les conditions de logement (coût, qualité, espace, chauffage) et l'environnement de vie quotidien (air, bruit, eau du robinet, nature, exposition aux canicules et inondations, accès aux transports et au numérique).

| Type | Plancher |
|---|---|
| Question posée à l'utilisateur | « Que doit refléter le logement et le cadre de vie ? Est-ce que chacun peut se loger correctement à un coût supportable, dans un environnement sain et bien desservi ? » |

**Contenu** : coût du logement ; qualité et surpeuplement ; précarité énergétique ; sans-abrisme ; environnement local (air, bruit, eau du robinet, espaces verts) ; exposition aux aléas climatiques ; accès aux services, aux transports et au numérique.

**Par rapport à v0** : même dimension ; reçoit l'accès au numérique (d'éducation) et les conditions subies auparavant comptées en planète (pollution locale, eau non conforme, aléas).

**Cadres qui la retiennent : 5 sur 6** — Doughnut (logement ; eau ; énergie ; connectivité), Stiglitz-Sen-Fitoussi (logement ; environnement présent), OCDE (logement ; qualité de l'environnement), Eurostat (conditions matérielles ; environnement naturel et cadre de vie), ODD et objectifs (eau, assainissement, énergie, PM2,5, passoires thermiques). INSEE : aucun.

**Indicateurs incontournables** : surpeuplement et qualité du logement ; pollution de l'air locale.

**Candidats France : ≈ 14 stricts, ≈ 18 élargis.** Crosswalk : 38 lignes (26 disponibles). INSEE : 30 séries, dont 25 conformes. Autres : SDES (exposition aux PM2,5), Santé publique France (jours de canicule 2004–2025), Baromètre du numérique (2007–2025), BCE (prix des logements). Exemples : surpeuplement ; surcharge des coûts du logement ; logement humide ou dégradé ; incapacité à chauffer son logement (2010–2024) ; exposition aux particules fines ; concentrations de PM10 (2010–2024) ; dépassements des normes de qualité de l'air ; jours de canicule ; haut débit à domicile (2010–2025) ; usage d'internet ; part des transports collectifs (2010–2024) ; bruit ressenti.

**Critères du gel 1**

| Critère | Verdict |
|---|---|
| ≥ 3 cadres ou finalité | oui (5) |
| Distincte | oui : conditions **subies** ici, pressions **exercées** en planète (R2) ; compétences numériques en éducation (R5) |
| Faisable | oui |
| Intelligible | oui |

**Arbitrages touchant cette page**
- **A3 — Énergie** : (A) tout ici ; (B) tout en planète ; (C) dimension propre « transition énergétique » ; (D) répartition. **Recommandé : D** — précarité énergétique ici ; consommation, fossiles, renouvelables en planète.
- **A7 — Numérique** : (A) tout en éducation (v0) ; (B) dimension « connectivité » (infaisable) ; (C) répartition. **Recommandé : C** — accès et usage ici ; compétences en éducation.
- **A14 — Adaptation au changement climatique** (canicules, inondations) : (A) planète ; (B) ici. **Recommandé : B** (conditions subies par les habitants).

**Recommandation** : valider.

**Décision attendue : valider / modifier (préciser) / refuser**
Décision de Léo : …  Arbitrages A3, A7, A14 : suivre la recommandation / autre option : …

---

## Page 4 — `sante` · Santé

**En une phrase** : l'état de santé de la population — durée de vie, vie en bonne santé, santé physique et mentale — et l'accès aux soins.

| Type | Plancher |
|---|---|
| Question posée à l'utilisateur | « Que doit refléter la santé ? Est-ce qu'on vit longtemps et en bonne santé, physique et mentale, et est-ce que chacun peut se soigner ? » |

**Contenu** : espérance de vie et mortalité (infantile, prématurée, évitable) ; espérance de vie sans incapacité ; santé perçue et maladies chroniques ; santé mentale (dépression, suicide) ; accès aux soins ; comportements (tabac, alcool, corpulence, activité physique).

**Par rapport à v0** : même dimension ; cède la sous-alimentation (→ niveau de vie) et les tués sur la route (→ sécurité).

**Cadres qui la retiennent : 6 sur 6** — Doughnut, Stiglitz-Sen-Fitoussi, OCDE, Eurostat, INSEE (espérance de vie sans incapacité), ODD (mortalité maternelle, infantile, prématurée).

**Indicateurs incontournables** : espérance de vie ; santé perçue et maladies chroniques ; santé mentale.

**Candidats France : ≈ 13 stricts, ≈ 18 élargis.** Crosswalk : 30 lignes (20 disponibles). INSEE : 63 séries, dont 17 conformes. Autres : Santé publique France (suicides, tabac), DREES (accessibilité aux médecins), OCDE (décès par suicide, alcool et drogues, 2004–2023). Exemples : espérance de vie à la naissance ; espérance de vie sans incapacité ; mortalité infantile ; mortalité prématurée ; suicides ; santé perçue ; maladies chroniques et limitations ; renoncement aux soins pour raisons financières ; besoins de soins non satisfaits ; tabagisme quotidien ; consommation d'alcool ; décès par suicide, alcool et drogues.

**Critères du gel 1**

| Critère | Verdict |
|---|---|
| ≥ 3 cadres ou finalité | oui (6) |
| Distincte | oui (accidents de la route en sécurité ; privation alimentaire en niveau de vie) |
| Faisable | oui |
| Intelligible | oui |

**Arbitrages touchant cette page** : A6 (sécurité routière : voir page 7) ; A2 (alimentation : la nutrition et la corpulence restent ici).

**Recommandation** : valider.

**Décision attendue : valider / modifier (préciser) / refuser**
Décision de Léo : …

---

## Page 5 — `education` · Éducation et compétences

**En une phrase** : le niveau d'éducation atteint et les compétences des jeunes et des adultes, y compris numériques, et l'accès à la formation tout au long de la vie.

| Type | Plancher |
|---|---|
| Question posée à l'utilisateur | « Que doit refléter l'éducation ? Est-ce que les jeunes sortent de l'école avec un diplôme et des compétences solides, et est-ce que les adultes continuent d'apprendre ? » |

**Contenu** : diplômes et sorties précoces ; compétences des élèves ; compétences des adultes ; compétences numériques et illectronisme ; formation des adultes ; accueil de la petite enfance.

**Par rapport à v0** : la culture passe en liens (loisirs) ; l'accès à internet passe en cadre de vie ; libellé raccourci (« Éducation, compétences et culture » → « Éducation et compétences »).

**Cadres qui la retiennent : 6 sur 6** — Doughnut, Stiglitz-Sen-Fitoussi, OCDE (connaissances et compétences ; capital humain), Eurostat, INSEE (sorties précoces), objectifs UE et France (sorties précoces < 9 %, diplômés du supérieur ≥ 45 %, formation des adultes 65 %, compétences numériques 80 %).

**Indicateurs incontournables** : diplôme du secondaire et sorties précoces ; compétences mesurées par des tests.

**Candidats France : ≈ 8 stricts, ≈ 15 élargis.** Crosswalk : 33 lignes (15 disponibles, 9 non : enquêtes non annuelles). INSEE : 10 séries, dont 9 conformes. Autres : DEPP (réussite au baccalauréat selon l'origine sociale depuis 1998), tests de lecture de la journée défense et citoyenneté, OCDE (PISA, PIAAC). Exemples : sorties précoces (depuis 2003) ; diplômés du supérieur parmi les 25-34 ans ; jeunes adultes diplômés du lycée ; formation des adultes ; compétences numériques de base ; faibles compétences numériques ; illectronisme ; jeunes en difficulté de lecture. Élargis (indicateurs irréguliers, D17) : PISA lecture, mathématiques, sciences et élèves en difficulté (8 vagues depuis 2000), PIAAC (2 vagues).

**Critères du gel 1**

| Critère | Verdict |
|---|---|
| ≥ 3 cadres ou finalité | oui (6) |
| Distincte | oui (accès au numérique en cadre de vie ; écarts selon l'origine sociale en égalités) |
| Faisable | oui, **de justesse** au sens strict ; confortable avec PISA et PIAAC (D17) |
| Intelligible | oui |

**Arbitrages touchant cette page** : A7 (numérique : les compétences restent ici) ; A13 (culture et sport : (A) ici comme v0 ; (B) en liens, au titre des loisirs — **recommandé : B**, ce sont des usages du temps libre).

**Recommandation** : valider.

**Décision attendue : valider / modifier (préciser) / refuser**
Décision de Léo : …  Arbitrage A13 : suivre la recommandation / autre option : …

---

## Page 6 — `liens_bien_etre` · Liens sociaux et bien-être ressenti

**En une phrase** : la qualité des relations (soutien, solitude, confiance envers les autres, engagement), le temps libre et les loisirs, et la manière dont chacun évalue et ressent sa vie.

| Type | Plancher |
|---|---|
| Question posée à l'utilisateur | « Que doit refléter cette dimension ? Est-ce que les gens peuvent compter sur d'autres, ont du temps pour eux et des loisirs, et se sentent bien dans leur vie ? » |

**Contenu** : relations et soutien ; solitude ; confiance envers les autres ; bénévolat et vie associative ; temps libre, loisirs, pratiques culturelles et sportives, vacances ; satisfaction dans la vie, émotions ressenties, sentiment que sa vie a un sens.

**Par rapport à v0** : même dimension ; reçoit la confiance envers les autres (de `securite_confiance`) et la culture et le sport (d'éducation).

**Cadres qui la retiennent : 5 sur 6** — Doughnut (cohésion sociale : soutien social), Stiglitz-Sen-Fitoussi (liens sociaux ; bien-être subjectif), OCDE (liens sociaux ; bien-être subjectif ; équilibre des temps), Eurostat (loisirs et interactions sociales ; expérience globale de la vie), INSEE (satisfaction dans la vie). Aucun objectif chiffré.

**Indicateurs incontournables** : satisfaction dans la vie ; soutien social (avoir quelqu'un sur qui compter) ; temps libre.

**Candidats France : ≈ 6 stricts, ≈ 13 élargis.** Crosswalk : 39 lignes, dont 22 déclaratives (10 disponibles, 17 probables, 12 non). INSEE : 6 séries (satisfaction dans la vie depuis 2010). Autres : OCDE (soutien social 2006–2025, émotions négatives 2006–2025, bénévolat 2007–2025, séries d'origine Gallup à confirmer), World Happiness Report (2011–2025), Eurostat (satisfaction et confiance, annuelles depuis peu), baromètre d'opinion de la DREES (2000–2024, à exploiter). Stricts : satisfaction dans la vie (INSEE) ; évaluation de la vie (World Happiness Report) ; soutien social ; émotions négatives ; bénévolat ; impossibilité de partir une semaine en vacances (à vérifier). Élargis : confiance envers les autres (7 points), solitude, satisfaction des relations et du temps libre, sens de la vie, pratiques sportives.

**Critères du gel 1**

| Critère | Verdict |
|---|---|
| ≥ 3 cadres ou finalité | oui (5) |
| Distincte | oui : une satisfaction **de domaine** (travail, logement, santé) va dans son domaine ; l'évaluation **globale** de la vie vient ici (règle R6) |
| Faisable | **sous condition** : 8 candidats seulement en admettant les séries courtes ou irrégulières (D17) et les séries Gallup relayées par l'OCDE |
| Intelligible | oui (libellé double assumé) |

**Arbitrages touchant cette page**
- **A1 — Satisfaction globale dans la vie.** (A) dimension propre « bien-être ressenti » : lisible, mais ≈ 5 candidats stricts, et les « liens sociaux » restants tomberaient à ≈ 4 ; exige de supprimer une autre dimension ; double comptage. (B) transversale, hors indice, affichée comme repère : conforme à Stiglitz-Sen-Fitoussi, mais l'utilisateur ne peut plus la pondérer et cette page perd son meilleur indicateur. (C) indicateur de cette dimension (v0) : faisable, l'utilisateur garde la main, comme l'INSEE. **Recommandé : C, et affichage de la satisfaction à côté de l'indice comme repère (B) sans la compter deux fois.**
- **A4 — Temps et travail non rémunéré.** (A) dimension propre « temps » : infaisable (enquêtes emploi du temps 1999, 2010, 2025) ; (B) répartition. **Recommandé : B** — temps libre et volume de travail domestique ici ; temps de travail rémunéré en travail ; répartition femmes-hommes en égalités.
- **A11 — Confiance** : (A) garder « sécurité et confiance » (v0) ; (B) confiance envers les autres ici, confiance dans les institutions en démocratie. **Recommandé : B.**
- **A13 — Culture et sport** : ici (voir page 5).

**Recommandation** : valider, **sous condition** : demander aux missions de phase 2 (M01, M04) de rechercher en priorité des séries publiques annuelles pour cette dimension (baromètre DREES, modules SRCV, INJEP, enquête de conjoncture auprès des ménages) et de confirmer l'origine et les conditions de réutilisation des séries OCDE d'origine Gallup.

**Décision attendue : valider / modifier (préciser) / refuser**
Décision de Léo : …  Arbitrages A1, A4, A11 : suivre la recommandation / autre option : …

---

## Page 7 — `securite` · Sécurité (ex-`securite_confiance`)

**En une phrase** : être protégé des atteintes aux personnes et aux biens, des accidents de la route et des coups durs financiers, et se sentir en sécurité.

| Type | Plancher |
|---|---|
| Question posée à l'utilisateur | « Que doit refléter la sécurité ? Est-ce qu'on est à l'abri des violences, des vols et des accidents, est-ce qu'on peut faire face à un coup dur financier, et est-ce qu'on se sent en sécurité ? » |

**Contenu** : atteintes aux personnes (homicides, violences physiques, sexuelles, intrafamiliales) ; atteintes aux biens (cambriolages, vols) ; sentiment d'insécurité ; sécurité routière ; sécurité économique des ménages (faire face à une dépense imprévue, retards de paiement, surendettement, épargne de précaution).

**Par rapport à v0** : la confiance en sort (vers liens et démocratie) ; la sécurité routière y entre ; la sécurité de l'emploi part en travail ; **identifiant renommé `securite`**.

**Cadres qui la retiennent : 5 sur 6** — Doughnut (paix et justice : homicides), Stiglitz-Sen-Fitoussi (insécurité physique et économique), OCDE (sécurité ; insécurité financière), Eurostat (sécurité économique et physique), ODD et objectifs (décès routiers ÷ 2). INSEE : aucun.

**Indicateurs incontournables** : homicides ; sécurité économique (dépense imprévue, épargne) ; sentiment d'insécurité.

**Candidats France : ≈ 13 stricts, ≈ 16 élargis.** Crosswalk : 14 lignes (11 disponibles). INSEE : 22 séries, dont 12 conformes. Autres : SSMSI (159 séries 2006–2023, dont le sentiment d'insécurité), ONISR (accidents 2005–2024), OCDE (homicides, sécurité la nuit 2006–2025, décès routiers), Banque de France (surendettement). Exemples : homicides ; violences physiques et sexuelles enregistrées ; cambriolages ; victimes de violences (enquête) ; sentiment d'insécurité dans le quartier ; se sentir en sécurité la nuit ; tués sur la route ; incapacité à faire face à une dépense imprévue ; retards de paiement ; surendettement (2010–2024) ; criminalité perçue dans le quartier.

**Critères du gel 1**

| Critère | Verdict |
|---|---|
| ≥ 3 cadres ou finalité | oui (5) |
| Distincte | oui : état de santé en santé ; sécurité de l'emploi en travail ; confiance ailleurs (R4, R7) |
| Faisable | oui |
| Intelligible | oui |

Point d'attention pour le gel 2 : la délinquance **enregistrée** monte aussi quand les victimes portent plainte davantage (violences intrafamiliales) — sens à documenter ; rupture de l'enquête de victimation en 2022.

**Arbitrages touchant cette page**
- **A6 — Sécurité routière** : (A) ici, comme l'OCDE ; (B) santé, comme l'ONU. **Recommandé : A.**
- **A10 — Fusion avec démocratie ?** (A) garder deux dimensions et les enrichir ; (B) fusion « Sécurité, justice et institutions » (précédents : ODD 16, Doughnut). **Recommandé : A** (crime et libertés sont deux préoccupations que l'utilisateur doit pouvoir pondérer séparément ; SSF, OCDE et Eurostat les séparent).

**Recommandation** : valider.

**Décision attendue : valider / modifier (préciser) / refuser**
Décision de Léo : …  Arbitrages A6, A10 : suivre la recommandation / autre option : …

---

## Page 8 — `democratie` · Démocratie et institutions

**En une phrase** : la qualité de la vie démocratique : participation des citoyens, libertés publiques, État de droit et justice, intégrité des institutions et confiance qu'elles inspirent.

| Type | Plancher |
|---|---|
| Question posée à l'utilisateur | « Que doit refléter la démocratie ? Est-ce que les citoyens participent et sont entendus, est-ce que les libertés sont respectées et est-ce qu'on peut faire confiance aux institutions ? » |

**Contenu** : participation électorale, sentiment d'avoir son mot à dire ; libertés d'expression, de la presse, académique ; État de droit et justice ; corruption ; confiance dans les institutions ; qualité de l'action publique.

**Par rapport à v0** : même dimension ; la confiance dans les institutions y est regroupée ; la parité politique part en égalités.

**Cadres qui la retiennent : 4 sur 6** — Doughnut (voix politique ; corruption), Stiglitz-Sen-Fitoussi (voix politique et gouvernance), OCDE (engagement civique ; capital social), Eurostat (gouvernance et droits fondamentaux). Ni INSEE, ni objectif chiffré.

**Indicateurs incontournables** : participation et voix politique. Présents dans deux cadres : corruption, confiance dans les institutions.

**Candidats France : ≈ 3 stricts hors indices composites ; ≈ 16 avec les composites (D18) et la participation électorale (D17).** Crosswalk : 17 lignes (5 disponibles, 9 non). INSEE : 21 séries (confiance dans la justice, la police, l'école, l'hôpital et l'armée 2013–2024 ; participation ; détention provisoire). Autres (M04) : V-Dem (démocratie libérale, liberté d'expression, contraintes judiciaires, liberté académique, 2000–2025), Freedom House (2002–2025), RSF (2002–2026, ruptures de méthode), indice de perception de la corruption (2012–2025), indicateurs de gouvernance de la Banque mondiale (1996–2025), confiance dans le gouvernement (OCDE 2006–2025), participation électorale (1999–2026).

**Critères du gel 1**

| Critère | Verdict |
|---|---|
| ≥ 3 cadres ou finalité | oui (4) |
| Distincte | oui (confiance envers les autres en liens ; parité en égalités) |
| Faisable | **sous condition** : dépend des indices composites admis par D18 |
| Intelligible | oui |

**Arbitrages touchant cette page**
- **A10 — Fusion avec sécurité ?** **Recommandé : non** (voir page 7). Pour le gel 2 : règle « une famille de composites = une variante principale » (par exemple V-Dem principal, Freedom House en variante) pour limiter le double comptage.
- **A11 — Confiance** : la confiance dans les institutions vient ici (voir page 6).

**Recommandation** : valider, **sous condition** d'admettre les composites (D18) avec la règle de familles ci-dessus.

**Décision attendue : valider / modifier (préciser) / refuser**
Décision de Léo : …

---

## Page 9 — `egalites` · Égalités

**En une phrase** : les écarts de situation entre les personnes et entre les groupes : répartition des revenus et du patrimoine, écarts entre femmes et hommes, selon l'origine, entre territoires et entre générations, et mobilité sociale.

| Type | Plancher (fondation sociale, comme dans le Doughnut ; indicateurs de sens « plus bas = mieux ») |
|---|---|
| Question posée à l'utilisateur | « Que doit refléter l'égalité ? Les écarts entre les plus aisés et les plus modestes, entre femmes et hommes, selon l'origine ou le lieu de vie, sont-ils acceptables ? » |

**Contenu** : inégalités de revenu et de patrimoine (rapport entre les 20 % les plus aisés et les 20 % les plus modestes, indice de Gini, ratio de Palma, effet de la redistribution) ; écarts femmes-hommes (salaires, emploi, temps domestique, représentation) ; écarts selon l'origine et discriminations ; territoires ; générations ; mobilité sociale.

**Par rapport à v0** : même dimension ; les discriminations selon l'origine et la parité politique y sont nommées.

**Cadres qui la retiennent** : comme **contenu**, 6 sur 6 (Doughnut, Stiglitz-Sen-Fitoussi, OCDE, Eurostat, INSEE, ODD 10.1 et objectifs femmes-hommes) ; comme **dimension nommée**, le seul Doughnut (« Égalité », *Equality*) — Stiglitz-Sen-Fitoussi et l'OCDE traitent les inégalités dans chaque dimension.

**Indicateurs incontournables** : inégalité de revenu ; écarts femmes-hommes.

**Candidats France : ≈ 16 stricts, ≈ 20 élargis.** Crosswalk : 33 lignes (17 disponibles). INSEE : 31 séries, dont 23 conformes. Autres : DREES (redistribution), PNUD (indice d'inégalité de genre, 1990–2023), DEPP (réussite selon l'origine sociale). Exemples : rapport S80/S20 (1996–2023) ; indice de Gini ; rapport D9/D1 ; ratio de Palma ; part des 40 % les plus modestes ; effet de la redistribution ; écart de salaire femmes-hommes (2010–2023) ; écart de taux d'emploi femmes-hommes ; femmes parmi les cadres dirigeants de la fonction publique ; femmes au Parlement ; indice d'inégalité de genre ; écart d'emploi entre Français et ressortissants de pays hors UE.

**Critères du gel 1**

| Critère | Verdict |
|---|---|
| ≥ 3 cadres ou finalité | oui comme contenu ; dimension propre **justifiée par la finalité** (valeur forte du débat public ; information sur la préférence des utilisateurs pour l'égalité) |
| Distincte | oui, **à condition d'appliquer la règle R3** : les écarts ici, les niveaux et taux de privation dans les autres dimensions (le taux de pauvreté reste en niveau de vie) |
| Faisable | oui |
| Intelligible | oui |

**Arbitrages touchant cette page**
- **A9 — Dimension propre ou transversale ?** (A) dimension propre (v0) ; (B) transversale : chaque dimension porte ses écarts et l'interface offre une « lentille équité » ; libère une place (par exemple pour une dimension « Économie et avenir »), mais beaucoup d'écarts ne sont pas annuels et l'interface grand public se complique. **Recommandé : A.**
- **A8 — Discriminations selon l'origine** : (A) ici (écarts d'emploi, de chômage, de pauvreté selon l'origine migratoire ; discriminations ressenties en irrégulier) ; (B) démocratie et droits (comme Eurostat). **Recommandé : A.**

**Recommandation** : valider.

**Décision attendue : valider / modifier (préciser) / refuser**
Décision de Léo : …  Arbitrages A8, A9 : suivre la recommandation / autre option : …

---

## Page 10 — `planete` · Planète

**En une phrase** : les pressions que le mode de vie et l'économie français exercent sur les grands équilibres naturels — climat, biodiversité, sols, eau, azote et phosphore, pollutions, ressources, énergie — à maintenir sous des plafonds.

| Type | **Plafond** (on vise en dessous d'un maximum) |
|---|---|
| Question posée à l'utilisateur | « Que doit refléter la planète ? Est-ce que notre façon de vivre reste dans les limites que la nature peut supporter, ici et ailleurs ? » |

**Contenu** : climat (émissions sur le territoire, empreinte carbone) ; énergie (consommation, part des fossiles, renouvelables) ; biodiversité ; sols (artificialisation, forêts) ; eau (prélèvements, état des rivières et des nappes, nitrates, pesticides) ; azote et phosphore ; pollutions et déchets ; consommation de matières et recyclage.

**Par rapport à v0** : même dimension ; l'énergie y est nommée ; les conditions subies (pollution locale, eau du robinet, canicules) passent en cadre de vie.

**Cadres qui la retiennent : 5 sur 6** — Doughnut (9 dimensions du plafond écologique), Stiglitz-Sen-Fitoussi (soutenabilité), OCDE (capital naturel), INSEE (empreinte carbone, artificialisation), ODD et objectifs (SNBC, zéro artificialisation nette, 30 % d'aires protégées…). Eurostat Quality of life : aucun.

**Indicateurs incontournables** : émissions de gaz à effet de serre et empreinte carbone ; usage des sols.

**Candidats France : ≥ 40 stricts.** Crosswalk : 55 lignes (33 disponibles). INSEE : 192 séries, dont 141 conformes. Autres : Citepa (1990–2025), SDES, OCDE, Hub'Eau. Bornes scientifiques disponibles : limites par habitant du Doughnut pour six empreintes (CO2 0,95 t/hab. ; azote 8,5 kg/hab. ; phosphore 0,85 kg/hab. ; eau bleue 384 m³/hab. ; perte d'espèces ; appropriation de la biomasse). Exemples : empreinte carbone (1990–2024) ; émissions sur le territoire ; consommation d'énergie ; part des énergies fossiles ; part des renouvelables ; artificialisation des sols ; oiseaux communs ; espèces menacées ; aires protégées ; excédent d'azote ; pesticides ; prélèvements d'eau ; nitrates dans les nappes ; empreinte matières ; recyclage.

**Critères du gel 1**

| Critère | Verdict |
|---|---|
| ≥ 3 cadres ou finalité | oui (5) |
| Distincte | oui : pressions **exercées** ici, conditions **subies** en cadre de vie (R2) ; précarité énergétique en logement (R10) |
| Faisable | oui |
| Intelligible | oui |

**Arbitrages touchant cette page** : A3 (énergie : consommation et mix ici) ; A14 (adaptation : en cadre de vie) ; A2 (agriculture : engrais, pesticides et bio ici).

**Recommandation** : valider.

**Décision attendue : valider / modifier (préciser) / refuser**
Décision de Léo : …

---

## Annexe — Table de correspondance v0 → v1 (pour le script de long-list)

**Usage** : pour chaque série d'un catalogue, prendre sa `dimension_v0`, parcourir les règles de `31_correspondance_v0_v1.csv` dans l'ordre (colonne `ordre`), et appliquer la **première** règle dont la `dimension_v0` correspond et dont le `motif_libelle` (expression régulière, insensible à la casse) se trouve dans le libellé de la série ; un motif vide s'applique à tout. Colonnes : `ordre, dimension_v0, motif_libelle, dimension_v1, regle, remarque`. Les règles R1 à R12 sont décrites au §3 de la proposition. Le rattachement automatique est un premier jet : la fiche indicateur (M05) peut le corriger, en le motivant.

| `dimension_v0` (catalogues) | Exceptions (motif dans le libellé → dimension v1) | Par défaut → | Séries INSEE concernées (repérage M01) |
|---|---|---|---|
| `niveau_de_vie` | surendettement, dépense imprévue, arriérés, impayés, épargne de précaution, actifs financiers liquides → `securite` | `niveau_de_vie` | 154 (aucune exception rencontrée) |
| `travail` | — | `travail` | 131 |
| `logement_cadre_vie` | — | `logement_cadre_vie` | 31 |
| `sante` | tués, blessés ou décès sur la route, accidents de la circulation → `securite` ; sous-alimentation, insécurité alimentaire, faim → `niveau_de_vie` | `sante` | 148 : 12 vers `securite`, 136 restent |
| `education` | compétences, illectronisme → `education` (prioritaire) ; internet, haut débit, fibre, connexion → `logement_cadre_vie` ; pratiques culturelles ou sportives → `liens_bien_etre` | `education` | 52 : 14 vers `logement_cadre_vie`, 38 restent |
| `liens_bien_etre` | — | `liens_bien_etre` | 60 |
| `securite_confiance` | confiance envers les autres → `liens_bien_etre` ; confiance dans les institutions, le gouvernement, la justice, la police → `democratie` ; transitions vers le chômage, insécurité du marché du travail → `travail` | **`securite`** (nouvel identifiant) | 28 : 1 vers `liens_bien_etre`, 27 vers `securite` |
| `democratie` | — | `democratie` | 21 |
| `egalites` | — | `egalites` | 47 |
| `planete` | eau non conforme → `logement_cadre_vie` ; catastrophes naturelles, inondations, canicules, températures extrêmes → `logement_cadre_vie` ; exposition aux particules, qualité de l'air, concentrations de PM ou NO2 → `logement_cadre_vie` | `planete` | 383 : 8 vers `logement_cadre_vie`, 375 restent |
| `non rattachable` (crosswalk) | stocks de capitaux → `niveau_de_vie` ; production domestique → `liens_bien_etre` ; levier, stabilité financière → hors grille | à classer | — |
| `contexte` | — | hors grille | 6 |
| `non_classe` | — | à classer | 2 |

Bilan sur les 1 063 séries INSEE repérées : **35 changent de dimension**, 27 changent seulement d'identifiant (`securite_confiance` → `securite`), 8 restent hors grille ou à classer. Si la variante « économie » (A5-B avec A9-B) était retenue, la règle par défaut de `niveau_de_vie` serait scindée (sous-thème économique → nouvelle dimension) et `egalites` deviendrait une lentille transversale : la table serait à refaire.
