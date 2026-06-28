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
from types import SimpleNamespace

from services.auth import CollectionShareUnavailableError, UserProfile

try:
    from tests.support.route_test_support import BaseAppRoutesTest
except ModuleNotFoundError:
    from tests.support.route_test_support import BaseAppRoutesTest


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

    def test_collection_share_exchange_route_is_public(self):
        """Verifie l'echange public d'un lien contre une session GUEST.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat HTTP public.
        """

        original_service = (
            app_module.authentication_controller.collection_share_authentication_service
        )
        app_module.authentication_controller.collection_share_authentication_service = (
            SimpleNamespace(exchange_share_link_token=lambda token: {
                "access_token": f"guest-session-for-{token}",
                "token_type": "Bearer",
                "expires_in": 3600,
            })
        )
        try:
            response = self.client.post(
                "/api/auth/collection-share/session",
                json={"token": "share-link"},
            )
        finally:
            app_module.authentication_controller.collection_share_authentication_service = (
                original_service
            )

        self.assertEqual(200, response.status_code)
        self.assertEqual("guest-session-for-share-link", response.get_json()["access_token"])

    def test_collection_share_exchange_returns_411_when_unavailable(self):
        """Verifie le statut specifique d'un partage expire ou revoque.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut et le code metier.
        """

        def reject_exchange(_token):
            raise CollectionShareUnavailableError("indisponible")

        original_service = (
            app_module.authentication_controller.collection_share_authentication_service
        )
        app_module.authentication_controller.collection_share_authentication_service = (
            SimpleNamespace(exchange_share_link_token=reject_exchange)
        )
        try:
            response = self.client.post(
                "/api/auth/collection-share/session",
                json={"token": "expired-link"},
            )
        finally:
            app_module.authentication_controller.collection_share_authentication_service = (
                original_service
            )

        self.assertEqual(411, response.status_code)
        self.assertEqual(
            "COLLECTION_SHARE_UNAVAILABLE",
            response.get_json()["error_code"],
        )

    def test_guest_can_read_route_catalog_with_explicit_profile_metadata(self):
        """Verifie l'acces GUEST au catalogue de routes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'acces et les profils annonces.
        """

        token = app_module.auth_token_service.create_access_token(
            "guest-share:8",
            UserProfile.GUEST.value,
            expires_at=4102444800,
            additional_claims={"collection_share_id": 8, "owner_user_id": 7},
        )
        original_validator = app_module.auth_guard.guest_session_validator
        app_module.auth_guard.guest_session_validator = SimpleNamespace(
            validate_guest_session=lambda payload: None,
        )
        try:
            response = self.client.get(
                "/api/routes",
                headers={"Authorization": f"Bearer {token}"},
            )
        finally:
            app_module.auth_guard.guest_session_validator = original_validator

        self.assertEqual(200, response.status_code)
        route = next(
            item for item in response.get_json()["routes"]
            if item["endpoint"] == "list_accessible_routes"
        )
        self.assertEqual(["GUEST", "USER", "ADMIN"], route["required_profiles"])

    def test_expired_guest_session_returns_411(self):
        """Verifie le statut 411 pour une session GUEST expiree.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'invalidation specifique.
        """

        token = app_module.auth_token_service.create_access_token(
            "guest-share:8",
            UserProfile.GUEST.value,
            expires_at=1,
            additional_claims={"collection_share_id": 8, "owner_user_id": 7},
        )

        response = self.client.get(
            "/api/routes",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(411, response.status_code)
        self.assertEqual("COLLECTION_SHARE_UNAVAILABLE", response.get_json()["error_code"])

    def test_expired_user_session_keeps_standard_401(self):
        """Verifie la non-regression du statut des sessions USER expirees.

        Args:
            Aucun.

        Returns:
            None: L'assertion valide le contrat HTTP existant.
        """

        token = app_module.auth_token_service.create_access_token(
            "user@example.com",
            UserProfile.USER.value,
            expires_at=1,
        )

        response = self.client.get(
            "/api/routes",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(401, response.status_code)

    def test_revoked_guest_session_returns_411_on_next_request(self):
        """Verifie la revalidation serveur de chaque session GUEST.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'invalidation au prochain appel.
        """

        def reject_guest(_payload):
            raise CollectionShareUnavailableError("revoque")

        token = app_module.auth_token_service.create_access_token(
            "guest-share:8",
            UserProfile.GUEST.value,
            expires_at=4102444800,
            additional_claims={"collection_share_id": 8, "owner_user_id": 7},
        )
        original_validator = app_module.auth_guard.guest_session_validator
        app_module.auth_guard.guest_session_validator = SimpleNamespace(
            validate_guest_session=reject_guest,
        )
        try:
            response = self.client.get(
                "/api/routes",
                headers={"Authorization": f"Bearer {token}"},
            )
        finally:
            app_module.auth_guard.guest_session_validator = original_validator

        self.assertEqual(411, response.status_code)

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
        self.assertEqual("Player_One", payload["display_name"])
        self.assertEqual(UserProfile.USER.value, payload["profile"])

    def test_register_user_route_returns_public_user(self):
        """Verifie la creation publique d'un utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload public.
        """

        response = self.client.post(
            "/api/auth/register",
            json={
                "email": " USER@Example.COM ",
                "pseudonym": "Player_One",
                "password": "VeryStrongPassword123!",
            },
        )
        user = response.get_json()["user"]

        self.assertEqual(201, response.status_code)
        self.assertEqual("user@example.com", user["email"])
        self.assertEqual("Player_One", user["pseudonym"])
        self.assertFalse(user["is_email_verified"])
        self.assertNotIn("password_hash", user)

    def test_register_user_route_rejects_duplicate_email(self):
        """Verifie le refus d'un email deja utilise.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut 409.
        """

        response = self.client.post(
            "/api/auth/register",
            json={
                "email": "duplicate@example.com",
                "pseudonym": "Player_One",
                "password": "VeryStrongPassword123!",
            },
        )

        self.assertEqual(409, response.status_code)

    def test_register_user_route_rejects_duplicate_pseudonym(self):
        """Verifie le refus d'un pseudonyme deja utilise.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut 409.
        """

        response = self.client.post(
            "/api/auth/register",
            json={
                "email": "other@example.com",
                "pseudonym": "Reserved",
                "password": "VeryStrongPassword123!",
            },
        )

        self.assertEqual(409, response.status_code)
        self.assertIn("pseudonyme", response.get_json()["error"])

    def test_register_user_route_rejects_invalid_payload(self):
        """Verifie le refus d'un mot de passe invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le message.
        """

        response = self.client.post(
            "/api/auth/register",
            json={"email": "user@example.com", "pseudonym": "Player_One", "password": "short"},
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("8 caracteres", response.get_json()["error"])

    def test_pseudonym_availability_route_is_public_and_case_insensitive(self):
        """Verifie la disponibilite publique des pseudonymes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les reponses sans token.
        """

        available_response = self.client.get(
            "/api/auth/pseudonym-availability?pseudonym=Player_One"
        )
        unavailable_response = self.client.get(
            "/api/auth/pseudonym-availability?pseudonym=Reserved"
        )

        self.assertEqual(200, available_response.status_code)
        self.assertTrue(available_response.get_json()["available"])
        self.assertEqual(200, unavailable_response.status_code)
        self.assertFalse(unavailable_response.get_json()["available"])

    def test_pseudonym_availability_route_rejects_invalid_format(self):
        """Verifie le refus public d'un pseudonyme invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut HTTP 400.
        """

        response = self.client.get("/api/auth/pseudonym-availability?pseudonym=ab")

        self.assertEqual(400, response.status_code)

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
