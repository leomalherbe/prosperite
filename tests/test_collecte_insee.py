"""Essai hors ligne de bout en bout de scripts/collecte_insee.py avec un faux client servant les fixtures.

Vérifie l'enchaînement des étapes, la reprise après un arrêt pour budget, l'écriture des inventaires,
des catalogues, des bilans, de la comparaison avec la phase 1 et des échantillons. Les réponses ne
sont pas cohérentes entre elles (ce sont des fixtures de requêtes différentes) : seul le circuit est testé.
"""

import csv
import gzip
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from src.sources.insee_http import ClientFixtures, Reponse

RACINE = Path(__file__).resolve().parent.parent
FIX = Path(__file__).parent / "fixtures" / "insee"


def charger_script():
    spec = importlib.util.spec_from_file_location("collecte_insee", RACINE / "scripts" / "collecte_insee.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def f(motif: str) -> bytes:
    return sorted(FIX.glob(motif))[-1].read_bytes()


def faux_client() -> ClientFixtures:
    compte = json.dumps({"observations": [], "paging": {"count": 3}}).encode()
    routes = [
        (lambda u: u.endswith("/series/sdmx/dataflow"), Reponse(200, f("bdm/bdm_dataflow_ODD-*.xml"), "")),
        (lambda u: "/codelist/FR1/" in u, Reponse(200, f("bdm/bdm_codelist_CL_PERIODICITE_*.xml"), "")),
        (lambda u: "/data/ODD-ERADICATION-PAUVRETE?detail=nodata" in u, Reponse(200, f("bdm/bdm_serie_010593281_*.xml"), "")),
        (lambda u: "/data/SERIES_BDM/" in u, Reponse(200, f("bdm/bdm_serie_010593281_*.xml"), "")),
        (lambda u: u.endswith("/melodi/catalog/all"), Reponse(200, f("melodi/melodi_catalog_all_*.json"), "")),
        (lambda u: "/melodi/range/" in u, Reponse(200, f("melodi/melodi_range_DS_SUIVI_DDE_TOUR_*.json"), "")),
        (lambda u: "/melodi/data/" in u and "totalCount=TRUE" in u, Reponse(200, compte, "")),
        (lambda u: "/melodi/data/" in u, Reponse(200, f("melodi/melodi_data_DS_POPULATIONS_REFERENCE_COM-*.json"), "")),
    ]
    return ClientFixtures(routes)


@pytest.fixture()
def script(tmp_path, monkeypatch):
    m = charger_script()
    cats = tmp_path / "catalogues"
    monkeypatch.setattr(m, "CATALOGUES", cats)
    monkeypatch.setattr(m, "ETAT_DIR", cats / "insee_etat")
    monkeypatch.setattr(m, "ECHANTILLONS", tmp_path / "echantillons")
    for nom in ("INVENTAIRE_BDM", "INVENTAIRE_MELODI", "CATALOGUE_BDM", "CATALOGUE_MELODI", "FLUX_CSV", "JEUX_CSV", "ZONES_CSV", "COMPARAISON_CSV", "BILAN_JSON"):
        monkeypatch.setattr(m, nom, cats / getattr(m, nom).name)
    client = faux_client()
    monkeypatch.setattr(m, "ClientHttp", lambda *a, **k: client)
    m.RACINE = tmp_path  # chemins relatifs des journaux
    return m


def lancer(m, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["collecte_insee.py", *args])
    return m.main()


def test_collecte_complete_puis_catalogage(script, monkeypatch, tmp_path):
    m = script
    # 1er passage : budget nul → arrêt propre après la liste des dataflows
    assert lancer(m, monkeypatch, "--budget-minutes", "0", "--max-jeux", "2") == 0
    etat = json.loads((tmp_path / "catalogues" / "insee_etat" / "etat.json").read_text())
    assert etat["etapes_terminees"] == ["bdm_flux", "echantillons"] and not etat["termine"]
    assert "budget" in etat["passages"][-1]["issue"]

    # 2e passage : reprise et fin du cycle
    assert lancer(m, monkeypatch, "--max-jeux", "2") == 0
    etat = json.loads((tmp_path / "catalogues" / "insee_etat" / "etat.json").read_text())
    assert etat["termine"] and len(etat["passages"]) == 2
    assert not (tmp_path / "catalogues" / "insee_etat" / "bdm_series.jsonl.gz").exists()

    inventaire = list(csv.DictReader(gzip.open(tmp_path / "catalogues" / "insee_bdm_inventaire.csv.gz", "rt", encoding="utf-8")))
    assert [l["idbank"] for l in inventaire] == ["010593281"]
    assert (inventaire[0]["premiere_periode"], inventaire[0]["derniere_periode"]) == ("2010", "2024")

    catalogue = list(csv.DictReader(open(tmp_path / "catalogues" / "insee_bdm_catalogue.csv", encoding="utf-8")))
    assert len(catalogue) == 1
    ligne = catalogue[0]
    assert (ligne["serie_id"], ligne["geo"], ligne["frequence"]) == ("010593281", "FM", "annuelle")
    assert (ligne["dimension_v0"], ligne["candidat"]) == ("liens_bien_etre", "oui")
    assert list(ligne)[:13] == ["source", "serie_id", "libelle", "unite", "frequence", "geo", "premiere_periode", "derniere_periode",
                                "derniere_maj", "theme_source", "dimension_v0", "candidat", "commentaire"]

    melodi = list(csv.DictReader(open(tmp_path / "catalogues" / "insee_melodi_catalogue.csv", encoding="utf-8")))
    assert melodi and all(r["serie_id"].startswith(("DD_CNA_AGREGATS?", "DD_CNA_APU?")) for r in melodi)
    jeux = list(csv.DictReader(open(tmp_path / "catalogues" / "insee_melodi_jeux.csv", encoding="utf-8")))
    assert {j["statut"] for j in jeux} >= {"traité", "non traité"}

    bilan = json.loads((tmp_path / "catalogues" / "insee_bilan.json").read_text())
    assert bilan["bdm"]["catalogue"] == 1 and bilan["comparaison_phase1"]["phase1"] == 1063
    comparaison = list(csv.DictReader(open(tmp_path / "catalogues" / "insee_comparaison_phase1.csv", encoding="utf-8")))
    assert len(comparaison) == 1063
    assert any(r["serie_id"] == "010593281" and r["statut_robot"] == "confirmee" for r in comparaison)

    echantillons = {p.name for p in (tmp_path / "echantillons").iterdir()}
    assert "provenance.csv" in echantillons
    assert any(n.startswith("bdm_dataflows_") for n in echantillons)

    # 3e passage hors ligne : catalogage seul depuis les inventaires
    assert lancer(m, monkeypatch, "--catalogage-seul") == 0
    assert len(list(csv.DictReader(open(tmp_path / "catalogues" / "insee_bdm_catalogue.csv", encoding="utf-8")))) == 1
