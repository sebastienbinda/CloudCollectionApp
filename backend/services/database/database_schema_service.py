#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-12
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : service d'initialisation du schema PostgreSQL au demarrage.

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .database_configuration import DatabaseConfiguration

EngineFactory = Callable[[str], Engine]
MigrationRunner = Callable[[Engine, DatabaseConfiguration, Path], None]


class DatabaseSchemaService:
    """Prepare le schema PostgreSQL et applique les migrations Alembic."""

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        migrations_path: Optional[Path] = None,
        engine_factory: Optional[EngineFactory] = None,
        migration_runner: Optional[MigrationRunner] = None,
    ):
        """Initialise le service de gestion du schema SQL.

        Args:
            configuration (DatabaseConfiguration): Configuration de connexion et de schema.
            migrations_path (Optional[Path]): Dossier Alembic contenant `env.py`.
            engine_factory (Optional[EngineFactory]): Fabrique SQLAlchemy injectable en test.
            migration_runner (Optional[MigrationRunner]): Lanceur Alembic injectable en test.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration
        self.migrations_path = migrations_path or Path(__file__).resolve().parents[2] / "migrations"
        self.engine_factory = engine_factory or create_engine
        self.migration_runner = migration_runner or run_alembic_migrations

    def initialize_database_schema(self) -> bool:
        """Cree le schema, applique les migrations et trace la version applicative.

        Args:
            Aucun.

        Returns:
            bool: `True` si l'initialisation a ete executee, sinon `False`.

        Raises:
            ValueError: Si la configuration est invalide.
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une operation.
        """

        self.configuration.validate()
        if not self.configuration.is_database_enabled():
            return False

        engine = self.engine_factory(self.configuration.database_url)
        with engine.begin() as connection:
            connection.execute(
                text(f'CREATE SCHEMA IF NOT EXISTS "{self.configuration.schema_name}"')
            )

        self.migration_runner(engine, self.configuration, self.migrations_path)
        self._upsert_schema_version(engine)
        return True

    def _upsert_schema_version(self, engine: Engine) -> None:
        """Inscrit la version applicative courante dans `t_schema_version`.

        Args:
            engine (Engine): Moteur SQLAlchemy connecte a PostgreSQL.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        schema_name = self.configuration.schema_name
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        with engine.begin() as connection:
            existing_creation_date = connection.execute(
                text(f'SELECT MIN(date_creation) FROM "{schema_name}".t_schema_version')
            ).scalar()
            creation_date = existing_creation_date or now
            connection.execute(text(f'DELETE FROM "{schema_name}".t_schema_version'))
            connection.execute(
                text(
                    f'INSERT INTO "{schema_name}".t_schema_version '
                    "(version, date_creation, update_date) "
                    "VALUES (:version, :date_creation, :update_date)"
                ),
                {
                    "version": self.configuration.application_version,
                    "date_creation": creation_date,
                    "update_date": now if existing_creation_date else None,
                },
            )


def run_alembic_migrations(
    engine: Engine,
    configuration: DatabaseConfiguration,
    migrations_path: Path,
) -> None:
    """Execute les migrations Alembic jusqu'a la revision `head`.

    Args:
        engine (Engine): Moteur SQLAlchemy utilise pour la transaction Alembic.
        configuration (DatabaseConfiguration): Configuration contenant le schema cible.
        migrations_path (Path): Dossier Alembic contenant `env.py` et `versions`.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    alembic_configuration = Config()
    alembic_configuration.set_main_option("script_location", str(migrations_path))
    alembic_configuration.attributes["connection"] = engine
    alembic_configuration.attributes["schema_name"] = configuration.schema_name
    command.upgrade(alembic_configuration, "head")
