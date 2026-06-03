Il faut désormais que la liste des type de fichier autorisé lors de l'import soit géré par le backend. 
Le frontend ne connais pas dur les valeurs possibles elles sont renvoyés par un nouveau endpoint dédié du backend GET /api/users/import/filetypes
```json
{
    "file_types" : [
        {
            "key" : "ods",
            "label" : "Libre office"
        }
    ]
}
```