"""Définition des indicateurs candidats hors INSEE/Eurostat (mission M04, T3).

Chaque appel à `ajouter()` décrit un indicateur et le rattache à une série repérée par le robot
(`serie(...)`, `annees_*()`), dont les années sont lues automatiquement. Voir construire_candidats.py.

Conventions :
- sens : haut (plus c'est élevé, mieux c'est) | bas | ambigu ;
- declaratif : oui pour une donnée d'enquête d'opinion, de perception ou de ressenti (y compris
  auto-évaluation de la santé, victimation déclarée, difficultés financières déclarées) ; non pour une
  mesure administrative, une estimation statistique ou une évaluation d'experts ;
- composite : oui pour un indice agrégeant plusieurs sous-indicateurs ou sources (D18) ;
- type : resultat | moyen | pression (D19) ;
- doublon_insee_eurostat : oui (même définition chez l'INSEE ou Eurostat), partiel (concept proche,
  définition, source ou champ différents), non. `ref_doublon` cite l'identifiant du doublon dans
  docs/sources/insee_indicateurs_reperes.csv (branche m01-insee, « INSEE <serie_id> ») ou dans
  catalogues/eurostat_jeux_catalogue.csv (branche m02-eurostat, « Eurostat <code_jeu> ») ; plusieurs
  références sont séparées par « + » ;
- geo : FR (France, champ du producteur), FE (France entière), FM (France métropolitaine / hexagonale),
  FR-D976 (France hors Mayotte), FR-UE (hexagone + outre-mer inclus dans l'UE, périmètre des inventaires
  d'émissions) ;
- ventilation : vide pour l'ensemble ; sinon la modalité (D21 : ventilations gardées, marquées).
"""

import re

import pandas as pd

from construire_candidats import (SERIES, ajouter, annees_fichiers, annees_liste, annees_texte, serie,
                                  serie_banque_mondiale_phase1)

# ============================================================================ outils de lecture dédiés

DREES_DISTRIB = "docs/sources/series/drees__barometre_2000_2025_distributions.csv"


def serie_drees(variable: str, modalites: list[str]) -> dict:
    """Baromètre d'opinion DREES : années où la variable a des réponses (parts pondérées calculées par le robot)."""
    d = pd.read_csv(SERIES / "drees__barometre_2000_2025_distributions.csv", dtype=str)
    x = d[(d.variable == variable) & d.modalite.isin(modalites)].copy()
    x["p"] = x.part_ponderee.astype(float)
    somme = x.groupby("annee").p.sum().round(2)
    return annees_liste([int(a) for a in somme.index], DREES_DISTRIB, n_distinctes=somme.nunique())


def serie_elections(motif: str) -> dict:
    """Participation par scrutin (agrégation nationale du fichier au bureau de vote par le robot)."""
    d = pd.read_csv(SERIES / "interieur_elections__participation_par_scrutin.csv", dtype=str)
    x = d[d.id_election.str.fullmatch(motif)]
    return annees_liste([int(i[:4]) for i in x.id_election],
                        "docs/sources/series/interieur_elections__participation_par_scrutin.csv",
                        n_distinctes=x.ratio_votants_inscrits.nunique())


def edgar_annees() -> dict:
    """EDGAR : années renseignées sur la ligne France de la feuille « TOTALS BY COUNTRY »."""
    texte = (SERIES / "edgar__ghg_ar5_france.txt").read_text(encoding="utf-8")
    feuille = texte.split("TOTALS BY COUNTRY", 2)[-1]
    entete = next(l for l in feuille.splitlines() if "Country_code_A3" in l)
    ligne = next(l for l in feuille.splitlines() if "| FRA | France |" in l)
    noms = [c.strip() for c in entete.split("] ", 1)[1].split(" | ")]
    valeurs = [c.strip() for c in ligne.split("] ", 1)[1].split(" | ")]
    ans = [int(n[2:]) for n, v in zip(noms, valeurs) if re.fullmatch(r"Y_\d{4}", n) and v not in ("", "None")]
    return annees_liste(ans, "docs/sources/series/edgar__ghg_ar5_france.txt")


# ============================================================================ OCDE — How's Life?
GALLUP = ("Source primaire : Gallup World Poll (confirmé par les métadonnées OCDE, PDF « How's Life? "
          "Well-being Database: definitions and metadata », lu par le robot) ; ~1 000 personnes par an ; "
          "moyennes groupées 2006-07 puis triennales 2008-10 … 2023-25, la même valeur étant répétée "
          "chaque année du bloc (7 valeurs depuis 2006) ; conditions de réutilisation des données Gallup "
          "non précisées dans ces métadonnées (non trouvé)")
