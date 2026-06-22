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
- From the Configuration page, a connected `USER` with collection access can
  open `/collection/import` to add games from a new file without
  reinitializing the current collection.
- The frontend must call `GET /api/users/me/collection` to decide between those
  two paths.
- The import page only collects the user collection file and displays
  interaction state. Validation, storage, deduplication and persistence belong
  to the backend.
- Before file analysis, the import page displays only the upload control and
  file type. The detailed collection and wishlist configuration is displayed
  after `POST /api/users/import/analyze/<file_type>` succeeds.
- After file analysis, the frontend may call `GET /api/users/import/`. When a
  saved configuration exists, it asks the user to confirm reuse before applying
  it to the import form. If no saved configuration exists, the current automatic
  prefill remains unchanged.
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
- `GET /api/users/import/` returns the last saved import configuration, or
  `404` when none exists.
- `POST /api/users/import` must use `application/json` and receives only the
  import configuration, including a mandatory top-level `wishlist` section.
- The import configuration may contain a global `price_unit`. It is mandatory
  when a layout configures `purchase_price` and accepts `EUR`, `USD`, `GBP`,
  `JPY`, `AUD`, `CAD`, `CHF`, `CNY` or `KRW`.
- `POST /api/users/collection/reinit` reinitializes only the connected user's
  collection and returns `{"reinitialized": true}` on success.
- Both routes require a Bearer token with at least profile `USER`.
- The connected user must always be derived from the Bearer token. Do not accept
  a user id from the request payload, URL or query string.
- A second import for a user whose `collection_file_path` is already set must
  be accepted as an additive import. Existing rows must be reused and missing
  user-game associations must be inserted without clearing the current
  collection.
- Missing temporary import files must return `404` from analyze and final import.
- Invalid or unreadable input for the requested `file_type` must return `400`.
- Temporary files that do not match the analyzed `file_type` must return `422`
  from analyze.
- Oversized upload or multipart body must return `413`.
- Unexpected failures must return `500` without leaking internal paths, SQL or
  stack traces.
- Reinitialization must return `404` when the connected user has no collection
  to reinitialize and `500` for unexpected failures.
- While an administrator Library reset is running, the backend must reject
  `GET /api/users/import/`, `POST /api/users/import/file/<file_type>`,
  `POST /api/users/import/analyze/<file_type>`, `POST /api/users/import` and
  `POST /api/users/collection/reinit` with `403` and a clear message telling
  the user to retry later. Authentication and profile checks still run before
  this reset lock.

## Persistence Rules

- Import must be atomic: all database changes succeed together or none are kept.
- `t_user.collection_file_path` must be updated only after the import data has
  been successfully persisted. On additive import, the stored file path and
  saved import configuration are replaced only after persistence succeeds.
- The temporary staged file can be overwritten before final import.
- The stored path format is:

```text
/users/workspace/<user_id>/<user_id>-collection.ods
```

- The copied file must be removed when import parsing or persistence fails.
- The copied file must be read-only for user and group: `0440`.
- Existing platforms, studios, games and user-game associations must be reused,
  not overwritten.
- Reused user-game associations update only private values that are non-null in
  the new import. Missing optional columns never erase previously stored data.
- Each configured private field is optional: `purchase_price`, `buy_location`,
  `buy_date`, `grade`, `condition`, `has_manual`, `is_collector`,
  `has_steelbook`, `is_digital`, `region` and `description`.
- A purchase price must be non-negative. Both decimal separators `,` and `.`
  are accepted. Values with more than two decimal digits are truncated toward
  the lower value to two digits. A negative value or invalid number becomes
  `NULL` with an `invalid_games` warning and does not reject the game.
- The global `price_unit` is stored on each imported association with a valid
  purchase price; no price conversion is performed.
- `t_user_collection` rows are inserted only when missing. Existing
  `(user_id, game_id)` rows are not errors.
- `game_additional_name` is not filled by the current import workflow.
- `t_user_collection.wishlist` is persisted for every inserted association:
  `false` means an owned collection entry and `true` means a wishlist entry.
- Reinitialization deletes only the connected user's `t_user_collection` rows,
  clears `t_user.collection_file_path`, keeps
  `t_user.collection_file_description` for future import prefill, and deletes
  the stored collection file when it exists.
- A missing stored collection file on disk must not block reinitialization; the
  database state is still cleaned.
- The Library reset workflow imports stored user collection files through the
  same backend import core as the connected-user import workflow. It must differ
  only in source-file preparation: reset imports the already stored file without
  copying it again, while user import copies the staged file into the workspace.

## ODS Import Rules

- Only configured sheets are imported.
- In shared-layout multi-sheet imports, `included_sheets` imports only selected
  sheets and `excluded_sheets` imports every sheet except selected sheets.
- `included_sheets` and `excluded_sheets` are exclusive.
- Technical sheets such as `Accueil` and `Liste de souhaits` must be ignored
  only when the import configuration excludes them.
- Platforms are matched by normalized platform name.
- When the best direct platform match is below `MATCHING_HIGH_LEVEL_RATING`, the
  backend searches platform aliases from the SQL reference catalog and uses an
  alias match only when it improves the direct score.
- Matching scores range from `0` to `100`. The defaults are
  `MATCHING_LOW_LVL_RATING=25` and `MATCHING_HIGH_LEVEL_RATING=75`.
- Scores greater than or equal to `MATCHING_HIGH_LEVEL_RATING` are imported
  without manual-verification warning.
- Scores greater than or equal to `MATCHING_LOW_LVL_RATING` and lower than
  `MATCHING_HIGH_LEVEL_RATING` are imported and reported in
  `warnings.platform_matches` for administrator verification.
