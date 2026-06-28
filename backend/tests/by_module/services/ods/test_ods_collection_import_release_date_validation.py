#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-10
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests des dates de sortie invalides dans le reader ODS.

import logging
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

try:
    from tests.by_module.services.ods.test_ods_collection_import_reader import FakeOdsReader, OdsCollectionImportReaderTest
except ModuleNotFoundError:
    from tests.by_module.services.ods.test_ods_collection_import_reader import FakeOdsReader, OdsCollectionImportReaderTest


class OdsCollectionImportReleaseDateValidationTest(unittest.TestCase):
    """Valide les warnings de dates invalides dans le reader ODS."""

    def test_read_warns_and_keeps_too_old_release_date_as_none(self):
        """Verifie qu'une date anterieure aux jeux video devient `None`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'avertissement et la date nulle.
        """

        helper = OdsCollectionImportReaderTest()
        logger = logging.getLogger("tests.ods_import_reader.too_old_date")
        service = helper._service_for_reader(
            FakeOdsReader(
                ["Switch"],
                {
                    "Switch": helper._dataframe(
                        [
                            {
                                "Nom du jeu": "Penny Blood",
                                "Studio": "Yukikaze",
                                "Date de sortie": "0200-11-24",
                            }
                        ]
                    )
                },
            ),
            logger=logger,
        )

        with self.assertLogs(logger, level="WARNING") as logs:
            import_data = service.read("/tmp/too-old-date.ods", helper._single_sheet_description())

        self.assertEqual(["Penny Blood"], [game.name for game in import_data.games])
        self.assertIsNone(import_data.games[0].release_date)
        self.assertIn("Date de sortie invalide", logs.output[0])
        self.assertEqual(
            [
                {
                    "name": "Penny Blood",
                    "invalid_fields": [
                        {"field": "release_date", "value": "0200-11-24"},
                    ],
                }
            ],
            import_data.warnings.invalid_games,
        )


if __name__ == "__main__":
    unittest.main()
