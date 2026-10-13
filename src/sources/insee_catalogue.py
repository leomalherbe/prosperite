"""Règles de catalogage des séries INSEE : zones, filtres, tagging `dimension_v0`, `candidat`, ventilations.

Utilisé par `scripts/collecte_insee.py` (étape « catalogage », exécutable hors ligne sur les inventaires
bruts). Les règles sont volontairement explicites et ordonnées pour être relues et corrigées par la
session mère ; chaque décision laisse un motif lisible dans la colonne `commentaire`.

Rappels (charte §3.4 et §4, fiche M01, décisions D15 à D21)
- filtres durs (série écartée du catalogue) : fréquence annuelle ou infra-annuelle agrégeable
  (A, S, T, B, M) ; zone nationale ; dernière période non manquante ≥ 2020 ;
- filtre souple « première période ≤ 2010 » : une série plus courte reste au catalogue, avec
  `candidat = a_verifier` si elle peut atteindre 10 points (raccordement D16), `non` sinon ;
- trois codes de zone principaux gardés distincts (D15) : FE (France), FM (France métropolitaine),
  FR-D976 (France hors Mayotte) ; les autres périmètres nationaux (Kyoto, champs PISA…) sont gardés ;
- ventilations (sexe, âge, revenu, PCS…) gardées et signalées dans `ventilation` (D21) ;
- indicateurs de moyens admis comme candidats, signalés « type moyen » (D19) ;
- indicateurs non annuels admis (D17) : signalés « série irrégulière ».
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Iterable, Optional

ANNEE_DERNIERE_MIN = 2020
ANNEE_PREMIERE_MAX = 2010
ANNEE_DEBUT_PROJET = 2000
POINTS_MIN = 10

FREQUENCES_RETENUES = {"A": "annuelle", "S": "semestrielle", "T": "trimestrielle", "B": "bimestrielle", "M": "mensuelle"}

DIMENSIONS_V0 = (
    "niveau_de_vie", "travail", "logement_cadre_vie", "sante", "education",
    "liens_bien_etre", "securite_confiance", "democratie", "egalites", "planete",
)

# --------------------------------------------------------------------------------------
# Normalisation du texte
# --------------------------------------------------------------------------------------

def normaliser(texte: str) -> str:
    """Minuscules, sans accents, apostrophes et tirets typographiques unifiés, espaces réduits."""
    t = (texte or "").replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-").replace(" ", " ")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t).strip()


# --------------------------------------------------------------------------------------
# Zones géographiques
# --------------------------------------------------------------------------------------

#: Codes principaux à garder distincts (D15).
ZONES_PRINCIPALES = {"FE": "France", "FM": "France métropolitaine", "FR-D976": "France hors Mayotte"}

#: Autres périmètres nationaux de la BDM (liste de codes CL_ZONE_GEO lue le 2026-10-13).
ZONES_NATIONALES_AUTRES = {
    "FM_D99_D978", "FM99_FR00", "FE_HPBIO", "FR-SPM-WF", "FM_D971_D972", "FM_D971_D972_D973",
    "FM_H_CORSE", "FM_H_CORSE_2018",
    "FHREUN15_FREUN18_PUBPRIVSSC_EL15TTECL", "FMDOMHREUN15_FMDOMCOMREUN18_EL15TTECL",
    "FMGUADMART15_FHMAY19_PUBPRIVSSC_ELEVCM1TTAGE", "FMGUADMART16_FHMAY21_PUBPRIVSSC_ELEVCM1TTAGE",
}

#: Zone « sans objet » ou absente : séries nationales sans dimension géographique (à vérifier).
ZONES_SANS_OBJET = {"", "SO"}


def classer_zone(code: str, libelle: str = "") -> str:
    """'principale' | 'nationale' | 'sans_objet' | 'hors_nationale'."""
    code = (code or "").strip()
    if code in ZONES_PRINCIPALES:
        return "principale"
    if code in ZONES_NATIONALES_AUTRES:
        return "nationale"
    if code in ZONES_SANS_OBJET:
        return "sans_objet"
    lib = normaliser(libelle)
    if lib.startswith("france") and not any(m in lib for m in ("hors ile", "hors paris", "province", "infra")):
        return "nationale"
    if re.match(r"^(jusqu|en \d{4}).*france", lib):  # champs composites des enquêtes PISA/PIRLS/TIMSS
        return "nationale"
    return "hors_nationale"


# --------------------------------------------------------------------------------------
# Tagging par dimension v0 (règles ordonnées : la première qui correspond l'emporte)
# --------------------------------------------------------------------------------------

def _r(*motifs: str) -> list[re.Pattern]:
    return [re.compile(m) for m in motifs]


#: (dimension, motifs sur le texte normalisé). L'ordre compte : les règles spécifiques d'abord.
REGLES_DIMENSIONS: list[tuple[str, list[re.Pattern]]] = [
    # — cas particuliers qui doivent passer avant les règles générales —
    ("egalites", _r(r"inegalit", r"\bgini\b", r"interquintile", r"interdecile", r"\bd9 ?/ ?d1\b", r"\bs80 ?/ ?s20\b", r"\(100 ?- ?s80\)", r"\bs40\b",
                    r"40 ?% (des |les )+plus (pauvres|modestes)", r"\bpalma\b")),
    ("travail", _r(r"accidents? (du|de) travail", r"maladies? professionnelles?", r"satisfaction (dans|au|a l'egard du|vis-a-vis du) (travail|emploi)",
                   r"satisfaction .*(travail|emploi)$", r"conditions de travail", r"intensite du travail", r"ni (en )?etudes,? ni (en )?formation",
                   r"ne suivant ni", r"\bneet\b")),
    ("sante", _r(r"renoncement aux soins", r"esperance de vie", r"\bvih\b", r"seropositivite", r"\bsida\b")),
    ("securite_confiance", _r(r"conjoncture aupres des menages", r"opinion (des menages|sur (leur|le|la))")),
    ("niveau_de_vie", _r(r"pauvrete", r"niveau de vie", r"privations? materielles?", r"pouvoir d'achat", r"revenu disponible", r"raisons financieres",
                         r"credits? budgetaires? publics? de r ?& ?d", r"recherche et developpement", r"effort de recherche", r"\bdird\b")),
    ("planete", _r(r"consommation (finale |primaire )?(brute )?d'energie", r"energies? renouvelables?", r"intensite (energetique|carbone|en ges)",
                   r"empreinte (carbone|matieres?|eau|environnementale)", r"gaz a effet de serre", r"changement climatique", r"economie circulaire",
                   r"transports? de marchandises", r"gaspillages?", r"antibiotiques", r"prelevements? (en |d')eau")),
    ("logement_cadre_vie", _r(r"taux d'effort", r"precarite energetique", r"eau distribuee", r"eau potable (non )?conforme", r"qualite de l'air", r"pollution de l'air",
                              r"particules (fines|pm)", r"\bpm ?10\b", r"\bpm ?2[.,]5\b", r"dioxyde d'azote", r"\bno2\b", r"\bozone\b",
                              r"logement a (une )?bonne temperature", r"transports? (en commun|collectifs?) de voyageurs")),
    ("liens_bien_etre", _r(r"satisfaction (dans|de) la vie", r"satisfaction .*(vie|loisirs|relations|temps libre)")),
    # — règles générales —
    ("egalites", _r(r"ecart (de|des|d'|entre)", r"part des femmes", r"proportion (des|de) femmes", r"femmes (cadres|dirigeantes|elues|parmi)",
                    r"parite", r"egalite (entre|femmes|professionnelle)", r"mobilite sociale", r"redistribution", r"discrimination")),
    ("democratie", _r(r"participation (au|aux|a l'|a la) .*(election|scrutin|tour)", r"taux de participation .*(election|scrutin|tour|vote|referendum)",
                      r"abstention", r"electoral", r"electeurs?", r"confiance .*institutions?",
                      r"confiance (dans|envers|en) (la justice|la police|l'armee|l'ecole|l'hopital|les medias|le gouvernement|le parlement|les partis)",
                      r"corruption", r"\bdetenus\b", r"\bprevenus\b", r"libertes?\b", r"\bvote\b", r"carceral", r"\becroue")),
    ("securite_confiance", _r(r"victimes?", r"violences?", r"homicides?", r"cambriolages?", r"\bvols?\b", r"insecurite", r"delinquance", r"\bcrimes?\b",
                              r"infractions?", r"auteurs poursuivables", r"surendettement", r"confiance (envers|dans|en) les autres", r"confiance interpersonnelle",
                              r"confiance des menages", r"conjoncture aupres des menages", r"opinion (des menages|sur (leur|le|la))", r"capacite d'epargne",
                              r"situation financiere", r"impayes?", r"difficultes? (financieres|a boucler)", r"securite routiere")),
    ("liens_bien_etre", _r(r"satisfaction", r"bien-etre", r"bonheur", r"isolement", r"solitude", r"relations? (sociales|familiales|amicales)", r"soutien social",
                           r"temps libre", r"loisirs?", r"vacances", r"depart en (voyage|vacances)", r"voyages?", r"touristique", r"tourisme",
                           r"licences? sportives?", r"pratique sportive", r"benevol", r"vie associative", r"\bassociations?\b", r"sens (de|a) (la|sa) vie",
                           r"emotions?", r"\baffects?\b", r"emploi du temps")),
    ("sante", _r(r"mortalite", r"\bdeces\b", r"\bmorts?\b", r"\btues\b", r"accidents? (de la route|de la circulation|corporels)", r"suicides?",
                 r"\bsante\b", r"maladies?", r"tabac", r"tabagisme", r"fumeurs?", r"alcool", r"obesite", r"surpoids", r"\bsoins\b",
                 r"medecins?", r"infirmi", r"pharmac", r"medicaments?", r"vaccin", r"handicap", r"limitations? (fonctionnelles?|d'activite)",
                 r"incapacite", r"depressi", r"detresse psychologique", r"drogues?", r"cannabis", r"nutrition", r"sedentarite", r"activite physique",
                 r"causes? de deces", r"tumeurs?", r"cancers?", r"cardio", r"hospitali", r"hopita", r"perinat", r"mortinatalite", r"kinesitherapeutes?",
                 r"dentistes?", r"sages-femmes", r"\bcmu\b", r"couverture maladie", r"\blits\b")),
    ("travail", _r(r"chomage", r"chomeurs?", r"\bbit\b", r"taux d'emploi", r"\bemplois?\b", r"population active", r"\bactifs?\b", r"taux d'activite",
                   r"sous-emploi", r"\bhalo\b", r"temps partiel", r"ni en emploi", r"demandeurs? d'emploi", r"duree (du|de) travail", r"heures? travaillees?",
                   r"contrats? (courts?|temporaires?|a duree)", r"\bcdd\b", r"\binterim", r"activite partielle", r"licenciements?", r"\bpenibilite\b",
                   r"\bsalaries?\b", r"effectifs? salaries?", r"travailleurs?", r"insertion professionnelle", r"fonction publique")),
    ("education", _r(r"sorties? precoces?", r"diplom", r"bachel", r"baccalaureat", r"scolari", r"\beleves?\b", r"etudiants?", r"enseignement", r"education",
                     r"\bformations?\b(?! (brute|nette) de capital)", r"competences?", r"\bpisa\b", r"\bpirls\b", r"\btimss\b", r"\blecture\b", r"litteratie", r"numeratie", r"illettrisme",
                     r"internet", r"numerique", r"haut debit", r"ordinateur", r"\btic\b", r"en ligne", r"\bcultur", r"musees?", r"bibliothe", r"\blivres?\b",
                     r"apprentissage", r"universit", r"redoublement", r"decrochage", r"\becoles?\b", r"\bcolleges?\b", r"\blycees?\b", r"monuments? historiques?")),
    ("logement_cadre_vie", _r(r"logements?", r"\bloyers?\b", r"surpeuplement", r"suroccupation", r"sans[- ]abri", r"sans domicile", r"mal[- ]loge",
                              r"hebergement", r"chauffage", r"\bbruit\b", r"nuisances?", r"espaces? verts?", r"acces a la nature",
                              r"transports? (en commun|collectifs?|publics?)", r"part modale", r"deplacements?", r"domicile-travail", r"navettes?", r"mobilite",
                              r"assainissement", r"\bproprietaires?\b", r"\blocataires?\b", r"parc (de logements|locatif|social)", r"\bhabitat\b",
                              r"residences? principales?", r"menages? equipes?", r"equipement des menages")),
    ("planete", _r(r"\bges\b", r"\bco2\b", r"carbone", r"emissions?", r"empreinte", r"rechauffement", r"energie", r"energetique", r"renouvelables?",
                   r"\benr\b", r"biodiversite", r"especes", r"oiseaux", r"artificialis", r"\bsols?\b", r"terres? agricoles", r"zones? (boisees|naturelles|humides)",
                   r"forets?", r"surfaces? (boisees|agricoles)", r"dechets?", r"recycl", r"matieres? premieres? secondaires", r"ressources? naturelles",
                   r"\beaux?\b", r"nitrates?", r"pesticides?", r"phytosanitaires?", r"\bazote\b", r"phosphore", r"masses? d'eau", r"littora", r"\bmarins?\b",
                   r"aires? (marines |terrestres )?protegees?", r"agriculture biologique", r"\bbio\b", r"pollutions?", r"ocean", r"\bpeche\b", r"halieutiques?",
                   r"recifs?", r"\butcatf\b", r"puits de carbone", r"prelevements? d'eau", r"polluants?", r"\bclimat(ique)?s?\b(?! des affaires)", r"nucleaire",
                   r"electricite", r"gaz naturel", r"petrole", r"charbon", r"combustibles?", r"vehicules? (electriques|propres)", r"plastiques?",
                   r"environnement", r"extinction", r"ecolog", r"agricoles?\b", r"exploitations? agricoles", r"(evenements|risques|catastrophes) naturel",
                   r"inondations?", r"secheresses?")),
    ("niveau_de_vie", _r(r"\bpauvres?\b", r"revenus?", r"salaires?", r"\bsmic\b", r"remunerations?", r"privations?", r"conditions de vie", r"\bpib\b",
                         r"produit interieur brut", r"revenu national", r"\brnb\b", r"consommation", r"depenses? de consommation", r"epargne", r"patrimoine",
                         r"richesse", r"dettes?", r"endettement", r"deficit", r"investissement", r"\bfbcf\b", r"formation brute de capital", r"recherche",
                         r"\br ?& ?d\b", r"innovation", r"prestations? sociales?", r"minima sociaux", r"\brsa\b", r"allocataires?", r"allocations?",
                         r"retraites?", r"pensions?", r"\bprix\b", r"inflation", r"valeur ajoutee", r"comptes? (nationaux|des menages)", r"menages?",
                         r"croissance", r"productivite", r"\bcapital\b", r"actifs? financiers", r"\bcredits?\b", r"\bbanques?\b", r"compte bancaire")),
    ("contexte", _r(r"\bpopulation\b", r"naissances?", r"fecondite", r"natalite", r"nuptialite", r"mariages?", r"\bpacs\b", r"divorces?",
                    r"solde (naturel|migratoire)", r"migrations?", r"immigr", r"estimations? de population", r"nombre de menages", r"taille des menages",
                    r"pyramide des ages", r"prenoms?", r"age moyen", r"^(?!.*pour [\d .,]+habitants).*\bhabitants?\b")),
]

#: Dimension par défaut des regroupements ODD de la BDM (utilisée seulement si le libellé ne dit rien).
DIMENSION_PAR_ODD = {
    "ODD-ERADICATION-PAUVRETE": "niveau_de_vie", "ODD-SECURITE-ALIMENTAIRE-AGRICULTURE-DURABLE": "planete",
    "ODD-SANTE-BIEN-ETRE": "sante", "ODD-EDUCATION-QUALITE": "education", "ODD-EGALITE-SEXES": "egalites",
    "ODD-EAU-PROPRE-ASSAINISSEMENT": "planete", "ODD-ENERGIE-PROPRE-COUT-ABORDABLE": "planete",
    "ODD-TRAVAIL-CROISSANCE": "travail", "ODD-INFRASTRUCTURES-RESILIENTES-INNOVATION": "niveau_de_vie",
    "ODD-REDUCTION-INEGALITES": "egalites", "ODD-VILLES-COMMUNAUTES-DURABLES": "logement_cadre_vie",
    "ODD-CONSOMMATION-PRODUCTION": "planete", "ODD-LUTTE-CHANGEMENT-CLIMATIQUE": "planete",
    "ODD-VIE-AQUATIQUE": "planete", "ODD-VIE-TERRESTRE": "planete",
    "ODD-PAIX-JUSTICE-INSTITUTIONS-EFFICACES": "securite_confiance", "ODD-PARTENARIATS-REALISATION": "niveau_de_vie",
}


#: Expressions techniques des libellés (surtout Melodi, comptes nationaux) retirées avant le tagging :
#: « Emploi ou débit » déclenchait la règle « emploi » → travail sur 8 000 séries de comptes publics.
BRUIT_LIBELLE = re.compile(
    r"emplois? ou debits?|ressources? ou credits?|emplois? et ressources?|devise nationale( \(euros\))?|evaluation standard"
    r"|non consolide|consolide|en valeur aux prix courants|aux prix de l'annee precedente chaines"
    r"|options sur titres des salaries|(total des |flux d'|variations? d')?actifs?( (non )?(financiers|produits|fixes)( produits)?| ou passifs)"
    r"|total des actifs|flux d'actifs|(par )?type d'actifs?"
)


def tagger(texte: str) -> Optional[str]:
    """Dimension v0 (ou 'contexte') de la première règle qui correspond, None sinon."""
    t = BRUIT_LIBELLE.sub(" ", normaliser(texte))
    for dimension, motifs in REGLES_DIMENSIONS:
        if any(m.search(t) for m in motifs):
            return dimension
    return None


# --------------------------------------------------------------------------------------
# Hors champ, moyens, séries arrêtées, anciennes bases
# --------------------------------------------------------------------------------------

#: Regroupements BDM hors champ (statistiques d'entreprises, prix de production, conjoncture,
#: échanges extérieurs, finances) : motif. Comparaison sur l'identifiant du dataflow.
FLUX_HORS_CHAMP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^BALANCE-PAIEMENTS"), "balance des paiements (hors champ)"),
    (re.compile(r"^CLIMAT-AFFAIRES"), "climat des affaires (conjoncture des entreprises)"),
    (re.compile(r"^ENQ-CONJ-(?!MENAGES)"), "enquête de conjoncture auprès des entreprises"),
    (re.compile(r"^COM-EXT"), "commerce extérieur (hors champ)"),
    (re.compile(r"^CONSTRUCTION-LOCAUX"), "construction de locaux non résidentiels"),
    (re.compile(r"^(CREATIONS|DEFAILLANCES|DEMOGRAPHIE)-ENTREPRISES"), "démographie des entreprises"),
    (re.compile(r"^ICA-"), "indice de chiffre d'affaires (entreprises)"),
    (re.compile(r"^(IPI|IPPI|IPPS|IPEA|IPAMPA|IPGD|ICT|IPPMP|IPLA|INDICES?-PRIX-PROD)"), "indice de production ou de prix de production (entreprises)"),
    (re.compile(r"^(IC-PROD-CONS|ICC|ILAT|ILC|IRL|INDEX-BT|BT-|TP-)"), "indice de coût ou de révision de contrats"),
    (re.compile(r"^COEFF-EURO-FRANC"), "coefficient de conversion euro-franc (outil)"),
    (re.compile(r"^(TAUX-CHANGE|COURS|PRIX-MATIERES|MATIERES-PREMIERES|PRIX-PETROLE|PRIX-ENERGIE-IMPORT)"), "cours, taux de change, matières premières"),
    (re.compile(r"^(COMPTES-ETAT|DETTE-NEGOCIABLE-ETAT)"), "comptes et dette de l'État (finances publiques, détail)"),
    (re.compile(r"^(CNA|CNT)-\d{4}-(CPEB|TEI|ERE|TOF|FBCF-BRANCHE)"), "comptes par branche ou par produit (hors champ)"),
    (re.compile(r"^EMPLOI-SALARIE-TRIM"), "emploi salarié par secteur (statistique d'entreprises) — à vérifier"),
    # ajouts de la phase 2 (règles éprouvées sur l'instantané de 158 166 séries du paquet R `insee`, août 2024)
    (re.compile(r"^IPAGRI"), "indices de prix agricoles (entreprises)"),
    (re.compile(r"^IPC-PM"), "prix moyens de détail par produit"),
    (re.compile(r"^ICHT"), "indice du coût horaire du travail (entreprises)"),
    (re.compile(r"^VOV-"), "volume des ventes du commerce (entreprises)"),
    (re.compile(r"^TOURISME-"), "fréquentation des hébergements touristiques (activité)"),
    (re.compile(r"^TCRED-ENTREPRISES-"), "statistiques d'entreprises (tableaux de l'économie française)"),
    (re.compile(r"^TCRED-ECONOMIE-VAB-REG"), "structure régionale de la valeur ajoutée"),
    (re.compile(r"^TCRED-CONSTRUCTION-LOCAUX"), "construction de locaux non résidentiels"),
]

#: Motifs de libellé hors champ (s'appliquent à tous les regroupements et jeux).
LIBELLES_HORS_CHAMP: list[tuple[re.Pattern, str]] = [
    (re.compile(p), m) for p, m in [
        (r"chiffre d'affaires", "chiffre d'affaires (entreprises)"),
        (r"climat des affaires", "climat des affaires"),
        (r"prix (de|a la) production|prix d'importation|prix de vente industriels", "prix de production (entreprises)"),
        (r"indice (des|de) prix|indice des loyers|\bipch?\b|prix a la consommation", "indice de prix (déflateur, pas un résultat)"),
        (r"production industrielle|indice de production|production manufacturiere", "production des entreprises"),
        (r"creations? d'(entreprises|etablissements)|defaillances?", "démographie des entreprises"),
        # « cours » au sens boursier seulement : « au cours des trois derniers mois » (usage d'internet,
        # renoncement aux soins…) ne doit pas être écarté (faux négatif corrigé le 13/10, phase 2).
        (r"taux de change|(?<!au )\bcours (du|des|de l') ?(petrole|baril|brent|or\b|metaux|matieres|devises|change|actions?|bourse|euro|dollar)"
         r"|matieres premieres", "cours et taux de change"),
        (r"prix agricoles|prix d'achat des moyens de production|prix de gros|\bippap\b|\bipampa\b|\bipga\b", "indice de prix agricoles ou de gros (entreprises)"),
        (r"prix moyens? (annuels? |mensuels? )?de vente", "prix de détail d'un produit"),
        (r"cout (horaire )?du travail|\bicht\b", "coût du travail (entreprises)"),
        (r"indice de volume des ventes", "ventes du commerce (entreprises)"),
        (r"taux de (charges|cotisations) sociales", "barème de cotisations sociales"),
        (r"indice des (salaires|taux de salaire)", "indice de taux de salaire par branche (barème, pas un niveau de vie)"),
        (r"\bnuitees\b|\barrivees dans|nombre d'hotels|hebergements? (collectifs )?touristiques|hotellerie (de plein air)?|chambres? d'hotes",
         "offre et fréquentation des hébergements touristiques (activité, pas un résultat pour la population)"),
        # trafic (activité des transporteurs) ; pas « à proximité du trafic routier » (PM10, ODD) ni la part
        # modale du transport ferroviaire de marchandises (ODD)
        (r"transport ferroviaire (interieur )?de voyageurs|trains? sous convention|frequentation de passagers|trafic (aerien|de voyageurs|de passagers)",
         "trafic de transport (activité)"),
        (r"categorie d'entreprise|taille d'entreprise|\bmicroentreprises\b", "statistique d'entreprises"),
        (r"coefficient de (transformation|conversion)", "coefficient de conversion"),
        (r"\b(cvs-cjo|cjo)\b.*(entreprises|branche)", "série d'entreprises"),
        (r"effectifs? (des|par) (secteurs?|branches?)|par branche|par secteur d'activite|secteur marchand", "ventilation par branche ou secteur (statistique d'entreprises)"),
        (r"\bprenoms?\b", "prénoms"),
        (r"^(importations|exportations)\b", "commerce extérieur"),
        (r"aide publique au developpement|\bapd\b", "aide publique au développement (moyen de politique internationale, hors champ v1)"),
    ]
]

#: Indicateurs de moyens (D19) : candidats admis, signalés.
LIBELLES_MOYENS = re.compile(
    r"depenses? (des administrations|publiques|de l'etat|de protection|d'education|de sante|de recherche)|credits? budgetaires|"
    r"aide publique au developpement|\bapd\b|personnel de recherche|chercheurs|effort de recherche|\bdird\b|emplois? aides?|"
    r"subventions?|prelevements? obligatoires|recettes? (fiscales|publiques)|impots?|administrations publiques|logements? (commences|autorises)"
)


# --------------------------------------------------------------------------------------
# Bruit des comptes nationaux et des ventilations techniques (phase 2)
# --------------------------------------------------------------------------------------
# Règles portant sur les codes des dimensions (BDM : SECT_INST, CNA_ACTIVITE, CNA_PRODUIT, FONCTION,
# OPERATION ; Melodi : REF_SECTOR, COUNTERPART_SECTOR, ACTIVITY, PRODUCT, EXPENDITURE, INSTR_ASSET,
# STO, PRICES, TRANSFORMATION…). Elles écartent les déclinaisons qui ne décrivent pas un résultat pour
# la population (sous-secteurs institutionnels, branches, produits détaillés, flux techniques), en
# gardant les agrégats : économie totale, ménages, administrations publiques, total ou premier niveau
# des nomenclatures. Constat de l'essai du 13/10 : 31 527 séries Melodi `oui` pour 9 jeux, dont
# 8 699 comptes détaillés des administrations publiques.

#: Secteurs institutionnels gardés : économie totale (S1, S0, S10), APU (S13), ménages (S14, S14B
#: « ménages hors entrepreneurs individuels », S1M = S14 + S15), ISBLSM (S15).
SECTEURS_RETENUS = {"", "S1", "S0", "S10", "S13", "S14", "S14B", "S15", "S1M", "S14_S15", "SO", "_Z", "_T"}
CONTREPARTIES_RETENUES = {"", "S1", "_T", "_Z", "SO"}
ZONES_CONTREPARTIE_RETENUES = {"", "W0", "W2", "_Z", "_T"}   # W0 Monde, W2 Territoire national (W1 = reste du monde)
PRIX_ECARTES = {"D": "déflateur (indice de prix)", "Y": "prix de l'année précédente (valorisation technique)",
                "O": "coût de remplacement de l'année précédente (valorisation technique)",
                "LFA": "volume aux prix de fin d'année précédente (valorisation technique)"}
TOTAUX_NOMENCLATURE = {"", "_T", "_Z", "SO", "NNTOTAL", "TOTAL", "ENSEMBLE", "D-CNT"}   # D-CNT : « Ensemble des biens et services » (comptes trimestriels)

#: Opérations des comptes nationaux gardées (codes SEC 2010 et agrégats INSEE) : soldes (PIB, revenu,
#: épargne, capacité de financement, patrimoine net), consommation, investissement, rémunérations,
#: prestations et impôts des ménages, emploi, dépenses, recettes et dette publiques, encours. Les autres
#: (revenus de la propriété D4, impôts sur la production D2-D3, transferts en capital D9, autres
#: changements de volume K…, opérations financières détaillées) sont des flux techniques.
OPERATIONS_RETENUES = {
    "", "_Z", "_T", "SO",
    "B1GQ", "B1G", "B1N", "B1NQ", "B2G", "B2N", "B3G", "B3N", "B2GEB3G", "B2NEB3N", "B5G", "B5N", "B5GQ", "B5NQ", "B6G", "B6N",
    "B7G", "B7N", "B8G", "B8N", "B9", "B9N", "B90", "B11", "B101",
    "P3", "P31", "P32", "P3NR", "P3R", "P4", "P41", "P42", "P5", "P51G", "P51C", "P51N",
    "D1", "D11", "D12", "D5", "D51", "D61", "D62", "D63", "D6M", "D632",
    "LE", "LE_N", "EMP", "EMPH", "POP", "SAL", "SELF",
    "OTE", "TE", "OTR", "TR", "GD", "PIB", "PIB_H", "RNB", "RNB_H", "ACTIFS_TOTAL", "AN", "AN1", "AN11", "AN2", "AF",
}
#: Regroupements / jeux de comptes nationaux auxquels s'applique la liste d'opérations.
COMPTES_NATIONAUX = re.compile(r"^(CNA|CNT)-|^D[DS]_CN[AT]_")


def _code_produit_detaille(code: str) -> bool:
    if code in TOTAUX_NOMENCLATURE:
        return False
    if re.fullmatch(r"FON[A-Z]*|FON\d{2}", code):      # BDM : COICOP total, agrégats, 1er niveau
        return False
    if re.fullmatch(r"CP_[A-Z_]+", code):               # Melodi : agrégats particuliers de l'INSEE
        return False
    return True


def motif_bruit_dimensions(theme: str, dimensions: Optional[dict[str, str]]) -> Optional[str]:
    """Motif d'exclusion tiré des codes de dimensions (None si la série est un agrégat utile)."""
    if not dimensions:
        return None
    # la BDM écrit « SECT-INST » (réponses réelles) là où l'instantané du paquet R écrit « SECT_INST »
    d = {k.upper().replace("-", "_"): str(v).strip() for k, v in dimensions.items()}
    for nom in ("SECT_INST", "REF_SECTOR"):
        v = d.get(nom)
        if v is not None and v not in SECTEURS_RETENUS:
            return f"secteur institutionnel détaillé ({nom}={v})"
    v = d.get("COUNTERPART_SECTOR")
    if v is not None and v not in CONTREPARTIES_RETENUES:
        return f"ventilation par secteur de contrepartie ({v})"
    v = d.get("COUNTERPART_AREA")
    if v is not None and v not in ZONES_CONTREPARTIE_RETENUES:
        return f"ventilation par zone de contrepartie ({v})"
    for nom in ("CNA_ACTIVITE", "ACTIVITY"):
        v = d.get(nom)
        if v is not None and v not in TOTAUX_NOMENCLATURE:
            return f"ventilation par branche ({nom}={v})"
    for nom in ("CNA_PRODUIT", "PRODUCT"):
        v = d.get(nom)
        if v is not None and _code_produit_detaille(v):
            return f"ventilation par produit ({nom}={v})"
    v = d.get("FONCTION", "")
    if re.fullmatch(r"FON\d{3,}", v):
        return f"fonction détaillée (COFOG niveau 2 : {v})"
    v = d.get("EXPENDITURE", "")
    if re.fullmatch(r"GF\d{4,}", v):
        return f"fonction détaillée (COFOG niveau 2 : {v})"
    if re.fullmatch(r"CP\d{3,}", v):
        return f"poste de consommation détaillé (COICOP niveau 2 ou plus : {v})"
    v = d.get("INSTR_ASSET", "")
    # patrimoine : instruments financiers de niveau ≥ 2 et actifs non financiers détaillés écartés,
    # sauf les logements (N111, AN111), utiles pour le patrimoine des ménages
    if re.fullmatch(r"F\d{2,}\w*|F\d[A-Z]\w*|N\d{3,}\w*|AN\d{3,}\w*", v) and not re.match(r"A?N111", v):
        return f"instrument ou actif détaillé ({v})"
    v = d.get("OPERATION", "")
    if re.fullmatch(r"AN\d{3,}\w*|F\d{2,}\w*", v) and not re.match(r"AN111(_|$)", v):
        return f"actif ou instrument détaillé ({v})"
    v = d.get("PRICES", "")
    if v in PRIX_ECARTES:
        return PRIX_ECARTES[v]
    v = d.get("TRANSFORMATION")
    if v is not None and v not in {"", "N", "GY", "_Z"}:
        return f"transformation technique ({v})"
    v = d.get("CONSOLIDATION")
    if v is not None and v not in {"", "C", "N", "_Z"}:
        return f"consolidation particulière ({v})"
    if d.get("MATURITY") in {"S", "L"}:
        return f"ventilation par échéance ({d['MATURITY']})"
    if COMPTES_NATIONAUX.search(theme or ""):
        for nom in ("STO", "OPERATION"):
            v = d.get(nom)
            if v is None or v.startswith("_"):
                continue
            v = re.sub(r"_?SEC\d+$|_\d{4}$", "", v)   # BDM : AN_SEC2010 → AN, D44_2010 → D44
            if v not in OPERATIONS_RETENUES:
                return f"opération des comptes nationaux hors liste des agrégats ({nom}={v})"
    return None

