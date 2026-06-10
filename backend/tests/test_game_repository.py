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
# Description : tests unitaires du repository SQL des jeux.

import unittest
from datetime import date

from services.database import DatabaseModelBase, SqlAlchemyGameRepository
from services.ods import OdsCollectionImportGame
from services.users import UserCollectionNameNormalizer


class FakeScalarResult:
    """Resultat SQL factice retournant une seule valeur scalaire."""

    def __init__(self, value):
        """Initialise le resultat SQL factice.

        Args:
            value (object): Valeur retournee par `scalar_one`.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.value = value

    def scalar_one(self):
        """Retourne la valeur scalaire configuree.

        Args:
            Aucun.

        Returns:
            object: Valeur scalaire configuree pour le test.
        """

        return self.value


class FakeConnection:
    """Connexion SQLAlchemy factice capturant les requetes executees."""

    def __init__(self):
        """Initialise la connexion factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.executed_statements = []

    def execute(self, statement, parameters=None):
        """Capture une requete SQL et ses parametres.

        Args:
            statement (object): Requete SQLAlchemy recue.
            parameters (dict | None): Parametres associes a la requete.

        Returns:
            FakeScalarResult: Resultat factice compatible avec `scalar_one`.
        """

        self.executed_statements.append((str(statement), parameters))
        return FakeScalarResult(42)


class GameRepositoryTest(unittest.TestCase):
    """Valide le repository SQL des jeux."""

    def test_game_model_exposes_developer_column(self):
        """Verifie que le modele ORM expose la colonne `developer`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le nom de colonne ORM.
        """

        game_table = DatabaseModelBase.metadata.tables["t_game"]

        self.assertEqual("developer", game_table.columns["developer"].name)

    def test_insert_uses_developer_column_and_parameter(self):
        """Verifie que l'insertion SQL utilise le nom `developer`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la requete et les parametres SQL.
        """

        connection = FakeConnection()
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )
        game = OdsCollectionImportGame(
            name="Chrono Trigger",
            platform_name="Super Nintendo",
            studio_name="Square",
            release_date=None,
        )

        game_id = repository.insert(connection, game, platform_id=7, studio_id=11)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(42, game_id)
        self.assertIn("developer", sql)
        self.assertEqual(11, parameters["developer"])

    def test_insert_ignores_unpersistable_release_date(self):
        """Verifie qu'une date hors plage n'est jamais envoyee a PostgreSQL.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le parametre SQL `release_date`.
        """

        connection = FakeConnection()
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )
        game = OdsCollectionImportGame(
            name="Chrono Trigger",
            platform_name="Super Nintendo",
            studio_name="Square",
            release_date="48113-11-21 00:00:01",
        )

        repository.insert(connection, game, platform_id=7, studio_id=11)

        _sql, parameters = connection.executed_statements[0]
        self.assertIsNone(parameters["release_date"])

    def test_insert_ignores_too_old_release_date(self):
        """Verifie qu'une date trop ancienne n'est jamais envoyee a PostgreSQL.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le parametre SQL `release_date`.
        """

        connection = FakeConnection()
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )
        game = OdsCollectionImportGame(
            name="Penny Blood",
            platform_name="Super Nintendo",
            studio_name="Square",
            release_date=date(200, 11, 24),
        )

        repository.insert(connection, game, platform_id=7, studio_id=11)

        _sql, parameters = connection.executed_statements[0]
        self.assertIsNone(parameters["release_date"])


if __name__ == "__main__":
    unittest.main()
