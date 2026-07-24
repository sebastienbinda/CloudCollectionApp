#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du lecteur CSV du catalogue plateformes.

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from services.database import PlatformCatalogCsvReader


class PlatformCatalogCsvReaderTest(unittest.TestCase):
    """Valide le parsing du CSV de plateformes."""

    def test_read_parses_partial_dates_and_special_values(self):
        """Verifie les dates partielles, `Inconnue` et `En vente`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les conversions.
        """

        csv_path = self._write_csv(
            "nom_machine,nom_fabricant,date_mise_en_vente,date_retrait_vente\n"
            "Console A,Fabricant A,2020,En vente\n"
            "Console B,Fabricant B,2020-05,Inconnue\n"
            "Console C,Fabricant C,2020-05-12,2021-06\n"
        )

        entries = PlatformCatalogCsvReader().read(csv_path)

        self.assertEqual(datetime(2020, 1, 1), entries[0].release_date)
        self.assertIsNone(entries[0].end_date)
        self.assertEqual(datetime(2020, 5, 1), entries[1].release_date)
        self.assertIsNone(entries[1].end_date)
        self.assertEqual(datetime(2020, 5, 12), entries[2].release_date)
        self.assertEqual(datetime(2021, 6, 1), entries[2].end_date)
        self.assertEqual({}, entries[0].description)

    def test_read_rejects_missing_column(self):
        """Verifie le refus d'une colonne obligatoire absente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        csv_path = self._write_csv(
            "nom_machine,nom_fabricant,date_mise_en_vente\n"
            "Console A,Fabricant A,2020\n"
        )

        with self.assertRaisesRegex(ValueError, "date_retrait_vente"):
            PlatformCatalogCsvReader().read(csv_path)

    def test_read_rejects_empty_name(self):
        """Verifie le refus d'un nom de plateforme vide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        csv_path = self._write_csv(
            "nom_machine,nom_fabricant,date_mise_en_vente,date_retrait_vente\n"
            ",Fabricant A,2020,En vente\n"
        )

        with self.assertRaisesRegex(ValueError, "nom_machine"):
            PlatformCatalogCsvReader().read(csv_path)

    def test_read_rejects_available_value_as_release_date(self):
        """Verifie que `En vente` est interdit en date de sortie.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        csv_path = self._write_csv(
            "nom_machine,nom_fabricant,date_mise_en_vente,date_retrait_vente\n"
            "Console A,Fabricant A,En vente,En vente\n"
        )

        with self.assertRaisesRegex(ValueError, "En vente"):
            PlatformCatalogCsvReader().read(csv_path)

    def test_project_catalog_contains_pc_platform(self):
        """Verifie la presence de la plateforme PC dans le catalogue applicatif.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la ligne de reference PC.
        """

        catalog_path = Path(__file__).resolve().parents[4] / "resources" / "platform_catalog.csv"

        entries = PlatformCatalogCsvReader().read(catalog_path)
        pc_entries = [entry for entry in entries if entry.name == "PC"]

        self.assertEqual(1, len(pc_entries))
        self.assertEqual("Multi-constructeurs", pc_entries[0].manufacturer)
        self.assertIsNone(pc_entries[0].end_date)

    def _write_csv(self, content: str) -> Path:
        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        csv_path = Path(temporary_directory.name) / "platforms.csv"
        csv_path.write_text(content, encoding="utf-8")
        return csv_path


if __name__ == "__main__":
    unittest.main()
