# 01 - Contrat et périmètre

## Objectif

Stabiliser le périmètre fonctionnel et les contrats HTTP avant de modifier le
code applicatif.

Cette tâche doit s'appuyer sur le rapport :

`tasks/user_collection_view/00_existing_code_analysis_result.md`

## Étapes

1. Lire et prendre en compte
   `tasks/user_collection_view/00_existing_code_analysis_result.md`.
2. Relire `tasks/user_collection_view/user_collection_view.md`.
3. Corriger les libellés et noms ambigus restants :
   - `user_whish_list_controller` vers `user_wishlist_controller`
   - `platform` pour les noms techniques
   - `plateforme` pour les descriptions fonctionnelles en français
4. Confirmer que les nouveaux endpoints de consultation sont :
   - `GET /collections/videogames`
   - `GET /collections/videogames/platforms/search`
   - `GET /collections/videogames/games/search`
   - `GET /collections/videogames/download`
5. Confirmer que `POST`, `PUT` et `DELETE /collections/videogames/games`
   restent enregistrés et retournent `501 Not Implemented`.
6. Confirmer que les endpoints supprimés ne sont plus enregistrés et sont donc
   absents de `/api/routes`.
7. Ajouter les réponses vides attendues pour les endpoints paginés.
8. Ajouter la liste des tests attendus dans la tâche de référence.

## Réponses vides attendues

### Plateformes

```json
{
  "page": {
    "totalElements": 0,
    "page": 0,
    "size": 500,
    "totalPages": 0
  },
  "platforms": []
}
```

### Jeux

```json
{
  "page": {
    "totalElements": 0,
    "page": 0,
    "size": 500,
    "totalPages": 0
  },
  "games": []
}
```

## Critères d'acceptation

- Le contrat des routes est clair et ne contient plus de route au singulier
  `/collection/...`.
- La suppression de la wishlist est explicitement décrite côté backend,
  frontend, permissions et navigation.
- Le comportement des routes supprimées est clair : elles ne sont plus
  enregistrées.
- Le comportement des actions futures est clair : elles retournent `501`.
- Le téléchargement ODS est décrit comme un téléchargement brut sans parsing.
- Les décisions du rapport d'analyse sont respectées ou les écarts sont
  explicitement justifiés.

## Validation attendue

- Relire la tâche principale.
- Vérifier qu'aucun point de contrat ne demande une décision implicite pendant
  l'implémentation.
