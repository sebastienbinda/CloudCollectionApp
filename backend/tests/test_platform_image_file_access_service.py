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
# Description : tests d'acces aux fichiers d'images de plateformes.

import tempfile
import unittest
from pathlib import Path

from services.database import DatabaseConfiguration
from services.library import PlatformImageConfiguration
from services.library.platform_image_service import (
    PlatformImageNotFoundError,
    PlatformImageService,
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


class PlatformImageFileAccessServiceTest(unittest.TestCase):
    """Valide la lecture des fichiers d'images de plateformes."""

    def setUp(self):
        """Prepare les dependances de test.

        Args:
            Aucun.

        Returns:
            None: Les fakes sont prepares.
        """

        self.temp_directory = tempfile.TemporaryDirectory()
        self.image_repository = FakePlatformImageRepository()
        self.service = PlatformImageService(
            DatabaseConfiguration(None, "collection", "0.1"),
            PlatformImageConfiguration(self.temp_directory.name, 10),
            image_repository=self.image_repository,
            user_repository=FakeUserRepository(),
            notifier=FakeNotifier(),
            engine=FakeEngine(),
        )

    def tearDown(self):
        """Nettoie le repertoire temporaire.

        Args:
            Aucun.

        Returns:
            None: Les fichiers temporaires sont supprimes.
        """

        self.temp_directory.cleanup()

    def test_get_accepted_image_returns_public_file(self):
        """Verifie la lecture publique d'une image acceptee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le fichier public.
        """

        image_path = Path(self.temp_directory.name) / "accepted.png"
        image_path.write_bytes(b"ok")
        self.image_repository.accepted_image = {"path": str(image_path)}

        image_file = self.service.get_accepted_image_file(1, 4)

        self.assertEqual(str(image_path), image_file.path)
        self.assertEqual("image/png", image_file.mimetype)

    def test_get_accepted_image_rejects_waiting_or_missing_file(self):
        """Verifie le refus public d'une image non acceptee ou illisible.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur 404 metier.
        """

        with self.assertRaises(PlatformImageNotFoundError):
            self.service.get_accepted_image_file(1, 4)
        self.image_repository.accepted_image = {
            "path": str(Path(self.temp_directory.name) / "missing.png")
        }
        with self.assertRaises(PlatformImageNotFoundError):
            self.service.get_accepted_image_file(1, 4)

    def test_get_moderation_image_returns_waiting_file(self):
        """Verifie la lecture admin d'une image en attente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le fichier protege.
        """

        image_path = Path(self.temp_directory.name) / "waiting.webp"
        image_path.write_bytes(b"ok")
        self.image_repository.moderation_image = {
            "path": str(image_path),
            "status": "WAITING_VALIDATION",
        }

        image_file = self.service.get_moderation_image_file(1, 4)

        self.assertEqual(str(image_path), image_file.path)
        self.assertEqual("image/webp", image_file.mimetype)

    def test_get_moderation_image_rejects_missing_file(self):
        """Verifie le refus admin d'une image introuvable ou illisible.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur 404 metier.
        """

        with self.assertRaises(PlatformImageNotFoundError):
            self.service.get_moderation_image_file(1, 4)
        self.image_repository.moderation_image = {
            "path": str(Path(self.temp_directory.name) / "missing.png"),
        }
        with self.assertRaises(PlatformImageNotFoundError):
            self.service.get_moderation_image_file(1, 4)


if __name__ == "__main__":
    unittest.main()
