# 02 - Upload utilisateur et accès public aux images acceptées

## Objectif

Implémenter le dépôt d'image par un utilisateur connecté et l'accès public aux
images acceptées.

Cette tâche dépend de :

- `00_existing_code_analysis_result.md`
- `01_database_schema_and_configuration.md`
- `documentation/backend-api.md`
- `documentation/authentication.md`
- `documentation/backend-arch.md`

## Endpoints À Ajouter Ou Modifier

Ajouter :

```http
POST /api/library/platforms/{id}/image
```

Le champ multipart attendu est `image`.

Ajouter :

```http
GET /api/library/platforms/{id}/image/{image_id}
```

Modifier :

```http
GET /api/library/platforms/{id}
```

pour retourner les images `ACCEPTED` associées à la plateforme.

## Règles Métier

- L'upload nécessite un utilisateur connecté.
- La page et les images acceptées restent publiques.
- Le fichier doit respecter la taille maximale configurée.
- Les formats acceptés sont `jpg`, `jpeg`, `png`, `webp` et `gif`.
- Le MIME et l'extension doivent être validés.
- L'image est copiée dans `/images/platforms/{slug nom}`.
- Le nom original est conservé ; en cas de collision, ajouter un compteur en
  suffixe.
- L'entrée créée a le type `OTHER` et le statut `WAITING_VALIDATION`.
- L'entrée créée renseigne `user_id` avec l'identifiant de l'utilisateur connecté
  à l'origine de l'upload.
- Le backend dérive `user_id` du token validé ; le frontend ne doit pas envoyer
  cet identifiant.
- Le chemin stocké en base est absolu.
- Un email administrateur est envoyé après création.
- Si l'email administrateur n'est pas configuré, un warning est loggé.

## Réponses HTTP

Pour l'upload :

- `201` si l'image est créée ;
- `403` si aucun utilisateur n'est connecté ;
- `404` si la plateforme est inconnue ;
- `422` si l'image est trop volumineuse ou invalide.

Pour l'accès public :

- `200` avec le corps de l'image si elle existe, est lisible et `ACCEPTED` ;
- `404` si l'image est absente, inaccessible ou non acceptée.

## Tests Attendus

Ajouter ou modifier des tests backend couvrant :

- refus sans token ;
- refus d'une plateforme inconnue ;
- refus d'une image trop volumineuse ;
- refus d'une extension ou d'un MIME invalide ;
- copie disque et insertion SQL ;
- insertion SQL avec `user_id` issu du token ;
- collision de nom de fichier ;
- notification email ou warning ;
- lecture publique d'une image `ACCEPTED` ;
- refus public d'une image `WAITING_VALIDATION` ;
- enrichissement du détail plateforme avec les images acceptées.

## Critères D'Acceptation

- Les routes respectent le contrat HTTP.
- La logique métier est dans un service backend.
- Le contrôleur ne contient que le mapping HTTP.
- Les tests backend ciblés passent.
