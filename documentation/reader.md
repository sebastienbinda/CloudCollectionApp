# Collection Reader Rules

## Purpose

This document defines how to implement a collection file reader. It is short on
purpose so agents can load it before creating or changing a reader without
bringing the whole import workflow into context.

Detailed import workflow rules remain in `documentation/import.md`, API
response contracts in `documentation/backend-api.md`, and backend layering rules
in `documentation/backend-arch.md`.

## Reader Contract

A reader for a file type must implement `CollectionFileReader` from
`backend/services/collection/imports/collection_file_reader.py`.

Required behavior:

- expose `accepted_extensions`, for example `(".ods",)` or `(".csv",)`;
- implement `analyze_sheets(file_path)` and return available sheet names for
  spreadsheet files; single-table formats such as CSV may return available
  column names through the same method so the shared workflow can prefill the
  mapping UI;
- implement `read(file_path, description)` and return `CollectionImportData`;
- raise `CollectionFileReadError` for unreadable files;
- raise `CollectionFileValidationError` or a compatible domain validation error
  for structurally invalid content;
- stay format-specific: parsing belongs in the reader, persistence and user
  workflow orchestration do not.
- limit format-specific readers to file extraction and row/column addressing;
  delegate reusable value conversion to `CollectionImportValueMapper` from
  `backend/services/collection/imports/`.

Register new readers through `CollectionFileReaderFactory`. Do not add reader
selection logic to controllers or persistence repositories.

## Supported Reader Shapes

ODS readers use `single_sheet_conf` or `multiple_sheets_conf` and map fields
with spreadsheet column letters in `column_information`.

CSV readers use `file_type = "csv"` and a top-level `mapping` object where each
import field maps directly to a CSV header name:

```json
{
  "file_type": "csv",
  "wishlist": {"mode": "column"},
  "mapping": {
    "name": "Jeu",
    "platform": "Console",
    "wishlist": "Souhait"
  }
}
```

CSV has no sheet concept. It must reject ODS sheet configuration and dedicated
wishlist-sheet mode. Wishlist may be absent or read from a mapped CSV column.

## Import Data Rules

Readers must return normalized domain models:

- `CollectionImportPlatform` for importable platforms;
- `CollectionImportStudio` for importable studios;
- `CollectionImportGame` for importable games;
- `CollectionImportWarnings` for non-blocking invalid information.

Game rows follow these rules:

- if the game name is null, empty, `NaT`, `NaN`, `None`, `null` or a spreadsheet
  error value, do not import the game row;
- if the game name is valid but another provided information is invalid, import
  the game and report the invalid information in `warnings.invalid_games`;
- empty optional information is not an error and must not appear in
  `warnings.invalid_games`;
- invalid optional information must be converted to `None` or a safe default
  before persistence;
- invalid or empty release dates must be returned as `None`;
- optional private fields may map purchase price, location/date, note, rating,
  condition, manual, collector, steelbook, digital version, region and
  description into `CollectionImportGame`;
- when a dedicated wishlist sheet is configured, it may map the same optional
  fields with its own `column_information`; missing wishlist mappings are not
  inferred from collection layouts;
- purchase price must be non-negative, accepts `,` or `.` as decimal separator,
  truncates additional decimal digits toward the lower value to two digits, and
  keeps the file-level ISO `price_unit` without conversion; a negative or
  non-numeric value is invalid;
- rating values keep their raw text in `grade` and normalize to
  `grade_normalized` on base 100, rounded down; plain numeric values use the
  file-level `rating_base`, while `<grade>/<base>` values use their own base;
- condition accepts `Mauvais`, `Correct`, `Bon`, `Très bon`, `Neuf` and maps
  them to integers `0` through `4`;
- invalid non-empty private values become `None` and are reported through
  `warnings.invalid_games`;
- region values are normalized and scored against the controlled region codes
  with `SequenceMatcher`; a unique score at or above `REGION_MATCH_LIMIT` is
  accepted, otherwise the value is invalid;
- condition values must be text and are scored against the confirmed French
  and English aliases for `Mauvais`, `Correct`, `Bon`, `Très bon` and `Neuf`;
  `used` and `occasion` map to `Correct`; `complet`, `complete`, `loose`,
  `loos`, `CIB` and `complete in box` are explicitly excluded; a unique score
  at or above `ETAT_MATCH_LIMIT` is accepted;
- the four private boolean fields share a normalized mapping: true for
  `oui`, `o`, `yes`, `y`, `true`, `vrai`, `1`, `x`, `✓`, `present`, `avec`;
  false for `non`, `n`, `no`, `false`, `faux`, `0`, `absent`, `sans`;
  spaces are ignored and a unique fuzzy match at or above `75` is accepted;
  native ODS booleans are accepted, empty cells stay null without warning, and
  ambiguous or unknown non-empty values stay null with an `invalid_games` warning;
- game release dates before 1950 are invalid because they are not plausible
  video game release dates;
- duplicate games after normalized `(platform, name, region)` matching keep the
  first retained game unless a documented duplicate policy says otherwise. Rows
  without a valid region use `EU-FR` for that key.

Use shared normalizers where possible:

- `SheetValueFormatter.clean_text` for empty spreadsheet values;
- `UserCollectionNameNormalizer` for stored names and comparison keys;
- existing wishlist parsers and duplicate policies for wishlist behavior.

## Invalid Game Warnings

`CollectionImportWarnings.invalid_games` reports games that were imported but
had invalid non-empty information.

Shape:

```json
[
  {
    "name": "Tomb Raider",
    "invalid_fields": [
      {
        "field": "release_date",
        "value": "48113-11-21 00:00:01"
      }
    ]
  }
]
```

Rules:

- include only games with a valid non-empty name;
- group multiple invalid fields under the same game entry;
- use stable field identifiers such as `release_date`;
- keep the original invalid value as displayable text when possible;
- do not add entries for empty values;
- do not block the import only because `invalid_games` is non-empty.

When adding validation for a new imported game field, update
`invalid_games` reporting and the frontend summary if the field should be
visible to users.

## Testing Rules

Reader changes must include backend unit tests covering:

- accepted extension routing through `CollectionFileReaderFactory`;
- sheet analysis for the file type;
- successful `CollectionImportData` mapping;
- ignored rows with invalid or empty game names;
- empty optional values not producing invalid-game warnings;
- invalid non-empty values producing `warnings.invalid_games`;
- unreadable or structurally invalid file errors;
- wishlist warnings when the reader supports wishlist input.

Run:

```bash
./scripts/test_backend.sh
cd frontend && npm run build
```

Rebuild Docker images when runtime reader behavior changes.
