# Extraction des cadres de référence (mission M03, tâche T1)

Version de travail — 13 octobre 2026 — agent M03 (phase 1). Document de méthodologie, sans valeur de décision : la grille v1 sera proposée en phase 2 (T3) et tranchée par la session mère.

## Mode d'emploi

- Une section par cadre, même structure : **références et accès** ; **dimensions** ; **indicateurs par dimension** (libellé, définition courte, unité, sens, seuil minimal ou cible, source de données citée) ; **principe d'agrégation** ; **remarques sur la pertinence pour la France**.
- Libellés traduits en français, libellé original anglais entre parenthèses quand il est utile.
- Sens : `haut` = plus c'est élevé, mieux c'est ; `bas` = l'inverse (convention de la charte §5.1).
- Les mentions **« à vérifier »** signalent une information plausible mais non confirmée sur la source primaire au moment de la rédaction ; **« non trouvé »** signale une information cherchée et non trouvée. Aucun seuil n'est reconstitué de mémoire sans cette mention.
- Le détail ligne à ligne (avec le rattachement à la grille v0) est dans `30_indicateurs_cadres_reference.csv` ; la matrice de synthèse est dans `30_crosswalk_synthese.md`.

## Vue d'ensemble

| § | Cadre | Dimensions | Lignes du CSV | Seuils normatifs chiffrés | Agrégation | Lecture de la source |
|---|---|---|---|---|---|---|
| 1 | Doughnut 3.0 (2025) | 12 sociales + 9 écologiques | 35 | 13 limites + 5 seuils sociaux (+ 0 % de privation) | aucun indice ; médianes de privation et de dépassement | tableaux 1 et 2 lus ; tableaux supplémentaires non accessibles |
| 2 | Stiglitz-Sen-Fitoussi (2009) | 8 (+ subjectif et inégalités transversaux, soutenabilité à part) | 39 | aucun | pluralité d'indices possibles (rec. 9) ; ne pas mêler présent et futur | lu jusqu'à la p. 50-51 |
| 3 | OCDE *How's Life? 2024* et BLI | 11 bien-être actuel + 4 capitaux | 100 + 4 | aucun (1 valeur guide OMS dans une définition) | tableau de bord ; BLI pondéré par l'utilisateur | liste et valeurs France par API SDMX ; guide du lecteur non lisible |
| 4 | Eurostat Quality of life (2017) | 8 + 1 | 94 | aucun | tableau de bord d'indicateurs phares | rapport lu jusqu'à la p. 46 ; codes partiellement vérifiés |
| 5 | INSEE NIR (édition 2025) | 3 domaines, 10 indicateurs | 15 | 4 références citées | tableau de bord | PDF lu en entier |
| 6 | ODD et objectifs officiels France-UE | — | 16 + 41 | 57 (dont 14 « à vérifier ») | sans objet (bornes) | textes primaires ou sources secondaires fiables |

---

## 1. Doughnut 3.0 (Fanning & Raworth, *Nature*, 2025)

### 1.1 Références et accès

