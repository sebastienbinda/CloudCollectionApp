#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-03
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : parsing des valeurs booleennes de wishlist.

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WishlistValueParseResult:
    """Represente le resultat du parsing d'une valeur wishlist.

    Attributes:
        value (bool): Valeur booleenne normalisee.
        is_valid (bool): Indique si la valeur source est reconnue.
        invalid_value (str): Valeur invalide normalisee pour les warnings.
    """

    value: bool
    is_valid: bool
    invalid_value: str = ""


class WishlistValueParser:
    """Parse les valeurs utilisateur representant un booleen wishlist."""

    TRUE_VALUES = frozenset({"oui", "o", "true", "yes", "y"})
    FALSE_VALUES = frozenset({"non", "n", "false", "no"})

    def parse(self, value: Any) -> WishlistValueParseResult:
        """Parse une valeur brute issue d'une colonne wishlist.

        Args:
            value (Any): Valeur brute lue dans le fichier de collection.

        Returns:
            WishlistValueParseResult: Resultat valide ou valeur invalide.

        Raises:
            Aucun.
        """

        normalized_value = self._normalize(value)
        if not normalized_value:
            return WishlistValueParseResult(False, True)
        if normalized_value in self.TRUE_VALUES:
            return WishlistValueParseResult(True, True)
        if normalized_value in self.FALSE_VALUES:
            return WishlistValueParseResult(False, True)
        return WishlistValueParseResult(False, False, str(value).strip())

    def _normalize(self, value: Any) -> str:
        """Normalise une valeur brute avant comparaison.

        Args:
            value (Any): Valeur brute a normaliser.

        Returns:
            str: Valeur textuelle trimmee et minuscule.

        Raises:
            Aucun.
        """

        if value is None:
            return ""
        return str(value).strip().lower()
