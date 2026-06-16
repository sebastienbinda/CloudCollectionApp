#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-16
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : service d'actualisation admin du catalogue plateformes.

from pathlib import Path
from typing import Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .database_configuration import DatabaseConfiguration
from .platform_catalog_cache import PlatformCatalogCache
from .platform_catalog_seed_service import (
    PlatformCatalogSeedResult,
    PlatformCatalogSeedService,
)

EngineFactory = Callable[[str], Engine]


class PlatformCatalogUpdateService:
    """Synchronise le catalogue plateformes SQL avec les ressources CSV."""

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        seed_service: PlatformCatalogSeedService | None = None,
        platform_catalog_cache: PlatformCatalogCache | None = None,
        resources_directory: Path | None = None,
        engine_factory: EngineFactory = create_engine,
    ):
        """Initialise le service d'actualisation catalogue.

        Args:
            configuration (DatabaseConfiguration): Configuration de connexion SQL.
            seed_service (PlatformCatalogSeedService | None): Seed injectable.
            platform_catalog_cache (PlatformCatalogCache | None): Cache plateformes injectable.
            resources_directory (Path | None): Repertoire des CSV backend.
            engine_factory (EngineFactory): Fabrique de moteur SQLAlchemy.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si la base de donnees n'est pas configuree.
        """

        configuration.validate()
        if not configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour actualiser les plateformes.")
        self.configuration = configuration
        self.seed_service = seed_service or PlatformCatalogSeedService(
            configuration.schema_name
        )
        self.platform_catalog_cache = platform_catalog_cache or PlatformCatalogCache()
        self.resources_directory = resources_directory or self.default_resources_directory()
        self.engine_factory = engine_factory

    @classmethod
    def from_environment(cls) -> "PlatformCatalogUpdateService":
        """Construit le service depuis l'environnement.

        Args:
            Aucun.

        Returns:
            PlatformCatalogUpdateService: Service configure.
        """

        return cls(DatabaseConfiguration.from_environment())

    @classmethod
    def default_resources_directory(cls) -> Path:
        """Retourne le repertoire des ressources backend embarquees.

        Args:
            Aucun.

        Returns:
            Path: Repertoire `backend/resources`.
        """

        return Path(__file__).resolve().parents[2] / "resources"

    def update_from_resources(self) -> PlatformCatalogSeedResult:
        """Ajoute en base les plateformes et alias CSV absents.

        Args:
            Aucun.

        Returns:
            PlatformCatalogSeedResult: Compteurs de plateformes et alias ajoutes.

        Raises:
            ValueError: Si les CSV contiennent des donnees invalides.
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la mise a jour.
        """

        engine = self.engine_factory(self.configuration.database_url)
        with engine.begin() as connection:
            result = self.seed_service.seed_from_csv_detailed(
                connection,
                self.resources_directory / "platform_catalog.csv",
                self.resources_directory / "platform_alias_catalog.csv",
            )
        self.platform_catalog_cache.invalidate(self.configuration.schema_name)
        return result
