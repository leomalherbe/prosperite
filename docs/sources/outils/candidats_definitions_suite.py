"""Suite des définitions des indicateurs candidats (mission M04, T3) : bien-être ressenti (DREES, WHR),
sécurité (SSMSI, ITDD), planète (Citepa, EDGAR, FoDaFo, SDES, ITDD, PNUD), santé, éducation, travail
(Santé publique France, DEPP, Assurance maladie) et Banque mondiale (WDI). Mêmes conventions que
candidats_definitions.py, qui importe ce module à la fin."""

from candidats_definitions import edgar_annees, serie_drees
from construire_candidats import ajouter, annees_texte, serie, serie_banque_mondiale_phase1

# ============================================================================ DREES — baromètre d'opinion (microdonnées 2000-2025)
DREES = "DREES — Baromètre d'opinion (microdonnées pondérées, data.drees)"
URL_DREES = "data.drees.solidarites-sante.gouv.fr, jeu 431_le-barometre-d-opinion, pièces jointes barometre2000_2024_diff_csv et barometre2025_diff_csv"
NOTE_DREES = ("Part pondérée calculée par le robot sur les microdonnées (poids de redressement fournis), NSP inclus au dénominateur ; "
              "codes de modalités lus dans le dictionnaire 2025 (stabilité sur toute la période à vérifier) ; pas d'enquête en 2003 ; "
              "champ géographique (métropole ou France entière) à confirmer dans la documentation DREES ; Licence Ouverte (à confirmer)")
DREES_LIGNES = [
    # variable, modalités, libellé, dim v0, sens, type, doublon, ref, commentaire
    ("og01", ["1", "2"], "Part des personnes jugeant leur situation personnelle actuelle bonne (très ou assez)", "liens_bien_etre", "haut", "resultat", "non", "",
     "Évaluation globale de sa situation (proche d'une satisfaction de vie, question différente de la note 0-10) ; série 2002-2025 sans équivalent INSEE/Eurostat"),
    ("og01", ["3", "4"], "Part des personnes jugeant leur situation personnelle actuelle mauvaise (assez ou très)", "liens_bien_etre", "bas", "resultat", "non", "",
     "Complément de la ligne précédente (variante « privation »)"),
    ("og03_1", ["1", "2"], "Part des personnes optimistes pour leur propre avenir", "liens_bien_etre", "haut", "resultat", "non", "",
     "Perspective d'avenir (dimension « sens et projection » du bien-être) ; 2000-2025"),
    ("og03_2", ["1", "2"], "Part des personnes optimistes pour l'avenir de leurs enfants et des générations futures", "liens_bien_etre", "haut", "resultat", "non", "",
     "Optimisme collectif ; 2000-2025"),
    ("cs05", ["1", "2"], "Part des personnes se sentant intégrées dans la société (très ou assez bien)", "liens_bien_etre", "haut", "resultat", "non", "",
     "Lien social et sentiment d'appartenance ; 2014-2025"),
    ("cs05", ["3", "4"], "Part des personnes ne se sentant pas intégrées dans la société", "liens_bien_etre", "bas", "resultat", "non", "",
     "Isolement social ressenti (variante « privation ») ; 2014-2025"),
    ("cs01", ["1", "2"], "Part des personnes jugeant la cohésion sociale forte (très ou assez)", "liens_bien_etre", "haut", "resultat", "non", "",
     "Perception de la cohésion de la société ; 2014-2025"),
    ("de07", ["1"], "Part des personnes apportant une aide régulière et bénévole à une personne âgée dépendante", "liens_bien_etre", "ambigu", "resultat", "non", "",
     "Aidance : solidarité de proximité mais aussi charge ; sens à discuter"),
    ("pe03", ["3"], "Part des personnes se considérant comme pauvres (pauvreté ressentie)", "niveau_de_vie", "bas", "resultat", "non", "",
     "Pauvreté subjective ; 2014-2025 (pas de 2024)"),
    ("pe03", ["1"], "Part des personnes estimant risquer de devenir pauvres dans les cinq ans", "securite_confiance", "bas", "resultat", "non", "",
     "Insécurité économique ressentie ; 2014-2025 (pas de 2024)"),
    ("og04_4", ["1", "2"], "Part des personnes préoccupées (beaucoup ou assez) par l'insécurité dans leur quartier ou village", "securite_confiance", "bas", "resultat", "partiel", "",
     "Proche du sentiment d'insécurité des enquêtes de victimation (SSMSI) ; 2014-2025"),
    ("in01", ["1"], "Part des personnes jugeant la société française plutôt juste", "egalites", "haut", "resultat", "non", "",
     "Perception de la justice sociale ; 2000-2025"),
    ("in02", ["1"], "Part des personnes estimant que les inégalités ont augmenté depuis cinq ans", "egalites", "bas", "resultat", "non", "",
     "Perception de l'évolution des inégalités ; 2000-2025"),
    ("cs09", ["1"], "Part des personnes témoins de discriminations envers les femmes au cours des 12 derniers mois", "egalites", "bas", "resultat", "non", "",
     "2014, 2016-2023, 2025"),
    ("sa01_ab", ["1", "2"], "Santé perçue comme bonne ou très bonne (baromètre DREES)", "sante", "haut", "resultat", "partiel", "Eurostat hlth_silc_01",
     "Échelle de réponse modifiée en 2004 et en 2007 (5 modalités depuis 2007) : série homogène 2007-2025 seulement ; préférer EU-SILC"),
    ("sa03", ["1"], "Part des personnes limitées depuis au moins 6 mois dans leurs activités par un problème de santé", "sante", "bas", "resultat", "partiel", "Eurostat hlth_silc_01",
     "Équivalent de l'indicateur GALI (EU-SILC) ; 2007-2025 sans 2016"),
    ("sa09_1", ["3"], "Part des personnes estimant manquer de médecins généralistes à proximité", "sante", "bas", "resultat", "non", "",
     "Accès aux soins ressenti ; 2002 puis 2015, 2017-2025"),
]
for var, modalites, lib, dim, sens, typ, doub, ref, com in DREES_LIGNES:
    s = serie_drees(var, modalites)
    ajouter(lib, dim, DREES, f"{URL_DREES} ; variable {var.upper()}, modalités {'+'.join(modalites)}", "% des répondants",
            sens, "oui", typ, "non", doub, f"{com} ; {NOTE_DREES}", s, niveau="2", ref_doublon=ref)

