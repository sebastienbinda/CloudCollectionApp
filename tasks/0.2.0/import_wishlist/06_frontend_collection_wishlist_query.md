# 06 - Consultation frontend collection avec filtre wishlist

## Objectif

Adapter la consultation frontend de collection pour utiliser le filtre
`wishlist=false` et rester centrée sur la collection réelle.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/import_wishlist/00_existing_code_analysis_result.md`
- `tasks/0.2.0/import_wishlist/import_wishlist.md`

## Périmètre Frontend

Modifier les fichiers désignés par le rapport pour :

- passer `wishlist=false` dans les appels de la page collection actuelle ;
- accepter le champ `wishlist` retourné par le backend sans l'afficher dans le
  tableau collection ;
- adapter la lecture des statistiques si `GET /collections/videogames` retourne
  désormais les sections `collection` et `wishlist` ;
- conserver la navigation existante ;
- ne pas recréer une page wishlist dédiée dans ce périmètre.

## Tests Ou Validations Attendues

Ajouter ou modifier les tests disponibles, ou documenter la validation manuelle
si le projet n'a pas de tests frontend adaptés :

- la page collection demande `wishlist=false` ;
- les souhaits ne sont pas affichés dans le tableau collection ;
- les statistiques collection utilisent la section `collection` ;
- le champ `wishlist` en réponse ne casse pas le rendu existant.

## Critères D'Acceptation

- La page collection reste fonctionnelle.
- La page collection n'affiche pas les entrées wishlist.
- Le frontend ne dépend pas d'une page wishlist non créée.
- Le build frontend passe.
