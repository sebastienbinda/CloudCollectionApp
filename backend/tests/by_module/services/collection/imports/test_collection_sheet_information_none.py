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
# Description : tests du contrat multi-onglets sans information portee par l'onglet.

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.collection.imports import (  # noqa: E402
    CollectionFileDescriptionValidationError,
    CollectionFileDescriptionValidator,
    CollectionImportField,
)


class CollectionSheetInformationNoneTest(unittest.TestCase):
    """Valide le mode multi-onglets sans champ porte par le nom d'onglet."""

    def setUp(self):
        """Prepare le validateur teste.

        Args:
            Aucun.

        Returns:
            None: Le validateur est initialise.
        """

        self.validator = CollectionFileDescriptionValidator()

    def test_accepts_shared_layout_without_sheet_information(self):
        """Verifie que la plateforme peut venir d'une colonne en layout partage.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la configuration.
        """

        description = self.validator.validate({
            "file_type": "libreoffice_ods",
            "wishlist": {"mode": "none"},
            "multiple_sheets_conf": {
                "shared_layout": {
                    "data_range": "A1:C200",
                    "header_row": 1,
                    "column_information": {"name": "A", "platform": "B", "studio": "C"},
                },
            },
        })

        self.assertIsNone(description.multiple_sheets_conf.sheet_information)
        self.assertEqual(
            "B",
            description.multiple_sheets_conf.shared_layout.column_information[
                CollectionImportField.PLATFORM
            ],
        )
        self.assertNotIn("sheet_information", description.to_dict()["multiple_sheets_conf"])

    def test_rejects_shared_layout_without_platform_column(self):
        """Verifie que la colonne plateforme reste obligatoire dans ce mode.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        with self.assertRaises(CollectionFileDescriptionValidationError) as context:
            self.validator.validate({
                "file_type": "libreoffice_ods",
                "wishlist": {"mode": "none"},
                "multiple_sheets_conf": {
                    "shared_layout": {
                        "data_range": "A1:C200",
                        "header_row": 1,
                        "column_information": {"name": "A", "studio": "C"},
                    },
                },
            })

        self.assertIn("colonne obligatoire manquante: platform.", context.exception.details)

    def test_accepts_per_sheet_layout_without_sheet_information(self):
        """Verifie le meme contrat pour une configuration par onglet.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la configuration.
        """

        description = self.validator.validate({
            "file_type": "libreoffice_ods",
            "wishlist": {"mode": "none"},
            "multiple_sheets_conf": {
                "sheets": [{
                    "sheet_name": "Jeux 2026",
                    "data_range": "A1:C200",
                    "header_row": 1,
                    "column_information": {"name": "A", "platform": "B", "studio": "C"},
                }],
            },
        })

        sheet = description.multiple_sheets_conf.sheets[0]
        self.assertIsNone(sheet.sheet_information)
        self.assertEqual("B", sheet.layout.column_information[CollectionImportField.PLATFORM])
        self.assertNotIn("sheet_information", description.to_dict()["multiple_sheets_conf"]["sheets"][0])


if __name__ == "__main__":
    unittest.main()
