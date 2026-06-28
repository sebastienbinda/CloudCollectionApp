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
# Description : tests du repository SQL de reset Bibliotheque.

from datetime import datetime
import unittest

from services.database import PlatformCatalogCache, SqlAlchemyLibraryResetRepository


class FakeDatabaseConfiguration:
    """Configuration de base factice."""

    database_url = "postgresql://example"
    schema_name = "public"

    def validate(self):
        """Valide toujours la configuration.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

    def is_database_enabled(self):
        """Indique que la base est active.

        Args:
            Aucun.

        Returns:
            bool: Toujours `True`.
        """

        return True


class FakeTransaction:
    """Transaction factice memorisant les rollbacks implicites."""

    def __init__(self, connection):
        """Initialise la transaction.

        Args:
            connection (FakeConnection): Connexion retournee.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection
        self.rolled_back = False

    def __enter__(self):
        """Retourne la connexion.

        Args:
            Aucun.

        Returns:
            FakeConnection: Connexion configuree.
        """

        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        """Memorise si une exception force le rollback.

        Args:
            exc_type (type | None): Type d'exception.
            exc_value (Exception | None): Exception recue.
            traceback (object | None): Traceback recu.

        Returns:
            bool: `False` pour propager les exceptions.
        """

        self.rolled_back = exc_type is not None
        return False


class FakeConnection:
    """Connexion SQL factice."""

    def __init__(self, rows=None, error_on_execute=None):
        """Initialise la connexion.

        Args:
            rows (list[dict] | None): Lignes retournees.
            error_on_execute (Exception | None): Erreur a lever.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.rows = rows or []
        self.error_on_execute = error_on_execute
        self.executed_sql = []

    def execute(self, statement):
        """Memorise le SQL execute.

        Args:
            statement (object): Statement SQLAlchemy.

        Returns:
            FakeResult: Resultat factice.

        Raises:
            Exception: Erreur configuree.
        """

        self.executed_sql.append(str(statement))
        if self.error_on_execute:
            raise self.error_on_execute
        return FakeResult(self.rows)


class FakeResult:
    """Resultat SQL factice."""

    def __init__(self, rows):
        """Initialise le resultat.

        Args:
            rows (list[dict]): Lignes retournees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.rows = rows

    def mappings(self):
        """Retourne le resultat comme mappings.

        Args:
            Aucun.

        Returns:
            FakeResult: Resultat courant.
        """

        return self

    def all(self):
        """Retourne toutes les lignes.

        Args:
            Aucun.

        Returns:
            list[dict]: Lignes configurees.
        """

        return self.rows


class FakeConnectContext:
    """Contexte de connexion factice."""

    def __init__(self, connection):
        """Initialise le contexte.

        Args:
            connection (FakeConnection): Connexion retournee.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection

    def __enter__(self):
        """Retourne la connexion.

        Args:
            Aucun.

        Returns:
            FakeConnection: Connexion configuree.
        """

        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        """Ne masque aucune exception.

        Args:
            exc_type (type | None): Type d'exception.
            exc_value (Exception | None): Exception recue.
            traceback (object | None): Traceback recu.

        Returns:
            bool: Toujours `False`.
        """

        return False


class FakeEngine:
    """Engine factice exposant `begin` et `connect`."""

    def __init__(self, connection):
        """Initialise l'engine.

        Args:
            connection (FakeConnection): Connexion partagee.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection
        self.transaction = FakeTransaction(connection)

    def begin(self):
        """Retourne une transaction.

        Args:
            Aucun.

        Returns:
            FakeTransaction: Transaction configuree.
        """

        return self.transaction

    def connect(self):
        """Retourne un contexte de connexion.

        Args:
            Aucun.

        Returns:
            FakeConnectContext: Contexte configure.
        """

        return FakeConnectContext(self.connection)


class LibraryResetRepositoryTest(unittest.TestCase):
    """Valide les requetes du repository de reset Bibliotheque."""

    def test_clean_library_tables_preserves_platform_catalog(self):
        """Verifie que le reset conserve le referentiel plateformes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'ordre SQL.
        """

        connection = FakeConnection()
        cache = PlatformCatalogCache()
        cache.remember("public", lambda: [{"id": 1, "name": "Switch"}])
        repository = SqlAlchemyLibraryResetRepository(
            FakeDatabaseConfiguration(),
            engine=FakeEngine(connection),
            platform_catalog_cache=cache,
        )

        repository.clean_library_tables()

        executed_sql = "\n".join(connection.executed_sql)
        self.assertLess(executed_sql.index("t_user_collection"), executed_sql.index("t_game"))
        self.assertLess(executed_sql.index("t_game"), executed_sql.index("t_studio"))
        self.assertNotIn("t_platform", executed_sql)
        self.assertEqual(0, cache.invalidate("public"))

    def test_clean_library_tables_rolls_back_on_error(self):
        """Verifie le rollback implicite quand le clean echoue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la transaction.
        """

        repository = SqlAlchemyLibraryResetRepository(
            FakeDatabaseConfiguration(),
            engine=FakeEngine(FakeConnection(error_on_execute=RuntimeError("db"))),
        )

        with self.assertRaises(RuntimeError):
            repository.clean_library_tables()

        self.assertTrue(repository.engine.transaction.rolled_back)

    def test_list_importable_users_orders_and_maps_rows(self):
        """Verifie la lecture des utilisateurs importables.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le mapping.
        """

        connection = FakeConnection(
            rows=[
                {
                    "id": 7,
                    "email": "user@example.com",
                    "collection_file_path": "/users/workspace/7/7-collection.ods",
                    "collection_file_description": {"file_type": "libreoffice_ods"},
                    "profile": "USER",
                    "status": "ACTIVE",
                    "creation_date": datetime(2026, 5, 1, 12),
                }
            ]
        )
        repository = SqlAlchemyLibraryResetRepository(
            FakeDatabaseConfiguration(),
            engine=FakeEngine(connection),
        )

        users = repository.list_importable_users()

        self.assertEqual(1, len(users))
        self.assertEqual(7, users[0].id)
        self.assertIn("collection_file_path IS NOT NULL", connection.executed_sql[0])
        self.assertIn("ORDER BY creation_date ASC, id ASC", connection.executed_sql[0])


if __name__ == "__main__":
    unittest.main()
