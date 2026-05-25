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

from services.formatting import SheetValueFormatter
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer

from .ods_archive_reader import OdsArchiveReader
from .ods_cache import OdsCache
from .ods_collection_import_models import (
    OdsCollectionImportData,
    OdsCollectionImportGame,
    OdsCollectionImportPlatform,
    OdsCollectionImportStudio,
)
from .ods_image_reader import OdsImageReader
from .ods_reader import OdsReader
from .ods_xml_reader import OdsXmlReader


class OdsCollectionImportReadError(ValueError):
    """Signale qu'un fichier ODS de collection ne peut pas etre lu."""


class OdsCollectionImportValidationError(ValueError):
    """Signale qu'un fichier ODS lu ne respecte pas le format attendu."""


class OdsCollectionImportReader:
    """Lit un fichier ODS de collection utilisateur pour le workflow d'import.

    Le service transforme les onglets plateforme en modeles metier et laisse la
    persistance a la couche d'import applicative.
    """

    EXCLUDED_SHEET_NAMES = {"Accueil", "Liste de souhaits"}
    REQUIRED_GAME_COLUMNS = {"Nom du jeu", "Studio", "Date de sortie"}

    def __init__(
        self,
        reader_factory: Optional[Callable[[str], OdsReader]] = None,
        name_normalizer: Optional[UserCollectionNameNormalizer] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialise le lecteur d'import de collection ODS.

        Args:
            reader_factory (Optional[Callable[[str], OdsReader]]): Fabrique de lecteur ODS.
            name_normalizer (Optional[UserCollectionNameNormalizer]): Normaliseur metier.
            logger (Optional[logging.Logger]): Logger utilise pour les avertissements.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.reader_factory = reader_factory or self._create_ods_reader
        self.name_normalizer = name_normalizer or UserCollectionNameNormalizer()
        self.logger = logger or logging.getLogger(__name__)

    def read(self, ods_path: str) -> OdsCollectionImportData:
        """Lit les donnees importables d'un fichier ODS de collection.

        Args:
            ods_path (str): Chemin du fichier ODS a lire.

        Returns:
            OdsCollectionImportData: Plateformes, studios et jeux extraits.

        Raises:
            OdsCollectionImportReadError: Si le fichier ODS ne peut pas etre lu.
            OdsCollectionImportValidationError: Si le fichier ne respecte pas le format attendu.
        """

        reader = None
        try:
            reader = self.reader_factory(ods_path)
            platform_entries = self._list_importable_platforms(reader)
            platforms = [
                OdsCollectionImportPlatform(name=platform_name)
                for _, platform_name in platform_entries
            ]
            games = self._read_platform_games(reader, platform_entries)
        except OdsCollectionImportValidationError:
            raise
        except Exception as exc:
            raise OdsCollectionImportReadError(
                "Le fichier ODS de collection est illisible."
            ) from exc
        finally:
            self._reset_reader_cache(reader)

        return OdsCollectionImportData(
            platforms=platforms,
            studios=self._build_studios(games),
            games=games,
        )

    def _list_importable_platforms(self, reader: OdsReader) -> list[tuple[str, str]]:
        """Liste les onglets plateforme importables du fichier ODS.

        Args:
            reader (OdsReader): Lecteur ODS bas niveau.

        Returns:
            list[tuple[str, str]]: Noms d'onglets et valeurs normalisees.

        Raises:
            OdsCollectionImportValidationError: Si aucun onglet plateforme n'existe.
        """

        platform_entries: list[tuple[str, str]] = []
        seen_platform_keys: set[str] = set()
        for sheet_name in reader.list_platforms():
            if sheet_name in self.EXCLUDED_SHEET_NAMES:
                continue
            stored_platform_name = self.name_normalizer.stored_value(sheet_name)
            platform_key = self.name_normalizer.comparison_key(sheet_name)
            if stored_platform_name is None or platform_key is None:
                continue
            if platform_key in seen_platform_keys:
                self.logger.warning("Plateforme dupliquee ignoree: %s", sheet_name)
                continue
            seen_platform_keys.add(platform_key)
            platform_entries.append((sheet_name, stored_platform_name))

        if not platform_entries:
            raise OdsCollectionImportValidationError(
                "Le fichier ODS ne contient aucun onglet plateforme importable."
            )
        return platform_entries

    def _read_platform_games(
        self,
        reader: OdsReader,
        platform_entries: list[tuple[str, str]],
    ) -> list[OdsCollectionImportGame]:
        """Lit les jeux de toutes les plateformes importables.

        Args:
            reader (OdsReader): Lecteur ODS bas niveau.
            platform_entries (list[tuple[str, str]]): Onglets et noms normalises.

        Returns:
            list[OdsCollectionImportGame]: Jeux importables.

        Raises:
            OdsCollectionImportValidationError: Si une feuille n'a pas les colonnes attendues.
        """

        games: list[OdsCollectionImportGame] = []
        seen_game_keys: set[tuple[str, str]] = set()
        for sheet_name, platform_name in platform_entries:
            dataframe = reader.read_games_dataframe(sheet_name)
            self._validate_platform_columns(sheet_name, dataframe)
            games.extend(self._build_games(platform_name, sheet_name, dataframe, seen_game_keys))
        return games

    def _validate_platform_columns(self, platform_name: str, dataframe: pd.DataFrame) -> None:
        """Valide les colonnes obligatoires d'une feuille plateforme.

        Args:
            platform_name (str): Nom de l'onglet plateforme.
            dataframe (pandas.DataFrame): Donnees lues depuis l'onglet.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            OdsCollectionImportValidationError: Si des colonnes obligatoires manquent.
        """

        missing_columns = sorted(self.REQUIRED_GAME_COLUMNS.difference(dataframe.columns))
        if missing_columns:
            raise OdsCollectionImportValidationError(
                f"L'onglet plateforme '{platform_name}' ne contient pas les colonnes attendues: "
                f"{', '.join(missing_columns)}."
            )

    def _build_games(
        self,
        platform_name: str,
        sheet_name: str,
        dataframe: pd.DataFrame,
        seen_game_keys: set[tuple[str, str]],
    ) -> list[OdsCollectionImportGame]:
        """Construit les jeux importables d'une plateforme.

        Args:
            platform_name (str): Nom normalise de la plateforme.
            sheet_name (str): Nom de l'onglet plateforme.
            dataframe (pandas.DataFrame): Donnees lues depuis l'onglet.
            seen_game_keys (set[tuple[str, str]]): Jeux deja conserves par plateforme.

        Returns:
            list[OdsCollectionImportGame]: Jeux avec nom non vide.
        """

        games: list[OdsCollectionImportGame] = []
        for row_index, row in dataframe.iterrows():
            game_name = self.name_normalizer.stored_value(row.get("Nom du jeu"))
            game_key = self.name_normalizer.comparison_key(row.get("Nom du jeu"))
            if not game_name or game_key is None:
                continue
            deduplication_key = (platform_name, game_key)
            if deduplication_key in seen_game_keys:
                self.logger.warning(
                    "Jeu duplique ignore: plateforme=%s, jeu=%s",
                    sheet_name,
                    row.get("Nom du jeu"),
                )
                continue
            seen_game_keys.add(deduplication_key)
            studio_name = self.name_normalizer.stored_value(row.get("Studio"))
            games.append(
                OdsCollectionImportGame(
                    name=game_name,
                    platform_name=platform_name,
                    studio_name=studio_name,
                    release_date=self._parse_release_date(
                        platform_name,
                        game_name,
                        row.get("Date de sortie"),
                        int(row_index) + 1,
                    ),
                )
            )
        return games

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
        """Journalise une date de sortie ignoree pendant l'import.

        Args:
            platform_name (str): Nom de l'onglet plateforme.
            game_name (str): Nom du jeu lu.
            row_number (int): Numero de ligne logique dans le DataFrame.
            value (Any): Valeur brute de date de sortie.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.logger.warning(
            "Date de sortie invalide ignoree: plateforme=%s, jeu=%s, ligne=%s, valeur=%s",
            platform_name,
            game_name,
            row_number,
            value,
        )

    def _build_studios(
        self,
        games: list[OdsCollectionImportGame],
    ) -> list[OdsCollectionImportStudio]:
        """Construit la liste des studios presents dans les jeux.

        Args:
            games (list[OdsCollectionImportGame]): Jeux lus depuis le fichier.

        Returns:
            list[OdsCollectionImportStudio]: Studios uniques dans l'ordre de lecture.
        """

        studios: list[OdsCollectionImportStudio] = []
        seen_studio_keys: set[str] = set()
        for game in games:
            studio_key = self.name_normalizer.comparison_key(game.studio_name)
            if game.studio_name is None or studio_key is None:
                continue
            if studio_key in seen_studio_keys:
                self.logger.warning("Studio duplique ignore: %s", game.studio_name)
                continue
            seen_studio_keys.add(studio_key)
            studios.append(OdsCollectionImportStudio(name=game.studio_name))
        return studios

    def _create_ods_reader(self, ods_path: str) -> OdsReader:
        """Cree le lecteur ODS bas niveau partage par les workflows applicatifs.

        Args:
            ods_path (str): Chemin du fichier ODS a lire.

        Returns:
            OdsReader: Lecteur ODS configure avec cache, XML et images.
        """

        cache = OdsCache(ods_path)
        archive_reader = OdsArchiveReader(ods_path, cache)
        xml_reader = OdsXmlReader(archive_reader, cache)
        image_reader = OdsImageReader(archive_reader, cache)
        return OdsReader(ods_path, cache, xml_reader, image_reader)

    def _reset_reader_cache(self, reader: Optional[OdsReader]) -> None:
        """Vide le cache du lecteur ODS d'import en fin de traitement.

        Args:
            reader (Optional[OdsReader]): Lecteur ODS utilise pour l'import.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        if reader is not None and hasattr(reader, "cache"):
            reader.cache.reset()
