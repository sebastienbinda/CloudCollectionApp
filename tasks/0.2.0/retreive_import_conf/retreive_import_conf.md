Le but de la tache est de permettre a un utilisateur de récupérer la configuration de l'import sauvegardé en base de données pour l'appliquer automatiquement par défaut au prochain import apres l'envoie du fichier.

Un nouvel endpoint backend est créé pour cela : GET /api/users/import/ dans le controller user_collection_import_controller.
Ce controller renvoie la conf sauvegardé en base de donnée  avec le code 200 ou 404 si il n'y a pas de conf existante.
Si il n'y a pas de conf existante le formulaire reste pre remplie comme actuellement sinon les valeurs sont utilisées pour pré remplire le formulaire d'import a condition que l'utilisateur valide via une popup interractive qu'il veut réutiliser la conf sauvegardée précédement.

La tache doit aussi permettre que la page d'onboarding soit accessible depuis le menu "Configuration" désormais si l'utilisateur a deja une collection. Ceci afin de pouvoir importer un nouveau fichier pour ajouter sans reinitialiser des jeux a sa collection.

Tests : 
- Ajout d'un test backend pour tester le nouvel endpoint en cas de 200 et en cas de 404

Documentation :
- Mise a jour des documentation : import.md, backend-api.md