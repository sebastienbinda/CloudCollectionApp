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


class FakeMappingResult:
    """Resultat SQL factice retournant des lignes mapping."""

    def __init__(self, rows):
        """Initialise le resultat mapping.

        Args:
            rows (list[dict]): Lignes retournees par `mappings`.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.rows = rows

    def mappings(self):
        """Retourne les lignes mapping configurees.

        Args:
            Aucun.

        Returns:
            list[dict]: Lignes SQL factices.
        """

        return self.rows


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
        self.mapping_results = []

    def execute(self, statement, parameters=None):
        """Capture une requete SQL et ses parametres.

        Args:
            statement (object): Requete SQLAlchemy recue.
            parameters (dict | None): Parametres associes a la requete.

        Returns:
            FakeScalarResult: Resultat factice compatible avec `scalar_one`.
        """

        self.executed_statements.append((str(statement), parameters))
        if self.mapping_results:
            return FakeMappingResult(self.mapping_results.pop(0))
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
        """Verifie que l'insertion SQL utilise les colonnes attendues.

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
        self.assertIn("duplicate_flag", sql)
        self.assertIn("FALSE", sql)
        self.assertEqual("Chrono Trigger", parameters["name"])
        self.assertEqual(11, parameters["developer"])

    def test_insert_standardizes_new_game_name(self):
        """Verifie que les nouveaux jeux sont stockes avec un nom standardise.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le parametre SQL `name`.
        """

        connection = FakeConnection()
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )
        game = OdsCollectionImportGame(
            name="oddworld:L'odyssée d'abe",
            platform_name="PlayStation",
            studio_name="Oddworld Inhabitants",
            release_date=None,
        )

        repository.insert(connection, game, platform_id=7, studio_id=11)

        _sql, parameters = connection.executed_statements[0]
        self.assertEqual("Oddworld : L'Odyssée d'Abe", parameters["name"])

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

    def test_load_references_includes_game_aliases_without_overriding_direct_names(self):
        """Verifie que les alias de doublons sont reutilisables au matching.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les cles de reference.
        """

        connection = FakeConnection()
        connection.mapping_results = [
            [
                {
                    "id": 1,
                    "name": "Sonic",
                    "release_date": date(1991, 6, 23),
                    "platform_name": "Mega Drive",
                },
                {
                    "id": 2,
                    "name": "Sonic the edgedog",
                    "release_date": date(1992, 11, 21),
                    "platform_name": "Mega Drive",
                },
            ],
            [
                {
                    "id": 1,
                    "name": "Sonic",
                    "release_date": date(1991, 6, 23),
                    "alias_name": "Sonic the edgedog",
                    "platform_name": "Mega Drive",
                }
            ],
        ]
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )

        references = repository.load_references_by_key(connection)

        self.assertEqual(
            (1, "Sonic", date(1991, 6, 23)),
            references[("mega drive", "sonic")],
        )
        self.assertEqual(
            (2, "Sonic the edgedog", date(1992, 11, 21)),
            references[("mega drive", "sonic the edgedog")],
        )


if __name__ == "__main__":
    unittest.main()
