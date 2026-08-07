#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-08-07
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de notification administrateur des echecs d'import.

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.collection.imports import (  # noqa: E402
    CollectionImportFailureAdminNotifier,
    CollectionImportFailureContext,
)
from tests.support.fake_platform_matching_email_sender import (  # noqa: E402
    FakePlatformMatchingEmailSender,
)


class CollectionImportFailureAdminNotifierTest(unittest.TestCase):
    """Valide l'email administrateur des echecs d'import."""

    def test_notify_import_failure_uses_backend_resource_template(self):
        """Verifie le rendu HTML depuis le template de ressources.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'email rendu.
        """

        sender = FakePlatformMatchingEmailSender()
        notifier = CollectionImportFailureAdminNotifier(sender, "admin@example.com")

        notifier.notify_import_failure(
            CollectionImportFailureContext(
                import_kind="bibliotheque_admin_csv",
                initiated_by_function="AdminLibraryImportService.import_csv_file",
                failing_function="studio_matching_service.py:_studio_matching_score",
                requester_user_id=None,
                requester_email="admin@example.com",
                file_type="csv",
                original_filename="admin <import>.csv",
                error_type="RuntimeError",
                error_message="db <down>",
                traceback_text="Traceback <secret>",
            )
        )

        self.assertEqual(1, len(sender.sent_emails))
        email = sender.sent_emails[0]
        self.assertEqual("admin@example.com", email["recipient_email"])
        self.assertEqual("Echec d'import - bibliotheque_admin_csv", email["subject"])
        self.assertEqual("html", email["content_subtype"])
        self.assertIn("<h1>Echec d'import</h1>", email["body"])
        self.assertIn("AdminLibraryImportService.import_csv_file", email["body"])
        self.assertIn("admin &lt;import&gt;.csv", email["body"])
        self.assertIn("RuntimeError: db &lt;down&gt;", email["body"])
        self.assertIn("Traceback &lt;secret&gt;", email["body"])

    def test_default_template_path_targets_backend_resource(self):
        """Verifie le nom du template par defaut.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la ressource utilisee.
        """

        template_path = CollectionImportFailureAdminNotifier.default_template_path()

        self.assertEqual("collection_import_failure_email_template.txt", template_path.name)
        self.assertTrue(template_path.exists())


if __name__ == "__main__":
    unittest.main()
