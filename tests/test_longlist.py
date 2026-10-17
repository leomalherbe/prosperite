"""Tests hors ligne de la long-list commune (src/pipeline/longlist.py).

Les fixtures `tests/fixtures/longlist/` sont de vraies lignes des catalogues (INSEE BDM et
Melodi de la branche m01-insee, Eurostat de la branche m02-eurostat, M04 de main au commit
39fada4, c'est-à-dire **avant** la correction du doublon Gini et le recalcul de
`dimension_v1_proposee` du 14/10 : elles gardent des propositions contraires à la table, utiles
pour tester la priorité des règles d'exception), copiées sans modification ; la table de
correspondance (39 règles, P1–P8) et la grille sont celles du dépôt. Quelques tests modifient
une ligne réelle en mémoire pour isoler une règle : ils le disent.
"""

from __future__ import annotations

import gzip
import json
import logging
import shutil
from pathlib import Path

import pandas as pd
import pytest

from src.pipeline import longlist as ll

DEPOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "longlist"
CHEMIN_M04 = "docs/sources/10_indicateurs_candidats_hors_insee_eurostat.csv"


def preparer_racine(destination: Path) -> Path:
    """Racine de dépôt minimale : fixtures + table de correspondance + grille v1 réelles."""
    shutil.copytree(FIXTURES, destination, dirs_exist_ok=True)
    (destination / "docs/methodo").mkdir(parents=True, exist_ok=True)
    (destination / "indicateurs").mkdir(parents=True, exist_ok=True)
    shutil.copy(DEPOT / ll.CHEMIN_TABLE, destination / ll.CHEMIN_TABLE)
    shutil.copy(DEPOT / ll.CHEMIN_GRILLE, destination / ll.CHEMIN_GRILLE)
    return destination


@pytest.fixture(scope="module")
def racine(tmp_path_factory) -> Path:
    return preparer_racine(tmp_path_factory.mktemp("depot"))


@pytest.fixture(scope="module")
def resultat(racine):
    return ll.construire_longlist(racine)


@pytest.fixture(scope="module")
def table(resultat) -> pd.DataFrame:
    return resultat.table


def ligne(table: pd.DataFrame, serie_id: str) -> pd.Series:
    trouvees = table[table["serie_id"] == serie_id]
    assert len(trouvees) == 1, f"{serie_id} : {len(trouvees)} lignes"
    return trouvees.iloc[0]


def ligne_libelle(table: pd.DataFrame, debut: str) -> pd.Series:
    trouvees = table[table["libelle"].str.startswith(debut)]
    assert len(trouvees) == 1, f"{debut} : {len(trouvees)} lignes"
    return trouvees.iloc[0]


# --- lecture tolérante et union ----------------------------------------------

def test_lecture_utf8_windows1252_et_gzip(tmp_path):
    contenu = "source,serie_id,libelle\nINSEE BDM,001,Espérance de vie à la naissance\n"
    (tmp_path / "a.csv").write_bytes(contenu.encode("utf-8"))
    (tmp_path / "b.csv").write_bytes(contenu.encode("cp1252"))
    (tmp_path / "c.csv.gz").write_bytes(gzip.compress(contenu.encode("utf-8")))
    (tmp_path / "d.csv").write_bytes(contenu.replace(",", ";").encode("utf-8"))
    for nom in ("a.csv", "b.csv", "c.csv.gz", "d.csv"):
        df = ll.lire_csv(tmp_path / nom)
        assert df.loc[0, "libelle"] == "Espérance de vie à la naissance", nom
        assert df.loc[0, "serie_id"] == "001", nom  # identifiants gardés en texte


def test_catalogue_compresse_trouve(tmp_path):
    (tmp_path / "catalogues").mkdir()
    (tmp_path / "catalogues/x.csv.gz").write_bytes(gzip.compress(b"a\n1\n"))
    assert ll.resoudre_chemin(tmp_path, "catalogues/x.csv").name == "x.csv.gz"
    assert ll.resoudre_chemin(tmp_path, "catalogues/absent.csv") is None


