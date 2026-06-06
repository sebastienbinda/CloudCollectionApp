# 06 - Ajustement des props de navigation et de session

## Objectif

Fournir à toutes les pages migrées les props nécessaires à `PageLayout` et au
menu principal.

## Prérequis

- Lire `tasks/0.2.0/fix_menu/00_existing_code_analysis_result.md`.
- Avancer ou terminer les migrations de pages.
- Lire `documentation/frontend-arch.md`.

## Étapes

1. Modifier `frontend/src/components/AppViewSwitch.jsx`.
2. Ajouter les props communes de session et de navigation aux vues migrées.
3. Factoriser la préparation des props communes si cela réduit la duplication
   sans rendre le code moins lisible.
4. Garder `App.jsx` comme point de composition.
5. Ne pas ajouter de chargement de données, d'appel API ou de logique métier dans
   `AppViewSwitch`.

## Critères D'Acceptation

- Les pages migrées reçoivent toutes les props nécessaires.
- La navigation existante continue d'utiliser les callbacks centralisés.
- `AppViewSwitch` reste conforme à `documentation/frontend-arch.md`.
- Aucune règle d'accès n'est modifiée.
