# 03 - Controller backend collection

## Objectif

Brancher la lecture SQL utilisateur dans un controller backend dédié à la
collection.

Cette tâche doit s'appuyer sur le rapport :

`tasks/user_collection_view/00_existing_code_analysis_result.md`

## Étapes

1. Lire et prendre en compte
   `tasks/user_collection_view/00_existing_code_analysis_result.md`.
2. Renommer `user_games_collection_controller` en `collection_controller`.
3. Adapter l'enregistrement du controller dans l'application Flask.
4. Extraire du `platform_controller` les endpoints qui concernent la collection
   utilisateur.
5. Ajouter ou remplacer les routes :
   - `GET /collections/videogames`
   - `GET /collections/videogames/platforms/search`
   - `GET /collections/videogames/games/search`
   - `GET /collections/videogames/download`
   - `POST /collections/videogames/games`
   - `PUT /collections/videogames/games`
   - `DELETE /collections/videogames/games`
6. Récupérer l'identité de l'utilisateur connecté via les mécanismes
   d'authentification existants.
7. Appeler le service SQL de consultation créé dans la tâche 02.
8. Faire retourner `501 Not Implemented` aux actions futures :
   - ajout de jeu ;
   - modification de jeu ;
   - suppression de jeu.
9. Modifier `GET /collections/videogames/download` pour :
   - lire `t_user.collection_file_path` pour l'utilisateur connecté ;
   - retourner `404` si le champ est vide ;
   - retourner `404` si le fichier n'existe pas sur disque ;
   - envoyer le fichier brut sans parser le contenu ODS.

## Critères d'acceptation

- Le controller ne manipule pas directement SQL.
- Le controller ne lit pas l'ODS.
- Le téléchargement ODS ne fait qu'envoyer le fichier utilisateur brut.
- Les routes SQL retournent les contrats définis dans la tâche 02.
- Les actions non implémentées retournent `501`.
- Les routes nécessitent un Bearer token selon les règles existantes.
- La cartographie controller/service du rapport d'analyse est respectée ou tout
  écart est justifié.

## Validation attendue

- Ajouter ou mettre à jour les tests de routes backend.
- Tester :
   - `GET /collections/videogames` ;
   - `GET /collections/videogames/platforms/search` ;
   - `GET /collections/videogames/games/search` ;
   - `GET /collections/videogames/download` avec fichier existant ;
   - `GET /collections/videogames/download` avec champ vide ;
   - `GET /collections/videogames/download` avec fichier absent ;
   - `POST /collections/videogames/games` en `501` ;
   - `PUT /collections/videogames/games` en `501` ;
   - `DELETE /collections/videogames/games` en `501`.
