Le but de la tache est de remplaccer le fonctionnement actuel qui permet à un utilisateur connecté de consulter les plateformes et les jeux d'un fichier ods configuré en paramètre .env par la consultation des plateformes et jeux associés a sa collection en base de données.

La lecture des fichiers ODS est désormais uniquement utilisée lors de la fonction d'import toute autre lecture est supprimée.

Toute lecture spécifique de la page acceuil du fichier ODS est supprimée du code.

Les pages frontend a modifier sont 
 - Ma collection
 - platform
 - wishlist

 Les controller backend a modifier
 - user_games_collection_controller : Renommer en collection_controller
 - platform_controller : Tous les endpoints liés à la collection sont extrait dans le nouveau controller collection_controller

 Toutes actions coté backend lié à la lecture des informations dans le fichier ODS et utiles à l'import sont regroupés dans un service services/collection/ods/UserCollectionODSReader. Ceci regroupe le contenu des service 
  - games_service
  - add_game_choise_service
 Toutes les fonctions non utiles lors de l'import sont supprimées. Si aucune n'est utile alors le service n'est pas créé les deux services cités sont supprimés. 
 Le téléchargement ODS reste autorisé uniquement comme téléchargement brut du fichier utilisateur. Le backend ne doit pas parser le contenu ODS pour cet endpoint.

 - La page Ma collection :
   affiche les mêmes informations que actuellement à savoir les plateformes et les statistiques par plateforme mais les informations sont désormais lues depuis la base de données coté backend via le controller collection_controller et le endpoint /collections/videogames/platforms/search. 
   Pour les statistiques globales, elles sont lues depuis le controller /collections/videogames.
 - La page plateforme :
   affiche les mêmes informations que actuellement à savoir tous les jeux de la plateforme selectionnée mais les informations sont désormais lues depuis la base de données coté backend via le controller collection_controller et le endpoint /collections/videogames/games/search. Toutefois, la selection de la plateforme se fait désormais par id dans l'url pour être plus efficace et la recherche coté backend ce fait également par id.
- La page wishlist est supprimée. Supprimer aussi la route frontend, les entrées de navigation éventuelles, les hooks/services dédiés et les permissions wishlist.

La pagination des endpoints est centralisée avec la pagination deja mise en place pour la bibliothèque et les endpoints associés.

Les actions de la page plateforme :
 - Supprimer : action non connecté : Cela sera une evolution future.
 - Modifier : action non connecté : Cela sera une evolution future.

 Coté backend, 
  controller user_whish_list_controller : supprimé.
  controller collection_controller :
  - GET "/collections/videogames" : Retourne les statistiques global de la collection de l'utilisateur
  ```json
  {
    "total": 420,
    "total_value": 0,
    "average_value" : 0,
    "max_platform": ""
  }
  ```
  Avec : 
    total : nombre total d'entrées dans la table t_user_collection pour l'utilisateur connecté
    total_value : 0. Sera calculée dans un future évolution.
    average_value : 0. Sera calculée dans un future évolution.
    max_platform: Retourne le nom de la plateforme dont l'utilisateur a le plus de jeux dans la table t_user_collection en lien avec la table t_platform. Retourne  "" si l'utilisateur n'a aucun jeux.
 Si l'utilisateur n'a aucun jeu on renvoi une réponse standard:
 ```json
 {
  "total": 0,
  "total_value": 0,
  "average_value": 0,
  "max_platform": ""
}
 ```

