# Journal de bord — M05-prep (script commun de long-list)

Tenu par l'agent M05-prep, lancé par la session mère. Une entrée horodatée (heure de Paris) par sous-tâche : fait, résultat, problèmes.
Mission : construire `src/pipeline/longlist.py`, exigé par la fiche M05 (section « Entrées ») — union des catalogues, rattachement à la grille v1, filtre d'éligibilité, dédoublonnage par concept, sorties par dimension et bilan. Branche `m05-longlist`.

---

## 2026-10-13 19:20 — Sous-tâche 0 : mise en route

- **Contexte** : un premier agent M05-prep (worktree `agent-ac1c8fc46ea0b88fa`) avait commencé le 13/10 vers 19 h 03 sans rien commiter ni pousser ; il n'était plus actif à 19 h 20. Sa branche locale `m05-longlist` reste extraite dans son worktree : ce worktree-ci travaille sur sa propre branche locale et pousse vers `origin/m05-longlist`. Son journal (lu, non repris tel quel) signalait deux points utiles, vérifiés ici : identifiants M04 non uniques (16 lignes) et nécessité de fournir `scripts/collecte_longlist.py` (sans lui, un push qui modifie `src/` lancerait toutes les collectes).
- **Lu** : `CLAUDE.md`, charte v1.2 (§3.4, §3.6, §4, §5.3), journal D13–D27, fiche M05, `indicateurs/dimensions.yaml` (v1 figée, R1–R8), `docs/methodo/31_correspondance_v0_v1.csv` (31 règles) et son mode d'emploi (annexe de `31_dossier_decision_gel1.md`), `docs/sources/autres_sources.md` §7 (colonnes M04), `docs/sources/insee.md` §2.6 et §12 (branche `m01-insee`), `docs/sources/eurostat.md` §10 (branche `m02-eurostat`).

## 2026-10-14 01:06 — Sous-tâche 1 : catalogues d'entrée (copies locales non commitées)

