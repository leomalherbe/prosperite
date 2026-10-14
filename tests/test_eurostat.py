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


def test_exclusions_hors_france_et_projections():
    toc = pd.DataFrame([
        {"code": "enps_demo_pjan", "titre": "Population on 1 January - ENP-South countries", "type": "dataset", "profondeur": 3,
         "theme_source": "Database by themes > General and regional statistics > Non EU countries", "theme_codes": "data > general > noneu",
         "parent": "", "derniere_maj": "", "derniere_modif_structure": "", "debut": "2005", "fin": "2024", "nb_valeurs": 1},
        {"code": "proj_23np", "titre": "Population on 1st January by age, sex and type of projection", "type": "dataset", "profondeur": 3,
         "theme_source": "Database by themes > Population and social conditions > Population projections", "theme_codes": "data > popul > proj",
         "parent": "", "derniere_maj": "", "derniere_modif_structure": "", "debut": "2022", "fin": "2100", "nb_valeurs": 1},
    ])
    c = cat.construire_catalogue_jeux(toc).set_index("code_jeu")
    assert c.loc["enps_demo_pjan", "candidat"] == "non" and c.loc["enps_demo_pjan", "motif_candidat"].startswith("pays hors UE")
    assert c.loc["proj_23np", "candidat"] == "non" and c.loc["proj_23np", "motif_candidat"].startswith("projections")


def test_faux_amis_mots_cles():
    # « cultures » (récoltes) ne relève pas de la culture ; « fertility » n'est pas « fertiliser »
    assert cat.etiqueter("ef_fsi_cdiv", "Crop diversity", "Diversité des cultures", "", "").dimension != "education"
    assert cat.etiqueter("demo_find", "Fertility indicators", "Indicateurs de fécondité", "", "").dimension != "planete"
    # v4 : « relatives à » (fr) n'est pas « relatives » (proches) ; « politique de sécurité » n'est pas la vie politique
    e = cat.etiqueter("migr_resbc11", "Persons subject to EU Blue Card decisions by length of validity",
                      "Personnes faisant l'objet de décisions relatives à la carte bleue européenne", "", "")
    assert e.dimension != "liens_bien_etre"
    assert cat.etiqueter("isoc_cisce_ra", "Security policy, measures, risks and staff awareness by size class of enterprise",
                         "Politique de sécurité, mesures, risques", "", "").dimension != "democratie"
    assert cat.etiqueter("road_tf_veh", "Road traffic performance by category of vehicle", "", "", "").dimension != "securite_confiance"
    assert cat.etiqueter("tran_sf_roadus", "Road traffic deaths by type of road", "", "", "").dimension == "securite_confiance"
    assert cat.etiqueter("iww_if_infrastr", "Length of navigable inland waterways by waterway type", "", "", "").dimension != "planete"


def test_candidature_v4_titre_principal_et_domaines_hors_perimetre():
    base = {"profondeur": 3, "parent": "", "derniere_maj": "", "derniere_modif_structure": "", "debut": "2000", "fin": "2024", "nb_valeurs": 1}
    agri = "Database by themes > Agriculture, forestry and fisheries > Agriculture"
    toc = pd.DataFrame([
        # mot-clé seulement dans le chemin (« forestry », « fisheries ») : étiquette sans candidature
        dict(base, code="apro_mk_strbt", titre="Butter - distribution of enterprises by volume of annual production",
             type="dataset", theme_source=agri, theme_codes="data > agric > agr"),
        # mot-clé seulement dans la ventilation (« by degree of urbanisation ») : non candidat
        dict(base, code="xyz_nights", titre="Nights spent at establishments by degree of urbanisation",
             type="dataset", theme_source="Database by themes > General", theme_codes="data > general"),
        # domaine hors périmètre malgré un mot-clé du titre (« fish ») ; sauf exception (surface boisée)
        dict(base, code="fish_ld_fr", titre="Landings of fishery products in France", type="dataset",
             theme_source=agri, theme_codes="data > agric > agr"),
        dict(base, code="for_area", titre="Area of wooded land (FAO)", type="dataset",
             theme_source=agri, theme_codes="data > agric > agr"),
        # mot-clé du titre principal : candidat ; agro-environnement conservé
        dict(base, code="aei_pr_gnb", titre="Gross nutrient balance", type="dataset", theme_source=agri, theme_codes="data > agric > agr"),
        # dossier prioritaire : candidat même sans mot-clé
        dict(base, code="demo_nind", titre="Marriage indicators", type="dataset",
             theme_source="Database by themes > Population and social conditions > Demography", theme_codes="data > popul > demo"),
    ])
    c = cat.construire_catalogue_jeux(toc).set_index("code_jeu")
    assert c.loc["apro_mk_strbt", "candidat"] == "non"
    assert c.loc["xyz_nights", "candidat"] == "non" and c.loc["xyz_nights", "motif_candidat"].startswith("mot-clé seulement")
    assert c.loc["fish_ld_fr", "candidat"] == "non" and c.loc["fish_ld_fr", "motif_candidat"].startswith("domaine hors périmètre (pêche")
    assert c.loc["for_area", "candidat"] == "oui" and c.loc["for_area", "dimension_v0"] == "planete"
    assert c.loc["aei_pr_gnb", "candidat"] == "oui" and c.loc["aei_pr_gnb", "dimension_v0"] == "planete"
    assert c.loc["demo_nind", "candidat"] == "oui" and c.loc["demo_nind", "dossier_prioritaire"] == "population"


