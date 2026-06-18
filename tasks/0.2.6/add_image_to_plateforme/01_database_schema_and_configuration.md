# 01 - Schéma SQL, configuration et volume Docker

## Objectif

Ajouter l'infrastructure persistante nécessaire aux images de plateformes :
schéma SQL, modèle ORM, configuration backend et volume Docker.

Cette tâche dépend de :

- `00_existing_code_analysis_result.md`
- `documentation/database.md`
- `documentation/backend-arch.md`

## Backend À Modifier

Selon les noms confirmés dans le rapport d'analyse :

- modèle ORM `PlatformImage` ;
- exports du package database ;
- migration Alembic ;
- configuration backend dédiée aux images de plateformes ;
- éventuels tests de configuration et de schéma.

## Schéma Attendu

Créer la table `t_platform_image` avec :

- `id` ;
- identifiant de plateforme ;
- chemin absolu de l'image ;
- type d'image `MAIN` ou `OTHER` ;
- statut `WAITING_VALIDATION` ou `ACCEPTED` ;
- colonne `user_id` contenant l'identifiant de l'utilisateur proposant l'image ;
- date de création.

Ajouter les clés étrangères vers `t_platform` et `t_user`.

`user_id` est obligatoire. Il doit être alimenté par le backend depuis le token
de l'utilisateur connecté au moment de l'upload, et non depuis une valeur fournie
par le frontend.

Ajouter une contrainte d'unicité permettant une seule image `MAIN` par
plateforme, sans empêcher plusieurs images `OTHER`.

## Configuration Attendue

Ajouter la lecture et la validation de :

- `BACKEND_IMG_DIR` ;
- `PLATFORM_IMAGE_MAX_UPLOAD_BYTES`.

La configuration doit créer le répertoire cible si nécessaire et respecter les
patterns existants de validation des variables d'environnement.

## Docker À Modifier

Mettre à jour les fichiers Docker Compose concernés pour monter le nouveau
volume d'images dans le conteneur backend.

## Tests Attendus

Ajouter ou modifier des tests backend couvrant :

- la validation des variables d'environnement ;
- la création du répertoire de stockage ;
- la structure SQL attendue ;
- la présence et la non-nullabilité de `user_id` ;
- la clé étrangère `user_id` vers `t_user.id` ;
- la contrainte unique sur l'image `MAIN`.

## Critères D'Acceptation

- La migration Alembic est créée.
- Le modèle ORM reflète le schéma cible.
- Les variables d'environnement sont validées.
- Les fichiers Docker exposent le volume attendu.
- Les tests backend ciblés passent.
