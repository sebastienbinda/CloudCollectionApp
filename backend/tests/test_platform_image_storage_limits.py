#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests des limites disque des images de plateformes.

from io import BytesIO
import tempfile
import unittest

from werkzeug.datastructures import FileStorage

from services.database import DatabaseConfiguration
from services.library import PlatformImageConfiguration
from services.library.platform_image_service import (
    PlatformImageService,
    PlatformImageStorageLimitExceededError,
)

try:
    from tests.test_platform_image_service import (
        FakeEngine,
        FakeNotifier,
        FakePlatformImageRepository,
        FakeUserRepository,
    )
except ModuleNotFoundError:
    from test_platform_image_service import (
        FakeEngine,
        FakeNotifier,
        FakePlatformImageRepository,
        FakeUserRepository,
    )


class PlatformImageStorageLimitsTest(unittest.TestCase):
    """Valide les limites disque des images de plateformes."""

    def setUp(self):
        """Prepare les dependances de test.

        Args:
            Aucun.

        Returns:
            None: Les fakes sont prepares.
        """

        self.temp_directory = tempfile.TemporaryDirectory()
        self.image_repository = FakePlatformImageRepository()
        self.notifier = FakeNotifier()

    def tearDown(self):
        """Nettoie le repertoire temporaire.

        Args:
            Aucun.

        Returns:
            None: Les fichiers temporaires sont supprimes.
        """

        self.temp_directory.cleanup()

    def create_service(self, configuration):
        """Construit un service image avec la configuration fournie.

        Args:
            configuration (PlatformImageConfiguration): Configuration image testee.

        Returns:
            PlatformImageService: Service configure avec des dependances factices.
        """

        return PlatformImageService(
            DatabaseConfiguration(None, "collection", "0.1"),
            configuration,
            image_repository=self.image_repository,
            user_repository=FakeUserRepository(),
            notifier=self.notifier,
            engine=FakeEngine(),
        )

    def image_file(self, content=b"image"):
        """Construit un fichier image multipart factice.

        Args:
            content (bytes): Contenu du fichier.

        Returns:
            FileStorage: Fichier multipart factice.
        """

        return FileStorage(
            stream=BytesIO(content),
            filename="console.png",
            content_type="image/png",
        )

    def test_upload_rejects_when_user_pending_image_count_limit_is_reached(self):
        """Verifie le blocage quand le nombre d'images en attente est atteint.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le quota utilisateur.
        """

        service = self.create_service(
            PlatformImageConfiguration(
                self.temp_directory.name,
                10,
                max_pending_images_per_user=1,
            )
        )
        self.image_repository.storage_usage = {
            "pending_image_count": 1,
            "pending_image_bytes": 3,
            "total_image_bytes": 3,
        }

        with self.assertRaises(PlatformImageStorageLimitExceededError):
            service.upload_image(1, self.image_file(), "user@example.com")

        self.assertEqual([], self.image_repository.created_images)
        self.assertEqual("pending_user_count", self.notifier.disabled_calls[0][1])

    def test_upload_rejects_when_user_pending_size_limit_is_exceeded(self):
        """Verifie le blocage quand la taille en attente utilisateur est depassee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le quota taille utilisateur.
        """

        service = self.create_service(
            PlatformImageConfiguration(
                self.temp_directory.name,
                10,
                max_pending_bytes_per_user=6,
                max_total_bytes=100,
            )
        )
        self.image_repository.storage_usage = {
            "pending_image_count": 1,
            "pending_image_bytes": 4,
            "total_image_bytes": 4,
        }

        with self.assertRaises(PlatformImageStorageLimitExceededError):
            service.upload_image(1, self.image_file(b"123"), "user@example.com")

        self.assertEqual([], self.image_repository.created_images)
        self.assertEqual("pending_user_bytes", self.notifier.disabled_calls[0][1])

    def test_upload_rejects_when_total_storage_limit_is_reached(self):
        """Verifie le blocage quand la taille totale disque est atteinte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le quota global.
        """

        service = self.create_service(
            PlatformImageConfiguration(
                self.temp_directory.name,
                10,
                max_pending_bytes_per_user=100,
                max_total_bytes=5,
            )
        )
        self.image_repository.storage_usage = {
            "pending_image_count": 0,
            "pending_image_bytes": 0,
            "total_image_bytes": 5,
        }

        with self.assertRaises(PlatformImageStorageLimitExceededError):
            service.upload_image(1, self.image_file(), "user@example.com")

        self.assertEqual([], self.image_repository.created_images)
        self.assertEqual("total_bytes", self.notifier.disabled_calls[0][1])


if __name__ == "__main__":
    unittest.main()