def test_colonne_absente_videe_et_signalee(tmp_path, caplog):
    racine = preparer_racine(tmp_path)
    chemin = racine / "catalogues/insee_bdm_catalogue.csv"
    pd.read_csv(chemin, dtype=str, keep_default_na=False).drop(columns=["unite"]).to_csv(chemin, index=False)
    with caplog.at_level(logging.WARNING, logger="longlist"):
        res = ll.construire_longlist(racine)
    bdm = res.table[res.table["catalogue_origine"] == "insee_bdm"]
    assert (bdm["unite"] == "").all()
    assert any("insee_bdm" in a and "unite" in a for a in res.avertissements)
    assert "colonnes absentes" in caplog.text


def test_union_schema_commun(table, resultat):
    assert set(ll.COLONNES_SORTIE) <= set(table.columns)
    assert set(ll.COLONNES_COMMUNES) <= set(ll.COLONNES_SORTIE)
    assert table["ligne_id"].is_unique
    comptes = table["catalogue_origine"].value_counts().to_dict()
    assert comptes == {"insee_bdm": 11, "insee_melodi": 5, "eurostat_series": 13, "autres_sources_m04": 10}
    assert {k: v["lignes"] for k, v in resultat.catalogues.items()} == comptes  # aucune ligne perdue
    # M04 : deux facteurs du WJP partagent la même URL de fichier, mais pas le même ligne_id
    wjp = table[table["serie_id"].str.contains("worldjusticeproject")]
    assert len(wjp) == 2 and wjp["ligne_id"].nunique() == 2
    # voies d'accès et URL
    assert ligne(table, "001688527")["voie_acces"] == "insee_bdm_sdmx"
    estat = ligne(table, "sdg_07_10?freq=A&unit=TOE_HAB&geo=FR")
    assert estat["url_api"] == ll.API_EUROSTAT + "sdg_07_10?freq=A&unit=TOE_HAB&geo=FR"
    wvs = ligne_libelle(table, "Part des personnes estimant qu'on peut faire confiance")
    assert (wvs["voie_acces"], wvs["niveau_source"]) == ("fichier_niveau2", "2")
    assert "preuve : " in wvs["commentaire"]
    # M04 : colonnes propres reprises dans le schéma commun
    assert wvs["declaratif"] == "oui" and wvs["frequence"] == "irreguliere"


def test_ventilation_eurostat_recalculee_sur_les_modalites(table):
    # nb_annees de la ligne = 1, mais ses modalités ont 22 à 23 années jusqu'en 2025
    vent = table[table["serie_id"].str.startswith("ilc_li02?freq=A&statinfo=MEAN_EI")].iloc[0]
    assert vent["nb_points_depuis_2000"] == "23"
    assert (vent["premiere_periode"], vent["derniere_periode"]) == ("2000", "2025")
    assert vent["eligible"] == "oui"


# --- rattachement v1 ---------------------------------------------------------

@pytest.fixture(scope="module")
def regles():
    return ll.charger_table(DEPOT)


