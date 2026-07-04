#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Exports publics des utilitaires de matching textuel."""

from .string_similarity import game_name_matching_score, matching_score

__all__ = ["game_name_matching_score", "matching_score"]
