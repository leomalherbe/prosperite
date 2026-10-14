# Audit croisé M06 — dimension `liens_bien_etre`

Auditeur M06 (session neuve, n'ayant pas participé à M05), 14 octobre 2026. Branche `m06-liens_bien_etre`, partie de `origin/main` au commit `48e2381` (fiches fusionnées par la PR #6). Aucune fiche, aucun script, aucun catalogue n'a été modifié : ce rapport propose, l'agent M05 (ou la session mère) corrige.

Lu avant d'agir : `CLAUDE.md` ; charte §3.1, §3.4, §3.6, §4, §5.1 ; journal D13–D30 ; fiche M06 ; `docs/methodo/33_methode_fiches_M05.md` ; `indicateurs/dimensions.yaml` (définition, exclusions, R1–R8) ; les 21 fiches, le tableau de validation, les règles et les deux tableaux de présélection ; journal et compte rendu M05 ; long-list `liens_bien_etre` et catalogues INSEE, Eurostat et M04 ; crosswalk (`30_indicateurs_cadres_reference.csv`, §5 de `30_crosswalk_synthese.md`) ; fiches `indicateurs/securite/*.yaml` et présélection `securite`. Contrôle préalable : `python scripts/verifier_fiches.py --dimension liens_bien_etre` → 0 erreur, 1 avertissement (`depart_vacances` hors catalogue de séries), identique au journal M05.

---

## 1. Avis global : `corrections_necessaires`

Les chiffres cités dans les fiches sont exacts partout où ils ont pu être relus à la source : périodes, nombres de points, valeurs citées et drapeaux de 9 jeux Eurostat, 2 séries OCDE, 1 série BDM et des extraits du robot (DREES, OCDE, WHR) concordent tous avec les fiches. Les recommandations respectent la charte et la grille (A1, A4/D25-D27, R3, R4, R5). Mais trois catégories de problèmes demandent une reprise avant la validation de Léo :

1. **Deux oublis de fond** dans des concepts nommés par le contenu de la dimension : le baromètre DREES mesure la **solitude** (question CS12, 7 vagues 2014-2025, contre 2 pour la série OCDE retenue) et l'**adhésion à une association** (SDASSYND_2, 25 années 2000-2025, alors que la seule mesure d'engagement retenue est une série Gallup à 7 valeurs et licence non confirmée).
2. **Une erreur factuelle répétée** : les 6 fiches du baromètre DREES portent `geo: FR`, alors que l'enquête porte sur la France métropolitaine (page DREES) et que les fiches `securite` de la même source portent `geo: FM`.
3. **Une fiche hors long-list à reprendre** (`depart_vacances`) : champ 15 ans ou plus, rupture de série 2020 documentée par Eurostat, variante INSEE omise.

Chiffres : **15 fiches auditées** sur 21 — **9 conformes**, **6 à corriger**, **0 non vérifiable** (deux réserves partielles : valeur Melodi 2025 de `satisfaction_vie`, poursuite de `satisfaction_relations`) ; plus 5 fiches hors échantillon touchées par des corrections transversales. **6 oublis** (dont 2 importants). **6 points de cohérence inter-dimensions** (aucun identifiant ni série en double avec `securite`).

Liste ordonnée des corrections : §9.

## 2. Échantillon

| Règle (fiche M06) | Fiches |
|---|---|
| `recommandation: ecarter` (2) | `evaluation_vie_cantril`, `aidance_personne_agee` |
| `incontournable: oui` (2) | `satisfaction_vie`, `soutien_social` |
| Signalées `a_verifier` ou `a_etudier` au journal M05 (§3 : 7) | `bonheur_ressenti`, `bilan_emotionnel_negatif`, `soutien_social`, `solitude`, `confiance_autrui` (aussi `raccordement: a_etudier`), `benevolat`, `participation_culturelle_sportive` |
| Rattachement proposé (2) | `privation_vacances`, `depart_vacances` |
| Point ouvert « à vérifier » au journal M05 §7 (1) | `satisfaction_relations` (« poursuite à vérifier ») |
| 20 % des 9 autres, tirage au hasard (2) | `optimisme_avenir_personnel`, `situation_personnelle_bonne` |

Tirage : `random.Random(20261014).sample(sorted(autres), 2)` sur les 9 fiches restantes (`cohesion_sociale_percue`, `integration_sociale`, `optimisme_avenir_personnel`, `optimisme_generations_futures`, `privation_loisirs`, `privation_sorties_proches`, `satisfaction_relations`, `satisfaction_vie_faible`, `situation_personnelle_bonne`), 20 % de 9 = 1,8 arrondi à 2, **graine 20261014**. `satisfaction_relations`, tirable, a été ajoutée au titre du journal M05 §7.

