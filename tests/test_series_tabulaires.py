"""Tests hors ligne de l'inventaire des séries (mission M04, phase 2)."""

import io
import json
import zipfile

import openpyxl
import pandas as pd

from src.sources import series_tabulaires as st


def test_parametres():
    assert st.parametres("series;cles=A|B;temps=T;filtre=code=FRA") == (
        "series", {"cles": "A|B", "temps": "T", "filtre": "code=FRA"})
    assert st.parametres("") == ("", {})


def test_encodage_et_periodes():
    assert st.detecter_encodage("Sécurité".encode("utf-8")) == "utf-8-sig"
    assert st.detecter_encodage("Sécurité intérieure".encode("cp1252")) == "cp1252"
    assert st.compresser_periodes(["2000", "2001", "2002", "2005", "2007", "2008"]) == "2000-2002,2005,2007-2008"
    assert st.compresser_periodes(["2020-Q1", "2020-Q2"]) == "2020-Q1,2020-Q2"


def test_series_sdmx_avec_libelles():
    csv = ("STRUCTURE,STRUCTURE_ID,ACTION,REF_AREA,Reference area,MEASURE,Measure,UNIT_MEASURE,Unit of measure,"
           "TIME_PERIOD,Time period,OBS_VALUE\n"
           "DATAFLOW,X,I,FRA,France,10_2,Feeling safe at night,PT,Percentage,2022,,74.1\n"
           "DATAFLOW,X,I,FRA,France,10_2,Feeling safe at night,PT,Percentage,2023,,72.0\n"
           "DATAFLOW,X,I,FRA,France,7_1,Social support,PT,Percentage,2023,,87.6\n")
    df = pd.read_csv(io.StringIO(csv), dtype=str)
    lignes = st.resumer_series(df, {"cles": "MEASURE", "temps": "TIME_PERIOD", "valeurs": "OBS_VALUE"}, "ocde", "t")
    par_id = {l["serie_id"]: l for l in lignes}
    assert par_id["10_2"]["libelle"] == "Feeling safe at night"
    assert par_id["10_2"]["unite"] == "Percentage"
    assert par_id["10_2"]["periodes"] == "2022-2023"
    assert par_id["10_2"]["derniere_valeur"] == "72"
    assert par_id["7_1"]["n_periodes"] == 1


def test_series_detection_et_filtre_owid():
    csv = "entity,code,year,civ_libs,owid_region\nFrance,FRA,2000,0.9,Europe\nFrance,FRA,2001,0.91,Europe\nItaly,ITA,2001,0.8,Europe\n"
    df = pd.read_csv(io.StringIO(csv), dtype=str)
    lignes = st.resumer_series(df, {"filtre": "code=FRA", "temps": "year", "cles": "code"}, "owid", "x")
    assert len(lignes) == 1
    assert lignes[0]["serie_id"] == "FRA"
    assert lignes[0]["libelle"] == "civ_libs"
    assert lignes[0]["premiere_periode"] == "2000" and lignes[0]["derniere_valeur"] == "0.91"


def test_series_somme_et_virgule_decimale():
    csv = "secteur;substance;annee;emission\nA;CO2;2000;1,5\nB;CO2;2000;2,5\nA;CO2;2001;1\n"
    df = pd.read_csv(io.StringIO(csv), sep=";", dtype=str)
    lignes = st.resumer_series(df, {"cles": "substance", "temps": "annee", "valeurs": "emission", "agg": "somme"})
    assert lignes[0]["derniere_valeur"] == "1"
    assert lignes[0]["n_valeurs_distinctes"] == 2


