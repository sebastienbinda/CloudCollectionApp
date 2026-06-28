#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-06
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du chiffrement des secrets d'environnement.

import os
import tempfile
import unittest
from typing import Optional

from services.auth import AuthTokenService
from services.security import EnvSecretCipher, EnvironmentSecretReader


class EnvSecretCipherTest(unittest.TestCase):
    """Valide le chiffrement des secrets stockes dans les fichiers .env."""

    def test_encrypt_then_decrypt_returns_original_value(self):
        """Verifie le cycle chiffrement puis dechiffrement.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la valeur dechiffree.
        """

        cipher = EnvSecretCipher(EnvSecretCipher.generate_key())

        encrypted_value = cipher.encrypt("secret-value")

        self.assertNotEqual("secret-value", encrypted_value)
        self.assertTrue(encrypted_value.startswith("fernet:"))
        self.assertEqual("secret-value", cipher.decrypt(encrypted_value))

    def test_auth_token_service_reads_encrypted_environment_secrets(self):
        """Verifie que le service d'authentification lit les secrets chiffres.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les identifiants dechiffres.
        """

        encryption_key = EnvSecretCipher.generate_key()
        cipher = EnvSecretCipher(encryption_key)
        previous_values = self._set_encrypted_auth_environment(cipher, encryption_key)
        try:
            service = AuthTokenService(username="admin")

            self.assertTrue(service.validate_credentials("admin", "secret-password"))
            token = service.create_access_token("admin")
            self.assertEqual("admin", service.validate_access_token(token)["sub"])
        finally:
            self._restore_environment(previous_values)

    def test_auth_token_service_requires_encryption_key_for_encrypted_secret(self):
        """Verifie qu'une cle de chiffrement manquante est refusee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de configuration.
        """

        previous_values = {
            "AUTH_ENV_ENCRYPTION_KEY": os.environ.pop("AUTH_ENV_ENCRYPTION_KEY", None),
            "AUTH_PASSWORD_ENCRYPTED": os.environ.get("AUTH_PASSWORD_ENCRYPTED"),
        }
        os.environ["AUTH_PASSWORD_ENCRYPTED"] = "fernet:invalid"
        try:
            with self.assertRaises(ValueError):
                AuthTokenService(username="admin", secret_key="plain-secret")
        finally:
            self._restore_environment(previous_values)

    def test_environment_secret_reader_uses_file_before_environment(self):
        """Verifie que la convention `_FILE` est prioritaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la valeur lue depuis le fichier.
        """

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as secret_file:
            secret_file.write("file-secret\n")
            secret_file_path = secret_file.name

        previous_values = {
            "SAMPLE_SECRET": os.environ.get("SAMPLE_SECRET"),
            "SAMPLE_SECRET_FILE": os.environ.get("SAMPLE_SECRET_FILE"),
        }
        os.environ["SAMPLE_SECRET"] = "env-secret"
        os.environ["SAMPLE_SECRET_FILE"] = secret_file_path
        try:
            self.assertEqual("file-secret", EnvironmentSecretReader.read("SAMPLE_SECRET"))
        finally:
            os.unlink(secret_file_path)
            self._restore_environment(previous_values)

    def test_environment_secret_reader_rejects_unreadable_file(self):
        """Verifie le refus d'un fichier de secret introuvable.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur attendue.
        """

        previous_values = {"MISSING_SECRET_FILE": os.environ.get("MISSING_SECRET_FILE")}
        os.environ["MISSING_SECRET_FILE"] = "/path/not/found"
        try:
            with self.assertRaises(ValueError):
                EnvironmentSecretReader.read("MISSING_SECRET")
        finally:
            self._restore_environment(previous_values)

    def _set_encrypted_auth_environment(
        self,
        cipher: EnvSecretCipher,
        encryption_key: str,
    ) -> dict[str, Optional[str]]:
        """Configure temporairement l'environnement avec des secrets chiffres.

        Args:
            cipher (EnvSecretCipher): Chiffreur utilise pour les secrets de test.
            encryption_key (str): Cle Fernet associee au chiffreur.

        Returns:
            dict[str, str | None]: Anciennes valeurs a restaurer apres le test.
        """

        names = [
            "AUTH_ENV_ENCRYPTION_KEY",
            "AUTH_PASSWORD_ENCRYPTED",
            "AUTH_SECRET_KEY_ENCRYPTED",
            "AUTH_ENV_ENCRYPTION_KEY_FILE",
            "AUTH_PASSWORD_ENCRYPTED_FILE",
            "AUTH_SECRET_KEY_ENCRYPTED_FILE",
            "AUTH_PASSWORD",
            "AUTH_SECRET_KEY",
        ]
        previous_values = {name: os.environ.get(name) for name in names}
        os.environ["AUTH_ENV_ENCRYPTION_KEY"] = encryption_key
        os.environ["AUTH_PASSWORD_ENCRYPTED"] = cipher.encrypt("secret-password")
        os.environ["AUTH_SECRET_KEY_ENCRYPTED"] = cipher.encrypt("token-secret")
        os.environ.pop("AUTH_PASSWORD", None)
        os.environ.pop("AUTH_SECRET_KEY", None)
        return previous_values

    def _restore_environment(self, previous_values: dict[str, Optional[str]]) -> None:
        """Restaure les variables d'environnement modifiees par un test.

        Args:
            previous_values (dict[str, str | None]): Valeurs a remettre en place.

        Returns:
            None: L'environnement du processus est restaure.
        """

        for name, value in previous_values.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


if __name__ == "__main__":
    unittest.main()
