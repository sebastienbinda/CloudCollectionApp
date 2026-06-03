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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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


class UserCollectionImportWishlistResultTest(unittest.TestCase):
    """Valide les compteurs wishlist retournes par le service."""

    def test_import_result_contains_wishlist_count_and_warnings(self):
        """Verifie le mapping des compteurs wishlist."""

        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "collection.ods"
            source_file.write_bytes(b"ods")
            service = UserCollectionImportService(
                UserCollectionImportConfiguration(
                    workspace_path=str(Path(directory) / "workspace"),
                    max_upload_bytes=1024,
                ),
                FakeImportRepository(),
                FakeReaderFactory(),
            )

            result = service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                CollectionFileDescription(CollectionFileType.LIBREOFFICE_ODS),
            )

        self.assertEqual(1, result.wishlisted_games)
        self.assertEqual(
            {
                "invalid_wishlist": 1,
                "invalid_wishlist_values_found": ["Peut etre"],
            },
            result.warnings,
        )
        self.assertEqual(1, result.to_dict()["wishlisted_games"])


if __name__ == "__main__":
    unittest.main()
