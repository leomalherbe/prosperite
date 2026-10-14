# Audit croisé M06 — dimension `securite`

Agent auditeur M06 (n'a pas participé à M05), 14 octobre 2026, branche `m06-securite` créée depuis `origin/main` (`48e2381`, fusion de la PR #7). Matériau audité : 33 fiches `indicateurs/securite/*.yaml`, `docs/validation/validation_securite.csv`, `preselection_securite*.csv`, `regles_preselection_securite.csv`, journal et compte rendu M05, `docs/cr/maintenance_catalogues.md`. Aucune fiche, aucun script ni aucun catalogue n'a été modifié. Le déroulé est décrit dans `docs/cr/M06_securite_journal.md`.

## 0. Avis global : `corrections_necessaires`

Les corrections sont **mineures** : elles ne remettent en cause ni la structure (25 familles), ni les variantes principales, ni les incontournables du crosswalk, qui ont tous une fiche `retenir`. Les données des 22 fiches auditées sont exactes : toutes les valeurs citées dans les motifs et les notes ont été retrouvées à la source. Restent à corriger, avant que Léo ne valide, une erreur de champ non documentée (`tues_route`), trois écarts dont le motif n'est pas un motif de la méthode (`escroqueries`, `destructions_degradations`, `vols_sans_violence`), deux justifications contredites par des données publiques (taux de plainte des vols de véhicules et des cambriolages) et la définition incohérente de `risque_pauvrete_ressenti`, hors échantillon. La liste ordonnée des corrections est au §9.

Contrôle préalable : `python scripts/verifier_fiches.py --dimension securite` donne 0 erreur et 0 avertissement (33 fiches, 25 familles, 20 `retenir`, 4 `retenir_variante`, 9 `ecarter`, 9 déclaratives, 7 incontournables, 182 variantes).

## 1. Échantillon

| Règle (fiche M06 et consigne de la session mère) | Fiches |
|---|---|
| `recommandation: ecarter` (9) | destructions_degradations, escroqueries, vols_sans_violence, victimes_traite, violences_intrafamiliales_enregistrees, violences_physiques_enregistrees, violences_sexuelles_enregistrees, sentiment_insecurite_quartier, tues_ferroviaire |
| `incontournable: oui` (7, dont 1 déjà comptée) | homicides, delinquance_quartier, preoccupation_insecurite_quartier, securite_nuit, depense_imprevue, pauvrete_actifs_liquides (+ sentiment_insecurite_quartier) |
| `a_verifier` (éligibilité) ou `a_etudier` (raccordement) | pauvrete_actifs_liquides, securite_nuit (déjà comptées) ; surendettement, vols_vehicules (+ sentiment_insecurite_quartier) |
| Incontournable contesté | tues_route |
| 20 % des 18 autres fiches, soit 4, tirées au hasard | homicides_conjugaux, solde_situation_financiere_passee, victimes_violences_conjugales, victimes_violences_physiques |

Tirage : `random.seed(20261014)` puis `random.sample(pool, 4)` en Python 3, où `pool` est la liste triée des 15 « autres » fiches qui ne sont pas déjà retenues d'office (les 18 autres moins tues_route, surendettement et vols_vehicules). **22 fiches auditées sur 33.**

## 2. Fiches auditées

Sources lues par WebFetch le 14/10/2026 : API Eurostat (`…/statistics/1.0/data/<code>?…&lang=fr`), BDM INSEE (`bdm.insee.fr/series/sdmx/data/SERIES_BDM/<idbank>`), API Banque mondiale, API data.gouv.fr et pages insee.fr. Fichiers lus dans le dépôt (extraits des robots, sans saisie de valeur) : `docs/sources/series/ssmsi__series_chronologiques.csv`, `ocde__hsl_bien_etre_actuel.csv`, `ocde__odd_16.csv`, `drees__barometre_2000_2025_distributions.csv` et les dictionnaires DREES.

| Fiche | Inclusion | Reco. M05 | Vérifié à la source | Verdict |
|---|---|---|---|---|
| tues_route | contesté | retenir | `sdg_11_40` : 25 valeurs 2000-2024, de 13,3 à 4,6, `b` en 2014, `p` en 2023-2024 ; jeux sources `DEMO_GIND` et `TRAN_SF_ROADRO`. Le champ est **mixte** (voir §4.1). | **a_corriger** |
| homicides | incontournable | retenir | `crim_hom_soff` (victimes) : 17 valeurs 2008-2024 entre 1,03 et 1,60, pic à 1,55 en 2015 ; Banque mondiale `VC.IHR.PSRC.P5` 2000-2023 : écart avec Eurostat de 0,009 à 0,035 sur 2008-2023, la Banque mondiale toujours au-dessus | conforme |
| delinquance_quartier | incontournable | retenir | `ilc_mddw03` : 18 valeurs (2004-2020 et 2023), 22,3 % puis 14,7 %, `b` en 2020, aucune valeur en 2021-2022 | conforme |
| preoccupation_insecurite_quartier | incontournable | retenir_variante | og04_4, modalités 1 et 2 (« beaucoup », « assez »), recalculé sur les distributions DREES : 40,8 % (2014), 37,5 % (2015, minimum), 47,6 % (2023, maximum), 47,1 % (2025) ; saut de +5,6 points en 2018 ; libellé exact de la question | conforme |
| sentiment_insecurite_quartier | écarter, incontournable, a_etudier | ecarter | Inventaire SSMSI : 14 valeurs (2007-2019 et 2021), France métropolitaine, 14 ans ou plus, en nombre. La suite VRS existe pourtant à l'INSEE (§4.4), et la vague 2021 a été collectée à 99 % par téléphone (data.gouv.fr). | **a_corriger** (mineur) |
| securite_nuit | incontournable, a_verifier | retenir | OCDE 10_2 : 20 périodes annuelles 2006-2025 mais 7 valeurs distinctes, dernière valeur 72,02 | conforme |
| depense_imprevue | incontournable | retenir | `ilc_mdes04` : 22 valeurs 2004-2025, de 34,2 % à 28,8 %, `b` en 2020 et en 2022 | conforme |
| pauvrete_actifs_liquides | incontournable, a_verifier | retenir | OCDE 1_6 : valeurs en 2009, 2014, 2017 et 2020, dernière 35,95 ; écart moyen de 3,7 ans, au-dessus du seuil de 1,5 an (D28) | conforme |
| surendettement | a_etudier | retenir | BDM 010594499 : « Situations de surendettement soumises aux commissions », France métropolitaine, nombre de dossiers ; 218 102 (2010), 108 748 (2020), 134 807 (2024) | conforme |
| vols_vehicules | a_etudier | retenir | `crim_off_cat` ICCS05021 : 14 valeurs, de 330,41 (2008) à 198,41 (2024), lacune 2017-2019. Libellé Eurostat : « Vol de véhicule motorisé **ou de ses pièces détachées** ». La justification par la plainte est contredite (§4.2). | **a_corriger** (mineur) |
| destructions_degradations | écarter | ecarter | Inventaire SSMSI : 10 valeurs annuelles 2016-2025, donc éligible selon la charte §3.4 | **a_corriger** (motif, §5.1) |
| escroqueries | écarter | ecarter | Inventaire SSMSI : 10 valeurs 2016-2025, éligible | **a_corriger** (motif, §5.1) |
| vols_sans_violence | écarter | ecarter | ICCS0502 : 1 503,87 (2008), 2 149,68 (2009, soit +42,9 %), 1 813,45 (2010, −15,6 %), 2 118,89 (2013, +17,8 %) ; aucun drapeau | **a_corriger** (champ `sens`, §5.1) |
| victimes_traite | écarter | ecarter | `sdg_16_70` : 16 valeurs, de 1,28 (2008) à 3,11 (2024), aucune en 2015, saut de 1,07 (2014) à 2,28 (2016) | conforme |
| violences_intrafamiliales_enregistrees | écarter | ecarter | Inventaire SSMSI : 10 valeurs 2016-2025 ; les valeurs n'ont pas pu être lues (fichier de 24,6 Mo) | conforme |
| violences_physiques_enregistrees | écarter | ecarter | ICCS020111 : de 293,62 (2008) à 613,21 (2024) ; BDM 010596044 : 2,1 % en 2010 comme en 2018 | conforme (motif à préciser, §3) |
| violences_sexuelles_enregistrees | écarter | ecarter | ICCS0301 : de 35,51 (2010) à 140,75 (2024) ; BDM 010596045 : entre 0,4 % et 0,8 % | conforme |
| tues_ferroviaire | écarter | ecarter | `tran_sf_railvi` : 19 valeurs 2006-2024 (98 puis 63). La mention « hors suicides » n'apparaît pas dans la réponse de l'API, et la fiche la donne déjà comme à vérifier. | conforme |
| homicides_conjugaux | tirage | retenir | `crim_hom_vrel` (partenaire intime) : 10 valeurs 2015-2024 entre 0,15 et 0,19, rien avant 2015 | conforme |
| solde_situation_financiere_passee | tirage | retenir | BDM 000857184 : titre, France métropolitaine, données brutes, mensuelle sans trou depuis janvier 1970 | conforme |
| victimes_violences_conjugales | tirage | retenir | BDM 010596046 : valeurs de 0,2 % à 0,9 %, 2010-2018 puis 2021-2023, rien en 2019-2020 ; champ des 18-75 ans confirmé par l'identifiant Melodi (`AGE=Y18T75`) | conforme |
| victimes_violences_physiques | tirage | retenir | BDM 010596044 : 2,1 % (2010 et 2018), de 1,0 % à 1,2 % en 2021-2023 | conforme (remarque de famille, §5.4) |

**Bilan : 16 `conforme`, 6 `a_corriger`, 0 `non_verifiable`.** Deux éléments seulement n'ont pas pu être vérifiés : les valeurs des séries SSMSI en nombre (fichier trop lourd pour WebFetch ; les périodes l'ont été sur l'inventaire du robot) et l'âge minimal du baromètre DREES (la fiche le donne déjà « à vérifier »). Les champs `type` (tous `resultat`) et `declaratif` des fiches auditées respectent la méthode §4 : `oui` pour les perceptions, `non` pour la victimation, la dépense imprévue et l'épargne.

## 3. Séries enregistrées écartées pour « sens ambigu » : l'argument tient-il ?

| Série | Argument M05 | Constat de l'audit | Jugement |
|---|---|---|---|
| Agressions graves (ICCS020111) | ×2,1 entre 2008 et 2024, contre 2,1 % de victimes dans l'enquête en 2010 comme en 2018 | Le motif compare deux périodes différentes. Sur la même période (2010-2018, enquête CVS), la série enregistrée gagne 26 % (358,67 → 450,77) alors que l'enquête reste à 2,1 %. Sur 2021-2023 (enquête VRS), les deux montent ensemble : +17 % pour la série enregistrée (523,08 → 611,41), de 1,0 % à 1,2 % pour l'enquête. Le taux de dépôt de plainte des victimes de violences physiques hors ménage n'est que de 29,7 % (SSMSI, CVS, dernière valeur 2020). | **Fondé**, mais à reformuler avec des périodes alignées et le taux de plainte |
| Violences sexuelles (ICCS0301) | ×4 entre 2010 et 2024, contre 0,4 à 0,8 % dans l'enquête | Sur 2010-2018, la série enregistrée est multipliée par 2,0 (35,51 → 71,63) et l'enquête passe de 0,4 % à 0,5 %. L'enquête est peu précise (valeurs arrondies au dixième, avec un 0,8 % isolé en 2017) : la preuve repose surtout sur l'écart d'ordre de grandeur. | **Fondé** ; ajouter une source sur la révélation des faits (taux de plainte) |
| Violences intrafamiliales (SSMSI) | hausse liée à la révélation des faits (M04, autres_sources §2.4) | L'argument n'est documenté que par la phrase générale de M04. Sur 2010-2018, l'enquête montre même une baisse des violences conjugales (0,7-0,9 % puis 0,5-0,6 %). La série enregistrée commence en 2016 et ses valeurs n'ont pas pu être lues. | **Fondé**, documentation à compléter |
| Traite (`sdg_16_70`) | dépend de l'effort de détection | Le saut de 1,07 à 2,28 entre 2014 et 2016 est compatible avec un changement de source ou de détection (cause non vérifiée). | **Fondé** |

Le test « enregistré contre enquête » est pertinent. Il est cependant appliqué de façon asymétrique : une série enregistrée qui baisse est gardée en `bas` sans contrôle quand aucune enquête vivante n'existe (cambriolages, vols de véhicules), alors que les taux de plainte ne sont que d'environ 45 à 50 % (§4.2). La donnée de référence pour documenter tous ces jugements existe : les séries SSMSI « Taux de dépôt de plainte » (enquête CVS, 2006-2020, par atteinte), présentes dans l'inventaire du robot et en partie dans la long-list `democratie` (m04-000297, m04-000298). Il faut les citer.

## 4. Erreurs factuelles (sources et valeurs attendues)

1. **`tues_route`, champ du taux.** La formule de `sdg_11_40` se retrouve à l'unité près : tués de `tran_sf_roadro` (FR) ÷ population moyenne de `demo_gind` (FR) × 100 000. Pour 2024 : 3 181 ÷ 68 775 952 = 4,63, publié 4,6 ; même calcul exact pour 2018 (4,8), 2020 (3,8) et 2021 (4,3). Le **numérateur est de champ métropolitain** : chaque année de 2018 à 2024, il est inférieur de 2 à 13 unités à la série INSEE France métropolitaine 010593288 (3 181 contre 3 193 en 2024). Le **dénominateur est la France entière** (68,78 millions, contre 66 479 199 pour la population moyenne 2024 de la métropole, BDM 000067671). Le taux est donc sous-estimé d'environ 3,3 %. Un taux métropolitain cohérent donnerait 3 193 ÷ 66 479 199 = **4,8** en 2024 (5,0 en 2018). Le rapport entre les deux populations varie peu (0,967 en 2018 comme en 2024), donc la tendance est préservée. **Correction attendue** : remplacer `champ_geo_a_verifier` par un drapeau de champ mixte (par exemple `champ_mixte_numerateur_FM_denominateur_FE`), l'écrire dans `geo`/`notes`, réécrire la note de pertinence, et clore la ligne 9 de `maintenance_catalogues.md`. Optionnellement, ajouter une variante calculée 010593288 ÷ 000067671 (2010-2024). Hypothèse non vérifiée : le drapeau `b` de 2014 pourrait venir de l'entrée de Mayotte dans la population FR. `source_organisme` dit « d'après l'ONISR », alors que l'API cite la DG MOVE (base CARE) : à préciser.
2. **`vols_vehicules`, justification par la plainte.** La note affirme que le vol de véhicule est « généralement déclaré puisque la plainte conditionne l'indemnisation ». Les données disent autre chose : le taux de plainte pour « vol ou tentative de vol de la voiture » est de **47,2 %** en 2019 (INSEE, enquête CVS, page 2526026) et de **51 %** dans la dernière valeur 2020 de la base SSMSI (inventaire du robot). La catégorie ICCS05021 comprend en outre les vols de **pièces détachées**, ce que la note ignore. **Correction attendue** : réécrire la note avec ces taux et ce champ. Le sens `bas` ne peut être confirmé qu'après avoir vérifié la stabilité du taux de plainte sur 2006-2020 ; à défaut, le marquer comme hypothèse. La même phrase figure dans `cambriolages_logements` (hors échantillon, §8).
3. **`vols_sans_violence`, cause des sauts.** « Sauts qui traduisent des changements d'enregistrement » est une affirmation sans source : la réponse de l'API ne porte ni drapeau ni note. **Correction attendue** : « cause non documentée », plus le taux de plainte de **26,9 %** pour les vols et tentatives de vols sans violence (SSMSI, CVS, dernière valeur 2020).
4. **`sentiment_insecurite_quartier`, suite VRS.** La suite VRS existe, contrairement à ce que dit la note (« aucune valeur après 2021 », « à cataloguer ») : l'INSEE publie « Sentiment d'insécurité selon l'âge et le sexe — Données annuelles de 2022 à 2024 » (chiffres-clés, 19/12/2025, `https://www.insee.fr/fr/statistiques/fichier/2526402/cond-sec-just-insecur.xlsx`). Cette suite comporte trois indicateurs (au domicile, dans le quartier ou le village, renoncer à sortir), mais sans total d'ensemble (ventilation par sexe et par âge seulement). Son champ (18 ans ou plus, France métropolitaine plus Guadeloupe, Martinique et La Réunion) diffère de celui de la CVS (14 ans ou plus, métropole). Le jeu CVS sur data.gouv.fr (`62029493ff5c2e6d510b42b6`) précise aussi que la vague 2021 a été collectée « quasi exclusivement (99 %) par téléphone » et que le SSMSI déconseille la comparaison avec la vague précédente. **Correction attendue** : note et raccordement mis à jour (la suite existe mais n'est pas comparable), un drapeau pour la collecte téléphonique de 2021, et la ligne 5 de `maintenance_catalogues.md` complétée avec cette adresse. La recommandation `ecarter` peut rester.

## 5. Désaccords de jugement

1. **`escroqueries` et `destructions_degradations` écartées pour leur brièveté.** Avec 10 valeurs (2016-2025), elles remplissent le critère de la charte (§3.4 : au moins 10 points depuis 2000, dernière valeur 2020 ou plus) et la long-list les classe `eligible: oui`. Or la méthode commune (§3) n'admet `ecarter` que pour un sens ambigu, une exclusion de champ ou une série dominée. Deux options :
   - garder `ecarter` avec `sens: ambigu` documenté (taux de plainte de 16,3 % pour les destructions et dégradations de la voiture en 2019 selon l'INSEE ; de 12,8 % pour les escroqueries bancaires en 2020 selon le SSMSI) ;
   - passer à `retenir` avec les drapeaux `debut_2016` et `en_nombre_taux_a_calculer`.

   Pour **`vols_sans_violence`**, le motif dit que la série ne mesure pas les vols : le champ devrait donc être `sens: ambigu` et non `bas`. Variante SSMSI à reconsidérer : la série des victimes de vols sans violence (2016-2025, 10 valeurs, éligible) n'a pas les sauts de 2009-2013.
2. **« Série arrêtée sans relais ⇒ écarter »** (journal M05 §2.8). Cette règle n'est pas dans la méthode commune. `sentiment_insecurite_quartier` (dernière valeur 2021) est éligible selon la charte. L'écart se défend ici (rupture CVS/VRS, collecte 2021 atypique, et le concept est déjà couvert par `delinquance_quartier`), mais c'est à la session mère de l'acter dans la méthode. Les séries CVS d'injures et de menaces écartées en bloc relèvent de la même règle.
3. **Rupture CVS/VRS des quatre séries d'enquête retenues** (`victimes_violences`, `_physiques`, `_sexuelles`, `_conjugales`). Le niveau tombe d'environ 40 % entre 2018 et 2021 (ensemble : 2,5 % puis 1,4 %). Les fiches portent `raccordement: non` et un drapeau. Dans un indice calculé sur une trajectoire, la série brute affichera une amélioration artificielle. Il faut proposer `raccordement: a_etudier` (deux segments, ou un coefficient de passage à rechercher auprès du SSMSI) plutôt que `non`.
4. **Familles imbriquées.** `victimes_violences` (violences physiques ou sexuelles) et ses composantes `victimes_violences_physiques`, `_sexuelles` et `_conjugales` sont quatre familles distinctes, toutes en `retenir` ; de même, `homicides` contient `homicides_conjugaux`. Une configuration qui cocherait tous les `retenir` compterait deux fois les mêmes victimes. Ce n'est pas une erreur au regard de la méthode, mais il faut le signaler à Léo pour le socle (l'ensemble **ou** les composantes) et pour le contrôle de redondance (charte §3.4).
5. **`tues_route` incontournable.** Je suis d'accord avec `non` selon la méthode : parmi les cinq cadres du §5 du crosswalk, seule l'OCDE (10_3) le cite ; l'ODD 3.6 et l'objectif UE 2030 sont des cibles, pas des cadres de bien-être. En revanche, l'arbitrage A6 et l'existence de cibles officielles plaident pour proposer `retenu_socle` à Léo.
6. **Soldes Camme** (`solde_situation_financiere_passee`, principal de sa famille). Il mesure une évolution perçue et non un niveau, ce que la note dit déjà. Pour le socle, `solde_capacite_epargne_actuelle` (un niveau) serait plus cohérent avec la définition de la dimension. Simple remarque.

## 6. Complétude (oublis)

- **Long-list** : les 928 lignes sont toutes affectées. Les 601 lignes éligibles écartées en bloc (aviation 540, activité répressive 50, personnels 8, stupéfiants 1, injures et menaces 2) ont des motifs recevables. Les 19 lignes `a_verifier` sont soit écartées (12 lignes `icw_pov_*`, 3 points), soit dans `securite_nuit` (7 lignes OCDE/Gallup). Tous les codes `crim_off_cat` du catalogue Eurostat pour la France sont traités, ainsi que les jeux `crim_hom_*`, `crim_thb_*`, `ilc_mdes04` à `08` et `ilc_mddw03`.
- **Incontournables du crosswalk** (§5) : homicides, sentiment d'insécurité et criminalité perçue, sécurité économique (dépense imprévue, épargne liquide). Chacun a au moins une fiche `retenir`. Rien ne manque.
- **Oublis et compléments** :
  1. **Enquête VRS 2022 et suivantes** : le fichier INSEE `cond-sec-just-insecur.xlsx` (§4.4) n'est pas catalogué. Les rapports VRS du SSMSI sont des PDF, exclus par D09. Je n'ai trouvé aucun jeu VRS sur data.gouv.fr (recherches « Vécu et ressenti en matière de sécurité » et « victimation VRS » : 0 résultat). L'adresse `statistiques.interieur.gouv.fr` n'a pas pu être lue (accès refusé dans le bac à sable).
  2. **Taux de dépôt de plainte** (SSMSI, CVS 2006-2020) : ce ne sont pas des indicateurs de la dimension, mais ils sont indispensables pour documenter le sens des séries enregistrées (§3). Deux d'entre eux sont dans la long-list `democratie`.
  3. **Long-list `sante`** : les lignes de causes de décès sur les homicides (X85-Y09_Y871 ; jeux `hlth_cd_asdr2`, `hlth_cd_acdr2`, `hlth_cd_ysdr2`) et sur les accidents de transport (V_Y85) n'ont été ni importées ni signalées ; M05 n'a importé que `sdg_16_10`. A6 et l'exclusion de `sante` (« tués et blessés sur la route → securite ») imposent de trancher leur rattachement, pour éviter un double rattachement quand M05 traitera `sante`. Ce sont des jeux régionaux NUTS 2 (D30), et la catégorie « accidents de transport » déborde la route.
  4. **Morts violentes au sein du couple** (étude nationale annuelle du ministère de l'Intérieur) : non trouvé sous forme de fichier (recherche data.gouv.fr : 0 résultat). `homicides_conjugaux` reste donc la seule série.
  5. `ilc_mdes09` (difficulté à joindre les deux bouts) et OCDE 1_5 sont dans `niveau_de_vie`, conformément à `dimensions.yaml` qui ne les cite pas en sécurité. Ce n'est pas un oubli, mais une frontière à garder en tête.

## 7. Cohérence inter-dimensions

- **Identifiants et séries** : aucun identifiant et aucune série (principale ou variante) ne figurent à la fois dans `indicateurs/securite` et `indicateurs/liens_bien_etre`. Aucune ligne de long-list n'est affectée dans les deux présélections (contrôle par script).
- **Concepts voisins dans `liens_bien_etre`** (baromètre DREES : `optimisme_avenir_personnel` OG03_1, `situation_personnelle_bonne`) face à `risque_pauvrete_ressenti` (PE03) et aux soldes Camme : les questions diffèrent, il n'y a pas de doublon, mais c'est à surveiller au contrôle de redondance.
- **`autre_dimension:democratie`** (3 lignes : `crim_pris_cap` ×2, `crim_pris_tri` TRI_PRE) : ce renvoi est cohérent avec le contenu de `democratie` (État de droit, justice). La long-list `democratie` contient déjà des équivalents : taux d'occupation carcérale (BDM 001779317, 001779318 ; 2012-2024) et détenus non condamnés (OCDE ODD 16.3.2, m04-000142 ; 2005-2024). Ce seront des doublons à traiter par M05 `democratie`.
- **`sante`** : `sdg_16_10` est importé comme variante de `homicides` avec `longlist: sante` (correction de table proposée, ligne 2 de la maintenance). La même règle d'exception (« homicide » → `securite`) devrait couvrir les lignes `hlth_cd_*` X85-Y09 (§6).
- **`logement_cadre_vie`** : `ilc_mdes07` (retards de paiement des factures courantes) est une variante de `retards_paiement`. M05 l'a signalé comme indicateur possible de précarité énergétique. Il faut veiller à ce que M05 `logement_cadre_vie` n'en fasse pas une fiche (R1).
- **`egalites`** : les parts de femmes parmi les victimes (ODD 5.i3b, 5.i4b) y restent, comme le veut R3 ; les nombres de victimes (5.i3a, 5.i4a) sont des variantes en sécurité. C'est cohérent.

## 8. Observations hors échantillon (relevées en passant, non auditées à fond)

- **`risque_pauvrete_ressenti`** : la fiche se contredit. `definition`, `libelle` et `source_serie_id` décrivent la seule modalité 1 de PE03, alors que le motif retient l'indicateur « à condition » d'ajouter la modalité 3. Valeurs recalculées et exactes : 32,14 + 7,87 = 40,0 % en 2014, 16,12 + 17,41 = 33,5 % en 2025. Il faut aligner la fiche sur le calcul retenu (en changeant le libellé : « se considèrent pauvres ou estiment risquer de le devenir »), ou bien suspendre la recommandation jusqu'à la correction de M04.
- **`cambriolages_logements`** : les valeurs sont exactes (259,74 en 2008, 381,75 en 2013, 295,47 en 2024, lacune 2017-2019). La même justification par l'assurance est contredite par un taux de plainte de 44,6 % pour « cambriolage ou tentative » en 2019 (INSEE, CVS) et de 52,7 % en 2020 (SSMSI).
- **`blesses_route`** : les valeurs sont exactes (2 726 en 2000, 990 en 2024, sans drapeau). Le motif rattache la série à l'objectif UE 2030, qui ne vise que les blessés **graves** ; la note le reconnaît, le motif devrait le dire aussi.
- **`vols_violence_enregistres`** : les valeurs sont exactes (166,60 en 2008, 190,02 en 2013, 82,81 en 2024).

## 9. Liste ordonnée des corrections (à faire par M05 ou la session mère)

1. `tues_route` : documenter le champ mixte (numérateur métropolitain, dénominateur France entière ; 4,6 publié contre 4,8 en métropole en 2024), modifier `qualite`, `geo`/`notes` et la note de pertinence, clore la ligne 9 de la maintenance (§4.1).
2. `escroqueries`, `destructions_degradations` : remplacer le motif « série courte » par un motif de la méthode, soit `sens: ambigu` avec les taux de plainte, soit `retenir` (§5.1).
3. `vols_sans_violence` : passer à `sens: ambigu`, écrire « cause des sauts non documentée » et citer le taux de plainte de 26,9 % (§4.3, §5.1).
4. `risque_pauvrete_ressenti` (hors échantillon) : aligner définition, libellé et `source_serie_id` sur les modalités 1 et 3, ou suspendre la recommandation (§8).
5. `vols_vehicules` et `cambriolages_logements` : remplacer l'argument de l'assurance par les taux de plainte mesurés (47,2 % et 44,6 % en 2019), et mentionner les pièces détachées pour ICCS05021 (§4.2).
6. Séries d'enquête CVS/VRS retenues : passer de `raccordement: non` à `a_etudier`, avec une note sur la chute d'environ 40 % du niveau (§5.3).
7. `sentiment_insecurite_quartier` : citer la suite VRS de l'INSEE (non comparable), ajouter le drapeau de collecte téléphonique 2021, compléter la ligne 5 de la maintenance (§4.4).
8. Motifs des séries enregistrées écartées : comparer des périodes alignées (2010-2018 : +26 % contre 2,1 % → 2,1 %) et citer les taux de plainte du SSMSI (§3).
9. Maintenance : ajouter le rattachement des lignes `hlth_cd_*` (homicides X85-Y09, accidents de transport V_Y85) de la long-list `sante` (§6).
10. Note pour Léo au tableau de validation : familles imbriquées (ensemble **ou** composantes au socle) et `tues_route` proposé en `retenu_socle` (§5.4, §5.5).

## 10. Questions pour la session mère

1. Faut-il inscrire dans la méthode commune la règle « série arrêtée sans relais ⇒ `ecarter` » (pratiquée par M05 `securite`, absente de `33_methode_fiches_M05.md`) ?
2. Une série courte mais éligible (10 points depuis 2016) peut-elle être écartée pour sa brièveté ? La méthode §3 ne le prévoit pas.
3. Pour les taux de la sécurité routière d'Eurostat, le champ mixte (numérateur métropolitain, dénominateur France entière) est-il acceptable une fois documenté, ou faut-il recalculer un taux métropolitain (D15) ?
4. Quelle règle pour les familles imbriquées (ensemble et composantes, homicides et homicides conjugaux) : familles distinctes avec avertissement de redondance, ou une seule famille ?
5. Faut-il confier à la maintenance M04 le catalogage du fichier INSEE VRS (2022-2024) et des séries SSMSI « Taux de dépôt de plainte » comme séries de contexte ?
