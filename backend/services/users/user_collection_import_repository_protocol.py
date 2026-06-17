#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-16
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : protocole de persistance requis par l'import utilisateur.

from typing import Protocol

from services.collection.imports import CollectionImportData
from services.database.user_collection_import_repository import (
    UserCollectionImportPersistenceResult,
)


class UserCollectionImportRepository(Protocol):
    """Definit les operations de persistance requises par l'import."""

    def user_has_collection(self, user_id: int) -> bool:
        """Indique si un utilisateur a deja une collection.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            bool: `True` si une collection existe deja.
        """

    def import_collection(
        self,
        user_id: int,
        collection_file_path: str,
        import_data: CollectionImportData,
        collection_file_description: dict,
    ) -> UserCollectionImportPersistenceResult:
        """Persiste les donnees importees dans une transaction.

        Args:
            user_id (int): Identifiant utilisateur.
            collection_file_path (str): Chemin final du fichier.
            import_data (CollectionImportData): Donnees lues depuis le fichier.
            collection_file_description (dict): Description valide ayant servi a l'import.

        Returns:
            UserCollectionImportPersistenceResult: Compteurs de persistance.
        """

    def reinitialize_collection(self, user_id: int) -> None:
        """Reinitialise la collection persistante d'un utilisateur.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            UserCollectionImportNotFoundError: Si aucune collection n'existe.
            UserCollectionImportUnexpectedError: Si la reinitialisation echoue.
        """