@pytest.mark.parametrize("libelle, v0, attendu, ordre", [
    ("Confiance envers les autres", "securite_confiance", "liens_bien_etre", 1),
    ("Confiance envers autrui par sexe, âge et niveau d'éducation atteint", "securite_confiance", "liens_bien_etre", 1),  # P1
    ("Part des personnes estimant qu'on peut faire confiance à la plupart des gens", "securite_confiance", "liens_bien_etre", 1),
    ("Confiance dans la police", "securite_confiance", "democratie", 2),
    ("Enquête mensuelle de conjoncture auprès des ménages - Opinion sur leur capacité d'épargne actuelle : Solde",
     "securite_confiance", "securite", 4),                                                    # P8, variante retenue
    ("Enquête mensuelle de conjoncture auprès des ménages - Opinion sur leur situation financière personnelle - Évolution passée",
     "securite_confiance", "securite", 4),
    ("Enquête mensuelle de conjoncture auprès des ménages - Opinion sur les prix - Évolution passée : Solde",
     "securite_confiance", "hors_grille", 5),                                                 # P8
    ("Cambriolages de logements", "securite_confiance", "securite", 6),
    ("Nombre de tués par accident de la route", "sante", "securite", 7),
    ("Prévalence de la sous-alimentation", "sante", "niveau_de_vie", 8),
    ("Espérance de vie à la naissance", "sante", "sante", 9),
    ("Compétences numériques : usage d'internet", "education", "education", 10),   # 10 avant 11
    ("Taux d'usage d'Internet dans les 3 mois", "education", "logement_cadre_vie", 11),
    ("Taux de personnes ayant effectué un achat en ligne dans les 3 mois", "education", "logement_cadre_vie", 11),  # P2
    ("Ménages raccordés à la fibre optique", "education", "logement_cadre_vie", 11),
    ("Activités industrielles — Préparation de fibres textiles et filature", "education", "education", 13),  # P2
    ("Personnes ayant participé à des activités culturelles", "education", "liens_bien_etre", 12),
    ("Taux de sortie précoce du système scolaire", "education", "education", 13),
    ("Conformité microbiologique de l'eau du robinet (% des prélèvements)", "planete", "logement_cadre_vie", 14),  # P3
    ("Nombre de jours de canicule", "planete", "planete", 15),
    ("Exposition de la population aux particules fines PM2,5", "planete", "logement_cadre_vie", 16),
    ("Emissions de gaz à effet de serre", "planete", "planete", 17),
    ("Situations de surendettement", "niveau_de_vie", "niveau_de_vie", 19),  # D49 : sécurité économique des ménages reste en niveau_de_vie
    ("Levier des institutions financières monétaires", "niveau_de_vie", "hors_grille", 20),    # P5
    ("Comptes de patrimoine financier - données annuelles — Consolidé ; Sociétés financières ; Avoirs ; Monnaies",
     "niveau_de_vie", "hors_v1", 21),                                                         # P6
    ("Comptes de patrimoine financier - données annuelles — Consolidé ; Ménages ; Avoirs ; Parts de fonds d'investissement",
     "niveau_de_vie", "niveau_de_vie", 24),                                                   # P4 et P6 : ménages gardés
    ("Dette trimestrielle des administrations publiques au sens de Maastricht - Ensemble", "niveau_de_vie", "hors_v1", 22),  # P4
    ("Endettement public (dette publique au sens de Maastricht)", "niveau_de_vie", "hors_v1", 22),
    ("Formation brute de capital fixe des ménages", "niveau_de_vie", "hors_v1", 22),
    ("Effort de recherche (en % du PIB)", "niveau_de_vie", "education", 23),
    ("Taux de pauvreté monétaire", "niveau_de_vie", "niveau_de_vie", 24),
    ("Temps libre", "liens_bien_etre", "hors_v1", 26),
    ("Satisfaction de la vie par sexe, âge, niveau d'éducation atteint et domaine — Emploi du temps", "liens_bien_etre", "hors_v1", 26),
    ("Conditions de vie : niveau de satisfaction — 16 ans ou plus ; Satisfaction moyenne concernant l'emploi principal",
     "liens_bien_etre", "travail", 27),                                                       # P7
    ("Personnes évaluant leur satisfaction de la vie comme élevée, moyenne ou faible par sexe, âge, niveau d'éducation "
     "atteint et domaine — Bas ; Emploi — par sexe", "liens_bien_etre", "travail", 27),
    ("Satisfaction de la vie par sexe, âge, niveau d'éducation atteint et domaine — Logement", "liens_bien_etre", "logement_cadre_vie", 28),
    ("Satisfaction moyenne concernant la situation financière", "liens_bien_etre", "niveau_de_vie", 30),
    ("Satisfaction dans la vie - Ensemble", "liens_bien_etre", "liens_bien_etre", 31),
    ("Levier des banques", "non rattachable", "hors_grille", 36),
    ("Population totale", "contexte", "hors_grille", 38),
    ("Série sans étiquette", "", "a_classer", 39),   # dimension_v0 vide = non_classe
])
def test_rattachement_premiere_regle(regles, libelle, v0, attendu, ordre):
    dimension, regle = ll.appliquer_table(libelle, v0, regles)
    assert (dimension, regle.ordre) == (attendu, ordre)


def test_table_exceptions_avant_defaut(regles):
    """Pour chaque dimension_v0, la règle par défaut (motif vide) vient après toutes ses exceptions."""
    assert [r.ordre for r in regles] == list(range(1, len(regles) + 1))
    for v0 in {r.dimension_v0 for r in regles}:
        propres = [r for r in regles if r.dimension_v0 == v0]
        defauts = [r for r in propres if r.motif is None]
        assert len(defauts) == 1 and propres[-1] is defauts[0], v0


