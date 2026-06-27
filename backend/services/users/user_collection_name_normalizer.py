#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : normalisation des noms de collection utilisateur.

import unicodedata
from typing import Any, Optional

from services.formatting import SheetValueFormatter


class UserCollectionNameNormalizer:
    """Normalise les noms metier de collection utilisateur.

    La valeur stockee conserve la casse et les accents, tandis que la cle de
    comparaison les neutralise pour detecter les doublons fonctionnels.
    """

    _LOWERCASE_TITLE_WORDS = {
        "a", "and", "or", "de", "du", "des", "le", "la", "les", "au", "of", "et",
    }
    _ROMAN_NUMERALS = {
        "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
        "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx",
    }

    def stored_value(self, value: Any) -> Optional[str]:
        """Construit la valeur metier destinee au stockage.

        Args:
            value (Any): Valeur brute a normaliser.

        Returns:
            Optional[str]: Valeur `trim()` avec casse et accents conserves, ou `None`.
        """

        if value is None:
            return None
        return SheetValueFormatter.clean_text(value)

    def stored_game_name(self, value: Any) -> Optional[str]:
        """Construit le nom de jeu standardise destine au referentiel.

        Args:
            value (Any): Nom brut du jeu a standardiser.

        Returns:
            Optional[str]: Nom trimme, espace autour de `:` et casse titre, ou `None`.
        """

        stored_value = self.stored_value(value)
        if stored_value is None:
            return None
        colon_normalized_value = " : ".join(
            segment.strip()
            for segment in stored_value.split(":")
            if segment.strip()
        )
        return " : ".join(
            self._standardize_title_segment(segment)
            for segment in colon_normalized_value.split(" : ")
        )

    def comparison_key(self, value: Any) -> Optional[str]:
        """Construit la cle de comparaison sans accents.

        Args:
            value (Any): Valeur brute a normaliser.

        Returns:
            Optional[str]: Valeur `trim().lower()` sans accents, ou `None`.
        """

        stored_value = self.stored_value(value)
        if stored_value is None:
            return None
        decomposed_value = unicodedata.normalize("NFD", stored_value.lower())
        return "".join(
            character
            for character in decomposed_value
            if unicodedata.category(character) != "Mn"
        )

    def are_equivalent(self, first_value: Any, second_value: Any) -> bool:
        """Compare deux noms selon la normalisation metier.

        Args:
            first_value (Any): Premiere valeur brute.
            second_value (Any): Seconde valeur brute.

        Returns:
            bool: `True` si les deux valeurs ont la meme cle de comparaison.
        """

        first_key = self.comparison_key(first_value)
        second_key = self.comparison_key(second_value)
        return first_key is not None and first_key == second_key

    def _standardize_title_segment(self, segment: str) -> str:
        words = segment.split()
        return " ".join(
            self._standardize_title_word(word, is_first_word=index == 0)
            for index, word in enumerate(words)
        )

    def _standardize_title_word(self, word: str, is_first_word: bool = False) -> str:
        lower_word = word.lower()
        if not is_first_word and lower_word in self._LOWERCASE_TITLE_WORDS:
            return lower_word
        if lower_word in self._ROMAN_NUMERALS:
            return lower_word.upper()
        if "-" in word:
            return self._standardize_hyphenated_word(word)
        if "'" in word:
            return self._standardize_apostrophe_word(word, is_first_word)
        return self._capitalize_word(word)

    def _standardize_hyphenated_word(self, word: str) -> str:
        return "-".join(
            self._standardize_title_word(part, True) if part else part
            for part in word.split("-")
        )

    def _standardize_apostrophe_word(self, word: str, is_first_word: bool) -> str:
        prefix, suffix = word.split("'", 1)
        if not suffix:
            return self._capitalize_word(word)
        normalized_prefix = prefix.lower()
        if normalized_prefix not in {"d", "l"}:
            return self._capitalize_word(word)
        if normalized_prefix != "d" and is_first_word:
            normalized_prefix = self._capitalize_word(prefix)
        elif normalized_prefix != "d":
            normalized_prefix = prefix.lower()
        return f"{normalized_prefix}'{self._standardize_title_word(suffix, True)}"

    def _capitalize_word(self, word: str) -> str:
        if not word:
            return word
        if any(character.islower() for character in word) and any(
            character.isupper() for character in word[1:]
        ):
            return word
        return word[:1].upper() + word[1:].lower()
