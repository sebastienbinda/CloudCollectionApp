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
from .collection_share import CollectionShare
from .collection_share_repository import SqlAlchemyCollectionShareRepository
from .game import Game
from .game_matching_configuration import GameMatchingConfiguration
from .game_matching_service import GameMatchingService
from .game_repository import SqlAlchemyGameRepository
from .library_reset_repository import LibraryResetImportableUser, SqlAlchemyLibraryResetRepository
from .platform import Platform
from .platform_alias import PlatformAlias
from .platform_alias_catalog_csv_reader import PlatformAliasCatalogCsvReader
from .platform_alias_catalog_entry import PlatformAliasCatalogEntry
from .platform_catalog_cache import PlatformCatalogCache
from .platform_catalog_csv_reader import PlatformCatalogCsvReader
from .platform_catalog_entry import PlatformCatalogEntry
from .platform_catalog_seed_service import PlatformCatalogSeedResult, PlatformCatalogSeedService
from .platform_catalog_update_service import PlatformCatalogUpdateService
from .platform_matching_admin_notifier import PlatformMatchingAdminNotifier
from .platform_matching_configuration import PlatformMatchingConfiguration
from .platform_matching_service import PlatformMatchingService
from .platform_image import PlatformImage
from .platform_image_repository import SqlAlchemyPlatformImageRepository
from .platform_repository import SqlAlchemyPlatformRepository
from .schema_version import SchemaVersion
from .studio import Studio
from .studio_repository import SqlAlchemyStudioRepository
from .user import User
from .user_collection import UserCollection
from .user_collection_file_repository import SqlAlchemyUserCollectionFileRepository
from .user_collection_import_repository import (
    CreatedGameMatchReport,
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
    "CollectionShare",
    "CreatedGameMatchReport",
    "Game",
    "GameMatchingConfiguration",
    "GameMatchingService",
    "LibraryResetImportableUser",
    "SqlAlchemyGameRepository",
    "SqlAlchemyCollectionShareRepository",
    "SqlAlchemyLibraryResetRepository",
    "SqlAlchemyPlatformImageRepository",
    "Platform",
    "PlatformAlias",
    "PlatformImage",
    "PlatformAliasCatalogCsvReader",
    "PlatformAliasCatalogEntry",
    "PlatformCatalogCache",
    "PlatformCatalogCsvReader",
    "PlatformCatalogEntry",
    "PlatformCatalogSeedResult",
    "PlatformCatalogSeedService",
    "PlatformCatalogUpdateService",
    "PlatformMatchingAdminNotifier",
    "PlatformMatchingConfiguration",
    "PlatformMatchingService",
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
