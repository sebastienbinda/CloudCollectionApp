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
# Description : tests wishlist du lecteur ODS d'import de collection.

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


class OdsCollectionImportWishlistReaderTest(unittest.TestCase):
    """Valide la lecture wishlist dans les imports ODS."""

    def test_read_without_wishlist_marks_every_game_as_collection(self):
        """Verifie le mode sans wishlist."""

        import_data = self._read(
            ["Collection"],
            {"Collection": self._dataframe([{"Nom du jeu": "Zelda"}])},
            self._single_sheet_description("none"),
        )

        self.assertEqual([False], [game.wishlist for game in import_data.games])
        self.assertEqual(0, import_data.warnings.invalid_wishlist)

    def test_read_wishlist_sheet_marks_dedicated_sheet_and_keeps_collection_duplicate(self):
        """Verifie l'onglet dedie et la priorite collection reelle."""

        import_data = self._read(
            ["Collection", "Wishlist"],
            {
                "Collection": self._dataframe([{"Nom du jeu": "Zelda"}]),
                "Wishlist": self._dataframe([
                    {"Nom du jeu": "Zelda"},
                    {"Nom du jeu": "Metroid"},
                ]),
            },
            self._wishlist_sheet_description(),
        )

        wishlist_by_name = {game.name: game.wishlist for game in import_data.games}
        self.assertEqual({"Zelda": False, "Metroid": True}, wishlist_by_name)

    def test_read_single_sheet_wishlist_column_parses_values_and_warnings(self):
        """Verifie les valeurs booleennes, vides et invalides en feuille unique."""

        import_data = self._read(
            ["Collection"],
            {
                "Collection": self._dataframe(
                    [
                        {"Nom du jeu": "Zelda", "Wishlist": "Oui"},
                        {"Nom du jeu": "Mario", "Wishlist": "No"},
                        {"Nom du jeu": "Doom", "Wishlist": ""},
                        {"Nom du jeu": "Chrono", "Wishlist": "Peut etre"},
                    ],
                    include_wishlist=True,
                )
            },
            self._single_sheet_description("column"),
        )

        self.assertEqual(["Zelda", "Mario", "Doom"], [game.name for game in import_data.games])
        self.assertEqual([True, False, False], [game.wishlist for game in import_data.games])
        self.assertEqual(1, import_data.warnings.invalid_wishlist)
        self.assertEqual(["Peut etre"], import_data.warnings.invalid_wishlist_values_found)

    def test_read_shared_layout_wishlist_column(self):
        """Verifie le mode colonne avec layout partage multi-onglets."""

        import_data = self._read(
            ["Switch", "PC"],
            {
                "Switch": self._dataframe(
                    [{"Nom du jeu": "Zelda", "Wishlist": "Y"}],
                    include_wishlist=True,
                    include_platform=False,
                ),
                "PC": self._dataframe(
                    [{"Nom du jeu": "Doom", "Wishlist": "N"}],
                    include_wishlist=True,
                    include_platform=False,
                ),
            },
            self._shared_layout_column_description(),
        )

        self.assertEqual(["Zelda", "Doom"], [game.name for game in import_data.games])
        self.assertEqual([True, False], [game.wishlist for game in import_data.games])

    def test_read_per_sheet_wishlist_column_and_true_duplicate_priority(self):
        """Verifie les layouts par onglet et la priorite du premier souhait."""

        import_data = self._read(
            ["Switch", "PC"],
            {
                "Switch": self._dataframe(
                    [{"Nom du jeu": "Doom", "Wishlist": "Yes"}],
                    include_wishlist=True,
                    include_platform=False,
                ),
                "PC": self._dataframe(
                    [{"Nom du jeu": "Doom", "Plateforme": "Switch", "Wishlist": "No"}],
                    include_wishlist=True,
                ),
            },
            self._per_sheet_column_description(),
        )

        self.assertEqual(["Doom"], [game.name for game in import_data.games])
        self.assertEqual([True], [game.wishlist for game in import_data.games])

    def _read(self, sheet_names, dataframes_by_sheet, description):
        return OdsCollectionImportReader(
            reader_factory=lambda ods_path: FakeOdsReader(sheet_names, dataframes_by_sheet)
        ).read("/tmp/collection.ods", description)

    def _dataframe(self, rows, include_wishlist=False, include_platform=True):
        columns = ["Nom du jeu"]
        if include_platform:
            columns.append("Plateforme")
        columns.extend(["Studio", "Date de sortie"])
        if include_wishlist:
            columns.append("Wishlist")
        normalized_rows = []
        for row in rows:
            normalized_row = dict(row)
            normalized_row.setdefault("Plateforme", "Switch")
            normalized_row.setdefault("Studio", "Nintendo")
            normalized_row.setdefault("Date de sortie", "")
            normalized_row.setdefault("Wishlist", "")
            normalized_rows.append(normalized_row)
        return pd.DataFrame(normalized_rows, columns=columns)

    def _single_sheet_description(self, wishlist_mode):
        payload = {
            "file_type": "libreoffice_ods",
            "wishlist": {"mode": wishlist_mode},
            "single_sheet_conf": self._layout(include_platform=True, include_wishlist=False),
        }
        if wishlist_mode == "column":
            payload["single_sheet_conf"] = self._layout(True, True)
        return CollectionFileDescriptionValidator().validate(payload)

    def _wishlist_sheet_description(self):
        return CollectionFileDescriptionValidator().validate(
            {
                "file_type": "libreoffice_ods",
                "wishlist": {
                    "mode": "sheet",
                    "sheet_name": "Wishlist",
                    **self._layout(include_platform=True, include_wishlist=False),
                },
                "single_sheet_conf": self._layout(True, False),
            }
        )

    def _shared_layout_column_description(self):
        return CollectionFileDescriptionValidator().validate(
            {
                "file_type": "libreoffice_ods",
                "wishlist": {"mode": "column"},
                "multiple_sheets_conf": {
                    "sheet_information": "platform",
                    "shared_layout": self._layout(False, True),
                },
            }
        )

    def _per_sheet_column_description(self):
        return CollectionFileDescriptionValidator().validate(
            {
                "file_type": "libreoffice_ods",
                "wishlist": {"mode": "column"},
                "multiple_sheets_conf": {
                    "sheets": [
                        {
                            "sheet_name": "Switch",
                            "sheet_information": "platform",
                            **self._layout(False, True),
                        },
                        {
                            "sheet_name": "PC",
                            **self._layout(True, True),
                        },
                    ]
                },
            }
        )

    def _layout(self, include_platform, include_wishlist):
        column_information = {
            "name": "A",
            "studio": "C" if include_platform else "B",
            "release_date": "D" if include_platform else "C",
        }
        if include_platform:
            column_information["platform"] = "B"
        if include_wishlist:
            column_information["wishlist"] = "E" if include_platform else "D"
        return {
            "data_range": "A1:E200" if include_wishlist and include_platform else "A1:D200",
            "header_row": 1,
            "column_information": column_information,
        }


if __name__ == "__main__":
    unittest.main()
