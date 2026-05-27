# 05 - Suppression de la wishlist

## Objectif

Retirer la fonctionnalité wishlist du périmètre backend et frontend actuel.

Cette tâche doit s'appuyer sur le rapport :

`tasks/user_collection_view/00_existing_code_analysis_result.md`

## Étapes backend

1. Lire et prendre en compte
   `tasks/user_collection_view/00_existing_code_analysis_result.md`.
2. Supprimer `user_wishlist_controller`.
3. Supprimer l'enregistrement du controller wishlist dans l'application Flask.
4. Supprimer les routes :
   - `POST /collections/videogames/wishlist/games`
   - `PUT /collections/videogames/wishlist/games`
   - `DELETE /collections/videogames/wishlist/games`
5. Supprimer ou isoler le code backend uniquement utilisé par la wishlist.
6. Vérifier que les routes wishlist sont absentes de `/api/routes`.

## Étapes frontend

1. Supprimer la route frontend wishlist.
2. Supprimer les entrées de navigation wishlist éventuelles.
3. Supprimer les hooks dédiés à la wishlist.
4. Supprimer les services dédiés à la wishlist.
5. Supprimer les permissions wishlist dans le service d'accès aux routes.
6. Supprimer les usages de composants uniquement dédiés à la wishlist.

## Critères d'acceptation

- La wishlist n'est plus accessible depuis l'interface.
- Les endpoints wishlist ne sont plus enregistrés.
- Les endpoints wishlist sont absents de `/api/routes`.
- Le frontend ne référence plus les services ou hooks wishlist supprimés.
- Les routes wishlist retournent `404`.
- Les éléments wishlist identifiés dans le rapport d'analyse sont supprimés ou
  explicitement conservés avec justification.

## Validation attendue

- Ajouter ou mettre à jour les tests backend.
- Lancer le build frontend.
- Vérifier par recherche code l'absence des références wishlist supprimées.
