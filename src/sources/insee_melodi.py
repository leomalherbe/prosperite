"""Accès à Melodi, le catalogue de données de l'INSEE (`https://api.insee.fr/melodi/`).

Voie retenue par la décision D14 (sans clé, 30 appels par minute en mode anonyme).
Fiche source : `docs/sources/insee.md` §3.

Fonctions principales
- `lister_jeux(client)` : catalogue complet (`/catalog/all`) réduit aux champs utiles ;
- `decrire_jeu(id, client)` : notice d'un jeu (`/catalog/<id>`) et valeurs de ses dimensions (`/range/<id>`) ;
- `obtenir_donnees(id, filtres, client)` : extraction filtrée (`/data/<id>?DIM=code…`) → lignes
  `serie_id, geo, periode, valeur, statut`. Le `serie_id` est la requête qui permet de relire la
  série : `<jeu>?DIM1=code1&DIM2=code2…` (dimensions triées, hors TIME_PERIOD) ;
- `iterer_observations(...)` : même extraction, observation par observation, avec pagination
  (100 000 lignes au plus par appel) ;
- `telecharger_fichier(url, client)` et `lire_zip_csv(contenu)` : fichier complet d'un jeu (ZIP de CSV).

Le débit (30 appels/minute) est garanti par le client (`insee_http.ClientHttp`, intervalle de
2,1 s pour l'hôte api.insee.fr) : voir `client_melodi()`.
"""

from __future__ import annotations

import csv
import io
import json
import math
import re
import unicodedata
import zipfile
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Iterator, Optional
from urllib.parse import quote

from .insee_http import Ligne, Reponse, en_nombre

URL_BASE = "https://api.insee.fr/melodi"
HOTE = "api.insee.fr"
LIMITE_RESULTATS = 100_000     # maxResult maximal accepté par /data
INTERVALLE_MIN = 2.1           # secondes entre deux appels : < 30 appels/minute

#: Types de niveau géographique considérés comme nationaux dans /range (champ `type.code`).
TYPES_NATIONAUX = {"FRANCE", "NAT"}

#: Attributs connus (colonnes des fichiers CSV qui ne sont pas des dimensions).
ATTRIBUTS_CONNUS = {
    "OBS_STATUS", "OBS_STATUS_FR", "OBS_QUAL", "OBS_TYPE", "OBS_CONF", "CONF_STATUS", "UNIT_MULT",
    "DECIMALS", "LAST_UPDATE", "REF_PERIOD_DETAIL", "TABLE_IDENTIFIER", "OBS_COMMENT", "COMMENT_OBS",
    "EMBARGO_TIME", "OBS_REV", "GEO_OBJECT", "GEO_REF", "OBS_VALUE", "TIME_PERIOD",
}


def client_melodi(**options):
    """Client HTTP réglé pour Melodi (30 appels/minute)."""
    from .insee_http import ClientHttp

    intervalles = {HOTE: INTERVALLE_MIN, **options.pop("intervalles", {})}
    return ClientHttp(intervalles=intervalles, **options)


def texte(valeur: Any, langue: str = "fr") -> str:
    """Libellé dans la langue demandée, quelle que soit la forme reçue.

    Formes rencontrées : `[{"lang": "fr", "content": "…"}]`, `{"fr": "…", "en": "…"}`, chaîne.
    """
    if valeur is None:
        return ""
    if isinstance(valeur, str):
        return valeur.strip()
    if isinstance(valeur, dict):
        if langue in valeur and isinstance(valeur[langue], str):
            return valeur[langue].strip()
        if "label" in valeur:
            return texte(valeur["label"], langue)
        if "content" in valeur:
            return str(valeur.get("content") or "").strip()
        autres = [v for v in valeur.values() if isinstance(v, str)]
        return autres[0].strip() if autres else ""
    if isinstance(valeur, list):
        for element in valeur:
            if isinstance(element, dict) and element.get("lang") == langue and element.get("content"):
                return str(element["content"]).strip()
        for element in valeur:
            t = texte(element, langue)
            if t:
                return t
    return ""


