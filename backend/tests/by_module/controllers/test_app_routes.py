#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
import unittest
import app as app_module


class AppRoutesTest(unittest.TestCase):
    def setUp(self):
        """Prepare le client Flask de test.
        Args:
            Aucun.
        Returns:
            None: Le client Flask est prepare pour chaque test.
        """
        app_module.app.config.update(TESTING=True)
        self.client = app_module.app.test_client()
    def get_auth_headers(self):
        """Construit un header Bearer valide pour les routes protegees.
        Args:
            Aucun.
        Returns:
            dict[str, str]: En-tetes HTTP contenant le token d'authentification.
        """
        token = app_module.auth_token_service.create_access_token("admin")
        return {"Authorization": f"Bearer {token}"}
    def test_auth_token_route_returns_bearer_token(self):
        """Verifie la generation d'un token OAuth2 Bearer.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/auth/token",
            json={"username": "admin", "password": "change-me"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Bearer", response.get_json()["token_type"])
        self.assertTrue(response.get_json()["access_token"])
    def test_auth_token_route_rejects_invalid_credentials(self):
        """Verifie le refus des identifiants invalides.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/auth/token",
            json={"username": "admin", "password": "bad-password"},
        )
        self.assertEqual(401, response.status_code)
        self.assertIn("invalides", response.get_json()["error"])
    def test_legacy_ods_routes_are_not_registered(self):
        """Verifie que les anciennes routes ODS globales ne sont plus exposees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les 404 Flask.
        """

        self.assertEqual(404, self.client.get("/collections/JeuxVideo/platforms").status_code)
        self.assertEqual(404, self.client.post("/collections/JeuxVideo/cache/reset").status_code)
        self.assertEqual(404, self.client.get("/collections/JeuxVideo/ods/download").status_code)

    def test_routes_route_lists_public_and_protected_routes(self):
        """Verifie le catalogue des routes et leurs contraintes d'authentification.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident le contrat de decouverte des routes.
        """
        response = self.client.get("/api/routes", headers=self.get_auth_headers())
        routes = response.get_json()["routes"]
        routes_by_key = {
            (route["path"], tuple(route["methods"])): route
            for route in routes
        }
        self.assertEqual(200, response.status_code)
        self.assertTrue(routes_by_key[("/api/routes", ("GET",))]["requires_auth"])
        self.assertFalse(routes_by_key[("/api/library/platforms", ("GET",))]["requires_auth"])
        self.assertFalse(
            routes_by_key[("/api/library/platforms/<int:platform_id>", ("GET",))]["requires_auth"]
        )
        self.assertTrue(routes_by_key[("/collections/videogames/games", ("POST",))]["requires_auth"])
        self.assertTrue(
            routes_by_key[("/api/users/collection/reinit", ("POST",))]["requires_auth"]
        )
        self.assertTrue(routes_by_key[("/api/feedback", ("POST",))]["requires_auth"])
        self.assertEqual(
            ["Bearer"],
            routes_by_key[("/collections/videogames/games", ("POST",))]["auth_schemes"],
        )

    def test_routes_route_requires_authentication(self):
        """Verifie que le catalogue des routes est protege.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le refus sans token.
        """

        response = self.client.get("/api/routes")

        self.assertEqual(403, response.status_code)

    def test_add_game_route_rejects_invalid_token(self):
        """Verifie que l'action reservee d'ajout refuse un token invalide.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/videogames/games",
            json={"platform": "Switch", "Nom du jeu": "Metroid"},
            headers={"Authorization": "Bearer invalid-token"},
        )
        self.assertEqual(401, response.status_code)
        self.assertIn("invalide", response.get_json()["error"])

    def test_reserved_game_actions_return_not_implemented(self):
        """Verifie que les actions jeu reservees retournent 501.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat courant.
        """

        response = self.client.post(
            "/collections/videogames/games",
            json={"platform": "Switch", "Nom du jeu": "Metroid"},
            headers=self.get_auth_headers(),
        )

        self.assertEqual(501, response.status_code)
        self.assertIn("not implemented", response.get_json()["error"].lower())

if __name__ == "__main__":
    unittest.main()
