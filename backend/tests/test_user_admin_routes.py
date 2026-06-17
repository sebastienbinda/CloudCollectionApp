#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-24
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests des routes d'administration utilisateur.

try:
    from tests.route_test_support import BaseAppRoutesTest, FakeEmailSender
except ModuleNotFoundError:
    from route_test_support import BaseAppRoutesTest, FakeEmailSender


class UserAdministrationRoutesTest(BaseAppRoutesTest):
    """Valide les routes d'administration utilisateur."""

    def test_user_search_route_requires_authentication_and_admin_profile(self):
        """Verifie les protections de recherche utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 403.
        """

        self.assertEqual(403, self.client.get("/api/users").status_code)
        self.assertEqual(403, self.client.get("/api/users", headers=self.get_auth_headers()).status_code)

    def test_user_search_route_filters_users(self):
        """Verifie les filtres de recherche utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        response = self.client.get("/api/users?name=user&creation_date_from=2026-05-01T00:00:00&last_connexion_date_to=2026-05-23T00:00:00&status=ACTIVE", headers=self.get_admin_auth_headers())
        user = response.get_json()["users"][0]

        self.assertEqual(200, response.status_code)
        self.assertEqual("user@example.com", user["email"])
        self.assertNotIn("password_hash", user)

    def test_user_search_route_rejects_invalid_filters(self):
        """Verifie le refus des filtres invalides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 400.
        """

        self.assertEqual(400, self.client.get("/api/users?status=DISABLED", headers=self.get_admin_auth_headers()).status_code)
        self.assertEqual(400, self.client.get("/api/users?creation_date_from=bad", headers=self.get_admin_auth_headers()).status_code)

    def test_user_delete_lock_unlock_routes(self):
        """Verifie suppression, blocage et deblocage.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les statuts.
        """

        headers = self.get_admin_auth_headers()

        self.assertEqual(204, self.client.delete("/api/users/7", headers=headers).status_code)
        self.assertEqual(404, self.client.delete("/api/users/404", headers=headers).status_code)
        self.assertEqual("LOCKED", self.client.post("/api/users/7/lock", headers=headers).get_json()["user"]["status"])
        self.assertEqual(404, self.client.post("/api/users/404/lock", headers=headers).status_code)
        self.assertEqual("ACTIVE", self.client.post("/api/users/7/unlock", headers=headers).get_json()["user"]["status"])
        self.assertEqual(404, self.client.post("/api/users/404/unlock", headers=headers).status_code)

    def test_user_validate_route_activates_user_and_sends_email(self):
        """Verifie la validation administrateur d'un nouvel utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut et l'email.
        """

        headers = self.get_admin_auth_headers()

        response = self.client.post("/api/users/9/validate", headers=headers)

        self.assertEqual(200, response.status_code)
        self.assertEqual("ACTIVE", response.get_json()["user"]["status"])
        self.assertEqual("waiting@example.com", FakeEmailSender.sent_emails[0]["recipient_email"])
        self.assertIn("valide par un administrateur", FakeEmailSender.sent_emails[0]["body"])
        self.assertIn("/auth?email=waiting%40example.com", FakeEmailSender.sent_emails[0]["body"])
        self.assertEqual(404, self.client.post("/api/users/404/validate", headers=headers).status_code)
