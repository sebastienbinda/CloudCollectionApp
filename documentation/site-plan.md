# Main Menu Summary

## Key Points

- Any unauthenticated user is redirected to the About page from every private
  site page.

## Public Routes

- `/about`: public About page for unauthenticated visitors.
- `/auth`: sign-in page. When opened from an activation email with
  `email=<address>`, it redirects to `/about` if that account is already
  connected, or asks the connected user to sign out before reconnecting with
  the requested account. Account creation requires a unique pseudonym, explains
  its display and future sharing purpose, checks availability on blur and
  disables submission until a valid available pseudonym is confirmed.
- `/auth/verify-email`: public email verification result page opened after the
  backend validates a browser verification link.
- `/collection/share/<token>`: transient public activation route. It clears any
  existing local session, exchanges the signed link token without
  Authorization, immediately removes the raw token from browser history, then
  opens the first shared category. It renders About with an error when exchange
  fails.
- `/bibliotheque`: public Library landing page with global entity counters and
  public global game search.
- `/bibliotheque/plateformes`: public paginated platform reference list.
- `/bibliotheque/plateformes/<platform_id>`: public platform detail from the
  global reference Library, including platform aliases, usage regions and
  accepted platform images.
- `/bibliotheque/studios`: public paginated studio reference list.
- `/bibliotheque/jeux`: public paginated game reference list.
  Authenticated administrators get an additional filter for games reported or
  not reported as duplicates, a validation status column and filter, and bulk
  validation/refusal actions for waiting games. Non-administrators must not see
  the validation status column on this public list.
- `/bibliotheque/jeux/<game_id>`: public game detail from the global
  reference Library. Connected `USER` accounts with an imported collection can
  report the displayed Library game as a possible duplicate after an explicit
  confirmation, even when that game is not attached to their own collection.
  When the displayed game is also in the connected user's collection, the page
  shows an ownership indicator.
- `/`: redirects to `/about` without a token, to `/collection` with a
  non-`ADMIN` token, and to `/configuration` with an `ADMIN` token.

The Bibliotheque routes must stay public and read-only. They consult the global
reference database. `/bibliotheque/jeux` may show connected `USER` markers when
the listed game is already in the user's collection or wishlist; the page must
still load as a public reference list without those markers when no valid token
is available.
The platform image file route
`GET /api/library/platforms/<platform_id>/image/<image_id>` is public only for
images accepted by an administrator; waiting images must not be displayed from
public pages.

## Authenticated Routes

- `/collection`: authenticated Ma collection page for non-`ADMIN` users who
  already have a collection.
- `/collection?platform_id=<platform_id>`: authenticated platform detail for a
  non-`ADMIN` user's collection, listing games attached to that platform.
- `/collection/statistics`: authenticated statistics page for non-`ADMIN`
  users with a collection. It displays backend-computed owned-collection
  diagrams and the games whose normalized note is greater than or equal to `90`.
- `/collection/jeux/<game_id>`: authenticated game detail, only for games
  attached to the connected user's collection. It may include `?region=<code>`
  to select one copy when the same Library game exists in several user
  regions/versions; without this parameter, the backend selects `EU-FR`.
  Nullable private purchase and copy information is shown only when available,
  including region flag and purchase-price unit. The connected `USER` can
  report the displayed game as a possible duplicate after an explicit
  confirmation. The page shows an ownership indicator.
- `/wishlist`: authenticated wishlist page for non-`ADMIN` users who already
  have a collection. It displays wished games from the connected user's SQL
  collection data and keeps the `wishlist_buy_status` filter in the URL.
- `/collection/import`: authenticated onboarding/import page shown when
  `GET /api/users/me/collection` returns `has_collection: false` for a
  non-`ADMIN` user, and reachable from Configuration when the same user already
  has a collection and wants to add games from another file. When opened from
  Configuration, the page must start from a fresh import form and must not show
  the previous import report.
- `/configuration`: authenticated Configuration page for protected application
  actions.
- `/configuration/partages`: authenticated owner page for creating, copying,
  listing and revoking temporary shares, including an optional recipient label.
  It is available only to a `USER` with an imported collection and discovered
  share-management route permissions.
- `/configuration/doublons/<game_id>`: authenticated `ADMIN` page for refusing
  or merging a Library game duplicate from a Library game detail, even when the
  game has not been reported by a user. After a reject or merge action, the page
  displays a dedicated result screen with a clear success or failure state and,
  after a successful merge, a button back to the kept Library game detail.
