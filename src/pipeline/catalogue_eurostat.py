"""Construction des catalogues Eurostat (mission M02) — logique pure, testée hors ligne.

- Niveau 1 (jeux) : à partir du TOC, filtres (type, dates, fréquence), dossier prioritaire,
  étiquette `dimension_v0` par mots-clés, décision `candidat` motivée.
- Niveau 2 (séries) : à partir d'une réponse JSON-stat pour la France, rôle de chaque
  dimension (contenu, total fixé, ventilation, unité), séries « par défaut » (totaux,
  unité principale) et lignes de ventilation (D21), avec contrôle d'éligibilité
  (≥ 10 années renseignées depuis 2000, dernière ≥ 2020 : charte §3.4).
- Amorce : statut des séries Eurostat des prototypes.

Le script scripts/collecte_eurostat.py orchestre les appels réseau et la reprise.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Optional

import pandas as pd

from src.sources.eurostat import DimensionJsonStat, JeuJsonStat, StructureJeu

ANNEE_MIN = 2000          # profondeur temporelle (charte §2)
ANNEE_FIN_MIN = 2020      # dernière valeur ≥ 2020 (charte §3.4, fiche M02)
ANNEE_DEBUT_MAX = 2010    # filtre de la fiche M02 sur le début des données
NB_ANNEES_MIN = 10        # au moins 10 points depuis 2000 (charte §3.4)

DIMENSIONS_V0 = [
    "niveau_de_vie", "travail", "logement_cadre_vie", "sante", "education",
    "liens_bien_etre", "securite_confiance", "democratie", "egalites", "planete",
]

# ---------------------------------------------------------------- outils texte et périodes


def sans_accents(texte: str) -> str:
    texte = unicodedata.normalize("NFKD", texte or "")
    return "".join(c for c in texte if not unicodedata.combining(c)).lower()


def annee(periode) -> Optional[int]:
    m = re.match(r"\s*(\d{4})", str(periode or ""))
    return int(m.group(1)) if m else None


def frequence_periode(periode: str) -> str:
    """Fréquence déduite du format d'une période Eurostat (« 2020 », « 2020-Q1 », « 2020-01 »…)."""
    p = str(periode or "").strip()
    if re.fullmatch(r"\d{4}", p):
        return "annuelle"
    if re.fullmatch(r"\d{4}-S\d", p):
        return "semestrielle"
    if re.fullmatch(r"\d{4}-Q\d", p):
        return "trimestrielle"
    if re.fullmatch(r"\d{4}-\d{2}", p) or re.fullmatch(r"\d{4}M\d{2}", p):
        return "mensuelle"
    if re.fullmatch(r"\d{4}-W\d{2}", p):
        return "hebdomadaire"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p):
        return "journaliere"
    return ""


FREQUENCES_SDMX = {"A": "annuelle", "S": "semestrielle", "Q": "trimestrielle", "M": "mensuelle", "W": "hebdomadaire", "D": "journaliere", "H": "semestrielle"}
PERIODES_PAR_AN = {"annuelle": 1, "semestrielle": 2, "trimestrielle": 4, "mensuelle": 12, "hebdomadaire": 52, "journaliere": 365, "": 1}

# ---------------------------------------------------------------- niveau 1 : dossiers prioritaires

#: (libellé, motif sur le code du jeu, titres de dossier du TOC anglais, normalisés)
DOSSIERS_PRIORITAIRES = [
    ("sdg", r"^sdg_", ("sustainable development indicators", "sustainable development goals")),
    ("qualite_de_vie", r"^(qol|ilc_pw)", ("quality of life",)),
    ("revenus_conditions_de_vie", r"^ilc_", ("income and living conditions",)),
    ("marche_du_travail", r"^(lfs|une_|earn_)", ("labour market",)),
    ("sante", r"^hlth_", ("health",)),
    ("education_formation", r"^(educ_|trng_|edat_)", ("education and training",)),
    ("criminalite", r"^crim_", ("crime and criminal justice",)),
    ("environnement", r"^env_", ("environment",)),
    ("energie", r"^nrg_", ("energy",)),
    ("comptes_nationaux", r"^(nama_10_pc$|nasa_10_)", ()),
    ("population", r"^demo_", ()),
    ("numerique", r"^isoc_", ("digital economy and society",)),
    ("culture", r"^cult_", ("culture",)),
    ("securite_transports", r"^tran_sf_", ("transport safety",)),
]


def dossier_prioritaire(code: str, theme_source: str) -> str:
    """Nom du dossier prioritaire (fiche M02, A3) auquel appartient le jeu, ou chaîne vide."""
    code = (code or "").lower()
    dossiers = [sans_accents(t).strip() for t in (theme_source or "").split(" > ")]
    for nom, motif, titres in DOSSIERS_PRIORITAIRES:
        if re.search(motif, code):
            return nom
        for titre in titres:
            if any(d == titre or d.startswith(titre + " (") for d in dossiers):
                return nom
    return ""


# ---------------------------------------------------------------- niveau 1 : étiquetage par mots-clés