# ============================================================================ World Happiness Report (Gallup)
s = annees_texte("whr__whr26_figure_2_1_france", r"\] (\d{4})\.0 \| \d+\.0 \| France \|")
ajouter("Évaluation de la vie (échelle de Cantril 0-10, moyenne sur 3 ans, World Happiness Report)", "liens_bien_etre",
        "World Happiness Report (données Gallup World Poll)", "https://files.worldhappiness.report/WHR26_Data_Figure_2.1.xlsx (colonne « Life evaluation (3-year average) »)",
        "note 0-10", "haut", "oui", "resultat", "non", "partiel",
        "Question unique (pas un indice composite, bien que D18 cite le WHR) ; moyennes glissantes sur 3 ans (l'année N couvre N-2 à N, selon les métadonnées OWID) ; "
        "pas de valeur 2013 ; données Gallup diffusées « gratuitement » pour la figure 2.1, sans licence explicite (non trouvée) ; nom de fichier nouveau à chaque édition ; "
        "relais OWID happiness-cantril-ladder",
        s, niveau="2", ref_doublon="INSEE 010593281 + Eurostat ilc_pw01")

# ============================================================================ SSMSI — base des séries chronologiques
SSMSI = "SSMSI (Interstats) — base des séries chronologiques (data.gouv.fr)"
URL_SSMSI = "https://www.data.gouv.fr/fr/datasets/r/631cff69-f0da-4890-b4fc-97aeada1476f"
SSMSI_LIGNES = [
    # motif libellé, motif détails, libellé, dim, sens, décl, doublon, ref, geo, commentaire
    ("^Homicides enregistrés", "Sous_indicateur=Homicides ;", "Homicides enregistrés par la police et la gendarmerie (victimes)", "securite_confiance", "bas", "non", "oui", "INSEE 010596040 + Eurostat crim_hom_soff", "FR",
     "Série 2016-2025 ; une série « Non renseigné » couvre 2008-2015 (raccordement possible)"),
    ("^Violences physiques enregistrées", "Sous_indicateur=Ensemble des lieux ;", "Victimes de violences physiques enregistrées", "securite_confiance", "ambigu", "non", "partiel", "Eurostat crim_off_cat", "FR",
     "Délinquance enregistrée : la hausse reflète aussi une meilleure révélation des faits (violences intrafamiliales)"),
    ("^Violences physiques intrafamiliales enregistrées", "Sous_indicateur=Ensemble des lieux ;", "Victimes de violences physiques intrafamiliales enregistrées", "securite_confiance", "ambigu", "non", "non", "", "FR",
     "Sens ambigu : effet de la libération de la parole et des plaintes"),
    ("^Violences sexuelles enregistrées", "Sous_indicateur=Ensemble des lieux ;", "Victimes de violences sexuelles enregistrées", "securite_confiance", "ambigu", "non", "partiel", "Eurostat crim_hom_soff", "FR",
     "Sens ambigu (révélation des faits)"),
    ("^Cambriolages de logement", "", "Cambriolages de logements enregistrés", "securite_confiance", "bas", "non", "partiel", "Eurostat crim_off_cat", "FR", ""),
    ("^Vols sans violence enregistrés", "", "Victimes de vols sans violence enregistrés", "securite_confiance", "bas", "non", "partiel", "Eurostat crim_off_cat", "FR", ""),
    ("^Vols violents sans arme", "", "Vols violents sans arme enregistrés", "securite_confiance", "bas", "non", "partiel", "Eurostat crim_off_cat", "FR", ""),
    ("^Vols avec armes", "", "Vols avec armes enregistrés", "securite_confiance", "bas", "non", "non", "", "FR", ""),
    ("^Escroqueries et les fraudes aux moyens de paiements enregistrées", "Sous_indicateur=Ensemble des lieux ;", "Victimes d'escroqueries et de fraudes aux moyens de paiement enregistrées", "securite_confiance", "bas", "non", "non", "", "FR", ""),
    ("^Destructions et dégradations", "", "Destructions et dégradations volontaires enregistrées", "securite_confiance", "bas", "non", "non", "", "FR", ""),
    ("^Atteintes à caractère raciste", "Sous_indicateur=Ensemble ;", "Atteintes à caractère raciste, xénophobe ou antireligieux enregistrées", "securite_confiance", "ambigu", "non", "non", "", "FR",
     "Discriminations selon l'origine (A8 : égalités en v1) ; sens ambigu (signalement)"),
    ("^Atteintes anti LGBT", "Sous_indicateur=Ensemble ;", "Atteintes anti-LGBT+ enregistrées", "securite_confiance", "ambigu", "non", "non", "", "FR", "Sens ambigu (signalement)"),
    ("^Infractions pour atteintes à la probité", "Sous_indicateur=Ensemble ;", "Infractions d'atteinte à la probité enregistrées (corruption, favoritisme, détournements)", "democratie", "ambigu", "non", "partiel", "Eurostat crim_off_cat",
     "FR", "Intégrité publique ; une hausse peut traduire une meilleure détection"),
    ("^Victimes de traite et", "Sous_indicateur=Ensemble ;", "Victimes de traite et d'exploitation des êtres humains enregistrées", "securite_confiance", "ambigu", "non", "non", "", "FR", ""),
    ("^Sentiment d'insécurité dans le quartier", "", "Personnes se sentant en insécurité dans leur quartier ou village (enquête CVS)", "securite_confiance", "bas", "oui", "non", "", "FM",
     "Enquête Cadre de vie et sécurité (14 ans et plus) ; série arrêtée en 2021 (nouvelle enquête VRS depuis 2022, rupture) ; aucun équivalent dans les catalogues M01/M02"),
    ("^Sentiment d'insécurité au domicile", "", "Personnes se sentant en insécurité à leur domicile (enquête CVS)", "securite_confiance", "bas", "oui", "non", "", "FM",
     "Enquête CVS ; arrêt en 2021 (rupture VRS)"),
    ("^Renoncement à sortir seul", "", "Personnes renonçant à sortir seules de chez elles pour des raisons de sécurité (enquête CVS)", "securite_confiance", "bas", "oui", "non", "", "FM",
     "Enquête CVS ; arrêt en 2021"),
    ("^Cambriolages et tentatives de cambriolages de résidences", "Unite_de_compte=Ménages victimes", "Ménages victimes de cambriolage ou de tentative (enquête CVS)", "securite_confiance", "bas", "oui", "non", "", "FM",
     "Victimation déclarée ; arrêt en 2020"),
    ("^Violences physiques hors ménage", "", "Victimes de violences physiques hors ménage (enquête CVS)", "securite_confiance", "bas", "oui", "non", "", "FM", "Victimation déclarée"),
    ("^Violences physiques et/ou sexuelles au sein du ménage", "Indicateur=Violences physiques", "Victimes de violences physiques ou sexuelles au sein du ménage (enquête CVS)", "securite_confiance", "bas", "oui", "non", "", "FM",
     "Victimation déclarée ; 2008-2018"),
    ("^Violences sexuelles hors ménage", "", "Victimes de violences sexuelles hors ménage (enquête CVS)", "securite_confiance", "bas", "oui", "non", "", "FM", "Victimation déclarée ; 2008-2018"),
    ("^Vols et tentatives de vols avec violence", "", "Victimes de vols ou tentatives de vols avec violence (enquête CVS)", "securite_confiance", "bas", "oui", "non", "", "FM", "Victimation déclarée"),
    ("^Injures", "", "Victimes d'injures (enquête CVS)", "securite_confiance", "bas", "oui", "non", "", "FM", "Victimation déclarée"),
    ("^Menaces", "", "Victimes de menaces (enquête CVS)", "securite_confiance", "bas", "oui", "non", "", "FM", "Victimation déclarée"),
    ("^Escroqueries bancaires", "Unite_de_compte=Ménages victimes", "Ménages victimes d'escroqueries bancaires (enquête CVS)", "securite_confiance", "bas", "oui", "non", "", "FM", "Victimation déclarée ; 2010-2020"),
    ("^Taux de dépôt de plainte", "Sous_indicateur=Violences physiques hors ménage", "Taux de dépôt de plainte des victimes de violences physiques hors ménage (enquête CVS)", "democratie", "ambigu", "oui", "non", "", "FM",
     "Accès à la justice et confiance dans la police (sens ambigu)"),
    ("^Taux de dépôt de plainte", "Sous_indicateur=Cambriolages", "Taux de dépôt de plainte des ménages victimes de cambriolage (enquête CVS)", "democratie", "ambigu", "oui", "non", "", "FM", "Sens ambigu"),
]
for lib_motif, det_motif, lib, dim, sens, decl, doub, ref, geo, com in SSMSI_LIGNES:
    cond = {"lib_motif": lib_motif, "det_motif": "Periodicite=Annuelle" + (".*" if det_motif else "")}
    s = serie("ssmsi__series_chronologiques", lib_motif=lib_motif,
              det_motif=f"(?=.*Periodicite=Annuelle)(?=.*Zone_geographique=France(?: métropolitaine)? ;)" + (f"(?=.*{det_motif})" if det_motif else ""))
    unite = "taux" if "Taux de dépôt" in lib else "nombre (à rapporter à la population)"
    ajouter(lib, dim, SSMSI, f"{URL_SSMSI} (Titre « {s['libelle_source']} » ; {s['details'][:160]})", unite, sens, decl, "resultat",
            "non", doub, com or "Délinquance enregistrée", s, niveau="2", geo=geo, ref_doublon=ref)

