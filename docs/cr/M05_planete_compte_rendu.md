# Compte rendu — M05, fiches indicateurs de la dimension `planete`

Agent de mission M05 (Planète, type plafond), 14 octobre 2026, branche `m05-planete`, PR #17 « M05 — fiches indicateurs : planete ». Méthode commune `docs/methodo/33_methode_fiches_M05.md` (v1.1) appliquée sans modification des scripts communs. Détail dans `docs/cr/M05_planete_journal.md`.

## 1. Livrables

| Fichier | Contenu |
|---|---|
| `docs/validation/regles_preselection_planete.csv` | 221 règles ordonnées |
| `docs/validation/preselection_planete.csv`, `preselection_planete_lignes.csv` | 221 groupes ; 21 534 lignes affectées (les 21 533 de la long-list, aucune sans règle, + 1 importée de `logement_cadre_vie`) |
| `indicateurs/planete/*.yaml` | 75 fiches (schéma étendu), 697 variantes |
| `docs/validation/validation_planete.csv` | tableau de validation à 18 colonnes, `decision_leo` vide ; `verifier_fiches.py` : 0 erreur, 2 avertissements (séries hors catalogue avec preuve) |
| `docs/cr/maintenance_catalogues_planete.md` | lignes PLA-1 à PLA-8 (statut `a_faire`), à consolider dans `maintenance_catalogues.md` |

## 2. Chiffres (avant l'audit ; chiffres à jour au §8)

