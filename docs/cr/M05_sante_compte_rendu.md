# Compte rendu — M05, fiches indicateurs de la dimension `sante`

Agents de mission M05 (Santé), 14 et 15 octobre 2026, branche `m05-sante`, pull request « M05 — fiches indicateurs : sante ». Mission commencée le 14/10 (règles, présélection, 41 fiches), interrompue, puis reprise et terminée le 15/10 (contrôle des fiches, 8 fiches ajoutées, maintenance, compte rendu). Méthode commune `docs/methodo/33_methode_fiches_M05.md` (v1.2) appliquée sans modification des scripts communs. Détail dans `docs/cr/M05_sante_journal.md`.

## 1. Livrables

| Fichier | Contenu |
|---|---|
| `docs/validation/regles_preselection_sante.csv` | 117 règles ordonnées |
| `docs/validation/preselection_sante.csv`, `preselection_sante_lignes.csv` | 117 groupes ; 14 188 lignes affectées (les 14 168 de la long-list + 20 importées de `logement_cadre_vie`), 0 sans règle |
| `indicateurs/sante/*.yaml` | 49 fiches (schéma étendu, `socle_v1` vide), 908 variantes |
| `docs/validation/validation_sante.csv` | tableau de validation à 18 colonnes, `decision_leo` vide |
| `docs/cr/maintenance_catalogues.md` | signalements `SAN-1` à `SAN-7` (statut `a_faire`) |

Contrôles : `main` fusionné (`792f1a5`, sans conflit) ; `python scripts/verifier_fiches.py --dimension sante` → **0 erreur**, 11 avertissements, tous « série principale hors catalogue avec preuve » (8 fiches hors long-list, une alerte par composante pour les séries DREES calculées) ; 0 ligne déjà prise par une autre dimension ; `pytest` : 398 réussis.

## 2. Chiffres

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
