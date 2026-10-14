"""Tests hors ligne du module Melodi (src/sources/insee_melodi.py) sur les fixtures de tests/fixtures/insee/melodi/."""

import io
import json
import zipfile
from pathlib import Path

import pytest

from src.sources import insee_melodi as mel
from src.sources.insee_http import ClientFixtures, Reponse

FIX = Path(__file__).parent / "fixtures" / "insee" / "melodi"


def fixture(motif: str) -> bytes:
    fichiers = sorted(FIX.glob(motif))
    assert fichiers, f"fixture introuvable : {motif}"
    return fichiers[-1].read_bytes()


def rep(contenu: bytes, statut: int = 200) -> Reponse:
    return Reponse(statut=statut, contenu=contenu, url="")


# --- catalogue ------------------------------------------------------------------------------

def test_analyser_catalogue_complet():
    jeux = mel.analyser_catalogue(fixture("melodi_catalog_all_*.json"))
    assert len(jeux) >= 96
    par_id = {j.id: j for j in jeux}
    cna = par_id["DD_CNA_AGREGATS"]
    assert cna.titre.startswith("Produit Intérieur Brut")
    assert cna.periodicite == "Annuel"
    assert cna.debut.startswith("1949") and cna.fin.startswith("2024")
    assert cna.niveaux_geo == ["NAT"] and cna.seulement_national
    produit = cna.produit_csv()
    assert produit and produit["accessURL"].startswith("https://api.insee.fr/melodi/file/DD_CNA_AGREGATS/")
    srcv = par_id["DS_SRCV_SATISFACTION"]
    assert srcv.niveau_national and srcv.seulement_national
    rp = par_id["DS_RP_LOGEMENT_PRINC"]
    assert rp.niveau_national and not rp.seulement_national


def test_analyser_catalogue_notice_unique():
    jeux = mel.analyser_catalogue(fixture("melodi_catalog_DS_EC_DECES_*.json"))
    assert [j.id for j in jeux] == ["DS_EC_DECES"]


def test_texte_formes_multiples():
    assert mel.texte([{"lang": "en", "content": "A"}, {"lang": "fr", "content": "B"}]) == "B"
    assert mel.texte({"fr": "C", "en": "D"}) == "C"
    assert mel.texte({"label": [{"lang": "fr", "content": "E"}]}) == "E"
    assert mel.texte(None) == ""


# --- plage (/range) --------------------------------------------------------------------------

def test_analyser_plage_et_geo_nationale():
    plage = mel.analyser_plage(fixture("melodi_range_DS_SUIVI_DDE_TOUR_*.json"))
    assert "TOUR_MEASURE" in plage
    assert plage["TOUR_MEASURE"].valeurs["DEPARTURE_TRAVEL_RATE"] == "Taux de départ en voyage"
    assert mel.valeurs_geo_nationales(plage) == [("FRANCE-FM", "France métropolitaine")]


@pytest.mark.parametrize(
    "type_code,libelle,attendu",
    [
        ("FRANCE", "France", True),
        ("NAT", "Niveau national", True),
        ("OTHER", "France hors Mayotte", True),
        ("OTHER", "France de province", False),
        ("OTHER", "France métropolitaine hors Île-de-France", False),
        ("DEP", "Ain", False),
        # essai du 13/10 : une commune (COM-47102) avait été prise pour un niveau national
        ("COM", "Franceville", False),
        ("OTHER", "Franceville", False),
        ("REG", "France entière", False),
        # passage du 14/10 : type FRANCE mais périmètre partiel (FRANCE-FM_X_R11)
        ("FRANCE", "France métropolitaine hors île de France", False),
        ("FRANCE", "France y compris les collectivités d'outre-mer", True),
    ],
)
def test_est_geo_nationale(type_code, libelle, attendu):
    assert mel.est_geo_nationale(type_code, libelle) is attendu


# --- données (/data) -------------------------------------------------------------------------

def test_observations_en_lignes_populations():
    corps = json.loads(fixture("melodi_data_DS_POPULATIONS_REFERENCE_COM-44109_*.json"))
    lignes = mel.observations_en_lignes("DS_POPULATIONS_REFERENCE", corps["observations"])
    assert len(lignes) == 3
    ids = {l.serie_id for l in lignes}
    assert "DS_POPULATIONS_REFERENCE?FREQ=A&GEO=COM-44109&POPREF_MEASURE=PMUN" in ids
    pmun = [l for l in lignes if l.serie_id.endswith("PMUN")][0]
    assert (pmun.geo, pmun.periode, pmun.valeur) == ("COM-44109", "2023", 327734.0)


