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
# Description : tests des routes publiques d'authentification.

import app as app_module
from services.auth import UserProfile

try:
    from tests.route_test_support import BaseAppRoutesTest
except ModuleNotFoundError:
    from route_test_support import BaseAppRoutesTest


class AuthenticationRoutesTest(BaseAppRoutesTest):
    """Valide les routes d'authentification, inscription et email."""

    def test_auth_token_route_returns_bearer_token(self):
        """Verifie la generation d'un token administrateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le token.
        """

        response = self.client.post("/auth/token", json={"username": "admin", "password": "change-me"})
        data = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertEqual("Bearer", data["token_type"])
        self.assertEqual(UserProfile.ADMIN.value, app_module.auth_token_service.validate_access_token(data["access_token"])["profile"])

    def test_auth_token_route_rejects_invalid_credentials(self):
        """Verifie le refus d'identifiants invalides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut HTTP.
        """

        response = self.client.post("/auth/token", json={"username": "admin", "password": "bad"})

        self.assertEqual(401, response.status_code)
        self.assertIn("invalides", response.get_json()["error"])

    def test_auth_token_route_accepts_verified_registered_user(self):
        """Verifie le token d'un utilisateur inscrit et verifie.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le sujet du token.
        """

        response = self.client.post("/auth/token", json={"username": "USER@Example.COM", "password": "VeryStrongPassword123!"})
        data = response.get_json()
        payload = app_module.auth_token_service.validate_access_token(data["access_token"])

        self.assertEqual(200, response.status_code)
        self.assertEqual("user@example.com", payload["sub"])
        self.assertEqual(UserProfile.USER.value, payload["profile"])

    def test_register_user_route_returns_public_user(self):
        """Verifie la creation publique d'un utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload public.
        """

        response = self.client.post("/api/auth/register", json={"email": " USER@Example.COM ", "password": "VeryStrongPassword123!"})
        user = response.get_json()["user"]

        self.assertEqual(201, response.status_code)
        self.assertEqual("user@example.com", user["email"])
        self.assertFalse(user["is_email_verified"])
        self.assertNotIn("password_hash", user)

    def test_register_user_route_rejects_duplicate_email(self):
        """Verifie le refus d'un email deja utilise.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut 409.
        """

        response = self.client.post("/api/auth/register", json={"email": "duplicate@example.com", "password": "VeryStrongPassword123!"})

        self.assertEqual(409, response.status_code)

    def test_register_user_route_rejects_invalid_payload(self):
        """Verifie le refus d'un mot de passe invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le message.
        """

        response = self.client.post("/api/auth/register", json={"email": "user@example.com", "password": "short"})

        self.assertEqual(400, response.status_code)
        self.assertIn("8 caracteres", response.get_json()["error"])

    def test_verify_email_route_returns_html_success(self):
        """Verifie la validation email via lien navigateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le HTML.
        """

        response = self.client.get("/api/auth/verify-email?token=valid-token")

        self.assertEqual(303, response.status_code)
        self.assertIn("/auth/verify-email?status=waiting_admin", response.headers["Location"])

    def test_verify_email_route_post_returns_verified_user_json(self):
        """Verifie la validation email JSON.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        response = self.client.post("/api/auth/verify-email", json={"token": "valid-token"})

        self.assertEqual(200, response.status_code)
        self.assertEqual("user@example.com", response.get_json()["user"]["email"])
        self.assertEqual("WAITING_VALIDATION", response.get_json()["user"]["status"])

    def test_verify_email_route_rejects_invalid_or_missing_token(self):
        """Verifie les refus de validation email.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les statuts 400.
        """

        response = self.client.get("/api/auth/verify-email")

        self.assertEqual(303, response.status_code)
        self.assertIn("/auth/verify-email?status=invalid", response.headers["Location"])
        self.assertEqual(400, self.client.post("/api/auth/verify-email", json={"token": "invalid-token"}).status_code)