Total : **15 fiches** = 12 fiches obligatoires distinctes (`soutien_social`, incontournable et « à vérifier », comptée une fois) + `satisfaction_relations` (journal M05 §7) + 2 fiches tirées. Les 6 autres ont reçu un contrôle léger (§5).

## 3. Tableau des fiches auditées

Nature : **F** = erreur factuelle ; **J** = désaccord de jugement ; **O** = oubli.

| Fiche | Motif d'échantillon | Source consultée (14/10/2026) | Verdict | Nature | Correction attendue (résumé ; détail §4) |
|---|---|---|---|---|---|
| `satisfaction_vie` | incontournable | BDM `010593281` (WebFetch) ; catalogue Melodi ; API Melodi refusée (robots.txt) | conforme | — | Réserve : valeur Melodi 2025 non relue (2025 = NaN dans la BDM). |
| `soutien_social` | incontournable, a_verifier | API OCDE `FRA.7_1.PT_POP_Y_GE15._T._T._T.` (jsondata) ; API Eurostat `ilc_pw06` ; métadonnées OCDE (extrait du robot, p. 21) | conforme | — | — |
| `evaluation_vie_cantril` | ecarter | extrait du robot `whr__whr26_figure_2_1_france.txt` ; page WHR `data-sharing` | conforme | — | — |
| `aidance_personne_agee` | ecarter | page DREES du jeu 431 ; dictionnaires et distributions DREES du robot | a_corriger | F | `geo: FM` ; drapeaux `pas_d_enquete_2012` → `question_non_posee_2012`, retirer `pas_d_enquete_2003` (hors période 2011-2025). |
| `bonheur_ressenti` | a_verifier | API Eurostat `ilc_pw08` | conforme | — | — |
| `bilan_emotionnel_negatif` | a_verifier | extrait OCDE du robot (`ocde__hsl_bien_etre_actuel.csv`) ; métadonnées OCDE p. 27 | conforme | — | — |
| `solitude` | a_verifier | API OCDE `FRA.7_4.PT_POP_Y_GE16._T._T._T.` ; dictionnaire et distributions DREES | a_corriger | O, F | Examiner la série DREES CS12 (7 vagues) comme variante principale ; aligner le motif de présélection (« la plupart du temps ou tout le temps ») sur la fiche (fréquence « non trouvée »). |
| `confiance_autrui` | a_verifier, a_etudier | API Eurostat `ilc_pw03` | conforme | (J) | Remarque : toutes les valeurs « u » ; bascule vers la série INSEE à trancher avec le raccordement. |
| `benevolat` | a_verifier | extrait OCDE du robot (`ocde__hsl_bien_etre_futur.csv`) | conforme | (O) | L'oubli DREES SDASSYND_2 (adhésion associative) relève d'une nouvelle fiche, pas de celle-ci (§6). |
| `participation_culturelle_sportive` | a_verifier | API Eurostat `ilc_scp01` | conforme | — | Réserve maintenue : période de référence 2022 (crise sanitaire) non vérifiée. |
| `privation_vacances` | rattachement proposé | API Eurostat `ilc_mdes02` ; long-list `travail` | a_corriger | O | Ajouter en variantes les 3 lignes `hlth_dm020` de la long-list `travail` (même item, 16 ans ou plus, 2010-2025). |
| `depart_vacances` | rattachement proposé, hors long-list | API Eurostat `tour_dem_totot` ; métadonnées Eurostat `tour_dem_esms` et `tour_dem_esmsdm_fr` ; catalogue Melodi des séries écartées | a_corriger | F, O | Champ « résidents de 15 ans ou plus » (unité, définition) ; drapeau `rupture_2020` et note ; panel non aléatoire ; variante INSEE `DS_SUIVI_DDE_TOUR`. |
| `optimisme_avenir_personnel` | tirage | page DREES ; dictionnaires et distributions DREES | a_corriger | F, (J) | `geo: FM`. Jugement : famille partagée avec `optimisme_generations_futures` (§8). |
| `situation_personnelle_bonne` | tirage | page DREES ; dictionnaires et distributions DREES | a_corriger | F | `geo: FM`. |
| `satisfaction_relations` | journal M05 §7 | catalogues Melodi (retenu et écarté) ; API Eurostat `ilc_pw01b` ; extrait OCDE `7_3` | conforme | — | Réserve : poursuite après 2022 non vérifiable (aucune valeur postérieure dans les catalogues ; API Melodi refusée). |

## 4. Détail des vérifications par fiche

