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
        "incontournable": "non", "socle_propose": "non", "recommandation": "retenir",
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
    ({"raccordement": "possible"}, "format « oui|non|a_etudier"),
    ({"raccordement": "a_etudier"}, "note courte obligatoire"),
])
def test_erreurs_detectees(depot: Path, surcharges: dict, attendu: str):
    _fiches_valides(depot)
    pre.main(["--dimension", "dimtest", "--racine", str(depot), "--maj-fiches"])
    _ecrire_fiche(depot, {**yaml.safe_load((depot / "indicateurs/dimtest/indic_a.yaml").read_text(encoding="utf-8")),
                          **surcharges})
    rapport = ver.verifier_dimension(depot, "dimtest")
    assert any(attendu in e for e in rapport.erreurs), rapport.erreurs


def test_borne_premiere_annee_1700():
    assert ver._controle_valeur("premiere_annee", "annee", 1750) is None          # V-Dem (D32)
    assert ver._controle_valeur("premiere_annee", "annee", 1650) is not None


def test_hors_longlist_avec_preuve(depot: Path):
    _fiches_valides(depot)
    pre.main(["--dimension", "dimtest", "--racine", str(depot), "--maj-fiches"])
    preuve = depot / "docs" / "sources" / "series" / "sortie_robot.csv"
    preuve.parent.mkdir(parents=True, exist_ok=True)
    preuve.write_text("variable,annee\nq1,2020\n", encoding="utf-8")
    fiche_h = yaml.safe_load((depot / "indicateurs/dimtest/indic_h.yaml").read_text(encoding="utf-8"))
    fiche_h.update({"source_serie_id": "baromètre, variable Q1", "preuve": "docs/sources/series/sortie_robot.csv",
                    "statut_serie": "a_calculer"})
    _ecrire_fiche(depot, fiche_h)
    rapport = ver.verifier_dimension(depot, "dimtest")
    assert rapport.erreurs == [] and any("valeurs à calculer" in a for a in rapport.avertissements)
    fiche_h["preuve"] = "docs/sources/series/absente.csv"
    _ecrire_fiche(depot, fiche_h)
    assert any("absente des catalogues" in e for e in ver.verifier_dimension(depot, "dimtest").erreurs)


def test_composantes_modalites_d_un_paquet(depot: Path):
    """Écart construit (D34) : chaque composante peut être une modalité d'un paquet catalogué."""
    _csv(depot / "catalogues" / "longlist_paquets.csv", COLONNES_LONGLIST, [
        ["p1", "Eurostat", "jeu_p?age=Y15-74&sex=M&sex=F&geo=FR", "Paquet par sexe", "eurostat_series", "oui", ""],
    ])
    paquets = ver.index_paquets({"jeu_p?age=Y15-74&sex=M&sex=F&geo=FR", "jeu_a?geo=FR"})
    assert ver.selection_de_paquet("jeu_p?age=Y15-74&sex=F&geo=FR", paquets)
    assert not ver.selection_de_paquet("jeu_p?age=Y15-74&sex=T&geo=FR", paquets)     # modalité absente
    assert not ver.selection_de_paquet("jeu_p?age=Y15-74&sex=F", paquets)            # clé manquante
    assert not ver.selection_de_paquet("jeu_p?age=Y15-74&sex=F&sex=M&geo=FR", paquets)
    _fiches_valides(depot)
    pre.main(["--dimension", "dimtest", "--racine", str(depot), "--maj-fiches"])
    fiche_a = yaml.safe_load((depot / "indicateurs/dimtest/indic_a.yaml").read_text(encoding="utf-8"))
    fiche_a.update({"composantes": ["jeu_p?age=Y15-74&sex=F&geo=FR", "jeu_p?age=Y15-74&sex=M&geo=FR"],
                    "formule": "abs(A - B)", "annee_reference": "observation"})
    _ecrire_fiche(depot, fiche_a)
    rapport = ver.verifier_dimension(depot, "dimtest")
    assert rapport.erreurs == [] and not any("hors schéma" in a for a in rapport.avertissements)
    fiche_a["composantes"] = ["jeu_p?age=Y15-74&sex=T&geo=FR"]
    _ecrire_fiche(depot, fiche_a)
    assert any("absente des catalogues" in e for e in ver.verifier_dimension(depot, "dimtest").erreurs)


