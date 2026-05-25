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

## Frontend Routes

The public frontend routes are:

| Route | View | Purpose |
| --- | --- | --- |
| `/bibliotheque` | `LibraryHomeView` | Shows global counters for platforms, studios and games. |
| `/bibliotheque/plateformes` | `LibraryEntityListView` | Lists reference platforms. |
| `/bibliotheque/studios` | `LibraryEntityListView` | Lists reference studios. |
| `/bibliotheque/jeux` | `LibraryEntityListView` | Lists reference games. |

These routes must remain accessible to unauthenticated visitors. They are also
available from the main menu through the `Bibliotheque` entry.

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

## Architecture Rules

- Frontend HTTP details stay in `frontend/src/services/LibraryApi.js`.
- Library state orchestration stays under `frontend/src/hooks/library/`.
- Page components only render state and user interactions.
- Backend routing stays in controllers under `backend/controllers/`.
- Bibliotheque business orchestration stays in `backend/services/library/`.
- SQL reads stay in repositories under `backend/services/database/`.
- Repositories used by Bibliotheque must not join or select user-private tables.

## Validation

When changing the Bibliotheque feature:

- verify unauthenticated access to all public frontend routes;
- verify unauthenticated access to all `/api/library/*` endpoints;
- verify that list endpoints remain read-only and paginated;
- verify that no private user table is exposed by repository queries;
- run backend tests when backend API, services or repositories change;
- run `npm run build` when frontend routes, hooks, services or components
  change.
