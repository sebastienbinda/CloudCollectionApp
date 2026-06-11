#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de l'import depuis fichier utilisateur deja stocke.

import tempfile
import unittest
from pathlib import Path

from services.users.stored_user_collection_import_service import StoredUserCollectionImportService
from services.users.user_collection_import_configuration import UserCollectionImportConfiguration

try:
    from tests.test_user_collection_import_service import (
        FakeCollectionFileReaderFactory,
        FakeOdsCollectionImportReader,
        FakeUserCollectionImportRepository,
        UserCollectionImportServiceTest,
    )
except ModuleNotFoundError:
    from test_user_collection_import_service import (
        FakeCollectionFileReaderFactory,
        FakeOdsCollectionImportReader,
        FakeUserCollectionImportRepository,
        UserCollectionImportServiceTest,
    )


class StoredUserCollectionImportServiceTest(unittest.TestCase):
    """Valide l'import depuis un fichier de collection deja conserve."""

    def test_import_stored_collection_reads_existing_file_without_copying(self):
        """Verifie que le fichier source conserve n'est ni copie ni supprime.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'import direct.
        """

        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "7-collection.ods"
            source_file.write_bytes(b"ods-content")
            repository = FakeUserCollectionImportRepository()
            reader = FakeOdsCollectionImportReader()
            service = StoredUserCollectionImportService(
                UserCollectionImportConfiguration(
                    workspace_path=str(Path(directory) / "workspace"),
                    max_upload_bytes=104857600,
                ),
                repository,
                FakeCollectionFileReaderFactory(reader),
            )

            result = service.import_stored_collection(
                7,
                str(source_file),
                UserCollectionImportServiceTest()._valid_description(),
            )

            target_file = Path(directory) / "workspace" / "7" / "7-collection.ods"
            self.assertFalse(target_file.exists())
            self.assertTrue(source_file.exists())
            self.assertEqual(str(source_file), reader.read_paths[0])
            self.assertEqual(str(source_file), repository.import_calls[0][1])
            self.assertEqual(1, result.associated_games)


if __name__ == "__main__":
    unittest.main()
