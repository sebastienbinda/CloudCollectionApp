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

from datetime import datetime
from pathlib import Path
import unittest

from alembic.config import Config
from alembic.script import ScriptDirectory

from services.database import DatabaseConfiguration, DatabaseSchemaService


class FakeScalarResult:
    """Resultat SQL factice retournant une valeur scalaire."""

    def __init__(self, value):
        """Initialise le resultat factice.

        Args:
            value (object): Valeur retournee par `scalar`.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.value = value

    def scalar(self):
        """Retourne la valeur scalaire factice.

        Args:
            Aucun.

        Returns:
            object: Valeur configuree dans le resultat factice.
        """

        return self.value


class FakeConnection:
    """Connexion SQLAlchemy factice capturant les requetes executees."""

    def __init__(self, existing_creation_date=None):
        """Initialise la connexion factice.

        Args:
            existing_creation_date (datetime | None): Date existante retournee par `SELECT`.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.existing_creation_date = existing_creation_date
        self.executed_statements = []

    def execute(self, statement, parameters=None):
        """Capture une requete SQL executee.

        Args:
            statement (object): Requete SQLAlchemy recue.
            parameters (dict | None): Parametres associes a la requete.

        Returns:
            FakeScalarResult: Resultat factice compatible avec `scalar`.
        """

        sql = str(statement)
        self.executed_statements.append((sql, parameters))
        if sql.startswith("SELECT MIN"):
            return FakeScalarResult(self.existing_creation_date)
        return FakeScalarResult(None)


class FakeTransaction:
    """Contexte transactionnel factice retournant une connexion."""

    def __init__(self, connection):
        """Initialise le contexte factice.

        Args:
            connection (FakeConnection): Connexion retournee dans le contexte.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection

    def __enter__(self):
        """Entre dans le contexte transactionnel factice.

        Args:
            Aucun.

        Returns:
            FakeConnection: Connexion factice.
        """

        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        """Sort du contexte transactionnel factice.

        Args:
            exc_type (type | None): Type d'exception eventuelle.
            exc_value (BaseException | None): Exception eventuelle.
            traceback (object | None): Traceback eventuel.

        Returns:
            bool: `False` pour ne pas masquer les exceptions.
        """

        return False


class FakeEngine:
    """Moteur SQLAlchemy factice capturant les transactions ouvertes."""

    def __init__(self, existing_creation_date=None):
        """Initialise le moteur factice.

        Args:
            existing_creation_date (datetime | None): Date existante retournee par `SELECT`.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = FakeConnection(existing_creation_date)
        self.begin_count = 0

    def begin(self):
        """Ouvre un contexte transactionnel factice.

        Args:
            Aucun.

        Returns:
            FakeTransaction: Contexte transactionnel factice.
        """

        self.begin_count += 1
        return FakeTransaction(self.connection)


class FakeLogger:
    """Journal factice capturant les messages d'information."""

    def __init__(self):
        """Initialise le journal factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.info_messages = []

    def info(self, message, *args):
        """Capture un message d'information.

        Args:
            message (str): Message journalise.
            *args (tuple): Parametres de formatage du message.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.info_messages.append((message, args))


