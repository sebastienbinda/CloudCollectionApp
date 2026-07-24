#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : persistance SQL du reset global de la Bibliotheque.

from dataclasses import dataclass
from datetime import datetime

from typing import Any, Callable

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .database_configuration import DatabaseConfiguration
from .platform_catalog_cache import PlatformCatalogCache


@dataclass(frozen=True)
class LibraryResetImportableUser:
    """Represente un utilisateur dont le fichier peut reconstruire la Bibliotheque.

    Attributes:
        id (int): Identifiant technique utilisateur.
        email (str): Adresse email utilisateur.
        collection_file_path (str): Chemin du fichier stocke.
        collection_file_description (dict | None): Configuration d'import sauvegardee.
        profile (str): Profil applicatif.
        status (str): Statut fonctionnel.
        creation_date (datetime): Date de creation utilisateur.
    """

    id: int
    email: str
    collection_file_path: str
    collection_file_description: dict | None
    profile: str
    status: str
    creation_date: datetime


@dataclass(frozen=True)
class LibraryResetPlatformImageSnapshot:
    """Represente une image de plateforme a restaurer apres reset.

    Attributes:
        platform_name (str): Nom de plateforme avant nettoyage.
        path (str): Chemin absolu du fichier image.
        file_size_bytes (int): Taille du fichier image en octets.
        type (str): Type fonctionnel de l'image.
        status (str): Statut de validation de l'image.
        user_id (int): Utilisateur ayant propose l'image.
        creation_date (datetime): Date de creation de la proposition.
    """

    platform_name: str
    path: str
    file_size_bytes: int
    type: str
    status: str
    user_id: int
    creation_date: datetime


EngineFactory = Callable[[str], Engine]


