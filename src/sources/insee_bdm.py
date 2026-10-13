"""Accès à la BDM de l'INSEE par le service web SDMX 2.1 (`https://bdm.insee.fr/series/sdmx/`).

Voie retenue par la décision D14 (sans clé). Fiche source : `docs/sources/insee.md` §2.

Fonctions principales
- `lister_dataflows(client)` : regroupements (dataflows) avec leur nombre de séries annoncé ;
- `lister_series(dataflow, client)` : une entrée par série (IDBANK, TITLE_FR, FREQ, UNIT_MEASURE,
  REF_AREA, LAST_UPDATE, dimensions de la clé dont SERIE_ARRETEE…), par `detail=nodata`
  (et non `serieskeysonly`, qui ne renvoie ni IDBANK ni titre — constat de phase 1).
  Le service refuse les réponses de plus de 2 000 séries : la requête est alors découpée
  automatiquement selon les dimensions de la clé (FREQ d'abord), à partir de la structure (DSD)
  et des listes de codes ; `avec_periodes=True` ajoute première et dernière période ;
- `obtenir_series(idbanks, client, params)` : requêtes `SERIES_BDM/<id1>+…` par lots de 400 au plus ;
- `obtenir_serie(idbank, client)` : lignes `serie_id, geo, periode, valeur, statut`, du plus ancien
  au plus récent, sans les valeurs manquantes de début et de fin de série (la BDM ajoute souvent
  une observation `NaN` pour l'année en cours).

Toutes les fonctions réseau prennent un `client` (voir `insee_http.ClientHttp`) ; les fonctions
`analyser_*` travaillent sur le contenu brut et sont testées hors ligne sur des fixtures.
"""

from __future__ import annotations

import io
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

from .insee_http import Ligne, Reponse, en_nombre, est_manquante

URL_BASE = "https://bdm.insee.fr/series/sdmx"
AGENCE = "FR1"
LIMITE_SERIES = 2000      # séries par réponse (guide SDMX v2.2, erreur 510 / HTTP 413)
LIMITE_IDBANKS = 400      # idbanks par requête SERIES_BDM (guide SDMX v2.2)

FREQUENCES = {
    "A": "annuelle",
    "S": "semestrielle",
    "T": "trimestrielle",
    "B": "bimestrielle",
    "M": "mensuelle",
}

#: Attributs de série communs à toutes les réponses de données (hors dimensions de la clé).
ATTRIBUTS_SERIE = ("IDBANK", "FREQ", "TITLE_FR", "TITLE_EN", "LAST_UPDATE", "UNIT_MEASURE", "UNIT_MULT", "REF_AREA", "DECIMALS")


def _local(tag: str) -> str:
    """Nom local d'une balise XML (sans espace de noms)."""
    return tag.rsplit("}", 1)[-1]


def _langue(element: ET.Element) -> Optional[str]:
    return element.get("{http://www.w3.org/XML/1998/namespace}lang")


# --------------------------------------------------------------------------------------
# Structures : dataflows, DSD, listes de codes
# --------------------------------------------------------------------------------------

@dataclass
class Dataflow:
    id: str
    nom_fr: str = ""
    nom_en: str = ""
    url_page: str = ""
    nb_series: Optional[int] = None


def analyser_dataflows(contenu: bytes) -> list[Dataflow]:
    """Analyse un message de structure contenant des `str:Dataflow`."""
    racine = ET.fromstring(contenu)
    flux = []
    for el in racine.iter():
        if _local(el.tag) != "Dataflow" or el.get("id") is None:
            continue
        df = Dataflow(id=el.get("id"))
        for enfant in el.iter():
            nom = _local(enfant.tag)
            if nom == "Name":
                if _langue(enfant) == "fr":
                    df.nom_fr = (enfant.text or "").strip()
                elif _langue(enfant) == "en":
                    df.nom_en = (enfant.text or "").strip()
            elif nom == "AnnotationURL":
                df.url_page = (enfant.text or "").strip()
            elif nom == "AnnotationText" and enfant.text and "séries" in enfant.text:
                chiffres = "".join(c for c in enfant.text if c.isdigit())
                df.nb_series = int(chiffres) if chiffres else None
        flux.append(df)
    return flux


