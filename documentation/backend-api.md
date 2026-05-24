# Backend API

## Purpose

This document describes the backend HTTP API exposed by CloudCollectionApp.
Authentication and authorization details must remain aligned with
`documentation/authentication.md`.

## Authentication

All application endpoints are protected by Bearer token except the public
authentication and registration endpoints listed below.

Send the token on protected calls:

```http
Authorization: Bearer <access_token>
```

### Issue Token

```http
POST /auth/token
Content-Type: application/json
```

Request:

```json
{
  "username": "admin",
  "password": "change-me"
}
```

The endpoint also accepts `client_id` and `client_secret` for a client
credentials compatible payload.

Response:

```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

Supported identities:

- configured technical account from `AUTH_USERNAME` and encrypted password,
  with profile `ADMIN`;
- registered database users using their verified email as username, with their
  database profile and only while their status is not `LOCKED`.

### Register User

```http
POST /api/auth/register
Content-Type: application/json
```

Request:

```json
{
  "email": "user@example.com",
  "password": "VeryStrongPassword123!"
}
```

This route is public because the user does not yet own a Bearer token. The
password is stored as a non-reversible hash. The created user remains unusable
until email verification succeeds.

### Verify Email

Browser link:

```http
GET /api/auth/verify-email?token=<token>
```

API payload:

```http
POST /api/auth/verify-email
Content-Type: application/json
```

```json
{
  "token": "..."
}
```

The backend stores only a SHA-256 hash of the verification token.

## Route Catalog

```http
GET /api/routes
```

Returns the backend route catalog, including:

- path;
- endpoint name;
- HTTP methods;
- `requires_auth`;
- access mode;
- auth schemes;
- authorized profiles.

This route is protected.

## Game Collection Routes

All routes in this section require a Bearer token with at least profile `USER`.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/collections/JeuxVideo/platforms` | Lists ODS platform sheets. |
| `GET` | `/collections/JeuxVideo/home` | Returns dashboard statistics from `Accueil`. |
| `GET` | `/collections/JeuxVideo/search?platform=Switch&q=mario` | Lists or filters games for one platform. |
| `GET` | `/collections/JeuxVideo/game-search?q=mario` | Searches games by name across all platforms. |
| `GET` | `/collections/JeuxVideo/column-values?platform=Switch` | Lists distinct values by column for filtering. |
| `GET` | `/collections/JeuxVideo/add-game-choices?platform=Switch` | Returns merged choices for the add-game form. |
| `GET` | `/collections/JeuxVideo/platform-image/Switch` | Returns the embedded platform image. |
| `POST` | `/collections/JeuxVideo/games` | Adds a game to a platform sheet. |
| `PUT` | `/collections/JeuxVideo/games` | Updates a game in a platform sheet. |
| `DELETE` | `/collections/JeuxVideo/games` | Deletes a game from a platform sheet. |
| `POST` | `/collections/JeuxVideo/cache/reset` | Clears the backend ODS cache. |
| `GET` | `/collections/JeuxVideo/ods/download` | Downloads the ODS file. |

### Add Game Payload

```json
{
  "platform": "Switch",
  "Nom du jeu": "Metroid Prime",
  "Studio": "Nintendo",
  "Date de sortie": "2026-05-23",
  "Date d'achat": "2026-05-23",
  "Lieu d'achat": "Boutique",
  "Note": "Edition standard",
  "Prix d'achat": "49.99",
  "Version": "Physique"
}
```

### Update Game Payload

```json
{
  "platform": "Switch",
  "original": {
    "Nom du jeu": "Metroid Prime"
  },
  "updated": {
    "Nom du jeu": "Metroid Prime Remastered"
  }
}
```

### Delete Game Payload

```json
{
  "platform": "Switch",
  "Nom du jeu": "Metroid Prime"
}
```

## Wishlist Routes