def test_rattachement_insensible_aux_accents_et_apostrophes(regles):
    for libelle in ("Qualité de l’air", "Qualite de l'air", "QUALITÉ DE L'AIR"):
        assert ll.appliquer_table(libelle, "planete", regles)[0] == "logement_cadre_vie", libelle
    assert ll.appliquer_table("Nombre de tues sur la route", "sante", regles)[0] == "securite"


def test_rattachement_v0_inconnue(regles):
    assert ll.appliquer_table("Quelque chose", "dimension_inventee", regles) == ("a_classer", None)


def test_ordre_des_regles_mecanisme():
    """Table réduite : la première règle qui correspond l'emporte ; motif vide = défaut."""
    import re
    regles = [
        ll.Regle(1, "x", re.compile("internet", re.I), "internet", "logement_cadre_vie", "R"),
        ll.Regle(2, "x", re.compile("compétences|internet", re.I), "", "education", "R"),
        ll.Regle(3, "x", None, "", "defaut", "—"),
    ]
    assert ll.appliquer_table("Compétences internet", "x", regles)[1].ordre == 1
    assert ll.appliquer_table("Compétences", "x", regles)[1].ordre == 2
    assert ll.appliquer_table("Autre", "x", regles)[0] == "defaut"


def test_regle_commune_a_toutes_les_dimensions():
    """dimension_v0 = « * » : s'applique à toute dimension v0 tant qu'elle précède son défaut."""
    import re
    regles = [
        ll.Regle(1, "*", re.compile("NACE", re.I), "NACE", "hors_grille", "—"),
        ll.Regle(2, "x", None, "", "defaut_x", "—"),
        ll.Regle(3, "y", None, "", "defaut_y", "—"),
        ll.Regle(4, "*", re.compile("tardif", re.I), "tardif", "jamais", "—"),
    ]
    assert ll.appliquer_table("Entreprises par activité NACE", "x", regles)[0] == "hors_grille"
    assert ll.appliquer_table("Entreprises par activité NACE", "y", regles)[0] == "hors_grille"
    assert ll.appliquer_table("Entreprises par activité NACE", "", regles)[0] == "hors_grille"  # non_classe
    assert ll.appliquer_table("Autre", "y", regles)[0] == "defaut_y"
    assert ll.appliquer_table("Motif tardif", "x", regles)[0] == "defaut_x"   # après le défaut de x
    assert ll.appliquer_table("Motif tardif", "z", regles)[0] == "jamais"     # z n'a pas de défaut


def test_rattachement_sur_les_catalogues(table):
    assert ligne(table, "010593288")["dimension_v1"] == "securite"          # tués sur la route (v0 santé)
    assert ligne(table, "010594852")["dimension_v1"] == "education"         # R&D (A5)
    assert ligne(table, "010596873")["dimension_v1"] == "hors_v1"           # dette publique (A5)
    assert ligne(table, "010595978")["regle_v1"].startswith("15")           # inondations : planète (A14)
    internet = ligne_libelle(table, "Pratiques en ligne des personnes — Taux d’usage d’Internet")
    assert internet["dimension_v1"] == "logement_cadre_vie"                 # A7
    achat = ligne_libelle(table, "Pratiques en ligne des personnes — Taux de personnes ayant effectué un achat")
    assert achat["dimension_v1"] == "logement_cadre_vie"                    # P2 : « en ligne »
    textile = ligne(table, "sbs_sc_ind_r2?freq=A&nace_r2=C131&indic_sb=V11110&size_emp=TOTAL&geo=FR")
    assert textile["dimension_v1"] == "education"                           # P2 : plus de « fibre » seul
    double_risque = ligne(table, "icw_pov_10?freq=A&sex=T&age=TOTAL&indic_ewb=POV_CONS_LFA&unit=PC&geo=FR")
    assert double_risque["dimension_v1"] == "niveau_de_vie"                 # règle 19 (D49 : reste en niveau_de_vie)
    autrui = ligne(table, "ilc_pw03?freq=A&statinfo=AVG&unit=RTG&isced11=TOTAL&domain=OTH&sex=T&age=Y_GE16&geo=FR")
    assert autrui["dimension_v1"] == "liens_bien_etre"                      # P1
    emploi = ligne_libelle(table, "Conditions de vie : niveau de satisfaction")
    assert emploi["dimension_v1"] == "travail"                              # P7


