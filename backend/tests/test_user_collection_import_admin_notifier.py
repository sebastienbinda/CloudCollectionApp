#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-16
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du rapport email administrateur apres import utilisateur.

import unittest

from services.collection.imports import CollectionImportWarnings
from services.users import UserCollectionImportAdminNotifier, UserCollectionImportReportContext
from tests.fake_platform_matching_email_sender import FakePlatformMatchingEmailSender


class UserCollectionImportAdminNotifierTest(unittest.TestCase):
    """Valide l'email administrateur de fin d'import utilisateur."""

    def test_notify_import_report_sends_email_without_warning(self):
        """Verifie que le rapport est envoye meme sans warning.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contenu du mail.
        """

        sender = FakePlatformMatchingEmailSender()
        notifier = UserCollectionImportAdminNotifier(sender, "admin@example.com")

        notifier.notify_import_report(self._context(CollectionImportWarnings()))

        self.assertEqual(1, len(sender.sent_emails))
        body = sender.sent_emails[0]["body"]
        self.assertIn("Utilisateur: 7", body)
        self.assertIn("Type de fichier: libreoffice_ods", body)
        self.assertIn("Jeux associes: 4", body)
        self.assertIn("Warnings: aucun warning detecte.", body)

    def test_notify_import_report_sends_all_warning_sections(self):
        """Verifie l'envoi des informations de warnings dans le rapport.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les sections du mail.
        """

        sender = FakePlatformMatchingEmailSender()
        notifier = UserCollectionImportAdminNotifier(sender, "admin@example.com")
        warnings = CollectionImportWarnings(
            invalid_wishlist=1,
            invalid_wishlist_values_found=["Peut etre"],
            invalid_games=[{"name": "Chrono"}],
            total_import_duration_seconds=1.234,
            platform_mappings=[
                {
                    "imported_platform": "Super Nintendo",
                    "matched_platform": "Super Nintendo Entertainment System / Super Famicom",
                    "score": 100,
                    "games_count": 3,
                    "matched_by_alias": True,
                    "matched_alias": "Super Nintendo",
                    "accepted": True,
                    "manual_check": False,
                    "reason": "",
                }
            ],
            platform_matches=[
                {
                    "game_name": "Sports",
                    "imported_platform": "Wii",
                    "matched_platform": "Nintendo Wii",
                    "score": 44,
                }
            ],
            skipped_games=[
                {
                    "game_name": "Unknown Game",
                    "imported_platform": "Unknown",
                    "score": 0,
                    "reason": "no_match",
                }
            ],
        )

        notifier.notify_import_report(self._context(warnings))

        body = sender.sent_emails[0]["body"]
        self.assertIn("Duree totale de l'import: 1.234 seconde(s).", body)
        self.assertIn("Super Nintendo", body)
        self.assertIn("Alias: oui (Super Nintendo)", body)
        self.assertIn("Sports", body)
        self.assertIn("Unknown Game", body)
        self.assertIn("Chrono", body)
        self.assertIn("Peut etre", body)

    def _context(self, warnings):
        return UserCollectionImportReportContext(
            user_id=7,
            file_type="libreoffice_ods",
            original_filename="collection.ods",
            source_mode="temporary_upload",
            copied_to_workspace=True,
            linked_platforms=1,
            created_studios=2,
            created_games=3,
            associated_games=4,
            wishlisted_games=1,
            warnings=warnings,
            collection_file_description={"file_type": "libreoffice_ods"},
        )


if __name__ == "__main__":
    unittest.main()