Valeurs entre parenthèses : lues à la source le 14/10/2026 (API par WebFetch) ou dans les extraits du robot commités dans `docs/sources/series/` (précisé).

**`satisfaction_vie`** — Identifiant présent au catalogue Melodi (`melodi-006207`, 2010-2025, 16 points, statut de la dernière valeur A, mise à jour 29/09/2026). BDM `010593281` « Satisfaction dans la vie - Ensemble », unité `NOTE_MOYENNE_0_10`, zone FM : 2010-2024 renseignés, 2025 = NaN (statut O), minimum 6,8 (2021), maximum 7,5 (2012) — la note « de 6,8 à 7,5 sur 2010-2024 » est exacte. Définition, unité, sens `haut`, `type: resultat`, `declaratif: oui`, `geo: FM`, incontournable (4 cadres, crosswalk §5) et recommandation (indicateur ordinaire, A1) conformes. Non vérifiable : la valeur Melodi 2025 et l'identité Melodi/BDM (l'outil de lecture est refusé par `api.insee.fr`, comme pour M05).

**`soutien_social`** — API OCDE : 20 observations 2006-2025 en 7 valeurs distinctes répétées par bloc (93,71 en 2006-2007 ; 92,72 ; 91,99 ; 88,38 ; 93,11 ; 90,78 ; 87,56 en 2023-2025) : « 87,6 % sur 2023-2025 » et « 7 valeurs distinctes » exacts. Définition conforme aux métadonnées OCDE (question Gallup, 15 ans ou plus, moyennes groupées de 3 ans et 2006-2007). Variante EU-SILC `ilc_pw06` : 2013, 2018, 2022 (92,4 ; 95,3 ; 90,6), soit les « 3 vagues » citées. Variante principale Gallup (plus profonde, plus fraîche) conforme à la méthode, licence signalée en `qualite`. `url_page` : « non trouvé » confirmé (page OCDE en erreur à l'outil).

**`evaluation_vie_cantril`** — Extrait du fichier WHR 2026 : années 2011, 2012, 2014-2025 (14 points, pas de 2013), dernière valeur 6,586. Page WHR `data-sharing` : aucun texte de licence (« available to download for free »). Recommandation `ecarter` (dominée par la série INSEE de même concept) cohérente avec la méthode §3.

**`aidance_personne_agee`** — Question DE07 et modalité 1 = « Oui » confirmées par les dictionnaires 2025 (modalité 3 : « Non car j'ai moi-même besoin d'aide »). Couverture : 2011, 2013-2025 (14 années) ; part pondérée de 26,8 % (2011) à 15,4 % (2025) d'après les distributions du robot. Recommandation `ecarter` cohérente : sens ambigu (§3.4) et travail non rémunéré hors v1 (A4 au sens de D25 : « temps et travail non rémunéré »). Erreurs : (1) `geo: FR` → `FM` : la page du jeu DREES décrit un échantillon « représentatif de la population vivant en France métropolitaine », et la variable de région `SDREG` ne compte que les 9 ZEAT métropolitaines (aucun département d'outre-mer dans `SDDEPT`) ; (2) `pas_d_enquete_2012` est inexact (le baromètre 2012 existe : OG01, OG03 ont des valeurs 2012 ; seule DE07 n'a pas été posée) ; `pas_d_enquete_2003` est hors de la période de la série.

**`bonheur_ressenti`** — API `ilc_pw08` (16 ans ou plus, total) : « toujours » 12,3 / 15,5 / 15,8 et « la plupart du temps » 49,8 / 52,3 / 50,6 en 2013 / 2018 / 2022, d'où 62,1 / 67,8 / 66,4 %, exactement les valeurs de la note ; aucun drapeau. Composantes et formule conformes.

**`bilan_emotionnel_negatif`** — Extrait OCDE du robot : 2006-2025, 20 périodes, 7 valeurs distinctes, dernière 12,54 %. Définition conforme aux métadonnées OCDE (p. 27 : colère, tristesse, inquiétude contre plaisir, repos, rire ou sourire ; la veille ; 15 ans ou plus).

**`solitude`** — API OCDE 7_4 : 2018 = 7,14 ; 2022 = 10,77 (la note cite 10,8 % : exact) ; unité « % des 16 ans ou plus ». La fréquence de référence n'est pas dans les métadonnées de l'API (vérifié) : la fiche dit « non trouvée », mais le motif de présélection affirme « la plupart du temps ou tout le temps » ; l'un des deux doit être aligné (en l'absence de source, garder « non trouvé » et corriger le motif). **Oubli** : le baromètre DREES pose « Vous arrive-t-il de vous sentir seul·e ? » (CS12 : souvent / parfois / jamais) en 2014, 2016 et 2021-2025 (7 vagues) ; part « souvent » de 13,4 % (2014) à 9,1 % (2025) d'après les distributions du robot (non-réponses au dénominateur). Même concept, 7 points publics contre 2, France métropolitaine : la variante principale de la famille est à réexaminer (règle « série la plus longue », à définition proche ; la règle « niveau 1 > 2 » joue dans l'autre sens et suppose une définition égale).