#: Mots-clés (sans accents, minuscules) ; chaque motif est précédé d'une frontière de mot.
#: Anglais (TOC en) et français (TOC fr). Un motif est une expression régulière.
MOTS_CLES = {
    "niveau_de_vie": [
        r"income", r"poverty", r"poor\b", r"depriv", r"gdp\b", r"gross domestic product", r"consumption expenditure",
        r"household consumption", r"final consumption", r"wealth", r"saving", r"debt", r"investment", r"purchasing power",
        r"price level", r"social protection", r"social benefit", r"social transfer", r"pension", r"minimum wage",
        r"make ends meet", r"financial burden", r"national income", r"living standard", r"standard of living",
        r"actual individual consumption", r"household budget", r"labour productivity",
        r"revenu", r"pauvrete", r"privation", r"\bpib\b", r"produit interieur brut", r"depenses de consommation",
        r"consommation (finale|des menages)", r"patrimoine", r"epargne", r"dette", r"investissement", r"pouvoir d'achat",
        r"protection sociale", r"prestations sociales", r"transferts sociaux", r"pension", r"niveau de vie",
        r"joindre les deux bouts",
    ],
    "travail": [
        r"employment", r"unemploy", r"employed", r"employee", r"labour market", r"labour force", r"labour cost",
        r"job", r"worker", r"working (time|hours|conditions|age)", r"hours (worked|of work)", r"earnings", r"wage",
        r"salar", r"part-time", r"temporary (employ|contract|job)", r"accidents at work", r"occupational", r"neet\b",
        r"not in employment", r"inactiv", r"activity rate", r"economic activity", r"self-employ", r"vacanc",
        r"in-work", r"labour status", r"health and safety at work", r"work accident", r"overtime", r"commut",
        r"emploi", r"chomage", r"chomeur", r"marche du travail", r"population active", r"travailleur", r"salaire",
        r"remuneration", r"gains", r"temps partiel", r"contrat temporaire", r"accidents? du travail", r"inactifs?",
        r"taux d'activite", r"heures (travaillees|de travail)",
    ],
    "logement_cadre_vie": [
        r"housing", r"dwelling", r"overcrowd", r"rooms?\b", r"accommodation", r"\brent", r"mortgage", r"keep (the )?home",
        r"warm", r"heating", r"energy poverty", r"noise", r"neighbourhood", r"green (space|area)", r"leaking roof",
        r"damp", r"bath or shower", r"toilet", r"tenure", r"homeless", r"passenger transport", r"modal split",
        r"public transport", r"mobility", r"access to (services|public)", r"urban", r"living environment",
        r"logement", r"surpeuplement", r"pieces?\b", r"loyer", r"chauff", r"precarite energetique", r"bruit",
        r"quartier", r"espaces? verts?", r"transport de (voyageurs|passagers)", r"transports? (publics?|en commun)",
        r"mobilite", r"sans-abri", r"cadre de vie", r"statut d'occupation",
    ],
    "sante": [
        r"health", r"life expectancy", r"mortality", r"death", r"causes of death", r"disease", r"illness", r"morbidity",
        r"hospital", r"medical", r"physician", r"doctor", r"nurse", r"smok", r"tobacco", r"alcohol", r"obes", r"overweight",
        r"body mass index", r"\bbmi\b", r"physical activit", r"depress", r"mental", r"suicide", r"activity limitation",
        r"healthy life", r"cancer", r"vaccinat", r"infant mortality", r"chronic", r"dental", r"pharmac", r"fruit",
        r"vegetable", r"drug", r"injur", r"disabilit", r"care (services|workers|beds)", r"long-term care", r"sick",
        r"sante", r"esperance de vie", r"mortalite", r"deces", r"maladie", r"hopit", r"medic", r"tabac", r"fumeur",
        r"alcool", r"obesite", r"surpoids", r"activite physique", r"depressi", r"mentale", r"suicide", r"handicap",
        r"limitation d'activite", r"bonne sante", r"soins", r"cancer", r"vaccin",
    ],
    "education": [
        r"education", r"educational", r"school", r"pupil", r"student", r"tertiary", r"early leavers", r"training",
        r"learning", r"skills", r"literacy", r"pisa\b", r"enrol", r"graduat", r"teacher", r"digital skills", r"internet",
        r"\bict\b", r"e-skills", r"culture", r"cultural", r"museum", r"reading", r"\bbooks?\b", r"language", r"lifelong",
        r"vocational", r"apprentic", r"isced", r"computer",
        r"education", r"enseignement", r"ecole", r"eleve", r"etudiant", r"superieur", r"sortie precoce",
        r"jeunes ayant quitte", r"formation", r"apprentissage", r"competence", r"scolari", r"diplome", r"culture",
        r"culturel", r"musee", r"lecture", r"langue", r"internet", r"ordinateur", r"numerique",
    ],
    "liens_bien_etre": [
        r"life satisfaction", r"satisf", r"happ(y|iness)", r"well-being", r"wellbeing", r"quality of life",
        r"social participation", r"social (relations|life|activities|support)", r"personal relationships",
        r"someone to (rely|ask|discuss)", r"lonel", r"leisure", r"time use", r"free time", r"volunt", r"meaning",
        r"worthwhile", r"feeling", r"work-life", r"friends", r"relatives", r"participation in (formal|informal|cultural|sport)",
        r"emotional", r"tension", r"sport",
        r"satisfaction", r"bien-etre", r"qualite de vie", r"participation sociale", r"relations", r"soutien",
        r"solitude", r"seul", r"loisirs", r"temps libre", r"benevol", r"emploi du temps", r"amis", r"sens de la vie",
    ],
    "securite_confiance": [
        r"crime", r"criminal", r"offence", r"homicide", r"violen", r"assault", r"robber", r"burglar", r"theft",
        r"police", r"prison", r"victim", r"safety", r"feel(ing)? safe", r"trust", r"road (accident|traffic|fatalit|death)",
        r"fatalit", r"persons killed", r"arrears", r"unexpected (financial )?expenses", r"insecur", r"vandalism",
        r"intentional", r"trafficking", r"sexual",
        r"criminalite", r"\bcrimes?\b", r"infraction", r"homicide", r"violence", r"agression", r"\bvols?\b", r"cambriol",
        r"police", r"prison", r"detenu", r"victime", r"securite routiere", r"sentiment de securite", r"confiance",
        r"accidents? de la route", r"\btues\b", r"arrieres", r"impayes", r"depenses imprevues", r"vandalisme",
    ],
    "democratie": [
        r"trust in (the )?(political|legal|police|institutions|parliament|government)", r"political", r"election",
        r"voting", r"\bvoter?s?\b", r"parliament", r"government", r"corruption", r"justice", r"judicial", r"courts?\b",
        r"civic", r"citizens' (participation|engagement)", r"seats", r"public authorities", r"e-government",
        r"rule of law", r"decision-making", r"governance",
        r"politique", r"election", r"\bvote\b", r"parlement", r"gouvernement", r"corruption", r"justice", r"judiciaire",
        r"tribunaux", r"citoyen", r"sieges", r"pouvoirs publics", r"administration en ligne", r"gouvernance",
    ],
    "egalites": [
        r"inequalit", r"gender", r"pay gap", r"employment gap", r"\bgaps?\b", r"quintile share", r"s80/s20",
        r"income share", r"\bgini\b", r"distribution of income", r"income distribution", r"dispersion", r"disparit",
        r"\bwomen\b", r"female", r"intergenerational", r"transmission of disadvantage", r"social mobility",
        r"discriminat", r"income quintile", r"top 10%", r"bottom 40%", r"relative median",
        r"inegalit", r"\bgenre\b", r"ecart", r"rapport interquintile", r"\bgini\b", r"distribution des revenus",
        r"repartition des revenus", r"dispersion", r"disparite", r"\bfemmes\b", r"intergenerationnel", r"mobilite sociale",
        r"discrimination",
    ],
    "planete": [
        r"emission", r"greenhouse", r"\bghg\b", r"carbon", r"\bco2\b", r"climat", r"air pollut", r"pollut",
        r"particulate", r"pm2", r"pm10", r"ozone", r"nitrogen", r"ammonia", r"phosph", r"pesticid", r"waste",
        r"recycl", r"circular", r"material (flow|footprint|consumption|productivity)", r"raw material",
        r"resource productivity", r"biodiversity", r"birds?\b", r"species", r"habitat", r"natura 2000",
        r"protected area", r"forest", r"land (use|cover|take|area)", r"\bsoil", r"erosion", r"sealing", r"artificial",
        r"water", r"freshwater", r"bathing", r"marine", r"fish", r"organic", r"environment", r"energy", r"renewable",
        r"fossil", r"electricity", r"fuel", r"footprint", r"ecosystem", r"drought", r"wildfire", r"eco-", r"nuclear",
        r"agri-environment", r"fertili", r"livestock", r"heat pump", r"vehicles?\b.*(emission|co2)",
        r"emissions?", r"effet de serre", r"carbone", r"climat", r"polluant", r"pollution", r"particules", r"azote",
        r"ammoniac", r"phosphore", r"pesticide", r"dechets", r"recyclage", r"circulaire", r"matieres", r"biodiversite",
        r"oiseaux", r"especes", r"habitats?", r"aires protegees", r"forets?", r"\bsols?\b", r"erosion", r"impermeabil",
        r"\beau\b", r"eaux", r"marin", r"poissons?", r"biologique", r"environnement", r"energ", r"renouvelable", r"fossile",
        r"electricite", r"combustible", r"empreinte", r"ecosysteme", r"secheresse",
    ],
}

