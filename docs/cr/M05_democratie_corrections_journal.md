# Journal des corrections après audit M06 — dimension `democratie`

Branche `m05-democratie-corr`, PR #23. Rapport d'audit appliqué : `docs/validation/audit_democratie.md` (§10, neuf corrections ; oublis O1 à O4 ; cohérence I1 à I7 ; désaccords J1 à J8), complété par les règles v1.2 de la méthode (`docs/methodo/33_methode_fiches_M05.md` §9, D32 à D36). Modèle suivi : corrections `securite` (`docs/cr/M05_securite_corrections_journal.md`, PR #18) et `egalites` (PR #19). Travail commencé le 14/10/2026 par un premier agent correcteur (vagues 9 et 10 du robot), interrompu, puis repris le 15/10/2026 par un second agent.

## 0. Mise en route et état de référence

- Reprise (15/10/2026) : `git checkout -B m05-democratie-corr origin/m05-democratie-corr`, fusion de `origin/main` sans conflit (méthode v1.2, corrections `securite` et `egalites`, classeurs du gel 2).
- Lus : `CLAUDE.md`, charte (§3.4, §3.6, §4), journal des décisions (D13-D36), méthode 33 v1.2, fiche M06, audit `democratie` en entier, compte rendu et journal M05 `democratie`, les 32 fiches, les sorties des vagues 9 et 10 et leurs journaux (`journaux/collecte_2026-10-14T0906_collecte_sources.py.log`, `…T0923…`), les corrections `securite` (journal, compte rendu §6, `maintenance_catalogues_securite.md`) et `egalites` (commit `c96e411`).
- Départ : `python -m pytest -q` → 399 réussis ; `python scripts/verifier_fiches.py --dimension democratie` → 0 erreur, 1 avertissement (`citoyennete_active`) ; 32 fiches, 24 familles, 22 `retenir`, 7 `retenir_variante`, 3 `ecarter`, 100 variantes.
- Sous-dossier de travail `tmp/democratie-corr/` (non commité, D36) : `champs.py` et `series_homogenes.py` (participation par champ), `regi2004.py` et `controle_inscrits.py` (contrôle des inscrits par département), `maj_regles.py` et `maj_fiches.py` (modifications), `doublons_serie_id.py` (D36). Aucun fichier sous `scripts/` ni `src/` modifié par la reprise.

## 1. Entrées horodatées

