# 04 - Résultat contrat du résultat d'import

## Résumé

La tâche 4 a été implémentée côté backend.

## Changements Réalisés

- Remplacement du compteur public `created_platforms` par `linked_platforms`.
- `UserCollectionImportPersistenceResult` expose maintenant
  `linked_platforms`.
- `UserCollectionImportResult.to_dict()` sérialise `linked_platforms`.
- Le compteur est calculé après matching sur les plateformes distinctes du
  référentiel réellement liées aux jeux importés.
- Le champ `created_platforms` n'est plus présent dans le payload backend.
- Les warnings ajoutés par la tâche 03 sont conservés :
  `platform_matches` et `skipped_games`.

## Tests Ajoutés Ou Modifiés

- Tests service d'import adaptés à `linked_platforms`.
- Tests route d'import vérifiant `linked_platforms` et l'absence de
  `created_platforms`.
- Test repository vérifiant le comptage de plateformes liées distinctes sans
  insertion plateforme.
- Tests wishlist adaptés au nouveau contrat de résultat.

## Validations

- Tests ciblés contrat import :
  `33 tests`, statut `OK`.

## Points Pour Les Tâches Suivantes

- La tâche 06 doit remplacer l'affichage frontend `created_platforms` par
  `linked_platforms`.
- La tâche 09 doit mettre à jour `documentation/backend-api.md` et
  `documentation/import.md`.
