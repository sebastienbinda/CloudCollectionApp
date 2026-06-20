#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-19
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests des routes HTTP des images de plateformes.

from io import BytesIO

from services.library import (
    PlatformImageModerationError,
    PlatformImageNotFoundError,
    PlatformImagePlatformNotFoundError,
    PlatformImageStorageLimitExceededError,
    PlatformImageValidationError,
)

try:
    from tests.route_test_support import BaseAppRoutesTest, FakePlatformImageRouteService
except ModuleNotFoundError:
    from route_test_support import BaseAppRoutesTest, FakePlatformImageRouteService


class PlatformImageRoutesTest(BaseAppRoutesTest):
    """Valide les routes d'images de plateformes."""

    def test_upload_rejects_missing_token(self):
        """Verifie le refus d'upload sans token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        response = self.client.post("/api/library/platforms/1/image")

        self.assertEqual(403, response.status_code)

    def test_upload_creates_waiting_image_with_token_subject(self):
        """Verifie la creation d'image avec utilisateur connecte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        response = self.client.post(
            "/api/library/platforms/1/image",
            data={"image": (BytesIO(b"img"), "console.png")},
            content_type="multipart/form-data",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual("WAITING_VALIDATION", response.get_json()["image"]["status"])
        self.assertEqual("user@example.com", FakePlatformImageRouteService.last_upload_call[2])

    def test_upload_returns_404_for_unknown_platform(self):
        """Verifie le statut d'une plateforme inconnue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        FakePlatformImageRouteService.next_upload_error = PlatformImagePlatformNotFoundError()

        response = self.client.post(
            "/api/library/platforms/99/image",
            data={"image": (BytesIO(b"img"), "console.png")},
            content_type="multipart/form-data",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(404, response.status_code)

    def test_upload_returns_422_for_invalid_image(self):
        """Verifie le statut d'une image invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        FakePlatformImageRouteService.next_upload_error = PlatformImageValidationError()

        response = self.client.post(
            "/api/library/platforms/1/image",
            data={"image": (BytesIO(b"img"), "console.txt")},
            content_type="multipart/form-data",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(422, response.status_code)

    def test_upload_returns_503_when_storage_limits_are_exceeded(self):
        """Verifie le statut temporaire quand les quotas disque bloquent l'upload.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut et le message.
        """

        FakePlatformImageRouteService.next_upload_error = PlatformImageStorageLimitExceededError(
            "total_bytes",
            {"total_image_bytes": 42},
        )

        response = self.client.post(
            "/api/library/platforms/1/image",
            data={"image": (BytesIO(b"img"), "console.png")},
            content_type="multipart/form-data",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(503, response.status_code)
        self.assertIn("temporairement desactivee", response.get_json()["error"])

    def test_public_image_route_serves_accepted_file(self):
        """Verifie la lecture publique d'une image acceptee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut public.
        """

        response = self.client.get("/api/library/platforms/1/image/12")

        self.assertEqual(200, response.status_code)
        self.assertEqual((1, 12), FakePlatformImageRouteService.last_public_call)

    def test_public_image_route_returns_404_for_waiting_image(self):
        """Verifie le refus public d'une image non acceptee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        FakePlatformImageRouteService.next_public_error = PlatformImageNotFoundError()

        response = self.client.get("/api/library/platforms/1/image/12")

        self.assertEqual(404, response.status_code)

    def test_admin_image_file_rejects_missing_token(self):
        """Verifie le refus de lecture admin sans token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        response = self.client.get("/api/library/platforms/1/image/12/moderation")

        self.assertEqual(403, response.status_code)

    def test_admin_image_file_accepts_admin(self):
        """Verifie la lecture admin d'une image en attente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'appel service.
        """

        response = self.client.get(
            "/api/library/platforms/1/image/12/moderation",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual((1, 12), FakePlatformImageRouteService.last_admin_file_call)

    def test_admin_image_file_returns_404_for_unknown_image(self):
        """Verifie le statut 404 pour une image admin inconnue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        FakePlatformImageRouteService.next_admin_file_error = PlatformImageNotFoundError()

        response = self.client.get(
            "/api/library/platforms/1/image/12/moderation",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(404, response.status_code)

    def test_admin_image_list_rejects_missing_token(self):
        """Verifie le refus de liste admin sans token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        response = self.client.get("/api/library/platforms/images")

        self.assertEqual(403, response.status_code)

    def test_admin_image_list_rejects_user_profile(self):
        """Verifie le refus de liste admin avec profil USER.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        response = self.client.get(
            "/api/library/platforms/images",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(403, response.status_code)

    def test_admin_image_list_accepts_admin_and_forwards_filters(self):
        """Verifie la liste admin paginee avec filtres.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        response = self.client.get(
            "/api/library/platforms/images?page=2&size=25&status=WAITING_VALIDATION&platform=Switch",
            headers=self.get_admin_auth_headers(),
        )
        payload = response.get_json()
        query = FakePlatformImageRouteService.last_list_query

        self.assertEqual(200, response.status_code)
        self.assertEqual(7, payload["images"][0]["user_id"])
        self.assertEqual(262144, payload["images"][0]["file_size_bytes"])
        self.assertEqual(3, payload["storage_summary"]["total_images"])
        self.assertEqual(786432, payload["storage_summary"]["total_size_bytes"])
        self.assertEqual("/api/library/platforms/1/image/12", payload["images"][0]["image_url"])
        self.assertEqual(
            "/api/library/platforms/1/image/12/moderation",
            payload["images"][0]["moderation_image_url"],
        )
        self.assertEqual("2", query.get("page"))
        self.assertEqual("WAITING_VALIDATION", query.get("status"))
        self.assertEqual("Switch", query.get("platform"))

    def test_admin_image_status_accepts_image(self):
        """Verifie l'acceptation d'une image par un admin.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'appel service.
        """

        response = self.client.put(
            "/api/library/platforms/1/image/12/status/accepted",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual((1, 12, "accepted"), FakePlatformImageRouteService.last_status_call)

    def test_admin_image_status_refuses_image(self):
        """Verifie le refus d'une image par un admin.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        response = self.client.put(
            "/api/library/platforms/1/image/12/status/refused",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(response.get_json()["deleted"])

    def test_admin_image_type_sets_main(self):
        """Verifie le typage MAIN d'une image par un admin.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'appel service.
        """

        response = self.client.put(
            "/api/library/platforms/1/image/12/type/MAIN",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual((1, 12, "MAIN"), FakePlatformImageRouteService.last_type_call)

    def test_admin_image_moderation_returns_404_for_unknown_image(self):
        """Verifie le statut 404 pour une image inconnue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        FakePlatformImageRouteService.next_moderation_error = PlatformImageNotFoundError()

        response = self.client.put(
            "/api/library/platforms/1/image/99/status/accepted",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(404, response.status_code)

    def test_admin_image_moderation_returns_404_for_invalid_value(self):
        """Verifie le statut 404 pour une valeur de moderation invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        FakePlatformImageRouteService.next_moderation_error = PlatformImageModerationError()

        response = self.client.put(
            "/api/library/platforms/1/image/12/type/BAD",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(404, response.status_code)

    def test_routes_catalog_lists_admin_image_constraints(self):
        """Verifie les metadonnees d'authentification des routes admin.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le catalogue.
        """

        response = self.client.get("/api/routes", headers=self.get_admin_auth_headers())
        routes_by_key = {
            (route["path"], tuple(route["methods"])): route
            for route in response.get_json()["routes"]
        }

        self.assertTrue(routes_by_key[("/api/library/platforms/images", ("GET",))]["requires_auth"])
        self.assertTrue(
            routes_by_key[
                (
                    "/api/library/platforms/<int:platform_id>/image/<int:image_id>/moderation",
                    ("GET",),
                )
            ]["requires_auth"]
        )
        self.assertEqual(
            ["ADMIN"],
            routes_by_key[("/api/library/platforms/images", ("GET",))]["required_profiles"],
        )
        self.assertTrue(
            routes_by_key[
                (
                    "/api/library/platforms/<int:platform_id>/image/<int:image_id>/type/<image_type>",
                    ("PUT",),
                )
            ]["requires_auth"]
        )


if __name__ == "__main__":
    unittest.main()
