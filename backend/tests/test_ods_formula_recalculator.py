#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-04
# Auteurs : Codex et Binda Sébastien
# License : Apache 2.0
#
"""Tests du recalcul LibreOffice des formules ODS.

Description:
    Ce module valide le comportement du service de recalcul lorsque LibreOffice
    est absent, obligatoire ou desactive.
"""

import unittest

from services.ods.ods_formula_recalculator import OdsFormulaRecalculator


class OdsFormulaRecalculatorTest(unittest.TestCase):
    """Tests unitaires du service de recalcul LibreOffice."""

    def test_auto_mode_skips_when_libreoffice_is_missing(self):
        """Verifie que le mode auto ignore LibreOffice absent.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le retour sans erreur.
        """

        recalculator = OdsFormulaRecalculator(mode="auto", binary_path="")

        self.assertFalse(recalculator.recalculate("/tmp/missing.ods"))

    def test_required_mode_rejects_missing_libreoffice(self):
        """Verifie que le mode requis echoue si LibreOffice est absent.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur attendue.
        """

        recalculator = OdsFormulaRecalculator(mode="required", binary_path="")

        with self.assertRaises(ValueError):
            recalculator.recalculate("/tmp/missing.ods")

    def test_disabled_mode_never_runs_libreoffice(self):
        """Verifie que le mode desactive saute toujours le recalcul.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le retour sans recalcul.
        """

        recalculator = OdsFormulaRecalculator(mode="disabled", binary_path="/bin/false")

        self.assertFalse(recalculator.recalculate("/tmp/missing.ods"))


if __name__ == "__main__":
    unittest.main()
