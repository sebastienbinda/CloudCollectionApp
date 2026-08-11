#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
# Projet : CloudCollectionApp
# Date de creation : 2026-08-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : erreurs metier du workflow d'import de collection utilisateur.


class UserCollectionImportError(Exception):
    """Classe de base des erreurs metier d'import de collection utilisateur."""


class UserCollectionImportInvalidFileError(UserCollectionImportError):
    """Signale qu'un fichier d'import est invalide ou illisible."""

    def __init__(self, message: str, details: list[str] | None = None):
        """Initialise l'erreur de fichier invalide.

        Args:
            message (str): Message fonctionnel principal.
            details (list[str] | None): Raisons techniques affichables.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.details = details or [message]
        super().__init__(message)


class UserCollectionImportTooLargeError(UserCollectionImportError):
    """Signale qu'un fichier d'import depasse la taille maximale autorisee."""


class UserCollectionImportTemporaryFileMissingError(UserCollectionImportError):
    """Signale que le fichier temporaire d'import est absent."""


class UserCollectionImportNotFoundError(UserCollectionImportError):
    """Signale qu'aucune collection utilisateur ne peut etre reinitialisee."""


class UserCollectionImportUnexpectedError(UserCollectionImportError):
    """Signale une erreur non fonctionnelle pendant l'import."""
