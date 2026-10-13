# Journal des décisions — Observatoire de la prospérité

Tenu par la session mère. Une ligne par décision, datée. Les agents proposent, ne modifient pas.

## Décisions actées

| Date | N° | Décision | Motif / contexte |
|---|---|---|---|
| 2026-10-13 | D01 | La structure à trois niveaux des prototypes (poids des dimensions → choix d'indicateurs → bornes/poids internes) est conservée ; le contenu (dimensions, indicateurs, sources, bornes, code) est refait. | Diagnostic des prototypes v11/v6. |
| 2026-10-13 | D02 | Construction des dimensions par la voie A (top-down conceptuelle, croisement des cadres de référence). Les méthodes statistiques ne servent qu'à détecter la redondance intra-dimension. | Séries annuelles France seule : trop peu de points, co-tendance générale. |
| 2026-10-13 | D03 | « Subjectif » a deux sens, tous deux retenus et distingués : paramétrage par l'utilisateur ; indicateurs déclaratifs (bien-être ressenti) admis comme indicateurs avec drapeau. | Réponse Léo Q1. |
| 2026-10-13 | D04 | Un seul indice 0–100. Bornes seuil minimal / objectif fixées par l'utilisateur. Règle d'agrégation au choix de l'utilisateur aux deux niveaux (moyenne généralisée : arithmétique, géométrique, minimum). | Réponse Léo Q2. |
| 2026-10-13 | D05 | Bornes initiales fixées par le projet pour chaque indicateur (hiérarchie de justification : officiel > scientifique > historique > européen > expert), remplacées par les bornes émergentes (médianes des utilisateurs) une fois un volume suffisant de réponses atteint. Socle versionné. | Réponse Léo Q3. |
| 2026-10-13 | D06 | Échelle nationale en v1 ; clé `geo` prévue dans le modèle de données. | Réponse Léo Q4. |
| 2026-10-13 | D07 | Au plus 10 dimensions ; beaucoup d'indicateurs par dimension. | Réponse Léo Q8. |
| 2026-10-13 | D08 | Profondeur temporelle : 2000 → aujourd'hui. | Réponse Léo Q9. |
| 2026-10-13 | D09 | Sources sans API acceptées si téléchargement CSV/XLSX à URL stable automatisable (niveau 2) ; lecture de PDF/graphiques exclue. | Réponse Léo Q10. |
| 2026-10-13 | D10 | Tout en français (interface, docs, identifiants). | Réponse Léo Q12. |
| 2026-10-13 | D11 | Le code est écrit dans les sessions Claude et exécuté sur GitHub Actions ; Python 3.12 ; front statique hébergé sur GitHub Pages ; base de réponses Supabase (UE) en phase 7. | Réseau du bac à sable fermé aux API (test du 13/10) ; Léo sans compétence technique → zéro administration de serveur. |
| 2026-10-13 | D12 | Le Projet claude.ai est la mémoire partagée entre session mère et agents (charte, fiches de mission, comptes rendus). Le dossier OneDrive « Prosperity x Claude » reçoit les copies et les fichiers volumineux ; le dépôt GitHub reçoit code et données. | Organisation du travail. |
| 2026-10-13 | D13 | Tous les agents de mission tournent avec Opus (pas de modèle plus léger) ; les agents de phase 2 sont des sessions neuves qui lisent les livrables de phase 1 sur leur branche. | Décision Léo (12 h 50) ; contexte des agents de phase 1 trop volumineux pour être prolongé. |
| 2026-10-13 | D14 | INSEE : voies retenues `bdm.insee.fr` (SDMX) et Melodi, sans clé ; Données locales hors v1 ; fichiers xlsx d'insee.fr téléchargés par le robot (Licence ouverte, identification, débit modéré) = niveau 2. | Bilan M01 phase 1. |
| 2026-10-13 | D15 | Les codes géographiques INSEE (métropole, hors Mayotte, France entière) restent distincts ; chaque fiche indicateur en choisit un et le documente. | Bilan M01. |
| 2026-10-13 | D16 | Couverture 2000–2009 : raccordement des séries ODD (souvent depuis 2010) aux séries longues Melodi, signalé par un drapeau `raccordement` dans la fiche. | Bilan M01. |
| 2026-10-13 | D17 | Indicateurs non annuels (participation électorale, PISA…) admis : report de la dernière valeur connue, drapeau `frequence: irreguliere`. | Bilan M04. |
| 2026-10-13 | D18 | Indices composites (V-Dem, CPI, gouvernance BM, World Happiness…) admis avec drapeau `composite: oui` ; le double comptage se traite au contrôle de redondance. | Bilan M04 ; seules mesures disponibles pour la dimension démocratie. |
| 2026-10-13 | D19 | Indicateurs de moyens (part des renouvelables, effort de R&D…) admis comme candidats avec `type: moyen` ; les cibles officielles correspondantes servent de bornes. | Bilan M03 ; la charte §3.4 exprime une préférence, pas une interdiction. |
| 2026-10-13 | D20 | Procédure de validation et de gel en deux temps (dimensions, puis indicateurs), validation par exception dans des classeurs Excel, audit croisé, versionnement sémantique de la base d'indicateurs. Détail en charte §3.6. | Validée par Léo (14 h 56). |
| 2026-10-13 | D21 | Pas de création de comptes ni de clés (Banque de France Webstat, Global Footprint Network) pour l'instant. Le script de vérification des accès de M04 est conservé et tourne chaque mois. Les fixtures INSEE reconstituées sont remplacées par de vraies réponses au premier passage du robot. Les ventilations (sexe, âge, quintile) sont gardées dans les catalogues, marquées `ventilation`. | Bilans M01/M04. |
| 2026-10-13 | D22 | Léo examine la proposition de grille v1 de M03 avant de donner des orientations (pas d'orientation a priori sur la satisfaction globale, l'alimentation, l'énergie, le temps, l'innovation). | Réponse Léo (point A). |

## Questions ouvertes

| N° | Question | Qui tranche | Échéance |
|---|---|---|---|
| Q-A | ~~Dépôt GitHub~~ — réglé : `leomalherbe/prosperite`, public, app GitHub de Claude installée (13/10) | — | Clos |
| Q-B | Place de la satisfaction globale dans la vie (dimension 6 ou transversale) ; rattachement alimentation, énergie, innovation | Session mère sur proposition M03 | Fin M03 |
| Q-C | Seuil de « volume suffisant » de réponses pour basculer vers les bornes émergentes ; agrégation par médiane des paramètres ou médiane des indices | Léo + session mère | Phase 7 |
| Q-D | Cadre institutionnel, publication visée, échéances | Léo | Quand utile |
| Q-E | Recrutement des répondants | Léo | Plus tard (décision explicite du 13/10) |
| Q-F | Statut des objectifs officiels à vérifier au moment du socle des bornes : objectif ZAN −50 % 2021–2031 (en vigueur en déc. 2025 ; la PPL TRACE, adoptée au Sénat le 18/03/2025, prévoit sa suppression ; examen à l'Assemblée annoncé pour février 2026, issue à vérifier) ; article L100-4 du code de l'énergie (33 % de renouvelables et −40 % de fossiles en 2030, années de référence 2012 ; loi de programmation énergie-climat à vérifier). | Session mère | Avant le socle des bornes |
