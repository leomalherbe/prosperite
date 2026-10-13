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


# --- corrections de la phase 2 (règles éprouvées sur l'instantané BDM d'août 2024 et l'essai du 13/10) ---

def _decider(libelle, theme="ODD-X", dims=None):
    return cat.decider(libelle=libelle, theme=theme, theme_libelle="", frequence="A", zone="principale",
                       premiere="2000", derniere="2024", dimensions_bruit=dims)


@pytest.mark.parametrize(
    "libelle",
    [
        # « au cours des … derniers mois » n'est pas un cours de bourse (faux négatif ODD corrigé)
        "Part des individus s'étant connectés à internet au cours des trois derniers mois - Ensemble",
        "Personnes n’ayant pas utilisé internet au cours des trois derniers mois ou sans aucune compétence",
        "Concentrations moyennes annuelles de PM10 à proximité du trafic routier",
        "Part modale des transports de marchandises dans le transport intérieur terrestre de marchandises - Transport ferroviaire",
    ],
)
def test_libelles_odd_restent_candidats(libelle):
    assert _decider(libelle).candidat == "oui"


@pytest.mark.parametrize(
    "libelle,theme",
    [
        ("Cours du pétrole brut (Brent) en euros", "X"),
        ("Indice annuel des prix agricoles à la production (IPPAP) - Gros bovins", "IPAGRI-BASE-2015"),
        ("Prix moyens annuels de vente au détail en métropole - Sucre en morceaux (1 kg)", "IPC-PM-2015"),
        ("Indice annuel du coût horaire du travail révisé - Salaires et charges - Tous salariés", "X"),
        ("Taux de cotisations sociales (part patronale) - Contribution au dialogue social", "SMIC-COTISATIONS"),
        ("Nuitées dans les hôtels - Résidents - France métropolitaine", "X"),
        ("Effectif salarié par catégorie d'entreprise - Microentreprises - France", "X"),
        ("Importations - Total - Valeur aux prix courants - Série CVS-CJO", "CNT-2020-PIB-EQB-RF"),
    ],
)
def test_nouveaux_hors_champ(libelle, theme):
    d = _decider(libelle, theme)
    assert d.candidat == "non" and d.commentaire.startswith("hors champ")


@pytest.mark.parametrize(
    "theme,dims,ecarte",
    [
        # secteurs institutionnels : sous-secteurs et sociétés écartés, agrégats gardés
        ("CNA-2020-CSI", {"SECT_INST": "S1313", "OPERATION": "B6G"}, True),
        ("CNA-2020-CSI", {"SECT_INST": "S14", "OPERATION": "B6G"}, False),
        ("DD_CNA_TEE", {"REF_SECTOR": "S11", "STO": "B8G"}, True),
        ("DD_CNA_TEE", {"REF_SECTOR": "S1M", "STO": "B8G", "COUNTERPART_AREA": "W0"}, False),
        ("DD_CNA_TEE", {"REF_SECTOR": "S14", "STO": "B8G", "COUNTERPART_AREA": "W1"}, True),     # reste du monde
        ("DD_CNA_APU", {"REF_SECTOR": "S13", "COUNTERPART_SECTOR": "S1313", "STO": "OTE"}, True),
        # branches, produits, fonctions
        ("CNA-2020-EMPLOI", {"CNA_ACTIVITE": "A38-CJ"}, True),
        ("CNA-2020-EMPLOI", {"CNA_ACTIVITE": "NNTOTAL"}, False),
        ("CNA-2020-CONSO-MEN", {"CNA_PRODUIT": "FON01", "OPERATION": "P4"}, False),
        ("CNA-2020-CONSO-MEN", {"CNA_PRODUIT": "FON011", "OPERATION": "P4"}, True),
        ("CNT-2020-PIB-EQB-RF", {"CNA_PRODUIT": "D-CNT", "OPERATION": "P3"}, False),
        ("DD_CNA_APU", {"REF_SECTOR": "S13", "EXPENDITURE": "GF07", "STO": "OTE"}, False),
        ("DD_CNA_APU", {"REF_SECTOR": "S13", "EXPENDITURE": "GF0702", "STO": "OTE"}, True),
        ("DD_CNA_CONSO_MENAGES_COICOP", {"EXPENDITURE": "CP0111", "STO": "P31"}, True),
        # patrimoine : logements gardés, instruments détaillés écartés
        ("DD_CNA_PATRIMOINE", {"REF_SECTOR": "S14", "INSTR_ASSET": "N111G", "STO": "LE"}, False),
        ("DD_CNA_PATRIMOINE", {"REF_SECTOR": "S14", "INSTR_ASSET": "F511", "STO": "LE"}, True),
        # valorisations et opérations techniques
        ("DD_CNA_AGREGATS", {"REF_SECTOR": "S1", "STO": "B1GQ", "PRICES": "D"}, True),
        ("DD_CNA_AGREGATS", {"REF_SECTOR": "S1", "STO": "B1GQ", "PRICES": "L", "TRANSFORMATION": "GY"}, False),
        ("DD_CNA_AGREGATS", {"REF_SECTOR": "S1", "STO": "D41"}, True),
        ("CNA-2020-PAT-NF", {"SECT_INST": "S1", "OPERATION": "AN_SEC2010"}, False),
        # hors comptes nationaux, la liste d'opérations ne s'applique pas
        ("DS_X", {"STO": "D41"}, False),
    ],
)
def test_motif_bruit_dimensions(theme, dims, ecarte):
    assert (cat.motif_bruit_dimensions(theme, dims) is not None) is ecarte
    d = _decider("Revenu disponible brut", theme, dims)
    assert (d.candidat == "non") is ecarte


@pytest.mark.parametrize(
    "libelle,dimension",
    [
        # libellés Melodi : « Emploi ou débit », « actifs », « formation brute de capital » ne trompent plus le tagging
        ("Comptes des administrations publiques — Devise nationale (Euros) ; Épargne brute ; Emploi ou débit", "niveau_de_vie"),
        ("Comptes de patrimoine — Emploi ou débit ; Monde ; Total ; Formation brute de capital fixe", "niveau_de_vie"),
        ("Tableau économique d'ensemble — Ménages ; Patrimoine en fin d'année ; Actifs fixes par type d'actifs", "niveau_de_vie"),
        ("Nombre de lits et places en chirurgie pour 100.000 habitants - France", "sante"),
        ("Population écrouée au 31 décembre - Densité carcérale pour 100 places - France", "democratie"),
        ("Activité, emploi et chômage - séries longues — Population active ; Femme", "travail"),
    ],
)
def test_tagger_libelles_techniques(libelle, dimension):
    assert cat.tagger(libelle) == dimension
