Désormais l'import doit ce faire en deux étapes.

Première étape : choix du file type et envoie du fichier de collection seul sans les informations d'extraction.
Via le nouveaux endpoint /api/users/import/file/{file_type}
Accessible par profile USER
Ce endpoint ne fait plus que copier le fichier avec un nom temporaire dans le répertoire de l'utilisateur current-import.{extesion} avec les meme droits que actuellement et extension dépendant du file_type et récupérer grâce au service instancé en fonction du file_type selectionné. La méthode pour récupérer l'extension du fichier existe deja.

Si le fichier existe deja il est écrasé.
Réponse : 
- 201 si le fichier temporaire est copié.
- 400 fichier absent/invalide.
- 409 si l’utilisateur a déjà une collection finale.
- 413 si trop volumineux.

Ensuite dans une deuxième étapes, les informations de configuration de l'import sont demandées via un nouveau endpoint
POST /api/users/import/analyze/{file_type}
Accessible par profile USER
Ce endpoint n'a pas de paramètre mais lit le fichier en fonction du file_type donné en paramètre dans la route et retourne :
404 : Le fichier n'existe pas
422 : Le fichier ne correspond pas au type donné
200 : success
```json
{
    "sheets": [
        "sheet1", "sheet2"
    ]
}
```
Grâce a cette réponse, dans un troisième temps, le frontend prérempis les informations de saisie demandées actuellement :
 - Si un seul onglet : 
   - Multiple onglet : Non
- Si plusieurs onglets :
   - included_sheets : Propose une liste a choix multiple parmis les onglets retournés
   - excluded_sheets : Propose une liste a choix multiple parmis les onglets retorunés

Une fois les informations collectées l'import est lancé  avec le endpoint existant /api/users/import.

Ce endpoint est modifié ce n'est plus un multipart et seul la configuration au format json est envoyé en body POST.
Ce endpoint fait la même chose que avant, a l'exception  de la copie du fichier de colleciton car il n'est plus passé en paramètre. Au lieu de cela,
il copie le fichier temporaire vers le fichier de destination finale et ensuite fait le même travail.
Les cas d'erreur reste les mêmes avec en plus : 
 - 404 : Le fichier temporaire n'existe pas.


Attention cette tache doit conserver le coté agnostique du service d'import et déléguer au reader instancié en reader ods grâce au file_type toute action dépendante du type de fichier comme la récupération de la liste des onglets.

Tests : 
Service : Il faut rajouter dans le test UserCollectionImportServiceGenericReaderTest qui test la généricité du reader le test de ce nouveau mécanisme.
Controller : Test du endpoint modifié et test des nouveaux endpoints



