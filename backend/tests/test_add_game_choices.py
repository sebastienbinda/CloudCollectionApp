#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-08
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# License : Apache 2.0
#
"""Tests des choix fusionnes du formulaire d'ajout.

Description:
    Ce module valide la fusion backend des plateformes et suggestions issues
    de la collection.
"""

import unittest

from services.games.add_game_choice_service import AddGameChoiceService


class FakeChoiceReader:
    """Lecteur factice exposant les valeurs distinctes utiles aux choix."""

    def list_platforms(self):
        """Retourne les plateformes collection.

        Args:
            Aucun.

        Returns:
            list[str]: Plateformes de collection.
        """

        return ["Switch", "Playstation 5"]

    def list_column_values(self, platform):
        """Retourne les valeurs distinctes d'une feuille.

        Args:
            platform (str): Feuille demandee.

        Returns:
            dict[str, list[str]]: Valeurs par colonne.
        """

        if platform == "Playstation 5":
            return {"Studio": ["Sucker Punch", "nintendo", None], "Version": ["PS5", "nan"]}
        return {"Studio": ["nintendo", "Retro", ""], "Version": ["PAL"]}


class AddGameChoiceServiceTest(unittest.TestCase):
    """Tests unitaires du service de choix d'ajout."""

    def setUp(self):
        """Prepare un service sans acces ODS reel.

        Args:
            Aucun.

        Returns:
            None: Le lecteur ODS est remplace par un fake.
        """

        self.reader = FakeChoiceReader()
        self.service = AddGameChoiceService(
            self.reader.list_platforms,
            self.reader.list_column_values,
        )

    def test_list_add_game_choices_merges_platforms_case_and_spaces(self):
        """Verifie le dedoublonnage des plateformes fusionnees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les choix retournes.
        """

        choices = self.service.list_choices()

        self.assertEqual(["Playstation 5", "Switch"], choices["platforms"])
        self.assertEqual(["Playstation 5", "Switch"], choices["values_by_column"]["Plateforme"])
        self.assertEqual(
            ["nintendo", "Retro", "Sucker Punch"],
            choices["values_by_column"]["Studio"],
        )
        self.assertEqual(["PAL", "PS5"], choices["values_by_column"]["Version"])
        self.assertNotIn("nan", choices["values_by_column"]["Plateforme"])


if __name__ == "__main__":
    unittest.main()