def test_bilan_dossiers():
    toc = _toc_synthetique()
    catalogue = cat.construire_catalogue_jeux(toc)
    b = cat.bilan_dossiers(toc, catalogue).set_index("code_dossier")
    # rattachement par l'ordre du TOC : ilc contient les 3 jeux qui le suivent (le tableau tps00001 est plus loin)
    assert b.loc["ilc", "nb_jeux"] == 3 and b.loc["ilc", "nb_candidats"] == 2 and b.loc["ilc", "nb_jeux_filtres"] == 1
    assert b.loc["data", "nb_jeux"] == 7
    assert b.loc["cc", "nb_jeux"] == 1  # ilc_li02, rangé aussi sous la seconde racine


def test_bilan_dossiers_toc_reel(toc_en):
    toc_fr = es.analyser_toc((FIX / "toc_extrait_fr.txt").read_text(encoding="utf-8"))
    catalogue = cat.construire_catalogue_jeux(toc_en, toc_fr)
    b = cat.bilan_dossiers(toc_en, catalogue, toc_fr)
    assert list(b.columns) == cat.COLONNES_DOSSIERS
    racines = b[b["code_dossier"] == "data"]  # les deux racines de même code sont deux lignes distinctes
    assert list(racines["chemin"]) == ["Database by themes", "Cross cutting topics"]
    assert list(racines["titre_fr"]) == ["Base de données par thèmes", "Thèmes transversaux"]
    assert b.set_index("chemin_codes").loc["data > general > euroind > ei_bp", "nb_jeux"] == 5  # 5 tableaux
    assert racines["nb_jeux"].sum() >= b[b["profondeur"] == 1]["nb_jeux"].max()


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


# ------------------------------------------------------------------ v5 (14/10) : bogue de l'amorce, D26


