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
# Description : ajustement du score de matching selon les dates de sortie.

from __future__ import annotations

from datetime import date, datetime


class GameReleaseDateScoreAdjuster:
    """Ajuste un score de matching incertain selon les dates de sortie.

    Returns:
        GameReleaseDateScoreAdjuster: Service d'ajustement reutilisable.

    Raises:
        Aucun.
    """

    UNCERTAIN_SCORE_MINIMUM = 85
    UNCERTAIN_SCORE_MAXIMUM = 95
    SIX_MONTHS_IN_DAYS = 183
    EIGHTEEN_MONTHS_IN_DAYS = 548
    THIRTY_SIX_MONTHS_IN_DAYS = 1096

    def adjust_score(
        self,
        score: int,
        imported_release_date: date | datetime | None,
        candidate_release_date: date | datetime | None,
    ) -> int:
        """Applique une penalite de date sur un score de nom incertain.

        Args:
            score (int): Score de matching calcule sur le nom.
            imported_release_date (date | datetime | None): Date de sortie importee.
            candidate_release_date (date | datetime | None): Date de sortie du candidat.

        Returns:
            int: Score ajuste entre `0` et `100`.

        Raises:
            Aucun.
        """

        if not self._is_uncertain_score(score):
            return score
        imported_date = self._date_value(imported_release_date)
        candidate_date = self._date_value(candidate_release_date)
        if imported_date is None or candidate_date is None:
            return score
        day_difference = abs((imported_date - candidate_date).days)
        return max(0, score - self._penalty(day_difference))

    def _is_uncertain_score(self, score: int) -> bool:
        return self.UNCERTAIN_SCORE_MINIMUM <= score < self.UNCERTAIN_SCORE_MAXIMUM

    def _date_value(self, value: date | datetime | None) -> date | None:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return None

    def _penalty(self, day_difference: int) -> int:
        if day_difference > self.THIRTY_SIX_MONTHS_IN_DAYS:
            return 35
        if day_difference > self.EIGHTEEN_MONTHS_IN_DAYS:
            return 20
        if day_difference > self.SIX_MONTHS_IN_DAYS:
            return 10
        return 0