All routes in this section require a Bearer token with at least profile `USER`.

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/collections/JeuxVideo/wishlist/games` | Adds a game to the wishlist. |
| `PUT` | `/collections/JeuxVideo/wishlist/games` | Updates a wishlist game. |
| `DELETE` | `/collections/JeuxVideo/wishlist/games` | Deletes a wishlist game. |

### Add Wishlist Game Payload

```json
{
  "Nom du jeu": "Chrono Trigger",
  "Console": "Switch 2",
  "Studio": "Square"
}
```

### Update Wishlist Game Payload

```json
{
  "original": {
    "Nom du jeu": "Chrono Trigger",
    "Console": "Switch 2"
  },
  "updated": {
    "Nom du jeu": "Chrono Trigger",
    "Console": "Switch 2",
    "Studio": "Square"
  }
}
```

### Delete Wishlist Game Payload

```json
{
  "Nom du jeu": "Chrono Trigger",
  "Console": "Switch 2"
}
```

## User Administration Routes

The routes in this section require profile `ADMIN`.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/users` | Searches users by email, dates and status. |
| `DELETE` | `/api/users/<id>` | Deletes a user. |
| `POST` | `/api/users/<id>/lock` | Locks a user with status `LOCKED`. |
| `POST` | `/api/users/<id>/unlock` | Unlocks a user with status `ACTIVE`. |

Supported search query parameters:

- `name`;
- `creation_date_from`;
- `creation_date_to`;
- `last_connexion_date_from`;
- `last_connexion_date_to`;
- `status`.

## User Collection Import Routes

The routes in this section require a Bearer token with at least profile `USER`.
They are self-service routes for the connected account and must not expose or
modify another user's collection.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/users/me/collection` | Returns whether the connected user already has an imported collection. |
| `POST` | `/api/users/import` | Imports the connected user's ODS collection from `multipart/form-data`. |

### Current User Collection Status Response

The status is derived from `t_user.collection_file_path`. The response must not
return the stored filesystem path.

```json
{
  "has_collection": false
}
```

### Import User Collection Payload

```http
POST /api/users/import
Content-Type: multipart/form-data
```

Field:

- `collection_file`: ODS file to import.

The upload is accepted only once per user. If `t_user.collection_file_path` is
already set, the backend returns `409` and does not replace the existing
collection data.

The backend copies the uploaded file to
`/users/workspace/<user_id>/<user_id>-collection.ods`, stores this complete path
in `t_user.collection_file_path` only after a successful import, and removes the
copied file if the import fails. The copied file is chmod `0440`.

Only ODS platform sheets are imported. Technical sheets such as `Accueil` and
`Liste de souhaits` are ignored by the import workflow. Missing platforms,
studios and games are created; existing records are reused. User-game
associations are inserted in `t_user_collection` when missing and ignored when
already present. No existing platform, studio, game or user association is
updated by this endpoint.

Successful response:

```json
{
  "created_platforms": 3,
  "created_studios": 12,
  "created_games": 42,
  "associated_games": 58
}
```

The `associated_games` counter is the number of games attached to the user after
the import payload is processed, including games that already existed before the
request.

Import errors use:

- `400` for a missing, invalid or unreadable ODS file;
- `409` when the connected user already has a collection;
- `413` when the multipart request exceeds `USER_COLLECTION_MAX_UPLOAD_BYTES`
  at the proxy or Flask layer, or when the uploaded file exceeds the same
  configured limit during import validation;
- `500` for an unexpected import failure.

## ODS Write Behavior

Before every write, the backend creates a backup in
`JEUXVIDEO_ODS_BACKUP_DIR`:

```text
collection.ods.backup-YYYYMMDDHHMMSSffffff
```

Writes update the ODS archive content while preserving existing spreadsheet
styles. After a write, the backend invalidates the ODS read cache.

## Email Configuration

Registration sends verification emails. Useful variables:

```bash
BACKEND_PUBLIC_URL=https://api.example.com
EMAIL_DELIVERY_MODE=smtp
EMAIL_VERIFICATION_TOKEN_TTL_HOURS=24
SMTP_FROM_EMAIL=noreply@example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
SMTP_USE_TLS=true
```

In local development, `EMAIL_DELIVERY_MODE=console` logs the generated email and
the Docker local stack can use Mailpit.

Test email delivery with:

```bash
./test_email.sh --to destinataire@example.com
```

For the production compose stack:

```bash
./test_email.sh -p --to destinataire@example.com
```