- Scores lower than `MATCHING_LOW_LVL_RATING`, including `0`, skip the impacted
  games and report them in `warnings.skipped_games`.
- The import warnings keep a `platform_mappings` list with the imported platform
  name, matched platform name, matching score, imported game count and alias
  usage flag for every platform read from the file.
- The import warnings keep `total_import_duration_seconds`, measured across the
  complete backend import execution after the user lock is acquired.
- At the end of each import, the backend sends exactly one administrator report
  when `ADMIN_NOTIFICATION_EMAIL` is configured, even when the import has no
  warning. The report is sent outside the reader layer and includes the import
  context, counters, validated configuration, total duration, platform mappings
  and every import warning.
- Studios are matched by normalized studio name.
- Games are matched by normalized game name and platform.
- Duplicate ODS entries after normalization keep the first occurrence and ignore
  later duplicates with warning-level logging.
- Empty or invalid game release dates must be persisted as `NULL`, not as
  invalid text values.
- Imported regions use the same normalized `SequenceMatcher` score as platform
  matching. A unique best region is accepted at or above `REGION_MATCH_LIMIT`
  (default `60`); lower scores and ambiguous ties become `NULL` and are reported
  in `warnings.invalid_games`.
- Imported condition values must be strings. They use the shared normalized
  similarity score against French labels and English aliases. A unique state is
  accepted at or above `ETAT_MATCH_LIMIT` (default `60`); lower scores,
  ambiguous ties and non-string values become `NULL` and are reported in
  `warnings.invalid_games` without rejecting the game.
- Condition aliases include the confirmed French and English physical-state
  vocabulary. `used` and `occasion` map to `Correct`. Content descriptions
  such as `complet`, `complete`, `loose`, `loos` and `CIB` are explicitly
  excluded from condition matching.
- Manual, collector, steelbook and digital columns share the documented
  French/English boolean mapping. Spaces are ignored and a unique fuzzy match
  with a score of at least `75` is accepted. Empty cells remain `NULL` silently;
  ambiguous or unknown non-empty values remain `NULL` and add an
  `invalid_games` warning without rejecting the game.
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

- Every collection or dedicated-wishlist layout must provide the game name and
  platform information. These are the only mandatory imported game fields.
- The platform may be mapped through the `platform` entry in
  `column_information` or supplied by `sheet_information = "platform"` in a
  multi-sheet layout.
- `studio`, `release_date` and every private game-information mapping are
  optional. When one of these columns is configured, an empty cell must be
  imported as `NULL` or the field's safe empty value without rejecting the row
  or the complete import.
- The frontend must identify the mandatory fields and reject an incomplete
  configuration before submission. The backend remains authoritative and must
  validate the same mandatory fields before accepting the configuration.
- `USER_COLLECTION_MAX_UPLOAD_BYTES` is the single upload size setting.
- The same value must configure Flask request size handling and the Nginx
  `client_max_body_size` used by the `web` service.
- `MATCHING_LOW_LVL_RATING` configures the minimum platform score accepted for
  import with administrator verification. Default: `25`.
- `MATCHING_HIGH_LEVEL_RATING` configures the platform score accepted without
  manual-verification warning. Default: `75`.
- `REGION_MATCH_LIMIT` configures the minimum region matching score. It must be
  an integer between `0` and `100`; its default is `60`.
- `ETAT_MATCH_LIMIT` configures the minimum condition matching score. It must
  be an integer between `0` and `100`; its default is `60`.
- Matching ratings must be numeric integers between `0` and `100`, and
  `MATCHING_LOW_LVL_RATING` must be strictly lower than
  `MATCHING_HIGH_LEVEL_RATING`.
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
- After analysis, fetch the saved import configuration and apply it only when
  the user confirms reuse.
- Prefill `header_row` from the first row of the selected data range and prefill
  mapping columns from the range columns in order.
- Send the final import configuration as JSON to `POST /api/users/import`.
- Display the successful import summary and let the user open `/collection`
  explicitly instead of redirecting immediately.
- Keep the reinitialization action in the Configuration page for non-`ADMIN`
  collection users. The action must confirm before calling the backend, use a
  dedicated hook under `frontend/src/hooks/collection/`, and redirect to
  `/collection/import` after success.
- Keep an import action in the Configuration page for non-`ADMIN` collection
  users so they can open `/collection/import` and add games from a new file
  without reinitialization.
- The import view may validate mandatory configuration fields for immediate UX
  feedback, but backend validation remains authoritative.
- Automatic backend calls must use the shared backend availability guard so a
  stopped backend cannot trigger unbounded request loops.

## Testing Rules

When changing this feature, update or run tests covering:

- missing collection status returns `has_collection: false`;
- existing collection status returns `has_collection: true`;
- unauthenticated access is rejected;
- successful import returns counters;
- successful import returns `wishlisted_games` and `warnings`;
- additive import with an existing collection succeeds and does not duplicate
  existing user-game associations;
- invalid file returns `400`;
- oversized file returns `413`;
- copied file cleanup happens on failure;
- `t_user.collection_file_path` is set only on success;
- `t_user_collection` associations are created without duplicating existing
  rows.
- successful reinitialization clears user associations and collection path while
  keeping the saved import configuration;
- missing collection reinitialization returns `404`;
- missing stored collection file does not prevent reinitialization.

Run:

```bash
./test_backend.sh
cd frontend && npm run build
```

Rebuild Docker images when runtime backend, frontend or Nginx behavior changes.