class SqlAlchemyLibraryResetRepository:
    """Execute les operations SQL necessaires au reset Bibliotheque."""

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        engine: Engine | None = None,
        engine_factory: EngineFactory = create_engine,
        platform_catalog_cache: PlatformCatalogCache | None = None,
    ):
        """Initialise le repository de reset Bibliotheque.

        Args:
            configuration (DatabaseConfiguration): Configuration SQLAlchemy.
            engine (Engine | None): Moteur SQLAlchemy injectable en test.
            engine_factory (EngineFactory): Fabrique de moteur SQLAlchemy.
            platform_catalog_cache (PlatformCatalogCache | None): Cache plateformes injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si aucune base de donnees n'est configuree.
        """

        configuration.validate()
        if not configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour reinitialiser la Bibliotheque.")
        self.configuration = configuration
        self.engine = engine or engine_factory(configuration.database_url)
        self.platform_catalog_cache = platform_catalog_cache or PlatformCatalogCache()

    def clean_library_tables(self) -> list[LibraryResetPlatformImageSnapshot]:
        """Vide les tables reconstruites par le reset Bibliotheque.

        Args:
            Aucun.

        Returns:
            list[LibraryResetPlatformImageSnapshot]: Images a reassocier apres reimport.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une suppression.
        """

        schema_name = self.configuration.schema_name
        table_names = (
            "t_user_collection",
            "t_game",
            "t_studio",
            "t_platform_image",
            "t_platform_alias",
            "t_platform",
        )
        with self.engine.begin() as connection:
            platform_image_snapshots = self._list_platform_image_snapshots(connection)
            for table_name in table_names:
                connection.execute(text(f'DELETE FROM "{schema_name}".{table_name}'))
        self.platform_catalog_cache.invalidate(schema_name)
        return platform_image_snapshots

    def restore_platform_images(
        self,
        platform_image_snapshots: list[LibraryResetPlatformImageSnapshot],
    ) -> int:
        """Reassocie les images sauvegardees aux plateformes recreees.

        Args:
            platform_image_snapshots (list[LibraryResetPlatformImageSnapshot]): Images sauvegardees.

        Returns:
            int: Nombre d'images restaurees.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une insertion.
        """

        if not platform_image_snapshots:
            return 0
        schema_name = self.configuration.schema_name
        restored_count = 0
        with self.engine.begin() as connection:
            platform_ids_by_key = self._load_platform_ids_by_name_or_alias(connection)
            for snapshot in platform_image_snapshots:
                platform_id = platform_ids_by_key.get(self._platform_key(snapshot.platform_name))
                if platform_id is None:
                    continue
                result = connection.execute(
                    text(
                        f'INSERT INTO "{schema_name}".t_platform_image '
                        "(platform, path, file_size_bytes, type, status, user_id, creation_date) "
                        "VALUES (:platform, :path, :file_size_bytes, :type, :status, "
                        ":user_id, :creation_date) "
                        "ON CONFLICT DO NOTHING"
                    ),
                    {
                        "platform": platform_id,
                        "path": snapshot.path,
                        "file_size_bytes": snapshot.file_size_bytes,
                        "type": snapshot.type,
                        "status": snapshot.status,
                        "user_id": snapshot.user_id,
                        "creation_date": snapshot.creation_date,
                    },
                )
                restored_count += int(result.rowcount or 0)
        self.platform_catalog_cache.invalidate(schema_name)
        return restored_count

    def _list_platform_image_snapshots(
        self,
        connection,
    ) -> list[LibraryResetPlatformImageSnapshot]:
        rows = connection.execute(
            text(
                f"SELECT platform.name AS platform_name, image.path, image.file_size_bytes, "
                f"image.type, image.status, image.user_id, image.creation_date "
                f'FROM "{self.configuration.schema_name}".t_platform_image image '
                f'JOIN "{self.configuration.schema_name}".t_platform platform '
                "ON platform.id = image.platform "
                "ORDER BY image.id ASC"
            )
        ).mappings().all()
        return [
            LibraryResetPlatformImageSnapshot(
                platform_name=str(row["platform_name"]),
                path=str(row["path"]),
                file_size_bytes=int(row["file_size_bytes"]),
                type=str(row["type"]),
                status=str(row["status"]),
                user_id=int(row["user_id"]),
                creation_date=row["creation_date"],
            )
            for row in rows
        ]

    def _load_platform_ids_by_name_or_alias(self, connection) -> dict[str, int]:
        platform_ids_by_key: dict[str, int] = {}
        rows = connection.execute(
            text(
                f'SELECT id, name FROM "{self.configuration.schema_name}".t_platform '
                "ORDER BY id ASC"
            )
        ).mappings().all()
        for row in rows:
            platform_ids_by_key.setdefault(self._platform_key(row["name"]), int(row["id"]))
        alias_rows = connection.execute(
            text(
                f'SELECT platform, name FROM "{self.configuration.schema_name}".t_platform_alias '
                "ORDER BY platform ASC, id ASC"
            )
        ).mappings().all()
        for row in alias_rows:
            platform_ids_by_key.setdefault(self._platform_key(row["name"]), int(row["platform"]))
        return platform_ids_by_key

    @staticmethod
    def _platform_key(value: Any) -> str:
        return str(value or "").strip().casefold()

    def list_importable_users(self) -> list[LibraryResetImportableUser]:
        """Liste les utilisateurs dont un fichier de collection est reference.

        Args:
            Aucun.

        Returns:
            list[LibraryResetImportableUser]: Utilisateurs ordonnes par date de creation.
        """

        schema_name = self.configuration.schema_name
        with self.engine.connect() as connection:
            rows = connection.execute(
                text(
                    f'SELECT id, email, collection_file_path, collection_file_description, '
                    f'profile, status, creation_date FROM "{schema_name}".t_user '
                    "WHERE collection_file_path IS NOT NULL "
                    "ORDER BY creation_date ASC, id ASC"
                )
            ).mappings().all()
        return [
            LibraryResetImportableUser(
                id=int(row["id"]),
                email=str(row["email"]),
                collection_file_path=str(row["collection_file_path"]),
                collection_file_description=row["collection_file_description"],
                profile=str(row["profile"]),
                status=str(row["status"]),
                creation_date=row["creation_date"],
            )
            for row in rows
        ]
