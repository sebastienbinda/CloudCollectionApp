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
from services.database import PlatformMatchingConfiguration, PlatformMatchingService
from services.users import UserCollectionNameNormalizer


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
        repository = object.__new__(SqlAlchemyUserCollectionImportRepository)
        repository.name_normalizer = UserCollectionNameNormalizer()
        repository.engine = SimpleNamespace(begin=lambda: nullcontext(object()))
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
        repository.platform_matching_notifier = SimpleNamespace(
            notify_import_report=lambda warnings: None,
        )
        repository.studio_repository = SimpleNamespace(load_ids_by_key=lambda connection: {})
        repository.game_repository = SimpleNamespace(
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

        repository = object.__new__(SqlAlchemyUserCollectionImportRepository)
        repository.name_normalizer = UserCollectionNameNormalizer()
        repository.engine = SimpleNamespace(begin=lambda: nullcontext(object()))
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
        repository.studio_repository = SimpleNamespace(load_ids_by_key=lambda connection: {})
        repository.game_repository = SimpleNamespace(
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

        self.assertEqual(1, result.linked_platforms)
        self.assertEqual(["Switch"], [game.platform_name for game in import_data.games])
        self.assertEqual("Sports", import_data.warnings.platform_matches[0]["game_name"])
        self.assertEqual("Switch", import_data.warnings.platform_mappings[0]["matched_platform"])


if __name__ == "__main__":
    unittest.main()
