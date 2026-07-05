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
# Description : tests de l'ajustement de score par date de sortie.

import unittest
from datetime import date, datetime

from services.database import GameReleaseDateScoreAdjuster


class GameReleaseDateScoreAdjusterTest(unittest.TestCase):
    """Valide les penalites de score liees aux dates de sortie."""

    def setUp(self):
        """Prepare l'ajusteur teste.

        Args:
            Aucun.

        Returns:
            None: La methode initialise le test.
        """

        self.adjuster = GameReleaseDateScoreAdjuster()

    def test_adjust_score_keeps_scores_outside_uncertain_range(self):
        """Verifie que les scores hors zone grise ne sont pas ajustes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les bornes de score.
        """

        imported_date = date(2000, 1, 1)
        candidate_date = date(2004, 1, 2)

        self.assertEqual(84, self.adjuster.adjust_score(84, imported_date, candidate_date))
        self.assertEqual(50, self.adjuster.adjust_score(85, imported_date, candidate_date))
        self.assertEqual(95, self.adjuster.adjust_score(95, imported_date, candidate_date))
        self.assertEqual(100, self.adjuster.adjust_score(100, imported_date, candidate_date))
        self.assertEqual(40, self.adjuster.adjust_score(40, imported_date, candidate_date))

    def test_adjust_score_keeps_uncertain_score_when_date_is_missing(self):
        """Verifie qu'une date absente ne penalise pas le matching.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les cas de dates incompletes.
        """

        known_date = date(2000, 1, 1)

        self.assertEqual(88, self.adjuster.adjust_score(88, None, known_date))
        self.assertEqual(88, self.adjuster.adjust_score(88, known_date, None))
        self.assertEqual(88, self.adjuster.adjust_score(88, None, None))

    def test_adjust_score_keeps_uncertain_score_with_six_month_gap_or_less(self):
        """Verifie qu'un ecart de six mois ou moins reste accepte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence de penalite.
        """

        self.assertEqual(
            88,
            self.adjuster.adjust_score(88, date(2000, 1, 1), date(2000, 7, 2)),
        )

    def test_adjust_score_applies_penalty_above_six_months(self):
        """Verifie la penalite de dix points apres six mois d'ecart.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score ajuste.
        """

        self.assertEqual(
            78,
            self.adjuster.adjust_score(88, date(2000, 1, 1), date(2000, 7, 3)),
        )

    def test_adjust_score_applies_penalty_above_eighteen_months(self):
        """Verifie la penalite de vingt points apres dix-huit mois d'ecart.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score ajuste.
        """

        self.assertEqual(
            68,
            self.adjuster.adjust_score(88, date(2000, 1, 1), date(2001, 7, 3)),
        )

    def test_adjust_score_applies_penalty_above_thirty_six_months(self):
        """Verifie la forte penalite apres trente-six mois d'ecart.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score ajuste.
        """

        self.assertEqual(
            53,
            self.adjuster.adjust_score(88, date(2000, 1, 1), date(2003, 1, 2)),
        )

    def test_adjust_score_supports_datetime_values(self):
        """Verifie l'acceptation des valeurs `datetime`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la conversion en date.
        """

        self.assertEqual(
            78,
            self.adjuster.adjust_score(
                88,
                datetime(2000, 1, 1, 12, 0, 0),
                datetime(2000, 7, 3, 0, 0, 0),
            ),
        )


if __name__ == "__main__":
    unittest.main()