GALLUP_PREUVE = "docs/sources/series/ocde__hsl_definitions_pdf.txt"
HSL = [
    # mesure, flux, motif d'unité, libellé, dim v0, sens, déclaratif, type, composite, doublon, ref, commentaire
    ("1_1", "cwb", None, "Revenu disponible net ajusté des ménages par habitant (USD PPA)", "niveau_de_vie", "haut", "non", "resultat", "non", "partiel", "", "Comptes nationaux en USD PPA ; l'INSEE publie le revenu disponible brut ajusté en euros"),
    ("1_2", "cwb", None, "Rapport des revenus disponibles moyens du quintile supérieur et du quintile inférieur", "egalites", "bas", "non", "resultat", "non", "oui", "INSEE 010594680 + Eurostat ilc_di11", "Équivalent du S80/S20"),
    ("1_3", "cwb", None, "Patrimoine net médian des ménages (USD PPA)", "niveau_de_vie", "haut", "non", "resultat", "non", "partiel", "", "Base OCDE de la distribution du patrimoine ; INSEE : enquête Patrimoine (euros)"),
    ("1_3_VER", "cwb", None, "Part du patrimoine détenue par les 10 % de ménages les plus riches", "egalites", "bas", "non", "resultat", "non", "partiel", "", "L'INSEE publie un Gini du patrimoine (ODD 10), pas cette part"),
    ("1_4", "cwb", None, "Taux de pauvreté monétaire relative (seuil OCDE à 50 % du revenu médian)", "niveau_de_vie", "bas", "non", "resultat", "non", "partiel", "Eurostat ilc_li02", "Seuil à 50 % ; INSEE et Eurostat publient aussi le seuil à 50 % (ilc_li02 par seuil)"),
    ("1_5", "cwb", None, "Difficulté à joindre les deux bouts", "niveau_de_vie", "bas", "oui", "resultat", "non", "oui", "Eurostat ilc_mdes09", "Question EU-SILC"),
    ("1_6", "cwb", None, "Pauvreté en actifs liquides (épargne liquide inférieure à 3 mois du seuil de pauvreté)", "securite_confiance", "bas", "non", "resultat", "non", "non", "", "Sécurité économique (épargne de précaution) ; enquêtes patrimoine (HFCS)"),
    ("2_1", "cwb", None, "Taux d'emploi des 25-64 ans", "travail", "haut", "non", "resultat", "non", "oui", "Eurostat lfsa_ergaed", "Enquête Forces de travail"),
    ("2_2", "cwb", None, "Écart de salaire médian entre femmes et hommes (temps plein)", "egalites", "bas", "non", "resultat", "non", "partiel", "Eurostat earn_gr_gpgr2", "Eurostat publie l'écart des salaires horaires moyens"),
    ("2_3", "cwb", None, "Taux de chômage de longue durée", "travail", "bas", "non", "resultat", "non", "oui", "Eurostat une_ltu_a + INSEE 010605073", ""),
    ("2_4", "cwb", None, "Jeunes de 15-24 ans ni en emploi ni en formation (NEET)", "travail", "bas", "non", "resultat", "non", "oui", "Eurostat edat_lfse_20", "Eurostat publie aussi les 15-29 ans"),
    ("2_5", "cwb", None, "Insécurité sur le marché du travail (perte de revenu attendue en cas de chômage)", "travail", "bas", "non", "resultat", "non", "non", "", "Indicateur OCDE de qualité de l'emploi"),
    ("2_6", "cwb", None, "Tension au travail (job strain)", "travail", "bas", "oui", "resultat", "oui", "partiel", "", "Indice OCDE construit sur l'enquête européenne sur les conditions de travail (Eurofound)"),
    ("2_7", "cwb", None, "Salariés travaillant au moins 50 heures par semaine", "travail", "bas", "non", "resultat", "non", "partiel", "Eurostat lfsi_hwu_a", "Eurostat diffuse les durées habituelles par tranche (seuils différents)"),
    ("2_8", "cwb", None, "Salaire brut annuel moyen (USD PPA)", "niveau_de_vie", "haut", "non", "resultat", "non", "partiel", "", "L'INSEE publie le salaire moyen en euros"),
    ("2_8_DEP", "cwb", None, "Salariés à temps plein gagnant moins des deux tiers du salaire médian", "travail", "bas", "non", "resultat", "non", "partiel", "Eurostat earn_ses_pub1s", "Enquête sur la structure des salaires (quadriennale) chez Eurostat"),
    ("2_8_VER", "cwb", None, "Rapport interdécile D9/D1 des salaires à temps plein", "egalites", "bas", "non", "resultat", "non", "partiel", "", "L'INSEE publie le D9/D1 des salaires (DSN)"),
    ("2_9", "cwb", None, "Satisfaction au travail (0-10)", "travail", "haut", "oui", "resultat", "non", "oui", "Eurostat ilc_pw05", "Module bien-être EU-SILC"),
    ("3_1", "cwb", None, "Ménages vivant dans un logement surpeuplé", "logement_cadre_vie", "bas", "non", "resultat", "non", "oui", "Eurostat ilc_lvho05a + INSEE 010596142", "EU-SILC"),
    ("3_2", "cwb", None, "Accessibilité financière du logement (part du revenu restant après dépenses de logement)", "logement_cadre_vie", "haut", "non", "resultat", "non", "partiel", "", "Comptes nationaux ; l'INSEE publie le taux d'effort"),
    ("3_3", "cwb", None, "Surcharge des coûts du logement (plus de 40 % du revenu)", "logement_cadre_vie", "bas", "non", "resultat", "non", "oui", "Eurostat ilc_lvho07a", "EU-SILC"),
    ("3_4", "cwb", None, "Ménages disposant d'un accès internet à domicile", "education", "haut", "non", "moyen", "non", "oui", "Eurostat isoc_ci_in_h", "Enquête TIC"),
    ("3_5", "cwb", None, "Incapacité à maintenir le logement à bonne température", "logement_cadre_vie", "bas", "oui", "resultat", "non", "oui", "Eurostat ilc_mdes01", "EU-SILC, auto-évaluation"),
    ("4_1", "cwb", None, "Temps consacré aux loisirs et aux soins personnels (heures par jour)", "liens_bien_etre", "haut", "non", "resultat", "non", "partiel", "", "Enquête Emploi du temps"),
    ("4_2", "cwb", None, "Personnes effectuant de longues heures de travail non rémunéré", "egalites", "bas", "non", "resultat", "non", "partiel", "", "Enquête Emploi du temps"),
    ("4_3", "cwb", None, "Écart femmes-hommes de temps de travail total (minutes par jour)", "egalites", "bas", "non", "resultat", "non", "partiel", "", "Enquête Emploi du temps"),
    ("4_4", "cwb", None, "Satisfaction à l'égard de l'emploi du temps (0-10)", "liens_bien_etre", "haut", "oui", "resultat", "non", "oui", "Eurostat ilc_pw05", "Module bien-être EU-SILC"),
    ("4_4_DEP", "cwb", None, "Part des personnes peu satisfaites de leur emploi du temps (note < 5)", "liens_bien_etre", "bas", "oui", "resultat", "non", "partiel", "Eurostat ilc_pw05", "Calcul OCDE sur EU-SILC"),
    ("4_4_VER", "cwb", None, "Inégalité de satisfaction à l'égard de l'emploi du temps (rapport des quintiles)", "egalites", "bas", "oui", "resultat", "non", "non", "", "Calcul OCDE sur EU-SILC"),
    ("5_1", "cwb", None, "Espérance de vie à la naissance (OCDE)", "sante", "haut", "non", "resultat", "non", "oui", "Eurostat demo_mlexpec", ""),
    ("5_2", "cwb", None, "Santé perçue comme bonne ou très bonne", "sante", "haut", "oui", "resultat", "non", "oui", "Eurostat hlth_silc_01", "EU-SILC"),
    ("5_2_DEP", "cwb", None, "Santé perçue comme mauvaise ou très mauvaise", "sante", "bas", "oui", "resultat", "non", "oui", "Eurostat hlth_silc_01", "EU-SILC"),
    ("5_3", "cwb", None, "Décès par suicide, alcool ou drogue (« morts de désespoir »)", "sante", "bas", "non", "resultat", "non", "partiel", "Eurostat hlth_cd_asdr2", "Agrégat OCDE de causes de décès ; Eurostat diffuse chaque cause séparément"),
    ("5_4", "cwb", None, "Dépression déclarée", "sante", "bas", "oui", "resultat", "non", "oui", "Eurostat hlth_ehis_mh1e", "Enquête EHIS"),
    ("6_1", "cwb", None, "Score moyen des élèves de 15 ans en compréhension de l'écrit (PISA)", "education", "haut", "non", "resultat", "non", "partiel", "INSEE DS_NAT_SDG?INDICATOR_SDG=4.i1a", "Enquête triennale (D17) ; l'INSEE (ODD 4) diffuse des parts d'élèves selon le niveau, pas le score moyen"),
    ("6_1_DEP", "cwb", None, "Élèves de 15 ans en difficulté dans les trois domaines PISA", "education", "bas", "non", "resultat", "non", "partiel", "INSEE DS_NAT_SDG?INDICATOR_SDG=4.i1a", "Enquête triennale (D17)"),
    ("6_1_VER", "cwb", None, "Écart de scores PISA en compréhension de l'écrit (rapport D9/D1)", "egalites", "bas", "non", "resultat", "non", "non", "", "Enquête triennale (D17)"),
    ("6_2", "cwb", None, "Score moyen des élèves de 15 ans en mathématiques (PISA)", "education", "haut", "non", "resultat", "non", "partiel", "INSEE DS_NAT_SDG?INDICATOR_SDG=4.i1a", "Enquête triennale (D17)"),
    ("6_2_VER", "cwb", None, "Écart de scores PISA en mathématiques (rapport D9/D1)", "egalites", "bas", "non", "resultat", "non", "non", "", "Enquête triennale (D17)"),
    ("6_3", "cwb", None, "Score moyen des élèves de 15 ans en sciences (PISA)", "education", "haut", "non", "resultat", "non", "partiel", "", "Enquête triennale (D17)"),
    ("6_3_VER", "cwb", None, "Écart de scores PISA en sciences (rapport D9/D1)", "egalites", "bas", "non", "resultat", "non", "non", "", "Enquête triennale (D17)"),
    ("6_4", "cwb", None, "Compétences des adultes en calcul (PIAAC)", "education", "haut", "non", "resultat", "non", "non", "", "Deux cycles (2012, 2023)"),
    ("6_4_DEP", "cwb", None, "Adultes ayant de faibles compétences en calcul (PIAAC)", "education", "bas", "non", "resultat", "non", "non", "", "Deux cycles"),
    ("6_4_VER", "cwb", None, "Écart de compétences des adultes en calcul (rapport D9/D1)", "egalites", "bas", "non", "resultat", "non", "non", "", "Un seul cycle"),
    ("6_5", "cwb", None, "Compétences des adultes en littératie (PIAAC)", "education", "haut", "non", "resultat", "non", "non", "", "Deux cycles"),
    ("6_5_VER", "cwb", None, "Écart de compétences des adultes en littératie (rapport D9/D1)", "egalites", "bas", "non", "resultat", "non", "non", "", "Un seul cycle"),
    ("7_1", "cwb", None, "Soutien social (avoir quelqu'un sur qui compter en cas de difficulté)", "liens_bien_etre", "haut", "oui", "resultat", "non", "partiel", "Eurostat ilc_scp15", GALLUP + " ; EU-SILC (ilc_scp15) mesure un concept proche en 2015 seulement"),
    ("7_1_DEP", "cwb", None, "Absence de soutien social", "liens_bien_etre", "bas", "oui", "resultat", "non", "partiel", "Eurostat ilc_scp15", GALLUP),
    ("7_2", "cwb", None, "Temps consacré aux interactions sociales (heures par semaine)", "liens_bien_etre", "haut", "non", "resultat", "non", "partiel", "", "Enquête Emploi du temps"),
    ("7_3", "cwb", None, "Satisfaction à l'égard des relations personnelles (0-10)", "liens_bien_etre", "haut", "oui", "resultat", "non", "oui", "Eurostat ilc_pw05", "Module bien-être EU-SILC"),
    ("7_3_DEP", "cwb", None, "Part des personnes peu satisfaites de leurs relations personnelles (note < 5)", "liens_bien_etre", "bas", "oui", "resultat", "non", "partiel", "Eurostat ilc_pw05", "Calcul OCDE sur EU-SILC"),
    ("7_3_VER", "cwb", None, "Inégalité de satisfaction à l'égard des relations personnelles (rapport des quintiles)", "egalites", "bas", "oui", "resultat", "non", "non", "", "Calcul OCDE sur EU-SILC"),
    ("7_4", "cwb", None, "Sentiment de solitude", "liens_bien_etre", "bas", "oui", "resultat", "non", "partiel", "", "EU-SILC (modules 2018 et 2022) ; aucun jeu Eurostat « solitude » repéré dans le catalogue M02"),
    ("8_1", "cwb", None, "Avoir son mot à dire sur l'action des pouvoirs publics", "democratie", "haut", "oui", "resultat", "non", "non", "", "Enquête OCDE sur les déterminants de la confiance (2021, 2023)"),
    ("8_1_DEP", "cwb", None, "Ne pas avoir son mot à dire sur l'action des pouvoirs publics", "democratie", "bas", "oui", "resultat", "non", "non", "", "Enquête OCDE sur la confiance"),
    ("8_2", "cwb", None, "Participation électorale aux élections législatives (OCDE)", "democratie", "haut", "non", "resultat", "non", "partiel", "INSEE 001778320", "L'INSEE diffuse la participation aux présidentielles, régionales, départementales, européennes ; voir les lignes Ministère de l'Intérieur"),
    ("9_1", "cwb", None, "Population urbaine ayant accès à des espaces verts", "logement_cadre_vie", "haut", "non", "resultat", "non", "non", "", "Estimation géospatiale OCDE"),
    ("9_2", "cwb", None, "Population exposée à plus de 10 µg/m³ de PM2,5", "logement_cadre_vie", "bas", "non", "resultat", "non", "partiel", "INSEE 010596141", "INSEE (ODD 11) : concentrations de PM10, pas l'exposition aux PM2,5"),
    ("9_3", "cwb", None, "Population exposée à des températures extrêmes", "logement_cadre_vie", "bas", "non", "resultat", "non", "non", "", "Estimation géospatiale OCDE"),
    ("10_1", "cwb", None, "Taux d'homicides (OCDE, causes de décès)", "securite_confiance", "bas", "non", "resultat", "non", "partiel", "INSEE 010596040 + Eurostat crim_hom_soff", "Source causes de décès ; INSEE et Eurostat diffusent les homicides enregistrés par la police"),
    ("10_2", "cwb", None, "Sentiment de sécurité en marchant seul la nuit", "securite_confiance", "haut", "oui", "resultat", "non", "non", "", GALLUP + " ; aucun équivalent INSEE/Eurostat repéré (le sentiment d'insécurité SSMSI est une autre question)"),
    ("10_2_DEP", "cwb", None, "Sentiment d'insécurité en marchant seul la nuit", "securite_confiance", "bas", "oui", "resultat", "non", "non", "", GALLUP),
    ("10_3", "cwb", None, "Décès sur la route (mortalité routière pour 100 000 habitants)", "sante", "bas", "non", "resultat", "non", "oui", "INSEE 010593288 + Eurostat tran_sf_roadus", "INSEE : nombre de tués"),
    ("11_1", "cwb", None, "Satisfaction dans la vie (0-10, OCDE)", "liens_bien_etre", "haut", "oui", "resultat", "non", "oui", "INSEE 010593281 + Eurostat ilc_pw01", "EU-SILC ; l'INSEE diffuse une série annuelle 2010-2024 (SRCV)"),
    ("11_1_DEP", "cwb", None, "Part des personnes peu satisfaites de leur vie (note < 5)", "liens_bien_etre", "bas", "oui", "resultat", "non", "partiel", "INSEE 010593281", "L'INSEE diffuse la satisfaction « faible (0-5) » en ventilation"),
    ("11_1_VER", "cwb", None, "Inégalité de satisfaction dans la vie (rapport des quintiles supérieur et inférieur)", "egalites", "bas", "oui", "resultat", "non", "non", "", ""),
    ("11_2", "cwb", None, "Bilan émotionnel négatif (plus d'émotions négatives que positives la veille)", "liens_bien_etre", "bas", "oui", "resultat", "non", "non", "", GALLUP),
    ("11_3", "cwb", None, "Douleur physique ressentie la veille", "sante", "bas", "oui", "resultat", "non", "non", "", GALLUP),
    ("12_1", "fwb", None, "Part des terres en couverture naturelle ou semi-naturelle", "planete", "haut", "non", "resultat", "non", "partiel", "", "Télédétection ; l'INSEE diffuse l'artificialisation des sols (autre source)"),
    ("12_2", "fwb", None, "Perte de couverture naturelle et semi-naturelle", "planete", "bas", "non", "pression", "non", "non", "", ""),
    ("12_3", "fwb", None, "Gain de couverture naturelle et semi-naturelle", "planete", "haut", "non", "resultat", "non", "non", "", ""),
    ("12_5", "fwb", None, "Aires protégées terrestres (% du territoire, OCDE)", "planete", "haut", "non", "moyen", "non", "partiel", "Eurostat env_bio4", "Base mondiale WDPA ; Eurostat : espaces protégés Natura 2000"),
    ("12_6", "fwb", None, "Aires marines protégées (% de la zone économique exclusive, OCDE)", "planete", "haut", "non", "moyen", "non", "partiel", "Eurostat env_bio4", "Base WDPA"),
    ("12_7", "fwb", None, "Indice Liste rouge des espèces menacées (OCDE)", "planete", "haut", "non", "resultat", "oui", "non", "", "Indice UICN (1 = aucune espèce menacée) ; même indice relayé par OWID (red-list-index) et l'ODD 15.5.1"),
    ("12_8", "fwb", None, "Émissions de gaz à effet de serre par habitant (OCDE)", "planete", "bas", "non", "pression", "non", "oui", "Eurostat env_air_gge", "Inventaire CCNUCC (voir aussi Citepa)"),
    ("12_9", "fwb", "T_CO2E", "Empreinte carbone par habitant (OCDE, t CO2e)", "planete", "bas", "non", "pression", "non", "partiel", "INSEE 010595988", "Méthode OCDE (tableaux entrées-sorties ICIO) ; l'INSEE/SDES publie une empreinte nationale différente"),
    ("12_10", "fwb", None, "Part des énergies renouvelables dans l'approvisionnement énergétique (OCDE)", "planete", "haut", "non", "moyen", "non", "partiel", "Eurostat nrg_ind_ren", "Eurostat : part dans la consommation finale brute (autre dénominateur)"),
    ("12_11", "fwb", None, "Excédent d'azote des sols agricoles (bilan nutritif)", "planete", "bas", "non", "pression", "non", "partiel", "Eurostat aei_pr_gnb", "Même concept, sources voisines"),
    ("12_12", "fwb", None, "Stress hydrique (prélèvements / ressources internes)", "planete", "bas", "non", "pression", "non", "partiel", "Eurostat env_wat_abs", "Eurostat diffuse les prélèvements et l'indice d'exploitation de l'eau"),
    ("12_13", "fwb", None, "Stress hydrique (prélèvements / ressources renouvelables totales)", "planete", "bas", "non", "pression", "non", "partiel", "Eurostat env_wat_abs", ""),
    ("12_14", "fwb", None, "Empreinte matières par habitant (OCDE)", "planete", "bas", "non", "pression", "non", "partiel", "Eurostat env_ac_rme", "INSEE/Eurostat : empreinte matières (RMC), méthode différente"),
    ("12_15", "fwb", None, "Taux de recyclage des déchets municipaux (OCDE)", "planete", "haut", "non", "resultat", "non", "oui", "Eurostat env_wasmun", ""),
    ("13_1", "fwb", None, "Jeunes adultes (25-34 ans) diplômés du second cycle du secondaire au moins", "education", "haut", "non", "resultat", "non", "oui", "Eurostat edat_lfse_03", "LFS"),
    ("13_2", "fwb", None, "Taux de sous-utilisation de la main-d'œuvre", "travail", "bas", "non", "resultat", "non", "partiel", "Eurostat lfsi_sla_a", "Eurostat : capacités excédentaires (définition proche)"),
    ("13_3", "fwb", None, "Mortalité prématurée (années potentielles de vie perdues)", "sante", "bas", "non", "resultat", "non", "partiel", "Eurostat hlth_cd_ptpyll", "Eurostat : années de vie perdues pour causes traitables et évitables (2011-2023)"),
    ("13_4", "fwb", None, "Prévalence du tabagisme quotidien (OCDE)", "sante", "bas", "oui", "resultat", "non", "oui", "INSEE 010593303 + Eurostat sdg_03_30", "INSEE : 2010-2024 (Santé publique France)"),
    ("13_5", "fwb", None, "Prévalence de l'obésité (OCDE)", "sante", "bas", "non", "resultat", "non", "partiel", "INSEE 010754778 + Eurostat hlth_ehis_bm1e", "Sources différentes"),
    ("14_1", "fwb", None, "Confiance dans les autres (0-10)", "securite_confiance", "haut", "oui", "resultat", "non", "partiel", "INSEE DS_SRCV_CONFIANCE + Eurostat ilc_pw03", "INSEE SRCV « confiance envers les autres » 2020-2024"),
    ("14_2", "fwb", None, "Confiance dans la police (0-10)", "democratie", "haut", "oui", "resultat", "non", "partiel", "INSEE 010596051", "Un seul point (2013) ; l'INSEE diffuse la confiance dans la police (CEVIPOF) 2013-2024"),
    ("14_3", "fwb", None, "Confiance dans le gouvernement national", "democratie", "haut", "oui", "resultat", "non", "partiel", "INSEE DS_NAT_SDG?INDICATOR_SDG=16.i4", GALLUP + " ; l'INSEE (ODD 16) diffuse la confiance dans d'autres institutions (CEVIPOF)"),
    ("14_4", "fwb", None, "Participation des parties prenantes à l'élaboration des réglementations (0-4)", "democratie", "haut", "non", "moyen", "oui", "non", "", "Indicateur composite OCDE (iREG)"),
    ("14_5", "fwb", None, "Part des femmes parmi les parlementaires (OCDE)", "egalites", "haut", "non", "resultat", "non", "oui", "Eurostat sdg_05_50", ""),
    ("14_6", "fwb", None, "Indice de perception de la corruption (Transparency International, via OCDE)", "democratie", "haut", "non", "resultat", "oui", "oui", "Eurostat sdg_16_50", "Valeurs du CPI de Transparency International ; relais OWID ti-corruption-perception-index ; le classeur TI CPI2025_Results.xlsx n'est pas lisible par openpyxl"),
    ("14_7", "fwb", None, "Bénévolat dans une association (au cours du mois écoulé)", "liens_bien_etre", "haut", "oui", "resultat", "non", "partiel", "Eurostat ilc_scp20", GALLUP + " ; EU-SILC (2015, 2022) mesure la participation à des activités bénévoles"),
    ("15_1", "fwb", None, "Actifs fixes produits par habitant (USD PPA)", "niveau_de_vie", "haut", "non", "moyen", "non", "partiel", "", "Comptes de patrimoine (INSEE en euros)"),
    ("15_2", "fwb", None, "Actifs de propriété intellectuelle par habitant (USD PPA)", "niveau_de_vie", "haut", "non", "moyen", "non", "partiel", "", "Comptes de patrimoine (INSEE en euros)"),
    ("15_3", "fwb", None, "Croissance de la formation brute de capital fixe", "niveau_de_vie", "haut", "non", "moyen", "non", "partiel", "", "Variation annuelle (%)"),
    ("15_4", "fwb", None, "Dépense intérieure de R-D (% du PIB, OCDE)", "niveau_de_vie", "haut", "non", "moyen", "non", "oui", "", "Même définition (manuel de Frascati) qu'INSEE/Eurostat (identifiant non retrouvé dans les catalogues M01/M02)"),
    ("15_5", "fwb", None, "Valeur financière nette de l'économie par habitant (USD PPA)", "niveau_de_vie", "haut", "non", "resultat", "non", "partiel", "", "Position extérieure nette"),
    ("15_6", "fwb", None, "Dette des ménages (% du revenu disponible net)", "niveau_de_vie", "bas", "non", "pression", "non", "partiel", "", "Voir aussi BCE et Banque de France"),
    ("15_7", "fwb", None, "Valeur financière nette des administrations publiques (% du PIB)", "niveau_de_vie", "haut", "non", "resultat", "non", "partiel", "INSEE 010596873", "INSEE/Eurostat : dette publique brute (concept proche)"),
    ("15_8", "fwb", None, "Levier des institutions financières monétaires", "niveau_de_vie", "ambigu", "non", "pression", "non", "non", "", "Stabilité financière : non retenue par la grille v1 (A16)"),
]
FICHIER_HSL = {"cwb": "ocde__hsl_bien_etre_actuel", "fwb": "ocde__hsl_bien_etre_futur"}
FLUX_HSL = {"cwb": "OECD.WISE.WDP,DSD_HSL@DF_HSL_CWB,1.1", "fwb": "OECD.WISE.WDP,DSD_HSL@DF_HSL_FWB,1.1"}
MESURES_GALLUP = {"7_1", "7_1_DEP", "10_2", "10_2_DEP", "11_2", "11_3", "14_3", "14_7"}
V1_FORCEE = {"15_8": "hors_grille"}
for mesure, flux, unite_motif, lib, dim, sens, decl, typ, comp, doub, ref, com in HSL:
    cond = {"id_debut": f"{mesure}.", "det_motif": "AGE=Total ; SEX=Total ; EDUCATION_LEV=Total"}
    if unite_motif:
        cond["id_motif"] = unite_motif
    s = serie(FICHIER_HSL[flux], **cond)
    ident = f"{FLUX_HSL[flux]} MEASURE={mesure} UNIT_MEASURE={s['serie_id'].split('.')[1]}"
    gallup = mesure in MESURES_GALLUP
    if gallup:
        s = dict(s, preuve=s["preuve"] + " ; " + GALLUP_PREUVE)
    ajouter(lib, dim, "OCDE — How's Life? (base du bien-être)", ident, s["unite_source"], sens, decl, typ, comp,
            doub, com, s, ref_doublon=ref, frequence="irreguliere" if gallup else None,
            points_effectifs=7 if gallup else None, dim_v1=V1_FORCEE.get(mesure))
    if gallup:  # ventilation par sexe (mêmes moyennes triennales) ; l'âge est en moyennes sur 7 ans (2 points)
        for code, nom in (("F", "femmes"), ("M", "hommes")):
            sv = serie(FICHIER_HSL[flux], id_debut=f"{mesure}.", det_motif=f"AGE=Total ; SEX={'Female' if code == 'F' else 'Male'} ;")
            sv = dict(sv, preuve=sv["preuve"] + " ; " + GALLUP_PREUVE)
            ajouter(lib, dim, "OCDE — How's Life? (base du bien-être)", ident + f" SEX={code}", sv["unite_source"], sens,
                    decl, typ, comp, doub, "Ventilation par sexe ; " + GALLUP, sv, ventilation=f"sexe : {nom}",
                    ref_doublon=ref, frequence="irreguliere", points_effectifs=7)

