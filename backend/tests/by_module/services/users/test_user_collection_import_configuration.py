#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires de la configuration d'import de collection utilisateur.

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.users import UserCollectionImportConfiguration


class UserCollectionImportConfigurationTest(unittest.TestCase):
    """Valide la configuration de l'import de collection utilisateur."""

    def test_from_environment_uses_default_values(self):
        """Verifie les valeurs par defaut de la configuration d'import.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les valeurs par defaut.
        """

        with patch.dict(os.environ, {}, clear=True):
            configuration = UserCollectionImportConfiguration.from_environment()

        self.assertEqual("/users/workspace", configuration.workspace_path)
        self.assertEqual(104857600, configuration.max_upload_bytes)

    def test_from_environment_reads_max_upload_bytes(self):
        """Verifie la lecture de la taille maximale d'upload.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la valeur configuree.
        """

        with patch.dict(
            os.environ,
            {"USER_COLLECTION_MAX_UPLOAD_BYTES": "2048", "USERS_WORKSPACE": "/ignored"},
            clear=True,
        ):
            configuration = UserCollectionImportConfiguration.from_environment()

        self.assertEqual("/users/workspace", configuration.workspace_path)
        self.assertEqual(2048, configuration.max_upload_bytes)

    def test_from_environment_rejects_invalid_max_upload_bytes(self):
        """Verifie le refus d'une taille maximale invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de configuration.
        """

        with patch.dict(os.environ, {"USER_COLLECTION_MAX_UPLOAD_BYTES": "0"}, clear=True):
            with self.assertRaises(ValueError) as context:
                UserCollectionImportConfiguration.from_environment()

        self.assertIn("USER_COLLECTION_MAX_UPLOAD_BYTES", str(context.exception))

    def test_ensure_workspace_directory_creates_target_directory(self):
        """Verifie la creation du repertoire cible par le runtime backend.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la creation du repertoire.
        """

        with tempfile.TemporaryDirectory() as directory:
            workspace_path = Path(directory) / "users" / "workspace"
            configuration = UserCollectionImportConfiguration(
                workspace_path=str(workspace_path),
                max_upload_bytes=104857600,
            )

            created_path = configuration.ensure_workspace_directory()
            self.assertEqual(workspace_path, created_path)
            self.assertTrue(created_path.is_dir())


if __name__ == "__main__":
    unittest.main()