- **Copiés** depuis les branches non fusionnées (état du 14/10 01 h 06) : `origin/m01-insee` (cc33f25) → `insee_bdm_catalogue.csv` (1 650 lignes), `insee_melodi_catalogue.csv` (6 454), `insee_bilan.json` ; `origin/m02-eurostat` (c2b28f0) → `eurostat_series_catalogue.csv.gz` décompressé en `.csv` (191 707 lignes), `eurostat_jeux_catalogue.csv` (7 560 jeux), `eurostat_bilan.json`. M04 : `docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv` (405 lignes, dans `main`).
- **Exclusion git** : les noms `.csv` figuraient déjà dans `.git/info/exclude` (ajoutés par le premier agent) ; l'ajout de `eurostat_series_catalogue.csv.gz` (fichier commun à tous les worktrees) n'a pas été autorisé : le catalogue Eurostat est donc gardé décompressé en `.csv`, déjà exclu. Aucun catalogue copié n'est commité.
- **État des collectes** (d'après leurs bilans) : INSEE — passage complet terminé (13/10, 15 h 33 UTC) ; Eurostat — niveau 2 **non terminé** (1 jeu restant, 1 793 jeux `ok`), et D26 annonce un recalcul ciblé des unités : le catalogue Eurostat changera encore.
- **Constats sur les colonnes** : Eurostat, lignes `ventilation` : `nb_annees` de la ligne ne décrit pas les modalités (ex. 1 alors que les modalités ont 22–23 années) → recalcul sur `modalites_ventilation` ; BDM infra-annuelle : `nb_annees_depuis_2000` vide (606 séries) → étendue des périodes utilisée, signalée ; M04 : `identifiant_ou_url` non unique (16 lignes) → colonne `ligne_id`.

## 2026-10-14 01:20 — Sous-tâche 2 : module `src/pipeline/longlist.py` (première version)

- Union des quatre catalogues dans le schéma commun (21 colonnes demandées + colonnes calculées), rattachement par la table (première règle, motif cherché dans le libellé aux apostrophes simplifiées et dans sa version sans accents), éligibilité (§3.4, D16–D19), clés de concept et choix d'une ligne de référence par concept, sorties et bilan. Premier essai sur les catalogues réels : 200 216 lignes en environ une minute.
- **Corrections après lecture des premiers résultats** :
  - lien de doublon M04 → Eurostat par code de jeu trop lâche (« Taux d'emploi des 25-64 ans » relié à la seule série par défaut de `lfsa_ergaed`, qui est celle des 15-74 ans) : seuls les idbanks INSEE fusionnent désormais les concepts ; la série Eurostat probable est seulement notée ;
  - clé de concept : « pour mille » et mentions de zone entre parenthèses (« (inclus Mayotte à partir de 2014) ») retirées ; pluriels simplifiés de façon plus régulière (« sociaux » → « social », mots invariables protégés) ;
  - mot « perçu » retiré du repérage des déclaratifs (« revenus perçus ») ;
  - signalement non bloquant des statistiques d'entreprises (voir sous-tâche 4).
- Commit 37ef13f, poussé vers `origin/m05-longlist` (nouvelle branche). Le robot « Collecte » a pris la cible `collecte_longlist.py` (et non « tous ») et n'a rien régénéré : catalogues INSEE/Eurostat absents de la branche (journal `journaux/collecte_2026-10-13T2323_collecte_longlist.py.log`).

## 2026-10-14 01:30 — Sous-tâche 3 : tests hors ligne

- Fixtures `tests/fixtures/longlist/` : vraies lignes, copiées sans modification — 11 BDM, 5 Melodi, 13 Eurostat séries, 5 Eurostat jeux, 10 M04 (dont les deux facteurs WJP de même URL, la canicule en désaccord, le levier hors grille, une série ponctuelle, les doublons M04 « oui » vers INSEE et vers Eurostat).
- `tests/test_longlist.py` : 59 tests (lecture UTF-8/Windows-1252/gzip/point-virgule, colonne et catalogue absents, union sans perte, 21 cas d'ordre des règles + mécanisme sur table réduite, accents et apostrophes, M04 conservé et désaccord signalé, motifs bloquants, D17, D16 par concept, par lien M04 et par jeu source, `candidat_non`, clés de concept, références INSEE > Eurostat et total > ventilation, doublons M04, sorties, compression, point d'entrée). Deux tests modifient une ligne réelle en mémoire pour isoler une règle (dit dans leur docstring). Suite complète : 95 tests réussis.
- **Corrections apportées en écrivant les tests** : `candidat_non` n'est ajouté que si aucun motif n'est recalculable (sinon le refus d'Eurostat « < 10 années » écrasait la dérogation D17 : 14 352 lignes, dont la satisfaction dans la vie `ilc_pw01`) ; raccordement limité aux lignes de même ventilation (ou liées par un doublon M04), partenaire choisi par même clé puis rang de source ; note D17 non répétée ; « niveau d'éducation atteint » retiré de la clé.

## 2026-10-14 01:36 — Sous-tâche 4 : exécution réelle et contrôle du rattachement

- **Exécution** : `python -m src.pipeline.longlist --dimension toutes --remarque "…"` sur les catalogues copiés (sous-tâche 1). 200 216 lignes ; 113 029 éligibles, 15 689 à vérifier, 71 498 non éligibles ; 166 714 concepts. Aucun avertissement de colonne.

| dimension | lignes | oui | à vérifier | non | concepts (oui / oui+à vérifier) | déclaratifs (oui + présumés) | statistiques d'entreprises signalées (dont oui) |
|---|---|---|---|---|---|---|---|
| niveau_de_vie | 28 660 | 24 740 | 3 013 | 907 | 20 723 / 23 227 | 2 + 20 | 183 (127) |
| travail | 39 527 | 17 219 | 6 835 | 15 473 | 12 481 / 18 219 | 2 + 15 | 30 336 (9 830) |
| logement_cadre_vie | 4 032 | 1 368 | 343 | 2 321 | 944 / 1 263 | 2 + 6 | 2 748 (306) |
| sante | 14 614 | 12 939 | 462 | 1 213 | 4 259 / 4 438 | 13 + 877 | 8 (7) |
| education | 82 091 | 38 475 | 4 027 | 39 589 | 32 961 / 36 857 | 0 + 385 | 65 605 (27 988) |
| liens_bien_etre | 994 | 533 | 228 | 233 | 402 / 460 | 36 + 647 | 116 (40) |
| securite | 955 | 787 | 27 | 141 | 599 / 607 | 23 + 31 | 0 |
| democratie | 2 615 | 681 | 178 | 1 756 | 676 / 847 | 15 + 10 | 1 781 (0) |
| egalites | 337 | 298 | 30 | 9 | 202 / 230 | 6 + 0 | 0 |
| planete | 21 497 | 15 989 | 546 | 4 962 | 15 942 / 16 475 | 0 + 0 | 1 265 (734) |
| hors grille (hors_v1 4 890, a_classer 3, hors_grille 1) | 4 894 | — | — | 4 894 | — | — | 28 |

- Motifs (lignes non éligibles) : `moins_de_10_points` 65 842 (plus 15 689 « à vérifier » : D17 pour 15 305, D16 pour 384), `derniere_periode_avant_2020` 27 602, `hors_v1` 4 890, `geo_non_nationale` 14, `a_classer` 3, `hors_grille` 1 ; `candidat_non` 0. Sorties : 11 CSV (éducation en `.csv.gz` : > 50 Mo en clair), 105 Mo en tout.
- **Constat principal** : le catalogue Eurostat de la branche `m02-eurostat` contient environ 100 000 lignes de statistiques d'entreprises et d'échanges extérieurs (`bop_its6_det` seul : 27 705 lignes en `education`) entrées par la règle « dossier prioritaire » (numérique, culture) ; plus 19 824 lignes de comptes par secteur en `niveau_de_vie` (dont 15 857 hors ménages). Les dimensions `education` et `travail` sont inexploitables en l'état pour M05 sans ce nettoyage.
- **Contrôle du rattachement** : 15 lignes par dimension (+ `hors_v1`), stratifiées par catalogue (3 M04, 4 BDM, 3 Melodi, 5 Eurostat), relues une à une. Rattachements conformes à la grille pour l'essentiel des lignes INSEE et M04 ; défauts relevés (détail et motifs proposés dans `docs/cr/M05prep_compte_rendu.md`) :
  - **confiance interpersonnelle** : « Confiance envers autrui » (Eurostat `ilc_pw03`, `ilc_pw04`, 8 lignes) et « faire confiance à la plupart des gens » (M04) ne sont pas captés par la règle 1 → `securite` au lieu de `liens_bien_etre` ;
  - **satisfaction par domaine** (R4) : ~200 lignes INSEE/Eurostat de v0 `liens_bien_etre` (emploi principal, logement, situation financière, santé) restent en liens ; 31 lignes « facteurs de risque pour le bien-être mental » (au travail) aussi ;
  - **usages d'internet** (A7) : 772 lignes « Pratiques en ligne » / achats en ligne restent en `education` (le motif de la règle 9 ne contient pas « en ligne ») ;
  - **faux positifs** : règle 9 « fibre » = fibres textiles (58 lignes NACE → cadre de vie) ; règle 10 « activités culturelles » = code NACE R91 (110 lignes → liens) ; règle 18 « investissement » = « fonds d'investissement » (4 366 lignes de comptes financiers → hors_v1, dont 396 du secteur des ménages) ;
  - **non captés par la règle 18** : 166 lignes de dette des administrations publiques (« Dette trimestrielle des administrations publiques au sens de Maastricht », « Dette brute… au sens du FMI ») restent en `niveau_de_vie` ;
  - **conjoncture auprès des ménages** (32 lignes de soldes d'opinion, v0 `securite_confiance`) → `securite` ;
  - **bruit v0** hors table : immatriculations de véhicules neufs en liens (M01), sécurité informatique des entreprises en démocratie (1 589 lignes, M02), accidents aériens par État d'occurrence en sécurité (556 lignes, M02), dépenses des administrations publiques par fonction en démocratie (103 lignes, M02).
- **Désaccords M04 / table** (11) : 7 où la table applique une décision du gel 1 postérieure au calcul de M04 (A14 : canicule et deux arrêtés de catastrophe naturelle ; A4 : deux lignes « emploi du temps » ; A5 : FBCF, R-D) et 4 où M04 a raison et la table a un trou (eau du robinet ×2, confiance WVS, levier).
- **Erreur M04** repérée : « Indice de Gini du revenu (Banque mondiale) » déclaré doublon strict de l'idbank 010594680, qui est le rapport S80/S20 ; le Gini du niveau de vie de l'INSEE est dans Melodi (pas d'idbank BDM au catalogue M01).

## 2026-10-14 01:50 — Sous-tâche 5 : documentation, propositions, livraison

- `docs/methodo/32_longlist_mode_emploi.md` : relance (locale et robot), entrées, sorties, colonnes, règles de rattachement, d'éligibilité et de dédoublonnage, bilan, usage en M05, limites.
- `docs/cr/M05prep_compte_rendu.md` : chiffres, huit corrections de motifs de la table (P1–P8) **simulées en mémoire** sur la long-list (le fichier `31_correspondance_v0_v1.csv` n'est pas modifié), règle de priorité « exception de la table > proposition M04 > défaut de la table » qui résout les 11 désaccords dans le sens du gel 1, propositions à M02 (préfixes hors périmètre), M04 (doublon Gini erroné, dimension v1 à recalculer) et M01, questions.
- Sorties commitées : `catalogues/longlist_*.csv`, `longlist_education.csv.gz`, `longlist_bilan.json` (provisoires, à régénérer après la fusion des PR #1 et #2). Catalogues copiés non commités (vérifié par `git status`).

## 2026-10-14 02:30 — Sous-tâche 6 : décisions de la session mère appliquées

**Table `docs/methodo/31_correspondance_v0_v1.csv`** (modification autorisée par la session mère ; 31 → 39 règles, renumérotées ; pour chaque `dimension_v0`, exceptions puis une seule règle par défaut en dernier, contrôlé par un test ; fins de ligne CRLF d'origine conservées). Correspondance des numéros : anciennes 1–3 → 1–3 ; 4 → 6 ; 5–7 → 7–9 ; 8–11 → 10–13 ; 12–15 → 14–17 ; 16 → 18 ; 17 → 19 ; 18 → 22 ; 19 → 23 ; 20 → 24 ; 21 → 25 ; 22 → 26 ; 23 → 31 ; 24–31 → 32–39. Les renvois des remarques sont mis à jour (« règle 17 » → 19, « règles 18a–18c » → 20 à 22, « règle 10 » → 12). Changements :
- **P1** (règle 1, `securite_confiance` → `liens_bien_etre`) : motif `confiance (envers|dans|en|à|a) (les )?autres|confiance envers autrui|autrui|plupart des gens|confiance interpersonnelle|trust in others` (avant : `confiance (envers|dans|en) (les )?autres|confiance interpersonnelle|trust in others`).
- **P8** (nouvelles règles 4 et 5, `securite_confiance`, avant le défaut), variante retenue : règle 4 `enqu[êe]te (mensuelle )?de conjoncture aupr[èe]s des m[ée]nages.*(situation financi[èe]re personnelle|capacit[ée] d'[ée]pargne)` → `securite` (R7) ; règle 5 `enqu[êe]te (mensuelle )?de conjoncture aupr[èe]s des m[ée]nages` → `hors_grille`.
- **P2** (règle 11, `education` → `logement_cadre_vie`) : `fibre` remplacé par `fibre optique|fibre jusqu`, `en ligne` ajouté.
- **P3** (règle 14, `planete` → `logement_cadre_vie`) : ajout de `eau du robinet|conformit[ée] .*eau`.
- **P5** (nouvelle règle 20, `niveau_de_vie`) : `levier|stabilité financière|stabilite financiere` → `hors_grille` (A16).
- **P6** (nouvelle règle 21, `niveau_de_vie`) : `^(?!.*m[ée]nages)(?=.*(tableau économique d'ensemble|comptes? de patrimoine|op[ée]rations (non )?financi[èe]res|compte de r[ée][ée]valuation|autres changements de volume|comptes financiers))` → `hors_v1` (A5).
- **P4** (règle 22, ex-18, `niveau_de_vie` → `hors_v1`) : `investissement` remplacé par `(?<!fonds d')investissement` ; ajout de `dette .*administrations publiques|au sens de Maastricht|valeur financière nette des administrations publiques`.
- **P7** (nouvelles règles 27 à 30, `liens_bien_etre`, entre « temps libre » (26) et le défaut (31), code R6 de M03 : la satisfaction d'un domaine va dans ce domaine) : 27 → `travail`, 28 → `logement_cadre_vie`, 29 → `sante`, 30 → `niveau_de_vie`, motifs du compte rendu. **Écart assumé** pour la règle 27 : le motif simulé `domaine — (élevé|moyen|faible|elevé) ; emploi$|domaine — emploi$` ne captait que 4 des 20 lignes Eurostat du domaine « Emploi » (Eurostat écrit « Bas », pas « Faible », et ajoute « — par sexe » aux ventilations) ; il devient `domaine — ((élevé|elevé|moyen|bas|faible) ; )?emploi( —|$)`, ce qui réalise l'intention de P7 (20 lignes sur 20).
- Les règles `hors_v1` / `hors_grille` sont gardées comme filet de sécurité, le bruit Eurostat étant traité en amont par M02.

**Script** : `dimension_v0 = *` accepté (règle commune à toutes les dimensions, effective si elle précède la règle par défaut de la dimension ; aucune règle `*` dans la table) ; **priorité** : une règle d'exception de la table l'emporte sur `dimension_v1_proposee` (note « exception de la table prioritaire »), une règle par défaut lui cède (note « désaccord … (retenu) ») ; bilan : `desaccords_catalogue_retenu` et `exceptions_table_prioritaires`. Sorties : CSV en clair par défaut (ignorés par git : `catalogues/longlist_*.csv` ajouté au `.gitignore`), `--compresser` pour l'exécution finale (`.csv.gz`) ; le seuil de 50 Mo est supprimé ; `scripts/collecte_longlist.py` passe `--compresser`. Tests : 83 dans `tests/test_longlist.py` (numéros de règles, cas P1–P8, ordre exceptions/défaut, règle `*`, priorité dans les deux sens, sorties), 119 pour la suite.

**M04** (`docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv`) : corrigé **à la source** pour qu'une reconstruction ne défasse rien — l'outil `docs/sources/outils/construire_candidats.py` reproduisait le fichier à l'identique (vérifié avant modification) ; il lit désormais la table gelée corrigée (au lieu de la copie M03), avec la même logique que la long-list (`*`, apostrophes, accents, priorité des exceptions sur les forçages) ; dans `candidats_definitions_suite.py`, l'indice de Gini de la Banque mondiale passe en doublon `partiel`, sans idbank, commentaire « Gini INSEE dans Melodi, pas d'idbank BDM », et deux commentaires « A14 : cadre de vie en v1 » deviennent « A14 : planète en v1, décision du gel 1 ». Fichier régénéré : 8 `dimension_v1_proposee` changent (emploi du temps ×2 → `hors_v1` ; FBCF → `hors_v1` ; R-D → `education` ; valeur financière nette des administrations publiques → `hors_v1` ; arrêtés de catastrophe naturelle ×2 et canicule → `planete`), les mentions de forçage devenues sans objet disparaissent (eau du robinet ×2, confiance WVS, levier).

**Effets sur le bilan** (mêmes catalogues partiels ; lignes, éligibles) : niveau_de_vie 28 660 → 13 162, 24 740 → 9 292 (P6 : 20 002 lignes de comptes par secteur hors ménages en `hors_v1`, P4 : 385 lignes de dette et d'investissement au lieu de 4 870) ; logement_cadre_vie 4 032 → 4 725, 1 368 → 1 699 (P2 « en ligne », P7) ; education 82 091 → 81 436 ; liens_bien_etre 994 → 826, 533 → 470 (P7 : 114 → travail, 40 → cadre de vie, 20 → niveau de vie ; P1 : 8 lignes reçues) ; securite 955 → 921, 787 → 761 (P1, P8 : 26 → `hors_grille`, 6 gardées) ; travail 39 527 → 39 641 ; hors grille 4 894 → 20 439 (`hors_v1` 20 409, `hors_grille` 27, `a_classer` 3) ; total éligibles 113 029 → 97 556. Désaccords catalogue/table : 11 → 0.

**Volumes et historique** : les CSV en clair et les `.csv.gz` provisoires sont retirés ; seul `catalogues/longlist_bilan.json` est commité. Historique de la branche réécrit (jamais entré dans `main`) : `git reset --soft origin/main`, un seul commit, `git push --force-with-lease` (autorisé par la session mère).