#: Ordre de préférence en cas d'égalité de score (du plus spécifique au plus général).
ORDRE_DEPARTAGE = [
    "egalites", "securite_confiance", "democratie", "liens_bien_etre", "logement_cadre_vie",
    "sante", "education", "travail", "niveau_de_vie", "planete",
]

#: Repli par objectif de développement durable (codes sdg_XX_…).
ODD_DIMENSION = {
    "01": "niveau_de_vie", "02": "planete", "03": "sante", "04": "education", "05": "egalites", "06": "planete",
    "07": "planete", "08": "travail", "09": "niveau_de_vie", "10": "egalites", "11": "logement_cadre_vie",
    "12": "planete", "13": "planete", "14": "planete", "15": "planete", "16": "securite_confiance", "17": "niveau_de_vie",
}

#: Repli par dossier prioritaire.
DOSSIER_DIMENSION = {
    "qualite_de_vie": "liens_bien_etre", "revenus_conditions_de_vie": "niveau_de_vie", "marche_du_travail": "travail",
    "sante": "sante", "education_formation": "education", "criminalite": "securite_confiance",
    "environnement": "planete", "energie": "planete", "comptes_nationaux": "niveau_de_vie", "population": "sante",
    "numerique": "education", "culture": "education", "securite_transports": "securite_confiance",
}

_MOTIFS = {dim: [re.compile(r"(?<![a-z0-9])" + m) for m in motifs] for dim, motifs in MOTS_CLES.items()}


def _correspondances(texte: str) -> set[str]:
    texte = sans_accents(texte)
    return {dim for dim, motifs in _MOTIFS.items() if any(m.search(texte) for m in motifs)}


def decouper_titre(titre: str, separateur: str) -> tuple[str, str]:
    """Sépare « Indicateur by ventilations - source » en (indicateur, ventilations)."""
    t = titre or ""
    m = re.search(rf"\s{separateur}\s", t, flags=re.IGNORECASE)
    if not m:
        return t, ""
    return t[: m.start()], t[m.end():]


@dataclass
class Etiquette:
    dimension: str
    secondaires: list[str]
    methode: str
    scores: dict[str, float] = field(default_factory=dict)


def etiqueter(code: str, titre_en: str, titre_fr: str, theme_source: str, dossier: str = "") -> Etiquette:
    """Étiquette `dimension_v0` d'un jeu par mots-clés.

    Score par dimension : 2 si un mot-clé figure dans la partie principale du titre (avant
    « by » / « par »), 0,5 s'il ne figure que dans la partie « ventilations », 1 s'il figure
    dans le chemin de dossiers. Égalités départagées par ORDRE_DEPARTAGE. Sans aucun mot-clé :
    repli sur l'objectif ODD (sdg_XX), puis sur le dossier prioritaire.
    """
    principal_en, ventil_en = decouper_titre(titre_en, "by")
    principal_fr, ventil_fr = decouper_titre(titre_fr, "par")
    scores: dict[str, float] = defaultdict(float)
    for dim in _correspondances(principal_en + " | " + principal_fr):
        scores[dim] += 2
    for dim in _correspondances(ventil_en + " | " + ventil_fr):
        scores[dim] += 0.5
    for dim in _correspondances(theme_source):
        scores[dim] += 1
    if scores:
        meilleur = max(scores.values())
        ordre = sorted(scores, key=lambda d: (-scores[d], ORDRE_DEPARTAGE.index(d)))
        secondaires = [d for d in ordre[1:] if scores[d] >= 1]
        return Etiquette(ordre[0], secondaires, "mots-clés", dict(scores))
    m = re.match(r"sdg_(\d{2})", (code or "").lower())
    if m and m.group(1) in ODD_DIMENSION:
        return Etiquette(ODD_DIMENSION[m.group(1)], [], f"objectif ODD {m.group(1)}")
    if dossier in DOSSIER_DIMENSION:
        return Etiquette(DOSSIER_DIMENSION[dossier], [], f"dossier {dossier}")
    return Etiquette("", [], "aucun mot-clé")


# ---------------------------------------------------------------- niveau 1 : catalogue des jeux

COLONNES_JEUX = [
    "source", "serie_id", "libelle", "unite", "frequence", "geo", "premiere_periode", "derniere_periode",
    "derniere_maj", "theme_source", "dimension_v0", "candidat", "commentaire",
    "code_jeu", "libelle_en", "type", "nb_valeurs", "derniere_modif_structure", "theme_codes", "autres_chemins",
    "dossier_prioritaire", "dimensions_v0_secondaires", "methode_etiquette", "filtre_toc", "motif_candidat",
    "statut_niveau2", "nb_series_fr", "nb_series_candidates", "structure_fr",
]


def filtre_dates(debut: str, fin: str, frequence: str) -> tuple[str, bool]:
    """Applique les filtres de la fiche (fin ≥ 2020, début ≤ 2010) ; renvoie (motif, rattrapable).

    `rattrapable` : début > 2010 mais ≥ 10 périodes annuelles possibles jusqu'à la fin
    (critère de la charte §3.4) — le jeu peut alors être repêché s'il est pertinent.
    """
    a_debut, a_fin = annee(debut), annee(fin)
    if a_debut is None or a_fin is None:
        return "exclu : dates absentes du TOC", False
    if a_fin < ANNEE_FIN_MIN:
        return f"exclu : fin des données {a_fin} < {ANNEE_FIN_MIN}", False
    if a_debut > ANNEE_DEBUT_MAX:
        rattrapable = a_fin - max(a_debut, ANNEE_MIN) + 1 >= NB_ANNEES_MIN
        return f"hors filtre : début des données {a_debut} > {ANNEE_DEBUT_MAX}", rattrapable
    return "retenu", False