def test_ligne_deja_prise_par_une_autre_dimension(depot: Path):
    _fiches_valides(depot)
    pre.main(["--dimension", "dimtest", "--racine", str(depot), "--maj-fiches"])
    _csv(depot / "docs/validation/preselection_autre_lignes.csv", pre.COLONNES_LIGNES,
         [["l2", "dimtest", "indic_femmes", "fiche", "indic_femmes", "série principale", "jeu_a?sex=F&geo=FR",
           "Eurostat", "eurostat_series", "Indicateur A — femmes", "oui", "", "10"]])
    rapport = ver.verifier_dimension(depot, "dimtest")
    assert rapport.erreurs == [] and rapport.compteurs["lignes_prises_ailleurs"] == 1
    assert any("déjà série principale de autre/indic_femmes" in a for a in rapport.avertissements)


def test_raccordement_formats_admis():
    for valeur in ("non", "non : rien avant 2010", "oui : série X raccordée en 2010", "a_etudier : série Y à comparer"):
        assert ver._controle_valeur("raccordement", "raccordement", valeur) is None, valeur


def test_decision_autre_dimension(depot: Path):
    chemin = depot / "docs/validation/regles_preselection_dimtest.csv"
    with chemin.open("a", encoding="utf-8") as f:
        f.write("15,indic_a_inconnu_ailleurs,autre_dimension:sante,,Relève de la santé.,,,,unk=,,\n")
    regles = pre.lire_regles(chemin, "dimtest", {"dimtest", "sante"})
    assert any(r["decision"] == "autre_dimension:sante" for r in regles)
    assert pre.main(["--dimension", "dimtest", "--racine", str(depot)]) == 0
    lignes = {l["ligne_id"]: l for l in csv.DictReader((depot / "docs/validation/preselection_dimtest_lignes.csv").open(encoding="utf-8"))}
    assert lignes["l3"]["decision"] == "autre_dimension:sante" and lignes["l3"]["fiche"] == ""
    with pytest.raises(pre.ErreurRegles):
        pre.lire_regles(chemin, "dimtest", {"dimtest"})        # dimension inconnue
    with pytest.raises(pre.ErreurRegles):
        pre.lire_regles(chemin, "sante", {"dimtest", "sante"})  # renvoi vers la dimension traitée


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


def _depot_pret(depot: Path) -> None:
    _fiches_valides(depot)
    pre.main(["--dimension", "dimtest", "--racine", str(depot), "--maj-fiches"])


@pytest.mark.parametrize("surcharges, attendu", [
    ({"socle_propose": None}, "socle_propose obligatoire"),
    ({"incontournable": "oui"}, "socle_propose: oui attendu"),
    ({"recommandation": "ecarter", "socle_propose": "oui"}, "exige la recommandation"),
])
def test_socle_propose_erreurs(depot: Path, surcharges: dict, attendu: str):
    """D41 : socle_propose obligatoire sur une principale, imposé aux incontournables, réservé aux « retenir »."""
    _depot_pret(depot)
    fiche = {**yaml.safe_load((depot / "indicateurs/dimtest/indic_a.yaml").read_text(encoding="utf-8")), **surcharges}
    fiche = {k: v for k, v in fiche.items() if v is not None}
    _ecrire_fiche(depot, fiche)
    rapport = ver.verifier_dimension(depot, "dimtest", catalogues=False)
    assert any(attendu in e for e in rapport.erreurs), rapport.erreurs


