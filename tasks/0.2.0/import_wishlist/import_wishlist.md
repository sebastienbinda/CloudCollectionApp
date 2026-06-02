L'objectif de la tache est double :
 - Ajouter  un champ wishlist de type boolean dans la table t_user_collection pour indiquer si oui ou non le jeux de la collection de l'utilisateur est dans sa collection (wishlist=false) ou si le jeu est un souhait (wishlist=true). La  valeur de cette nouvelle colonne est false par défaut.
 - Permettre lors de l'import d'indiquer le champ ou l'onget du fichier de collection qui contient l'information

Lors de l'import le workflow est donc modifié.
 - Coté IHM on affiche que la section d'upload du fichier et le choix tu type de fichier dans un premier temps. Le reste est caché avant d'avoir le retour du backend sur l'analyse du fichier
 - Une fois l'analyse terminée le reste du formulaire est affichée.
 - Une fois la plage de données selectionnée :
    - l'information header row est préremplie avec la première ligne  de plage saisie.
    - les informations de mapping sont préremplies avec les colonnes de la plage en commencant par la première  pour la première information.
 - Une nouvelle section wishlist est ajoutée avant la selection des plages de données de la collection, cette  section permet de définir ou trouver l'information de wishlist dans le fichier. Plusieurs possibilités : 
    - Pas de wishlist
    - Un onglet dédié
    - Une colonne dédiée dans chaque onglet.
 - Désormais après le retour 200 du succès d'import, il faut afficher un nouvel écran qui affiche le résumé de l'import avec les informations retournées par le backend. Un message explicatif des résultats est ajouté en entête de la page. Ce  message doit également expliqué que la collection est désormais consultable via le menu associé. Ceci est une modification de la spec actuelle et il ne faut donc plus rediriger vers la page collection après l'import mais proposé un lien vers cette page et la documentation doit être mise  a jour en conséquence.
    
 Cas pas de wishlist : 
  Rien de change a l'import actuel et le json de configuration de l'import est enrichie d'une section wishlist vide 
  ```json
  {
    "wishlist": {
        "mode": "none"
    }
  }
  ```

Cas un onglet dédié : 
 Dans ce cas une nouvelle section de configuration apparait en fin du formulaire demandant la plage de données et le mapping des informations identique a celles demandées pour la collection. Le code coté frontend doit être  centraliser pour afficher ce composent afin de ne pas dupliquer et réutiliser le même composant react.
le json de configuration de l'import est enrichie :

 ```json
{
  "wishlist": {
    "mode": "sheet",
    "sheet_name": "Wishlist",
    "data_range": "A1:H200",
    "header_row": 1,
    "column_information": {
      "name": "A",
      "platform": "B",
      "studio": "C",
      "release_date": "D"
    }
  }
}
```

Cas colonne dédiée dans chaque onglet de la collection :
 Sous cas collection `single_sheet_conf` : 
  Modification de la configuration du mapping colonne/inforamtion existant pour ajouter le mapping de la nouvelle contenant l'information.
  le json de configuration de l'import est enrichie 
  ```json
{
  "file_type": "libreoffice_ods",
  "wishlist": {
    "mode": "column"
  },
  "single_sheet_conf": {
    "data_range": "A1:H200",
    "header_row": 1,
    "column_information": {
      "name": "A",
      "platform": "B",
      "studio": "C",
      "release_date": "D",
      "wishlist": "E"
    }
  }
}
```
Sous cas collection `multiple_sheets_conf.shared_layout` :
 Dans ce cas le mapping est ajoutée a la configuration partagée du mapping.  le json de configuration de l'import est enrichie 
 ```json
{
  "file_type": "libreoffice_ods",
  "wishlist": {
    "mode": "column"
  },
  "multiple_sheets_conf": {
    "sheet_information": "platform",
    "shared_layout": {
      "included_sheets": ["Sheet1", "Sheet2"],
      "excluded_sheets": [],
      "data_range": "A1:H200",
      "header_row": 1,
      "column_information": {
        "name": "A",
        "studio": "C",
        "release_date": "D",
        "wishlist": "E"
      }
    }
  }
}
```
Sous  cas collection `multiple_sheets_conf.sheets` :
 Dans  ce cas le mapping est ajouter a la configuration de chaque onglet individuel. e json de configuration de l'import est enrichie 
 ```json
{
  "file_type": "libreoffice_ods",
  "wishlist": {
    "mode": "column"
  },
  "multiple_sheets_conf": {
    "sheets": [
      {
        "sheet_name": "Playstation",
        "sheet_information": "platform",
        "data_range": "A1:H200",
        "header_row": 1,
        "column_information": {
          "name": "A",
          "studio": "C",
          "release_date": "D",
          "wishlist": "E"
        }
      }
    ]
  }
}
```