ZONE_LIBELLE = {
    "FE": "France", "FM": "France métropolitaine", "FR-D976": "France hors Mayotte",
    "FM_D99_D978": "France métropolitaine, Drom et Saint-Martin (périmètre Kyoto)",
}


def motif_hors_champ(dataflow: str, texte: str) -> Optional[str]:
    for motif, explication in FLUX_HORS_CHAMP:
        if motif.search(dataflow or ""):
            return explication
    t = normaliser(texte)
    for motif, explication in LIBELLES_HORS_CHAMP:
        if motif.search(t):
            return explication
    return None


def flux_anciennes_bases(flux: Iterable[str]) -> dict[str, str]:
    """Regroupements dont il existe une version plus récente (même préfixe, millésime de base plus grand).

    Ex. CNA-2014-RDB → remplacé par la famille CNA-2020-* ; ICA-2005-* → ICA-2010-* / ICA-2021-*.
    Renvoie {dataflow: millésime le plus récent de la famille}.
    """
    familles: dict[str, list[tuple[int, str]]] = {}
    for f in flux:
        m = re.match(r"^(.*?)-?((?:19|20)\d{2})(-.*)?$", f)
        if not m:
            continue
        prefixe = m.group(1)
        familles.setdefault(prefixe, []).append((int(m.group(2)), f))
    anciens: dict[str, str] = {}
    for prefixe, membres in familles.items():
        recent = max(a for a, _ in membres)
        for a, f in membres:
            if a < recent:
                anciens[f] = str(recent)
    return anciens