- Fanning A.L., Raworth K. (2025), « Doughnut of social and planetary boundaries monitors a world out of balance », *Nature* 646, 47–56 (rubrique *Analysis*), publié en ligne le 1er octobre 2025, DOI 10.1038/s41586-025-09385-1, accès libre CC BY 4.0.
- **Version lue** : version publiée déposée sur White Rose eprints (https://eprints.whiterose.ac.uk/id/eprint/233706, fichier PDF « Published Version », CC BY 4.0). **Tableau 1 p. 51** (fondation sociale), **tableau 2 p. 52** (plafond écologique), section *Methods*.
- **Non accessibles** pendant la mission : les pages `…/tables/1` et `…/tables/2` de nature.com (lecture interdite par le robots.txt) ; les *Supplementary Information* (Supplementary Discussion 1 et 2, Supplementary Tables 1 et 2 : sources détaillées par indicateur) hébergées sur static-content.springer.com (même interdiction) ; le dépôt Zenodo des données et du code (DOI 10.5281/zenodo.15688961, refus HTTP 429) ; l'explorateur de données de https://doughnuteconomics.org/doughnut/ (contenu chargé en JavaScript) ; le rapport « The Evolving Doughnut » (Raworth 2025, DOI 10.64981/XGRX2738, erreur de téléchargement).
- Conséquence : la **source primaire exacte de chaque indicateur social** (organisme fournisseur) n'a pas pu être lue dans le tableau supplémentaire 1. L'article indique seulement que les séries sociales proviennent de la **base de données des indicateurs ODD de l'ONU** (réf. 14) et que les données écologiques suivent la mise à jour des limites planétaires de **Richardson et al. (2023)**, *Science Advances* (réf. 13). Les fournisseurs probables (FAO, OMS, Banque mondiale, Gallup, V-Dem…) sont indiqués « à vérifier » dans le CSV.
- Les valeurs chiffrées ci-dessous ont été relevées avec l'outil de lecture de page sur le PDF publié ; elles sont cohérentes entre elles (recalcul des dépassements vérifié pour l'aragonite et l'ozone) mais une relecture visuelle des tableaux 1 et 2 reste souhaitable.

### 1.2 Dimensions

21 dimensions : **12 dimensions sociales** (fondation sociale, « plancher » sous lequel se trouve une privation humaine critique) et **9 dimensions écologiques** (plafond écologique = les neuf processus des limites planétaires, au-delà desquels se trouve une dégradation planétaire critique). **35 indicateurs** : 22 sociaux (dont 1 sans données, l'inégalité raciale : 21 renseignés) et 13 écologiques. Au plus deux indicateurs par dimension.

| Fondation sociale (12) | Plafond écologique (9) |
|---|---|
| Alimentation (*Food*) | Changement climatique (*Climate change*) |
| Santé (*Health*) | Acidification des océans (*Ocean acidification*) |
| Éducation (*Education*) | Pollution chimique (*Chemical pollution*) |
| Revenu et travail (*Income and work*) | Pollution par les nutriments (*Nutrient pollution*) |
| Eau et assainissement (*Water and sanitation*) | Pollution de l'air (*Air pollution*) |
| Énergie (*Energy*) | Perturbation de l'eau douce (*Freshwater disruption*) |
| Connectivité (*Connectivity*) | Conversion des terres (*Land conversion*) |
| Logement (*Housing*) | Effondrement de la biodiversité (*Biodiversity breakdown*) |
| Égalité (*Equality*) | Appauvrissement de la couche d'ozone (*Ozone-layer depletion*) |
| Cohésion sociale (*Social cohesion*) | |
| Voix politique (*Political voice*) | |
| Paix et justice (*Peace and justice*) | |

### 1.3 Indicateurs de la fondation sociale (tableau 1, p. 51)

Chaque indicateur social est exprimé en **% de la population mondiale en situation de privation** (« shortfall ») : sens `bas`, cible implicite **0 %** (personne sous le plancher) ; la colonne « seuil » donne le **standard minimal** qui définit la privation. Valeurs mondiales : moyennes sur deux ans ; entre parenthèses, première année postérieure à 2000 (insécurité alimentaire 2015 ; NEET, soutien social, corruption 2005).

| Dimension | Indicateur | Définition (tableau 1) | Standard minimal / seuil de privation | Monde 2000–01 → 2021–22 |
|---|---|---|---|---|
| Alimentation | Sous-alimentation (*Undernourished*) | % de la population sous-alimentée | prévalence de la sous-alimentation (définition FAO, ODD 2.1.1 — à vérifier) | 13 → 10 % |
| Alimentation | Insécurité alimentaire (*Food insecurity*) | % de la population en insécurité alimentaire modérée ou grave | échelle FIES, ODD 2.1.2 (à vérifier) | (23) → 29 % |
| Santé | Mortalité des moins de 5 ans (*Under-5 mortality*) | % de la population vivant dans un pays où la mortalité avant 5 ans dépasse 25 ‰ naissances vivantes | **25 décès pour 1 000 naissances vivantes** (cible ODD 3.2) | 75 → 42 % |
| Santé | Manque de services de santé (*Lack of health services*) | % de la population vivant dans un pays sans couverture élevée en services de santé essentiels | **indice de couverture sanitaire universelle (CSU) < 60/100** (ODD 3.8.1) | 79 → 28 % |
| Éducation | Analphabétisme (*Illiteracy rate*) | % des adultes de 15 ans ou plus analphabètes | non trouvé (définition UNESCO probable, à vérifier) | 23 → 16 % |
| Éducation | Secondaire inachevé (*Incomplete secondary school*) | % des jeunes adultes de 21 à 23 ans sans diplôme du deuxième cycle du secondaire | achèvement du 2nd cycle du secondaire (ODD 4.1.2, à vérifier) | 61 → 37 % |
| Revenu et travail | Pauvreté sociétale (*Societal poverty*) | % de la population sous le seuil de pauvreté sociétale | **moitié du revenu (ou consommation) médian national, ou 15 $ par jour** selon le plus élevé (formulation exacte à vérifier) | 85 → 73 % |
| Revenu et travail | Jeunes NEET (*Youth NEET*) | % des 15–24 ans ni en emploi, ni en études, ni en formation | ODD 8.6.1 | (25) → 21 % |
| Eau et assainissement | Eau potable non sûre (*Unsafe drinking water*) | % de la population sans service d'eau potable géré en toute sécurité | « géré en toute sécurité » (ODD 6.1.1) | 39 → 37 % |
| Eau et assainissement | Assainissement non sûr (*Unsafe sanitation*) | % de la population sans service d'assainissement géré en toute sécurité | « géré en toute sécurité » (ODD 6.2.1) | 66 → 42 % |
| Énergie | Absence d'électricité (*Lack of electricity*) | % de la population sans accès à l'électricité | ODD 7.1.1 | 21 → 8 % |
| Énergie | Absence de combustibles propres (*Lack of clean fuels indoors*) | % de la population sans combustibles et technologies propres pour cuisiner, se chauffer, s'éclairer | ODD 7.1.2 | 50 → 27 % |
| Connectivité | Absence de transports publics (*Lack of public transport*) | % de la population urbaine sans accès commode aux transports publics | « accès commode » (ODD 11.2.1) ; donnée 2020 seulement | – → 53 % |
| Connectivité | Absence d'internet (*Lack of internet*) | % de la population n'utilisant pas internet | ODD 17.8.1 (à vérifier) | 93 → 37 % |
| Logement | Bidonvilles ou logement informel (*Slums or informal housing*) | % de la population urbaine vivant en bidonville ou en habitat informel | ODD 11.1.1 | 40 → 32 % |
| Égalité | Inégalité femmes-hommes (*Gender inequality*) | score de l'indice d'inégalité de genre (IIG/GII, PNUD) pondéré par la population (santé reproductive, autonomisation, emploi) | aucun seuil chiffré (score directement interprété comme écart à l'égalité) | 46 → 35 (score IIG × 100, à vérifier) |
| Égalité | Inégalité raciale (*Racial inequality*) | aucun indicateur mondial ne suit les écarts raciaux et ethniques | — (pas de données) | – |
| Cohésion sociale | Manque de soutien social (*Lack of social support*) | % de la population n'ayant personne sur qui compter en cas de difficulté | question Gallup World Poll (à vérifier) | (21) → 24 % |
| Cohésion sociale | Inégalité de revenu (*Income inequality*) | % de la population vivant dans un pays où le **ratio de Palma ≥ 2** | **ratio de Palma = 2** | 72 → 65 % |
| Voix politique | Régimes autocratiques (*Autocratic regimes*) | % de la population vivant dans un pays gouverné par un régime autocratique | classification des régimes (V-Dem « Regimes of the World », à vérifier) | 46 → 71 % |
| Paix et justice | Corruption (*Corruption*) | % de la population percevant une corruption généralisée dans l'État et les entreprises | question Gallup World Poll (à vérifier) | (80) → 75 % |
| Paix et justice | Taux d'homicide (*Homicide rate*) | % de la population vivant dans un pays où le taux d'homicide est ≥ 5 pour 100 000 habitants | **5 homicides pour 100 000** (les auteurs notent l'absence de seuil officiel) | 29 → 20 % |

Critères de sélection des indicateurs sociaux (*Methods*) : pertinence mondiale ; privation mesurée en part de la population ; données récentes, large couverture et séries ; seuils minimaux officiellement reconnus ; suivi dans le cadre mondial des indicateurs ODD ; au plus deux indicateurs par dimension.

### 1.4 Indicateurs du plafond écologique (tableau 2, p. 52)

Chaque indicateur écologique est une **variable de contrôle mondiale** rapportée à une **limite planétaire** (sens `bas` sauf mention ; « dépassement » = écart relatif à la limite, voir 1.5). Valeurs : moyennes sur deux ans (ozone : cinq ans, 2000–2004 et 2018–2022).

| Dimension | Indicateur | Variable de contrôle (unité) | Limite | Monde 2000–01 → 2021–22 (dépassement) |
|---|---|---|---|---|
| Changement climatique | Concentration de CO2 | CO2 atmosphérique (ppm) | **≤ 350 ppm** | 370 ppm (+28 %) → 416 ppm (+94 %) |
| Changement climatique | Forçage radiatif | forçage radiatif anthropique au sommet de l'atmosphère (W/m²) | **≤ 1 W/m²** | 1,8 (+78 %) → 2,8 (+183 %) |
| Acidification des océans | Saturation en aragonite | état de saturation moyen en aragonite en surface (Ωarag) — sens `haut` | **≥ 80 % de l'état préindustriel (3,44 Ωarag)** | 2,99 (−34 %) → 2,80 (−6 %) : sous la limite mais en dégradation |
| Pollution chimique | Produits chimiques dangereux | production de produits chimiques dangereux (Mt/an) | **≤ 5 % de la production chimique totale de 2000 (1 200 Mt)** = 60 Mt | 933 Mt (+1 455 %) → 1 964 Mt (+3 174 %) |
| Pollution par les nutriments | Phosphore | phosphore appliqué aux sols comme engrais (Mt/an) | **≤ 6,2 Mt/an** | 14 (+123 %) → 23 (+273 %) |
| Pollution par les nutriments | Azote | azote appliqué aux sols comme engrais (Mt/an) | **≤ 62 Mt/an** | 134 (+116 %) → 193 (+212 %) |
| Pollution de l'air | Aérosols interhémisphériques | asymétrie de l'épaisseur optique des aérosols (AOD) entre hémisphères | **≤ 0,1 AOD** | 0,08 (−29 %) → 0,08 (−29 %) ; tendance inconnue |
| Perturbation de l'eau douce | Eau bleue | % des terres émergées où le débit d'eau bleue est perturbé hors de la variabilité holocène | **≤ 10,2 %** | 18,2 % (+78 %) → 18,2 % (+78 %) |
| Perturbation de l'eau douce | Eau verte | % des terres émergées où l'humidité du sol racinaire sort de la variabilité holocène | **≤ 11,1 %** | 15,9 % (+43 %) → 19,3 % (+74 %) |
| Conversion des terres | Surface forestière | surface forestière en part du couvert forestier d'avant altération (millions de km²) — sens `haut` | **≥ 75 % de 64 millions de km²** | 39 (+55 %) → 38 (+61 %) |
| Effondrement de la biodiversité | Taux d'extinction | extinctions par million d'espèces-années (E/MSY) | **≤ 10 E/MSY** | 100 (+900 %) → 100 (+900 %) ; tendance inconnue |
| Effondrement de la biodiversité | Appropriation humaine de la production primaire nette (HANPP) | Gt de carbone par an | **≤ 10 % de 55,9 Gt C** | 15 (+162 %) → 17 (+204 %) |
| Appauvrissement de la couche d'ozone | Ozone stratosphérique | concentration en unités Dobson (DU) — sens `haut` | **baisse ≤ 5 % par rapport à la valeur 1964–1980 de 290 DU** | 283,0 (−50 %) → 283,4 (−53 %) |

### 1.5 Principe d'agrégation

- **Aucun indice composite.** L'article publie des valeurs par indicateur, des tendances (régression linéaire MCO, base 2000) et deux statistiques de synthèse : la **médiane** (et l'intervalle interquartile) de la privation sociale (35 % de la population mondiale en 2022) et du dépassement écologique (environ ×2, médiane 96 %).
- **Normalisation écologique** : dépassement = (x_t − x_base)/(x* − x_base) − 1, où x* est la limite et x_base la valeur préindustrielle (holocène) ; formule inversée pour l'aragonite, la forêt et l'ozone. Borne inférieure −100 % (valeur préindustrielle), pas de borne supérieure.
- **Scénarios** : trajectoire linéaire jusqu'à zéro privation en **2030** (social, 8 ans) et zéro dépassement en **2050** (écologique, 28 ans).
- **Déclinaison par groupes de pays** (RNB/hab. en $ PPA 2017, PNUD 2023/24) : < 8 100 $ (40 % les plus pauvres), 8 100–33 200 $, > 33 200 $ (20 % les plus riches, groupe de la France). Pour le plafond, empreintes de consommation 2017 (Tian et al. 2024, *Nature*) sur six indicateurs (CO2, azote, phosphore, eau bleue, perte d'espèces, HANPP) et budgets par habitant égalitaires pour quatre limites.

### 1.6 Remarques sur la pertinence pour la France

- **Fondation sociale** : conçue pour les privations mondiales ; en France, plusieurs indicateurs sont proches de 0 % ou non pertinents (électricité, combustibles propres, bidonvilles, sous-alimentation, eau potable). Les seuils binaires « pays au-dessus/au-dessous » (mortalité infantile, CSU, Palma, homicides) placent la France entière d'un côté du seuil : pour un indicateur national, il faut reprendre la **variable continue** (taux de mortalité infantile, ratio de Palma, taux d'homicide) et réutiliser la valeur du seuil comme borne. Ce que la fondation apporte au-delà de v0 : **pauvreté relative à 50 % du médian**, **NEET**, **soutien social**, **corruption perçue**, **régime politique**, **transports publics**, **inégalité femmes-hommes**, **sous-alimentation/insécurité alimentaire**.
- **Inégalité raciale** : aucun indicateur mondial ; en France, la statistique ethnique est très encadrée (enquête Trajectoires et Origines, discriminations ressenties) — besoin non couvert explicitement par v0.
- **Plafond écologique** : variables mondiales, non mesurables à l'échelle nationale telles quelles ; la déclinaison nationale passe par des **empreintes de consommation** (CO2, azote, phosphore, eau bleue, biodiversité, HANPP : Tian et al. 2024) ou des **budgets par habitant** (« downscaling »). Proxys nationaux probables : empreinte carbone (SDES), excédent d'azote (Eurostat), surface forestière, indice d'exploitation de l'eau, ventes de produits phytosanitaires, etc. — à confirmer en M01/M02/M04.
- La **pollution de l'air** du Doughnut est un phénomène planétaire (aérosols) et non la qualité de l'air locale (PM2,5), que v0 range dans `logement_cadre_vie`.
- Les **portraits de ville** (*Doughnut Unrolled*, portraits nationaux) mêlent local et global : non retenus ici, conformément à la fiche M03.

---

## 2. Rapport Stiglitz-Sen-Fitoussi (2009)

### 2.1 Références et accès

- Stiglitz J.E. (président), Sen A. (conseiller), Fitoussi J.-P. (coordinateur), *Report by the Commission on the Measurement of Economic Performance and Social Progress*, Paris, 2009 (commission créée en février 2008). Version française : *Rapport de la Commission sur la mesure des performances économiques et du progrès social*.
- **Versions lues** : PDF anglais hébergé par Eurostat (https://ec.europa.eu/eurostat/documents/8131721/8131772/Stiglitz-Sen-Fitoussi-Commission-report.pdf) et copie sur base.socioeco.org (`rapport_anglais.pdf`) ; PDF français sur vie-publique.fr (`094000427.pdf`). Les numéros de page ci-dessous sont ceux du PDF anglais (approximatifs, déduits des marqueurs de page).
- **Limite** : l'outil de lecture tronque le texte vers la **p. 50–51** sur les trois copies. Sont donc **lus** : synthèse et 12 recommandations (p. 12–18), chapitre 1 (questions classiques relatives au PIB), chapitre 2 jusqu'à « voix politique et gouvernance » (p. 41–51). **Non lus** : fin du chapitre 2 (liens sociaux, conditions environnementales, insécurité physique et économique, corrélations et agrégation des dimensions) et chapitre 3 (développement durable et environnement, à partir de la p. 61). Les mesures de ces parties sont signalées « à vérifier ».

### 2.2 Dimensions

Huit dimensions clés du bien-être (synthèse, § 28, p. 14–15), à considérer **simultanément** :

1. Niveau de vie matériel (revenu, consommation et patrimoine) — *Material living standards (income, consumption and wealth)*
2. Santé — *Health*
3. Éducation — *Education*
4. Activités personnelles, dont le travail — *Personal activities including work*
5. Voix politique et gouvernance — *Political voice and governance*
6. Liens et rapports sociaux — *Social connections and relationships*
7. Environnement (conditions présentes et futures) — *Environment (present and future conditions)*
8. Insécurité, tant économique que physique — *Insecurity, of an economic as well as a physical nature*

Le rapport ajoute deux « couches » transversales : le **bien-être subjectif** (évaluations de la vie et affects, recommandation 10) et les **inégalités** dans toutes les dimensions (recommandations 4 et 7), ainsi qu'un pilier distinct de **soutenabilité** (recommandations 11 et 12).

### 2.3 Les douze recommandations (synthèse, p. 12–18, paraphrasées)

| N° | Recommandation | Page |
|---|---|---|
| 1 | Évaluer le bien-être matériel par le revenu et la consommation plutôt que par la production | 12 |
| 2 | Privilégier le point de vue des ménages | 13 |
| 3 | Considérer le revenu et la consommation conjointement avec le patrimoine | 13 |
| 4 | Accorder plus d'importance à la répartition des revenus, de la consommation et des richesses | 14 |
| 5 | Élargir les indicateurs de revenus aux activités non marchandes | 14 |
| 6 | La qualité de la vie dépend des conditions objectives et des capacités ; améliorer les mesures de santé, d'éducation, d'activités personnelles, d'environnement, et surtout de liens sociaux, de voix politique et d'insécurité | 15 |
| 7 | Évaluer de manière exhaustive les inégalités dans toutes les dimensions de la qualité de la vie | 16 |
| 8 | Concevoir les enquêtes pour évaluer les liens entre domaines de qualité de la vie pour chaque personne (cumul des avantages et désavantages) | 16 |
| 9 | Fournir l'information nécessaire pour agréger les dimensions et construire différents indices | 16 |
| 10 | Inclure dans les enquêtes des questions sur l'évaluation de la vie, les expériences hédoniques et les priorités | 17 |
| 11 | Évaluer la soutenabilité par un tableau de bord de stocks ; un éventuel indice monétaire doit rester centré sur les aspects économiques | 17 |
| 12 | Suivre les aspects environnementaux de la soutenabilité par des indicateurs physiques, dont un indicateur clair de proximité de niveaux dangereux de dommages (climat, ressources halieutiques) | 17–18 |

### 2.4 Mesures citées par dimension

Le rapport **ne fixe pas de liste fermée d'indicateurs ni de seuils** : il recommande des familles de mesures. Aucun seuil chiffré n'est proposé (hors mention de « niveaux dangereux » pour l'environnement, non chiffrés).

| Dimension | Mesures citées (page) |
|---|---|
| Niveau de vie matériel | revenu national net disponible (p. 25) ; revenu disponible réel des ménages, ajusté des transferts en nature (p. 13, 25, 31) ; consommation des ménages (p. 12–13) ; patrimoine et bilans des ménages (p. 14, 30) ; valeurs médianes et non seulement moyennes du revenu, de la consommation et du patrimoine (p. 33–34) ; statistiques de pauvreté (p. 14) ; valorisation de la production domestique et des loisirs (p. 36–37) ; indices de prix par groupe (p. 35) |
| Santé | espérance de vie à la naissance et mortalité par âge, plusieurs mesures à suivre (p. 46) ; morbidité : prévalence et limitations fonctionnelles, déclarations et registres (p. 47) ; santé mentale, jugée sous-mesurée (p. 47) ; gradient social de l'espérance de vie (p. 47) ; indices combinés mortalité-morbidité sans consensus (p. 47) |
| Éducation | taux de diplômés, années de scolarité (p. 47–48) ; compétences mesurées par des tests standardisés (littératie, numératie) (p. 47–48) ; inégalités de résultats, notamment des jeunes les plus en difficulté (p. 48) |
| Activités personnelles dont travail | indicateurs de « travail décent » : emploi non standard, écarts femmes-hommes d'emploi et de salaire, discriminations, formation tout au long de la vie, accès des personnes handicapées, temps de travail et horaires atypiques, équilibre vie professionnelle-vie privée, accidents du travail, intensité du travail, dialogue social, autonomie (p. 49–50) ; travail domestique non rémunéré et sa répartition (p. 50) ; temps de trajet domicile-travail, accessibilité et coût des transports (p. 50) ; loisirs : quantité, qualité, participation culturelle, « loisirs pauvres » (enfants sans vacances) (p. 50) ; logement : sans-abrisme, hébergement d'urgence, qualité, surpeuplement, services de proximité (p. 50) ; enquêtes emploi du temps avec ressenti par activité (p. 50–51) |
| Voix politique et gouvernance | démocratie effective, suffrage universel, médias libres, organisations de la société civile, garanties légales, État de droit (p. 50–51) ; aucun indicateur chiffré nommé |
| Liens et rapports sociaux | non lu (fin du chapitre 2) ; mesures évoquées dans la synthèse : capital social comme stock (p. 14) ; confiance, isolement, bénévolat, participation associative — **à vérifier** |
| Environnement | conditions présentes : exposition à la pollution (air, bruit), accès aux aménités environnementales — **à vérifier** (pages non lues) ; soutenabilité : concentration de gaz à effet de serre et émissions qui y mènent, épuisement des ressources halieutiques (p. 17–18, § 39) |
| Insécurité | non lu ; mesures évoquées : insécurité physique (victimation, crainte de la criminalité) et économique (risques de chômage, de maladie, de vieillesse) — **à vérifier** |
| Bien-être subjectif (transversal) | évaluations de la vie, globales et par domaine ; affects positifs (joie, fierté) et négatifs (douleur, inquiétude), à mesurer séparément ; part du temps où le sentiment dominant est négatif (p. 16–17, 44–45) |
| Soutenabilité (pilier distinct) | tableau de bord de stocks : capital physique, humain, social, naturel (§ 37–38, p. 17) ; indice monétaire limité aux aspects économiques ; indicateurs physiques de pression environnementale (rec. 12) |

### 2.5 Principe d'agrégation

- Priorité à un **système statistique pluriel** ; l'agrégation est secondaire (§ 21). Plusieurs mesures synthétiques possibles selon la question posée (§ 32) : satisfaction moyenne dans la vie, indices composites type IDH, part du temps à affect dominant négatif, comptages de privations objectives, mesures en **revenu équivalent** (approche des « allocations équitables », pondération par les préférences des personnes, p. 42–43).
- La recommandation 9 demande aux instituts statistiques de fournir les données permettant à chacun de **construire différents indices** — directement en phase avec la philosophie de l'observatoire (pondérations paramétrables).
- **Ne pas mêler bien-être actuel et soutenabilité** dans un même chiffre (analogie du tableau de bord d'une voiture : vitesse et niveau d'essence, § 36).

### 2.6 Remarques sur la pertinence pour la France

- Cadre fondateur des NIR de l'INSEE (loi du 13 avril 2015), du cadre Eurostat et du cadre de l'OCDE : sa grille de huit dimensions est très proche de v0.
- Deux points structurants pour la grille v1 : (1) le bien-être subjectif y est **transversal** (couche de mesure) et non une dimension (argument pour l'arbitrage Q-B) ; (2) la **soutenabilité** (stocks de capitaux, dont dette et patrimoine) est un pilier séparé — v0 range investissement et dette dans `niveau_de_vie`, ce que le rapport déconseille implicitement.
- Le rapport rattache **logement, transports et loisirs** aux « activités personnelles » (emploi du temps) : découpage différent de v0, qui regroupe logement et cadre de vie.
- L'insécurité économique (risques) y est rapprochée de l'insécurité physique, comme dans v0 (`securite_confiance`) et dans le cadre Eurostat.

---

## 3. OCDE — *How's Life? 2024* et Better Life Index

### 3.1 Références et accès

- OCDE (2024), *How's Life? 2024: Well-being and Resilience in Times of Crisis*, éditions OCDE, Paris, novembre 2024 (sixième édition ; « plus de 80 indicateurs » ; aucune édition plus récente trouvée au 13/10/2026). Pages web du rapport consultées : https://www.oecd.org/en/publications/how-s-life-2024_90ba854a-en/full-report (le contenu des chapitres est chargé en JavaScript : **tableau des indicateurs et guide du lecteur non lisibles** avec l'outil).
- **Source utilisée pour la liste des indicateurs** : la base de données *How's Life? Well-being Database* de l'OCDE, lue par son **API SDMX** (structure de données `DSD_HSL` v1.1, agence `OECD.WISE.WDP`) :
  - liste des domaines : codelist `CL_DOMAIN` (https://sdmx.oecd.org/public/rest/codelist/OECD.WISE.WDP/CL_DOMAIN/latest) ;
  - liste des mesures : codelist `CL_MEASURE` (https://sdmx.oecd.org/public/rest/codelist/OECD.WISE.WDP/CL_MEASURE/latest) ;
  - dernières valeurs France : flux `DSD_HSL@DF_HSL_CWB` (bien-être actuel) et `DSD_HSL@DF_HSL_FWB` (ressources pour le bien-être futur), requête `FRA..._T._T._T.?lastNObservations=1`, consultés le 13/10/2026.
- Les **définitions** ci-dessous sont des résumés établis à partir des libellés OCDE ; les définitions détaillées et les **sources primaires** (EU-SILC, Gallup World Poll, PISA, PIAAC, comptes nationaux…) n'ont pas pu être lues dans le guide du lecteur : elles sont indiquées « à vérifier » dans le CSV.
- **Better Life Index** (BLI, https://www.oecdbetterlifeindex.org) : site interdit à l'outil (robots.txt). Composition reprise d'une source secondaire (page méthodologique de Statistics Jersey) et des connaissances antérieures : **à vérifier**.

### 3.2 Dimensions

Cadre de bien-être de l'OCDE (révisé en 2020 et utilisé dans *How's Life? 2024*) : **11 dimensions du bien-être actuel** et **4 capitaux** (ressources pour le bien-être futur). Chaque dimension est suivie sous trois angles : **moyennes**, **inégalités** (verticales, entre le haut et le bas de la distribution — suffixe `_VER` — et horizontales, entre groupes) et **privations** (part sous un seuil — suffixe `_DEP`).

| Code | Bien-être actuel | Code | Ressources pour le bien-être futur |
|---|---|---|---|
| HSL_1 | Revenu et patrimoine (*Income and wealth*) | HSL_12 | Capital naturel (*Natural capital*) |
| HSL_2 | Travail et qualité de l'emploi (*Work and job quality*) | HSL_13 | Capital humain (*Human capital*) |
| HSL_3 | Logement (*Housing*) | HSL_14 | Capital social (*Social capital*) |
| HSL_4 | Équilibre vie professionnelle-vie privée (*Work-life balance*) | HSL_15 | Capital économique (*Economic capital*) |
| HSL_5 | Santé (*Health*) | | |
| HSL_6 | Connaissances et compétences (*Knowledge and skills*) | | |
| HSL_7 | Liens sociaux (*Social connections*) | | |
| HSL_8 | Engagement civique (*Civic engagement*) | | |
| HSL_9 | Qualité de l'environnement (*Environmental quality*) | | |
| HSL_10 | Sécurité (*Safety*) | | |
| HSL_11 | Bien-être subjectif (*Subjective well-being*) | | |

### 3.3 Indicateurs par dimension (codelist `CL_MEASURE`) et dernière valeur France

Valeurs France : dernière observation de l'API SDMX (total, tous âges, deux sexes, tous niveaux d'éducation). « – » : pas de valeur France renvoyée. Aucun indicateur OCDE ne porte de **seuil normatif** ; les seuils figurant dans les indicateurs de privation (`_DEP`) sont des seuils de définition (ex. note < 5/10).

| Code | Indicateur (libellé OCDE) | Définition résumée | Unité | Sens | France (année) |
|---|---|---|---|---|---|
| 1_1 | Revenu disponible net ajusté par habitant (*Households and NPISHs net adjusted disposable income per capita*) | revenu disponible des ménages et ISBLSM, net, ajusté des transferts sociaux en nature | $ PPA par hab. | haut | 49 616 (2024) |
| 1_2 | Rapport des revenus du quintile supérieur (*Top average household disposable income quintile*) | rapport S80/S20 du revenu disponible (inégalité verticale) | ratio | bas | 4,56 (2023) |
| 1_3 | Patrimoine net médian (*Median net wealth*) | patrimoine net médian des ménages | $ PPA par ménage | haut | 195 938 (2020) |
| 1_3_VER | Part du décile le plus riche (*Top wealthiest households decile*) | part du patrimoine total détenue par les 10 % de ménages les plus riches | % | bas | 49,9 (2020) |
| 1_4 | Pauvreté monétaire relative (*Household disposable income below the relative income poverty line*) | part de la population sous 50 % du revenu médian (seuil à vérifier) | % | bas | 8,7 (2023) |
| 1_5 | Difficultés à joindre les deux bouts (*Difficulty making ends meet*) | part des 16 ans et plus déclarant des difficultés | % | bas | 21,7 (2025) |
| 1_6 | Insécurité financière (*liquid financial assets below three months of the poverty line*) | part de la population dont les actifs financiers liquides sont inférieurs à 3 mois du seuil de pauvreté | % | bas | 35,9 (2020) |
| 2_1 | Taux d'emploi (*Employment rate*) | part des 25-64 ans en emploi (tranche d'après l'unité renvoyée) | % | haut | 77,7 (2025) |
| 2_2 | Écart salarial femmes-hommes (*Gender wage gap*) | écart de salaire médian entre hommes et femmes, en % du salaire masculin | % | bas | 6,6 (2024) |
| 2_3 | Taux de chômage de longue durée (*Long-term unemployment rate*) | chômeurs depuis 12 mois ou plus, en % de la population active | % | bas | 1,8 (2025) |
| 2_4 | Jeunes NEET (*Youth not in employment, education or training*) | part des 15-24 ans | % | bas | 12,5 (2024) |
| 2_5 | Insécurité sur le marché du travail (*Labour market insecurity*) | perte de revenu attendue liée au risque de chômage, en % des gains antérieurs | % | bas | 3,1 (2016) |
| 2_6 | Tension au travail (*Job strain*) | part des salariés exposés à des exigences élevées et des ressources faibles | % | bas | 25,8 (2015) |
| 2_7 | Longues heures de travail rémunéré (*Long hours in paid work*) | part des salariés travaillant habituellement 50 heures ou plus par semaine (seuil à vérifier) | % | bas | 5,9 (2025) |
| 2_8 | Salaire annuel brut moyen (*Average annual gross earnings*) | salaire brut moyen des salariés à temps plein | $ PPA | haut | 60 608 (2024) |
| 2_8_DEP | Bas salaires (*Full-time employees earning less than two-thirds of gross median earnings*) | part des salariés à temps plein gagnant moins de 2/3 du salaire médian | % | bas | 5,8 (2024) |
| 2_8_VER | Dispersion des salaires (*Top earnings of full-time employees decile*) | rapport entre le décile supérieur et le décile inférieur (D9/D1, à vérifier) | ratio | bas | 2,78 (2024) |
| 2_9 | Satisfaction au travail (*Job satisfaction*) | note moyenne 0-10 | note | haut | 7,1 (2023) |
| 2_9_DEP | Faible satisfaction au travail | part avec note < 5 | % | bas | – |
| 2_9_VER | Inégalité de satisfaction au travail | rapport quintile supérieur / inférieur (à vérifier) | ratio | bas | – |
| 3_1 | Surpeuplement (*Households living in overcrowded conditions*) | part des ménages en logement surpeuplé | % | bas | 7,6 (2024) |
| 3_2 | Accessibilité financière du logement (*Housing affordability*) | part du revenu disponible restant après les dépenses de logement | % | haut | 79,8 (2024) |
| 3_3 | Surcharge des coûts du logement (*Housing cost overburden*) | part de la population (ménages modestes) consacrant plus de 40 % du revenu au logement (définition à vérifier) | % | bas | 10,7 (2024) |
| 3_4 | Accès à internet à domicile (*Households with internet access at home*) | part des ménages | % | haut | 88,1 (2021) |
| 3_5 | Incapacité à maintenir le logement suffisamment chaud (*Inability to keep home adequately warm*) | part des 16 ans et plus | % | bas | 11,8 (2024) |
| 4_1 | Temps libre (*Time off*) | heures par jour consacrées aux loisirs et soins personnels (salariés à temps plein) | h/jour | haut | 16,2 (2009) |
| 4_2 | Longues heures de travail non rémunéré (*Long unpaid working hours*) | part des 15-64 ans consacrant de longues heures au travail non rémunéré (seuil à vérifier) | % | bas | 7,2 (2009) |
| 4_3 | Écart femmes-hommes de temps de travail (*Gender gap in working hours*) | écart de temps de travail total (rémunéré + non rémunéré) | min/jour | bas | 27 (2009) |
| 4_4 | Satisfaction à l'égard de l'emploi du temps (*Satisfaction with time use*) | note moyenne 0-10 | note | haut | 6,6 (2022) |
| 4_4_DEP | Faible satisfaction de l'emploi du temps | part avec note < 5 | % | bas | 16,9 (2022) |
| 4_4_VER | Inégalité de satisfaction de l'emploi du temps | rapport quintile supérieur / inférieur | ratio | bas | 2,88 (2022) |
| 5_1 | Espérance de vie à la naissance (*Life expectancy at birth*) | | années | haut | 83 (2023) |
| 5_2 | Santé perçue positive (*Perceived health as positive*) | part des 16 ans et plus se déclarant en bonne ou très bonne santé ; variante 5_2_DEP : santé perçue négative | % | haut | 66,2 (2024) ; DEP 9,7 |
| 5_3 | Décès par suicide, alcool et drogues (*Deaths from suicide, alcohol, drugs*) | taux standardisé | pour 100 000 | bas | 18,7 (2023) |
| 5_4 | Dépression déclarée (*Self-reported depression*) | part des 15 ans et plus | % | bas | 10,8 (2019) |
| 6_1 / 6_2 / 6_3 | Compétences des élèves en lecture, mathématiques, sciences (*Student … skills*) | score moyen PISA à 15 ans | score | haut | 474 / 474 / 487 (2022) |
| 6_x_DEP | Élèves faibles dans les trois domaines (*Students with low skills in reading, mathematics and science*) | part des élèves de 15 ans sous le niveau 2 dans les trois domaines (à vérifier) | % | bas | 16,8 (2022) |
| 6_1/2/3_VER | Dispersion des scores des élèves | rapport décile supérieur / inférieur | ratio | bas | 1,84 / 1,68 / 1,77 (2022) |
| 6_4 / 6_5 | Compétences des adultes en numératie / littératie (*Adult numeracy / literacy skills*) | score moyen PIAAC | score | haut | 257 / 255 (2023) |
| 6_4_DEP / 6_5_DEP | Adultes faiblement compétents en numératie / littératie | part sous le niveau 2 (à vérifier) | % | bas | 22,6 (2023) / – |
| 6_4_VER / 6_5_VER | Dispersion des scores des adultes | rapport décile supérieur / inférieur | ratio | bas | 1,79 / 1,63 (2012) |
| 7_1 | Soutien social (*Social support*) | part des 15 ans et plus ayant quelqu'un sur qui compter ; variante 7_1_DEP : absence de soutien | % | haut | 87,6 (2025) ; DEP 12,2 |
| 7_2 | Temps consacré aux interactions sociales (*Time spent in social interactions*) | | h/semaine | haut | 6,2 (2009) |
| 7_3 | Satisfaction à l'égard des relations personnelles | note moyenne 0-10 ; 7_3_DEP (< 5) ; 7_3_VER (rapport des quintiles) | note | haut | 7,7 (2022) ; DEP 4,8 ; VER 1,92 |
| 7_4 | Sentiment de solitude (*Feeling lonely*) | part des 16 ans et plus se sentant seuls (fréquence à vérifier) | % | bas | 10,8 (2022) |
| 8_1 | Avoir son mot à dire sur l'action du gouvernement (*Having a say in government*) | part des 16-65 ans estimant avoir leur mot à dire ; 8_1_DEP : l'inverse | % | haut | 26,3 (2023) ; DEP 57,6 |
| 8_2 | Participation électorale (*Voter turnout*) | votants en % de la population en âge de voter (élections nationales) | % | haut | 73,7 (2022) |
| 9_1 | Accès aux espaces verts (*Access to green space*) | part de la population urbaine ayant un espace vert accessible à pied (définition à vérifier) | % | haut | 62,2 (2018) |
| 9_2 | Exposition à la pollution de l'air (*Exposed to air pollution*) | part de la population exposée à des PM2,5 supérieures à la valeur guide de l'OMS (5 µg/m³, à vérifier) | % | bas | 99,7 (2020) |
| 9_3 | Exposition aux températures extrêmes (*Exposure to extreme temperature*) | part de la population exposée (définition à vérifier) | % | bas | 1,0 (2024) |
| 10_1 | Homicides (*Homicides*) | | pour 100 000 | bas | 0,8 (2022) |
| 10_2 | Sentiment de sécurité la nuit (*Feeling safe at night*) | part des 15 ans et plus se sentant en sécurité seuls la nuit ; 10_2_DEP : l'inverse | % | haut | 72,0 (2025) ; DEP 26,3 |
| 10_3 | Décès sur la route (*Road deaths*) | | pour 100 000 | bas | 4,7 (2024) |
| 11_1 | Satisfaction dans la vie (*Life satisfaction*) | note moyenne 0-10 ; 11_1_DEP : part < 5 ; 11_1_VER : rapport des quintiles | note | haut | 7,1 (2025) ; DEP 6,9 (2024) ; VER 2,08 (2024) |
| 11_2 | Solde d'affects négatifs (*Negative affect balance*) | part des 15 ans et plus ayant plus d'affects négatifs que positifs | % | bas | 12,5 (2025) |
| 11_3 | Douleur physique (*Feelings of physical pain*) | part des 15 ans et plus ayant ressenti de la douleur physique la veille (à vérifier) | % | bas | 33,0 (2025) |
| 12_1 | Couverture naturelle et semi-naturelle (*Natural and semi-natural land cover*) | part de la superficie terrestre | % | haut | 52,2 (2022) |
| 12_2 / 12_3 | Perte / gain de couverture naturelle et semi-naturelle | en % de la couverture d'une année de référence (à vérifier) | % | bas / haut | 1,30 / 1,62 (2022) |
| 12_4 | Paysages forestiers intacts (*Intact forest landscapes*) | | km² | haut | 0 (2016) |
| 12_5 / 12_6 | Aires protégées terrestres / marines | part de la superficie terrestre / de la ZEE | % | haut | 31,8 / 33,9 (2024) |
| 12_7 | Indice de la liste rouge (*Red list index of threatened species*) | 1 = aucune espèce menacée | indice 0-1 | haut | 0,84 (2025) |
| 12_8 | Émissions de GES par habitant (*Greenhouse gas emissions per capita*) | émissions territoriales | t éq. CO2/hab. (unité OCDE affichée « kg », à vérifier) | bas | 5,65 (2023) |
| 12_9 | Empreinte carbone (*Carbon footprint*) | émissions liées à la demande finale intérieure | t CO2/hab. ou t éq. CO2/hab. | bas | 6,83 t CO2 (2018) ; 8,37 t éq. CO2 (2020) |
| 12_10 | Énergies renouvelables (*Renewable energy*) | part dans l'approvisionnement total en énergie | % | haut | 14,0 (2024) |
| 12_11 | Bilan des nutriments du sol (*Soil nutrient balance*) | excédent d'azote par hectare de terre agricole (à vérifier) | kg/ha | bas | 17,5 (2023) |
| 12_12 / 12_13 | Stress hydrique (ressources internes / renouvelables totales) | prélèvements en % des ressources | % | bas | 12,1 / 11,4 (2022) |
| 12_14 | Empreinte matières par habitant (*Material footprint per capita*) | | t/hab. | bas | 17,5 (2024) |
| 12_15 | Taux de recyclage (*Recycling rate*) | part des déchets traités qui est recyclée (à vérifier) | % | haut | 42,9 (2024) |
| 13_1 | Niveau d'études des jeunes adultes (*Educational attainment among young adults*) | part des 25-34 ans diplômés au moins du 2nd cycle du secondaire | % | haut | 89,4 (2024) |
| 13_2 | Taux de sous-utilisation de la main-d'œuvre (*Labour underutilisation rate*) | chômeurs, découragés et sous-employés en % de la population active élargie | % | bas | 14,1 (2025) |
| 13_3 | Mortalité prématurée (*Premature mortality*) | années potentielles de vie perdues | années pour 100 000 | bas | 4 125 (2022) |
| 13_4 | Prévalence du tabagisme (*Smoking prevalence*) | fumeurs quotidiens, 15 ans et plus | % | bas | 23,1 (2023) |
| 13_5 | Prévalence de l'obésité (*Obesity prevalence*) | 15 ans et plus (mesurée ou déclarée, à vérifier) | % | bas | 14,4 (2019) |
| 14_1 | Confiance dans les autres (*Trust in others*) | note moyenne 0-10 | note | haut | 4,0 (2025) |
| 14_2 | Confiance dans la police (*Trust in the police*) | note moyenne 0-10 | note | haut | 5,6 (2013) |
| 14_3 | Confiance dans le gouvernement (*Trust in government*) | part des 15 ans et plus ayant confiance | % | haut | 37,3 (2025) |
| 14_4 | Implication des parties prenantes (*Government stakeholder engagement*) | indice composite d'association des parties prenantes à l'élaboration des réglementations | indice 0-4 | haut | 1,97 (2024) |
| 14_5 | Parité en politique (*Gender parity in politics*) | part des femmes parmi les parlementaires | % | haut | 36,2 (2026) |
| 14_6 | Corruption (*Corruption*) | indice de perception de la corruption (Transparency International, à vérifier) ; 100 = très intègre | indice 0-100 | haut | 66 (2025) |
| 14_7 | Bénévolat dans des organisations (*Volunteering through organisations*) | part des 15 ans et plus | % | haut | 31,0 (2025) |
| 15_1 | Actifs fixes produits (*Produced fixed assets*) | stock net par habitant | $ PPA/hab. | haut | 189 920 (2024) |
| 15_2 | Actifs de propriété intellectuelle (*Intellectual property assets*) | stock net par habitant | $ PPA/hab. | haut | 8 913 (2024) |
| 15_3 | Formation brute de capital fixe (*Gross fixed capital formation*) | unité « PC » renvoyée par l'API (croissance en %, à vérifier) | % | haut | 0,48 (2025) |
| 15_4 | Investissement en R&D (*Investment in R&D*) | en % du PIB (concept comptable, distinct de la DIRD, à vérifier) | % du PIB | haut | 1,77 (2024) |
| 15_5 | Valeur financière nette de l'économie (*Total economy net financial worth*) | | $ PPA/hab. | haut | −1 225 (2025) |
| 15_6 | Dette des ménages (*Households and NPISHs debt*) | en % du revenu disponible net | % | bas | 115,2 (2024) |
| 15_7 | Valeur financière nette des administrations publiques (*General government net financial worth*) | | % du PIB | haut | −73,4 (2025) |
| 15_8 | Levier des institutions financières monétaires (*Monetary financial institutions leverage*) | | ratio | bas | 18,1 (2025) |

### 3.4 Better Life Index (rappel, à vérifier)

Le BLI est la version interactive grand public du cadre : **11 thèmes** du bien-être actuel (sans les capitaux) et environ **24 indicateurs**, dont quelques-uns absents de la codelist ci-dessus : logements sans équipements sanitaires de base, nombre de pièces par personne, dépenses de logement, durée prévisible de scolarité (*years in education*), qualité de l'eau (satisfaction), patrimoine financier net des ménages. Calcul : normalisation min-max sur les pays de l'OCDE, moyenne simple des indicateurs dans un thème (0-10), puis **pondération des thèmes choisie par l'utilisateur** sur le site (poids 0 à 5). Les réponses des utilisateurs du BLI sont collectées et publiées par l'OCDE — précédent direct de la finalité 2 de l'observatoire (indicateur intersubjectif). Composition et méthode **à vérifier** (site non lisible par l'outil).

### 3.5 Principe d'agrégation

- *How's Life?* : **tableau de bord sans indice composite** ; évaluation par le sens de la variation de chaque indicateur (amélioration / stabilité / détérioration) et par la position relative du pays (tiers de l'OCDE).
- BLI : indice composite à pondération choisie par l'utilisateur (voir 3.4).
- Distinction stricte **bien-être actuel / ressources pour le futur** (capitaux), héritée de SSF.

### 3.6 Remarques sur la pertinence pour la France

- Cadre le plus complet et le plus proche de v0 ; séries France disponibles pour la plupart des indicateurs, mais **certaines sont anciennes** (enquêtes emploi du temps 2009, *job strain* 2015, insécurité du marché du travail 2016, PIAAC dispersion 2012) ou **propriétaires** (Gallup : soutien social, sentiment de sécurité, affects, confiance dans le gouvernement).
- Découpages différents de v0 : **équilibre vie pro/perso** est une dimension à part (v0 : dans `liens_bien_etre`) ; **engagement civique** est restreint (participation, avoir son mot à dire) et la **confiance institutionnelle et la corruption** sont classées en capital social ; le **bien-être subjectif** est une dimension à part entière ; la **sécurité** ne comprend pas la sécurité économique (rangée en revenu et patrimoine : insécurité financière, difficultés à joindre les deux bouts) ; l'**accès à internet** est rangé dans le logement ; la **dette** et l'**investissement** relèvent du capital économique (ressources futures) et non du niveau de vie.
- Les **inégalités** ne forment pas une dimension : elles sont mesurées dans chaque dimension (`_VER`, écarts entre groupes).
- Le capital naturel apporte des indicateurs nationaux directement exploitables pour `planete` (empreinte carbone, empreinte matières, excédent d'azote, stress hydrique, aires protégées, liste rouge, recyclage).

---

## 4. Eurostat — cadre « Quality of life » (8 + 1)

### 4.1 Références et accès

- Eurostat (2017), *Final report of the expert group on quality of life indicators*, Statistical reports, KS-FT-17-004 (https://ec.europa.eu/eurostat/documents/7870049/7960327/KS-FT-17-004-EN-N.pdf). Groupe d'experts créé après le rapport du *Sponsorship Group on Measuring Progress* (novembre 2011) ; experts de 10 instituts nationaux, scientifiques, OCDE, Eurofound ; réunions 2012-2016. **Lu jusqu'à la p. 46 environ** (texte tronqué par l'outil au début de la dimension santé) : pour les dimensions 3 à 9, les indicateurs proviennent de la vue d'ensemble et du tableau des indicateurs phares du rapport, les pages détaillées n'ont pas été lues.
- Statistics Explained, *Quality of life indicators – measuring quality of life* (présentation des 8+1 dimensions) et articles par dimension (conditions de vie matérielles 2023-2024 ; activité productive, données 2012 ; sécurité économique et physique, données 2016 ; gouvernance et droits fondamentaux 2024 ; environnement naturel et cadre de vie 2025 ; expérience globale de la vie 2024). **Non lus** : articles santé et éducation (erreur de l'outil), loisirs et interactions sociales (refus HTTP 429).
- **Codes de jeux de données** : la base Eurostat « Quality of life » est organisée en neuf dossiers `qol_mlc`, `qol_act`, `qol_hlt`, `qol_edu`, `qol_lei`, `qol_saf`, `qol_gov`, `qol_env`, `qol_lif` (cités dans Statistics Explained) qui regroupent des tables d'autres domaines (`ilc_*`, `lfsa_*`, `hlth_*`, `edat_*`…). L'arborescence de la base n'a pas pu être lue (arbre de navigation vide, sommaire de l'API tronqué). Les codes sont marqués **« vérifié »** quand ils sont cités dans un article Statistics Explained ou confirmés par l'API Eurostat (`ilc_di11`, `ilc_pw01b`, `ilc_pw03`), sinon **« à vérifier »** (à confirmer par la mission M02).

### 4.2 Dimensions

| N° | Dimension | Sous-dimensions | Indicateur(s) phare(s) (rapport 2017) |
|---|---|---|---|
| 1 | Conditions de vie matérielles (*Material living conditions*) | revenu ; consommation ; conditions matérielles (privation, logement) | revenu équivalent médian ; S80/S20 ; privation matérielle grave |
| 2 | Activité productive ou principale (*Productive or main activity*) | quantité d'emploi ; qualité de l'emploi ; autre activité principale (inactivité, travail non rémunéré) | taux d'emploi ; satisfaction au travail |
| 3 | Santé (*Health*) | état de santé ; déterminants ; accès aux soins | espérance de vie ; santé perçue |
| 4 | Éducation (*Education*) | compétences ; formation tout au long de la vie ; possibilités d'éducation | diplômés du supérieur |
| 5 | Loisirs et interactions sociales (*Leisure and social interactions*) | loisirs ; interactions sociales | satisfaction de l'emploi du temps ; avoir quelqu'un sur qui compter |
| 6 | Sécurité économique et physique (*Economic security and physical safety*) | sécurité économique ; sécurité physique | dépense imprévue ; homicides ; criminalité perçue dans le quartier |
| 7 | Gouvernance et droits fondamentaux (*Governance and basic rights*) | institutions et services publics ; discriminations et égalité des chances ; citoyenneté active | confiance dans le système judiciaire |
| 8 | Environnement naturel et cadre de vie (*Natural and living environment*) | pollution (dont bruit) ; accès aux espaces verts ; paysage et cadre bâti | exposition urbaine aux particules ; pollution perçue |
| +1 | Expérience globale de la vie (*Overall experience of life*) | satisfaction dans la vie ; affects ; eudémonie (sens) | satisfaction dans la vie |

### 4.3 Indicateurs

Le détail (94 indicateurs, avec sous-dimension, définition, unité, sens, code de table et statut de vérification du code) est dans le CSV (`cadre = Eurostat Quality of life`). Synthèse :

- **Dimension 1** (13) : revenu médian, S80/S20, risque de pauvreté (60 %), pauvreté ancrée 2008, satisfaction financière, consommation individuelle effective, part des dépenses de base, privation matérielle grave, capacité à joindre les deux bouts, problèmes du logement, surpeuplement, sous-occupation, satisfaction du logement.
- **Dimension 2** (24) : emploi, chômage, chômage de longue durée, très faible intensité de travail, temps partiel subi, bas salaires, contrats temporaires (et subis), surqualification (mesurée et déclarée), accidents du travail mortels et déclarés, problèmes de santé liés au travail, expositions physiques et psychosociales, durée du travail, longues durées (> 48 h), horaires atypiques, flexibilité, satisfaction du temps de trajet, satisfaction au travail, autonomie (à développer), inactivité par raison, travail non rémunéré (à développer).
- **Dimension 3** (11) : espérance de vie, années de vie en bonne santé, santé perçue, maladies chroniques et limitations, santé mentale, IMC, tabac, alcool, activité physique, fruits et légumes, besoins de soins non satisfaits.
- **Dimension 4** (8) : diplômés du supérieur, sorties précoces, compétences numériques, langues étrangères (deux indicateurs), littératie PIAAC, formation des adultes, scolarisation à 4 ans.
- **Dimension 5** (12) : non-participation culturelle ou sportive, satisfaction de l'emploi du temps, qualité des loisirs (à développer), obstacles financiers aux loisirs, rencontres entre amis, satisfaction des relations, bénévolat formel et informel, aide d'autrui, confident, confiance dans les autres, inclusion sociale perçue (à développer).
- **Dimension 6** (6) : dépense imprévue, arriérés, transitions emploi-chômage, homicides, criminalité perçue, sentiment de sécurité la nuit.
- **Dimension 7** (11) : confiance dans la justice, le système politique, la police ; satisfaction des services publics (à développer) ; discriminations (à développer) ; écarts d'emploi et de salaire femmes-hommes ; écart d'emploi nationaux / pays tiers ; citoyenneté active ; participation électorale ; voix et responsabilité (à développer).
- **Dimension 8** (5) : exposition urbaine aux particules, pollution perçue, bruit, satisfaction des espaces verts, satisfaction du cadre de vie.
- **Dimension +1** (4) : satisfaction dans la vie, affects négatifs, affects positifs, sens de la vie.

Aucun seuil normatif dans le cadre ; seuls existent des seuils de définition (60 % du revenu médian, 4 privations sur 9, intensité de travail ≤ 0,20, 2/3 du salaire médian, 48 heures).

### 4.4 Principe d'agrégation

- **Tableau de bord** de quelques indicateurs phares par dimension, complété par des indicateurs secondaires peu corrélés ; **pas d'indice composite**. Le rapport note que des indicateurs synthétiques pourraient être construits pour des variables très corrélées, et que tirer les indicateurs phares d'une même source (EU-SILC) faciliterait une agrégation ultérieure.
- Critères de sélection (p. 8-9) : pertinence, exactitude, actualité, comparabilité, clarté ; mélange d'indicateurs objectifs et subjectifs ; lien avec le bien-être ; interprétation univoque ; sensibilité aux politiques ; cohérence avec Europe 2020 et les ODD ; ventilations par sous-population ; continuité de la collecte.

### 4.5 Remarques sur la pertinence pour la France

- Données harmonisées EU-SILC / EFT, mêmes enquêtes que l'INSEE (SRCV, enquête Emploi) : priorité INSEE selon la charte, Eurostat utile pour les comparaisons de bornes.
- Beaucoup d'indicateurs subjectifs proviennent de **modules ad hoc** (2013, 2018, 2022) : trois points seulement, sous le critère de 10 points de la charte. Exception : la satisfaction dans la vie (`ilc_pw01`) et la confiance dans les autres (`ilc_pw03`), devenues plus fréquentes (à confirmer en M02).
- Découpages différents de v0 : la **satisfaction globale** est une dimension « +1 » distincte ; la **sécurité économique** (dépense imprévue, arriérés) est réunie avec la **sécurité physique**, comme dans v0 ; la **confiance interpersonnelle** relève des interactions sociales (v0 : sécurité et confiance) ; les **inégalités femmes-hommes et selon la nationalité** relèvent de la gouvernance et des droits fondamentaux (v0 : égalités) ; le **temps de trajet** relève de l'activité principale (v0 : cadre de vie). **Pas de dimension planétaire** : l'environnement est limité au cadre de vie (pollution locale, bruit, espaces verts) ; la soutenabilité est suivie par le jeu d'indicateurs ODD de l'UE.

---

## 5. INSEE — Les nouveaux indicateurs de richesse (NIR, loi du 13 avril 2015)

### 5.1 Références et accès

- Loi **n° 2015-411 du 13 avril 2015** (référence confirmée sur la page INSEE ; intitulé non affiché) : le Gouvernement remet chaque année au Parlement un rapport sur l'évolution de nouveaux indicateurs de richesse.
- INSEE, *Les nouveaux indicateurs de richesse — Indicateurs statistiques — Chiffres détaillés*, **édition 2025**, 28 pages, avec les services statistiques ministériels (enseignement supérieur-recherche, santé-affaires sociales, éducation nationale, environnement) : https://www.insee.fr/fr/statistiques/fichier/3281778/NIR2025.pdf — **lu en entier**.
- Page « Indicateurs de richesse nationale » (https://www.insee.fr/fr/statistiques/3281778, parue le 17/07/2026) : seul le PDF est proposé, **aucun fichier XLSX/CSV ni identifiant de série (idbank)** n'y figure — les séries devront être retrouvées en M01 dans les sources sous-jacentes (BDM, Melodi, SDES, Agreste).

### 5.2 Dimensions

Trois domaines (page INSEE et rapport p. 3) — le rapport isole la satisfaction dans la vie comme indicateur « psychologique » :

| Domaine | Indicateurs |
|---|---|
| Économique | 1. Taux d'emploi ; 2. Effort de recherche ; 3. Endettement |
| Social (dont psychologique) | 4. Espérance de vie sans incapacité ; 5. Satisfaction dans la vie ; 6. Inégalités de revenus ; 7. Privation matérielle et sociale ; 8. Sorties précoces du système scolaire |
| Environnemental | 9. Empreinte carbone ; 10. Artificialisation des sols |

### 5.3 Indicateurs (rapport NIR 2025)

| N° | Indicateur (libellé du rapport ; libellé de la page web) | Définition | Unité | Sens | Dernière valeur France | Depuis | Source | Cible ou référence citée (page) |
|---|---|---|---|---|---|---|---|---|
| 1 | Taux d'emploi des 15-64 ans | part des personnes en emploi parmi les 15-64 ans | % | haut | 68,8 % (2024) | 1975 | INSEE, enquête Emploi | ODD 8, cible 8.5 (p. 6), sans valeur chiffrée |
| 2 | Effort de recherche (DIRD/PIB) | dépense intérieure de R&D rapportée au PIB | % du PIB | haut | 2,18 % (2023, estimation 2024 identique) | 2003 | MESRE-SIES ; OCDE pour l'UE | ODD 9.5 ; **objectif européen de 3 % du PIB (horizon 2020)** (p. 8-9) |
| 3 | Endettement (dette publique et privée) | dette des administrations publiques (Maastricht), des sociétés non financières et des ménages, rapportée au PIB | % du PIB | bas | APU 112,6 % ; SNF 90,7 % ; ménages 59,6 % (fin 2024) | 2014 (figure) | Eurostat ; INSEE comptes nationaux base 2020 | **critère de Maastricht : 60 % du PIB pour la dette publique** ; ODD 17.13 (p. 10) |
| 4 | Espérance de vie sans incapacité (« espérance de vie en bonne santé ») | années à vivre sans incapacité dans les gestes de la vie quotidienne (déclaratif) | années | haut | 63,7 ans (hommes), 64,1 ans (femmes) (2024) | 2008 | INSEE SRCV ; calculs DREES (méthode EHEMU) ; Eurostat | ODD 3, sans cible chiffrée (p. 12) |
| 5 | Satisfaction dans la vie (« satisfaction globale dans la vie ») | note de 0 à 10 de satisfaction à l'égard de sa vie actuelle | note | haut | 7,2 (début 2024, France métropolitaine) | 2010 | INSEE SRCV ; Eurostat EU-SILC | ODD 3.4 (p. 15), sans cible chiffrée |
| 6 | Inégalités de revenus (« dispersion des revenus ») | rapport des niveaux de vie des 20 % les plus aisés et des 20 % les plus modestes après redistribution (S80/S20) | ratio | bas | 4,5 (2023, France métropolitaine) | 1996 | INSEE-DGFiP-Cnaf-Cnav-CCMSA, ERFS ; EU-SILC | ODD 10.4 (p. 17), sans cible chiffrée |
| 7 | Privation matérielle et sociale (« taux de pauvreté en conditions de vie ») | part des personnes cumulant au moins 5 privations ou difficultés sur 13 | % population | bas | 12,7 % (début 2024, France métropolitaine) | 2013 | INSEE SRCV ; EU-SILC | **ODD 1.2 : réduire au moins de moitié la pauvreté sous toutes ses formes** (p. 19) |
| 8 | Sorties précoces du système scolaire | part des 18-24 ans hors études et formation sans diplôme de niveau CAP, BEP ou supérieur | % des 18-24 ans | bas | 7,9 % (2024) | 2003 | INSEE enquêtes Emploi ; DEPP | ODD 4.4 ; **objectif UE de 9 % en 2030** ; **cible française de 9,5 %** (stratégie de Lisbonne) (p. 22) |
| 9 | Empreinte carbone | émissions de GES induites par la demande finale intérieure, importations comprises | Mt CO2 éq. ; t CO2 éq./hab. | bas | 563 Mt CO2 éq., 8,2 t/hab. (2024) | 1990 | INSEE et SDES ; Eurostat, Citepa, Douanes, OCDE | ODD 13.2 (p. 24), sans cible chiffrée dans le rapport (cible SNBC 3 : voir section 6) |
| 10 | Artificialisation des sols | part du territoire occupée par des sols artificialisés | % du territoire | bas | 9,5 % du territoire métropolitain (2023) | 1983 | Agreste, enquête Teruti ; Eurostat LUCAS | ODD 11.3 (p. 27), sans cible chiffrée dans le rapport (objectif ZAN : voir section 6) |

Indicateurs **complémentaires** présentés dans le rapport : espérance de vie à la naissance (p. 12-13) ; taux de pauvreté monétaire à 60 % du niveau de vie médian (p. 19) ; rapport interquintile avant redistribution (p. 17) ; composantes de la DIRD (DIRDE entreprises, DIRDA administrations, p. 8) ; endettement des SNF et des ménages (p. 10, déjà inclus dans l'indicateur 3) ; émissions des unités résidentes hors importations (p. 24-25).

Le rapport ne mentionne **ni la SNBC, ni l'objectif de zéro artificialisation nette** (constat de lecture) : les cibles nationales correspondantes sont relevées en section 6.

### 5.4 Principe d'agrégation

**Tableau de bord** de dix indicateurs, sans indice composite ni pondération ; évolutions commentées indicateur par indicateur et comparaisons européennes.

### 5.5 Remarques sur la pertinence pour la France

- Seul cadre **officiel français** ; indicateurs tous disponibles en séries annuelles longues (sauf satisfaction dans la vie depuis 2010 et privation matérielle et sociale depuis 2013), donc candidats naturels au socle de l'observatoire.
- Couverture partielle de v0 : **aucun indicateur** pour `logement_cadre_vie`, `liens_bien_etre` (hors satisfaction globale), `securite_confiance` et `democratie`.
- Deux indicateurs sont des **moyens** ou des **stocks** plutôt que des résultats au sens de la charte (§3.4) : effort de recherche (moyen) et endettement (soutenabilité économique) — à arbitrer en phase 2 (Q-B : innovation, soutenabilité économique).
- Libellés différents entre la page web et le rapport (indicateurs 4, 6, 7) : retenir les définitions du rapport.

---

## 6. ODD et objectifs officiels chiffrés (France, UE)

### 6.1 Références et accès

- **ODD** : résolution A/RES/70/1 (2015) et cadre mondial d'indicateurs (A/RES/71/313, version après la revue de 2025) — PDF *Global indicator framework* lu sur unstats.un.org (libellés des cibles et des indicateurs vérifiés).
- **Climat et énergie** : décret **n° 2026-636 du 16 juillet 2026** relatif aux budgets carbone nationaux et à la SNBC (JO n° 166 du 18 juillet 2026, lu via la base AIDA de l'Ineris) ; **résumé de la SNBC 3** (ministère de la Transition écologique, juillet 2026, PDF lu) ; article L100-4 du code de l'énergie (Légifrance et ecologie.gouv.fr inaccessibles à l'outil : contenu repris du **rapport du Sénat n° 657 (2018-2019)** sur la loi énergie-climat — texte en vigueur **à vérifier**) ; PPE 3 (décret de février 2026, JORFTEXT000053464980, d'après *Techniques de l'ingénieur*, 18/02/2026).
- **Sols** : loi n° 2021-1104 (Climat et résilience), art. 191, modifiée par la loi n° 2023-630 ; état de la proposition de loi TRACE d'après *Weka* (11/12/2025) — **statut au 13/10/2026 à vérifier**.
- **Biodiversité** : art. L110-4 du code de l'environnement, décret n° 2022-527 (d'après Landot avocats, 20/11/2024) ; Ecophyto 2030 (d'après L'Info durable, 03/05/2024).
- **Social et éducation (UE)** : Conseil de l'UE, doc. 9519/22 REV 1 (objectifs 2030 du socle européen des droits sociaux) et **doc. 15277/25 ADD 1** (27/11/2025, annexes du rapport conjoint sur l'emploi 2026 : **objectifs nationaux de la France**) ; résolution du Conseil **2021/C 66/01** (espace européen de l'éducation, annexe II, lue sur EUR-Lex).
- Les objectifs non confirmés sur une source primaire ou secondaire fiable pendant la mission sont marqués **« à vérifier »** (loi européenne sur le climat, RED III, directive déchets, loi AGEC, lois Copé-Zimmermann et Rixain, sécurité routière UE, valeurs de la directive qualité de l'air et de l'OMS).

### 6.2 Cibles ODD chiffrées utiles au socle des bornes

| Cible | Contenu chiffré | Échéance | Rattachement v0 |
|---|---|---|---|
| 1.1 | éliminer l'extrême pauvreté (< 1,25 $/jour) | 2030 | niveau_de_vie (non pertinent France) |
| 1.2 | réduire **au moins de moitié** la pauvreté sous toutes ses formes (définitions nationales) | 2030 | niveau_de_vie |
| 2.1 | éliminer la faim | 2030 | sante (alimentation, Q-B) |
| 3.1 | mortalité maternelle **< 70 / 100 000** naissances vivantes | 2030 | sante |
| 3.2 | mortalité néonatale **≤ 12 ‰** ; moins de 5 ans **≤ 25 ‰** | 2030 | sante |
| 3.4 | mortalité prématurée par maladies non transmissibles **−1/3** | 2030 | sante |
| 3.6 | décès et blessés de la route **÷ 2** | 2020 (dépassée) | securite_confiance |
| 4.1 | achèvement du secondaire pour tous (100 %) | 2030 | education |
| 6.1 / 6.2 / 7.1 | accès universel (100 %) à l'eau, à l'assainissement, à l'énergie | 2030 | logement_cadre_vie |
| 7.3 | **doubler** le rythme d'amélioration de l'efficacité énergétique | 2030 | planete |
| 10.1 | croissance des revenus des 40 % les plus modestes **> moyenne nationale** | 2030 | egalites |
| 12.3 | gaspillage alimentaire par habitant **÷ 2** | 2030 | planete |
| 14.5 | au moins **10 %** des zones marines protégées | 2020 (dépassée) | planete |

Cibles sans valeur chiffrée (non retenues comme bornes) : 3.9, 4.2, 5.5, 6.4, 7.2, 8.5, 8.6, 11.1, 11.2, 11.6, 12.5, 16.1, 16.5.

### 6.3 Objectifs officiels France et UE

| Domaine | Objectif | Valeur et échéance | Référence | Statut |
|---|---|---|---|---|
| Climat | émissions brutes de GES | **−50 % en 2030 / 1990** | SNBC 3 (résumé juillet 2026, p. 2) | vérifié |
| Climat | neutralité carbone | **2050** | art. L100-4 C. énergie ; SNBC 3 | vérifié (rapport Sénat, SNBC 3) |
| Climat | budgets carbone (hors puits) | **342 / 262 / 194 Mt CO2 éq./an** (2024-28 / 2029-33 / 2034-38) | décret n° 2026-636 | vérifié |
| Climat | empreinte carbone (indicatif) | 516-531 / 408-446 / 312-358 Mt CO2 éq./an ; **2050 : 2,3 t/hab.** (1,5 °C) ou 3,1 t/hab. (2 °C) | décret n° 2026-636 ; SNBC 3 p. 22 | vérifié |
| Climat | puits UTCATF (indicatif) | −46 / −33 / −31 Mt CO2 éq./an | décret n° 2026-636 | vérifié |
| Climat (UE) | émissions nettes de l'UE | −55 % en 2030 / 1990 ; neutralité 2050 | règlement (UE) 2021/1119 | à vérifier |
| Énergie | consommation finale | **−20 % en 2030, −50 % en 2050 / 2012** | art. L100-4, I, 2° | à vérifier (rapport Sénat ; PPE 3 pour 2050) |
| Énergie | énergies fossiles primaires | **−40 % en 2030** (base 2012 à vérifier) | art. L100-4, I, 3° | à vérifier (rapport Sénat) |
| Énergie | renouvelables / consommation finale brute | **33 % en 2030** | art. L100-4, I, 4° | à vérifier (rapport Sénat) |
| Agriculture | engrais azotés minéraux | **−30 % en 2030**, −54 % en 2050 / 2020 | SNBC 3 p. 10 | vérifié |
| Agriculture | agriculture biologique | **≈ 21 % de la SAU en 2030** | SNBC 3 p. 10 | vérifié |
| Agriculture | produits phytopharmaceutiques (HRI1) | **−50 % en 2030 / 2011-2013** | Ecophyto 2030 | vérifié (source secondaire) |
| Déchets | déchets ménagers et assimilés | **−15 % en 2030 / 2010** | SNBC 3 p. 17-18 (loi AGEC) | vérifié (SNBC 3) |
| Déchets (UE) | recyclage des déchets municipaux | 55 % 2025, 60 % 2030, 65 % 2035 | directive (UE) 2018/851 | à vérifier |
| Déchets | gaspillage alimentaire | −50 % en 2025 / 2030 selon secteurs (base 2015) | loi AGEC | à vérifier |
| Sols | zéro artificialisation nette | **2050** | loi n° 2021-1104, art. 191 | vérifié (en vigueur ; réforme en cours) |
| Sols | consommation d'ENAF | **−50 % sur 2021-2031 / 2011-2021** | loi n° 2021-1104, art. 191 | **contesté** (PPL TRACE) — statut à vérifier |
| Biodiversité | aires protégées | **≥ 30 %** du territoire et des eaux, dont **≥ 10 % en protection forte** | art. L110-4 C. env. ; décret 2022-527 | vérifié (source secondaire) |
| Biodiversité | haies | **+50 000 km nets en 2030** | SNBC 3 p. 10, 20 | vérifié |
| Logement | passoires énergétiques | éradication en 2035-2040 | SNBC 3 p. 13-14 | vérifié |
| Air (UE) | PM2,5 moyenne annuelle | 10 µg/m³ en 2030 | directive (UE) 2024/2881 | à vérifier (valeur finale) |
| Air (OMS) | valeur guide PM2,5 | 5 µg/m³ | OMS 2021 | à vérifier |
| Emploi | taux d'emploi 20-64 ans | **France 78,0 % en 2030** (UE ≥ 78 %) | Conseil UE 15277/25 ADD 1 | vérifié |
| Emploi (UE) | NEET 15-29 ans | **≤ 9 % en 2030** | Conseil UE 9519/22 | vérifié |
| Emploi (UE) | écart d'emploi femmes-hommes | **÷ 2 en 2030 / 2019** | Conseil UE 9519/22 | vérifié |
| Compétences | formation des adultes (12 mois) | **France 65,0 % en 2030** (UE ≥ 60 %) | Conseil UE 15277/25 ADD 1 | vérifié |
| Compétences (UE) | compétences numériques de base | **≥ 80 % des 16-74 ans en 2030** | Conseil UE 9519/22 | vérifié |
| Pauvreté | AROPE | **France −1,1 million de personnes en 2030 / 2019** (UE −15 M) | Conseil UE 15277/25 ADD 1 | vérifié |
| Éducation (UE) | faibles performeurs 15 ans | < 15 % en 2030 | résolution 2021/C 66/01 | vérifié |
| Éducation (UE) | faibles compétences numériques 8e année | < 15 % en 2030 | résolution 2021/C 66/01 | vérifié |
| Éducation (UE) | éducation et accueil des jeunes enfants | ≥ 96 % en 2030 | résolution 2021/C 66/01 | vérifié |
| Éducation | sorties précoces | **< 9 % en 2030 (UE)** ; 9,5 % (cible française de Lisbonne) | résolution 2021/C 66/01 ; NIR 2025 p. 22 | vérifié |
| Éducation (UE) | diplômés du supérieur 25-34 ans | ≥ 45 % en 2030 | résolution 2021/C 66/01 | vérifié |
| Éducation (UE) | formation par le travail (EFP) ; apprentissage des adultes | ≥ 60 % (2025) ; ≥ 47 % (2025) | résolution 2021/C 66/01 | vérifié |
| Recherche | DIRD/PIB | 3 % (UE, horizon 2020) | NIR 2025 p. 8-9 | vérifié |
| Finances publiques | dette publique / déficit | 60 % du PIB / 3 % du PIB | NIR 2025 p. 10 (dette) ; protocole n° 12 TFUE (déficit) | dette vérifiée ; déficit à vérifier |
| Égalité | femmes dans les conseils d'administration | 40 % | loi n° 2011-103 | à vérifier |
| Égalité | femmes cadres dirigeants | 30 % en 2026, 40 % en 2029 | loi n° 2021-1774 | à vérifier |
| Sécurité routière (UE) | tués et blessés graves | −50 % entre 2020 et 2030 | cadre UE 2021-2030 | à vérifier |

### 6.4 Principe d'agrégation

Sans objet : ces cibles servent de **bornes** (seuil minimal ou objectif) au sens de la charte §3.3, au premier rang de la hiérarchie de justification (« objectif légal ou officiel France/UE »).

### 6.5 Remarques sur la pertinence pour la France

- Les dimensions **`planete`**, **`education`** et **`travail`** disposent d'objectifs officiels chiffrés nombreux ; **`liens_bien_etre`**, **`securite_confiance`** (hors routes) et **`democratie`** n'en ont **aucun** : leurs bornes devront venir de l'historique, des comparaisons européennes ou du dire d'expert.
- Plusieurs cibles ODD sont **déjà atteintes** par la France (mortalité infantile, accès à l'eau et à l'énergie, sorties précoces sous 9 %) : utiles comme seuil minimal, pas comme objectif.
- Plusieurs objectifs sont des **moyens** (part d'ENR, agriculture biologique, haies, R&D, déficit) ou des **trajectoires** (budgets carbone) : leur conversion en bornes d'indicateurs de résultat est un choix méthodologique de phase 4.
- Les objectifs sont **datés et révisables** (SNBC 3 de juillet 2026 remplaçant L100-4 pour 2030 ; ZAN en cours de réforme) : le socle de bornes devra enregistrer la date et la version du texte de référence.
