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
# Description : factory de lecteurs de fichiers de collection.

from .collection_file_description import CollectionFileType
from .collection_file_reader import CollectionFileReader


class CollectionFileReaderFactory:
    """Selectionne le lecteur de collection adapte au type de fichier."""

    def create(self, file_type: CollectionFileType) -> CollectionFileReader:
        """Construit le lecteur correspondant au type de fichier.

        Args:
            file_type (CollectionFileType): Type de fichier valide.

        Returns:
            CollectionFileReader: Lecteur specialise.

        Raises:
            ValueError: Si le type de fichier n'a pas de lecteur associe.
        """

        if file_type == CollectionFileType.LIBREOFFICE_ODS:
            from services.ods import OdsCollectionImportReader

            return OdsCollectionImportReader()
        raise ValueError(f"Type de fichier non supporte: {file_type.value}.")
