#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-24
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests des droits de consultation de collection du profil GUEST.

import app as app_module
from services.auth import CollectionShareUnavailableError

try:
    from tests.support.route_test_fakes import FakeUserCollectionQueryService
    from tests.support.route_test_support import BaseAppRoutesTest
except ModuleNotFoundError:
    from tests.support.route_test_fakes import FakeUserCollectionQueryService
    from tests.support.route_test_support import BaseAppRoutesTest


class AvailableGuestSessionValidator:
    """Simule un partage GUEST encore actif pendant les tests HTTP."""

    def validate_guest_session(self, payload):
        """Accepte la session invitee fournie.

        Args:
            payload (dict): Claims GUEST deja signes.

        Returns:
            None: La session reste valide.

        Raises:
            Aucun.
        """


class UnavailableGuestSessionValidator:
    """Simule un partage GUEST expire ou revoque."""

    def validate_guest_session(self, payload):
        """Refuse la session invitee fournie.

        Args:
            payload (dict): Claims GUEST deja signes.

        Returns:
            None: La methode ne retourne pas normalement.

        Raises:
            CollectionShareUnavailableError: Toujours, pour produire HTTP 411.
        """

        raise CollectionShareUnavailableError("Partage indisponible.")


class GuestCollectionRoutesTest(BaseAppRoutesTest):
    """Valide le perimetre de lecture de collection d'un GUEST."""

    def setUp(self):
        """Prepare un validateur de partage injectable.

        Args:
            Aucun.

        Returns:
            None: Le client et le validateur GUEST sont prepares.
        """

        super().setUp()
        self.original_guest_session_validator = app_module.auth_guard.guest_session_validator
        app_module.auth_guard.guest_session_validator = AvailableGuestSessionValidator()

    def tearDown(self):
        """Restaure le validateur reel des sessions GUEST.

        Args:
            Aucun.

        Returns:
            None: Les dependances globales sont restaurees.
        """

        app_module.auth_guard.guest_session_validator = self.original_guest_session_validator
        super().tearDown()

    def get_guest_auth_headers(self, collection=True, wishlist=False, prices=False):
        """Construit une session GUEST signee.

        Args:
            collection (bool): Autorise les jeux possedes.
            wishlist (bool): Autorise la liste de souhaits.
            prices (bool): Autorise les informations de prix.

        Returns:
            dict[str, str]: En-tete Bearer GUEST.

        Raises:
            Aucun.
        """

        token = app_module.auth_token_service.create_access_token(
            "guest-share:8",
            "GUEST",
            additional_claims={
                "collection_share_id": 8,
                "owner_user_id": 91,
                "permissions": {
                    "collection": collection,
                    "wishlist": wishlist,
                    "prices": prices,
                },
            },
        )
        return {"Authorization": f"Bearer {token}"}

    def test_guest_reads_only_shared_owner_collection(self):
        """Verifie l'isolation proprietaire et le cadrage de categorie.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'identifiant et le filtre forces.
        """

        response = self.client.get(
            "/collections/videogames/games/search",
            headers=self.get_guest_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(91, FakeUserCollectionQueryService.last_user_id)
        self.assertFalse(FakeUserCollectionQueryService.last_games_criteria.wishlist)

    def test_guest_category_permission_combinations(self):
        """Verifie collection seule, wishlist seule et acces conjoint.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les trois combinaisons.
        """

        collection_response = self.client.get(
            "/collections/videogames/games/search?wishlist=false",
            headers=self.get_guest_auth_headers(),
        )
        forbidden_wishlist = self.client.get(
            "/collections/videogames/games/search?wishlist=true",
            headers=self.get_guest_auth_headers(),
        )
        wishlist_response = self.client.get(
            "/collections/videogames/platforms/search",
            headers=self.get_guest_auth_headers(False, True),
        )
        wishlist_criteria = FakeUserCollectionQueryService.last_platforms_criteria
        both_response = self.client.get(
            "/collections/videogames/games/search?wishlist=true",
            headers=self.get_guest_auth_headers(True, True),
        )

        self.assertEqual(200, collection_response.status_code)
        self.assertEqual(403, forbidden_wishlist.status_code)
        self.assertEqual(200, wishlist_response.status_code)
        self.assertTrue(wishlist_criteria.wishlist)
        self.assertEqual(200, both_response.status_code)

    def test_guest_without_price_permission_has_masked_prices(self):
        """Verifie les listes, details et statistiques sans prix.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le masquage complet des prix.
        """

        headers = self.get_guest_auth_headers()
        game_list = self.client.get(
            "/collections/videogames/games/search?wishlist=false", headers=headers
        ).get_json()["games"][0]
        game_detail = self.client.get(
            "/collections/videogames/games/3", headers=headers
        ).get_json()["game"]
        platform = self.client.get(
            "/collections/videogames/platforms/search?wishlist=false", headers=headers
        ).get_json()["platforms"][0]
        statistics = self.client.get(
            "/collections/videogames", headers=headers
        ).get_json()

        for game in (game_list, game_detail):
            self.assertNotIn("purchase_price", game)
            self.assertNotIn("price_unit", game)
        for values in (statistics, statistics["collection"], platform):
            self.assertEqual(0, values["total_value"])
            self.assertEqual(0, values["average_value"])
        self.assertEqual((True, False), FakeUserCollectionQueryService.last_statistics_scope)
        self.assertEqual(0, statistics["wishlist"]["total"])

    def test_guest_with_price_permission_keeps_prices(self):
        """Verifie la conservation des prix explicitement partages.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les champs de prix.
        """

        response = self.client.get(
            "/collections/videogames/games/search?wishlist=false",
            headers=self.get_guest_auth_headers(prices=True),
        )
        game = response.get_json()["games"][0]
        self.assertEqual(59.99, game["purchase_price"])
        self.assertEqual("EUR", game["price_unit"])

    def test_guest_game_detail_rejects_unshared_category(self):
        """Verifie HTTP 403 pour un detail de categorie interdite.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le refus.
        """

        response = self.client.get(
            "/collections/videogames/games/4",
            headers=self.get_guest_auth_headers(),
        )
        self.assertEqual(403, response.status_code)

    def test_guest_write_download_import_and_image_routes_are_forbidden(self):
        """Verifie HTTP 403 pour toutes les actions non consultatives.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les routes interdites.
        """

        headers = self.get_guest_auth_headers(True, True, True)
        requests_to_check = [
            ("GET", "/collections/videogames/download"),
            ("POST", "/collections/videogames/games"),
            ("PUT", "/collections/videogames/games"),
            ("DELETE", "/collections/videogames/games"),
            ("POST", "/api/users/import/file/ods"),
            ("POST", "/api/users/import/analyze/ods"),
            ("POST", "/api/users/import"),
            ("POST", "/api/users/collection/reinit"),
            ("POST", "/api/library/platforms/1/image"),
        ]
        for method, path in requests_to_check:
            response = self.client.open(path, method=method, headers=headers)
            self.assertEqual(403, response.status_code, path)

    def test_guest_share_invalidation_returns_411(self):
        """Verifie l'invalidation au prochain appel de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident HTTP 411.
        """

        app_module.auth_guard.guest_session_validator = UnavailableGuestSessionValidator()
        response = self.client.get(
            "/collections/videogames",
            headers=self.get_guest_auth_headers(),
        )
        self.assertEqual(411, response.status_code)