# ============================================================================ ITDD (INSEE-SDES), fichier France entière
ITDD = "SDES-INSEE — Indicateurs territoriaux de développement durable (ITDD), France entière"
URL_ITDD = "DiDo SDES rid 305ea0e3-269b-47ee-bab5-7553fec6f010"
ITDD_LIGNES = [
    # variable, libellé, dim, sens, type, doublon, ref, commentaire
    ("infrac_tx_homicides.nan", "Homicides pour 1 000 habitants (ITDD)", "securite_confiance", "bas", "resultat", "partiel", "INSEE 010596040", "Taux calculé sur les données SSMSI ; 2016-2024"),
    ("infrac_tx_violences_horsfam.nan", "Violences physiques hors cadre familial pour 1 000 habitants (ITDD)", "securite_confiance", "bas", "resultat", "non", "", "SSMSI ; 2016-2024"),
    ("infrac_tx_violences_intrafam.nan", "Violences intrafamiliales enregistrées pour 1 000 habitants (ITDD)", "securite_confiance", "ambigu", "resultat", "non", "", "Sens ambigu (révélation)"),
    ("infrac_tx_violences_sex.nan", "Violences sexuelles enregistrées pour 1 000 habitants (ITDD)", "securite_confiance", "ambigu", "resultat", "non", "", "Sens ambigu (révélation)"),
    ("infrac_tx_cambriolages.nan", "Cambriolages pour 1 000 logements (ITDD)", "securite_confiance", "bas", "resultat", "non", "", "SSMSI"),
    ("infrac_tx_vols_pers.nan", "Vols sans violence contre des personnes pour 1 000 habitants (ITDD)", "securite_confiance", "bas", "resultat", "non", "", "SSMSI"),
    ("infrac_tx_vols_vehic.nan", "Vols de véhicules pour 1 000 habitants (ITDD)", "securite_confiance", "bas", "resultat", "non", "", "SSMSI"),
    ("infrac_tx_degrad.nan", "Destructions et dégradations pour 1 000 habitants (ITDD)", "securite_confiance", "bas", "resultat", "non", "", "SSMSI"),
    ("infrac_tx_fraudpaie.nan", "Fraudes aux moyens de paiement pour 1 000 habitants (ITDD)", "securite_confiance", "bas", "resultat", "non", "", "SSMSI"),
    ("nb_dossiers_deposes.nan", "Situations de surendettement soumises aux commissions (nombre de dossiers)", "niveau_de_vie", "bas", "resultat", "partiel", "",
     "Banque de France ; nombre (à rapporter aux ménages) ; INSEE (ODD 1) a un indicateur de surendettement (identifiant à préciser)"),
    ("part_agribio_surf.nan", "Part de la surface agricole en agriculture biologique", "planete", "haut", "moyen", "partiel", "", "Agence Bio ; Eurostat diffuse la même part (jeu org_cropar, non vérifié dans le catalogue M02)"),
    ("taux_conform_prelev_microbio.nan", "Conformité microbiologique de l'eau du robinet (% des prélèvements)", "planete", "haut", "resultat", "partiel", "",
     "Ministère de la santé (contrôle sanitaire) ; INSEE (ODD 6) : population desservie par une eau non conforme (identifiant à préciser)"),
    ("taux_conform_prelev_physico.nan", "Conformité physico-chimique de l'eau du robinet (% des prélèvements)", "planete", "haut", "resultat", "partiel", "", "Contrôle sanitaire (pesticides, nitrates…)"),
    ("part_class_5_eau_sout_nit.nan", "Part des stations d'eaux souterraines trop chargées en nitrates (> 50 mg/l)", "planete", "bas", "resultat", "partiel", "", "Naïades/ADES ; INSEE (ODD 6) diffuse un indicateur nitrates voisin"),
    ("part_baign_douce.excel", "Part des sites de baignade en eau douce de qualité excellente", "planete", "haut", "resultat", "partiel", "Eurostat sdg_06_40", "Directive baignade ; 2013-2024"),
    ("part_baign_mer.excel", "Part des sites de baignade en mer de qualité excellente", "planete", "haut", "resultat", "partiel", "", "Directive baignade ; 2013-2024"),
    ("step_taux_conform.nan", "Taux de conformité des stations d'épuration", "planete", "haut", "moyen", "non", "", "Directive eaux résiduaires urbaines ; 2007-2023"),
    ("taux_rendmt_res_distr.nan", "Rendement des réseaux d'eau potable (part de l'eau non perdue en fuites)", "planete", "haut", "moyen", "non", "", "SISPEA ; 2010-2024"),
    ("vol_prelev.total", "Prélèvements d'eau douce, tous usages (volume)", "planete", "bas", "pression", "partiel", "Eurostat env_wat_abs", "BNPE ; 2014-2022"),
    ("prop_com_catnat.ino", "Part des communes ayant fait l'objet d'un arrêté de catastrophe naturelle pour inondation", "planete", "bas", "resultat", "non", "",
     "Exposition aux aléas (A14 : cadre de vie en v1) ; dépend aussi des procédures de reconnaissance"),
    ("prop_com_catnat.sec", "Part des communes ayant fait l'objet d'un arrêté de catastrophe naturelle pour sécheresse (retrait-gonflement des argiles)", "planete", "bas", "resultat", "non", "",
     "Exposition aux aléas climatiques"),
    ("part_critair_1_0_vp.nan", "Part des voitures particulières Crit'Air 1 ou électriques dans le parc", "planete", "haut", "moyen", "non", "", "SDES (parc automobile) ; 2011-2024"),
    ("bas_niveau_francais.nan", "Part des élèves de 6e de bas niveau en français (évaluations nationales)", "education", "bas", "resultat", "non", "", "DEPP ; 2017-2024 (évaluations de début de 6e)"),
    ("bas_niveau_maths.nan", "Part des élèves de 6e de bas niveau en mathématiques (évaluations nationales)", "education", "bas", "resultat", "non", "", "DEPP ; 2017-2024"),
]
for var, lib, dim, sens, typ, doub, ref, com in ITDD_LIGNES:
    s = serie("sdes__itdd_france_entiere", id=f"FRA.{var}")
    ajouter(lib, dim, ITDD, f"{URL_ITDD} (variable {var.replace('.nan', '')})", s["unite_source"], sens, "non", typ, "non", doub,
            com + " ; produit commun INSEE-SDES (à signaler à M01 pour éviter le double moissonnage)", s, niveau="1", geo="FE", ref_doublon=ref,
            dim_v1="logement_cadre_vie" if "eau du robinet" in lib else None)  # règle R2 (eau du robinet : condition subie)

