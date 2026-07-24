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

from services.collection.imports import CollectionImportWarnings
from services.database import PlatformMatchingAdminNotifier
from tests.support.fake_platform_matching_email_sender import FakePlatformMatchingEmailSender


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

    def test_notify_import_report_sends_platform_mappings_and_warnings(self):
        """Verifie le rapport complet de fin d'import.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contenu du mail.
        """

        sender = FakePlatformMatchingEmailSender()
        notifier = PlatformMatchingAdminNotifier(sender, "admin@example.com")
        warnings = CollectionImportWarnings(
            invalid_wishlist=1,
            invalid_wishlist_values_found=["Peut etre"],
            invalid_games=[{"name": "Chrono"}],
            total_import_duration_seconds=1.234,
            platform_mappings=[
                {
                    "imported_platform": "Super Famicom",
                    "matched_platform": "Super Nintendo",
                    "score": 100,
                    "games_count": 3,
                    "matched_by_alias": True,
                    "matched_alias": "Super Famicom",
                    "accepted": True,
                    "manual_check": False,
                    "reason": "",
                }
            ],
            platform_matches=[],
            skipped_games=[
                {
                    "game_name": "Unknown Game",
                    "imported_platform": "Unknown",
                    "score": 0,
                    "reason": "no_match",
                }
            ],
        )

        notifier.notify_import_report(warnings)

        self.assertEqual(1, len(sender.sent_emails))
        body = sender.sent_emails[0]["body"]
        self.assertIn("Super Nintendo", body)
        self.assertIn("Jeux: 3", body)
        self.assertIn("Duree totale de l'import: 1.234 seconde(s).", body)
        self.assertIn("Alias: oui (Super Famicom)", body)
        self.assertIn("Unknown Game", body)
        self.assertIn("Chrono", body)
        self.assertIn("Peut etre", body)


if __name__ == "__main__":
    unittest.main()