**`confiance_autrui`** — API `ilc_pw03` : 5,0 (2013, u) ; 5,9 (2018, b u) ; 4,5 (2021, u) ; 4,1 (2022, b u) ; 4,4 (2023, u) ; 4,3 (2024, u) ; 4,0 (2025, u). Années, ruptures 2018 et 2022, drapeau « u » sur toutes les valeurs et baisse « de 5,9 à 4,5 » exacts. Variante principale (Eurostat, 7 vagues) conforme à la méthode ; `raccordement: a_etudier` au bon format. Remarque de jugement : avec une série entièrement « peu fiable », la bascule vers la série INSEE (`DS_SRCV_CONFIANCE`, 2020-2025) mérite d'être tranchée au moment du raccordement, pas reportée.

**`benevolat`** — Extrait OCDE du robot (14_7, total) : 2007-2025, 19 périodes, 7 valeurs distinctes, dernière 30,99 %. Libellé conforme au libellé français de l'OCDE (« Bénévolat dans des associations »), `declaratif: non` conforme à la règle de la session mère. L'oubli de l'adhésion associative DREES est traité au §6 (concept distinct : adhésion ≠ bénévolat).

**`participation_culturelle_sportive`** — API `ilc_scp01` : « au moins une fois » 74,1 (2006), 80,6 (2015), 59,1 (2022), sans drapeau ; complément « pas au cours des 12 derniers mois » 25,9 / 19,4 / 40,9. Valeurs de la note exactes.

**`privation_vacances`** — API `ilc_mdes02` (total) : 2004-2025, 22 valeurs ; 33,4 (2004), 22,0 (2024), 23,2 (2025) ; drapeau « b » en 2020 et 2022. Tout est exact. **Oubli** : la long-list `travail` contient `hlth_dm020` (« Incapacité à se payer une semaine de vacances… par niveau de handicap, sexe et âge »), dont la ligne `estat-021832` (`lev_limit=TOTAL&age=Y_GE16&sex=T`, 2010-2025, 16 points, éligible) est le même item pour les 16 ans ou plus, et `estat-021833`/`021834` ses ventilations par âge et sexe (absentes de `ilc_mdes02`). La présélection `securite` a repris l'équivalent `hlth_dm040` en variante de `depense_imprevue` : à harmoniser.

**`depart_vacances`** — API `tour_dem_totot` (`N_GE4`, `WORLD`, `PC_POP`) : 2012-2025, 14 valeurs (65,49 en 2012 ; 63,06 en 2016 ; 57,35 en 2017 ; 59,40 en 2020 ; 61,93 en 2025), aucun drapeau, mise à jour 09/10/2026 : conforme à la fiche. Erreurs et compléments, d'après les métadonnées Eurostat : (1) **champ** : « all residents … aged 15 or over » (`tour_dem_esms`) ; la fiche écrit « part de la population » et `unite: % de la population` → « % des résidents de 15 ans ou plus » (le drapeau `champ_age_a_verifier` est levé ; le dénominateur exact n'est pas précisé par les métadonnées) ; (2) **rupture** : la fiche nationale `tour_dem_esmsdm_fr` indique que l'enquête Suivi de la demande touristique (SDT) est reprise par l'INSEE en 2020 (auparavant DGE), avec une rupture de série en 2020 due aux changements de méthode et une correction de non-réponse qui relève les niveaux, le coefficient d'extrapolation étant recalculé jusqu'en 2018 ; questionnaire révisé en 2023 et 2024 ; échantillon tiré d'un panel non aléatoire → ajouter `rupture_2020` (et la note), garder le décrochage 2017 « non expliqué par les métadonnées » ; (3) **oubli de variante** : l'INSEE publie la même enquête dans Melodi, `DS_SUIVI_DDE_TOUR` (« Taux de départ en voyage ; Voyage pour motif personnel », annuel 2022-2025, mensuel 2018-2025, catalogue `insee_melodi_catalogue_non`). La recommandation `retenir` reste défendable (seule mesure du départ effectif) mais la note doit avertir de la rupture.

