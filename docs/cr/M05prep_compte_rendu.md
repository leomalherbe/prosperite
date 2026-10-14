# Compte rendu — M05-prep (script commun de long-list)

Agent M05-prep, 14 octobre 2026. Branche `m05-longlist`, PR #5. Journal détaillé : `docs/cr/M05prep_journal.md`. Mode d'emploi : `docs/methodo/32_longlist_mode_emploi.md`. Version 2 : décisions de la session mère du 14/10 appliquées (§3).

## 1. Fait

- `src/pipeline/longlist.py` (`python -m src.pipeline.longlist --dimension <id>|hors_grille|toutes [--compresser]`) : union des catalogues INSEE BDM, INSEE Melodi, Eurostat séries et M04 dans le schéma commun demandé (+ colonnes calculées) ; rattachement v1 par `31_correspondance_v0_v1.csv` (première règle, `dimension_v0` ou `*`, motif insensible à la casse, aux accents et aux apostrophes typographiques) ; **une règle d'exception de la table l'emporte sur la proposition M04, une règle par défaut lui cède** ; éligibilité §3.4 avec motifs traçables et dérogations D16 (raccordement par concept, par lien M04 ou par jeu source Eurostat), D17 (irrégulières, y compris de fait), D18, D19 ; clé de concept et ligne de référence par concept (éligible > INSEE > Eurostat > autres > plus longue > total avant ventilation), liens de doublon M04 par idbank ; sorties par dimension, hors grille et bilan JSON.
- `scripts/collecte_longlist.py` : cible du robot pour cette branche ; exécution finale (`--compresser`) seulement quand les quatre catalogues sont présents.
- Table `docs/methodo/31_correspondance_v0_v1.csv` : corrections P1–P8, 39 règles renumérotées (exceptions avant défaut pour chaque `dimension_v0`).
- M04 : `docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv` corrigé et régénéré par son outil (`docs/sources/outils/`), désormais branché sur la table gelée.
- Tests : `tests/test_longlist.py` (83 tests, fixtures = vraies lignes des quatre catalogues) ; suite complète : 119 tests réussis.
- Volumes : CSV en clair ignorés par git ; seuls le bilan et les `.csv.gz` d'une exécution finale sont commités. Au 14/10 : **bilan seulement** (catalogues INSEE/Eurostat non fusionnés).

## 2. Chiffres (catalogues partiels du 14/10, table corrigée)

200 216 lignes : 97 556 éligibles, 15 687 à vérifier, 86 973 non éligibles. Par dimension (lignes / éligibles / à vérifier / concepts éligibles) : niveau_de_vie 13 162 / 9 292 / 3 033 / 7 514 ; travail 39 641 / 17 282 / 6 840 / 12 530 ; logement_cadre_vie 4 725 / 1 699 / 538 / 1 140 ; sante 14 614 / 12 939 / 462 / 4 259 ; education 81 436 / 38 142 / 3 832 / 32 763 ; liens_bien_etre 826 / 470 / 209 / 353 ; securite 921 / 761 / 19 / 579 ; democratie 2 615 / 681 / 178 / 676 ; egalites 337 / 298 / 30 / 203 ; planete 21 500 / 15 992 / 546 / 15 945 ; hors grille 20 439 (`hors_v1` 20 409, `hors_grille` 27, `a_classer` 3). Désaccords M04/table : 0.

Le bruit Eurostat (statistiques d'entreprises et d'échanges extérieurs, environ 100 000 lignes, surtout en `education` et `travail`) reste signalé dans `note_eligibilite` ; il est traité en amont par M02.

## 3. Décisions de la session mère appliquées (14/10)

| # | Règle (nouvelle numérotation) | Effet sur le bilan |
|---|---|---|
| P1 | 1 : « autrui », « plupart des gens » → `liens_bien_etre` | 8 lignes Eurostat quittent `securite` ; la ligne WVS de M04 n'est plus forcée |
| P2 | 11 : « fibre optique », « en ligne » → `logement_cadre_vie` | les fibres textiles restent en `education` ; pratiques et achats en ligne en cadre de vie (+ commerce électronique des entreprises, bruit M02) |
| P3 | 14 : « eau du robinet », « conformité … eau » → `logement_cadre_vie` | 2 lignes M04 |
| P4 | 22 : `(?<!fonds d')investissement`, dette des administrations publiques | 385 lignes `hors_v1` au lieu de 4 870 |
| P5 | 20 : levier, stabilité financière → `hors_grille` | 1 ligne M04 |
| P6 | 21 : comptes par secteur hors ménages → `hors_v1` | 20 002 lignes sortent de `niveau_de_vie` |
| P7 | 27–30 : satisfaction par domaine | 114 → travail, 40 → cadre de vie, 20 → niveau de vie, 0 → santé |
| P8 | 4 (situation financière personnelle, capacité d'épargne → `securite`) et 5 (autres soldes de conjoncture → `hors_grille`) | 6 gardées, 26 → `hors_grille` |

- **Écart assumé sur P7** : le motif « emploi » tel que proposé ne captait que 4 des 20 lignes Eurostat du domaine « Emploi » (Eurostat écrit « Bas » et ajoute « — par sexe ») ; corrigé en `domaine — ((élevé|elevé|moyen|bas|faible) ; )?emploi( —|$)` (20 sur 20).
- **Script** : `dimension_v0 = *` accepté (aucune règle `*` dans la table) ; priorité des exceptions sur M04 ; les règles `hors_v1`/`hors_grille` restent comme filet de sécurité.
- **M04** : Gini de la Banque mondiale en doublon `partiel` (« Gini INSEE dans Melodi, pas d'idbank BDM ») ; `dimension_v1_proposee` recalculée (8 changements : emploi du temps ×2 → `hors_v1`, FBCF → `hors_v1`, R-D → `education`, valeur financière nette des administrations publiques → `hors_v1`, catastrophes naturelles ×2 et canicule → `planete`) ; correction faite dans l'outil et ses définitions, puis fichier régénéré (l'outil reproduisait le fichier à l'identique avant modification) ; deux commentaires « A14 : cadre de vie en v1 » corrigés en « A14 : planète en v1 ».
- **Historique** : branche réécrite en un seul commit sans les gros CSV (`git reset --soft origin/main`, `push --force-with-lease`).

## 4. Points restants

- Domaines de satisfaction Eurostat « Lieu de résidence » et « Temps de trajet domicile/travail » restés en `liens_bien_etre` (hors du périmètre de P7) : à trancher en M05 ou par une règle.
- M01 : quelques étiquettes v0 manifestement fausses (ex. « Immatriculations de véhicules neufs » en `liens_bien_etre`).
- Régénération finale (`--compresser`) à faire après la fusion des PR #1 et #2, puis commit des `.csv.gz` et du bilan.

## 5. Limites

Bilan provisoire (catalogues INSEE/Eurostat non fusionnés ; Eurostat incomplet et unités à recalculer) ; clé de concept heuristique (14 concepts seulement communs à plusieurs catalogues) ; raccordement = condition de périodes, pas de définitions ; `declaratif = presume` par mots du libellé ; `composite` et `type` inconnus hors M04.
