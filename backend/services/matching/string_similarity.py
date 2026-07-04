#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : calcul partage des scores de similarite textuelle.

from __future__ import annotations

from difflib import SequenceMatcher
import re


_SEQUEL_SUFFIX_PATTERN = re.compile(
    r"^(?P<base>.+?) (?P<suffix>(?:\d+|[ivxlcdm]+)(?:-(?:\d+|[ivxlcdm]+))*)$"
)
_ROMAN_VALUES = {
    "i": 1,
    "v": 5,
    "x": 10,
    "l": 50,
    "c": 100,
    "d": 500,
    "m": 1000,
}


def matching_score(imported_key: str, candidate_key: str) -> int:
    """Calcule un score entier de similarite entre deux cles normalisees.

    Args:
        imported_key (str): Cle issue de la valeur importee.
        candidate_key (str): Cle du candidat de reference.

    Returns:
        int: Score compris entre 0 et 100.

    Raises:
        Aucun.
    """

    if imported_key == candidate_key:
        return 100
    if not imported_key or not candidate_key:
        return 0
    return int(round(SequenceMatcher(None, imported_key, candidate_key).ratio() * 100))


def game_name_matching_score(imported_key: str, candidate_key: str) -> int:
    """Calcule le score de matching entre deux cles normalisees de jeux.

    Args:
        imported_key (str): Cle normalisee du jeu importe.
        candidate_key (str): Cle normalisee du jeu candidat.

    Returns:
        int: Score metier compris entre 0 et 100.

    Raises:
        Aucun.
    """

    sequel_score = _sequel_matching_score(imported_key, candidate_key)
    if sequel_score is not None:
        return sequel_score
    word_suffix_score = _word_suffix_matching_score(imported_key, candidate_key)
    if word_suffix_score is not None:
        return word_suffix_score
    return matching_score(imported_key, candidate_key)


def _sequel_matching_score(imported_key: str, candidate_key: str) -> int | None:
    if _has_numeric_suffix_extension(imported_key, candidate_key):
        return 0
    imported_base, imported_suffix = _split_sequel_suffix(imported_key)
    candidate_base, candidate_suffix = _split_sequel_suffix(candidate_key)
    if imported_base != candidate_base:
        return None
    if imported_suffix is None and candidate_suffix is None:
        return None
    if imported_suffix is None or candidate_suffix is None:
        return 0
    return 100 if imported_suffix == candidate_suffix else 0


def _has_numeric_suffix_extension(first_key: str, second_key: str) -> bool:
    return _is_numeric_suffix_extension(first_key, second_key) or _is_numeric_suffix_extension(
        second_key,
        first_key,
    )


def _is_numeric_suffix_extension(base_key: str, extended_key: str) -> bool:
    if not base_key or len(extended_key) <= len(base_key):
        return False
    if not extended_key.startswith(base_key):
        return False
    remaining_suffix = extended_key[len(base_key):]
    return bool(re.match(r"^[ -]\d", remaining_suffix))


def _word_suffix_matching_score(imported_key: str, candidate_key: str) -> int | None:
    imported_words = imported_key.split()
    candidate_words = candidate_key.split()
    if len(imported_words) < 3 or len(imported_words) != len(candidate_words):
        return None
    if imported_words[:-1] != candidate_words[:-1]:
        return None
    if imported_words[-1] == candidate_words[-1]:
        return None
    return 0


def _split_sequel_suffix(game_name_key: str) -> tuple[str, tuple[int, ...] | None]:
    suffix_match = _SEQUEL_SUFFIX_PATTERN.match(game_name_key)
    if suffix_match is None:
        return game_name_key, None
    suffix = _numeric_suffix(suffix_match.group("suffix"))
    if suffix is None:
        return game_name_key, None
    return suffix_match.group("base"), suffix


def _numeric_suffix(suffix: str) -> tuple[int, ...] | None:
    values = []
    for suffix_part in suffix.split("-"):
        if suffix_part.isdigit():
            values.append(int(suffix_part))
            continue
        roman_value = _roman_to_integer(suffix_part)
        if roman_value is None:
            return None
        values.append(roman_value)
    return tuple(values)


def _roman_to_integer(value: str) -> int | None:
    total = 0
    previous_value = 0
    for character in reversed(value):
        current_value = _ROMAN_VALUES.get(character)
        if current_value is None:
            return None
        if current_value < previous_value:
            total -= current_value
        else:
            total += current_value
            previous_value = current_value
    return total if _integer_to_roman(total) == value else None


def _integer_to_roman(value: int) -> str:
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
