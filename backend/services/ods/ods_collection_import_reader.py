#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : lecteur ODS dedie au workflow d'import de collection utilisateur.

import logging
from typing import Any, Callable, Optional

from services.collection.imports import (
    CollectionFileDescription,
    CollectionFileDescriptionValidationError,
    CollectionFileReadError,
    CollectionFileValidationError,
    CollectionImportData,
    CollectionImportField,
    CollectionImportGame,
    CollectionImportPlatform,
    CollectionImportStudio,
    CollectionImportWarnings,
    CollectionImportValueMapper,
    CollectionMultipleSheetsConfiguration,
    CollectionSheetLayout,
    WishlistDuplicatePolicy,
    WishlistImportMode,
)
from services.collection.imports.spreadsheet_cell_reference import (
    SpreadsheetCellReferenceParser,
)

from .ods_cache import OdsCache
from .ods_collection_import_game_builder import OdsCollectionImportGameBuilder
from .ods_import_error_context import OdsImportErrorContext
from .ods_reader import OdsReader


class OdsCollectionImportReadError(CollectionFileReadError):
    """Signale qu'un fichier ODS de collection ne peut pas etre lu."""


class OdsCollectionImportValidationError(CollectionFileValidationError):
    """Signale qu'un fichier ODS lu ne respecte pas le format attendu."""


