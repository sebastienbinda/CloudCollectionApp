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

For a GUEST session, the same invariant applies with a different trusted
source: the target collection is `owner_user_id` from the signed GUEST Bearer,
whose share and owner have just been revalidated in PostgreSQL. The frontend
must never choose or submit the owner identifier. Complete lifecycle rules are
in `documentation/share.md`.

## Backend Routes

The current collection consultation uses:

- `GET /collections/videogames` for collection and wishlist statistics;
- `GET /collections/statistics` for detailed owned-collection statistics;
- `GET /collections/videogames/platforms/search` for collection platforms;
- `GET /collections/videogames/games/search` for collection and wishlist
  games;
- `GET /collections/videogames/games/<game_id>` for one connected-user game
  detail;
- `GET /collections/videogames/download` for the raw imported ODS file.

`POST`, `PUT` and `DELETE /collections/videogames/games` are reserved for
future actions and currently return `501`.

The four `GET` consultation routes except ODS download accept `GUEST`, `USER`
and `ADMIN`. ODS download and every mutation remain restricted to at least
`USER`; GUEST cannot import, reinitialize, download or modify collection data.

## GUEST Consultation Scope

The backend creates a collection-access context from the validated token:

- USER/ADMIN: owner resolved from the Bearer `sub` email;
- GUEST: owner resolved from signed `owner_user_id`, with
  `permissions.collection`, `permissions.wishlist` and `permissions.prices`.

An explicit `wishlist=false` request requires collection permission; an
explicit `wishlist=true` request requires wishlist permission. A forbidden
category returns `403`. When the criterion is absent, a GUEST with only one
category is forced to that category; a GUEST with both permissions may query
both. Game detail checks the persisted row category and returns `403` when that
category is not shared.

When prices are not shared, backend removes `purchase_price` and `price_unit`
from every game list/detail payload and sets `total_value` and `average_value`
to zero in root, collection, wishlist and platform statistics. Other code must
not infer or recalculate these values. When prices are shared, persisted values
and units are returned without conversion.

The statistics response includes only permitted category counts for GUEST. A
non-permitted collection or wishlist section is empty rather than leaking its
game count.
The dedicated detailed statistics endpoint exposes only owned-collection
statistics and therefore requires the GUEST `collection` permission.

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

For GUEST, collection detail remains read-only. Frontend hides add, edit,
delete, import, reinitialization, download and platform-image proposal actions.
These visual restrictions supplement the backend profile checks.

Platforms that only contain wishlist games must not appear in Ma collection.

The wishlist frontend page is centered on wished entries. It must request
`wishlist=true` from `GET /collections/videogames/games/search`, display only
the user-facing wishlist columns and must not expose the technical `wishlist`
field.

The wishlist page may add `wishlist_buy_status=all|yes|no` to the backend game
search. `all` keeps every wished game. `yes` keeps wished games whose purchase
date, purchase location or purchase price is defined. `no` keeps wished games
where none of those purchase-in-progress fields is defined. The selected value
is preserved in the URL for direct access. For GUEST sessions, the initial URL
value is derived from the signed share claim
`wishlist_buy_status_default_filter` when the query parameter is absent, and
the GUEST can change it afterwards.

## Statistics

`GET /collections/videogames` returns separate sections:

- `collection`: totals computed with `wishlist=false`;
- `wishlist`: totals computed with `wishlist=true`.

Root-level statistic fields are compatibility aliases for the `collection`
section. Frontend collection statistics must prefer the `collection` section
when present.

For collection and platform statistics, `total_value` is the sum of persisted
`purchase_price` values. `average_value` is calculated only from entries whose
`purchase_price` is not null and is rounded to two decimal places. An empty set
of prices returns zero for both values.

`GET /collections/statistics` returns detailed, backend-computed statistics for
`wishlist=false`: platform proportions, release-year distribution,
purchase-year distribution and games whose numeric note is strictly greater
than `9`. Frontend pages must not recalculate these distributions from game
lists.

## Filtering

Collection game and platform search endpoints support `wishlist=true` and
`wishlist=false`. Only those two textual boolean values are accepted from query
parameters; any other value returns `400` with a clear JSON `error` message.

Unsupported collection search parameters, unsupported sort columns, unsupported
sort directions and invalid criterion formats also return `400` with a clear
JSON `error` message.

The `wishlist` filter is optional at API level. Without it, backend search
endpoints can return both owned and wished entries, which is useful for future
features. The current collection page must always pass `wishlist=false`.
The `wishlist_buy_status` filter is optional and meaningful for wishlist game
searches; invalid values return `400`.

Collection and wishlist list ordering must be requested through backend `sort`
parameters. React pages may keep local display filters, but must not apply an
additional local sort to backend collection results.

Game list filters must be displayed above the table/list, not as a filter row
inside the table. The collection platform page exposes a game-name search and
the current platform selector above the table. The wishlist page exposes a
game-name search, a buy-status selector and a platform selector above the
table. Desktop and mobile layouts must use the same filter state, while mobile
keeps the compact game entry rendering.

## Validation

When changing collection consultation:

- update backend tests for query parsing, SQL filters and response mapping;
- update frontend build validation when API calls or normalization change;
- run `./scripts/test_backend.sh`;
- run `npm run build` from `frontend/`;
- rebuild backend and web Docker images when runtime behavior changes.
