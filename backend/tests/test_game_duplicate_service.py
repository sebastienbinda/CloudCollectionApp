#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du service de gestion des doublons de jeux.

import unittest

from services.database import DatabaseConfiguration
from services.database.game_duplicate_repository import SqlAlchemyGameDuplicateRepository
from services.library.game_duplicate_service import (
    GameDuplicateError,
    GameDuplicatePermissionError,
    GameDuplicateService,
)


class FakeConnectionContext:
    """Contexte transactionnel factice."""

    def __init__(self, connection):
        """Initialise le contexte.

        Args:
            connection (object): Connexion retournee.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection

    def __enter__(self):
        """Entre dans le contexte.

        Args:
            Aucun.

        Returns:
            object: Connexion factice.
        """

        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        """Sort du contexte.

        Args:
            exc_type (type | None): Type d'exception.
            exc_value (BaseException | None): Exception.
            traceback (object | None): Traceback.

        Returns:
            bool: `False` pour ne pas masquer les erreurs.
        """

        return False


class FakeSqlConnection:
    """Connexion SQL factice capturant les requetes executees."""

    def __init__(self):
        """Initialise la capture SQL.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.executed_statements = []

    def execute(self, statement, parameters=None):
        """Capture une requete SQL.

        Args:
            statement (object): Requete SQLAlchemy recue.
            parameters (dict | None): Parametres SQL recus.

        Returns:
            None: Aucun resultat SQL n'est requis.
        """

        self.executed_statements.append((str(statement), parameters))
        return FakeSqlResult()


class FakeSqlResult:
    """Resultat SQL factice avec compteur de lignes."""

    rowcount = 1


class FakeEngine:
    """Moteur SQLAlchemy factice."""

    def __init__(self):
        """Initialise le moteur.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = object()

    def begin(self):
        """Ouvre un contexte transactionnel.

        Args:
            Aucun.

        Returns:
            FakeConnectionContext: Contexte factice.
        """

        return FakeConnectionContext(self.connection)

    def connect(self):
        """Ouvre un contexte de lecture.

        Args:
            Aucun.

        Returns:
            FakeConnectionContext: Contexte factice.
        """

        return FakeConnectionContext(self.connection)


class FakeGameDuplicateRepository:
    """Repository factice pour les doublons."""

    def __init__(self):
        """Initialise les donnees factices.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.games = {
            1: {"id": 1, "name": "Sonic the edgedog", "platform": 7, "platform_name": "Mega Drive", "duplicate_flag": True},
            2: {"id": 2, "name": "Sonic", "platform": 7, "platform_name": "Mega Drive", "duplicate_flag": False},
            3: {"id": 3, "name": "Sonic", "platform": 8, "platform_name": "Master System", "duplicate_flag": False},
            4: {"id": 4, "name": "Sonic 1", "platform": 7, "platform_name": "Mega Drive", "duplicate_flag": False},
        }
        self.aliases = []
        self.deleted_games = []
        self.lock_calls = []
        self.updated_values = []
        self.remap_calls = []
        self.user_has_game_result = True

    def lock_global_game_catalog(self, connection):
        """Memorise la prise du verrou global des jeux.

        Args:
            connection (object): Connexion ignoree.

        Returns:
            None: Le verrou est seulement memorise en test.
        """

        self.lock_calls.append("global_game_catalog")

    def find_game_for_duplicate_management(self, connection, game_id):
        """Retourne un jeu factice.

        Args:
            connection (object): Connexion ignoree.
            game_id (int): Identifiant du jeu.

        Returns:
            dict | None: Jeu trouve ou absence.
        """

        return self.games.get(game_id)

    def user_has_game(self, connection, user_id, game_id):
        """Indique si l'utilisateur possede le jeu.

        Args:
            connection (object): Connexion ignoree.
            user_id (int): Identifiant utilisateur.
            game_id (int): Identifiant du jeu.

        Returns:
            bool: Valeur configuree.
        """

        return self.user_has_game_result

    def mark_game_as_duplicate(self, connection, game_id):
        """Marque un jeu comme doublon.

        Args:
            connection (object): Connexion ignoree.
            game_id (int): Identifiant du jeu.

        Returns:
            bool: Toujours `True`.
        """

        self.games[game_id]["duplicate_flag"] = True
        return True

    def reject_duplicate(self, connection, game_id):
        """Refuse un signalement.

        Args:
            connection (object): Connexion ignoree.
            game_id (int): Identifiant du jeu.

        Returns:
            bool: `True` si le jeu etait signale.
        """

        if not self.games.get(game_id, {}).get("duplicate_flag"):
            return False
        self.games[game_id]["duplicate_flag"] = False
        return True

    def count_users_with_game(self, connection, game_id):
        """Compte les utilisateurs concernes.

        Args:
            connection (object): Connexion ignoree.
            game_id (int): Identifiant du jeu.

        Returns:
            int: Nombre factice.
        """

        return 4

    def insert_game_alias(self, connection, target_game_id, alias_name):
        """Memorise l'alias cree.

        Args:
            connection (object): Connexion ignoree.
            target_game_id (int): Jeu conserve.
            alias_name (str): Alias ajoute.

        Returns:
            bool: Toujours `True`.
        """

        self.aliases.append((target_game_id, alias_name))
        return True

    def update_game_values(self, connection, game_id, selected_values):
        """Memorise les valeurs choisies.

        Args:
            connection (object): Connexion ignoree.
            game_id (int): Jeu conserve.
            selected_values (dict): Valeurs choisies.

        Returns:
            int: Nombre de lignes factice.
        """

        self.updated_values.append((game_id, selected_values))
        return 1

    def remap_user_collections(self, connection, duplicate_game_id, target_game_id):
        """Memorise le remapping.

        Args:
            connection (object): Connexion ignoree.
            duplicate_game_id (int): Jeu supprime.
            target_game_id (int): Jeu conserve.

        Returns:
            dict[str, int]: Compteurs factices.
        """

        self.remap_calls.append((duplicate_game_id, target_game_id))
        return {"updated_rows": 3, "merged_rows": 1}

    def delete_game(self, connection, game_id):
        """Memorise la suppression.

        Args:
            connection (object): Connexion ignoree.
            game_id (int): Jeu supprime.

        Returns:
            bool: Toujours `True`.
        """

        self.deleted_games.append(game_id)
        return True


