# Main Menu Summary

## Key Points

- Any unauthenticated user is redirected to the About page from every private
  site page.

## Public Routes

- `/about`: public About page for unauthenticated visitors.
- `/auth`: sign-in page.
- `/bibliotheque`: public Library landing page with global entity counters.
- `/bibliotheque/plateformes`: public paginated platform reference list.
- `/bibliotheque/studios`: public paginated studio reference list.
- `/bibliotheque/jeux`: public paginated game reference list.
- `/`: redirects to `/about` without a token, to `/collection` with a
  non-`ADMIN` token, and to the administration dashboard with an `ADMIN` token.

The Bibliotheque routes must stay public and read-only. They consult the global
reference database and must not depend on connected-user collection status.

## Authenticated Routes

- `/collection`: authenticated Ma collection page for non-`ADMIN` users who
  already have a collection.
- `/collection/import`: authenticated onboarding page shown when
  `GET /api/users/me/collection` returns `has_collection: false` for a
  non-`ADMIN` user.
- `/users`: user administration page, visible only when backend route discovery
  confirms access to `GET /api/users`.

After sign-in, the frontend must check the connected user's collection status
before opening Ma collection, except for the configured `ADMIN` account. Users
with `has_collection: true` continue to `/collection`. Users with
`has_collection: false` are redirected to `/collection/import`, where they can
upload an ODS file, analyze its sheets, configure extraction, and launch final
import. After a successful import, the frontend redirects to `/collection`.

The import onboarding page lets non-`ADMIN` users configure single-sheet import,
shared-layout multi-sheet import with included or excluded sheets, and per-sheet
layouts. Backend validation and persistence remain authoritative.

The `ADMIN` profile keeps backend access through the route catalog and Bearer
token hierarchy, but the frontend must not offer collection ownership screens to
that profile. `Ma collection`, platform detail, add-game and collection import
routes must be disabled or redirected to the administration dashboard for
`ADMIN`.

The import onboarding page must remain a frontend workflow only: validation,
deduplication, database updates and filesystem storage decisions belong to the
backend.
