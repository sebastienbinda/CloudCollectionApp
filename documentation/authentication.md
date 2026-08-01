# Authentication Summary

## Key Points

- Every backend endpoint is protected except explicitly documented public
  authentication and registration endpoints.
- Without a Bearer token: `403`; invalid or expired token: `401`.
- Unregistered routes return Flask's standard `404` and are not converted into
  authentication errors.
- The frontend only sends or clears the token; security remains in the backend.
- Every protected call must use `Authorization: Bearer <access_token>`.
- Every public exception must be documented and tested.

This document describes the functional constraints to follow for any change that
touches authentication, backend routes, or frontend API calls.

## Objective

The application uses simple Bearer authentication to protect collection data.
The backend remains the single authority for validating tokens and deciding
whether a request is authorized.

The frontend must never contain business security logic. It may hide actions or
avoid unnecessary calls, but all real protection must remain on the backend side.

## Backend Contract

- All application backend endpoints must require a valid Bearer token unless
  they are explicitly listed as public below.
- Public backend routes are:
  - `POST /auth/token`, used to obtain a token.
  - `POST /api/auth/collection-share/session`, used to exchange a signed,
    temporary collection-share link token for a revocable GUEST Bearer session.
  - `POST /api/auth/register`, used to create an account before the user can
    own a Bearer token.
  - `GET /api/auth/pseudonym-availability`, used to validate a registration
    pseudonym before account creation.
  - `GET /api/auth/verify-email` and `POST /api/auth/verify-email`, used from
    an email verification link before sign-in.
  - `GET /api/library/entities`, used to expose public reference entity counts.
  - `GET /api/library/platforms`, used to expose public reference platforms.
  - `GET /api/library/platforms/<platform_id>`, used to expose one public
    reference platform.
  - `GET /api/library/platforms/<platform_id>/image/<image_id>`, used to expose
    accepted public platform images.
  - `GET /api/library/studios`, used to expose public reference studios.
  - `GET /api/library/games` and `GET /api/library/games/<game_id>`, used to
    expose public reference games. `GET /api/library/games` also accepts an
    optional valid `USER` Bearer to expose only the booleans
    `in_current_user_collection` and `in_current_user_wishlist` for current-user
    collection and wishlist matches.
- CORS `OPTIONS` requests remain exempt to allow preflights.
- Routes must be protected globally with `AuthGuard.protect_all_routes`.
- Do not add a new public route without an explicit decision and without
  documenting the exception in this file.
- Do not duplicate authentication logic in business services.
- Do not read or validate the token directly in endpoints, except for a very
  local and justified need.

## Obtaining a Token

Endpoint:

```http
POST /auth/token
Content-Type: application/json
```

Accepted JSON body:

```json
{
  "username": "admin",
  "password": "password"
}
```

The backend also accepts the `client_id` and `client_secret` fields for a flow
compatible with client credentials.

Expected response:

