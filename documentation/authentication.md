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
  - `POST /api/auth/register`, used to create an account before the user can
    own a Bearer token.
  - `GET /api/auth/verify-email` and `POST /api/auth/verify-email`, used from
    an email verification link before sign-in.
  - `GET /api/library/entities`, used to expose public reference entity counts.
  - `GET /api/library/platforms`, used to expose public reference platforms.
  - `GET /api/library/studios`, used to expose public reference studios.
  - `GET /api/library/games` and `GET /api/library/games/<game_id>`, used to
    expose public reference games.
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

- `USER`: default profile for registered users.
- `ADMIN`: profile reserved for the configured `AUTH_USERNAME` /
  `AUTH_PASSWORD_ENCRYPTED` account.

Profiles are hierarchical. `ADMIN` inherits every route right granted to `USER`.
Protected user routes require at least `USER`, while administrative routes such
as `POST /api/library/reset` and `POST /api/library/platform-catalog/sync`
require `ADMIN`.

This hierarchy is a backend authorization rule only. The configured technical
`ADMIN` account is not a collection owner in the frontend workflow: it must not
be offered the `Ma collection`, platform detail, add-game or collection import
screens. After sign-in, an `ADMIN` session opens `/configuration` instead of
checking connected-user collection status.

Connected-user collection routes are protected routes with the same minimum
profile:

- `GET /api/users/me/collection`
- `POST /api/users/import/file/<file_type>`
- `POST /api/users/import/analyze/<file_type>`
- `POST /api/users/import`
- `POST /api/users/collection/reinit`
- `GET /collections/videogames`
- `GET /collections/videogames/platforms/search`
- `GET /collections/videogames/games/search`
- `GET /collections/videogames/games/<game_id>`
- `GET /collections/videogames/download`
- `POST /collections/videogames/games`
- `PUT /collections/videogames/games`
- `DELETE /collections/videogames/games`

These routes must derive the target user from the validated Bearer token and
must not accept a user identifier from the request payload or query string.

The Bearer token payload must contain:

- `sub`: authenticated subject;
- `profile`: `USER` or `ADMIN`;
- `iat`: issue timestamp;
- `exp`: expiration timestamp.

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
- Never accept an unsigned token or a token whose expiration has passed.

## Environment Variables

Main variables:

- `AUTH_USERNAME`: authorized username.
- `AUTH_PASSWORD_ENCRYPTED`: encrypted application password.
- `AUTH_SECRET_KEY_ENCRYPTED`: encrypted signing secret.
- `AUTH_ENV_ENCRYPTION_KEY`: Fernet key used to decrypt secrets.
- `AUTH_TOKEN_TTL_SECONDS`: Bearer token lifetime.

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
  detail pages.
- The authenticated Ma collection page is `HomeView` on `/collection`.
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
- If a sent token is rejected (`401` or `403`), the frontend must clear the local
  session and open the sign-in flow again.

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
./test_backend.sh
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
