#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de notification admin du matching plateformes.

import unittest

from services.database import PlatformMatchingAdminNotifier
from tests.fake_platform_matching_email_sender import FakePlatformMatchingEmailSender


class PlatformMatchingAdminNotifierTest(unittest.TestCase):
    """Valide l'email de verification manuelle des plateformes."""

    def test_notify_manual_matches_sends_email_only_when_needed(self):
        """Verifie l'envoi conditionnel de l'email administrateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'email.
        """

        sender = FakePlatformMatchingEmailSender()
        notifier = PlatformMatchingAdminNotifier(sender, "admin@example.com")

        notifier.notify_manual_matches([])
        notifier.notify_manual_matches([
            {
                "game_name": "Sports",
                "imported_platform": "Wii",
                "matched_platform": "Switch",
                "score": 33,
            }
        ])

        self.assertEqual(1, len(sender.sent_emails))
        self.assertEqual("admin@example.com", sender.sent_emails[0]["recipient_email"])
        self.assertIn("Sports", sender.sent_emails[0]["body"])
        self.assertIn("Switch", sender.sent_emails[0]["body"])


if __name__ == "__main__":
    unittest.main()
