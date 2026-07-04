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
# Description : regle de fallback fuzzy des titres de jeux.

from __future__ import annotations

from difflib import SequenceMatcher

try:
    from .game_title_matching_decision import GameTitleMatchingDecision
    from .game_title_matching_result import GameTitleMatchingResult
except ImportError:
    from game_title_matching_decision import GameTitleMatchingDecision
    from game_title_matching_result import GameTitleMatchingResult


class FuzzyTitleMatchingRule:
    """Calcule le score fuzzy generique en dernier recours.

    Returns:
        FuzzyTitleMatchingRule: Regle de scoring fuzzy.

    Raises:
        Aucun.
    """

    def evaluate(
        self,
        imported_key: str,
        candidate_key: str,
    ) -> GameTitleMatchingResult:
        """Calcule le score fuzzy entre deux titres normalises.

        Args:
            imported_key (str): Cle normalisee du titre importe.
            candidate_key (str): Cle normalisee du titre candidat.

        Returns:
            GameTitleMatchingResult: Score fuzzy generique.

        Raises:
            Aucun.
        """

        if imported_key == candidate_key:
            score = 100
        elif not imported_key or not candidate_key:
            score = 0
        else:
            score = int(round(SequenceMatcher(None, imported_key, candidate_key).ratio() * 100))
        return GameTitleMatchingResult(
            score,
            GameTitleMatchingDecision.SCORED,
            "fuzzy_similarity",
            "Score de similarite textuelle generique.",
        )