@dataclass
class Dimension:
    id: str
    position: int
    codelist: Optional[str] = None


def analyser_structure(contenu: bytes) -> list[Dimension]:
    """Dimensions de la clé d'un DSD, dans l'ordre de la clé (sans TIME_PERIOD)."""
    racine = ET.fromstring(contenu)
    dims = []
    for el in racine.iter():
        # Les relations d'attributs du DSD réel citent aussi les dimensions (`<str:Dimension><Ref id="FREQ"/>`,
        # sans attribut id) : 108 éléments de plus dans CHOMAGE-TRIM-NATIONAL, qui allongeaient la clé
        # (constaté sur la réponse réelle du 13/10 ; la fixture reconstituée ne les contenait pas).
        if _local(el.tag) != "Dimension" or not el.get("id"):
            continue
        codelist = None
        for enfant in el.iter():
            if _local(enfant.tag) == "Enumeration":
                for ref in enfant:
                    if _local(ref.tag) == "Ref":
                        codelist = ref.get("id")
        position = int(el.get("position") or len(dims) + 1)
        dims.append(Dimension(id=el.get("id"), position=position, codelist=codelist))
    dims.sort(key=lambda d: d.position)
    return dims


def analyser_codelist(contenu: bytes) -> dict[str, str]:
    """Codes d'une liste de codes SDMX → libellé français (ou anglais à défaut)."""
    racine = ET.fromstring(contenu)
    codes: dict[str, str] = {}
    for el in racine.iter():
        if _local(el.tag) != "Code":
            continue
        libelles = {_langue(n): (n.text or "").strip() for n in el if _local(n.tag) == "Name"}
        codes[el.get("id")] = libelles.get("fr") or libelles.get("en") or ""
    return codes


# --------------------------------------------------------------------------------------
# Données (StructureSpecificData)
# --------------------------------------------------------------------------------------

@dataclass
class SerieBdm:
    """Une série telle que renvoyée par le service : attributs + observations (éventuelles)."""

    attributs: dict[str, str]
    observations: list[dict[str, str]] = field(default_factory=list)

    @property
    def idbank(self) -> str:
        return self.attributs.get("IDBANK", "")

    @property
    def geo(self) -> str:
        return self.attributs.get("REF_AREA", "")

    @property
    def freq(self) -> str:
        return self.attributs.get("FREQ", "")

    def resume(self, annee_min: int = 2000) -> "ResumePeriodes":
        return resumer_observations(self.observations, annee_min)


def analyser_donnees(contenu: bytes) -> list[SerieBdm]:
    """Analyse une réponse StructureSpecificData (avec ou sans observations).

    Lecture en flux (`iterparse`) pour limiter la mémoire sur les grosses réponses.
    """
    series: list[SerieBdm] = []
    courante: Optional[SerieBdm] = None
    for evenement, el in ET.iterparse(io.BytesIO(contenu), events=("start", "end")):
        nom = _local(el.tag)
        if evenement == "start" and nom == "Series":
            courante = SerieBdm(attributs=dict(el.attrib))
        elif evenement == "end" and nom == "Obs" and courante is not None:
            courante.observations.append(dict(el.attrib))
            el.clear()
        elif evenement == "end" and nom == "Series" and courante is not None:
            series.append(courante)
            courante = None
            el.clear()
    return series


@dataclass
class ResumePeriodes:
    premiere: str = ""          # première période avec une valeur
    derniere: str = ""          # dernière période avec une valeur
    nb_valeurs: int = 0         # nombre d'observations non manquantes reçues
    nb_annees_depuis: int = 0   # nombre d'années distinctes (≥ annee_min) avec au moins une valeur
    statut_derniere: str = ""   # OBS_STATUS de la dernière valeur
    manquantes_fin: int = 0     # nombre d'observations manquantes après la dernière valeur
    manquantes_debut: int = 0   # nombre d'observations manquantes avant la première valeur


def annee(periode: str) -> Optional[int]:
    try:
        return int(str(periode)[:4])
    except (TypeError, ValueError):
        return None