def test_large():
    csv = "CODGEO;VARIABLE;LIBELLE_VARIABLE;A2001;A2000;A1999\nFR;tx_homicides;Taux d'homicides;1,2;;1,0\n"
    df = pd.read_csv(io.StringIO(csv), sep=";", dtype=str)
    lignes = st.resumer_large(df, {"cles": "CODGEO|VARIABLE", "libelle": "LIBELLE_VARIABLE"})
    assert lignes[0]["serie_id"] == "FR.tx_homicides"
    assert lignes[0]["periodes"] == "1999,2001"
    pnud = pd.DataFrame({"iso3": ["FRA"], "hdi_2000": ["0.85"], "hdi_2001": ["0.86"], "le_2001": ["79"]})
    l2 = st.resumer_large(pnud, {"filtre": "iso3=FRA", "cles": "iso3", "motif_colonne": r"^(.+)_(\d{4})$"})
    assert {l["serie_id"] for l in l2} == {"FRA#hdi", "FRA#le"}


def test_couverture(tmp_path):
    f = tmp_path / "micro.csv"
    f.write_text("ident;annee;og01;og02\n1;2000;3;\n2;2000;1;\n3;2001;;2\n", encoding="utf-8")
    lignes = {l["variable"]: l for l in st.couverture_microdonnees(f, {"annee": "annee"})}
    assert lignes["og01"]["annees"] == "2000"
    assert lignes["og02"]["annees"] == "2001"
    assert lignes["__effectifs__"]["annees"] == "2000:2 2001:1"


def test_lignes_csv_et_classeur_dans_zip():
    contenu = "pays;score\nFinlande;86\nFrance;76,7\n".encode("cp1252")
    texte = st.lignes_correspondantes(contenu, "France")
    assert "France;76,7" in texte
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Country", "1990", "2024"])
    for i in range(20):
        ws.append([f"Pays{i}", 1, 2])
    ws.append(["France", 10.5, 4.0])
    t = io.BytesIO()
    wb.save(t)
    z = io.BytesIO()
    with zipfile.ZipFile(z, "w") as arch:
        arch.writestr("donnees.xlsx", t.getvalue())
    texte = st.lignes_correspondantes(z.getvalue(), "^France$")
    assert "France | 10.5 | 4" in texte


def test_catalogues_ods_dido_bm():
    ods = [{"dataset_id": "suicides-deces-france", "metas": {"default": {"title": "Suicides", "records_count": 135}},
            "fields": [{"name": "annee", "type": "text"}, {"name": "taux_standardise", "type": "double"}]}]
    l = st.catalogue_ods(json.dumps(ods).encode())
    assert l[0]["champs"] == "annee(text) ; taux_standardise(double)"
    dido = {"total": 1, "data": [{"id": "j1", "title": "Air", "datafiles": [{"rid": "r1", "title": "PM2,5"}]}]}
    assert st.catalogue_dido(json.dumps(dido).encode())[0]["rid"] == "r1"
    bm = [{"page": 1}, [{"indicator": {"id": "GOV_WGI_VA.SC", "value": "Voice"}, "date": "2024", "value": 85.1},
                        {"indicator": {"id": "GOV_WGI_VA.SC", "value": "Voice"}, "date": "2023", "value": None}]]
    s = st.series_banque_mondiale(json.dumps(bm).encode())
    assert s[0]["periodes"] == "2024" and s[0]["derniere_valeur"] == "85.1"


def test_agregat(tmp_path):
    f = tmp_path / "elections.csv"
    f.write_text("id_election;code_bv;inscrits;votants\n2022_pres_t1;1;100;80\n2022_pres_t1;2;100;70\n2024_euro_t1;1;50;25\n",
                 encoding="utf-8")
    lignes = {l["id_election"]: l for l in st.agreger(f, {"cle": "id_election", "sommes": "inscrits|votants",
                                                           "ratio": "votants/inscrits"})}
    assert lignes["2022_pres_t1"]["inscrits"] == 200
    assert lignes["2022_pres_t1"]["ratio_votants_inscrits"] == "75.00"
    assert lignes["2024_euro_t1"]["n_lignes"] == 1


