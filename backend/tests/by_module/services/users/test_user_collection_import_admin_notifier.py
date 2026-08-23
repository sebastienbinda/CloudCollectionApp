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
        self.assertNotIn("<h2>Warnings</h2>", body)
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
            skipped_mandatory_games=1,
        )

        notifier.notify_import_report(self._context(warnings))

        body = sender.sent_emails[0]["body"]
        self.assertIn("<h2>Compteurs d'erreur</h2>", body)
        self.assertLess(
            body.index("<h2>Compteurs d'erreur</h2>"),
            body.index("<h2>Plateformes à valider par l'admin</h2>"),
        )
        self.assertLess(
            body.index("<h2>Plateformes à valider par l'admin</h2>"),
            body.index("<h2>Studios importes</h2>"),
        )
        self.assertIn("Jeux avec erreur bloquante", body)
        self.assertIn("Jeux lus dans le fichier", body)
        self.assertIn("Jeux avec information invalide", body)
        self.assertIn("Jeux refuses ou ignores", body)
        self.assertIn("Lignes sans nom ou plateforme obligatoire", body)
        self.assertIn("Jeux avec plateforme a valider", body)
        self.assertIn("Non bloquant: validation admin attendue.", body)
        self.assertIn("Lignes wishlist ignorees", body)
        self.assertIn("Duree totale de l'import: 1.234 seconde(s).", body)
        self.assertIn("Lecture du fichier: 0.120 seconde(s).", body)
        self.assertIn("Calcul des associations: 0.340 seconde(s).", body)
        self.assertIn("Requetes base de donnees: 0.560 seconde(s).", body)
        self.assertIn("<h2>Plateformes à valider par l'admin</h2>", body)
        self.assertIn("Valeur dans le fichier", body)
        self.assertIn("Plateforme proposée", body)
        self.assertIn("background:#fff7ed", body)
        self.assertIn("Wii", body)
        self.assertIn("Nintendo Wii", body)
        self.assertIn("En attente de validation", body)
        self.assertIn("Sports", body)
        self.assertNotIn("<h2>Warnings</h2>", body)

    def test_notify_import_report_groups_manual_platform_values(self):
        """Verifie le mapping des valeurs plateformes a valider dans le mail.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la synthese admin.
        """

        sender = FakePlatformMatchingEmailSender()
        notifier = UserCollectionImportAdminNotifier(sender, "admin@example.com")
        warnings = CollectionImportWarnings(
            platform_matches=[
                {
                    "game_name": "Legend of dragoon",
                    "imported_platform": "La Playstation de la mort",
                    "matched_platform": "PlayStation Portable",
                    "score": 50,
                },
                {
                    "game_name": "Loaded",
                    "imported_platform": "La Playstation de la mort",
                    "matched_platform": "PlayStation Portable",
                    "score": 50,
                },
            ],
        )

        notifier.notify_import_report(self._context(warnings))

        body = sender.sent_emails[0]["body"]
        self.assertIn("<h2>Plateformes à valider par l'admin</h2>", body)
        self.assertIn("background:#fff7ed", body)
        self.assertIn("La Playstation de la mort", body)
        self.assertIn("PlayStation Portable", body)
        self.assertIn("Legend of dragoon, Loaded", body)
        self.assertIn("En attente de validation", body)
        self.assertIn("Legend of dragoon", body)
        self.assertIn("Loaded", body)
        self.assertNotIn("<h2>Warnings</h2>", body)

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
                    ImportedGameMatchReport(
                        "Unknown",
                        False,
                        "",
                        12,
                        "valeur à vérifier",
                        "below_threshold",
                        "Score insuffisant.",
                    ),
                ),
            )
        )

        body = sender.sent_emails[0]["body"]
        self.assertIn("background:#ecfdf3", body)
        self.assertIn("background:#dcfce7", body)
        self.assertIn("Zelda &lt;DX&gt;", body)
        self.assertIn('<strong style="color:#166534;">Oui</strong>', body)
        self.assertIn("&nbsp;", body)
        self.assertIn("33", body)
        self.assertIn("fuzzy_similarity", body)
        self.assertIn("Mario Kart 8 Deluxe", body)
        self.assertIn("exact_normalized_key", body)
        self.assertIn("background:#fef2f2", body)
        self.assertIn("background:#fee2e2", body)
        self.assertIn('<strong style="color:#991b1b;">valeur à vérifier</strong>', body)

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
        self.assertIn("Nom du studio importé", body)
        self.assertIn("Créé", body)
        self.assertIn("Nom du Studio associé", body)
        self.assertIn("Score de matching", body)
        self.assertIn("background:#ecfdf3", body)
        self.assertIn("background:#dcfce7", body)
        self.assertIn("Acclaim &lt;Import&gt;", body)
        self.assertIn('<span style="color:#475569;">Non</span>', body)
        self.assertIn("Acclaim Studios", body)
        self.assertIn("100", body)
        self.assertIn("Rare", body)
        self.assertIn('<strong style="color:#166534;">Oui</strong>', body)
        self.assertIn("22", body)

    def test_notify_import_report_formats_configuration_json(self):
        """Verifie que la configuration JSON du mail est coloree et indentee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le rendu HTML lisible du JSON.
        """

        sender = FakePlatformMatchingEmailSender()
        notifier = UserCollectionImportAdminNotifier(sender, "admin@example.com")

        notifier.notify_import_report(
            self._context(
                CollectionImportWarnings(),
                collection_file_description={
                    "file_type": "libreoffice_ods",
                    "first_data_row": 2,
                    "columns": {"name": "Jeu <Nom>", "wishlist": True},
                },
            )
        )

        body = sender.sent_emails[0]["body"]
        self.assertIn(
            '<pre style="background:#f8fafc;border:1px solid #d9e2ec;',
            body,
        )
        self.assertIn('\n  <span style="color:#0f5e9c;font-weight:600;">', body)
        self.assertIn('&quot;columns&quot;:', body)
        self.assertIn('&quot;Jeu &lt;Nom&gt;&quot;', body)
        self.assertIn(
            '<span style="color:#7c3aed;font-weight:600;">2</span>',
            body,
        )
        self.assertIn(
            '<span style="color:#8a4f00;font-weight:600;">true</span>',
            body,
        )

    def _context(
        self,
        warnings,
        created_game_match_reports=(),
        imported_game_match_reports=(),
        imported_studio_match_reports=(),
        collection_file_description=None,
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
            collection_file_description=collection_file_description
            or {"file_type": "libreoffice_ods"},
            created_game_match_reports=created_game_match_reports,
            imported_game_match_reports=imported_game_match_reports,
            imported_studio_match_reports=imported_studio_match_reports,
            file_read_duration_seconds=0.12,
            association_calculation_duration_seconds=0.34,
            database_query_duration_seconds=0.56,
        )


if __name__ == "__main__":
    unittest.main()
