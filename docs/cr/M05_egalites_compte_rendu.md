# Compte rendu — M05, fiches indicateurs de la dimension `egalites`

Agent de mission M05 (Égalités), 14 octobre 2026, branche `m05-egalites`, PR « M05 — fiches indicateurs : egalites ». Méthode commune `docs/methodo/33_methode_fiches_M05.md` appliquée sans modification des scripts communs. Détail dans `docs/cr/M05_egalites_journal.md`.

## 1. Livrables

| Fichier | Contenu |
|---|---|
| `docs/validation/regles_preselection_egalites.csv` | 136 règles ordonnées |
| `docs/validation/preselection_egalites.csv`, `preselection_egalites_lignes.csv` | 136 groupes ; 499 lignes affectées (les 330 de la long-list + 169 importées d'autres long-lists) |
| `indicateurs/egalites/*.yaml` | 50 fiches (schéma étendu), 331 variantes |
| `docs/validation/validation_egalites.csv` | tableau de validation à 18 colonnes, `decision_leo` vide ; `verifier_fiches.py` : 0 erreur, 0 avertissement |
| `docs/cr/maintenance_catalogues.md` | lignes 10 à 20 ajoutées (statut `a_faire`) |

## 2. Chiffres

- **50 fiches, 37 familles** : **32 `retenir`**, **11 `retenir_variante`**, **7 `ecarter`**.
- 5 déclaratives (perceptions DREES ×3, santé perçue, inégalité de satisfaction) ; 5 composites (PNUD ×3, V-Dem ×2, D18) ; 4 à vérifier (D17 : patrimoine ×2, PISA, inégalité de satisfaction) ; 0 hors long-list.
- **11 incontournables** (familles `inegalite_revenu`, `ecart_emploi_fh`, `ecart_salaire_fh`, `indice_composite_genre`, concepts du §5 du crosswalk) : tous présents et retenus.
- **12 indicateurs d'écart construits** (champ `formule`) à partir des ventilations des long-lists `travail`, `niveau_de_vie`, `education`, `sante` : écarts femmes-hommes de chômage, de pauvreté et de salaire en EQTP ; écarts selon l'origine de chômage, de pauvreté, de NEET et de sorties précoces ; écarts selon l'origine sociale ou le diplôme (baccalauréat, chômage) ; écarts de santé perçue et d'accès aux soins selon le revenu ; écart de pauvreté entre jeunes et seniors. Signe vérifié à la source pour 7 d'entre eux (API Eurostat pour 6, extrait du robot M04 pour la DEPP).
- Sous-thèmes : femmes-hommes 16 fiches ; revenu 8 ; origine et discriminations 6 ; origine sociale 4 ; santé et handicap 4 ; territoires 3 ; perceptions 3 ; patrimoine 2 ; générations 2 ; salaires 1 ; multidimensionnel 1.

## 3. Rattachements proposés (à trancher au gel 2)

- **Vers `egalites`** (169 lignes importées, dont 18 portent une série principale) : mesures de dispersion ERFS (S80/S20 après et avant redistribution, S90/S50, parts cumulées), parts du patrimoine par quantile et parts de la masse salariale des mieux payés, aujourd'hui en `niveau_de_vie` ou `travail` ; écart de rémunération par branche `earn_gr_gpgr2*` (`travail`) ; femmes au Parlement `sdg_05_50` (`democratie`, A8) ; écart d'emploi lié au handicap `hlth_dlm200` (`sante`). Pour les écarts construits, les lignes sources sont des **composantes partagées** : le niveau reste dans sa dimension, l'écart va dans `egalites` (R3).
- **Hors d'`egalites`** : 86 lignes de niveaux de revenu (`ilc_di04`, `ilc_di07`, `ilc_di13b`, `ilc_di14b`, seuils `ilc_di01`) → `niveau_de_vie` ; `ilc_li70b` (prestations des chômeurs) → `securite`.

## 4. Erreurs de catalogue et sources manquantes (maintenance n° 10-20)

Table de correspondance (n° 10-11) ; unité « Euro » des parts `ilc_di01` (12) ; libellé incohérent du Gini du patrimoine Melodi (13) ; périodes des paquets de modalités (17) ; définition d'`ilc_pnp12` (18) ; lignes ERFS `BWA/BWB` qui ne sont pas des séries (20) ; garder les dispersions régionales nationales lors de l'exclusion NUTS (15) ; séries à cataloguer : DREES CS16_1 « témoins de discriminations liées à l'origine » (14), taux d'emploi 20-64 ans par origine (16), PISA selon le statut social, espérance de vie par niveau de vie, TeO, Défenseur des droits, femmes dans les conseils d'administration (19). Aucune exclusion abusive dans la long-list.

## 5. Points à faire vérifier par Léo

1. **Une seule famille pour l'inégalité de revenu** : S80/S20 principal (ERFS rétropolé, 4,62 en 2024), Gini, Palma, D9/D1 et part des 40 % en alternatives. Le seuil Palma = 2 du Doughnut n'est pas une borne utilisable en France (Palma EU-SILC calculé 1,14 en 2025 ; 2,64 avant impôt selon le WID).
2. **Écart de salaire** : principal = écart horaire non corrigé d'Eurostat (ODD national 5.i1, 15,4 % en 2006, 11,8 % en 2024) plutôt que l'écart INSEE en EQTP, plus long (1996-2024) mais construit ; **part du 1 %** : WID (niveau 2) plutôt qu'EU-SILC.
3. **Effet de la redistribution écarté** (sens ambigu, rupture 2020) alors que le contenu de la dimension le cite : le couple S80/S20 avant (retenu) et après redistribution porte l'information.
4. **Écarts selon l'origine (A8)** : aucune mesure directe des discriminations au catalogue (V-Dem écarté : quasi constant) ; quatre écarts de résultats (chômage, pauvreté, NEET, sorties précoces) servent de mesures indirectes ; la question DREES CS16_1 est à cataloguer.
5. **Sens ambigu → écarter** : écart de chômage femmes-hommes (change de signe en 2012), revenu relatif des seniors (passe par 1), indice de développement de genre, part des femmes parmi les victimes de violences.
6. **Handicap** (`ecart_emploi_handicap`) et **inégalités de santé** (santé perçue, accès aux soins selon le revenu) ajoutés au titre de la définition (« écarts entre groupes ») : à confirmer dans `egalites`.

## 6. Questions pour la session mère

1. Valider la convention des **écarts construits** : lignes sources importées en décision `fiche` depuis leur long-list (elles figurent donc aussi dans la présélection de leur dimension d'origine, comme ventilations).
2. **Vérificateur** : la borne `premiere_annee ≥ 1900` refuse les séries V-Dem (1789, 1851), ramenées à 1900 avec une note ; élargir la borne de `scripts/verifier_fiches.py` ?
3. Confirmer `incontournable: non` pour les écarts de temps partiel, de pension, de pauvreté et la parité politique (hors §5 du crosswalk).
4. Numérotation de `maintenance_catalogues.md` : les lignes 10-20 peuvent entrer en conflit avec celles d'autres agents M05 ; renuméroter à la fusion si besoin.