| Horodatage (Paris) | N° (audit §10) | Verdict traité | Ce qui a changé | Commit |
|---|---|---|---|---|
| 2026-10-14 11:05 | 1 (participation) | F, `a_corriger` | Vague 9 du robot : `agreger` (`src/sources/series_tabulaires.py`) admet une clé multiple (`id_election\|code_departement`) et compte les valeurs manquantes ; test associé ; définition de la sortie `interieur_elections / participation_par_departement` dans `docs/sources/verif_acces/series.csv`. Run du robot : 5 723 lignes (scrutin × département). | `4e50e21`, `c8e976d` (robot) |
| 2026-10-14 11:11 | — | — | Instantanés de vérification des accès remis à l'état de `main` (bruit du run). | `74bc348` |
| 2026-10-14 11:22 | 5 (O1, adhésion syndicale) | O, D33 | Vague 10 du robot : distribution pondérée des questions `sdassynd_1` et `sdassynd_2` du baromètre DREES (sortie `drees / barometre_2000_2025_syndicat_association`, 115 lignes). | `4da7770`, `f68d978` (robot) |
| 2026-10-15 13:14 | — | — | Instantanés de vérification des accès remis à l'état de `main` après le run de la vague 10. | `0202dc7` |
| 2026-10-15 13:36 | 1 (participation) | F, `a_corriger` | Les six fiches `participation_*` recalculées sur le champ homogène métropole + DROM (codes `01`-`95`, `2A`, `2B`, `ZA`-`ZD`, `ZM` ; `971`-`974`, `976` en 2026) à partir de la vague 9 ; `composantes`, `formule`, `preuve`, `geo: FE`, `source_serie_id` distinct par scrutin, `url_api` du CSV lu ; recoupement (§2) ; municipales depuis 2014 (2008 : communes de plus de 3 500 habitants) ; régionales depuis 2010 (2004 mal codé, cause trouvée, DEM-1) ; législatives : rupture de 2012 supprimée par le champ (Français de l'étranger exclus) ; motifs, notes et natures des variantes INSEE réécrits ; ligne 24 de la liste partagée précisée. | `8460d48` |
| 2026-10-15 13:36 | J3 (départementales) | J | `participation_departementales` : `ecarter` → `retenir_variante` sur 2015-2021 (2 scrutins, D17, D28, D32), cantonales 2001-2011 exclues de la série (renouvellement par moitié), libellé « départementales ». | `8460d48` |
| 2026-10-15 13:36 | 2 (Freedom House) | F, `a_corriger` | Années OWID = années couvertes (`qualite: annee_couverte`, `annee_reference: observation`) ; définition, notes (séries OWID et fichier par édition mises en regard) et note de pertinence (édition 2026, baisse de 93-96 à 89) corrigées. | `8460d48` |
| 2026-10-15 13:36 | 3 (WGI) et J1 | A (D33), J | Familles de concept (D35) : `etat_de_droit` (WGI principal, WJP en `retenir_variante`), `corruption` (WGI principal, CPI en `retenir_variante`), `qualite_democratique` (V-Dem libéral principal ; V-Dem participatif, Freedom House et WGI voix et responsabilité en `retenir_variante`) ; famille `rsf` renommée `liberte_presse_rsf`. Règles 600 à 850 : sous-indices V-Dem d'État de droit (2) et de corruption (6) rattachés aux familles de leur concept ; autres sous-indices WGI (efficacité, réglementation, stabilité politique, 6 lignes) écartés en bloc. | `8460d48` |
| 2026-10-15 13:36 | J5 (WGI) | J | Documentation WGI lue (score 0-100 produit « pour faciliter les comparaisons entre pays et dans le temps ») : série principale des trois fiches WGI passée de l'estimation (`.EST`) au score 0-100 (`.SC`), estimation en variante ; `url_page` = page de documentation ; trajectoire complète de voix et responsabilité (0,95 en 2000, 0,91 en 2003, pic 1,48 en 2005, 1,16 en 2025) et drapeau `volatilite_2003_2005`. | `8460d48` |
| 2026-10-15 13:36 | 4 (V-Dem) | A (D32) | `premiere_annee: 1789` (libéral, participatif, liberté d'expression), phrase « ramenée à 1900 » supprimée ; `faible_variation` sur l'indice libéral (0,789-0,822 depuis 2000). | `8460d48` |
| 2026-10-15 13:36 | J6 et D34 | J, A | `annee_reference` sur les 11 composites : `observation` (V-Dem ×4, Freedom House, WGI ×3, CPI), `edition` (RSF, WJP). | `8460d48` |
| 2026-10-15 13:36 | J7 | J | Motifs : Freedom House non incontournable (absent de la table des cadres) ; liberté d'expression V-Dem non incontournable (« indices V-Dem » cités seulement comme proxys généraux de SSF). | `8460d48` |
| 2026-10-15 13:36 | 5 (O1) | O, D33 | Fiche hors long-list `adhesion_syndicale` (SDASSYND_1, `geo: FM`, 2000-2025, 25 points, `statut_serie: disponible`, `preuve` = sortie de la vague 10, `composantes`, `formule`) ; règle 202 `hors_longlist = oui` ; `retenir`, sens `haut` motivé ; aucune valeur officielle publiée pour recouper (`non_recoupe`, voir §4). | `8460d48` |
| 2026-10-15 13:36 | 6 (O2) | O | Fiche `participation_en_ligne` (`isoc_ci_ac_i`, `I_IUVOTE`, 2011-2025, 10 points, valeurs lues sur l'API) importée de la long-list `logement_cadre_vie` (règles 205 et 206, ventilations en variante), `rattachement_propose`, `retenir`, incontournable (participation et voix politique). | `8460d48` |
| 2026-10-15 13:36 | 7 (O3, I2) | O, D33 | Les 14 lignes `crim_pris_*` que `securite` renvoie désormais ici importées : fiche `taux_detention` (détenus pour 100 000 habitants, `sens: ambigu`, `ecarter`), ventilations par âge, sexe, nationalité et condamnés en variantes (règle 496), nombre de condamnés écroués de l'INSEE passé d'écart en bloc à variante (règle 490), détenus par infraction écartés en bloc (règle 497, D35). | `8460d48` |
| 2026-10-15 13:36 | 8 (voix) | `non_verifiable` | `voix_pouvoirs_publics` : définition « source primaire à vérifier (PIAAC ou enquête Confiance de l'OCDE) », drapeau `source_a_verifier` ; recherche infructueuse (PDF de définitions refusé à l'outil, extrait du robot limité à Gallup, page *Government at a Glance 2025* sans le texte). | `8460d48` |
| 2026-10-15 13:36 | 9 (mineurs) et J4 | — | Motif de `perception_corruption_cpi` (« de 71 en 2012 à 66 en 2025, maximum 72 ») ; `url_page` et « documentation lue » pour les WGI ; WJP : identifiant commun des huit facteurs signalé (DEM-3, non modifiable ici : les variantes viennent de la long-list) ; `detention_provisoire` : raccordement `oui` → `a_etudier` (rupture de 2019 : 29,0 % en 2018, 25,9 % en 2019). | `8460d48` |
| 2026-10-15 13:45 | 1 e et signalements | — | `docs/cr/maintenance_catalogues.md` ligne 24 précisée ; nouveaux signalements DEM-1 à DEM-7 dans `docs/cr/maintenance_catalogues_democratie.md` ; ce journal ; compte rendu §7. | (commit suivant) |
| 2026-10-15 13:50 | — | — | PR #23 « M05 — democratie : corrections après audit » ouverte vers `main` par l'API GitHub (corps : liste des corrections et verdict d'audit traité). | — |

## 2. Participation électorale : champ homogène et recoupement (correction n° 1, D34)

Constat sur la sortie de la vague 9 : le code `ZZ` (Français de l'étranger) n'apparaît qu'à partir de 2012 (2014 pour les européennes), les collectivités d'outre-mer (`ZN`, `ZP`, `ZS`, `ZW`, `ZX`) apparaissent entre 2008 et 2012 selon le scrutin, Mayotte (`ZM`) à partir de 2004. Le taux de « tous les bureaux » mêlait donc deux champs. Le champ métropole + DROM est présent à tous les scrutins (hors Mayotte en 1999 et 2002) et c'est le champ « France » (`FE`) des séries de l'INSEE.

| Scrutin (premier tour) | Calcul du projet | Valeur officielle | Source du recoupement |
|---|---|---|---|
| Présidentielle 2002 | 72,11 % | 72,11 % | archives du ministère : France entière (41 197 964 inscrits, 29 497 888 votants, 71,60 %) moins étranger, Mayotte, Nouvelle-Calédonie, Polynésie, Saint-Pierre-et-Miquelon, Wallis-et-Futuna (730 411 inscrits, 314 712 votants) |
| Présidentielle 2007 | 84,73 % | 84,73 % | archives : France entière (44 472 834, 37 254 242, 83,77 %) moins étranger et collectivités hors Mayotte (1 152 694, 549 434) |
| Présidentielle 2012 / 2017 / 2022 | 80,67 / 79,02 / 75,28 % | 80,7 / 79,0 / 75,3 % | INSEE BDM 001778320 |
| Législatives 2012 / 2017 / 2022 / 2024 | 58,18 / 49,61 / 48,38 / 67,87 % | 58,2 / 49,6 / 48,4 / 67,9 % | INSEE BDM 001778442 |
| Européennes 2014 / 2019 / 2024 | 43,37 / 51,28 / 52,95 % | 43,4 / 51,3 / 53,0 % | INSEE BDM 001778185 |
| Régionales 2010 | 46,33 % | 46,33 % | archives : 43 642 325 inscrits, 20 219 958 votants (fichier : 43 643 115 et 20 219 768) |
| Régionales 2015 / 2021 | 49,91 / 33,27 % | 49,9 / 33,3 % | INSEE BDM 001777817 |
| Départementales 2015 / 2021 | 50,17 / 33,32 % | 50,2 / 33,3 % | INSEE BDM 001778052 |
| Municipales 2020 | 44,60 % | 44,6 % | INSEE BDM 001785274 |
| Municipales 2014 / 2020 / 2026 (tous bureaux) | 63,55 / 44,66 / 57,12 % | 63,55 / 44,66 / 57,1 % | taux nationaux publiés (repris par LCP en 2026) ; communiqué du ministère (2026) |
| Municipales 2014 (champ) | 63,52 % | 63,4 % | INSEE BDM 001785274 : écart non expliqué |
| Régionales 2004 | 59,39 % | 60,84 % | archives : fichier mal codé (DEM-1), valeur non retenue |

Non recoupés (pages d'archives illisibles à l'outil) : législatives 2002 et 2007, européennes 1999-2009. Contrôle complémentaire : aucun premier tour hors outre-mer n'a de département dont les inscrits s'écartent de plus de 8 % de ceux des scrutins nationaux voisins, sauf les régionales 2004 ; la Saône-et-Loire manque aux législatives 2002 (1 % du champ, effet inférieur à 0,02 point), la Manche aux régionales 2004.

## 3. Autres demandes (règles v1.2, D32 à D36)

| Demande | Ce qui a changé | Limites |
|---|---|---|
| D34 : `composantes` et `formule` des séries calculées | Six fiches de participation (fichier `general_results` ; formule avec les codes départementaux et la première année lue) et `adhesion_syndicale` (microdonnées pondérées, vague 10). | La composante des fiches de participation est l'identifiant de la long-list (commun aux sept lignes M04) ; les modalités (scrutin, départements) sont dans la `formule` (DEM-4). |
| D34 : recoupement avant `retenir` | Participation : 5 valeurs officielles pour la présidentielle (principale), 3 à 4 pour les autres scrutins (§2). | `adhesion_syndicale` reste `retenir` sans recoupement possible (question sans valeur publiée) : point soumis à la session mère. |
| D34 : `annee_reference` des composites | 11 fiches. | Convention du CPI (année de l'indice, paraît l'année suivante) à confirmer. |
| D35 : famille = concept substituable | Voir §1 (n° 3, J1). | Choix de la variante principale de `qualite_democratique` (V-Dem libéral, niveau 2, plutôt que WGI voix et responsabilité, niveau 1) : dérogation motivée à la méthode §4 (concept le plus large), à confirmer. |
| D36 : `serie_id` unique par variante | Contrôle par script : 2 identifiants restent en double, tous deux hérités du catalogue M04 (participation : composante commune et variante second tour ; WJP : score global et huit facteurs). | Non corrigeable dans les fiches (les variantes sont injectées depuis la long-list) : DEM-3 et DEM-4. |
| D36 : chercher dans toutes les long-lists avant « non catalogué » | Recherche « syndic » dans toutes les long-lists et catalogues (`*_non` compris) : aucune série d'adhésion syndicale. | — |

## 4. Points soumis à la session mère et à Léo

- **Session mère** : (1) `adhesion_syndicale` en `retenir` sans recoupement possible (D34) ou en attente ; (2) variante principale de `qualite_democratique` (V-Dem libéral plutôt que WGI, dérogation au critère « niveau 1 > 2 ») ; (3) rattachements proposés : `I_IUVOTE` (O2) et les 17 lignes `crim_pris_*` à `democratie` (DEM-5) ; (4) les mesures `I_IUPOL*` (expression politique en ligne) laissées à `logement_cadre_vie`.
- **Léo** : choix d'un seul indice par famille de composites (qualité démocratique, État de droit, corruption) ; WGI en principale pour l'État de droit et la corruption, le WJP et le CPI, plus connus mais plus courts, en variantes ; régionales et municipales réduites à 3 points ; participation des départementales gardée en variante sur 2 points.

## 5. Contrôles finaux

- `python scripts/preselection.py --dimension democratie --maj-fiches` : 269 lignes affectées (250 de la long-list, 19 importées : 17 de `securite`, 2 de `logement_cadre_vie`), 93 groupes (35 `fiche`, 44 `variante_de`, 12 `ecarte_en_bloc`, 2 `autre_dimension`).
- `python scripts/verifier_fiches.py --dimension democratie --tableau` : **0 erreur**, 2 avertissements attendus (`adhesion_syndicale` et `citoyennete_active`, séries hors catalogue) ; 35 fiches, 25 familles, 22 `retenir`, 10 `retenir_variante`, 3 `ecarter`, 10 déclaratives, 11 composites, 10 « à vérifier », 2 hors long-list, 13 incontournables, 102 variantes, 0 ligne prise ailleurs.
- `python -m pytest -q` : 399 réussis.
- Tableau de validation régénéré (`docs/validation/validation_democratie.csv`), `decision_leo` vide.