- `/users`: user administration page, visible only when backend route discovery
  confirms access to `GET /api/users`.

## GUEST Routes

A GUEST session is a non-`ADMIN` read-only session scoped by signed share
claims:

- `/collection` and platform views are available only with collection
  permission and display `Collection de <pseudonyme>`;
- `/collection/statistics` is available only with collection permission and
  displays the shared owner's owned-collection statistics;
- `/wishlist` is available only with wishlist permission, displays
  `Liste de souhaits de <pseudonyme>` and initializes the buy-status filter
  from the share claim when the URL does not already define it;
- `/collection/jeux/<game_id>` is available only when backend confirms that
  the game, optionally selected with `?region=<code>`, belongs to a shared
  category;
- `/bibliotheque/**`, `/about` and Logout remain available;
- `/configuration`, every `/configuration/**` subroute, `/users`, `/add-game`
  and `/collection/import` are unavailable. Direct navigation redirects to the
  shared Collection first, otherwise Wishlist, otherwise About.

When a protected GUEST call returns `411`, the frontend clears the session and
returns to `/about` with the expired/revoked-share message. It does not open the
ordinary sign-in modal. Missing price claims are reflected by absent price UI,
not frontend calculation.

After sign-in, the frontend must check the connected user's collection status
before opening Ma collection, except for the configured `ADMIN` account. Users
with `has_collection: true` continue to `/collection`. Users with
`has_collection: false` are redirected to `/collection/import`, where they can
upload an ODS or CSV file, analyze its sheets or columns, configure extraction,
and launch final import. After a successful import, the frontend displays a
summary of the backend counters and offers an explicit action to open
`/collection`.

The import onboarding page lets non-`ADMIN` users configure single-sheet import,
shared-layout multi-sheet import with included or excluded sheets, per-sheet
layouts, and optional wishlist extraction from no source, a dedicated sheet, or
a dedicated column for ODS files. For CSV files, it lets users map each
importable information to a detected CSV column and supports wishlist from no
source or from a dedicated column. It also lets the user select one global ISO
price unit, one global rating base and map optional private game-information
columns. Backend validation and persistence remain authoritative.

The `ADMIN` profile keeps backend access through the route catalog and Bearer
token hierarchy, but the frontend must not offer collection ownership screens to
that profile. `Ma collection`, statistics, wishlist, platform detail, add-game and
collection import routes must be disabled or redirected to `/configuration` for
`ADMIN`.

Authenticated registered-user headers display the pseudonym from the signed
token rather than the email. The configured technical administrator continues
to display its configured username.

The `/users` administration page lets an `ADMIN` validate users with status
`WAITING_VALIDATION`. Validation activates the account on the backend and sends
the user an activation email containing the sign-in link with the validated
email as the `email` query parameter.
Administrator notification emails are sent after user email verification and may
link directly to
`/users?status=WAITING_VALIDATION`, which must open the users page filtered to
all accounts waiting for validation.

The Configuration page exposes collection-level protected actions for
authenticated non-`ADMIN` users. It must expose an import action that opens
`/collection/import` without reinitializing the current collection.
`Reinitialiser la collection` must only be shown to collection users when route
discovery confirms access to `POST /api/users/collection/reinit`; after success
it opens `/collection/import`.

For `ADMIN`, the Configuration page may expose a protected `Reset Bibliotheque`
action only when backend route discovery confirms access to
`POST /api/library/reset`. The action must ask for explicit confirmation before
launching the reset, display a success message after `202`, display an
already-running message after `409`, and must not add polling or a job status
page. This does not make public Bibliotheque pages writable; they remain public
read-only consultation routes.

For `ADMIN`, the Configuration page may also expose `Mettre a jour` for the
platform catalog only when route discovery confirms access to
`POST /api/library/platform-catalog/sync`. The action must ask for explicit
confirmation before inserting missing platforms and aliases from backend CSV
resources, then display the insertion counters returned by the backend.

For `ADMIN`, the Configuration page may expose a platform image moderation
section only when backend route discovery confirms access to
`GET /api/library/platforms/images`. The section lists images with server-side
pagination, status and platform filters, thumbnail preview, proposer `user_id`
and proposer email when available. Accept and refuse actions must call the
protected status endpoint only when route discovery confirms access; refusal
removes the image from the local list after backend success. The `MAIN` action
must call the protected type endpoint only when route discovery confirms access
and refresh the list after success.

The import onboarding page must remain a frontend workflow only: validation,
deduplication, database updates and filesystem storage decisions belong to the
backend.