class OdsCollectionImportReader:
    """Lit un fichier ODS de collection utilisateur pour le workflow d'import."""

    def __init__(
        self,
        reader_factory: Optional[Callable[[str], OdsReader]] = None,
        cell_reference_parser: Optional[SpreadsheetCellReferenceParser] = None,
        error_context: Optional[OdsImportErrorContext] = None,
        logger: Optional[logging.Logger] = None,
        wishlist_duplicate_policy: Optional[WishlistDuplicatePolicy] = None,
        value_mapper: Optional[CollectionImportValueMapper] = None,
    ):
        """Initialise le lecteur d'import de collection ODS.

        Args:
            reader_factory (Optional[Callable[[str], OdsReader]]): Fabrique de lecteur ODS.
            cell_reference_parser (Optional[SpreadsheetCellReferenceParser]): Parser tableur.
            error_context (Optional[OdsImportErrorContext]): Contexte d'erreurs.
            logger (Optional[logging.Logger]): Logger utilise pour les avertissements.
            wishlist_duplicate_policy (Optional[WishlistDuplicatePolicy]): Politique doublons.
            value_mapper (Optional[CollectionImportValueMapper]): Mapper generique injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.reader_factory = reader_factory or self._create_ods_reader
        self.cell_reference_parser = cell_reference_parser or SpreadsheetCellReferenceParser()
        self.error_context = error_context or OdsImportErrorContext()
        self.logger = logger or logging.getLogger(__name__)
        self.wishlist_duplicate_policy = wishlist_duplicate_policy or WishlistDuplicatePolicy()
        self.value_mapper = value_mapper or CollectionImportValueMapper(logger=self.logger)
        self.game_builder = OdsCollectionImportGameBuilder(
            self.cell_reference_parser,
            self.error_context,
            self.logger,
            self.wishlist_duplicate_policy,
            self.value_mapper,
        )

    @property
    def accepted_extensions(self) -> tuple[str, ...]:
        """Retourne les extensions acceptees par le reader LibreOffice ODS.

        Args:
            Aucun.

        Returns:
            tuple[str, ...]: Extensions ODS acceptees.
        """

        return (".ods",)

    def read(
        self,
        ods_path: str,
        description: CollectionFileDescription,
    ) -> CollectionImportData:
        """Lit les donnees importables d'un fichier ODS de collection.

        Args:
            ods_path (str): Chemin du fichier ODS a lire.
            description (CollectionFileDescription): Description valide du fichier.

        Returns:
            CollectionImportData: Plateformes, studios et jeux extraits.

        Raises:
            OdsCollectionImportReadError: Si le fichier ODS ne peut pas etre lu.
            OdsCollectionImportValidationError: Si le fichier ne respecte pas le format attendu.
        """

        reader = None
        try:
            reader = self.reader_factory(ods_path)
            games, warnings = self._read_configured_games(reader, description)
        except (OdsCollectionImportReadError, OdsCollectionImportValidationError):
            raise
        except CollectionFileDescriptionValidationError:
            raise
        except Exception as exc:
            raise OdsCollectionImportReadError(
                "Le fichier ODS de collection est illisible."
            ) from exc
        finally:
            self._reset_reader_cache(reader)

        return CollectionImportData(
            platforms=self._build_platforms(games),
            studios=self._build_studios(games),
            games=games,
            warnings=warnings,
        )

    def analyze_sheets(self, ods_path: str) -> list[str]:
        """Retourne les onglets disponibles dans un fichier ODS.

        Args:
            ods_path (str): Chemin du fichier ODS a analyser.

        Returns:
            list[str]: Noms d'onglets dans l'ordre du fichier.

        Raises:
            OdsCollectionImportReadError: Si le fichier ODS ne peut pas etre lu.
        """

        reader = None
        try:
            reader = self.reader_factory(ods_path)
            return reader.list_sheets()
        except Exception as exc:
            raise OdsCollectionImportReadError(
                "Le fichier ODS de collection est illisible."
            ) from exc
        finally:
            self._reset_reader_cache(reader)

    def _read_configured_games(
        self,
        reader: OdsReader,
        description: CollectionFileDescription,
    ) -> tuple[list[CollectionImportGame], CollectionImportWarnings]:
        sheet_names = reader.list_sheets()
        if not sheet_names:
            raise OdsCollectionImportValidationError("Le fichier ODS ne contient aucun onglet.")
        games: list[CollectionImportGame] = []
        game_indexes_by_key: dict[tuple[str, str, str], int] = {}
        warnings = {"invalid_wishlist": 0, "invalid_values": [], "invalid_games": []}
        if description.single_sheet_conf is not None:
            self.game_builder.merge_games(
                games,
                game_indexes_by_key,
                self._read_layout_games(
                    reader,
                    sheet_names[0],
                    description.single_sheet_conf,
                    None,
                    description.wishlist.mode,
                    warnings,
                    price_unit=description.price_unit,
                    rating_base=description.rating_base,
                ),
                description.wishlist.mode,
            )
        else:
            self.game_builder.merge_games(
                games,
                game_indexes_by_key,
                self._read_multiple_sheets_games(
                    reader,
                    description.multiple_sheets_conf,
                    sheet_names,
                    description.wishlist.mode,
                    warnings,
                    description.price_unit,
                    description.rating_base,
                ),
                description.wishlist.mode,
            )
        if description.wishlist.mode == WishlistImportMode.SHEET:
            self._ensure_sheets_exist([description.wishlist.sheet_name], sheet_names)
            self.game_builder.merge_games(
                games,
                game_indexes_by_key,
                self._read_layout_games(
                    reader,
                    description.wishlist.sheet_name,
                    description.wishlist.layout,
                    None,
                    description.wishlist.mode,
                    warnings,
                    forced_wishlist=True,
                    price_unit=description.price_unit,
                    rating_base=description.rating_base,
                ),
                description.wishlist.mode,
            )
        return games, CollectionImportWarnings(
            invalid_wishlist=warnings["invalid_wishlist"],
            invalid_wishlist_values_found=warnings["invalid_values"],
            invalid_games=warnings["invalid_games"],
        )

    def _read_multiple_sheets_games(
        self,
        reader: OdsReader,
        configuration: CollectionMultipleSheetsConfiguration,
        available_sheet_names: list[str],
        wishlist_mode: WishlistImportMode,
        warnings: dict[str, Any],
        price_unit: str | None,
        rating_base: int | None,
    ) -> list[CollectionImportGame]:
        games: list[CollectionImportGame] = []
        if configuration.shared_layout is not None:
            layout = configuration.shared_layout
            self._ensure_sheets_exist(layout.excluded_sheets or [], available_sheet_names)
            sheet_names = self._selected_shared_layout_sheets(layout, available_sheet_names)
            self._ensure_sheets_exist(sheet_names, available_sheet_names)
            for sheet_name in sheet_names:
                games.extend(
                    self._read_layout_games(
                        reader,
                        sheet_name,
                        layout,
                        configuration.sheet_information,
                        wishlist_mode,
                        warnings,
                        price_unit=price_unit,
                        rating_base=rating_base,
                    )
                )
            return games
        for sheet_configuration in configuration.sheets or []:
            self._ensure_sheets_exist([sheet_configuration.sheet_name], available_sheet_names)
            games.extend(
                self._read_layout_games(
                    reader,
                    sheet_configuration.sheet_name,
                    sheet_configuration.layout,
                    sheet_configuration.sheet_information,
                    wishlist_mode,
                    warnings,
                    price_unit=price_unit,
                    rating_base=rating_base,
                )
            )
        return games

    def _selected_shared_layout_sheets(
        self,
        layout: CollectionSheetLayout,
        available_sheet_names: list[str],
    ) -> list[str]:
        if layout.included_sheets is not None:
            return layout.included_sheets
        if layout.excluded_sheets is not None:
            excluded_sheet_names = set(layout.excluded_sheets)
            return [name for name in available_sheet_names if name not in excluded_sheet_names]
        return available_sheet_names

    def _read_layout_games(
        self,
        reader: OdsReader,
        sheet_name: str,
        layout: CollectionSheetLayout,
        sheet_information: Optional[CollectionImportField],
        wishlist_mode: WishlistImportMode,
        warnings: dict[str, Any],
        forced_wishlist: Optional[bool] = None,
        price_unit: str | None = None,
        rating_base: int | None = None,
    ) -> list[CollectionImportGame]:
        try:
            dataframe = reader.read_sheet_dataframe(
                sheet_name,
                layout.data_range,
                layout.header_row,
                self._configured_columns(layout),
            )
        except Exception as exc:
            raise OdsCollectionImportReadError(
                self.error_context.sheet_message(
                    "Lecture de l'onglet impossible",
                    sheet_name,
                    layout,
                )
            ) from exc
        return self.game_builder.build_games(
            sheet_name,
            dataframe,
            layout,
            sheet_information,
            wishlist_mode,
            warnings,
            forced_wishlist,
            price_unit,
            rating_base,
        )

    def _configured_columns(self, layout: CollectionSheetLayout) -> str:
        return ",".join(self._selected_columns(layout))

    def _selected_columns(self, layout: CollectionSheetLayout) -> list[str]:
        return sorted(
            set(layout.column_information.values()),
            key=self.cell_reference_parser.column_to_index,
        )

    def _build_studios(
        self,
        games: list[CollectionImportGame],
    ) -> list[CollectionImportStudio]:
        """Construit la liste des studios presents dans les jeux.

        Args:
            games (list[OdsCollectionImportGame]): Jeux lus depuis le fichier.

        Returns:
            list[OdsCollectionImportStudio]: Studios uniques dans l'ordre de lecture.
        """

        studios: list[CollectionImportStudio] = []
        seen_studio_keys: set[str] = set()
        for game in games:
            studio_key = self.value_mapper.comparison_key(game.studio_name)
            if game.studio_name is None or studio_key is None:
                continue
            if studio_key in seen_studio_keys:
                self.logger.warning("Studio duplique ignore: %s", game.studio_name)
                continue
            seen_studio_keys.add(studio_key)
            studios.append(CollectionImportStudio(name=game.studio_name))
        return studios

    def _build_platforms(
        self,
        games: list[CollectionImportGame],
    ) -> list[CollectionImportPlatform]:
        platforms: list[CollectionImportPlatform] = []
        seen_platform_keys: set[str] = set()
        for game in games:
            platform_key = self.value_mapper.comparison_key(game.platform_name)
            if platform_key is None or platform_key in seen_platform_keys:
                continue
            seen_platform_keys.add(platform_key)
            platforms.append(CollectionImportPlatform(name=game.platform_name))
        return platforms
    def _ensure_sheets_exist(
        self,
        expected_sheet_names: list[str],
        available_sheet_names: list[str],
    ) -> None:
        missing_sheets = sorted(set(expected_sheet_names).difference(available_sheet_names))
        if missing_sheets:
            raise CollectionFileDescriptionValidationError(
                [f"onglet absent du fichier: {sheet_name}." for sheet_name in missing_sheets]
            )
    def _create_ods_reader(self, ods_path: str) -> OdsReader:
        cache = OdsCache(ods_path)
        return OdsReader(ods_path, cache)

    def _reset_reader_cache(self, reader: Optional[OdsReader]) -> None:
        if reader is not None and hasattr(reader, "cache"):
            close = getattr(reader, "close", None)
            if callable(close):
                close()
            reader.cache.reset()
