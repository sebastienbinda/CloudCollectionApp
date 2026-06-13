# Bibliotheque

## Purpose

This document defines the functional rules to preserve for the public
Bibliotheque feature. It covers the frontend consultation pages and the backend
endpoints that expose the global reference database.

## Core Rules

- The Bibliotheque is public: visitors can consult it without a Bearer token.
- The Bibliotheque is read-only: it must never create, update or delete data.
- The Bibliotheque reads only the global reference tables:
  - `t_platform`;
  - `t_studio`;
  - `t_game`.
- The Bibliotheque must not expose private user data from `t_user`,
  `t_user_collection` or uploaded user collection file paths.
- The global reference database can be enriched by backend import workflows, but
  Bibliotheque pages and endpoints remain consultation-only.
- Public Bibliotheque API calls must not require or send authentication headers.
- The only write-capable Bibliotheque route is the protected administrator
  reset endpoint documented below. It is not part of the public consultation
  API and must require profile `ADMIN`.

## Frontend Routes

The public frontend routes are:

| Route | View | Purpose |
| --- | --- | --- |
| `/bibliotheque` | `LibraryHomeView` | Shows global counters and a public global game search. |
| `/bibliotheque/plateformes` | `LibraryEntityListView` | Lists reference platforms. |
| `/bibliotheque/studios` | `LibraryEntityListView` | Lists reference studios. |
| `/bibliotheque/jeux` | `LibraryEntityListView` | Lists reference games. |

These routes must remain accessible to unauthenticated visitors. They are also
available from the main menu through the `Bibliotheque` entry.

The `/bibliotheque` page includes a game search field using the same interaction
pattern as the collection search UI: a search input, result count, close action
when results are visible, loading state and compact result cards. This search
must query the global game reference through `GET /api/library/games` with the
`name` filter. It must not call connected-user collection endpoints and must not
send authentication headers.

Search result cards may display only public reference fields returned by the
Library API, such as game name, platform, release date, developer, editor and
status. They must not display purchase price, purchase date, user note,
wishlist state, uploaded file metadata or any user-private collection value.

## Backend Endpoints

The public backend endpoints are:

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/library/entities` | Counts global platforms, studios and games. |
| `GET` | `/api/library/platforms` | Lists global platforms. |
| `GET` | `/api/library/studios` | Lists global studios. |
| `GET` | `/api/library/games` | Lists global games. |

List endpoints accept:

- `name`: optional case-insensitive and accent-insensitive name filter;
- `page`: zero-based page index, default `0`;
- `size`: page size, default `500`, maximum `500`;
- `sort`: repeatable sort parameter using `column,direction`, where direction
  is `asc` or `desc`.

Allowed sort columns:

| Endpoint | Sort columns |
| --- | --- |
| `/api/library/platforms` | `name`, `release_date`, `manufacturer` |
| `/api/library/studios` | `name`, `country`, `creation_date` |
| `/api/library/games` | `name`, `release_date`, `developer`, `platform` |

Invalid pagination or sort values fall back to the documented defaults.

## Response Shape

`GET /api/library/entities` returns:

```json
{
  "platforms": 12,
  "studios": 34,
  "games": 56
}
```

List endpoints return a collection key and a shared `page` object:

```json
{
  "platforms": [],
  "page": {
    "page": 0,
    "size": 500,
    "totalElements": 0,
    "totalPages": 0
  }
}
```

The collection key is `platforms`, `studios` or `games` according to the
endpoint.

## Protected Administration Endpoint

`POST /api/library/reset` is an authenticated `ADMIN` endpoint exposed for the
Configuration page. It starts an asynchronous reset job that rebuilds the global
Library from stored user collection files and saved import configurations.

This endpoint is the explicit exception to the public read-only rule. It must
not be called by public Library pages, and public `GET /api/library/*`
consultation routes must remain unauthenticated and read-only.

The reset job:

- deletes global Library data and user-game associations in a transactionally
  controlled backend workflow;
- processes users with a stored collection file in registration order;
- reuses the same backend import core as the connected-user import workflow;
- continues with the next user when a user file is missing, unreadable, has no
  saved configuration or fails during import;
- can therefore rebuild the Library partially when one or more user imports
  fail;
- sends the final status report to `ADMIN_NOTIFICATION_EMAIL` when configured.

Only one reset can run at a time. A second launch attempt returns `409`.

## Architecture Rules

- Frontend HTTP details stay in `frontend/src/services/LibraryApi.js`.
- Protected admin reset HTTP details stay outside the public `LibraryApi`
  client so public read-only calls and destructive admin actions remain
  separated.
- Library state orchestration stays under `frontend/src/hooks/library/`.
- Page components only render state and user interactions.
- Backend routing stays in controllers under `backend/controllers/`.
- Bibliotheque business orchestration stays in `backend/services/library/`.
- SQL reads stay in repositories under `backend/services/database/`.
- Repositories used by Bibliotheque must not join or select user-private tables.

## Validation

When changing the Bibliotheque feature:

- verify unauthenticated access to all public frontend routes;
- verify unauthenticated access to public `GET /api/library/*` consultation
  endpoints;
- verify that `POST /api/library/reset` remains protected by profile `ADMIN`;
- verify that list endpoints remain read-only and paginated;
- verify that no private user table is exposed by repository queries;
- run backend tests when backend API, services or repositories change;
- run `npm run build` when frontend routes, hooks, services or components
  change.