def test_mesure_indice_de_prix_et_statut():
    corps = json.loads(fixture("melodi_data_DS_IPC_PRINC_*.json"))
    obs = corps["observations"][0]
    assert mel.mesure_et_valeur(obs) == ("OBS_VALUE_INDICE_DE_PRIX", 99.14)
    lignes = mel.observations_en_lignes("DS_IPC_PRINC", corps["observations"])
    assert lignes[0].statut == "A" and lignes[0].geo == "DEP-974"


def test_compter():
    client = ClientFixtures([(lambda u: "totalCount=TRUE" in u, rep(fixture("melodi_data_DS_POPULATIONS_REFERENCE_totalCount_*.json")))])
    assert mel.compter("DS_POPULATIONS_REFERENCE", None, client) == 106065
    assert "maxResult=0" in client.appels[0]


def test_jeu_inexistant_erreur_500():
    client = ClientFixtures([(lambda u: "DS_NEXISTEPAS" in u, rep(fixture("melodi_data_DS_NEXISTEPAS_*.txt"), 500))])
    with pytest.raises(mel.ErreurMelodi) as exc:
        mel.compter("DS_NEXISTEPAS", None, client)
    assert "500" in str(exc.value)


def test_obtenir_donnees_filtre_geo():
    donnees = fixture("melodi_data_DS_POPULATIONS_REFERENCE_COM-44109_*.json")
    corps = json.loads(donnees)
    compte = json.dumps({"observations": [], "paging": {"count": len(corps["observations"])}}).encode()
    client = ClientFixtures([
        (lambda u: "totalCount=TRUE" in u, rep(compte)),
        (lambda u: "GEO=COM-44109" in u, rep(donnees)),
    ])
    lignes = mel.obtenir_donnees("DS_POPULATIONS_REFERENCE", {"GEO": "COM-44109"}, client)
    assert len(lignes) == 3
    assert any("maxResult=100000" in u for u in client.appels)


def test_pagination_ignoree_est_signalee():
    """Le service renvoie la même page pour page=2 : l'extraction est marquée incomplète."""
    donnees = fixture("melodi_data_DS_POPULATIONS_REFERENCE_COM-44109_*.json")
    client = ClientFixtures([(lambda u: "/data/" in u, rep(donnees))])
    ext = mel.Extraction()
    obs = list(mel.iterer_observations("DS_POPULATIONS_REFERENCE", None, client, total=6, max_par_page=3, extraction=ext))
    assert len(obs) == 3
    assert ext.pages == 2 and not ext.complete
    assert "pagination" in ext.remarque


def test_identifiant_serie_et_url():
    sid = mel.identifiant_serie("DS_X", {"TIME_PERIOD": "2020", "GEO": "2025-FRANCE-F", "SEX": "_T"})
    assert sid == "DS_X?GEO=FRANCE-F&SEX=_T"
    assert mel.url_donnees("DS_X", {"GEO": "FRANCE-F"}) == "https://api.insee.fr/melodi/data/DS_X?GEO=FRANCE-F"


# --- fichier complet (ZIP de CSV) -----------------------------------------------------------

def test_lire_zip_csv_structure():
    """Structure du ZIP Melodi (`<jeu>_data.csv` + `<jeu>_metadata.csv`) ; contenu construit à partir
    des observations réelles de la fixture DS_POPULATIONS_REFERENCE (cas GEO_OBJECT communal ; le ZIP réel
    enregistré par le robot est testé plus bas, `test_fichier_zip_reel_…`)."""
    corps = json.loads(fixture("melodi_data_DS_POPULATIONS_REFERENCE_COM-44109_*.json"))
    lignes = ["GEO;GEO_OBJECT;FREQ;POPREF_MEASURE;TIME_PERIOD;OBS_VALUE"]
    for o in corps["observations"]:
        d = o["dimensions"]
        objet, code = d["GEO"].split("-", 2)[1:]
        lignes.append(f"{code};{objet};{d['FREQ']};{d['POPREF_MEASURE']};{d['TIME_PERIOD']};{o['measures']['OBS_VALUE_NIVEAU']['value']}")
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as z:
        z.writestr("DS_POPULATIONS_REFERENCE_data.csv", "\n".join(lignes))
        z.writestr("DS_POPULATIONS_REFERENCE_metadata.csv", "COD_VAR;LIB_VAR;COD_MOD;LIB_MOD\nPOPREF_MEASURE;Mesure;PMUN;Population municipale\n")
    colonnes, flux, libelles = mel.lire_zip_csv(tampon.getvalue())
    assert colonnes[0] == "GEO"
    observations = [mel.ligne_csv_en_observation(l) for l in flux]
    assert observations[0]["dimensions"]["GEO"] == "COM-44109"
    assert "GEO_OBJECT" not in observations[0]["dimensions"]
    assert libelles[("POPREF_MEASURE", "PMUN")] == "Population municipale"
    lignes_sortie = mel.observations_en_lignes("DS_POPULATIONS_REFERENCE", observations)
    assert {l.valeur for l in lignes_sortie} == {327734.0, 332515.0, 4781.0}


