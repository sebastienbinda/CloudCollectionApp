# 07 - Tests backend approfondis

## Objectif

Centraliser les tests backend de non-régression pour le nouveau référentiel de
plateformes et le mapping d'import.

Cette tâche doit s'appuyer sur :

- `task/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
- les tâches backend `02`, `03`, `04` et `05`.

## Tests À Couvrir

Ajouter ou compléter les tests backend pour valider :

- schéma `t_platform` ;
- chargement du catalogue plateformes ;
- endpoint de liste / recherche plateformes ;
- cache serveur du catalogue plateformes avec TTL 5 heures ;
- absence de requêtes SQL répétées pour le catalogue plateformes avant
  expiration du cache ;
- import avec rattachement exact ;
- import avec casse différente ;
- import avec accents différents ;
- import avec espaces différents ;
- import avec coquille acceptée ;
- import avec score entre 25% et 75%, warning et email administrateur ;
- import refusé avec score inférieur à 25% ;
- import refusé avec score à 0% ;
- seuils par défaut `MATCHING_LOW_LVL_RATING=25` et
  `MATCHING_HIGH_LEVEL_RATING=75` ;
- seuils personnalisés par variables d'environnement ;
- refus d'une configuration de seuils non numérique ;
- refus d'une configuration avec seuil bas supérieur ou égal au seuil haut ;
- refus d'une configuration hors bornes `0..100` ;
- import avec correspondance ambiguë ;
- warnings d'import ;
- email administrateur ;
- absence de création de plateforme par l'import ;
- utilisation du cache plateformes pendant l'import ;
- compteur de plateformes liées.

## Validation

Lancer :

```bash
./test_backend.sh
```

Si la suite complète est trop longue, lancer d'abord les tests ciblés puis la
suite complète avant clôture de la fonctionnalité.

## Critères D'Acceptation

- Les tests ciblés existent.
- Les tests couvrent les cas de coquille demandés par la tâche chapeau.
- `./test_backend.sh` passe ou les échecs non liés sont explicitement listés.
