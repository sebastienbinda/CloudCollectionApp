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
# Description : moteur explicable de matching des titres de jeux.

from __future__ import annotations

try:
    from .different_final_word_matching_rule import DifferentFinalWordMatchingRule
    from .fuzzy_title_matching_rule import FuzzyTitleMatchingRule
    from .game_title_matching_result import GameTitleMatchingResult
    from .game_title_matching_rule import GameTitleMatchingRule
    from .numeric_suffix_matching_rule import NumericSuffixMatchingRule
except ImportError:
    from different_final_word_matching_rule import DifferentFinalWordMatchingRule
    from fuzzy_title_matching_rule import FuzzyTitleMatchingRule
    from game_title_matching_result import GameTitleMatchingResult
    from game_title_matching_rule import GameTitleMatchingRule
    from numeric_suffix_matching_rule import NumericSuffixMatchingRule


class GameTitleMatchingEngine:
    """Applique les regles de matching metier des titres de jeux.

    Returns:
        GameTitleMatchingEngine: Moteur reutilisable de matching.

    Raises:
        Aucun.
    """

    def __init__(
        self,
        rules: list[GameTitleMatchingRule] | None = None,
        fallback_rule: FuzzyTitleMatchingRule | None = None,
    ):
        """Initialise le moteur avec ses regles ordonnees.

        Args:
            rules (list[GameTitleMatchingRule] | None): Regles metier prioritaires.
            fallback_rule (FuzzyTitleMatchingRule | None): Regle fuzzy de secours.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            Aucun.
        """

        self.rules = rules or [
            NumericSuffixMatchingRule(),
            DifferentFinalWordMatchingRule(),
        ]
        self.fallback_rule = fallback_rule or FuzzyTitleMatchingRule()

    def evaluate(self, imported_key: str, candidate_key: str) -> GameTitleMatchingResult:
        """Evalue deux titres normalises et retourne un resultat explicable.

        Args:
            imported_key (str): Cle normalisee du titre importe.
            candidate_key (str): Cle normalisee du titre candidat.

        Returns:
            GameTitleMatchingResult: Resultat explicable du matching.

        Raises:
            Aucun.
        """

        for rule in self.rules:
            result = rule.evaluate(imported_key, candidate_key)
            if result is not None:
                return result
        return self.fallback_rule.evaluate(imported_key, candidate_key)