def test_socle_propose_valide_et_compte(depot: Path):
    _depot_pret(depot)
    fiche = yaml.safe_load((depot / "indicateurs/dimtest/indic_a.yaml").read_text(encoding="utf-8"))
    _ecrire_fiche(depot, {**fiche, "socle_propose": "oui", "incontournable": "oui"})
    rapport = ver.verifier_dimension(depot, "dimtest", catalogues=False)
    assert not [e for e in rapport.erreurs if "socle" in e]
    assert rapport.compteurs["socle_propose"] == ["indic_a"]
    # oui sur une fiche non principale : refusé
    fiche_h = yaml.safe_load((depot / "indicateurs/dimtest/indic_h.yaml").read_text(encoding="utf-8"))
    _ecrire_fiche(depot, {**fiche_h, "socle_propose": "oui"})
    assert any("réservé aux variantes principales" in e for e in ver.verifier_dimension(depot, "dimtest").erreurs)


def test_socle_propose_plafond_de_8(depot: Path):
    _depot_pret(depot)
    for i in range(9):
        _ecrire_fiche(depot, _fiche(id=f"socle_{i}", famille=f"socle_{i}", socle_propose="oui", ligne_id=""))
    rapport = ver.verifier_dimension(depot, "dimtest", catalogues=False)
    assert any("9 fiches socle_propose: oui (8 au plus" in e for e in rapport.erreurs)


def test_socle_transitoire_et_incontournable_non_principal(tmp_path: Path):
    """Dimension encore en correction (D41) : absence du champ = avertissement ; D38 d : avertissement."""
    fiche = _fiche(dimension="sante", incontournable="oui")
    del fiche["socle_propose"]
    _ecrire_fiche(tmp_path, fiche)
    variante = _fiche(id="indic_v", dimension="sante", variante_principale="non", recommandation="retenir_variante",
                      incontournable="oui")
    del variante["socle_propose"]
    _ecrire_fiche(tmp_path, variante)
    rapport = ver.verifier_dimension(tmp_path, "sante", catalogues=False)
    assert not [e for e in rapport.erreurs if "socle" in e], rapport.erreurs
    assert any("socle_propose absent" in a for a in rapport.avertissements)
    assert any("indic_v" in a and "D38 d" in a for a in rapport.avertissements)
    # même situation dans une dimension corrigée : erreurs
    _ecrire_fiche(tmp_path, {**fiche, "dimension": "travail"})
    assert any("socle_propose" in e for e in ver.verifier_dimension(tmp_path, "travail", catalogues=False).erreurs)


def test_tableau_ancien_format_admis_en_transition(tmp_path: Path):
    fiche = _fiche(dimension="sante")
    del fiche["socle_propose"]
    _ecrire_fiche(tmp_path, fiche)
    chemin = tmp_path / "docs" / "validation" / "validation_sante.csv"
    ligne = ver.ligne_tableau(fiche)
    _csv(chemin, ver.COLONNES_TABLEAU_V12, [[str(ligne[c] if ligne[c] is not None else "") for c in ver.COLONNES_TABLEAU_V12]])
    rapport = ver.verifier_dimension(tmp_path, "sante", catalogues=False)
    assert not [e for e in rapport.erreurs if "tableau" in e], rapport.erreurs
    assert any("format antérieur" in a for a in rapport.avertissements)
    chemin_t = tmp_path / "docs" / "validation" / "validation_travail.csv"
    _ecrire_fiche(tmp_path, {**fiche, "dimension": "travail", "socle_propose": "non"})
    _csv(chemin_t, ver.COLONNES_TABLEAU_V12, [[str(ligne[c] if ligne[c] is not None else "") for c in ver.COLONNES_TABLEAU_V12]])
    assert any("colonnes inattendues" in e for e in ver.verifier_dimension(tmp_path, "travail", catalogues=False).erreurs)


