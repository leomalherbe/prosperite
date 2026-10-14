# Journal de bord — M05, dimension `planete` (Planète)

Agent de mission M05 (dimension Planète, type plafond), branche `m05-planete`, 14 octobre 2026. Méthode commune appliquée : `docs/methodo/33_methode_fiches_M05.md` (v1.1), modèles `securite`, `liens_bien_etre`, `egalites`, `democratie` et audits M06.

## 0. Mise en route (10 h 05)

- Branche `m05-planete` créée depuis `origin/main` (`1a0697c`, fusion de la PR #12).
- Lus : `CLAUDE.md` ; charte §3.1 à §3.6, §4, §5.1 ; journal des décisions D13 à D33 (en particulier D15, D16, D17, D18, D19, D23 à D28, D32, D33) ; fiche M05 ; méthode commune v1.1 ; `indicateurs/dimensions.yaml` (définition, contenu, exclusions de `planete`, R1 à R8) ; fiches et règles des dimensions faites ; compte rendu `egalites` ; audits M06 `securite` et `liens_bien_etre` ; §5 et §8 de `30_crosswalk_synthese.md` ; lignes `planete` de `30_indicateurs_cadres_reference.csv` ; `10_indicateurs_candidats_hors_insee_eurostat.csv` ; `docs/sources/autres_sources.md` ; extraits du robot M04 (`docs/sources/series/` : Citepa, OCDE, OWID, SPF, SDES, Footprint Data Foundation, PNUD).
- Tests au départ : `python -m pytest -q` → 397 réussis.
- Outils communs utilisés tels quels (`scripts/preselection.py`, `scripts/verifier_fiches.py`) ; aucun fichier de `scripts/` ni de `src/` modifié (pas de déclenchement du robot « Collecte »). Les générateurs de travail (règles, fiches) restent dans le bac à sable ; leur produit est entièrement dans le dépôt.
- Présélections des autres dimensions relues (R1, D32) : aucune ligne de la long-list `planete` n'y est utilisée, aucune règle `autre_dimension:planete` ; la règle `crim_off_cat_non_eligibles` de `securite` mentionne les infractions environnementales (non éligibles), sans renvoi.

## 1. Ce que contient la long-list `planete` (10 h 15)

21 533 lignes : 15 945 éligibles, 559 à vérifier, 5 029 non éligibles. Eurostat 21 063 (229 jeux), INSEE BDM 194, Melodi 205, sources M04 71 (Citepa 21, OCDE 19, SDES 11, OWID 9, PNUD 3, Banque mondiale 3, Footprint Data Foundation 3, EDGAR 1, Santé publique France 1).

| Bloc | Lignes | Constat |
|---|---|---|
| Bilans énergétiques Eurostat (`nrg_cb_*`, `nrg_bal_*`, stocks, échanges, capacités, pompes à chaleur) | ≈ 11 000 | matière première des indicateurs agrégés, aucune lecture propre |
| Pesticides par culture et par substance (`aei_pestuse`) | 3 067 | 2 points par culture (2011, 2021) |
| Dépenses, subventions, taxes et investissements de protection de l'environnement (`env_epea_*`, `env_esst_*`, `env_ac_ep*`, `env_ac_pep*`, `env_ac_tax*`) | ≈ 2 270 | moyens budgétaires (charte §3.4) |
| Inventaires détaillés GES (`env_air_gge`, 811) et polluants (`env_air_emis`, 911), comptes d'émissions (`env_ac_ai*`) | ≈ 2 100 | sous-catégories CRF/NFR, tableaux de passage |
| Déchets (échanges, installations, emballages, DEEE, VHU, traitement) | ≈ 1 200 | détails techniques |
| Indicateurs ODD nationaux INSEE (BDM et Melodi `DS_NAT_SDG`, doublons l'un de l'autre) | ≈ 350 | cœur de la dimension (climat, énergie, eau, biodiversité, sols, déchets, agriculture) |
| Comptes de patrimoine (ressources naturelles en valeur, `DD_CNA_*`) | 49 | patrimoine national (A5) |
| Sources M04 (Citepa, OCDE How's Life « capital naturel », OWID, SDES ITDD, SPF, Footprint, PNUD, Banque mondiale) | 71 | |

Lignes à signaler : les masses d'eau (ODD 6.i2, 14.i1 : 4 points 2013-2021) et le gaspillage alimentaire (ODD 12.i3 : 5 points 2015-2023) sont **non éligibles** dans la long-list alors que D28 les rend candidates (écart moyen ≥ 1,5 an) : la règle de `src/pipeline/longlist.py` n'admet la souplesse D17 que si l'étendue atteint 10 ans (maintenance PLA-1).

## 2. Présélection (10 h 30)

- `docs/validation/regles_preselection_planete.csv` écrit par un générateur (bac à sable) : séries principales exactes (`ligne_id`), variantes précises, un import (`logement_cadre_vie`), écarts en bloc par expression sur `serie_id`, renvois.
- `python scripts/preselection.py --dimension planete` → **21 534 lignes affectées** (21 533 de la long-list, aucune sans règle, aucune règle vide ; 1 importée : OCDE 9_3 « population exposée à des températures extrêmes » de `logement_cadre_vie`, rattachement proposé au titre d'A14), **219 groupes** : 73 `fiche`, 120 `variante_de`, 23 `ecarte_en_bloc`, 3 `autre_dimension`.
