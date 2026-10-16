# Compte rendu — M05, fiches indicateurs de la dimension `sante`

Agents de mission M05 (Santé), 14 et 15 octobre 2026, branche `m05-sante`, PR #20 « M05 — fiches indicateurs : sante ». Mission commencée le 14/10 (règles, présélection, 41 fiches), interrompue, puis reprise et terminée le 15/10 (contrôle des fiches, 8 fiches ajoutées, maintenance, compte rendu). Méthode commune `docs/methodo/33_methode_fiches_M05.md` (v1.2) appliquée sans modification des scripts communs. Détail dans `docs/cr/M05_sante_journal.md`.

## 1. Livrables

| Fichier | Contenu |
|---|---|
| `docs/validation/regles_preselection_sante.csv` | 117 règles ordonnées |
| `docs/validation/preselection_sante.csv`, `preselection_sante_lignes.csv` | 117 groupes ; 14 188 lignes affectées (les 14 168 de la long-list + 20 importées de `logement_cadre_vie`), 0 sans règle |
| `indicateurs/sante/*.yaml` | 49 fiches (schéma étendu, `socle_v1` vide), 908 variantes |
| `docs/validation/validation_sante.csv` | tableau de validation à 18 colonnes, `decision_leo` vide |
| `docs/cr/maintenance_catalogues.md` | signalements `SAN-1` à `SAN-7` (statut `a_faire`) |

Contrôles : `main` fusionné (`792f1a5`, sans conflit) ; `python scripts/verifier_fiches.py --dimension sante` → **0 erreur**, 11 avertissements, tous « série principale hors catalogue avec preuve » (8 fiches hors long-list, une alerte par composante pour les séries DREES calculées) ; 0 ligne déjà prise par une autre dimension ; `pytest` : 398 réussis.

## 2. Chiffres (avant l'audit ; chiffres à jour au §8)

