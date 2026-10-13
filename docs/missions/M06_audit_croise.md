# Fiche de mission M06 — Audit croisé des fiches indicateurs

**Prérequis** : PR M05 ouverte pour la dimension auditée. L'auditeur **n'a pas participé** à M05 pour cette dimension (session neuve, Opus).

**Prompt de lancement** :

> Tu es un agent auditeur du projet « Observatoire de la prospérité ». Lis dans le Projet la charte `claude/00_charte_projet.md` (§3.4, §3.6, §5.1), le journal des décisions, puis cette fiche `claude/missions/M06_audit_croise.md`. Attache le dépôt `leomalherbe/prosperite`, clone-le, lis `CLAUDE.md`. Dimension à auditer : `<id>` (branche `m05-<dimension>`). Tu ne modifies pas les fiches : tu produis un rapport d'audit. Termine par `claude/cr/M06_<dimension>_audit.md` et `docs/cr/`.

## Objectif
Vérifier, sans a priori, que les fiches et recommandations de M05 sont exactes, complètes et cohérentes avant que Léo valide. L'audit est la garantie que le travail ne se note pas lui-même.

## Tâches
1. **Échantillon** : toutes les fiches `recommandation: ecarter` ; toutes les fiches `incontournable: oui` ; 20 % des autres tirées au hasard (graine notée) ; plus toute fiche signalée `a_verifier` dans le journal de M05.
2. **Pour chaque fiche de l'échantillon**, vérifier contre la source (WebFetch sur l'URL d'API ou la page) : l'identifiant de série existe ; la définition correspond ; l'unité et le sens sont corrects ; la période annoncée est exacte ; le type (résultat/moyen/pression) et `declaratif` sont justes ; la famille et la variante principale sont pertinentes ; la recommandation est cohérente avec les critères de la charte. Noter `conforme` / `a_corriger` (avec la correction précise) / `non_verifiable` (raison).
3. **Complétude** : comparer la long-list éligible et les fiches ; chercher dans les catalogues des indicateurs pertinents oubliés (notamment déclaratifs et ventilations pour `egalites`) ; comparer aux incontournables du crosswalk.
4. **Cohérence inter-dimensions** : signaler tout indicateur qui figure aussi dans une autre dimension (même id ou même série source).
5. **Rapport** `docs/validation/audit_<dimension>.md` : tableau des fiches auditées avec verdict, liste des oublis, liste des incohérences, et un avis global (`pret_pour_validation` / `corrections_necessaires`). Les corrections sont ensuite faites par l'agent M05 (ou la session mère), pas par l'auditeur.

## Critères d'acceptation
- Chaque verdict `a_corriger` cite la source consultée et la valeur attendue.
- Le rapport distingue erreurs factuelles, désaccords de jugement et oublis.
