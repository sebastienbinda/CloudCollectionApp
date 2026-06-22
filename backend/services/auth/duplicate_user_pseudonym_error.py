#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-22
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : erreur metier de collision de pseudonyme utilisateur.


class DuplicateUserPseudonymError(ValueError):
    """Signale qu'un pseudonyme est deja rattache a un compte."""
