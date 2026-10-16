# Compte rendu — M05, fiches indicateurs de la dimension `travail`

Agent de mission M05 (Travail et emploi), 14 octobre 2026, branche `m05-travail`, PR #15 « M05 — fiches indicateurs : travail ». Méthode commune `docs/methodo/33_methode_fiches_M05.md` (v1.1) appliquée sans modification des scripts communs. Détail dans `docs/cr/M05_travail_journal.md`.

## 1. Livrables

| Fichier | Contenu |
|---|---|
| `docs/validation/regles_preselection_travail.csv` | 123 règles ordonnées |
| `docs/validation/preselection_travail.csv`, `preselection_travail_lignes.csv` | 123 groupes ; 6 525 lignes affectées (les 6 520 de la long-list + 5 importées de `niveau_de_vie`), 0 sans règle |
| `indicateurs/travail/*.yaml` | 37 fiches (schéma étendu, `socle_v1` vide), 1 675 variantes |
| `docs/validation/validation_travail.csv` | tableau de validation à 18 colonnes, `decision_leo` vide ; `verifier_fiches.py --dimension travail` : **0 erreur**, 2 avertissements (fiches DREES hors catalogue, avec preuve), 0 ligne déjà prise ailleurs |
| `docs/cr/maintenance_catalogues_travail.md` | signalements `TRA-1` à `TRA-10` (statut `a_faire`), à consolider dans la liste partagée |

## 2. Chiffres (avant l'audit ; chiffres à jour au §8)

- **Long-list** : 6 520 lignes (5 327 éligibles, 253 à vérifier, 940 non éligibles) ; Eurostat 4 040, Melodi 2 014 (dont `DD_EEC_SERIES` 1 673), BDM 452, M04 14. Décisions : 36 lignes en `fiche`, 1 671 en `variante_de`, 4 161 en `ecarte_en_bloc` (3 131 éligibles : structures par profession, branche, territoire, effectifs en nombre, comptes nationaux, statistiques d'entreprises, enquête sur la structure des salaires détaillée), 652 en `autre_dimension`.
- **37 fiches, 28 familles** : **24 `retenir`**, **8 `retenir_variante`**, **5 `ecarter`**.
- 3 déclaratives (préoccupation pour le chômage, risque de chômage perçu, satisfaction au travail) ; 0 composite ; 3 à vérifier (D17 : bas salaires OCDE, bas salaires SES, risques psychosociaux) ; 2 hors long-list (baromètre DREES OG04_6 et SDRICHOM).
- **Incontournables** (§5 du crosswalk) : taux d'emploi (3 fiches de la famille) et longues durées de travail ; tous deux `retenir`. Le taux de chômage n'atteint pas trois cadres (`incontournable: non`).
- **Ventilations signalées à `egalites`** : 361 lignes en `autre_dimension:egalites`, dont 51 déjà reprises par `egalites`, **305 ventilations par sexe** des taux d'emploi, de chômage et de la part du temps partiel (écarts déjà au catalogue d'`egalites` : `ecart_emploi_fh`, `ecart_chomage_fh`, `ecart_temps_partiel_fh`), 3 lignes de taux d'emploi par nationalité (`sdg_08_30a`) et 2 d'inactivité pour responsabilités familiales (`sdg_05_40`). Les ventilations par sexe des autres mesures (NEET, sous-emploi, halo, contrats temporaires, accidents…) restent en variantes ici, faute d'écart au catalogue d'`egalites`.
- Sous-thèmes : chômage 6 fiches ; emploi 5 ; qualité et sécurité de l'emploi 9 ; conditions et santé au travail 9 ; rémunération 4 ; sous-emploi et temps partiel 3 ; satisfaction 1.

## 3. Choix structurants

