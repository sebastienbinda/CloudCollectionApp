En tant qu'utilisateur connecté, je veux pouvoir importer un fichier au format csv contenant ma collection de jeu.
Pour l'instant seul le format ods librefofice est proposé il faut rajouter le format csv. 
Cela implique de  :
  - créer un nouveau reader coté backend
  - créer un nouveau format de configuration d'import

Le nouveau format de configuration d'import doit permettre uniquement de préciser la nom de la colonne qui correspond l'information nécessaire à l'import.
Il n'y a pas de notion de différentes feuilles comme pour libreoffice.

Le workflow coté user : 
 1. Je choisi le format de mon fichier 'csv"
 2. J'upload mon fichié
 2. Après upload, je demande l'analyse du fichier qui m'indique que c'est un format csv retourne les noms des colonnes du fichier csv
 3. Je choisi pour chaque information à quelle colonne ca correspond via une liste déroulante contenant les colonnes possibles
 Les informations possibles qu'il faut mapper sont les meme que pour le format ods a savoir : 
  - Nom du jeu 
  - Plateforme
  - Studio
  - Date de sortie
  - Prix d'achat
  - Lieu d'achat
  - Date d'achat
  - Note
  - Etat
  - Notice
  - Collector
  - Steelbook
  - Version digitale
  - Region
  - Description
  - Whishlist
Format json :
```json
{
    "file_type": "csv",
    "mapping": {
        "name": 1,
        "platform": 2,
        "studio": 3,
        "release_date": 4,
        "purchase_price": 5,
        "buy_location": 6,
        "buy_date": 7,
        "grade": 8,
        "condition": 9,
        "has_manual": 10,
        "region": 11,
        "collector": ,
        "steelbook": ,
        "description": ,
        "whishlist" : ,
        
    }
}`
```
Comme pour le format libreofice, apres upload et si une conf est déja sauvegardé elle est proposé a utiliser comme configuration a l'utilisation.
4. Je valide le formulaire et démarre l'import de la collection.

Important : Il faut que cela rentre dans le meme workflow que pour l'import de fichier excel. Le code doit etre adapté car il est prévu pour permettre un nouveau reader de fichier pour un format différent.

Coté IHM cela doit rester un workflow identique également.