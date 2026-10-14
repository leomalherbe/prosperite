"""Tests hors ligne de scripts/preselection.py et scripts/verifier_fiches.py (mission M05).

Un mini-dépôt est construit dans un dossier temporaire (long-list, catalogue des jeux, règles, fiches) ;
un dernier test vérifie les fiches réelles de la dimension pilote liens_bien_etre.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parent.parent


def _charger(nom: str):
    spec = importlib.util.spec_from_file_location(nom, RACINE / "scripts" / f"{nom}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom] = module
    spec.loader.exec_module(module)
    return module


pre = _charger("preselection")
ver = _charger("verifier_fiches")

COLONNES_LONGLIST = ["ligne_id", "source", "serie_id", "libelle", "catalogue_origine", "eligible", "motif_exclusion"]


def _csv(chemin: Path, colonnes: list[str], lignes: list[list[str]]) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(colonnes)
        w.writerows(lignes)


def _fiche(**surcharges) -> dict:
    fiche = {
        "id": "indic_a", "libelle": "Indicateur A", "dimension": "dimtest", "sous_theme": "thème",
        "famille": "indic_a", "variante_principale": "oui", "definition": "Définition de A.", "unite": "%",
        "sens": "haut", "type": "resultat", "declaratif": "oui", "composite": "non", "source_organisme": "Eurostat",
        "source_jeu": "jeu_a", "source_serie_id": "jeu_a?geo=FR", "source_niveau": 1,
        "url_api": "https://exemple.org/a", "url_page": "non trouvé", "frequence": "annuelle",
        "premiere_annee": 2010, "derniere_annee": 2024, "nb_points_depuis_2000": 15, "geo": "FR",
        "eligibilite_longlist": "oui", "ligne_id": "l1", "hors_longlist": "non", "raccordement": "non",
        "incontournable": "non", "recommandation": "retenir",
        "motif_recommandation": "Série annuelle de 15 points couvrant 2010-2024.",
        "note_pertinence": "Première phrase de la note. Deuxième phrase de la note.",
        "variantes": [], "socle_v1": {"seuil_minimal": None, "objectif": None, "type_justification": None,
                                      "justification": ""},
        "qualite": [], "notes": "",
    }
    fiche.update(surcharges)
    return fiche


def _ecrire_fiche(racine: Path, fiche: dict) -> None:
    dossier = racine / "indicateurs" / fiche["dimension"]
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / f"{fiche['id']}.yaml").write_text(yaml.safe_dump(fiche, allow_unicode=True, sort_keys=False),
                                                 encoding="utf-8")


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    _csv(tmp_path / "catalogues" / "longlist_dimtest.csv", COLONNES_LONGLIST, [
        ["l1", "Eurostat", "jeu_a?geo=FR", "Indicateur A", "eurostat_series", "oui", ""],
        ["l2", "Eurostat", "jeu_a?sex=F&geo=FR", "Indicateur A — femmes", "eurostat_series", "oui", ""],
        ["l3", "Eurostat", "jeu_a?unk=1&geo=FR", "Indicateur A — inconnu", "eurostat_series", "oui", ""],
        ["l4", "INSEE BDM", "000000001", "Indicateur B", "insee_bdm", "a_verifier", "moins_de_10_points"],
    ])
    _csv(tmp_path / "catalogues" / "longlist_autre.csv", COLONNES_LONGLIST, [
        ["x1", "Eurostat", "jeu_a?age=Y16-24&geo=FR", "Indicateur A — jeunes", "eurostat_series", "oui", ""],
        ["x2", "Eurostat", "jeu_z?geo=FR", "Autre chose", "eurostat_series", "oui", ""],
    ])
    _csv(tmp_path / "catalogues" / "eurostat_jeux_catalogue.csv", ["code_jeu"], [["jeu_a"], ["jeu_h"]])
    _csv(tmp_path / "docs" / "validation" / "regles_preselection_dimtest.csv", pre.COLONNES_REGLES, [
        ["10", "indic_a", "fiche", "série principale", "Motif A.", "", "", "", r"^jeu_a\?geo=FR$", "", ""],
        ["20", "indic_a_inconnu", "ecarte_en_bloc", "", "Non-réponse.", "", "", "", r"unk=", "", ""],
        ["30", "indic_a_ventilations", "variante_de:indic_a", "ventilation", "Ventilations.", "", "", "",
         r"^jeu_a\?", "", ""],
        ["40", "indic_a_import", "variante_de:indic_a", "ventilation (autre long-list)", "Import.", "autre", "",
         "", r"^jeu_a\?", "", ""],
        ["50", "indic_b", "fiche", "série principale", "Motif B.", "", "^insee_bdm$", "", "", "Indicateur B", ""],
        ["60", "indic_h", "fiche", "série principale (hors long-list)", "Motif H.", "", "", "", "", "", "oui"],
    ])
    return tmp_path


def _fiches_valides(racine: Path) -> None:
    _ecrire_fiche(racine, _fiche())
    _ecrire_fiche(racine, _fiche(id="indic_b", famille="indic_b", source_organisme="INSEE", source_jeu="BDM",
                                 source_serie_id="000000001", ligne_id="l4", eligibilite_longlist="a_verifier",
                                 frequence="irreguliere"))
    _ecrire_fiche(racine, _fiche(id="indic_h", famille="indic_a", variante_principale="non",
                                 recommandation="retenir_variante", source_serie_id="jeu_h?geo=FR", ligne_id="",
                                 hors_longlist="oui", eligibilite_longlist="hors_longlist"))


def test_preselection_affecte_toutes_les_lignes(depot: Path):
    assert pre.main(["--dimension", "dimtest", "--racine", str(depot)]) == 0
    lignes = list(csv.DictReader((depot / "docs/validation/preselection_dimtest_lignes.csv").open(encoding="utf-8")))
    groupes = {l["ligne_id"]: l["groupe"] for l in lignes}
    assert groupes == {"l1": "indic_a", "l2": "indic_a_ventilations", "l3": "indic_a_inconnu", "l4": "indic_b",
                       "x1": "indic_a_import"}
    synthese = {r["groupe"]: r for r in csv.DictReader((depot / "docs/validation/preselection_dimtest.csv").open(encoding="utf-8"))}
    assert synthese["indic_h"]["nb_lignes"] == "0" and synthese["indic_b"]["nb_a_verifier"] == "1"


def test_preselection_signale_une_ligne_sans_regle(depot: Path):
    with (depot / "catalogues" / "longlist_dimtest.csv").open("a", encoding="utf-8") as f:
        f.write("l9,OCDE,orpheline,Ligne sans règle,autres_sources_m04,oui,\n")
    assert pre.main(["--dimension", "dimtest", "--racine", str(depot)]) == 1


def test_regles_invalides(depot: Path):
    chemin = depot / "docs/validation/regles_preselection_dimtest.csv"
    texte = chemin.read_text(encoding="utf-8").replace("variante_de:indic_a,ventilation,", "variante_de:inconnu,ventilation,")
    chemin.write_text(texte, encoding="utf-8")
    with pytest.raises(pre.ErreurRegles):
        pre.lire_regles(chemin)


def test_chaine_complete_sans_erreur(depot: Path):
    _fiches_valides(depot)
    assert pre.main(["--dimension", "dimtest", "--racine", str(depot), "--maj-fiches"]) == 0
    fiche_a = yaml.safe_load((depot / "indicateurs/dimtest/indic_a.yaml").read_text(encoding="utf-8"))
    assert {v["ligne_id"] for v in fiche_a["variantes"]} == {"l2", "x1"}
    assert [v.get("longlist") for v in fiche_a["variantes"]] == [None, "autre"]
    ver.ecrire_tableau(depot, "dimtest", [f for _, f in ver.lire_fiches(depot, "dimtest")])
    rapport = ver.verifier_dimension(depot, "dimtest")
    assert rapport.erreurs == []
    assert rapport.compteurs["retenir"] == 2 and rapport.compteurs["retenir_variante"] == 1
    assert rapport.compteurs["hors_longlist"] == 1 and rapport.compteurs["a_verifier"] == 1
    assert any("indic_h" in a for a in rapport.avertissements)


@pytest.mark.parametrize("surcharges, attendu", [
    ({"sens": "ambigu"}, "sens ambigu"),
    ({"motif_recommandation": "Première phrase. Seconde phrase."}, "une phrase"),
    ({"note_pertinence": "Une seule phrase."}, "de 2 à 4 phrases"),
    ({"socle_v1": {"seuil_minimal": 1.0}}, "vide"),
    ({"recommandation": "retenir_variante"}, "variante principale"),
    ({"source_serie_id": "absente?geo=FR"}, "absente des catalogues"),
    ({"type": "impact"}, "type ="),
    ({"url_page": "www.exemple.org"}, "URL"),
])
def test_erreurs_detectees(depot: Path, surcharges: dict, attendu: str):
    _fiches_valides(depot)
    pre.main(["--dimension", "dimtest", "--racine", str(depot), "--maj-fiches"])
    _ecrire_fiche(depot, {**yaml.safe_load((depot / "indicateurs/dimtest/indic_a.yaml").read_text(encoding="utf-8")),
                          **surcharges})
    rapport = ver.verifier_dimension(depot, "dimtest")
    assert any(attendu in e for e in rapport.erreurs), rapport.erreurs


def test_identifiant_en_double_entre_dimensions(depot: Path):
    _fiches_valides(depot)
    pre.main(["--dimension", "dimtest", "--racine", str(depot), "--maj-fiches"])
    _ecrire_fiche(depot, _fiche(dimension="autre"))
    rapport = ver.verifier_dimension(depot, "dimtest", catalogues=False)
    assert any("présent 2 fois" in e for e in rapport.erreurs)


def test_variantes_desynchronisees(depot: Path):
    _fiches_valides(depot)
    pre.main(["--dimension", "dimtest", "--racine", str(depot)])  # sans --maj-fiches
    rapport = ver.verifier_dimension(depot, "dimtest")
    assert any("--maj-fiches" in e for e in rapport.erreurs)


def test_tableau_conserve_les_decisions_de_leo(depot: Path):
    _fiches_valides(depot)
    pre.main(["--dimension", "dimtest", "--racine", str(depot), "--maj-fiches"])
    fiches = [f for _, f in ver.lire_fiches(depot, "dimtest")]
    chemin = ver.ecrire_tableau(depot, "dimtest", fiches)
    texte = chemin.read_text(encoding="utf-8").splitlines()
    entete, lignes = texte[0], texte[1:]
    lignes = [l[:-2] + ",retenu_socle,ok" if l.startswith("indic_a,") else l for l in lignes]
    chemin.write_text("\n".join([entete, *lignes]) + "\n", encoding="utf-8")
    ver.ecrire_tableau(depot, "dimtest", fiches)
    relu = {r["id"]: r for r in csv.DictReader(chemin.open(encoding="utf-8"))}
    assert relu["indic_a"]["decision_leo"] == "retenu_socle" and relu["indic_a"]["commentaire_leo"] == "ok"
    assert ver.verifier_dimension(depot, "dimtest").erreurs == []
    chemin.write_text(chemin.read_text(encoding="utf-8").replace("retenu_socle", "peut-être"), encoding="utf-8")
    assert any("decision_leo" in e for e in ver.verifier_dimension(depot, "dimtest").erreurs)


def test_identifiants_numeriques_entre_guillemets():
    texte = pre.texte_yaml({"serie_id": "010593281", "autre": "001755278", "mot": "oui", "annee": 2010})
    assert "serie_id: '010593281'" in texte and "autre: '001755278'" in texte
    assert "mot: oui" in texte and "annee: 2010" in texte
    assert yaml.safe_load(texte)["serie_id"] == "010593281"


def test_nb_phrases():
    assert ver.nb_phrases("Indicateur de richesse nationale n° 5, série 2010-2025.") == 1
    assert ver.nb_phrases("Une phrase (D17). Une autre « citée ».") == 2
    assert ver.premiere_phrase("Première. Seconde.") == "Première."


@pytest.mark.skipif(not (RACINE / "indicateurs" / "liens_bien_etre").exists(), reason="fiches pilotes absentes")
def test_fiches_reelles_liens_bien_etre():
    rapport = ver.verifier_dimension(RACINE, "liens_bien_etre")
    assert rapport.erreurs == [], rapport.erreurs
    assert rapport.compteurs["fiches"] >= 1
