#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Exports publics des utilitaires de matching textuel."""

from .game_title_matching_decision import GameTitleMatchingDecision
from .game_title_matching_engine import GameTitleMatchingEngine
from .game_title_matching_result import GameTitleMatchingResult
from .string_similarity import (
    explain_game_name_matching,
    game_name_matching_score,
    matching_score,
)

__all__ = [
    "GameTitleMatchingDecision",
    "GameTitleMatchingEngine",
    "GameTitleMatchingResult",
    "explain_game_name_matching",
    "game_name_matching_score",
    "matching_score",
]
