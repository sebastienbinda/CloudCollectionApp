#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du rattachement plateformes dans le repository d'import.

from contextlib import nullcontext
from types import SimpleNamespace
import unittest

from services.collection.imports import (
    CollectionImportData,
    CollectionImportGame,
    CollectionImportPlatform,
)
from services.database.user_collection_import_repository import (
    SqlAlchemyUserCollectionImportRepository,
)
from services.database.admin_library_import_repository import (
    SqlAlchemyAdminLibraryImportRepository,
)
from services.database import (
    GameMatchingConfiguration,
    GameMatchingService,
    PlatformMatchingConfiguration,
    PlatformMatchingService,
)
from services.users import UserCollectionNameNormalizer


class FakeImportConnection:
    """Connexion factice capturant les requetes executees pendant l'import."""

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
            parameters (dict | None): Parametres SQL associes.

        Returns:
            SimpleNamespace: Resultat factice sans donnees.
        """

        self.executed_statements.append((str(statement), parameters or {}))
        return SimpleNamespace()


class UserCollectionImportPlatformMatchingRepositoryTest(unittest.TestCase):
    """Valide que l'import ne cree plus de plateformes utilisateur."""

    def test_ensure_platforms_reuses_catalog_ids_without_insert(self):
        """Verifie l'absence d'insertion plateforme pendant l'import.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les identifiants retournes.
        """

        insert_calls = []
        repository = object.__new__(SqlAlchemyUserCollectionImportRepository)
        repository.name_normalizer = UserCollectionNameNormalizer()
        repository.platform_repository = SimpleNamespace(
            load_ids_by_key=lambda connection: {"switch": 7, "nes": 8},
            insert=lambda connection, name: insert_calls.append(name),
        )

        platform_ids, linked_platforms = repository._ensure_platforms(
            object(),
            CollectionImportData(
                [CollectionImportPlatform("Switch")],
                [],
                [
                    SimpleNamespace(platform_name="Switch"),
                    SimpleNamespace(platform_name="Switch"),
                    SimpleNamespace(platform_name="NES"),
                    SimpleNamespace(platform_name="Unknown"),
                ],
            ),
        )

        self.assertEqual({"switch": 7, "nes": 8}, platform_ids)
        self.assertEqual(2, linked_platforms)
        self.assertEqual([], insert_calls)

    def test_import_collection_invalidates_platform_cache_after_success(self):
        """Verifie l'invalidation cache apres creation de jeux.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'invalidation.
        """

        invalidations = []
        connection = FakeImportConnection()
        repository = object.__new__(SqlAlchemyUserCollectionImportRepository)
        repository.name_normalizer = UserCollectionNameNormalizer()
        repository.engine = SimpleNamespace(begin=lambda: nullcontext(connection))
        repository.user_file_repository = SimpleNamespace(
            lock_user_collection_state=lambda connection, user_id: "",
            find_user_email=lambda connection, user_id: "importer@example.com",
            update_collection_file=lambda connection, user_id, path, description: None,
        )
        repository.platform_repository = SimpleNamespace(
            load_catalog_rows=lambda connection: [{"name": "Switch"}],
            load_ids_by_key=lambda connection: {"switch": 7},
            invalidate_cache=lambda: invalidations.append("platforms"),
        )
        repository.platform_matching_service = SimpleNamespace(
            match_import_data=lambda import_data, platform_rows: import_data,
        )
        repository.game_matching_service = GameMatchingService(
            GameMatchingConfiguration(low_level_rating=25, high_level_rating=75),
            repository.name_normalizer,
        )
        repository.platform_matching_notifier = SimpleNamespace(
            notify_import_report=lambda warnings: None,
        )
        repository.studio_repository = SimpleNamespace(load_ids_by_key=lambda connection: {})
        repository.game_repository = SimpleNamespace(
            load_references_by_key=lambda connection: {},
            load_ids_by_key=lambda connection: {},
            game_key=lambda game: (
                repository.name_normalizer.comparison_key(game.platform_name),
                repository.name_normalizer.comparison_key(game.name),
            ),
            insert=lambda connection, game, platform_id, studio_id: 11,
        )
        repository.user_collection_repository = SimpleNamespace(
            ensure_user_game_associations=lambda connection, user_id, associations: len(associations),
        )

        result = repository.import_collection(
            7,
            "/users/workspace/7/7-collection.ods",
            CollectionImportData(
                platforms=[CollectionImportPlatform("Switch")],
                studios=[],
                games=[CollectionImportGame("Zelda", "Switch", "", None)],
            ),
            {"file_type": "libreoffice_ods"},
        )

        self.assertEqual(["platforms"], invalidations)
        self.assertIn("pg_advisory_xact_lock", connection.executed_statements[0][0])
        self.assertEqual(
            repository.GLOBAL_GAME_IMPORT_LOCK_KEY,
            connection.executed_statements[0][1]["lock_key"],
        )
        self.assertEqual("importer@example.com", result.user_email)
        self.assertEqual(1, result.linked_platforms)
        self.assertEqual(1, result.created_games)

    def test_import_collection_exposes_platform_matching_warnings_to_caller(self):
        """Verifie la propagation des warnings de matching vers le service.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les warnings de l'objet d'import initial.
        """

        connection = FakeImportConnection()
        repository = object.__new__(SqlAlchemyUserCollectionImportRepository)
        repository.name_normalizer = UserCollectionNameNormalizer()
        repository.engine = SimpleNamespace(begin=lambda: nullcontext(connection))
        repository.user_file_repository = SimpleNamespace(
            lock_user_collection_state=lambda connection, user_id: "",
            find_user_email=lambda connection, user_id: "importer@example.com",
            update_collection_file=lambda connection, user_id, path, description: None,
        )
        repository.platform_repository = SimpleNamespace(
            load_catalog_rows=lambda connection: [{"name": "Switch"}],
            load_ids_by_key=lambda connection: {"switch": 7},
            invalidate_cache=lambda: None,
        )
        repository.platform_matching_service = PlatformMatchingService(
            PlatformMatchingConfiguration(low_level_rating=25, high_level_rating=75)
        )
        repository.game_matching_service = GameMatchingService(
            GameMatchingConfiguration(low_level_rating=25, high_level_rating=75),
            repository.name_normalizer,
        )
        repository.studio_repository = SimpleNamespace(load_ids_by_key=lambda connection: {})
        repository.game_repository = SimpleNamespace(
            load_references_by_key=lambda connection: {},
            load_ids_by_key=lambda connection: {},
            game_key=lambda game: (
                repository.name_normalizer.comparison_key(game.platform_name),
                repository.name_normalizer.comparison_key(game.name),
            ),
            insert=lambda connection, game, platform_id, studio_id: 11,
        )
        repository.user_collection_repository = SimpleNamespace(
            ensure_user_game_associations=lambda connection, user_id, associations: len(associations),
        )
        import_data = CollectionImportData(
            platforms=[CollectionImportPlatform("Wii")],
            studios=[],
            games=[CollectionImportGame("Sports", "Wii", "", None)],
        )

        result = repository.import_collection(
            7,
            "/users/workspace/7/7-collection.ods",
            import_data,
            {"file_type": "libreoffice_ods"},
        )

        self.assertIn("pg_advisory_xact_lock", connection.executed_statements[0][0])
        self.assertEqual(1, result.linked_platforms)
        self.assertEqual(["Switch"], [game.platform_name for game in import_data.games])
        self.assertEqual("Sports", import_data.warnings.platform_matches[0]["game_name"])
        self.assertEqual("Switch", import_data.warnings.platform_mappings[0]["matched_platform"])

    def test_ensure_games_reuses_existing_game_with_high_unique_score(self):
        """Verifie le rattachement d'un jeu existant par score de nom.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence de creation.
        """

        insert_calls = []
        repository = object.__new__(SqlAlchemyUserCollectionImportRepository)
        repository.name_normalizer = UserCollectionNameNormalizer()
        repository.game_matching_service = GameMatchingService(
            GameMatchingConfiguration(low_level_rating=25, high_level_rating=75),
            repository.name_normalizer,
        )
        repository.game_repository = SimpleNamespace(
            load_references_by_key=lambda connection: {
                ("switch", "the legend of zelda"): (31, "The Legend of Zelda")
            },
            load_ids_by_key=lambda connection: {("switch", "the legend of zelda"): 31},
            game_key=lambda game: (
                repository.name_normalizer.comparison_key(game.platform_name),
                repository.name_normalizer.comparison_key(game.name),
            ),
            insert=lambda connection, game, platform_id, studio_id: insert_calls.append(game),
        )

        (
            associations,
            created_games,
            created_game_match_reports,
            imported_game_match_reports,
        ) = repository._ensure_games(
            object(),
            CollectionImportData(
                platforms=[CollectionImportPlatform("Switch")],
                studios=[],
                games=[CollectionImportGame("Legend of Zelda", "Switch", "", None)],
            ),
            {"switch": 7},
            {},
        )

        self.assertEqual(0, created_games)
        self.assertEqual([], created_game_match_reports)
        self.assertEqual(1, len(imported_game_match_reports))
        self.assertFalse(imported_game_match_reports[0].created)
        self.assertEqual("The Legend of Zelda", imported_game_match_reports[0].associated_game_name)
        self.assertGreaterEqual(imported_game_match_reports[0].score, 75)
        self.assertEqual([], insert_calls)
        self.assertEqual(31, associations[0].game_id)

    def test_ensure_games_reuses_existing_game_with_stored_name_key(self):
        """Verifie le rattachement exact avec le nom standardise du referentiel.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence d'insertion en doublon.
        """

        insert_calls = []
        repository = object.__new__(SqlAlchemyUserCollectionImportRepository)
        repository.name_normalizer = UserCollectionNameNormalizer()
        repository.game_matching_service = GameMatchingService(
            GameMatchingConfiguration(low_level_rating=25, high_level_rating=99),
            repository.name_normalizer,
        )
        repository.game_repository = SimpleNamespace(
            load_references_by_key=lambda connection: {
                ("playstation 2", "burnout 3 : takedown"): (
                    107,
                    "Burnout 3 : Takedown",
                    None,
                )
            },
            game_key=lambda game: (
                repository.name_normalizer.comparison_key(game.platform_name),
                repository.name_normalizer.game_comparison_key(game.name),
            ),
            insert=lambda connection, game, platform_id, studio_id: insert_calls.append(game),
        )

        (
            associations,
            created_games,
            created_game_match_reports,
            imported_game_match_reports,
        ) = repository._ensure_games(
            object(),
            CollectionImportData(
                platforms=[CollectionImportPlatform("PlayStation 2")],
                studios=[],
                games=[CollectionImportGame("Burnout 3\xa0: Takedown", "PlayStation 2", "", None)],
            ),
            {"playstation 2": 7},
            {},
        )

        self.assertEqual(0, created_games)
        self.assertEqual([], created_game_match_reports)
        self.assertEqual([], insert_calls)
        self.assertEqual(107, associations[0].game_id)
        self.assertFalse(imported_game_match_reports[0].created)
        self.assertEqual(
            "Burnout 3 : Takedown",
            imported_game_match_reports[0].associated_game_name,
        )

    def test_ensure_games_reports_created_game_best_existing_candidate(self):
        """Verifie le diagnostic de matching pour un jeu cree.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le rapport de creation.
        """

        repository = object.__new__(SqlAlchemyUserCollectionImportRepository)
        repository.name_normalizer = UserCollectionNameNormalizer()
        repository.game_matching_service = GameMatchingService(
            GameMatchingConfiguration(low_level_rating=25, high_level_rating=90),
            repository.name_normalizer,
        )
        repository.game_repository = SimpleNamespace(
            load_references_by_key=lambda connection: {
                ("switch", "mario kart"): (31, "Mario Kart")
            },
            game_key=lambda game: (
                repository.name_normalizer.comparison_key(game.platform_name),
                repository.name_normalizer.comparison_key(game.name),
            ),
            insert=lambda connection, game, platform_id, studio_id: 41,
        )

        (
            associations,
            created_games,
            created_game_match_reports,
            imported_game_match_reports,
        ) = repository._ensure_games(
            object(),
            CollectionImportData(
                platforms=[CollectionImportPlatform("Switch")],
                studios=[],
                games=[CollectionImportGame("Zelda", "Switch", "", None)],
            ),
            {"switch": 7},
            {},
        )

        self.assertEqual(1, created_games)
        self.assertEqual(41, associations[0].game_id)
        self.assertEqual(1, len(created_game_match_reports))
        self.assertEqual("Zelda", created_game_match_reports[0].imported_game_name)
        self.assertEqual("Switch", created_game_match_reports[0].platform_name)
        self.assertEqual("Mario Kart", created_game_match_reports[0].best_existing_game_name)
        self.assertGreaterEqual(created_game_match_reports[0].best_score, 0)
        self.assertEqual(1, len(imported_game_match_reports))
        self.assertTrue(imported_game_match_reports[0].created)
        self.assertEqual("Zelda", imported_game_match_reports[0].imported_game_name)
        self.assertEqual("", imported_game_match_reports[0].associated_game_name)
        self.assertEqual("fuzzy_similarity", imported_game_match_reports[0].rule)