# Satisfaction dans la vie et solitude : ventilations par sexe (EU-SILC relayé par l'OCDE)
for mesure, lib, dim, sens, ref in (("11_1", "Satisfaction dans la vie (0-10, OCDE)", "liens_bien_etre", "haut", "INSEE 010593281 + Eurostat ilc_pw01"),
                                    ("7_4", "Sentiment de solitude", "liens_bien_etre", "bas", "")):
    for code, nom in (("Female", "femmes"), ("Male", "hommes")):
        sv = serie("ocde__hsl_bien_etre_actuel", id_debut=f"{mesure}.", det_motif=f"AGE=Total ; SEX={code} ;")
        ajouter(lib, dim, "OCDE — How's Life? (base du bien-être)", f"{FLUX_HSL['cwb']} MEASURE={mesure} SEX={code[0]}",
                sv["unite_source"], sens, "oui", "resultat", "non", "partiel" if ref else "non",
                "Ventilation par sexe (EU-SILC)", sv, ventilation=f"sexe : {nom}", ref_doublon=ref)

# Inégalités « verticales » (rapports entre haut et bas de la distribution) non encore listées
for mesure, lib in (("11_1_VER", None),):
    pass

# ============================================================================ OCDE — indicateurs ODD (sources ONU relayées)
ODD = "OCDE — indicateurs ODD (base « Measuring distance to the SDG targets »)"
ODD_LIGNES = [
    # fichier, id exact, libellé, dim, sens, décl, type, composite, doublon, ref, commentaire
    ("ocde__odd_3", "3_4_2_OECD._T._T._T._T._T.DT_10P5HB", "Décès par suicide (lésions auto-infligées, pour 100 000 habitants, OCDE)", "sante", "bas", "non", "resultat", "non", "partiel", "INSEE 010599567 + Eurostat hlth_cd_asdr2", "Série longue 2000-2022 ; l'INSEE diffuse le taux standardisé 2011-2023"),
    ("ocde__odd_3", "3_5_2_OECD._T._T._T._T._T.L_PS", "Consommation d'alcool par habitant (litres d'alcool pur)", "sante", "bas", "non", "resultat", "non", "partiel", "Eurostat hlth_ehis_al1e", "Ventes (OCDE/OMS) ; Eurostat : consommation déclarée (EHIS)"),
    ("ocde__odd_3", "3_6_1_OECD._T._T._T._T._T.DT_10P5HB", "Décès dus aux accidents de la route (pour 100 000 habitants, OCDE)", "sante", "bas", "non", "resultat", "non", "partiel", "INSEE 010593288 + Eurostat tran_sf_roadus", "Causes de décès ; série 2000-2022"),
    ("ocde__odd_10", "10_3_1_OECD._T._T._T._T._T.PT_POP_Y_GE15", "Part de la population qui estime que son lieu de résidence est un bon endroit où vivre", "logement_cadre_vie", "haut", "oui", "resultat", "non", "non", "", "Question de sondage (origine Gallup probable, non confirmée : à vérifier dans les métadonnées ODD de l'OCDE)"),
    ("ocde__odd_11", "11_1_1_EN_LND_INDQTHSNG._T._T._T._T._T.PT_POP_URB", "Population urbaine vivant dans un logement inadéquat (ONU-Habitat)", "logement_cadre_vie", "bas", "non", "resultat", "non", "partiel", "Eurostat ilc_lvho05a", "Estimation ONU-Habitat (surpeuplement, qualité) ; valeurs peu variables"),
    ("ocde__odd_11", "11_6_2_OECD._T._T._T._T._T.M3", "Exposition moyenne de la population aux PM2,5 (OCDE)", "logement_cadre_vie", "bas", "non", "resultat", "non", "partiel", "INSEE 010596141", "Modélisation satellitaire ; unité de la source : « Cubic metres » (lire µg/m³)"),
    ("ocde__odd_15", "15_1_2_ER_PTD_TERR._T._T._T._T._T.PT_AR_BIOD_K_TERR", "Part des zones clés de biodiversité terrestres couvertes par des aires protégées", "planete", "haut", "non", "moyen", "non", "non", "", "Indicateur ODD 15.1.2 (UICN, BirdLife)"),
    ("ocde__odd_15", "15_1_2_ER_PTD_FRHWTR._T._T._T._T._T.PT_AR_BIOD_K_WAT_FR", "Part des zones clés de biodiversité d'eau douce couvertes par des aires protégées", "planete", "haut", "non", "moyen", "non", "non", "", "Indicateur ODD 15.1.2"),
    ("ocde__odd_15", "15_4_1_ER_PTD_MTN._T._T._T._T._T.PT_AR_BIOD_K_MTN", "Part des zones clés de biodiversité de montagne couvertes par des aires protégées", "planete", "haut", "non", "moyen", "non", "non", "", "Indicateur ODD 15.4.1"),
    ("ocde__odd_15", "15_1_2_OECD._T._T._T._T._T.PT_LAR", "Aires protégées (% de la surface terrestre, OCDE ODD)", "planete", "haut", "non", "moyen", "non", "partiel", "Eurostat env_bio4", "Même concept que How's Life 12_5"),
    ("ocde__odd_15", "15_5_1_ER_RSK_LST._T._T._T._T._T.IX", "Indice Liste rouge (ODD 15.5.1)", "planete", "haut", "non", "resultat", "oui", "non", "", "Même indice que How's Life 12_7 et OWID red-list-index"),
    ("ocde__odd_16", "16_1_1_OECD._T._T._T._T._T.DT_10P5HB", "Décès par agression (homicides, causes de décès, pour 100 000 habitants)", "securite_confiance", "bas", "non", "resultat", "non", "partiel", "INSEE 010596040 + Eurostat crim_hom_soff", "Même source que How's Life 10_1, série plus longue (2000-2022)"),
    ("ocde__odd_16", "16_1_1_VC_IHR_PSRCN._T._T._T._T._T.PS", "Victimes d'homicide volontaire (nombre, ONUDC)", "securite_confiance", "bas", "non", "resultat", "non", "partiel", "INSEE 010596040 + Eurostat crim_hom_soff", "Nombre (à rapporter à la population)"),
    ("ocde__odd_16", "16_1_3_VC_VOV_PHY_ASLT._T._T._T._T._T.PT_POP", "Victimes d'agression physique au cours des 12 derniers mois (enquête)", "securite_confiance", "bas", "oui", "resultat", "non", "non", "", "Enquête de victimation (CVS puis VRS) relayée par l'ONUDC ; rupture d'enquête en 2022"),
    ("ocde__odd_16", "16_1_3_VC_VOV_ROBB._T._T._T._T._T.PT_POP", "Victimes de vol avec violence au cours des 12 derniers mois (enquête)", "securite_confiance", "bas", "oui", "resultat", "non", "non", "", "Enquête de victimation relayée par l'ONUDC"),
    ("ocde__odd_16", "16_1_3_VC_VOV_SEX_ASLT._T._T._T._T._T.PT_POP", "Victimes d'agression sexuelle au cours des 12 derniers mois (enquête)", "securite_confiance", "bas", "oui", "resultat", "non", "non", "", "Enquête de victimation relayée par l'ONUDC"),
    ("ocde__odd_16", "16_1_3_VC_VOV_PHYL._T._T._T._T._T.PT_POP", "Victimes de violences physiques au cours des 12 derniers mois (enquête)", "securite_confiance", "bas", "oui", "resultat", "non", "non", "", "Enquête de victimation relayée par l'ONUDC"),
    ("ocde__odd_16", "16_3_1_VC_PRR_PHYV._T._T._T._T._T.PT_POP", "Taux de signalement à la police des agressions physiques", "democratie", "ambigu", "oui", "resultat", "non", "non", "", "Accès à la justice (ODD 16.3.1) ; une hausse peut traduire la confiance dans la police ou un changement de comportement"),
    ("ocde__odd_16", "16_3_1_VC_PRR_ROBB._T._T._T._T._T.PT_POP", "Taux de signalement à la police des vols avec violence", "democratie", "ambigu", "oui", "resultat", "non", "non", "", "ODD 16.3.1"),
    ("ocde__odd_16", "16_3_2_VC_PRS_UNSNT._T._T._T._T._T.PT_POP_PRSN", "Détenus non condamnés (part de la population carcérale)", "democratie", "bas", "non", "resultat", "non", "partiel", "", "Détention provisoire ; l'INSEE (ODD 16) diffuse un indicateur de détention provisoire (identifiant à préciser)"),
    ("ocde__odd_5", "5_5_2_IC_GEN_MGTL.Y_GE15.F._T._T._T.PT_W", "Part des femmes parmi les cadres dirigeants (OIT, 13e CIST)", "egalites", "haut", "non", "resultat", "non", "partiel", "", "Estimation OIT sur l'enquête Emploi"),
    ("ocde__odd_5", "5_5_1_SG_GEN_PARLN._T.F._T._T._T.PARL_MEM", "Nombre de sièges détenus par des femmes au Parlement", "egalites", "haut", "non", "resultat", "non", "oui", "Eurostat sdg_05_50", "Nombre (Eurostat : part en %)"),
    ("ocde__odd_5", "5_B_1_OECD._T.F._T._T._T.PT_POP", "Femmes utilisant internet", "education", "haut", "non", "moyen", "non", "oui", "Eurostat isoc_ci_ifp_iu", "Ventilation par sexe de l'usage d'internet"),
]
for fichier, ident, lib, dim, sens, decl, typ, comp, doub, ref, com in ODD_LIGNES:
    s = serie(fichier, id_debut=ident)
    ident = s["serie_id"]
    ajouter(lib, dim, ODD, f"{fichier.split('__')[1]} : {ident}", s["unite_source"], sens, decl, typ, comp, doub, com, s,
            ref_doublon=ref, ventilation="sexe : femmes" if ".F." in ident else "")