- GET "/collections/videogames/platforms/search" : Retourne la liste des plateformes pourlequel l'utilisateur a au moins une entrée dans la table "t_user_collection".
  Paramètre de recherche :
 - name : recherche de type contains, sans casse et sans accents.
 - page : numéro de la page a retourner. Défaut 0
 - size : taille de la page. défaut 500, maximum 500
 - sort : tri choix du nom de la colonne et du mode de tri example sort=name,asc. Colonnes autorisées : name
  Endpoint paginé
  ```json
  {
    "page": {
        "totalElements": 10,
        "page": 0,
        "size": 500,
        "totalPages": 1
    },
    "platforms": [
        {
            "id": 1,
            "name": "platform",
            "nb_games": 25,
            "total_value": 0,
            "average_value": 0
        },
    ]
  }
  ```
  Avec :
   nb_games : Nombre total de jeux dans la table t_user_collection dont le jeux associé est associé à la plateforme.
   total_value : 0. Ce champs sera calculé dans une autre évolution.
   average_value : 0. Ce champ sera calculé dans une autre évolution.

   - GET "/collections/videogames/games/search" : Retourne la liste des jeux de l'utilisateur présent dans la table "t_user_collection"
   Paramètres de recherche : 
     - name : recherche de type contains, sans casse et sans accents.
     - release_date : plage de date. release_date=YYYY-MM-DD..YYYY-MM-DD
     - studio_name : recherche de type contains, sans casse et sans accents.
     - platform_id : Si le paramètre est invalide ou ne correspond a aucun jeu de l'utilisateur alors on renvoie une liste vide.
     - platform_name : recherche de type contains, sans casse et sans accents.
     - page : numéro de la page a retourner. Défaut 0
     - size : taille de la page. défaut 500, maximum 500
     - sort : tri choix du nom de la colonne et du mode de tri example sort=name,asc. 
              Colonnes autorisées : name, platform_name, release_date, studio_name, buy_date, grade
   ```json
   {
    "page": {
        "totalElements": 10,
        "page": 0,
        "size": 500,
        "totalPages": 1
    },
     "games": [
        {
            "id": 1,
            "name": "",
            "platform_name": "",
            "platform_id": 1,
            "release_date": "",
            "studio_name": "",
            "studio_id": 10,
            "version": "",
            "buy_date": "",
            "buy_location": "",
            "grade": ""
        }
     ]
   }
   ```
   Avec : 
    - name : nom du jeu dans t_game
    - release_date : release_date du jeu dans t_game
    - studio_name : nom du studio associé au jeu dans t_game (lien avec t_studio)
    - studio_id : id du studio associé au jeu dans t_game
    - version : vide pour l'instant. Evolution fufure. Retourne "".
    - buy_date : vide pour l'instant. Evolution fufure. Retourne "".
    - buy_location : vide pour l'instant. Evolution fufure. Retourne "".
    - grade : vide pour l'instant. Evolution fufure. Retourne "".

 - GET /collections/videogames/download :
   Désormais le fichier téléchargé est le fichier de l'utilisateur courant trouvé dans la table t_user.collection_file_path. Si le fichier n'existe pas sur disque ou si le champ en base est vide, on retourne un 404.

- GET /collections/videogames/home :
   A supprimer.

- POST /collections/videogames/cache/reset : 
  A supprimer.

- GET  /collections/videogames/search : 
  A supprimer

- POST /collections/videogames/games : 
  A vider. Action implémenter plus tard. Retourner 501 Not Implemented. Reste dans  /api/routes.

- DELETE /collections/videogames/games : 
  A vider. Action implémenté plus tard. Retourner 501 Not Implemented. Reste dans  /api/routes.

- PUT /collections/videogames/games
  A vider. Action implémenté plus tard. Retourner 501 Not Implemented. Reste dans  /api/routes.

Endpoint  additionnel a supprimer : 
GET /collections/videogames/platforms
GET /collections/videogames/column-values
GET /collections/videogames/add-game-choices
GET /collections/videogames/platform-image/<platform>
POST/PUT/DELETE /collections/videogames/wishlist/games

Tous les endpoints  supprimés sont supprimés de /api/routes

Pour tous les nouveaux endpoints, on ne vérifie pas si l'utilisateur a importé sa collection ou non. Si il ne l'a pas importé alors les endpoints ne retourneront des informations vides car il n'y aura pas d'entrée dans la table t_user_collection.

Gestion du tri : Equivalent a celui de la bibliothèque.

Documentation : 
 - README: Mise a jour nécessaire.
 - documentation/** : Mettre a jour les documentation en fonction.

