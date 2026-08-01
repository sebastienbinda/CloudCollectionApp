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
from services.database.game_repository import (
    GAME_STATUS_ACCEPTED,
    GAME_STATUS_WAITING_VALIDATION,
)
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
            FakeMappingResult: Resultat iterable compatible SQLAlchemy.
        """

        return self

    def first(self):
        """Retourne la premiere ligne mapping disponible.

        Args:
            Aucun.

        Returns:
            dict | None: Premiere ligne ou absence.
        """

        return self.rows[0] if self.rows else None

    def __iter__(self):
        """Itere sur les lignes mapping configurees.

        Args:
            Aucun.

        Returns:
            iterator: Iterateur des lignes factices.
        """

        return iter(self.rows)


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

    def test_game_model_exposes_validation_status_column(self):
        """Verifie que le modele ORM expose le statut de validation.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident colonne, defaut et contrainte ORM.
        """

        game_table = DatabaseModelBase.metadata.tables["t_game"]

        self.assertEqual("status", game_table.columns["status"].name)
        self.assertFalse(game_table.columns["status"].nullable)
        self.assertEqual(32, game_table.columns["status"].type.length)
        self.assertEqual("'ACCEPTED'", str(game_table.columns["status"].server_default.arg))
        self.assertIn("ck_t_game_status", {constraint.name for constraint in game_table.constraints})

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

        game_id = repository.insert(
            connection,
            game,
            platform_id=7,
            studio_id=11,
            initial_validation_status=GAME_STATUS_WAITING_VALIDATION,
        )

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(42, game_id)
        self.assertIn("developer", sql)
        self.assertIn("duplicate_flag", sql)
        self.assertIn("FALSE", sql)
        self.assertIn("status", sql)
        self.assertEqual(GAME_STATUS_WAITING_VALIDATION, parameters["status"])
        self.assertEqual("Chrono Trigger", parameters["name"])
        self.assertEqual(11, parameters["developer"])

    def test_insert_rejects_invalid_validation_status(self):
        """Verifie que l'insertion refuse un statut de validation inconnu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur fonctionnelle.
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

        with self.assertRaises(ValueError):
            repository.insert(
                connection,
                game,
                platform_id=7,
                studio_id=11,
                initial_validation_status="REFUSED",
            )

        self.assertEqual([], connection.executed_statements)

    def test_list_public_library_games_selects_validation_status(self):
        """Verifie que la liste Bibliotheque expose le statut lu en base.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la projection SQL.
        """

        connection = FakeConnection()
        connection.mapping_results = [[]]
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )

        repository.list_public_library_games(
            connection,
            _library_criteria(),
        )

        sql, _parameters = connection.executed_statements[0]
        self.assertIn("game.status", sql)

    def test_list_public_library_games_filters_waiting_validation_by_default(self):
        """Verifie que la liste publique masque les jeux en attente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le filtre SQL.
        """

        connection = FakeConnection()
        connection.mapping_results = [[]]
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )

        repository.list_public_library_games(
            connection,
            _library_criteria(),
        )

        sql, parameters = connection.executed_statements[0]
        self.assertIn("game.status = :accepted_status", sql)
        self.assertEqual(GAME_STATUS_ACCEPTED, parameters["accepted_status"])

    def test_list_public_library_games_does_not_filter_waiting_validation_for_admin(self):
        """Verifie que la liste admin inclut tous les statuts.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence de filtre statut.
        """

        connection = FakeConnection()
        connection.mapping_results = [[]]
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )

        repository.list_public_library_games(
            connection,
            _library_criteria(requester_profile="ADMIN"),
        )

        sql, parameters = connection.executed_statements[0]
        self.assertNotIn("game.status = :accepted_status", sql)
        self.assertNotIn("accepted_status", parameters)

    def test_list_public_library_games_filters_validation_status_for_admin(self):
        """Verifie que la liste admin peut filtrer le statut de validation.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le filtre SQL admin.
        """

        connection = FakeConnection()
        connection.mapping_results = [[]]
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )

        repository.list_public_library_games(
            connection,
            _library_criteria(
                requester_profile="ADMIN",
                status=GAME_STATUS_WAITING_VALIDATION,
            ),
        )

        sql, parameters = connection.executed_statements[0]
        self.assertIn("game.status = :validation_status", sql)
        self.assertEqual(GAME_STATUS_WAITING_VALIDATION, parameters["validation_status"])
        self.assertNotIn("accepted_status", parameters)

    def test_find_public_library_game_selects_validation_status(self):
        """Verifie que le detail Bibliotheque expose le statut lu en base.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la projection SQL.
        """

        connection = FakeConnection()
        connection.mapping_results = [[]]
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )

        repository.find_public_library_game(connection, 42)

        sql, parameters = connection.executed_statements[0]
        self.assertIn("game.status", sql)
        self.assertIn("game.status = :accepted_status", sql)
        self.assertIn("t_user_collection", sql)
        self.assertEqual(GAME_STATUS_ACCEPTED, parameters["accepted_status"])
        self.assertEqual(-1, parameters["current_user_id"])
        self.assertFalse(parameters["include_waiting_validation"])

    def test_find_public_library_game_allows_admin_visibility(self):
        """Verifie que le detail admin ne filtre pas les jeux en attente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le parametre SQL.
        """

        connection = FakeConnection()
        connection.mapping_results = [[]]
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )

        repository.find_public_library_game(connection, 42, True)

        _sql, parameters = connection.executed_statements[0]
        self.assertTrue(parameters["include_waiting_validation"])

    def test_find_public_library_game_allows_current_user_collection_owner(self):
        """Verifie que le detail public accepte le proprietaire collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le parametre utilisateur.
        """

        connection = FakeConnection()
        connection.mapping_results = [[]]
        repository = SqlAlchemyGameRepository(
            "collection",
            UserCollectionNameNormalizer(),
        )

        repository.find_public_library_game(connection, 42, False, 7)

        _sql, parameters = connection.executed_statements[0]
        self.assertEqual(7, parameters["current_user_id"])

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

        repository.insert(
            connection,
            game,
            platform_id=7,
            studio_id=11,
            initial_validation_status=GAME_STATUS_ACCEPTED,
        )

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

        repository.insert(
            connection,
            game,
            platform_id=7,
            studio_id=11,
            initial_validation_status=GAME_STATUS_ACCEPTED,
        )

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

        repository.insert(
            connection,
            game,
            platform_id=7,
            studio_id=11,
            initial_validation_status=GAME_STATUS_ACCEPTED,
        )

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


def _library_criteria(requester_profile="PUBLIC", status=""):
    """Construit des criteres Bibliotheque minimaux pour les tests repository.

    Args:
        requester_profile (str): Profil de visibilite.
        status (str): Filtre optionnel de statut de validation.

    Returns:
        LibraryQueryCriteria: Criteres de liste sans filtre.
    """

    from services.library.library_query_contract import (
        LibraryPageRequest,
        LibraryQueryCriteria,
        LibrarySortRule,
    )

    return LibraryQueryCriteria(
        page_request=LibraryPageRequest(page=0, size=500),
        name="",
        normalized_name="",
        platform="",
        normalized_platform="",
        duplicate_flag=None,
        status=status,
        current_user_id=None,
        requester_profile=requester_profile,
        sort_rules=(LibrarySortRule("name", "asc"),),
    )


if __name__ == "__main__":
    unittest.main()
