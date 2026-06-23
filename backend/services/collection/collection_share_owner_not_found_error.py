#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : erreur d'absence du proprietaire d'un partage de collection.


class CollectionShareOwnerNotFoundError(ValueError):
    """Signale que le sujet Bearer ne correspond a aucun proprietaire."""