def resumer_observations(observations: Iterable[dict[str, str]], annee_min: int = 2000) -> ResumePeriodes:
    """Première/dernière période non manquante d'une liste d'observations (ordre quelconque)."""
    obs = sorted(observations, key=lambda o: o.get("TIME_PERIOD", ""))
    valides = [o for o in obs if not est_manquante(o.get("OBS_VALUE"))]
    r = ResumePeriodes()
    if not valides:
        r.manquantes_fin = len(obs)
        return r
    r.premiere = valides[0]["TIME_PERIOD"]
    r.derniere = valides[-1]["TIME_PERIOD"]
    r.nb_valeurs = len(valides)
    r.statut_derniere = valides[-1].get("OBS_STATUS", "")
    annees = {annee(o["TIME_PERIOD"]) for o in valides}
    r.nb_annees_depuis = sum(1 for a in annees if a is not None and a >= annee_min)
    r.manquantes_fin = sum(1 for o in obs if o.get("TIME_PERIOD", "") > r.derniere)
    r.manquantes_debut = sum(1 for o in obs if o.get("TIME_PERIOD", "") < r.premiere)
    return r


def series_en_lignes(series: Iterable[SerieBdm]) -> list[Ligne]:
    """Lignes `serie_id, geo, periode, valeur, statut`, ordre chronologique.

    Les valeurs manquantes de début et de fin de série sont ignorées ; une valeur manquante
    au milieu de la série est conservée avec `valeur=None` (son statut, souvent « O », est gardé).
    """
    lignes: list[Ligne] = []
    for s in series:
        obs = sorted(s.observations, key=lambda o: o.get("TIME_PERIOD", ""))
        indices = [i for i, o in enumerate(obs) if not est_manquante(o.get("OBS_VALUE"))]
        if not indices:
            continue
        for o in obs[indices[0]: indices[-1] + 1]:
            lignes.append(Ligne(s.idbank, s.geo, o.get("TIME_PERIOD", ""), en_nombre(o.get("OBS_VALUE")), o.get("OBS_STATUS", "")))
    return lignes


# --------------------------------------------------------------------------------------
# Appels réseau
# --------------------------------------------------------------------------------------

def url_dataflows() -> str:
    return f"{URL_BASE}/dataflow"


def lister_dataflows(client) -> list[Dataflow]:
    rep = client.get(url_dataflows())
    _verifier(rep)
    return analyser_dataflows(rep.contenu)


def obtenir_structure(dataflow: str, client) -> list[Dimension]:
    rep = client.get(f"{URL_BASE}/datastructure/{AGENCE}/{dataflow}")
    _verifier(rep)
    return analyser_structure(rep.contenu)


def obtenir_codelist(codelist: str, client) -> dict[str, str]:
    rep = client.get(f"{URL_BASE}/codelist/{AGENCE}/{codelist}")
    _verifier(rep)
    return analyser_codelist(rep.contenu)


class ErreurBdm(RuntimeError):
    def __init__(self, reponse: Reponse):
        super().__init__(f"HTTP {reponse.statut} sur {reponse.url} : {reponse.extrait()}")
        self.reponse = reponse


def _verifier(rep: Reponse) -> None:
    if not rep.ok:
        raise ErreurBdm(rep)


def est_trop_volumineuse(rep: Reponse) -> bool:
    """Réponse refusée parce qu'elle dépasse la limite de séries (HTTP 413 / code SDMX 510)."""
    if rep.statut == 413:
        return True
    if rep.ok or rep.statut == 404:
        return False
    texte = rep.texte()[:3000].lower()
    return 'code="510"' in texte or "exceeds" in texte or "trop volumineu" in texte or "too large" in texte


def construire_cle(dims: list[Dimension], parties: dict[str, list[str]]) -> str:
    """Clé SDMX : une position par dimension, codes séparés par « + », vide = toutes valeurs."""
    if not parties:
        return ""
    return ".".join("+".join(parties.get(d.id) or []) for d in dims)


@dataclass
class Listage:
    """Résultat de `lister_series` : séries (attributs) + compteurs pour le journal."""

    dataflow: str
    series: list[dict[str, str]] = field(default_factory=list)
    requetes: int = 0
    decoupages: int = 0
    erreurs: list[str] = field(default_factory=list)
    reponses: list[tuple[str, Reponse]] = field(default_factory=list)  # (clé, réponse) gardées si demandé