def test_rattachement_m04_exception_de_la_table_prioritaire(table):
    # proposition M04 d'avant le gel (cadre de vie) contre l'exception A14 de la table (planète)
    canicule = ligne_libelle(table, "Nombre de jours-départements en canicule")
    assert canicule["dimension_v1"] == "planete"
    assert canicule["regle_v1"].startswith("15")
    assert "exception de la table prioritaire" in canicule["rattachement_note"]
    assert "logement_cadre_vie" in canicule["rattachement_note"]
    # forçage M04 désormais conforme à une exception de la table (P5, P1) : aucun écart
    levier = ligne_libelle(table, "Levier des institutions financières monétaires")
    assert levier["dimension_v1"] == "hors_grille" and levier["rattachement_note"] == ""
    assert (levier["eligible"], levier["motif_exclusion"]) == ("non", "hors_grille")
    wvs = ligne_libelle(table, "Part des personnes estimant qu'on peut faire confiance")
    assert wvs["dimension_v1"] == "liens_bien_etre" and wvs["rattachement_note"] == ""
    accord = ligne_libelle(table, "Espérance de vie à la naissance (OCDE)")
    assert accord["rattachement_note"] == "" and accord["regle_v1"].startswith("catalogue")


def test_rattachement_m04_regle_par_defaut_cede(tmp_path):
    """Ligne M04 réelle dont la proposition est changée en mémoire (travail → egalites) : la table
    n'a que sa règle par défaut pour travail, la proposition du catalogue est retenue et signalée."""
    racine = preparer_racine(tmp_path)
    chemin = racine / CHEMIN_M04
    df = pd.read_csv(chemin, dtype=str, keep_default_na=False)
    df.loc[df["indicateur"] == "Taux d'emploi des 25-64 ans", "dimension_v1_proposee"] = "egalites"
    df.to_csv(chemin, index=False)
    t = ll.construire_longlist(racine).table
    emploi = ligne_libelle(t, "Taux d'emploi des 25-64 ans")
    assert emploi["dimension_v1"] == "egalites"
    assert emploi["regle_v1"] == "catalogue ; table : 25"
    assert "désaccord : catalogue → egalites (retenu), table → travail" in emploi["rattachement_note"]


# --- éligibilité et dérogations -----------------------------------------------

def test_eligibilite_criteres_bloquants(table):
    hors_idf = table[table["geo"] == "FRANCE-FM_X_R11"].iloc[0]
    assert (hors_idf["eligible"], hors_idf["motif_exclusion"]) == ("non", "geo_non_nationale")
    bop = table[table["serie_id"].str.startswith("bop_its6_det")].iloc[0]
    assert bop["eligible"] == "non"
    assert bop["motif_exclusion"] == "derniere_periode_avant_2020 ; moins_de_10_points"
    assert ll.NOTE_CHAMP_ENTREPRISES in bop["note_eligibilite"]
    dette = ligne(table, "010596873")
    assert (dette["eligible"], dette["motif_exclusion"]) == ("non", "hors_v1")
    ponctuelle = ligne_libelle(table, "Temps consacré aux loisirs et aux soins personnels")
    assert ponctuelle["eligible"] == "non" and "moins_de_10_points" in ponctuelle["motif_exclusion"]


def test_eligibilite_oui(table):
    for serie in ("010593281", "sdg_01_10?freq=A&age=TOTAL&unit=PC&geo=FR", "010594852"):
        assert ligne(table, serie)["eligible"] == "oui", serie
        assert ligne(table, serie)["motif_exclusion"] == "", serie
    assert "D19" in ligne(table, "010594852")["note_eligibilite"]          # type moyen (D19)
    wjp = ligne_libelle(table, "Indice de l'État de droit, score global")
    assert wjp["eligible"] == "oui" and "D18" in wjp["note_eligibilite"]   # composite irrégulier ≥ 10 points


def test_infra_annuelle_sans_compte_de_points(table):
    chomage = ligne(table, "001688527")                                      # trimestrielle 1975-2026
    assert chomage["nb_points_depuis_2000"] == "" and chomage["nb_annees_etendue"] == "27"
    assert chomage["eligible"] == "oui"
    assert "agrégation annuelle" in chomage["note_eligibilite"]


