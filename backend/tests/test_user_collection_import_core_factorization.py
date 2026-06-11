#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de factorisation du coeur d'import de collection.

import tempfile
import unittest
from pathlib import Path

from services.users.stored_user_collection_import_service import StoredUserCollectionImportService
from services.users.user_collection_import_service import (
    UserCollectionImportResult,
    UserCollectionImportService,
)

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


class RecordingUserCollectionImportService(UserCollectionImportService):
    """Service d'import factice enregistrant l'appel au coeur centralise."""

    def _import_collection_file(self, user_id, source_file_path, original_filename, file_description, copy_to_workspace):
        """Enregistre les arguments recus par le coeur centralise.

        Args:
            user_id (int): Identifiant utilisateur.
            source_file_path (Path): Fichier source transmis.
            original_filename (str): Nom original transmis.
            file_description (object): Description d'import.
            copy_to_workspace (bool): Mode de copie demande.

        Returns:
            UserCollectionImportResult: Resultat factice.
        """

        self.recorded_core_call = (
            user_id,
            source_file_path,
            original_filename,
            file_description,
            copy_to_workspace,
        )
        return UserCollectionImportResult(0, 0, 0, 0)


class RecordingStoredUserCollectionImportService(
    RecordingUserCollectionImportService,
    StoredUserCollectionImportService,
):
    """Service stocke factice utilisant le meme enregistreur centralise."""


class UserCollectionImportCoreFactorizationTest(unittest.TestCase):
    """Verifie que les deux workflows utilisent le meme coeur d'import."""

    def test_user_import_delegates_to_central_import_core_with_copy(self):
        """Verifie que l'import utilisateur demande une copie workspace.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la delegation.
        """

        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "collection.ods"
            source_file.write_bytes(b"ods-content")
            service = self._build_service(RecordingUserCollectionImportService, directory)
            description = UserCollectionImportServiceTest()._valid_description()

            service.import_collection(7, str(source_file), "collection.ods", description)

            self.assertEqual(7, service.recorded_core_call[0])
            self.assertEqual(source_file, service.recorded_core_call[1])
            self.assertEqual("collection.ods", service.recorded_core_call[2])
            self.assertIs(description, service.recorded_core_call[3])
            self.assertTrue(service.recorded_core_call[4])

    def test_stored_import_delegates_to_central_import_core_without_copy(self):
        """Verifie que l'import reset utilise le fichier stocke sans copie.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la delegation.
        """

        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "7-collection.ods"
            source_file.write_bytes(b"ods-content")
            service = self._build_service(RecordingStoredUserCollectionImportService, directory)
            description = UserCollectionImportServiceTest()._valid_description()

            service.import_stored_collection(7, str(source_file), description)

            self.assertEqual(7, service.recorded_core_call[0])
            self.assertEqual(source_file, service.recorded_core_call[1])
            self.assertEqual("7-collection.ods", service.recorded_core_call[2])
            self.assertIs(description, service.recorded_core_call[3])
            self.assertFalse(service.recorded_core_call[4])

    def _build_service(self, service_class, directory):
        return service_class(
            UserCollectionImportServiceTest()._build_service(directory)[0].configuration,
            FakeUserCollectionImportRepository(),
            FakeCollectionFileReaderFactory(FakeOdsCollectionImportReader()),
        )


if __name__ == "__main__":
    unittest.main()