# --------------------------------------------------------------------------------------
# Catalogue
# --------------------------------------------------------------------------------------

@dataclass
class JeuMelodi:
    id: str
    titre: str = ""
    sous_titre: str = ""
    description: str = ""
    periodicite: str = ""
    debut: str = ""
    fin: str = ""
    spatial: str = ""
    niveaux_geo: list[str] = field(default_factory=list)
    nb_observations: Optional[int] = None
    nb_series: Optional[int] = None
    modifie: str = ""
    themes: list[str] = field(default_factory=list)
    produits: list[dict[str, Any]] = field(default_factory=list)
    composants: list[str] = field(default_factory=list)
    mots_cles: list[str] = field(default_factory=list)

    @property
    def niveau_national(self) -> bool:
        return any(n in TYPES_NATIONAUX for n in self.niveaux_geo)

    @property
    def seulement_national(self) -> bool:
        return bool(self.niveaux_geo) and all(n in TYPES_NATIONAUX for n in self.niveaux_geo)

    def produit_csv(self) -> Optional[dict[str, Any]]:
        """Produit « fichier complet » en CSV (ZIP), langue FR de préférence."""
        csvs = [p for p in self.produits if str(p.get("format", "")).upper() == "CSV" and p.get("accessURL")]
        csvs.sort(key=lambda p: (str(p.get("language", "")).upper() != "FR", p.get("byteSize") or 0))
        return csvs[0] if csvs else None


def analyser_jeu(entree: dict[str, Any]) -> JeuMelodi:
    temporel = entree.get("temporal") or {}
    return JeuMelodi(
        id=entree.get("identifier", ""),
        titre=texte(entree.get("title")),
        sous_titre=texte(entree.get("subtitle")),
        description=texte(entree.get("description")),
        periodicite=texte((entree.get("accrualPeriodicity") or {}).get("label")),
        debut=str(temporel.get("startPeriod") or "")[:10],
        fin=str(temporel.get("endPeriod") or "")[:10],
        spatial=str((entree.get("spatial") or {}).get("id") or ""),
        niveaux_geo=[str(n.get("id")) for n in entree.get("spatialResolution") or [] if n.get("id")],
        nb_observations=entree.get("numObservations"),
        nb_series=entree.get("numSeries"),
        modifie=str(entree.get("modified") or "")[:10],
        themes=[texte(t.get("label")) for t in entree.get("theme") or [] if texte(t.get("label"))],
        produits=list(entree.get("product") or []),
        composants=list(entree.get("ordreComposants") or []),
        mots_cles=[texte(k.get("label")) for k in entree.get("keyword") or [] if texte(k.get("label"))],
    )


def analyser_catalogue(donnees: Any) -> list[JeuMelodi]:
    if isinstance(donnees, (bytes, str)):
        donnees = json.loads(donnees)
    if isinstance(donnees, dict):  # notice unique
        donnees = [donnees]
    return [analyser_jeu(e) for e in donnees if isinstance(e, dict) and e.get("identifier")]


def lister_jeux(client) -> list[JeuMelodi]:
    rep = client.get(f"{URL_BASE}/catalog/all")
    _verifier(rep)
    return analyser_catalogue(rep.contenu)


# --------------------------------------------------------------------------------------
# Plage de valeurs des dimensions (/range)
# --------------------------------------------------------------------------------------

@dataclass
class Concept:
    code: str
    libelle: str = ""
    valeurs: dict[str, str] = field(default_factory=dict)        # code → libellé
    types: dict[str, str] = field(default_factory=dict)          # code → type géographique (GEO)
    identifiants: dict[str, str] = field(default_factory=dict)   # code → id complet (GEO : « 2025-FRANCE-F »)


