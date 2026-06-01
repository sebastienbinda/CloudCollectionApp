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
from datetime import date, datetime
from typing import Any, Callable, Optional

import pandas as pd

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
    CollectionMultipleSheetsConfiguration,
    CollectionSheetLayout,
)
from services.collection.imports.spreadsheet_cell_reference import (
    SpreadsheetCellReferenceParser,
)
from services.formatting import SheetValueFormatter
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer

from .ods_cache import OdsCache
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
        name_normalizer: Optional[UserCollectionNameNormalizer] = None,
        cell_reference_parser: Optional[SpreadsheetCellReferenceParser] = None,
        error_context: Optional[OdsImportErrorContext] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialise le lecteur d'import de collection ODS.

        Args:
            reader_factory (Optional[Callable[[str], OdsReader]]): Fabrique de lecteur ODS.
            name_normalizer (Optional[UserCollectionNameNormalizer]): Normaliseur metier.
            cell_reference_parser (Optional[SpreadsheetCellReferenceParser]): Parser tableur.
            error_context (Optional[OdsImportErrorContext]): Contexte d'erreurs.
            logger (Optional[logging.Logger]): Logger utilise pour les avertissements.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.reader_factory = reader_factory or self._create_ods_reader
        self.name_normalizer = name_normalizer or UserCollectionNameNormalizer()
        self.cell_reference_parser = cell_reference_parser or SpreadsheetCellReferenceParser()
        self.error_context = error_context or OdsImportErrorContext()
        self.logger = logger or logging.getLogger(__name__)

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
            games = self._read_configured_games(reader, description)
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
    ) -> list[CollectionImportGame]:
        sheet_names = reader.list_sheets()
        if not sheet_names:
            raise OdsCollectionImportValidationError("Le fichier ODS ne contient aucun onglet.")
        seen_game_keys: set[tuple[str, str]] = set()
        if description.single_sheet_conf is not None:
            return self._read_layout_games(
                reader,
                sheet_names[0],
                description.single_sheet_conf,
                None,
                seen_game_keys,
            )
        return self._read_multiple_sheets_games(
            reader,
            description.multiple_sheets_conf,
            sheet_names,
            seen_game_keys,
        )

    def _read_multiple_sheets_games(
        self,
        reader: OdsReader,
        configuration: CollectionMultipleSheetsConfiguration,
        available_sheet_names: list[str],
        seen_game_keys: set[tuple[str, str]],
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
                        seen_game_keys,
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
                    seen_game_keys,
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
        seen_game_keys: set[tuple[str, str]],
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
        return self._build_games(
            sheet_name,
            dataframe,
            layout,
            sheet_information,
            seen_game_keys,
        )

    def _build_games(
        self,
        sheet_name: str,
        dataframe: pd.DataFrame,
        layout: CollectionSheetLayout,
        sheet_information: Optional[CollectionImportField],
        seen_game_keys: set[tuple[str, str]],
    ) -> list[CollectionImportGame]:
        """Construit les jeux importables d'une feuille.

        Args:
            sheet_name (str): Nom de l'onglet plateforme.
            dataframe (pandas.DataFrame): Donnees lues depuis l'onglet.
            layout (CollectionSheetLayout): Layout configure.
            sheet_information (Optional[CollectionImportField]): Champ porte par l'onglet.
            seen_game_keys (set[tuple[str, str]]): Jeux deja conserves par plateforme.

        Returns:
            list[CollectionImportGame]: Jeux avec nom non vide.
        """

        games: list[CollectionImportGame] = []
        column_positions = self._column_positions(layout)
        for row_index, row in dataframe.iterrows():
            row_number = self.error_context.spreadsheet_row_number(layout, row_index)
            try:
                game_name = self.name_normalizer.stored_value(
                    self._field_value(row, column_positions, CollectionImportField.NAME)
                )
                game_key = self.name_normalizer.comparison_key(game_name)
                if not game_name or game_key is None:
                    continue
                platform_name = self._normalized_field_value(
                    row,
                    column_positions,
                    CollectionImportField.PLATFORM,
                    sheet_information,
                    sheet_name,
                )
                if platform_name is None:
                    continue
                deduplication_key = (platform_name, game_key)
                if deduplication_key in seen_game_keys:
                    self.logger.warning(
                        "Jeu duplique ignore: plateforme=%s, jeu=%s",
                        sheet_name,
                        game_name,
                    )
                    continue
                seen_game_keys.add(deduplication_key)
                studio_name = self._normalized_field_value(
                    row,
                    column_positions,
                    CollectionImportField.STUDIO,
                    sheet_information,
                    sheet_name,
                )
                games.append(
                    CollectionImportGame(
                        name=game_name,
                        platform_name=platform_name,
                        studio_name=studio_name,
                        release_date=self._parse_release_date(
                            platform_name,
                            game_name,
                            self._field_value(
                                row,
                                column_positions,
                                CollectionImportField.RELEASE_DATE,
                            ),
                            row_number,
                        ),
                    )
                )
            except Exception as exc:
                raise OdsCollectionImportValidationError(
                    self.error_context.row_message(sheet_name, row_number, layout)
                ) from exc
        return games

    def _column_positions(self, layout: CollectionSheetLayout) -> dict[CollectionImportField, int]:
        selected_columns = self._selected_columns(layout)
        return {
            field: selected_columns.index(column_name)
            for field, column_name in layout.column_information.items()
        }

    def _configured_columns(self, layout: CollectionSheetLayout) -> str:
        return ",".join(self._selected_columns(layout))

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
        """Convertit la date de sortie d'une ligne ODS.

        Args:
            platform_name (str): Nom de l'onglet plateforme.
            game_name (str): Nom du jeu lu.
            value (Any): Valeur brute de date de sortie.
            row_number (int): Numero de ligne logique dans le DataFrame.

        Returns:
            Optional[date]: Date valide ou `None`.
        """

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
            studio_key = self.name_normalizer.comparison_key(game.studio_name)
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
            platform_key = self.name_normalizer.comparison_key(game.platform_name)
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
            reader.cache.reset()
