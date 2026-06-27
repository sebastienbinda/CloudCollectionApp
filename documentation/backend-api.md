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

Registered-user tokens keep the verified email in `sub` and expose the public
pseudonym in the signed `display_name` claim. The configured administrator uses
its configured username as both values.

Supported identities:

- configured technical account from `AUTH_USERNAME` and encrypted password,
  with profile `ADMIN`;
- registered database users using their verified email as username, with their
  database profile and only while their status is `ACTIVE`.

Users with status `WAITING_VALIDATION` receive `401` with a clear message
indicating that administrator validation is still required.

### Exchange Collection Share Token

```http
POST /api/auth/collection-share/session
Content-Type: application/json
```

Request:

```json
{
  "token": "<signed-share-link-token>"
}
```

This route is public because the caller owns only the temporary token embedded
in `/collection/share/<token>`. A valid active share returns a Bearer session:

```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

The GUEST session expires no later than the persisted share and contains the
share identifier, owner identity and granted permissions. Invalid signatures
return `401`. Expired or revoked shares and deleted or locked owners return
`411` with `error_code: COLLECTION_SHARE_UNAVAILABLE`.

Decoded GUEST claims have this functional shape:

```json
{
  "sub": "guest-share:42",
  "display_name": "Player_One",
  "profile": "GUEST",
  "collection_share_id": 42,
  "owner_user_id": 7,
  "owner_pseudonym": "Player_One",
  "permissions": {
    "collection": true,
    "wishlist": false,
    "prices": true
  },
  "iat": 1782288000,
  "exp": 1782374400
}
```

Exchange status contract:

- `200`: GUEST Bearer issued;
- `401`: missing, malformed, incorrectly signed or wrong-kind link token;
- `411`: expired/revoked share or deleted/locked owner, with
  `error_code: COLLECTION_SHARE_UNAVAILABLE`;
- `503`: database or sharing service unavailable;
- `500`: unexpected exchange failure.

### Register User

```http
POST /api/auth/register
Content-Type: application/json
```

Request:

```json
{
  "email": "user@example.com",
  "pseudonym": "Player_One",
  "password": "VeryStrongPassword123!"
}
```

This route is public because the user does not yet own a Bearer token. The
password is stored as a non-reversible hash. The created user remains unusable
until email verification succeeds. When `ADMIN_ACCOUNT_VALIDATION_ENABLED=true`,
the account also remains unusable until an administrator validates it.
The pseudonym must contain 3 to 32 letters, digits, `_` or `-`. Its uniqueness
is case-insensitive. A duplicate email or pseudonym returns `409`.

### Check Pseudonym Availability

```http
GET /api/auth/pseudonym-availability?pseudonym=Player_One
```

Response:

```json
{
  "pseudonym": "Player_One",
  "available": true
}
```

This route is public and applies the same format rules as registration. An
invalid format returns `400`. Availability does not replace the authoritative
unique constraint checked again during registration.

### Verify Email

Browser link:

```http
GET /api/auth/verify-email?token=<token>
```

The browser flow validates the token and returns a redirect to the public
frontend page `/auth/verify-email?status=<result>`.

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

This route is protected and explicitly accepts `GUEST`, `USER` and `ADMIN`.

## Collection Share Management

These routes require a Bearer profile with at least `USER`. The share owner is
resolved from the token subject; no owner identifier is accepted from the
client.

### Create Share

```http
POST /api/collection-shares
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "recipient": "Alice",
  "duration_hours": 24,
  "allow_collection": true,
  "allow_wishlist": false,
  "allow_prices": true
}
```

`recipient` is optional. When present, it must be a string of at most 256
characters after trimming; blank values are stored and returned as `null`.
It is used only for owner display and backend access logs, not for
authorization. `duration_hours` must be an integer from 1 to 240. All
permissions must be JSON booleans, and at least collection or wishlist access
must be enabled. Success returns `201` with a `share` containing recipient,
dates, permissions, `ACTIVE` status and an absolute `/collection/share/<token>`
frontend link.

Creation returns `400` for invalid duration/permissions, `404` when the Bearer
subject no longer resolves to an owner, `503` when PostgreSQL is unavailable,
and `500` for an unexpected failure. Missing authentication or insufficient
profile follows the common `403` contract.

### List Shares

```http
GET /api/collection-shares
Authorization: Bearer <access_token>
```

Returns `shares` owned by the connected user, including active, expired and
revoked entries. Each entry contains `id`, `created_at`, `expires_at`, nullable
`revoked_at`, nullable `recipient`, `permissions`, `status` and a reconstructed
signed `link`. Raw tokens are not stored in PostgreSQL.

The list uses `200`, `404` for an unresolved owner, `503` for unavailable
PostgreSQL and `500` for an unexpected failure.

### Revoke Share

```http
DELETE /api/collection-shares/<share_id>
Authorization: Bearer <access_token>
```

Revocation is idempotent for an existing owned share and returns the share with
status `REVOKED`. An unknown share or a share owned by another user returns
`404` without exposing its owner.

Invalid identifiers return `400`; unavailable PostgreSQL returns `503`; an
unexpected failure returns `500`.

## Public Library Routes

The routes in this section are public and read-only. They expose only global
reference data from platforms, studios and games. They must not expose connected
user data, imported collection file paths or `t_user_collection` associations.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/library/entities` | Counts global reference platforms, studios and games. |
| `GET` | `/api/library/platforms` | Lists global reference platforms. |
| `GET` | `/api/library/platforms/<platform_id>` | Returns one global reference platform with aliases. |
| `GET` | `/api/library/platforms/<platform_id>/image/<image_id>` | Returns one accepted platform image file. |
| `GET` | `/api/library/studios` | Lists global reference studios. |
| `GET` | `/api/library/games` | Lists global reference games. |
| `GET` | `/api/library/games/<game_id>` | Returns one global reference game. |

