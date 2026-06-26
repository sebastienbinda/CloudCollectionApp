En tant qu'administrateur depuis la section configuration je veux un nouvel encart dédié au profile ADMIN qui permet d'importer un fichier csv en réutilisant le reader existant mais pour ajouter des jeux a la collection de l'utilisateur qui n'a pas de collection car ADMIN mais juste pour ajouter les jeux, et studios dans la biblotheque.
Nouvel écran d'import : 
 - Pas de section wishlist
 - Pas d'information liées à la collection comme "date d'achat" par exemple.
 - Pas de sauvegarde de la configuration d'import
 - Uniquement format csv proposé
 - Configuration fix de l'import, pas de configuration de mapping custom.
 Configuration fix de l'import : 
 Format json :
```json
{
    "file_type": "csv",
    "mapping": {
        "name": 1,
        "platform": 2,
        "studio": 3,
        "release_date": 4        
    }
}
````
Cette configuration fix est un fichier json sauvegardé coté backend dans resources/admin_import_conf.json

Le fichier importé n'est pas sauvegardé sur disque, uniquement utilisé pour l'import.
Si il est nécessaire de le sauvegardé sur disque pour garder le code commun avec l'import standard, c'est possible mais il faut le supprimer a la fin de l'import quoi qu'il arrive meme en cas d'erreur.