def test_derogation_d17_serie_irreguliere(table):
    # Eurostat juge ilc_pw01 « non » (7 années < 10) : la dérogation D17 prévaut, pas candidat_non
    satisfaction = ligne(table, "ilc_pw01?freq=A&statinfo=AVG&unit=RTG&isced11=TOTAL&life_sat=LIFE&sex=T&age=Y_GE16&geo=FR")
    assert satisfaction["candidat"] == "non"
    assert satisfaction["eligible"] == "a_verifier"
    assert satisfaction["motif_exclusion"] == "moins_de_10_points"
    assert "D17" in satisfaction["note_eligibilite"]
    assert ligne(table, "010596199")["eligible"] == "a_verifier"            # déchets : 7 points sur 13 ans
    wvs = ligne_libelle(table, "Part des personnes estimant qu'on peut faire confiance")
    assert wvs["eligible"] == "a_verifier"                                   # fréquence irrégulière, 3 points


def test_derogation_d16_raccordement_meme_concept(table):
    court = ligne(table, "prc_ppp_ind_1?freq=A&indic_ppp=VI_PPS_EU27_2020_HAB&ppp_cat18=A010101&geo=FR")
    assert court["eligible"] == "a_verifier" and court["motif_exclusion"] == "moins_de_10_points"
    assert "raccordement possible avec prc_ppp_ind?" in court["note_eligibilite"]
    # lien de doublon M04 → INSEE : la série INSEE sert de partenaire
    ocde = ligne_libelle(table, "Rapport des revenus disponibles moyens")
    assert "raccordement possible avec 010594680" in ocde["note_eligibilite"]


def _table_modifiee(racine: Path, modifier) -> pd.DataFrame:
    chemin = racine / "catalogues/eurostat_series_catalogue.csv"
    df = pd.read_csv(chemin, dtype=str, keep_default_na=False)
    modifier(df)
    df.to_csv(chemin, index=False)
    return ll.construire_longlist(racine).table


def test_derogation_d16_par_jeu_source(tmp_path):
    """Ligne réelle sdg_01_10 raccourcie en mémoire (2017-2025, 9 points, sans trou) : sans
    jeu source, elle est exclue ; avec son vrai jeu source ilc_pecs01 (2014-2025 d'après le
    catalogue des jeux), 10 points sont atteignables : à vérifier (D16)."""
    racine = preparer_racine(tmp_path)
    serie = "sdg_01_10?freq=A&age=TOTAL&unit=PC&geo=FR"

    def raccourcir(jeu_source):
        def f(df):
            i = df.index[df["serie_id"] == serie][0]
            df.loc[i, ["premiere_periode", "nb_annees", "nb_points", "jeu_source"]] = ["2017", "9", "9", jeu_source]
        return f

    t = _table_modifiee(racine, raccourcir(""))
    assert (ligne(t, serie)["eligible"], ligne(t, serie)["motif_exclusion"]) == ("non", "moins_de_10_points")
    t = _table_modifiee(racine, raccourcir("ilc_pecs01"))
    assert ligne(t, serie)["eligible"] == "a_verifier"
    assert "jeu source ilc_pecs01 (2014-2025" in ligne(t, serie)["note_eligibilite"]


def test_candidat_non_sans_motif_recalculable(tmp_path):
    """Ligne réelle lfsa_ergaed passée à « non » en mémoire : aucun critère mécanique ne
    l'explique, le refus du catalogue source est repris sous le motif candidat_non."""
    racine = preparer_racine(tmp_path)

    def refuser(df):
        df.loc[df["code_jeu"] == "lfsa_ergaed", "candidat"] = "non"

    t = _table_modifiee(racine, refuser)
    emploi = t[t["serie_id"].str.startswith("lfsa_ergaed")].iloc[0]
    assert (emploi["eligible"], emploi["motif_exclusion"]) == ("non", "candidat_non")


# --- concepts et doublons ------------------------------------------------------

