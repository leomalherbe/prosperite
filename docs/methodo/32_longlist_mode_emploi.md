# Long-list commune des indicateurs — mode d'emploi

Script : `src/pipeline/longlist.py` (v1.0, mission M05-prep, 14 octobre 2026). Entrée exigée par la fiche M05 (section « Entrées ») et par la procédure du gel 2 (charte §3.6, étapes 1 et 2).

Le script réunit les catalogues de séries candidates, rattache chaque ligne à une dimension de la grille v1 figée, applique le filtre d'éligibilité mécanique de la charte (§3.4, avec les dérogations D16 à D19) et repère les lignes qui décrivent un même concept. **Aucune ligne n'est supprimée** et **aucune exclusion ne tient à la redondance** : le choix des familles, des variantes principales et des recommandations reste le travail des fiches M05.

> **État au 14/10/2026 : bilan provisoire seulement.** Les catalogues INSEE et Eurostat ne sont pas encore fusionnés dans `main` ; l'exécution a été faite sur des copies des branches `m01-insee` (passage complet) et `m02-eurostat` (niveau 2 non terminé, recalcul des unités annoncé par D26). Seul `catalogues/longlist_bilan.json` est commité ; les `.csv.gz` seront produits par l'exécution finale après la fusion des PR #1 et #2 (voir §3 et §7).

---

## 1. Relancer

```bash
pip install -r requirements.txt
python -m src.pipeline.longlist --dimension toutes          # toutes les sorties (CSV en clair) + bilan
python -m src.pipeline.longlist --dimension sante           # une seule dimension (bilan affiché, pas écrit)
python -m src.pipeline.longlist --dimension hors_grille     # lignes hors_v1, hors_grille, a_classer
python -m src.pipeline.longlist --dimension toutes --compresser --remarque "provenance des catalogues…"   # exécution finale
```