- **Long-list** : 21 533 lignes (15 945 éligibles, 559 à vérifier, 5 029 non éligibles ; Eurostat 21 063 dans 229 jeux, INSEE BDM 194, Melodi 205, M04 71). Affectation : 73 lignes en série principale, 697 en variantes, **20 747 écartées en bloc** (dont 11 059 de bilans énergétiques, 3 067 de pesticides par culture, 2 268 de moyens budgétaires, 1 118 de détail des déchets, 1 650 de sous-catégories des inventaires d'émissions), 16 renvoyées à une autre dimension.
- **75 fiches, 65 familles** : **61 `retenir`**, **9 `retenir_variante`**, **5 `ecarter`** (sens ambigu : communes couvertes par un PPR, races locales menacées, captures de pêche, prélèvements de bois en volume, préoccupation pour l'environnement).
- **38 pressions, 25 résultats** (états des milieux et aléas subis), **12 moyens** (D19) ; 1 déclarative (baromètre DREES, écartée) ; 2 composites (empreinte écologique, empreinte de consommation de l'UE, D18) ; 7 séries irrégulières (D17 : habitats, espèces exotiques envahissantes, érosion, état des eaux de surface et des nappes, gaspillage alimentaire, déchets toutes activités) ; 3 `a_verifier` ; 2 hors long-list (D32).
- **7 incontournables** (concepts du §5 du crosswalk) : émissions de GES du territoire et par habitant, empreinte carbone et par habitant (4 cadres) ; artificialisation, espaces naturels, taux de boisement (« usage des sols », 3 cadres). Tous présents et `retenir` ou `retenir_variante`.
- Sous-thèmes : eau 12 fiches ; biodiversité 9 ; aléas et adaptation 8 ; énergie 8 ; déchets et matières 7 ; pollutions 7 ; sols et forêts 6 ; agriculture et pesticides 5 ; azote et phosphore 5 ; empreintes 4 ; émissions du territoire 3 ; perceptions 1.
- Sources des séries principales des 75 fiches : Eurostat 38, INSEE 23 (BDM, dont 2 INSEE-SDES pour l'empreinte), OCDE 5, ITDD SDES-INSEE 4, et une chacune pour le Citepa, la Footprint Data Foundation, Santé publique France, le SDES et la DREES ; 3 de niveau 2.

## 3. Choix structurants

1. **Émissions et empreinte, deux familles** (méthode §8) : inventaire territorial (INSEE 010596008, 1990-2024) et empreinte (INSEE-SDES 010595981, 1995-2024) en millions de tonnes comme séries principales, parce que les budgets carbone, l'objectif −50 % 2030/1990 et les fourchettes de la SNBC 3 sont exprimés en Mt ; les séries **par habitant** sont des fiches `retenir_variante` (repères par personne). Les émissions nettes (UTCATF inclus) sont une variante ; le **puits de carbone** forme une famille propre (Eurostat CRF 4 : absorption de 60,98 Mt en 2004, 41,18 Mt en 2024).
2. **Énergie** : consommation **finale** et **primaire** en familles distinctes, avec Eurostat (définitions de la directive efficacité énergétique, 2005-2024) plutôt que l'INSEE (2011-2024) ; renouvelables (`sdg_07_40`, 2004-2025), part des fossiles (`nrg_ind_ffgae`) et productivité énergétique (`sdg_07_30`) en familles propres ; la dépendance aux importations (sécurité d'approvisionnement) est écartée en bloc comme hors définition.
3. **Eau** : une famille de **pression** (prélèvements d'eau douce par habitant, WEI+ en variante) et sept familles d'**état** (état écologique des eaux de surface, état chimique des nappes, nitrates, phosphates, pesticides, baignade, eutrophisation marine), plus les flux d'azote et de phosphore à la mer.
4. **Biodiversité** : oiseaux communs spécialistes (INSEE), indice Liste rouge (ODD 15.5.1), aires protégées terrestres (cible de 30 %) avec la protection forte (cible de 10 %) en variante de famille, aires marines, état des habitats et espèces exotiques envahissantes (D17).
5. **Aléas (A14)** : pertes économiques (Eurostat), communes reconnues en catastrophe naturelle pour inondation et pour sécheresse (ITDD 1991-2024), événements naturels très graves (INSEE), jours de canicule (Santé publique France) avec la part de population exposée à la chaleur (OCDE, importée de `logement_cadre_vie`), sécheresse des écosystèmes (Eurostat).
6. **Ventilations fines écartées en bloc** (sous-catégories CRF et NFR, croisements gaz × secteur, composantes des bilans) pour garder des listes de variantes lisibles ; les totaux par gaz, par grand secteur, par polluant, par usage et par mode de traitement restent en variantes.

## 4. Rattachements proposés (à trancher au gel 2)

- **Vers `planete`** : OCDE How's Life 9_3 « population exposée à des températures extrêmes » (long-list `logement_cadre_vie`) → famille `chaleur_extreme` (A14).
- **Hors de `planete`** : pollution et problèmes environnementaux du quartier déclarés (`ilc_mddw02`, `ilc_mddw05`, `hlth_dhc120`, 8 lignes) et assainissement (`sdg_06_20`, `env_ww_con`, conformité des stations ITDD, 3 lignes) → `logement_cadre_vie` ; privation alimentaire (`ilc_mdes03`, `hlth_dm030`, 5 lignes) → `niveau_de_vie` (A2).
- **À confirmer dans `planete`** : exposition des animaux d'élevage aux antibiotiques (agriculture, A2, ou santé ?), eaux de baignade (état des eaux ou cadre de vie ?), rendement des réseaux d'eau potable (ressource ou service ?).

## 5. Erreurs de catalogue et sources manquantes (PLA-1 à PLA-8)

Règle D28 mal appliquée par la long-list aux séries pluriannuelles de moins de 10 ans d'étendue (masses d'eau, gaspillage alimentaire : PLA-1) ; deux séries extraites par le robot mais non cataloguées, reprises hors long-list (intensité d'exploitation des forêts de l'OCDE : PLA-2 ; préoccupation pour l'environnement de la DREES : PLA-3) ; sources à rechercher (consommation d'espaces naturels, agricoles et forestiers de l'objectif ZAN, haies, état des stocks halieutiques : PLA-4) ; jeux d'empreinte FIGARO et de bassins hydrographiques classés « sans dimension géographique » (PLA-5) ; exceptions de la table de correspondance (PLA-6) ; unité de l'OCDE 12_8 (kg au lieu de t : PLA-7) ; zone des séries d'émissions et d'empreinte différente entre BDM (`FM_D99_D978`) et Melodi (`FRANCE-F`) (PLA-8).

Lectures impossibles le 14/10/2026 : BDM INSEE (robots.txt, aucune valeur INSEE citée), `sdg_06_40` et `sdg_14_60` (refus 429 du proxy) ; drapeaux non relus pour quatre autres séries Eurostat (marqués dans les fiches).

## 6. Points à faire vérifier par Léo (gel 2)

1. **Totaux ou par habitant** pour les émissions et l'empreinte : les totaux en Mt sont principaux (cibles officielles), mais les séries par habitant (5,3 t de GES en 2024 ; empreinte : repère de 2,3 t en 2050) sont plus parlantes ; une seule des deux est à cocher au socle.
2. **Masses d'eau et gaspillage alimentaire** retenus malgré l'exclusion de la long-list (4 et 5 points, D28) ; ce sont les indicateurs de référence de la qualité des rivières et des nappes et de la cible ODD 12.3.
3. **Aléas subis dans un indice de prospérité** : sept fiches de sens `bas` qui pénaliseront des années de crues, de canicules ou de sécheresse sans lien avec les pressions exercées ; des moyennes glissantes (en variante pour les pertes économiques et la sécheresse) seraient plus stables.
4. **Moyens budgétaires écartés** (dépenses de protection de l'environnement, écotaxes, financement climat international, obligations vertes : 2 268 lignes) au titre de la charte §3.4, alors que D19 admet des moyens physiques adossés à une cible ; à confirmer.
5. **Séries dont la lecture demande une précaution** : HRI1 des pesticides (chute de 111 à 59 entre 2018 et 2019, à expliquer), émissions de CO2 des voitures neuves (rupture WLTP en 2017), déchets municipaux (saut de 2016 sans drapeau, valeurs estimées), excédent de phosphore devenu négatif en 2023.
6. **Seule mesure déclarative** (préoccupation pour l'environnement, DREES, 2000-2025) écartée pour sens ambigu ; la retenir comme contexte ou indicateur d'adhésion relève d'un choix de Léo.

## 7. Questions et propositions pour la session mère

1. Consolider PLA-1 à PLA-8 dans `maintenance_catalogues.md` ; PLA-1 touche la règle d'éligibilité de `src/pipeline/longlist.py` (D28) et changerait l'éligibilité de séries d'autres dimensions.
2. Le fichier `preselection_planete_lignes.csv` pèse 8,8 Mo (21 534 lignes) ; accepter, ou adapter les scripts communs à une version compressée (`.csv.gz`) pour les grandes dimensions.
3. Proposer dans la méthode commune deux règles pratiquées ici : (a) écart en bloc des ventilations de second rang quand une variante de premier rang porte déjà la même information ; (b) pour une grandeur visée par une cible en volume, total principal et version par habitant en `retenir_variante` de la même famille.
4. Prévoir au contrôle de redondance les recouvrements entre empreinte carbone, empreinte écologique et empreinte de consommation de l'UE, et entre excédent d'azote, ammoniac et nitrates.
5. Les lectures de vérification ont buté sur les limites des sites (BDM INSEE refusée, Eurostat 429 après une vingtaine d'appels) : les valeurs INSEE des fiches restent à confirmer au premier passage du robot.

## 8. Corrections après audit (M06, D34-D40) — branche `m05-planete-corr`, PR #__PR__

Audit : `docs/validation/audit_planete.md` (42 fiches auditées : 23 conformes, 18 à corriger, 1 non vérifiable ; 14 corrections au §9, oublis O1-O3, cohérence I1-I6, désaccords J1-J9). Toutes les corrections sont appliquées ou tranchées ; détail, fichiers et limites : `docs/cr/M05_planete_corrections_journal.md`.

| Fiche ou groupe | Correction |
|---|---|
| `part_espaces_naturels` | étiquettes INSEE inversées (les « proportions » Teruti sont des hectares, les « surfaces » des pourcentages arrondis) : part **recalculée** sur les hectares (D34 : `composantes`, `formule`), 39,95 % en 2000, 40,07 % en 2022, recoupée avec la série arrondie et avec la part artificialisée publiée ; famille propre `espaces_naturels`, principale, incontournable (J1, D38 i) ; PLA-12 |
| six polluants `env_air_emis` | série principale = total « pour tout l'ensemble du territoire » (`NFR_TOT_NAT`), homogène (D40) ; le total de conformité passe en variante ; champ métropolitain documenté (directive (UE) 2016/2284, art. 2 §2) ; COVNM : rupture du total de conformité expliquée (art. 4 §3 d : COVNM agricoles 3B et 3D exclus en 2005 et depuis 2020) ; oxydes d'azote sans rupture |
| `gaspillage_alimentaire` | rupture 2015/2020 (ADEME contre méthode UE) ; série annuelle de 4 points comparables : `retenir_variante` dans la famille `production_dechets` (D38 f, D40) ; PLA-1 corrigée |
| `empreinte_carbone`, `empreinte_carbone_par_habitant` | par habitant principal (D38 h), total en Mt en variante ; valeurs BDM relues |
| `eutrophisation_eaux_marines` | moyenne sur quatre ans en principale (J3), champ ZEE métropolitaine, méthode lue |
| `indice_liste_rouge` | How's Life 12_7 (quatre décimales, 2004-2025) en principale (J4), raccordement 2000-2003 à étudier |
| `emploi_economie_circulaire` (nouvelle) | D39 : moyen en `retenir_variante` dans la famille du taux d'utilisation circulaire ; Eurostat `cei_cie011` (2005-2023) ; séries INSEE et lignes Melodi reçues de `travail` en variantes |
| compléments | `annee_reference` des deux composites ; `composantes`/`formule` de la série DREES (recoupée en 2025) ; drapeaux relus (nitrates, circularité, habitats, bois, races, HRI1 : pic de 2018 expliqué) ; note de `prelevements_eau` ; champ de `jours_canicule` (96 départements, `geo: FM`) |
| lignes reçues (D38 a) | 30 lignes : degrés-jours de refroidissement, répartition modale du fret Eurostat, véhicules électriques de transport en commun (de `logement_cadre_vie`), fret rapporté au PIB (de `niveau_de_vie`), emploi circulaire par pilier (de `travail`) en variantes ; 3 lignes de `niveau_de_vie` écartées avec motif |
| robot (O2) | vague 11 : population concernée et sévérité des canicules (Santé publique France) en variantes avec `preuve` (PLA-10) |

Chiffres après corrections : **76 fiches, 65 familles : 61 `retenir`, 10 `retenir_variante`, 5 `ecarter`** ; 38 pressions, 25 résultats, 13 moyens ; 1 déclarative ; 2 composites ; 5 incontournables (portés par les principales, D38 d : émissions du territoire, empreinte par habitant, artificialisation, espaces naturels, boisement) ; 732 variantes. Présélection : 229 groupes (76 `fiche`, 127 `variante_de`, 23 `ecarte_en_bloc`, 3 `autre_dimension`) ; 21 564 lignes dont 31 importées. Vérificateur : 0 erreur, 2 avertissements attendus. Tests : 399 réussis. Classeur : `docs/validation/classeurs/validation_planete.xlsx` (décisions par défaut : 5 `retenu_socle`, 66 `retenu`, 5 `ecarte`).

Maintenance (`docs/cr/maintenance_catalogues_planete.md`) : PLA-1, PLA-2, PLA-6, PLA-7 précisées ; PLA-9 (feux de forêt), PLA-10 (canicules de Santé publique France), PLA-11 (`for_vol_efa` en m³), PLA-12 (étiquettes Teruti), PLA-13 (exceptions de la table de correspondance pour les lignes échangées).

À trancher : session mère — transfert des deux fiches d'assainissement de `logement_cadre_vie` vers `planete` (D39 ; renvoi maintenu pour éviter un doublon) ; famille d'accueil du gaspillage alimentaire (`production_dechets`) ; protection forte gardée en variante (J7) ; OCDE gardée pour l'intensité d'exploitation forestière (J9). Léo — une seule des deux lectures de l'empreinte et des émissions au socle ; aléas subis dans un indice de prospérité (§6.3).