class DatabaseSchemaServiceTest(unittest.TestCase):
    def test_migrations_keep_single_linear_head(self):
        """Verifie que le dossier Alembic contient une seule branche lineaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la structure des revisions Alembic.
        """

        migrations_path = Path(__file__).resolve().parents[1] / "migrations"
        alembic_configuration = Config()
        alembic_configuration.set_main_option("script_location", str(migrations_path))

        script_directory = ScriptDirectory.from_config(alembic_configuration)
        revisions = list(script_directory.walk_revisions())

        revisions_by_id = {revision.revision: revision for revision in revisions}

        self.assertEqual(["20260525_0005"], script_directory.get_heads())
        self.assertEqual(2, len(revisions))
        self.assertEqual("20260522_0004", revisions_by_id["20260525_0005"].down_revision)
        self.assertIsNone(revisions_by_id["20260522_0004"].down_revision)

    def test_collection_query_index_migration_declares_expected_indexes(self):
        """Verifie que la migration d'index cible les colonnes attendues.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les index declares.
        """

        migration_path = (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "versions"
            / "20260525_0005_add_collection_query_indexes.py"
        )
        migration_source = migration_path.read_text(encoding="utf-8")

        self.assertIn('"ix_t_user_collection_game_id"', migration_source)
        self.assertIn('"t_user_collection"', migration_source)
        self.assertIn('["game_id"]', migration_source)
        self.assertIn('"ix_t_game_platform"', migration_source)
        self.assertIn('["platform"]', migration_source)
        self.assertIn('"ix_t_game_developer"', migration_source)
        self.assertIn('["developer"]', migration_source)

    def test_initialize_database_schema_skips_when_database_url_is_absent(self):
        """Verifie que l'initialisation est ignoree sans `DATABASE_URL`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident qu'aucune connexion n'est ouverte.
        """

        engine_factory_called = False

        def engine_factory(database_url):
            nonlocal engine_factory_called
            engine_factory_called = True
            return FakeEngine()

        configuration = DatabaseConfiguration(
            database_url=None,
            schema_name="collection",
            application_version="1.0",
        )
        service = DatabaseSchemaService(configuration, engine_factory=engine_factory)

        self.assertFalse(service.initialize_database_schema())
        self.assertFalse(engine_factory_called)

    def test_initialize_database_schema_on_startup_logs_skip_without_database_url(self):
        """Verifie que l'initialisation de demarrage trace une base absente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut et le message journalise.
        """

        logger = FakeLogger()
        configuration = DatabaseConfiguration(
            database_url=None,
            schema_name="collection",
            application_version="1.0",
        )

        initialized = DatabaseSchemaService.initialize_database_schema_on_startup(
            logger,
            configuration=configuration,
        )

        self.assertFalse(initialized)
        self.assertEqual(
            ("DATABASE_URL absent : initialisation SQL ignoree.", ()),
            logger.info_messages[0],
        )

    def test_initialize_database_schema_creates_schema_and_updates_version(self):
        """Verifie l'orchestration schema, migration et version applicative.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les requetes executees.
        """

        fake_engine = FakeEngine()
        migrations = []
        configuration = DatabaseConfiguration(
            database_url="postgresql://database/app",
            schema_name="collection",
            application_version="1.0",
        )

        def migration_runner(engine, runner_configuration, migrations_path):
            migrations.append((engine, runner_configuration, migrations_path))

        service = DatabaseSchemaService(
            configuration,
            engine_factory=lambda database_url: fake_engine,
            migration_runner=migration_runner,
        )

        self.assertTrue(service.initialize_database_schema())

        executed_sql = [statement for statement, parameters in fake_engine.connection.executed_statements]
        self.assertIn('CREATE SCHEMA IF NOT EXISTS "collection"', executed_sql)
        self.assertTrue(any(statement.startswith("SELECT MIN") for statement in executed_sql))
        self.assertTrue(any(statement.startswith("DELETE FROM") for statement in executed_sql))
        self.assertTrue(any(statement.startswith("INSERT INTO") for statement in executed_sql))
        self.assertEqual(1, len(migrations))
        self.assertEqual(configuration, migrations[0][1])

    def test_initialize_database_schema_keeps_existing_creation_date(self):
        """Verifie que la date de creation existante est conservee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les parametres d'insertion.
        """

        existing_creation_date = datetime(2026, 5, 1, 8, 30, 0)
        fake_engine = FakeEngine(existing_creation_date)
        configuration = DatabaseConfiguration(
            database_url="postgresql://database/app",
            schema_name="collection",
            application_version="1.1",
        )
        service = DatabaseSchemaService(
            configuration,
            engine_factory=lambda database_url: fake_engine,
            migration_runner=lambda engine, runner_configuration, migrations_path: None,
        )

        service.initialize_database_schema()

        insert_parameters = [
            parameters
            for statement, parameters in fake_engine.connection.executed_statements
            if statement.startswith("INSERT INTO")
        ][0]
        self.assertEqual("1.1", insert_parameters["version"])
        self.assertEqual(existing_creation_date, insert_parameters["date_creation"])
        self.assertIsNotNone(insert_parameters["update_date"])


if __name__ == "__main__":
    unittest.main()
