#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-03
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : construction des jeux importes depuis un dataframe ODS.

import logging
from dataclasses import replace
from datetime import date, datetime
from typing import Any, Optional

import pandas as pd

from services.collection.imports import (
    CollectionImportField,
    CollectionImportGame,
    CollectionSheetLayout,
    WishlistDuplicatePolicy,
    WishlistImportMode,
    WishlistValueParser,
)
from services.collection.imports.spreadsheet_cell_reference import (
    SpreadsheetCellReferenceParser,
)
from services.formatting import SheetValueFormatter
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer

from .ods_import_error_context import OdsImportErrorContext


class OdsCollectionImportGameBuilder:
    """Construit et dedoublonne les jeux lus dans des feuilles ODS."""

    def __init__(
        self,
        name_normalizer: UserCollectionNameNormalizer,
        cell_reference_parser: SpreadsheetCellReferenceParser,
        error_context: OdsImportErrorContext,
        logger: logging.Logger,
        wishlist_value_parser: WishlistValueParser,
        wishlist_duplicate_policy: WishlistDuplicatePolicy,
    ):
        """Initialise le constructeur de jeux importes.

        Args:
            name_normalizer (UserCollectionNameNormalizer): Normaliseur de noms.
            cell_reference_parser (SpreadsheetCellReferenceParser): Parser tableur.
            error_context (OdsImportErrorContext): Contexte d'erreurs ODS.
            logger (logging.Logger): Logger applicatif.
            wishlist_value_parser (WishlistValueParser): Parser wishlist.
            wishlist_duplicate_policy (WishlistDuplicatePolicy): Politique doublons.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.name_normalizer = name_normalizer
        self.cell_reference_parser = cell_reference_parser
        self.error_context = error_context
        self.logger = logger
        self.wishlist_value_parser = wishlist_value_parser
        self.wishlist_duplicate_policy = wishlist_duplicate_policy

    def build_games(
        self,
        sheet_name: str,
        dataframe: pd.DataFrame,
        layout: CollectionSheetLayout,
        sheet_information: Optional[CollectionImportField],
        wishlist_mode: WishlistImportMode,
        warnings: dict[str, Any],
        forced_wishlist: Optional[bool],
    ) -> list[CollectionImportGame]:
        """Construit les jeux valides d'une feuille.

        Args:
            sheet_name (str): Nom de l'onglet lu.
            dataframe (pd.DataFrame): Donnees de la feuille.
            layout (CollectionSheetLayout): Layout configure.
            sheet_information (Optional[CollectionImportField]): Champ porte par l'onglet.
            wishlist_mode (WishlistImportMode): Mode wishlist courant.
            warnings (dict[str, Any]): Warnings a enrichir.
            forced_wishlist (Optional[bool]): Valeur wishlist forcee.

        Returns:
            list[CollectionImportGame]: Jeux importables.
        """

        games: list[CollectionImportGame] = []
        column_positions = self._column_positions(layout)
        for row_index, row in dataframe.iterrows():
            row_number = self.error_context.spreadsheet_row_number(layout, row_index)
            try:
                game = self._build_game(
                    sheet_name,
                    row,
                    row_number,
                    column_positions,
                    sheet_information,
                    wishlist_mode,
                    warnings,
                    forced_wishlist,
                )
                if game is not None:
                    games.append(game)
            except Exception as exc:
                from .ods_collection_import_reader import OdsCollectionImportValidationError

                raise OdsCollectionImportValidationError(
                    self.error_context.row_message(sheet_name, row_number, layout)
                ) from exc
        return games

    def merge_games(
        self,
        games: list[CollectionImportGame],
        game_indexes_by_key: dict[tuple[str, str], int],
        candidates: list[CollectionImportGame],
        wishlist_mode: WishlistImportMode,
    ) -> None:
        """Fusionne des jeux candidats selon les regles de doublons.

        Args:
            games (list[CollectionImportGame]): Jeux deja retenus.
            game_indexes_by_key (dict[tuple[str, str], int]): Index par cle jeu.
            candidates (list[CollectionImportGame]): Jeux candidats.
            wishlist_mode (WishlistImportMode): Mode wishlist courant.

        Returns:
            None: La liste `games` est modifiee.
        """

        for candidate in candidates:
            game_key = self.name_normalizer.comparison_key(candidate.name)
            platform_key = self.name_normalizer.comparison_key(candidate.platform_name)
            if game_key is None or platform_key is None:
                continue
            deduplication_key = (platform_key, game_key)
            existing_index = game_indexes_by_key.get(deduplication_key)
            if existing_index is None:
                game_indexes_by_key[deduplication_key] = len(games)
                games.append(candidate)
                continue
            existing = games[existing_index]
            wishlist = self.wishlist_duplicate_policy.resolve_wishlist_value(
                wishlist_mode,
                existing.wishlist,
                candidate.wishlist,
            )
            games[existing_index] = replace(existing, wishlist=wishlist)
            self.logger.warning(
                "Jeu duplique ignore: plateforme=%s, jeu=%s",
                candidate.platform_name,
                candidate.name,
            )

    def _build_game(
        self,
        sheet_name: str,
        row,
        row_number: int,
        column_positions: dict[CollectionImportField, int],
        sheet_information: Optional[CollectionImportField],
        wishlist_mode: WishlistImportMode,
        warnings: dict[str, Any],
        forced_wishlist: Optional[bool],
    ) -> Optional[CollectionImportGame]:
        game_name = self.name_normalizer.stored_value(
            self._field_value(row, column_positions, CollectionImportField.NAME)
        )
        game_key = self.name_normalizer.comparison_key(game_name)
        if not game_name or game_key is None:
            return None
        platform_name = self._normalized_field_value(
            row,
            column_positions,
            CollectionImportField.PLATFORM,
            sheet_information,
            sheet_name,
        )
        if platform_name is None:
            return None
        wishlist = self._row_wishlist_value(
            row,
            column_positions,
            wishlist_mode,
            forced_wishlist,
            sheet_name,
            game_name,
            row_number,
            warnings,
        )
        if wishlist is None:
            return None
        return CollectionImportGame(
            name=game_name,
            platform_name=platform_name,
            studio_name=self._normalized_field_value(
                row,
                column_positions,
                CollectionImportField.STUDIO,
                sheet_information,
                sheet_name,
            ),
            release_date=self._parse_release_date(
                platform_name,
                game_name,
                self._field_value(row, column_positions, CollectionImportField.RELEASE_DATE),
                row_number,
            ),
            wishlist=wishlist,
        )

    def _row_wishlist_value(
        self,
        row,
        column_positions: dict[CollectionImportField, int],
        wishlist_mode: WishlistImportMode,
        forced_wishlist: Optional[bool],
        sheet_name: str,
        game_name: str,
        row_number: int,
        warnings: dict[str, Any],
    ) -> Optional[bool]:
        if forced_wishlist is not None:
            return forced_wishlist
        if wishlist_mode != WishlistImportMode.COLUMN:
            return False
        result = self.wishlist_value_parser.parse(
            self._field_value(row, column_positions, CollectionImportField.WISHLIST)
        )
        if result.is_valid:
            return result.value
        warnings["invalid_wishlist"] += 1
        if result.invalid_value not in warnings["invalid_values"]:
            warnings["invalid_values"].append(result.invalid_value)
        self.logger.warning(
            "Valeur wishlist invalide ignoree: onglet=%s, jeu=%s, ligne=%s, valeur=%s",
            sheet_name,
            game_name,
            row_number,
            result.invalid_value,
        )
        return None

    def _column_positions(self, layout: CollectionSheetLayout) -> dict[CollectionImportField, int]:
        selected_columns = self._selected_columns(layout)
        return {
            field: selected_columns.index(column_name)
            for field, column_name in layout.column_information.items()
        }

    def _selected_columns(self, layout: CollectionSheetLayout) -> list[str]:
        return sorted(
            set(layout.column_information.values()),
            key=self.cell_reference_parser.column_to_index,
        )

    def _field_value(
        self,
        row,
        column_positions: dict[CollectionImportField, int],
        field: CollectionImportField,
    ) -> Any:
        position = column_positions.get(field)
        if position is None or position >= len(row):
            return None
        return row.iloc[position]

    def _normalized_field_value(
        self,
        row,
        column_positions: dict[CollectionImportField, int],
        field: CollectionImportField,
        sheet_information: Optional[CollectionImportField],
        sheet_name: str,
    ) -> Optional[str]:
        value = sheet_name if sheet_information == field else self._field_value(
            row,
            column_positions,
            field,
        )
        return self.name_normalizer.stored_value(value)

    def _parse_release_date(
        self,
        platform_name: str,
        game_name: str,
        value: Any,
        row_number: int,
    ) -> Optional[date]:
        if value is None or SheetValueFormatter.clean_text(value) is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        try:
            parsed_value = pd.to_datetime(value, errors="coerce")
        except (OverflowError, ValueError, TypeError):
            self._warn_invalid_release_date(platform_name, game_name, row_number, value)
            return None
        if pd.isna(parsed_value):
            self._warn_invalid_release_date(platform_name, game_name, row_number, value)
            return None
        try:
            return parsed_value.date()
        except (OverflowError, ValueError, AttributeError):
            self._warn_invalid_release_date(platform_name, game_name, row_number, value)
            return None

    def _warn_invalid_release_date(
        self,
        platform_name: str,
        game_name: str,
        row_number: int,
        value: Any,
    ) -> None:
        self.logger.warning(
            "Date de sortie invalide ignoree: plateforme=%s, jeu=%s, ligne=%s, valeur=%s",
            platform_name,
            game_name,
            row_number,
            value,
        )