def _script():
    """Module du script de collecte, importé sans l'exécuter (aucun appel réseau à l'import)."""
    import importlib.util
    chemin = Path(__file__).resolve().parent.parent / "scripts" / "collecte_eurostat.py"
    spec = importlib.util.spec_from_file_location("collecte_eurostat_test", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_non_regression_cube_vide_geo_sans_modalite():
    # bogue des passages 2 et 3 : env_bio3 n'a que l'agrégat UE ; geo=FR renvoie HTTP 200 avec une dimension
    # geo de taille 0 → IndexError dans attribuer_roles (liste `codes` vide)
    jeu = es.charger_jsonstat(FIX / "sdg_10_20_FR_fr.json")
    lignes, roles = cat.construire_series(jeu, annee_min=0)
    assert lignes == [] and roles.defauts == {}
    roles = cat.attribuer_roles(jeu, {})
    assert "geo" not in roles.defauts
    vide = es.charger_jsonstat(FIX / "erreur_modalite_inexistante.json")  # dimension unit de taille 0
    assert cat.construire_series(vide)[0] == []
    l = cat.ligne_amorce(PROTO, None, "réponse sans aucune valeur pour la France", present_toc=True)
    assert l["statut"] == "sans donnée FR"


def test_verifier_remplacement_cube_vide_et_structure_inattendue(monkeypatch):
    script = _script()
    vide = es.charger_jsonstat(FIX / "sdg_10_20_FR_fr.json")
    monkeypatch.setattr(script.es, "obtenir_jeu", lambda *a, **k: vide)
    assert script._verifier_remplacement("env_bio3") == "env_bio3 : aucune valeur pour la France (cube vide)"
    plein = es.charger_jsonstat(FIX / "sdg_01_10_FR_fr.json")
    monkeypatch.setattr(script.es, "obtenir_jeu", lambda *a, **k: plein)
    assert script._verifier_remplacement("sdg_01_10").startswith("sdg_01_10 vérifié pour la France : 2015–2025")

    def casse(*a, **k):
        raise ValueError("forme inconnue")
    monkeypatch.setattr(script.cat, "construire_series", casse)
    assert script._verifier_remplacement("sdg_01_10").startswith("sdg_01_10 : structure inattendue (ValueError")


def _ligne_toc(code, titre, chemin, debut="2000", fin="2024", type_="dataset"):
    return {"code": code, "titre": titre, "type": type_, "profondeur": chemin.count(">") + 1, "theme_source": chemin,
            "theme_codes": "", "parent": "", "derniere_maj": "", "derniere_modif_structure": "", "debut": debut, "fin": fin, "nb_valeurs": 1}


def test_niveau1_v5_entreprises_peche_sylviculture_contexte():
    numerique = "Database by themes > Science, technology, digital society > Digital economy and society"
    agri = "Database by themes > Agriculture, forestry and fisheries > Fisheries"
    demo = "Database by themes > Population and social conditions > Demography"
    toc = pd.DataFrame([
        _ligne_toc("bd_size", "Business demography by size class and NACE Rev. 2 activity", numerique),
        _ligne_toc("isoc_ci_in_es", "Internet access by size class of enterprise", numerique),
        _ligne_toc("isoc_xyz_n2", "Something new by NACE Rev. 2 activity", numerique),
        _ligne_toc("isoc_ci_ifp_iu", "Individuals - internet use", numerique),
        _ligne_toc("bop_rem6", "Personal transfers and compensation of employees", "Database by themes > Economy"),
        _ligne_toc("lc_ncost_r2", "Labour cost, wages and salaries by NACE Rev. 2 activity", "Database by themes > Labour market"),
        _ligne_toc("fish_ca_main", "Catches - major fishing areas (from 2000 onwards)", agri),
        _ligne_toc("fish_ld_fr", "Landings of fishery products in France", agri),
        _ligne_toc("fish_aq2a", "Production from aquaculture excluding hatcheries", agri, debut="2008"),
        _ligne_toc("for_remov", "Roundwood removals by type of wood and assortment", agri, debut="1988"),
        _ligne_toc("for_vol", "Volume of timber (FAO)", agri, debut="1990"),
        _ligne_toc("for_basic", "Roundwood, fuelwood and other basic products", agri, debut="1988"),
        _ligne_toc("apro_cpsh1", "Crop production in EU standard humidity", agri),
        _ligne_toc("demo_pjan", "Population on 1 January by age and sex", demo),
        _ligne_toc("rd_e_gerdtot", "GERD by sector of performance", "Database by themes > Science"),
        _ligne_toc("htec_emp_nat2", "Employed persons in technology and knowledge-intensive sectors by NACE Rev. 2 activity", "Database by themes > Science"),
        _ligne_toc("naio_10_cp16", "Use table at purchasers' prices", "Database by themes > Economy > National accounts"),
    ])
    c = cat.construire_catalogue_jeux(toc).set_index("code_jeu")
    for code in ("bd_size", "isoc_ci_in_es", "isoc_xyz_n2", "bop_rem6", "lc_ncost_r2", "htec_emp_nat2", "naio_10_cp16"):
        assert c.loc[code, "candidat"] == "non", code
        assert c.loc[code, "motif_candidat"].startswith("entreprises ou échanges extérieurs"), code
    assert c.loc["isoc_ci_ifp_iu", "candidat"] == "oui"  # particuliers : gardé
    for code in ("fish_ca_main", "for_remov", "for_vol"):
        assert c.loc[code, "candidat"] == "oui" and c.loc[code, "dimension_v0"] == "planete", code
        assert c.loc[code, "motif_candidat"].startswith("pêche et sylviculture réintégrées (D26)"), code
    for code in ("fish_ld_fr", "fish_aq2a", "for_basic", "apro_cpsh1"):
        assert c.loc[code, "candidat"] == "non" and c.loc[code, "motif_candidat"].startswith("domaine hors périmètre"), code
    assert c.loc["demo_pjan", "candidat"] == "oui" and c.loc["demo_pjan", "dimension_v0"] == "contexte"
    assert c.loc["rd_e_gerdtot", "candidat"] == "oui" and c.loc["rd_e_gerdtot", "dimension_v0"] == "education"


def test_unites_absolues_preferees_aux_indices_relatifs():
    assert cat.choisir_unite(["PC_EU27_2020_HAB_MEUR_CP", "CLV10_EUR_HAB", "CLV20_EUR_HAB", "CP_EUR_HAB", "CLV_PCH_PRE_HAB"]) == "CLV20_EUR_HAB"
    assert cat.choisir_unite(["PC_EU27_2020_MEUR_CP", "PC_GDP", "CP_MEUR"]) == "PC_GDP"
    assert cat.choisir_unite(["INX_A_AVG", "RCH_A_AVG"]) == "RCH_A_AVG"
    assert cat.choisir_unite(["I15", "THS_T"]) == "THS_T"
    assert cat.choisir_unite(["CLV_I10", "CP_MEUR"]) == "CP_MEUR"
    assert cat.choisir_unite(["I15", "PCH_PRE"]) == "I15"  # pas d'unité absolue : l'indice reste préférable à une variation
    assert cat.choisir_unite(["PPS_EU27_2020_HAB", "PC_EU27_2020_HAB_MPPS_CP"]) == "PPS_EU27_2020_HAB"  # SPA par habitant : absolu
    assert cat.choisir_unite(["CLV15_MEUR", "CLV20_MEUR", "CLV05_MEUR"]) == "CLV20_MEUR"  # année de référence la plus récente
    assert cat.choisir_unite(["THS_PER", "PC"]) == "PC"
    series = pd.DataFrame([
        {"code_jeu": "nama_10_pc", "type_ligne": "defaut", "unite_code": "PC_EU27_2020_HAB_MEUR_CP", "unites_disponibles": "CLV20_EUR_HAB ; PC_EU27_2020_HAB_MEUR_CP"},
        {"code_jeu": "nama_10_pc", "type_ligne": "ventilation", "unite_code": "PC_EU27_2020_HAB_MEUR_CP", "unites_disponibles": "CLV20_EUR_HAB ; PC_EU27_2020_HAB_MEUR_CP"},
        {"code_jeu": "ilc_li02", "type_ligne": "defaut", "unite_code": "PC", "unites_disponibles": "PC ; THS_PER"},
        {"code_jeu": "env_x", "type_ligne": "defaut", "unite_code": "I15", "unites_disponibles": "I15"},
    ])
    assert cat.jeux_a_refaire_unites(series) == {"nama_10_pc": 1}


def test_controle_qualite_v5_faux_amis_partenaire_origine():
    # « besoins de soins non satisfaits » relève de la santé ; « sages-femmes » n'est pas un écart femmes-hommes
    assert cat.etiqueter("sdg_03_60", "Self-reported unmet need for medical examination and care by sex",
                         "Besoins auto-déclarés de traitement médical non satisfaits par sexe", "", "").dimension == "sante"
    assert cat.etiqueter("hlth_rs_prsns", "Nursing and caring professionals", "Infirmiers, sages-femmes et aides-soignants", "", "").dimension != "egalites"
    assert cat.etiqueter("ilc_pw01", "Overall life satisfaction", "Satisfaction globale de la vie", "", "").dimension == "liens_bien_etre"
    # partenaire fixé au monde entier ; nationalité en ventilation
    lignes, roles = cat.construire_series(_jeu_roles("partner", ["WORLD", "DE", "JM"]))
    assert roles.defauts["partner"] == "WORLD" and roles.contenu == [] and len(lignes) == 1
    lignes, roles = cat.construire_series(_jeu_roles("citizen", ["TOTAL", "NAT", "FOR"]))
    assert roles.ventilations == ["citizen"] and [l["type_ligne"] for l in lignes] == ["defaut", "ventilation"]
    # captures de pêche : tous organismes (F00), toutes zones (0) ou la grande zone du jeu (27)
    assert cat.code_total("species", ["AGN", "F00", "F01"]) == "F00"
    assert cat.code_total("fishreg", ["0", "27", "37"]) == "0"
    assert cat.code_total("fishreg", ["27", "27_8", "27_8_A"]) == "27"
    assert cat.code_total("fishreg", ["27_8", "27_9"]) is None
    series = pd.DataFrame({"code_jeu": ["educ_uoe_mobs02", "ilc_li31", "ilc_li02"], "type_ligne": ["defaut"] * 3,
                           "serie_id": ["educ_uoe_mobs02?partner=JM&geo=FR", "ilc_li31?citizen=TOTAL&geo=FR", "ilc_li02?sex=T&geo=FR"]})
    assert cat.jeux_a_refaire_dimensions(series) == {"educ_uoe_mobs02": 1, "ilc_li31": 1}


def _series_df(lignes):
    base = {c: "" for c in cat.COLONNES_SERIES}
    return pd.DataFrame([dict(base, **l) for l in lignes], columns=cat.COLONNES_SERIES)


def test_secteurs_hors_menages_ecartes():
    s = _series_df([
        {"code_jeu": "nasa_10_f_bs", "serie_id": "nasa_10_f_bs?freq=A&unit=MIO_EUR&sector=S11&geo=FR", "candidat": "oui"},
        {"code_jeu": "nasa_10_f_bs", "serie_id": "nasa_10_f_bs?freq=A&unit=MIO_EUR&sector=S14_S15&geo=FR", "candidat": "oui"},
        {"code_jeu": "nasa_10_nf_tr", "serie_id": "nasa_10_nf_tr?freq=A&sector=S1&geo=FR", "candidat": "oui"},
        {"code_jeu": "nasa_10_nf_tr", "serie_id": "nasa_10_nf_tr?freq=A&sector=S13&geo=FR", "candidat": "oui", "commentaire": "note"},
        {"code_jeu": "gov_10a_main", "serie_id": "gov_10a_main?freq=A&sector=S13&geo=FR", "candidat": "oui"},
        {"code_jeu": "nasa_10_f_cp", "serie_id": "nasa_10_f_cp?freq=A&sector2=S12&sector=S14_S15&geo=FR", "candidat": "oui"},
    ])
    gardees, exclues = cat.separer_series_exclues(s)
    assert list(gardees["serie_id"].str.extract(r"[?&]sector=(\w+)")[0]) == ["S14_S15", "S1", "S13"]
    assert list(gardees["code_jeu"]) == ["nasa_10_f_bs", "nasa_10_nf_tr", "gov_10a_main"]
    assert len(exclues) == 3 and set(exclues["candidat"]) == {"non"}
    assert all(c.startswith("secteur_hors_menages : secteur S1") for c in exclues["commentaire"][:2])
    assert exclues["commentaire"].iloc[1].endswith(" ; note")
    assert exclues["commentaire"].iloc[2].startswith("secteur_hors_menages : secteur de contrepartie S12")
    # idempotent : une ligne déjà écartée garde son motif
    assert list(cat.separer_series_exclues(exclues)[1]["commentaire"]) == list(exclues["commentaire"])


def test_resynchronisation_et_derniere_verification():
    s = _series_df([
        {"code_jeu": "demo_pjan", "serie_id": "demo_pjan?a", "dimension_v0": "sante", "date_verification": "2026-10-13"},
        {"code_jeu": "ilc_li02", "serie_id": "ilc_li02?a", "dimension_v0": "niveau_de_vie", "date_verification": "2026-07-01"},
        {"code_jeu": "ilc_li02", "serie_id": "ilc_li02?b", "dimension_v0": "niveau_de_vie", "date_verification": "2026-07-01"},
        {"code_jeu": "ilc_li02", "serie_id": "ilc_li02?a", "dimension_v0": "niveau_de_vie", "date_verification": "2026-10-13"},
    ])
    jeux = pd.DataFrame({"code_jeu": ["demo_pjan", "ilc_li02"], "dimension_v0": ["contexte", "niveau_de_vie"], "theme_source": ["P", "R"]})
    assert cat.resynchroniser_series(s, jeux) == 4  # étiquette de demo_pjan et chemins
    assert s.loc[0, "dimension_v0"] == "contexte" and set(s["theme_source"]) == {"P", "R"}
    d = cat.garder_derniere_verification(s)
    assert list(d["serie_id"]) == ["demo_pjan?a", "ilc_li02?a"] and list(d["date_verification"]) == ["2026-10-13", "2026-10-13"]


def test_script_regles_catalogue_et_peremption(tmp_path, monkeypatch):
    script = _script()
    monkeypatch.setattr(script, "FICHIER_SERIES", tmp_path / "s.csv")
    monkeypatch.setattr(script, "FICHIER_SERIES_NON", tmp_path / "s_non.csv.gz")
    monkeypatch.setattr(script, "FICHIER_JEUX", tmp_path / "j.csv")
    _series_df([
        {"code_jeu": "nasa_10_f_bs", "serie_id": "nasa_10_f_bs?sector=S11&geo=FR", "type_ligne": "defaut", "candidat": "oui", "date_verification": "2026-10-13"},
        {"code_jeu": "nasa_10_f_bs", "serie_id": "nasa_10_f_bs?sector=S14&geo=FR", "type_ligne": "defaut", "candidat": "oui", "date_verification": "2026-10-13"},
        {"code_jeu": "bd_size", "serie_id": "bd_size?geo=FR", "type_ligne": "defaut", "candidat": "oui", "date_verification": "2026-10-13"},
    ]).to_csv(tmp_path / "s.csv", index=False)
    pd.DataFrame({"code_jeu": ["nasa_10_f_bs"], "dimension_v0": ["niveau_de_vie"], "theme_source": ["T"], "candidat": ["oui"],
                  "statut_niveau2": [""], "nb_series_fr": [""], "nb_series_candidates": [""], "structure_fr": [""]}).to_csv(tmp_path / "j.csv", index=False)
    etat = {"etapes": {"niveau2": {"version": 2, "termine": True, "regles": 6,
                                   "jeux": {"nasa_10_f_bs": {"statut": "ok", "date": "2026-10-13T15:00:00Z", "nb_series": 2}}}}}
    bilan = script._appliquer_regles_catalogue(etat)
    assert bilan["lignes"] == 1 and bilan["lignes_ecartees"] == 1  # bd_size retiré (plus suivi), S11 écarté
    non = pd.read_csv(tmp_path / "s_non.csv.gz", dtype=str, keep_default_na=False)
    assert list(non["serie_id"]) == ["nasa_10_f_bs?sector=S11&geo=FR"] and non["commentaire"][0].startswith("secteur_hors_menages")
    script.mettre_a_jour_catalogue_jeux(etat)
    assert pd.read_csv(tmp_path / "j.csv", dtype=str)["nb_series_fr"][0] == "1"
    # péremption : 90 jours pour le niveau 2, 30 jours pour le niveau 1
    suivi = {"a": {"statut": "ok", "date": "2020-01-01T00:00:00Z"}, "b": {"statut": "ok", "date": script.maintenant()},
             "c": {"statut": "erreur_donnees", "date": "2020-01-01T00:00:00Z"}}
    assert script.jeux_perimes(suivi) == ["a"]
    assert script.etape_a_faire({"etapes": {"niveau2": {"version": 2, "termine": True, "regles": 6, "jeux": suivi}}}, "niveau2")
    assert not script.etape_a_faire({"etapes": {"niveau2": {"version": 2, "termine": True, "regles": 6, "jeux": {"b": suivi["b"]}}}}, "niveau2")
    assert script.etape_a_faire({"etapes": {"niveau2": {"version": 2, "termine": True, "regles": 4, "jeux": {}}}}, "niveau2")
    assert script.etape_a_faire({"etapes": {"niveau1": {"version": script.ETAPES["niveau1"], "termine": True, "date": "2020-01-01T00:00:00Z"}}}, "niveau1")
    assert not script.etape_a_faire({"etapes": {"niveau1": {"version": script.ETAPES["niveau1"], "termine": True, "date": script.maintenant()}}}, "niveau1")