@pytest.mark.parametrize("a, b", [
    ("Taux de chômage au sens du BIT - Ensemble - France hors Mayotte - Données CVS",
     "Taux de chômage au sens du BIT - Ensemble - France métropolitaine - Données brutes"),
    ("Consommation d’énergie primaire", "Consommation d'énergie primaire"),
    ("Personnes en risque de pauvreté ou d'exclusion sociale — par âge",
     "Personnes en risque de pauvreté ou d'exclusion sociale"),
    ("Taux de mortalité pour 1000 personnes - Hommes - Total - France (inclus Mayotte à partir de 2014)",
     "Taux de mortalité - Femmes - France métropolitaine"),
    ("Émissions de gaz à effet de serre (Citepa)", "Emissions de gaz a effet de serre"),
    ("Satisfaction dans la vie - Ensemble", "Satisfaction dans la vie - Femmes"),
    ("Taux d'emploi par niveau d'éducation atteint", "Taux d'emploi"),
    ("Dépenses de santé (2005-2020) — Pourcentage", "Dépenses de santé — Millions d'euros"),
])
def test_cle_concept_identique(a, b):
    assert ll.cle_concept(a) == ll.cle_concept(b) != ""


@pytest.mark.parametrize("a, b", [
    ("Espérance de vie à 60 ans - Hommes", "Espérance de vie à la naissance - Hommes"),
    ("Taux de pauvreté monétaire - Seuil de 60 %", "Taux de pauvreté monétaire - Seuil de 50 %"),
    ("Taux de chômage", "Taux d'emploi"),
])
def test_cle_concept_differente(a, b):
    assert ll.cle_concept(a) != ll.cle_concept(b)


def test_cle_concept_vide():
    assert ll.cle_concept("") == ""
    assert ll.cle_concept("France - 2020 - Pourcentage") == ""


def test_doublons_reference_et_ventilation(table):
    ensemble, femmes = ligne(table, "010593281"), ligne(table, "010593282")
    assert ensemble["doublon_de"] == "" and ensemble["concept_id"] == ensemble["ligne_id"]
    assert femmes["doublon_de"] == "010593281" and femmes["doublon_de_ligne"] == ensemble["ligne_id"]
    assert femmes["doublon_note"] == "même clé de concept" and femmes["nb_lignes_concept"] == "2"
    total = ligne(table, "sdg_01_10?freq=A&age=TOTAL&unit=PC&geo=FR")
    par_age = ligne(table, "sdg_01_10?freq=A&age=Y_LT18&unit=PC&geo=FR")   # total avant ventilation
    assert total["doublon_de"] == "" and par_age["doublon_de"] == total["serie_id"]


def test_doublons_insee_avant_eurostat(table):
    # même concept : la série INSEE (14 points) passe avant la série Eurostat (20 points)
    estat = ligne(table, "sdg_07_10?freq=A&unit=TOE_HAB&geo=FR")
    assert estat["doublon_de"] == "010760755"
    assert ligne(table, "010760755")["doublon_de"] == ""


def test_doublons_m04(table):
    ocde = ligne_libelle(table, "Rapport des revenus disponibles moyens")
    assert ocde["doublon_de"] == "010594680"                                  # idbank INSEE : fusion
    assert "M04" in ocde["doublon_note"] and ocde["dimensions_concept"] == ""
    emploi = ligne_libelle(table, "Taux d'emploi des 25-64 ans")              # code de jeu Eurostat seul
    assert emploi["doublon_de"] == ""
    assert "lfsa_ergaed" in emploi["doublon_note"] and "probable" in emploi["doublon_note"]
    partiel = ligne_libelle(table, "Part des personnes estimant qu'on peut faire confiance")
    assert partiel["doublon_de"] == "" and "partiel" in partiel["doublon_note"]


def test_aucune_ligne_supprimee_ni_exclue_pour_redondance(table):
    doublons = table[table["doublon_de"] != ""]
    assert len(doublons) > 0
    assert not doublons["motif_exclusion"].str.contains("redond|doublon").any()
    assert set(table["eligible"]) <= {"oui", "non", "a_verifier"}
    motifs = {m for texte in table["motif_exclusion"] for m in texte.split(" ; ") if m}
    assert motifs <= set(ll.MOTIFS)


def test_declaratifs(table):
    assert ligne(table, "010593281")["declaratif"] == "presume"               # « satisfaction »
    assert ligne(table, "001688527")["declaratif"] == ""                      # inconnu
    assert ligne_libelle(table, "Taux d'emploi des 25-64 ans")["declaratif"] == "non"  # lu (M04)
    t = pd.DataFrame({"libelle": ["Revenus perçus par les ménages"], "declaratif": [""]})
    ll.marquer_declaratifs(t)
    assert t.loc[0, "declaratif"] == ""                                       # « perçu » = reçu


