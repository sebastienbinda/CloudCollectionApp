# 04 - Consultation backend collection et wishlist

## Objectif

Adapter les endpoints SQL de collection pour prendre en compte
`t_user_collection.wishlist` dans les filtres, les résultats et les
statistiques.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/import_wishlist/00_existing_code_analysis_result.md`
- `tasks/0.2.0/import_wishlist/import_wishlist.md`

## Endpoints Impactés

- `GET /collections/videogames`
- `GET /collections/videogames/games/search`

## Règles Attendues

Pour `GET /collections/videogames/games/search` :

- ajouter un filtre `wishlist` ;
- retourner la valeur `wishlist` dans chaque jeu ;
- conserver la pagination et les tris existants ;
- la page collection frontend doit pouvoir demander explicitement
  `wishlist=false`.

Pour `GET /collections/videogames` :

- retourner une section `collection` ;
- retourner une section `wishlist` ;
- calculer les totaux collection sur les lignes `wishlist=false` ;
- calculer les totaux wishlist sur les lignes `wishlist=true` ;
- conserver les autres contrats existants sauf décision contraire documentée
  dans le rapport d'analyse.

## Tests Attendus

Ajouter ou modifier des tests backend couvrant :

- recherche de jeux avec `wishlist=false` ;
- recherche de jeux avec `wishlist=true` ;
- recherche sans filtre selon la règle décidée dans le rapport d'analyse ;
- présence du champ `wishlist` dans les lignes de réponse ;
- statistiques séparées collection et wishlist ;
- pagination et tri inchangés.

## Critères D'Acceptation

- Les endpoints restent protégés comme avant.
- Les réponses restent compatibles avec les contrats documentés.
- La consultation collection n'affiche pas les souhaits si le frontend demande
  `wishlist=false`.
- Les tests backend ciblés passent.
