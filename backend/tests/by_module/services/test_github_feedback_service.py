#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du service de retours beta GitHub.

import unittest

from services.feedback import GitHubFeedbackConfiguration, GitHubFeedbackService


class GitHubFeedbackServiceTest(unittest.TestCase):
    """Valide la creation d'issues GitHub depuis les retours utilisateur."""

    def test_submit_feedback_creates_issue_payload(self):
        """Verifie le payload transmis a GitHub.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le titre et le corps.
        """

        calls = []

        def fake_post(url, payload, token):
            calls.append((url, payload, token))
            return {"number": 42, "html_url": "https://github.com/acme/app/issues/42"}

        service = GitHubFeedbackService(
            GitHubFeedbackConfiguration("acme/app", "token", ("feedback",), "[Beta]"),
            http_post=fake_post,
        )

        result = service.submit_feedback(
            {
                "category": "bug",
                "title": "Le bouton ne reagit pas",
                "message": "Le bouton de partage ne reagit pas sur mobile.",
                "page_url": "http://localhost/about",
                "user_agent": "Firefox",
            },
            "user@example.com",
        )

        self.assertEqual(42, result["issue_number"])
        self.assertEqual("https://github.com/acme/app/issues/42", result["issue_url"])
        self.assertEqual("https://api.github.com/repos/acme/app/issues", calls[0][0])
        self.assertEqual("token", calls[0][2])
        self.assertEqual("[Beta] Bug - Le bouton ne reagit pas", calls[0][1]["title"])
        self.assertIn("user@example.com", calls[0][1]["body"])
        self.assertEqual(["feedback"], calls[0][1]["labels"])

    def test_submit_feedback_rejects_short_message(self):
        """Verifie la validation de la taille minimale du message.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = GitHubFeedbackService(
            GitHubFeedbackConfiguration("acme/app", "token", ("feedback",), "[Beta]"),
            http_post=lambda url, payload, token: {},
        )

        with self.assertRaises(ValueError):
            service.submit_feedback({"category": "bug", "message": "Court"}, "user@example.com")


if __name__ == "__main__":
    unittest.main()
