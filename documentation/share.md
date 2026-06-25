# Collection Sharing

## Purpose

This document is the concise functional reference for temporary collection
sharing. Detailed HTTP payloads remain in `documentation/backend-api.md`, token
rules in `documentation/authentication.md`, collection filtering in
`documentation/collection.md`, and persistence in `documentation/database.md`.

## Core Invariants

- A registered `USER` may create temporary links whose target is always their
  own collection. The frontend offers management only after an import exists.
  `GUEST` cannot manage shares and does not inherit `USER` or `ADMIN` rights.
- A share must allow the owned collection, the wishlist, or both. Price access
  is independent and never grants access to a category by itself.
- Share duration is an integer from 1 to 240 hours.
- PostgreSQL stores the share identifier, owner, dates, optional recipient and
  permissions, never a raw link token or GUEST Bearer token.
- Backend checks remain authoritative. Frontend menu and page restrictions are
  presentation rules, not a security boundary.

## Lifecycle

1. The owner creates a share with `POST /api/collection-shares`.
2. Backend persists `t_collection_share`, including the optional recipient
   label used for owner display and access logs, signs a link token and returns
   an absolute `<FRONTEND_PUBLIC_URL>/collection/share/<token>` link.
3. The visitor opens the transient public frontend route. Any existing local
   session is cleared and the link token is exchanged without Authorization at
   `POST /api/auth/collection-share/session`.
4. Frontend immediately replaces the token-bearing URL with `/about`, then
   stores the returned GUEST Bearer and redirects to `/collection` when allowed,
   otherwise `/wishlist`.
5. Every protected GUEST request verifies the Bearer signature and expiration,
   then reloads the share and owner from PostgreSQL. The data owner is always
   `owner_user_id` from the validated GUEST claims, never a client parameter.
6. Expiration, explicit revocation, owner deletion or owner locking invalidates
   the session on its next backend call. Backend returns `411` with
   `error_code: COLLECTION_SHARE_UNAVAILABLE`; frontend clears the Bearer and
   returns to `/about` with an unavailable-share message.

Expired and revoked rows remain available in owner history. Owner deletion
cascades to their shares.

## Tokens And Claims

The link token and the GUEST Bearer are distinct signed credentials:

- link token: `token_kind=COLLECTION_SHARE_LINK`, `collection_share_id`, `sub`,
  `profile=GUEST`, `iat`, `exp`; it is accepted only by the public exchange
  endpoint and is rejected as a Bearer;
- GUEST Bearer: standard `sub`, `display_name`, `profile`, `iat`, `exp`, plus
  `collection_share_id`, `owner_user_id`, `owner_pseudonym`, and
  `permissions.collection`, `permissions.wishlist`, `permissions.prices`.

The GUEST Bearer expires no later than the persisted share. Link and Bearer
signatures use the existing `AuthTokenService`; neither credential is logged.
When a link token is exchanged for a GUEST Bearer, backend logs the share id,
owner id and stored recipient label, but never logs the raw token.

## Permissions And Data Filtering

| Permission | Backend effect | Frontend effect |
| --- | --- | --- |
| `collection` | Allows `wishlist=false` statistics, platform search, game search and detail. | Shows Collection, platform pages and `Collection de <pseudonyme>`. |
| `wishlist` | Allows `wishlist=true` statistics, search and detail. | Shows Wishlist and `Liste de souhaits de <pseudonyme>`. |
| `prices` | Keeps `purchase_price`, `price_unit`, `total_value` and `average_value`. | Shows price fields and statistics when present. |

Without `prices`, game list/detail payloads omit `purchase_price` and
`price_unit`; platform and collection price statistics are returned as zero.
Frontend must not recreate, infer, convert or display missing prices.

When a GUEST explicitly requests a forbidden category, backend returns `403`.
When no `wishlist` criterion is supplied, backend forces the only allowed
category; it may leave the criterion open only when both categories are shared.

## Routes

| Access | Method and route | Purpose |
| --- | --- | --- |
| Public | `POST /api/auth/collection-share/session` | Exchange link token for GUEST Bearer. |
| USER/ADMIN | `POST /api/collection-shares` | Create an owned share. |
| USER/ADMIN | `GET /api/collection-shares` | List owned active, expired and revoked shares. |
| USER/ADMIN | `DELETE /api/collection-shares/<share_id>` | Revoke an owned share idempotently. |
| GUEST/USER/ADMIN | `GET /collections/videogames` | Read permitted statistics. |
| GUEST/USER/ADMIN | `GET /collections/videogames/platforms/search` | Read permitted platforms. |
| GUEST/USER/ADMIN | `GET /collections/videogames/games/search` | Read permitted games. |
| GUEST/USER/ADMIN | `GET /collections/videogames/games/<game_id>` | Read a permitted game detail. |

Download, game mutations, import, reinitialization, share management and image
upload remain unavailable to GUEST.

## Frontend Rules

- Owner management is routed at `/configuration/partages` and is shown only to
  a `USER` with an imported collection and discovered share-management rights.
- Owner management lets the owner set an optional recipient label when creating
  a share and displays that label in the existing-share list.
- GUEST identity is `Invité de <pseudonyme>` with the yellow desktop/mobile
  treatment.
- Collection and Wishlist menu entries are omitted when their respective claim
  is false. Library, About and Logout remain available.
- Configuration, all Configuration subpages, add/edit/delete, import,
  reinitialization and image proposal are hidden from GUEST; direct navigation
  redirects to the first allowed category, otherwise About.
- The public link route is transient: the raw link token must be removed from
  browser history before any shared page is rendered.

## Validation

Changes to sharing require backend tests for creation, ownership, exchange,
permission combinations, price filtering, revocation and `411`; frontend tests
for exchange, redirects, session clearing and presentation policies; a frontend
production build; and rebuilt backend/web Docker images when runtime behavior
changes.
