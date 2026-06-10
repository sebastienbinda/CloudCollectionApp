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
