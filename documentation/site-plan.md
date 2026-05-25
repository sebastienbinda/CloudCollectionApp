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
- `/`: redirects to `/about` without a token and to `/accueil` with a token.

The Bibliotheque routes must stay public and read-only. They consult the global
reference database and must not depend on connected-user collection status.

## Authenticated Routes

- `/accueil`: authenticated home page for users who already have a collection.
- `/collection/import`: authenticated onboarding page shown when
  `GET /api/users/me/collection` returns `has_collection: false`.
- `/users`: user administration page, visible only when backend route discovery
  confirms access to `GET /api/users`.

After sign-in, the frontend must check the connected user's collection status
before opening the home page. Users with `has_collection: true` continue to
`/accueil`. Users with `has_collection: false` are redirected to
`/collection/import`, where they can upload an ODS file through
`POST /api/users/import`. After a successful import, the frontend redirects to
`/accueil`.

The import onboarding page must remain a frontend workflow only: validation,
deduplication, database updates and filesystem storage decisions belong to the
backend.