- Durée : environ une minute pour 200 000 lignes. Aucun accès réseau : le script lit des fichiers du dépôt ; il tourne donc aussi dans le bac à sable.
- Même avec une seule dimension, tous les catalogues sont lus (les doublons et les raccordements se cherchent dans l'ensemble).
- **Sur GitHub Actions** : `scripts/collecte_longlist.py` régénère la long-list en exécution finale (`--compresser`) ; le workflow « Collecte » commite le bilan et les `.csv.gz` (cible `collecte_longlist.py` : `python scripts/actions.py lancer --branche <b> --cible collecte_longlist.py`). Il ne fait rien tant que les quatre catalogues d'entrée ne sont pas présents sur la branche. Dans la collecte mensuelle de `main` (scripts lancés par ordre alphabétique), il passe après `collecte_eurostat.py` et `collecte_insee.py` : la long-list suit donc les catalogues.
- Tests hors ligne : `python -m pytest -q tests/test_longlist.py` (fixtures : vraies lignes des quatre catalogues dans `tests/fixtures/longlist/`).

## 2. Entrées

| Catalogue (`catalogue_origine`) | Fichier (`.csv` ou `.csv.gz`) | Producteur | Rang de source |
|---|---|---|---|
| `insee_bdm` | `catalogues/insee_bdm_catalogue.csv` | M01 | INSEE (1) |
| `insee_melodi` | `catalogues/insee_melodi_catalogue.csv` | M01 | INSEE (1) |
| `eurostat_series` | `catalogues/eurostat_series_catalogue.csv` | M02 (niveau 2) | Eurostat (2) |
| `autres_sources_m04` | `docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv` | M04 | autres (3) |
| (auxiliaire) | `catalogues/eurostat_jeux_catalogue.csv` | M02 (niveau 1) | sert seulement au raccordement par jeu source (§4.3) |

Plus la table `docs/methodo/31_correspondance_v0_v1.csv` (39 règles depuis le 14/10/2026 : les 31 règles du gel 1 corrigées et complétées par P1–P8, décision de la session mère ; détail dans `docs/cr/M05prep_journal.md`) et `indicateurs/dimensions.yaml` (identifiants v1). Les catalogues `*_non.csv.gz` d'INSEE (séries écartées par M01) ne sont pas lus : ils sont hors long-list par construction.

**Lecture tolérante** : UTF-8 (avec ou sans BOM) puis Windows-1252 ; séparateur virgule ou point-virgule (détecté sur l'en-tête) ; fichier compressé lu directement ; si `x.csv` et `x.csv.gz` coexistent, le plus récent est lu (avertissement). Une colonne attendue absente est laissée vide et signalée (journal et `avertissements` du bilan) ; un catalogue absent est ignoré et signalé. Les colonnes propres à un catalogue sont reprises sous un nom interne (correspondances : `CATALOGUES` dans le module).

## 3. Sorties

| Fichier | Contenu |
|---|---|
| `catalogues/longlist_<dimension>.csv` | une par dimension v1 : toutes les lignes rattachées, éligibles ou non |
| `catalogues/longlist_hors_grille.csv` | lignes `hors_v1`, `hors_grille` et `a_classer` |
| `catalogues/longlist_bilan.json` | chiffres (§5) |

CSV UTF-8, virgule, fins de ligne LF. **Règle de volume** (décision de la session mère du 14/10/2026) :
- par défaut, les CSV sont écrits **en clair** : ce sont des sorties de travail, **ignorées par git** (`catalogues/longlist_*.csv` dans `.gitignore`) ; un `.csv.gz` déjà présent n'est pas touché ;
- avec `--compresser` (exécution finale, et toujours sur le robot), ils sont écrits en **`.csv.gz`** (le `.csv` en clair du même nom est supprimé) ;
- **seuls `catalogues/longlist_bilan.json` et les `.csv.gz` d'une exécution finale sont commités.** Au 14/10, seul le bilan l'est : les `.csv.gz` seront produits par l'exécution finale après la fusion des catalogues INSEE et Eurostat.

`pandas.read_csv` lit indifféremment le `.csv` et le `.csv.gz`. Un `.csv` en clair, s'il existe, vient de la dernière exécution locale ; les `.csv.gz` commités, de la dernière exécution finale.

**Ordre des lignes** : les lignes d'un même concept sont regroupées, la ligne de référence en tête ; les concepts dont la référence est éligible viennent d'abord, puis « à vérifier », puis non éligibles.

## 4. Colonnes et règles

### 4.1 Schéma commun (colonnes demandées par la fiche)

| Colonne | Contenu |
|---|---|
| `source` | organisme (INSEE BDM, INSEE Melodi, Eurostat, nom de la source M04) |
| `voie_acces` | `insee_bdm_sdmx`, `insee_melodi_api`, `eurostat_api_statistics`, `api_niveau1`, `fichier_niveau2` (M04, d'après `niveau_source`) |
| `serie_id` | identifiant du catalogue (idbank ; requête Melodi ; requête Eurostat `code?filtres` ; identifiant ou URL M04 — **pas toujours unique** chez M04, voir `ligne_id`) |
| `libelle`, `unite`, `frequence`, `geo` | lus dans le catalogue |
| `premiere_periode`, `derniere_periode` | lues ; pour une ligne `ventilation` d'Eurostat, recalculées sur les modalités (§4.3) |
| `nb_points_depuis_2000` | années avec valeur depuis 2000 (`nb_annees_depuis_2000` INSEE, `nb_annees` Eurostat, `nb_points_depuis_2000` M04) ; **vide** pour les séries BDM infra-annuelles (non comptées par M01) |
| `dimension_v0` | étiquette du catalogue (orientation de moissonnage) |
| `dimension_v1` | rattachement v1 (§4.2) : une des 10 dimensions, ou `hors_v1`, `hors_grille`, `a_classer` |
| `candidat` | statut du catalogue source (`oui`, `a_verifier`, `non`, `ventilation` ; vide pour M04) |
| `ventilation` | dimension ventilée (vide = ensemble) |
| `declaratif` | `oui`/`non` lu (M04) ; sinon `presume` si le libellé évoque une opinion ou un ressenti (satisfaction, sentiment, santé perçue, confiance…), vide = inconnu |
| `composite`, `type` | lus (M04) ; `type = moyen` pour les séries INSEE marquées « type moyen (D19) » ; vide = inconnu |
| `url_api` | lue ; Eurostat : `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/` + `serie_id` (modèle documenté dans `docs/sources/eurostat.md` §2.2) ; M04 : l'identifiant s'il s'agit d'une URL |
| `url_page` | lue si le catalogue la fournit (aucun ne la fournit aujourd'hui : vide) |
| `commentaire` | commentaire du catalogue ; M04 : complété par `preuve : <fichier du robot>` |
| `catalogue_origine` | catalogue d'où vient la ligne |

### 4.2 Rattachement à la grille v1 — colonnes `regle_v1`, `rattachement_note`

- Pour chaque ligne : **première règle** de `31_correspondance_v0_v1.csv` (ordre de la colonne `ordre`) dont la `dimension_v0` est celle de la ligne **ou vaut `*`** et dont le `motif_libelle` (expression régulière, insensible à la casse) se trouve dans le libellé ; motif vide = s'applique à tout. Le motif est cherché dans le libellé aux apostrophes typographiques simplifiées et dans sa version sans accents.
- **Règles `*`** (communes à toutes les dimensions v0, aucune au 14/10) : elles ne s'appliquent à une dimension que si elles précèdent sa règle par défaut ; les placer en tête de table.
- **Ordre de la table** : pour chaque `dimension_v0`, les exceptions (motif non vide) puis une seule règle par défaut (motif vide), en dernier ; contrôlé par les tests.
- `dimension_v0` vide = `non_classe` (règle 39 → `a_classer`) ; `dimension_v0` absente de la table → `a_classer`, signalé.
- **Catalogue portant déjà une dimension v1** (`dimension_v1_proposee` de M04, ou une colonne `dimension_v1`) — **priorité** (décision de la session mère du 14/10/2026) : une **règle d'exception** de la table (motif non vide) **l'emporte** sur la proposition du catalogue (`regle_v1` = la règle ; note « exception de la table prioritaire (règle n) : catalogue → X, retenu → Y ») ; une **règle par défaut** (ou l'absence de règle) **lui cède** (`regle_v1` = `catalogue ; table : n` ; s'ils diffèrent, note « désaccord : catalogue → X (retenu), table → Y »). L'outil de M04 (`docs/sources/outils/construire_candidats.py`) applique la même table et la même priorité : au 14/10, `dimension_v1_proposee` y est recalculée et aucun écart ne subsiste.
- `regle_v1` = `ordre (code de règle)` de la règle appliquée ; `rattachement_note` signale aussi les dimensions v0 « déduites du seul regroupement » (M01).
- Le rattachement automatique est un premier jet (annexe du dossier du gel 1) : la fiche M05 peut le corriger en le motivant.

### 4.3 Éligibilité — colonnes `eligible`, `motif_exclusion`, `note_eligibilite`, `nb_annees_etendue`

`eligible` vaut `oui`, `non` ou `a_verifier`. `motif_exclusion` liste **tous** les motifs constatés (séparés par « ; », dans l'ordre ci-dessous) ; `note_eligibilite` explique les cas « à vérifier » (préfixe « à vérifier : ») et donne des informations non bloquantes.

| Motif | Règle | Bloquant ? |
|---|---|---|
| `hors_v1`, `hors_grille`, `a_classer` | dimension v1 hors des 10 dimensions | oui |
| `candidat_non` | le catalogue source dit `non` et aucun des critères ci-dessous ne l'explique (sinon c'est le motif recalculé, avec ses dérogations, qui compte : un « < 10 années » d'Eurostat peut devenir « à vérifier » par D17) | oui |
| `geo_non_nationale` | zone hors liste nationale : FR, FX, FE, FM, FR-D976, FEHM, FRANCE-F, FRANCE-FM, FRANCE-F_X_D976 et périmètres nationaux particuliers (FM99_FR00, FM_D99_D978, FM_H_CORSE_2018, FR-SPM-WF, FE_HPBIO, FR-UE, signalés en note) ; exemple exclu : `FRANCE-FM_X_R11` (métropole hors Île-de-France). Zone vide → à vérifier | oui |
| `frequence_non_agregable` | fréquence hors {annuelle, semestrielle, trimestrielle, bimestrielle, mensuelle, hebdomadaire, quotidienne, irrégulière, ponctuelle}, ou `agregable = non` (INSEE). Infra-annuelle agrégeable : note « agrégation annuelle à prévoir ». Fréquence vide → à vérifier | oui |
| `derniere_periode_avant_2020` | année de `derniere_periode` < 2020 (inconnue → à vérifier) | oui |
| `moins_de_10_points` | `nb_points_depuis_2000` < 10. Si le nombre de points est inconnu (BDM infra-annuelle) : étendue = années de max(première période, 2000) à la dernière (`nb_annees_etendue`) ; ≥ 10 → admis avec note, < 10 → motif | oui, **sauf dérogation** (ci-dessous) |

**Dérogations** (le motif `moins_de_10_points` reste écrit, la ligne passe à `a_verifier`) :
- **D17 — série irrégulière** : fréquence `irreguliere`, ou série dont les points sont espacés (étendue ≥ 10 années mais moins de points que d'années : enquêtes quinquennales, PISA, modules SILC…).
- **D16 — raccordement** : 10 points atteignables (de la première année du partenaire, au plus tôt 2000, à la dernière année de la ligne) grâce à (1) une autre ligne du **même concept** (§4.4) et de même ventilation, qui commence plus tôt et rejoint la ligne sans trou (préférence : même clé, INSEE > Eurostat > autres, la plus ancienne ; une ligne M04 et la série INSEE dont elle est déclarée doublon sont partenaires même si leur ventilation diffère) ; ou (2) pour Eurostat, le **jeu source** (`jeu_source`, ex. `ilc_pecs01` pour `sdg_01_10`), d'après les périodes du catalogue des jeux (toutes zones : borne haute) ; ou (3) un catalogue source qui annonce un « raccordement » (M01).
- **D18 (composites)** et **D19 (moyens)** ne sont jamais des motifs : simple note.

Notes non bloquantes : « raccordement souhaitable pour couvrir 2000-2009 (D16, catalogue source) » (série de ≥ 10 points qui commence après 2010) ; « champ à vérifier : statistiques d'entreprises ou d'échanges extérieurs » (libellé contenant NACE, entreprise(s), commerce international, balance des paiements — repérage du bruit des catalogues, voir §7).

### 4.4 Concepts et doublons — colonnes `cle_concept`, `concept_id`, `doublon_de`, `doublon_de_ligne`, `doublon_note`, `nb_lignes_concept`, `dimensions_concept`

- **`cle_concept`** : libellé en minuscules, sans accents ; découpé en segments (« — », « - » entre espaces, « ; ») ; retrait des segments qui ne sont qu'une **unité** (pourcentage, euros, millions d'euros, nombre, pour mille, indice, données CVS/brutes…), une **zone** (France, France métropolitaine, hors Mayotte…) ou une modalité de **total, sexe ou âge** (Ensemble, Total, Hommes, Femmes, « de 15 à 24 ans »…) ; puis retrait dans le reste des mentions de **ventilation** (« par sexe et âge », « par niveau d'éducation atteint »…), de **source** (INSEE, Eurostat, OCDE, Citepa, Banque mondiale… et parenthèses de source), d'**ODD**, d'**unité**, de **zone** et d'**année** (« (2005-2020) », « base 2020 ») ; mots vides retirés, **pluriels simplifiés** (règles régulières, mots invariables protégés). Exemples : « Taux de chômage au sens du BIT - Ensemble - France hors Mayotte - Données CVS » → `taux chomage sens bit` ; « Personnes en risque de pauvreté ou d'exclusion sociale — par âge » → même clé que la ligne totale.
- **Même concept** = même clé non vide, **ou** ligne M04 déclarée doublon strict (`doublon_insee_eurostat = oui`) d'un **idbank INSEE** présent dans la long-list (lu dans le commentaire « doublon : INSEE 0105… »). Un doublon M04 cité seulement par un **code de jeu Eurostat** ne fusionne pas (un jeu contient plusieurs séries : âge, unité, seuil…) : la série Eurostat probable (seule série par défaut du jeu) est donnée dans `doublon_note`, à vérifier. Les doublons M04 `partiel` sont seulement notés.
- **Ligne de référence** de chaque concept, dans cet ordre : éligible (`oui`, puis `a_verifier`, puis `non` — ajout au cahier des charges, pour qu'une série exclue ne serve pas de référence) ; **INSEE > Eurostat > autres** ; série la plus longue (points depuis 2000, à défaut étendue) ; **total avant ventilation** ; dernière période la plus récente ; `ligne_id`.
- `concept_id` = `ligne_id` de la référence ; `doublon_de` = `serie_id` de la référence (vide pour la référence), `doublon_de_ligne` = son `ligne_id` (utile quand le `serie_id` n'est pas unique) ; `doublon_note` = « même clé de concept », « doublon strict signalé par M04 : … », etc. ; `nb_lignes_concept` = taille du groupe ; `dimensions_concept` = dimensions v1 du groupe quand il y en a plusieurs (contrôle R1 : un concept dans deux dimensions est à trancher).
- **Une ligne `doublon_de` n'est pas écartée** : c'est une variante (autre zone, autre unité, ventilation, autre source). Deux définitions différentes d'un même phénomène (INSEE contre Eurostat) ont en général des clés différentes : la clé ne repère que les libellés quasi identiques, le regroupement en familles reste à faire en M05.

### 4.5 Autres colonnes

`ligne_id` (identifiant unique et stable tant que le catalogue ne change pas : `bdm-000001`, `melodi-…`, `estat-…`, `m04-…`, numéro de ligne du catalogue) ; `niveau_source` (1 = API, 2 = fichier ; INSEE et Eurostat : 1).

## 5. Bilan (`catalogues/longlist_bilan.json`)

- `date`, `script`, `grille` (version, statut, date de gel), `table_correspondance` (fichier, nombre de règles), `remarque` (texte libre de `--remarque` : provenance des catalogues), `catalogues` (fichier lu, lignes, colonnes absentes), `etat_des_collectes` (d'après `insee_bilan.json` et `eurostat_bilan.json` : collecte terminée ou non, jeux Eurostat restants), `avertissements`.
- `total`, `par_dimension.<id>`, `hors_grille` : `lignes`, `eligibles`, `a_verifier`, `non_eligibles`, `motifs` (par motif : nombre de lignes `non` et `a_verifier` qui le portent ; une ligne peut en porter plusieurs), `declaratifs` (`oui`, `presume`), `declaratifs_eligibles_ou_a_verifier`, `composites`, `ventilations`, `statistiques_entreprises_signalees` (lignes, dont éligibles), `concepts_distincts` (nombre de `concept_id`), `concepts_distincts_eligibles`, `concepts_distincts_eligibles_ou_a_verifier`, `lignes_de_reference`, `par_source` (lignes, éligibles, à vérifier par catalogue), `rattachement` (lignes par règle appliquée, `desaccords_catalogue_retenu`, `exceptions_table_prioritaires`).
- `hors_grille_par_statut`, `concepts_sur_plusieurs_dimensions`.

## 6. Utilisation en M05

1. `python -m src.pipeline.longlist --dimension <id>` puis lire `catalogues/longlist_<id>.csv` (sortie locale en clair ; les `.csv.gz` commités sont ceux de la dernière exécution finale).
2. Partir des lignes `eligible = oui` et `a_verifier`, regroupées par `concept_id` ; relire les « à vérifier » (D16/D17) et un échantillon des `non` (exclusion abusive = erreur de catalogue à corriger dans la branche de la source).
3. Relire `rattachement_note` (désaccords) et `dimensions_concept` (concepts à cheval) ; toute correction de rattachement est motivée dans la fiche, la session mère tranche.
4. Écarter le bruit de catalogue signalé (`note_eligibilite` contenant « champ à vérifier ») après contrôle.

## 7. Limites connues

- **Catalogues partiels ou provisoires** (14/10) : INSEE et Eurostat copiés de branches non fusionnées ; Eurostat : niveau 2 non terminé (1 jeu restant) et recalcul des unités annoncé (D26). Tous les chiffres sont à régénérer après fusion.
- **Bruit du catalogue Eurostat** : environ 100 000 lignes (dont 39 000 éligibles) portent un libellé de statistiques d'entreprises ou d'échanges extérieurs (commerce international de services `bop_its6_det`, démographie des entreprises `bd_*`, statistiques structurelles `sbs_*`, coût de la main-d'œuvre `lc_*`, TIC des entreprises `isoc_*`…), entrées par la règle « dossier prioritaire » de M02 (dossiers numérique et culture) et étiquetées surtout `education` et `travail` ; s'y ajoutent les comptes financiers par secteur (`nasa_10_f_*`, `naidsa_10_f_*`) en niveau de vie. Le script les **signale** sans les exclure (la liste des motifs est fermée). Le nettoyage est fait **en amont par M02** (préfixes hors périmètre, décision de la session mère du 14/10) ; la table garde des règles de **filet de sécurité** : comptes par secteur hors ménages → `hors_v1` (règle 21, P6), dette publique et investissement → `hors_v1` (règle 22), soldes d'opinion de conjoncture → `hors_grille` (règle 5).
- **Étiquette v0 d'Eurostat** : une seule par jeu, recopiée sur toutes ses séries ; le rattachement v1 en hérite.
- **Clé de concept** : heuristique sur le libellé ; elle regroupe les variantes de zone, d'unité, de sexe et d'âge d'une même série, mais rarement deux sources différentes (14 concepts communs à plusieurs catalogues au 14/10) ; elle peut regrouper à tort des séries qui ne diffèrent que par un segment retiré (ex. une modalité d'âge porteuse de sens). Le regroupement en familles reste le travail de M05.
- **Raccordement** : condition nécessaire (périodes compatibles), pas suffisante (définitions à comparer) ; périodes des jeux Eurostat toutes zones confondues.
- **Points des séries BDM infra-annuelles** non comptés par M01 : étendue utilisée (borne haute).
- **`declaratif = presume`** : repérage par mots du libellé, à confirmer ; `composite` et `type` sont inconnus (vides) hors M04.
- **Dimension v1 proposée par M04** : recalculée le 14/10 avec la table corrigée (8 lignes changent : A14, A4, A5, P4) ; avec la priorité des exceptions, aucun désaccord ne subsiste. Une future proposition contraire à une règle par défaut serait retenue et signalée.
- **Doublons déclarés par M04** repris tels quels : une erreur de M04 se propagerait (cas corrigé le 14/10 : l'indice de Gini de la Banque mondiale était déclaré doublon strict de l'idbank 010594680, qui est le rapport S80/S20 ; il est désormais `partiel`, « Gini INSEE dans Melodi, pas d'idbank BDM »).
- **Rattachements encore discutables** (non traités par P1–P8) : domaines Eurostat de satisfaction « Lieu de résidence » et « Temps de trajet domicile/travail » restés en `liens_bien_etre` ; règle 11 « en ligne » qui envoie aussi en cadre de vie le commerce électronique des entreprises (bruit M02).
