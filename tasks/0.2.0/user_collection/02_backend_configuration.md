# 02 - Configuration backend et Docker

## Objectif

Ajouter la configuration nécessaire au stockage des fichiers de collection utilisateur et au contrôle de taille d'upload.

## Étapes

1. Ajouter `USERS_WORKSPACE` uniquement dans la configuration Docker Compose pour choisir le répertoire hôte à monter.
2. Ajouter la configuration `USER_COLLECTION_MAX_UPLOAD_BYTES`.
3. Définir les valeurs par défaut si le projet utilise une configuration centralisée.
4. Mettre à jour la configuration Docker pour monter `${USERS_WORKSPACE}` dans `/users/workspace`.
5. Vérifier que le répertoire cible peut être créé par le runtime backend.
6. Mettre à jour la documentation concernée si les variables d'environnement ou Docker changent.

## Critères d'acceptation

- `USERS_WORKSPACE` sert uniquement au montage Docker du répertoire hôte.
- Le backend n'a pas besoin de lire `USERS_WORKSPACE`.
- Le backend peut lire la taille maximale d'upload depuis la configuration.
- Le montage Docker `/users/workspace` est documenté et configuré.
- Aucune valeur secrète n'est ajoutée.

## Validation attendue

- Lancer les tests backend existants.
- Vérifier si le README doit être mis à jour.
- Rebuilder les images Docker si la configuration runtime Docker est modifiée.
