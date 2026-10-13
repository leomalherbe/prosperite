"""Accès à Eurostat — catalogue (TOC), structure des jeux (SDMX 2.1) et données (JSON-stat 2.0).

Documentation de la source : docs/sources/eurostat.md.

Trois fonctions publiques, utilisées par le script de collecte (scripts/collecte_eurostat.py) :

- `lire_toc(lang)` : table des matières tabulée → DataFrame, une ligne par entrée
  (dossier, jeu ou tableau) avec la hiérarchie de dossiers conservée (`theme_source`) ;
- `decrire_jeu(code)` : structure SDMX 2.1 d'un jeu (dimensions ordonnées, modalités
  réellement présentes dans le jeu et leurs libellés) ;
- `obtenir_donnees(code, filtres)` : API Statistics 1.0 (JSON-stat 2.0) → lignes
  `serie_id, geo, periode, valeur, statut`.

Les fonctions `analyser_*` travaillent sur un contenu déjà téléchargé (texte, octets,
dictionnaire JSON) : ce sont elles que les tests exercent hors ligne sur les fixtures.

Toutes les requêtes passent par `ClientEurostat` : requêtes séquentielles, pause entre
deux requêtes (0,2 s par défaut), nouvelles tentatives avec attente croissante sur
HTTP 429, 5xx et coupures réseau, détection des réponses asynchrones (avertissement 413).
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional

import pandas as pd
import requests

RACINE_API = "https://ec.europa.eu/eurostat/api/dissemination"
URL_TOC = RACINE_API + "/catalogue/toc/txt"
URL_STATISTIQUES = RACINE_API + "/statistics/1.0/data/{code}"
URL_DATAFLOW = RACINE_API + "/sdmx/2.1/dataflow/ESTAT/{code}"
URL_DATASTRUCTURE = RACINE_API + "/sdmx/2.1/datastructure/ESTAT/{code}"

AGENT = "ObservatoireProsperite/0.2 (+https://github.com/leomalherbe/prosperite)"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

#: Paramètres de l'API Statistics qui ne sont pas des dimensions.
PARAMETRES_TEMPS = {"time", "time_period", "sinceTimePeriod", "untilTimePeriod", "lastTimePeriod", "geoLevel"}


# --------------------------------------------------------------------------- erreurs


class ErreurEurostat(Exception):
    """Erreur renvoyée par Eurostat (HTTP ≥ 400 ou corps d'erreur JSON/XML)."""

    def __init__(self, message: str, statut_http: Optional[int] = None, code: Optional[str] = None, url: str = ""):
        super().__init__(message)
        self.statut_http = statut_http
        self.code = code
        self.url = url


class AucuneDonnee(ErreurEurostat):
    """La requête est valide mais ne renvoie aucune donnée (code Eurostat 100, ou ressource absente)."""


class ReponseAsynchrone(ErreurEurostat):
    """Eurostat traite la requête en différé (avertissement 413 ASYNCHRONOUS_RESPONSE) : la renvoyer plus tard."""


class ExtractionTropVolumineuse(ErreurEurostat):
    """Extraction trop grosse (413 EXTRACTION_TOO_BIG) : ajouter des filtres ou découper."""


# --------------------------------------------------------------------------- client HTTP


class ClientEurostat:
    """Client HTTP séquentiel, poli et tolérant aux erreurs transitoires.

    - `pause` : délai minimal entre deux requêtes (secondes) ;
    - `essais` : nombre total de tentatives sur 429 / 5xx / coupure réseau ;
    - `attente_base` : première attente avant nouvel essai, multipliée par 3 à chaque échec
      (l'en-tête Retry-After est respecté s'il est présent) ;
    - `journal` : fonction appelée avec un message texte (print par défaut).
    """

    def __init__(
        self,
        pause: float = 0.2,
        delai: float = 180.0,
        essais: int = 5,
        attente_base: float = 10.0,
        session: Optional[requests.Session] = None,
        journal: Optional[Callable[[str], None]] = None,
    ):
        self.pause = pause
        self.delai = delai
        self.essais = essais
        self.attente_base = attente_base
        self.session = session or requests.Session()
        self.session.headers.setdefault("User-Agent", AGENT)
        self.journal = journal or (lambda m: print(m, flush=True))
        self.nb_requetes = 0
        self.nb_nouveaux_essais = 0
        self.octets = 0
        self._derniere = 0.0

    def _attendre_pause(self) -> None:
        reste = self.pause - (time.monotonic() - self._derniere)
        if reste > 0:
            time.sleep(reste)

    def get(self, url: str, params: Optional[Iterable[tuple[str, str]]] = None) -> requests.Response:
        """GET avec nouvelles tentatives. Renvoie la réponse (y compris 4xx, à interpréter par l'appelant)."""
        params = list(params or [])
        derniere_erreur: Optional[Exception] = None
        for essai in range(1, self.essais + 1):
            self._attendre_pause()
            try:
                rep = self.session.get(url, params=params, timeout=self.delai)
            except (requests.ConnectionError, requests.Timeout) as exc:
                rep, derniere_erreur = None, exc
            finally:
                self._derniere = time.monotonic()
                self.nb_requetes += 1
            if rep is not None and rep.status_code != 429 and rep.status_code < 500:
                self.octets += len(rep.content)
                return rep
            if essai == self.essais:
                break
            attente = self.attente_base * (3 ** (essai - 1))
            if rep is not None and rep.headers.get("Retry-After", "").isdigit():
                attente = max(attente, float(rep.headers["Retry-After"]))
            motif = f"HTTP {rep.status_code}" if rep is not None else type(derniere_erreur).__name__
            self.journal(f"    {motif} sur {url} : nouvel essai {essai + 1}/{self.essais} dans {attente:.0f} s")
            self.nb_nouveaux_essais += 1
            time.sleep(min(attente, 600))
        if rep is not None:
            return rep
        raise ErreurEurostat(f"échec réseau après {self.essais} essais : {derniere_erreur}", url=url)


_CLIENT_DEFAUT: Optional[ClientEurostat] = None


def client_defaut() -> ClientEurostat:
    global _CLIENT_DEFAUT
    if _CLIENT_DEFAUT is None:
        _CLIENT_DEFAUT = ClientEurostat()
    return _CLIENT_DEFAUT


def decompresser_si_gzip(contenu: bytes) -> bytes:
    """Décompresse un contenu gzip (fichiers `compressed=true`, metabase) ; le renvoie tel quel sinon."""
    return gzip.decompress(contenu) if contenu[:2] == b"\x1f\x8b" else contenu


# --------------------------------------------------------------------------- catalogue (TOC)

COLONNES_TOC = ["titre", "code", "type", "derniere_maj", "derniere_modif_structure", "debut", "fin", "nb_valeurs"]


def _date_toc(valeur: str) -> str:
    """'02.10.2026' → '2026-10-02' ; vide si absent."""
    valeur = (valeur or "").strip()
    m = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{4})", valeur)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else valeur


