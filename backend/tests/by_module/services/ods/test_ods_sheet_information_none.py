#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests ODS du mode multi-onglets sans information d'onglet.

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.collection.imports import CollectionFileDescriptionValidator  # noqa: E402
from services.ods import OdsCollectionImportReader  # noqa: E402

try:
    from tests.by_module.services.ods.test_ods_collection_import_reader import FakeOdsReader
except ModuleNotFoundError:
    from tests.by_module.services.ods.test_ods_collection_import_reader import FakeOdsReader


class OdsSheetInformationNoneTest(unittest.TestCase):
    """Valide la lecture ODS quand l'onglet ne porte aucune information."""

    def test_read_uses_platform_column_when_sheet_information_is_missing(self):
        """Verifie que la plateforme importee vient de la colonne configuree.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les jeux lus.
        """

        fake_reader = FakeOdsReader(
            ["Janvier", "Fevrier"],
            {
                "Janvier": self._dataframe("Zelda", "Switch"),
                "Fevrier": self._dataframe("Doom", "PC"),
            },
        )
        service = OdsCollectionImportReader(reader_factory=lambda ods_path: fake_reader)

        import_data = service.read("/tmp/no-sheet-info.ods", self._description())

        self.assertEqual(["Switch", "PC"], [platform.name for platform in import_data.platforms])
        self.assertEqual(["Switch", "PC"], [game.platform_name for game in import_data.games])
        self.assertEqual(
            [("Janvier", "A1:C200", 1, "A,B,C"), ("Fevrier", "A1:C200", 1, "A,B,C")],
            fake_reader.sheet_dataframe_calls,
        )

    def _dataframe(self, name, platform):
        return pd.DataFrame(
            [{"Nom du jeu": name, "Plateforme": platform, "Studio": ""}],
            columns=["Nom du jeu", "Plateforme", "Studio"],
        )

    def _description(self):
        return CollectionFileDescriptionValidator().validate({
            "file_type": "libreoffice_ods",
            "wishlist": {"mode": "none"},
            "multiple_sheets_conf": {
                "shared_layout": {
                    "included_sheets": ["Janvier", "Fevrier"],
                    "data_range": "A1:C200",
                    "header_row": 1,
                    "column_information": {"name": "A", "platform": "B", "studio": "C"},
                },
            },
        })


if __name__ == "__main__":
    unittest.main()
