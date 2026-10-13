"""Définition des indicateurs candidats hors INSEE/Eurostat (mission M04, T3).

Chaque appel à `ajouter()` décrit un indicateur et le rattache à une série repérée par le robot
(`serie(...)`), dont les années sont lues automatiquement. Voir construire_candidats.py.

Conventions :
- sens : haut (plus c'est élevé, mieux c'est) | bas | ambigu ;
- declaratif : oui pour une donnée d'enquête d'opinion, de perception ou de ressenti (y compris
  auto-évaluation de la santé ou des difficultés financières) ; non pour une mesure administrative,
  une estimation statistique ou une évaluation d'experts ;
- composite : oui pour un indice agrégeant plusieurs sous-indicateurs ou sources (D18) ;
- doublon_insee_eurostat : oui (même définition chez l'INSEE ou Eurostat), partiel (concept proche,
  définition, source ou champ différents), non. Références : docs/sources/insee_indicateurs_reperes.csv
  (branche m01-insee) et jeux Eurostat des dossiers SDG, Quality of life, EU-SILC, LFS, Health, Education.
"""

from construire_candidats import ajouter, annees_texte, serie, serie_banque_mondiale_phase1

# ============================================================================ OCDE — How's Life
GALLUP = ("Valeurs triennales répétées chaque année (moyennes sur 3 ans) ; origine Gallup World Poll "
          "probable, à confirmer dans les métadonnées OCDE : fréquence effective triennale.")
