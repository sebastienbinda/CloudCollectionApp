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
# Description : regle de matching des suffixes numeriques de titres de jeux.

from __future__ import annotations

import re
from difflib import SequenceMatcher

try:
    from .game_title_matching_decision import GameTitleMatchingDecision
    from .game_title_matching_result import GameTitleMatchingResult
except ImportError:
    from game_title_matching_decision import GameTitleMatchingDecision
    from game_title_matching_result import GameTitleMatchingResult


class NumericSuffixMatchingRule:
    """Force ou accepte le matching selon les suffixes numeriques de titre.

    Returns:
        NumericSuffixMatchingRule: Regle applicable aux suites numerotees.

    Raises:
        Aucun.
    """

    _SEQUEL_SUFFIX_PATTERN = re.compile(
        r"^(?P<base>.+?) (?P<suffix>(?:\d+|[ivxlcdm]+)(?:-(?:\d+|[ivxlcdm]+))*)$"
    )
    _SEQUEL_PREFIX_PATTERN = re.compile(
        r"^(?P<base>.+?) (?P<suffix>(?:\d+|[ivxlcdm]+)(?:-(?:\d+|[ivxlcdm]+))*)(?P<extra>\s+.+)?$"
    )
    _EQUIVALENT_SUFFIX_WITH_EXTRA_TEXT_SCORE = 85
    _SERIES_BASE_MINIMUM_SCORE = 90
    _ROMAN_VALUES = {
        "i": 1,
        "v": 5,
        "x": 10,
        "l": 50,
        "c": 100,
        "d": 500,
        "m": 1000,
    }

    def evaluate(
        self,
        imported_key: str,
        candidate_key: str,
    ) -> GameTitleMatchingResult | None:
        """Evalue les suffixes numeriques de deux titres normalises.

        Args:
            imported_key (str): Cle normalisee du titre importe.
            candidate_key (str): Cle normalisee du titre candidat.

        Returns:
            GameTitleMatchingResult | None: Resultat si un suffixe numerique decide.

        Raises:
            Aucun.
        """

        if self._has_numeric_suffix_extension(imported_key, candidate_key):
            return self._rejected("numeric_suffix_extension")
        series_number_result = self._series_number_result(imported_key, candidate_key)
        if series_number_result is not None:
            return series_number_result
        imported_base, imported_suffix = self._split_sequel_suffix(imported_key)
        candidate_base, candidate_suffix = self._split_sequel_suffix(candidate_key)
        if imported_base != candidate_base:
            return None
        if imported_suffix is None and candidate_suffix is None:
            return None
        if imported_suffix is None or candidate_suffix is None:
            return self._rejected("missing_numeric_suffix")
        if imported_suffix == candidate_suffix:
            return self._accepted_equivalent_suffix()
        return self._rejected("different_numeric_suffix")

    def _rejected(self, rule: str) -> GameTitleMatchingResult:
        return GameTitleMatchingResult(
            0,
            GameTitleMatchingDecision.REJECTED,
            rule,
            "Les suffixes numeriques indiquent des jeux differents.",
        )

    def _has_numeric_suffix_extension(self, first_key: str, second_key: str) -> bool:
        return self._is_numeric_suffix_extension(
            first_key,
            second_key,
        ) or self._is_numeric_suffix_extension(
            second_key,
            first_key,
        )

    def _is_numeric_suffix_extension(self, base_key: str, extended_key: str) -> bool:
        if not base_key or len(extended_key) <= len(base_key):
            return False
        if not extended_key.startswith(base_key):
            return False
        remaining_suffix = extended_key[len(base_key):]
        return bool(re.match(r"^[ -]\d", remaining_suffix))

    def _split_sequel_suffix(self, game_name_key: str) -> tuple[str, tuple[int, ...] | None]:
        suffix_match = self._SEQUEL_SUFFIX_PATTERN.match(game_name_key)
        if suffix_match is None:
            return game_name_key, None
        suffix = self._numeric_suffix(suffix_match.group("suffix"))
        if suffix is None:
            return game_name_key, None
        return suffix_match.group("base"), suffix

    def _series_number_result(
        self,
        first_key: str,
        second_key: str,
    ) -> GameTitleMatchingResult | None:
        (
            first_base,
            first_suffix,
            first_has_extra_text,
        ) = self._split_leading_sequel_number(first_key)
        (
            second_base,
            second_suffix,
            second_has_extra_text,
        ) = self._split_leading_sequel_number(second_key)
        if not self._has_same_series_base(first_base, second_base):
            return None
        if first_suffix is None or second_suffix is None:
            return None
        if first_suffix == second_suffix:
            if first_has_extra_text or second_has_extra_text:
                return self._scored_equivalent_suffix_with_extra_text()
            return self._accepted_equivalent_suffix()
        return self._rejected("different_numeric_suffix")

    def _accepted_equivalent_suffix(self) -> GameTitleMatchingResult:
        return GameTitleMatchingResult(
            100,
            GameTitleMatchingDecision.ACCEPTED,
            "equivalent_numeric_suffix",
            "Les suffixes numeriques des titres sont equivalents.",
        )

    def _scored_equivalent_suffix_with_extra_text(self) -> GameTitleMatchingResult:
        return GameTitleMatchingResult(
            self._EQUIVALENT_SUFFIX_WITH_EXTRA_TEXT_SCORE,
            GameTitleMatchingDecision.SCORED,
            "equivalent_numeric_suffix_with_extra_text",
            "Les suffixes numeriques sont equivalents mais un titre contient un complement.",
        )

    def _has_same_series_base(self, first_base: str, second_base: str) -> bool:
        if first_base == second_base:
            return True
        if not first_base or not second_base:
            return False
        score = int(round(SequenceMatcher(None, first_base, second_base).ratio() * 100))
        return score >= self._SERIES_BASE_MINIMUM_SCORE

    def _split_leading_sequel_number(
        self,
        game_name_key: str,
    ) -> tuple[str, tuple[int, ...] | None, bool]:
        suffix_match = self._SEQUEL_PREFIX_PATTERN.match(game_name_key)
        if suffix_match is None:
            return game_name_key, None, False
        suffix = self._numeric_suffix(suffix_match.group("suffix"))
        if suffix is None:
            return game_name_key, None, False
        return suffix_match.group("base"), suffix, bool(suffix_match.group("extra"))

    def _numeric_suffix(self, suffix: str) -> tuple[int, ...] | None:
        values = []
        for suffix_part in suffix.split("-"):
            if suffix_part.isdigit():
                values.append(int(suffix_part))
                continue
            roman_value = self._roman_to_integer(suffix_part)
            if roman_value is None:
                return None
            values.append(roman_value)
        return tuple(values)

    def _roman_to_integer(self, value: str) -> int | None:
        total = 0
        previous_value = 0
        for character in reversed(value):
            current_value = self._ROMAN_VALUES.get(character)
            if current_value is None:
                return None
            if current_value < previous_value:
                total -= current_value
            else:
                total += current_value
                previous_value = current_value
        return total if self._integer_to_roman(total) == value else None

    def _integer_to_roman(self, value: int) -> str:
        parts = []
        for roman_value, roman_label in (
            (1000, "m"),
            (900, "cm"),
            (500, "d"),
            (400, "cd"),
            (100, "c"),
            (90, "xc"),
            (50, "l"),
            (40, "xl"),
            (10, "x"),
            (9, "ix"),
            (5, "v"),
            (4, "iv"),
            (1, "i"),
        ):
            while value >= roman_value:
                parts.append(roman_label)
                value -= roman_value
        return "".join(parts)
