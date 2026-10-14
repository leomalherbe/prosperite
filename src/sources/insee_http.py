"""Client HTTP commun aux voies d'accès INSEE (BDM, Melodi, fichiers insee.fr).

Rôle : identifier le projet (User-Agent), respecter un débit maximal par hôte,
reprendre automatiquement sur les erreurs transitoires (429, 5xx, coupures) et
renvoyer une réponse simple (statut, contenu, en-têtes) sans lever d'exception
pour les statuts « métier » (404 = aucun résultat, 413 = réponse trop volumineuse).

Le client est injectable : les modules `insee_bdm`, `insee_melodi` et
`insee_fichiers` acceptent tout objet ayant une méthode `get(url, params=None,
entetes=None) -> Reponse`. Les tests utilisent un faux client qui sert des
fixtures (aucun appel réseau dans les tests).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Mapping, NamedTuple, Optional
from urllib.parse import urlparse

AGENT = (
    "ObservatoireProsperite/0.2 (projet de recherche non commercial ; "
    "+https://github.com/leomalherbe/prosperite)"
)

#: Statuts HTTP pour lesquels une nouvelle tentative a du sens.
STATUTS_TRANSITOIRES = {429, 500, 502, 503, 504}


class Ligne(NamedTuple):
    """Format commun de sortie des séries (CLAUDE.md) : une observation par ligne."""

    serie_id: str
    geo: str
    periode: str
    valeur: Optional[float]
    statut: str


def est_manquante(valeur: object) -> bool:
    """Vrai si la valeur est absente ou vaut NaN (convention BDM : OBS_VALUE="NaN")."""
    if valeur is None:
        return True
    if isinstance(valeur, float):
        return valeur != valeur  # NaN
    texte = str(valeur).strip()
    return texte == "" or texte.lower() in {"nan", "na", "n/a"}


def en_nombre(valeur: object) -> Optional[float]:
    """Convertit une valeur d'observation en float, None si manquante ou illisible."""
    if est_manquante(valeur):
        return None
    try:
        return float(str(valeur).replace(",", ".")) if not isinstance(valeur, (int, float)) else float(valeur)
    except ValueError:
        return None


@dataclass
class Reponse:
    """Réponse HTTP réduite à ce dont les modules ont besoin."""

    statut: int
    contenu: bytes
    url: str
    entetes: Mapping[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return 200 <= self.statut < 300

    def texte(self, encodage: str = "utf-8") -> str:
        return self.contenu.decode(encodage, errors="replace")

    def extrait(self, n: int = 300) -> str:
        """Début du corps, sur une ligne (pour les journaux)."""
        return " ".join(self.texte()[:n].split())


class ErreurReseau(RuntimeError):
    """Échec définitif après toutes les tentatives (coupure, délai dépassé…)."""


class ClientHttp:
    """Client `requests` avec débit maximal par hôte et reprises.

    - `intervalles` : intervalle minimal (secondes) entre deux appels vers un même hôte,
      par ex. {"api.insee.fr": 2.1} pour rester sous 30 appels/minute (Melodi).
    - `essais` : nombre total de tentatives sur erreur transitoire ou coupure.
    - les délais d'attente entre tentatives croissent (10 s, 30 s, 90 s…) et
      respectent l'en-tête `Retry-After` quand il est présent.
    """

    def __init__(
        self,
        intervalles: Optional[Mapping[str, float]] = None,
        intervalle_defaut: float = 1.0,
        essais: int = 4,
        delai_connexion: float = 20.0,
        delai_lecture: float = 300.0,
        journal: Optional[Callable[[str], None]] = None,
        agent: str = AGENT,
    ) -> None:
        import requests  # import local : les tests n'en ont pas besoin

        self._requests = requests
        self.session = requests.Session()
        self.session.headers["User-Agent"] = agent
        self.session.headers["Accept-Encoding"] = "gzip, deflate"
        self.intervalles = dict(intervalles or {})
        self.intervalle_defaut = intervalle_defaut
        self.essais = max(1, essais)
        self.delais = (delai_connexion, delai_lecture)
        self.journal = journal or (lambda message: None)
        self._dernier_appel: dict[str, float] = {}
        self.nb_appels = 0
        self.nb_octets = 0

    def _patienter(self, hote: str) -> None:
        intervalle = self.intervalles.get(hote, self.intervalle_defaut)
        ecoule = time.monotonic() - self._dernier_appel.get(hote, 0.0)
        if ecoule < intervalle:
            time.sleep(intervalle - ecoule)
        self._dernier_appel[hote] = time.monotonic()

    def get(self, url: str, params: Optional[Mapping[str, str]] = None, entetes: Optional[Mapping[str, str]] = None) -> Reponse:
        hote = urlparse(url).netloc
        derniere_erreur = ""
        for tentative in range(1, self.essais + 1):
            self._patienter(hote)
            try:
                r = self.session.get(url, params=params, headers=dict(entetes or {}), timeout=self.delais)
            except self._requests.RequestException as exc:  # coupure, délai dépassé, TLS…
                derniere_erreur = f"{type(exc).__name__}: {exc}"
                attente = 10 * 3 ** (tentative - 1)
                self.journal(f"    réseau : {derniere_erreur[:200]} (tentative {tentative}/{self.essais}, attente {attente} s)")
                if tentative < self.essais:
                    time.sleep(attente)
                continue
            self.nb_appels += 1
            self.nb_octets += len(r.content)
            reponse = Reponse(statut=r.status_code, contenu=r.content, url=r.url, entetes=dict(r.headers))
            if r.status_code in STATUTS_TRANSITOIRES and tentative < self.essais:
                attente = _attente_retry_after(r.headers.get("Retry-After")) or 10 * 3 ** (tentative - 1)
                self.journal(f"    HTTP {r.status_code} sur {r.url[:160]} (tentative {tentative}/{self.essais}, attente {attente} s)")
                time.sleep(attente)
                continue
            return reponse
        raise ErreurReseau(f"{url} : {derniere_erreur}")


def _attente_retry_after(valeur: Optional[str]) -> Optional[int]:
    if not valeur:
        return None
    try:
        return max(1, min(600, int(float(valeur))))
    except ValueError:
        return None


class ClientFixtures:
    """Faux client pour les tests : associe une URL (ou un préfixe) à une réponse.

    `routes` : liste de (prédicat, réponse) où prédicat est une fonction
    (url_complete) -> bool ; la première route qui correspond est servie.
    Les URL demandées sont mémorisées dans `appels`.
    """

    def __init__(self, routes: list[tuple[Callable[[str], bool], Reponse]]) -> None:
        self.routes = routes
        self.appels: list[str] = []
        self.nb_appels = 0
        self.nb_octets = 0

    def get(self, url: str, params: Optional[Mapping[str, str]] = None, entetes: Optional[Mapping[str, str]] = None) -> Reponse:
        complete = url
        if params:
            complete += ("&" if "?" in url else "?") + "&".join(f"{k}={v}" for k, v in params.items())
        self.appels.append(complete)
        self.nb_appels += 1
        for predicat, reponse in self.routes:
            if predicat(complete):
                self.nb_octets += len(reponse.contenu)
                return Reponse(statut=reponse.statut, contenu=reponse.contenu, url=complete, entetes=reponse.entetes)
        return Reponse(statut=404, contenu=b"", url=complete)
