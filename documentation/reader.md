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

- expose `accepted_extensions`, for example `(".ods",)`;
- implement `analyze_sheets(file_path)` and return available sheet names;
- implement `read(file_path, description)` and return `CollectionImportData`;
- raise `CollectionFileReadError` for unreadable files;
- raise `CollectionFileValidationError` or a compatible domain validation error
  for structurally invalid content;
- stay format-specific: parsing belongs in the reader, persistence and user
  workflow orchestration do not.

Register new readers through `CollectionFileReaderFactory`. Do not add reader
selection logic to controllers or persistence repositories.

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
- game release dates before 1950 are invalid because they are not plausible
  video game release dates;
- duplicate games after normalized `(platform, name)` matching keep the first
  retained game unless a documented duplicate policy says otherwise.

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
./test_backend.sh
cd frontend && npm run build
```

Rebuild Docker images when runtime reader behavior changes.
