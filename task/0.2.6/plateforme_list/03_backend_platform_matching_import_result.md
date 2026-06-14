# 03 - Résultat matching des plateformes pendant l'import

## Résumé

La tâche 3 a été implémentée côté backend.

## Changements Réalisés

- Ajout d'une configuration de matching plateformes :
  `PlatformMatchingConfiguration`.
- Ajout d'un service de matching plateformes :
  `PlatformMatchingService`.
- Ajout d'une notification administrateur pour les scores faibles :
  `PlatformMatchingAdminNotifier`.
- Utilisation du cache serveur plateformes par le repository d'import via le
  repository plateformes.
- Suppression de la création de plateformes pendant l'import utilisateur :
  les plateformes sont uniquement rattachées au référentiel existant.
- Filtrage des jeux sans plateforme fiable avant persistance.
- Filtrage des studios pour ne conserver que ceux des jeux effectivement
  importés.

## Seuils Appliqués

- `MATCHING_LOW_LVL_RATING`, défaut `25`.
- `MATCHING_HIGH_LEVEL_RATING`, défaut `75`.
- `score >= seuil haut` : import sans warning plateforme.
- `seuil bas <= score < seuil haut` : import avec warning `platform_matches`
  et email administrateur si `ADMIN_NOTIFICATION_EMAIL` est configuré.
- `0 < score < seuil bas` : jeu ignoré avec warning `skipped_games`.
- `score = 0` : jeu ignoré avec warning `skipped_games`.
- Ambiguïté entre plusieurs plateformes au meilleur score : jeu ignoré avec
  warning `skipped_games`.

## Contrat De Warnings

Le dictionnaire `warnings` contient maintenant :

- `invalid_wishlist` ;
- `invalid_wishlist_values_found` ;
- `invalid_games` ;
- `platform_matches` ;
- `skipped_games`.

## Tests Ajoutés Ou Modifiés

- Tests de configuration des seuils.
- Tests du matching exact, casse, accents, espaces et coquille mineure.
- Tests des scores faibles acceptés avec warning.
- Tests des scores trop faibles, score nul et ambiguïtés.
- Tests de notification email administrateur.
- Test de non-création de plateforme pendant l'import.
- Tests de routes et résultat d'import adaptés aux nouveaux warnings.

## Validations

- Tests ciblés matching/import/routes :
  `36 tests`, statut `OK`.
- Suite backend complète :
  `380 tests`, statut `OK`.

## Points Pour Les Tâches Suivantes

- La tâche 04 doit remplacer le compteur public `created_platforms` par un
  compteur de plateformes liées au référentiel.
- La tâche 04 doit conserver les warnings `platform_matches` et `skipped_games`
  dans le contrat HTTP.
- La tâche 09 doit documenter les variables de seuils, les warnings de matching
  et l'email administrateur.
