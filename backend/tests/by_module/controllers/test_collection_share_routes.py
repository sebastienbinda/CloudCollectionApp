#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests HTTP de gestion proprietaire des partages.

from types import SimpleNamespace
import unittest

import app as app_module
from services import UserProfile
from services.collection.collection_share_not_found_error import CollectionShareNotFoundError

try:
    from tests.support.route_test_support import BaseAppRoutesTest
except ModuleNotFoundError:
    from tests.support.route_test_support import BaseAppRoutesTest


class FakeCollectionShareManagementRouteService:
    """Simule le service de gestion appele par le controleur."""

    def __init__(self):
        """Initialise les appels captures.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.calls = []

    def create_share(
        self,
        owner_subject,
        duration_hours,
        allow_collection,
        allow_wishlist,
        allow_prices,
        recipient=None,
        wishlist_buy_status_default_filter="all",
    ):
        """Retourne un partage cree factice.

        Args:
            owner_subject (str): Sujet proprietaire.
            duration_hours (int): Duree recue.
            allow_collection (bool): Permission collection.
            allow_wishlist (bool): Permission wishlist.
            allow_prices (bool): Permission prix.
            recipient (str | None): Destinataire du partage.
            wishlist_buy_status_default_filter (str): Filtre wishlist par defaut.

        Returns:
            dict: Partage serialisable.
        """

        self.calls.append((
            "create",
            owner_subject,
            duration_hours,
            allow_collection,
            allow_wishlist,
            allow_prices,
            recipient,
            wishlist_buy_status_default_filter,
        ))
        if type(duration_hours) is not int:
            raise ValueError("duration_hours invalide.")
        return self._share_payload(4, "ACTIVE")

    def list_shares(self, owner_subject):
        """Retourne une liste factice.

        Args:
            owner_subject (str): Sujet proprietaire.

        Returns:
            list[dict]: Partages factices.
        """

        self.calls.append(("list", owner_subject))
        return [self._share_payload(4, "ACTIVE")]

    def revoke_share(self, owner_subject, share_id):
        """Retourne un partage revoque ou une absence.

        Args:
            owner_subject (str): Sujet proprietaire.
            share_id (int): Identifiant cible.

        Returns:
            dict: Partage revoque.

        Raises:
            CollectionShareNotFoundError: Si l'identifiant vaut 999.
        """

        self.calls.append(("revoke", owner_subject, share_id))
        if share_id == 999:
            raise CollectionShareNotFoundError("Partage introuvable.")
        return self._share_payload(share_id, "REVOKED")

    @staticmethod
    def _share_payload(share_id, status):
        return {
            "id": share_id,
            "created_at": "2030-01-01T10:00:00",
            "expires_at": "2030-01-02T10:00:00",
            "revoked_at": "2030-01-01T11:00:00" if status == "REVOKED" else None,
            "permissions": {"collection": True, "wishlist": False, "prices": True},
            "recipient": "Alice",
            "wishlist_buy_status_default_filter": "all",
            "status": status,
            "link": f"https://collection.example/collection/share/token-{share_id}",
        }


class CollectionShareRoutesTest(BaseAppRoutesTest):
    """Valide les routes protegees de partage de collection."""

    def setUp(self):
        """Installe le service HTTP factice.

        Args:
            Aucun.

        Returns:
            None: Le client et le fake sont prets.
        """

        super().setUp()
        self.original_service = app_module.collection_share_controller.management_service
        self.service = FakeCollectionShareManagementRouteService()
        app_module.collection_share_controller.management_service = self.service

    def tearDown(self):
        """Restaure le service applicatif.

        Args:
            Aucun.

        Returns:
            None: Les dependances globales sont restaurees.
        """

        app_module.collection_share_controller.management_service = self.original_service
        super().tearDown()

    def test_create_share_uses_connected_user_and_returns_201(self):
        """Verifie la creation pour le sujet Bearer.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident appel et reponse.
        """

        response = self.client.post(
            "/api/collection-shares",
            headers=self.get_user_auth_headers(),
            json={
                "duration_hours": 24,
                "allow_collection": True,
                "allow_wishlist": False,
                "allow_prices": True,
                "recipient": "Alice",
                "wishlist_buy_status_default_filter": "yes",
            },
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual("user@example.com", self.service.calls[0][1])
        self.assertEqual("Alice", self.service.calls[0][6])
        self.assertEqual("yes", self.service.calls[0][7])
        self.assertEqual("Alice", response.get_json()["share"]["recipient"])
        self.assertIn("/collection/share/", response.get_json()["share"]["link"])

    def test_list_and_revoke_share_use_connected_owner(self):
        """Verifie la liste et la revocation du proprietaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les deux contrats.
        """

        list_response = self.client.get(
            "/api/collection-shares",
            headers=self.get_user_auth_headers(),
        )
        revoke_response = self.client.delete(
            "/api/collection-shares/4",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(200, list_response.status_code)
        self.assertEqual("ACTIVE", list_response.get_json()["shares"][0]["status"])
        self.assertEqual(200, revoke_response.status_code)
        self.assertEqual("REVOKED", revoke_response.get_json()["share"]["status"])
        self.assertIn(("revoke", "user@example.com", 4), self.service.calls)

    def test_invalid_payload_and_foreign_share_return_400_and_404(self):
        """Verifie le mapping des erreurs de validation et de propriete.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les statuts HTTP.
        """

        invalid_response = self.client.post(
            "/api/collection-shares",
            headers=self.get_user_auth_headers(),
            json={},
        )
        missing_response = self.client.delete(
            "/api/collection-shares/999",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(400, invalid_response.status_code)
        self.assertEqual(404, missing_response.status_code)

    def test_routes_reject_missing_token_and_guest_profile(self):
        """Verifie la protection USER des routes de gestion.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les refus 403.
        """

        missing_response = self.client.get("/api/collection-shares")
        guest_token = app_module.auth_token_service.create_access_token(
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
            guest_response = self.client.get(
                "/api/collection-shares",
                headers={"Authorization": f"Bearer {guest_token}"},
            )
        finally:
            app_module.auth_guard.guest_session_validator = original_validator

        self.assertEqual(403, missing_response.status_code)
        self.assertEqual(403, guest_response.status_code)

    def test_route_catalog_declares_user_and_admin_profiles(self):
        """Verifie les metadonnees de decouverte des routes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les profils annonces.
        """

        response = self.client.get("/api/routes", headers=self.get_user_auth_headers())
        routes = {
            (route["path"], tuple(route["methods"])): route
            for route in response.get_json()["routes"]
        }

        for key in (
            ("/api/collection-shares", ("POST",)),
            ("/api/collection-shares", ("GET",)),
            ("/api/collection-shares/<int:share_id>", ("DELETE",)),
        ):
            self.assertEqual(["USER", "ADMIN"], routes[key]["required_profiles"])


if __name__ == "__main__":
    unittest.main()
