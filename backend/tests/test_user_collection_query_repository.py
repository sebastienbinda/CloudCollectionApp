#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-25
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du repository de consultation collection.

import unittest

from services.collection import UserCollectionQueryParser
from services.database import SqlAlchemyUserCollectionQueryRepository


class FakeRepositoryResult:
    """Resultat SQL factice compatible avec les appels du repository."""

    def __init__(self, scalar_value=0, rows=None):
        """Initialise le resultat factice.

        Args:
            scalar_value (int | str | None): Valeur scalaire retournee.
            rows (list[dict] | None): Lignes retournees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.scalar_value = scalar_value
        self.rows = rows or []

    def scalar_one(self):
        """Retourne la valeur scalaire configuree.

        Args:
            Aucun.

        Returns:
            int | str | None: Valeur scalaire configuree.
        """

        return self.scalar_value

    def scalar_one_or_none(self):
        """Retourne la valeur scalaire optionnelle configuree.

        Args:
            Aucun.

        Returns:
            int | str | None: Valeur scalaire configuree.
        """

        return self.scalar_value

    def mappings(self):
        """Retourne les lignes configurees.

        Args:
            Aucun.

        Returns:
            list[dict]: Lignes de resultat.
        """

        return self.rows


class FakeRepositoryConnection:
    """Connexion SQLAlchemy factice capturant les requetes executees."""

    def __init__(self, scalar_value=0, rows=None):
        """Initialise la connexion factice.

        Args:
            scalar_value (int | str | None): Valeur scalaire retournee.
            rows (list[dict] | None): Lignes retournees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.scalar_value = scalar_value
        self.rows = rows or []
        self.executed_statements = []

    def execute(self, statement, parameters=None):
        """Capture une requete SQL et ses parametres.

        Args:
            statement (object): Requete SQLAlchemy recue.
            parameters (dict | None): Parametres associes a la requete.

        Returns:
            FakeRepositoryResult: Resultat SQL factice.
        """

        self.executed_statements.append((str(statement), parameters or {}))
        return FakeRepositoryResult(self.scalar_value, self.rows)


class UserCollectionQueryRepositoryTest(unittest.TestCase):
    """Valide les requetes SQL de consultation collection utilisateur."""

    def setUp(self):
        """Prepare le repository et le parseur testes.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.query_parser = UserCollectionQueryParser()
        self.repository = SqlAlchemyUserCollectionQueryRepository("collection")

    def test_statistics_queries_are_filtered_by_user(self):
        """Verifie les requetes de statistiques utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les filtres SQL.
        """

        count_connection = FakeRepositoryConnection(scalar_value=7)
        max_connection = FakeRepositoryConnection(scalar_value="Switch")

        self.assertEqual(7, self.repository.count_collection_games(count_connection, 12))
        self.assertEqual("Switch", self.repository.find_max_platform_name(max_connection, 12))

        count_sql, count_parameters = count_connection.executed_statements[0]
        max_sql, max_parameters = max_connection.executed_statements[0]
        self.assertIn("t_user_collection", count_sql)
        self.assertIn("WHERE user_id = :user_id", count_sql)
        self.assertIn("JOIN", max_sql)
        self.assertIn("t_platform", max_sql)
        self.assertIn("user_collection.user_id = :user_id", max_sql)
        self.assertEqual({"user_id": 12}, count_parameters)
        self.assertEqual({"user_id": 12}, max_parameters)

    def test_list_platforms_filters_by_user_name_sort_and_pagination(self):
        """Verifie la liste paginee des plateformes utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la requete generee.
        """

        criteria = self.query_parser.parse_platforms(
            {"name": " École ", "page": "2", "size": "25", "sort": "name,desc"}
        )
        connection = FakeRepositoryConnection(rows=[{"id": 1, "name": "Switch", "nb_games": 3}])

        rows = self.repository.list_platforms(connection, 12, criteria)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual([{"id": 1, "name": "Switch", "nb_games": 3}], rows)
        self.assertIn("COUNT(game.id) AS nb_games", sql)
        self.assertIn("user_collection.user_id = :user_id", sql)
        self.assertIn("TRANSLATE(LOWER(platform.name)", sql)
        self.assertIn("GROUP BY platform.id, platform.name", sql)
        self.assertIn("ORDER BY platform.name DESC", sql)
        self.assertEqual(12, parameters["user_id"])
        self.assertEqual("%ecole%", parameters["platform_name_pattern"])
        self.assertEqual(25, parameters["limit"])
        self.assertEqual(50, parameters["offset"])

    def test_list_games_applies_all_filters_and_allowed_sort(self):
        """Verifie la liste paginee des jeux utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident filtres, tri et isolation utilisateur.
        """

        criteria = self.query_parser.parse_games(
            {
                "name": " Zelda ",
                "studio_name": " Équipe ",
                "platform_name": " Switch ",
                "platform_id": "5",
                "release_date": "1986-01-01..1986-12-31",
                "sort": ["studio_name,desc", "grade,asc"],
            }
        )
        connection = FakeRepositoryConnection(rows=[{"id": 3, "name": "Zelda"}])

        self.repository.list_games(connection, 12, criteria)

        sql, parameters = connection.executed_statements[0]
        self.assertIn("t_user_collection", sql)
        self.assertIn("t_game", sql)
        self.assertIn("t_platform", sql)
        self.assertIn("t_studio", sql)
        self.assertIn("user_collection.user_id = :user_id", sql)
        self.assertIn("TRANSLATE(LOWER(game.name)", sql)
        self.assertIn("TRANSLATE(LOWER(studio.name)", sql)
        self.assertIn("TRANSLATE(LOWER(platform.name)", sql)
        self.assertIn("platform.id = :platform_id", sql)
        self.assertIn("game.release_date >= :release_date_from", sql)
        self.assertIn("game.release_date <= :release_date_to", sql)
        self.assertIn("ORDER BY studio.name DESC, NULL ASC, game.name ASC", sql)
        self.assertEqual(12, parameters["user_id"])
        self.assertEqual(5, parameters["platform_id"])
        self.assertEqual("%zelda%", parameters["name_pattern"])
        self.assertEqual("%equipe%", parameters["studio_name_pattern"])
        self.assertEqual("%switch%", parameters["platform_name_pattern"])
        self.assertEqual("1986-01-01", parameters["release_date_from"].isoformat())
        self.assertEqual("1986-12-31", parameters["release_date_to"].isoformat())

    def test_count_games_uses_same_filters_without_pagination(self):
        """Verifie le compteur des jeux utilisateur filtres.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence de pagination.
        """

        criteria = self.query_parser.parse_games({"platform_id": "5"})
        connection = FakeRepositoryConnection(scalar_value=2)

        count = self.repository.count_games_by_criteria(connection, 12, criteria)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(2, count)
        self.assertIn("SELECT COUNT(*)", sql)
        self.assertIn("platform.id = :platform_id", sql)
        self.assertNotIn("LIMIT", sql)
        self.assertEqual(12, parameters["user_id"])
        self.assertEqual(5, parameters["platform_id"])


if __name__ == "__main__":
    unittest.main()
