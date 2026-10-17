# Journal — Transfert D49 (sécurité économique des ménages : `securite` → `niveau_de_vie`) et socles D50

Agent de mission du 17/10/2026, branche `m05-transfert-d49` (depuis `origin/main` au commit `597a3d3` : fusion transversale PR #36, grille v1.1, D47 à D50). Consigne de la session mère : exécuter le transfert D49 et les compléments de socle D50. Non modifiés : charte, journal des décisions, `CLAUDE.md`, fiches de mission, `dimensions.yaml`, table de correspondance, méthode 33, dimensions autres que `securite`, `niveau_de_vie`, `planete` (socle) et `travail` (socle). Dossier de travail non commité : `tmp/d49/` (scripts `fiches.py`, `regles.py`, sorties du vérificateur avant et après).

## 1. Mise en route et état de départ

- Lus : `CLAUDE.md` ; journal des décisions (D41, D45 à D50) ; méthode 33 v1.3 (§6, §7, §10) ; `indicateurs/dimensions.yaml` v1.1 (R9, contenu de `niveau_de_vie`) ; en-têtes de `scripts/preselection.py` et `scripts/verifier_fiches.py` ; `docs/cr/M05_transversal_gel2_journal.md` (§3, §3 ter, §4) ; `validation_securite.csv` et `validation_niveau_de_vie.csv` ; crosswalk (`docs/methodo/30_crosswalk_synthese.md` §5 et `30_indicateurs_cadres_reference.csv`).
- `python -m pytest -q` : 432 tests passés. Vérificateur : 0 erreur sur les 10 dimensions (`securite` : 35 fiches, 0 avertissement ; `niveau_de_vie` : 28 fiches, 7 avertissements, tous antérieurs : 2 séries DREES à cataloguer, 5 lignes R1 partagées avec des écarts construits d'`egalites`). `--lignes-renvoyées` : 0 orpheline, 0 renvoi hors long-list non repris, 0 ligne retenue et écartée ; couple `niveau_de_vie → securite` : 19 lignes (2 fiches, 15 variantes, 2 écartées).

## 2. Fiches transférées (11)

Toutes passent de `indicateurs/securite/` à `indicateurs/niveau_de_vie/` avec `dimension: niveau_de_vie` et `sous_theme: sécurité économique des ménages` (sous-thème ajouté au contenu de la dimension par la grille v1.1). Familles, variantes principales, variantes (`serie_id` uniques, D36), séries et recommandations conservées, sauf `solde_situation_financiere_future` (ci-dessous). Les 9 fiches dont la série principale est dans la long-list `securite` portent `rattachement_propose` (groupe de renvoi cité) et une note de transfert (décision `a_discuter` de Léo en `securite`, à revalider ici) ; `charge_remboursement_dettes_lourde` et `endettement_menages` (créées en `securite` par la reprise des renvois, D46) retrouvent leur long-list d'origine : `rattachement_propose` « à transférer » retiré, note mise à jour.

| Fiche | Famille | Principale | Recommandation | Incontournable | Socle proposé | Série principale (ligne) | Variantes |
|---|---|---|---|---|---|---|---|
| `depense_imprevue` | `depense_imprevue` | oui | retenir | oui | **oui** | estat-031706 | 5 (4 de la long-list securite, 1 manuelle Melodi) |
| `pauvrete_actifs_liquides` | `epargne_precaution` | oui | retenir | oui | non (dérogation) | m04-000007 | 0 |
| `retards_paiement` | `retards_paiement` | oui | retenir | non | non | estat-031708 | 11 (10 securite, 1 manuelle) |
| `surendettement` | `surendettement` | oui | retenir | non | non | bdm-000874 | 2 (securite) |
| `risque_pauvrete_ressenti` | `insecurite_economique_ressentie` | oui | retenir | non | non | m04-000263 | 0 |
| `solde_capacite_epargne_actuelle` | `capacite_epargne_percue` | oui | retenir | non | non | bdm-000701 | 1 (securite) |
| `solde_capacite_epargne_future` | `capacite_epargne_percue` | non | retenir_variante | non | non | bdm-000704 | 1 (securite) |
| `solde_situation_financiere_passee` | `situation_financiere_percue` | oui | retenir | non | non | bdm-000702 | 1 (hors_grille) |
| `solde_situation_financiere_future` | `situation_financiere_percue` | non | **ecarter** | non | non | bdm-000703 | 1 (hors_grille) |
| `charge_remboursement_dettes_lourde` | `charge_remboursement_dettes` | oui | retenir | non | non | estat-031755 | 5 (niveau_de_vie) |
| `endettement_menages` | `endettement_menages` | oui | retenir | non | non | estat-008085 | 10 (niveau_de_vie) |

- **`solde_situation_financiere_future`** : la fiche était `retenir_variante` ; Léo l'a écartée au gel 2 de `securite` (D49, `decision_leo: ecarte`). Recommandation alignée sur sa décision (`ecarter`, motif réécrit en ce sens, méthode 33 §10.1 : les décisions de Léo priment) ; la décision `ecarte` est reportée dans `validation_niveau_de_vie.csv`.
- **Incontournables** (crosswalk §5, ≥ 3 cadres) : « sécurité économique (dépense imprévue, épargne liquide) » réunit SSF (insécurité économique, proxy dépense imprévue), OCDE (1_6, insécurité financière : actifs liquides) et Eurostat QoL (dépense imprévue, indicateur phare) : **`depense_imprevue` et `pauvrete_actifs_liquides` gardent `incontournable: oui`** (familles distinctes, comme en `securite`). Non incontournables : arriérés de paiement (Eurostat seul), endettement des ménages (OCDE 15_6 et INSEE NIR : 2 cadres), surendettement, risque de pauvreté ressenti, soldes de conjoncture et charge de remboursement (aucun cadre).
- **Doublons avec `niveau_de_vie`** : `risque_pauvrete_ressenti` (modalité 1 de PE03, « oui, plutôt » : risque de devenir pauvre dans les cinq ans) et `pauvrete_ressentie` (modalité 3, « je me considère déjà comme pauvre », variante de la famille `pauvrete_subjective` dont `difficulte_joindre_deux_bouts` est principale) **restent en familles distinctes** : un risque anticipé ne se substitue pas à un état ressenti (l'utilisateur ne prendrait pas l'un pour l'autre, définition de la famille, D35), les deux modalités sont exclusives et se lisent ensemble (coordination NDV-4 / SEC-2), et une fusion ferait passer `risque_pauvrete_ressenti` en `retenir_variante` sans décision de Léo. Motif écrit dans les notes des deux fiches (références `securite/risque_pauvrete_ressenti` de `pauvrete_ressentie` mises à jour). Autres rapprochements vérifiés, sans doublon : `situation_financiere_percue` (évolution perçue, conjoncture) et `satisfaction_situation_financiere` (niveau de satisfaction, EU-SILC) ; `capacite_epargne_percue` et `taux_epargne_menages` (agrégat des comptes, écarté) ; `endettement_menages` et `patrimoine_menages` ; dépense imprévue et arriérés (`ilc_mdes04`, `ilc_mdes05`) ne figurent pas parmi les variantes de `privation_materielle_sociale`. Aucune série (principale, composante ou variante) des 11 fiches n'est partagée avec une autre fiche du dépôt.

## 3. Règles de présélection

| Dimension | Avant | Après | Changements |
|---|---|---|---|
| `securite` | 125 règles | 109 | règles 880 à 1080 (fiches et variantes de la sécurité économique, long-list `securite`) remplacées par **10 renvois `autre_dimension:niveau_de_vie`** à liste exacte de `ligne_id` (880 `depense_imprevue_niveau_de_vie` 5 lignes, 910 `retards_paiement_…` 11, 950 `surendettement_…` 3, 980 `pauvrete_actifs_liquides_…` 1, 990 `double_pauvrete_niveau_de_vie` 12, 1000 `risque_pauvrete_ressenti_…` 1, 1010 et 1030 soldes de situation financière 1 + 1, 1050 et 1070 soldes de capacité d'épargne 2 + 2), motif D49 (grille v1.1, R9) ; règles 1020 et 1040 (imports `hors_grille`) et 1170 à 1190 (lignes de la long-list `niveau_de_vie` reprises par `securite`) retirées ; 1195 (`ilc_li70b`, renvoyé par `egalites`, écarté) conservée |
| `niveau_de_vie` | 150 règles | 175 | règle 1120 (`endettement_menages`, `autre_dimension:securite`) remplacée par 5 règles à liste exacte (1120 fiche `endettement_menages`, 1121 ses 10 variantes, 1122 fiche `charge_remboursement_dettes_lourde`, 1123 ses 5 variantes, 1124 `actifs_financiers_nets_comptes` écarté en bloc) ; **21 règles de reprise** 1420 à 1520 (`longlist = securite`, et `hors_grille` pour les deux soldes CVS 1485 et 1495), motif citant `securite/<groupe>` : 9 fiches, 10 groupes de variantes, 1 écart en bloc (`double_pauvrete_actifs_liquides`, statistiques expérimentales `icw_pov_10` à `12` avec actifs liquides, même motif qu'en `securite`) |

Le renvoi de la double pauvreté (12 lignes écartées) accompagne le sous-thème : l'épargne de précaution relève désormais de `niveau_de_vie` (R9), dont la règle 450 garde en variantes de `taux_pauvrete_60` les lignes « pauvreté monétaire et de consommation » du même jeu. `--lignes-renvoyées` après transfert : couple `securite → niveau_de_vie` = **39 lignes (9 fiches, 18 variantes, 12 écartées, 0 relayée, 0 orpheline)** ; le couple `niveau_de_vie → securite` (19) disparaît ; total : 0 ligne orpheline, 0 renvoi hors long-list non repris, 0 ligne retenue et écartée.

**Table de correspondance** (`docs/methodo/31_correspondance_v0_v1.csv`, non modifiée) : la règle 19 (`niveau_de_vie` + « surendettement, dépenses imprévues, arriérés, impayés, épargne de précaution, actifs financiers liquides » → `securite`) existe ; elle place 13 des 39 lignes en `securite`, la règle 4 (`securite_confiance`, enquête de conjoncture : situation financière personnelle, capacité d'épargne) 6 lignes, la règle 6 (défaut `securite_confiance` → `securite`) les 20 autres. Correction à faire par la session mère : signalement **NDV-13** (`docs/cr/maintenance_catalogues_niveau_de_vie.md`) ; en attendant, le rattachement passe par les règles de présélection ci-dessus.

## 4. Socles proposés (D41, D50)

| Dimension | Socle proposé final | Motif (une ligne) |
|---|---|---|
| `niveau_de_vie` (7) | `niveau_vie_median`, `revenu_disponible_ajuste_habitant`, `taux_pauvrete_60`, `privation_materielle_sociale` | incontournables (inchangé) |
| | `privation_alimentaire`, `patrimoine_net_median` | accès à l'alimentation (A2) ; patrimoine (inchangé) |
| | **`depense_imprevue`** | sécurité économique des ménages : incontournable (SSF, OCDE, Eurostat), indicateur phare Eurostat QoL, annuel 2004-2025 sans lacune |
| | `pauvrete_actifs_liquides` hors socle, `derogation_socle` | même concept du crosswalk que `depense_imprevue`, 4 valeurs irrégulières (2009-2020) : une fiche au socle pour le sous-thème (D50) ; Léo peut l'ajouter (8e place libre) |
| `securite` (4) | `homicides`, `victimes_violences`, `cambriolages_logements`, `tues_route` | socle validé par Léo (D49) ; dérogations `delinquance_quartier`, `securite_nuit` inchangées |
| `planete` (8) | + **`deces_chaleur`** | aléas climatiques et adaptation (A14, D43, D50) |
| `travail` (5) | + **`taux_chomage`** | chômage (D50) |

Les 5 sous-thèmes de `niveau_de_vie` dans `dimensions.yaml` ont chacun au moins une fiche au socle proposé.

## 5. Tableaux de validation (méthode 33 §7)

- `validation_securite.csv` : 11 lignes des fiches transférées retirées (8 `a_discuter` et le commentaire commun de Léo : « ce qui relève de la sécurité économique correspond plutôt à la dimension niveau de vie », recopié dans la note de transfert de chaque fiche ; `ecarte` de `solde_situation_financiere_future`, reporté) puis tableau régénéré : 24 lignes, décisions et commentaires des 24 fiches restantes identiques, cellule par cellule (3 `retenu_socle`, 2 `retenu`, 19 vides) ; **plus aucune ligne `a_discuter`**.
- `validation_niveau_de_vie.csv` : 39 lignes ; une seule décision de Léo, `ecarte` sur `solde_situation_financiere_future` ; les 10 autres fiches transférées sont sans décision (Léo les revalidera ici).
- `validation_planete.csv`, `validation_travail.csv` : seule la colonne `socle_propose` de `deces_chaleur` et de `taux_chomage` change.
- `python scripts/classeur_validation.py exporter --dimension niveau_de_vie` : fonctionne (39 lignes, sous-thème « sécurité économique des ménages » dans la synthèse, `depense_imprevue` en `retenu_socle` par défaut, `solde_situation_financiere_future` à `ecarte`) ; classeur produit non commité (le fichier suivi a été restauré). Les classeurs suivis `validation_securite.xlsx` et `validation_niveau_de_vie.xlsx` sont donc antérieurs au transfert : à régénérer par la session mère.

## 6. Contrôles finaux

| Contrôle | Résultat |
|---|---|
| `python -m pytest -q` | 432 passés |
| Vérificateur, 10 dimensions | 0 erreur ; avertissements inchangés (`securite` 0, `niveau_de_vie` 7, `planete` 3, `travail` 4…) |
| `securite` | 35 → 24 fiches, 27 → 18 familles, `retenir` 22 → 13, `retenir_variante` 4 → 2, `ecarter` 9, déclaratifs 10 → 4, variantes 231 → 194, lignes renvoyées ailleurs 17 → 56, lignes reçues 75 → 56, incontournables `homicides`, `delinquance_quartier`, `securite_nuit` |
| `niveau_de_vie` | 28 → 39 fiches, 18 → 27 familles, `retenir` 17 → 26, `retenir_variante` 10 → 11, `ecarter` 1 → 2, déclaratifs 7 → 13, à vérifier 2 → 3, variantes 1 282 → 1 319, lignes renvoyées ailleurs 706 → 687, lignes reçues 105 → 144, incontournables 4 → 6, socle 6 → 7, 1 dérogation |
| `--lignes-renvoyées` | 0 orpheline, 0 renvoi hors long-list non repris, 0 ligne retenue et écartée |
| Séries principales partagées | aucune dans tout `indicateurs/` ; aucune série des 11 fiches partagée avec une autre fiche |

## 7. Questions et suites pour la session mère

1. **Socle de `niveau_de_vie`** : `pauvrete_actifs_liquides` reste incontournable mais hors socle (dérogation, consigne « une fiche ») ; la règle D41 stricte (incontournables + une fiche par sous-thème) donnerait 8 fiches avec elle. À confirmer, ou passer `socle_propose: oui` et retirer `derogation_socle` (une ligne, puis `--tableau`).
2. **Table de correspondance** : appliquer NDV-13 (règles 19 et 4 vers `niveau_de_vie`, exception avant la règle 6, remarques 3 et 6) ; après régénération des long-lists, vider la colonne `longlist` des règles 1420 à 1520 de `niveau_de_vie` et retirer les renvois 880 à 1070 de `securite`.
3. **Références à mettre à jour hors périmètre** (dimensions figées, non touchées) : `democratie/adhesion_syndicale.yaml` et `liens_bien_etre/cohesion_sociale_percue.yaml` citent « securite/risque_pauvrete_ressenti » (désormais `niveau_de_vie/risque_pauvrete_ressenti`) ; signalement SEC-2 (`maintenance_catalogues_securite.md`) : la fiche qu'il cite est maintenant en `niveau_de_vie`.
4. `ilc_li70b` (couverture des prestations des chômeurs, renvoyé par `egalites` à `securite`, écarté en `securite`, règle 1195) : laissé tel quel ; relève plutôt de `travail` (D39, D45) si la règle d'`egalites` est reprise un jour.
5. Classeurs `validation_securite.xlsx` et `validation_niveau_de_vie.xlsx` à régénérer (session mère).

## 8. Commits et pull request

Branche rebasée sur `origin/main` (`1b4b42b`, classeurs v1.3 de trois dimensions, sans conflit) avant le premier envoi. Commits : `1dbe497` (transfert D49 : fiches, règles, présélections, tableaux), `f3527cd` (socles D50 de `planete` et `travail`), `a2d5208` (journal et NDV-13), puis le numéro de la pull request dans ce journal. Pull request **#37** (« Transfert D49 : sécurité économique des ménages → niveau_de_vie ; socles proposés D50 »).
