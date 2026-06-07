#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du repository de fichier de collection utilisateur.

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.database.user_collection_file_repository import (  # noqa: E402
    SqlAlchemyUserCollectionFileRepository,
)


class FakeConnection:
    """Connexion factice capturant la derniere requete executee."""

    def __init__(self, rows=None):
        """Initialise la connexion factice.

        Args:
            rows (list[dict] | None): Lignes retournees par les SELECT.

        Returns:
            None: La connexion capture les executions.
        """

        self.executed_statements = []
        self.rows = rows or []

    def execute(self, statement, parameters=None):
        """Capture une execution SQL.

        Args:
            statement (object): Requete SQLAlchemy recue.
            parameters (dict | None): Parametres lies.

        Returns:
            object: Resultat factice compatible avec le repository.
        """

        self.executed_statements.append((str(statement), parameters or {}))
        return FakeResult(self.rows)


class FakeResult:
    """Resultat SQL factice compatible avec `mappings`."""

    def __init__(self, rows=None):
        """Initialise le resultat factice.

        Args:
            rows (list[dict] | None): Lignes retournees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.rows = rows or []

    def mappings(self):
        """Retourne le resultat courant.

        Args:
            Aucun.

        Returns:
            FakeResult: Resultat courant.
        """

        return self

    def first(self):
        """Retourne la premiere ligne.

        Args:
            Aucun.

        Returns:
            dict | None: Premiere ligne ou absence.
        """

        return self.rows[0] if self.rows else None


class UserCollectionFileRepositoryTest(unittest.TestCase):
    """Valide la persistance du fichier et de sa description."""

    def test_update_collection_file_updates_path_and_description_together(self):
        """Verifie la mise a jour atomique des colonnes d'import.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident SQL et parametres.
        """

        repository = SqlAlchemyUserCollectionFileRepository("collection")
        connection = FakeConnection()
        description = {"file_type": "libreoffice_ods"}

        repository.update_collection_file(
            connection,
            7,
            "/users/workspace/7/7-collection.ods",
            description,
        )

        sql, parameters = connection.executed_statements[0]
        self.assertIn("collection_file_path = :collection_file_path", sql)
        self.assertIn("collection_file_description = :collection_file_description", sql)
        self.assertEqual(7, parameters["user_id"])
        self.assertEqual("/users/workspace/7/7-collection.ods", parameters["collection_file_path"])
        self.assertEqual(description, parameters["collection_file_description"])

    def test_lock_user_collection_state_returns_existing_path(self):
        """Verifie la lecture verrouillee du chemin de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident SQL et resultat.
        """

        repository = SqlAlchemyUserCollectionFileRepository("collection")
        connection = FakeConnection(
            [{"collection_file_path": "/users/workspace/7/7-collection.ods"}]
        )

        collection_file_path = repository.lock_user_collection_state(connection, 7)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual("/users/workspace/7/7-collection.ods", collection_file_path)
        self.assertIn("FOR UPDATE", sql)
        self.assertEqual({"user_id": 7}, parameters)

    def test_clear_collection_file_sets_path_and_description_to_null(self):
        """Verifie le nettoyage des colonnes collection utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident SQL et parametres.
        """

        repository = SqlAlchemyUserCollectionFileRepository("collection")
        connection = FakeConnection()

        repository.clear_collection_file(connection, 7)

        sql, parameters = connection.executed_statements[0]
        self.assertIn("collection_file_path = NULL", sql)
        self.assertIn("collection_file_description = NULL", sql)
        self.assertEqual({"user_id": 7}, parameters)


if __name__ == "__main__":
    unittest.main()
