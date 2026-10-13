"""Tests des règles de catalogage INSEE (src/sources/insee_catalogue.py)."""

import pytest

from src.sources import insee_catalogue as cat


@pytest.mark.parametrize(
    "code,libelle,attendu",
    [
        ("FE", "", "principale"),
        ("FM", "", "principale"),
        ("FR-D976", "", "principale"),
        ("FM_D99_D978", "", "nationale"),
        ("SO", "Sans objet", "sans_objet"),
        ("", "", "sans_objet"),
        ("D75", "75 - Paris", "hors_nationale"),
        ("R11", "Île-de-France", "hors_nationale"),
        ("F_H_IDF", "France métropolitaine hors Île-de-France", "hors_nationale"),
        ("PROVINCE", "France de province", "hors_nationale"),
        ("XNOUVEAU", "France entière y compris COM", "nationale"),
    ],
)
def test_classer_zone(code, libelle, attendu):
    assert cat.classer_zone(code, libelle) == attendu


@pytest.mark.parametrize(
    "libelle,dimension",
    [
        # libellés réels lus dans la BDM (fixtures et repérage de phase 1)
        ("Satisfaction dans la vie - Ensemble", "liens_bien_etre"),
        ("Taux de chômage au sens du BIT - Ensemble - France hors Mayotte - Données CVS", "travail"),
        ("Taux de pauvreté monétaire - Seuil de 60 % du niveau de vie médian selon le statut d’activité - Actifs occupés", "niveau_de_vie"),
        ("Inégalités des revenus - Rapport interquintile des masses de niveau de vie (100-S80)/S20", "egalites"),
        ("Taux d’effort net en logement - 1er quartile de revenu par unité de consommation", "logement_cadre_vie"),
        ("Espérance de vie en bonne santé - Femmes", "sante"),
        ("Taux de sorties précoces du système scolaire des 18-24 ans", "education"),
        ("Empreinte carbone par habitant", "planete"),
        ("Proportion de sols artificialisés", "planete"),
        ("Confiance de la population dans les institutions - La justice", "democratie"),
        ("Proportion des adultes victimes de violences physiques et/ou sexuelles", "securite_confiance"),
        ("Taux de participation au 1er tour des élections présidentielles - France", "democratie"),
        ("Taux de participation des jeunes et des adultes à une formation formelle et non formelle - Ensemble", "education"),
        ("Taux de fréquence des accidents du travail par catégorie socio-professionnelle - Cadres", "travail"),
        ("Enquête mensuelle de conjoncture auprès des ménages - Opinion sur le niveau de vie passé en France : Solde des réponses", "securite_confiance"),
        ("Démographie - Population moyenne de l'année - France métropolitaine", "contexte"),
        ("Bénéficiaires d'allocations familiales - Taux d'allocataires pour 1 000 ménages - France", "niveau_de_vie"),
    ],
)
def test_tagger(libelle, dimension):
    assert cat.tagger(libelle) == dimension


def test_tagger_aucune_regle():
    assert cat.tagger("Coefficient XYZ") is None


def test_ventilations_titre():
    assert cat.ventilations_titre("Satisfaction dans la vie - Faible (0-5) - 75 ans ou plus") == ["age"]
    assert cat.ventilations_titre("Taux de chômage au sens du BIT (moyenne annuelle) - Hommes - France hors Mayotte") == ["sexe"]
    assert cat.ventilations_titre("Taux d’effort net en logement - 1er quartile de revenu par unité de consommation") == ["revenu"]
    # l'âge qui définit l'indicateur n'est pas une ventilation
    assert cat.ventilations_titre("Taux de sorties précoces du système scolaire des 18-24 ans") == []
    # un écart femmes-hommes n'est pas une ventilation par sexe
    assert cat.ventilations_titre("Écart de taux d'emploi entre les femmes et les hommes - Ensemble") == []


def test_ventilations_dimensions():
    assert cat.ventilations_dimensions({"SEX": "F", "AGE": "_T", "GEO": "FRANCE-F"}) == ["sexe"]
    assert cat.ventilations_dimensions({"SEX": "_T", "AGE": "Y15T24"}) == ["age"]
    assert cat.ventilations_dimensions({"SEXE": "0"}) == []


def test_flux_anciennes_bases():
    anciens = cat.flux_anciennes_bases(["CNA-2010-PIB", "CNA-2014-PIB", "CNA-2020-PIB", "ODD-SANTE-BIEN-ETRE", "ICA-2005-EMAGSA", "ICA-2010-EMAGSA"])
    assert anciens == {"CNA-2010-PIB": "2020", "CNA-2014-PIB": "2020", "ICA-2005-EMAGSA": "2010"}


def decider(**kw):
    base = dict(libelle="Satisfaction dans la vie - Ensemble", theme="ODD-SANTE-BIEN-ETRE", theme_libelle="", frequence="A", zone="principale",
                premiere="2010", derniere="2024", nb_annees_depuis_2000=15)
    base.update(kw)
    return cat.decider(**base)


def test_decider_oui():
    d = decider()
    assert (d.dimension_v0, d.candidat) == ("liens_bien_etre", "oui")


def test_decider_premiere_periode_tardive():
    d = decider(premiere="2013", nb_annees_depuis_2000=12)
    assert d.candidat == "a_verifier" and "D16" in d.commentaire
    d = decider(premiere="2020", nb_annees_depuis_2000=4)
    assert d.candidat == "non" and "moins de 10 points" in d.commentaire


def test_decider_serie_irreguliere():
    d = decider(premiere="2000", nb_annees_depuis_2000=8)
    assert d.candidat == "a_verifier" and "D17" in d.commentaire


def test_decider_exclusions():
    assert decider(serie_arretee=True).candidat == "non"
    assert "ancienne base" in decider(ancienne_base="2020").commentaire
    assert decider(theme="CLIMAT-AFFAIRES").candidat == "non"
    assert decider(libelle="Indice des prix à la consommation - Ensemble").candidat == "non"
    assert decider(libelle="Population au 1er janvier", theme="POPULATION-STRUCTURE").dimension_v0 == "contexte"
    d = decider(libelle="Coefficient XYZ", theme="AUTRE")
    assert (d.dimension_v0, d.candidat) == ("", "non")


def test_decider_dimension_deduite_du_regroupement():
    d = decider(libelle="Indicateur sans mot-clé", theme="ODD-SANTE-BIEN-ETRE")
    assert (d.dimension_v0, d.candidat) == ("sante", "a_verifier")


def test_decider_infra_annuelle_et_ventilation():
    d = decider(libelle="Taux de chômage au sens du BIT - Femmes - France hors Mayotte - Données CVS", frequence="T", nb_annees_depuis_2000=None,
                premiere="1975-Q1", derniere="2026-Q2")
    assert d.candidat == "oui"
    assert "infra-annuelle" in d.commentaire and d.ventilation == "sexe"
