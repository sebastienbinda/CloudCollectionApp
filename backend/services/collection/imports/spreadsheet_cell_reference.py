#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : utilitaires de validation des references de cellules tableur.

import re
from typing import Optional


class SpreadsheetCellReferenceParser:
    """Parse les references tableur utilisees par la configuration d'import."""

    RANGE_PATTERN = re.compile(r"^([A-Z]+)([1-9][0-9]*):([A-Z]+)([1-9][0-9]*)$")
    COLUMN_PATTERN = re.compile(r"^[A-Z]+$")

    def parse_range(
        self,
        value: str,
    ) -> Optional[tuple[int, int, int, int]]:
        """Parse une plage tableur inclusive.

        Args:
            value (str): Plage brute au format `A1:H200`.

        Returns:
            Optional[tuple[int, int, int, int]]: Bornes colonne/ligne ou `None`.
        """

        match = self.RANGE_PATTERN.match(value)
        if not match:
            return None
        start_column, start_row, end_column, end_row = match.groups()
        bounds = (
            self.column_to_index(start_column),
            int(start_row),
            self.column_to_index(end_column),
            int(end_row),
        )
        if bounds[0] > bounds[2] or bounds[1] > bounds[3]:
            return None
        return bounds

    def is_column_name(self, value: str) -> bool:
        """Indique si une valeur est une colonne tableur valide.

        Args:
            value (str): Valeur a verifier.

        Returns:
            bool: `True` si la valeur est une colonne comme `A` ou `AA`.
        """

        return bool(self.COLUMN_PATTERN.match(value))

    def column_to_index(self, column_name: str) -> int:
        """Convertit une colonne tableur en index numerique.

        Args:
            column_name (str): Nom de colonne comme `A` ou `AA`.

        Returns:
            int: Index commencant a `1`.
        """

        index = 0
        for character in column_name:
            index = index * 26 + (ord(character) - ord("A") + 1)
        return index