class FakePublicGameRepository:
    """Repository factice pour la recherche publique des jeux."""

    def __init__(self):
        """Initialise les lignes de jeux factices.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.criteria = None
        self.rows = [
            {
                "id": 1,
                "name": "Sonic the edgedog",
                "platform": "Mega Drive",
                "platform_id": 7,
                "duplicate_flag": True,
            },
            {
                "id": 2,
                "name": "Sonic",
                "platform": "Mega Drive",
                "platform_id": 7,
                "duplicate_flag": False,
            },
        ]

    def list_public_library_games(self, connection, criteria):
        """Retourne les jeux publics factices.

        Args:
            connection (object): Connexion ignoree.
            criteria (LibraryQueryCriteria): Criteres de recherche recus.

        Returns:
            list[dict]: Jeux factices.
        """

        self.criteria = criteria
        return self.rows


class GameDuplicateServiceTest(unittest.TestCase):
    """Valide les regles metier des doublons de jeux."""

    def setUp(self):
        """Prepare le service teste.

        Args:
            Aucun.

        Returns:
            None: Le service est initialise.
        """

        self.repository = FakeGameDuplicateRepository()
        self.game_repository = FakePublicGameRepository()
        self.service = GameDuplicateService(
            DatabaseConfiguration(None, "collection", "0.1"),
            repository=self.repository,
            game_repository=self.game_repository,
            engine=FakeEngine(),
        )

    def test_report_duplicate_requires_game_in_user_collection(self):
        """Verifie le refus si le jeu n'appartient pas a l'utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'exception.
        """

        self.repository.user_has_game_result = False

        with self.assertRaises(GameDuplicatePermissionError):
            self.service.report_duplicate(7, 1)

    def test_repository_global_game_catalog_lock_uses_import_advisory_lock(self):
        """Verifie que le verrou doublon utilise le verrou PostgreSQL des imports.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la requete SQL de verrou.
        """

        repository = SqlAlchemyGameDuplicateRepository("collection")
        connection = FakeSqlConnection()

        repository.lock_global_game_catalog(connection)

        sql, parameters = connection.executed_statements[0]
        self.assertIn("pg_advisory_xact_lock", sql)
        self.assertEqual(repository.GLOBAL_GAME_IMPORT_LOCK_KEY, parameters["lock_key"])

    def test_repository_remap_user_collections_keeps_numeric_condition_as_numeric(self):
        """Verifie que la fusion ne compare pas `condition` a une chaine vide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le SQL de fusion des collections.
        """

        repository = SqlAlchemyGameDuplicateRepository("collection")
        connection = FakeSqlConnection()

        result = repository.remap_user_collections(connection, 1590, 1676)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual({"merged_rows": 1, "updated_rows": 1}, result)
        self.assertIn('"condition" = COALESCE(target."condition", duplicate."condition")', sql)
        self.assertNotIn("NULLIF(target.condition", sql)
        self.assertNotIn("NULLIF(target.\"condition\"", sql)
        self.assertEqual({"duplicate_game_id": 1590, "target_game_id": 1676}, parameters)

    def test_search_candidates_reuses_public_game_search_on_same_platform(self):
        """Verifie que les candidats passent par la recherche publique des jeux.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les criteres et l'exclusion du doublon.
        """

        candidates = self.service.search_candidates(1, "Sonic", 10)

        self.assertEqual([2], [candidate["id"] for candidate in candidates])
        self.assertEqual("Sonic", self.game_repository.criteria.name)
        self.assertEqual("sonic", self.game_repository.criteria.normalized_name)
        self.assertEqual("Mega Drive", self.game_repository.criteria.platform)
        self.assertEqual("mega drive", self.game_repository.criteria.normalized_platform)
        self.assertEqual(11, self.game_repository.criteria.page_request.size)

    def test_merge_duplicate_remaps_collections_and_creates_alias(self):
        """Verifie la fusion nominale avec alias et remapping.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les compteurs.
        """

        result = self.service.merge_duplicate(
            1,
            2,
            {"release_date": "1991-06-23"},
            True,
        )

        self.assertEqual((2, "Sonic the edgedog"), self.repository.aliases[0])
        self.assertEqual(["global_game_catalog"], self.repository.lock_calls)
        self.assertEqual([(1, 2)], self.repository.remap_calls)
        self.assertEqual([1], self.repository.deleted_games)
        self.assertEqual(4, result.remapped_user_count)
        self.assertEqual(3, result.updated_collection_rows)
        self.assertEqual(1, result.merged_collection_rows)

    def test_merge_duplicate_accepts_unreported_source_for_admin_correction(self):
        """Verifie qu'un admin peut fusionner un jeu non signale.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la fusion sans `duplicate_flag`.
        """

        result = self.service.merge_duplicate(4, 2, {}, True)

        self.assertEqual(4, result.duplicate_game_id)
        self.assertEqual(2, result.target_game_id)
        self.assertEqual((2, "Sonic 1"), self.repository.aliases[0])
        self.assertEqual([4], self.repository.deleted_games)

    def test_merge_duplicate_rejects_cross_platform_target(self):
        """Verifie qu'une fusion inter-plateforme est refusee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'exception.
        """

        with self.assertRaises(GameDuplicateError):
            self.service.merge_duplicate(1, 3)

    def test_reject_duplicate_locks_global_game_catalog(self):
        """Verifie que le refus de doublon est serialise avec les imports.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la prise de verrou.
        """

        result = self.service.reject_duplicate(1)

        self.assertFalse(result["duplicate_flag"])
        self.assertEqual(["global_game_catalog"], self.repository.lock_calls)


if __name__ == "__main__":
    unittest.main()