def analyser_plage(donnees: Any) -> dict[str, Concept]:
    if isinstance(donnees, (bytes, str)):
        donnees = json.loads(donnees)
    concepts: dict[str, Concept] = {}
    for bloc in donnees.get("range") or []:
        c = bloc.get("concept") or {}
        concept = Concept(code=c.get("code", ""), libelle=texte(c.get("label")))
        for v in bloc.get("values") or []:
            code = str(v.get("code", ""))
            if concept.code == "GEO":
                type_code = str((v.get("type") or {}).get("code") or "")
                cle = f"{type_code}-{code}" if type_code else code
                concept.types[cle] = type_code
                concept.identifiants[cle] = str(v.get("id") or "")
                concept.valeurs[cle] = texte(v.get("label"))
            else:
                concept.valeurs[code] = texte(v.get("label"))
        concepts[concept.code] = concept
    return concepts


def obtenir_plage(jeu: str, client) -> dict[str, Concept]:
    rep = client.get(f"{URL_BASE}/range/{jeu}")
    _verifier(rep)
    return analyser_plage(rep.contenu)


def _normaliser(t: str) -> str:
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t).strip()


def est_geo_nationale(type_code: str, libelle: str) -> bool:
    """Niveau national : type FRANCE/NAT, ou type OTHER dont le libellé désigne la France entière
    (métropole, hors Mayotte…) et non une partie (province, hors Île-de-France, DOM…)."""
    if type_code in TYPES_NATIONAUX:
        return True
    lib = _normaliser(libelle)
    if not lib.startswith("france"):
        return False
    return not any(m in lib for m in ("province", "hors ile", "hors paris", "outre-mer", "infra"))


def valeurs_geo_nationales(plage: dict[str, Concept]) -> list[tuple[str, str]]:
    """(filtre GEO, libellé) des valeurs nationales ; liste vide si le jeu n'a pas de dimension GEO."""
    geo = plage.get("GEO")
    if geo is None:
        return []
    return [(cle, geo.valeurs.get(cle, "")) for cle, t in geo.types.items() if est_geo_nationale(t, geo.valeurs.get(cle, ""))]


def decrire_jeu(jeu: str, client) -> tuple[Optional[JeuMelodi], dict[str, Concept]]:
    rep = client.get(f"{URL_BASE}/catalog/{jeu}")
    notice = analyser_catalogue(rep.contenu)[0] if rep.ok else None
    return notice, obtenir_plage(jeu, client)


# --------------------------------------------------------------------------------------
# Données (/data)
# --------------------------------------------------------------------------------------

def normaliser_geo(valeur: str) -> str:
    """« 2025-COM-44109 » → « COM-44109 » (forme utilisée dans les filtres)."""
    return re.sub(r"^\d{4}-", "", str(valeur or ""))


def identifiant_serie(jeu: str, dimensions: dict[str, Any], mesure: str = "") -> str:
    """`<jeu>?DIM=code&…` (dimensions triées, GEO normalisé, sans TIME_PERIOD)."""
    morceaux = []
    for cle in sorted(dimensions):
        if cle == "TIME_PERIOD":
            continue
        valeur = normaliser_geo(dimensions[cle]) if cle == "GEO" else str(dimensions[cle])
        morceaux.append(f"{cle}={valeur}")
    sid = f"{jeu}?{'&'.join(morceaux)}" if morceaux else jeu
    return f"{sid}#{mesure}" if mesure else sid


def url_donnees(jeu: str, filtres: Optional[dict[str, str]] = None) -> str:
    requete = "&".join(f"{k}={quote(str(v), safe='-_.')}" for k, v in (filtres or {}).items())
    return f"{URL_BASE}/data/{jeu}" + (f"?{requete}" if requete else "")


class ErreurMelodi(RuntimeError):
    def __init__(self, reponse: Reponse):
        super().__init__(f"HTTP {reponse.statut} sur {reponse.url} : {reponse.extrait()}")
        self.reponse = reponse


def _verifier(rep: Reponse) -> None:
    if not rep.ok:
        raise ErreurMelodi(rep)


def compter(jeu: str, filtres: Optional[dict[str, str]], client) -> int:
    """Nombre de lignes d'une extraction (`totalCount=TRUE&maxResult=0`)."""
    params = {**(filtres or {}), "totalCount": "TRUE", "maxResult": "0"}
    rep = client.get(f"{URL_BASE}/data/{jeu}", params=params)
    _verifier(rep)
    return int(((json.loads(rep.contenu) or {}).get("paging") or {}).get("count") or 0)


