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
- identifiant utilisateur proposant l'image ;
- date de création.

Ajouter les clés étrangères vers `t_platform` et `t_user`.

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
- la contrainte unique sur l'image `MAIN`.

## Critères D'Acceptation

- La migration Alembic est créée.
- Le modèle ORM reflète le schéma cible.
- Les variables d'environnement sont validées.
- Les fichiers Docker exposent le volume attendu.
- Les tests backend ciblés passent.