1. **INSEE et Eurostat : une famille par concept, INSEE en principale.** Le taux d'emploi, le taux de chômage, le NEET, le sous-emploi, l'activité, la part du temps partiel et celle des CDD et de l'intérim prennent les **séries longues rétropolées** de l'enquête Emploi (Melodi `DD_EEC_SERIES`, 1975 ou 1982 à 2025, champ France entière). La page INSEE de ces séries (lue le 14/10) indique que les ruptures de **2003**, **2013** et **2021** y sont corrigées, alors que toutes les séries Eurostat lues portent le drapeau « définition différente » (« d ») depuis 2021. Eurostat et la BDM trimestrielle sont des variantes ; Eurostat devient une **fiche variante** quand la lecture diffère : taux d'emploi des 20-64 ans (cible de 78 % en 2030), temps partiel involontaire rapporté au temps partiel, emploi temporaire subi, contrats très courts.
2. **Ruptures** documentées dans `qualite` et `raccordement` : saut de 2003 (longues durées 8,0 % → 13,4 %, dimanche 9,7 % → 12,9 %) ; **chute non signalée de 2013** du travail de nuit (7,1 % → 3,7 %, nouveau questionnaire) ; 2021 (temps partiel involontaire 36,9 % → 27,2 %, emploi temporaire subi 7,3 % → 5,8 %) ; rupture de 2020 de `ilc_lvhl36` (12,0 % → 19,3 %).
3. **Séries trimestrielles** : principales seulement sans série annuelle de même définition (taux d'emploi en EQTP ; part des personnes contraintes sur leur offre de travail, mesure INSEE de la sous-utilisation). Le **taux de chômage de longue durée**, publié par l'INSEE en trimestriel seulement, est **calculé** sur les séries longues annuelles (chômeurs depuis un an ou plus / actifs, 1975-2025) ; de même la part des CDD et de l'intérim (somme de deux parts). Calculs confiés au pipeline (TRA-2).
4. **Accidents du travail : deux familles.** `accidents_travail` (indice de fréquence des accidents avec arrêt, Assurance maladie, 2005-2024) et `accidents_travail_mortels` (Eurostat `hsw_n2_02`, 2008-2024 ; `sdg_08_60` en variante, mêmes valeurs depuis 2010). Motifs : un décès n'est pas substituable à un accident avec arrêt (méthode §1, concepts complémentaires) et les accidents mortels portent une préoccupation publique propre (§9, D32). La principale non mortelle est nationale plutôt qu'européenne : la série ESAW `hsw_n2_01` varie de 3 443,59 (2008) à 2 303,37 (2009) pour 100 000 et compte quatre ruptures.
5. **Écartées** : taux d'activité, part du temps partiel, durée hebdomadaire moyenne (sens ambigu) ; maladies professionnelles reconnues (en nombre, dépend de la reconnaissance) ; demandeurs d'emploi (série administrative en nombre, dominée par le chômage BIT).
6. **Contenu de la dimension couvert** : emploi, chômage, chômage de longue durée, sous-emploi, halo, NEET ; contrats courts, temps partiel subi, bas salaires, surqualification, passages au chômage (A15) ; accidents, expositions, longues durées et horaires atypiques (D27) ; satisfaction au travail. Exclus conformément à `dimensions.yaml` : temps libre et conciliation des temps (lignes `lfst_hh*`, raisons d'inactivité, A4), écarts femmes-hommes (→ `egalites`).

## 4. Rattachements proposés (à trancher au gel 2)

- **Vers `travail`** (5 lignes importées de `niveau_de_vie`) : salaire net moyen en EQTP en euros constants (Melodi `DS_DERA_PRIVE_SERIES_LONGUES`, série principale de `salaire_net_moyen_reel`) et trois variantes (temps complet depuis 1951, indice du pouvoir d'achat, OCDE 2_8), au titre de la « rémunération » de la définition de `travail` ; `sdg_01_41` en variante de `pauvrete_en_emploi` (même définition que `ilc_iw01`). Le revenu des ménages reste à `niveau_de_vie`, la dispersion des salaires à `egalites`.
- **Hors de `travail`** (652 lignes) : `egalites` 361 (§2) ; `securite` 171 (`lfsa_ugadra`, chômeurs selon l'indemnisation, comme `ilc_li70b` renvoyé par `egalites`) ; `education` 96 (part de chaque diplôme dans la population de l'enquête Emploi, formation des salariés) ; `liens_bien_etre` 20 (lignes déjà reprises, consigne I4 de l'audit M06) ; `planete` 4 (emploi de l'économie circulaire, ODD 12).
- **Frontières à surveiller** : `menages_tres_faible_intensite_travail` (composante de l'AROPE, `niveau_de_vie`) ; `pauvrete_en_emploi` (taux de pauvreté par statut d'activité) ; `sous_utilisation_main_oeuvre` recoupe chômage, halo et sous-emploi (famille imbriquée, à traiter au contrôle de redondance).

## 5. Maintenance (TRA-1 à TRA-10)

DREES OG04_6 et SDRICHOM à cataloguer et calculer (1) ; formules du pipeline (2) ; unité des mesures `PT_*` de Melodi, dont le libellé est ambigu, à confirmer sur les valeurs (3) ; exceptions de la table v0→v1 pour les lignes renvoyées ailleurs (4), les salaires (5) et la pauvreté en emploi (6) ; Assurance maladie : accidents mortels du régime général et taux de maladies professionnelles (7) ; source nationale des conditions de travail, DARES (8, non trouvé) ; métadonnées Eurostat à lire et valeurs refusées à l'outil (9) ; chute non signalée de 2013 du travail de nuit (10). Aucune exclusion abusive dans la long-list.

## 6. Points à faire vérifier par Léo (priorité au gel 2)

1. **Séries longues de l'INSEE en principale** (rétropolées, « fondées sur des hypothèses » selon l'INSEE) plutôt que les séries Eurostat ou BDM : c'est le choix qui structure 9 familles.
2. **Salaire moyen réel dans `travail`** (rémunération = qualité de l'emploi) plutôt que dans `niveau_de_vie` ; même question pour la pauvreté des personnes en emploi.
3. **Exposition aux risques psychosociaux** retenue avec 3 points non comparables (49,0 % en 2007, 60,8 % en 2013, 53,5 % en 2020, définitions différentes puis rupture) : seule mesure des conditions de travail psychosociales au catalogue ; à garder faute de mieux ou à suspendre jusqu'à une source DARES.
4. **Sécurité de l'emploi ressentie** : la préoccupation pour le chômage (DREES, 2000-2025) mêle inquiétude personnelle et opinion sur le pays ; la question SDRICHOM (risque pour soi ou un proche) est plus juste mais reste à calculer.
5. **Ruptures lourdes** de `transitions_temporaire_permanent` (2020), `temps_partiel_subi` et `emploi_temporaire_subi` (2021), `travail_nuit` (2013, non signalée) : retenues, mais leur trajectoire n'est lisible qu'après raccordement.
6. **Écarts** : taux d'activité, part du temps partiel et durée moyenne du travail (sens ambigu), demandeurs d'emploi (série administrative).

## 7. Propositions pour la session mère

1. Corriger l'exclusion de `travail` dans `indicateurs/dimensions.yaml` : elle cite encore « longues durées de travail, horaires atypiques » comme hors v1, contrairement au contenu de la dimension et à D27.
2. Acter la **règle des séries trimestrielles** appliquée ici (principale seulement sans série annuelle de même définition ; sinon calcul sur les séries annuelles) et l'étendre à `niveau_de_vie` (comptes trimestriels).
3. Acter la règle des **ventilations par sexe** : `autre_dimension:egalites` quand l'écart est au catalogue d'`egalites`, variante sinon ; `egalites` pourrait construire de nouveaux écarts sur les séries longues de l'INSEE (sous-emploi, NEET, CDD), plus longues que ses composantes Eurostat.
4. Trancher la frontière **rémunération** entre `travail` et `niveau_de_vie` avant que M05 `niveau_de_vie` ne commence (TRA-5, TRA-6).
5. Faire relire par l'audit M06 en priorité : les deux formules (TRA-2), l'unité des mesures `PT_*` (TRA-3) et la famille `accidents_travail` (choix de la source nationale).

## 8. Corrections après audit (M06, D34-D40) — branche `m05-travail-corr`, PR #31

Audit : `docs/validation/audit_travail.md` (37 fiches auditées : 23 conformes, 12 à corriger, 2 non vérifiables ; 4 oublis ; 7 points de cohérence ; 7 désaccords de jugement ; 10 corrections au §12). Les dix corrections et les oublis O1 à O3 sont appliqués (O4 : signalé à `niveau_de_vie`, TRA-14) ; détail, fichiers et limites : `docs/cr/M05_travail_corrections_journal.md`. Une collecte ciblée du robot (15/10/2026, `scripts/collecte_travail.py`) a lu les séries Melodi, les séries BDM de contrôle, 18 jeux Eurostat et les jeux de l'Assurance maladie ; la vague 11 du robot (16/10/2026) a calculé la question SDRICHOM du baromètre DREES.

| Fiche | Correction |
|---|---|
| onze fiches Melodi (TRA-3) | séries lues et comparées à la BDM : les mesures `PT_*` sont des taux (à 0,1 point des séries BDM) ; le code `EMPSTA=3` des lignes NEET est un artefact (chômeurs compris) ; valeurs et contrôles dans les notes |
| `taux_emploi_20_64` (F1) | principale `lfsi_emp_a` 20-64 ans (2003-2025, 23 points), `sdg_08_30` en variante, raccordement inutile ; incontournable porté par la seule principale de la famille (D38 d), comme pour `taux_emploi_eqtp` |
| `halo_chomage` (J1) | principale BDM 011818623 (15-64 ans, trimestrielle 2003-2026 : 3,8 % en 2003, 4,5 % en 2025), Melodi (15 ans ou plus, 2014-2025) en variante |
| `accidents_travail_mortels` (D40, O2, F6) | série nationale de l'Assurance maladie : décès par accident du travail pour 100 000 salariés du régime général, 2015-2024 (2,90 → 3,67), calculée sur deux jeux et recoupée (733 décès en 2019, 738 en 2022, 759 en 2023) ; hausse de 2019 liée à la prise en compte des malaises ; Eurostat `hsw_n2_02` (2008-2024) en variante |
| `exposition_risques_sante_physique`, `problemes_sante_lies_travail` (nouvelles, O1, D39) | modules ad hoc `hsw_exp2` (74,9 % en 2020) et `hsw_pb1` (8,3 % en 2020) importés de la long-list `sante`, familles propres, `retenir` avec trajectoire non comparable (J2) |
| `preoccupation_chomage`, `risque_chomage_percu` (J7, D38 b) | deux familles : opinion sur la société (63,5 % en 2025) et risque perçu pour soi ou un proche (SDRICHOM, 28,7 % en 2025, principale de `insecurite_emploi_percue`) ; `retenir` avec `non_recoupe` et plausibilité contre les publications de la DREES |
| `taux_chomage_longue_duree`, `part_emploi_temporaire` (D34) | formules normalisées et recoupements (BDM, Eurostat ; parts publiées par l'INSEE : 11,0 % en 2017, 10,3 % en 2022, 9,5 % en 2024) |
| `contrats_tres_courts`, `longues_durees_travail` (F2, F3) | contrat de trois mois au plus en % des salariés ; seuil de 49 heures, saut de 2021 |
| `emploi_temporaire_subi`, `temps_partiel_subi`, `sorties_chomage_emploi`, `passages_emploi_chomage` (F4, F5, F7) | dénominateurs, drapeaux et ruptures relus sur les sorties du robot |
| `salaire_net_moyen_reel`, `pauvrete_en_emploi`, `satisfaction_travail`, `bas_salaires`, `sous_utilisation_main_oeuvre`, `menages_tres_faible_intensite_travail`, `duree_hebdomadaire_travail` | champ avant 2000 (J5), définitions précisées, URL OCDE lue par le robot, familles imbriquées signalées (J4), choix contraire du cadre Qualité de vie cité (J6) |

Lignes renvoyées (D38 a) : les 521 lignes que `niveau_de_vie` (354), `sante` (104), `education` (56) et `logement_cadre_vie` (7) renvoient vers `travail` sont toutes reprises (2 nouvelles fiches, 119 variantes) ou écartées explicitement (379) ; 20 ventilations par sexe du salaire sont renvoyées à `egalites` (D35). `lfsa_ugadra` (171 lignes, D39) est écarté explicitement ; `estat-054299` est renvoyé à `egalites` (plus d'alerte R1).

Chiffres après corrections : **39 fiches, 31 familles : 27 `retenir`, 7 `retenir_variante`, 5 `ecarter`** ; 3 déclaratives ; 0 composite ; 5 « à vérifier » ; 3 hors long-list ; 2 incontournables (`taux_emploi`, `longues_durees_travail`) ; 1 790 variantes. Présélection : 143 groupes (39 `fiche`, 59 `variante_de`, 34 `ecarte_en_bloc`, 11 `autre_dimension`) ; 7 041 lignes, dont 521 importées. Vérificateur : 0 erreur, 4 avertissements attendus (séries hors catalogue avec preuve). Tests : 403 réussis. Classeur : `docs/validation/classeurs/validation_travail.xlsx`.

Liste de maintenance (`docs/cr/maintenance_catalogues_travail.md`) : TRA-3 et TRA-7 faits ; TRA-1 et TRA-9 en cours ; TRA-11 (catalogage des décès Ameli), TRA-12 et TRA-13 (table de correspondance), TRA-14 (OG04_9) ajoutés.

À trancher : **session mère** — écart explicite de `lfsa_ugadra` ou fiche d'indemnisation des chômeurs ; dénominateurs des séries du baromètre DREES ; fiche variante Eurostat des accidents mortels pour 2008-2014 ; numéro de la vague 11 du robot à la fusion. **Léo** — séries nationales de l'Assurance maladie (régime général) en principale des accidents ; modules ad hoc de santé au travail (3 vagues non comparables) ; familles imbriquées au socle (sous-utilisation ou ses composantes ; intensité de travail et AROPE) ; deux mesures ressenties de l'insécurité de l'emploi.
