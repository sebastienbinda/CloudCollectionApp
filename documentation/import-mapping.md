# Import Value Mapping Rules

## Purpose

This document is the compact reference for converting values read from a user
collection file into imported domain values and persisted SQL values. Read it
before changing import fields, parsers, aliases, matching thresholds or
warnings. Detailed workflow rules remain in `documentation/import.md` and
reader architecture rules in `documentation/reader.md`.

## General Rules

- `name` and `platform` are the only mandatory game information. Platform may
  come from a column or from `sheet_information = "platform"`.
- A row without a usable game name or platform is skipped.
- Empty optional cells become `None`/SQL `NULL` without warning, including
  configured columns that are entirely empty or absent at the end of a sheet.
- Invalid non-empty optional values become `None` and are appended to
  `warnings.invalid_games`; they do not reject the game or complete import.
- Text cleaning uses `SheetValueFormatter.clean_text`: spreadsheet null/error
  values and blank text become `None`; other text is trimmed.
- Matching uses normalized lowercase, accent-free text. Matching scores are
  integer percentages from `0` to `100`; ties are rejected when uniqueness is
  required.

## Field Mapping

| Imported field | Accepted input | Persisted value | Invalid non-empty input |
| --- | --- | --- | --- |
| `name` | Non-empty text | Trimmed game name | Row skipped |
| `platform` | Non-empty column value or sheet name | Matched platform reference | Row skipped when empty; low platform score skips the game |
| `studio` | Text | Matched studio reference or `NULL` | `NULL` |
| `release_date` | Parseable date, year `>= 1950` | SQL date or `NULL` | `NULL` + warning |
| `purchase_price` | Number from `0` to `9999999999.99` using `,` or `.` | `NUMERIC(12,2)`; extra digits truncated downward (`2,259` → `2.25`) | `NULL` + warning |
| `price_unit` | File-level `EUR`, `USD`, `GBP`, `JPY`, `AUD`, `CAD`, `CHF`, `CNY`, `KRW` | Same ISO code when price is valid, otherwise `NULL` | Configuration rejected |
| `buy_location` | Text | Trimmed text or `NULL` | — |
| `buy_date` | Parseable date | SQL date or `NULL` | `NULL` + warning |
| `grade` | Text | Trimmed text or `NULL` | — |
| `condition` | French/English physical-condition label | `0` Mauvais, `1` Correct, `2` Bon, `3` Très bon, `4` Neuf | `NULL` + warning |
| `has_manual`, `is_collector`, `has_steelbook`, `is_digital` | Native boolean or mapped text | SQL boolean or `NULL` | `NULL` + warning |
| `region` | Controlled code, exact alias or unique fuzzy match | Controlled region code or `NULL` | `NULL` + warning |
| `description` | Text | Trimmed text or `NULL` | — |

## Names and Platform References

- Stored imported names are trimmed and preserve their original case and
  accents. Comparison keys are trimmed, lowercased and accent-free.
- Games are deduplicated by normalized `(platform, name)`; the first retained
  row wins unless a wishlist duplicate rule applies.
- Platforms are scored first against canonical catalog names. When the direct
  score is below `MATCHING_HIGH_LEVEL_RATING`, catalog aliases are evaluated
  and used only when they improve the score.
- A unique platform score at or above `MATCHING_HIGH_LEVEL_RATING` is accepted;
  a score from `MATCHING_LOW_LVL_RATING` up to the high threshold is accepted
  with a manual-check warning; a lower or ambiguous score skips affected games.
- Studios use their normalized name. Existing studios are reused and missing
  non-empty studios are created.

## Boolean Mapping

- True labels: `oui`, `o`, `yes`, `y`, `true`, `vrai`, `1`, `x`, `✓`,
  `present`, `avec`.
- False labels: `non`, `n`, `no`, `false`, `faux`, `0`, `absent`, `sans`.
- Case, accents and spaces are ignored.
- An exact normalized match wins. Otherwise the unique best true/false match is
  accepted at score `>= 75`; examples: `Ouii` → `true`, `No n` → `false`.
- An ambiguous result, a score below `75`, or a non-text/non-boolean value is
  invalid.

## Condition Mapping

- Labels and aliases are defined by `CONDITION_LABELS_BY_VALUE`.
- The unique best condition is accepted at `ETAT_MATCH_LIMIT` (default `60`).
- `used` and `occasion` map to `Correct` (`1`).
- Content descriptions `complet`, `complete`, `loose`, `loos`, `CIB` and
  `complete in box` are explicitly invalid as condition values.

## Region Mapping

- Persisted codes: `JAP`, `US`, `EU-FR`, `EU-UK`, `EU-DE`, `EU-ES`, `EU-IT`,
  `AU`, `ASIA`, `KOR`, `TWN`, `HK`, `CHN`.
- Exact aliases run before fuzzy matching:
  `FR` → `EU-FR`, `UK` → `EU-UK`, `DE` → `EU-DE`, `ES` → `EU-ES`,
  `IT` → `EU-IT`.
- Otherwise the unique best normalized code is accepted at
  `REGION_MATCH_LIMIT` (default `60`).

## Wishlist Mapping

- `mode=none`: every imported row gets `wishlist=false`.
- `mode=sheet`: valid rows from the dedicated sheet get `wishlist=true`.
- `mode=column`: accepted pairs are `Oui/Non`, `O/N`, `True/False`, `Yes/No`
  and `Y/N`, case-insensitively. Empty means `false`.
- An invalid non-empty wishlist value skips that row and increments
  `warnings.invalid_wishlist`.
- When the same game is both owned and wished, owned (`false`) wins, except the
  documented column-mode duplicate policy keeps `true` between duplicate rows.

## Reference Implementation

Do not duplicate mapping tables. Update the implementation, tests and this
document together:

- private fields and aliases:
  `backend/services/collection/imports/collection_private_information_contract.py`;
- reusable value mapping, including private fields and release dates:
  `backend/services/collection/imports/collection_import_value_mapper.py`;
- matching threshold configuration:
  `backend/services/collection/imports/region_matching_configuration.py` and
  `condition_matching_configuration.py`;
- wishlist parsing and duplicates:
  `backend/services/collection/imports/wishlist_value_parser.py` and
  `wishlist_duplicate_policy.py`;
- names and matching scores: `backend/services/users/user_collection_name_normalizer.py`
  and `backend/services/matching/`;
- platform matching: `backend/services/database/platform_matching_service.py`
  and `platform_matching_configuration.py`;
- release-date validation:
  `backend/services/collection/imports/collection_import_date_validator.py`;
- regression tests: `backend/tests/test_collection_import_value_mapper.py`
  and the ODS import reader test modules.