class AdminLibraryImportRepositoryTest(unittest.TestCase):
    """Valide le repository d'import admin Bibliotheque."""

    def test_import_library_creates_games_without_user_associations(self):
        """Verifie que l'import admin ne touche pas aux collections utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les compteurs et appels.
        """

        invalidations = []
        connection = FakeImportConnection()
        user_association_calls = []
        repository = object.__new__(SqlAlchemyAdminLibraryImportRepository)
        repository.name_normalizer = UserCollectionNameNormalizer()
        repository.engine = SimpleNamespace(begin=lambda: nullcontext(connection))
        repository.platform_repository = SimpleNamespace(
            load_catalog_rows=lambda connection: [{"name": "Switch"}],
            load_ids_by_key=lambda connection: {"switch": 7},
            invalidate_cache=lambda: invalidations.append("platforms"),
        )
        repository.platform_matching_service = SimpleNamespace(
            match_import_data=lambda import_data, platform_rows: import_data,
        )
        repository.game_matching_service = GameMatchingService(
            GameMatchingConfiguration(low_level_rating=25, high_level_rating=75),
            repository.name_normalizer,
        )
        repository.studio_repository = SimpleNamespace(
            load_ids_by_key=lambda connection: {},
            insert=lambda connection, name: 13,
        )
        repository.game_repository = SimpleNamespace(
            load_references_by_key=lambda connection: {},
            load_ids_by_key=lambda connection: {},
            game_key=lambda game: (
                repository.name_normalizer.comparison_key(game.platform_name),
                repository.name_normalizer.comparison_key(game.name),
            ),
            insert=lambda connection, game, platform_id, studio_id: 11,
        )
        repository.user_collection_repository = SimpleNamespace(
            ensure_user_game_associations=lambda connection, user_id, associations: (
                user_association_calls.append((user_id, associations))
            ),
        )

        result = repository.import_library(
            CollectionImportData(
                platforms=[CollectionImportPlatform("Switch")],
                studios=[],
                games=[CollectionImportGame("Zelda", "Switch", "", None)],
            ),
        )

        self.assertEqual(["platforms"], invalidations)
        self.assertIn("pg_advisory_xact_lock", connection.executed_statements[0][0])
        self.assertEqual([], user_association_calls)
        self.assertEqual(1, result.linked_platforms)
        self.assertEqual(0, result.created_studios)
        self.assertEqual(1, result.created_games)


if __name__ == "__main__":
    unittest.main()
