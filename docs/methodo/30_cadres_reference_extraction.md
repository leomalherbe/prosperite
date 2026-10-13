# Extraction des cadres de référence (mission M03, tâche T1)

Version de travail — 13 octobre 2026 — agent M03 (phase 1). Document de méthodologie, sans valeur de décision : la grille v1 sera proposée en phase 2 (T3) et tranchée par la session mère.

## Mode d'emploi

- Une section par cadre, même structure : **références et accès** ; **dimensions** ; **indicateurs par dimension** (libellé, définition courte, unité, sens, seuil minimal ou cible, source de données citée) ; **principe d'agrégation** ; **remarques sur la pertinence pour la France**.
- Libellés traduits en français, libellé original anglais entre parenthèses quand il est utile.
- Sens : `haut` = plus c'est élevé, mieux c'est ; `bas` = l'inverse (convention de la charte §5.1).
- Les mentions **« à vérifier »** signalent une information plausible mais non confirmée sur la source primaire au moment de la rédaction ; **« non trouvé »** signale une information cherchée et non trouvée. Aucun seuil n'est reconstitué de mémoire sans cette mention.
- Le détail ligne à ligne (avec le rattachement à la grille v0) est dans `30_indicateurs_cadres_reference.csv` ; la matrice de synthèse est dans `30_crosswalk_synthese.md`.

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
