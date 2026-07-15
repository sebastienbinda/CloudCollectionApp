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
from pathlib import Path

from services.collection.imports import CollectionImportWarnings
from services.database import (
    CreatedGameMatchReport,
    ImportedGameMatchReport,
    ImportedStudioMatchReport,
)
from services.users import UserCollectionImportAdminNotifier, UserCollectionImportReportContext
from tests.support.fake_platform_matching_email_sender import FakePlatformMatchingEmailSender


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
        self.assertIn("Email utilisateur: importer@example.com", body)
        self.assertIn("Type de fichier: libreoffice_ods", body)
        self.assertIn("Jeux associes: 4", body)
        self.assertIn("Aucun studio importe.", body)
        self.assertIn("Aucun jeu importe.", body)
        self.assertIn("Warnings: aucun warning detecte.", body)
        self.assertEqual("html", sender.sent_emails[0]["content_subtype"])

    def test_notify_import_report_uses_backend_resource_template(self):
        """Verifie que le rapport utilise le template texte des ressources backend.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le chemin et le rendu du template.
        """

        sender = FakePlatformMatchingEmailSender()
        template_path = UserCollectionImportAdminNotifier.default_template_path()
        notifier = UserCollectionImportAdminNotifier(sender, "admin@example.com")

        notifier.notify_import_report(self._context(CollectionImportWarnings()))

        self.assertEqual(Path("backend/resources"), Path(*template_path.parts[-3:-1]))
        self.assertTrue(template_path.exists())
        self.assertIn(
            template_path.read_text(encoding="utf-8").splitlines()[0],
            sender.sent_emails[0]["body"],
        )

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

    def test_notify_import_report_sends_imported_game_match_reports_table(self):
        """Verifie le tableau HTML de diagnostic des jeux importes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la section du mail.
        """

        sender = FakePlatformMatchingEmailSender()
        notifier = UserCollectionImportAdminNotifier(sender, "admin@example.com")

        notifier.notify_import_report(
            self._context(
                CollectionImportWarnings(),
                created_game_match_reports=(
                    CreatedGameMatchReport("Zelda", "Switch", "Mario Kart", 33),
                    CreatedGameMatchReport("Chrono", "SNES", "", 0),
                ),
                imported_game_match_reports=(
                    ImportedGameMatchReport(
                        "Zelda <DX>",
                        True,
                        "",
                        33,
                        "scored",
                        "fuzzy_similarity",
                        "Score de similarite textuelle generique.",
                    ),
                    ImportedGameMatchReport(
                        "Mario Kart",
                        False,
                        "Mario Kart 8 Deluxe",
                        100,
                        "accepted",
                        "exact_normalized_key",
                        "Cle plateforme/jeu normalisee deja presente.",
                    ),
                ),
            )
        )

        body = sender.sent_emails[0]["body"]
        self.assertIn("<td>Zelda &lt;DX&gt;</td>", body)
        self.assertIn("<td>Oui</td>", body)
        self.assertIn("<td>&nbsp;</td>", body)
        self.assertIn("<td>33</td>", body)
        self.assertIn("<td>fuzzy_similarity</td>", body)
        self.assertIn("<td>Mario Kart 8 Deluxe</td>", body)
        self.assertIn("<td>exact_normalized_key</td>", body)

    def test_notify_import_report_sends_imported_studio_match_reports_table(self):
        """Verifie le tableau HTML de diagnostic des studios importes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la section du mail.
        """

        sender = FakePlatformMatchingEmailSender()
        notifier = UserCollectionImportAdminNotifier(sender, "admin@example.com")

        notifier.notify_import_report(
            self._context(
                CollectionImportWarnings(),
                imported_studio_match_reports=(
                    ImportedStudioMatchReport("Acclaim <Import>", False, "Acclaim Studios", 100),
                    ImportedStudioMatchReport("Rare", True, "", 22),
                ),
            )
        )

        body = sender.sent_emails[0]["body"]
        self.assertIn("<th>Nom du studio importé</th>", body)
        self.assertIn("<th>Créé</th>", body)
        self.assertIn("<th>Nom du Studio associé</th>", body)
        self.assertIn("<th>Score de matching</th>", body)
        self.assertIn("<td>Acclaim &lt;Import&gt;</td>", body)
        self.assertIn("<td>Non</td>", body)
        self.assertIn("<td>Acclaim Studios</td>", body)
        self.assertIn("<td>100</td>", body)
        self.assertIn("<td>Rare</td>", body)
        self.assertIn("<td>Oui</td>", body)
        self.assertIn("<td>22</td>", body)

    def _context(
        self,
        warnings,
        created_game_match_reports=(),
        imported_game_match_reports=(),
        imported_studio_match_reports=(),
    ):
        return UserCollectionImportReportContext(
            user_id=7,
            user_email="importer@example.com",
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
            created_game_match_reports=created_game_match_reports,
            imported_game_match_reports=imported_game_match_reports,
            imported_studio_match_reports=imported_studio_match_reports,
        )


if __name__ == "__main__":
    unittest.main()
