#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : chargement du catalogue applicatif des plateformes.

import unicodedata
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Connection
from sqlalchemy.sql import bindparam

from .platform_alias_catalog_csv_reader import PlatformAliasCatalogCsvReader
from .platform_alias_catalog_entry import PlatformAliasCatalogEntry
from .platform_catalog_csv_reader import PlatformCatalogCsvReader
from .platform_catalog_entry import PlatformCatalogEntry


class PlatformCatalogSeedService:
    """Charge le catalogue applicatif des plateformes dans PostgreSQL."""

    def __init__(
        self,
        schema_name: str,
        csv_reader: PlatformCatalogCsvReader | None = None,
        alias_csv_reader: PlatformAliasCatalogCsvReader | None = None,
    ):
        """Initialise le service de chargement du catalogue plateformes.

        Args:
            schema_name (str): Nom du schema PostgreSQL.
            csv_reader (PlatformCatalogCsvReader | None): Lecteur CSV injectable.
            alias_csv_reader (PlatformAliasCatalogCsvReader | None): Lecteur CSV alias.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name
        self.csv_reader = csv_reader or PlatformCatalogCsvReader()
        self.alias_csv_reader = alias_csv_reader or PlatformAliasCatalogCsvReader()

    def seed_from_csv(
        self,
        connection: Connection,
        csv_path: Path,
        alias_csv_path: Path | None = None,
    ) -> int:
        """Insere les plateformes et alias absents des catalogues CSV.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            csv_path (Path): Chemin du fichier CSV de reference.
            alias_csv_path (Path | None): Chemin du fichier CSV des alias.

        Returns:
            int: Nombre total de plateformes et alias inseres.

        Raises:
            ValueError: Si le CSV contient des donnees invalides.
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        inserted_count = self._seed_platforms(connection, self.csv_reader.read(csv_path))
        if alias_csv_path is None:
            return inserted_count
        return inserted_count + self._seed_aliases(
            connection,
            self.alias_csv_reader.read(alias_csv_path),
        )

    def catalog_key(self, value: str) -> str:
        """Construit la cle d'unicite fonctionnelle du catalogue.

        Args:
            value (str): Nom de plateforme a normaliser.

        Returns:
            str: Cle trimmee, minuscule et sans accents.
        """

        normalized_value = unicodedata.normalize("NFD", str(value or "").strip().lower())
        return "".join(
            character
            for character in normalized_value
            if unicodedata.category(character) != "Mn"
        )

    def _seed_platforms(
        self,
        connection: Connection,
        entries: list[PlatformCatalogEntry],
    ) -> int:
        existing_keys = self._load_existing_platform_keys(connection)
        inserted_count = 0
        for entry in entries:
            entry_key = self.catalog_key(entry.name)
            if entry_key in existing_keys:
                continue
            self._insert_entry(connection, entry)
            existing_keys.add(entry_key)
            inserted_count += 1
        return inserted_count

    def _seed_aliases(
        self,
        connection: Connection,
        entries: list[PlatformAliasCatalogEntry],
    ) -> int:
        platform_ids_by_key = self._load_platform_ids_by_key(connection)
        existing_alias_keys = self._load_existing_alias_keys(connection)
        inserted_count = 0
        for entry in entries:
            platform_id = platform_ids_by_key.get(self.catalog_key(entry.platform_name))
            if platform_id is None:
                raise ValueError(f"Alias rattache a une plateforme inconnue: {entry.platform_name}.")
            alias_key = (platform_id, self.catalog_key(entry.alias_name))
            if alias_key in existing_alias_keys:
                continue
            self._insert_alias(connection, platform_id, entry)
            existing_alias_keys.add(alias_key)
            inserted_count += 1
        return inserted_count

    def _load_existing_platform_keys(self, connection: Connection) -> set[str]:
        rows = connection.execute(
            text(f'SELECT name FROM "{self.schema_name}".t_platform')
        ).mappings()
        return {self.catalog_key(row["name"]) for row in rows}

    def _load_platform_ids_by_key(self, connection: Connection) -> dict[str, int]:
        rows = connection.execute(
            text(f'SELECT id, name FROM "{self.schema_name}".t_platform')
        ).mappings()
        return {self.catalog_key(row["name"]): int(row["id"]) for row in rows}

    def _load_existing_alias_keys(self, connection: Connection) -> set[tuple[int, str]]:
        rows = connection.execute(
            text(f'SELECT platform, name FROM "{self.schema_name}".t_platform_alias')
        ).mappings()
        return {
            (int(row["platform"]), self.catalog_key(row["name"]))
            for row in rows
        }

    def _insert_entry(self, connection: Connection, entry: PlatformCatalogEntry) -> None:
        connection.execute(
            text(
                f'INSERT INTO "{self.schema_name}".t_platform '
                "(name, release_date, end_date, manufacturer, description) "
                "VALUES (:name, :release_date, :end_date, :manufacturer, :description)"
            ).bindparams(bindparam("description", type_=JSONB)),
            {
                "name": entry.name,
                "release_date": entry.release_date,
                "end_date": entry.end_date,
                "manufacturer": entry.manufacturer,
                "description": entry.description,
            },
        )

    def _insert_alias(
        self,
        connection: Connection,
        platform_id: int,
        entry: PlatformAliasCatalogEntry,
    ) -> None:
        connection.execute(
            text(
                f'INSERT INTO "{self.schema_name}".t_platform_alias '
                "(platform, name, category, usage_region, comment) "
                "VALUES (:platform, :name, :category, :usage_region, :comment)"
            ),
            {
                "platform": platform_id,
                "name": entry.alias_name,
                "category": entry.category or None,
                "usage_region": entry.usage_region or None,
                "comment": entry.comment or None,
            },
        )