# ============================================================================ Banque mondiale — WGI (gouvernance)
WGI = {"VA": ("Voix et responsabilité (expression, association, élections libres)", "democratie"),
       "RL": ("État de droit (respect des contrats, police, justice)", "democratie"),
       "CC": ("Contrôle de la corruption", "democratie"),
       "GE": ("Efficacité de l'action publique", "democratie"),
       "RQ": ("Qualité de la réglementation", "democratie"),
       "PV": ("Stabilité politique et absence de violence", "democratie")}
for code, (lib, dim) in WGI.items():
    for suffixe, unite, note in (("EST", "estimation (-2,5 à +2,5)", "Échelle d'origine des WGI"),
                                 ("SC", "score 0-100", "Même indicateur sur l'échelle 0-100 introduite en 2025 : variante d'échelle")):
        s = serie(f"banque_mondiale__wgi_{code.lower()}_{suffixe.lower()}", id=f"GOV_WGI_{code}.{suffixe}")
        ajouter(f"{lib} — WGI ({unite})", dim, "Banque mondiale — Worldwide Governance Indicators",
                f"api.worldbank.org/v2/country/FRA/indicator/GOV_WGI_{code}.{suffixe}?source=3", unite, "haut", "non",
                "resultat", "oui", "non",
                f"Indice composite agrégeant 30+ sources d'experts et d'enquêtes (D18) ; pas de valeur en 1997, 1999, 2001 ; {note}"
                + (" ; qualité de la réglementation : surtout climat des affaires, lien faible avec la prospérité ressentie" if code == "RQ" else ""),
                s)