# ============================================================================ Citepa — inventaire national (format Secten, édition 2026)
CITEPA = "Citepa — inventaire national des émissions, format Secten (édition 2026)"
URL_CITEPA = "https://www.citepa.org/wp-content/uploads/2026/06/serie_longue_Citepa_Secten_ed_2026-d.xlsx"
CITEPA_TOTAUX = [
    ("GES.France hexagonale + Outre-mer inclus dans l'UE.total GES.MtCO2e", "Émissions territoriales de gaz à effet de serre hors UTCATF (Citepa)", "oui", "Eurostat env_air_gge", "FR-UE"),
    ("GES.France hexagonale + Outre-mer inclus dans l'UE.CO2.Mt", "Émissions territoriales de CO2 hors UTCATF (Citepa)", "partiel", "Eurostat env_air_gge", "FR-UE"),
    ("GES.France hexagonale + Outre-mer inclus dans l'UE.CH4.kt", "Émissions de méthane (Citepa)", "partiel", "Eurostat env_air_gge", "FR-UE"),
    ("GES.France hexagonale + Outre-mer inclus dans l'UE.N2O.kt", "Émissions de protoxyde d'azote (Citepa)", "partiel", "Eurostat env_air_gge", "FR-UE"),
    ("GES.France hexagonale + Outre-mer inclus dans l'UE.Total gaz fluorés.kt CO2e", "Émissions de gaz fluorés (Citepa)", "partiel", "Eurostat env_air_gge", "FR-UE"),
    ("AEPP (acidifiants, eutrophisants, polluants photochimiques).France hexagonale.NOX.kt", "Émissions d'oxydes d'azote (Citepa)", "oui", "Eurostat env_air_emis", "FM"),
    ("AEPP (acidifiants, eutrophisants, polluants photochimiques).France hexagonale.SO2.kt", "Émissions de dioxyde de soufre (Citepa)", "oui", "Eurostat env_air_emis", "FM"),
    ("AEPP (acidifiants, eutrophisants, polluants photochimiques).France hexagonale.NH3.kt", "Émissions d'ammoniac (Citepa)", "oui", "Eurostat env_air_emis", "FM"),
    ("AEPP (acidifiants, eutrophisants, polluants photochimiques).France hexagonale.COVNM.kt", "Émissions de composés organiques volatils non méthaniques (Citepa)", "oui", "Eurostat env_air_emis", "FM"),
    ("PM (particules).France hexagonale.PM2.5.kt", "Émissions de particules fines PM2,5 (Citepa)", "oui", "Eurostat env_air_emis", "FM"),
    ("PM (particules).France hexagonale.PM10.kt", "Émissions de particules PM10 (Citepa)", "oui", "Eurostat env_air_emis", "FM"),
    ("PM (particules).France hexagonale.BC.kt", "Émissions de carbone suie (Citepa)", "non", "", "FM"),
    ("POP (polluants organiques persistants).France hexagonale.PCDD-F.g-ITEQ", "Émissions de dioxines et furanes (Citepa)", "non", "", "FM"),
    ("Métaux lourds.France hexagonale.Pb.t", "Émissions de plomb (Citepa)", "non", "", "FM"),
]
for ident, lib, doub, ref, geo in CITEPA_TOTAUX:
    s = serie("citepa__secten_totaux_hors_utcatf", id=ident)
    ajouter(lib, "planete", CITEPA, f"{URL_CITEPA} (feuille BDD_Secten : {ident})", ident.split(".")[-1], "bas", "non", "pression", "non", doub,
            "Inventaire officiel (CCNUCC/CEE-ONU) ; URL nouvelle chaque édition ; licence non trouvée (label « statistique d'intérêt général ») ; "
            "volume total (à rapporter à la population)", s, niveau="2", geo=geo, ref_doublon=ref)
