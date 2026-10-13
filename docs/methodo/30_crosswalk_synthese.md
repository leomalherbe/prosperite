# Crosswalk des cadres de référence vers la grille v0 — synthèse (mission M03, tâche T2)

Version de travail — 13 octobre 2026 — agent M03 (phase 1). Constats factuels uniquement : **aucune proposition de grille v1 ici** (elle relève de la phase 2, tâche T3).

Fichiers associés : `30_indicateurs_cadres_reference.csv` (344 lignes, une par indicateur de cadre) et `30_cadres_reference_extraction.md` (extraction détaillée et sources).

## 1. Méthode et conventions

- **Une ligne = un indicateur tel que le cadre le définit.** Chaque ligne est rattachée à **une seule** dimension de la grille v0 (`indicateurs/dimensions.yaml`), celle dont le *contenu indicatif* est le plus proche ; quand deux rattachements sont plausibles, l'alternative est notée dans la colonne `commentaire` (mots « alternative » ou « arbitrage … (Q-B) »). « non rattachable » = aucune dimension v0 ne convient.
- **Les comptes de la matrice sont des nombres de lignes, pas de concepts distincts.** Ils dépendent de la granularité de chaque cadre : l'OCDE publie des variantes distributionnelles (`_DEP` privations, `_VER` inégalités verticales) qui comptent chacune pour une ligne ; le rapport Stiglitz-Sen-Fitoussi (SSF) cite des familles de mesures plutôt que des indicateurs ; ODD et objectifs officiels ne comptent que les **cibles chiffrées**.
- `disponibilite_france_estimee` : **oui** = série France existante pour ce concept (même définition ou équivalent national direct) ; **probable** = existe vraisemblablement, ou seulement sous une forme adaptée (proxy national), ou avec une profondeur insuffisante pour la charte, à confirmer en M01/M02/M04 ; **non** = pas de série France pertinente (enquête unique ou ponctuelle, indicateur « à développer », variable mondiale sans équivalent) ; **inconnue** = non évalué (aucune ligne).
- « Déclaratif » : repéré par la mention « Déclaratif » dans le commentaire (charte §3.1).
- Cadres en colonnes : Doughnut 3.0 ; SSF 2009 ; OCDE *How's Life? 2024* (HL) ; OCDE Better Life Index (BLI, 4 indicateurs propres seulement) ; Eurostat Quality of life (QoL) ; INSEE NIR 2025 (10 indicateurs + 5 complémentaires) ; ODD (cibles chiffrées) ; objectifs officiels France-UE.

## 2. Matrice cadres × dimensions v0 (nombre de lignes)

| Dimension v0 | Doughnut | SSF | OCDE HL | OCDE BLI | Eurostat QoL | INSEE NIR | ODD | Obj. FR-UE | Total |
|---|---|---|---|---|---|---|---|---|---|
| `niveau_de_vie` | 2 | 6 | 11 | **0** | 9 | 5 | 2 | 4 | 39 |
| `travail` | 1 | 4 | 11 | **0** | 22 | 1 | **0** | 2 | 41 |
| `logement_cadre_vie` | 6 | 4 | 8 | 3 | 10 | **0** | 3 | 3 | 37 |
| `sante` | 3 | 3 | 8 | **0** | 11 | 2 | 5 | **0** | 32 |
| `education` | 3 | 3 | 9 | 1 | 9 | 1 | 1 | 9 | 36 |
| `liens_bien_etre` | 1 | 5 | 13 | **0** | 14 | 1 | **0** | **0** | 34 |
| `securite_confiance` | 1 | 2 | 5 | **0** | 7 | **0** | 1 | 1 | 17 |
| `democratie` | 2 | 2 | 6 | **0** | 7 | **0** | **0** | **0** | 17 |
| `egalites` | 3 | 6 | 13 | **0** | 5 | 2 | 1 | 3 | 33 |
| `planete` | 13 | 2 | 15 | **0** | **0** | 3 | 3 | 19 | 55 |
| `non rattachable` | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 3 |
| **Total** | **35** | **39** | **100** | **4** | **94** | **15** | **16** | **41** | **344** |

Lecture : le Doughnut rattache 13 indicateurs à `planete` (ses 13 indicateurs écologiques) ; Eurostat n'en rattache aucun (pas de dimension planétaire dans son cadre).

### 2.1 Répartition des dimensions de chaque cadre sur v0

