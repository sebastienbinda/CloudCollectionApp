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
# Description : tests des modes configurables du lecteur ODS d'import.

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.collection.imports import CollectionFileDescriptionValidator  # noqa: E402
from services.ods import OdsCollectionImportReader  # noqa: E402

try:
    from tests.test_ods_collection_import_reader import FakeOdsReader
except ModuleNotFoundError:
    from test_ods_collection_import_reader import FakeOdsReader


class ConfigurableOdsCollectionImportReaderTest(unittest.TestCase):
    """Valide les modes de configuration du lecteur ODS."""

    def test_read_uses_shared_layout_configuration(self):
        """Verifie un import multi-onglets avec layout partage.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les donnees importees.
        """

        service = self._service_for_reader(
            FakeOdsReader(
                ["Switch", "PC"],
                {
                    "Switch": self._dataframe(
                        [{"Nom du jeu": "Zelda", "Studio": "Nintendo", "Date de sortie": ""}]
                    ),
                    "PC": self._dataframe(
                        [{"Nom du jeu": "Doom", "Studio": "id Software", "Date de sortie": ""}]
                    ),
                },
            )
        )

        import_data = service.read("/tmp/shared.ods", self._shared_layout_description())

        self.assertEqual(["Switch", "PC"], [platform.name for platform in import_data.platforms])
        self.assertEqual(["Zelda", "Doom"], [game.name for game in import_data.games])

    def test_read_uses_per_sheet_configuration(self):
        """Verifie un import multi-onglets avec layout par onglet.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les donnees importees.
        """

        service = self._service_for_reader(
            FakeOdsReader(
                ["Switch", "PC"],
                {
                    "Switch": self._dataframe(
                        [{"Nom du jeu": "Zelda", "Studio": "Nintendo", "Date de sortie": ""}]
                    ),
                    "PC": self._dataframe(
                        [
                            {
                                "Nom du jeu": "Doom",
                                "Plateforme": "PC",
                                "Studio": "id Software",
                                "Date de sortie": "",
                            }
                        ]
                    ),
                },
            )
        )

        import_data = service.read("/tmp/per-sheet.ods", self._per_sheet_description())

        self.assertEqual(["Switch", "PC"], [platform.name for platform in import_data.platforms])
        self.assertEqual(["Zelda", "Doom"], [game.name for game in import_data.games])

    def test_read_applies_sheet_name_as_studio_information(self):
        """Verifie l'injection du nom d'onglet comme studio.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le studio porte par l'onglet.
        """

        service = self._service_for_reader(
            FakeOdsReader(
                ["Nintendo"],
                {
                    "Nintendo": self._dataframe(
                        [{"Nom du jeu": "Zelda", "Plateforme": "Switch", "Date de sortie": ""}]
                    )
                },
            )
        )

        import_data = service.read("/tmp/sheet-studio.ods", self._sheet_studio_description())

        self.assertEqual("Nintendo", import_data.games[0].studio_name)
        self.assertEqual(["Nintendo"], [studio.name for studio in import_data.studios])

    def _service_for_reader(self, fake_reader):
        return OdsCollectionImportReader(reader_factory=lambda ods_path: fake_reader)

    def _dataframe(self, rows):
        normalized_rows = []
        for row in rows:
            normalized_row = dict(row)
            normalized_row.setdefault("Plateforme", "Switch")
            normalized_rows.append(normalized_row)
        return pd.DataFrame(
            normalized_rows,
            columns=["Nom du jeu", "Plateforme", "Studio", "Date de sortie"],
        )

    def _shared_layout_description(self):
        return CollectionFileDescriptionValidator().validate(
            {
                "file_type": "libreoffice_ods",
                "wishlist": {"mode": "none"},
                "multiple_sheets_conf": {
                    "sheet_information": "platform",
                    "shared_layout": {
                        "data_range": "A1:D200",
                        "header_row": 1,
                        "column_information": {
                            "name": "A",
                            "studio": "C",
                            "release_date": "D",
                        },
                    },
                },
            }
        )

    def _per_sheet_description(self):
        return CollectionFileDescriptionValidator().validate(
            {
                "file_type": "libreoffice_ods",
                "wishlist": {"mode": "none"},
                "multiple_sheets_conf": {
                    "sheets": [
                        {
                            "sheet_name": "Switch",
                            "sheet_information": "platform",
                            "data_range": "A1:D200",
                            "header_row": 1,
                            "column_information": {
                                "name": "A",
                                "studio": "C",
                                "release_date": "D",
                            },
                        },
                        {
                            "sheet_name": "PC",
                            "data_range": "A1:D200",
                            "header_row": 1,
                            "column_information": {
                                "name": "A",
                                "platform": "B",
                                "studio": "C",
                                "release_date": "D",
                            },
                        },
                    ]
                },
            }
        )

    def _sheet_studio_description(self):
        return CollectionFileDescriptionValidator().validate(
            {
                "file_type": "libreoffice_ods",
                "wishlist": {"mode": "none"},
                "multiple_sheets_conf": {
                    "sheet_information": "studio",
                    "shared_layout": {
                        "data_range": "A1:D200",
                        "header_row": 1,
                        "column_information": {
                            "name": "A",
                            "platform": "B",
                            "release_date": "D",
                        },
                    },
                },
            }
        )


if __name__ == "__main__":
    unittest.main()