def analyser_toc(texte: str) -> pd.DataFrame:
    """Analyse le TOC tabulé (`catalogue/toc/txt`) en DataFrame.

    Une ligne par entrée du TOC, dans l'ordre du fichier (un même code peut apparaître
    plusieurs fois, à plusieurs endroits de l'arborescence). Colonnes :
    `code, titre, type, profondeur, theme_source, theme_codes, parent, derniere_maj,
    derniere_modif_structure, debut, fin, nb_valeurs`.

    - la profondeur est donnée par l'indentation du titre (4 espaces par niveau) ;
    - `theme_source` = titres des dossiers ancêtres joints par « > » (racine comprise) ;
      `theme_codes` = leurs codes ; `parent` = code de l'entrée immédiatement au-dessus
      (un tableau peut être rangé sous un jeu) ;
    - dates converties en AAAA-MM-JJ ; `nb_valeurs` entier ou None.
    """
    texte = texte.lstrip("﻿")
    lecteur = csv.reader(io.StringIO(texte), delimiter="\t", quotechar='"')
    pile: list[tuple[int, str, str, str]] = []  # (profondeur, code, titre, type)
    lignes = []
    for rang, champs in enumerate(lecteur):
        if not champs or (rang == 0 and champs[0].strip().lower() == "title"):
            continue
        champs = (champs + [""] * 8)[:8]
        titre_brut, code, type_, maj, struct, debut, fin, valeurs = champs
        profondeur = (len(titre_brut) - len(titre_brut.lstrip(" "))) // 4
        while pile and pile[-1][0] >= profondeur:
            pile.pop()
        dossiers = [e for e in pile if e[3] == "folder"]
        valeurs = valeurs.strip()
        lignes.append(
            {
                "code": code.strip(),
                "titre": titre_brut.strip(),
                "type": type_.strip(),
                "profondeur": profondeur,
                "theme_source": " > ".join(e[2] for e in dossiers),
                "theme_codes": " > ".join(e[1] for e in dossiers),
                "parent": pile[-1][1] if pile else "",
                "derniere_maj": _date_toc(maj),
                "derniere_modif_structure": _date_toc(struct),
                "debut": debut.strip(),
                "fin": fin.strip(),
                "nb_valeurs": int(valeurs) if valeurs.isdigit() else None,
            }
        )
        pile.append((profondeur, code.strip(), titre_brut.strip(), type_.strip()))
    df = pd.DataFrame(lignes, columns=["code", "titre", "type", "profondeur", "theme_source", "theme_codes", "parent", "derniere_maj", "derniere_modif_structure", "debut", "fin", "nb_valeurs"])
    df["nb_valeurs"] = df["nb_valeurs"].astype("Int64")
    return df


