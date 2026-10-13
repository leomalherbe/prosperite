# Compte rendu — mission M04 (sources hors INSEE et Eurostat)

Agent de mission M04 — 13 octobre 2026. Branche `m04-sources`, pull request #4. Journal détaillé : `docs/cr/M04_journal.md`.
Phase 1 (T1 fiches par source, T2 inventaire) puis phase 2 (T3 indicateurs candidats), reprise après l'interruption d'un premier agent de phase 2.

## 1. Fait

| Tâche | Livrable | État |
|---|---|---|
| T1 — fiches par source | `docs/sources/autres_sources.md` (Projet : `claude/10_sources_hors_insee_eurostat.md`) | fait ; §7 de synthèse de phase 2 ajouté |
| T2 — inventaire | `docs/sources/10_sources_inventaire.csv` (74 sources) | fait ; mis à jour en phase 2 |
| T3 — indicateurs candidats | `docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv` (404 lignes) (Projet : `claude/10_indicateurs_candidats_hors_insee_eurostat.csv`) | fait |
| Outils | robot `scripts/collecte_sources.py` + `src/sources/series_tabulaires.py` (modes séries, large, couverture, distribution, colonne, pdf…) ; constructeur `docs/sources/outils/construire_candidats.py` + définitions | 36 tests hors ligne passent |
| Preuves | `docs/sources/verif_acces/` (accès, phase 1), `docs/sources/series/` (séries listées, vagues 5 à 8), `journaux/` | commités par le robot |

**Méthode de la phase 2.** Le robot GitHub Actions télécharge chaque ressource et en dresse la liste des séries (identifiant, première et dernière période, nombre de points, valeurs distinctes). Chaque indicateur candidat est décrit dans les fichiers de définitions et rattaché à une de ces sorties : les années ne sont jamais saisies à la main, une série introuvable fait échouer la construction, les identifiants de doublon sont contrôlés contre les catalogues M01 (`insee_indicateurs_reperes.csv`) et M02 (`eurostat_jeux_catalogue.csv`), la dimension v1 est calculée par la table de correspondance de M03. Pour reconstruire : `python docs/sources/outils/construire_candidats.py [--references <dossier des deux catalogues>]`.

## 2. Chiffres clés de la liste des candidats

404 lignes (370 indicateurs + 34 ventilations), toutes `fiabilite = verifie`. Hors ventilations : 79 déclaratifs, 83 composites, 88 non annuels (D17), 310 résultats, 36 pressions, 24 moyens ; 247 lignes satisfont les critères chiffrés de la charte §3.4 (annuel, ≥ 10 points depuis 2000, dernière valeur ≥ 2020).

| Dimension v1 proposée (v0 entre parenthèses si différente) | Lignes | Ventilations | Déclaratifs | Composites | Non annuels | Critères §3.4 | Doublon oui / partiel |
|---|---|---|---|---|---|---|---|
| democratie | 101 | 2 | 13 | 64 | 31 | 60 | 6 / 10 |
| planete | 68 | 7 | 0 | 7 | 3 | 57 | 9 / 29 |
| securite (securite_confiance : 52) | 53 | 4 | 19 | 0 | 3 | 31 | 2 / 13 |
| egalites | 41 | 4 | 6 | 10 | 15 | 20 | 4 / 9 |
| liens_bien_etre (v0 : 36) | 38 | 12 | 24 | 0 | 16 | 9 | 3 / 12 |
| logement_cadre_vie (v0 : 20) | 28 | 1 | 2 | 0 | 1 | 25 | 5 / 9 |
| sante (v0 : 30) | 28 | 2 | 11 | 0 | 8 | 15 | 7 / 9 |
| niveau_de_vie (v0 : 18) | 16 | 0 | 2 | 1 | 1 | 14 | 2 / 11 |
| education (v0 : 19) | 16 | 0 | 0 | 0 | 7 | 7 | 3 / 5 |
| travail | 14 | 2 | 2 | 1 | 3 | 8 | 4 / 7 |
| hors grille | 1 | 0 | 0 | 0 | 0 | 1 | 0 / 0 |

Doublons (hors ventilations) : 45 `oui`, 114 `partiel`, 211 `non` ; 68 identifiants INSEE/Eurostat cités, tous présents dans les catalogues M01/M02. Sources : OCDE How's Life 122 lignes, OWID 66, SSMSI 27, ITDD 24, OCDE ODD 23, Citepa 21, DREES 17, PNUD 17, WGI 12, Odissé 11, SDES 10, WDI 10, WJP 9, Intérieur 8, Freedom House 7, RSF 6, DEPP 6, Footprint Data Foundation 3, Ameli 3, WHR 1, EDGAR 1.

## 3. Conditions du gel 1 : `liens_bien_etre` et `democratie`

