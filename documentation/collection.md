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
- `GET /collections/videogames/games/search` for collection and wishlist
  games;
- `GET /collections/videogames/games/<game_id>` for one connected-user game
  detail;
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

The collection game detail page is reachable from collection search results,
platform game tables and wishlist tables. It must call
`GET /collections/videogames/games/<game_id>` and the backend must return a
game only when the connected user owns the corresponding `t_user_collection`
association.

Platform game tables and wishlist tables must open game detail by clicking or
keyboard-activating the whole game row. They must not reserve a dedicated
detail icon column for this action. Row-level edit or delete actions, when
available, remain separate controls and must not trigger detail navigation.

On mobile, collection and wishlist game tables are rendered as compact game
entries instead of dense tabular rows. The first line displays the game name.
For the collection platform page, the second line displays the release date,
purchase price and grade when those values are available; it must not repeat
the platform already selected by the page filter. Wishlist entries keep the
release date and platform on their second line. The region flag is displayed in
both desktop and mobile lists. This mobile presentation must keep the same
row-click detail navigation as desktop.

On desktop, the collection platform game table displays only the game name,
region/version icon, release date, purchase date, grade and purchase price.

The frontend must accept `wishlist` in game rows returned by the backend, but it
must not display that technical value in the collection table.

The authenticated collection game detail displays private purchase and copy
information only when it is not null. Purchase price uses its persisted ISO
unit without conversion. Condition integers are mapped in the frontend from
`Mauvais` to `Neuf`; region codes are displayed with their corresponding flag,
using a globe for `ASIA`. Public Library game detail must never expose these
user-specific fields.

Platforms that only contain wishlist games must not appear in Ma collection.

The wishlist frontend page is centered on wished entries. It must request
`wishlist=true` from `GET /collections/videogames/games/search`, display only
the user-facing wishlist columns and must not expose the technical `wishlist`
field.

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
parameters; any other value returns `400` with a clear JSON `error` message.

Unsupported collection search parameters, unsupported sort columns, unsupported
sort directions and invalid criterion formats also return `400` with a clear
JSON `error` message.

The wishlist filter is optional at API level. Without it, backend search
endpoints can return both owned and wished entries, which is useful for future
features. The current collection page must always pass `wishlist=false`.

Collection and wishlist list ordering must be requested through backend `sort`
parameters. React pages may keep local display filters, but must not apply an
additional local sort to backend collection results.

Game list filters must be displayed above the table/list, not as a filter row
inside the table. The collection platform page exposes a game-name search and
the current platform selector above the table. The wishlist page exposes a
game-name search and a platform selector above the table. Desktop and mobile
layouts must use the same filter state, while mobile keeps the compact game
entry rendering.

## Validation

When changing collection consultation:

- update backend tests for query parsing, SQL filters and response mapping;
- update frontend build validation when API calls or normalization change;
- run `./test_backend.sh`;
- run `npm run build` from `frontend/`;
- rebuild backend and web Docker images when runtime behavior changes.
