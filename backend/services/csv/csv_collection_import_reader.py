#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-26
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : lecteur CSV dedie au workflow d'import de collection utilisateur.

import csv
import logging
from dataclasses import replace
from typing import Any, Iterable

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
    CollectionImportValueMapper,
    CollectionImportWarnings,
    WishlistDuplicatePolicy,
    WishlistImportMode,
)


class CsvCollectionImportReadError(CollectionFileReadError):
    """Signale qu'un fichier CSV de collection ne peut pas etre lu."""


class CsvCollectionImportValidationError(CollectionFileValidationError):
    """Signale qu'un fichier CSV lu ne respecte pas le format attendu."""


class CsvCollectionImportReader:
    """Lit un fichier CSV de collection utilisateur pour le workflow d'import."""

    def __init__(
        self,
        logger: logging.Logger | None = None,
        value_mapper: CollectionImportValueMapper | None = None,
        wishlist_duplicate_policy: WishlistDuplicatePolicy | None = None,
    ):
        """Initialise le lecteur d'import de collection CSV.

        Args:
            logger (logging.Logger | None): Logger applicatif optionnel.
            value_mapper (CollectionImportValueMapper | None): Mapper generique injectable.
            wishlist_duplicate_policy (WishlistDuplicatePolicy | None): Politique doublons.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.logger = logger or logging.getLogger(__name__)
        self.value_mapper = value_mapper or CollectionImportValueMapper(logger=self.logger)
        self.wishlist_duplicate_policy = wishlist_duplicate_policy or WishlistDuplicatePolicy()

    @property
    def accepted_extensions(self) -> tuple[str, ...]:
        """Retourne les extensions acceptees par le reader CSV.

        Args:
            Aucun.

        Returns:
            tuple[str, ...]: Extensions CSV acceptees.
        """

        return (".csv",)

    def analyze_sheets(self, file_path: str) -> list[str]:
        """Retourne les colonnes disponibles dans un fichier CSV.

        Args:
            file_path (str): Chemin du fichier CSV a analyser.

        Returns:
            list[str]: Noms de colonnes dans l'ordre du fichier.

        Raises:
            CsvCollectionImportReadError: Si le fichier CSV ne peut pas etre lu.
            CsvCollectionImportValidationError: Si l'en-tete CSV est invalide.
        """

        try:
            return self._read_header(file_path)
        except (CsvCollectionImportReadError, CsvCollectionImportValidationError):
            raise
        except Exception as exc:
            raise CsvCollectionImportReadError(
                "Le fichier CSV de collection est illisible."
            ) from exc

    def read(
        self,
        file_path: str,
        description: CollectionFileDescription,
    ) -> CollectionImportData:
        """Lit les donnees importables d'un fichier CSV de collection.

        Args:
            file_path (str): Chemin du fichier CSV a lire.
            description (CollectionFileDescription): Description valide du fichier.

        Returns:
            CollectionImportData: Plateformes, studios et jeux extraits.

        Raises:
            CsvCollectionImportReadError: Si le fichier CSV ne peut pas etre lu.
            CsvCollectionImportValidationError: Si le fichier ne respecte pas le format attendu.
        """

        if description.csv_conf is None:
            raise CollectionFileDescriptionValidationError(["mapping est requis pour csv."])
        try:
            rows, columns = self._read_rows(file_path)
            self._ensure_configured_columns_exist(
                description.csv_conf.column_information,
                columns,
            )
            games, warnings = self._build_games(rows, description)
        except (CollectionFileDescriptionValidationError, CsvCollectionImportValidationError):
            raise
        except Exception as exc:
            raise CsvCollectionImportReadError(
                "Le fichier CSV de collection est illisible."
            ) from exc
        return CollectionImportData(
            platforms=self._build_platforms(games),
            studios=self._build_studios(games),
            games=games,
            warnings=warnings,
        )

    def _read_rows(self, file_path: str) -> tuple[list[dict[str, Any]], list[str]]:
        with open(file_path, newline="", encoding="utf-8-sig") as csv_file:
            sample = csv_file.read(4096)
            csv_file.seek(0)
            dialect = self._sniff_dialect(sample)
            reader = csv.DictReader(csv_file, dialect=dialect)
            columns = self._clean_header(reader.fieldnames)
            if len(columns) != len(set(columns)):
                raise CsvCollectionImportValidationError(
                    "Le fichier CSV contient des colonnes dupliquees."
                )
            reader.fieldnames = columns
            return list(reader), columns

    def _read_header(self, file_path: str) -> list[str]:
        _, columns = self._read_rows(file_path)
        return columns

    def _sniff_dialect(self, sample: str):
        if not sample.strip():
            raise CsvCollectionImportValidationError("Le fichier CSV est vide.")
        try:
            return csv.Sniffer().sniff(sample, delimiters=",;	")
        except csv.Error:
            return csv.excel

    def _clean_header(self, fieldnames: Iterable[str] | None) -> list[str]:
        if not fieldnames:
            raise CsvCollectionImportValidationError(
                "Le fichier CSV ne contient aucun en-tete."
            )
        columns = [str(fieldname or "").strip() for fieldname in fieldnames]
        if any(not column for column in columns):
            raise CsvCollectionImportValidationError(
                "Le fichier CSV contient une colonne sans nom."
            )
        return columns

    def _ensure_configured_columns_exist(
        self,
        column_information: dict[CollectionImportField, str],
        columns: list[str],
    ) -> None:
        available_columns = set(columns)
        missing_columns = [
            column_name
            for column_name in column_information.values()
            if column_name not in available_columns
        ]
        if missing_columns:
            raise CollectionFileDescriptionValidationError(
                [f"colonne CSV absente: {column_name}." for column_name in missing_columns]
            )

    def _build_games(
        self,
        rows: list[dict[str, Any]],
        description: CollectionFileDescription,
    ) -> tuple[list[CollectionImportGame], CollectionImportWarnings]:
        games: list[CollectionImportGame] = []
        game_indexes_by_key: dict[tuple[str, str, str], int] = {}
        warnings = {
            "invalid_wishlist": 0,
            "invalid_values": [],
            "invalid_games": [],
            "skipped_mandatory_games": 0,
        }
        for row_index, row in enumerate(rows, start=2):
            game = self._build_game(row, row_index, description, warnings)
            if game is not None:
                self._merge_game(games, game_indexes_by_key, game, description.wishlist.mode)
        return games, CollectionImportWarnings(
            invalid_wishlist=warnings["invalid_wishlist"],
            invalid_wishlist_values_found=warnings["invalid_values"],
            invalid_games=warnings["invalid_games"],
            skipped_mandatory_games=warnings["skipped_mandatory_games"],
        )

    def _build_game(
        self,
        row: dict[str, Any],
        row_index: int,
        description: CollectionFileDescription,
        warnings: dict[str, Any],
    ) -> CollectionImportGame | None:
        column_information = description.csv_conf.column_information
        game_name = self.value_mapper.map_name(
            self._field_value(row, column_information, CollectionImportField.NAME)
        )
        if not game_name or self.value_mapper.comparison_key(game_name) is None:
            warnings["skipped_mandatory_games"] += 1
            return None
        platform_name = self.value_mapper.map_name(
            self._field_value(row, column_information, CollectionImportField.PLATFORM)
        )
        if platform_name is None:
            warnings["skipped_mandatory_games"] += 1
            return None
        wishlist = self.value_mapper.map_wishlist(
            self._field_value(row, column_information, CollectionImportField.WISHLIST),
            description.wishlist.mode,
            None,
            game_name,
            warnings,
            source_context=f"ligne={row_index}",
        )
        if wishlist is None:
            return None
        private_values = {
            field: self._field_value(row, column_information, field)
            for field in CollectionImportField
        }
        return CollectionImportGame(
            name=game_name,
            platform_name=platform_name,
            studio_name=self.value_mapper.map_name(
                self._field_value(row, column_information, CollectionImportField.STUDIO)
            ),
            release_date=self.value_mapper.map_release_date(
                self._field_value(row, column_information, CollectionImportField.RELEASE_DATE),
                game_name,
                warnings,
                source_context=f"plateforme={platform_name}, ligne={row_index}",
            ),
            wishlist=wishlist,
            **self.value_mapper.map_private_values(
                private_values,
                game_name,
                warnings,
                description.price_unit,
                description.rating_base,
            ),
        )

    def _field_value(
        self,
        row: dict[str, Any],
        column_information: dict[CollectionImportField, str],
        field: CollectionImportField,
    ) -> Any:
        column_name = column_information.get(field)
        if column_name is None:
            return None
        return row.get(column_name)

    def _merge_game(
        self,
        games: list[CollectionImportGame],
        game_indexes_by_key: dict[tuple[str, str, str], int],
        candidate: CollectionImportGame,
        wishlist_mode: WishlistImportMode,
    ) -> None:
        game_key = self.value_mapper.comparison_key(candidate.name)
        platform_key = self.value_mapper.comparison_key(candidate.platform_name)
        if game_key is None or platform_key is None:
            return
        deduplication_key = (
            platform_key,
            game_key,
            self._deduplication_region_key(candidate.region),
        )
        existing_index = game_indexes_by_key.get(deduplication_key)
        if existing_index is None:
            game_indexes_by_key[deduplication_key] = len(games)
            games.append(candidate)
            return
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
        """Construit la partie region de la cle de deduplication CSV.

        Args:
            region (str | None): Region importee et normalisee.

        Returns:
            str: Cle region stable, `EU-FR` quand absente.
        """

        normalized_region = "" if region is None else str(region).strip()
        return normalized_region or "EU-FR"

    def _build_studios(
        self,
        games: list[CollectionImportGame],
    ) -> list[CollectionImportStudio]:
        studios: list[CollectionImportStudio] = []
        seen_studio_keys: set[str] = set()
        for game in games:
            studio_key = self.value_mapper.comparison_key(game.studio_name)
            if game.studio_name is None or studio_key is None or studio_key in seen_studio_keys:
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