def telecharger_toc(lang: str = "en", client: Optional[ClientEurostat] = None) -> str:
    """Texte brut du TOC dans la langue demandée (en, fr, de)."""
    client = client or client_defaut()
    rep = client.get(URL_TOC, [("lang", lang)])
    if rep.status_code != 200:
        raise ErreurEurostat(f"TOC {lang} : HTTP {rep.status_code}", rep.status_code, url=rep.url)
    rep.encoding = "utf-8"
    return rep.text


def lire_toc(lang: str = "en", client: Optional[ClientEurostat] = None, texte: Optional[str] = None) -> pd.DataFrame:
    """TOC complet → DataFrame (voir `analyser_toc`). `texte` permet de passer un TOC déjà lu."""
    return analyser_toc(texte if texte is not None else telecharger_toc(lang, client))


# --------------------------------------------------------------------------- structure (SDMX 2.1)


@dataclass
class DimensionStructure:
    """Une dimension d'un jeu : identifiant, position (1 = première), liste de codes, modalités."""

    id: str
    position: int
    liste_codes: str = ""
    libelle: str = ""
    modalites: dict[str, str] = field(default_factory=dict)  # code → libellé (ordre de la liste)


@dataclass
class StructureJeu:
    code: str
    libelle: str
    dimensions: list[DimensionStructure]  # ordonnées, hors temps
    dimension_temps: str = "TIME_PERIOD"
    partielle: bool = True  # True : modalités limitées à celles présentes dans le jeu

    @property
    def ids(self) -> list[str]:
        return [d.id for d in self.dimensions]

    def dimension(self, ident: str) -> Optional[DimensionStructure]:
        return next((d for d in self.dimensions if d.id.lower() == ident.lower()), None)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _noms(element: ET.Element) -> dict[str, str]:
    return {n.get(XML_LANG, ""): (n.text or "").strip() for n in element if _local(n.tag) == "Name"}


def _choisir_langue(noms: dict[str, str], lang: str) -> str:
    for cle in (lang, "en", "fr", ""):
        if noms.get(cle):
            return noms[cle]
    return next(iter(noms.values()), "")


def _verifier_erreur_xml(racine: ET.Element) -> None:
    if _local(racine.tag) == "Error":
        message = " ".join(t.text or "" for t in racine.iter() if _local(t.tag) == "Text").strip()
        code = next((e.get("code") for e in racine.iter() if _local(e.tag) == "ErrorMessage"), None)
        classe = AucuneDonnee if code == "100" else ErreurEurostat
        raise classe(message or "erreur SDMX", code=code)