# --------------------------------------------------------------------------------------
# Ventilations (D21)
# --------------------------------------------------------------------------------------

_VENTILATIONS_TITRE = [
    ("sexe", re.compile(r"\b(hommes?|femmes?|garcons|filles|masculin|feminin)\b")),
    ("age", re.compile(r"(\b\d{1,2} ?(-|a) ?\d{1,2} ans\b|\bmoins de \d+ ans\b|\b\d+ ans (ou|et) plus\b|\b\d+ ans et \+|classe d'age|tranche d'age|selon l'age|par age)")),
    ("revenu", re.compile(r"(quintile|decile|quartile|centile|tranche de (revenu|niveau de vie)|selon le niveau de vie)")),
    ("pcs", re.compile(r"(categorie socio|\bpcs\b|\bcadres?\b|ouvriers?|employes?|professions? intermediaires?|agriculteurs?|artisans?)")),
    ("diplome", re.compile(r"(diplom|niveau d'etudes|niveau d'education)")),
    ("menage", re.compile(r"(type de menage|familles? monoparentales?|couples?|personnes? seules?|configuration familiale)")),
    ("activite", re.compile(r"(statut d'activite|\bchomeurs\b|\bretraites\b|\binactifs\b|actifs occupes|statut d'occupation|locataires|proprietaires)")),
    ("territoire", re.compile(r"(unite urbaine|commune rurale|aire d'attraction|quartiers? prioritaires?|\bqpv\b|densite)")),
    ("nationalite", re.compile(r"(immigres?|etrangers?|nationalite|lieu de naissance)")),
]

