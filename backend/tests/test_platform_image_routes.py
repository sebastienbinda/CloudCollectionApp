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
    PlatformImageNotFoundError,
    PlatformImagePlatformNotFoundError,
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


if __name__ == "__main__":
    unittest.main()