@dataclass
class Extraction:
    total: Optional[int] = None
    pages: int = 0
    recues: int = 0
    complete: bool = True
    remarque: str = ""


def iterer_observations(
    jeu: str,
    filtres: Optional[dict[str, str]],
    client,
    total: Optional[int] = None,
    max_par_page: int = LIMITE_RESULTATS,
    extraction: Optional[Extraction] = None,
    reponses: Optional[list[Reponse]] = None,
) -> Iterator[dict[str, Any]]:
    """Observations brutes (`{"dimensions", "attributes", "measures"}`) d'une extraction, page par page.

    Si `total` dépasse `max_par_page`, les pages suivantes sont demandées avec `page=2, 3…` ; si le
    service renvoie la même page (pagination non prise en compte), l'extraction est marquée
    incomplète dans `extraction` au lieu de boucler.
    """
    ext = extraction if extraction is not None else Extraction()
    ext.total = total
    nb_pages = max(1, math.ceil((total or 0) / max_par_page)) if total is not None else 1
    premiere_cle = None
    page = 1
    while page <= nb_pages:
        params = {**(filtres or {}), "maxResult": str(max_par_page)}
        if page > 1:
            params["page"] = str(page)
        rep = client.get(f"{URL_BASE}/data/{jeu}", params=params)
        _verifier(rep)
        if reponses is not None:
            reponses.append(rep)
        corps = json.loads(rep.contenu)
        observations = corps.get("observations") or []
        ext.pages += 1
        if not observations:
            break
        cle = json.dumps(observations[0], sort_keys=True)
        if page > 1 and cle == premiere_cle:
            ext.complete = False
            ext.remarque = f"pagination ignorée par le service (page {page} identique à la page 1)"
            break
        premiere_cle = premiere_cle or cle
        for obs in observations:
            ext.recues += 1
            yield obs
        if total is None:
            pagination = corps.get("paging") or {}
            if pagination.get("next"):
                nb_pages += 1
        page += 1
    if total is not None and ext.recues < total and ext.complete:
        ext.complete = False
        ext.remarque = ext.remarque or f"{ext.recues} observations reçues sur {total}"


def mesure_et_valeur(observation: dict[str, Any]) -> tuple[str, Optional[float]]:
    """Nom et valeur de la mesure d'une observation (OBS_VALUE_NIVEAU, OBS_VALUE_INDICE_DE_PRIX…)."""
    mesures = observation.get("measures") or {}
    for nom, contenu in mesures.items():
        valeur = contenu.get("value") if isinstance(contenu, dict) else contenu
        return nom, en_nombre(valeur)
    return "", None


def observations_en_lignes(jeu: str, observations: Iterable[dict[str, Any]], plusieurs_mesures: bool = False) -> list[Ligne]:
    """Lignes `serie_id, geo, periode, valeur, statut` triées par série puis période.

    Les observations sans valeur en début et en fin de série sont ignorées.
    """
    par_serie: dict[str, list[Ligne]] = {}
    for obs in observations:
        dims = obs.get("dimensions") or {}
        mesure, valeur = mesure_et_valeur(obs)
        sid = identifiant_serie(jeu, dims, mesure if plusieurs_mesures else "")
        statut = str((obs.get("attributes") or {}).get("OBS_STATUS") or "")
        par_serie.setdefault(sid, []).append(Ligne(sid, normaliser_geo(dims.get("GEO", "")), str(dims.get("TIME_PERIOD", "")), valeur, statut))
    lignes: list[Ligne] = []
    for sid in sorted(par_serie):
        serie = sorted(par_serie[sid], key=lambda l: l.periode)
        indices = [i for i, l in enumerate(serie) if l.valeur is not None]
        if indices:
            lignes += serie[indices[0]: indices[-1] + 1]
    return lignes


