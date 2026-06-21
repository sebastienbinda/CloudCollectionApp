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
# Description : tests des lignes de jeux sans nom importable.

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from tests.test_ods_collection_import_reader import FakeOdsReader, OdsCollectionImportReaderTest
except ModuleNotFoundError:
    from test_ods_collection_import_reader import FakeOdsReader, OdsCollectionImportReaderTest


class OdsCollectionImportEmptyGameNamesTest(unittest.TestCase):
    """Valide l'ignorance des lignes sans nom de jeu exploitable."""

    def test_read_ignores_rows_without_valid_game_name(self):
        """Verifie qu'une ligne sans nom de jeu importable est ignoree.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence de jeu `NaT`.
        """

        helper = OdsCollectionImportReaderTest()
        service = helper._service_for_reader(
            FakeOdsReader(
                ["Switch"],
                {
                    "Switch": helper._dataframe(
                        [
                            {
                                "Nom du jeu": pd.NaT,
                                "Studio": "Nintendo",
                                "Date de sortie": "2017-03-03",
                            },
                            {
                                "Nom du jeu": "",
                                "Studio": "Nintendo",
                                "Date de sortie": "2017-03-03",
                            },
                            {
                                "Nom du jeu": "Tomb Raider",
                                "Studio": "Core Design",
                                "Date de sortie": pd.NaT,
                            },
                        ]
                    )
                },
            )
        )

        import_data = service.read("/tmp/empty-name.ods", helper._single_sheet_description())

        self.assertEqual(["Tomb Raider"], [game.name for game in import_data.games])
        self.assertIsNone(import_data.games[0].release_date)

    def test_read_accepts_configured_optional_columns_with_empty_cells(self):
        """Verifie que les cellules optionnelles vides ne bloquent pas l'import.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le jeu importe sans information optionnelle.
        """

        helper = OdsCollectionImportReaderTest()
        service = helper._service_for_reader(
            FakeOdsReader(
                ["Switch"],
                {
                    "Switch": helper._dataframe(
                        [
                            {
                                "Nom du jeu": "Tomb Raider",
                                "Studio": "",
                                "Date de sortie": pd.NaT,
                            }
                        ]
                    )
                },
            )
        )

        import_data = service.read("/tmp/empty-optionals.ods", helper._single_sheet_description())

        self.assertEqual(1, len(import_data.games))
        self.assertIsNone(import_data.games[0].studio_name)
        self.assertIsNone(import_data.games[0].release_date)
        self.assertEqual([], import_data.warnings.invalid_games)


if __name__ == "__main__":
    unittest.main()
