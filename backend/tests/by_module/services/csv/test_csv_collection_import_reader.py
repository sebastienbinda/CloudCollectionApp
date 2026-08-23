#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-26
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du reader CSV d'import de collection.

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.collection.imports import (  # noqa: E402
    CollectionFileDescriptionValidationError,
    CollectionFileDescriptionValidator,
)
from services.csv import (  # noqa: E402
    CsvCollectionImportReader,
    CsvCollectionImportValidationError,
)


class CsvCollectionImportReaderTest(unittest.TestCase):
    """Valide la lecture CSV du workflow d'import de collection."""

    def setUp(self):
        """Prepare le reader et le validateur testes.

        Args:
            Aucun.

        Returns:
            None: Les dependances sont initialisees.
        """

        self.reader = CsvCollectionImportReader()
        self.validator = CollectionFileDescriptionValidator()

    def test_analyze_sheets_returns_csv_columns(self):
        """Verifie que l'analyse retourne les noms de colonnes CSV.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les colonnes detectees.
        """

        csv_path = self._write_csv("Jeu;Console;Studio\nZelda;Switch;Nintendo\n")

        self.assertEqual(["Jeu", "Console", "Studio"], self.reader.analyze_sheets(csv_path))

    def test_read_maps_valid_csv_games(self):
        """Verifie le mapping nominal des jeux CSV.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les donnees importees.
        """

        csv_path = self._write_csv(
            "Jeu;Console;Studio;Sortie;Prix;Souhait;Notice\n"
            "Zelda;Switch;Nintendo;2017-03-03;49,999;Oui;Oui\n"
            "Mario;Switch;Nintendo;2018;39.90;Non;Non\n"
        )
        description = self._description()

        import_data = self.reader.read(csv_path, description)

        self.assertEqual(["Switch"], [platform.name for platform in import_data.platforms])
        self.assertEqual(["Nintendo"], [studio.name for studio in import_data.studios])
        self.assertEqual(2, len(import_data.games))
        self.assertEqual("Zelda", import_data.games[0].name)
        self.assertEqual("49.99", str(import_data.games[0].purchase_price))
        self.assertEqual("EUR", import_data.games[0].price_unit)
        self.assertTrue(import_data.games[0].wishlist)
        self.assertTrue(import_data.games[0].has_manual)
        self.assertFalse(import_data.games[1].wishlist)

    def test_read_ignores_empty_game_names_and_empty_optionals(self):
        """Verifie que les noms vides sont ignores sans warning optionnel vide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les lignes retenues et les warnings.
        """

        csv_path = self._write_csv(
            "Jeu;Console;Studio;Sortie;Prix;Souhait;Notice\n"
            ";Switch;Nintendo;2017-03-03;49;Oui;Oui\n"
            "Mario;Switch;;;;Non;\n"
        )

        import_data = self.reader.read(csv_path, self._description())

        self.assertEqual(["Mario"], [game.name for game in import_data.games])
        self.assertEqual([], import_data.warnings.invalid_games)
        self.assertEqual(1, import_data.warnings.skipped_mandatory_games)
        self.assertEqual(0, import_data.warnings.invalid_wishlist)

    def test_read_reports_invalid_optional_values(self):
        """Verifie les warnings sur valeurs optionnelles non vides invalides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les warnings invalid_games.
        """

        csv_path = self._write_csv(
            "Jeu;Console;Studio;Sortie;Prix;Souhait;Notice\n"
            "Zelda;Switch;Nintendo;1900-01-01;-1;Non;Peut etre\n"
        )

        import_data = self.reader.read(csv_path, self._description())

        self.assertEqual(1, len(import_data.games))
        invalid_fields = {
            field["field"]
            for field in import_data.warnings.invalid_games[0]["invalid_fields"]
        }
        self.assertEqual({"release_date", "purchase_price", "has_manual"}, invalid_fields)

    def test_read_skips_invalid_wishlist_rows(self):
        """Verifie qu'une valeur wishlist invalide ignore la ligne CSV.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le compteur wishlist.
        """

        csv_path = self._write_csv(
            "Jeu;Console;Studio;Sortie;Prix;Souhait;Notice\n"
            "Zelda;Switch;Nintendo;2017-03-03;49;Peut etre;Oui\n"
        )

        import_data = self.reader.read(csv_path, self._description())

        self.assertEqual([], import_data.games)
        self.assertEqual(1, import_data.warnings.invalid_wishlist)
        self.assertEqual(["Peut etre"], import_data.warnings.invalid_wishlist_values_found)

    def test_read_rejects_missing_configured_column(self):
        """Verifie le refus d'une colonne configuree absente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de configuration.
        """

        csv_path = self._write_csv("Jeu;Console\nZelda;Switch\n")

        with self.assertRaises(CollectionFileDescriptionValidationError):
            self.reader.read(csv_path, self._description())

    def test_analyze_rejects_empty_or_invalid_header(self):
        """Verifie les erreurs structurelles de fichier CSV.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de validation.
        """

        csv_path = self._write_csv("")

        with self.assertRaises(CsvCollectionImportValidationError):
            self.reader.analyze_sheets(csv_path)

    def _description(self):
        return self.validator.validate(
            {
                "file_type": "csv",
                "wishlist": {"mode": "column"},
                "price_unit": "EUR",
                "mapping": {
                    "name": "Jeu",
                    "platform": "Console",
                    "studio": "Studio",
                    "release_date": "Sortie",
                    "purchase_price": "Prix",
                    "wishlist": "Souhait",
                    "has_manual": "Notice",
                },
            }
        )

    def _write_csv(self, content: str) -> str:
        temporary_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            encoding="utf-8",
            newline="",
            delete=False,
        )
        with temporary_file:
            temporary_file.write(content)
        return temporary_file.name


if __name__ == "__main__":
    unittest.main()
