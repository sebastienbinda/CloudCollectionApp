#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du service d'import avec un reader generique non ODS.

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

try:
    from tests.by_module.services.users.test_user_collection_import_service import (
        FakeOdsCollectionImportReader,
        UserCollectionImportServiceTest,
    )
    from services.ods import OdsCollectionImportReadError
    from services.users.user_collection_import_service import (
        UserCollectionImportInvalidFileError,
        UserCollectionImportTemporaryFileMissingError,
    )
except ModuleNotFoundError:
    from tests.by_module.services.users.test_user_collection_import_service import (
        FakeOdsCollectionImportReader,
        UserCollectionImportServiceTest,
    )
    from services.ods import OdsCollectionImportReadError
    from services.users.user_collection_import_service import (
        UserCollectionImportInvalidFileError,
        UserCollectionImportTemporaryFileMissingError,
    )


class UserCollectionImportServiceGenericReaderTest(unittest.TestCase):
    """Valide l'utilisation d'un reader de collection non ODS."""

    def test_import_collection_accepts_non_ods_reader_from_factory(self):
        """Verifie que le service utilise l'extension issue du lecteur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le chemin final et les compteurs.
        """

        helper = UserCollectionImportServiceTest()
        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = helper._build_service(
                directory,
                reader=FakeOdsCollectionImportReader(accepted_extensions=(".txt",)),
                source_filename="collection.txt",
            )

            result = service.import_collection(
                7,
                str(source_file),
                "collection.txt",
                helper._valid_description(),
            )

            target_file = Path(directory) / "workspace" / "7" / "7-collection.txt"
            self.assertTrue(target_file.exists())
            self.assertEqual(str(target_file), reader.read_paths[0])
            self.assertEqual(1, result.created_games)
            self.assertEqual(1, len(repository.import_calls))

    def test_import_collection_exposes_invalid_reader_details(self):
        """Verifie les raisons affichables d'une erreur de lecture.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les details.
        """

        helper = UserCollectionImportServiceTest()
        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = helper._build_service(
                directory,
                reader=FakeOdsCollectionImportReader(error=OdsCollectionImportReadError("bad")),
            )

            with self.assertRaises(UserCollectionImportInvalidFileError) as context:
                service.import_collection(
                    7,
                    str(source_file),
                    "collection.ods",
                    helper._valid_description(),
                )

            self.assertEqual(["bad"], context.exception.details)
            self.assertEqual([], repository.import_calls)

    def test_temporary_file_workflow_uses_reader_extension_and_analysis(self):
        """Verifie le depot, l'analyse et l'import depuis un fichier temporaire."""

        helper = UserCollectionImportServiceTest()
        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = helper._build_service(
                directory,
                reader=FakeOdsCollectionImportReader(accepted_extensions=(".txt",)),
                source_filename="collection.txt",
            )

            service.upload_import_file(
                7,
                str(source_file),
                "collection.txt",
                helper._valid_description().file_type,
            )
            temporary_file = Path(directory) / "workspace" / "7" / "current-import.txt"
            self.assertTrue(temporary_file.exists())
            self.assertEqual(0o750, temporary_file.stat().st_mode & 0o777)

            self.assertEqual(
                ["Switch", "NES"],
                service.analyze_import_file(7, helper._valid_description().file_type),
            )
            result = service.import_collection_from_temporary_file(
                7,
                helper._valid_description(),
            )

            target_file = Path(directory) / "workspace" / "7" / "7-collection.txt"
            self.assertFalse(temporary_file.exists())
            self.assertTrue(target_file.exists())
            self.assertEqual(str(temporary_file), reader.analyze_paths[0])
            self.assertEqual(str(target_file), reader.read_paths[0])
            self.assertEqual(1, result.created_games)
            self.assertEqual(1, len(repository.import_calls))

    def test_analyze_import_file_rejects_missing_temporary_file(self):
        """Verifie le refus si le fichier temporaire est absent."""

        helper = UserCollectionImportServiceTest()
        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = helper._build_service(directory)

            with self.assertRaises(UserCollectionImportTemporaryFileMissingError):
                service.analyze_import_file(7, helper._valid_description().file_type)

            self.assertEqual([], reader.analyze_paths)
            self.assertEqual([], repository.import_calls)


if __name__ == "__main__":
    unittest.main()
