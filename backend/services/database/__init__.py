#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-12
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Exports publics du domaine database."""

from .database_configuration import DatabaseConfiguration
from .database_model_base import DatabaseModelBase
from .database_schema_service import DatabaseSchemaService
from .game import Game
from .game_repository import SqlAlchemyGameRepository
from .library_reset_repository import LibraryResetImportableUser, SqlAlchemyLibraryResetRepository
from .platform import Platform
from .platform_catalog_cache import PlatformCatalogCache
from .platform_catalog_csv_reader import PlatformCatalogCsvReader
from .platform_catalog_entry import PlatformCatalogEntry
from .platform_catalog_seed_service import PlatformCatalogSeedService
from .platform_repository import SqlAlchemyPlatformRepository
from .schema_version import SchemaVersion
from .studio import Studio
from .studio_repository import SqlAlchemyStudioRepository
from .user import User
from .user_collection import UserCollection
from .user_collection_file_repository import SqlAlchemyUserCollectionFileRepository
from .user_collection_import_repository import (
    SqlAlchemyUserCollectionImportRepository,
    UserCollectionImportPersistenceResult,
    UserCollectionImportUserNotFoundError,
)
from .user_collection_query_repository import SqlAlchemyUserCollectionQueryRepository
from .user_collection_repository import SqlAlchemyUserCollectionRepository, UserGameAssociation
from .user_repository import SqlAlchemyUserRepository

__all__ = [
    "DatabaseConfiguration",
    "DatabaseModelBase",
    "DatabaseSchemaService",
    "Game",
    "LibraryResetImportableUser",
    "SqlAlchemyGameRepository",
    "SqlAlchemyLibraryResetRepository",
    "Platform",
    "PlatformCatalogCache",
    "PlatformCatalogCsvReader",
    "PlatformCatalogEntry",
    "PlatformCatalogSeedService",
    "SqlAlchemyPlatformRepository",
    "SchemaVersion",
    "Studio",
    "SqlAlchemyStudioRepository",
    "SqlAlchemyUserCollectionFileRepository",
    "SqlAlchemyUserCollectionImportRepository",
    "SqlAlchemyUserCollectionQueryRepository",
    "SqlAlchemyUserCollectionRepository",
    "SqlAlchemyUserRepository",
    "User",
    "UserCollection",
    "UserCollectionImportPersistenceResult",
    "UserCollectionImportUserNotFoundError",
    "UserGameAssociation",
]
