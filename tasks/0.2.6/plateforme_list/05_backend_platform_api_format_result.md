# 05 - Résultat format API plateformes backend

## Résumé

La tâche 5 a été implémentée côté backend.

## Changements Réalisés

- Le format public Bibliothèque des plateformes reste aligné sur `t_platform` :
  `id`, `name`, `release_date`, `end_date`, `manufacturer`, `description` et
  `total_games`.
- La recherche de plateformes de collection expose aussi les champs catalogue :
  `release_date`, `end_date`, `manufacturer`, `description` et `total_games`.
- Le champ obsolète `status` n'est pas exposé par les payloads plateformes.
- Les compteurs collection historiques sont conservés sur l'endpoint collection :
  `nb_games`, `total_value` et `average_value`.
- Le tri des plateformes de collection accepte désormais `name`,
  `release_date`, `end_date` et `manufacturer`.
- Les tâches suivantes ont été ajustées :
  - tâche 06 : consommation frontend des champs plateformes collection ;
  - tâche 07 : couverture explicite des endpoints public et collection.

## Cache

- Le cache serveur du catalogue plateformes reste utilisé par la recherche
  publique Bibliothèque et par les imports via le repository plateformes.
- L'endpoint collection continue de lire SQL directement, car son résultat est
  dépendant de l'utilisateur, de la wishlist et des compteurs de collection.

## Tests Ajoutés Ou Modifiés

- Tests route collection vérifiant le nouveau format, `end_date`, `total_games`
  et l'absence de `status`.
- Tests repository collection vérifiant la sélection SQL des nouvelles colonnes
  et les tris `manufacturer` avec fallback `name`.
- Tests service collection vérifiant la sérialisation des dates, descriptions et
  compteurs.
- Test parseur collection vérifiant les tris plateformes catalogue.

## Validations

- Tests ciblés :
  `71 tests`, statut `OK`.

## Points Pour Les Tâches Suivantes

- La tâche 06 doit adapter le frontend aux champs ajoutés et remplacer
  `created_platforms` par `linked_platforms` dans le résumé d'import.
- La tâche 07 doit compléter la non-régression backend globale, notamment cache,
  endpoints public et collection, matching et import.
- La tâche 09 doit mettre à jour `documentation/backend-api.md`.