List endpoints support these query parameters:

- `name`: optional name filter, matched without case or accent sensitivity;
- `platform`: optional filter for `/api/library/games`, matched exactly after
  removing case, accents and spaces;
- `page`: zero-based page index, default `0`;
- `size`: page size, default `500`, maximum `500`;
- `sort`: repeatable `column,direction` rule, where direction is `asc` or
  `desc`.

Allowed sort columns:

| Route | Columns |
| --- | --- |
| `/api/library/platforms` | `name`, `release_date`, `end_date`, `manufacturer` |
| `/api/library/studios` | `name`, `country`, `creation_date` |
| `/api/library/games` | `name`, `release_date`, `developer`, `platform` |

Invalid page, size or sort values fall back to the default page, default size or
`name,asc` sort.

### Library Entity Counts Response

```json
{
  "platforms": 12,
  "studios": 34,
  "games": 56
}
```

### Library Platform List Response

```json
{
  "platforms": [
    {
      "id": 1,
      "name": "Switch",
      "release_date": "2017-03-03",
      "end_date": null,
      "manufacturer": "Nintendo",
      "description": {},
      "total_games": 42
    }
  ],
  "page": {
    "page": 0,
    "size": 500,
    "totalElements": 1,
    "totalPages": 1
  }
}
```

### Library Studio List Response

```json
{
  "studios": [
    {
      "id": 1,
      "name": "Nintendo",
      "country": "Japon",
      "city": "Kyoto",
      "creation_date": "1889-09-23",
      "status": "",
      "editor_total_games": 12,
      "developer_total_games": 34
    }
  ],
  "page": {
    "page": 0,
    "size": 500,
    "totalElements": 1,
    "totalPages": 1
  }
}
```

### Library Platform Detail Response

```json
{
  "platform": {
    "id": 1,
    "name": "Super NES",
    "release_date": "1990-11-21",
    "end_date": "2003-09-25",
    "manufacturer": "Nintendo",
    "description": {},
    "total_games": 42,
    "aliases": [
      {
        "name": "Super Famicom",
        "category": "regional",
        "usage_region": "Japon",
        "comment": "Nom japonais"
      }
    ],
    "images": [
      {
        "id": 12,
        "platform_id": 1,
        "type": "MAIN",
        "status": "ACCEPTED",
        "user_id": 4
      }
    ]
  }
}
```

The `images` array contains only accepted images. Public platform detail pages
build image URLs with
`/api/library/platforms/<platform_id>/image/<image_id>` and may add a
cache-busting query parameter.

### Library Platform Image File

```http
GET /api/library/platforms/<platform_id>/image/<image_id>
```

This route is public but only serves images whose persisted status is
`ACCEPTED`. It returns the raw image file with its detected MIME type and
`Cache-Control` disabled by `max_age=0`.

Image file errors use:

- `404` when the platform image is unknown, not accepted, missing on disk or
  unreadable.

### Library Game List Response

