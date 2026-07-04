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
# Description : resultat explicable du matching de titres de jeux.

from __future__ import annotations

from dataclasses import dataclass

try:
    from .game_title_matching_decision import GameTitleMatchingDecision
except ImportError:
    from game_title_matching_decision import GameTitleMatchingDecision


@dataclass(frozen=True)
class GameTitleMatchingResult:
    """Decrit le resultat explicable du matching entre deux titres de jeux.

    Attributes:
        score (int): Score de matching entre `0` et `100`.
        decision (GameTitleMatchingDecision): Decision metier produite.
        rule (str): Identifiant stable de la regle appliquee.
        reason (str): Raison lisible de la decision.
    """

    score: int
    decision: GameTitleMatchingDecision
    rule: str
    reason: str
