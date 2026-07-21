#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-07-21
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : suppression du fichier de collection stocke.

import logging
from pathlib import Path


class UserCollectionFileRemover:
    """Supprime le fichier de collection stocke sur disque."""

    def __init__(self, logger=None):
        """Initialise le suppresseur de fichier.

        Args:
            logger (logging.Logger | None): Logger applicatif.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.logger = logger or logging.getLogger(__name__)

    def delete_collection_file(self, collection_file_path: str) -> None:
        """Supprime le fichier de collection si son chemin est renseigne.

        Args:
            collection_file_path (str): Chemin du fichier a supprimer.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            OSError: Si le fichier existe mais ne peut pas etre supprime.
        """

        if not collection_file_path:
            return
        resolved_path = Path(collection_file_path)
        try:
            resolved_path.unlink()
        except FileNotFoundError:
            self.logger.warning("Fichier de collection absent pendant la reinitialisation.")
