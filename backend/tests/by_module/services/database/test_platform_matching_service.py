#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du matching des plateformes importees.

import unittest

from services.collection.imports import (
    CollectionImportData,
    CollectionImportGame,
    CollectionImportPlatform,
)
from services.database import PlatformMatchingConfiguration, PlatformMatchingService


class PlatformMatchingServiceTest(unittest.TestCase):
    """Valide le rattachement des plateformes au referentiel."""

    def test_match_import_data_accepts_exact_case_accent_space_and_minor_typo(self):
        """Verifie les correspondances fiables.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les rattachements.
        """

        import_data = CollectionImportData(
            platforms=[
                CollectionImportPlatform("switch"),
                CollectionImportPlatform("Mega  Drive"),
                CollectionImportPlatform("Playstation"),
            ],
            studios=[],
            games=[
                CollectionImportGame(
                    "Zelda", "switch", "", None,
                    purchase_price=59, price_unit="EUR", region="EU-FR",
                ),
                CollectionImportGame("Sonic", "Mega  Drive", "", None),
                CollectionImportGame("Ridge Racer", "Playstation", "", None),
            ],
        )
        rows = [{"name": "Switch"}, {"name": "Méga Drive"}, {"name": "PlayStation"}]

        matched_data = self._service().match_import_data(import_data, rows)

        self.assertEqual(["Switch", "Méga Drive", "PlayStation"], [
            game.platform_name for game in matched_data.games
        ])
        self.assertEqual([], matched_data.warnings.platform_matches)
        self.assertEqual([], matched_data.warnings.skipped_games)
        self.assertEqual(59, matched_data.games[0].purchase_price)
        self.assertEqual("EUR", matched_data.games[0].price_unit)
        self.assertEqual("EU-FR", matched_data.games[0].region)

    def test_match_import_data_accepts_low_score_with_warning(self):
        """Verifie un score faible importe avec warning.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le warning.
        """

        import_data = CollectionImportData(
            platforms=[CollectionImportPlatform("Wii")],
            studios=[],
            games=[CollectionImportGame("Sports", "Wii", "", None)],
        )
        rows = [{"name": "Switch"}]

        matched_data = self._service().match_import_data(import_data, rows)

        self.assertEqual(["Switch"], [game.platform_name for game in matched_data.games])
        self.assertEqual("Sports", matched_data.warnings.platform_matches[0]["game_name"])
        self.assertEqual(
            [
                {
                    "imported_platform": "Wii",
                    "matched_platform": "Switch",
                    "score": 44,
                    "games_count": 1,
                    "matched_by_alias": False,
                    "matched_alias": "",
                    "accepted": True,
                    "manual_check": True,
                    "reason": "",
                }
            ],
            matched_data.warnings.platform_mappings,
        )
        self.assertEqual([], matched_data.warnings.skipped_games)

    def test_match_import_data_uses_alias_when_direct_score_is_not_high(self):
        """Verifie le recours aux alias quand le score direct est sous le seuil haut.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le matching par alias.
        """

        import_data = CollectionImportData(
            platforms=[CollectionImportPlatform("Super Nintendo")],
            studios=[],
            games=[CollectionImportGame("Mario", "Super Nintendo", "", None)],
        )
        rows = [
            {
                "name": "Super Nintendo Entertainment System / Super Famicom",
                "aliases": [{"name": "Super Nintendo"}, {"name": "Super Famicom"}],
            },
            {"name": "Nintendo Switch", "aliases": [{"name": "Switch"}]},
        ]

        matched_data = self._service().match_import_data(import_data, rows)

        self.assertEqual(
            ["Super Nintendo Entertainment System / Super Famicom"],
            [game.platform_name for game in matched_data.games],
        )
        self.assertTrue(matched_data.warnings.platform_mappings[0]["matched_by_alias"])
        self.assertEqual(
            "Super Nintendo",
            matched_data.warnings.platform_mappings[0]["matched_alias"],
        )
        self.assertEqual(1, matched_data.warnings.platform_mappings[0]["games_count"])
        self.assertEqual([], matched_data.warnings.platform_matches)
        self.assertEqual([], matched_data.warnings.skipped_games)

    def test_match_import_data_maps_pc_store_aliases_to_pc_platform(self):
        """Verifie que les boutiques PC importees sont rattachees a PC.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le matching par alias PC.
        """

        import_data = CollectionImportData(
            platforms=[
                CollectionImportPlatform("Steam"),
                CollectionImportPlatform("Steam machine"),
                CollectionImportPlatform("Epic Game Store"),
                CollectionImportPlatform("Good Old Games"),
                CollectionImportPlatform("Ordinateur"),
            ],
            studios=[],
            games=[
                CollectionImportGame("Half-Life Alyx", "Steam", "", None),
                CollectionImportGame("Portal 2", "Steam machine", "", None),
                CollectionImportGame("Fortnite", "Epic Game Store", "", None),
                CollectionImportGame("The Witcher 3", "Good Old Games", "", None),
                CollectionImportGame("Civilization VI", "Ordinateur", "", None),
            ],
        )
        rows = [
            {
                "name": "PC",
                "aliases": [
                    {"name": "Steam"},
                    {"name": "Steam machine"},
                    {"name": "Epic Game Store"},
                    {"name": "Good Old Games"},
                    {"name": "Ordinateur"},
                ],
            },
            {"name": "Steam Deck", "aliases": [{"name": "Valve Steam Deck"}]},
        ]

        matched_data = self._service().match_import_data(import_data, rows)

        self.assertEqual(["PC", "PC", "PC", "PC", "PC"], [
            game.platform_name for game in matched_data.games
        ])
        self.assertEqual([], matched_data.warnings.platform_matches)
        self.assertEqual([], matched_data.warnings.skipped_games)
        self.assertTrue(
            all(mapping["matched_by_alias"] for mapping in matched_data.warnings.platform_mappings)
        )

    def test_match_import_data_rejects_too_low_score_zero_and_ambiguity(self):
        """Verifie les jeux ignores faute de plateforme fiable.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les refus.
        """

        import_data = CollectionImportData(
            platforms=[
                CollectionImportPlatform("Unknown"),
                CollectionImportPlatform("qqq"),
                CollectionImportPlatform("Unknown"),
                CollectionImportPlatform("abc"),
            ],
            studios=[],
            games=[
                CollectionImportGame("Low", "Unknown", "", None),
                CollectionImportGame("Zero", "qqq", "", None),
                CollectionImportGame("Ambiguous", "abc", "", None),
            ],
        )
        rows = [{"name": "Switch"}, {"name": "def"}, {"name": "abx"}, {"name": "aby"}]

        matched_data = self._service().match_import_data(import_data, rows)

        self.assertEqual([], matched_data.games)
        reasons = [warning["reason"] for warning in matched_data.warnings.skipped_games]
        self.assertIn("low_score", reasons)
        self.assertIn("no_match", reasons)
        self.assertIn("ambiguous", reasons)

    def _service(self):
        return PlatformMatchingService(
            PlatformMatchingConfiguration(low_level_rating=25, high_level_rating=75)
        )


if __name__ == "__main__":
    unittest.main()