**`optimisme_avenir_personnel`** — Question OG03_1 et modalités 1+2 (« très » et « plutôt optimiste ») confirmées ; 2000-2002 et 2004-2025 (25 années) ; de 69,1 % (2000) à 46,7 % (2025) d'après les distributions du robot ; motif exact (« série annuelle la plus longue de la dimension »). Erreur : `geo: FR` → `FM` (même motif que ci-dessus). Jugement (§8) : `optimisme_generations_futures` est rangée dans la même famille alors que sa note dit qu'elle « ne remplace pas l'optimisme pour soi-même ».

**`situation_personnelle_bonne`** — Question OG01 (« Vous personnellement, comment qualifieriez-vous votre situation actuelle ? ») et modalités 1+2 confirmées ; 2002, 2004-2025 (23 années) ; de 81,0 % (2002) à 79,2 % (2025). Place en `retenir_variante` de la famille `satisfaction_vie` cohérente (couvre 2002-2009). Erreur : `geo: FR` → `FM`.

**`satisfaction_relations`** — Catalogue Melodi : série France métropolitaine 2010-2022 (11 points), série France hors Mayotte réduite à 2022 ; aucune valeur postérieure à 2022 dans les catalogues. Variante Eurostat `ilc_pw01b` (`PER_RELS`) : 2013, 2018, 2022 seulement (7,8 ; 8,0 ; 7,7), ce qui est compatible avec une question devenue périodique, sans que je puisse le prouver. Éligibilité (dernière valeur ≥ 2020, 11 points) et recommandation conformes ; la poursuite reste **non vérifiable** ici et doit être tranchée au premier passage du robot.

## 5. Contrôles hors échantillon (transversaux)

| Fiche | Constat | Source | Correction |
|---|---|---|---|
| `cohesion_sociale_percue`, `integration_sociale`, `optimisme_generations_futures` | `geo: FR` pour une enquête métropolitaine | page DREES du jeu 431 ; `SDREG` | `geo: FM`, remplacer `champ_geographique_a_verifier` par `enquete_metropole` (drapeau de `securite`). |
| `cohesion_sociale_percue` | Les « ne sait pas » de CS01, comptés au dénominateur, passent de 0,6 % (2017) à 5,3 % (2018), puis restent entre 2,3 et 4,2 % (2019-2025) ; la fiche `securite` `risque_pauvrete_ressenti` signale le même saut en 2018 (« changement de protocole possible ») | distributions DREES du robot | Ajouter `rupture_possible_2018` et le dire dans la note (ou calculer hors non-réponses). Pour OG01, OG03 et CS05, le saut est faible (≤ 1,5 point). |
| `privation_loisirs` | `age=TOTAL` = `age=Y_GE16` pour chaque année 2014-2025 (même valeur) : le champ est 16 ans ou plus | API Eurostat `ilc_mdes11a` | Lever `champ_age_a_verifier`, unité « % des 16 ans ou plus ». |
| `privation_sorties_proches` | Valeurs 2014-2025 entre 4,9 et 6,8 % (exact) ; ruptures 2020 et 2022 exactes | API Eurostat `ilc_mdes10a` | Même correction de champ que `privation_loisirs` (même module, à confirmer à la relecture du jeu). |
| Toutes les fiches DREES (6) | `url_api` pointe vers `barometre2000_2024_diff_csv` (+ fichier 2025) ; le robot et les fiches `securite` utilisent la pièce jointe unique `barometre2000_2025_diff_csv` (présente au jeu, vérifiée par le robot le 13/10) | `docs/sources/verif_acces/extraits/drees__jeu_431_le-barometre-d-opinion.txt` | Harmoniser sur `barometre2000_2025_diff_csv`. |

`satisfaction_vie_faible` : non contrôlée à la source au-delà du catalogue (2010-2025, 16 points, `SATISFNOTE=0T5` libellé « Faible (0-5) »), rien à signaler.

## 6. Complétude : oublis

Couverture de la long-list : les 668 lignes sont affectées (vérificateur) ; éligibles 389 = 12 séries principales + 296 variantes + 81 écarts en bloc (65 catégories « 6-8 », 16 licences par fédération) ; « à vérifier » 208 = 8 + 152 + 48 (catégories « moyen », non-réponses, classes de fréquence) ; non éligibles 71 (dont 40 renvoyées à `logement_cadre_vie`). Les écarts en bloc sont motivés et je n'en conteste aucun. Les oublis sont donc **hors long-list** :

