# User Collection Import Rules

## Purpose

This document gives future AI agents and developers the functional rules to
preserve when changing the user collection import workflow. It is intentionally
synthetic. Detailed route contracts remain in `documentation/backend-api.md`,
database structure in `documentation/database.md`, and frontend navigation in
`documentation/site-plan.md`.

## Core Workflow

- A connected `USER` without collection must be redirected to
  `/collection/import` after sign-in.
- A connected user with `t_user.collection_file_path` already set must continue
  to `/accueil`.
- The frontend must call `GET /api/users/me/collection` to decide between those
  two paths.
- The import page only collects the ODS file and displays interaction state.
  Validation, storage, deduplication and persistence belong to the backend.
- After a successful import, the frontend must redirect to `/accueil`.

## Backend API Contract

- `GET /api/users/me/collection` returns only:

```json
{
  "has_collection": true
}
```

- `POST /api/users/import` must use `multipart/form-data` with field
  `collection_file`.
- Both routes require a Bearer token with at least profile `USER`.
- The connected user must always be derived from the Bearer token. Do not accept
  a user id from the request payload, URL or query string.
- A second import for a user whose `collection_file_path` is already set must
  return `409`.
- Invalid or unreadable ODS input must return `400`.
- Oversized upload or multipart body must return `413`.
- Unexpected failures must return `500` without leaking internal paths, SQL or
  stack traces.

## Persistence Rules

- Import must be atomic: all database changes succeed together or none are kept.
- `t_user.collection_file_path` must be updated only after the import data has
  been successfully persisted.
- The stored path format is:

```text
/users/workspace/<user_id>/<user_id>-collection.ods
```

- The copied file must be removed when import parsing or persistence fails.
- The copied file must be read-only for user and group: `0440`.
- Existing platforms, studios, games and user-game associations must be reused,
  not overwritten.
- `t_user_collection` rows are inserted only when missing. Existing
  `(user_id, game_id)` rows are not errors.
- `game_additional_name` is not filled by the current import workflow.

## ODS Import Rules

- Only platform sheets are imported.
- Technical sheets such as `Accueil` and `Liste de souhaits` must be ignored.
- Platforms are matched by normalized platform name.
- Studios are matched by normalized studio name.
- Games are matched by normalized game name and platform.
- Duplicate ODS entries after normalization keep the first occurrence and ignore
  later duplicates with warning-level logging.
- Empty or invalid game release dates must be persisted as `NULL`, not as
  invalid text values.
- The editor field remains empty until a dedicated rule is specified.

## Normalization Rules

- Stored names are `trim().lower()` while preserving accents.
- Comparison keys are `trim().lower()` with accents removed through Unicode
  normalization.
- Do not replace this behavior with plain case-insensitive SQL matching unless
  accent equivalence is still preserved.

## Configuration Rules

- `USER_COLLECTION_MAX_UPLOAD_BYTES` is the single upload size setting.
- The same value must configure Flask request size handling and the Nginx
  `client_max_body_size` used by the `web` service.
- Docker must mount the host `USERS_WORKSPACE` into `/users/workspace` for the
  backend container.
- Do not hardcode secrets, tokens or user-specific absolute host paths.

## Frontend Rules

- Keep the import workflow in `frontend/src/hooks/collection/`.
- Keep HTTP details in `frontend/src/services/UserCollectionApi.js` or another
  service in `frontend/src/services/`.
- Use `FormData` for upload and do not manually set the multipart
  `Content-Type` header.
- The import view must not duplicate backend validation rules beyond basic file
  selection UX.
- Automatic backend calls must use the shared backend availability guard so a
  stopped backend cannot trigger unbounded request loops.

## Testing Rules

When changing this feature, update or run tests covering:

- missing collection status returns `has_collection: false`;
- existing collection status returns `has_collection: true`;
- unauthenticated access is rejected;
- successful import returns counters;
- duplicate import returns `409`;
- invalid file returns `400`;
- oversized file returns `413`;
- copied file cleanup happens on failure;
- `t_user.collection_file_path` is set only on success;
- `t_user_collection` associations are created without duplicating existing
  rows.

Run:

```bash
./test_backend.sh
cd frontend && npm run build
```

Rebuild Docker images when runtime backend, frontend or Nginx behavior changes.
