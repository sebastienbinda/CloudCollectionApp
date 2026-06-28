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
from types import SimpleNamespace
import unittest

from alembic.config import Config
from alembic.script import ScriptDirectory

from services.database import DatabaseConfiguration, DatabaseSchemaService

BACKEND_DIR = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "app.py").exists()
)


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


def build_noop_platform_seed_service(schema_name):
    """Construit un service de seed plateformes sans effet.

    Args:
        schema_name (str): Schema PostgreSQL ignore.

    Returns:
        SimpleNamespace: Service factice compatible avec l'initialisation.
    """

    return SimpleNamespace(seed_from_csv=lambda connection, csv_path, alias_csv_path: 0)


class DatabaseSchemaServiceTest(unittest.TestCase):
    def test_migrations_keep_single_linear_head(self):
        """Verifie que le dossier Alembic contient une seule branche lineaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la structure des revisions Alembic.
        """

        migrations_path = BACKEND_DIR / "migrations"
        alembic_configuration = Config()
        alembic_configuration.set_main_option("script_location", str(migrations_path))

        script_directory = ScriptDirectory.from_config(alembic_configuration)
        revisions = list(script_directory.walk_revisions())

        revisions_by_id = {revision.revision: revision for revision in revisions}

        self.assertEqual(["20260628_0017"], script_directory.get_heads())
        self.assertEqual(14, len(revisions))
        self.assertEqual("20260627_0016", revisions_by_id["20260628_0017"].down_revision)
        self.assertEqual("20260625_0015", revisions_by_id["20260627_0016"].down_revision)
        self.assertEqual("20260623_0014", revisions_by_id["20260625_0015"].down_revision)
        self.assertEqual("20260622_0013", revisions_by_id["20260623_0014"].down_revision)
        self.assertEqual("20260620_0010", revisions_by_id["20260620_0011"].down_revision)
        self.assertEqual("20260614_0008", revisions_by_id["20260618_0009"].down_revision)
        self.assertEqual("20260605_0007", revisions_by_id["20260614_0008"].down_revision)
        self.assertEqual("20260603_0006", revisions_by_id["20260605_0007"].down_revision)
        self.assertEqual("20260525_0005", revisions_by_id["20260603_0006"].down_revision)
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
            BACKEND_DIR
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

    def test_collection_share_migration_declares_expected_schema(self):
        """Verifie la migration de stockage des partages de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident table, relation et index.
        """

        migration_path = (
            BACKEND_DIR
            / "migrations"
            / "versions"
            / "20260623_0014_add_collection_shares.py"
        )
        migration_source = migration_path.read_text(encoding="utf-8")

        self.assertIn('down_revision: Union[str, None] = "20260622_0013"', migration_source)
        self.assertIn('"s_collection_share"', migration_source)
        self.assertIn('"t_collection_share"', migration_source)
        self.assertIn('"owner_user_id"', migration_source)
        self.assertIn('"allow_collection"', migration_source)
        self.assertIn('"allow_wishlist"', migration_source)
        self.assertIn('"allow_prices"', migration_source)
        self.assertIn('ondelete="CASCADE"', migration_source)
        self.assertIn("ck_t_collection_share_expiration", migration_source)
        self.assertIn("ix_t_collection_share_owner_user_id", migration_source)

    def test_collection_share_recipient_migration_declares_expected_column(self):
        """Verifie la migration du destinataire des partages.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la colonne et la chaine Alembic.
        """

        migration_path = (
            BACKEND_DIR
            / "migrations"
            / "versions"
            / "20260625_0015_add_collection_share_recipient.py"
        )
        migration_source = migration_path.read_text(encoding="utf-8")

        self.assertIn('down_revision: Union[str, None] = "20260623_0014"', migration_source)
        self.assertIn('"t_collection_share"', migration_source)
        self.assertIn('"recipient"', migration_source)
        self.assertIn("sa.String(length=256)", migration_source)

    def test_wishlist_migration_declares_expected_column_and_backfill(self):
        """Verifie que la migration wishlist preserve les donnees existantes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la colonne et le backfill.
        """

        migration_path = (
            BACKEND_DIR
            / "migrations"
            / "versions"
            / "20260603_0006_add_user_collection_wishlist.py"
        )
        migration_source = migration_path.read_text(encoding="utf-8")

        self.assertIn('"wishlist"', migration_source)
        self.assertIn("sa.Boolean()", migration_source)
        self.assertIn("server_default=sa.text(\"false\")", migration_source)
        self.assertIn("nullable=False", migration_source)
        self.assertIn("SET wishlist = false WHERE wishlist IS NULL", migration_source)
        self.assertIn("op.drop_column", migration_source)

    def test_platform_catalog_migration_declares_expected_schema_changes_and_seed(self):
        """Verifie que la migration plateformes charge le catalogue CSV.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les changements declares.
        """

        migration_path = (
            BACKEND_DIR
            / "migrations"
            / "versions"
            / "20260614_0008_platform_catalog_schema.py"
        )
        migration_source = migration_path.read_text(encoding="utf-8")

        self.assertIn('"end_date"', migration_source)
        self.assertIn("op.add_column", migration_source)
        self.assertIn('op.drop_column("t_platform", "status"', migration_source)
        self.assertIn("t_platform_alias", migration_source)
        self.assertIn("s_platform_alias", migration_source)
        self.assertIn("PlatformCatalogSeedService", migration_source)
        self.assertIn('"resources"', migration_source)
        self.assertIn("platform_catalog.csv", migration_source)
        self.assertIn("platform_alias_catalog.csv", migration_source)

    def test_platform_image_migration_declares_expected_schema_changes(self):
        """Verifie que la migration images plateformes declare le schema attendu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les changements declares.
        """

        migration_path = (
            BACKEND_DIR
            / "migrations"
            / "versions"
            / "20260618_0009_add_platform_images.py"
        )
        migration_source = migration_path.read_text(encoding="utf-8")

        self.assertIn("t_platform_image", migration_source)
        self.assertIn("s_platform_image", migration_source)
        self.assertIn('"user_id"', migration_source)
        self.assertIn("nullable=False", migration_source)
        self.assertIn("t_user.id", migration_source)
        self.assertIn("ck_t_platform_image_type", migration_source)
        self.assertIn("ck_t_platform_image_status", migration_source)
        self.assertIn("ix_t_platform_image_user_id", migration_source)
        self.assertIn("uq_t_platform_image_single_main", migration_source)
        self.assertIn("postgresql_where=sa.text(\"type = 'MAIN'\")", migration_source)

    def test_platform_image_file_size_migration_declares_expected_schema_changes(self):
        """Verifie que la migration de taille image declare le schema attendu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les changements declares.
        """

        migration_path = (
            BACKEND_DIR
            / "migrations"
            / "versions"
            / "20260620_0010_add_platform_image_file_size.py"
        )
        migration_source = migration_path.read_text(encoding="utf-8")

        self.assertIn('"file_size_bytes"', migration_source)
        self.assertIn("sa.BigInteger()", migration_source)
        self.assertIn("server_default=sa.text(\"0\")", migration_source)
        self.assertIn("ck_t_platform_image_file_size_bytes", migration_source)
        self.assertIn("file_size_bytes >= 0", migration_source)

    def test_decimal_purchase_price_migration_preserves_existing_values(self):
        """Verifie la migration du prix d'achat vers deux decimales.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le type et la conversion PostgreSQL.
        """

        migration_path = (
            BACKEND_DIR
            / "migrations"
            / "versions"
            / "20260621_0012_decimal_purchase_price.py"
        )
        migration_source = migration_path.read_text(encoding="utf-8")

        self.assertIn('down_revision: Union[str, None] = "20260620_0011"', migration_source)
        self.assertIn("sa.Numeric(precision=12, scale=2)", migration_source)
        self.assertIn('postgresql_using="purchase_price::numeric(12,2)"', migration_source)

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
            platform_catalog_seed_service_factory=build_noop_platform_seed_service,
        )

        self.assertTrue(service.initialize_database_schema())

        executed_sql = [statement for statement, parameters in fake_engine.connection.executed_statements]
        self.assertIn('CREATE SCHEMA IF NOT EXISTS "collection"', executed_sql)
        self.assertTrue(any(statement.startswith("SELECT MIN") for statement in executed_sql))
        self.assertTrue(any(statement.startswith("DELETE FROM") for statement in executed_sql))
        self.assertTrue(any(statement.startswith("INSERT INTO") for statement in executed_sql))
        self.assertEqual(1, len(migrations))
        self.assertEqual(configuration, migrations[0][1])

    def test_initialize_database_schema_seeds_platform_catalog_on_each_startup(self):
        """Verifie que le catalogue plateformes est recharge apres les migrations.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le seed idempotent de demarrage.
        """

        fake_engine = FakeEngine()
        configuration = DatabaseConfiguration(
            database_url="postgresql://database/app",
            schema_name="collection",
            application_version="1.0",
        )
        seed_calls = []

        def seed_service_factory(schema_name):
            return SimpleNamespace(
                seed_from_csv=lambda connection, csv_path, alias_csv_path: seed_calls.append(
                    (schema_name, connection, csv_path, alias_csv_path)
                ) or 2
            )

        service = DatabaseSchemaService(
            configuration,
            engine_factory=lambda database_url: fake_engine,
            migration_runner=lambda engine, runner_configuration, migrations_path: None,
            platform_catalog_seed_service_factory=seed_service_factory,
        )

        self.assertTrue(service.initialize_database_schema())

        self.assertEqual(1, len(seed_calls))
        schema_name, connection, csv_path, alias_csv_path = seed_calls[0]
        self.assertEqual("collection", schema_name)
        self.assertIs(fake_engine.connection, connection)
        self.assertEqual("resources", csv_path.parent.name)
        self.assertEqual("resources", alias_csv_path.parent.name)
        self.assertEqual("platform_catalog.csv", csv_path.name)
        self.assertEqual("platform_alias_catalog.csv", alias_csv_path.name)

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
            platform_catalog_seed_service_factory=build_noop_platform_seed_service,
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