| # | Oubli | Données (lues) | Importance | Proposition |
|---|---|---|---|---|
| O1 | **Solitude, baromètre DREES (CS12)** « Vous arrive-t-il de vous sentir seul·e ? » | 2014, 2016, 2021-2025 (7 vagues) ; « souvent » 13,4 % → 9,1 % (distributions du robot) | forte | Candidat M04 (catalogue `10_indicateurs_candidats…`), puis variante principale ou fiche de la famille `solitude` (D17). |
| O2 | **Adhésion à une association, baromètre DREES (SDASSYND_2)** « Vous personnellement, êtes-vous membre d'une association ? » | couverture 2000-2002, 2004-2025 (25 années), taux de réponse 2025 = 1,000 ; valeurs : non trouvé (distribution non calculée par le robot) | forte | Nouvelle fiche « vie associative » (`declaratif: non`, sens `haut`), seule mesure publique et annuelle de l'engagement depuis 2000 ; la calculer par le robot M04. |
| O3 | Privation de vacances par niveau de handicap `hlth_dm020` (long-list `travail`) | `estat-021832` à `021834`, 2010-2025, éligibles | moyenne | Variantes de `privation_vacances` (règle `longlist = travail`). |
| O4 | Taux de départ en voyage INSEE `DS_SUIVI_DDE_TOUR` | annuel 2022-2025 (4 points), mensuel 2018-2025 ; catalogue des séries écartées | moyenne | Variante de `depart_vacances` (ajout manuel avec `catalogue`). |
| O5 | Modules EU-SILC exclus en amont : rencontres et contacts avec la famille et les amis (`ilc_scp09`-`ilc_scp12`), bénévolat formel et informel (`ilc_scp19`, `ilc_scp20`) | 2015 et 2022 (catalogue des jeux) | moyenne (déjà signalé par M05) | Par cohérence avec `solitude` (2 points retenus) et `depart_vacances` (fiche hors long-list), une fiche hors long-list « rencontres avec les proches » (indicateur Eurostat *Quality of life* cité au crosswalk) et des variantes publiques de `benevolat`. |
| O6 | (autre dimension) Adhésion à un syndicat, baromètre DREES (SDASSYND_1) | couverture 2000-2025 (25 années) | à signaler | Candidat `democratie` (participation), à transmettre à M04. |

