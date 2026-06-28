#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/|_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests des notifications utilisateur apres fusion de doublon.

import unittest
from pathlib import Path

from services.database.game_duplicate_repository import SqlAlchemyGameDuplicateRepository
from services.library import GameDuplicateUserNotifier
from tests.support.fake_platform_matching_email_sender import FakePlatformMatchingEmailSender


class FakeSqlConnection:
    """Connexion SQL factice pour les utilisateurs impactes."""

    def __init__(self):
        """Initialise la connexion factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.executed_statements = []

    def execute(self, statement, parameters=None):
        """Capture la requete executee.

        Args:
            statement (object): Requete SQLAlchemy.
            parameters (dict | None): Parametres SQL.

        Returns:
            FakeMappingResult: Resultat factice.
        """

        self.executed_statements.append((str(statement), parameters))
        return FakeMappingResult()


class FakeMappingResult:
    """Resultat SQL factice exposant des mappings."""

    def mappings(self):
        """Retourne des lignes de mappings factices.

        Args:
            Aucun.

        Returns:
            list[dict]: Lignes utilisateur factices.
        """

        return [
            {
                "user_id": 7,
                "user_email": "user@example.com",
                "had_target_game": True,
            }
        ]


class GameDuplicateUserNotifierTest(unittest.TestCase):
    """Valide les emails envoyes aux utilisateurs impactes par une fusion."""

    def test_notify_merge_sends_templated_email_to_impacted_user(self):
        """Verifie le rendu du mail utilisateur apres fusion.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le mail.
        """

        sender = FakePlatformMatchingEmailSender()
        notifier = GameDuplicateUserNotifier(
            email_sender=sender,
            site_url="https://app.example.com/",
        )

        sent_count = notifier.notify_merge(
            [{"user_email": "user@example.com", "had_target_game": True}],
            {"id": 12, "name": "Sonic the edgedog", "platform_name": "Mega Drive"},
            {"id": 8, "name": "Sonic", "platform_name": "Mega Drive"},
        )

        self.assertEqual(1, sent_count)
        self.assertEqual(1, len(sender.sent_emails))
        body = sender.sent_emails[0]["body"]
        self.assertEqual("user@example.com", sender.sent_emails[0]["recipient_email"])
        self.assertEqual("Mise a jour de votre collection", sender.sent_emails[0]["subject"])
        self.assertIn("Sonic the edgedog", body)
        self.assertIn("Sonic", body)
        self.assertIn("Mega Drive", body)
        self.assertIn("fusionnees en une seule entree", body)
        self.assertIn("https://app.example.com/collection/jeux/8", body)

    def test_notify_merge_uses_backend_resource_template(self):
        """Verifie que le notifier utilise le template des ressources backend.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le chemin du template.
        """

        template_path = GameDuplicateUserNotifier.default_template_path()

        self.assertEqual(Path("backend/resources"), Path(*template_path.parts[-3:-1]))
        self.assertTrue(template_path.exists())

    def test_repository_lists_users_impacted_by_merge(self):
        """Verifie la requete SQL des utilisateurs impactes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le SQL et les parametres.
        """

        connection = FakeSqlConnection()
        repository = SqlAlchemyGameDuplicateRepository("collection")

        impacted_users = repository.list_users_impacted_by_merge(connection, 12, 8)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(1, len(impacted_users))
        self.assertEqual("user@example.com", impacted_users[0]["user_email"])
        self.assertIn('FROM "collection".t_user_collection duplicate', sql)
        self.assertIn('JOIN "collection".t_user app_user', sql)
        self.assertIn("EXISTS", sql)
        self.assertEqual({"duplicate_game_id": 12, "target_game_id": 8}, parameters)


if __name__ == "__main__":
    unittest.main()
