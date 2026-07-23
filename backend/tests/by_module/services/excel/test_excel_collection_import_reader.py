#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-07-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du lecteur d'import de collection Excel.

import sys
import unittest
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.collection.imports import (  # noqa: E402
    CollectionFileDescriptionValidator,
)
from services.excel import (  # noqa: E402
    ExcelCollectionImportReadError,
    ExcelCollectionImportReader,
    ExcelCollectionImportValidationError,
)


class FakeExcelReader:
    """Simule le lecteur Excel bas niveau pour les tests d'import."""

    def __init__(self, sheet_names, dataframes_by_sheet=None, error=None, dataframe_error=None):
        """Initialise le lecteur Excel factice.

        Args:
            sheet_names (list[str]): Onglets retournes.
            dataframes_by_sheet (dict[str, pandas.DataFrame] | None): Donnees par onglet.
            error (Exception | None): Erreur a lever lors de la lecture des onglets.
            dataframe_error (Exception | None): Erreur a lever lors de la lecture d'une feuille.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.sheet_names = sheet_names
        self.dataframes_by_sheet = dataframes_by_sheet or {}
        self.error = error
        self.dataframe_error = dataframe_error
        self.sheet_dataframe_calls = []
        self.close_count = 0

    def list_sheets(self):
        """Retourne les onglets factices.

        Args:
            Aucun.

        Returns:
            list[str]: Noms d'onglets.

        Raises:
            Exception: Si le lecteur est configure avec une erreur.
        """

        if self.error:
            raise self.error
        return self.sheet_names

    def read_sheet_dataframe(self, sheet_name, data_range, header_row, selected_columns=None):
        """Retourne les jeux factices d'une feuille.

        Args:
            sheet_name (str): Nom de l'onglet.
            data_range (str): Plage demandee.
            header_row (int): Ligne d'en-tete.
            selected_columns (str | None): Colonnes configurees.

        Returns:
            pandas.DataFrame: Jeux de l'onglet.
        """

        self.sheet_dataframe_calls.append((sheet_name, data_range, header_row, selected_columns))
        if self.dataframe_error:
            raise self.dataframe_error
        return self.dataframes_by_sheet[sheet_name]

    def close(self):
        """Memorise la fermeture du lecteur.

        Args:
            Aucun.

        Returns:
            None: La methode met a jour le compteur.
        """

        self.close_count += 1


class ExcelCollectionImportReaderTest(unittest.TestCase):
    """Valide la lecture Excel dediee a l'import de collection utilisateur."""

    def test_analyze_sheets_returns_excel_sheet_names(self):
        """Verifie l'analyse des onglets Excel.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les noms et la fermeture.
        """

        fake_reader = FakeExcelReader(["Collection", "Wishlist"])
        service = self._service_for_reader(fake_reader)

        self.assertEqual(["Collection", "Wishlist"], service.analyze_sheets("/tmp/file.xlsx"))
        self.assertEqual(1, fake_reader.close_count)

    def test_read_returns_business_structure_for_valid_excel_file(self):
        """Verifie la structure metier retournee pour un fichier Excel valide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident plateformes, studios et jeux.
        """

        fake_reader = FakeExcelReader(
            ["Collection"],
            {
                "Collection": pd.DataFrame(
                    [
                        {
                            "Nom du jeu": " Zelda ",
                            "Plateforme": "Switch",
                            "Studio": " Nintendo ",
                            "Date de sortie": "2017-03-03",
                        },
                        {
                            "Nom du jeu": "Mario",
                            "Plateforme": "Switch",
                            "Studio": "Retro",
                            "Date de sortie": date(2023, 10, 20),
                        },
                    ]
                )
            },
        )
        service = self._service_for_reader(fake_reader)

        import_data = service.read("/tmp/collection.xlsx", self._single_sheet_description())

        self.assertEqual(
            [("Collection", "A1:D200", 1, "A,B,C,D")],
            fake_reader.sheet_dataframe_calls,
        )
        self.assertEqual(["Switch"], [platform.name for platform in import_data.platforms])
        self.assertEqual(["Nintendo", "Retro"], [studio.name for studio in import_data.studios])
        self.assertEqual(2, len(import_data.games))
        self.assertEqual("Zelda", import_data.games[0].name)
        self.assertEqual(date(2017, 3, 3), import_data.games[0].release_date)
        self.assertEqual(1, fake_reader.close_count)

    def test_read_rejects_empty_excel_workbook(self):
        """Verifie le refus d'un fichier Excel sans onglet importable.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de validation.
        """

        service = self._service_for_reader(FakeExcelReader([]))

        with self.assertRaises(ExcelCollectionImportValidationError):
            service.read("/tmp/empty.xlsx", self._single_sheet_description())

    def test_read_rejects_unreadable_excel_file(self):
        """Verifie le refus d'un fichier Excel illisible.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de lecture.
        """

        service = self._service_for_reader(FakeExcelReader([], error=OSError("boom")))

        with self.assertRaises(ExcelCollectionImportReadError):
            service.read("/tmp/broken.xlsx", self._single_sheet_description())

    def _service_for_reader(self, fake_reader):
        return ExcelCollectionImportReader(reader_factory=lambda _: fake_reader)

    def _single_sheet_description(self):
        return CollectionFileDescriptionValidator().validate(
            {
                "file_type": "excel_xlsx",
                "wishlist": {"mode": "none"},
                "single_sheet_conf": {
                    "data_range": "A1:D200",
                    "header_row": 1,
                    "column_information": {
                        "name": "A",
                        "platform": "B",
                        "studio": "C",
                        "release_date": "D",
                    },
                },
            }
        )


if __name__ == "__main__":
    unittest.main()
