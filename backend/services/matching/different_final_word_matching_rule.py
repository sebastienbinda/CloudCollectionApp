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
# Description : regle de rejet des titres de meme serie au suffixe final different.

from __future__ import annotations

try:
    from .game_title_matching_decision import GameTitleMatchingDecision
    from .game_title_matching_result import GameTitleMatchingResult
except ImportError:
    from game_title_matching_decision import GameTitleMatchingDecision
    from game_title_matching_result import GameTitleMatchingResult


class DifferentFinalWordMatchingRule:
    """Rejette deux titres de meme prefixe avec un dernier mot different.

    Returns:
        DifferentFinalWordMatchingRule: Regle des suffixes textuels divergents.

    Raises:
        Aucun.
    """

    def evaluate(
        self,
        imported_key: str,
        candidate_key: str,
    ) -> GameTitleMatchingResult | None:
        """Evalue le dernier mot significatif de deux titres normalises.

        Args:
            imported_key (str): Cle normalisee du titre importe.
            candidate_key (str): Cle normalisee du titre candidat.

        Returns:
            GameTitleMatchingResult | None: Rejet si les suffixes textuels divergent.

        Raises:
            Aucun.
        """

        imported_words = imported_key.split()
        candidate_words = candidate_key.split()
        if len(imported_words) < 3 or len(imported_words) != len(candidate_words):
            return None
        if imported_words[:-1] != candidate_words[:-1]:
            return None
        if imported_words[-1] == candidate_words[-1]:
            return None
        return GameTitleMatchingResult(
            0,
            GameTitleMatchingDecision.REJECTED,
            "different_final_word",
            "Les titres ont le meme prefixe mais un suffixe final different.",
        )