# --- sorties et bilan ---------------------------------------------------------

def test_sorties_et_bilan(tmp_path):
    racine = preparer_racine(tmp_path)
    res = ll.construire_longlist(racine)
    ecrits = ll.ecrire_sorties(res, racine, "toutes", remarque="essai")
    noms = {p.name for p in ecrits}
    assert {f"longlist_{d}.csv" for d in res.dimensions} | {"longlist_hors_grille.csv", "longlist_bilan.json"} == noms
    bilan = json.loads((racine / "catalogues/longlist_bilan.json").read_text(encoding="utf-8"))
    assert list(bilan["par_dimension"]) == res.dimensions
    total = bilan["total"]["lignes"]
    assert total == len(res.table) == sum(d["lignes"] for d in bilan["par_dimension"].values()) + bilan["hors_grille"]["lignes"]
    for partie in [bilan["total"], *bilan["par_dimension"].values()]:
        assert partie["eligibles"] + partie["a_verifier"] + partie["non_eligibles"] == partie["lignes"]
    assert bilan["remarque"] == "essai" and bilan["table_correspondance"]["regles"] == 39
    assert bilan["total"]["rattachement"]["exceptions_table_prioritaires"] >= 1   # canicule (A14)
    assert bilan["hors_grille_par_statut"] == {"hors_v1": 1, "hors_grille": 1}
    lue = pd.read_csv(racine / "catalogues/longlist_securite.csv", dtype=str, keep_default_na=False)
    assert list(lue.columns) == ll.COLONNES_SORTIE
    assert set(lue["dimension_v1"]) == {"securite"}
    hors = pd.read_csv(racine / "catalogues/longlist_hors_grille.csv", dtype=str, keep_default_na=False)
    assert set(hors["dimension_v1"]) == {"hors_v1", "hors_grille"}


def test_sorties_en_clair_ou_compressees(tmp_path):
    racine = preparer_racine(tmp_path)
    res = ll.construire_longlist(racine)
    gz = racine / "catalogues/longlist_sante.csv.gz"
    gz.write_bytes(gzip.compress(b"commite"))
    # en clair (défaut) : sortie de travail ; le .csv.gz commité n'est pas touché
    assert [p.name for p in ll.ecrire_sorties(res, racine, "sante")] == ["longlist_sante.csv"]
    assert gzip.decompress(gz.read_bytes()) == b"commite"
    # compressée (exécution finale) : .csv.gz réécrit, le .csv en clair périmé est supprimé
    ecrits = ll.ecrire_sorties(res, racine, "sante", compresser=True)
    assert [p.name for p in ecrits] == ["longlist_sante.csv.gz"]
    assert not (racine / "catalogues/longlist_sante.csv").exists()
    lue = pd.read_csv(ecrits[0], dtype=str, keep_default_na=False)
    assert len(lue) == (res.table["dimension_v1"] == "sante").sum()


def test_sorties_en_clair_ignorees_par_git():
    regles = (DEPOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "catalogues/longlist_*.csv" in regles


def test_point_entree(tmp_path, capsys):
    racine = preparer_racine(tmp_path)
    assert ll.main(["--dimension", "egalites", "--racine", str(racine)]) == 0
    assert (racine / "catalogues/longlist_egalites.csv").exists()
    assert not (racine / "catalogues/longlist_bilan.json").exists()           # bilan : mode « toutes »
    assert '"lignes"' in capsys.readouterr().out
    assert ll.main(["--dimension", "toutes", "--compresser", "--racine", str(racine)]) == 0
    assert (racine / "catalogues/longlist_bilan.json").exists()
    assert (racine / "catalogues/longlist_planete.csv.gz").exists()
    assert not (racine / "catalogues/longlist_egalites.csv").exists()
    with pytest.raises(SystemExit):
        ll.main(["--dimension", "dimension_inventee", "--racine", str(racine)])


def test_catalogue_absent_ignore(tmp_path):
    racine = preparer_racine(tmp_path)
    (racine / CHEMIN_M04).unlink()
    res = ll.construire_longlist(racine)
    assert res.catalogues["autres_sources_m04"]["present"] is False
    assert any("absent" in a for a in res.avertissements)
    assert "autres_sources_m04" not in set(res.table["catalogue_origine"])
