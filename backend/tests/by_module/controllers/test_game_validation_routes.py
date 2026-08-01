#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-01
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests des routes HTTP admin de validation des jeux.

import app as app_module

try:
    from tests.support.route_test_support import BaseAppRoutesTest
except ModuleNotFoundError:
    from tests.support.route_test_support import BaseAppRoutesTest


class FakeGameValidationRouteService:
    """Service validation jeux factice pour les routes."""

    summary_calls = 0

    def get_summary(self):
        """Retourne un resume de validation factice.

        Args:
            Aucun.

        Returns:
            dict: Resume factice.
        """

        self.__class__.summary_calls += 1
        return {
            "waiting_validation_count": 3,
            "has_waiting_validation": True,
        }


class GameValidationRoutesTest(BaseAppRoutesTest):
    """Valide les routes de resume admin des jeux a valider."""

    def setUp(self):
        """Prepare les fakes de routes.

        Args:
            Aucun.

        Returns:
            None: Les services sont injectes.
        """

        super().setUp()
        self.original_game_validation_service_factory = (
            app_module.library_controller.game_validation_service_factory
        )
        app_module.library_controller.game_validation_service_factory = (
            FakeGameValidationRouteService
        )
        FakeGameValidationRouteService.summary_calls = 0

    def tearDown(self):
        """Restaure le service de validation original.

        Args:
            Aucun.

        Returns:
            None: Les dependances sont restaurees.
        """

        app_module.library_controller.game_validation_service_factory = (
            self.original_game_validation_service_factory
        )
        super().tearDown()

    def test_summary_requires_authentication(self):
        """Verifie que le resume refuse les appels anonymes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut HTTP.
        """

        response = self.client.get("/api/library/games/validation/summary")

        self.assertEqual(403, response.status_code)
        self.assertEqual(0, FakeGameValidationRouteService.summary_calls)

    def test_summary_rejects_user_profile(self):
        """Verifie que le resume est reserve aux administrateurs.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le refus du profil USER.
        """

        response = self.client.get(
            "/api/library/games/validation/summary",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(403, response.status_code)
        self.assertEqual(0, FakeGameValidationRouteService.summary_calls)

    def test_admin_can_read_summary(self):
        """Verifie la lecture admin du resume de validation.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        response = self.client.get(
            "/api/library/games/validation/summary",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, FakeGameValidationRouteService.summary_calls)
        self.assertEqual(3, response.get_json()["summary"]["waiting_validation_count"])
        self.assertTrue(response.get_json()["summary"]["has_waiting_validation"])

    def test_routes_catalog_exposes_admin_summary_contract(self):
        """Verifie les metadonnees d'acces du resume admin.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident `/api/routes`.
        """

        response = self.client.get("/api/routes", headers=self.get_admin_auth_headers())
        routes_by_key = {
            (route["path"], tuple(route["methods"])): route
            for route in response.get_json()["routes"]
        }
        summary_route = routes_by_key[("/api/library/games/validation/summary", ("GET",))]

        self.assertTrue(summary_route["requires_auth"])
        self.assertEqual(["Bearer"], summary_route["auth_schemes"])
        self.assertEqual(["ADMIN"], summary_route["required_profiles"])


if __name__ == "__main__":
    unittest.main()
