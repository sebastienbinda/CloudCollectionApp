# 03 - Endpoints backend de modération administrateur

## Objectif

Ajouter les endpoints backend permettant à un administrateur de lister,
d'accepter, de refuser et de typer les images proposées.

Cette tâche dépend de :

- `00_existing_code_analysis_result.md`
- `01_database_schema_and_configuration.md`
- `02_backend_user_upload_and_public_images.md`
- `documentation/backend-api.md`
- `documentation/authentication.md`
- `documentation/backend-arch.md`

## Endpoints À Ajouter

Lister les images :

```http
GET /api/library/platforms/images
```

Modifier le type :

```http
PUT /api/library/platforms/{platform_id}/image/{image_id}/type/{type}
```

Modifier le statut :

```http
PUT /api/library/platforms/{platform_id}/image/{image_id}/status/{status}
```

## Règles Métier

- Ces endpoints nécessitent un profil `ADMIN`.
- La liste est paginée avec les mêmes paramètres et le même format de réponse
  que les endpoints de liste existants.
- La liste supporte les filtres `status` et `platform`.
- La liste retourne au minimum :
  - identifiant image ;
  - nom de plateforme ;
  - statut ;
  - type ;
  - identifiant ou nom de l'utilisateur proposant l'image ;
  - date de création ;
  - informations nécessaires pour reconstruire l'URL image.
- Le passage en `MAIN` bascule les autres images de la plateforme en `OTHER`.
- Le statut `accepted` met l'image en `ACCEPTED`.
- Le statut `refused` supprime le fichier disque et l'entrée SQL.
- `refused` n'est pas un statut stocké en base.

## Réponses HTTP

- `200` en cas de succès, y compris pour un refus supprimant l'image ;
- `403` si l'utilisateur n'est pas connecté ou n'est pas `ADMIN` ;
- `404` si la plateforme ou l'image est inconnue.

## Tests Attendus

Ajouter ou modifier des tests backend couvrant :

- accès refusé sans token ;
- accès refusé avec profil `USER` ;
- liste acceptée avec profil `ADMIN` ;
- pagination et filtres ;
- acceptation d'image ;
- refus avec suppression disque et SQL ;
- définition d'une image `MAIN` ;
- bascule automatique des anciennes images `MAIN` en `OTHER` ;
- métadonnées `/api/routes` conformes.

## Critères D'Acceptation

- Les endpoints sont protégés par profil `ADMIN`.
- Les règles de modération sont transactionnelles.
- Les tests backend ciblés passent.