def analyser_structure(contenu: bytes, code: str = "", lang: str = "fr") -> StructureJeu:
    """Analyse un message de structure SDMX-ML 2.1 (dataflow avec `references=descendants`, ou datastructure).

    Indépendant des préfixes d'espaces de noms. Les listes de codes jointes au message
    (partielles avec `detail=referencepartial`) donnent les modalités et leurs libellés.
    """
    racine = ET.fromstring(contenu)
    _verifier_erreur_xml(racine)
    listes: dict[tuple[str, str], dict[str, str]] = {}
    partielle = False
    for liste in racine.iter():
        if _local(liste.tag) != "Codelist":
            continue
        partielle = partielle or liste.get("isPartial") == "true"
        modalites = {c.get("id"): _choisir_langue(_noms(c), lang) for c in liste if _local(c.tag) == "Code"}
        listes[(liste.get("id", ""), liste.get("version", ""))] = modalites
        listes.setdefault((liste.get("id", ""), ""), modalites)
    concepts = {c.get("id"): _choisir_langue(_noms(c), lang) for c in racine.iter() if _local(c.tag) == "Concept"}
    libelle = ""
    for flux in racine.iter():
        if _local(flux.tag) == "Dataflow":
            libelle = _choisir_langue(_noms(flux), lang)
            code = code or flux.get("id", "")
            break
    dsd = next((e for e in racine.iter() if _local(e.tag) == "DataStructure"), None)
    if dsd is None:
        raise ErreurEurostat(f"structure de {code} : aucun élément DataStructure")
    code = code or dsd.get("id", "")
    dimensions, temps = [], "TIME_PERIOD"
    for dim in dsd.iter():
        nom = _local(dim.tag)
        if nom == "TimeDimension":
            temps = dim.get("id", temps)
        if nom != "Dimension":
            continue
        ref_liste = ref_concept = None
        for sous in dim.iter():
            if _local(sous.tag) == "Enumeration":
                ref_liste = next((r for r in sous if _local(r.tag) == "Ref"), None)
            if _local(sous.tag) == "ConceptIdentity":
                ref_concept = next((r for r in sous if _local(r.tag) == "Ref"), None)
        id_liste = ref_liste.get("id", "") if ref_liste is not None else ""
        version = ref_liste.get("version", "") if ref_liste is not None else ""
        modalites = listes.get((id_liste, version)) or listes.get((id_liste, "")) or {}
        concept = ref_concept.get("id", "") if ref_concept is not None else dim.get("id", "")
        dimensions.append(
            DimensionStructure(
                id=dim.get("id", ""),
                position=int(dim.get("position") or len(dimensions) + 1),
                liste_codes=id_liste,
                libelle=concepts.get(concept, ""),
                modalites=dict(modalites),
            )
        )
    dimensions.sort(key=lambda d: d.position)
    return StructureJeu(code=code.lower(), libelle=libelle, dimensions=dimensions, dimension_temps=temps, partielle=partielle)


def decrire_jeu(code: str, client: Optional[ClientEurostat] = None, lang: str = "fr") -> StructureJeu:
    """Dimensions et modalités d'un jeu, via SDMX 2.1.

    Requête principale : `dataflow/ESTAT/{CODE}?references=descendants&detail=referencepartial`
    (structure + listes de codes limitées aux modalités présentes dans le jeu, avec libellés).
    Repli : `datastructure/ESTAT/{CODE}?references=children` (listes de codes complètes).
    """
    client = client or client_defaut()
    code_maj = code.upper()
    essais = [
        (URL_DATAFLOW.format(code=code_maj), [("references", "descendants"), ("detail", "referencepartial")]),
        (URL_DATASTRUCTURE.format(code=code_maj), [("references", "children")]),
    ]
    derniere: Optional[Exception] = None
    for url, params in essais:
        rep = client.get(url, params)
        if rep.status_code == 404:
            raise AucuneDonnee(f"{code} : structure introuvable (HTTP 404)", 404, url=rep.url)
        if rep.status_code != 200:
            derniere = ErreurEurostat(f"{code} : structure HTTP {rep.status_code}", rep.status_code, url=rep.url)
            continue
        try:
            structure = analyser_structure(rep.content, code, lang)
        except ET.ParseError as exc:
            derniere = ErreurEurostat(f"{code} : XML illisible ({exc})", url=rep.url)
            continue
        if url.startswith(URL_DATASTRUCTURE.split("{")[0]):
            structure.partielle = False
        return structure
    raise derniere or ErreurEurostat(f"{code} : structure indisponible")


# --------------------------------------------------------------------------- données (JSON-stat 2.0)


@dataclass
class DimensionJsonStat:
    id: str
    libelle: str
    codes: list[str]  # dans l'ordre de l'index
    libelles: dict[str, str]