def construire_catalogue_jeux(toc_en: pd.DataFrame, toc_fr: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Catalogue niveau 1 : un jeu (type = dataset) par ligne, dédoublonné par code.

    Le chemin principal est celui de la « Database by themes » (racine `data`) s'il existe ;
    les autres emplacements du même code sont listés dans `autres_chemins`.
    Règle `candidat` :
      - non si le jeu échoue aux filtres de dates (sauf rattrapage ci-dessous) ou s'il est infra-annuel ;
      - oui s'il est dans un dossier prioritaire, ou si un mot-clé du titre le rattache à une dimension v0 ;
      - rattrapage (oui) : début > 2010 mais ≥ 10 années possibles jusqu'à la fin, et pertinent (dossier ou mot-clé).
    """
    jeux = toc_en[toc_en["type"] == "dataset"].copy()
    titres_fr = {}
    if toc_fr is not None and len(toc_fr):
        for code, titre in zip(toc_fr["code"], toc_fr["titre"]):
            titres_fr.setdefault(code, titre)
    lignes = []
    for code, groupe in jeux.groupby("code", sort=False):
        groupe = groupe.reset_index(drop=True)
        principal_idx = next((i for i, c in enumerate(groupe["theme_codes"]) if c.startswith("data")), 0)
        p = groupe.iloc[principal_idx]
        autres = [c for i, c in enumerate(groupe["theme_source"]) if i != principal_idx]
        titre_fr = titres_fr.get(code, "") or p["titre"]
        frequence = frequence_periode(p["debut"]) or frequence_periode(p["fin"])
        tous_chemins = " | ".join(groupe["theme_source"])
        dossier = dossier_prioritaire(code, tous_chemins.replace(" | ", " > "))
        etiquette = etiqueter(code, p["titre"], titre_fr, p["theme_source"], dossier)
        filtre, rattrapable = filtre_dates(p["debut"], p["fin"], frequence)
        pertinent = bool(dossier) or etiquette.methode == "mots-clés"
        if frequence and frequence != "annuelle":
            candidat, motif = "non", f"infra-annuel ({frequence}) : une version annuelle existe en général"
        elif filtre == "retenu" and dossier:
            candidat, motif = "oui", f"dossier prioritaire ({dossier})"
        elif filtre == "retenu" and etiquette.methode == "mots-clés":
            candidat, motif = "oui", f"mots-clés ({etiquette.dimension})"
        elif filtre == "retenu":
            candidat, motif = "non", "aucun mot-clé ni dossier prioritaire"
        elif rattrapable and pertinent:
            candidat, motif = "oui", "rattrapage : début > 2010 mais ≥ 10 années possibles (charte §3.4) ; " + (
                f"dossier prioritaire ({dossier})" if dossier else f"mots-clés ({etiquette.dimension})")
        else:
            candidat, motif = "non", filtre
        lignes.append(
            {
                "source": "Eurostat",
                "serie_id": code,
                "libelle": titre_fr,
                "unite": "",
                "frequence": frequence,
                "geo": "",
                "premiere_periode": p["debut"],
                "derniere_periode": p["fin"],
                "derniere_maj": p["derniere_maj"],
                "theme_source": p["theme_source"],
                "dimension_v0": etiquette.dimension,
                "candidat": candidat,
                "commentaire": motif,
                "code_jeu": code,
                "libelle_en": p["titre"],
                "type": "dataset",
                "nb_valeurs": p["nb_valeurs"],
                "derniere_modif_structure": p["derniere_modif_structure"],
                "theme_codes": p["theme_codes"],
                "autres_chemins": " | ".join(autres),
                "dossier_prioritaire": dossier,
                "dimensions_v0_secondaires": " ; ".join(etiquette.secondaires),
                "methode_etiquette": etiquette.methode,
                "filtre_toc": filtre,
                "motif_candidat": motif,
                "statut_niveau2": "",
                "nb_series_fr": "",
                "nb_series_candidates": "",
                "structure_fr": "",
            }
        )
    return pd.DataFrame(lignes, columns=COLONNES_JEUX)


def bilan_dossiers(toc_en: pd.DataFrame, catalogue: pd.DataFrame, toc_fr: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Une ligne par dossier du TOC : chemin, nombre de jeux dessous, après filtres, candidats."""
    dossiers = toc_en[toc_en["type"] == "folder"].drop_duplicates("code")
    titres_fr = dict(zip(toc_fr["code"], toc_fr["titre"])) if toc_fr is not None else {}
    jeux = toc_en[toc_en["type"] == "dataset"][["code", "theme_codes"]]
    statut = catalogue.set_index("code_jeu")
    lignes = []
    for _, d in dossiers.iterrows():
        chemin_codes = (d["theme_codes"] + " > " + d["code"]).strip(" >")
        dessous = jeux[(jeux["theme_codes"] == chemin_codes) | jeux["theme_codes"].str.startswith(chemin_codes + " > ")]
        codes = sorted(set(dessous["code"]))
        sous = statut.loc[[c for c in codes if c in statut.index]]
        lignes.append(
            {
                "code_dossier": d["code"],
                "titre_en": d["titre"],
                "titre_fr": titres_fr.get(d["code"], ""),
                "profondeur": d["profondeur"],
                "chemin": (d["theme_source"] + " > " + d["titre"]).strip(" >"),
                "nb_jeux": len(codes),
                "nb_jeux_filtres": int((sous["filtre_toc"] == "retenu").sum()) if len(sous) else 0,
                "nb_candidats": int((sous["candidat"] == "oui").sum()) if len(sous) else 0,
            }
        )
    return pd.DataFrame(lignes)


# ---------------------------------------------------------------- niveau 2 : rôles des dimensions

CODES_TOTAL = ("TOTAL", "T", "_T", "TOT", "ALL", "TOTAL_HH")
CODES_TOTAL_PAR_DIMENSION = {"wstatus": ("POP", "TOTAL"), "sex": ("T",), "age": ("TOTAL",)}

#: Dimensions de ventilation conservées en lignes séparées (D21) et leur libellé.
VENTILATIONS = {
    "sex": "sexe", "age": "âge", "quantile": "quantile de revenu", "quant_inc": "quintile de revenu",
    "incgrp": "groupe de revenu", "quant_expn": "quintile de dépenses", "hhtyp": "type de ménage",
    "hhcomp": "composition du ménage", "deg_urb": "degré d'urbanisation",
}
PREFIXES_VENTILATION = {"isced": "niveau d'éducation"}

DIMENSIONS_TECHNIQUES = {"freq", "geo", "unit", "time", "TIME_PERIOD"}


def est_ventilation(dim: str) -> bool:
    return dim in VENTILATIONS or any(dim.startswith(p) for p in PREFIXES_VENTILATION)


def libelle_ventilation(dim: str) -> str:
    if dim in VENTILATIONS:
        return VENTILATIONS[dim]
    return next((v for p, v in PREFIXES_VENTILATION.items() if dim.startswith(p)), dim)


def code_total(dim: str, codes: Iterable[str]) -> Optional[str]:
    codes = list(codes)
    for candidat in CODES_TOTAL_PAR_DIMENSION.get(dim, ()) + CODES_TOTAL:
        if candidat in codes:
            return candidat
    return None


_AGE = re.compile(r"^Y(?:_?(GE|LT|LE|GT))?(\d+)(?:-(\d+))?$")


def intervalle_age(code: str) -> Optional[tuple[int, int, bool]]:
    """(début, fin, âge_unique) d'un code d'âge Eurostat ; None si non interprétable.

    TOTAL → (0, 150) ; Y_GE65 → (65, 150) ; Y_LT18 → (0, 17) ; Y15-64 → (15, 64) ; Y25 → (25, 25, unique).
    """
    if code == "TOTAL":
        return 0, 150, False
    m = _AGE.match(code or "")
    if not m:
        return None
    op, a, b = m.group(1), int(m.group(2)), m.group(3)
    if op in ("GE",):
        return a, 150, False
    if op == "GT":
        return a + 1, 150, False
    if op == "LT":
        return 0, a - 1, False
    if op == "LE":
        return 0, a, False
    if b is not None:
        return a, int(b), False
    return a, a, True


def age_par_defaut(codes: Iterable[str], titre: str = "") -> Optional[str]:
    """`TOTAL` s'il existe, sinon la classe d'âge la plus large (à la naissance pour une espérance de vie)."""
    codes = list(codes)
    if "TOTAL" in codes:
        return "TOTAL"
    t = sans_accents(titre)
    if "life expectancy" in t or "esperance de vie" in t:
        for c in ("Y_LT1", "Y0", "Y_LT01"):
            if c in codes:
                return c
    meilleurs = []
    for c in codes:
        iv = intervalle_age(c)
        if iv and not iv[2]:
            meilleurs.append((iv[1] - iv[0], -iv[0], c))
    if meilleurs:
        return max(meilleurs)[2]
    return codes[0] if codes else None


def score_unite(code: str) -> tuple[int, str]:
    """Rang de préférence d'une unité (plus petit = préféré) : taux et parts, puis par habitant,
    années, indices, niveaux absolus ; les variations (PCH…) en dernier."""
    c = code.upper()
    if "PCH" in c or c.startswith("CH_") or "_CH_" in c or c.endswith("_CH"):
        rang = 9
    elif c.startswith("PC") or c in ("PERCENT", "PC_POP"):
        rang = 0
    elif c.startswith("RT") or "_RT" in c or c.startswith("P_") or "HAB" in c or "_PER_" in c or c.endswith("_PER") and not c.startswith("THS"):
        rang = 1
    elif c in ("YR", "NR_YR", "RAT", "RATIO", "IDX", "AVG"):
        rang = 2
    elif re.match(r"^(I|IDX)\d", c) or c.startswith("I_"):
        rang = 4
    elif c.startswith(("THS", "MIO", "NR", "BN", "MIL", "T", "TJ", "KTOE", "GWH")):
        rang = 6
    else:
        rang = 3
    return rang, c


def choisir_unite(codes: Iterable[str]) -> Optional[str]:
    codes = list(codes)
    return min(codes, key=score_unite) if codes else None


@dataclass
class Roles:
    """Rôle de chaque dimension hors temps d'une réponse JSON-stat FR."""

    ordre: list[str]
    defauts: dict[str, str]          # dimension → modalité par défaut (dimensions fixées, ventilations, freq, geo)
    contenu: list[str]               # dimensions énumérées (chaque modalité = un indicateur distinct)
    ventilations: list[str]          # dimensions de ventilation (ayant une modalité par défaut)
    unite: Optional[str]             # id de la dimension unité ('unit') si présente

    def description(self, jeu: JeuJsonStat) -> str:
        parties = []
        for d in jeu.dimensions_hors_temps:
            n = len(d.codes)
            if d.id == self.unite:
                parties.append(f"{d.id} ({n}) [unité]")
            elif d.id in self.contenu:
                parties.append(f"{d.id} ({n}) [contenu]")
            elif d.id in self.ventilations:
                parties.append(f"{d.id}→{self.defauts[d.id]} ({n}) [ventilation]")
            else:
                parties.append(f"{d.id}→{self.defauts.get(d.id, '?')} ({n}) [fixé]")
        return " ; ".join(parties)


def attribuer_roles(jeu: JeuJsonStat, codes_avec_donnees: dict[str, set[str]], defauts_imposes: Optional[dict] = None) -> Roles:
    """Rôle des dimensions : `freq`/`geo` fixés ; `unit` choisie série par série ; âge fixé à TOTAL
    ou à la classe la plus large ; une dimension ayant un code total est fixée à ce total
    (ventilation si c'est sexe, âge, quantile, type de ménage, niveau d'éducation, degré
    d'urbanisation) ; une dimension à une seule modalité est fixée ; les autres sont du contenu.
    `codes_avec_donnees` : modalités ayant au moins une observation, par dimension."""
    defauts_imposes = dict(defauts_imposes or {})
    ordre = [d.id for d in jeu.dimensions_hors_temps]
    defauts: dict[str, str] = {}
    contenu, ventilations = [], []
    unite = "unit" if "unit" in ordre else None
    for d in jeu.dimensions_hors_temps:
        codes = [c for c in d.codes if c in codes_avec_donnees.get(d.id, set())] or list(d.codes)
        if d.id == unite and d.id not in defauts_imposes:
            continue
        if d.id in defauts_imposes:
            defauts[d.id] = defauts_imposes[d.id]
            if est_ventilation(d.id) and len(codes) > 1:
                ventilations.append(d.id)
            continue
        if d.id == "freq":
            defauts[d.id] = "A" if "A" in codes else codes[0]
            continue
        if d.id == "geo":
            defauts[d.id] = "FR" if "FR" in codes else ("FX" if "FX" in codes else codes[0])
            continue
        total = age_par_defaut(codes, jeu.libelle) if d.id == "age" else code_total(d.id, codes)
        if len(codes) == 1:
            defauts[d.id] = codes[0]
        elif total is not None:
            defauts[d.id] = total
            if est_ventilation(d.id):
                ventilations.append(d.id)
        else:
            contenu.append(d.id)
    if unite in defauts_imposes:
        unite = None
    return Roles(ordre, defauts, contenu, ventilations, unite)


# ---------------------------------------------------------------- niveau 2 : séries

COLONNES_SERIES = [
    "source", "serie_id", "libelle", "unite", "frequence", "geo", "premiere_periode", "derniere_periode",
    "derniere_maj", "theme_source", "dimension_v0", "candidat", "commentaire",
    "code_jeu", "libelle_jeu", "type_ligne", "ventilation", "modalites", "libelles_modalites", "unite_code",
    "unites_disponibles", "nb_points", "nb_annees", "derniere_valeur", "drapeaux", "modalites_ventilation",
    "jeu_source", "date_verification",
]


@dataclass
class StatSerie:
    nb_points: int
    annees: set
    premiere: str
    derniere: str
    derniere_valeur: float
    drapeaux: Counter

    @property
    def nb_annees(self) -> int:
        return len(self.annees)

    @property
    def derniere_annee(self) -> Optional[int]:
        return annee(self.derniere)


def statistiques(points: list[tuple[str, float, str]], annee_min: int = ANNEE_MIN) -> Optional[StatSerie]:
    pts = sorted((p for p in points if (annee(p[0]) or 0) >= annee_min), key=lambda p: p[0])
    if not pts:
        return None
    return StatSerie(
        nb_points=len(pts),
        annees={annee(p[0]) for p in pts},
        premiere=pts[0][0],
        derniere=pts[-1][0],
        derniere_valeur=pts[-1][1],
        drapeaux=Counter(p[2] for p in pts if p[2]),
    )


def eligibilite(stat: StatSerie) -> tuple[str, str]:
    """('oui', '') si ≥ 10 années renseignées depuis 2000 et dernière ≥ 2020 ; sinon ('non', motif)."""
    motifs = []
    if stat.nb_annees < NB_ANNEES_MIN:
        motifs.append(f"{stat.nb_annees} années renseignées depuis {ANNEE_MIN} (< {NB_ANNEES_MIN})")
    if (stat.derniere_annee or 0) < ANNEE_FIN_MIN:
        motifs.append(f"dernière période {stat.derniere} < {ANNEE_FIN_MIN}")
    return ("non", " ; ".join(motifs)) if motifs else ("oui", "")


def texte_drapeaux(compteur: Counter) -> str:
    return " ; ".join(f"{k}:{v}" for k, v in sorted(compteur.items())) if compteur else ""


def regrouper_series(jeu: JeuJsonStat) -> dict[tuple[str, ...], list[tuple[str, float, str]]]:
    series: dict[tuple[str, ...], list] = defaultdict(list)
    for codes, periode, valeur, statut in jeu.observations:
        series[codes].append((periode, valeur, statut))
    return series


@dataclass
class ContexteJeu:
    """Informations de niveau 1 recopiées dans les lignes de séries."""

    theme_source: str = ""
    dimension_v0: str = ""
    date_verification: str = ""


def construire_series(
    jeu: JeuJsonStat,
    contexte: Optional[ContexteJeu] = None,
    defauts_imposes: Optional[dict] = None,
    annee_min: int = ANNEE_MIN,
) -> tuple[list[dict], Roles]:
    """Lignes du catalogue niveau 2 pour un jeu (réponse JSON-stat filtrée sur la France).

    Une ligne `defaut` par combinaison des dimensions de contenu (dimensions fixées à leur
    défaut, unité principale parmi celles qui ont des données pour cette combinaison) ;
    une ligne `ventilation` par dimension de ventilation offrant d'autres modalités avec
    données, les autres dimensions restant à leur défaut. Toutes les séries écrites ont été
    lues dans la réponse (aucune combinaison théorique).
    """
    contexte = contexte or ContexteJeu()
    series = regrouper_series(jeu)
    ordre = [d.id for d in jeu.dimensions_hors_temps]
    dims = {d.id: d for d in jeu.dimensions_hors_temps}
    libelles = {d.id: d.libelles for d in jeu.dimensions_hors_temps}
    libelles_dims = {d.id: (d.libelle or d.id) for d in jeu.dimensions_hors_temps}
    avec_donnees: dict[str, set[str]] = defaultdict(set)
    for codes in series:
        for dim, c in zip(ordre, codes):
            avec_donnees[dim].add(c)
    roles = attribuer_roles(jeu, avec_donnees, defauts_imposes)
    rang = {d: i for i, d in enumerate(ordre)}
    fixes = dict(roles.defauts)

    def aux_defauts(codes: tuple[str, ...], sauf: str = "") -> bool:
        return all(codes[rang[d]] == v for d, v in fixes.items() if d != sauf)

    # combinaisons de contenu → unités disponibles (sur les séries aux défauts)
    par_contenu: dict[tuple[str, ...], dict[str, tuple[str, ...]]] = defaultdict(dict)
    for codes in series:
        if aux_defauts(codes):
            cle = tuple(codes[rang[d]] for d in roles.contenu)
            par_contenu[cle][codes[rang[roles.unite]] if roles.unite else ""] = codes
    # index des ventilations : (dimension, clé sans cette dimension) → [(modalité, codes)]
    index_v: dict[tuple[str, tuple], list[tuple[str, tuple[str, ...]]]] = defaultdict(list)
    for v in roles.ventilations:
        for codes in series:
            c = codes[rang[v]]
            if c == fixes[v] or not aux_defauts(codes, sauf=v):
                continue
            if v == "age" and (intervalle_age(c) or (0, 0, False))[2]:
                continue  # âges détaillés année par année : non retenus
            index_v[(v, codes[: rang[v]] + codes[rang[v] + 1:])].append((c, codes))
    plusieurs = [d for d in roles.contenu if len(avec_donnees[d]) > 1]
    lignes = []
    for cle in sorted(par_contenu):
        unites = par_contenu[cle]
        u = choisir_unite([x for x in unites if x]) if roles.unite else ""
        codes = unites[u]
        stat = statistiques(series[codes], annee_min)
        if stat is None:
            continue
        code_unite = codes[rang["unit"]] if "unit" in rang else ""
        candidat, motif = eligibilite(stat)
        details = [libelles[d].get(codes[rang[d]], codes[rang[d]]) for d in plusieurs]
        libelle = jeu.libelle + (" — " + " ; ".join(details) if details else "")
        freq = FREQUENCES_SDMX.get(codes[rang["freq"]], "") if "freq" in rang else frequence_periode(stat.derniere)
        base = {
            "source": "Eurostat",
            "serie_id": jeu.serie_id(codes),
            "libelle": libelle,
            "unite": libelles["unit"].get(code_unite, code_unite) if code_unite else "",
            "frequence": freq,
            "geo": codes[rang["geo"]] if "geo" in rang else "",
            "premiere_periode": stat.premiere,
            "derniere_periode": stat.derniere,
            "derniere_maj": (jeu.mise_a_jour or "")[:10],
            "theme_source": contexte.theme_source,
            "dimension_v0": contexte.dimension_v0,
            "candidat": candidat,
            "commentaire": motif,
            "code_jeu": jeu.code,
            "libelle_jeu": jeu.libelle,
            "type_ligne": "defaut",
            "ventilation": "",
            "modalites": " ; ".join(f"{d}={c}" for d, c in zip(ordre, codes)),
            "libelles_modalites": " ; ".join(
                f"{libelles_dims[d]} : {libelles[d].get(c, c)}" for d, c in zip(ordre, codes) if d != "geo"),
            "unite_code": code_unite,
            "unites_disponibles": " ; ".join(sorted(x for x in unites if x)),
            "nb_points": stat.nb_points,
            "nb_annees": stat.nb_annees,
            "derniere_valeur": stat.derniere_valeur,
            "drapeaux": texte_drapeaux(stat.drapeaux),
            "modalites_ventilation": "",
            "jeu_source": jeu.jeu_source,
            "date_verification": contexte.date_verification,
        }
        lignes.append(base)
        # ventilations : une ligne par dimension, avec la couverture de chaque modalité
        for v in roles.ventilations:
            candidats_v = index_v.get((v, codes[: rang[v]] + codes[rang[v] + 1:]), [])
            stats_v = [(c, s) for c, autre in candidats_v if (s := statistiques(series[autre], annee_min)) is not None]
            if not stats_v:
                continue
            ordre_codes = {c: i for i, c in enumerate(dims[v].codes)}
            stats_v.sort(key=lambda cs: ordre_codes.get(cs[0], 0))
            nb_ok = sum(1 for _, s in stats_v if eligibilite(s)[0] == "oui")
            cle_v: list = list(codes)
            cle_v[rang[v]] = [c for c, _ in stats_v]
            ligne = dict(base)
            ligne.update(
                {
                    "serie_id": jeu.serie_id(tuple(cle_v)),
                    "libelle": libelle + f" — par {libelle_ventilation(v)}",
                    "candidat": "ventilation",
                    "commentaire": (f"{len(stats_v)} modalités de {v} hors défaut ({fixes[v]}), dont {nb_ok} "
                                    f"éligibles (≥ {NB_ANNEES_MIN} années, fin ≥ {ANNEE_FIN_MIN})"),
                    "type_ligne": "ventilation",
                    "ventilation": v,
                    "modalites": " ; ".join(f"{d}={'+'.join(c) if isinstance(c, list) else c}" for d, c in zip(ordre, cle_v)),
                    "libelles_modalites": " ; ".join(f"{c}={libelles[v].get(c, c)}" for c, _ in stats_v),
                    "premiere_periode": min(s.premiere for _, s in stats_v),
                    "derniere_periode": max(s.derniere for _, s in stats_v),
                    "nb_points": min(s.nb_points for _, s in stats_v),
                    "nb_annees": min(s.nb_annees for _, s in stats_v),
                    "derniere_valeur": "",
                    "drapeaux": texte_drapeaux(sum((s.drapeaux for _, s in stats_v), Counter())),
                    "modalites_ventilation": " ; ".join(f"{c}:{s.premiere}-{s.derniere}:{s.nb_annees}" for c, s in stats_v),
                }
            )
            lignes.append(ligne)
    return lignes, roles


def codes_de_ligne(ligne: dict) -> tuple[str, ...]:
    """Codes (ordre des dimensions) d'une ligne `defaut`, relus dans la colonne `modalites`."""
    return tuple(x.split("=", 1)[1] for x in ligne["modalites"].split(" ; "))


# ---------------------------------------------------------------- niveau 2 : plan de requêtes

def estimer_cellules(structure: StructureJeu, fixes: dict[str, list[str]], nb_periodes: int) -> int:
    """Taille majorée du cube demandé : produit des modalités (structure, tous pays) × périodes."""
    total = max(nb_periodes, 1)
    for d in structure.dimensions:
        if d.id in fixes:
            total *= max(len(fixes[d.id]), 1)
        else:
            total *= max(len(d.modalites), 1)
    return total


def planifier_requetes(
    structure: StructureJeu,
    geo: str,
    frequence: Optional[str],
    nb_periodes: int,
    seuil: int = 300_000,
    max_requetes: int = 60,
) -> tuple[list[dict], str]:
    """Filtres des requêtes JSON-stat nécessaires pour lire toutes les séries FR utiles d'un jeu.

    1. geo et freq fixés ; si le cube majoré dépasse `seuil` cellules :
    2. les dimensions ayant un total (hors ventilations) sont fixées à leur total ;
    3. puis découpage de la plus grande dimension restante en paquets (repeated params).
    Renvoie (liste de filtres, note explicative).
    """
    fixes: dict[str, list[str]] = {"geo": [geo]}
    if frequence and structure.dimension("freq") is not None:
        fixes["freq"] = [frequence]
    notes = []
    if estimer_cellules(structure, fixes, nb_periodes) > seuil:
        for d in structure.dimensions:
            if d.id in fixes or d.id == "unit" or est_ventilation(d.id):
                continue
            total = code_total(d.id, d.modalites)
            if total:
                fixes[d.id] = [total]
        notes.append("dimensions à total fixées à la requête (jeu volumineux)")
    taille = estimer_cellules(structure, fixes, nb_periodes)
    if taille <= seuil:
        return [{k: (v[0] if len(v) == 1 else v) for k, v in fixes.items()}], " ; ".join(notes)
    libres = [d for d in structure.dimensions if d.id not in fixes and len(d.modalites) > 1]
    if not libres:
        return [{k: v[0] for k, v in fixes.items()}], " ; ".join(notes)
    grande = max(libres, key=lambda d: len(d.modalites))
    codes = list(grande.modalites)
    par_paquet = max(1, int(len(codes) * seuil / taille))
    par_paquet = min(par_paquet, 40)  # longueur d'URL raisonnable
    paquets = [codes[i:i + par_paquet] for i in range(0, len(codes), par_paquet)]
    if len(paquets) > max_requetes:
        notes.append(f"découpage limité à {max_requetes} requêtes sur {len(paquets)} nécessaires ({grande.id})")
        paquets = paquets[:max_requetes]
    else:
        notes.append(f"découpage en {len(paquets)} requêtes sur {grande.id}")
    filtres = []
    for paquet in paquets:
        f = {k: (v[0] if len(v) == 1 else v) for k, v in fixes.items()}
        f[grande.id] = paquet
        filtres.append(f)
    return filtres, " ; ".join(notes)


def fusionner_jeux(jeux: list[JeuJsonStat]) -> Optional[JeuJsonStat]:
    """Réunit les réponses de plusieurs requêtes sur un même jeu (dimensions alignées par codes)."""
    jeux = [j for j in jeux if j is not None]
    if not jeux:
        return None
    if len(jeux) == 1:
        return jeux[0]
    premier = jeux[0]
    dims = []
    for k, d in enumerate(premier.dimensions):
        codes, libs = [], {}
        for j in jeux:
            dj = j.dimensions[k]
            for c in dj.codes:
                if c not in libs:
                    codes.append(c)
                    libs[c] = dj.libelles.get(c, c)
        dims.append(DimensionJsonStat(d.id, d.libelle, codes, libs))
    observations = [o for j in jeux for o in j.observations]
    return JeuJsonStat(premier.code, premier.libelle, max(j.mise_a_jour for j in jeux), dims, premier.dimension_temps, observations, premier.annotations)


# ---------------------------------------------------------------- amorce (séries des prototypes)

COLONNES_AMORCE = [
    "id_prototype", "dimension_prototype", "libelle_prototype", "code_eurostat", "statut", "nouveau_code",
    "libelle_eurostat_fr", "premiere_periode_fr", "derniere_periode_fr", "nb_periodes_fr", "unite_par_defaut",
    "unites_disponibles", "dimensions_du_jeu", "ventilations_utiles", "jeu_source", "derniere_maj", "drapeaux",
    "date_verification", "commentaire",
]

SEPARATEUR_ROBOT = " || robot : "


def ligne_amorce(proto: dict, jeu: Optional[JeuJsonStat], erreur: str = "", defauts: Optional[dict] = None, date: str = "", present_toc: Optional[bool] = None) -> dict:
    """Ligne de `docs/sources/eurostat_amorce_prototypes.csv` pour une série de prototype.

    `proto` : ligne de docs/archives/prototypes_indicateurs.csv (+ éventuel `commentaire_manuel`).
    Statuts : disponible ; disponible (série courte) ; sans donnée FR ; à remplacer (code absent).
    """
    ligne = {c: "" for c in COLONNES_AMORCE}
    ligne.update(
        {
            "id_prototype": proto["id_prototype"],
            "dimension_prototype": proto["dimension_prototype"],
            "libelle_prototype": proto.get("libelle", proto.get("libelle_prototype", "")),
            "code_eurostat": proto["code_source"],
            "date_verification": date,
        }
    )
    manuel = proto.get("commentaire_manuel", "")
    notes = []
    if jeu is None:
        if present_toc is False:
            ligne["statut"] = "à remplacer"
            notes.append(f"code absent du TOC et de l'API ({erreur})")
        else:
            ligne["statut"] = "sans donnée FR"
            notes.append(erreur or "aucune donnée pour la France")
        ligne["commentaire"] = (manuel + SEPARATEUR_ROBOT if manuel else "robot : ") + " ; ".join(notes)
        return ligne
    series = regrouper_series(jeu)
    ordre = [d.id for d in jeu.dimensions_hors_temps]
    avec: dict[str, set[str]] = defaultdict(set)
    for codes in series:
        for d, c in zip(ordre, codes):
            avec[d].add(c)
    lignes, roles = construire_series(jeu, defauts_imposes=defauts, annee_min=0)
    defaut = next((l for l in lignes if l["type_ligne"] == "defaut"), None)
    ligne["libelle_eurostat_fr"] = jeu.libelle
    ligne["dimensions_du_jeu"] = " ; ".join(d.id for d in jeu.dimensions)
    ligne["jeu_source"] = jeu.jeu_source
    ligne["derniere_maj"] = (jeu.mise_a_jour or "")[:10]
    unites = sorted(avec.get("unit", set()))
    ligne["unites_disponibles"] = " ; ".join(unites)
    dims = {d.id: d for d in jeu.dimensions_hors_temps}
    ventil = [f"{d} ({' ; '.join(c for c in dims[d].codes if c in avec[d])})"
              for d in ordre if d not in DIMENSIONS_TECHNIQUES and len(avec[d]) > 1]
    ligne["ventilations_utiles"] = " ; ".join(ventil) if ventil else "aucune dans la vue"
    if defaut is None:
        ligne["statut"] = "sans donnée FR"
        notes.append("aucune série aux modalités par défaut")
    else:
        ligne["premiere_periode_fr"] = defaut["premiere_periode"]
        ligne["derniere_periode_fr"] = defaut["derniere_periode"]
        ligne["nb_periodes_fr"] = defaut["nb_points"]
        ligne["unite_par_defaut"] = defaut["unite_code"] or "(pas de dimension unit)"
        ligne["drapeaux"] = " ; ".join(sorted({k.split(":")[0] for k in defaut["drapeaux"].split(" ; ") if k})) or "aucun"
        a_deb, a_fin = annee(defaut["premiere_periode"]), annee(defaut["derniere_periode"])
        depuis_2000 = len({annee(p) for p, _, _ in series[codes_de_ligne(defaut)] if (annee(p) or 0) >= ANNEE_MIN})
        courte = depuis_2000 < NB_ANNEES_MIN or (a_fin or 0) < ANNEE_FIN_MIN
        ligne["statut"] = "disponible (série courte)" if courte else "disponible"
        filtres = " ; ".join(f"{d}={c}" for d, c in (x.split("=", 1) for x in defaut["modalites"].split(" ; ")) if d not in ("geo", "freq"))
        notes.append(f"série par défaut : {filtres}")
        if courte:
            notes.append(f"{depuis_2000} années depuis {ANNEE_MIN}, dernière {a_fin} : critère charte §3.4 non rempli")
        if len([l for l in lignes if l["type_ligne"] == "defaut"]) > 1:
            notes.append(f"{len([l for l in lignes if l['type_ligne'] == 'defaut'])} séries de contenu distinctes dans la vue")
    ligne["commentaire"] = (manuel + SEPARATEUR_ROBOT if manuel else "robot : ") + " ; ".join(notes)
    return ligne
