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
# Description : tests des routes publiques Bibliotheque et catalogue.

import app as app_module

try:
    from tests.support.route_test_support import BaseAppRoutesTest
    from tests.support.route_test_fakes import FakeLibraryService
except ModuleNotFoundError:
    from tests.support.route_test_support import BaseAppRoutesTest
    from tests.support.route_test_fakes import FakeLibraryService


class LibraryRoutesTest(BaseAppRoutesTest):
    """Valide les routes publiques Bibliotheque."""

    def test_library_entities_route_is_public(self):
        """Verifie les compteurs publics.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        response = self.client.get("/api/library/entities")

        self.assertEqual(200, response.status_code)
        self.assertEqual({"platforms": 2, "studios": 3, "games": 4}, response.get_json())
        self.assertEqual("PUBLIC", FakeLibraryService.last_entities_requester_profile)

    def test_library_entities_route_uses_optional_admin_bearer(self):
        """Verifie le profil admin optionnel des compteurs.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contexte de visibilite.
        """

        response = self.client.get("/api/library/entities", headers=self.get_admin_auth_headers())

        self.assertEqual(200, response.status_code)
        self.assertEqual("ADMIN", FakeLibraryService.last_entities_requester_profile)

    def test_library_controller_reuses_single_service_instance(self):
        """Verifie que les controleurs Bibliotheque reutilisent leur service.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident une seule construction par controleur.
        """

        created_services = {
            "platforms": [],
            "studios": [],
            "games": [],
        }

        def create_platform_service():
            service = FakeLibraryService()
            created_services["platforms"].append(service)
            return service

        def create_studio_service():
            service = FakeLibraryService()
            created_services["studios"].append(service)
            return service

        def create_game_service():
            service = FakeLibraryService()
            created_services["games"].append(service)
            return service

        app_module.platform_controller.library_service_factory = create_platform_service
        app_module.studio_controller.library_service_factory = create_studio_service
        app_module.game_controller.library_service_factory = create_game_service

        self.client.get("/api/library/entities")
        self.client.get("/api/library/platforms")
        self.client.get("/api/library/studios")
        self.client.get("/api/library/studios")
        self.client.get("/api/library/games")
        self.client.get("/api/library/games")

        self.assertEqual(1, len(created_services["platforms"]))
        self.assertEqual(1, len(created_services["studios"]))
        self.assertEqual(1, len(created_services["games"]))

    def test_library_platforms_route_is_public_and_uses_query_contract(self):
        """Verifie la route plateformes publique.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les criteres.
        """

        response = self.client.get("/api/library/platforms?name=École&page=2&size=25&sort=manufacturer,desc")
        criteria = FakeLibraryService.last_platforms_criteria

        self.assertEqual(200, response.status_code)
        self.assertEqual("Switch", response.get_json()["platforms"][0]["name"])
        self.assertEqual("ecole", criteria.normalized_name)
        self.assertEqual(("manufacturer", "desc"), (criteria.sort_rules[0].column, criteria.sort_rules[0].direction))

    def test_library_studios_route_is_public_and_falls_back_on_invalid_parameters(self):
        """Verifie les fallbacks de la route studios.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les valeurs par defaut.
        """

        response = self.client.get("/api/library/studios?page=-1&size=999&sort=private,desc")
        criteria = FakeLibraryService.last_studios_criteria

        self.assertEqual(200, response.status_code)
        self.assertEqual({"page": 0, "size": 500}, {"page": response.get_json()["page"]["page"], "size": response.get_json()["page"]["size"]})
        self.assertEqual(("name", "asc"), (criteria.sort_rules[0].column, criteria.sort_rules[0].direction))

    def test_library_games_route_is_public(self):
        """Verifie la route jeux publique.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload public.
        """

        response = self.client.get("/api/library/games?platform=NÉS&sort=developer,desc")
        game = response.get_json()["games"][0]
        criteria = FakeLibraryService.last_games_criteria

        self.assertEqual(200, response.status_code)
        self.assertEqual("Final Fantasy", game["name"])
        self.assertEqual("1995-08-14", game["platform_end_date"])
        self.assertEqual("NES", game["platform_common_alias"])
        self.assertNotIn("collection_file_path", game)
        self.assertFalse(game["in_current_user_collection"])
        self.assertEqual("nes", criteria.normalized_platform)
        self.assertEqual("developer", criteria.sort_rules[0].column)
        self.assertIsNone(criteria.current_user_id)
        self.assertEqual("PUBLIC", criteria.requester_profile)

    def test_library_games_route_enriches_user_collection_status_with_user_token(self):
        """Verifie l'enrichissement optionnel collection pour un USER connecte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le marqueur collection.
        """

        response = self.client.get("/api/library/games", headers=self.get_user_auth_headers())
        game = response.get_json()["games"][0]
        criteria = FakeLibraryService.last_games_criteria

        self.assertEqual(200, response.status_code)
        self.assertTrue(game["in_current_user_collection"])
        self.assertEqual(7, criteria.current_user_id)
        self.assertEqual("USER", criteria.requester_profile)

    def test_library_games_route_uses_admin_visibility_context(self):
        """Verifie que la liste jeux transmet le profil ADMIN au service.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contexte de visibilite.
        """

        response = self.client.get("/api/library/games", headers=self.get_admin_auth_headers())
        criteria = FakeLibraryService.last_games_criteria

        self.assertEqual(200, response.status_code)
        self.assertEqual("ADMIN", criteria.requester_profile)
        self.assertIsNone(criteria.current_user_id)

    def test_library_games_route_rejects_invalid_optional_bearer(self):
        """Verifie qu'un Bearer optionnel invalide reste refuse proprement.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut d'authentification.
        """

        response = self.client.get(
            "/api/library/games",
            headers={"Authorization": "Bearer invalid-token"},
        )

        self.assertEqual(401, response.status_code)

    def test_library_platform_detail_route_is_public(self):
        """Verifie la route publique de detail d'une plateforme.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload public.
        """

        response = self.client.get("/api/library/platforms/1")
        platform = response.get_json()["platform"]

        self.assertEqual(200, response.status_code)
        self.assertEqual("Switch", platform["name"])
        self.assertEqual("Japon", platform["aliases"][0]["usage_region"])
        self.assertEqual([{"id": 41, "type": "MAIN"}], platform["images"])
        self.assertNotIn("collection_file_path", platform)

    def test_library_platform_detail_route_returns_404_for_unknown_platform(self):
        """Verifie l'absence de plateforme publique.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut 404.
        """

        response = self.client.get("/api/library/platforms/999")

        self.assertEqual(404, response.status_code)

    def test_library_game_detail_route_is_public(self):
        """Verifie la route publique de detail d'un jeu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload public.
        """

        response = self.client.get("/api/library/games/3")
        game = response.get_json()["game"]

        self.assertEqual(200, response.status_code)
        self.assertEqual("Final Fantasy", game["name"])
        self.assertEqual("NES", game["platform"])
        self.assertEqual("1995-08-14", game["platform_end_date"])
        self.assertEqual("NES", game["platform_common_alias"])
        self.assertNotIn("collection_file_path", game)
        self.assertEqual(("PUBLIC", None), FakeLibraryService.last_game_detail_context)

    def test_library_game_detail_route_uses_user_owner_context(self):
        """Verifie le contexte proprietaire optionnel du detail jeu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident profil et utilisateur transmis.
        """

        response = self.client.get("/api/library/games/3", headers=self.get_user_auth_headers())

        self.assertEqual(200, response.status_code)
        self.assertEqual(("USER", 7), FakeLibraryService.last_game_detail_context)

    def test_library_game_detail_route_uses_admin_context(self):
        """Verifie le contexte administrateur optionnel du detail jeu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le profil transmis.
        """

        response = self.client.get("/api/library/games/3", headers=self.get_admin_auth_headers())

        self.assertEqual(200, response.status_code)
        self.assertEqual(("ADMIN", None), FakeLibraryService.last_game_detail_context)

    def test_library_game_detail_route_returns_404_for_unknown_game(self):
        """Verifie l'absence de jeu public.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut 404.
        """

        response = self.client.get("/api/library/games/999")

        self.assertEqual(404, response.status_code)

    def test_routes_route_requires_authentication(self):
        """Verifie que le catalogue reste protege.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 403.
        """

        self.assertEqual(403, self.client.get("/api/routes").status_code)

    def test_routes_route_lists_auth_constraints(self):
        """Verifie les contraintes de routes publiques et protegees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le catalogue.
        """

        response = self.client.get("/api/routes", headers=self.get_auth_headers())
        routes_by_key = {(route["path"], tuple(route["methods"])): route for route in response.get_json()["routes"]}

        self.assertFalse(routes_by_key[("/auth/token", ("POST",))]["requires_auth"])
        self.assertFalse(routes_by_key[("/api/auth/register", ("POST",))]["requires_auth"])
        self.assertFalse(
            routes_by_key[("/api/auth/pseudonym-availability", ("GET",))]["requires_auth"]
        )
        self.assertFalse(routes_by_key[("/api/auth/verify-email", ("GET", "POST"))]["requires_auth"])
        self.assertFalse(routes_by_key[("/api/library/platforms/<int:platform_id>", ("GET",))]["requires_auth"])
        self.assertFalse(routes_by_key[("/api/library/games", ("GET",))]["requires_auth"])
        self.assertFalse(routes_by_key[("/api/library/games/<int:game_id>", ("GET",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/api/routes", ("GET",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/collections/videogames/games/<int:game_id>", ("GET",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/collections/videogames/games", ("POST",))]["requires_auth"])
        self.assertEqual(["Bearer"], routes_by_key[("/collections/videogames/games", ("POST",))]["auth_schemes"])
