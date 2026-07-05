#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-07-04
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du matching de jeux ajuste par date de sortie.

import unittest
from datetime import date

from services.collection.imports import CollectionImportGame
from services.database import GameMatchingConfiguration, GameMatchingService
from services.users import UserCollectionNameNormalizer


class GameMatchingReleaseDateServiceTest(unittest.TestCase):
    """Valide l'ajustement du matching de jeux par date de sortie."""

    def setUp(self):
        """Prepare un service avec seuils de matching controles.

        Args:
            Aucun.

        Returns:
            None: La methode initialise le test.
        """

        self.service = GameMatchingService(
            GameMatchingConfiguration(low_level_rating=25, high_level_rating=75),
            UserCollectionNameNormalizer(),
        )

    def test_release_date_penalty_rejects_grand_theft_auto_false_positive(self):
        """Verifie qu'un faux positif GTA proche est rejete par l'ecart de date.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score final `52`.
        """

        result = self._evaluate(
            CollectionImportGame(
                "Grand Theft Auto Vice City",
                "PS2",
                "",
                date(2002, 10, 29),
            ),
            {
                ("ps2", "grand theft auto vice city stories"): (
                    17,
                    "Grand Theft Auto Vice City Stories",
                    date(2006, 10, 31),
                )
            },
        )

        self.assertIsNone(result.existing_game_id)
        self.assertEqual("Grand Theft Auto Vice City Stories", result.best_candidate.game_name)
        self.assertEqual(52, result.best_candidate.score)

    def test_release_date_penalty_keeps_medium_grand_theft_auto_candidate_above_threshold(self):
        """Verifie une penalite moderee sur deux Grand Theft Auto proches.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score final `78`.
        """

        result = self._evaluate(
            CollectionImportGame(
                "Grand Theft Auto Liberty City Stories",
                "PSP",
                "",
                date(2005, 10, 24),
            ),
            {
                ("psp", "grand theft auto vice city stories"): (
                    19,
                    "Grand Theft Auto Vice City Stories",
                    date(2006, 10, 31),
                )
            },
        )

        self.assertEqual(19, result.existing_game_id)
        self.assertEqual("Grand Theft Auto Vice City Stories", result.best_candidate.game_name)
        self.assertEqual(80, result.best_candidate.score)

    def test_release_date_penalty_does_not_adjust_score_without_imported_date(self):
        """Verifie qu'une date importee absente conserve le score de nom.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score final `87`.
        """

        result = self._evaluate(
            CollectionImportGame("Grand Theft Auto Vice City", "PS2", "", None),
            {
                ("ps2", "grand theft auto vice city stories"): (
                    17,
                    "Grand Theft Auto Vice City Stories",
                    date(2006, 10, 31),
                )
            },
        )

        self.assertEqual(17, result.existing_game_id)
        self.assertEqual(87, result.best_candidate.score)

    def test_release_date_penalty_does_not_adjust_low_final_fantasy_tactics_score(self):
        """Verifie qu'un score inferieur a la zone grise n'est pas remonte ni penalise.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score final `84`.
        """

        result = self._evaluate(
            CollectionImportGame(
                "Final Fantasy Tactics",
                "GBA",
                "",
                date(1997, 6, 20),
            ),
            {
                ("gba", "final fantasy tactics advance"): (
                    23,
                    "Final Fantasy Tactics Advance",
                    date(2003, 2, 14),
                )
            },
        )

        self.assertEqual(23, result.existing_game_id)
        self.assertEqual(84, result.best_candidate.score)

    def test_release_date_penalty_does_not_adjust_high_zelda_hd_score(self):
        """Verifie qu'un score de nom tres eleve n'est pas penalise par la date.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score final `96`.
        """

        result = self._evaluate(
            CollectionImportGame(
                "The Legend of Zelda Twilight Princess",
                "Wii U",
                "",
                date(2006, 11, 19),
            ),
            {
                ("wii u", "the legend of zelda twilight princess hd"): (
                    29,
                    "The Legend of Zelda Twilight Princess HD",
                    date(2016, 3, 4),
                )
            },
        )

        self.assertEqual(29, result.existing_game_id)
        self.assertEqual(96, result.best_candidate.score)

    def test_release_date_penalty_can_change_best_candidate_after_adjustment(self):
        """Verifie que la date peut faire passer un meilleur nom derriere un autre candidat.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le meilleur score final `67`.
        """

        result = self._evaluate(
            CollectionImportGame(
                "Grand Theft Auto Vice City",
                "PS2",
                "",
                date(2002, 10, 29),
            ),
            {
                ("ps2", "grand theft auto vice city stories"): (
                    17,
                    "Grand Theft Auto Vice City Stories",
                    date(2006, 10, 31),
                ),
                ("ps2", "grand theft auto san andreas"): (
                    31,
                    "Grand Theft Auto San Andreas",
                    date(2004, 10, 26),
                ),
            },
        )

        self.assertIsNone(result.existing_game_id)
        self.assertEqual("Grand Theft Auto San Andreas", result.best_candidate.game_name)
        self.assertEqual(67, result.best_candidate.score)

    def test_release_date_penalty_rejects_persona_5_royal_when_dates_diverge(self):
        """Verifie qu'une edition Persona proche peut etre rejetee par la date.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score final `50`.
        """

        result = self._evaluate(
            CollectionImportGame(
                "Persona 5",
                "PS4",
                "",
                date(2016, 9, 15),
            ),
            {
                ("ps4", "persona 5 royal"): (
                    37,
                    "Persona 5 Royal",
                    date(2019, 10, 31),
                )
            },
        )

        self.assertIsNone(result.existing_game_id)
        self.assertEqual("Persona 5 Royal", result.best_candidate.game_name)
        self.assertEqual(50, result.best_candidate.score)

    def test_release_date_penalty_keeps_persona_5_royal_uncertain_without_dates(self):
        """Verifie que Persona 5 Royal reste en zone grise sans date d'entree.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score final `85`.
        """

        result = self._evaluate(
            CollectionImportGame("Persona 5", "PS4", "", None),
            {
                ("ps4", "persona 5 royal"): (
                    37,
                    "Persona 5 Royal",
                    date(2019, 10, 31),
                )
            },
        )

        self.assertEqual(37, result.existing_game_id)
        self.assertEqual("Persona 5 Royal", result.best_candidate.game_name)
        self.assertEqual(85, result.best_candidate.score)

    def _evaluate(
        self,
        game: CollectionImportGame,
        existing_game_references: dict[tuple[str, str], tuple[int, str, date]],
    ):
        existing_game_ids = {
            game_key: game_reference[0]
            for game_key, game_reference in existing_game_references.items()
        }
        return self.service.evaluate_existing_game(
            game,
            existing_game_ids,
            self.service.build_platform_index(existing_game_references),
        )


if __name__ == "__main__":
    unittest.main()
