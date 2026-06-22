#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : calcul partage des scores de similarite textuelle.

from difflib import SequenceMatcher


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
