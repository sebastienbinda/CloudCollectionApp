#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : erreur d'indisponibilite d'un partage de collection.


class CollectionShareUnavailableError(ValueError):
    """Signale un partage expire, revoque ou prive de proprietaire actif."""
