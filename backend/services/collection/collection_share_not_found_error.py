#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : erreur d'absence d'un partage appartenant au proprietaire.


class CollectionShareNotFoundError(ValueError):
    """Signale qu'un partage n'appartient pas au proprietaire connecte."""