```json
{
  "games": [
    {
      "id": 1,
      "name": "The Legend of Zelda",
      "release_date": "1986-02-21",
      "developer": "Nintendo",
      "editor": "Nintendo",
      "status": "",
      "platform": "NES"
    }
  ],
  "page": {
    "page": 0,
    "size": 500,
    "totalElements": 1,
    "totalPages": 1
  }
}
```

### Library Game Detail Response

```json
{
  "game": {
    "id": 1,
    "name": "The Legend of Zelda",
    "release_date": "1986-02-21",
    "developer": "Nintendo",
    "editor": "Nintendo",
    "status": "",
    "platform": "NES"
  }
}
```

Library errors use:

- `503` when database configuration is missing or invalid;
- `500` when a read fails unexpectedly.

## Protected Library Image Routes

The upload route requires a Bearer token with at least profile `USER`. The
connected user is derived from the token subject; the client must not send a
user id.

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/api/library/platforms/<platform_id>/image` | Uploads a proposed image for one platform. |

### Upload Platform Image

```http
POST /api/library/platforms/<platform_id>/image
Authorization: Bearer <user-token>
Content-Type: multipart/form-data
```

The multipart field name is `image`. Accepted MIME types are JPEG, PNG, WebP
and GIF. The backend stores the file under `BACKEND_IMG_DIR`, creates a
`t_platform_image` row with `type = OTHER`, `status = WAITING_VALIDATION` and
`user_id` resolved from the Bearer token subject, then notifies
`ADMIN_NOTIFICATION_EMAIL` when configured.

Successful response:

```json
{
  "image": {
    "id": 12,
    "platform_id": 1,
    "type": "OTHER",
    "status": "WAITING_VALIDATION",
    "user_id": 4
  }
}
```

with status `201`.

Access and error status:

- `403` when the Bearer token is missing or the token subject cannot be mapped
  to a known user;
- `404` when the platform is unknown;
- `422` when the multipart field is missing, the extension or MIME type is not
  allowed, or the file exceeds `PLATFORM_IMAGE_MAX_UPLOAD_BYTES`.

## Protected Library Administration Routes

The routes in this section require a Bearer token with profile `ADMIN`. They
are separate from the public read-only Library consultation endpoints.

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/api/library/reset` | Starts an asynchronous reset and rebuild of the global Library. |
| `POST` | `/api/library/platform-catalog/sync` | Adds missing platforms and aliases from backend CSV resources. |
| `GET` | `/api/library/platforms/images` | Lists platform images for moderation. |
| `PUT` | `/api/library/platforms/<platform_id>/image/<image_id>/status/<status>` | Accepts or refuses one platform image. |
| `PUT` | `/api/library/platforms/<platform_id>/image/<image_id>/type/<image_type>` | Changes one platform image type. |

### Reset Library

```http
POST /api/library/reset
Authorization: Bearer <admin-token>
```

The route starts an asynchronous job and returns immediately. It deletes and
rebuilds the global `t_platform`, `t_studio`, `t_game` and `t_user_collection`
data from stored user collection files and their saved import configurations.
Users are processed in registration order. Each user import reuses the backend
collection import service core.

Successful response:

```json
{
  "job_id": 25
}
```

with status `202`.

If a reset is already running, the backend returns status `409`:

```json
{
  "error": "Un reset de la Bibliotheque est deja en cours."
}
```

Access and error status:

- `403` when the Bearer token is missing or does not carry profile `ADMIN`;
- `409` when another reset job is already running;
- `500` only for unexpected launch failures before the asynchronous job starts.

The reset job has no status endpoint. Its final result is sent by email to
`ADMIN_NOTIFICATION_EMAIL` when configured. If one user file is missing,
unreadable, has no saved import configuration or fails during import, the job
logs the user error, records it in the in-memory reset context and continues
with the next user. In that case, the Library can be rebuilt partially from the
successful user imports. If the initial database clean fails, the reset stops
and the clean transaction is rolled back.

### Sync Platform Catalog

```http
POST /api/library/platform-catalog/sync
Authorization: Bearer <admin-token>
```

The route compares the SQL platform and alias catalog with
`backend/resources/platform_catalog.csv` and
`backend/resources/platform_alias_catalog.csv`. It inserts only missing
platforms and aliases. Existing rows are preserved.

Successful response:

```json
{
  "inserted_platforms": 1,
  "inserted_aliases": 2,
  "total_inserted": 3
}
```