Montre les **différences de découpage** : une dimension de cadre qui se répartit sur plusieurs dimensions v0 (ou l'inverse) signale une frontière tracée autrement.

**Doughnut 3.0** — Alimentation → `sante` 1, `niveau_de_vie` 1 ; Santé → `sante` 2 ; Éducation → `education` 2 ; Revenu et travail → `niveau_de_vie` 1, `travail` 1 ; Eau et assainissement → `logement_cadre_vie` 2 ; Énergie → `logement_cadre_vie` 2 ; Connectivité → `logement_cadre_vie` 1, `education` 1 ; Logement → `logement_cadre_vie` 1 ; Égalité → `egalites` 2 ; Cohésion sociale → `liens_bien_etre` 1, `egalites` 1 ; Voix politique → `democratie` 1 ; Paix et justice → `democratie` 1, `securite_confiance` 1 ; 9 dimensions écologiques → `planete` 13.

**SSF 2009** — Niveau de vie matériel → `niveau_de_vie` 6, non rattachable 1 ; Santé → `sante` 3, `egalites` 1 ; Éducation → `education` 2, `egalites` 1 ; **Activités personnelles dont travail → `travail` 4, `logement_cadre_vie` 3, `egalites` 2, `liens_bien_etre` 2, `education` 1** ; Voix politique → `democratie` 2 ; Liens sociaux → `liens_bien_etre` 1 ; Environnement (présent) → `logement_cadre_vie` 1 ; Environnement (soutenabilité) → `planete` 2 ; Insécurité → `securite_confiance` 2 ; Bien-être subjectif → `liens_bien_etre` 2 ; Inégalités → `egalites` 2 ; Soutenabilité → non rattachable 1.

**OCDE HL** — Revenu et patrimoine → `niveau_de_vie` 4, `egalites` 2, `securite_confiance` 1 ; Travail et qualité de l'emploi → `travail` 10, `egalites` 3 ; Logement → `logement_cadre_vie` 5 ; **Équilibre vie pro-vie privée → `liens_bien_etre` 4, `egalites` 2** ; Santé → `sante` 4 ; Connaissances et compétences → `education` 8, `egalites` 3 ; Liens sociaux → `liens_bien_etre` 5, `egalites` 1 ; Engagement civique → `democratie` 2 ; Qualité de l'environnement → `logement_cadre_vie` 3 ; Sécurité → `securite_confiance` 3 ; Bien-être subjectif → `liens_bien_etre` 3, `egalites` 1, `sante` 1 ; Capital naturel → `planete` 15 ; Capital humain → `sante` 3, `education` 1, `travail` 1 ; **Capital social → `democratie` 4, `securite_confiance` 1, `egalites` 1, `liens_bien_etre` 1** ; Capital économique → `niveau_de_vie` 7, non rattachable 1.

**Eurostat QoL** — Conditions de vie matérielles → `niveau_de_vie` 8, `logement_cadre_vie` 4, `egalites` 1 ; Activité productive → `travail` 22, `logement_cadre_vie` 1, `liens_bien_etre` 1 ; Santé → `sante` 11 ; Éducation → `education` 8 ; **Loisirs et interactions sociales → `liens_bien_etre` 9, `education` 1, `niveau_de_vie` 1, `securite_confiance` 1** ; Sécurité économique et physique → `securite_confiance` 6 ; **Gouvernance et droits fondamentaux → `democratie` 7, `egalites` 4** ; Environnement naturel et cadre de vie → `logement_cadre_vie` 5 ; Expérience globale de la vie → `liens_bien_etre` 4.

**INSEE NIR** — Économique → `niveau_de_vie` 2 (R&D, endettement), `travail` 1 ; Social → `sante` 1, `egalites` 1, `niveau_de_vie` 1, `education` 1 ; Social (psychologique) → `liens_bien_etre` 1 ; Environnemental → `planete` 2 (+ compléments).

## 3. Cases vides : dimensions v0 non couvertes

### 3.1 Par cadre

| Cadre | Dimensions v0 sans aucun indicateur | Remarque |
|---|---|---|
| Doughnut 3.0 | aucune | mais une seule ligne pour `travail` (NEET), `liens_bien_etre` (soutien social), `securite_confiance` (homicides) |
| SSF 2009 | aucune | couverture qualitative (familles de mesures) |
| OCDE HL | aucune | cadre le plus complet |
| Eurostat QoL | **`planete`** | choix de conception : environnement limité au cadre de vie |
| INSEE NIR | **`logement_cadre_vie`, `securite_confiance`, `democratie`** | `liens_bien_etre` couvert par la seule satisfaction dans la vie |
| ODD (cibles chiffrées) | **`travail`, `liens_bien_etre`, `democratie`** | les cibles correspondantes (8.5, 16.x) n'ont pas de valeur chiffrée |
| Objectifs officiels France-UE | **`sante`, `liens_bien_etre`, `democratie`** | aucun objectif national chiffré de santé relevé (hors ODD) |

### 3.2 Toutes sources confondues

**Aucune dimension v0 n'est vide.** Les deux dimensions les **moins couvertes** sont `securite_confiance` (17 lignes) et `democratie` (17 lignes) ; `democratie` cumule aussi la plus forte part de séries indisponibles (9 « non » sur 17).

### 3.3 Éléments du contenu indicatif de v0 couverts par aucun cadre, ou très faiblement

| Dimension v0 | Élément du contenu indicatif v0 | Couverture constatée |
|---|---|---|
| `niveau_de_vie` | PIB par habitant | **aucun cadre** ne le retient comme indicateur de bien-être (SSF recommande revenu et consommation des ménages ; Eurostat ne l'utilise qu'en contexte) |
| `niveau_de_vie` | investissement, dette | OCDE (capital économique = ressources futures), INSEE NIR (endettement) ; SSF les range dans la soutenabilité, pas le bien-être actuel |
| `egalites` | inégalités territoriales | **aucun cadre** (tous nationaux) |
| `egalites` | inégalités intergénérationnelles | **aucun cadre** (seulement des ventilations par âge) |
| `egalites` | mobilité sociale | **aucun cadre** |
| `democratie` | libertés (presse, expression, académique) | SSF seulement, sans indicateur chiffré (« médias libres ») |
| `democratie` | indépendance de la justice | Eurostat seulement, en déclaratif (confiance dans le système judiciaire, module 2013) |
| `securite_confiance` | violences (hors homicides) | SSF (victimation, pages non lues, à vérifier) ; aucun indicateur précis |
| `liens_bien_etre` | sens, affects | Eurostat (sens de la vie, affects), OCDE (solde d'affects), SSF — tous déclaratifs, séries courtes |
| `education` | pratiques culturelles | SSF, Eurostat (modules ponctuels) |
| `logement_cadre_vie` | mobilité | Doughnut (transports publics, une année), SSF (trajets), Eurostat (satisfaction du trajet) |

## 4. Besoins non couverts par v0

### 4.1 Indicateurs « non rattachables » (3)

| Cadre | Dimension du cadre | Indicateur | Pourquoi |
|---|---|---|---|
| SSF | Niveau de vie matériel | Production domestique et activités non marchandes | mesure élargie du revenu (valorisation du temps) plutôt qu'un résultat ; aucune dimension « temps » dans v0 |
| SSF | Soutenabilité (pilier distinct) | Tableau de bord des stocks de capitaux | logique de stocks (ressources futures) distincte du bien-être actuel |
| OCDE HL | Capital économique | [15_8] Levier des institutions financières monétaires | stabilité financière : aucun équivalent dans v0 |

### 4.2 Rattachements forcés : thèmes présents dans les cadres mais absents du contenu indicatif de v0

Ces indicateurs ont été rattachés faute de mieux ; ils signalent des besoins que v0 ne nomme pas (détail dans la colonne `commentaire`) :

1. **Sécurité routière** — OCDE 10_3 (décès sur la route), ODD 3.6, objectif UE 2030 : rattachés à `securite_confiance` (alternative `sante`).
2. **Temps et travail non rémunéré** — SSF (emploi du temps, production domestique, travail domestique), OCDE (dimension *Work-life balance* : temps libre, travail non rémunéré, écart F-H de temps de travail, satisfaction de l'emploi du temps), Eurostat (travail non rémunéré, à développer) : dispersés entre `liens_bien_etre`, `egalites` et « non rattachable ».
3. **Énergie** (accès, précarité, renouvelables, consommation) — Doughnut (électricité, combustibles propres), OCDE (3_5 chauffage, 12_10 renouvelables), ODD 7.1 et 7.3, objectifs L100-4 et SNBC : partagés entre `logement_cadre_vie` et `planete` (arbitrage Q-B).
4. **Alimentation** — Doughnut (sous-alimentation, insécurité alimentaire), Eurostat (fruits et légumes), ODD 2.1 : partagés entre `sante` et `niveau_de_vie` (arbitrage Q-B).
5. **Connectivité et infrastructures** — Doughnut (internet, transports publics), OCDE 3_4 (internet à domicile) : partagés entre `education` et `logement_cadre_vie` (arbitrage Q-B innovation/infrastructures).
6. **Innovation et soutenabilité économique** — INSEE NIR (R&D, endettement), OCDE (capital économique : actifs fixes, propriété intellectuelle, R&D, patrimoine financier net, dettes), objectifs (3 % R&D, 60 % dette, 3 % déficit) : rattachés à `niveau_de_vie` alors qu'ils relèvent des ressources futures (SSF rec. 11 ; OCDE) et sont parfois des moyens (critère charte §3.4).
7. **Discriminations et inégalités selon l'origine** — Doughnut (inégalité raciale, sans données), Eurostat (discriminations à développer ; écart d'emploi nationaux / pays tiers) : `egalites`, contenu non nommé dans v0.
8. **Adaptation au changement climatique** — OCDE 9_3 (exposition aux températures extrêmes) : rattaché à `logement_cadre_vie` (alternative `planete`).
9. **Gouvernance et qualité de l'action publique** — OCDE 14_4 (association des parties prenantes à la réglementation), Eurostat (satisfaction des services publics, à développer) : `democratie`.
10. **Variables planétaires sans équivalent national** — Doughnut : forçage radiatif, acidification, aérosols, eau verte, taux d'extinction, ozone : rattachées à `planete` mais marquées « non » disponibles ; leur usage national passe par des empreintes ou des proxys.

## 5. Recoupements entre cadres

Concepts présents (sous une forme proche) dans **au moins trois des cinq cadres de bien-être** (Doughnut, SSF, OCDE, Eurostat, INSEE), d'après les lignes du CSV — décompte par concept établi à la lecture, non automatique :

| Concept | Cadres | Nb |
|---|---|---|
| Inégalité de revenu (S80/S20, Palma) | Doughnut, SSF, OCDE, Eurostat, INSEE | 5 |
| Pauvreté monétaire relative (50 % ou 60 % du médian) | Doughnut, SSF, OCDE, Eurostat, INSEE (complément) | 5 |
| Diplôme du secondaire / sorties précoces | Doughnut, SSF, OCDE, Eurostat, INSEE | 5 |
| Satisfaction dans la vie | SSF, OCDE, Eurostat, INSEE | 4 |
| Espérance de vie | SSF, OCDE, Eurostat, INSEE (complément) | 4 |
| Écarts femmes-hommes (emploi, salaire, inégalité de genre) | Doughnut, SSF, OCDE, Eurostat | 4 |
| Participation et voix politique | Doughnut (régime), SSF, OCDE, Eurostat | 4 |
| Émissions de GES / empreinte carbone | Doughnut, SSF, OCDE, INSEE | 4 |
| Santé perçue, morbidité, limitations | SSF, OCDE, Eurostat (+ INSEE : espérance de vie sans incapacité, déclarative) | 3-4 |
| Soutien social (avoir quelqu'un sur qui compter) | Doughnut, OCDE, Eurostat (+ SSF, à vérifier) | 3-4 |
| Homicides | Doughnut, OCDE, Eurostat (+ SSF, victimation) | 3-4 |
| Revenu disponible des ménages | SSF, OCDE, Eurostat | 3 |
| Taux d'emploi | OCDE, Eurostat, INSEE | 3 |
| Privation matérielle / cumul des difficultés | SSF, Eurostat, INSEE | 3 |
| Sécurité économique (dépense imprévue, épargne liquide) | SSF, OCDE, Eurostat | 3 |
| Compétences mesurées (PISA, PIAAC) | SSF, OCDE, Eurostat | 3 |
| Sentiment d'insécurité / criminalité perçue | SSF, OCDE, Eurostat | 3 |
| Surpeuplement et qualité du logement | SSF, OCDE, Eurostat (+ Doughnut : bidonvilles) | 3-4 |
| Longues durées de travail | SSF, OCDE, Eurostat | 3 |
| Temps libre / emploi du temps | SSF, OCDE, Eurostat | 3 |
| Pollution de l'air locale | SSF, OCDE, Eurostat | 3 |
| Usage des sols (forêt, couverture naturelle, artificialisation) | Doughnut, OCDE, INSEE | 3 |

Présents dans deux cadres seulement : NEET (Doughnut, OCDE), corruption (Doughnut, OCDE), confiance dans les institutions (OCDE, Eurostat), confiance dans les autres (OCDE, Eurostat), satisfaction au travail (OCDE, Eurostat), accès aux soins (Doughnut, Eurostat), dette et R&D (OCDE, INSEE), azote, eau et biodiversité (Doughnut, OCDE), bruit et espaces verts (OCDE ou SSF, Eurostat), patrimoine (SSF, OCDE), tabac et obésité (OCDE, Eurostat).

## 6. Différences de découpage entre cadres (constats)

| Thème | Doughnut | SSF | OCDE | Eurostat | INSEE | v0 |
|---|---|---|---|---|---|---|
| Sécurité économique | — | avec l'insécurité physique | revenu et patrimoine (insécurité financière, difficultés), travail (insécurité du marché du travail) | **avec la sécurité physique** | — | `securite_confiance` |
| Confiance interpersonnelle | — | liens sociaux (à vérifier) | **capital social** | **interactions sociales** | — | `securite_confiance` |
| Confiance institutionnelle, corruption | corruption en **paix et justice** | voix politique et gouvernance | **capital social** | gouvernance | — | `democratie` |
| Inégalités | égalité (genre, race) ; Palma en **cohésion sociale** | **transversal** (rec. 4, 7) | **transversal** (`_VER`, écarts entre groupes) | S80/S20 en conditions matérielles ; écarts F-H et nationalité en **gouvernance** | social | dimension propre `egalites` |
| Satisfaction globale | absente | **transversal** (rec. 10) | dimension *Subjective well-being* | dimension **+1** | indicateur « psychologique » | dans `liens_bien_etre` |
| Temps, équilibre vie pro/perso | — | activités personnelles | **dimension propre** | loisirs (et temps de trajet en activité) | — | dans `liens_bien_etre` |
| Logement | logement + eau, énergie, connectivité séparés | activités personnelles | dimension (dont internet) | conditions de vie matérielles | absent | `logement_cadre_vie` (avec cadre de vie) |
| Environnement local | — | environnement présent | qualité de l'environnement | dimension 8 | — | `logement_cadre_vie` |
| Environnement planétaire | **9 dimensions** | soutenabilité (physique) | capital naturel (ressources futures) | **absent** | 2 indicateurs | `planete` |
| Investissement, dette, R&D | — | **soutenabilité** (stocks) | **capital économique** (futur) | — | domaine économique | `niveau_de_vie` |
| NEET | revenu et travail | — | travail | — | — | `travail` |
| Internet | connectivité | — | logement | compétences numériques (éducation) | — | `education` (numérique) |

## 7. Disponibilité et nature des indicateurs par dimension v0

| Dimension v0 | oui | probable | non | dont déclaratifs |
|---|---|---|---|---|
| `niveau_de_vie` | 35 | 3 | 1 | 3 |
| `travail` | 27 | 7 | 7 | 4 |
| `logement_cadre_vie` | 25 | 10 | 2 | 7 |
| `sante` | 20 | 12 | 0 | 5 |
| `education` | 16 | 10 | 10 | 0 |
| `liens_bien_etre` | 8 | 15 | 11 | 20 |
| `securite_confiance` | 14 | 3 | 0 | 5 |
| `democratie` | 5 | 3 | 9 | 7 |
| `egalites` | 17 | 11 | 5 | 4 |
| `planete` | 33 | 15 | 7 | 0 |
| `non rattachable` | 1 | 2 | 0 | 0 |

Constats : `liens_bien_etre` est majoritairement **déclaratif** (20 lignes sur 34) et peu disponible en séries longues (modules SILC 2013-2018-2022, enquêtes emploi du temps, Gallup propriétaire) ; `education` souffre d'enquêtes **non annuelles** (PISA triennal, PIAAC 2012-2023, AES quinquennale) ; `democratie` a peu de séries publiques annuelles (participation électorale au rythme des scrutins ; confiance institutionnelle en modules ponctuels ou Gallup).

## 8. Seuils et cibles chiffrés relevés

Décompte manuel des seuils **normatifs** (hors seuils de simple définition statistique comme « 60 % du médian » ou « note < 5/10 ») :

| Source | Seuils / cibles normatifs chiffrés | Exemples |
|---|---|---|
| Doughnut 3.0 | **18** valeurs spécifiques (13 limites planétaires + 5 seuils sociaux), plus une cible implicite de 0 % de privation pour chaque indicateur social | CO2 ≤ 350 ppm ; azote ≤ 62 Mt/an ; phosphore ≤ 6,2 Mt/an ; mortalité < 5 ans ≤ 25 ‰ ; Palma = 2 ; homicides < 5 / 100 000 ; indice CSU ≥ 60 |
| INSEE NIR 2025 | **4** | R&D 3 % du PIB ; dette publique 60 % du PIB ; sorties précoces < 9 % (UE 2030) et 9,5 % (France) ; ODD 1.2 (pauvreté ÷ 2) |
| OCDE HL | **1** (à vérifier) | valeur guide OMS PM2,5 de 5 µg/m³ dans la définition de 9_2 |
| SSF, Eurostat QoL, BLI | **0** | — |
| ODD (cibles chiffrées) | **16** | mortalité maternelle < 70 / 100 000 ; néonatale ≤ 12 ‰ ; mortalité prématurée −1/3 ; gaspillage alimentaire ÷ 2 |
| Objectifs officiels France-UE | **41** (dont 14 « à vérifier ») | GES −50 % 2030/1990 (SNBC 3) ; budgets carbone 342/262/194 Mt ; empreinte 2,3 t/hab. en 2050 ; ZAN 2050 ; aires protégées 30 %/10 % ; emploi 78 % ; formation des adultes 65 % ; AROPE −1,1 million |
| **Total** | **≈ 80** valeurs (avec quelques doublons : 25 ‰, 9 %, 3 %, 60 %) | |

Répartition par dimension v0 des 94 lignes portant une valeur normative (y compris la cible implicite de 0 % des indicateurs sociaux du Doughnut) : `planete` 35, `education` 13, `logement_cadre_vie` 13, `niveau_de_vie` 11, `sante` 8, `egalites` 5, `travail` 3, `securite_confiance` 3, `democratie` 2, `liens_bien_etre` 1. **Hors cette cible implicite de 0 %**, `liens_bien_etre` et `democratie` n'ont **aucune** borne chiffrée et `securite_confiance` n'en a que trois (homicides < 5 / 100 000 du Doughnut ; décès routiers ÷ 2 de l'ODD 3.6 et de l'objectif UE 2020-2030) : leurs bornes initiales devront venir des niveaux 3 à 5 de la hiérarchie de la charte (historique, référence européenne, dire d'expert).

## 9. Premiers constats factuels

1. **Couverture** : la grille v0 couvre l'essentiel des six cadres — 341 lignes sur 344 se rattachent à une dimension v0 ; aucune dimension v0 n'est vide toutes sources confondues.
2. **Déséquilibre de couverture** : `planete` (55 lignes, 35 cibles chiffrées) et `travail` (41) sont très fournis ; `securite_confiance` et `democratie` (17 chacune) le sont peu et ont peu de séries annuelles et de bornes.
3. **Le Doughnut et Eurostat sont complémentaires** : le Doughnut apporte presque tout le plafond écologique et des seuils, mais une ligne seulement pour le travail, les liens et la sécurité ; Eurostat apporte le détail du travail et du bien-être subjectif, mais rien sur la planète.
4. **Trois cadres (SSF, OCDE, et implicitement INSEE) distinguent bien-être actuel et ressources futures** ; v0 range investissement, dette et R&D dans `niveau_de_vie`.
5. **La satisfaction dans la vie est traitée de quatre façons** : absente (Doughnut), couche transversale (SSF), dimension à part (OCDE, Eurostat « +1 »), indicateur parmi d'autres (INSEE) — c'est l'arbitrage Q-B.
6. **Les inégalités sont transversales dans SSF et l'OCDE**, réparties entre plusieurs dimensions chez Eurostat et le Doughnut, et forment une dimension propre seulement dans v0.
7. **Thèmes non nommés par v0 mais présents dans les cadres** : sécurité routière, temps et travail non rémunéré, énergie, alimentation, connectivité, discriminations selon l'origine, adaptation climatique, stabilité financière.
8. **Thèmes nommés par v0 mais absents des cadres** : PIB par habitant, inégalités territoriales et intergénérationnelles, mobilité sociale, libertés de la presse et académique (sans indicateur chiffré).
9. **Indicateurs mondiaux du Doughnut** : 6 des 13 indicateurs écologiques n'ont pas d'équivalent national (disponibilité « non ») ; plusieurs indicateurs sociaux sont proches de 0 % en France (électricité, combustibles propres, eau, bidonvilles) et peu discriminants.
10. **Sources propriétaires** : plusieurs indicateurs OCDE et Doughnut reposent sur le Gallup World Poll (soutien social, corruption perçue, sentiment de sécurité, affects, confiance dans le gouvernement), non diffusable librement ; des équivalents publics existent souvent dans EU-SILC ou les enquêtes françaises (à confirmer en M02/M04).
