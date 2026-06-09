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
  database profile and only while their status is `ACTIVE`.

Users with status `WAITING_VALIDATION` receive `401` with a clear message
indicating that administrator validation is still required.

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
until email verification succeeds and an administrator validates the account.

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

## Public Library Routes

The routes in this section are public and read-only. They expose only global
reference data from platforms, studios and games. They must not expose connected
user data, imported collection file paths or `t_user_collection` associations.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/library/entities` | Counts global reference platforms, studios and games. |
| `GET` | `/api/library/platforms` | Lists global reference platforms. |
| `GET` | `/api/library/studios` | Lists global reference studios. |
| `GET` | `/api/library/games` | Lists global reference games. |

List endpoints support these query parameters:

- `name`: optional name filter, matched without case or accent sensitivity;
- `page`: zero-based page index, default `0`;
- `size`: page size, default `500`, maximum `500`;
- `sort`: repeatable `column,direction` rule, where direction is `asc` or
  `desc`.

Allowed sort columns:

| Route | Columns |
| --- | --- |
| `/api/library/platforms` | `name`, `release_date`, `manufacturer` |
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
      "manufacturer": "Nintendo",
      "description": {},
      "status": "",
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

Library errors use:

- `503` when database configuration is missing or invalid;
- `500` when a read fails unexpectedly.

## Game Collection Routes

All routes in this section require a Bearer token with at least profile `USER`.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/collections/videogames` | Returns connected-user collection statistics from SQL. |
| `GET` | `/collections/videogames/platforms/search` | Lists platforms owned by the connected user from SQL. |
| `GET` | `/collections/videogames/games/search` | Lists connected-user games from SQL. |
| `GET` | `/collections/videogames/download` | Downloads the connected user's imported ODS file as raw bytes. |
| `POST` | `/collections/videogames/games` | Reserved for a future add action and returns `501`. |
| `PUT` | `/collections/videogames/games` | Reserved for a future update action and returns `501`. |
| `DELETE` | `/collections/videogames/games` | Reserved for a future delete action and returns `501`. |

The connected user is derived from the Bearer token. These routes never accept a
user identifier in the URL, query string or payload.

### Collection Statistics Response

```json
{
  "total": 420,
  "total_value": 0,
  "average_value": 0,
  "max_platform": "Switch",
  "collection": {
    "total": 420,
    "total_value": 0,
    "average_value": 0,
    "max_platform": "Switch"
  },
  "wishlist": {
    "total": 12,
    "total_value": 0,
    "average_value": 0,
    "max_platform": "NES"
  }
}
```

The root fields are kept for compatibility and mirror the `collection` section.
Collection statistics are computed with `t_user_collection.wishlist = false`;
wishlist statistics are computed with `wishlist = true`.

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
      "total_value": 0,
      "average_value": 0
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
      "version": "",
      "buy_date": "",
      "buy_location": "",
      "grade": "",
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
| `POST` | `/api/users/<id>/validate` | Validates a waiting user with status `ACTIVE` and sends an activation email. |

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
| `POST` | `/api/users/import/analyze/<file_type>` | Analyzes the temporary file and returns sheet names. |
| `POST` | `/api/users/import` | Imports the connected user's collection from the temporary file and JSON configuration. |
| `POST` | `/api/users/collection/reinit` | Reinitializes the connected user's imported collection. |

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

Field:

- `collection_file`: ODS file to stage before configuration.

The backend stores the file as
`/users/workspace/<user_id>/current-import.ods`, overwriting any previous
temporary import file for the same user. The copied file is chmod `0440`.

Upload errors use:

- `400` for a missing or invalid file;
- `409` when the connected user already has a final collection;
- `413` when the uploaded file exceeds `USER_COLLECTION_MAX_UPLOAD_BYTES`;
- `500` for unexpected failures.

### Analyze User Collection File

```http
POST /api/users/import/analyze/libreoffice_ods
```

Successful response:

```json
{
  "sheets": ["Sheet1", "Sheet2"]
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
- `single_sheet_conf` for a single imported sheet;
- `multiple_sheets_conf.shared_layout.included_sheets` to import only selected
  sheets;
- `multiple_sheets_conf.shared_layout.excluded_sheets` to import every sheet
  except selected sheets;
- `multiple_sheets_conf.sheets` for per-sheet layouts.

`included_sheets` and `excluded_sheets` are exclusive. Invalid JSON or
configuration returns `422` with `error` and `details`.

Wishlist modes:

- `{"mode": "none"}`: no wishlist source, all imported rows are collection
  rows;
- `{"mode": "sheet", ...}`: a dedicated sheet supplies wishlist rows and must
  include `sheet_name`, `data_range`, `header_row` and `column_information`;
- `{"mode": "column"}`: every collection layout must define
  `column_information.wishlist`.

Accepted wishlist column values are `Oui/Non`, `O/N`, `True/False`,
`Yes/No` and `Y/N`, case-insensitively. Empty values are imported as
`wishlist=false`. Invalid non-empty values make the row ignored and are
reported in import warnings.

The upload is accepted only once per user. If `t_user.collection_file_path` is
already set, the backend returns `409` and does not replace the existing
collection data.

The backend copies the staged temporary file to
`/users/workspace/<user_id>/<user_id>-collection.ods`, stores this complete path
in `t_user.collection_file_path` only after a successful import, and removes the
final copied file if the import fails. The copied file is chmod `0440`.

Only configured ODS sheets are imported. With a shared layout, the user may
either provide the sheets to import or the sheets to exclude; without either
list, every sheet is imported. Missing platforms, studios and games are
created; existing records are reused. User-game associations are inserted in
`t_user_collection` when missing with their `wishlist` value and ignored when
already present. No existing platform, studio, game or user association is
updated by this endpoint.

Successful response:

```json
{
  "created_platforms": 3,
  "created_studios": 12,
  "created_games": 42,
  "associated_games": 58,
  "wishlisted_games": 12,
  "warnings": {
    "invalid_wishlist": 3,
    "invalid_wishlist_values_found": ["Ok", "Peut etre", "Nop"]
  }
}
```

The `associated_games` counter is the number of games attached to the user after
the import payload is processed, including games that already existed before the
request. `wishlisted_games` counts imported games whose final retained import
value is `wishlist=true`.

Import errors use:

- `400` for an invalid or unreadable ODS file;
- `404` when the temporary file does not exist;
- `409` when the connected user already has a collection;
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
EMAIL_VERIFICATION_TOKEN_TTL_HOURS=24
SMTP_FROM_EMAIL=noreply@example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
SMTP_USE_TLS=true
```

`ADMIN_NOTIFICATION_EMAIL` receives a message after every successful public
registration. The message links to `/users?status=WAITING_VALIDATION` on
`FRONTEND_PUBLIC_URL` so an administrator can validate the waiting accounts. The
message includes the new user's email and the total number of users currently
waiting for administrator validation.

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