@dataclass
class JeuJsonStat:
    """Réponse JSON-stat analysée : métadonnées + observations indexées par codes (et non par positions)."""

    code: str
    libelle: str
    mise_a_jour: str
    dimensions: list[DimensionJsonStat]  # ordre de `id`, temps compris
    dimension_temps: str
    observations: list[tuple[tuple[str, ...], str, float, str]]  # (codes hors temps, période, valeur, drapeau)
    annotations: dict[str, str] = field(default_factory=dict)

    @property
    def dimensions_hors_temps(self) -> list[DimensionJsonStat]:
        return [d for d in self.dimensions if d.id != self.dimension_temps]

    @property
    def jeu_source(self) -> str:
        return self.annotations.get("DISSEMINATION_SOURCE_DATASET", "").lower()

    def serie_id(self, codes: tuple) -> str:
        """Identifiant de série = code du jeu + filtres de l'API Statistics (ordre des dimensions).

        Directement réutilisable : `…/statistics/1.0/data/` + serie_id. Une position peut
        contenir une liste de modalités (lignes de ventilation) : paramètre répété.
        """
        ids = [d.id for d in self.dimensions_hors_temps]
        morceaux = []
        for i, c in zip(ids, codes):
            for valeur in (c if isinstance(c, (list, tuple)) else [c]):
                morceaux.append(f"{i}={valeur}")
        return f"{self.code}?" + "&".join(morceaux)

    def lignes(self) -> pd.DataFrame:
        """Lignes `serie_id, geo, periode, valeur, statut` (statut vide en l'absence de drapeau)."""
        ids = [d.id for d in self.dimensions_hors_temps]
        rang_geo = ids.index("geo") if "geo" in ids else None
        donnees = [
            (self.serie_id(codes), codes[rang_geo] if rang_geo is not None else "", periode, valeur, statut)
            for codes, periode, valeur, statut in self.observations
        ]
        return pd.DataFrame(donnees, columns=["serie_id", "geo", "periode", "valeur", "statut"])


def _erreur_json(doc: dict, statut_http: Optional[int], url: str) -> Optional[ErreurEurostat]:
    """Traduit un corps d'erreur ou d'avertissement Eurostat en exception (None si la réponse est normale)."""
    for cle in ("error", "warning"):
        if cle not in doc:
            continue
        contenu = doc[cle]
        if isinstance(contenu, list):
            contenu = contenu[0] if contenu else {}
        if not isinstance(contenu, dict):
            contenu = {"label": str(contenu)}
        statut = str(contenu.get("status", statut_http or ""))
        code = str(contenu.get("id", contenu.get("code", "")))
        libelle = str(contenu.get("label", contenu.get("message", "")))
        message = f"{statut} {code} {libelle}".strip()
        if "ASYNCHRONOUS" in libelle.upper():
            return ReponseAsynchrone(message, 413, code, url)
        if "TOO_BIG" in libelle.upper() or "TOO BIG" in libelle.upper():
            return ExtractionTropVolumineuse(message, 413, code, url)
        if code == "100" or "NO RESULT" in libelle.upper() or "NO DATA" in libelle.upper():
            return AucuneDonnee(message, statut_http, code, url)
        if cle == "error":
            return ErreurEurostat(message, statut_http, code, url)
    return None


def _en_liste(index: Any) -> list[str]:
    if isinstance(index, dict):
        return [c for c, _ in sorted(index.items(), key=lambda kv: kv[1])]
    return list(index or [])


def _positions(valeurs: Any) -> Iterable[tuple[int, Any]]:
    if isinstance(valeurs, dict):
        return ((int(k), v) for k, v in valeurs.items())
    if isinstance(valeurs, list):
        return enumerate(valeurs)
    return iter(())