with status `200`.

Access and error status:

- `403` when the Bearer token is missing or does not carry profile `ADMIN`;
- `500` when the CSV read or SQL update fails unexpectedly.

### List Platform Images For Moderation

```http
GET /api/library/platforms/images
Authorization: Bearer <admin-token>
```

Supported query parameters:

- `status`: optional status filter. `waiting_validation` and `accepted` aliases
  are normalized to `WAITING_VALIDATION` and `ACCEPTED`;
- `platform`: optional platform name filter;
- `page`: zero-based page index, default `0`;
- `size`: page size, default `500`, maximum `500`;
- `sort`: repeatable `column,direction` rule.

Allowed sort columns are `creation_date`, `platform`, `status` and `type`.
Invalid values fall back to `creation_date,desc`.

Response:

```json
{
  "images": [
    {
      "id": 12,
      "platform_id": 1,
      "type": "OTHER",
      "status": "WAITING_VALIDATION",
      "user_id": 4,
      "platform_name": "Super NES",
      "user_email": "user@example.com",
      "creation_date": "2026-06-19T10:30:00",
      "image_url": "/api/library/platforms/1/image/12"
    }
  ],
  "page": {
    "page": 0,
    "size": 500,
    "totalElements": 1,
    "totalPages": 1
  }
}
```

### Moderate Platform Image Status

```http
PUT /api/library/platforms/<platform_id>/image/<image_id>/status/<status>
Authorization: Bearer <admin-token>
```

Accepted status values are `accepted` and `refused`. `accepted` persists
`status = ACCEPTED`. `refused` deletes the database row and removes the stored
file from disk.

Successful response status is `200`. For refused images, the response includes
`deleted: true` with the deleted image payload.

Access and error status:

- `403` when the Bearer token is missing or does not carry profile `ADMIN`;
- `404` when the platform, image or status is unknown or invalid.

### Moderate Platform Image Type

```http
PUT /api/library/platforms/<platform_id>/image/<image_id>/type/<image_type>
Authorization: Bearer <admin-token>
```

Accepted type values are `MAIN` and `OTHER`. Setting one image to `MAIN`
automatically switches previous `MAIN` images for the same platform back to
`OTHER`.

Successful response status is `200` with the updated `image` payload.

Access and error status:

- `403` when the Bearer token is missing or does not carry profile `ADMIN`;
- `404` when the platform, image or type is unknown or invalid.

## Game Collection Routes

