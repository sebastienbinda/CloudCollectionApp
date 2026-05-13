#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-13
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires de la configuration email.

import os
import unittest
from unittest.mock import patch

from services.email import EmailConfiguration


class EmailConfigurationTest(unittest.TestCase):
    def test_generic_smtp_configuration_uses_environment_values(self):
        """Verifie la configuration SMTP generique.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la configuration SMTP.
        """

        with patch.dict(
            os.environ,
            {
                "EMAIL_DELIVERY_MODE": "smtp",
                "SMTP_FROM_EMAIL": "noreply@example.com",
                "SMTP_HOST": "smtp.example.com",
                "SMTP_PORT": "2525",
                "SMTP_USERNAME": "user",
                "SMTP_PASSWORD": "password",
                "SMTP_USE_TLS": "false",
            },
            clear=True,
        ):
            configuration = EmailConfiguration.from_environment()

        self.assertEqual("smtp", configuration.delivery_mode)
        self.assertEqual("noreply@example.com", configuration.sender_email)
        self.assertEqual("smtp.example.com", configuration.smtp_host)
        self.assertEqual(2525, configuration.smtp_port)
        self.assertEqual("user", configuration.smtp_username)
        self.assertEqual("password", configuration.smtp_password)
        self.assertFalse(configuration.smtp_use_tls)

    def test_smtp_mode_requires_host(self):
        """Verifie le refus d'une configuration SMTP sans hote.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        with patch.dict(
            os.environ,
            {
                "EMAIL_DELIVERY_MODE": "smtp",
                "SMTP_FROM_EMAIL": "noreply@example.com",
            },
            clear=True,
        ):
            with self.assertRaises(ValueError) as context:
                EmailConfiguration.from_environment()

        self.assertIn("SMTP_HOST", str(context.exception))


if __name__ == "__main__":
    unittest.main()