for secteur, nom in (("Transport", "transports"), ("Usage des bâtiments et activités résidentiels/tertiaires", "bâtiments résidentiels et tertiaires"),
                     ("Agriculture / sylviculture", "agriculture"), ("Industrie manufacturière et construction", "industrie manufacturière et construction"),
                     ("Industrie de l'énergie", "industrie de l'énergie"), ("Déchets centralisés", "déchets"), ("UTCATF", "puits de carbone (UTCATF, solde)")):
    ident = f"GES.{secteur}.France hexagonale + Outre-mer inclus dans l'UE.total GES.MtCO2e"
    s = serie("citepa__secten_series", id=ident)
    ajouter(f"Émissions de gaz à effet de serre : secteur {nom} (Citepa)", "planete", CITEPA, f"{URL_CITEPA} ({ident})", "MtCO2e",
            "haut" if secteur == "UTCATF" else "bas", "non", "pression", "non", "partiel",
            "Ventilation sectorielle Secten (cibles de la SNBC par secteur)" + (" ; solde négatif = absorption nette : plus il est négatif, mieux c'est (sens à vérifier)" if secteur == "UTCATF" else ""),
            s, niveau="2", geo="FR-UE", ventilation=f"secteur : {nom}", ref_doublon="Eurostat env_air_gge")

# ============================================================================ EDGAR, empreinte écologique, PNUD
s = edgar_annees()
ajouter("Émissions de gaz à effet de serre (EDGAR, GWP100 AR5)", "planete", "Commission européenne (JRC) — EDGAR 2025",
        "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/EDGAR/datasets/EDGAR_2025_GHG/EDGAR_AR5_GHG_1970_2024.zip (feuille TOTALS BY COUNTRY)",
        "Gg CO2e", "bas", "non", "pression", "non", "partiel",
        "Estimation harmonisée internationale (calibrage européen) ; CC BY 4.0 sauf CO2 combustion (IEA-EDGAR, CC BY-NC-ND 4.0) ; dossier nouveau à chaque édition",
        s, niveau="2", ref_doublon="Eurostat env_air_gge")
FODAFO = "Footprint Data Foundation — comptes nationaux d'empreinte écologique et de biocapacité (édition 2026)"
URL_FODAFO = "https://fodafo.org/wp-content/uploads/NEFBA2026_bulk_v1_0_omiting_Iceland_Faroe_Islands.xlsx (feuille national_data)"
s = annees_texte("gfn_fodafo__nfba2026_france", r"\] France \| FRA \| (\d{4}) \|")
for col, lib, sens, typ, com in (("efc_total_percapita", "Empreinte écologique de la consommation par habitant", "bas", "pression", "Hectares globaux par habitant"),
                                 ("biocap_total_percapita", "Biocapacité par habitant", "haut", "resultat", "Capacité biologique du territoire"),
                                 ("efp_total_percapita", "Empreinte écologique de la production par habitant", "bas", "pression", "Variante « production »")):
    ajouter(lib, "planete", FODAFO, f"{URL_FODAFO} (colonne {col})", "hag par habitant", sens, "non", typ, "oui", "non",
            f"{com} ; indicateur composite (6 types de surfaces) ; 2024-2025 estimés (drapeau E) ; téléchargement direct sans inscription (contourne la clé GFN, D21) ; "
            "licence de l'édition FoDaFo non trouvée (paquet public GFN : CC BY-SA 4.0)", s, niveau="2")
PNUD = "PNUD — Rapport sur le développement humain 2025 (séries composites)"
URL_PNUD = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv"
PNUD_LIGNES = [
    ("hdi", "Indice de développement humain (IDH)", "niveau_de_vie", "haut", "resultat", "oui", "non", "", "Composite (santé, éducation, revenu)"),
    ("ihdi", "IDH ajusté aux inégalités", "egalites", "haut", "resultat", "oui", "non", "", "Composite ; 2010-2023"),
    ("coef_ineq", "Coefficient d'inégalité humaine (PNUD)", "egalites", "bas", "resultat", "oui", "non", "", "Moyenne des inégalités en santé, éducation et revenu"),
    ("ineq_inc", "Inégalité de revenu (indice d'Atkinson, PNUD)", "egalites", "bas", "resultat", "non", "partiel", "INSEE 010594680", "Base de données mondiale ; l'INSEE publie Gini et rapports interquintiles"),
    ("ineq_le", "Inégalité d'espérance de vie (indice d'Atkinson, PNUD)", "egalites", "bas", "resultat", "non", "non", "", ""),
    ("ineq_edu", "Inégalité d'éducation (indice d'Atkinson, PNUD)", "egalites", "bas", "resultat", "non", "non", "", ""),
    ("gii", "Indice d'inégalité de genre (PNUD)", "egalites", "bas", "resultat", "oui", "non", "", "Composite (santé reproductive, autonomisation, marché du travail)"),
    ("gdi", "Indice de développement de genre (rapport IDH femmes / IDH hommes)", "egalites", "ambigu", "resultat", "oui", "non", "", "Optimum à 1 (écart dans les deux sens)"),
    ("phdi", "IDH ajusté aux pressions planétaires", "planete", "haut", "resultat", "oui", "non", "", "Composite (IDH corrigé des émissions de CO2 et de l'empreinte matières)"),
    ("mf", "Empreinte matières par habitant (PNUD)", "planete", "bas", "pression", "non", "partiel", "Eurostat env_ac_rme", "Base mondiale (PNUE-IRP)"),
    ("co2_prod", "Émissions de CO2 par habitant, production (PNUD)", "planete", "bas", "pression", "non", "partiel", "Eurostat env_air_gge", ""),
    ("mys", "Durée moyenne de scolarisation des 25 ans et plus (années)", "education", "haut", "resultat", "non", "non", "", "Estimation PNUD (Barro-Lee, UNESCO)"),
    ("eys", "Durée attendue de scolarisation (années)", "education", "haut", "resultat", "non", "non", "", "Estimation PNUD (UNESCO)"),
    ("mmr", "Ratio de mortalité maternelle (pour 100 000 naissances vivantes)", "sante", "bas", "resultat", "non", "non", "", "Estimation inter-agences ONU (modélisée)"),
    ("abr", "Taux de natalité des adolescentes (pour 1 000 femmes de 15-19 ans)", "sante", "bas", "resultat", "non", "partiel", "", "Eurostat diffuse les taux de fécondité par âge"),
]
for col, lib, dim, sens, typ, comp, doub, ref, com in PNUD_LIGNES:
    s = serie("pnud__hdr25_series_composites_france", id=f"FRA#{col}")
    ajouter(lib, dim, PNUD, f"{URL_PNUD} (colonnes {col}_<année>)", "indice ou unité PNUD", sens, "non", typ, comp, doub,
            (com + " ; " if com else "") + "URL par édition ; licence CC BY 3.0 IGO annoncée par le PNUD (non revérifiée)", s, niveau="2", ref_doublon=ref)
