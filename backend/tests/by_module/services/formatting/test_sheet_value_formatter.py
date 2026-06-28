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
from datetime import date, datetime
import unittest

import pandas as pd

from services.formatting import SheetValueFormatter


class SheetValueFormatterTest(unittest.TestCase):
    def test_clean_text_returns_none_for_empty_values(self):
        """Verifie le nettoyage des valeurs texte vides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        self.assertIsNone(SheetValueFormatter.clean_text(None))
        self.assertIsNone(SheetValueFormatter.clean_text("   "))
        self.assertIsNone(SheetValueFormatter.clean_text(float("nan")))
        self.assertIsNone(SheetValueFormatter.clean_text(pd.NaT))
        self.assertIsNone(SheetValueFormatter.clean_text("NaT"))
        self.assertIsNone(SheetValueFormatter.clean_text("Err:510"))
        self.assertEqual("Mario", SheetValueFormatter.clean_text(" Mario "))

    def test_serialize_converts_dates_and_nan(self):
        """Verifie la serialisation JSON des dates et valeurs NaN.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        self.assertEqual("2026-05-03", SheetValueFormatter.serialize(date(2026, 5, 3)))
        self.assertEqual(
            "2026-05-03T10:15:00",
            SheetValueFormatter.serialize(datetime(2026, 5, 3, 10, 15)),
        )
        self.assertIsNone(SheetValueFormatter.serialize(float("nan")))
        self.assertIsNone(SheetValueFormatter.serialize("NaT"))
        self.assertIsNone(SheetValueFormatter.serialize("Err:510"))
        self.assertEqual("Switch", SheetValueFormatter.serialize("Switch"))

    def test_normalize_platform_name_ignores_case_and_spaces(self):
        """Verifie la normalisation des noms de plateformes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        self.assertEqual(
            "playstation5",
            SheetValueFormatter.normalize_platform_name(" PlayStation 5 "),
        )


if __name__ == "__main__":
    unittest.main()
