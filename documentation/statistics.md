# Collection Statistics

## Purpose

This document summarizes the dedicated collection statistics screen. Detailed
HTTP payloads remain in `documentation/backend-api.md`, authentication in
`documentation/authentication.md`, sharing rules in `documentation/share.md`,
and collection consultation rules in `documentation/collection.md`.

## Functional Scope

The Statistics page is available at `/collection/statistics` for connected
non-`ADMIN` collection users. It displays backend-computed statistics for the
owned collection only, meaning `t_user_collection.wishlist = false`.

The page shows:

- game proportions by platform;
- game counts by release year;
- game counts by purchase year;
- games whose numeric grade is strictly greater than `9`, with name, platform,
  release date and purchase date.

Wishlist entries are excluded from every statistic on this page.

## Backend Contract

The page calls `GET /collections/statistics`. The endpoint accepts only `USER`
and `GUEST` profiles. `ADMIN` is intentionally excluded because the frontend
administrator is not a collection owner.

The backend derives the target user from the Bearer token:

- `USER`: database user resolved from `sub`;
- `GUEST`: shared owner resolved from the signed and revalidated
  `owner_user_id` claim.

For `GUEST`, the endpoint requires the `collection` permission. A wishlist-only
share receives `403` and must not learn owned-collection statistics.

All statistics are calculated in backend SQL repositories. The frontend must not
recompute totals from game lists.

## Frontend Rules

The menu entry is named `Statistiques`, uses a dedicated chart icon, and is
visible on desktop and mobile only when:

- a non-`ADMIN` authenticated session exists;
- collection viewing is allowed;
- backend route discovery confirms access to `GET /collections/statistics`.

For GUEST, the entry is visible only with the signed `collection` permission.
The page uses `PageLayout` and must not recreate the application header, menu or
footer.

The visual charts are CSS-based bars. No chart dependency is required.
