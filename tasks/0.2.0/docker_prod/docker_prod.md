L'objectif de la tache est de modifier le compose docker de production pour le rendre cohérent avec les nouvelles fonctionnalités à savoir le déploiement de la base de données.

Ce compose ne doit plus build les images web et backend mais tirer les images existantes et générées par la CI depuis github.
ghcr.io/sebastienbinda/cloudcollectionapp/backend:0.1.0
ghcr.io/sebastienbinda/cloudcollectionapp/frontend:0.1.0

La version des images est une variable d'env du fichier .env APP_VERSION. Par défaut si non précisé on utilise "latest".
