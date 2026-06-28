#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-03
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests des compteurs wishlist retournes par l'import utilisateur.

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.collection.imports import (  # noqa: E402
    CollectionFileDescription,
    CollectionFileType,
    CollectionImportData,
    CollectionImportGame,
    CollectionImportWarnings,
)
from services.database.user_collection_import_repository import (  # noqa: E402
    UserCollectionImportPersistenceResult,
)
from services.users import UserCollectionImportConfiguration  # noqa: E402
from services.users.user_collection_import_service import UserCollectionImportService  # noqa: E402


class FakeImportRepository:
    """Simule la persistance d'un import utilisateur."""

    def user_has_collection(self, user_id):
        """Indique qu'aucune collection n'existe.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            bool: Toujours `False`.
        """

        return False

    def import_collection(self, user_id, collection_file_path, import_data, description):
        """Retourne des compteurs de persistance factices."""

        return UserCollectionImportPersistenceResult(1, 1, 2, len(import_data.games))


class FakePlatformWarningImportRepository(FakeImportRepository):
    """Simule une persistance ajoutant des warnings de matching plateforme."""

    def import_collection(self, user_id, collection_file_path, import_data, description):
        """Ajoute un warning plateforme puis retourne des compteurs factices.

        Args:
            user_id (int): Identifiant utilisateur ignore.
            collection_file_path (str): Chemin de fichier ignore.
            import_data (CollectionImportData): Donnees d'import a enrichir.
            description (dict): Description d'import ignoree.

        Returns:
            UserCollectionImportPersistenceResult: Compteurs factices.
        """

        import_data.warnings.platform_mappings.append(
            {
                "imported_platform": "Wii",
                "matched_platform": "Switch",
                "score": 44,
                "games_count": 1,
                "matched_by_alias": False,
                "matched_alias": "",
                "accepted": True,
                "manual_check": True,
                "reason": "",
            }
        )
        import_data.warnings.platform_matches.append(
            {
                "game_name": "Zelda",
                "imported_platform": "Wii",
                "matched_platform": "Switch",
                "score": 44,
            }
        )
        return UserCollectionImportPersistenceResult(1, 1, 1, len(import_data.games))


class FakeWishlistReader:
    """Reader factice retournant des jeux avec wishlist et warnings."""

    accepted_extensions = (".ods",)

    def read(self, file_path, description):
        """Retourne des donnees d'import wishlist factices."""

        return CollectionImportData(
            platforms=[],
            studios=[],
            games=[
                CollectionImportGame("Zelda", "Switch", "Nintendo", None, False),
                CollectionImportGame("Metroid", "Switch", "Nintendo", None, True),
            ],
            warnings=CollectionImportWarnings(1, ["Peut etre"]),
        )


class FakeReaderFactory:
    """Factory factice du reader d'import."""

    def create(self, file_type):
        """Retourne le reader factice."""

        return FakeWishlistReader()


class FakeImportReportNotifier:
    """Capture le rapport administrateur de fin d'import."""

    def __init__(self):
        """Initialise le notifier factice."""

        self.contexts = []

    def notify_import_report(self, context):
        """Memorise le contexte transmis au notifier."""

        self.contexts.append(context)


class UserCollectionImportWishlistResultTest(unittest.TestCase):
    """Valide les compteurs wishlist retournes par le service."""

    def test_import_result_contains_wishlist_count_and_warnings(self):
        """Verifie le mapping des compteurs wishlist."""

        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "collection.ods"
            source_file.write_bytes(b"ods")
            notifier = FakeImportReportNotifier()
            service = UserCollectionImportService(
                UserCollectionImportConfiguration(
                    workspace_path=str(Path(directory) / "workspace"),
                    max_upload_bytes=1024,
                ),
                FakeImportRepository(),
                FakeReaderFactory(),
                report_notifier=notifier,
            )

            result = service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                CollectionFileDescription(CollectionFileType.LIBREOFFICE_ODS),
            )

        self.assertEqual(1, result.wishlisted_games)
        self.assertEqual(1, result.linked_platforms)
        self.assertNotIn("created_platforms", result.to_dict())
        self.assertEqual(1, result.to_dict()["linked_platforms"])
        self.assertGreaterEqual(result.warnings["total_import_duration_seconds"], 0)
        self.assertEqual(1, len(notifier.contexts))
        self.assertEqual(7, notifier.contexts[0].user_id)
        self.assertEqual(1, notifier.contexts[0].warnings.invalid_wishlist)
        self.assertEqual(
            {
                "invalid_wishlist": 1,
                "invalid_wishlist_values_found": ["Peut etre"],
                "invalid_games": [],
                "platform_mappings": [],
                "platform_matches": [],
                "skipped_games": [],
                "total_import_duration_seconds": result.warnings[
                    "total_import_duration_seconds"
                ],
            },
            result.warnings,
        )
        self.assertEqual(1, result.to_dict()["wishlisted_games"])

    def test_import_notifier_receives_platform_matching_warnings(self):
        """Verifie que le mail admin recoit les warnings de matching.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la propagation vers le notifier.
        """

        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "collection.ods"
            source_file.write_bytes(b"ods")
            notifier = FakeImportReportNotifier()
            service = UserCollectionImportService(
                UserCollectionImportConfiguration(
                    workspace_path=str(Path(directory) / "workspace"),
                    max_upload_bytes=1024,
                ),
                FakePlatformWarningImportRepository(),
                FakeReaderFactory(),
                report_notifier=notifier,
            )

            result = service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                CollectionFileDescription(CollectionFileType.LIBREOFFICE_ODS),
            )

        self.assertEqual("Switch", result.warnings["platform_mappings"][0]["matched_platform"])
        self.assertEqual("Zelda", result.warnings["platform_matches"][0]["game_name"])
        self.assertEqual(1, len(notifier.contexts))
        self.assertEqual("Switch", notifier.contexts[0].warnings.platform_mappings[0]["matched_platform"])


if __name__ == "__main__":
    unittest.main()
