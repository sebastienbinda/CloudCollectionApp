# 03 - Visibilité Bibliothèque publique et détail jeu

## Objectif

Adapter les endpoints de consultation Bibliothèque pour masquer les jeux en
attente aux visiteurs non administrateurs, tout en préservant l'accès Collection
du propriétaire.

Cette tâche dépend de `01_database_game_validation_status.md` et
`02_backend_import_status_assignment.md`.

## Règles Fonctionnelles

- `GET /api/library/games` doit retourner uniquement les jeux `ACCEPTED` pour
  les anonymes, `GUEST` et `USER`.
- `GET /api/library/games` doit retourner tous les jeux pour `ADMIN`.
- `GET /api/library/games/<game_id>` doit retourner `404` si le jeu est
  `WAITING_VALIDATION` et que le demandeur n'est pas `ADMIN` ni le propriétaire
  d'un rattachement dans sa collection.
- Un `USER` connecté peut ouvrir le détail d'un jeu `WAITING_VALIDATION` depuis
  sa collection si `t_user_collection` contient ce jeu.
- Les endpoints de collection protégés ne doivent pas filtrer les jeux selon
  `t_game.status`.
- Les compteurs Bibliothèque publics et les totaux de plateformes doivent
  appliquer les mêmes règles de visibilité que les listes publiques.

## Contraintes Techniques

- Préserver le caractère public des routes Bibliothèque.
- Accepter un Bearer optionnel sur les routes jeux quand il est présent.
- Ne pas exposer de données privées utilisateur dans les payloads Bibliothèque.
- Garder les décisions de visibilité dans les services/repositories backend,
  pas dans le frontend.

## Tests Attendus

Créer ou modifier les tests backend pour couvrir :

- liste anonyme masquant `WAITING_VALIDATION` ;
- liste `USER` masquant `WAITING_VALIDATION` ;
- liste `ADMIN` affichant tous les statuts ;
- détail anonyme d'un jeu en attente retournant `404` ;
- détail `USER` propriétaire d'un jeu en attente retournant `200` ;
- détail `USER` non propriétaire retournant `404` ;
- détail `ADMIN` retournant `200` ;
- endpoints Collection continuant à retourner les jeux rattachés.

## Critères D'Acceptation

- Les jeux en attente ne sont pas visibles publiquement.
- Les utilisateurs peuvent consulter leurs propres jeux en attente depuis leur
  collection.
- Les administrateurs gardent une vue complète.
- Les tests backend ciblés passent.
