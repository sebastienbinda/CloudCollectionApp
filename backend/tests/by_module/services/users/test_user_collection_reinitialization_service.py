#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-07
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du service de reinitialisation de collection utilisateur.

import unittest

from services.database.user_collection_import_repository import (
    UserCollectionReinitializationNotFoundError,
)
from services.users.user_collection_import_configuration import (
    UserCollectionImportConfiguration,
)
from services.users.user_collection_import_service import (
    UserCollectionImportNotFoundError,
    UserCollectionImportService,
    UserCollectionImportUnexpectedError,
)


class FakeReinitializationRepository:
    """Repository factice de reinitialisation de collection."""

    def __init__(self, error=None):
        """Initialise le repository factice.

        Args:
            error (Exception | None): Erreur levee pendant la reinitialisation.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.error = error
        self.calls = []

    def user_has_collection(self, user_id):
        """Indique que le statut n'est pas utilise dans ces tests.

        Args:
            user_id (int): Identifiant utilisateur ignore.

        Returns:
            bool: Toujours `False`.
        """

        return False

    def reinitialize_collection(self, user_id):
        """Memorise l'appel de reinitialisation.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            Exception: Erreur configuree pour le test.
        """

        self.calls.append(user_id)
        if self.error:
            raise self.error


class FakeReaderFactory:
    """Factory de lecteur inutilisee par la reinitialisation."""


class UserCollectionReinitializationServiceTest(unittest.TestCase):
    """Valide l'orchestration service de la reinitialisation."""

    def test_reinitialize_collection_delegates_to_import_repository(self):
        """Verifie la delegation au repository d'import existant.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'appel repository.
        """

        repository = FakeReinitializationRepository()
        service = self._build_service(repository)

        service.reinitialize_collection(7)

        self.assertEqual([7], repository.calls)

    def test_reinitialize_collection_maps_not_found_error(self):
        """Verifie le mapping de l'absence de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur metier.
        """

        repository = FakeReinitializationRepository(
            UserCollectionReinitializationNotFoundError("missing")
        )
        service = self._build_service(repository)

        with self.assertRaises(UserCollectionImportNotFoundError):
            service.reinitialize_collection(7)

    def test_reinitialize_collection_maps_unexpected_error(self):
        """Verifie le mapping des erreurs techniques.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur inattendue.
        """

        repository = FakeReinitializationRepository(RuntimeError("disk"))
        service = self._build_service(repository)

        with self.assertRaises(UserCollectionImportUnexpectedError):
            service.reinitialize_collection(7)

    def _build_service(self, repository):
        """Construit le service d'import teste.

        Args:
            repository (FakeReinitializationRepository): Repository injecte.

        Returns:
            UserCollectionImportService: Service configure pour le test.
        """

        return UserCollectionImportService(
            UserCollectionImportConfiguration(
                workspace_path="/tmp/cloudcollection-test",
                max_upload_bytes=1024,
            ),
            repository,
            FakeReaderFactory(),
        )


if __name__ == "__main__":
    unittest.main()