The four read routes in this section explicitly accept `GUEST`, `USER` and
`ADMIN`. For USER/ADMIN, the collection owner is resolved from the Bearer
subject. For GUEST, it is resolved from the validated `owner_user_id` claim and
the persisted share is revalidated before each request. Download and mutation
routes require at least `USER`; GUEST receives `403`.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/collections/videogames` | Returns connected-user collection statistics from SQL. |
| `GET` | `/collections/videogames/platforms/search` | Lists platforms owned by the connected user from SQL. |
| `GET` | `/collections/videogames/games/search` | Lists connected-user games from SQL. |
| `GET` | `/collections/videogames/games/<game_id>` | Returns one game only when attached to the connected user. |
| `GET` | `/collections/videogames/download` | Downloads the connected user's imported ODS file as raw bytes. |
| `POST` | `/collections/videogames/games` | Reserved for a future add action and returns `501`. |
| `PUT` | `/collections/videogames/games` | Reserved for a future update action and returns `501`. |
| `DELETE` | `/collections/videogames/games` | Reserved for a future delete action and returns `501`. |

The connected user is derived from the Bearer token. These routes never accept a
user identifier in the URL, query string or payload.

For GUEST reads:

- `permissions.collection` controls requests scoped with `wishlist=false`;
- `permissions.wishlist` controls requests scoped with `wishlist=true`;
- an explicitly forbidden category returns `403`;
- when `wishlist` is omitted and only one category is allowed, backend forces
  that category; when both are allowed, the unscoped request may include both;
- a detail request returns `403` when its game belongs to a forbidden category;
- without `permissions.prices`, game responses omit `purchase_price` and
  `price_unit`, while `total_value` and `average_value` are zero in root,
  category and platform statistics;
- an invalidated GUEST session returns `411` with
  `error_code: COLLECTION_SHARE_UNAVAILABLE`.

### Collection Statistics Response

```json
{
  "total": 420,
  "total_value": 12550.75,
  "average_value": 34.86,
  "max_platform": "Switch",
  "collection": {
    "total": 420,
    "total_value": 12550.75,
    "average_value": 34.86,
    "max_platform": "Switch"
  },
  "wishlist": {
    "total": 12,
    "total_value": 359.88,
    "average_value": 29.99,
    "max_platform": "NES"
  }
}
```

The root fields are kept for compatibility and mirror the `collection` section.
Collection statistics are computed with `t_user_collection.wishlist = false`;
wishlist statistics are computed with `wishlist = true`.
`total_value` sums persisted purchase prices. `average_value` ignores null
purchase prices and is rounded to two decimal places. Both values are zero when
no purchase price is available.

When the connected user has no game in `t_user_collection`, both sections are
empty:

```json
{
  "total": 0,
  "total_value": 0,
  "average_value": 0,
  "max_platform": "",
  "collection": {
    "total": 0,
    "total_value": 0,
    "average_value": 0,
    "max_platform": ""
  },
  "wishlist": {
    "total": 0,
    "total_value": 0,
    "average_value": 0,
    "max_platform": ""
  }
}
```

### Collection Platform Search

Supported query parameters:

- `name`: optional platform name filter, matched without case or accent
  sensitivity;
- `wishlist`: optional boolean filter. Only `true` and `false` are accepted.
  Invalid values return `400`;
- `page`: zero-based page index, default `0`;
- `size`: page size, default `500`, maximum `500`;
- `sort`: repeatable `column,direction` rule. Allowed column: `name`.
  Unsupported columns or directions return `400`.

Unsupported query parameters return `400` with a JSON `error` message listing
the accepted parameters.

Response:

```json
{
  "page": {
    "totalElements": 1,
    "page": 0,
    "size": 500,
    "totalPages": 1
  },
  "platforms": [
    {
      "id": 1,
      "name": "Switch",
      "nb_games": 25,
      "total_value": 749.75,
      "average_value": 34.08
    }
  ]
}
```

Platform `total_value` and `average_value` use the same null-price and rounding
rules as global collection statistics and apply to the platform's filtered
collection entries.

Empty response:

```json
{
  "page": {
    "totalElements": 0,
    "page": 0,
    "size": 500,
    "totalPages": 0
  },
  "platforms": []
}
```

### Collection Game Search

Supported query parameters:

- `name`: optional game name filter, matched without case or accent
  sensitivity;
- `studio_name`: optional studio name filter, matched without case or accent
  sensitivity;
- `platform_name`: optional platform name filter, matched without case or
  accent sensitivity;
- `platform_id`: optional exact platform id. Invalid values return `400`;
- `release_date`: optional range formatted as `YYYY-MM-DD..YYYY-MM-DD`;
- `wishlist`: optional boolean filter. Only `true` and `false` are accepted.
  Invalid values return `400`. The current collection page sends
  `wishlist=false`;
- `page`: zero-based page index, default `0`;
- `size`: page size, default `500`, maximum `500`;
- `sort`: repeatable `column,direction` rule.

Allowed sort columns:

- `name`;
- `platform_name`;
- `release_date`;
- `studio_name`;
- `buy_date`;
- `grade`.

Unsupported query parameters, unsupported sort columns, unsupported sort
directions and invalid criterion formats return `400` with a JSON `error`
message.

Response:

```json
{
  "page": {
    "totalElements": 1,
    "page": 0,
    "size": 500,
    "totalPages": 1
  },
  "games": [
    {
      "id": 1,
      "name": "The Legend of Zelda",
      "platform_name": "NES",
      "platform_id": 1,
      "release_date": "1986-02-21",
      "studio_name": "Nintendo",
      "studio_id": 10,
      "version": "EU-FR",
      "purchase_price": 59.99,
      "price_unit": "EUR",
      "buy_date": "2026-06-01",
      "buy_location": "Paris",
      "grade": "Rare",
      "condition": 3,
      "has_manual": true,
      "is_collector": false,
      "has_steelbook": true,
      "is_digital": false,
      "region": "EU-FR",
      "description": "Edition complete",
      "wishlist": false
    }
  ]
}
```

Empty response:

```json
{
  "page": {
    "totalElements": 0,
    "page": 0,
    "size": 500,
    "totalPages": 0
  },
  "games": []
}
```

### Collection Game Detail Response

`GET /collections/videogames/games/<game_id>` returns `404` when the game is not
attached to the connected user's `t_user_collection` rows.

```json
{
  "game": {
    "id": 1,
    "name": "The Legend of Zelda",
    "platform_name": "NES",
    "platform_id": 1,
    "release_date": "1986-02-21",
    "studio_name": "Nintendo",
    "studio_id": 10,
    "version": "EU-FR",
    "purchase_price": 59.99,
    "price_unit": "EUR",
    "buy_date": "2026-06-01",
    "buy_location": "Paris",
    "grade": "Rare",
    "condition": 3,
    "has_manual": true,
    "is_collector": false,
    "has_steelbook": true,
    "is_digital": false,
    "region": "EU-FR",
    "description": "Edition complete",
    "wishlist": false
  }
}
```

Private collection fields are nullable and hidden from the visual detail when
their value is null. `purchase_price` is a non-negative decimal number stored
with two fractional digits; additional imported digits are truncated toward the
lower value. `price_unit` carries its
ISO unit and the API performs no conversion. Condition values map from `0`
(`Mauvais`) through `4` (`Neuf`).

### Collection ODS Download

`GET /collections/videogames/download` reads `t_user.collection_file_path` for
the connected user and sends that file without parsing the ODS content.

Download errors use:

- `404` when `collection_file_path` is empty;
- `404` when the file no longer exists on disk;
- `500` for unexpected download failures.

### Future Game Actions

`POST`, `PUT` and `DELETE /collections/videogames/games` are registered so the
route catalog can announce future actions, but they currently return:

```json
{
  "error": "Not implemented."
}
```

with HTTP status `501`.

## User Administration Routes

The routes in this section require profile `ADMIN`.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/users` | Searches users by email, dates and status. |
| `DELETE` | `/api/users/<id>` | Deletes a user. |
| `POST` | `/api/users/<id>/lock` | Locks a user with status `LOCKED`. |
| `POST` | `/api/users/<id>/unlock` | Unlocks a user with status `ACTIVE`. |
| `POST` | `/api/users/<id>/validate` | Validates a waiting user with status `ACTIVE` and sends an activation email whose sign-in link includes the user email as `email=<address>`. |

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
| `GET` | `/api/users/import/` | Returns the connected user's last saved import configuration. |
| `POST` | `/api/users/import/file/<file_type>` | Stores the connected user's temporary collection file. |
| `POST` | `/api/users/import/analyze/<file_type>` | Analyzes the temporary file and returns ODS sheet names or CSV column names. |
| `POST` | `/api/users/import` | Imports the connected user's collection from the temporary file and JSON configuration. |
| `POST` | `/api/users/collection/reinit` | Reinitializes the connected user's imported collection. |

