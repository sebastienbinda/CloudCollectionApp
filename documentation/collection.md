# User Collection Consultation

## Purpose

This document defines the functional rules for consulting the connected user's
collection after import. Detailed HTTP contracts remain in
`documentation/backend-api.md`, route protection in
`documentation/authentication.md`, and database structure in
`documentation/database.md`.

## Scope

The collection consultation pages read SQL data from PostgreSQL. They must not
parse the imported ODS file, recalculate spreadsheet formulas, or depend on a
global collection file.

The connected user is always derived from the Bearer token. Collection
consultation routes must not accept a user id in the URL, query string or
payload.

## Backend Routes

The current collection consultation uses:

- `GET /collections/videogames` for collection and wishlist statistics;
- `GET /collections/videogames/platforms/search` for collection platforms;
- `GET /collections/videogames/games/search` for collection games;
- `GET /collections/videogames/download` for the raw imported ODS file.

`POST`, `PUT` and `DELETE /collections/videogames/games` are reserved for
future actions and currently return `501`.

## Wishlist Semantics

`t_user_collection.wishlist=false` means the game belongs to the user's real
collection. `t_user_collection.wishlist=true` means the game is a wished game.

The current Ma collection frontend is intentionally centered on owned
collection entries. It must request `wishlist=false` for:

- platform lists;
- platform game lists;
- home page game search.

The frontend must accept `wishlist` in game rows returned by the backend, but it
must not display that technical value in the collection table.

Platforms that only contain wishlist games must not appear in Ma collection.

## Statistics

`GET /collections/videogames` returns separate sections:

- `collection`: totals computed with `wishlist=false`;
- `wishlist`: totals computed with `wishlist=true`.

Root-level statistic fields are compatibility aliases for the `collection`
section. Frontend collection statistics must prefer the `collection` section
when present.

## Filtering

Collection game and platform search endpoints support `wishlist=true` and
`wishlist=false`. Only those two textual boolean values are accepted from query
parameters; any other value is ignored.

The wishlist filter is optional at API level. Without it, backend search
endpoints can return both owned and wished entries, which is useful for future
features. The current collection page must always pass `wishlist=false`.

## Validation

When changing collection consultation:

- update backend tests for query parsing, SQL filters and response mapping;
- update frontend build validation when API calls or normalization change;
- run `./test_backend.sh`;
- run `npm run build` from `frontend/`;
- rebuild backend and web Docker images when runtime behavior changes.
