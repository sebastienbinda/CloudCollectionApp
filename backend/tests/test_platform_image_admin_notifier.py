#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-19
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du notifier administrateur des images de plateformes.

import logging
import unittest

from services.library.platform_image_admin_notifier import PlatformImageAdminNotifier


class FakeEmailSender:
    """Expediteur email factice."""

    def __init__(self):
        """Initialise l'expediteur factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.sent = []

    def send_email(self, recipient_email, subject, body):
        """Memorise l'email envoye.

        Args:
            recipient_email (str): Destinataire.
            subject (str): Sujet.
            body (str): Corps.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.sent.append((recipient_email, subject, body))


class PlatformImageAdminNotifierTest(unittest.TestCase):
    """Valide les notifications admin des images."""

    def test_notifier_sends_email_when_admin_is_configured(self):
        """Verifie l'envoi d'email admin.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le message.
        """

        email_sender = FakeEmailSender()
        notifier = PlatformImageAdminNotifier(
            email_sender=email_sender,
            admin_notification_email="admin@example.com",
        )

        notifier.notify_image_created("Switch", 4, "user@example.com")

        self.assertEqual("admin@example.com", email_sender.sent[0][0])
        self.assertIn("Switch", email_sender.sent[0][2])

    def test_notifier_logs_warning_without_admin_email(self):
        """Verifie le warning si aucun email admin n'est configure.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le log.
        """

        logger = logging.getLogger("platform-image-test")
        notifier = PlatformImageAdminNotifier(admin_notification_email="", logger=logger)

        with self.assertLogs("platform-image-test", level="WARNING") as logs:
            notifier.notify_image_created("Switch", 4, "user@example.com")

        self.assertIn("ADMIN_NOTIFICATION_EMAIL", logs.output[0])


if __name__ == "__main__":
    unittest.main()