When a Library reset job is running, the backend rejects the import workflow
routes that can read, write or reinitialize user import state:

- `GET /api/users/import/`;
- `POST /api/users/import/file/<file_type>`;
- `POST /api/users/import/analyze/<file_type>`;
- `POST /api/users/import`;
- `POST /api/users/collection/reinit`.

The response uses status `403`:

```json
{
  "error": "Un reset de la Bibliotheque est en cours. Veuillez réessayer plus tard."
}
```

Authentication and profile checks still run first. A missing or invalid Bearer
token keeps the existing authentication response.

### Current User Collection Status Response

The status is derived from `t_user.collection_file_path`. The response must not
return the stored filesystem path.

```json
{
  "has_collection": false
}
```

### Get Saved Import Configuration

```http
GET /api/users/import/
```

Successful response is the last JSON import configuration stored in
`t_user.collection_file_description`.

When no saved configuration exists, the backend returns:

```json
{
  "error": "Configuration d'import introuvable."
}
```

with status `404`.

### Upload User Collection File

```http
POST /api/users/import/file/libreoffice_ods
Content-Type: multipart/form-data
```

CSV uses the same route shape:

```http
POST /api/users/import/file/csv
Content-Type: multipart/form-data
```

Field:

- `collection_file`: ODS or CSV file to stage before configuration.

The backend stores the file as
`/users/workspace/<user_id>/current-import.<extension>`, overwriting any
previous temporary import file for the same user. The copied file is chmod
`0440`.

Upload errors use:

- `400` for a missing or invalid file;
- `413` when the uploaded file exceeds `USER_COLLECTION_MAX_UPLOAD_BYTES`;
- `500` for unexpected failures.

### Analyze User Collection File

```http
POST /api/users/import/analyze/libreoffice_ods
```

