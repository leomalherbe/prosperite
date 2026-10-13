"""Tests hors ligne de l'accès Eurostat (src/sources/eurostat.py) et des catalogues
(src/pipeline/catalogue_eurostat.py), sur les fixtures de tests/fixtures/eurostat/."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.pipeline import catalogue_eurostat as cat
from src.sources import eurostat as es

FIX = Path(__file__).parent / "fixtures" / "eurostat"


def charger(nom: str) -> dict:
    return json.loads((FIX / nom).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ TOC


@pytest.fixture(scope="module")
def toc_en() -> pd.DataFrame:
    return es.analyser_toc((FIX / "toc_extrait_en.txt").read_text(encoding="utf-8"))


def test_toc_entete_ignoree_et_types(toc_en):
    assert "title" not in set(toc_en["titre"])
    assert set(toc_en["type"]) == {"folder", "table", "dataset"}
    assert toc_en.iloc[0]["code"] == "data" and toc_en.iloc[0]["profondeur"] == 0


def test_toc_hierarchie_conservee(toc_en):
    ligne = toc_en.set_index("code").loc["ei_bssi_m_r2"]
    assert ligne["profondeur"] == 5
    assert ligne["theme_source"] == (
        "Database by themes > General and regional statistics > European and national indicators for short-term analysis"
        " > Business and consumer surveys > Business and consumer survey - composite indicators"
    )
    assert ligne["theme_codes"] == "data > general > euroind > ei_bcs > ei_bcs_mi"


def test_toc_tableau_range_sous_un_jeu(toc_en):
    # sdg_08_10 est un « table » rangé sous le jeu nama_10_pc (et ailleurs sous le dossier Goal 8)
    lignes = toc_en[toc_en["code"] == "sdg_08_10"]
    assert list(lignes["type"]) == ["table", "table"]
    assert lignes.iloc[0]["parent"] == "nama_10_pc"
    assert lignes.iloc[0]["theme_codes"] == "data > economy > na10 > nama10 > nama_10_ma"  # dossiers seulement
    assert lignes.iloc[1]["theme_source"] == "Cross cutting topics > EU policies > Sustainable development indicators > Goal 8 - Decent work and economic growth"


def test_toc_deux_racines_de_meme_code(toc_en):
    racines = toc_en[toc_en["profondeur"] == 0]
    assert list(racines["titre"]) == ["Database by themes", "Cross cutting topics"]
    assert set(racines["code"]) == {"data"}  # piège : les deux racines portent le code « data »


def test_toc_dates_et_valeurs(toc_en):
    ligne = toc_en.set_index("code").loc["ei_bpm6ca_q"]
    assert ligne["derniere_maj"] == "2026-10-02"
    assert (ligne["debut"], ligne["fin"]) == ("1991-Q1", "2026-Q2")
    assert ligne["nb_valeurs"] == 314789
    dossier = toc_en.set_index("code").loc["ei_bp"]
    assert dossier["derniere_maj"] == "" and pd.isna(dossier["nb_valeurs"])


def test_toc_francais():
    fr = es.analyser_toc((FIX / "toc_extrait_fr.txt").read_text(encoding="utf-8"))
    assert fr.set_index("code").loc["general", "titre"] == "Statistiques générales et régionales"
    assert fr.set_index("code").loc["ei_bpm6ca_q", "derniere_maj"] == "2026-10-02"
    assert fr[fr["code"] == "ilc_pw01"].iloc[0]["titre"] == "Satisfaction globale de la vie par sexe, âge et niveau d'éducation atteint"


# ------------------------------------------------------------------ JSON-stat


def test_jsonstat_positions_clairsemees():
    jeu = es.analyser_jsonstat(charger("sdg_01_10_FR_fr.json"))
    assert jeu.code == "sdg_01_10"
    assert [d.id for d in jeu.dimensions] == ["freq", "age", "unit", "geo", "time"]
    lignes = jeu.lignes()
    assert list(lignes.columns) == ["serie_id", "geo", "periode", "valeur", "statut"]
    assert len(lignes) == 44  # 4 séries × 11 années (la période 2014 est présente mais vide)
    idx = lignes.set_index(["serie_id", "periode"])
    assert idx.loc[("sdg_01_10?freq=A&age=TOTAL&unit=PC&geo=FR", "2015"), "valeur"] == 18.4
    # position 25 = (age=Y_LT18 → 1) × 24 + (unit=PC → 0) × 12 + (time=2015 → 1)
    assert idx.loc[("sdg_01_10?freq=A&age=Y_LT18&unit=PC&geo=FR", "2015"), "valeur"] == 22.4
    assert idx.loc[("sdg_01_10?freq=A&age=TOTAL&unit=THS_PER&geo=FR", "2025"), "valeur"] == 13863
    assert idx.loc[("sdg_01_10?freq=A&age=TOTAL&unit=PC&geo=FR", "2020"), "statut"] == "b"
    assert idx.loc[("sdg_01_10?freq=A&age=TOTAL&unit=PC&geo=FR", "2021"), "statut"] == ""
    assert "2014" not in set(lignes["periode"])
    assert set(lignes["geo"]) == {"FR"}
    assert jeu.jeu_source == "ilc_pecs01"


def test_jsonstat_sans_status():
    jeu = es.analyser_jsonstat(charger("sdg_08_10_FR_2022_fr.json"))
    lignes = jeu.lignes()
    assert len(lignes) == 2 and set(lignes["statut"]) == {""}
    assert lignes.set_index("serie_id").loc["sdg_08_10?freq=A&unit=CLV20_EUR_HAB&na_item=B1GQ&geo=FR", "valeur"] == 37280
    assert jeu.mise_a_jour.startswith("2026-10-09")


def test_jsonstat_valeurs_en_liste_et_statut_unique():
    doc = {
        "version": "2.0", "class": "dataset", "label": "Essai", "id": ["unit", "geo", "time"], "size": [1, 1, 3],
        "dimension": {
            "unit": {"category": {"index": ["PC"], "label": {"PC": "Pourcentage"}}},
            "geo": {"category": {"index": {"FR": 0}}},
            "time": {"category": {"index": {"2000": 0, "2001": 1, "2002": 2}}},
        },
        "value": [1.5, None, 2.5], "status": "p", "extension": {"id": "ESSAI"},
    }
    lignes = es.analyser_jsonstat(doc).lignes()
    assert list(lignes["periode"]) == ["2000", "2002"]
    assert set(lignes["statut"]) == {"p"}
    assert lignes.iloc[0]["serie_id"] == "essai?unit=PC&geo=FR"


def test_jsonstat_incoherent():
    doc = {"id": ["geo", "time"], "size": [2, 1], "dimension": {"geo": {"category": {"index": {"FR": 0}}}, "time": {"category": {"index": {"2000": 0}}}}, "value": {}}
    with pytest.raises(es.ErreurEurostat):
        es.analyser_jsonstat(doc)


@pytest.mark.parametrize(
    "doc, classe",
    [
        ({"error": {"status": "400", "id": 100, "label": "No results found"}}, es.AucuneDonnee),
        ({"error": {"status": "400", "id": 150, "label": "Semantic error: unknown code XXX"}}, es.ErreurEurostat),
        ({"warning": {"status": 413, "label": "ASYNCHRONOUS_RESPONSE. Your request will be treated asynchronously."}}, es.ReponseAsynchrone),
        ({"error": [{"status": "413", "label": "EXTRACTION_TOO_BIG: 9000000 rows > 5000000"}]}, es.ExtractionTropVolumineuse),
    ],
)
def test_erreurs_json(doc, classe):
    with pytest.raises(classe):
        es.analyser_jsonstat(doc)


def test_serie_id_ventilation_parametre_repete():
    jeu = es.analyser_jsonstat(charger("sdg_01_10_FR_fr.json"))
    assert jeu.serie_id(("A", ["TOTAL", "Y_LT18"], "PC", "FR")) == "sdg_01_10?freq=A&age=TOTAL&age=Y_LT18&unit=PC&geo=FR"


def test_jsonstat_reel_multidimensionnel():
    jeu = es.charger_jsonstat(FIX / "ilc_li02_FR_T_PC_depuis2015_fr.json")
    assert [d.id for d in jeu.dimensions] == ["freq", "statinfo", "unit", "rskpovth", "sex", "age", "geo", "time"]
    lignes = jeu.lignes().set_index(["serie_id", "periode"])
    assert len(lignes) == 2387
    cle = "ilc_li02?freq=A&statinfo=MED_EI&unit=PC&rskpovth=B_60&sex=T&age=TOTAL&geo=FR"
    assert lignes.loc[(cle, "2015"), "valeur"] == 13.6
    assert lignes.loc[(cle, "2022"), ["valeur", "statut"]].tolist() == [15.6, "b"]
    assert lignes.loc[(cle, "2025"), "valeur"] == 16.3


def test_jsonstat_modalite_inexistante_cube_vide():
    # HTTP 200 sans erreur : la dimension filtrée sur un code inconnu a une taille 0
    jeu = es.charger_jsonstat(FIX / "erreur_modalite_inexistante.json")
    assert jeu.observations == [] and jeu.lignes().empty


def test_jsonstat_sans_donnee_france():
    jeu = es.charger_jsonstat(FIX / "sdg_10_20_FR_fr.json")
    assert [len(d.codes) for d in jeu.dimensions if d.id == "geo"] == [0] and jeu.observations == []


def test_jsonstat_last_time_period():
    jeu = es.charger_jsonstat(FIX / "sdg_01_10_FR_lastTimePeriod3_fr.json")
    assert sorted({p for _, p, _, _ in jeu.observations}) == ["2023", "2024", "2025"]


def test_jsonstat_jeu_inexistant():
    with pytest.raises(es.AucuneDonnee):
        es.charger_jsonstat(FIX / "erreur_jeu_inexistant.json")


# ------------------------------------------------------------------ structure SDMX


def test_structure_reelle_referencepartial():
    s = es.analyser_structure((FIX / "dataflow_SDG_01_10_referencepartial.xml").read_bytes())
    assert (s.code, s.partielle, s.dimension_temps) == ("sdg_01_10", True, "TIME_PERIOD")
    assert s.libelle == "Personnes en risque de pauvreté ou d'exclusion sociale"
    assert s.ids == ["freq", "age", "unit", "geo"]
    assert s.dimension("unit").modalites == {"THS_PER": "Milliers de personnes", "PC": "Pourcentage"}
    assert s.dimension("geo").libelle == "Entité géopolitique (déclarante)"
    assert "FR" in s.dimension("geo").modalites and len(s.dimension("geo").modalites) == 39
    s = es.analyser_structure((FIX / "dataflow_ILC_LI02_referencepartial.xml").read_bytes())
    assert s.ids == ["freq", "statinfo", "unit", "rskpovth", "sex", "age", "geo"]
    assert len(s.dimension("age").modalites) == 33


def test_structure_reelle_sans_listes_de_codes():
    s = es.analyser_structure((FIX / "datastructure_SDG_01_10.xml").read_bytes())
    assert s.ids == ["freq", "age", "unit", "geo"] and not s.partielle
    assert all(not d.modalites for d in s.dimensions)


def test_structure_inexistante_enveloppe_soap():
    with pytest.raises(es.AucuneDonnee):
        es.analyser_structure((FIX / "erreur_structure_inexistante.xml").read_bytes())


#: Message SDMX-ML 2.1 synthétique (forme du standard : dataflow + liste de codes partielle + DSD).
STRUCTURE_SYNTHETIQUE = b"""<?xml version="1.0" encoding="UTF-8"?>
<m:Structure xmlns:m="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
  xmlns:s="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure"
  xmlns:c="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common">
 <m:Header><m:ID>ESSAI</m:ID></m:Header>
 <m:Structures>
  <s:Dataflows><s:Dataflow id="SDG_01_10" agencyID="ESTAT" version="1.0">
   <c:Name xml:lang="en">People at risk of poverty or social exclusion</c:Name>
   <c:Name xml:lang="fr">Personnes en risque de pauvret\xc3\xa9 ou d'exclusion sociale</c:Name>
   <s:Structure><Ref id="SDG_01_10" agencyID="ESTAT" version="2.0" class="DataStructure"/></s:Structure>
  </s:Dataflow></s:Dataflows>
  <s:Codelists>
   <s:Codelist id="FREQ" agencyID="ESTAT" version="3.9" isPartial="true"><c:Name xml:lang="en">Frequency</c:Name>
    <s:Code id="A"><c:Name xml:lang="en">Annual</c:Name><c:Name xml:lang="fr">Annuel</c:Name></s:Code></s:Codelist>
   <s:Codelist id="AGE" agencyID="ESTAT" version="9.0" isPartial="true"><c:Name xml:lang="en">Age class</c:Name>
    <s:Code id="TOTAL"><c:Name xml:lang="en">Total</c:Name><c:Name xml:lang="fr">Total</c:Name></s:Code>
    <s:Code id="Y_LT18"><c:Name xml:lang="en">Less than 18 years</c:Name><c:Name xml:lang="fr">Moins de 18 ans</c:Name></s:Code></s:Codelist>
   <s:Codelist id="UNIT" agencyID="ESTAT" version="82.0" isPartial="true"><c:Name xml:lang="en">Unit</c:Name>
    <s:Code id="PC"><c:Name xml:lang="en">Percentage</c:Name><c:Name xml:lang="fr">Pourcentage</c:Name></s:Code>
    <s:Code id="THS_PER"><c:Name xml:lang="en">Thousand persons</c:Name></s:Code></s:Codelist>
   <s:Codelist id="GEO" agencyID="ESTAT" version="28.0" isPartial="true"><c:Name xml:lang="en">Geo</c:Name>
    <s:Code id="EU27_2020"><c:Name xml:lang="en">European Union</c:Name></s:Code>
    <s:Code id="FR"><c:Name xml:lang="en">France</c:Name><c:Name xml:lang="fr">France</c:Name></s:Code></s:Codelist>
  </s:Codelists>
  <s:Concepts><s:ConceptScheme id="ESTAT_CONCEPTS" agencyID="ESTAT" version="1.0">
   <s:Concept id="age"><c:Name xml:lang="en">Age class</c:Name><c:Name xml:lang="fr">Classe d'\xc3\xa2ge</c:Name></s:Concept>
  </s:ConceptScheme></s:Concepts>
  <s:DataStructures><s:DataStructure id="SDG_01_10" agencyID="ESTAT" version="2.0"><s:DataStructureComponents>
   <s:DimensionList id="DimensionDescriptor">
    <s:Dimension id="freq" position="1"><s:ConceptIdentity><Ref id="freq"/></s:ConceptIdentity>
     <s:LocalRepresentation><s:Enumeration><Ref id="FREQ" version="3.9" agencyID="ESTAT"/></s:Enumeration></s:LocalRepresentation></s:Dimension>
    <s:Dimension id="unit" position="3"><s:ConceptIdentity><Ref id="unit"/></s:ConceptIdentity>
     <s:LocalRepresentation><s:Enumeration><Ref id="UNIT" version="82.0" agencyID="ESTAT"/></s:Enumeration></s:LocalRepresentation></s:Dimension>
    <s:Dimension id="age" position="2"><s:ConceptIdentity><Ref id="age"/></s:ConceptIdentity>
     <s:LocalRepresentation><s:Enumeration><Ref id="AGE" version="9.0" agencyID="ESTAT"/></s:Enumeration></s:LocalRepresentation></s:Dimension>
    <s:Dimension id="geo" position="4"><s:ConceptIdentity><Ref id="geo"/></s:ConceptIdentity>
     <s:LocalRepresentation><s:Enumeration><Ref id="GEO" version="28.0" agencyID="ESTAT"/></s:Enumeration></s:LocalRepresentation></s:Dimension>
    <s:TimeDimension id="TIME_PERIOD" position="5"/>
   </s:DimensionList>
  </s:DataStructureComponents></s:DataStructure></s:DataStructures>
 </m:Structures>