for col, nom in (("lfpr_f", "femmes"), ("lfpr_m", "hommes")):
    s = serie("pnud__hdr25_series_composites_france", id=f"FRA#{col}")
    ajouter("Taux d'activité des 15 ans et plus (OIT, via PNUD)", "travail", PNUD, f"{URL_PNUD} ({col})", "%", "haut", "non", "resultat", "non", "oui",
            "Estimation modélisée OIT ; ventilation utile pour l'écart femmes-hommes", s, niveau="2", ventilation=f"sexe : {nom}", ref_doublon="Eurostat lfsa_ergaed")

# ============================================================================ SDES — qualité de l'air (DiDo)
SDES = "SDES — qualité de l'air (plateforme DiDo)"
SDES_LIGNES = [
    ("sdes__air_exposition_pm25_fond_urbain", "PM2_5.Fond_urbain#INDICATEUR_EXPO_MOY", "Exposition moyenne de la population urbaine aux PM2,5 (fond urbain, moyenne triennale)", "µg/m³", "d237b4e4-c1ce-431f-8716-4297be69f261",
     "Indicateur réglementaire (objectifs 2020, 2025, 2030 publiés dans le même fichier : 14,7 ; 11,2 ; 10 µg/m³) ; moyennes triennales glissantes"),
    ("sdes__air_concentrations_ugm3", "NO2.fond_urbain_periurbain", "Concentration moyenne annuelle de NO2 en fond urbain", "µg/m³", "9db8c875-10d8-49b3-ac30-1e6f358ab6b0", ""),
    ("sdes__air_concentrations_ugm3", "NO2.proximite_trafic_urbain", "Concentration moyenne annuelle de NO2 à proximité du trafic", "µg/m³", "9db8c875-10d8-49b3-ac30-1e6f358ab6b0", ""),
    ("sdes__air_concentrations_ugm3", "PM10.fond_urbain_periurbain", "Concentration moyenne annuelle de PM10 en fond urbain", "µg/m³", "9db8c875-10d8-49b3-ac30-1e6f358ab6b0", "Doublon INSEE (ODD 11, 2010-2024) ; série SDES depuis 2007"),
    ("sdes__air_concentrations_ugm3", "PM2_5.fond_urbain_periurbain", "Concentration moyenne annuelle de PM2,5 en fond urbain", "µg/m³", "9db8c875-10d8-49b3-ac30-1e6f358ab6b0", "Depuis 2009"),
    ("sdes__air_concentrations_indice", "O3.Fond_urbain", "Concentration d'ozone en fond urbain (indice base 100 en 2000)", "indice", "b10a6294-7f55-47be-b2e7-2ea2a856e564", "Polluant secondaire, dépend de la météo"),
    ("sdes__air_depassements_sante_pct_agglomerations", "NO2", "Part des agglomérations dépassant la norme de protection de la santé pour le NO2", "%", "a956734e-0f63-4629-821e-669f477d5f53", ""),
    ("sdes__air_depassements_sante_pct_agglomerations", "PM10", "Part des agglomérations dépassant la norme de protection de la santé pour les PM10", "%", "a956734e-0f63-4629-821e-669f477d5f53", ""),
    ("sdes__air_depassements_sante_pct_agglomerations", "O3", "Part des agglomérations dépassant la norme de protection de la santé pour l'ozone", "%", "a956734e-0f63-4629-821e-669f477d5f53", ""),
    ("sdes__air_depassements_o3_vegetation", "O3.Fond_rural", "Part des stations rurales dépassant la valeur cible d'ozone pour la protection de la végétation", "%", "6bcf0cf8-c721-4de9-a964-f040cb2798ab",
     "Impact sur les écosystèmes (planète) ; moyennes pluriannuelles glissantes"),
]
for fichier, ident, lib, unite, rid, com in SDES_LIGNES:
    s = serie(fichier, id=ident)
    dim = "planete" if "végétation" in lib else "logement_cadre_vie"
    doub, ref = ("partiel", "INSEE 010596141") if "PM10" in lib else ("non", "")
    ajouter(lib, dim, SDES, f"https://data.statistiques.developpement-durable.gouv.fr/dido/api/v1/datafiles/{rid}/csv ({ident})", unite, "bas", "non",
            "resultat", "non", doub, (com + " ; " if com else "") + "Stations de mesure (Geod'air)", s, niveau="1", ref_doublon=ref)

