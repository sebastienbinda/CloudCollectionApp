#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-18
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de configuration des images de plateformes.

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.library import PlatformImageConfiguration


class PlatformImageConfigurationTest(unittest.TestCase):
    """Valide la configuration de stockage des images de plateformes."""

    def test_from_environment_uses_default_values(self):
        """Verifie les valeurs par defaut de la configuration d'images.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les valeurs par defaut.
        """

        with patch.dict(os.environ, {}, clear=True):
            configuration = PlatformImageConfiguration.from_environment()

        self.assertEqual("/images", configuration.image_directory_path)
        self.assertEqual(10485760, configuration.max_upload_bytes)

    def test_from_environment_reads_image_settings(self):
        """Verifie la lecture des variables d'environnement d'images.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les valeurs configurees.
        """

        with patch.dict(
            os.environ,
            {
                "BACKEND_IMG_DIR": "/custom/images",
                "PLATFORM_IMAGE_MAX_UPLOAD_BYTES": "2048",
            },
            clear=True,
        ):
            configuration = PlatformImageConfiguration.from_environment()

        self.assertEqual("/custom/images", configuration.image_directory_path)
        self.assertEqual(2048, configuration.max_upload_bytes)

    def test_from_environment_rejects_empty_image_directory(self):
        """Verifie le refus d'un repertoire image vide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de configuration.
        """

        with patch.dict(os.environ, {"BACKEND_IMG_DIR": "   "}, clear=True):
            with self.assertRaises(ValueError) as context:
                PlatformImageConfiguration.from_environment()

        self.assertIn("BACKEND_IMG_DIR", str(context.exception))

    def test_from_environment_rejects_invalid_max_upload_bytes(self):
        """Verifie le refus d'une taille maximale invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de configuration.
        """

        with patch.dict(os.environ, {"PLATFORM_IMAGE_MAX_UPLOAD_BYTES": "0"}, clear=True):
            with self.assertRaises(ValueError) as context:
                PlatformImageConfiguration.from_environment()

        self.assertIn("PLATFORM_IMAGE_MAX_UPLOAD_BYTES", str(context.exception))

    def test_ensure_image_directory_creates_target_directory(self):
        """Verifie la creation du repertoire cible par le runtime backend.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la creation du repertoire.
        """

        with tempfile.TemporaryDirectory() as directory:
            image_directory_path = Path(directory) / "images"
            configuration = PlatformImageConfiguration(
                image_directory_path=str(image_directory_path),
                max_upload_bytes=10485760,
            )

            created_path = configuration.ensure_image_directory()

            self.assertEqual(image_directory_path, created_path)
            self.assertTrue(created_path.is_dir())


if __name__ == "__main__":
    unittest.main()