def test_agregat_cle_multiple_et_manquants(tmp_path):
    f = tmp_path / "elections.csv"
    f.write_text("id_election;code_departement;inscrits;votants\n"
                 "2002_pres_t1;01;100;80\n2002_pres_t1;01;100;\n2002_pres_t1;ZZ;50;20\n2002_pres_t1;;10;5\n"
                 "2012_pres_t1;01;100;70\n", encoding="utf-8")
    lignes = st.agreger(f, {"cle": "id_election|code_departement", "sommes": "inscrits|votants",
                            "ratio": "votants/inscrits", "manquants": "oui"}, taille_morceau=2)
    par_cle = {(l["id_election"], l["code_departement"]): l for l in lignes}
    assert set(par_cle) == {("2002_pres_t1", "01"), ("2002_pres_t1", "ZZ"), ("2002_pres_t1", ""),
                            ("2012_pres_t1", "01")}
    l01 = par_cle[("2002_pres_t1", "01")]
    assert (l01["n_lignes"], l01["inscrits"], l01["votants"], l01["manquants_votants"]) == (2, 200, 80, 1)
    assert l01["ratio_votants_inscrits"] == "40.00"
    assert par_cle[("2002_pres_t1", "")]["inscrits"] == 10
    assert list(lignes[0])[:3] == ["id_election", "code_departement", "n_lignes"]


def test_colonne_correspondante():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "WJP 2021"
    ws.append(["Country", "Finland", "France"])
    ws.append(["Country Code", "FIN", "FRA"])
    ws.append(["WJP Rule of Law Index: Overall Score", 0.88, 0.72])
    t = io.BytesIO()
    wb.save(t)
    texte = st.colonne_correspondante(t.getvalue(), "^France$")
    assert "colonne 2" in texte
    assert "WJP Rule of Law Index: Overall Score | 0.72" in texte


def test_distribution_ponderee(tmp_path):
    f = tmp_path / "micro.csv"
    f.write_text("ident;annee;poids;og01;sdsexe\n1;2000;1;1;1\n2;2000;3;2;2\n3;2001;1;2;1\n4;2001;1;;2\n",
                 encoding="utf-8")
    lignes = st.distribution_ponderee(f, {"annee": "annee", "poids": "poids", "variables": "og.*"})
    parts = {(l["variable"], l["annee"], l["modalite"]): l["part_ponderee"] for l in lignes}
    assert parts[("og01", "2000", "1")] == "25.00"
    assert parts[("og01", "2000", "2")] == "75.00"
    assert parts[("og01", "2001", "2")] == "100.00"
    assert not any(v == "sdsexe" for v, _, _ in parts)


def _pdf_minimal(lignes: list[str]) -> bytes:
    """PDF d'une page, police Helvetica, une ligne de texte par élément (construit à la main)."""
    flux = "BT /F1 12 Tf 14 TL 72 720 Td " + " ".join(f"({l}) Tj T*" for l in lignes) + " ET"
    objets = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        "/Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(flux)} >>\nstream\n{flux}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    sortie, positions = "%PDF-1.4\n", []
    for i, o in enumerate(objets, 1):
        positions.append(len(sortie))
        sortie += f"{i} 0 obj\n{o}\nendobj\n"
    debut_xref = len(sortie)
    sortie += f"xref\n0 {len(objets) + 1}\n0000000000 65535 f \n"
    sortie += "".join(f"{p:010d} 00000 n \n" for p in positions)
    sortie += f"trailer\n<< /Size {len(objets) + 1} /Root 1 0 R >>\nstartxref\n{debut_xref}\n%%EOF\n"
    return sortie.encode("latin-1")


def test_lignes_pdf():
    contenu = _pdf_minimal(["Social support", "Source: Gallup World Poll", "Unit: percentage"])
    texte = st.lignes_pdf(contenu, "(?i)gallup", contexte=1)
    assert "Pages : 1" in texte
    assert "Social support / Source: Gallup World Poll / Unit: percentage" in texte
    assert "1 lignes correspondantes" in texte
