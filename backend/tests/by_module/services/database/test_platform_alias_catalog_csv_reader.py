#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-15
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du lecteur CSV des alias de plateformes.

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from services.database import PlatformAliasCatalogCsvReader


class PlatformAliasCatalogCsvReaderTest(unittest.TestCase):
    """Valide la lecture du catalogue CSV des alias de plateformes."""

    def test_read_returns_alias_entries(self):
        """Verifie la conversion des lignes CSV en entrees d'alias.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les valeurs normalisees.
        """

        with TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "aliases.csv"
            csv_path.write_text(
                '"nom_machine","nom_alternatif","categorie","zone_ou_usage","commentaire"\n'
                '"Super Nintendo Entertainment System / Super Famicom",'
                '"Super Nintendo","nom_court","France","Nom courant."\n',
                encoding="utf-8",
            )

            entries = PlatformAliasCatalogCsvReader().read(csv_path)

        self.assertEqual(1, len(entries))
        self.assertEqual(
            "Super Nintendo Entertainment System / Super Famicom",
            entries[0].platform_name,
        )
        self.assertEqual("Super Nintendo", entries[0].alias_name)
        self.assertEqual("nom_court", entries[0].category)

    def test_read_rejects_missing_required_column(self):
        """Verifie le refus d'un CSV sans colonne obligatoire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        with TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "aliases.csv"
            csv_path.write_text(
                '"nom_machine","categorie","zone_ou_usage","commentaire"\n'
                '"NES","abreviation","Occident","Alias."\n',
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                PlatformAliasCatalogCsvReader().read(csv_path)

    def test_project_alias_catalog_contains_pc_import_aliases(self):
        """Verifie les alias PC utiles au matching d'import.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les alias de boutiques et systemes.
        """

        catalog_path = (
            Path(__file__).resolve().parents[4] / "resources" / "platform_alias_catalog.csv"
        )

        entries = PlatformAliasCatalogCsvReader().read(catalog_path)
        pc_aliases = {
            entry.alias_name
            for entry in entries
            if entry.platform_name == "PC"
        }

        self.assertTrue({
            "Steam",
            "Steam machine",
            "Epic",
            "Epic Game Store",
            "GoG",
            "Good Old Games",
            "Windows",
            "Ordinateur",
            "Mac",
            "Mac OS",
            "Mac OSX",
        }.issubset(pc_aliases))


if __name__ == "__main__":
    unittest.main()
