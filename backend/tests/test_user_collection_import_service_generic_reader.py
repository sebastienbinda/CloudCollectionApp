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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from tests.test_user_collection_import_service import (
        FakeOdsCollectionImportReader,
        UserCollectionImportServiceTest,
    )
except ModuleNotFoundError:
    from test_user_collection_import_service import (
        FakeOdsCollectionImportReader,
        UserCollectionImportServiceTest,
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


if __name__ == "__main__":
    unittest.main()