</m:Structure>"""


def test_structure_dimensions_ordonnees_et_modalites():
    s = es.analyser_structure(STRUCTURE_SYNTHETIQUE)
    assert s.code == "sdg_01_10"
    assert s.libelle == "Personnes en risque de pauvreté ou d'exclusion sociale"
    assert s.ids == ["freq", "age", "unit", "geo"]
    assert s.partielle
    assert s.dimension("age").modalites == {"TOTAL": "Total", "Y_LT18": "Moins de 18 ans"}
    assert s.dimension("age").libelle == "Classe d'âge"
    assert s.dimension("unit").modalites["THS_PER"] == "Thousand persons"  # repli sur l'anglais
    assert "FR" in s.dimension("geo").modalites


def test_structure_erreur_sdmx():
    xml = b"""<mes:Error xmlns:mes="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
      xmlns:com="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common">
      <mes:ErrorMessage code="100"><com:Text>No results found</com:Text></mes:ErrorMessage></mes:Error>"""
    with pytest.raises(es.AucuneDonnee):
        es.analyser_structure(xml)


# ------------------------------------------------------------------ client HTTP


class _Rep:
    def __init__(self, statut, contenu=b"{}", entetes=None):
        self.status_code, self.content, self.headers, self.url = statut, contenu, entetes or {}, "http://essai"


class _Session:
    def __init__(self, reponses):
        self.reponses, self.appels, self.headers = list(reponses), 0, {}

    def get(self, url, params=None, timeout=None):
        self.appels += 1
        rep = self.reponses.pop(0)
        if isinstance(rep, Exception):
            raise rep
        return rep


def test_client_nouvel_essai_sur_429_et_coupure():
    import requests

    session = _Session([_Rep(429), requests.ConnectionError("coupure"), _Rep(200, b'{"ok": 1}')])
    client = es.ClientEurostat(pause=0, attente_base=0, session=session, journal=lambda m: None)
    rep = client.get("http://essai")
    assert rep.status_code == 200 and session.appels == 3 and client.nb_nouveaux_essais == 2


def test_client_renvoie_4xx_sans_nouvel_essai():
    session = _Session([_Rep(400, b'{"error": {"id": 150}}')])
    client = es.ClientEurostat(pause=0, attente_base=0, session=session, journal=lambda m: None)
    assert client.get("http://essai").status_code == 400 and session.appels == 1


def test_decompression_gzip():
    import gzip

    assert es.decompresser_si_gzip(gzip.compress(b"abc")) == b"abc"
    assert es.decompresser_si_gzip(b"abc") == b"abc"


# ------------------------------------------------------------------ niveau 1


@pytest.mark.parametrize(
    "periode, attendu",
    [("2020", "annuelle"), ("2020-Q1", "trimestrielle"), ("2020-01", "mensuelle"), ("2020-S2", "semestrielle"), ("", "")],
)
def test_frequence_periode(periode, attendu):
    assert cat.frequence_periode(periode) == attendu


def test_filtre_dates():
    assert cat.filtre_dates("1995", "2025", "annuelle") == ("retenu", False)
    assert cat.filtre_dates("2000", "2018", "annuelle")[0].startswith("exclu : fin")
    motif, rattrapable = cat.filtre_dates("2015", "2025", "annuelle")
    assert motif.startswith("hors filtre") and rattrapable
    assert cat.filtre_dates("2019", "2025", "annuelle") == ("hors filtre : début des données 2019 > 2010", False)


@pytest.mark.parametrize(
    "code, chemin, attendu",
    [
        ("sdg_01_10", "Database by themes", "sdg"),
        ("ilc_pw01", "", "qualite_de_vie"),
        ("ilc_li02", "", "revenus_conditions_de_vie"),
        ("lfsa_ergaed", "", "marche_du_travail"),
        ("nama_10_pc", "", "comptes_nationaux"),
        ("nama_10_gdp", "", ""),
        ("hsw_mi08", "Database by themes > Population and social conditions > Health > Health and safety at work", "sante"),
        ("apro_cpsh1", "Database by themes > Agriculture, forestry and fisheries", ""),
    ],
)
def test_dossier_prioritaire(code, chemin, attendu):
    assert cat.dossier_prioritaire(code, chemin) == attendu


@pytest.mark.parametrize(
    "code, titre_en, chemin, dimension",
    [
        ("ilc_li02", "At-risk-of-poverty rate by poverty threshold, age and sex", "Income and living conditions", "niveau_de_vie"),
        ("lfsa_ergaed", "Employment rates by sex, age and educational attainment level (%)", "Labour market", "travail"),
        ("sdg_05_20", "Gender pay gap in unadjusted form", "Sustainable development indicators", "egalites"),
        ("sdg_07_60", "Population unable to keep home adequately warm by poverty status", "", "logement_cadre_vie"),
        ("ilc_pw01", "Overall life satisfaction by sex, age and educational attainment", "Quality of life", "liens_bien_etre"),
        ("env_air_gge", "Greenhouse gas emissions by source sector", "Environment", "planete"),
        ("crim_off_cat", "Police-recorded offences by offence category", "Crime and criminal justice", "securite_confiance"),
        ("edat_lfse_03", "Population by educational attainment level, sex and age (%)", "Education and training", "education"),
    ],
)
def test_etiquetage(code, titre_en, chemin, dimension):
    assert cat.etiqueter(code, titre_en, "", chemin, cat.dossier_prioritaire(code, chemin)).dimension == dimension


def test_etiquetage_repli_odd():
    e = cat.etiqueter("sdg_17_10", "Official development assistance as share of GNI", "", "", "sdg")
    assert (e.dimension, e.methode) == ("niveau_de_vie", "objectif ODD 17")  # aucun mot-clé : repli sur l'ODD
    e = cat.etiqueter("sdg_14_99", "Xyz", "", "", "sdg")
    assert (e.dimension, e.methode) == ("planete", "objectif ODD 14")


def _toc_synthetique() -> pd.DataFrame:
    lignes = [
        ("data", "Database by themes", "folder", 0, "", "", "", ""),
        ("ilc", "Income and living conditions", "folder", 1, "Database by themes", "data", "", ""),
        ("ilc_li02", "At-risk-of-poverty rate by poverty threshold, age and sex", "dataset", 2, "Database by themes > Income and living conditions", "data > ilc", "1995", "2025"),
        ("ilc_pecs01", "Persons at risk of poverty or social exclusion by age and sex", "dataset", 2, "Database by themes > Income and living conditions", "data > ilc", "2015", "2025"),
        ("ilc_old", "Old indicator", "dataset", 2, "Database by themes > Income and living conditions", "data > ilc", "1995", "2015"),
        ("agri", "Agriculture", "folder", 1, "Database by themes", "data", "", ""),
        ("apro_x", "Crop production", "dataset", 2, "Database by themes > Agriculture", "data > agri", "1990", "2025"),
        ("org_x", "Organic farming area", "dataset", 2, "Database by themes > Agriculture", "data > agri", "2000", "2024"),
        ("une_rt_m", "Unemployment by sex and age - monthly data", "dataset", 2, "Database by themes > Labour market", "data > lab", "1983-01", "2026-08"),
        ("tps00001", "Population on 1 January", "table", 2, "Database by themes > Income and living conditions", "data > ilc", "2015", "2025"),
        ("cc", "Cross cutting", "folder", 0, "", "", "", ""),
        ("ilc_li02", "At-risk-of-poverty rate by poverty threshold, age and sex", "dataset", 1, "Cross cutting", "cc", "1995", "2025"),
    ]
    return pd.DataFrame(
        [{"code": c, "titre": t, "type": ty, "profondeur": p, "theme_source": ts, "theme_codes": tc, "parent": "",
          "derniere_maj": "2026-10-01", "derniere_modif_structure": "", "debut": d, "fin": f, "nb_valeurs": 10}
         for c, t, ty, p, ts, tc, d, f in lignes]
    )


def test_catalogue_jeux_regles():
    brut = cat.construire_catalogue_jeux(_toc_synthetique())
    cat_jeux = brut.set_index("code_jeu")
    assert list(brut.columns)[:13] == ["source", "serie_id", "libelle", "unite", "frequence", "geo", "premiere_periode", "derniere_periode", "derniere_maj", "theme_source", "dimension_v0", "candidat", "commentaire"]
    assert cat_jeux.loc["tps00001", "type"] == "table" and cat_jeux.loc["tps00001", "candidat"] == "non"  # tableaux non candidats
    assert cat_jeux.loc["ilc_li02", "candidat"] == "oui"
    assert cat_jeux.loc["ilc_li02", "theme_source"] == "Database by themes > Income and living conditions"
    assert cat_jeux.loc["ilc_li02", "autres_chemins"] == "Cross cutting"
    assert cat_jeux.loc["ilc_pecs01", "candidat"] == "oui" and cat_jeux.loc["ilc_pecs01", "motif_candidat"].startswith("rattrapage")
    assert cat_jeux.loc["ilc_old", "candidat"] == "non" and "fin des données" in cat_jeux.loc["ilc_old", "motif_candidat"]
    assert cat_jeux.loc["apro_x", "candidat"] == "non"
    assert cat_jeux.loc["org_x", "candidat"] == "oui" and cat_jeux.loc["org_x", "dimension_v0"] == "planete"
    assert cat_jeux.loc["une_rt_m", "candidat"] == "non" and cat_jeux.loc["une_rt_m", "motif_candidat"].startswith("infra-annuel")


def test_catalogue_sur_toc_reel(toc_en):
    toc_fr = es.analyser_toc((FIX / "toc_extrait_fr.txt").read_text(encoding="utf-8"))
    c = cat.construire_catalogue_jeux(toc_en, toc_fr).set_index("code_jeu")
    # indicateurs ODD typés « table » : candidats (exception motivée)
    assert c.loc["sdg_01_10", "type"] == "table" and c.loc["sdg_01_10", "candidat"] == "oui"
    assert c.loc["sdg_01_10", "motif_candidat"].startswith("indicateur ODD typé")
    assert "rattrapage" in c.loc["sdg_01_10", "motif_candidat"]  # début 2014 > 2010
    assert c.loc["sdg_08_10", "candidat"] == "oui"
    assert c.loc["tps00001", "candidat"] == "non" and c.loc["tps00001", "motif_candidat"] == "tableau rangé sous le jeu demo_gind"
    assert c.loc["lfsq_egais", "candidat"] == "non" and c.loc["lfsq_egais", "motif_candidat"].startswith("infra-annuel (trimestrielle)")
    # chemin principal sous « Database by themes », autres emplacements conservés
    assert c.loc["ilc_pw01", "theme_source"].startswith("Database by themes > Population and social conditions")
    assert "Cross cutting topics > Cross cutting topics > Quality of life" in c.loc["ilc_pw01", "autres_chemins"]
    assert c.loc["ilc_pw01", "libelle"] == "Satisfaction globale de la vie par sexe, âge et niveau d'éducation atteint"
    assert c.loc["ilc_pw01", "dimension_v0"] == "liens_bien_etre"
    assert c.loc["hlth_silc_10", "dossier_prioritaire"] == "sante"  # le préfixe du code prime sur le dossier QoL


def test_bilan_dossiers():
    toc = _toc_synthetique()
    catalogue = cat.construire_catalogue_jeux(toc)
    b = cat.bilan_dossiers(toc, catalogue).set_index("code_dossier")
    assert b.loc["ilc", "nb_jeux"] == 4 and b.loc["ilc", "nb_candidats"] == 2  # 3 jeux + 1 tableau
    assert b.loc["data", "nb_jeux"] == 7


# ------------------------------------------------------------------ niveau 2


@pytest.mark.parametrize(
    "code, attendu",
    [("TOTAL", (0, 150, False)), ("Y_GE65", (65, 150, False)), ("Y_LT18", (0, 17, False)), ("Y15-64", (15, 64, False)), ("Y25", (25, 25, True)), ("UNK", None)],
)
def test_intervalle_age(code, attendu):
    assert cat.intervalle_age(code) == attendu


def test_age_et_unite_par_defaut():
    assert cat.age_par_defaut(["Y15-64", "Y20-64", "Y15-74"]) == "Y15-74"
    assert cat.age_par_defaut(["Y_LT18", "TOTAL"]) == "TOTAL"
    assert cat.age_par_defaut(["Y_LT1", "Y1", "Y_GE85"], "Life expectancy by age and sex") == "Y_LT1"
    assert cat.choisir_unite(["THS_PER", "PC"]) == "PC"
    assert cat.choisir_unite(["CLV_PCH_PRE_HAB", "CLV20_EUR_HAB"]) == "CLV20_EUR_HAB"
    assert cat.choisir_unite(["THS_T", "T_HAB", "I90"]) == "T_HAB"


def test_series_sdg_01_10():
    jeu = es.analyser_jsonstat(charger("sdg_01_10_FR_fr.json"))
    lignes, roles = cat.construire_series(jeu, cat.ContexteJeu("Chemin", "niveau_de_vie", "2026-10-13"))
    assert roles.ventilations == ["age"] and roles.contenu == [] and roles.unite == "unit"
    defaut = [l for l in lignes if l["type_ligne"] == "defaut"]
    assert len(defaut) == 1
    d = defaut[0]
    assert d["serie_id"] == "sdg_01_10?freq=A&age=TOTAL&unit=PC&geo=FR"
    assert (d["premiere_periode"], d["derniere_periode"], d["nb_annees"], d["candidat"]) == ("2015", "2025", 11, "oui")
    assert d["drapeaux"] == "b:2" and d["unites_disponibles"] == "PC ; THS_PER" and d["derniere_valeur"] == 20.8
    assert d["dimension_v0"] == "niveau_de_vie" and d["jeu_source"] == "ilc_pecs01"
    v = [l for l in lignes if l["type_ligne"] == "ventilation"]
    assert len(v) == 1 and v[0]["candidat"] == "ventilation" and v[0]["ventilation"] == "age"
    assert v[0]["modalites_ventilation"] == "Y_LT18:2015-2025:11"


def _jeu_synthetique() -> es.JeuJsonStat:
    """indic (contenu, 2 modalités) × sex (T, M, F) × unit (PC, THS) × geo FR × 12 années."""
    annees = [str(a) for a in range(2010, 2022)]
    ids, tailles = ["freq", "indic", "sex", "unit", "geo", "time"], [1, 2, 3, 2, 1, len(annees)]
    valeurs, pos = {}, 0
    for i in range(2):
        for s in range(3):
            for u in range(2):
                for t in range(len(annees)):
                    if not (i == 1 and t < 5):  # indic B : 7 années seulement
                        valeurs[str(pos)] = float(i * 100 + s * 10 + u + t / 100)
                    pos += 1
    doc = {
        "label": "Jeu d'essai", "id": ids, "size": tailles, "updated": "2026-10-01T23:00:00+0200",
        "dimension": {
            "freq": {"category": {"index": {"A": 0}}},
            "indic": {"label": "Indicateur", "category": {"index": {"A1": 0, "B2": 1}, "label": {"A1": "Indicateur A", "B2": "Indicateur B"}}},
            "sex": {"category": {"index": {"T": 0, "M": 1, "F": 2}, "label": {"T": "Total", "M": "Hommes", "F": "Femmes"}}},
            "unit": {"category": {"index": {"PC": 0, "THS": 1}, "label": {"PC": "Pourcentage", "THS": "Milliers"}}},
            "geo": {"category": {"index": {"FR": 0}}},
            "time": {"category": {"index": {a: k for k, a in enumerate(annees)}}},
        },
        "value": valeurs, "status": {"0": "b"}, "extension": {"id": "ESSAI_X"},
    }
    return es.analyser_jsonstat(doc)


def test_series_contenu_ventilation_eligibilite():
    lignes, roles = cat.construire_series(_jeu_synthetique())
    assert roles.contenu == ["indic"] and roles.ventilations == ["sex"]
    defaut = {l["serie_id"]: l for l in lignes if l["type_ligne"] == "defaut"}
    assert set(defaut) == {"essai_x?freq=A&indic=A1&sex=T&unit=PC&geo=FR", "essai_x?freq=A&indic=B2&sex=T&unit=PC&geo=FR"}
    a = defaut["essai_x?freq=A&indic=A1&sex=T&unit=PC&geo=FR"]
    assert a["candidat"] == "oui" and a["nb_annees"] == 12 and a["drapeaux"] == "b:1"
    assert a["libelle"] == "Jeu d'essai — Indicateur A"
    b = defaut["essai_x?freq=A&indic=B2&sex=T&unit=PC&geo=FR"]
    assert b["candidat"] == "non" and "7 années" in b["commentaire"]
    v = [l for l in lignes if l["type_ligne"] == "ventilation" and "indic=A1" in l["serie_id"]][0]
    assert v["serie_id"] == "essai_x?freq=A&indic=A1&sex=M&sex=F&unit=PC&geo=FR"
    assert v["modalites"] == "freq=A ; indic=A1 ; sex=M+F ; unit=PC ; geo=FR"
    assert v["libelles_modalites"] == "M=Hommes ; F=Femmes"


def test_series_defauts_imposes():
    lignes, roles = cat.construire_series(_jeu_synthetique(), defauts_imposes={"indic": "B2", "unit": "THS"})
    defaut = [l for l in lignes if l["type_ligne"] == "defaut"]
    assert len(defaut) == 1 and defaut[0]["serie_id"] == "essai_x?freq=A&indic=B2&sex=T&unit=THS&geo=FR"
    assert defaut[0]["unite"] == "Milliers"


def test_planification_requetes():
    s = es.analyser_structure(STRUCTURE_SYNTHETIQUE)
    plan, note = cat.planifier_requetes(s, "FR", "A", 26)
    assert plan == [{"geo": "FR", "freq": "A"}] and note == ""
    gros = es.StructureJeu("gros", "", [
        es.DimensionStructure("freq", 1, modalites={"A": ""}),
        es.DimensionStructure("siec", 2, modalites={**{f"P{i}": "" for i in range(80)}, "TOTAL": ""}),
        es.DimensionStructure("nrg_bal", 3, modalites={f"B{i}": "" for i in range(200)}),
        es.DimensionStructure("unit", 4, modalites={"KTOE": "", "TJ": "", "GWH": ""}),
        es.DimensionStructure("geo", 5, modalites={"FR": "", "DE": ""}),
    ])
    plan, note = cat.planifier_requetes(gros, "FR", "A", 26)
    assert len(plan) == 1 and plan[0]["siec"] == "TOTAL" and "fixées" in note
    plan, note = cat.planifier_requetes(gros, "FR", "A", 26, seuil=5_000)
    assert len(plan) > 1 and all(isinstance(p["nrg_bal"], list) for p in plan)
    assert sum(len(p["nrg_bal"]) for p in plan) == 200


def test_fusion_reponses():
    jeu = _jeu_synthetique()
    moitie = len(jeu.observations) // 2
    a = es.JeuJsonStat(jeu.code, jeu.libelle, jeu.mise_a_jour, jeu.dimensions, jeu.dimension_temps, jeu.observations[:moitie])
    b = es.JeuJsonStat(jeu.code, jeu.libelle, jeu.mise_a_jour, jeu.dimensions, jeu.dimension_temps, jeu.observations[moitie:])
    fusion = cat.fusionner_jeux([a, None, b])
    assert len(fusion.observations) == len(jeu.observations)
    assert cat.fusionner_jeux([]) is None


# ------------------------------------------------------------------ amorce


PROTO = {"id_prototype": "arope", "dimension_prototype": "Pauvreté & précarité", "libelle": "Risque de pauvreté ou d'exclusion sociale", "code_source": "sdg_01_10"}


def test_amorce_disponible():
    jeu = es.analyser_jsonstat(charger("sdg_01_10_FR_fr.json"))
    l = cat.ligne_amorce(dict(PROTO, commentaire_manuel="Note de phase 1"), jeu, date="2026-10-13", present_toc=True)
    assert list(l) == cat.COLONNES_AMORCE
    assert l["statut"] == "disponible"
    assert (l["premiere_periode_fr"], l["derniere_periode_fr"], l["nb_periodes_fr"]) == ("2015", "2025", 11)
    assert l["unite_par_defaut"] == "PC" and l["unites_disponibles"] == "PC ; THS_PER"
    assert l["ventilations_utiles"] == "age (TOTAL ; Y_LT18)" and l["drapeaux"] == "b" and l["jeu_source"] == "ilc_pecs01"
    assert l["commentaire"].startswith("Note de phase 1" + cat.SEPARATEUR_ROBOT)


def test_amorce_serie_courte_et_absente():
    jeu = es.analyser_jsonstat(charger("sdg_08_10_FR_2022_fr.json"))
    l = cat.ligne_amorce(dict(PROTO, code_source="sdg_08_10"), jeu, defauts={"unit": "CLV20_EUR_HAB"}, present_toc=True)
    assert l["statut"] == "disponible (série courte)" and l["unite_par_defaut"] == "CLV20_EUR_HAB"
    l = cat.ligne_amorce(PROTO, None, "AucuneDonnee : 404", present_toc=False)
    assert l["statut"] == "à remplacer"
    l = cat.ligne_amorce(PROTO, None, "réponse sans valeur", present_toc=True)
    assert l["statut"] == "sans donnée FR"


def _jeu_roles(dimension: str, codes: list[str]) -> es.JeuJsonStat:
    doc = {
        "label": "Essai rôles", "id": ["freq", dimension, "geo", "time"], "size": [1, len(codes), 1, 10],
        "dimension": {
            "freq": {"category": {"index": {"A": 0}}},
            dimension: {"category": {"index": {c: i for i, c in enumerate(codes)}}},
            "geo": {"category": {"index": {"FR": 0}}},
            "time": {"category": {"index": {str(2010 + k): k for k in range(10)}}},
        },
        "value": {str(i): 1.0 for i in range(len(codes) * 10)}, "extension": {"id": "ESSAI"},
    }
    return es.analyser_jsonstat(doc)


def test_causes_de_deces_enumerees_meme_avec_total():
    lignes, roles = cat.construire_series(_jeu_roles("icd10", ["TOTAL", "A-B", "X60-X84_Y870"]))
    assert roles.contenu == ["icd10"] and len([l for l in lignes if l["type_ligne"] == "defaut"]) == 3


def test_type_d_individus_isoc_en_ventilation():
    lignes, roles = cat.construire_series(_jeu_roles("ind_type", ["IND_TOTAL", "Y16_24", "F_Y16_74"]))
    assert roles.ventilations == ["ind_type"] and roles.defauts["ind_type"] == "IND_TOTAL"
    assert [l["type_ligne"] for l in lignes] == ["defaut", "ventilation"]