# ============================================================================ Santé publique France (Odissé)
ODISSE = "Santé publique France — Odissé (Opendatasoft)"
ODISSE_LIGNES = [
    ("spf_odisse__canicules-nombres-de-jours-de-canicule-france", None, "Nombre de jours-départements en canicule", "planete", "bas", "non", "resultat", "non", "",
     "canicules-nombres-de-jours-de-canicule-france (nb_jdep_can)", "Exposition aux vagues de chaleur (A14 : cadre de vie en v1) ; 2004-2025 (2003 non couvert)"),
    ("spf_odisse__tabagisme-prevalence-selon-le-sexe", "Hommes et Femmes#taux", "Prévalence du tabagisme quotidien (Baromètre de Santé publique France)", "sante", "bas", "oui", "resultat", "oui", "INSEE 010593303",
     "tabagisme-prevalence-selon-le-sexe (taux)", "Enquête Baromètre (18-75 ans) ; 2000, 2005, 2010 puis annuelle depuis 2014 ; l'INSEE reprend la même source"),
    ("spf_odisse__perinatalite-prematurite-france", "FR#tx_prematurite_inf37sa", "Taux de naissances prématurées (< 37 semaines d'aménorrhée)", "sante", "bas", "non", "resultat", "non", "",
     "perinatalite-prematurite-france (tx_prematurite_inf37sa)", "PMSI ; 2012-2024"),
    ("spf_odisse__perinatalite-prematurite-france", "FR#tx_poids_naissance_inf_2500g", "Taux de naissances de faible poids (< 2 500 g)", "sante", "bas", "non", "resultat", "non", "",
     "perinatalite-prematurite-france (tx_poids_naissance_inf_2500g)", "PMSI ; 2012-2024"),
    ("spf_odisse__couvertures-vaccinales-issues-des-certificats-de-sante-du-24eme-mois-depuis-2004-france", "cs24_ror2", "Couverture vaccinale ROR deux doses à 24 mois", "sante", "haut", "non", "moyen", "non", "",
     "couvertures-vaccinales-…-24eme-mois (cs24_ror2)", "Certificats de santé du 24e mois ; 2010-2024"),
    ("spf_odisse__couvertures-vaccinales-issues-des-certificats-de-sante-du-24eme-mois-depuis-2004-france", "cs24_dtpch3", "Couverture vaccinale DTP-coqueluche-Hib à 24 mois", "sante", "haut", "non", "moyen", "non", "",
     "couvertures-vaccinales-…-24eme-mois (cs24_dtpch3)", "2004-2024"),
    ("spf_odisse__cancer-participation-au-depistage-organise-du-cancer-du-sein_fra", None, "Participation au dépistage organisé du cancer du sein (taux standardisé, sur 2 ans)", "sante", "haut", "non", "moyen", "non", "",
     "cancer-participation-au-depistage-organise-du-cancer-du-sein_fra (tx_part_insee_std)", "Campagnes biennales glissantes"),
    ("spf_odisse__sante-mentale-episodes-depressifs-caracterises-dans-les-12-derniers-mois_fra", "Hommes et Femmes#taux_depisodes_depressifs_12_derniers_mois", "Prévalence des épisodes dépressifs caractérisés au cours des 12 derniers mois", "sante", "bas", "oui", "resultat", "partiel", "Eurostat hlth_ehis_mh1e",
     "sante-mentale-episodes-depressifs-…_fra", "Baromètre santé 2005, 2010, 2017, 2021 (D17)"),
    ("spf_odisse__sante-mentale-pensees-suicidaires-et-tentatives-de-suicide_fra", "Hommes et Femmes#ps_12m_v", "Pensées suicidaires au cours des 12 derniers mois", "sante", "bas", "oui", "resultat", "non", "",
     "sante-mentale-pensees-suicidaires-et-tentatives-de-suicide_fra (ps_12m_v)", "Baromètre santé 2005, 2010, 2017, 2021 (D17)"),
    ("spf_odisse__gestes-auto-infliges-hospitalisations-france", "Tous.Hommes et Femmes#taux_standardise", "Hospitalisations pour geste auto-infligé (taux standardisé)", "sante", "bas", "non", "resultat", "non", "",
     "gestes-auto-infliges-hospitalisations-france (taux_standardise)", "PMSI ; 2019-2024"),
    ("spf_odisse__suicides-deces-france", "Hommes et Femmes.Tous#taux_standardise", "Taux standardisé de décès par suicide (Santé publique France)", "sante", "bas", "non", "resultat", "oui", "INSEE 010599567",
     "suicides-deces-france (taux_standardise)", "CépiDc ; 2019-2023 dans ce jeu (l'INSEE diffuse 2011-2023)"),
]
for fichier, ident, lib, dim, sens, decl, typ, doub, ref, ident_aff, com in ODISSE_LIGNES:
    s = serie(fichier, id=ident) if ident else serie(fichier)
    ajouter(lib, dim, ODISSE, f"https://odisse.santepubliquefrance.fr/api/explore/v2.1/catalog/datasets/{ident_aff}", s["unite_source"] or "taux ou nombre",
            sens, decl, typ, "non", doub, com, s, niveau="1", ref_doublon=ref)

# ============================================================================ DEPP (éducation)
DEPP = "DEPP — data.education.gouv.fr (Opendatasoft)"
DEPP_LIGNES = [
    ("depp__fr-en-proportion-de-bacheliers-dans-une-generation", "France hors Mayotte.Tous baccalauréats.données définitives#pourcentage_de_bacheliers_dans_une_generation",
     "Proportion de bacheliers dans une génération", "education", "haut", "partiel", "", "", "Données définitives 2001-2023 (provisoires 2024-2025 dans le même jeu)", "FR-D976"),
    ("depp__fr-en-reussite-au-baccalaureat-origine-sociale", "Ensemble#pourcentage_d_admis_au_baccalaureat", "Taux de réussite au baccalauréat (toutes séries)", "education", "haut", "non", "", "",
     "Taux d'admis parmi les présents ; sensible aux évolutions de l'examen", "FR"),
    ("depp__fr-en-reussite-au-baccalaureat-origine-sociale", "Ouvriers#pourcentage_d_admis_au_baccalaureat", "Taux de réussite au baccalauréat (toutes séries)", "egalites", "haut", "non", "", "origine sociale : enfants d'ouvriers",
     "Ventilation par origine sociale (écart avec les enfants de cadres à calculer)", "FR"),
    ("depp__fr-en-reussite-au-baccalaureat-origine-sociale", "Cadres, professions intellectuelles supérieures#pourcentage_d_admis_au_baccalaureat", "Taux de réussite au baccalauréat (toutes séries)", "egalites", "haut", "non", "",
     "origine sociale : enfants de cadres", "Ventilation par origine sociale", "FR"),
    ("depp__fr-en-objectifs_europeens_education_formation", "France.Ensemble#elet", "Sortants précoces du système éducatif (18-24 ans, objectif européen)", "education", "bas", "oui", "Eurostat edat_lfse_14", "",
     "Reprise par la DEPP de l'indicateur européen (2013-2024)", "FR"),
    ("depp__fr-en-objectifs_europeens_education_formation", "France.Ensemble#dipl_sup", "Diplômés de l'enseignement supérieur parmi les 25-34 ans (objectif européen)", "education", "haut", "oui", "Eurostat edat_lfse_03", "",
     "Reprise par la DEPP de l'indicateur européen", "FR"),
]
for fichier, ident, lib, dim, sens, doub, ref, vent, com, geo in DEPP_LIGNES:
    s = serie(fichier, id=ident)
    sens_final = "bas" if lib.startswith("Sortants") else sens
    ajouter(lib, dim, DEPP, f"https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/{fichier.split('__')[1]} ({ident})", "%", sens_final, "non",
            "resultat", "non", doub, com, s, niveau="1", geo=geo, ventilation=vent, ref_doublon=ref)

