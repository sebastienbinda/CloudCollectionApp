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
from typing import Any, Optional

import pandas as pd

from services.collection.imports import (
    CollectionImportField,
    CollectionImportGame,
    CollectionImportValueMapper,
    CollectionSheetLayout,
    WishlistDuplicatePolicy,
    WishlistImportMode,
)
from services.collection.imports.spreadsheet_cell_reference import (
    SpreadsheetCellReferenceParser,
)
from .ods_import_error_context import OdsImportErrorContext


class OdsCollectionImportGameBuilder:
    """Construit et dedoublonne les jeux lus dans des feuilles ODS."""

    def __init__(
        self,
        cell_reference_parser: SpreadsheetCellReferenceParser,
        error_context: OdsImportErrorContext,
        logger: logging.Logger,
        wishlist_duplicate_policy: WishlistDuplicatePolicy,
        value_mapper: CollectionImportValueMapper | None = None,
        validation_error_class: type[Exception] | None = None,
    ):
        """Initialise le constructeur de jeux importes.

        Args:
            cell_reference_parser (SpreadsheetCellReferenceParser): Parser tableur.
            error_context (OdsImportErrorContext): Contexte d'erreurs ODS.
            logger (logging.Logger): Logger applicatif.
            wishlist_duplicate_policy (WishlistDuplicatePolicy): Politique doublons.
            value_mapper (CollectionImportValueMapper | None): Mapper de valeurs generique.
            validation_error_class (type[Exception] | None): Erreur de validation a lever.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.cell_reference_parser = cell_reference_parser
        self.error_context = error_context
        self.logger = logger
        self.wishlist_duplicate_policy = wishlist_duplicate_policy
        self.value_mapper = value_mapper or CollectionImportValueMapper(logger=self.logger)
        self.validation_error_class = validation_error_class

    def build_games(
        self,
        sheet_name: str,
        dataframe: pd.DataFrame,
        layout: CollectionSheetLayout,
        sheet_information: Optional[CollectionImportField],
        wishlist_mode: WishlistImportMode,
        warnings: dict[str, Any],
        forced_wishlist: Optional[bool],
        price_unit: str | None = None,
        rating_base: int | None = None,
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
            price_unit (str | None): Unite globale du prix d'achat.
            rating_base (int | None): Base globale de notation.

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
                    price_unit,
                    rating_base,
                )
                if game is not None:
                    games.append(game)
            except Exception as exc:
                if self.validation_error_class is None:
                    from .ods_collection_import_reader import OdsCollectionImportValidationError

                    self.validation_error_class = OdsCollectionImportValidationError

                raise self.validation_error_class(
                    self.error_context.row_message(sheet_name, row_number, layout)
                ) from exc
        return games

    def merge_games(
        self,
        games: list[CollectionImportGame],
        game_indexes_by_key: dict[tuple[str, str, str], int],
        candidates: list[CollectionImportGame],
        wishlist_mode: WishlistImportMode,
    ) -> None:
        """Fusionne des jeux candidats selon les regles de doublons.

        Args:
            games (list[CollectionImportGame]): Jeux deja retenus.
            game_indexes_by_key (dict[tuple[str, str, str], int]): Index par cle jeu.
            candidates (list[CollectionImportGame]): Jeux candidats.
            wishlist_mode (WishlistImportMode): Mode wishlist courant.

        Returns:
            None: La liste `games` est modifiee.
        """

        for candidate in candidates:
            game_key = self.value_mapper.comparison_key(candidate.name)
            platform_key = self.value_mapper.comparison_key(candidate.platform_name)
            if game_key is None or platform_key is None:
                continue
            deduplication_key = (
                platform_key,
                game_key,
                self._deduplication_region_key(candidate.region),
            )
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

    def _deduplication_region_key(self, region: str | None) -> str:
        """Construit la partie region de la cle de deduplication.

        Args:
            region (str | None): Region importee et normalisee.

        Returns:
            str: Cle region stable, `EU-FR` quand absente.
        """

        normalized_region = "" if region is None else str(region).strip()
        return normalized_region or "EU-FR"

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
        price_unit: str | None,
        rating_base: int | None,
    ) -> Optional[CollectionImportGame]:
        game_name = self.value_mapper.map_name(
            self._field_value(row, column_positions, CollectionImportField.NAME)
        )
        game_key = self.value_mapper.comparison_key(game_name)
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
        wishlist = self.value_mapper.map_wishlist(
            self._field_value(row, column_positions, CollectionImportField.WISHLIST),
            wishlist_mode,
            forced_wishlist,
            game_name,
            warnings,
            source_context=f"onglet={sheet_name}, ligne={row_number}",
        )
        if wishlist is None:
            return None
        private_values = {
            field: self._field_value(row, column_positions, field)
            for field in CollectionImportField
        }
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
            release_date=self.value_mapper.map_release_date(
                self._field_value(row, column_positions, CollectionImportField.RELEASE_DATE),
                game_name,
                warnings,
                source_context=f"plateforme={platform_name}, ligne={row_number}",
            ),
            wishlist=wishlist,
            **self.value_mapper.map_private_values(
                private_values,
                game_name,
                warnings,
                price_unit,
                rating_base,
            ),
        )

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
        return self.value_mapper.map_name(value)
