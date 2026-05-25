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

try:
    from tests.route_test_support import BaseAppRoutesTest
    from tests.route_test_fakes import FakeLibraryService
except ModuleNotFoundError:
    from route_test_support import BaseAppRoutesTest
    from route_test_fakes import FakeLibraryService


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

        response = self.client.get("/api/library/games?sort=developer,desc")
        game = response.get_json()["games"][0]
        criteria = FakeLibraryService.last_games_criteria

        self.assertEqual(200, response.status_code)
        self.assertEqual("Final Fantasy", game["name"])
        self.assertNotIn("collection_file_path", game)
        self.assertEqual("developer", criteria.sort_rules[0].column)

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
        self.assertFalse(routes_by_key[("/api/auth/verify-email", ("GET", "POST"))]["requires_auth"])
        self.assertFalse(routes_by_key[("/api/library/games", ("GET",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/api/routes", ("GET",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/collections/videogames/games", ("POST",))]["requires_auth"])
        self.assertEqual(["Bearer"], routes_by_key[("/collections/videogames/games", ("POST",))]["auth_schemes"])
