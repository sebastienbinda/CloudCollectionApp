# 02 - Statut initial lors des imports

## Objectif

Appliquer le bon statut initial aux jeux créés selon le contexte d'import.

Cette tâche dépend de `01_database_game_validation_status.md`.

## Règles Fonctionnelles

- Un jeu créé par l'import de collection d'un utilisateur doit être créé avec
  `status = WAITING_VALIDATION`.
- Un jeu créé par l'import CSV admin doit être créé avec `status = ACCEPTED`.
- Un jeu créé pendant un reset admin de la Bibliothèque doit être créé avec
  `status = ACCEPTED`.
- Le matching d'import peut rattacher un jeu importé à un jeu existant quel que
  soit son statut.
- Le statut d'un jeu existant ne doit pas être modifié par un simple
  rattachement d'import.

## Périmètre Backend

Modifier les services/repositories d'import pour :

- transmettre explicitement le statut de création attendu ;
- éviter une valeur implicite partagée entre import utilisateur, import admin et
  reset ;
- préserver le verrou global d'import existant ;
- préserver les compteurs d'import existants.

## Hors Périmètre

- Filtrage des endpoints Bibliothèque.
- Endpoints de modération admin.
- Frontend.
- Documentation finale.

## Tests Attendus

Créer ou modifier les tests backend pour couvrir :

- import utilisateur créant un nouveau jeu `WAITING_VALIDATION` ;
- import utilisateur rattachant un jeu existant `WAITING_VALIDATION` ou
  `ACCEPTED` sans changer son statut ;
- import CSV admin créant un nouveau jeu `ACCEPTED` ;
- reset Bibliothèque créant les nouveaux jeux `ACCEPTED`.

## Critères D'Acceptation

- Les statuts de création sont explicites par contexte.
- Le matching reste indépendant du statut.
- Les compteurs d'import restent cohérents.
- Les tests backend ciblés passent.
