#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de configuration du matching des etats.

import os
import unittest
from unittest.mock import patch

from services.collection.imports import ConditionMatchingConfiguration


class ConditionMatchingConfigurationTest(unittest.TestCase):
    """Valide le seuil configurable de matching des etats."""

    def test_environment_supports_default_and_custom_limit(self):
        """Verifie les valeurs par defaut et personnalisee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les seuils.
        """

        with patch.dict(os.environ, {}, clear=True):
            default_configuration = ConditionMatchingConfiguration.from_environment()
        with patch.dict(os.environ, {"ETAT_MATCH_LIMIT": "72"}, clear=True):
            custom_configuration = ConditionMatchingConfiguration.from_environment()

        self.assertEqual(60, default_configuration.match_limit)
        self.assertEqual(72, custom_configuration.match_limit)

    def test_environment_rejects_invalid_limits(self):
        """Verifie le refus des valeurs invalides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les erreurs.
        """

        for raw_value in ("bad", "-1", "101"):
            with self.subTest(raw_value=raw_value):
                with patch.dict(os.environ, {"ETAT_MATCH_LIMIT": raw_value}, clear=True):
                    with self.assertRaises(ValueError):
                        ConditionMatchingConfiguration.from_environment()


if __name__ == "__main__":
    unittest.main()