**`liens_bien_etre`** (page 6 du dossier : rechercher des séries publiques annuelles, confirmer Gallup).
- Séries publiques annuelles trouvées, sans doublon INSEE/Eurostat : **baromètre d'opinion de la DREES** (microdonnées pondérées 2000-2025) — situation personnelle jugée bonne (2002-2025, 23 points), optimisme pour soi et pour les générations futures (2000-2025, 25 points), sentiment d'être intégré dans la société et cohésion sociale perçue (2014-2025), aide bénévole à une personne âgée (2011-2025) ; **World Happiness Report** — évaluation de la vie (Gallup, moyenne glissante sur 3 ans, 2011-2025, licence non précisée). Avec la satisfaction dans la vie de l'INSEE (2010-2024), la dimension compte une dizaine de candidats annuels, presque tous déclaratifs.
- **Origine Gallup confirmée** par le PDF officiel de l'OCDE (lu par le robot) pour le soutien social, la sécurité la nuit, les émotions négatives, la douleur, la confiance dans le gouvernement et le bénévolat : moyennes groupées (2006-07 puis triennales jusqu'à 2023-25), soit **7 valeurs** depuis 2006 — ce ne sont pas des séries annuelles. **Conditions de réutilisation : non trouvées** (aucune mention dans le PDF ; conditions générales de l'OCDE illisibles par l'outil).
- Rien d'exploitable chez l'INJEP (aucun jeu sur data.gouv.fr), le CEPREMAP, le Crédoc ou le CEVIPOF (PDF).

**`democratie`**. Hors composites, les séries sont rares : participation électorale par type de scrutin (Intérieur, 1999-2026, irrégulière, recalculée par le robot), part des votes blancs, détention provisoire (ODD 16.3.2, 2005-2024), taux de signalement à la police (ODD 16.3.1), atteintes à la probité enregistrées (SSMSI 2016-2023), confiance dans les institutions (WVS/EVS : 3 vagues depuis 2000 ; Gallup via OCDE : 7 valeurs). Les composites sont nombreux et redondants (V-Dem 31 lignes, WGI 12, Freedom House 10, WJP 9, RSF 6, CPI 2) : la règle « une famille de composites = une variante principale » proposée par M03 est indispensable. Aucune série annuelle publique de confiance dans le gouvernement ou le Parlement nationaux n'a été trouvée.

## 4. Problèmes rencontrés

- L'outil de lecture web respecte les `robots.txt` (Opendatasoft, OCDE PDF, BCE…) : tout passe par le robot, ce qui impose des allers-retours de 4 minutes par vague.
- Un lancement manuel du robot est parti avant la poussée de la vague 8 et a rejoué la vague 7 (sans dommage).
- Séries SSMSI en nombre (pas en taux), délinquance enregistrée de sens ambigu, rupture de l'enquête de victimation en 2022.
- Participation électorale : taux recalculés sur le fichier agrégé, à recouper avec les résultats officiels (2002 et 2007 surtout).
- Baromètre DREES : codes de modalités lus dans le dictionnaire 2025, stabilité sur 25 ans et champ géographique à confirmer ; ruptures d'échelle connues pour la santé perçue.
- Licences non trouvées : Citepa, RSF, Freedom House, WJP, WHR, Footprint Data Foundation, données Gallup relayées par l'OCDE.
- Les fichiers CSV de la branche étaient en fins de ligne CRLF ; normalisés en LF (diff d'ensemble sur `series.csv` et la liste des candidats).

## 5. Propositions (pour la session mère ; la charte et le journal ne sont pas modifiés)

1. **Admettre le baromètre DREES** comme source principale de `liens_bien_etre` (niveau 2, pièces jointes Opendatasoft), avec un module de collecte dédié qui recalcule les parts pondérées.
2. **Séries Gallup via l'OCDE** : les classer `frequence: irreguliere` (7 points), ne pas les présenter comme annuelles, et demander à l'OCDE (wellbeing@oecd.org) les conditions de réutilisation avant toute diffusion publique.
3. **Démocratie** : retenir une variante principale par famille de composites (V-Dem démocratie libérale ou libertés civiles ; WGI voix et responsabilité ; RSF en variante après traitement des ruptures) et compléter par la participation électorale (D17) et la détention provisoire.
4. **Sécurité** : préférer les taux ITDD (pour 1 000 habitants) aux nombres SSMSI, et marquer `sens: ambigu` les violences intrafamiliales et sexuelles enregistrées.
5. **Empreinte écologique** : retenir la Footprint Data Foundation (sans clé) et clore la question de la clé GFN (D21).
6. **Veille mensuelle** du robot sur `main` : regrouper les ressources utiles dans une vague « veille » (le script n'exécute que la dernière vague de `series.csv`).

## 6. Points à faire vérifier par Léo

1. Le **baromètre DREES** comme pilier de `liens_bien_etre` (enquête d'opinion de 3 000 à 4 000 personnes, questions sur la situation personnelle et l'optimisme plutôt qu'une note de satisfaction) : acceptable ?
2. Les **séries Gallup** (7 valeurs depuis 2006, licence inconnue) : les garder comme candidates ou les écarter ?
3. Le **poids des composites** en démocratie (64 lignes sur 101) et la règle de familles.
4. Les **taux de participation** recalculés par le robot (à recouper avec quelques chiffres officiels connus).
5. Les **sens ambigus** (19 lignes : délinquance enregistrée, votes blancs, aidance, taux de plainte).