def analyser_jsonstat(doc: dict, code: str = "", url: str = "") -> JeuJsonStat:
    """Analyse une réponse JSON-stat 2.0 de l'API Statistics.

    Respecte l'ordre des dimensions (`id`) et leurs tailles (`size`) : la position linéaire
    d'une observation vaut Σ pos_k × Π_{j>k} size_j (la dernière dimension varie le plus vite).
    `value` et `status` peuvent être des objets clairsemés {"position": …} ou des listes ;
    `status` est souvent absent. Les valeurs nulles sont ignorées.
    """
    erreur = _erreur_json(doc, None, url)
    if erreur is not None:
        raise erreur
    ids: list[str] = list(doc.get("id", []))
    tailles: list[int] = [int(t) for t in doc.get("size", [])]
    if len(ids) != len(tailles):
        raise ErreurEurostat(f"JSON-stat incohérent : id={ids} size={tailles}", url=url)
    temps = "time" if "time" in ids else (ids[-1] if ids else "time")
    dims: list[DimensionJsonStat] = []
    for ident, taille in zip(ids, tailles):
        bloc = doc.get("dimension", {}).get(ident, {})
        categorie = bloc.get("category", {})
        libelles = dict(categorie.get("label", {}) or {})
        codes = _en_liste(categorie.get("index")) or list(libelles)
        if len(codes) != taille:
            raise ErreurEurostat(f"dimension {ident} : {len(codes)} modalités pour size={taille}", url=url)
        dims.append(DimensionJsonStat(ident, bloc.get("label", ""), codes, {c: libelles.get(c, c) for c in codes}))
    pas = [1] * len(tailles)
    for k in range(len(tailles) - 2, -1, -1):
        pas[k] = pas[k + 1] * tailles[k + 1]
    rang_temps = ids.index(temps)
    statuts = doc.get("status")
    if isinstance(statuts, str):
        statut_unique, statuts = statuts, None
    else:
        statut_unique = None
        statuts = dict(_positions(statuts)) if statuts else {}
    observations = []
    for position, valeur in _positions(doc.get("value", {})):
        if valeur is None:
            continue
        indices = [(position // pas[k]) % tailles[k] for k in range(len(tailles))]
        codes = tuple(dims[k].codes[i] for k, i in enumerate(indices) if k != rang_temps)
        periode = dims[rang_temps].codes[indices[rang_temps]]
        drapeau = statut_unique if statut_unique is not None else statuts.get(position, "")
        observations.append((codes, periode, float(valeur), drapeau or ""))
    extension = doc.get("extension", {}) or {}
    annotations = {}
    for a in extension.get("annotation", []) or []:
        if a.get("type") and a["type"] not in annotations:
            annotations[a["type"]] = a.get("title") or a.get("date") or a.get("href") or ""
    code = (code or extension.get("id", "")).lower()
    return JeuJsonStat(
        code=code,
        libelle=doc.get("label", ""),
        mise_a_jour=doc.get("updated", ""),
        dimensions=dims,
        dimension_temps=temps,
        observations=observations,
        annotations=annotations,
    )


def _parametres(filtres: Optional[dict], lang: str) -> list[tuple[str, str]]:
    params: list[tuple[str, str]] = [("lang", lang)]
    for cle, valeur in (filtres or {}).items():
        valeurs = valeur if isinstance(valeur, (list, tuple, set)) else [valeur]
        params.extend((cle, str(v)) for v in valeurs)
    return params


def obtenir_jeu(code: str, filtres: Optional[dict] = None, lang: str = "fr", client: Optional[ClientEurostat] = None) -> JeuJsonStat:
    """Interroge l'API Statistics et renvoie la réponse analysée (métadonnées + observations).

    `filtres` : {dimension: code ou liste de codes} et paramètres temporels
    (`sinceTimePeriod`, `untilTimePeriod`, `lastTimePeriod`, `time`).
    Lève `AucuneDonnee`, `ReponseAsynchrone`, `ExtractionTropVolumineuse` ou `ErreurEurostat`.
    """
    client = client or client_defaut()
    url = URL_STATISTIQUES.format(code=code.lower())
    rep = client.get(url, _parametres(filtres, lang))
    try:
        doc = rep.json()
    except ValueError:
        if rep.status_code == 404:
            raise AucuneDonnee(f"{code} : HTTP 404", 404, url=rep.url)
        raise ErreurEurostat(f"{code} : réponse non JSON (HTTP {rep.status_code})", rep.status_code, url=rep.url)
    erreur = _erreur_json(doc, rep.status_code, rep.url) if isinstance(doc, dict) else None
    if erreur is not None:
        raise erreur
    if rep.status_code == 404:
        raise AucuneDonnee(f"{code} : HTTP 404", 404, url=rep.url)
    if rep.status_code == 413:
        raise ExtractionTropVolumineuse(f"{code} : HTTP 413", 413, url=rep.url)
    if rep.status_code >= 400:
        raise ErreurEurostat(f"{code} : HTTP {rep.status_code}", rep.status_code, url=rep.url)
    return analyser_jsonstat(doc, code, rep.url)


def obtenir_donnees(code: str, filtres: Optional[dict] = None, lang: str = "fr", client: Optional[ClientEurostat] = None) -> pd.DataFrame:
    """Lignes `serie_id, geo, periode, valeur, statut` d'un jeu filtré (ex. `{"geo": "FR", "sinceTimePeriod": 2000}`)."""
    return obtenir_jeu(code, filtres, lang, client).lignes()


def charger_jsonstat(chemin) -> JeuJsonStat:
    """Analyse une réponse JSON-stat enregistrée sur disque (fixtures, échantillons)."""
    with open(chemin, encoding="utf-8") as f:
        return analyser_jsonstat(json.load(f))