_EXCEPTIONS_SEXE = re.compile(r"(femmes et (les )?hommes|hommes et (les )?femmes|femmes-hommes|hommes-femmes|part des femmes|proportion (des|de) femmes|femmes (cadres|dirigeantes|elues|parmi))")

_TOTAUX = {"", "_t", "t", "0", "_z", "z", "ens", "ensemble", "total", "all", "_all", "tot", "so", "_x", "x"}

_DIMENSIONS_VENTILATION = [
    ("sexe", re.compile(r"^(SEX|SEXE|GENDER)")),
    ("age", re.compile(r"(^AGE|_AGE$|^AGE_)")),
    ("revenu", re.compile(r"(QUANT|QUINT|DECIL|QUART|NIVVIE|INCOME)")),
    ("pcs", re.compile(r"(PCS|^CS\d|SOCIO|OCCUP)")),
    ("diplome", re.compile(r"(DIPL|EDUC|ISCED)")),
    ("menage", re.compile(r"(TYPMEN|MENAGE|HOUSEHOLD|HH_|FAMIL)")),
    ("activite", re.compile(r"(EMPSTA|ACTIVITY_STATUS|STAT_ACT|ACTEFF|TACT)")),
    ("nationalite", re.compile(r"(NATIO|IMMI|CITIZEN)")),
]