# --- réponses réelles enregistrées par le robot le 2026-10-13 (décision D21) --------------------

def test_catalogue_reel_octobre_2026():
    import gzip

    jeux = {j.id: j for j in mel.analyser_catalogue(gzip.decompress(fixture("melodi_catalog_all_2026-10-13.json.gz")))}
    assert len(jeux) == 145
    assert "DS_NAT_SDG" in jeux  # absent du catalogue de janvier 2026, cité par les pages ODD de mai 2026
    assert jeux["DS_SRCV_SATISFACTION"].niveau_national


def test_notice_reelle_srcv_satisfaction():
    jeu = mel.analyser_catalogue(fixture("melodi_catalog_DS_SRCV_SATISFACTION_*.json"))[0]
    assert (jeu.id, jeu.periodicite, jeu.debut[:4], jeu.niveaux_geo) == ("DS_SRCV_SATISFACTION", "Annuel", "2010", ["FRANCE"])
    assert "SRCV_MEASURE" in jeu.composants and "TIME_PERIOD" in jeu.composants
    assert jeu.produit_csv()["accessURL"].startswith("https://api.insee.fr/melodi/file/DS_SRCV_SATISFACTION/")


def test_plage_reelle_srcv_deux_niveaux_nationaux():
    plage = mel.analyser_plage(fixture("melodi_range_DS_SRCV_SATISFACTION_*.json"))
    assert mel.valeurs_geo_nationales(plage) == [("FRANCE-F_X_D976", "France hors Mayotte"), ("FRANCE-FM", "France métropolitaine")]
    assert plage["SRCV_MEASURE"].valeurs["TRAVSATISF"] == "Satisfaction moyenne concernant l'emploi principal"


def test_plage_reelle_odd_nationaux():
    plage = mel.analyser_plage(fixture("melodi_range_DS_NAT_SDG_*.json"))
    assert [c for c, _ in mel.valeurs_geo_nationales(plage)] == ["FRANCE-FM", "FRANCE-F", "FRANCE-F_X_D976"]
    assert plage["INDICATOR_SDG"].valeurs["3.i1a"] == "Espérance de vie en bonne santé"
    assert len(plage["INDICATOR_SDG"].valeurs) == 167


def test_comptage_et_donnees_reelles_srcv():
    assert json.loads(fixture("melodi_data_DS_SRCV_SATISFACTION_totalCount_*.json"))["paging"]["count"] == 8520
    client = ClientFixtures([(lambda u: "totalCount=TRUE" in u, rep(fixture("melodi_data_DS_SRCV_SATISFACTION_totalCount_*.json")))])
    assert mel.compter("DS_SRCV_SATISFACTION", None, client) == 8520
    corps = json.loads(fixture("melodi_data_DS_SRCV_SATISFACTION_extrait_*.json"))
    lignes = mel.observations_en_lignes("DS_SRCV_SATISFACTION", corps["observations"])
    assert len(lignes) == 40
    premiere = lignes[0]
    assert premiere.geo == "FRANCE-F_X_D976" and premiere.serie_id.startswith("DS_SRCV_SATISFACTION?AGE=")
    assert "GEO=FRANCE-F_X_D976" in premiere.serie_id and "TIME_PERIOD" not in premiere.serie_id


def test_fichier_zip_reel_et_api_donnent_le_meme_identifiant_de_serie():
    """Extraits réels (60 premières lignes) du ZIP de DS_SRCV_SATISFACTION : même identifiant de série que /data."""
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as z:
        z.writestr("DS_SRCV_SATISFACTION_2025_data.csv", fixture("melodi_file_DS_SRCV_SATISFACTION_*_data_extrait_*.csv"))
        z.writestr("DS_SRCV_SATISFACTION_2025_metadata.csv", fixture("melodi_file_DS_SRCV_SATISFACTION_*_metadata_extrait_*.csv"))
    colonnes, flux, libelles = mel.lire_zip_csv(tampon.getvalue())
    assert colonnes[:2] == ["GEO", "GEO_OBJECT"] and colonnes[-1] == "OBS_VALUE"
    assert libelles[("AGE", "Y25T34")] == "De 25 à 34 ans"
    observations = [mel.ligne_csv_en_observation(l) for l in flux]
    fichier = mel.observations_en_lignes("DS_SRCV_SATISFACTION", observations)
    api = mel.observations_en_lignes("DS_SRCV_SATISFACTION", json.loads(fixture("melodi_data_DS_SRCV_SATISFACTION_extrait_*.json"))["observations"])
    assert fichier[0].serie_id == api[0].serie_id
    assert (fichier[0].periode, fichier[0].valeur) == ("2022", 7.7)