HSL = [
    # mesure, fichier, motif d'unité, libellé, dimension, sens, déclaratif, type, composite, doublon, commentaire
    ("1_1", "cwb", None, "Revenu disponible net ajusté des ménages par habitant (USD PPA)", "niveau_de_vie", "haut", "non", "resultat", "non", "partiel", "Comptes nationaux en USD PPA ; INSEE publie le RDB ajusté en euros."),
    ("1_2", "cwb", None, "Rapport des revenus disponibles moyens du quintile supérieur et du quintile inférieur", "egalites", "bas", "non", "resultat", "non", "oui", "Équivalent du S80/S20 (Eurostat ilc_di11, INSEE)."),
    ("1_3", "cwb", None, "Patrimoine net médian des ménages (USD PPA)", "niveau_de_vie", "haut", "non", "resultat", "non", "partiel", "Base OCDE de la distribution du patrimoine ; INSEE enquête Patrimoine (euros)."),
    ("1_3_VER", "cwb", None, "Part du patrimoine détenue par les 10 % de ménages les plus riches", "egalites", "bas", "non", "resultat", "non", "partiel", "INSEE publie un Gini du patrimoine (ODD 10.i3), pas cette part."),
    ("1_4", "cwb", None, "Taux de pauvreté monétaire relative (OCDE)", "niveau_de_vie", "bas", "non", "resultat", "non", "partiel", "Définition OCDE (seuil à 50 % du revenu médian) ; INSEE/Eurostat au seuil de 60 %."),
    ("1_5", "cwb", None, "Difficulté à joindre les deux bouts", "niveau_de_vie", "bas", "oui", "resultat", "non", "oui", "Question EU-SILC (Eurostat ilc_mdes09)."),
    ("1_6", "cwb", None, "Pauvreté en actifs liquides (épargne liquide inférieure à 3 mois du seuil de pauvreté)", "securite_confiance", "bas", "non", "resultat", "non", "non", "Sécurité économique (épargne de précaution) ; enquêtes patrimoine (HFCS)."),
    ("2_1", "cwb", None, "Taux d'emploi des 25-64 ans", "travail", "haut", "non", "resultat", "non", "oui", "Enquête Forces de travail (Eurostat LFS)."),
    ("2_2", "cwb", None, "Écart de salaire médian entre femmes et hommes", "egalites", "bas", "non", "resultat", "non", "partiel", "Écart des salaires médians à temps plein ; Eurostat/INSEE publient l'écart des salaires horaires moyens."),
    ("2_3", "cwb", None, "Taux de chômage de longue durée", "travail", "bas", "non", "resultat", "non", "oui", "LFS."),
    ("2_4", "cwb", None, "Jeunes de 15-24 ans ni en emploi ni en formation (NEET)", "travail", "bas", "non", "resultat", "non", "oui", "LFS (Eurostat publie aussi les 15-29 ans)."),
    ("2_5", "cwb", None, "Insécurité sur le marché du travail (perte de revenu attendue en cas de chômage)", "travail", "bas", "non", "resultat", "non", "non", "Indicateur OCDE de qualité de l'emploi ; série arrêtée en 2016."),
    ("2_6", "cwb", None, "Tension au travail (job strain)", "travail", "bas", "oui", "resultat", "oui", "partiel", "Indice OCDE construit sur l'enquête européenne sur les conditions de travail (Eurofound) ; 3 points."),
    ("2_7", "cwb", None, "Salariés travaillant au moins 50 heures par semaine", "travail", "bas", "non", "resultat", "non", "partiel", "LFS ; Eurostat diffuse les longues durées avec d'autres seuils."),
    ("2_8", "cwb", None, "Salaire brut annuel moyen (USD PPA)", "niveau_de_vie", "haut", "non", "resultat", "non", "partiel", "INSEE publie le salaire moyen en euros."),
    ("2_8_DEP", "cwb", None, "Salariés à temps plein gagnant moins des deux tiers du salaire médian", "travail", "bas", "non", "resultat", "non", "partiel", "Eurostat publie la part des bas salaires (enquête sur la structure des salaires, quadriennale)."),
    ("2_8_VER", "cwb", None, "Rapport interdécile D9/D1 des salaires à temps plein", "egalites", "bas", "non", "resultat", "non", "partiel", "INSEE publie le D9/D1 des salaires (sources DSN)."),
    ("2_9", "cwb", None, "Satisfaction au travail (0-10)", "travail", "haut", "oui", "resultat", "non", "oui", "Module bien-être EU-SILC (Eurostat ilc_pw01)."),
    ("3_1", "cwb", None, "Ménages vivant dans un logement surpeuplé", "logement_cadre_vie", "bas", "non", "resultat", "non", "oui", "EU-SILC (Eurostat ilc_lvho05a)."),
    ("3_2", "cwb", None, "Accessibilité financière du logement (part du revenu restant après dépenses de logement)", "logement_cadre_vie", "haut", "non", "resultat", "non", "partiel", "Comptes nationaux ; INSEE publie le taux d'effort."),
    ("3_3", "cwb", None, "Surcharge des coûts du logement (plus de 40 % du revenu)", "logement_cadre_vie", "bas", "non", "resultat", "non", "oui", "EU-SILC (Eurostat ilc_lvho07a)."),
    ("3_4", "cwb", None, "Ménages disposant d'un accès internet à domicile", "education", "haut", "non", "moyen", "non", "oui", "Enquête TIC (Eurostat isoc, INSEE) ; série OCDE arrêtée en 2021."),
    ("3_5", "cwb", None, "Incapacité à maintenir le logement à bonne température", "logement_cadre_vie", "bas", "oui", "resultat", "non", "oui", "EU-SILC (INSEE ODD 7.i1, Eurostat ilc_mdes01) ; auto-évaluation."),
    ("4_1", "cwb", None, "Temps consacré aux loisirs et aux soins personnels (heures par jour)", "liens_bien_etre", "haut", "non", "resultat", "non", "partiel", "Enquête Emploi du temps 2009-2010 : un seul point."),
    ("4_2", "cwb", None, "Personnes effectuant de longues heures de travail non rémunéré", "egalites", "bas", "non", "resultat", "non", "partiel", "Enquête Emploi du temps : un seul point."),
    ("4_3", "cwb", None, "Écart femmes-hommes de temps de travail total (minutes par jour)", "egalites", "bas", "non", "resultat", "non", "partiel", "Enquête Emploi du temps : un seul point."),
    ("4_4", "cwb", None, "Satisfaction à l'égard de l'emploi du temps (0-10)", "liens_bien_etre", "haut", "oui", "resultat", "non", "oui", "Module bien-être EU-SILC."),
    ("4_4_DEP", "cwb", None, "Part des personnes peu satisfaites de leur emploi du temps (note < 5)", "liens_bien_etre", "bas", "oui", "resultat", "non", "partiel", "Calcul OCDE sur EU-SILC."),
    ("4_4_VER", "cwb", None, "Inégalité de satisfaction à l'égard de l'emploi du temps (rapport des quintiles)", "egalites", "bas", "oui", "resultat", "non", "non", "Calcul OCDE sur EU-SILC."),
    ("5_1", "cwb", None, "Espérance de vie à la naissance", "sante", "haut", "non", "resultat", "non", "oui", "INSEE/Eurostat."),
    ("5_2", "cwb", None, "Santé perçue comme bonne ou très bonne", "sante", "haut", "oui", "resultat", "non", "oui", "EU-SILC (Eurostat hlth_silc_01)."),
    ("5_2_DEP", "cwb", None, "Santé perçue comme mauvaise ou très mauvaise", "sante", "bas", "oui", "resultat", "non", "oui", "EU-SILC."),
    ("5_3", "cwb", None, "Décès par suicide, alcool ou drogue (« morts de désespoir »)", "sante", "bas", "non", "resultat", "non", "partiel", "Agrégat OCDE de causes de décès (Eurostat diffuse chaque cause séparément)."),
    ("5_4", "cwb", None, "Dépression déclarée", "sante", "bas", "oui", "resultat", "non", "oui", "Enquête EHIS (Eurostat hlth_ehis_cd1e) ; 2 points."),
    ("6_1", "cwb", None, "Score moyen des élèves de 15 ans en compréhension de l'écrit (PISA)", "education", "haut", "non", "resultat", "non", "partiel", "Eurostat diffuse la part d'élèves en difficulté, pas le score moyen ; enquête triennale."),
    ("6_1_DEP", "cwb", None, "Élèves de 15 ans en difficulté dans les trois domaines PISA", "education", "bas", "non", "resultat", "non", "partiel", "Eurostat diffuse la part d'élèves en difficulté par domaine (sdg_04_40)."),
    ("6_1_VER", "cwb", None, "Écart de scores PISA en compréhension de l'écrit (rapport D9/D1)", "egalites", "bas", "non", "resultat", "non", "non", ""),
    ("6_2", "cwb", None, "Score moyen des élèves de 15 ans en mathématiques (PISA)", "education", "haut", "non", "resultat", "non", "partiel", ""),
    ("6_2_VER", "cwb", None, "Écart de scores PISA en mathématiques (rapport D9/D1)", "egalites", "bas", "non", "resultat", "non", "non", ""),
    ("6_3", "cwb", None, "Score moyen des élèves de 15 ans en sciences (PISA)", "education", "haut", "non", "resultat", "non", "partiel", ""),
    ("6_3_VER", "cwb", None, "Écart de scores PISA en sciences (rapport D9/D1)", "egalites", "bas", "non", "resultat", "non", "non", ""),
    ("6_4", "cwb", None, "Compétences des adultes en calcul (PIAAC)", "education", "haut", "non", "resultat", "non", "non", "Deux cycles (2012, 2023)."),
    ("6_4_DEP", "cwb", None, "Adultes ayant de faibles compétences en calcul (PIAAC)", "education", "bas", "non", "resultat", "non", "non", "Deux cycles."),
    ("6_4_VER", "cwb", None, "Écart de compétences des adultes en calcul (rapport D9/D1)", "egalites", "bas", "non", "resultat", "non", "non", "Un seul cycle."),
    ("6_5", "cwb", None, "Compétences des adultes en littératie (PIAAC)", "education", "haut", "non", "resultat", "non", "non", "Deux cycles."),
    ("6_5_VER", "cwb", None, "Écart de compétences des adultes en littératie (rapport D9/D1)", "egalites", "bas", "non", "resultat", "non", "non", "Un seul cycle."),
    ("7_1", "cwb", None, "Soutien social (avoir quelqu'un sur qui compter)", "liens_bien_etre", "haut", "oui", "resultat", "non", "partiel", GALLUP + " Eurostat (EU-SILC) mesure un concept proche (ilc_scp15) sur peu d'années."),
    ("7_1_DEP", "cwb", None, "Absence de soutien social", "liens_bien_etre", "bas", "oui", "resultat", "non", "partiel", GALLUP),
    ("7_2", "cwb", None, "Temps consacré aux interactions sociales (heures par semaine)", "liens_bien_etre", "haut", "non", "resultat", "non", "partiel", "Enquête Emploi du temps : un seul point."),
    ("7_3", "cwb", None, "Satisfaction à l'égard des relations personnelles (0-10)", "liens_bien_etre", "haut", "oui", "resultat", "non", "oui", "Module bien-être EU-SILC (Eurostat ilc_pw01)."),
    ("7_3_DEP", "cwb", None, "Part des personnes peu satisfaites de leurs relations personnelles (note < 5)", "liens_bien_etre", "bas", "oui", "resultat", "non", "partiel", ""),
    ("7_3_VER", "cwb", None, "Inégalité de satisfaction à l'égard des relations personnelles (rapport des quintiles)", "egalites", "bas", "oui", "resultat", "non", "non", ""),
    ("7_4", "cwb", None, "Sentiment de solitude", "liens_bien_etre", "bas", "oui", "resultat", "non", "partiel", "EU-SILC (modules 2018, 2022)."),
    ("8_1", "cwb", None, "Avoir son mot à dire sur l'action des pouvoirs publics", "democratie", "haut", "oui", "resultat", "non", "non", "Enquête OCDE sur la confiance (2021, 2023)."),
    ("8_1_DEP", "cwb", None, "Ne pas avoir son mot à dire sur l'action des pouvoirs publics", "democratie", "bas", "oui", "resultat", "non", "non", "Enquête OCDE sur la confiance."),
    ("8_2", "cwb", None, "Participation électorale aux élections législatives (OCDE)", "democratie", "haut", "non", "resultat", "non", "oui", "INSEE diffuse la participation aux législatives ; voir aussi les lignes Ministère de l'Intérieur."),
    ("9_1", "cwb", None, "Population urbaine ayant accès à des espaces verts", "logement_cadre_vie", "haut", "non", "resultat", "non", "non", "Estimation géospatiale OCDE ; 2 points."),
    ("9_2", "cwb", None, "Population exposée à plus de 10 µg/m³ de PM2,5", "logement_cadre_vie", "bas", "non", "resultat", "non", "partiel", "Eurostat diffuse l'exposition moyenne (sdg_11_50) ; série OCDE arrêtée en 2020."),
    ("9_3", "cwb", None, "Population exposée à des températures extrêmes", "logement_cadre_vie", "bas", "non", "resultat", "non", "non", "Estimation géospatiale OCDE."),
    ("10_1", "cwb", None, "Taux d'homicides (OCDE, causes de décès)", "securite_confiance", "bas", "non", "resultat", "non", "partiel", "Source causes de décès (OMS) ; INSEE diffuse le nombre d'homicides enregistrés (SSMSI)."),
    ("10_2", "cwb", None, "Sentiment de sécurité en marchant seul la nuit", "securite_confiance", "haut", "oui", "resultat", "non", "partiel", GALLUP + " INSEE/SSMSI : sentiment d'insécurité (enquêtes CVS/VRS), question différente."),
    ("10_2_DEP", "cwb", None, "Sentiment d'insécurité en marchant seul la nuit", "securite_confiance", "bas", "oui", "resultat", "non", "partiel", GALLUP),
    ("10_3", "cwb", None, "Mortalité routière (pour 100 000 habitants)", "sante", "bas", "non", "resultat", "non", "oui", "INSEE ODD 3.i6 (nombre de tués)."),
    ("11_1", "cwb", None, "Satisfaction dans la vie (0-10, OCDE)", "liens_bien_etre", "haut", "oui", "resultat", "non", "oui", "EU-SILC et enquêtes nationales ; l'INSEE diffuse une série annuelle 2010-2024 (SRCV)."),
    ("11_1_DEP", "cwb", None, "Part des personnes peu satisfaites de leur vie (note < 5)", "liens_bien_etre", "bas", "oui", "resultat", "non", "partiel", "INSEE diffuse la satisfaction « faible (0-5) » en ventilation."),
    ("11_1_VER", "cwb", None, "Inégalité de satisfaction dans la vie (rapport des quintiles supérieur et inférieur)", "egalites", "bas", "oui", "resultat", "non", "non", ""),
    ("11_2", "cwb", None, "Bilan émotionnel négatif (plus d'émotions négatives que positives la veille)", "liens_bien_etre", "bas", "oui", "resultat", "non", "non", GALLUP),
    ("11_3", "cwb", None, "Douleur physique ressentie la veille", "sante", "bas", "oui", "resultat", "non", "non", GALLUP),
    ("12_1", "fwb", None, "Part des terres en couverture naturelle ou semi-naturelle", "planete", "haut", "non", "resultat", "non", "partiel", "Télédétection ; INSEE diffuse l'artificialisation des sols (autre source)."),
    ("12_2", "fwb", None, "Perte de couverture naturelle et semi-naturelle", "planete", "bas", "non", "pression", "non", "non", "5 points."),
    ("12_3", "fwb", None, "Gain de couverture naturelle et semi-naturelle", "planete", "haut", "non", "resultat", "non", "non", "5 points."),
    ("12_4", "fwb", None, "Paysages forestiers intacts", "planete", "haut", "non", "resultat", "non", "non", "Valeur nulle pour la France : sans intérêt."),
    ("12_5", "fwb", None, "Aires protégées terrestres (% du territoire)", "planete", "haut", "non", "moyen", "non", "partiel", "Base WDPA ; INSEE diffuse les aires protégées (définition nationale, protection forte)."),
    ("12_6", "fwb", None, "Aires marines protégées (% de la zone économique exclusive)", "planete", "haut", "non", "moyen", "non", "partiel", "Base WDPA."),
    ("12_7", "fwb", None, "Indice Liste rouge des espèces menacées", "planete", "haut", "non", "resultat", "oui", "non", "Indice UICN (1 = aucune espèce menacée) ; aussi OWID red-list-index (1980-2025) et ODD OCDE 15.5.1."),
    ("12_8", "fwb", None, "Émissions de gaz à effet de serre par habitant (OCDE)", "planete", "bas", "non", "pression", "non", "oui", "Inventaire CCNUCC (INSEE/Eurostat, voir aussi Citepa)."),
    ("12_9", "fwb", "T_CO2E", "Empreinte carbone par habitant (OCDE, t CO2e)", "planete", "bas", "non", "pression", "non", "partiel", "Méthode OCDE (tableaux entrées-sorties ICIO) ; l'INSEE/SDES publie une empreinte nationale différente ; série arrêtée en 2020."),
    ("12_10", "fwb", None, "Part des énergies renouvelables dans l'approvisionnement énergétique", "planete", "haut", "non", "moyen", "non", "partiel", "Eurostat diffuse la part dans la consommation finale brute (autre dénominateur)."),
    ("12_11", "fwb", None, "Excédent d'azote des sols agricoles (bilan nutritif)", "planete", "bas", "non", "pression", "non", "partiel", "Eurostat aei_pr_gnb (même concept, sources voisines)."),
    ("12_12", "fwb", None, "Stress hydrique (prélèvements / ressources internes)", "planete", "bas", "non", "pression", "non", "partiel", "Eurostat diffuse l'indice d'exploitation de l'eau (WEI+)."),
    ("12_13", "fwb", None, "Stress hydrique (prélèvements / ressources renouvelables totales)", "planete", "bas", "non", "pression", "non", "partiel", ""),
    ("12_14", "fwb", None, "Empreinte matières par habitant (OCDE)", "planete", "bas", "non", "pression", "non", "partiel", "INSEE diffuse l'empreinte matières (RMC) 2010-2022, méthode différente."),
    ("12_15", "fwb", None, "Taux de recyclage des déchets municipaux (OCDE)", "planete", "haut", "non", "resultat", "non", "oui", "INSEE/Eurostat (taux de recyclage des déchets municipaux)."),
    ("13_1", "fwb", None, "Jeunes adultes (25-34 ans) diplômés du second cycle du secondaire au moins", "education", "haut", "non", "resultat", "non", "oui", "LFS."),
    ("13_2", "fwb", None, "Taux de sous-utilisation de la main-d'œuvre", "travail", "bas", "non", "resultat", "non", "partiel", "Eurostat diffuse le « labour market slack » (définition proche)."),
    ("13_3", "fwb", None, "Mortalité prématurée (années potentielles de vie perdues)", "sante", "bas", "non", "resultat", "non", "partiel", "Eurostat/INSEE diffusent des taux de mortalité prématurée (autre définition)."),
    ("13_4", "fwb", None, "Prévalence du tabagisme quotidien (OCDE)", "sante", "bas", "oui", "resultat", "non", "oui", "INSEE diffuse la prévalence du tabagisme quotidien (2010-2024, Santé publique France)."),
    ("13_5", "fwb", None, "Prévalence de l'obésité (OCDE)", "sante", "bas", "non", "resultat", "non", "partiel", "INSEE diffuse des prévalences d'obésité (sources différentes)."),
    ("14_1", "fwb", None, "Confiance dans les autres (0-10)", "securite_confiance", "haut", "oui", "resultat", "non", "partiel", "EU-SILC/enquêtes nationales ; INSEE SRCV « confiance envers les autres » 2020-2024."),
    ("14_2", "fwb", None, "Confiance dans la police (0-10)", "securite_confiance", "haut", "oui", "resultat", "non", "partiel", "Un seul point (2013) ; INSEE diffuse la confiance dans la police (CEVIPOF) 2013-2024."),
    ("14_3", "fwb", None, "Confiance dans le gouvernement national", "democratie", "haut", "oui", "resultat", "non", "partiel", GALLUP + " INSEE (ODD 16.i4) : confiance dans d'autres institutions (CEVIPOF)."),
    ("14_4", "fwb", None, "Participation des parties prenantes à l'élaboration des réglementations (0-4)", "democratie", "haut", "non", "moyen", "oui", "non", "Indicateur composite OCDE (iREG) ; 4 points."),
    ("14_5", "fwb", None, "Part des femmes parmi les parlementaires (OCDE)", "egalites", "haut", "non", "resultat", "non", "oui", "Eurostat sdg_05_50 ; INSEE (ODD 5)."),
    ("14_6", "fwb", None, "Indice de perception de la corruption (Transparency International, via OCDE)", "democratie", "haut", "non", "resultat", "oui", "oui", "Valeurs identiques au CPI (Eurostat sdg_16_50 le diffuse) ; relais OWID ti-corruption-perception-index (2012-2024) ; le classeur TI CPI2025_Results.xlsx n'est pas lisible par openpyxl."),
    ("14_7", "fwb", None, "Bénévolat dans une association", "liens_bien_etre", "haut", "oui", "resultat", "non", "partiel", GALLUP + " Eurostat (EU-SILC 2015, 2022) mesure la participation à des activités bénévoles."),
    ("15_1", "fwb", None, "Actifs fixes produits par habitant (USD PPA)", "niveau_de_vie", "haut", "non", "moyen", "non", "partiel", "Comptes de patrimoine (INSEE en euros)."),
    ("15_2", "fwb", None, "Actifs de propriété intellectuelle par habitant (USD PPA)", "niveau_de_vie", "haut", "non", "moyen", "non", "partiel", ""),
    ("15_3", "fwb", None, "Croissance de la formation brute de capital fixe", "niveau_de_vie", "haut", "non", "moyen", "non", "partiel", "Variation annuelle (%)."),
    ("15_4", "fwb", None, "Dépense intérieure de R-D (% du PIB)", "niveau_de_vie", "haut", "non", "moyen", "non", "oui", "Eurostat/INSEE (même définition, manuel de Frascati)."),
    ("15_5", "fwb", None, "Valeur financière nette de l'économie par habitant (USD PPA)", "niveau_de_vie", "haut", "non", "resultat", "non", "partiel", "Position extérieure nette."),
    ("15_6", "fwb", None, "Dette des ménages (% du revenu disponible net)", "niveau_de_vie", "bas", "non", "pression", "non", "partiel", "Voir aussi BCE (ligne dédiée) et Banque de France."),
    ("15_7", "fwb", None, "Valeur financière nette des administrations publiques (% du PIB)", "niveau_de_vie", "haut", "non", "resultat", "non", "partiel", "Eurostat diffuse la dette publique brute (concept proche)."),
    ("15_8", "fwb", None, "Levier des institutions financières monétaires", "niveau_de_vie", "ambigu", "non", "pression", "non", "non", "Indicateur de risque financier, interprétation délicate."),
]
FICHIER_HSL = {"cwb": "ocde__hsl_bien_etre_actuel", "fwb": "ocde__hsl_bien_etre_futur"}
FLUX_HSL = {"cwb": "OECD.WISE.WDP,DSD_HSL@DF_HSL_CWB,1.1", "fwb": "OECD.WISE.WDP,DSD_HSL@DF_HSL_FWB,1.1"}
for mesure, flux, unite_motif, lib, dim, sens, decl, typ, comp, doub, com in HSL:
    cond = {"id_debut": f"{mesure}.", "det_motif": "AGE=Total ; SEX=Total ; EDUCATION_LEV=Total"}
    if unite_motif:
        cond["id_motif"] = unite_motif
    s = serie(FICHIER_HSL[flux], **cond)
    unite = s["unite_source"] if s else "non trouvé"
    ident = f"{FLUX_HSL[flux]} MEASURE={mesure}" + (f" UNIT_MEASURE={s['serie_id'].split('.')[1]}" if s else "")
    ajouter(lib, dim, "OCDE — How's Life? (base du bien-être)", ident, unite, sens, decl, typ, comp, doub, com, s)
