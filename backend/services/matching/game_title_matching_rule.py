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
# Description : contrat des regles de matching de titres de jeux.

from __future__ import annotations

from typing import Protocol

try:
    from .game_title_matching_result import GameTitleMatchingResult
except ImportError:
    from game_title_matching_result import GameTitleMatchingResult


class GameTitleMatchingRule(Protocol):
    """Definit une regle de matching de titres de jeux.

    Returns:
        GameTitleMatchingRule: Contrat structurel des regles.

    Raises:
        Aucun.
    """

    def evaluate(
        self,
        imported_key: str,
        candidate_key: str,
    ) -> GameTitleMatchingResult | None:
        """Evalue une paire de titres normalises.

        Args:
            imported_key (str): Cle normalisee du titre importe.
            candidate_key (str): Cle normalisee du titre candidat.

        Returns:
            GameTitleMatchingResult | None: Resultat si la regle s'applique.

        Raises:
            Aucun.
        """
