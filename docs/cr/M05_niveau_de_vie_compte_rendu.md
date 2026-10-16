# Compte rendu — M05, fiches indicateurs de la dimension `niveau_de_vie`

Agent de mission M05 (Niveau de vie), 14 octobre 2026, branche `m05-niveau_de_vie`, PR #16 « M05 — fiches indicateurs : niveau_de_vie ». Méthode commune `docs/methodo/33_methode_fiches_M05.md` (v1.1) appliquée sans modification des scripts communs. Détail dans `docs/cr/M05_niveau_de_vie_journal.md`.

## 1. Livrables

| Fichier | Contenu |
|---|---|
| `docs/validation/regles_preselection_niveau_de_vie.csv` | 140 règles ordonnées |
| `docs/validation/preselection_niveau_de_vie.csv`, `preselection_niveau_de_vie_lignes.csv` | 140 groupes ; 11 912 lignes affectées (les 11 821 de la long-list, 0 sans règle, + 91 importées : 86 d'`egalites`, 5 de `planete`) |
| `indicateurs/niveau_de_vie/*.yaml` | 25 fiches (schéma étendu, `socle_v1` vide), 1 285 variantes (dont 3 ajouts manuels du catalogue des séries écartées) |
| `docs/validation/validation_niveau_de_vie.csv` | tableau de validation à 18 colonnes, `decision_leo` vide ; `verifier_fiches.py` : **0 erreur**, 5 avertissements attendus (§2) |
| `docs/cr/maintenance_catalogues_niveau_de_vie.md` | signalements NDV-1 à NDV-10 (statut `a_faire`), à consolider dans la liste partagée |

## 2. Chiffres

- **Long-list** : 11 821 lignes (7 874 éligibles, 3 124 à vérifier, 823 non éligibles). Décisions : 24 lignes en `fiche` (+ 1 fiche hors long-list), 1 271 en `variante_de`, 9 831 écartées en bloc (43 règles motivées), 695 renvoyées à une autre dimension (`travail` 354, `egalites` 249, `logement_cadre_vie` 45, `education` 24, `securite` 19, `planete` 4).
- **25 fiches, 19 familles** : **17 `retenir`**, **6 `retenir_variante`** (pouvoir d'achat par UC, taux de pauvreté à 50 %, pauvreté ancrée 2008, privation sévère, pauvreté ressentie, revenu national par habitant), **2 `ecarter`** (taux d'épargne des ménages : sens ambigu ; IDH : composite hors champ).
- **4 déclaratives** (difficulté à joindre les deux bouts, pauvreté ressentie, satisfaction à l'égard de la situation financière, perception de la hausse de la pauvreté) ; **2 composites** (AROPE, IDH) ; **2 irrégulières à vérifier** (D17 : patrimoine net médian, 5 vagues 2010-2024 ; satisfaction financière, 3 vagues 2013-2022) ; **1 hors long-list** (`pauvrete_percue_hausse`, DREES PE01, valeurs déjà calculées par le robot M04).
- **6 incontournables** (familles du §5 du crosswalk) : pauvreté monétaire relative (`taux_pauvrete_60`, `taux_pauvrete_50`), revenu disponible des ménages (`revenu_disponible_ajuste_habitant`, `niveau_vie_median`), privation matérielle (`privation_materielle_sociale`, `privation_materielle_sociale_severe`) : tous présents et retenus.
- Sous-thèmes : revenus et pouvoir d'achat 5 fiches ; pauvreté monétaire 5 ; pauvreté et exclusion 1 ; privations 2 ; accès à l'alimentation 1 ; pauvreté ressentie 4 ; production et revenu national 3 ; consommation 2 ; épargne et patrimoine 2.
- **Avertissements du vérificateur** : 1 série principale hors catalogue avec preuve (`pauvrete_percue_hausse`) ; 4 lignes EU-SILC (`ilc_li02` par sexe et par âge, `ilc_li31` étrangers et nationaux) gardées en ventilations de `taux_pauvrete_60` alors qu'elles sont séries principales d'écarts construits d'`egalites` (convention D32, attendu).

## 3. Choix structurants

### 3.1 Comptes nationaux (D30)
Les ≈ 7 900 lignes de comptes nationaux et de prix (INSEE `DD_CNA_*` et BDM, Eurostat `nasa_*`, `nama_*`, `naida_*`, `gov_*`, `prc_ppp_*`, Budget de famille) sont traitées **par jeu et par mesure** : écart en bloc motivé des administrations publiques (A5), des secteurs hors ménages (D29 P6), des opérations techniques des ménages (revenus primaires, cotisations, impôts, transferts, CCF…), du patrimoine et des comptes financiers par actif, de la consommation par produit, des niveaux de prix, des comptes trimestriels (conjoncture). Restent **neuf fiches intelligibles** : revenu disponible ajusté réel par habitant, pouvoir d'achat par UC, PIB par habitant, revenu national réel par habitant, consommation individuelle effective par habitant, part des dépenses pré-engagées, taux d'épargne (écarté), patrimoine (valeur nette des comptes en variante de la médiane d'enquête), plus 241 variantes (totaux, autres unités, autres sources).

Le niveau réel par habitant du revenu disponible et de la consommation **n'existe qu'à Eurostat** (`nasa_10_nf_tr` B7G_R_HAB : 21 496 € en 2000, 27 882 € en 2024 ; `nama_10_pc` P41) : l'INSEE ne publie au catalogue que des évolutions (`_PAM_UC`) et des montants totaux. Les principales sont donc Eurostat, la mesure INSEE du débat public (pouvoir d'achat par UC, en évolution) étant une variante de fiche de la même famille.

### 3.2 Familles INSEE / Eurostat
INSEE principal à définition égale (charte §3.5, méthode §4) : taux de pauvreté à 60 % et à 50 %, intensité, niveau de vie médian et premier décile (ERFS rétropolée 1996-2024, sans rupture, préférée à EU-SILC qui a des ruptures en 2001, 2004, 2020 et 2022 (corrigé après l'audit M06, T5 : aucune en 2008) et à la série ODD de la BDM qui s'arrête en 2023) ; privation matérielle et sociale (BDM ODD 1.i2, 2013-2024, préférée à `ilc_mdsd07` 2014-2025 : un an de profondeur contre un an de fraîcheur) ; privation alimentaire (ODD 2.i1) ; PIB par habitant. Eurostat principal faute d'équivalent INSEE : privation sévère, AROPE, pauvreté persistante, ancrée, subjective, satisfaction financière.

### 3.3 Autres choix
- **Pauvreté des enfants** : fiche propre (préoccupation publique propre, D32), bien que ventilation de la pauvreté d'ensemble.
- **Privation alimentaire** (A2) : fiche propre bien qu'élément de la privation matérielle et sociale ; aucune mesure d'insécurité alimentaire (FIES) au catalogue (NDV-7).
- **Pauvreté subjective** : une famille réunit la difficulté à joindre les deux bouts (Eurostat `ilc_sbjp01`, principale ; vérifiée égale à la somme « grande difficulté » + « difficulté » d'`ilc_mdes09`, ce qui raccorde 2004-2009) et l'auto-identification comme pauvre (DREES PE03, modalité 3).
- **Taux d'épargne** : fiche gardée pour la transparence, `sens: ambigu` → `ecarter` (20,03 % en 2020 contre 14,24 % en 2019, confinements).
- **IDH** : `ecarter`, composite santé-éducation-revenu qui double trois dimensions ; repère externe possible.
- **Endettement des ménages** renvoyé à `securite` (exclusion de la dimension : « réserves financières des ménages et surendettement → securite ») ; à défaut A16.

## 4. Rattachements proposés (à trancher au gel 2)

- **Hors de `niveau_de_vie`** (règles `autre_dimension:*`, NDV-2) : salaires, SMIC, pauvreté des travailleurs → `travail` ; dispersion du revenu et du patrimoine, répartition par tranches de revenu, impact des transferts, taux de remplacement des pensions → `egalites` ; privation liée au logement, coût du logement, bancarisation → `logement_cadre_vie` ; modes de garde, personnel de recherche, brevets → `education` ; endettement des ménages, actifs financiers nets rapportés au revenu → `securite` ; intensité du transport, taxes environnementales, revenu agricole → `planete`.
- **Vers `niveau_de_vie`** : les 86 lignes d'`egalites` (niveaux de revenu EU-SILC, maintenance n° 11) et les 5 lignes `ilc_mdes03`, `hlth_dm030` de `planete` (privation alimentaire, maintenance n° 35).

## 5. Erreurs de catalogue et sources manquantes (NDV-1 à NDV-10)

Unité erronée des mesures par habitant de `nasa_10_nf_tr` (NDV-1) ; table de correspondance (NDV-2) ; DREES PE01 et PE02 à cataloguer (NDV-3) ; coordination PE03 avec la correction n° 3 de `securite` (NDV-4) ; libellé d'`ilc_mdho06q` (NDV-5) ; `ilc_li22` ancré 2019 (NDV-6) ; insécurité alimentaire introuvable (NDV-7) ; SRCV Melodi 2020-2025 (NDV-8, complète la n° 8) ; niveaux INSEE manquants : revenu disponible par UC en euros constants, satisfaction financière SRCV, pauvreté des enfants rétropolée, pauvreté en conditions de vie (NDV-9) ; `sdg_10_20` marqué sans donnée France (NDV-10). Aucune exclusion abusive relevée dans la long-list ; les 510 lignes BWA/BWB de l'ERFS non rétropolée sont des valeurs de rupture (maintenance n° 20), écartées en bloc sauf pour la pauvreté des enfants.

## 6. Points à faire vérifier par Léo

1. **Revenu des ménages en deux familles** : niveau macroéconomique par habitant (Eurostat, ajusté des services publics, principal) avec le pouvoir d'achat par UC de l'INSEE en variante (évolution), et niveau de vie médian d'enquête (INSEE) ; toutes deux marquées incontournables. Faut-il plutôt une seule famille « revenu » ?
2. **PIB par habitant** (A12) retenu comme indicateur ordinaire, avec le revenu national réel par habitant comme substitut ; son entrée au socle est à décider au gel 2.
3. **Redondances à arbitrer pour le socle** : AROPE contient la pauvreté à 60 % et la privation sévère ; la pauvreté des enfants est une ventilation de la pauvreté ; la privation alimentaire est un élément de la privation matérielle et sociale ; plusieurs éléments de cette privation sont des fiches de `liens_bien_etre` et `securite` ; les dépenses pré-engagées recoupent le coût du logement.
4. **Taux d'épargne écarté** (sens ambigu) et **IDH écarté** (composite multidimensionnel) : deux écarts de jugement, à confirmer.
5. **Indicateurs subjectifs** : la perception de la hausse de la pauvreté (PE01) plafonne autour de 90 % depuis 2009 ; la satisfaction financière n'a que trois points (2013, 2018, 2022).
6. **Pauvreté ressentie (PE03)** : la modalité 3 est ici, la modalité 1 en `securite` ; la correction n° 3 de la maintenance les additionnerait (NDV-4).

## 7. Questions et propositions pour la session mère

1. Valider le principe « Eurostat principal quand l'INSEE ne publie pas le niveau » (revenu disponible et consommation par habitant), ou demander à M01 une série INSEE en niveau (NDV-9).
2. Trancher les 695 lignes `autre_dimension` (NDV-2), en particulier l'endettement des ménages (`securite` ou hors v1 au titre d'A16) et la bancarisation (`logement_cadre_vie` ou écart).
3. Les opinions du baromètre de conjoncture des ménages sur le niveau de vie **en France** (BDM 000857176, 000857177, 000857188, 000857189) sont en `hors_grille` par P8 (D29) ; elles pourraient rejoindre `niveau_de_vie` comme opinions sur la société (D32), à l'image de PE01.
4. Volume des variantes : les ventilations sont toutes rattachées (1 285 variantes, dont 258 pour `niveau_vie_median` et 225 pour `taux_pauvrete_60`) ; une règle commune « ventilations EU-SILC des séries non principales → écart en bloc » allégerait les fiches sans perte pour le gel 2.
5. Bac à sable partagé : plusieurs agents M05 écrivent dans le même dossier de travail (un fichier de cet agent a été écrasé par celui de `travail`) ; proposer dans la méthode un sous-dossier par agent.

## 8. Pull request

PR #16 vers `main` (https://github.com/leomalherbe/prosperite/pull/16), ouverte le 14/10/2026 par l'API GitHub ; à ne pas fusionner pendant un run du robot (D26).

## 9. Corrections après l'audit M06 (16/10/2026, PR #27)

Agent correcteur, branche `m05-niveau_de_vie-corr`, PR #27 « M05 — niveau_de_vie : corrections après audit ». Audit appliqué : `docs/validation/audit_niveau_de_vie.md` (verdict `corrections_necessaires`), avec les décisions D37 à D40. Détail, sources relues et contrôles : `docs/cr/M05_niveau_de_vie_corrections_journal.md`. Les sections 1 à 8 ci-dessus décrivent l'état de M05 ; les chiffres à jour sont ceux de la présente section.

### 9.1 Corrections appliquées (liste ordonnée de l'audit)

1. **Privation alimentaire** : série principale EU-SILC `ilc_mdes03` (2004-2025, 22 points, ligne de la long-list `planete`), plus longue de 6 ans et plus fraîche d'un an que l'indicateur ODD 2.i1 de l'INSEE (écart au plus 0,2 point sur 2010-2024), qui passe en variante ; ruptures 2020 et 2022.
2. **`ilc_mdho06q`** (privation sévère liée au logement, libellé du catalogue erroné) retiré des variantes de la privation sévère et renvoyé à `logement_cadre_vie`.
3. **IDH** : `retenir_variante` dans la famille du PIB par habitant, jamais au socle (D38 c), `annee_reference: observation`.
4. **Pauvreté ancrée en 2008** : valeurs relues (12,5 % en 2008, 12,1 % en 2019, 15,6 % en 2025), ruptures 2020 et 2022, qui portent toute la hausse ; série toujours publiée.
5. **Perception de la hausse de la pauvreté (PE01)** : rupture possible en 2007, anomalie en 2014, `non_recoupe` et contrôle de plausibilité sur la publication 2025 (D38 b) ; PE02 (évolution future) en variante.
6. **Pauvreté ressentie (PE03)** : rupture possible en 2018, `non_recoupe`, URL de la pièce jointe unique, note alignée sur `securite` (modalité 1 là-bas, modalité 3 ici).
7. **Privation matérielle et sociale** : valeurs de la principale INSEE citées ; la série n'est pas rétropolée (rupture SRCV entre 2019 et 2020 selon l'INSEE).
8. **Transversales** : `annee_reference` des composites ; ventilations par sexe du taux à 60 % renvoyées à `egalites` (D35, 9 lignes) ; `rattachement_propose` des imports ; métadonnées du revenu national ; incontournable porté par la seule principale de chaque famille (D38 d).
9. **Maintenance** : NDV-4 faite, NDV-5 vérifiée, NDV-6 et NDV-10 abandonnées, NDV-11 et NDV-12 nouvelles ; ruptures EU-SILC corrigées (2001, 2004, 2020 et 2022, aucune en 2008).
10. **Décisions D38 et D39** : soldes d'opinion de l'enquête de conjoncture sur le niveau de vie en France en deux fiches `retenir_variante` (D38 j) ; lignes renvoyées par `logement_cadre_vie` et `sante` importées (D38 a).

Non appliqué : l'IDH ajusté aux inégalités en variante (O5), déjà variante d'`egalites/coefficient_inegalite_humaine`.

### 9.2 Chiffres après corrections

- **27 fiches, 18 familles** : **17 `retenir`**, **9 `retenir_variante`** (pouvoir d'achat par UC, taux de pauvreté à 50 %, pauvreté ancrée 2008, privation sévère, pauvreté ressentie, revenu national par habitant, IDH, soldes d'opinion passé et futur sur le niveau de vie en France), **1 `ecarter`** (taux d'épargne, sens ambigu).
- 6 déclaratives, 2 composites (AROPE, IDH), 2 irrégulières (D17), 1 hors long-list (PE01), **4 incontournables** (`taux_pauvrete_60`, `revenu_disponible_ajuste_habitant`, `niveau_vie_median`, `privation_materielle_sociale`).
- Présélection : 149 règles, 11 930 lignes (109 importées) ; 1 282 variantes ; 706 lignes renvoyées à d'autres dimensions (`travail` 354, `egalites` 258, `logement_cadre_vie` 47, `education` 24, `securite` 19, `planete` 4).
- Vérificateur : 0 erreur, 6 avertissements attendus ; `pytest` : 399 réussis. Classeur `docs/validation/classeurs/validation_niveau_de_vie.xlsx` : décisions par défaut 4 `retenu_socle`, 22 `retenu`, 1 `ecarte`.

### 9.3 Désaccords tranchés

J1 (IDH) et J5 (soldes d'opinion) par D38 (c) et (j) ; J3 par D38 (d) ; J2 (deux familles de revenu) et J6 (taux d'épargne écarté) maintenus, comme le recommandait l'auditeur ; J4 : pauvreté ancrée gardée dans la famille du premier décile, avec la dépendance aux ruptures écrite.

### 9.4 Questions pour la session mère

1. Ventilations par sexe : D35 appliqué aux 9 lignes du taux à 60 % (au-delà de la seule ligne citée par l'audit) ; `egalites` doit les importer.
2. Famille `perception_niveau_vie_france` (PE01 principale, soldes en variantes) : substituabilité à confirmer.
3. Identifiants DREES du catalogue M04 (NDV-12, Q6 de l'audit).
4. IDH ajusté aux inégalités : à rapprocher de l'IDH au gel 2 ?
5. Volume des variantes (1 282) : appliquer en bloc la règle D35 sur les ventilations de second rang avant le gel 2 ?
