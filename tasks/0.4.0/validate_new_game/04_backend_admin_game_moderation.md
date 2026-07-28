# 04 - Modération admin des jeux

## Objectif

Créer les actions backend permettant à un administrateur de valider ou refuser
un ou plusieurs jeux en attente.

Cette tâche dépend de `03_backend_public_library_visibility.md`.

## Règles Fonctionnelles

- Un `ADMIN` peut valider un ou plusieurs jeux.
- Valider passe les jeux sélectionnés à `status = ACCEPTED`.
- Les updates doivent être faits par blocs de 500 ids maximum.
- Un `ADMIN` peut refuser un ou plusieurs jeux.
- Refuser supprime les jeux sélectionnés de `t_game`.
- Refuser désassocie les jeux supprimés des collections utilisateur concernées.
- Les utilisateurs impactés reçoivent un email listant les jeux refusés.
- Un email utilisateur doit être envoyé après succès de la transaction de
  suppression.

## Contrat API À Implémenter

Définir et implémenter des endpoints protégés `ADMIN` pour :

- validation par lot ;
- refus par lot.

Les payloads doivent accepter une liste d'identifiants de jeux. Les réponses
doivent retourner au minimum :

- nombre de jeux demandés ;
- nombre de jeux validés ou refusés ;
- nombre d'utilisateurs impactés pour les refus ;
- erreurs ou ids ignorés si le contrat retenu autorise les succès partiels.

## Contraintes Techniques

- Utiliser le verrou global PostgreSQL partagé avec les imports et corrections
  de doublons.
- Garder les contrôleurs limités au mapping HTTP.
- Mettre la logique de validation/refus dans un service de domaine
  `library`.
- Mettre les requêtes SQL dans un repository dédié ou existant cohérent.
- Utiliser le système de templates email existant.

## Tests Attendus

Créer ou modifier les tests backend pour couvrir :

- refus d'accès sans profil `ADMIN` ;
- validation d'un jeu en attente ;
- validation par lot de plus de 500 ids avec découpage ;
- refus supprimant les rattachements `t_user_collection` ;
- refus notifiant chaque utilisateur impacté avec sa liste de jeux ;
- transaction rollback sans email si la suppression échoue ;
- route catalog exposant les nouveaux droits admin.

## Critères D'Acceptation

- Les endpoints admin existent et sont protégés.
- Les validations/refus fonctionnent par lot.
- Les utilisateurs impactés sont notifiés après refus réussi.
- Les tests backend ciblés passent.