def lister_series(
    dataflow: str,
    client,
    nb_annonce: Optional[int] = None,
    codelists: Optional[dict[str, dict[str, str]]] = None,
    avec_periodes: bool = False,
    garder_reponses: bool = False,
    journal: Optional[Callable[[str], None]] = None,
) -> Listage:
    """Liste toutes les séries d'un dataflow par `detail=nodata`, avec découpage automatique.

    - `nb_annonce` : nombre de séries annoncé par la liste des dataflows ; au-delà de 2 000, on
      découpe d'emblée (la requête globale échouerait) ;
    - `codelists` : cache partagé des listes de codes (évite de les retélécharger) ;
    - `avec_periodes` : ajoute `PREMIERE_PERIODE`, `DERNIERE_PERIODE` (valeurs non manquantes)
      par deux requêtes `firstNObservations` / `lastNObservations` par lot d'idbanks.
    """
    res = Listage(dataflow=dataflow)
    cache = codelists if codelists is not None else {}
    note = journal or (lambda m: None)
    dims: Optional[list[Dimension]] = None

    def charger_dims() -> list[Dimension]:
        nonlocal dims
        if dims is None:
            res.requetes += 1
            dims = obtenir_structure(dataflow, client)
        return dims

    def codes_de(dim: Dimension) -> list[str]:
        if not dim.codelist:
            return []
        if dim.codelist not in cache:
            res.requetes += 1
            try:
                cache[dim.codelist] = obtenir_codelist(dim.codelist, client)
            except ErreurBdm as exc:
                res.erreurs.append(f"liste de codes {dim.codelist} : {exc}")
                cache[dim.codelist] = {}
        return [c for c in cache[dim.codelist] if "." not in c and "+" not in c]

    def interroger(parties: dict[str, list[str]]) -> Optional[list[dict[str, str]]]:
        """None = trop volumineuse ; liste (éventuellement vide) sinon."""
        cle = construire_cle(charger_dims(), parties) if parties else ""
        url = f"{URL_BASE}/data/{dataflow}" + (f"/{cle}" if cle else "")
        rep = client.get(url, params={"detail": "nodata"})
        res.requetes += 1
        if garder_reponses:
            res.reponses.append((cle, rep))
        if rep.ok:
            return [s.attributs for s in analyser_donnees(rep.contenu)]
        if rep.statut == 404:
            return []
        if est_trop_volumineuse(rep) or (not parties and (nb_annonce or 0) > LIMITE_SERIES):
            return None
        res.erreurs.append(f"clé « {cle or '(toutes)'} » : HTTP {rep.statut} {rep.extrait(160)}")
        return []

    def decouper(parties: dict[str, list[str]], profondeur: int) -> list[dict[str, str]]:
        res.decoupages += 1
        if profondeur > 12:
            res.erreurs.append(f"découpage abandonné (profondeur) : {parties}")
            return []
        # 1. une dimension déjà restreinte à plusieurs codes : on coupe en deux
        for d in charger_dims():
            codes = parties.get(d.id)
            if codes and len(codes) > 1:
                m = len(codes) // 2
                return explorer({**parties, d.id: codes[:m]}, profondeur + 1) + explorer({**parties, d.id: codes[m:]}, profondeur + 1)
        # 2. première dimension libre (ordre de la clé) : par code, ou par paquets si la liste est longue
        for d in charger_dims():
            if parties.get(d.id):
                continue
            codes = codes_de(d)
            if not codes:
                continue
            taille = 1 if len(codes) <= 12 else min(60, math.ceil(len(codes) / 8))
            sortie: list[dict[str, str]] = []
            for i in range(0, len(codes), taille):
                sortie += explorer({**parties, d.id: codes[i:i + taille]}, profondeur + 1)
            return sortie
        res.erreurs.append(f"découpage impossible (toutes les dimensions fixées) : {parties}")
        return []

    def explorer(parties: dict[str, list[str]], profondeur: int = 0) -> list[dict[str, str]]:
        trouvees = interroger(parties)
        if trouvees is None:
            return decouper(parties, profondeur)
        return trouvees

    if nb_annonce is not None and nb_annonce > LIMITE_SERIES:
        note(f"    {dataflow} : {nb_annonce} séries annoncées > {LIMITE_SERIES}, découpage d'emblée")
        series = decouper({}, 0)
    else:
        series = explorer({})

    # dédoublonnage (un même idbank ne peut venir que d'une clé, mais par prudence)
    vus: dict[str, dict[str, str]] = {}
    for s in series:
        vus.setdefault(s.get("IDBANK", ""), s)
    res.series = list(vus.values())

    if avec_periodes and res.series:
        periodes = periodes_par_idbank([s["IDBANK"] for s in res.series], client)
        for s in res.series:
            p = periodes.get(s["IDBANK"])
            if p:
                s["PREMIERE_PERIODE"], s["DERNIERE_PERIODE"] = p.premiere, p.derniere
    return res