def ventilations_titre(titre: str) -> list[str]:
    """Axes de ventilation lus dans le titre, après le premier « - » (style BDM « Indicateur - Femmes - 15-24 ans »)
    ou dans une tournure « selon … / par … »."""
    t = normaliser(titre)
    morceaux = t.split(" - ", 1)
    queue = morceaux[1] if len(morceaux) > 1 else ""
    selon = " ".join(re.findall(r"\b(?:selon|par) (?:le |la |l'|les )?[a-z' -]{3,40}", t))
    zone = f"{queue} {selon}".strip()
    if not zone:
        return []
    axes = []
    for axe, motif in _VENTILATIONS_TITRE:
        if axe == "sexe" and _EXCEPTIONS_SEXE.search(t):
            continue
        if motif.search(zone):
            axes.append(axe)
    return axes


def ventilations_dimensions(dimensions: dict[str, str]) -> list[str]:
    """Axes de ventilation lus dans les dimensions (Melodi, BDM) dont la valeur n'est pas un total."""
    axes = []
    for nom, valeur in dimensions.items():
        if nom in {"GEO", "FREQ", "TIME_PERIOD", "UNIT_MEASURE", "REF_AREA"}:
            continue
        if normaliser(str(valeur)) in _TOTAUX or str(valeur).upper().startswith(("_T", "ENS", "TOT")):
            continue
        for axe, motif in _DIMENSIONS_VENTILATION:
            if motif.search(nom.upper()) and axe not in axes:
                axes.append(axe)
    return axes