```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

The endpoint accepts both authentication sources:

- the configured backend credentials from `AUTH_USERNAME` and
  `AUTH_PASSWORD_ENCRYPTED`, which receive the `ADMIN` profile;
- registered database users, using their verified email as `username`, only
  after email verification has succeeded and while their status is `ACTIVE`,
  which receive their database profile.

Invalid credentials, unknown users, unverified users, locked users or wrong
passwords return `401` with a `WWW-Authenticate: Bearer realm="CloudCollectionApp"`.

## Profiles And Route Rights

The supported user profiles are:

- `GUEST`: read-only profile scoped to one persisted collection share. It does
  not inherit `USER` or `ADMIN` rights.
- `USER`: default profile for registered users.
- `ADMIN`: profile reserved for the configured `AUTH_USERNAME` /
  `AUTH_PASSWORD_ENCRYPTED` account.

Profiles are hierarchical. `ADMIN` inherits every route right granted to `USER`.
`GUEST` remains outside this hierarchy and can call only routes that list it
explicitly. `GET /api/routes` lists `GUEST`, `USER` and `ADMIN` because every
authenticated frontend session needs route discovery.
Protected user routes require at least `USER`, while administrative routes such
as `POST /api/library/reset` and `POST /api/library/platform-catalog/sync`
require `ADMIN`.

This hierarchy is a backend authorization rule only. The configured technical
`ADMIN` account is not a collection owner in the frontend workflow: it must not
be offered the `Ma collection`, platform detail, add-game or collection import
screens. After sign-in, an `ADMIN` session opens `/configuration` instead of
checking connected-user collection status.

Owner workflow routes require at least `USER` (`ADMIN` inherits the backend
right even when its frontend does not expose collection ownership):

- `POST /api/collection-shares`
- `GET /api/collection-shares`
- `DELETE /api/collection-shares/<share_id>`
- `GET /api/users/me/collection`
- `POST /api/users/import/file/<file_type>`
- `POST /api/users/import/analyze/<file_type>`
- `POST /api/users/import`
- `POST /api/users/collection/reinit`
- `GET /collections/videogames/download`
- `POST /collections/videogames/games`
- `PUT /collections/videogames/games`
- `DELETE /collections/videogames/games`
- `POST /api/library/games/<game_id>/doublon`
- `POST /api/library/platforms/<platform_id>/image`

The collection read routes below explicitly accept `GUEST`, `USER` and
`ADMIN`, then apply the validated identity and share scope:

- `GET /collections/videogames`
- `GET /collections/statistics`
- `GET /collections/videogames/platforms/search`
- `GET /collections/videogames/games/search`
- `GET /collections/videogames/games/<game_id>`

These routes must derive the target user from the validated Bearer token and
must not accept a user identifier from the request payload or query string.
`GET /collections/statistics` accepts only `USER` and `GUEST` profiles, and
requires the GUEST `collection` permission because it exposes owned-collection
statistics only.
Collection-share management resolves the owner from the Bearer subject and
allows a user to list or revoke only shares attached to that owner.
For platform image upload, the backend resolves `t_platform_image.user_id` from
the token subject and stores proposed images with status `WAITING_VALIDATION`.

Protected administrator routes include:

- `POST /api/library/reset`
- `POST /api/library/platform-catalog/sync`
- `GET /api/library/platforms/images`
- `GET /api/library/games/validation/summary`
- `GET /api/library/games/<game_id>/doublon`
- `GET /api/library/games/<game_id>/doublon/candidates`
- `POST /api/library/games/doublon`
- `PUT /api/library/platforms/<platform_id>/image/<image_id>/status/<status>`
- `PUT /api/library/platforms/<platform_id>/image/<image_id>/type/<image_type>`

Platform image moderation must require profile `ADMIN`. Accepting an image
changes its status to `ACCEPTED`; refusing an image deletes the row and stored
file; setting an image to `MAIN` switches any previous platform `MAIN` image to
`OTHER`.

The Bearer token payload must contain:

- `sub`: authenticated subject;
- `profile`: `GUEST`, `USER` or `ADMIN`;
- `display_name`: registered-user pseudonym, or configured administrator name;
- `iat`: issue timestamp;
- `exp`: expiration timestamp.

A GUEST Bearer additionally contains the collection-share identifier, owner
identifier, current owner pseudonym, granted collection, wishlist and price
permissions, and the `wishlist_buy_status_default_filter` share option used by
the frontend to initialize `/wishlist`. The public link token has a distinct
signed token kind and cannot be used directly as a Bearer token. The exchange
endpoint reloads the share and owner from PostgreSQL before issuing the GUEST
session.

## Collection Share Authentication

Collection sharing uses two signed tokens with separate purposes:

1. The link token is created after `t_collection_share` has been persisted. It
   contains `token_kind=COLLECTION_SHARE_LINK` and `collection_share_id`, is
   embedded in `/collection/share/<token>`, and cannot authorize protected
   routes.
2. `POST /api/auth/collection-share/session` validates the link token without
   requiring Authorization, reloads the active share and active owner, and
   returns a revocable GUEST Bearer whose expiration does not exceed
   `t_collection_share.expires_at`.

The GUEST Bearer claims are:

- `sub`: `guest-share:<collection_share_id>`;
- `display_name` and `owner_pseudonym`: current owner pseudonym;
- `profile`: `GUEST`;
- `collection_share_id` and `owner_user_id`;
- `permissions.collection`, `permissions.wishlist`, `permissions.prices`;
- `wishlist_buy_status_default_filter`: `all`, `yes` or `no`;
- `iat` and `exp`.

Every GUEST backend request validates the signature and expiration, then loads
the share joined with its owner. A missing share, elapsed expiration, non-null
revocation date, deleted owner, or owner status other than `ACTIVE` produces
HTTP `411` with `error_code: COLLECTION_SHARE_UNAVAILABLE`. An expired GUEST
Bearer also maps to `411`; ordinary USER/ADMIN expiration remains `401`.

The raw link token and GUEST Bearer are not stored in PostgreSQL or application
logs. The exchange success log may contain the share id, owner id and persisted
recipient label so an owner can audit who a link was intended for; it must not
contain the raw link token or Bearer. The frontend stores only the exchanged
Bearer using the existing session mechanism and removes the link token from
browser history immediately.

Route authorization must be enforced by `AuthGuard` from the token profile.
Frontend route permissions may mirror the route catalog, but they must not be
treated as a security boundary.

## Registration And Email Verification

Registration and email verification are public by design because they happen
before the user can authenticate.

- `POST /api/auth/register` creates an unverified user and sends a verification
  link. With `ADMIN_ACCOUNT_VALIDATION_ENABLED=true`, the user status is
  `WAITING_VALIDATION`; with it disabled, the status is `ACTIVE` but the user
  still cannot sign in before email verification.
- Registration requires a case-insensitively unique pseudonym. The public
  availability endpoint supports the frontend blur check, while registration
  and the database unique index remain authoritative.
- `GET /api/auth/verify-email?token=<token>` validates an email from a browser
  link and redirects to the public frontend page `/auth/verify-email` with a
  stable result status. The frontend page tells the user whether the account is
  active or still awaiting administrator validation.
- `POST /api/auth/verify-email` validates an email from an API payload.
- The administrator notification for a new account is sent after email
  verification when `ADMIN_NOTIFICATION_EMAIL` is configured, even when
  administrator validation is disabled.
- The frontend `/auth` page may receive `email=<address>` from account
  activation emails. If the requested account is already connected, it opens
  `/about`; if another account is connected, it displays a sign-out choice
  before reconnecting with the requested account.

These routes must not expose collection data, password hashes, raw passwords,
verification token hashes, or raw verification tokens. Detailed implementation
rules are in `documentation/register.md`.

## Protected Calls

All calls to protected endpoints must send:

```http
Authorization: Bearer <access_token>
```

Response codes to preserve:

- `403` if no Bearer token is provided.
- `401` if a token is provided but is invalid or expired.
- `411` if a GUEST share is expired, revoked, or its owner is deleted or locked.
- `200`, `201`, `400`, `404`, or `500` according to the route's business
  contract once the token has been validated.

The current message for a missing token is `Token Bearer manquant.`.

## Token Format and Validation

- Tokens are created by `AuthTokenService`.
- The internal format is `payload.signature`.
- The payload contains at least `sub`, `profile`, `iat`, and `exp`.
- The signature uses HMAC SHA-256 with the application secret.
- The default lifetime is 3600 seconds.
- Validation must check the structure, signature, and expiration.
- Every GUEST request must additionally reload the persisted share and owner;
  no polling is required because invalidation is detected on the next call.
- Never accept an unsigned token or a token whose expiration has passed.

## Environment Variables

Main variables:

- `AUTH_USERNAME`: authorized username.
- `AUTH_PASSWORD_ENCRYPTED`: encrypted application password.
- `AUTH_SECRET_KEY_ENCRYPTED`: encrypted signing secret.
- `AUTH_ENV_ENCRYPTION_KEY`: Fernet key used to decrypt secrets.
- `AUTH_TOKEN_TTL_SECONDS`: Bearer token lifetime.

Runtime environment conventions are documented in `documentation/deploy.md`.

The plaintext variables `AUTH_PASSWORD` and `AUTH_SECRET_KEY` exist as
development fallbacks, but no hardcoded secret must be introduced in code,
tests, documentation, or scripts.

## Frontend Contract

- The token is stored in `localStorage` under `cloudCollectionAccessToken`.
- Local expiration is stored under `cloudCollectionAccessTokenExpiresAt`.
- All protected backend calls must go through `VideoGamesApi` or reuse
  `VideoGamesApi.getAuthorizationHeaders()`.
- Protected media resources used by CSS backgrounds or image tags must first be
  fetched with an authenticated `fetch` request, then displayed with a local
  object URL. Direct `url("/protected-route")` references do not send Bearer
  headers and must not be used for protected resources.
- The frontend must avoid calling protected endpoints when no token is stored.
- Public unauthenticated frontend pages are `AboutView` on `/about` and the
  Library consultation pages under `/bibliotheque`, including public game
  detail pages, public platform detail pages and accepted platform images.
- The authenticated Ma collection page is `HomeView` on `/collection`.
- `/collection/share/<token>` is a transient public frontend route. It clears
  any existing local USER, ADMIN or GUEST session, exchanges the link without
  an Authorization header, replaces the URL with `/about`, then stores the new
  GUEST Bearer and redirects according to its category permissions.
- Authenticated game detail pages under `/collection/jeux/<game_id>` must remain
  unavailable without a non-`ADMIN` collection session.
- The `/` route functionally redirects to `/about` without a token and to
  `/collection` with a non-`ADMIN` token.
- With an `ADMIN` token, collection pages remain unavailable in the frontend:
  `/collection`, `/collection/import`, platform detail and add-game views must
  redirect to `/configuration` or expose disabled navigation entries. This
  frontend restriction does not remove backend endpoint access.
- The connected-user indicator in the desktop navigation area must stay
  consistent with the locally stored token, even if route discovery temporarily
  fails after a local restart. Action buttons must remain disabled until the
  backend route catalog confirms their availability.
- The connected-user indicator reads `display_name` from the token and therefore
  shows the pseudonym instead of the email. The token `sub` remains the email
  used by backend repositories to resolve the connected user.
- If a sent token is rejected (`401` or `403`), the frontend must clear the local
  session and open the sign-in flow again.
- If a GUEST call returns `411`, the frontend must clear the local session,
  dispatch the unavailable-share flow and replace the current route with
  `/about`. It must not open the ordinary USER/ADMIN sign-in modal.
- GUEST presentation reads `owner_pseudonym` and permissions from the signed
  Bearer. It displays `Invité de <pseudonyme>` and must not expose
  Configuration, mutations, import, reinitialization, download or image upload.
- Public accepted platform images may be used directly in `<img>` tags because
  their file route is explicitly public. Pending images are moderated only from
  protected administrator API calls and must not be publicly visible before
  acceptance.

## Route Discovery

`GET /api/routes` is itself protected. It helps the frontend calculate action
permissions, but it must not become a source of truth for security. Security
remains enforced by the backend before each request.

The routes returned by this catalog must correctly indicate:

- `requires_auth`
- `access`
- `auth_schemes`
- `required_profiles`

Every protected route must announce `requires_auth: true` and `auth_schemes:
["Bearer"]`.
Protected routes must announce the profiles that can call them in
`required_profiles`. A route requiring `USER` must list both `USER` and `ADMIN`
because `ADMIN` inherits `USER` rights.
Public routes must announce `requires_auth: false`, `access: "public"` and
`auth_schemes: []`.

## Tests to Maintain

Any authentication change must update or add backend tests covering at least:

- `POST /auth/token` with valid credentials.
- `POST /auth/token` with invalid credentials.
- `POST /auth/token` rejecting a `WAITING_VALIDATION` user with a clear
  user-facing message.
- `POST /api/auth/register` without a Bearer token preserving registration
  behavior.
- `GET` or `POST /api/auth/verify-email` without a Bearer token preserving
  verification behavior.
- Administrator notification after successful email verification.
- A protected endpoint without a token returning `403`.
- A protected endpoint with an invalid token returning `401`.
- A protected endpoint with a valid token preserving its business behavior.
- The `/api/routes` catalog and its authentication indicators.

After modification, run:

```bash
./scripts/test_backend.sh
```

If the change impacts runtime behavior, rebuild the affected Docker images when
the Docker daemon is available.

## Development Rules

- Never expose collection data from the backend without a token.
- Never reintroduce a public read mode that only hides some fields on the backend
  side.
- Keep registration and email verification public, but limited to account
  creation and email validation behavior.
- Never hardcode a secret, token, password, or signing key.
- Do not add an external authentication dependency without strong justification.
- Prefer extending `AuthGuard` and `AuthTokenService` over scattered checks.
- Every public exception must be explicit, tested, and mentioned in this
  document.