def lots(elements: list[str], taille: int) -> list[list[str]]:
    return [elements[i:i + taille] for i in range(0, len(elements), taille)]


def obtenir_series(
    idbanks: list[str],
    client,
    params: Optional[dict[str, str]] = None,
    taille_lot: int = LIMITE_IDBANKS,
    erreurs: Optional[list[str]] = None,
) -> list[SerieBdm]:
    """Séries par idbank (`SERIES_BDM/<id1>+<id2>…`), par lots ; un lot en échec est coupé en deux."""
    sortie: list[SerieBdm] = []
    for lot in lots(list(idbanks), max(1, min(taille_lot, LIMITE_IDBANKS))):
        sortie += _obtenir_lot(lot, client, params or {}, erreurs)
    return sortie


def _obtenir_lot(lot: list[str], client, params: dict[str, str], erreurs: Optional[list[str]]) -> list[SerieBdm]:
    rep = client.get(f"{URL_BASE}/data/SERIES_BDM/{'+'.join(lot)}", params=params or None)
    if rep.ok:
        return analyser_donnees(rep.contenu)
    if len(lot) > 1 and rep.statut != 404:
        m = len(lot) // 2
        return _obtenir_lot(lot[:m], client, params, erreurs) + _obtenir_lot(lot[m:], client, params, erreurs)
    if erreurs is not None:
        erreurs.append(f"SERIES_BDM ({len(lot)} idbank(s), {lot[0]}…) : HTTP {rep.statut} {rep.extrait(120)}")
    return []


def periodes_par_idbank(idbanks: list[str], client, erreurs: Optional[list[str]] = None) -> dict[str, ResumePeriodes]:
    """Première et dernière période non manquante de chaque série.

    Deux requêtes par lot (`firstNObservations=1`, `lastNObservations=3`) ; les séries dont ces
    observations sont toutes manquantes sont relues en entier.
    """
    premieres = {s.idbank: s for s in obtenir_series(idbanks, client, {"firstNObservations": "1"}, erreurs=erreurs)}
    dernieres = {s.idbank: s for s in obtenir_series(idbanks, client, {"lastNObservations": "3"}, erreurs=erreurs)}
    resultat: dict[str, ResumePeriodes] = {}
    a_relire: list[str] = []
    for idb in idbanks:
        p, d = premieres.get(idb), dernieres.get(idb)
        if p is None and d is None:
            continue
        rp = p.resume() if p else ResumePeriodes()
        rd = d.resume() if d else ResumePeriodes()
        if not rp.premiere or not rd.derniere:
            a_relire.append(idb)
            continue
        resultat[idb] = ResumePeriodes(premiere=rp.premiere, derniere=rd.derniere, statut_derniere=rd.statut_derniere)
    for s in obtenir_series(a_relire, client, taille_lot=25, erreurs=erreurs):
        resultat[s.idbank] = s.resume()
    return resultat


def obtenir_serie(idbank: str, client, params: Optional[dict[str, str]] = None) -> list[Ligne]:
    """Une série complète → lignes `serie_id, geo, periode, valeur, statut` (ordre chronologique)."""
    rep = client.get(f"{URL_BASE}/data/SERIES_BDM/{idbank}", params=params or None)
    _verifier(rep)
    return series_en_lignes(analyser_donnees(rep.contenu))
