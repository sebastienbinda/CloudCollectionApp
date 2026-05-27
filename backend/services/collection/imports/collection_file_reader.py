#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : abstraction generique de lecture de fichier de collection.

from typing import Protocol

from .collection_file_description import CollectionFileDescription
from .collection_import_models import CollectionImportData


class CollectionFileReadError(ValueError):
    """Signale qu'un fichier de collection ne peut pas etre lu."""


class CollectionFileValidationError(ValueError):
    """Signale qu'un fichier lu ne respecte pas la configuration fournie."""


class CollectionFileReader(Protocol):
    """Definit le contrat commun des lecteurs de fichiers de collection."""

    @property
    def accepted_extensions(self) -> tuple[str, ...]:
        """Retourne les extensions de fichier acceptees.

        Args:
            Aucun.

        Returns:
            tuple[str, ...]: Extensions en minuscules avec le point initial.
        """

    def read(
        self,
        file_path: str,
        description: CollectionFileDescription,
    ) -> CollectionImportData:
        """Lit un fichier de collection selon une description valide.

        Args:
            file_path (str): Chemin du fichier a lire.
            description (CollectionFileDescription): Description valide du fichier.

        Returns:
            CollectionImportData: Donnees metier extraites.

        Raises:
            CollectionFileReadError: Si le fichier est illisible.
            CollectionFileValidationError: Si son contenu ne respecte pas la configuration.
        """