CSV uses:

```http
POST /api/users/import/analyze/csv
```

Successful response:

```json
{
  "sheets": ["Sheet1", "Sheet2"]
}
```

For CSV, the same `sheets` field contains detected CSV column names in file
order:

```json
{
  "sheets": ["Jeu", "Console", "Studio"]
}
```

Analyze errors use:

- `404` when the temporary file does not exist;
- `422` when the temporary file does not match the requested `file_type`;
- `500` for unexpected failures.

### Import User Collection Payload

```http
POST /api/users/import
Content-Type: application/json
```

Body:

- UTF-8 JSON import configuration.

The JSON configuration supports:

- a mandatory top-level `wishlist` section;
- an optional top-level `price_unit` selected globally for the file; it becomes
  mandatory when any layout maps `purchase_price` and accepts `EUR`, `USD`,
  `GBP`, `JPY`, `AUD`, `CAD`, `CHF`, `CNY` or `KRW`;
- `single_sheet_conf` for a single imported sheet;
- `multiple_sheets_conf.shared_layout.included_sheets` to import only selected
  sheets;
- `multiple_sheets_conf.shared_layout.excluded_sheets` to import every sheet
  except selected sheets;
- `multiple_sheets_conf.sheets` for per-sheet layouts;
- `mapping` for CSV, where each import field maps directly to a CSV header
  name.

Example CSV payload:

```json
{
  "file_type": "csv",
  "price_unit": "EUR",
  "wishlist": {"mode": "column"},
  "mapping": {
    "name": "Jeu",
    "platform": "Console",
    "studio": "Studio",
    "release_date": "Sortie",
    "purchase_price": "Prix",
    "wishlist": "Souhait"
  }
}
```

Every collection layout may map the nullable private fields `purchase_price`,
`buy_location`, `buy_date`, `grade`, `condition`, `has_manual`, `is_collector`,
`has_steelbook`, `is_digital`, `region` and `description`. Invalid non-empty
values are ignored and reported in `warnings.invalid_games` without rejecting
the complete import.
Region values are fuzzy-matched against the controlled codes. The unique best
match must reach `REGION_MATCH_LIMIT` (default `60`); otherwise the imported
region is stored as null and reported as invalid.
Condition values must be strings and are fuzzy-matched against the French state
labels and supported English aliases. The unique best match must reach
`ETAT_MATCH_LIMIT` (default `60`); otherwise `condition` is null and the warning
is returned without rejecting the game.
The four nullable boolean fields accept native booleans and normalized
French/English values (`oui/non`, `yes/no`, `true/false`, `1/0`, `x`, `✓`,
`present/absent`, `avec/sans`). Spaces are ignored and a unique fuzzy match with
a score of at least `75` is accepted. Ambiguous or unknown non-empty values are
returned through `warnings.invalid_games` and stored as null without rejecting
the game.

`included_sheets` and `excluded_sheets` are exclusive. CSV does not accept
`single_sheet_conf`, `multiple_sheets_conf`, ODS sheet settings or
`wishlist.mode = "sheet"`. Invalid JSON or configuration returns `422` with
`error` and `details`.

Wishlist modes:

- `{"mode": "none"}`: no wishlist source, all imported rows are collection
  rows;
- `{"mode": "sheet", ...}`: a dedicated sheet supplies wishlist rows and must
  include `sheet_name`, `data_range`, `header_row` and `column_information`;
- `{"mode": "column"}`: every collection layout must define
  `column_information.wishlist`, or CSV must define `mapping.wishlist`.

Accepted wishlist column values are `Oui/Non`, `O/N`, `True/False`,
`Yes/No` and `Y/N`, case-insensitively. Empty values are imported as
`wishlist=false`. Invalid non-empty values make the row ignored and are
reported in import warnings.

The upload can be repeated for a user who already has a collection. The
temporary file is overwritten and the final import adds missing games to the
existing collection without clearing current associations.

The backend copies the staged temporary file to
`/users/workspace/<user_id>/<user_id>-collection.<extension>`, stores this
complete path in `t_user.collection_file_path` only after a successful import,
and removes the final copied file if the import fails. On additive import, the
stored collection file and saved import configuration are replaced only after
persistence succeeds. The copied file is chmod `0440`.

