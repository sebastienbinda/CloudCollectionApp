#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : erreur explicite d'expiration d'un token Bearer signe.


class ExpiredAccessTokenError(ValueError):
    """Signale un token signe expire en conservant son payload valide."""

    def __init__(self, payload: dict):
        """Initialise l'erreur d'expiration.

        Args:
            payload (dict): Payload dont la signature a ete validee.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        super().__init__("Token expire.")
        self.payload = payload