Recherches sans résultat : `ilc_pw*` (aucun autre jeu éligible : sens de la vie `MEANLIFE` 2013 seulement, vérifié sur l'API `ilc_pw01b` ; se sentir exclu `ilc_pw10/11/13` 2022 seulement) ; OCDE *How's Life* (toutes les mesures liens présentes ; 11_3 douleur physique relève de `sante`) ; INSEE SRCV (confiance `DS_SRCV_CONFIANCE` et privations `DS_SRCV_PMS` déjà en variantes) ; EHIS soutien social perçu (`hlth_ehis_ss1*`, 2014-2019, terminé). Pratique sportive et pratiques culturelles annuelles : aucune série au catalogue (recherche INJEP/DEPS déjà demandée à M04 par M05).

**Incontournables du crosswalk** (§5) : satisfaction dans la vie et soutien social présents et marqués ; temps libre (3 cadres) absent à bon droit (A4, seule série OCDE 4_1 de 2009 ; satisfaction de l'emploi du temps rangée `hors_grille`). Concepts à deux cadres : confiance, satisfaction des relations, affects, solitude, bénévolat présents ; fréquence des rencontres (O5) et avoir un confident (`ilc_scp17/18`, 2013-2015, non éligible) absents.

## 7. Cohérence inter-dimensions

Contrôle mécanique sur les 21 fiches `liens_bien_etre` et les 33 fiches `securite` (séries principales, composantes et variantes) : **aucun identifiant commun, aucune série commune**. Deux jeux partagés avec des mesures distinctes : `DS_SRCV_PMS` (`DIF_VACANCES`, `DIF_LOISIRS`, `DIF_INVITATION` ici ; `DIF_NON_PREVUE`, `DIF_PAIE` en `securite`) et `DS_NAT_SDG` (3.i4a ici ; 1.i5, 3.i6, 5.i3a, 5.i4a, 16.i1, 16.i2 en `securite`). La présélection `securite` ne contient aucune ligne de confiance envers autrui ni de baromètre DREES relevant de cette dimension.

| # | Incohérence | Correction |
|---|---|---|
| I1 | Même source DREES, `geo` différent : `FR` ici, `FM` en `securite` | `FM` ici (§4, §5). |
| I2 | Même source DREES, `url_api` différent (`2000_2024` + `2025` ici, `2000_2025` en `securite`) | Harmoniser (§5). |
| I3 | Variantes « par niveau de handicap » : reprises en `securite` (`hlth_dm040`, `hlth_dm050`), omises ici (`hlth_dm020`) | O3. |
| I4 | 20 lignes de la long-list `travail` sont utilisées ici (`ilc_mdes02` ×2 et 15 lignes Melodi de satisfaction par statut d'activité, dont 5 écartées) ou devraient l'être (`hlth_dm020` ×3) ; tant que M05 `travail` n'est pas fait, rien n'empêche leur reprise en double | Consigne à M05 `travail` : règles `autre_dimension:liens_bien_etre` pour ces lignes (R1). |
| I5 | Rupture possible 2018 du baromètre DREES (hausse des non-réponses) signalée en `securite`, pas ici | §5 (`cohesion_sociale_percue`). |
| I6 | Voisinages à surveiller au contrôle de redondance du gel 2 (pas des doublons : questions et sources différentes) : `optimisme_avenir_personnel` (DREES OG03_1) / `solde_situation_financiere_future` (INSEE, enquête de conjoncture) ; `situation_personnelle_bonne` (OG01) / `solde_situation_financiere_passee` | Aucune correction ; à noter pour la session mère. |

## 8. Synthèse par nature

**Erreurs factuelles** (corrections certaines, source citée)
1. `geo: FR` au lieu de `FM` sur les 6 fiches DREES (`aidance_personne_agee`, `optimisme_avenir_personnel`, `situation_personnelle_bonne`, `cohesion_sociale_percue`, `integration_sociale`, `optimisme_generations_futures`) — page DREES du jeu 431 et variable `SDREG`.
2. `depart_vacances` : champ 15 ans ou plus (unité, définition) ; rupture 2020 et panel non aléatoire non signalés — métadonnées Eurostat `tour_dem_esms`, `tour_dem_esmsdm_fr`.
3. `aidance_personne_agee` : drapeaux `pas_d_enquete_2012` (question non posée, enquête réalisée) et `pas_d_enquete_2003` (hors période).
4. `solitude` : fréquence de référence affirmée dans le motif de présélection, « non trouvée » dans la fiche.
5. `privation_loisirs` (et probablement `privation_sorties_proches`) : champ 16 ans ou plus établi, drapeau `champ_age_a_verifier` à lever.

**Désaccords de jugement** (à trancher par la session mère ou Léo ; je ne les compte pas comme erreurs)
- J1. `optimisme_generations_futures` est dans la famille `optimisme` en `retenir_variante`, alors que sa propre note dit qu'elle ne remplace pas l'optimisme pour soi (méthode §1 : concepts complémentaires = familles distinctes) ; et `cohesion_sociale_percue`, autre opinion sur la société, est `retenir` en famille propre. Traiter les deux opinions sur la société de la même façon (deux familles propres, recommandation identique), en cohérence avec la question déjà posée à Léo par M05 (compte rendu §6.2).
- J2. `confiance_autrui` : la série principale est « peu fiable » sur toutes ses valeurs ; trancher le raccordement à la série INSEE avant le gel 2 plutôt qu'après.
- J3. `aidance_personne_agee` : l'écart est fondé (A4, D25), mais le cadre Eurostat *Quality of life* range l'aide informelle parmi les interactions sociales (bénévolat informel) : à noter pour une v2.

**Oublis** : O1 à O6 (§6), dont deux de fond (O1 solitude DREES, O2 adhésion associative DREES).

## 9. Corrections ordonnées pour l'agent M05

1. **O1, O2** — Faire calculer par le robot M04 les séries DREES CS12 (« souvent », et « souvent + parfois » en variante) et SDASSYND_2 (« oui »), sur `barometre2000_2025_diff_csv`, non-réponses au dénominateur comme les autres séries DREES ; puis réexaminer la variante principale de `solitude` et créer une fiche « vie associative ».
2. **`geo: FM`** sur les 6 fiches DREES, drapeau `enquete_metropole` à la place de `champ_geographique_a_verifier`, `url_api` harmonisée sur `barometre2000_2025_diff_csv` ; régénérer le tableau de validation.
3. **`depart_vacances`** : unité et définition « résidents de 15 ans ou plus » ; `qualite` + `rupture_2020` ; note citant la fiche nationale Eurostat (reprise INSEE en 2020, niveaux relevés, panel non aléatoire, questionnaire révisé en 2023-2024) ; variante INSEE `DS_SUIVI_DDE_TOUR`.
4. **`privation_vacances`** : règles de présélection pour les 3 lignes `hlth_dm020` de la long-list `travail` (variantes, rattachement proposé), comme `hlth_dm040` en `securite`.
5. **`cohesion_sociale_percue`** : drapeau `rupture_possible_2018` et note sur la hausse des non-réponses.
6. **`solitude`** : aligner le motif de présélection sur la fiche (fréquence de référence « non trouvée »).
7. **`aidance_personne_agee`** : drapeaux `question_non_posee_2012` et retrait de `pas_d_enquete_2003`.
8. **`privation_loisirs`, `privation_sorties_proches`** : champ « 16 ans ou plus » (vérifier `ilc_mdes10a` comme `ilc_mdes11a`), lever `champ_age_a_verifier`.
9. **O5** (si la session mère l'accepte) : fiche hors long-list « rencontres avec les proches » (`ilc_scp09`) et variantes publiques `ilc_scp19`/`ilc_scp20` de `benevolat`.
10. Puis `python scripts/preselection.py --dimension liens_bien_etre --maj-fiches`, `verifier_fiches.py --tableau`, `verifier_fiches.py` (0 erreur).

## 10. Questions pour la session mère

1. Qui calcule les deux séries DREES oubliées (O1, O2) : une maintenance M04 (robot) avant la reprise par M05, ou M05 avec le robot de M04 ?
2. Règle de famille pour les opinions sur la société (J1) : familles propres et même recommandation pour `cohesion_sociale_percue` et `optimisme_generations_futures` ?
3. Consigne à donner à M05 `travail` pour les 20 lignes de sa long-list utilisées par `liens_bien_etre` (I4) ?
4. Transmettre SDASSYND_1 (adhésion syndicale, 2000-2025) comme candidat `democratie` (O6) ?
5. Accepter les fiches hors long-list issues des modules EU-SILC exclus en amont (O5), à l'image de `depart_vacances` ?

## Annexe — sources consultées

| Source | Usage |
|---|---|
| `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_mdes02?geo=FR&hhcomp=TOTAL&rskpovth=TOTAL&unit=PC` | `privation_vacances` |
| `…/data/tour_dem_totot?geo=FR&duration=N_GE4&c_dest=WORLD&unit=PC_POP` | `depart_vacances` |
| `…/data/ilc_pw08?geo=FR&unit=PC&isced11=TOTAL&sex=T&age=Y_GE16` | `bonheur_ressenti` |
| `…/data/ilc_pw03?geo=FR&statinfo=AVG&unit=RTG&isced11=TOTAL&domain=OTH&sex=T&age=Y_GE16` | `confiance_autrui` |
| `…/data/ilc_scp01?geo=FR&isced11=TOTAL&age=Y_GE16&sex=T&unit=PC` | `participation_culturelle_sportive` |
| `…/data/ilc_mdes11a?geo=FR&unit=PC&rskpovth=TOTAL&sex=T` ; `…/data/ilc_mdes10a?…&age=TOTAL` | `privation_loisirs`, `privation_sorties_proches` |
| `…/data/ilc_pw06?geo=FR` ; `…/data/ilc_pw01b?geo=FR&statinfo=AVG&isced11=TOTAL&sex=T&age=Y_GE16&unit=RTG` | `soutien_social`, `satisfaction_relations`, sens de la vie |
| `https://ec.europa.eu/eurostat/cache/metadata/en/tour_dem_esms.htm` ; `…/tour_dem_esmsdm_fr.htm` | champ et rupture de `depart_vacances` |
| `https://sdmx.oecd.org/public/rest/data/OECD.WISE.WDP,DSD_HSL@DF_HSL_CWB,1.1/FRA.7_1.PT_POP_Y_GE15._T._T._T.?startPeriod=2000&format=jsondata` (et `FRA.7_1......`, `FRA.7_4.PT_POP_Y_GE16._T._T._T.`) | `soutien_social`, `solitude` ; la clé à 8 positions des fiches est acceptée par l'API ; le format `csvfilewithlabels` n'est pas lisible par l'outil (contenu binaire) |
| `https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/010593281` | `satisfaction_vie` |
| `https://data.drees.solidarites-sante.gouv.fr/explore/dataset/431_le-barometre-d-opinion/information/` | champ métropolitain du baromètre DREES |
| `https://worldhappiness.report/data-sharing/` | licence WHR |
| Refusés à l'outil : `api.insee.fr/melodi` (robots.txt), liste des pièces jointes de l'API DREES (robots.txt), page OCDE *How's Life* (erreur) | — |
| Extraits du robot commités : `docs/sources/series/drees__barometre_*`, `ocde__hsl_*`, `whr__whr26_figure_2_1_france.txt`, `docs/sources/verif_acces/extraits/drees__jeu_431_le-barometre-d-opinion.txt` | valeurs DREES, OCDE, WHR |
