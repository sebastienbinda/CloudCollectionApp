#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-24
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires des repositories d'entites Bibliotheque.

import unittest

from services.database import (
    SqlAlchemyGameRepository,
    SqlAlchemyPlatformRepository,
    SqlAlchemyStudioRepository,
)
from services.library import LibraryQueryParser
from services.users import UserCollectionNameNormalizer


class FakeRepositoryResult:
    """Resultat SQL factice compatible avec les appels des repositories."""

    def __init__(self, scalar_value=0, rows=None):
        """Initialise le resultat factice.

        Args:
            scalar_value (int): Valeur retournee par `scalar_one`.
            rows (list[dict] | None): Lignes retournees par `mappings`.

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
            int: Valeur scalaire configuree.
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
            scalar_value (int): Valeur scalaire retournee.
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


class LibraryEntityRepositoriesTest(unittest.TestCase):
    """Valide les methodes de consultation publique des repositories."""

    def setUp(self):
        """Prepare les repositories et le parseur testes.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        normalizer = UserCollectionNameNormalizer()
        self.query_parser = LibraryQueryParser(normalizer)
        self.platform_repository = SqlAlchemyPlatformRepository("collection", normalizer)
        self.studio_repository = SqlAlchemyStudioRepository("collection", normalizer)
        self.game_repository = SqlAlchemyGameRepository("collection", normalizer)

    def test_count_public_library_entities_reads_only_reference_tables(self):
        """Verifie les compteurs globaux des entites de reference.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les tables lues.
        """

        connection = FakeRepositoryConnection(scalar_value=7)

        self.assertEqual(7, self.platform_repository.count_public_library_platforms(connection))
        self.assertEqual(7, self.studio_repository.count_public_library_studios(connection))
        self.assertEqual(7, self.game_repository.count_public_library_games(connection))

        executed_sql = "\n".join(statement for statement, _ in connection.executed_statements)
        self.assertIn("t_platform", executed_sql)
        self.assertIn("t_studio", executed_sql)
        self.assertIn("t_game", executed_sql)
        self.assertNotIn("t_user", executed_sql)
        self.assertNotIn("t_user_collection", executed_sql)

    def test_list_public_library_platforms_applies_filter_sort_and_pagination(self):
        """Verifie la liste publique des plateformes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la requete generee.
        """

        criteria = self.query_parser.parse(
            "platforms",
            {"name": " École ", "page": "2", "size": "25", "sort": "manufacturer,desc"},
        )
        connection = FakeRepositoryConnection(
            rows=[{"id": 1, "name": "Switch", "total_games": 12}]
        )

        rows = self.platform_repository.list_public_library_platforms(connection, criteria)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual([{"id": 1, "name": "Switch", "total_games": 12}], rows)
        self.assertIn("COUNT(game.id) AS total_games", sql)
        self.assertIn("LEFT JOIN", sql)
        self.assertIn("t_game", sql)
        self.assertIn("TRANSLATE(LOWER(platform.name)", sql)
        self.assertIn("ORDER BY platform.manufacturer DESC, platform.name ASC", sql)
        self.assertEqual("%ecole%", parameters["name_pattern"])
        self.assertEqual(25, parameters["limit"])
        self.assertEqual(50, parameters["offset"])
        self.assertNotIn("t_user", sql)

    def test_list_public_library_studios_counts_editor_and_developer_games(self):
        """Verifie la liste publique des studios.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les compteurs de jeux.
        """

        criteria = self.query_parser.parse(
            "studios",
            {"sort": ["country,asc", "creation_date,desc"]},
        )
        connection = FakeRepositoryConnection(rows=[{"id": 2, "name": "Square"}])

        self.studio_repository.list_public_library_studios(connection, criteria)

        sql, parameters = connection.executed_statements[0]
        self.assertIn("COUNT(DISTINCT editor_game.id) AS editor_total_games", sql)
        self.assertIn("COUNT(DISTINCT developer_game.id) AS developer_total_games", sql)
        self.assertIn("editor_game.editor = studio.id", sql)
        self.assertIn("developer_game.developer = studio.id", sql)
        self.assertIn("ORDER BY studio.country ASC, studio.creation_date DESC, studio.name ASC", sql)
        self.assertEqual(500, parameters["limit"])
        self.assertEqual(0, parameters["offset"])
        self.assertNotIn("t_user", sql)

    def test_list_public_library_games_returns_related_entity_names(self):
        """Verifie la liste publique des jeux.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les jointures de noms.
        """

        criteria = self.query_parser.parse(
            "games",
            {"name": "Final", "sort": "developer,desc"},
        )
        connection = FakeRepositoryConnection(rows=[{"id": 3, "name": "Final Fantasy"}])

        self.game_repository.list_public_library_games(connection, criteria)

        sql, parameters = connection.executed_statements[0]
        self.assertIn("developer_studio.name AS developer", sql)
        self.assertIn("editor_studio.name AS editor", sql)
        self.assertIn("platform.name AS platform", sql)
        self.assertIn("developer_studio.id = game.developer", sql)
        self.assertIn("editor_studio.id = game.editor", sql)
        self.assertIn("platform.id = game.platform", sql)
        self.assertIn("ORDER BY developer_studio.name DESC, game.name ASC", sql)
        self.assertEqual("%final%", parameters["name_pattern"])
        self.assertNotIn("t_user", sql)

    def test_count_public_library_entities_by_criteria_uses_bound_name_filter(self):
        """Verifie les compteurs filtres par nom sans interpolation brute.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les parametres bindes.
        """

        criteria = self.query_parser.parse("games", {"name": " Zelda "})
        connection = FakeRepositoryConnection(scalar_value=4)

        count = self.game_repository.count_public_library_games_by_criteria(
            connection,
            criteria,
        )

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(4, count)
        self.assertIn("TRANSLATE(LOWER(game.name)", sql)
        self.assertIn(":name_pattern", sql)
        self.assertNotIn("Zelda", sql)
        self.assertEqual("%zelda%", parameters["name_pattern"])


if __name__ == "__main__":
    unittest.main()
