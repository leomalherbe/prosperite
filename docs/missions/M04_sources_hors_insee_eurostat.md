# Fiche de mission M04 — Inventaire des sources de données hors INSEE et Eurostat

**Prompt de lancement** (à coller dans une nouvelle session rattachée au Projet « Observatoire de la prospérité ») :

> Tu es un agent du projet « Observatoire de la prospérité ». Lis d'abord dans le Projet la charte `claude/00_charte_projet.md`, puis cette fiche de mission `claude/missions/M04_sources_hors_insee_eurostat.md`. Attache ensuite le dépôt GitHub `leomalherbe/prosperite` (accès en écriture), clone-le et lis son `CLAUDE.md`. Exécute la fiche intégralement, en français, sans modifier la charte ni le journal des décisions, en travaillant sur une branche `m04-sources` et en ouvrant une pull request vers `main`. Dépose les livrables documentaires dans le Projet (chemins `claude/…` de la fiche) et dans le dépôt (`docs/…`). Termine par un compte rendu dans `claude/cr/M04_compte_rendu.md` (Projet) et `docs/cr/M04_compte_rendu.md` (dépôt).

**Modèle conseillé** : Sonnet 5.5. **Peut démarrer immédiatement.** **Durée estimée** : 1 session longue.

## Contexte
L'INSEE (M01) et Eurostat (M02) ne couvrent pas tout : gouvernance et libertés, bien-être ressenti infra-annuel, biodiversité, sécurité (statistiques ministérielles), éducation (DEPP), santé (DREES, Santé publique France), environnement (SDES, Ademe, OFB)… La charte (§3.5, D09) admet les sources **niveau 1** (API) et **niveau 2** (CSV/XLSX à URL stable téléchargeable par script) et exclut les PDF/graphiques.

## Objectif
Un inventaire qualifié de **toutes les sources utiles**, avec pour chacune la voie d'accès automatisable, et une liste d'**indicateurs candidats** par dimension v0 que ces sources apportent et que l'INSEE/Eurostat n'apportent pas (ou apportent moins bien).

## Tâches

### T1. Fiche par source (même structure pour toutes)
Pour chaque source : organisme ; périmètre thématique ; **voie d'accès** (API — type, URL de base, authentification, format ; ou téléchargement direct — URL stable d'un CSV/XLSX, à vérifier en ouvrant l'URL) ; **niveau** (1, 2, ou exclu) ; licence ; fréquence de mise à jour ; profondeur temporelle ; couverture géographique ; 3 à 10 exemples d'indicateurs pertinents pour la prospérité, avec identifiant ou URL exacte du fichier ; limites.

Sources à couvrir (ajouter toute source découverte en route) :

**Services statistiques ministériels et agences françaises**
1. SDES — environnement, énergie, logement, transports (`data.statistiques.developpement-durable.gouv.fr`, API ?).
2. DREES — santé, solidarité, baromètre d'opinion DREES (`data.drees.solidarites-sante.gouv.fr`).
3. Santé publique France — Géodes (indicateurs de santé).
4. SSMSI (Interstats) — délinquance enregistrée, enquête Vécu et ressenti en matière de sécurité (VRS/CVS), sentiment d'insécurité.
5. DEPP — éducation (`data.education.gouv.fr`), évaluations, PISA/PIAAC pour la France (OCDE).
6. OFB / Observatoire national de la biodiversité (`naturefrance.fr`), indicateurs ONB.
7. Ademe (`data.ademe.fr`), Citepa (inventaire des émissions, Secten).
8. Banque de France — Webstat (API), endettement des ménages, épargne.
9. data.gouv.fr — API du catalogue ; identifier les jeux « résultats » utiles (élections : participation ; etc.).
10. Ministère de l'Intérieur — résultats électoraux (participation) ; CEVIPOF baromètre de la confiance politique (données ouvertes ?).
11. CEPREMAP — Observatoire du bien-être (baromètre trimestriel) : les données sont-elles téléchargeables (CSV/XLSX) ou seulement en PDF ?
12. Crédoc (Conditions de vie et aspirations), Observatoire des inégalités (secondaire) : accès réel aux données ?

**Organisations internationales et bases ouvertes**
13. OCDE Data Explorer — API SDMX (`sdmx.oecd.org/public/rest/…`), dont *How's Life?* database, PISA, PIAAC, temps de travail, confiance.
14. Banque mondiale — API v2 (déjà utilisée par les prototypes).
15. Our World in Data — points d'entrée CSV des graphiques (`…/grapher/{slug}.csv`), et API de données ; V-Dem (démocratie, libertés), RSF (liberté de la presse), Transparency International (CPI), Freedom House.
16. World Happiness Report (xlsx annuel), Gallup World Poll (fermé : à exclure), Eurofound EQLS / Living, working and COVID-19, European Social Survey (microdonnées avec inscription : statuer), Eurobaromètre (confiance, GESIS).
17. Global Footprint Network (empreinte écologique France), EDGAR (émissions), Copernicus (qualité de l'air).

### T2. Tableau d'inventaire
CSV `10_sources_inventaire.csv` : `source, organisme, theme, voie_acces (api|telechargement|exclu), url_base_ou_fichier, authentification, format, licence, frequence, premiere_annee, derniere_annee, geo, niveau (1|2|exclu), fiabilite_acces (verifie|probable|non_verifie), commentaire`.

### T3. Indicateurs candidats apportés
CSV `10_indicateurs_candidats_hors_insee_eurostat.csv` : `indicateur, dimension_v0, source, identifiant_ou_url, unite, sens, declaratif (oui|non), frequence, premiere_annee, derniere_annee, doublon_insee_eurostat (oui|non|partiel), commentaire`. Viser 60 à 120 lignes, toutes vérifiées (URL ouverte, série repérée).

## Livrables (docs Projet + pièces jointes)
- `claude/10_sources_hors_insee_eurostat.md` (T1).
- `claude/10_sources_inventaire.csv` (T2).
- `claude/10_indicateurs_candidats_hors_insee_eurostat.csv` (T3).
- `claude/cr/M04_compte_rendu.md`.

## Critères d'acceptation
- Chaque source a un niveau et une voie d'accès **vérifiés** (l'URL a été ouverte et renvoie bien des données) ou est marquée `non_verifie` avec la raison.
- Aucune source « PDF seulement » n'est classée niveau 1 ou 2.
- Les indicateurs candidats indiquent s'ils doublonnent une série INSEE/Eurostat.

## Pièges connus
- Beaucoup de portails français utilisent Opendatasoft (API `…/api/explore/v2.1/catalog/datasets/…`) : documenter ce point d'entrée une fois et le réutiliser.
- Les indices composites (CPI, Freedom House, World Happiness) sont des **indicateurs agrégés** : les signaler comme tels (`commentaire`), ils posent une question de double comptage.
- Pour OWID, préférer la source primaire quand elle est accessible (V-Dem, RSF…) et noter OWID comme voie d'accès commode.