# ============================================================================ Our World in Data (relais de V-Dem, Freedom House, etc.)
OWID = "Our World in Data (relais)"
OWID_LIGNES = [
    # slug, colonne (None = FRA), libellé, dim, sens, décl, type, composite, doublon, ref, commentaire
    ("liberal-democracy-index", None, "Indice de démocratie libérale (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem v16 (CC BY-SA 4.0) via OWID ; source primaire par formulaire"),
    ("electoral-democracy-index", None, "Indice de démocratie électorale (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("deliberative-democracy-index-vdem", None, "Indice de démocratie délibérative (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("egalitarian-democracy-index-vdem", None, "Indice de démocratie égalitaire (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("participatory-democracy-index", None, "Indice de démocratie participative (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("freedom-of-expression-index", None, "Liberté d'expression et sources d'information alternatives (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID (série des prototypes)"),
    ("freedom-of-association-index", None, "Liberté d'association (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("academic-freedom-index", None, "Liberté académique (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID (série des prototypes)"),
    ("judicial-constraints-on-the-executive-index", None, "Contraintes judiciaires sur l'exécutif (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID (série des prototypes)"),
    ("legislative-constraints-on-the-executive-index", None, "Contraintes législatives sur l'exécutif (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("rule-of-law-index", None, "État de droit (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("human-rights-index-vdem", None, "Libertés civiles (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("political-civil-liberties-index", None, "Libertés civiles politiques (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("private-civil-liberties-index", None, "Libertés civiles privées (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("individual-liberties-and-equality-before-the-law-index", None, "Libertés individuelles et égalité devant la loi (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("physical-integrity-rights-index-vdem", None, "Droits à l'intégrité physique (absence de torture et d'exécutions politiques, V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("equal-rights-protection-index", None, "Égale protection des droits (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("equality-of-civil-liberties-across-social-groups-score", None, "Égalité des libertés civiles entre groupes sociaux (V-Dem)", "egalites", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID ; score sans borne fixe (modèle de mesure)"),
    ("strong-civil-society-index", None, "Vigueur de la société civile (V-Dem)", "democratie", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("political-polarization-score", None, "Polarisation politique (V-Dem)", "democratie", "bas", "non", "resultat", "non", "non", "", "Évaluation d'experts V-Dem (question unique) ; plus haut = plus polarisé"),
    ("clientelism-index", None, "Clientélisme (V-Dem)", "democratie", "bas", "non", "resultat", "oui", "non", "", "V-Dem via OWID ; plus haut = plus de clientélisme"),
    ("political-corruption-index", None, "Corruption politique (V-Dem)", "democratie", "bas", "non", "resultat", "oui", "non", "", "V-Dem via OWID ; plus haut = plus corrompu ; 6 valeurs distinctes depuis 1900"),
    ("executive-corruption-index", None, "Corruption de l'exécutif (V-Dem)", "democratie", "bas", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("public-sector-corruption-index", None, "Corruption du secteur public (V-Dem)", "democratie", "bas", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("judicial-corruption-score", None, "Absence de corruption judiciaire (V-Dem)", "democratie", "haut", "non", "resultat", "non", "non", "", "Question d'experts V-Dem (plus haut = moins de corruption) ; 2 valeurs distinctes : peu informatif"),
    ("legislative-corruption-score", None, "Absence de corruption législative (V-Dem)", "democratie", "haut", "non", "resultat", "non", "non", "", "Question d'experts V-Dem (plus haut = moins de corruption)"),
    ("media-corruption-score", None, "Absence de corruption des médias (V-Dem)", "democratie", "haut", "non", "resultat", "non", "non", "", "Question d'experts V-Dem ; 4 valeurs distinctes"),
    ("rigorous-and-impartial-public-administration-score", None, "Administration publique rigoureuse et impartiale (V-Dem)", "democratie", "haut", "non", "resultat", "non", "non", "", "Question d'experts V-Dem"),
    ("key-media-freedoms", "FRA#v2mecenefm__estimate_best", "Absence de censure des médias par l'État (V-Dem)", "democratie", "haut", "non", "resultat", "non", "non", "", "Question d'experts V-Dem"),
    ("key-media-freedoms", "FRA#v2meharjrn__estimate_best", "Absence de harcèlement des journalistes (V-Dem)", "democratie", "haut", "non", "resultat", "non", "non", "", "Question d'experts V-Dem"),
    ("key-media-freedoms", "FRA#v2meslfcen__estimate_best", "Absence d'autocensure des médias (V-Dem)", "democratie", "haut", "non", "resultat", "non", "non", "", "Question d'experts V-Dem"),
    ("key-media-freedoms", "FRA#v2mebias__estimate_best", "Pluralisme et absence de biais des médias (V-Dem)", "democratie", "haut", "non", "resultat", "non", "non", "", "Question d'experts V-Dem"),
    ("women-political-empowerment-index", None, "Autonomisation politique des femmes (V-Dem)", "egalites", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("women-civil-liberties-index", None, "Libertés civiles des femmes (V-Dem)", "egalites", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("women-civil-society-participation-index", None, "Participation des femmes à la société civile (V-Dem)", "egalites", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("women-political-participation-index", None, "Participation politique des femmes (V-Dem)", "egalites", "haut", "non", "resultat", "oui", "non", "", "V-Dem via OWID"),
    ("share-of-women-in-parliament", None, "Part des femmes à la chambre basse du Parlement (V-Dem)", "egalites", "haut", "non", "resultat", "non", "oui", "Eurostat sdg_05_50", "V-Dem via OWID"),
    ("freedom-score-fh", None, "Score global de liberté (Freedom House, 0-100)", "democratie", "haut", "non", "resultat", "oui", "non", "", "Freedom in the World via OWID ; 7 valeurs distinctes depuis 2002 (peu de variation)"),
    ("political-rights-score-fh", None, "Droits politiques (Freedom House, 0-40)", "democratie", "haut", "non", "resultat", "oui", "non", "", "Freedom House via OWID ; 2 valeurs distinctes : peu informatif"),
    ("civil-liberties-score-fh", None, "Libertés civiles (Freedom House, 0-60)", "democratie", "haut", "non", "resultat", "oui", "non", "", "Freedom House via OWID"),
    ("ti-corruption-perception-index", None, "Indice de perception de la corruption (Transparency International, via OWID)", "democratie", "haut", "non", "resultat", "oui", "oui", "Eurostat sdg_16_50", "CPI comparable depuis 2012 ; relais OWID (2012-2024) ; source primaire : classeur annuel TI"),
    ("press-freedom-index-rsf", None, "Classement mondial de la liberté de la presse, score (RSF via OWID, ancienne échelle)", "democratie", "bas", "non", "resultat", "oui", "non", "", "Relais arrêté en 2021 (plus bas = mieux) : préférer la source primaire RSF"),
    ("physical-integrity-rights-score-fariss-kenwick-reuning", None, "Protection des droits humains (score latent Fariss et al.)", "democratie", "haut", "non", "resultat", "oui", "non", "", "Série arrêtée en 2019"),
    ("lgbt-rights-index", None, "Indice des droits des personnes LGBT+ (OWID)", "egalites", "haut", "non", "resultat", "oui", "non", "", "Série arrêtée en 2019"),
    ("voter-turnout-of-registered-voters", None, "Participation électorale (% des inscrits, élections nationales, V-Dem/IDEA)", "democratie", "haut", "non", "resultat", "non", "partiel", "INSEE 001778320", "Élections nationales principales seulement ; voir les séries Ministère de l'Intérieur par scrutin"),
    ("voter-turnout-of-voting-age-population", None, "Participation électorale (% de la population en âge de voter, V-Dem/IDEA)", "democratie", "haut", "non", "resultat", "non", "non", "", "Rapporte les votants à toute la population majeure (non-inscrits compris)"),
    ("self-reported-trust-attitudes", None, "Part des personnes estimant qu'on peut faire confiance à la plupart des gens (WVS/EVS)", "securite_confiance", "haut", "oui", "resultat", "non", "partiel", "INSEE DS_SRCV_CONFIANCE", "Enquêtes mondiale et européenne sur les valeurs (vagues 1984, 1993, 2004, 2010, 2022) (D17)"),
    ("share-of-people-who-say-they-are-happy", None, "Part des personnes se déclarant heureuses (WVS/EVS)", "liens_bien_etre", "haut", "oui", "resultat", "non", "non", "", "Vagues 1984, 1993, 2004, 2010, 2022 (D17)"),
    ("share-of-people-who-say-they-are-happy-eurobarometer", None, "Part des personnes se déclarant heureuses (Eurobaromètre)", "liens_bien_etre", "haut", "oui", "resultat", "non", "non", "", "Eurobaromètre standard ; série OWID arrêtée en 2016"),
    ("trust-state-institutions-wvs", "FRA#confidence_justice_system_courts", "Confiance dans la justice (WVS/EVS)", "democratie", "haut", "oui", "resultat", "non", "partiel", "INSEE 010596052", "Vagues des enquêtes sur les valeurs (D17)"),
    ("trust-state-institutions-wvs", "FRA#confidence_police", "Confiance dans la police (WVS/EVS)", "democratie", "haut", "oui", "resultat", "non", "partiel", "INSEE 010596051", "Vagues des enquêtes sur les valeurs (D17)"),
    ("trust-state-institutions-wvs", "FRA#confidence_parliament", "Confiance dans le Parlement (WVS/EVS)", "democratie", "haut", "oui", "resultat", "non", "non", "", "Vagues des enquêtes sur les valeurs (D17)"),
    ("trust-state-institutions-wvs", "FRA#confidence_civil_services", "Confiance dans l'administration (WVS/EVS)", "democratie", "haut", "oui", "resultat", "non", "non", "", "Vagues des enquêtes sur les valeurs (D17)"),
    ("trust-state-institutions-wvs", "FRA#confidence_armed_forces", "Confiance dans l'armée (WVS/EVS)", "democratie", "haut", "oui", "resultat", "non", "partiel", "INSEE 010596050", "Vagues des enquêtes sur les valeurs (D17)"),
    ("gini-coefficient-wid", None, "Indice de Gini des revenus avant impôts (WID)", "egalites", "bas", "non", "resultat", "non", "partiel", "INSEE 010594680", "World Inequality Database via OWID : revenu avant impôts (INSEE/Eurostat : niveau de vie disponible)"),
    ("palma-ratio-wid", None, "Ratio de Palma des revenus avant impôts (WID)", "egalites", "bas", "non", "resultat", "non", "partiel", "", "WID via OWID ; l'INSEE publie un ratio de Palma du niveau de vie (identifiant à préciser)"),
    ("incomes-of-the-richest", None, "Part du revenu avant impôts détenue par les 1 % les plus riches (WID)", "egalites", "bas", "non", "resultat", "non", "non", "", "WID via OWID"),
    ("red-list-index", None, "Indice Liste rouge des espèces menacées (UICN, via OWID)", "planete", "haut", "non", "resultat", "oui", "non", "", "Indicateur ODD 15.5.1 ; série la plus longue (1980-2025) ; aussi How's Life 12_7"),
    ("terrestrial-protected-areas", None, "Aires protégées terrestres (% du territoire, WDPA via OWID)", "planete", "haut", "non", "moyen", "non", "partiel", "Eurostat env_bio4", "ODD 15.1.2"),
    ("marine-protected-areas", None, "Aires marines protégées (% des eaux territoriales, WDPA via OWID)", "planete", "haut", "non", "moyen", "non", "non", "", "ODD 14.5.1"),
    ("forest-area-as-share-of-land-area", None, "Surface forestière (% du territoire, FAO via OWID)", "planete", "haut", "non", "resultat", "non", "non", "", "FAO (évaluation des ressources forestières) ; valeurs annuelles en partie interpolées"),
]
for slug, col, lib, dim, sens, decl, typ, comp, doub, ref, com in OWID_LIGNES:
    s = serie(f"owid__{slug}", id=col or "FRA")
    nom_col = (col or "").split("#")[-1] or s["libelle_source"]
    ajouter(lib, dim, OWID, f"https://ourworldindata.org/grapher/{slug}.csv (colonne {nom_col})", "indice ou % (voir source)",
            sens, decl, typ, comp, doub, com, s, niveau="2", ref_doublon=ref,
            dim_v1="liens_bien_etre" if slug == "self-reported-trust-attitudes" else None)  # confiance interpersonnelle (R4)

CO2 = [("co2_per_capita", "Émissions territoriales de CO2 fossile par habitant (Global Carbon Project via OWID)", "partiel", "Eurostat env_air_gge"),
       ("consumption_co2_per_capita", "Émissions de CO2 fondées sur la consommation par habitant (Global Carbon Project via OWID)", "partiel", "INSEE 010595988"),
       ("trade_co2_share", "Part des émissions de CO2 importées dans la consommation (Global Carbon Project via OWID)", "non", ""),
       ("ghg_excluding_lucf_per_capita", "Émissions de gaz à effet de serre par habitant hors usage des terres (Jones et al. via OWID)", "partiel", "Eurostat env_air_gge"),
       ("energy_per_capita", "Consommation d'énergie primaire par habitant (Energy Institute via OWID)", "partiel", "Eurostat nrg_bal_c")]
for col, lib, doub, ref in CO2:
    s = serie("owid__co2_data_france", id=f"FRA#{col}")
    ajouter(lib, "planete", OWID, f"https://github.com/owid/co2-data (colonne {col})", "t ou kWh par habitant",
            "bas", "non", "pression", "non", doub, "Données co2-data d'OWID (CC BY 4.0)", s, niveau="2", ref_doublon=ref)

# ============================================================================ Sources primaires de gouvernance
s = annees_fichiers(r"rsf__classement_(\d{4})\.txt", r"^\[\d+\] (?:[\d-]+;)?FRA;")
ajouter("Classement mondial de la liberté de la presse, score de la France (RSF)", "democratie",
        "Reporters sans frontières (source primaire)", "https://rsf.org/sites/default/files/import_classement/<année>.csv",
        "score", "ambigu", "non", "resultat", "oui", "non",
        "Indice composite (questionnaire d'experts + exactions) ; trois échelles successives constatées dans les fichiers : "
        "2002-2012 plus bas = mieux, 2013-2021 réexprimé plus haut = mieux, depuis 2022 nouvelle méthode (plus haut = mieux) : "
        "sens à fixer par période, ruptures en 2013 et 2022 ; pas de fichier 2011 (édition 2011-2012 publiée en 2012) ; licence non trouvée",
        s, niveau="2", frequence="annuelle")
for colonne, lib in (("Political Context", "contexte politique"), ("Economic Context", "contexte économique"),
                     ("Legal Context", "cadre légal"), ("Social Context", "contexte social"), ("Safety", "sécurité des journalistes")):
    s = annees_fichiers(r"rsf__classement_(\d{4})\.txt", rf"(?s){colonne}.*\n\[\d+\] FRA;")
    ajouter(f"Liberté de la presse : indicateur « {lib} » (RSF, méthode 2022)", "democratie",
            "Reporters sans frontières (source primaire)", f"https://rsf.org/sites/default/files/import_classement/<année>.csv (colonne {colonne})",
            "score 0-100", "haut", "non", "resultat", "oui", "non", "Sous-score de la méthode 2022 (5 points depuis 2022)", s, niveau="2")

FH_CAT = {"A": "processus électoral", "B": "pluralisme et participation politiques", "C": "fonctionnement du gouvernement",
          "D": "liberté d'expression et de croyance", "E": "droits d'association et d'organisation", "F": "État de droit",
          "G": "autonomie personnelle et droits individuels"}
s_fh = annees_texte("freedom_house__fiw_2013_2024_france", r"\] France \| Europe \| c \| (\d{4}) \|")
for lettre, lib in FH_CAT.items():
    ajouter(f"Freedom in the World : catégorie {lettre} « {lib} » (Freedom House)", "democratie",
            "Freedom House (source primaire)", f"https://freedomhouse.org/sites/default/files/2024-02/All_data_FIW_2013-2024.xlsx (colonne {lettre})",
            "points", "haut", "non", "resultat", "oui", "non",
            "Sous-score d'experts ; années = éditions ; éditions 2025-2026 sur demande seulement (formulaire) ; licence non trouvée",
            s_fh, niveau="2")

WJP_FACTEURS = [("Overall Score", "Indice de l'État de droit, score global (World Justice Project)"),
                ("(?:Constraints on|Limited) Government Powers", "État de droit WJP : limitation des pouvoirs du gouvernement"),
                ("Absence of Corruption", "État de droit WJP : absence de corruption"),
                ("Open Government", "État de droit WJP : gouvernement ouvert"),
                ("Fundamental Rights", "État de droit WJP : droits fondamentaux"),
                ("Order and Security", "État de droit WJP : ordre et sécurité"),
                ("Regulatory Enforcement", "État de droit WJP : application de la réglementation"),
                ("Civil Justice", "État de droit WJP : justice civile"),
                ("Criminal Justice", "État de droit WJP : justice pénale")]
for facteur, lib in WJP_FACTEURS:
    motif = r"Feuille « WJP ROL Index (?:\d{4}-)?(\d{4}) Scores » : colonne \d+ ===\n(?:\[\d+\] [^\n]*\n)*?\[\d+\] [^\n]*" + facteur
    s = annees_texte("wjp__historique_2025_essai_c", motif)
    ajouter(lib, "democratie", "World Justice Project (source primaire)",
            "https://worldjusticeproject.org/rule-of-law-index/downloads/2025_wjp_rule_of_law_index_HISTORICAL_DATA_FILE.xlsx",
            "score 0-1", "haut", "non", "resultat", "oui", "non",
            "Indice composite (enquêtes auprès des ménages et d'experts) ; éditions 2012-2013 et 2017-2018 regroupées (année de fin retenue) ; "
            "scores antérieurs à 2015 non strictement comparables ; licence non trouvée",
            s, niveau="2", frequence="irreguliere")

# ============================================================================ Ministère de l'Intérieur — participation électorale
ELECTIONS = "Ministère de l'Intérieur — résultats électoraux (data.gouv.fr, fichier agrégé au bureau de vote)"
for motif, lib, doub, ref in ((r"\d{4}_pres_t1", "Taux de participation au premier tour de l'élection présidentielle", "oui", "INSEE 001778320"),
                              (r"\d{4}_pres_t2", "Taux de participation au second tour de l'élection présidentielle", "non", ""),
                              (r"\d{4}_legi_t1", "Taux de participation au premier tour des élections législatives", "partiel", ""),
                              (r"\d{4}_euro_t1", "Taux de participation aux élections européennes", "oui", "INSEE 001778185"),
                              (r"\d{4}_regi_t1", "Taux de participation au premier tour des élections régionales", "oui", "INSEE 001777817"),
                              (r"\d{4}_(cant|dpmt)_t1", "Taux de participation au premier tour des élections cantonales puis départementales", "oui", "INSEE 001778052"),
                              (r"\d{4}_muni_t1", "Taux de participation au premier tour des élections municipales", "non", "")):
    s = serie_elections(motif)
    ajouter(lib, "democratie", ELECTIONS,
            "https://data-pipeline-open.s3.sbg.io.cloud.ovh.net/elections/general_results.parquet (somme votants / somme inscrits)",
            "% des inscrits", "haut", "non", "resultat", "non", doub,
            "Calcul du robot (agrégation de tous les bureaux) : à recouper avec les résultats officiels (champ des inscrits "
            "variable selon les années, Français de l'étranger) ; report de la dernière valeur entre deux scrutins (D17)"
            + (" ; série absente du repérage INSEE (M01) ; OCDE How's Life 8_2 la relaie" if "legi" in motif else ""),
            s, niveau="2", geo="FR", ref_doublon=ref)
s = serie_elections(r"20(17|22)_(pres|legi)_t[12]|20(19|24)_euro_t1|2020_muni_t[12]|2021_(regi|dpmt)_t[12]|2024_legi_t[12]|2026_muni_t[12]")
ajouter("Part des votes blancs parmi les votants (scrutins depuis 2017)", "democratie", ELECTIONS,
        "general_results : colonnes blancs, votants", "% des votants", "ambigu", "non", "resultat", "non", "non",
        "Les blancs ne sont comptés à part des nuls que depuis 2014 (colonne nulle avant 2017 dans le fichier) ; signal de défiance ou d'offre politique : sens à discuter",
        s, niveau="2")

# ============================================================================ suite (bien-être, sécurité, planète, santé…)
import candidats_definitions_suite  # noqa: E402,F401