# --------------------------------------------------------------------------------------
# Décision « candidat »
# --------------------------------------------------------------------------------------

@dataclass
class Decision:
    dimension_v0: str
    candidat: str                 # oui | non | a_verifier
    motifs: list[str] = field(default_factory=list)
    ventilation: str = ""

    @property
    def commentaire(self) -> str:
        return " ; ".join(self.motifs)


def annee_de(periode: str) -> Optional[int]:
    try:
        return int(str(periode)[:4])
    except (TypeError, ValueError):
        return None


def nombre_annees_estime(premiere: str, derniere: str) -> int:
    a, b = annee_de(premiere), annee_de(derniere)
    if a is None or b is None:
        return 0
    return max(0, b - max(a, ANNEE_DEBUT_PROJET) + 1)


def decider(
    libelle: str,
    theme: str,
    theme_libelle: str,
    frequence: str,
    zone: str,
    premiere: str,
    derniere: str,
    nb_annees_depuis_2000: Optional[int] = None,
    serie_arretee: bool = False,
    ancienne_base: Optional[str] = None,
    dimensions: Optional[dict[str, str]] = None,
    dimensions_bruit: Optional[dict[str, str]] = None,
) -> Decision:
    """Tagging et décision « candidat » pour une série déjà retenue au catalogue (filtres durs passés).

    `zone` : résultat de `classer_zone` ; `frequence` : code A/S/T/B/M ; `nb_annees_depuis_2000` :
    nombre exact d'années avec valeur depuis 2000 (séries annuelles lues en entier) ou None (estimé).
    `dimensions` : dimensions lues pour repérer les ventilations (D21) ; `dimensions_bruit` : toutes
    les dimensions de la série, pour les règles de `motif_bruit_dimensions` (par défaut `dimensions`).
    """
    motifs: list[str] = []
    dimension = tagger(libelle)
    origine_theme = False
    if dimension is None:
        dimension = DIMENSION_PAR_ODD.get(theme) or tagger(theme_libelle) or tagger(theme)
        origine_theme = dimension is not None
    axes = ventilations_titre(libelle)
    for axe in ventilations_dimensions(dimensions or {}):
        if axe not in axes:
            axes.append(axe)
    ventilation = ";".join(axes)
    dim = dimension or ""

    hors_champ = motif_hors_champ(theme, libelle)
    if hors_champ:
        return Decision(dim, "non", [f"hors champ : {hors_champ}"], ventilation)
    bruit = motif_bruit_dimensions(theme, dimensions_bruit if dimensions_bruit is not None else dimensions)
    if bruit:
        return Decision(dim, "non", [f"déclinaison technique : {bruit}"], ventilation)
    if serie_arretee:
        return Decision(dim, "non", ["série arrêtée"], ventilation)
    if ancienne_base:
        return Decision(dim, "non", [f"ancienne base (remplacée par la base {ancienne_base})"], ventilation)
    if dimension is None:
        return Decision("", "non", ["aucune règle de dimension ne correspond"], ventilation)
    if dimension == "contexte":
        return Decision("contexte", "non", ["contexte démographique (dénominateur), pas un indicateur de prospérité"], ventilation)

    candidat = "oui"
    if origine_theme:
        candidat = "a_verifier"
        motifs.append("dimension déduite du regroupement (aucun mot-clé dans le libellé)")
    if zone == "sans_objet":
        candidat = "a_verifier"
        motifs.append("zone non renseignée (SO ou absente)")
    elif zone == "nationale":
        motifs.append("périmètre national particulier (pas FE/FM/FR-D976)")

    a_premiere = annee_de(premiere)
    exact = nb_annees_depuis_2000 is not None
    n = nb_annees_depuis_2000 if exact else nombre_annees_estime(premiere, derniere)
    if a_premiere is not None and a_premiere > ANNEE_PREMIERE_MAX:
        if n >= POINTS_MIN:
            candidat = "a_verifier"
            motifs.append(f"première période {premiere} > {ANNEE_PREMIERE_MAX} : raccordement à prévoir (D16)")
        else:
            return Decision(dim, "non", [f"moins de {POINTS_MIN} points depuis {ANNEE_DEBUT_PROJET} ({n}, première période {premiere})"], ventilation)
    elif exact and n < POINTS_MIN:
        candidat = "a_verifier"
        motifs.append(f"série irrégulière : {n} années avec valeur depuis {ANNEE_DEBUT_PROJET} (D17)")

    if frequence != "A":
        motifs.append("infra-annuelle : agrégation annuelle à prévoir")
    if LIBELLES_MOYENS.search(normaliser(libelle)):
        motifs.append("type moyen (D19)")
    if ventilation:
        motifs.append(f"ventilation : {ventilation}")
    return Decision(dim, candidat, motifs, ventilation)
