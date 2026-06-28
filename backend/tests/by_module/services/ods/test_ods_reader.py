#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from services.ods import OdsCache, OdsReader, OdsXmlReader


class OdsReaderImportTest(unittest.TestCase):
    def setUp(self):
        """Prepare un lecteur ODS d'import avec dependances factices.

        Args:
            Aucun.

        Returns:
            None: L'instance de test est initialisee.
        """

        self.reader = OdsReader(
            ods_path="/tmp/import.ods",
            cache=OdsCache("/tmp/import.ods"),
        )
        self.reader.cache.reset()

    def test_list_sheets_returns_all_sheet_names(self):
        """Verifie que tous les onglets du fichier sont exposes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la liste brute des onglets.
        """

        excel_file = MagicMock()
        excel_file.sheet_names = ["Accueil", "Switch", "Liste de souhaits", "Playstation"]
        with patch("services.ods.ods_reader.pd.ExcelFile", return_value=excel_file):
            sheets = self.reader.list_sheets()

        self.assertEqual(["Accueil", "Switch", "Liste de souhaits", "Playstation"], sheets)

    def test_read_sheet_dataframe_uses_selected_columns_when_provided(self):
        """Verifie que la lecture configurable peut cibler les colonnes utiles.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les options pandas.
        """

        dataframe = pd.DataFrame([{"Nom": "Zelda", "Studio": "Nintendo"}])
        with patch("services.ods.ods_reader.pd.read_excel", return_value=dataframe) as read_excel:
            sheet = self.reader.read_sheet_dataframe("Collection", "A1:H200", 1, "A,C")

        self.assertEqual("Zelda", sheet.iloc[0]["Nom"])
        read_excel.assert_called_once()
        self.assertEqual("A,C", read_excel.call_args.kwargs["usecols"])
        self.assertEqual(199, read_excel.call_args.kwargs["nrows"])

    def test_read_sheet_dataframe_fills_selected_trailing_empty_columns(self):
        """Verifie la lecture de colonnes configurees mais entierement vides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le repli et les valeurs absentes.
        """

        complete_dataframe = pd.DataFrame(
            [[None] * 5 + ["Zelda", "Nintendo", "2000-01-01", None, "Paris", "A", 20]],
            columns=[f"column-{index}" for index in range(12)],
        )
        out_of_bounds_error = ValueError(
            "Defining usecols with out-of-bounds indices is not allowed. "
            "[13, 14] are out-of-bounds."
        )
        with patch(
            "services.ods.ods_reader.pd.read_excel",
            side_effect=[out_of_bounds_error, complete_dataframe],
        ) as read_excel:
            sheet = self.reader.read_sheet_dataframe(
                "Playstation2",
                "F6:O700",
                6,
                "F,G,H,I,J,K,L,M,N,O",
            )

        self.assertEqual(2, read_excel.call_count)
        self.assertNotIn("usecols", read_excel.call_args_list[1].kwargs)
        self.assertEqual("Zelda", sheet.iloc[0, 0])
        self.assertEqual(20, sheet.iloc[0, 6])
        self.assertIsNone(sheet.iloc[0, 7])
        self.assertIsNone(sheet.iloc[0, 8])
        self.assertIsNone(sheet.iloc[0, 9])

    def test_read_sheet_dataframe_does_not_hide_other_value_errors(self):
        """Verifie que les erreurs sans rapport avec `usecols` restent bloquantes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la propagation de l'erreur.
        """

        with patch(
            "services.ods.ods_reader.pd.read_excel",
            side_effect=ValueError("ODS corrompu"),
        ) as read_excel:
            with self.assertRaisesRegex(ValueError, "ODS corrompu"):
                self.reader.read_sheet_dataframe("Playstation2", "F6:O700", 6, "F,O")

        read_excel.assert_called_once()

    def test_xml_reader_returns_none_for_formula_float_without_cached_value(self):
        """Verifie la lecture d'une formule sans resultat calcule en cache.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence de crash et la valeur vide.
        """

        value_type_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value-type"
        value_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value"
        date_value_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}date-value"
        cell = self._cell_with_attribute(value_type_attribute, "float")

        xml_reader = OdsXmlReader.__new__(OdsXmlReader)
        value = xml_reader.extract_cell_value(
            cell,
            value_type_attribute,
            value_attribute,
            date_value_attribute,
        )

        self.assertIsNone(value)

    def _cell_with_attribute(self, attribute, value):
        """Construit une cellule XML avec un attribut.

        Args:
            attribute (str): Nom qualifie de l'attribut XML.
            value (str): Valeur d'attribut.

        Returns:
            xml.etree.ElementTree.Element: Cellule XML factice.
        """

        import xml.etree.ElementTree as ET

        return ET.Element(
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell",
            {attribute: value},
        )


if __name__ == "__main__":
    unittest.main()
