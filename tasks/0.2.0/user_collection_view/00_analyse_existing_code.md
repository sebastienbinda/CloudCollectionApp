# 00 - Analyse du code existant

## Objectif

Produire un rapport d'analyse du code actuel avant de développer la consultation
SQL de collection utilisateur.

Le rapport doit permettre de valider l'architecture cible et les modifications
prévues avant toute implémentation.

Le livrable attendu est un fichier Markdown :

`tasks/user_collection_view/00_existing_code_analysis_result.md`

## Étapes

1. Lire `tasks/user_collection_view/user_collection_view.md`.
2. Lire les tâches découpées :
   - `tasks/user_collection_view/01_contract_and_scope.md`
   - `tasks/user_collection_view/02_backend_sql_collection_read_model.md`
   - `tasks/user_collection_view/03_backend_collection_controller.md`
   - `tasks/user_collection_view/04_remove_legacy_ods_collection_routes.md`
   - `tasks/user_collection_view/05_remove_wishlist_feature.md`
   - `tasks/user_collection_view/06_frontend_collection_sql_views.md`
   - `tasks/user_collection_view/07_cleanup_documentation_validation.md`
3. Lire les documentations concernées :
   - `documentation/backend-api.md`
   - `documentation/backend-arch.md`
   - `documentation/frontend-arch.md`
   - `documentation/database.md`
   - `documentation/authentication.md`
   - `documentation/site-plan.md`
   - `documentation/menu.md`
4. Identifier les endpoints backend actuels de collection, plateformes,
   wishlist et ODS :
   - routes à remplacer ;
   - routes à supprimer ;
   - routes à conserver ;
   - routes à créer.
5. Identifier les contrôleurs backend à modifier ou supprimer :
   - `user_games_collection_controller`
   - `platform_controller`
   - `user_wishlist_controller`
   - tout enregistrement associé dans la composition Flask.
6. Identifier les services backend actuels qui lisent ou écrivent l'ODS :
   - services à supprimer ;
   - services à limiter à l'import ;
   - méthodes à déplacer ou à conserver.
7. Identifier les repositories SQL existants à réutiliser ou étendre :
   - utilisateurs ;
   - plateformes ;
   - studios ;
   - jeux ;
   - associations `t_user_collection` ;
   - fichier utilisateur `t_user.collection_file_path`.
8. Identifier les modèles et champs database réellement disponibles :
   - `t_user.collection_file_path`
   - `t_user_collection.user_id`
   - `t_user_collection.game_id`
   - `t_user_collection.game_additional_name`
   - `t_game.id`
   - `t_game.name`
   - `t_game.release_date`
   - `t_game.developer`
   - `t_game.platform`
   - `t_platform.id`
   - `t_platform.name`
   - `t_studio.id`
   - `t_studio.name`
9. Identifier les conventions existantes à réutiliser pour :
   - pagination ;
   - tri ;
   - filtres sans casse et sans accents ;
   - réponses paginées ;
   - erreurs HTTP ;
   - protection Bearer ;
   - catalogue `/api/routes`.
10. Identifier les impacts frontend :
   - services API ;
   - hooks `home`, `platforms`, `games`, `wishlist`, `collection` ;
   - routing et URL `platform_id` ;
   - navigation et menu ;
   - permissions d'action ;
   - composants liés aux images ODS et à la wishlist.
11. Identifier les tests existants à modifier et les nouveaux tests à créer.
12. Identifier les documents à mettre à jour.
13. Créer `tasks/user_collection_view/00_existing_code_analysis_result.md`.
14. Dans le rapport, proposer une architecture cible validable avant
    développement.

## Contenu attendu du rapport

Le fichier `00_existing_code_analysis_result.md` doit contenir au minimum :

1. Synthèse de l'état actuel.
2. Liste des documentations relues.
3. Cartographie des endpoints actuels.
4. Tableau des endpoints cibles :
   - endpoint ;
   - méthode HTTP ;
   - controller cible ;
   - service cible ;
   - statut : créé, remplacé, supprimé, conservé.
5. Cartographie des contrôleurs backend à modifier, renommer ou supprimer.
6. Cartographie des services ODS actuels et décision pour chacun :
   - supprimer ;
   - conserver pour import ;
   - conserver pour téléchargement brut ;
   - remplacer par lecture SQL.
7. Proposition d'architecture backend cible :
   - controller ;
   - service métier ;
   - repositories ;
   - objets de critères ou contrats si nécessaires.
8. Proposition d'architecture frontend cible :
   - services API ;
   - hooks ;
   - pages ;
   - navigation ;
   - permissions.
9. Contrats SQL et champs utilisés.
10. Stratégie de pagination, tri et filtres.
11. Stratégie de suppression de la wishlist.
12. Stratégie de suppression des routes ODS hors import.
13. Tests backend à ajouter ou modifier.
14. Tests ou validations frontend à effectuer.
15. Documentation à mettre à jour.
16. Risques techniques et points à valider avant développement.

## Critères d'acceptation

- Le fichier `tasks/user_collection_view/00_existing_code_analysis_result.md`
  existe.
- Les endpoints actuels et cibles y sont listés.
- Les fichiers backend à modifier, supprimer ou créer y sont listés.
- Les fichiers frontend à modifier, supprimer ou créer y sont listés.
- Les services ODS à supprimer ou à conserver pour l'import y sont identifiés.
- Les repositories SQL à réutiliser ou étendre y sont identifiés.
- Les impacts sur `/api/routes` y sont explicités.
- Les impacts wishlist y sont explicités.
- Les tests attendus y sont listés.
- Les documents à mettre à jour y sont listés.
- Les risques et arbitrages restants y sont visibles.

## Validation attendue

- Aucun changement fonctionnel.
- Aucun test applicatif obligatoire.
- Relire et valider le rapport avant de démarrer la tâche 01.
