#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de configuration du matching des regions.

import os
import unittest
from unittest.mock import patch

from services.collection.imports import RegionMatchingConfiguration


class RegionMatchingConfigurationTest(unittest.TestCase):
    """Valide le seuil configurable de matching des regions."""

    def test_environment_supports_default_and_custom_limit(self):
        """Verifie la valeur par defaut et une valeur personnalisee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les seuils.
        """

        with patch.dict(os.environ, {}, clear=True):
            default_configuration = RegionMatchingConfiguration.from_environment()
        with patch.dict(os.environ, {"REGION_MATCH_LIMIT": "75"}, clear=True):
            custom_configuration = RegionMatchingConfiguration.from_environment()

        self.assertEqual(60, default_configuration.match_limit)
        self.assertEqual(75, custom_configuration.match_limit)

    def test_environment_rejects_non_numeric_and_out_of_range_limits(self):
        """Verifie le refus des seuils invalides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les erreurs.
        """

        for raw_value in ("bad", "-1", "101"):
            with self.subTest(raw_value=raw_value):
                with patch.dict(os.environ, {"REGION_MATCH_LIMIT": raw_value}, clear=True):
                    with self.assertRaises(ValueError):
                        RegionMatchingConfiguration.from_environment()


if __name__ == "__main__":
    unittest.main()
