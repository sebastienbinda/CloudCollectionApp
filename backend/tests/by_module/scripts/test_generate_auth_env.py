#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-08
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du generateur de secrets d'environnement.

import sys
import unittest
from pathlib import Path

PROJECT_DIR = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "scripts" / "generate_auth_env.py").exists()
)
sys.path.insert(0, str(PROJECT_DIR))

from scripts.generate_auth_env import AuthEnvGenerator, EnvSecretCipher  # noqa: E402


class AuthEnvGeneratorTest(unittest.TestCase):
    """Valide les secrets produits pour l'authentification et Postgres."""

    def test_generate_returns_postgres_password_and_encrypted_copy(self):
        """Verifie la generation du mot de passe Postgres et de sa copie chiffree.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les variables Postgres generees.
        """

        values = AuthEnvGenerator(
            password_length=12,
            secret_key_bytes=16,
            postgres_password_length=18,
        ).generate()
        cipher = EnvSecretCipher(values["AUTH_ENV_ENCRYPTION_KEY"])

        self.assertEqual(18, len(values["POSTGRES_PASSWORD"]))
        self.assertEqual(values["POSTGRES_PASSWORD"], values["GENERATED_POSTGRES_PASSWORD"])
        self.assertTrue(values["POSTGRES_PASSWORD_ENCRYPTED"].startswith("fernet:"))
        self.assertEqual(
            values["POSTGRES_PASSWORD"],
            cipher.decrypt(values["POSTGRES_PASSWORD_ENCRYPTED"]),
        )


if __name__ == "__main__":
    unittest.main()