Only configured ODS sheets are imported. With a shared layout, the user may
either provide the sheets to import or the sheets to exclude; without either
list, every sheet is imported. CSV imports one tabular file using its configured
header mapping. Platforms are matched against the application reference catalog
and are not created by this endpoint. Missing studios and games are created;
existing records are reused. User-game associations are inserted in
`t_user_collection` when missing with their `wishlist` value and ignored when
already present. No existing platform, studio, game or user association is
updated by this endpoint.

Successful response:

```json
{
  "linked_platforms": 3,
  "created_studios": 12,
  "created_games": 42,
  "associated_games": 58,
  "wishlisted_games": 12,
  "warnings": {
    "invalid_wishlist": 3,
    "invalid_wishlist_values_found": ["Ok", "Peut etre", "Nop"],
    "invalid_games": [],
    "platform_mappings": [
      {
        "imported_platform": "Super Nintendo",
        "matched_platform": "Super Nintendo Entertainment System / Super Famicom",
        "score": 100,
        "games_count": 3,
        "matched_by_alias": true,
        "matched_alias": "Super Nintendo",
        "accepted": true,
        "manual_check": false,
        "reason": ""
      }
    ],
    "platform_matches": [],
    "skipped_games": [],
    "total_import_duration_seconds": 2.431
  }
}
```

The `associated_games` counter is the number of games attached to the user after
the import payload is processed, including games that already existed before the
request. `wishlisted_games` counts imported games whose final retained import
value is `wishlist=true`. `linked_platforms` counts distinct reference catalog
platforms used by the imported games.
`warnings.platform_mappings` lists every platform name read from the imported
file, the reference platform retained by matching, the matching score, the
number of imported games using that source platform name, and whether a platform
alias produced the retained match.
`warnings.platform_matches` lists games imported with a platform score greater
than or equal to `PLATFORM_MATCHING_LOW_LVL_RATING` and lower than
`PLATFORM_MATCHING_HIGH_LEVEL_RATING`; they are imported but require manual
administrator verification. `warnings.skipped_games` lists games ignored
because the platform score is lower than `PLATFORM_MATCHING_LOW_LVL_RATING`.
`warnings.total_import_duration_seconds` contains the total backend import
duration in seconds, measured around file validation, optional workspace copy,
file reading, matching and SQL persistence.

Import errors use:

- `400` for an invalid or unreadable collection file;
- `404` when the temporary file does not exist;
- `422` for invalid JSON configuration;
- `500` for an unexpected import failure.

### Reinitialize User Collection

```http
POST /api/users/collection/reinit
```

The connected user is derived exclusively from the validated Bearer token. The
route does not accept a user identifier in the URL, query string or request
body.

Successful response:

```json
{
  "reinitialized": true
}
```

On success, the backend removes the connected user's rows from
`t_user_collection` and clears `t_user.collection_file_path`. The saved
`t_user.collection_file_description` is kept so the next import can offer to
reuse the last validated configuration. If a collection file path was stored
and the file still exists on disk, the file is deleted. If the stored file is
already missing from disk, the reinitialization still succeeds after logging a
warning; the database cleanup remains authoritative.

Reinitialization errors use:

- `404` when the connected user has no collection to reinitialize;
- `500` for an unexpected reinitialization failure.

## Email Configuration

Registration sends verification emails. Useful variables:

```bash
BACKEND_PUBLIC_URL=https://api.example.com
FRONTEND_PUBLIC_URL=https://app.example.com
EMAIL_DELIVERY_MODE=smtp
ADMIN_NOTIFICATION_EMAIL=admin@example.com
ADMIN_ACCOUNT_VALIDATION_ENABLED=true
EMAIL_VERIFICATION_TOKEN_TTL_HOURS=24
SMTP_FROM_EMAIL=noreply@example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
SMTP_USE_TLS=true
```

`ADMIN_NOTIFICATION_EMAIL` receives a message after every successful user email
verification, even when administrator validation is disabled. The message links
to `/users?status=WAITING_VALIDATION` on `FRONTEND_PUBLIC_URL` so an
administrator can validate waiting accounts when required. The message includes
the user's email and the total number of users currently waiting for
administrator validation.

The same address receives the final report of each asynchronous Library reset
job, including the global status, successfully imported users and per-user
errors when the rebuild is partial.

The same address receives exactly one report after each user collection import
when the import reaches its final backend step. This report is sent outside the
file reader layer and does not depend on the imported file type. It is sent even
when the import has no warning and includes the user import context, counters,
validated import configuration, total duration, platform mappings and every
import warning.

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
