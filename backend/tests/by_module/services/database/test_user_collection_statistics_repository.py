#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-07-05
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du repository de statistiques detaillees.

import unittest

from services.database.user_collection_statistics_repository import (
    SqlAlchemyUserCollectionStatisticsRepository,
)


class FakeRepositoryResult:
    """Resultat SQL factice."""

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
    """Connexion factice capturant les requetes SQL."""

    def __init__(self, rows=None):
        """Initialise la connexion factice.

        Args:
            rows (list[dict] | None): Lignes retournees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.rows = rows or []
        self.executed_statements = []

    def execute(self, statement, parameters=None):
        """Capture une requete SQL et ses parametres.

        Args:
            statement (object): Requete recue.
            parameters (dict | None): Parametres SQL.

        Returns:
            FakeRepositoryResult: Resultat configure.
        """

        self.executed_statements.append((str(statement), parameters or {}))
        return FakeRepositoryResult(self.rows)


class UserCollectionStatisticsRepositoryTest(unittest.TestCase):
    """Valide les requetes de statistiques detaillees."""

    def setUp(self):
        """Prepare le repository teste.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.repository = SqlAlchemyUserCollectionStatisticsRepository("collection")

    def test_list_platform_distribution_filters_owned_collection(self):
        """Verifie la repartition par plateforme hors wishlist.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la requete SQL.
        """

        connection = FakeRepositoryConnection(rows=[{"platform_id": 1}])

        self.repository.list_platform_distribution(connection, 12)

        sql, parameters = connection.executed_statements[0]
        self.assertIn('FROM "collection".t_user_collection', sql)
        self.assertIn("JOIN", sql)
        self.assertIn("user_collection.user_id = :user_id", sql)
        self.assertIn("user_collection.wishlist = FALSE", sql)
        self.assertIn("GROUP BY platform.id, platform.name", sql)
        self.assertEqual({"user_id": 12}, parameters)

    def test_year_distributions_filter_null_dates(self):
        """Verifie les distributions temporelles.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les colonnes utilisees.
        """

        release_connection = FakeRepositoryConnection(rows=[{"year": 1992}])
        purchase_connection = FakeRepositoryConnection(rows=[{"year": 2024}])

        self.repository.list_release_year_distribution(release_connection, 12)
        self.repository.list_purchase_year_distribution(purchase_connection, 12)

        release_sql, _ = release_connection.executed_statements[0]
        purchase_sql, _ = purchase_connection.executed_statements[0]
        self.assertIn("EXTRACT(YEAR FROM game.release_date)", release_sql)
        self.assertIn("game.release_date IS NOT NULL", release_sql)
        self.assertIn("EXTRACT(YEAR FROM user_collection.buy_date)", purchase_sql)
        self.assertIn("user_collection.buy_date IS NOT NULL", purchase_sql)

    def test_year_distributions_can_filter_platform(self):
        """Verifie le filtre optionnel par plateforme des distributions temporelles.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le filtre SQL.
        """

        connection = FakeRepositoryConnection(rows=[{"year": 1992}])

        self.repository.list_release_year_distribution(connection, 12, platform_id=3)

        sql, parameters = connection.executed_statements[0]
        self.assertIn("AND game.platform = :platform_id", sql)
        self.assertEqual({"user_id": 12, "platform_id": 3}, parameters)

    def test_list_top_rated_games_filters_normalized_grade_at_least_ninety(self):
        """Verifie le filtrage SQL des jeux les mieux notes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le seuil de note.
        """

        connection = FakeRepositoryConnection(rows=[{"id": 3}])

        self.repository.list_top_rated_games(connection, 12)

        sql, parameters = connection.executed_statements[0]
        self.assertIn("user_collection.grade", sql)
        self.assertIn("user_collection.grade_normalized", sql)
        self.assertIn("user_collection.grade_normalized >= 90", sql)
        self.assertIn("ORDER BY user_collection.grade_normalized DESC", sql)
        self.assertIn("user_collection.wishlist = FALSE", sql)
        self.assertEqual({"user_id": 12}, parameters)

    def test_list_top_rated_games_can_filter_platform(self):
        """Verifie le filtre plateforme applique aux meilleurs jeux.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les parametres SQL.
        """

        connection = FakeRepositoryConnection(rows=[{"id": 3}])

        self.repository.list_top_rated_games(connection, 12, platform_id=7)

        sql, parameters = connection.executed_statements[0]
        self.assertIn("AND game.platform = :platform_id", sql)
        self.assertEqual({"user_id": 12, "platform_id": 7}, parameters)


if __name__ == "__main__":
    unittest.main()