- **Long-list** : 14 168 lignes (12 547 éligibles, 461 à vérifier, 1 160 non éligibles) ; Eurostat 13 705 (dont 8 184 lignes d'activité hospitalière `hlth_co_*` et 3 609 lignes de causes de décès `hlth_cd_*`), BDM 232, Melodi 203, M04 28. Décisions : 41 lignes en `fiche`, 873 en `variante_de`, 13 073 en `ecarte_en_bloc` (11 741 éligibles : activité hospitalière, ressources et dépenses de santé, causes de décès détaillées, en nombre ou par région, catégories détaillées de la santé perçue, raisons personnelles des besoins non satisfaits…), 181 en `autre_dimension` (`travail` 104, `securite` 54, `niveau_de_vie` 12, `egalites` 10, `logement_cadre_vie` 1).
- **49 fiches, 38 familles** : **37 `retenir`**, **11 `retenir_variante`**, **1 `ecarter`** (`decouvertes_vih`, sens ambigu).
- 11 déclaratives (santé perçue bonne et mauvaise, limitations et limitations fortes, années de vie en bonne santé à la naissance et à 65 ans, douleur, manque de médecins perçu, santé des Français perçue dégradée, satisfaction hôpitaux et urgences) ; 1 composite (couverture sanitaire universelle) ; 4 à vérifier (D17 : douleur physique, épisodes dépressifs, pensées suicidaires, obésité) ; 8 hors long-list ; types : 40 résultats, 6 moyens (D19 : densité de généralistes, dépistage, reste à charge, trois vaccinations), 3 pressions (tabac, alcool, antibiotiques).
- **Incontournables** (§5 du crosswalk) : espérance de vie (naissance, 65 ans) ; santé perçue, morbidité, limitations (santé perçue bonne et mauvaise, maladie chronique, limitations et limitations fortes, années de vie en bonne santé à la naissance et à 65 ans) — 9 fiches, toutes `retenir` ou `retenir_variante`.
- Sous-thèmes : comportements et prévention 8 ; causes de décès 6 ; accès aux soins 7 ; mortalité 6 ; santé perçue et limitations 6 ; périnatalité 4 ; espérance de vie 4 ; santé mentale 4 ; perceptions 3 ; maladies infectieuses 1.

## 3. Choix structurants

1. **Eurostat (EU-SILC) principal pour la santé perçue, la morbidité, les limitations et les besoins non satisfaits** : l'INSEE ne publie pas ces niveaux (D35). L'ODD national INSEE 3.i7a (renoncement pour raisons financières) a exactement les valeurs d'Eurostat sur 2010-2023 ; Eurostat est gardé parce qu'il couvre 2008-2025. Les ruptures SRCV de 2020 et 2022 et deux chutes **non signalées** (maladie chronique 2007-2008, besoins non satisfaits 2014-2015) sont documentées (`raccordement: a_etudier`).
2. **Espérance de vie** : Eurostat principal (l'INSEE ne publie que par sexe) ; espérance de vie à 65 ans et années de vie en bonne santé à 65 ans en fiches variantes.
3. **Causes de décès** : une fiche par grand chapitre intelligible (cancers, circulatoire, respiratoire, diabète, chutes, suicide, maladies infectieuses), taux standardisés `hlth_cd_asdr2` (2011-2023) ; les causes détaillées, nombres, taux bruts et moyennes triennales régionales sont écartés en bloc (D35). Homicides et accidents de transport → `securite` (A6), sauf la mortalité infantile par accident de transport, qui reste en `sante` (SEC-1 ; règle corrigée à la reprise).
4. **Mortinatalité spontanée** (Santé publique France, hors long-list) préférée à la mortinatalité totale d'Eurostat, qui comprend les interruptions médicales de grossesse et n'a donc pas de sens univoque.
5. **Opinions et satisfaction (baromètre DREES)** : satisfaction envers les hôpitaux publics et les urgences (R4), état de santé des Français perçu dégradé (opinion sur la société, D32), manque de médecins perçu ; valeurs calculées sur les distributions du robot ; une seule valeur officielle recoupée par série (2025) pour SA05, SA07_1 et SA09_1, aucune pour SA07_2 (D34 incomplet).
6. **Familles** : besoins dentaires séparés des besoins médicaux (non substituables, D35) ; familles imbriquées signalées (mortalité traitable dans la mortalité évitable ; « morts de désespoir » contenant le suicide ; causes de décès contenues dans la mortalité prématurée et évitable).
7. **Écartée** : découvertes de séropositivité VIH (le nombre suit l'effort de dépistage autant que l'épidémie) ; l'incidence estimée du VIH (OCDE 3.3.1) est gardée en variante de la mortalité par maladies infectieuses.

## 4. Rattachements proposés (à trancher au gel 2)

- **Vers `sante`** : `ilc_lvhl01` (état de santé déclaré des 18 ans ou plus par degré d'urbanisation, 20 lignes de la long-list `logement_cadre_vie`) : 16 lignes en variantes de la santé perçue, 4 lignes « moyen » écartées.
- **Hors de `sante`** (181 lignes) : `travail` (enquêtes `hsw_*` sur la santé au travail) ; `securite` (homicides, accidents de transport, lignes déjà importées par `securite`) ; `niveau_de_vie` (privations par niveau de limitation `hlth_dm070` à `hlth_dm110`) ; `egalites` (lignes de santé perçue et de besoins non satisfaits par quintile, écart d'emploi lié au handicap, déjà utilisées par ses écarts construits) ; `logement_cadre_vie` (ODD national 7.i1, précarité énergétique).
- **Frontières à surveiller** : `deces_pollution_air` (résultat de santé ici ; exposition en `logement_cadre_vie`, émissions en `planete`) ; `satisfaction_soins_hopital` et la confiance dans l'hôpital rangée en `democratie` ; `mortalite_chutes` (accidents de la vie courante, absents du contenu de toutes les dimensions) ; DREES SA13 (confiance dans ce que disent les médecins), à signaler à `democratie`.

## 5. Maintenance (SAN-1 à SAN-7)

OCDE ODD 3 : séries 3.4.1, 3.8.1, 3.b.1 et variantes à cataloguer (1) ; Eurostat `sdg_03_42` : modalités TRT et PRVT (2) ; DREES : questions SA05, SA07_*, SA09_*, SA27 à calculer et cataloguer, modalité ajoutée en 2014 à SA07_* (3) ; table de correspondance v0→v1 (ODD 7.i1, `hsw_*`, `hlth_dm*`, `ilc_lvhl01`, mortalité infantile par transport) (4) ; Santé publique France : mortinatalité, chutes des 65 ans ou plus, jeu cardio-neurovasculaire mal lu par le robot (5) ; anomalie d'intervalle de confiance des pensées suicidaires (6) ; sources à rechercher : accessibilité potentielle localisée, médecin traitant, délais, activité physique, fruits et légumes, diabète traité, complémentaire santé, reste à charge par habitant (7). Aucune exclusion abusive dans la long-list. Préfixe `SAN-` gardé parce que les fiches le citent ; renumérotation à la fusion (D33).

## 6. Points à faire vérifier par Léo (priorité au gel 2)

1. **Ruptures de SRCV (2020, 2022) et chutes non signalées** : elles touchent 10 fiches de santé perçue, limitations, morbidité, besoins non satisfaits et années de vie en bonne santé ; ces séries sont retenues, mais leur trajectoire récente n'est lisible qu'après raccordement.
2. **Séries irrégulières à 4 points** (épisodes dépressifs, pensées suicidaires : 2005, 2010, 2017, 2021) : seules mesures de prévalence de la santé mentale ; dernière valeur 2021.
3. **Fiches à la marge du contenu** : consommation d'antibiotiques, natalité des adolescentes (`hors_contenu_cite`).
4. **Séries calculées sur le baromètre DREES** (4 fiches, `geo = FM`) : un seul recoupement officiel (2025), aucun pour les urgences ; et rupture possible de 2014 des questions de satisfaction.
5. **Choix pour le socle** : ensemble **ou** composantes (mortalité évitable ou traitable ; suicide ou « morts de désespoir » ; causes de décès et mortalité prématurée), bonne **ou** mauvaise santé perçue.
6. **Valeurs non lues** : `deces_pollution_air` (API Eurostat refusée deux fois, HTTP 429) ; mortinatalité 2014-2023 (API Odissé non lue) ; vaccination HPV avant 2023.

## 7. Questions pour la session mère

1. Les accidents de la vie courante (chutes) n'apparaissent dans le contenu d'aucune dimension : `sante` (choix fait ici) ou `securite` ?
2. Faut-il admettre comme fiche une opinion DREES courte mais pertinente (SA06_1 et SA06_3, égalité d'accès aux soins selon le revenu et le lieu de vie, 7 vagues annuelles 2018-2025, non éligibles) quand elle atteindra 10 points ?
3. La modalité « je n'y suis jamais allé » ajoutée en 2014 aux questions de satisfaction DREES doit-elle sortir du dénominateur (satisfaction des usagers) ? Les fiches suivent aujourd'hui la convention du tableau officiel (non-réponses et non-usagers au dénominateur).
4. Le classeur Excel de validation de `sante` reste à produire (`scripts/classeur_validation.py`, fusionné sur `main`) : à faire par la session mère au gel 2, comme pour les autres dimensions.

## 8. Corrections après audit (M06, D38-D46) — branche `m05-sante-corr`, PR #33

Audit : `docs/validation/audit_sante.md` (49 fiches auditées : 35 conformes, 14 à corriger ; 7 oublis ; 9 points de cohérence ; 8 désaccords de jugement ; 10 corrections au §10), réponses de la session mère en D43. Toutes les corrections F et A et les oublis O1 à O7 sont traités ; détail, fichiers et limites : `docs/cr/M05_sante_corrections_journal.md`. Une collecte ciblée du robot (vague 13, 16/10/2026) a lu sept jeux de Santé publique France fermés à l'outil de lecture.

| Fiche | Correction |
|---|---|
| `satisfaction_soins_hopital`, `satisfaction_urgences` (D39, D43) | parts recalculées hors « jamais allé.e » : (modalités 1 + 2) / (100 − modalité 6) ; hôpitaux publics 75,2 % (2014) → 63,7 % (2025), urgences 57,0 % → 44,1 % ; `rupture_2014`, `non_recoupe` (D38 b), plausibilité contre la valeur officielle 2025 (61,29 %) |
| `deces_pollution_air` (F) | 18 valeurs lues (61 pour 100 000 en 2005, 22 en 2023, 2006 absent) ; contrefactuel 5 µg/m³ ; saut de 2013-2014 (53 → 34) en `raccordement: a_etudier` |
| `prevalence_diabete` (nouvelle, O1, D43) | Santé publique France, taux standardisé 4,69 % (2010) → 5,24 % (2023), famille propre, `retenir`, sens bas, `depend_du_depistage` |
| `vaccination_hpv` (F2, O2, J3) | série nationale de Santé publique France (schéma complet des filles de 16 ans, 2011-2025 : 44,7 % en 2023, 50,7 % en 2025) en principale, OCDE 3.b.1 et garçons en variantes |
| `episodes_depressifs`, `pensees_suicidaires`, `tabagisme_quotidien` (F3, O3, D43) | `geo: FM` (18-75 ans, métropole) ; édition 2024 du Baromètre en **nouvelle série** (variante, `raccordement: a_etudier`) : 15,6 %, 5,2 %, 17,4 % des 18-79 ans ; `episodes_depressifs` incontournable (santé mentale, D43) |
| `esperance_vie_65` (J1, O6, D43) | principale `demo_mlexpec` âge 65 ans (1998-2024), `hlth_hlye` en variante (écart de 0,1 à 0,5 an depuis 2014) |
| `obesite` (F1) | `frequence: irreguliere` (6 vagues) |
| 4 fiches variantes (D38 d) | `incontournable: non` : espérance de vie et années de vie en bonne santé à 65 ans, limitations fortes, santé perçue mauvaise |
| `sante_francais_percue_degradee`, `manque_medecins_percu` (D38 b, D45) | `non_recoupe`, plausibilité écrite, formules avec la convention de dénominateur |
| `vaccination_grippe_seniors`, `depistage_cancer_colorectal` (O2, O4) | séries de Santé publique France en variantes (année Eurostat N = campagne N-1/N ; campagnes de dépistage glissantes de deux ans) |
| `mortalite_chutes`, règles `ilc_lvhl01` (D39) | rattachements tranchés par D39 cités |
| mineurs (§7.5, J4) | densité de généralistes, mortalité traitable, VIH (statut E), Mayotte en 2014, natalité des adolescentes (estimations divergentes ; taux de fécondité des 15-19 ans de l'état civil en variante), champ SRCV des 10 fiches EU-SILC (D15) |

Lignes renvoyées (D38 a, D46) : les 20 lignes `ilc_lvhl01` reçues de `logement_cadre_vie` sont importées (16 variantes, 4 écartées) ; aucune autre ligne n'est renvoyée à `sante` ; les 181 lignes renvoyées par `sante` sont toutes reprises par leurs destinataires (`travail` 104, `securite` 54, `niveau_de_vie` 12, `egalites` 10, `logement_cadre_vie` 1), avec un motif ; deux renvois hors long-list sont tracés (décès attribuables à la chaleur → `planete`, A14, D43 ; confiance dans les médecins → `democratie`).

Socle proposé (D41, `socle_propose: oui`, 8 fiches) : `esperance_vie_naissance`, `esperance_vie_sans_incapacite`, `sante_percue_bonne`, `maladie_chronique`, `limitations_activite`, `episodes_depressifs` (les 6 incontournables), `besoins_soins_non_satisfaits` (accès aux soins), `tabagisme_quotidien` (comportements et nutrition).

Chiffres après corrections : **50 fiches, 39 familles : 38 `retenir`, 11 `retenir_variante`, 1 `ecarter`** ; 11 déclaratives ; 1 composite ; 4 « à vérifier » ; 10 hors long-list ; 6 incontournables ; 921 variantes ; types : 41 résultats, 6 moyens, 3 pressions. Présélection : 122 groupes (50 `fiche`, 43 `variante_de`, 21 `ecarte_en_bloc`, 8 `autre_dimension`) ; 14 189 lignes, dont 21 importées. Vérificateur : 0 erreur, 65 avertissements attendus (50 « socle_propose hors schéma » tant que le vérificateur n'est pas mis à jour, 15 séries hors catalogue avec preuve) ; `pytest` : 403 réussis.

Liste de maintenance : SAN-3, SAN-4 et SAN-7 précisées (`docs/cr/maintenance_catalogues.md`) ; SAN-8 (jeux de Santé publique France lus par la vague 13), SAN-9 (`demo_mlexpec` âge 65 ans), SAN-10 (décès attribuables à la chaleur → `planete`), SAN-11 (SA13 → `democratie`), SAN-12 (`demo_frate` → `sante`) dans `docs/cr/maintenance_catalogues_sante.md`.

Réponses aux questions du §7 : 1. chutes → `sante` (D39) ; 3. modalité « jamais allé » exclue (D39, D43) ; 4. classeur régénéré par la session mère. La question 2 (SA06) reste ouverte.

À trancher : **session mère** — incontournable « santé mentale » porté par la seule `episodes_depressifs` (le suicide porterait le socle à 9) ; principale nationale de la vaccination HPV (J3) ; série d'état civil en principale de la natalité des adolescentes (J4) ; non-réponses au dénominateur des satisfactions ; numéro de la vague 13 du robot à la fusion. **Léo** — rupture de 2014 des satisfactions, saut de 2014 des décès attribuables aux PM2,5, séries du Baromètre 2024 non raccordées (dernière valeur comparable 2021 pour la santé mentale), sens bas de la prévalence du diabète traité, choix du tabac pour le socle « comportements et nutrition ».
