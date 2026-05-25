# 06 - Frontend Ma collection et plateforme

## Objectif

Adapter les pages frontend `Ma collection` et `platform` pour consommer les
nouveaux endpoints SQL de collection utilisateur.

Cette tâche doit s'appuyer sur le rapport :

`tasks/user_collection_view/00_existing_code_analysis_result.md`

## Étapes

1. Lire et prendre en compte
   `tasks/user_collection_view/00_existing_code_analysis_result.md`.
2. Mettre à jour `VideoGamesApi` pour utiliser :
   - `GET /collections/videogames`
   - `GET /collections/videogames/platforms/search`
   - `GET /collections/videogames/games/search`
   - `GET /collections/videogames/download`
3. Supprimer les appels frontend aux routes supprimées :
   - `/collections/videogames/home`
   - `/collections/videogames/search`
   - `/collections/videogames/platforms`
   - `/collections/videogames/column-values`
   - `/collections/videogames/add-game-choices`
   - `/collections/videogames/platform-image/<platform>`
4. Adapter la page `Ma collection` pour afficher :
   - les statistiques globales depuis `GET /collections/videogames` ;
   - les plateformes depuis `GET /collections/videogames/platforms/search`.
5. Adapter la page `platform` pour charger les jeux depuis
   `GET /collections/videogames/games/search`.
6. Faire passer la plateforme sélectionnée par `platform_id` dans l'URL.
7. Adapter la navigation depuis `Ma collection` vers une plateforme avec son id.
8. Retirer l'affichage ou les appels liés à l'image plateforme ODS.
9. Masquer ou désactiver les actions `Modifier` et `Supprimer`, car elles sont
   prévues pour une évolution future.
10. Conserver les responsabilités existantes :
   - appels HTTP dans les services ;
   - orchestration dans les hooks ;
   - rendu dans les composants.

## Critères d'acceptation

- La page `Ma collection` n'utilise plus de données issues d'une lecture ODS.
- La page `platform` n'utilise plus de données issues d'une lecture ODS.
- La navigation de plateforme repose sur `platform_id`.
- Les pages gèrent les réponses vides.
- Le frontend ne tente plus d'appeler les endpoints supprimés.
- Les permissions wishlist et ODS supprimées ne sont plus utilisées.
- Les fichiers frontend modifiés correspondent à l'architecture validée dans le
  rapport d'analyse.

## Validation attendue

- Lancer `npm run build`.
- Tester manuellement les cas principaux si un serveur local est disponible :
   - utilisateur avec collection ;
   - utilisateur sans collection ;
   - sélection d'une plateforme ;
   - recherche de jeux ;
   - téléchargement ODS.
