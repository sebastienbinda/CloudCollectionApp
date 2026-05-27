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
   - utiliser `user_wishlist_controller` pour le controller wishlist
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

## Contrat HTTP confirmé

Les endpoints de consultation conservés ou créés sont :

- `GET /collections/videogames`
- `GET /collections/videogames/platforms/search`
- `GET /collections/videogames/games/search`
- `GET /collections/videogames/download`

Les endpoints d'actions futures restent enregistrés dans `/api/routes` et
retournent `501 Not Implemented` :

- `POST /collections/videogames/games`
- `PUT /collections/videogames/games`
- `DELETE /collections/videogames/games`

Les endpoints supprimés ne sont plus enregistrés dans Flask. Ils retournent donc
`404` par absence de route et sont absents de `/api/routes`.

Le téléchargement ODS est un téléchargement brut du fichier utilisateur courant
trouvé via `t_user.collection_file_path`. Le backend ne parse pas le contenu ODS
pour cet endpoint.

## Endpoints supprimés

- `GET /collections/videogames/home`
- `POST /collections/videogames/cache/reset`
- `GET /collections/videogames/search`
- `GET /collections/videogames/platforms`
- `GET /collections/videogames/column-values`
- `GET /collections/videogames/add-game-choices`
- `GET /collections/videogames/platform-image/<platform>`
- `POST /collections/videogames/wishlist/games`
- `PUT /collections/videogames/wishlist/games`
- `DELETE /collections/videogames/wishlist/games`

## Suppression wishlist confirmée

La wishlist est retirée du périmètre :

- backend : suppression de `user_wishlist_controller`, de son enregistrement
  Flask et des routes `/collections/videogames/wishlist/games` ;
- frontend : suppression de la route, des entrées de navigation, des hooks, des
  services, des composants dédiés et des permissions wishlist ;
- permissions et navigation : aucune permission ou action wishlist ne doit
  rester exposée par l'interface.

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
- Vérifier que la tâche principale contient la liste des tests attendus.
