#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires de normalisation des noms de collection utilisateur.

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.users import UserCollectionNameNormalizer


class UserCollectionNameNormalizerTest(unittest.TestCase):
    """Valide la normalisation metier des noms de collection utilisateur."""

    def setUp(self):
        """Prepare le normaliseur teste.

        Args:
            Aucun.

        Returns:
            None: L'instance de test est initialisee.
        """

        self.normalizer = UserCollectionNameNormalizer()

    def test_stored_value_keeps_case_and_accents(self):
        """Verifie la valeur stockee avec casse et accents conserves.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la normalisation de stockage.
        """

        self.assertEqual("École du Jeu", self.normalizer.stored_value("  École du Jeu  "))

    def test_comparison_key_removes_accents(self):
        """Verifie la cle de comparaison sans accents.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la suppression des accents.
        """

        self.assertEqual("ecole du jeu", self.normalizer.comparison_key("  École du Jeu  "))

    def test_accent_case_and_outer_space_differences_are_equivalent(self):
        """Verifie l'equivalence metier malgre accents, casse et espaces.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'equivalence.
        """

        self.assertTrue(self.normalizer.are_equivalent(" École ", "ecole"))

    def test_empty_values_return_none(self):
        """Verifie la normalisation des valeurs vides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence de valeur normalisee.
        """

        self.assertIsNone(self.normalizer.stored_value("  "))
        self.assertIsNone(self.normalizer.stored_value(pd.NaT))
        self.assertIsNone(self.normalizer.stored_value("NaT"))
        self.assertIsNone(self.normalizer.stored_value(float("nan")))
        self.assertIsNone(self.normalizer.comparison_key(None))

    def test_stored_game_name_standardizes_title_case(self):
        """Verifie la standardisation des noms de jeux crees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la casse titre attendue.
        """

        cases = {
            "le roi lion": "Le Roi Lion",
            "Elden ring night reign": "Elden Ring Night Reign",
            "Dirge of cerberus : Final fantasy 7": "Dirge of Cerberus : Final Fantasy 7",
            "Dirge of cerberus : Final fantasy vii": "Dirge of Cerberus : Final Fantasy VII",
            "Final Fantasy Xiii-3 Lightning Returns": "Final Fantasy XIII-3 Lightning Returns",
            "xiom chronicles": "Xiom Chronicles",
            "GoldenEye: au service du mal": "GoldenEye : Au Service du Mal",
            "oddworld:L'odyssée d'abe": "Oddworld : L'Odyssée d'Abe",
            "assassin's creed": "Assassin's Creed",
            "Like a dragon gaiden : The man Who Erased his name": (
                "Like a Dragon Gaiden : The Man Who Erased His Name"
            ),
            "Paper mario et la porte millénaire": "Paper Mario et la Porte Millénaire",
        }

        for raw_name, expected_name in cases.items():
            with self.subTest(raw_name=raw_name):
                self.assertEqual(expected_name, self.normalizer.stored_game_name(raw_name))


if __name__ == "__main__":
    unittest.main()
