# 05 - Format API des plateformes

## Objectif

Adapter les endpoints backend de recherche et de liste des plateformes au
nouveau format `t_platform`.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
- `tasks/0.2.6/plateforme_list/02_database_platform_schema_and_seed.md`
- `documentation/backend-api.md`

## Backend À Modifier

Selon les noms confirmés dans le rapport d'analyse :

- repository public Bibliothèque ;
- service Bibliothèque ;
- controller plateformes ;
- endpoint de recherche plateformes utilisé par la collection ;
- cache serveur du catalogue plateformes ;
- tests de route et service.

## Format Cible

Le format doit inclure au minimum :

- `id` ;
- `name` ;
- `release_date` ;
- `end_date` ;
- `manufacturer` ;
- `description` ;
- `total_games` quand le contexte le permet.

Le champ `status` doit être retiré du contrat si la colonne est supprimée par
la tâche SQL.

## Tests Attendus

Ajouter ou modifier des tests backend couvrant :

- liste paginée des plateformes ;
- recherche par nom ;
- tri par `name`, `release_date`, `end_date` et `manufacturer` si supporté ;
- sérialisation de `end_date` ;
- absence de champ obsolète si applicable.
- utilisation du cache plateformes sur les recherches répétées ;
- expiration du cache après 5 heures.

## Critères D'Acceptation

- Les endpoints retournent le format cible.
- Les tests backend de routes plateformes passent.
- Le contrat est prêt pour les adaptations frontend.