def test_tableau_porte_sous_theme_et_socle(depot: Path):
    _depot_pret(depot)
    chemin = ver.ecrire_tableau(depot, "dimtest", [f for _, f in ver.lire_fiches(depot, "dimtest")])
    relu = {r["id"]: r for r in csv.DictReader(chemin.open(encoding="utf-8"))}
    assert list(next(iter(relu.values()))) == ver.COLONNES_TABLEAU
    assert relu["indic_a"]["sous_theme"] == "thème" and relu["indic_a"]["socle_propose"] == "non"


def _preselection_autre(depot: Path, lignes: list[list[str]]) -> None:
    _csv(depot / "docs/validation/preselection_autre_lignes.csv", pre.COLONNES_LIGNES, lignes)


def test_lignes_renvoyees_orphelines(depot: Path):
    """D46 : une ligne renvoyée à dimtest et non reprise par dimtest est signalée ; reprise, elle ne l'est plus."""
    _depot_pret(depot)
    _preselection_autre(depot, [
        ["x2", "autre", "renvoi_z", "autre_dimension:dimtest", "", "", "jeu_z?geo=FR", "Eurostat", "eurostat_series",
         "Autre chose", "oui", "", "10"],
        ["x1", "autre", "renvoi_jeunes", "autre_dimension:dimtest", "", "", "jeu_a?age=Y16-24&geo=FR", "Eurostat",
         "eurostat_series", "Indicateur A — jeunes", "oui", "", "20"],
    ])
    rapport = ver.verifier_dimension(depot, "dimtest")
    assert rapport.compteurs["lignes_recues"] == 2 and rapport.compteurs["lignes_recues_orphelines"] == 1
    assert any("renvoyée(s) par autre (groupe renvoi_z) non reprises" in a for a in rapport.avertissements)
    renvois = ver.lignes_renvoyees(ver.lire_preselections(depot))
    assert dict(zip(renvois["ligne_id"], renvois["statut"])) == {"x2": "orpheline", "x1": "variante"}
    texte = "\n".join(ver.rapport_lignes_renvoyees(depot))
    assert "autre → dimtest : 2 ; 0, 1, 0, 0 ; 1" in texte and "x2 [renvoi_z]" in texte
    # reprise explicite (écart en bloc) : plus d'orpheline
    with (depot / "docs/validation/regles_preselection_dimtest.csv").open("a", encoding="utf-8") as f:
        f.write("70,autre_z,ecarte_en_bloc,,Hors champ.,autre,,,^jeu_z,,\n")
    pre.main(["--dimension", "dimtest", "--racine", str(depot), "--maj-fiches"])
    assert ver.verifier_dimension(depot, "dimtest").compteurs["lignes_recues_orphelines"] == 0


def test_ligne_retenue_ici_et_ecartee_ailleurs(depot: Path):
    _depot_pret(depot)
    _preselection_autre(depot, [["l2", "dimtest", "doublon", "ecarte_en_bloc", "", "", "jeu_a?sex=F&geo=FR", "Eurostat",
                                 "eurostat_series", "Indicateur A — femmes", "oui", "", "10"]])
    rapport = ver.verifier_dimension(depot, "dimtest")
    assert rapport.compteurs["lignes_retenues_ecartees"] == 1
    assert any("l2 retenue ici et écartée par autre/doublon" in a for a in rapport.avertissements)


def test_main_lignes_renvoyees_sans_dimension(depot: Path, capsys):
    _depot_pret(depot)
    assert ver.main(["--lignes-renvoyees", "--racine", str(depot)]) == 0
    assert "0 ligne(s) orpheline(s)" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        ver.main(["--racine", str(depot)])


@pytest.mark.skipif(not (RACINE / "indicateurs" / "liens_bien_etre").exists(), reason="fiches pilotes absentes")
def test_fiches_reelles_liens_bien_etre():
    rapport = ver.verifier_dimension(RACINE, "liens_bien_etre")
    assert rapport.erreurs == [], rapport.erreurs
    assert rapport.compteurs["fiches"] >= 1
