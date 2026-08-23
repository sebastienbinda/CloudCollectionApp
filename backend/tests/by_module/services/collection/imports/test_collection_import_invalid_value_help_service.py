#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de l'aide aux valeurs d'import refusees.

import unittest

from services.collection.imports import CollectionImportInvalidValueHelpService


class CollectionImportInvalidValueHelpServiceTest(unittest.TestCase):
    """Valide les aides de correction des valeurs refusees."""

    def test_get_help_returns_region_reason_and_possible_values(self):
        """Verifie l'aide d'une region invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la raison et les valeurs possibles.
        """

        help_result = CollectionImportInvalidValueHelpService().get_help(
            "region",
            "Ici ou parla",
        )

        self.assertEqual("region", help_result.field)
        self.assertEqual("Ici ou parla", help_result.value)
        self.assertIn("region", help_result.reason)
        self.assertIn("EU-FR", help_result.possible_values)
        self.assertIn("PAL - UK", help_result.possible_values)

    def test_get_help_returns_generic_reason_for_unknown_field(self):
        """Verifie le repli pour un champ inconnu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le repli.
        """

        help_result = CollectionImportInvalidValueHelpService().get_help(
            "custom",
            "x",
        )

        self.assertEqual("custom", help_result.field)
        self.assertEqual("x", help_result.value)
        self.assertEqual([], help_result.possible_values)
        self.assertIn("format attendu", help_result.reason)


if __name__ == "__main__":
    unittest.main()
