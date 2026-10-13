"""Tests hors ligne du script de vérification des voies d'accès (M04)."""

import io

import openpyxl

from scripts.collecte_sources import (
    combinaisons_distinctes,
    correspondances,
    decrire_classeur,
    deviner_nature,
    nom_extrait,
    valeurs_distinctes,
    verdict,
)


def test_nature_json_csv_html_pdf():
    assert deviner_nature("application/json; charset=utf-8", b'{"total_count": 3}') == "json"
    assert deviner_nature("text/csv", b"entity,code,year\nFrance,FRA,2024\n") == "csv"
    assert deviner_nature("", b"annee;valeur\n2000;1.5\n") == "csv"
    assert deviner_nature("text/html", b"<!DOCTYPE html><html>") == "html"
    assert deviner_nature("application/octet-stream", b"%PDF-1.7") == "pdf"
    assert deviner_nature("application/xml", b'<?xml version="1.0"?>') == "xml"


def test_nature_binaires():
    assert deviner_nature("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b"PK\x03\x04abc") == "xlsx"
    assert deviner_nature("application/octet-stream", b"PK\x03\x04abc", "https://x.org/f.xlsx?v=2") == "xlsx"
    assert deviner_nature("application/zip", b"PK\x03\x04abc") == "zip"
    assert deviner_nature("", b"PAR1\x15\x04") == "parquet"


def test_verdict():
    assert verdict(200, "csv") == "donnees"
    assert verdict(200, "html") == "page_html"
    assert verdict(200, "pdf") == "pdf"
    assert verdict(401, "json") == "erreur"
    assert verdict(None, "") == "erreur"


def test_nom_extrait():
    assert nom_extrait("Banque mondiale", "SP.DYN.LE00.IN") == "banque_mondiale__sp_dyn_le00_in.txt"


def test_decrire_classeur():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Donnees"
    ws.append(["pays", "annee", "score"])
    ws.append(["France", 2024, 7.1])
    tampon = io.BytesIO()
    wb.save(tampon)
    texte = decrire_classeur(tampon.getvalue())
    assert "Donnees" in texte
    assert "France | 2024 | 7.1" in texte


def test_valeurs_distinctes():
    contenu = "Titre;Valeurs\nHomicides;1\nHomicides;2\nCambriolages;3\n".encode()
    texte = valeurs_distinctes(contenu, "Titre")
    assert "2 valeurs distinctes" in texte
    assert "Homicides\t2" in texte
    assert "absente" in valeurs_distinctes(contenu, "Inconnue")


def test_combinaisons_distinctes():
    contenu = "﻿MEASURE,Measure,TIME_PERIOD\nLS,Life satisfaction,2020\nLS,Life satisfaction,2021\nSS,Social support,2020\n".encode()
    texte = combinaisons_distinctes(contenu, ["MEASURE", "Measure"])
    assert "2 combinaisons distinctes" in texte
    assert "LS\tLife satisfaction" in texte
    assert "absentes" in combinaisons_distinctes(contenu, ["X"])


def test_correspondances():
    xml = (b'<s:Dataflow id="DF_A" agencyID="OECD.X"><c:Name xml:lang="en">A</c:Name></s:Dataflow>'
           b'<s:Dataflow id="DF_B" agencyID="OECD.Y"><c:Name xml:lang="en">B</c:Name></s:Dataflow>')
    texte = correspondances(xml, r'Dataflow id="([^"]+)" agencyID="([^"]+)"')
    assert "2 correspondances" in texte
    assert "DF_B\tOECD.Y" in texte