def obtenir_donnees(jeu: str, filtres: Optional[dict[str, str]], client, compter_avant: bool = True) -> list[Ligne]:
    """Extraction filtrée complète → lignes. Compte d'abord les lignes pour paginer si besoin."""
    total = compter(jeu, filtres, client) if compter_avant else None
    if total == 0:
        return []
    return observations_en_lignes(jeu, iterer_observations(jeu, filtres, client, total=total))


# --------------------------------------------------------------------------------------
# Fichiers complets (ZIP de CSV)
# --------------------------------------------------------------------------------------

def telecharger_fichier(url: str, client) -> bytes:
    rep = client.get(url)
    _verifier(rep)
    return rep.contenu


def _separateur(premiere_ligne: str) -> str:
    comptes = {s: premiere_ligne.count(s) for s in (";", ",", "\t", "|")}
    return max(comptes, key=comptes.get) if max(comptes.values()) > 0 else ";"


def lire_zip_csv(contenu: bytes) -> tuple[list[str], Iterator[dict[str, str]], dict[tuple[str, str], str]]:
    """Ouvre le ZIP d'un jeu Melodi : (colonnes, lignes du fichier de données, libellés).

    Les libellés viennent du fichier `*_metadata.csv` quand il existe : {(COD_VAR, COD_MOD): LIB_MOD}
    et {(COD_VAR, ""): LIB_VAR}.
    """
    archive = zipfile.ZipFile(io.BytesIO(contenu))
    noms = archive.namelist()
    donnees = [n for n in noms if n.lower().endswith("_data.csv")] or [n for n in noms if n.lower().endswith(".csv") and "metadata" not in n.lower()]
    if not donnees:
        raise ValueError(f"aucun fichier de données CSV dans l'archive ({', '.join(noms)[:200]})")
    libelles: dict[tuple[str, str], str] = {}
    for nom in noms:
        if nom.lower().endswith("_metadata.csv"):
            texte_meta = archive.read(nom).decode("utf-8-sig", errors="replace")
            lecteur = csv.DictReader(io.StringIO(texte_meta), delimiter=_separateur(texte_meta.splitlines()[0] if texte_meta else ";"))
            for ligne in lecteur:
                var = (ligne.get("COD_VAR") or "").strip()
                if not var:
                    continue
                if ligne.get("LIB_VAR"):
                    libelles.setdefault((var, ""), ligne["LIB_VAR"].strip())
                if ligne.get("COD_MOD") is not None:
                    libelles[(var, ligne["COD_MOD"].strip())] = (ligne.get("LIB_MOD") or "").strip()
    flux = io.TextIOWrapper(archive.open(donnees[0]), encoding="utf-8-sig", errors="replace", newline="")
    premiere = flux.readline()
    sep = _separateur(premiere)
    colonnes = [c.strip().strip('"') for c in next(csv.reader([premiere], delimiter=sep))]
    lecteur = csv.DictReader(flux, fieldnames=colonnes, delimiter=sep)
    return colonnes, iter(lecteur), libelles


def ligne_csv_en_observation(ligne: dict[str, str], dimensions: Optional[set[str]] = None) -> dict[str, Any]:
    """Convertit une ligne du CSV complet au format d'observation de /data.

    `dimensions` : noms des colonnes à traiter comme dimensions (sinon : toutes les colonnes qui ne
    sont ni la valeur, ni la période, ni un attribut connu). GEO est reconstitué en `<GEO_OBJECT>-<GEO>`.
    """
    dims: dict[str, str] = {}
    attributs: dict[str, str] = {}
    for col, val in ligne.items():
        if col is None:
            continue
        val = (val or "").strip()
        if col == "TIME_PERIOD":
            dims[col] = val
        elif col == "OBS_VALUE":
            continue
        elif col == "GEO":
            objet = (ligne.get("GEO_OBJECT") or "").strip()
            dims["GEO"] = f"{objet}-{val}" if objet and not val.startswith(objet + "-") else val
        elif (dimensions is not None and col in dimensions) or (dimensions is None and col not in ATTRIBUTS_CONNUS):
            dims[col] = val
        else:
            attributs[col] = val
    return {"dimensions": dims, "attributes": attributs, "measures": {"OBS_VALUE": {"value": ligne.get("OBS_VALUE")}}}
