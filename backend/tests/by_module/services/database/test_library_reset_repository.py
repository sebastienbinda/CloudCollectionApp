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

from services.database import (
    LibraryResetPlatformImageSnapshot,
    PlatformCatalogCache,
    SqlAlchemyLibraryResetRepository,
)


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

    def __init__(self, rows=None, error_on_execute=None, rows_by_query=None, rowcount=1):
        """Initialise la connexion.

        Args:
            rows (list[dict] | None): Lignes retournees.
            error_on_execute (Exception | None): Erreur a lever.
            rows_by_query (dict | None): Lignes retournees selon un fragment SQL.
            rowcount (int): Nombre de lignes modifiees retourne.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.rows = rows or []
        self.error_on_execute = error_on_execute
        self.rows_by_query = rows_by_query or {}
        self.rowcount = rowcount
        self.executed_sql = []
        self.executed_parameters = []

    def execute(self, statement, parameters=None):
        """Memorise le SQL execute.

        Args:
            statement (object): Statement SQLAlchemy.
            parameters (dict | None): Parametres SQL.

        Returns:
            FakeResult: Resultat factice.

        Raises:
            Exception: Erreur configuree.
        """

        sql = str(statement)
        self.executed_sql.append(sql)
        self.executed_parameters.append(parameters or {})
        if self.error_on_execute:
            raise self.error_on_execute
        for query_fragment, rows in self.rows_by_query.items():
            if query_fragment in sql:
                return FakeResult(rows, self.rowcount)
        return FakeResult(self.rows, self.rowcount)


class FakeResult:
    """Resultat SQL factice."""

    def __init__(self, rows, rowcount=1):
        """Initialise le resultat.

        Args:
            rows (list[dict]): Lignes retournees.
            rowcount (int): Nombre de lignes modifiees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.rows = rows
        self.rowcount = rowcount

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

    def test_clean_library_tables_removes_platform_catalog_before_reimport(self):
        """Verifie que le reset vide aussi le referentiel plateformes.

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

        snapshots = repository.clean_library_tables()

        deleted_tables = [self._deleted_table_name(sql) for sql in connection.executed_sql]
        self.assertEqual([], snapshots)
        self.assertLess(deleted_tables.index("t_user_collection"), deleted_tables.index("t_game"))
        self.assertLess(deleted_tables.index("t_game"), deleted_tables.index("t_studio"))
        self.assertLess(deleted_tables.index("t_game"), deleted_tables.index("t_platform"))
        self.assertLess(deleted_tables.index("t_platform_image"), deleted_tables.index("t_platform"))
        self.assertLess(deleted_tables.index("t_platform_alias"), deleted_tables.index("t_platform"))
        self.assertIn("t_platform", deleted_tables)
        self.assertEqual(0, cache.invalidate("public"))

    def test_clean_library_tables_returns_platform_image_snapshots(self):
        """Verifie la sauvegarde des images de plateformes avant suppression.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les snapshots.
        """

        connection = FakeConnection(
            rows_by_query={
                "FROM \"public\".t_platform_image image": [
                    {
                        "platform_name": "Switch",
                        "path": "/images/switch.png",
                        "file_size_bytes": 42,
                        "type": "MAIN",
                        "status": "ACCEPTED",
                        "user_id": 7,
                        "creation_date": datetime(2026, 6, 1, 12),
                    }
                ]
            }
        )
        repository = SqlAlchemyLibraryResetRepository(
            FakeDatabaseConfiguration(),
            engine=FakeEngine(connection),
        )

        snapshots = repository.clean_library_tables()

        self.assertEqual(1, len(snapshots))
        self.assertEqual("Switch", snapshots[0].platform_name)
        self.assertEqual("/images/switch.png", snapshots[0].path)
        self.assertEqual(42, snapshots[0].file_size_bytes)

    def test_restore_platform_images_uses_recreated_platform_name_or_alias(self):
        """Verifie la reassociation des images par nom ou alias de plateforme.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les insertions.
        """

        connection = FakeConnection(
            rows_by_query={
                "SELECT id, name FROM \"public\".t_platform": [
                    {"id": 10, "name": "Switch"},
                    {"id": 11, "name": "Super Nintendo"},
                ],
                "SELECT platform, name FROM \"public\".t_platform_alias": [
                    {"platform": 11, "name": "Super Famicom"},
                ],
            }
        )
        repository = SqlAlchemyLibraryResetRepository(
            FakeDatabaseConfiguration(),
            engine=FakeEngine(connection),
        )
        snapshots = [
            LibraryResetPlatformImageSnapshot(
                "Switch",
                "/images/switch.png",
                42,
                "MAIN",
                "ACCEPTED",
                7,
                datetime(2026, 6, 1, 12),
            ),
            LibraryResetPlatformImageSnapshot(
                "Super Famicom",
                "/images/sfc.png",
                43,
                "OTHER",
                "WAITING_VALIDATION",
                8,
                datetime(2026, 6, 2, 12),
            ),
        ]

        restored_count = repository.restore_platform_images(snapshots)

        insert_parameters = [
            parameters
            for sql, parameters in zip(connection.executed_sql, connection.executed_parameters)
            if "INSERT INTO" in sql and "t_platform_image" in sql
        ]
        self.assertEqual(2, restored_count)
        self.assertEqual([10, 11], [parameters["platform"] for parameters in insert_parameters])
        self.assertEqual(["/images/switch.png", "/images/sfc.png"], [
            parameters["path"] for parameters in insert_parameters
        ])

    @staticmethod
    def _deleted_table_name(sql: str) -> str:
        """Extrait le nom de table d'un `DELETE FROM` de test.

        Args:
            sql (str): Requete SQL capturee.

        Returns:
            str: Nom de table cible.
        """

        return sql.rsplit(".", maxsplit=1)[-1]

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