Coté  backend :

POST /api/users/import/analyze/{file_type} : non impacté
POST  /api/users/import/file/{file_type} : non impacté
POST /api/users/import : Modifier pour sauvegarder la nouvelle configuration d'import et prendre en compte le nouvel élément à lire du fichier de collection et a ajouter en base de données, en gardant la généricité du type de fichier et l'implémentation adéquate.
Le format attendue des valeurs dans la nouvelle colonne peux être : 
 - Oui/Non (on ignore la casse)
 - O/N (on ignore la casse)
 - True/False (on ignore la casse)
 - Yes/No (on ignore la casse)
 - Y/N (on ignore la casse)
Si c'est un onglet dédié et non une colonne, alors l'information est automatiquement positionnée  a true en bd pour les jeux ajoutés a la collection de l'onglet dédiée.

Cas d'erreur : 
 - L'onglet dédié : Même type d'erreur que pour les onglets de la collection
 - Colonne dans les onglets existant : Si la valeur de la colonne configurée ne  correspond a aucune des valeurs attendues : On ne rollback pas l'import on continue. le jeu n'est pas ajouté a la collection. Un warning dans les logs est affichée. Dans le json de retour on indique le nombre de jeux pour lesquels la colonne wishlist est invalide et la liste des valeurs invalide detectées.

Cas spéciaux : 
 - Si un  jeu est présent à la fois dans l'onglet dédié wishlist et dans un autre onglet à importer, alors le jeu n'est pas dupliqué en base de données et il est noté wishlist=false.
 - Si un est jeu est en double dans l'onglet wishlist, on ne conserve que le premier
 - Si un jeu est en double avec wishlist=true et wishlist=false alors ne conserve que le premier avec wishlist=true.
 - ligne avec valeur wishlist vide : -> Valeur par défaut de wishlist=false
 - valeur invalide : on ignore la ligne complètement

 Modification du retour pour ajouter les nouvelles informations : 
 ```json
{
  "created_platforms": 3,
  "created_studios": 12,
  "created_games": 42,
  "associated_games": 58,
  "wishlisted_games": 12,
  "warnings": {
    "invalid_wishlist": 3,
    "invalid_wishlist_values_found" : [ "Ok", "Peut etre", "Nop" ]
  }
}
```

La nouvelle information wishlist en base de données :
 - Cette nouvelle information n'est pas affichée dans la page collection.
 - Le endpoint de recherche existant /collections/videogames/games/search est modifié pour ajouter un filtre de recherche sur ce nouveau paramètre et pour retourner la valeur dans le json de retour. Par défaut la page actuelle de collection passe toujours ce paramètre à false.
 - Le endpoint /collections/videogames est modifié pour envoyer les statistiques de wishlist et les calculs total, total_value et average_value sont calculés sur les entrées dont la colonne wishlist est false.
 ```json
{
    "collection": {
        "total": 420,
        "total_value": 0,
        "average_value": 0,
        "max_platform": "Switch"
    },
    "wishlist": {
        "total": 420,
        "total_value": 0,
        "average_value": 0,
        "max_platform": "Switch"
    }
}
```

Documentation : 
La documentation database.md, import.md, backend-api.md, site-plan.md doit être mise a jour.
La documentation collection.md doit être créée car elle manque, et indiquer le fonctionnement de la consultation de la collection de l'utilisateur.
Mise a jour du README.md en restant très synthétique.

Sous-tâches :

1. `00_existing_code_analysis_and_architecture.md` : analyser le code existant
   et produire `00_existing_code_analysis_result.md` avec l'architecture cible
   et les noms des classes, méthodes, composants et tests à créer ou modifier.
2. `01_wishlist_import_contract.md` : stabiliser et valider le contrat JSON
   wishlist.
3. `02_database_wishlist_schema.md` : ajouter la colonne SQL `wishlist` et
   adapter ORM / repositories.
4. `03_backend_import_wishlist.md` : intégrer la wishlist dans le workflow
   backend d'import.
5. `04_backend_collection_wishlist_query.md` : adapter les endpoints SQL de
   consultation collection.
6. `05_frontend_import_wishlist_workflow.md` : adapter l'onboarding import et
   l'écran de résumé.
7. `06_frontend_collection_wishlist_query.md` : adapter la page collection pour
   demander `wishlist=false`.
8. `07_documentation_and_validation.md` : mettre à jour la documentation et
   valider l'ensemble.

Toutes les sous-tâches à partir de `01` doivent s'appuyer sur
`00_existing_code_analysis_result.md`.
