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
  to `/collection`.
- The frontend must call `GET /api/users/me/collection` to decide between those
  two paths.
- The import page only collects the user collection file and displays
  interaction state. Validation, storage, deduplication and persistence belong
  to the backend.
- Before file analysis, the import page displays only the upload control and
  file type. The detailed collection and wishlist configuration is displayed
  after `POST /api/users/import/analyze/<file_type>` succeeds.
- After a successful import, the frontend displays an import summary using the
  backend counters and offers a link to `/collection`; it must not redirect
  automatically.
- From the Configuration page, a connected `USER` with collection access can
  reinitialize the current collection. After a successful reinitialization, the
  frontend redirects to `/collection/import` so the user can import a new file.

## Backend API Contract

- `GET /api/users/me/collection` returns only:

```json
{
  "has_collection": true
}
```

- `POST /api/users/import/file/<file_type>` must use `multipart/form-data` with
  field `collection_file` and stores `/users/workspace/<user_id>/current-import.<extension>`.
- `POST /api/users/import/analyze/<file_type>` reads the temporary file and
  returns its sheet names.
- `POST /api/users/import` must use `application/json` and receives only the
  import configuration, including a mandatory top-level `wishlist` section.
- `POST /api/users/collection/reinit` reinitializes only the connected user's
  collection and returns `{"reinitialized": true}` on success.
- Both routes require a Bearer token with at least profile `USER`.
- The connected user must always be derived from the Bearer token. Do not accept
  a user id from the request payload, URL or query string.
- A second import for a user whose `collection_file_path` is already set must
  return `409`.
- Missing temporary import files must return `404` from analyze and final import.
- Invalid or unreadable input for the requested `file_type` must return `400`.
- Temporary files that do not match the analyzed `file_type` must return `422`
  from analyze.
- Oversized upload or multipart body must return `413`.
- Unexpected failures must return `500` without leaking internal paths, SQL or
  stack traces.
- Reinitialization must return `404` when the connected user has no collection
  to reinitialize and `500` for unexpected failures.

## Persistence Rules

- Import must be atomic: all database changes succeed together or none are kept.
- `t_user.collection_file_path` must be updated only after the import data has
  been successfully persisted.
- The temporary staged file can be overwritten before final import.
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
- `t_user_collection.wishlist` is persisted for every inserted association:
  `false` means an owned collection entry and `true` means a wishlist entry.
- Reinitialization deletes only the connected user's `t_user_collection` rows,
  clears `t_user.collection_file_path`, clears
  `t_user.collection_file_description`, and deletes the stored collection file
  when it exists.
- A missing stored collection file on disk must not block reinitialization; the
  database state is still cleaned.

## ODS Import Rules

- Only configured sheets are imported.
- In shared-layout multi-sheet imports, `included_sheets` imports only selected
  sheets and `excluded_sheets` imports every sheet except selected sheets.
- `included_sheets` and `excluded_sheets` are exclusive.
- Technical sheets such as `Accueil` and `Liste de souhaits` must be ignored
  only when the import configuration excludes them.
- Platforms are matched by normalized platform name.
- Studios are matched by normalized studio name.
- Games are matched by normalized game name and platform.
- Duplicate ODS entries after normalization keep the first occurrence and ignore
  later duplicates with warning-level logging.
- Empty or invalid game release dates must be persisted as `NULL`, not as
  invalid text values.
- The editor field remains empty until a dedicated rule is specified.

## Wishlist Import Rules

- The import payload must include `wishlist.mode`.
- `wishlist.mode = "none"` means every imported row is persisted with
  `wishlist=false`.
- `wishlist.mode = "sheet"` reads a dedicated sheet with its own `sheet_name`,
  `data_range`, `header_row` and `column_information`; every valid row from
  that sheet is imported with `wishlist=true`.
- `wishlist.mode = "column"` reads a `wishlist` column from every collection
  layout.
- Accepted wishlist column values are `Oui/Non`, `O/N`, `True/False`,
  `Yes/No` and `Y/N`, case-insensitively.
- An empty wishlist value in column mode is treated as `wishlist=false`.
- An invalid wishlist value in column mode does not roll back the import; the
  row is ignored, a warning is logged, and the import response exposes the
  warning count and distinct invalid values.
- If the same game appears both in the collection and in a dedicated wishlist
  sheet, the collection value wins and the final association is
  `wishlist=false`.
- If duplicate rows appear inside wishlist input, the first normalized game is
  kept.
- If duplicate rows in column mode contain `wishlist=true` and `wishlist=false`,
  the final retained row is `wishlist=true`.

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
  `Content-Type` header on `POST /api/users/import/file/<file_type>`.
- Analyze the uploaded temporary file before final import and use the returned
  sheet names to prefill single-sheet or multi-sheet configuration.
- Prefill `header_row` from the first row of the selected data range and prefill
  mapping columns from the range columns in order.
- Send the final import configuration as JSON to `POST /api/users/import`.
- Display the successful import summary and let the user open `/collection`
  explicitly instead of redirecting immediately.
- Keep the reinitialization action in the Configuration page for non-`ADMIN`
  collection users. The action must confirm before calling the backend, use a
  dedicated hook under `frontend/src/hooks/collection/`, and redirect to
  `/collection/import` after success.
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
- successful import returns `wishlisted_games` and `warnings`;
- duplicate import returns `409`;
- invalid file returns `400`;
- oversized file returns `413`;
- copied file cleanup happens on failure;
- `t_user.collection_file_path` is set only on success;
- `t_user_collection` associations are created without duplicating existing
  rows.
- successful reinitialization clears user associations and collection metadata;
- missing collection reinitialization returns `404`;
- missing stored collection file does not prevent reinitialization.

Run:

```bash
./test_backend.sh
cd frontend && npm run build
```

Rebuild Docker images when runtime backend, frontend or Nginx behavior changes.
