#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-03
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du repository d'associations utilisateur-collection.

import unittest

from services.database import SqlAlchemyUserCollectionRepository, UserGameAssociation


class FakeRepositoryResult:
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
        """Retourne les lignes configurees.

        Args:
            Aucun.

        Returns:
            list[dict]: Lignes de resultat.
        """

        return self.rows


class FakeRepositoryConnection:
    """Connexion SQL factice capturant les requetes executees."""

    def __init__(self, existing_wishlist_values=None):
        """Initialise la connexion factice.

        Args:
            existing_wishlist_values (dict[int, bool] | None): Valeurs wishlist existantes.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.existing_wishlist_values = existing_wishlist_values or {}
        self.executed_statements = []

    def execute(self, statement, parameters=None):
        """Capture une requete SQL.

        Args:
            statement (object): Requete SQLAlchemy recue.
            parameters (dict | None): Parametres SQL.

        Returns:
            FakeRepositoryResult: Resultat compatible avec le repository.
        """

        sql = str(statement)
        self.executed_statements.append((sql, parameters or {}))
        if sql.strip().startswith("SELECT"):
            return FakeRepositoryResult(
                [
                    {"game_id": game_id, "wishlist": wishlist}
                    for game_id, wishlist in sorted(self.existing_wishlist_values.items())
                ]
            )
        return FakeRepositoryResult()


class UserCollectionRepositoryTest(unittest.TestCase):
    """Valide la persistance des associations utilisateur-jeu."""

    def setUp(self):
        """Prepare le repository teste.

        Args:
            Aucun.

        Returns:
            None: Le repository est initialise.
        """

        self.repository = SqlAlchemyUserCollectionRepository("collection")

    def test_creates_association_with_wishlist_false_by_default(self):
        """Verifie l'insertion par defaut avec wishlist=false."""

        connection = FakeRepositoryConnection()

        count = self.repository.ensure_user_game_associations(connection, 7, [42])

        insert_sql, parameters = connection.executed_statements[1]
        self.assertEqual(1, count)
        self.assertIn("wishlist", insert_sql)
        self.assertEqual({"user_id": 7, "game_id": 42, "wishlist": False}, parameters)

    def test_reads_existing_wishlist_values(self):
        """Verifie la lecture des valeurs wishlist existantes."""

        connection = FakeRepositoryConnection(existing_wishlist_values={42: True, 43: False})

        values = self.repository.find_user_game_wishlist_values(connection, 7)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual({42: True, 43: False}, values)
        self.assertIn("SELECT game_id, wishlist", sql)
        self.assertEqual({"user_id": 7}, parameters)

    def test_creates_association_with_wishlist_true(self):
        """Verifie l'insertion d'un souhait."""

        connection = FakeRepositoryConnection()

        count = self.repository.ensure_user_game_associations(
            connection,
            7,
            [UserGameAssociation(42, True)],
        )

        _, parameters = connection.executed_statements[1]
        self.assertEqual(1, count)
        self.assertEqual({"user_id": 7, "game_id": 42, "wishlist": True}, parameters)

    def test_does_not_duplicate_existing_user_game_association(self):
        """Verifie qu'une association existante n'est pas reinseree."""

        connection = FakeRepositoryConnection(existing_wishlist_values={42: False})

        count = self.repository.ensure_user_game_associations(
            connection,
            7,
            [UserGameAssociation(42, True)],
        )

        self.assertEqual(1, count)
        self.assertEqual(1, len(connection.executed_statements))
        self.assertIn("SELECT game_id, wishlist", connection.executed_statements[0][0])


if __name__ == "__main__":
    unittest.main()
