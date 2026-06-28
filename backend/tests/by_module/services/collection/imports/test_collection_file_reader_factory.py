#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de la factory de lecteurs de fichiers de collection.

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.collection.imports import (  # noqa: E402
    CollectionFileReaderFactory,
    CollectionFileType,
)
from services.csv import CsvCollectionImportReader  # noqa: E402
from services.ods import OdsCollectionImportReader  # noqa: E402


class CollectionFileReaderFactoryTest(unittest.TestCase):
    """Valide la selection des lecteurs de fichiers de collection."""

    def test_create_returns_ods_reader_for_libreoffice_ods(self):
        """Verifie le mapping du type LibreOffice ODS.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le lecteur retourne.
        """

        reader = CollectionFileReaderFactory().create(CollectionFileType.LIBREOFFICE_ODS)

        self.assertIsInstance(reader, OdsCollectionImportReader)
        self.assertEqual((".ods",), reader.accepted_extensions)

    def test_create_returns_csv_reader_for_csv(self):
        """Verifie le mapping du type CSV.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le lecteur retourne.
        """

        reader = CollectionFileReaderFactory().create(CollectionFileType.CSV)

        self.assertIsInstance(reader, CsvCollectionImportReader)
        self.assertEqual((".csv",), reader.accepted_extensions)


if __name__ == "__main__":
    unittest.main()
