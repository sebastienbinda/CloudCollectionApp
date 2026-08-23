#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
# Projet : CloudCollectionApp
# Date de creation : 2026-08-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de notification administrateur des imports refuses.

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.collection.imports import (  # noqa: E402
    CollectionImportData,
    CollectionImportGame,
    CollectionImportPlatform,
    CollectionImportRefusalAdminNotifier,
    CollectionImportRefusalContext,
    CollectionImportWarnings,
)
from tests.support.fake_platform_matching_email_sender import (  # noqa: E402
    FakePlatformMatchingEmailSender,
)


class CollectionImportRefusalAdminNotifierTest(unittest.TestCase):
    """Valide l'email administrateur des imports refuses."""

    def test_notify_import_refusal_uses_backend_resource_template(self):
        """Verifie le rendu HTML depuis le template de ressources.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'email rendu.
        """

        sender = FakePlatformMatchingEmailSender()
        notifier = CollectionImportRefusalAdminNotifier(sender, "admin@example.com")

        notifier.notify_import_refusal(
            CollectionImportRefusalContext(
                import_kind="collection_utilisateur",
                requester_user_id=7,
                requester_email="user@example.com",
                file_type="csv",
                original_filename="collection <bad>.csv",
                refusal={
                    "refused": True,
                    "reason": "too_many_invalid_games",
                    "invalid_games_count": 2,
                    "total_games_count": 3,
                    "message": "Import refuse car 2/3 jeux contiennent une erreur.",
                },
                import_data=CollectionImportData(
                    platforms=[CollectionImportPlatform("Switch")],
                    studios=[],
                    games=[
                        CollectionImportGame("Zelda", "Switch", None, None),
                        CollectionImportGame("Mario", "Switch", None, None),
                        CollectionImportGame("Metroid", "Switch", None, None),
                    ],
                    warnings=CollectionImportWarnings(
                        invalid_games=[
                            {
                                "name": "Zelda <DX>",
                                "invalid_fields": [
                                    {"field": "release_date", "value": "1900-01-01"}
                                ],
                            },
                            {"name": "Mario", "invalid_fields": [{"field": "condition"}]},
                        ],
                        platform_matches=[
                            {
                                "game_name": "Legend of dragoon",
                                "imported_platform": "La Playstation de la mort",
                                "matched_platform": "PlayStation Portable",
                                "score": 50,
                            },
                        ],
                        skipped_games=[
                            {
                                "game_name": "Unknown Game",
                                "imported_platform": "Unknown",
                                "score": 0,
                                "reason": "no_match",
                            },
                        ],
                        skipped_mandatory_games=1,
                        invalid_wishlist=1,
                    ),
                ),
            )
        )

        self.assertEqual(1, len(sender.sent_emails))
        email = sender.sent_emails[0]
        self.assertEqual("admin@example.com", email["recipient_email"])
        self.assertEqual("Import refuse - collection_utilisateur", email["subject"])
        self.assertEqual("html", email["content_subtype"])
        self.assertIn("<h1>Import refuse</h1>", email["body"])
        self.assertIn("collection &lt;bad&gt;.csv", email["body"])
        self.assertIn("too_many_invalid_games", email["body"])
        self.assertIn("2/3", email["body"])
        self.assertIn("<h2>Compteurs d'erreur</h2>", email["body"])
        self.assertIn("Jeux avec erreur bloquante", email["body"])
        self.assertIn("Jeux avec information invalide", email["body"])
        self.assertIn("Jeux refuses ou ignores", email["body"])
        self.assertIn("Lignes sans nom ou plateforme obligatoire", email["body"])
        self.assertIn("Jeux avec plateforme a valider", email["body"])
        self.assertIn("Lignes wishlist ignorees", email["body"])
        self.assertIn("Total utilise pour refuser le fichier.", email["body"])
        self.assertIn("Zelda &lt;DX&gt;", email["body"])
        self.assertIn("release_date: 1900-01-01", email["body"])
        self.assertIn("Plateformes à valider par l'admin", email["body"])
        self.assertIn("La Playstation de la mort", email["body"])
        self.assertIn("PlayStation Portable", email["body"])
        self.assertIn("Legend of dragoon", email["body"])
        self.assertIn("En attente de validation", email["body"])
        self.assertNotIn("<h2>Warnings</h2>", email["body"])
        self.assertNotIn("- Jeux invalides:", email["body"])

    def test_default_template_path_targets_backend_resource(self):
        """Verifie le nom du template par defaut.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la ressource utilisee.
        """

        template_path = CollectionImportRefusalAdminNotifier.default_template_path()

        self.assertEqual("collection_import_refusal_email_template.txt", template_path.name)
        self.assertTrue(template_path.exists())


if __name__ == "__main__":
    unittest.main()