# ============================================================================ Assurance maladie — risques professionnels
AMELI = "Assurance maladie — risques professionnels (data.ameli.fr)"
for ident, lib, sens, com in (("Accidents du travail.TOUS.Tous secteurs confondus.Tous secteurs confondus#indice_frequence_int", "Indice de fréquence des accidents du travail (pour 1 000 salariés, régime général)", "bas", "Accidents avec arrêt ; 2005-2024"),
                              ("Accidents de trajet.TOUS.Tous secteurs confondus.Tous secteurs confondus#indice_frequence_int", "Indice de fréquence des accidents de trajet (pour 1 000 salariés)", "bas", ""),
                              ("Maladies professionnelles.TOUS.Tous secteurs confondus.Tous secteurs confondus#nb_sinistres_int", "Maladies professionnelles reconnues (nombre, régime général)", "ambigu",
                               "Nombre (à rapporter aux salariés : colonne nb_salaries_int) ; une hausse peut traduire une meilleure reconnaissance")):
    s = serie("cnam_ameli__sinistralite_naf1", id=ident)
    ajouter(lib, "travail", AMELI, f"https://data.ameli.fr/api/explore/v2.1/catalog/datasets/sinistralite-par-secteur-d-activite-concerne-naf-1 ({ident})",
            "pour 1 000 salariés" if "indice" in ident else "nombre", sens, "non", "resultat", "non", "partiel", com, s, niveau="1",
            ref_doublon="Eurostat hsw_mi08")

# ============================================================================ Banque mondiale — WDI (extraits de phase 1, séries des prototypes)
BM = "Banque mondiale — World Development Indicators (API v2)"
BM_LIGNES = [
    ("VC.IHR.PSRC.P5", "Homicides volontaires pour 100 000 habitants (ONUDC, via Banque mondiale)", "securite_confiance", "bas", "resultat", "partiel", "INSEE 010596040 + Eurostat crim_hom_soff", "Source ONUDC"),
    ("EN.ATM.PM25.MC.M3", "Exposition moyenne annuelle aux PM2,5 (Banque mondiale)", "logement_cadre_vie", "bas", "resultat", "partiel", "INSEE 010596141", "Modélisation ; série des prototypes"),
    ("EN.GHG.CO2.PC.CE.AR5", "Émissions de CO2 par habitant (Banque mondiale, remplaçant de EN.ATM.CO2E.PC archivé)", "planete", "bas", "pression", "partiel", "Eurostat env_air_gge", "Série des prototypes (code remplacé)"),
    ("EN.GHG.ALL.PC.CE.AR5", "Émissions totales de gaz à effet de serre par habitant (Banque mondiale)", "planete", "bas", "pression", "partiel", "Eurostat env_air_gge", ""),
    ("NY.ADJ.NNTY.PC.KD", "Revenu national net ajusté par habitant (dollars constants)", "niveau_de_vie", "haut", "resultat", "non", "", "Déduit la dépréciation du capital et l'épuisement des ressources ; série figée à 2021"),
    ("NY.ADJ.SVNG.GN.ZS", "Épargne nette ajustée (% du RNB)", "planete", "haut", "resultat", "non", "", "Indicateur de soutenabilité (« épargne véritable ») ; série figée à 2021"),
    ("SL.TLF.CACT.FM.ZS", "Rapport des taux d'activité femmes / hommes (OIT modélisé)", "egalites", "haut", "resultat", "partiel", "Eurostat lfsa_ergaed", "Estimation modélisée OIT"),
    ("IT.NET.USER.ZS", "Personnes utilisant internet (% de la population)", "education", "haut", "moyen", "oui", "Eurostat isoc_ci_ifp_iu", "UIT"),
    ("SL.GDP.PCAP.EM.KD", "PIB par personne employée (productivité du travail, PPA)", "niveau_de_vie", "haut", "moyen", "partiel", "", "Productivité ; repère économique (A12)"),
    ("SI.POV.GINI", "Indice de Gini du revenu (Banque mondiale)", "egalites", "bas", "resultat", "oui", "INSEE 010594680", "Reprend EU-SILC : préférer la source nationale"),
]
for code, lib, dim, sens, typ, doub, ref, com in BM_LIGNES:
    s = serie_banque_mondiale_phase1(code)
    ajouter(lib, dim, BM, f"https://api.worldbank.org/v2/country/FRA/indicator/{code}?format=json", "voir source", sens, "non", typ, "non", doub,
            com + (" ; " if com else "") + "Extrait de phase 1 (vague 4)", s, niveau="1", ref_doublon=ref)

# ============================================================================ BCE — comptes financiers trimestriels (série longue, vague 8)
s = serie("bce__qsa_dette_menages_revenu_longue", id_debut="QSA.Q.N.FR.W0.S1M.S1.N.L.LE.F4")
ajouter("Endettement des ménages : crédits rapportés au revenu disponible brut ajusté (BCE)", "niveau_de_vie",
        "BCE — ECB Data Portal (SDMX, comptes financiers trimestriels QSA)",
        "https://data-api.ecb.europa.eu/service/data/QSA/Q.N.FR.W0.S1M.S1.N.L.LE.F4.T._Z.XDC_R_B6GA_CY._T.S.V.N._T",
        "% du revenu disponible brut ajusté", "bas", "non", "pression", "non", "partiel",
        "Trimestriel depuis 1999T4 (agrégeable en annuel : 4e trimestre ou moyenne) ; sans clé (alternative à Webstat, D21) ; "
        "même concept que How's Life 15_6 (base différente)", s, niveau="1", frequence="annuelle")
