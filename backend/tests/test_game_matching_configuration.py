#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de configuration du matching des jeux.

import os
import unittest
from unittest.mock import patch

from services.database import GameMatchingConfiguration


class GameMatchingConfigurationTest(unittest.TestCase):
    """Valide les seuils configurables du matching des jeux."""

    def test_from_environment_uses_defaults_and_custom_values(self):
        """Verifie les valeurs par defaut et personnalisees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la configuration.
        """

        with patch.dict(os.environ, {}, clear=True):
            default_configuration = GameMatchingConfiguration.from_environment()
        with patch.dict(
            os.environ,
            {
                "GAME_MATCHING_LOW_LVL_RATING": "30",
                "GAME_MATCHING_HIGH_LEVEL_RATING": "80",
            },
            clear=True,
        ):
            custom_configuration = GameMatchingConfiguration.from_environment()

        self.assertEqual(25, default_configuration.low_level_rating)
        self.assertEqual(75, default_configuration.high_level_rating)
        self.assertEqual(30, custom_configuration.low_level_rating)
        self.assertEqual(80, custom_configuration.high_level_rating)

    def test_from_environment_rejects_invalid_values(self):
        """Verifie le refus des seuils invalides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les erreurs.
        """

        invalid_environments = [
            {"GAME_MATCHING_LOW_LVL_RATING": "bad"},
            {
                "GAME_MATCHING_LOW_LVL_RATING": "75",
                "GAME_MATCHING_HIGH_LEVEL_RATING": "75",
            },
            {"GAME_MATCHING_LOW_LVL_RATING": "-1"},
            {"GAME_MATCHING_HIGH_LEVEL_RATING": "101"},
        ]

        for environment in invalid_environments:
            with self.subTest(environment=environment):
                with patch.dict(os.environ, environment, clear=True):
                    with self.assertRaises(ValueError):
                        GameMatchingConfiguration.from_environment()


if __name__ == "__main__":
    unittest.main()
