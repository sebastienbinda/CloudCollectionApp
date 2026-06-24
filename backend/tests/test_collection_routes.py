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
# Description : tests des routes de lecture de collection jeux video.

try:
    from tests.route_test_support import BaseAppRoutesTest
    from tests.route_test_fakes import FakeUserCollectionQueryService
except ModuleNotFoundError:
    from route_test_support import BaseAppRoutesTest
    from route_test_fakes import FakeUserCollectionQueryService

class CollectionRoutesTest(BaseAppRoutesTest):
    """Valide les routes protegees de lecture et outils collection."""

    def test_read_routes_require_authentication(self):
        """Verifie que les routes de lecture collection exigent un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 403.
        """

        for path in [
            "/collections/videogames",
            "/collections/videogames/platforms/search",
            "/collections/videogames/games/search?q=mario",
            "/collections/videogames/games/3",
            "/collections/videogames/download",
        ]:
            self.assertEqual(403, self.client.get(path).status_code)

    def test_collection_statistics_platforms_and_games_return_sql_contracts(self):
        """Verifie les routes de lecture collection authentifiees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les payloads.
        """

        headers = self.get_user_auth_headers()

        statistics = self.client.get("/collections/videogames", headers=headers).get_json()
        platforms = self.client.get(
            "/collections/videogames/platforms/search?name=École&page=2&size=25&sort=end_date,desc",
            headers=headers,
        ).get_json()
        games = self.client.get(
            "/collections/videogames/games/search?name=mario&platform_id=1&wishlist=false&sort=studio_name,desc",
            headers=headers,
        ).get_json()

        self.assertEqual(42, statistics["total"])
        self.assertEqual("Switch", statistics["max_platform"])
        self.assertEqual(42, statistics["collection"]["total"])
        self.assertEqual(3, statistics["wishlist"]["total"])
        self.assertEqual("Switch", platforms["platforms"][0]["name"])
        self.assertEqual(25, platforms["platforms"][0]["nb_games"])
        self.assertEqual("2017-03-03", platforms["platforms"][0]["release_date"])
        self.assertEqual("", platforms["platforms"][0]["end_date"])
        self.assertEqual("Nintendo", platforms["platforms"][0]["manufacturer"])
        self.assertEqual({"generation": "8"}, platforms["platforms"][0]["description"])
        self.assertEqual(25, platforms["platforms"][0]["total_games"])
        self.assertNotIn("status", platforms["platforms"][0])
        self.assertEqual("Mario Kart", games["games"][0]["name"])
        self.assertEqual(1, games["games"][0]["platform_id"])
        self.assertFalse(games["games"][0]["wishlist"])
        self.assertFalse(FakeUserCollectionQueryService.last_games_criteria.wishlist)
        self.assertEqual("ecole", FakeUserCollectionQueryService.last_platforms_criteria.normalized_name)
        self.assertEqual(("end_date", "desc"), (
            FakeUserCollectionQueryService.last_platforms_criteria.sort_rules[0].column,
            FakeUserCollectionQueryService.last_platforms_criteria.sort_rules[0].direction,
        ))
        self.assertEqual(("studio_name", "desc"), (
            FakeUserCollectionQueryService.last_games_criteria.sort_rules[0].column,
            FakeUserCollectionQueryService.last_games_criteria.sort_rules[0].direction,
        ))

    def test_collection_game_detail_returns_current_user_game(self):
        """Verifie la route de detail d'un jeu de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload protege.
        """

        response = self.client.get(
            "/collections/videogames/games/3",
            headers=self.get_user_auth_headers(),
        )
        game = response.get_json()["game"]

        self.assertEqual(200, response.status_code)
        self.assertEqual("Mario Kart", game["name"])
        self.assertEqual("Switch", game["platform_name"])
        self.assertFalse(game["wishlist"])

    def test_collection_game_detail_returns_404_for_unknown_game(self):
        """Verifie l'absence d'un jeu dans la collection de l'utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut 404.
        """

        response = self.client.get(
            "/collections/videogames/games/999",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(404, response.status_code)

    def test_games_search_returns_clear_error_for_invalid_sort_column(self):
        """Verifie le message HTTP pour une colonne de tri jeux inconnue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut et le message JSON.
        """

        response = self.client.get(
            "/collections/videogames/games/search?sort=unknown,asc",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("Unsupported sort column 'unknown'", response.get_json()["error"])

    def test_games_search_returns_clear_error_for_invalid_filter_parameter(self):
        """Verifie le message HTTP pour un critere jeux inconnu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut et le message JSON.
        """

        response = self.client.get(
            "/collections/videogames/games/search?unknown_filter=value",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("Unsupported query parameter 'unknown_filter'", response.get_json()["error"])

    def test_games_search_returns_clear_error_for_invalid_criteria_format(self):
        """Verifie le message HTTP pour un format de critere invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut et le message JSON.
        """

        response = self.client.get(
            "/collections/videogames/games/search?platform_id=abc",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual("Invalid platform_id. Expected a positive integer.", response.get_json()["error"])

    def test_legacy_collection_type_search_route_is_not_registered(self):
        """Verifie que l'ancien chemin typé de collection n'est plus expose.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la suppression de l'ancien format de route.
        """

        legacy_collection_type = "Jeux" + "Video"
        legacy_path = f"/collections/{legacy_collection_type}/search"
        response = self.client.get(legacy_path, headers=self.get_user_auth_headers())

        self.assertEqual(404, response.status_code)

    def test_legacy_ods_collection_routes_are_not_registered(self):
        """Verifie que les anciennes routes ODS de consultation sont supprimees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les 404.
        """

        headers = self.get_user_auth_headers()
        requests_to_check = [
            ("GET", "/collections/videogames/home"),
            ("POST", "/collections/videogames/cache/reset"),
            ("GET", "/collections/videogames/search?platform=Switch"),
            ("GET", "/collections/videogames/platforms"),
            ("GET", "/collections/videogames/column-values?platform=Switch"),
            ("GET", "/collections/videogames/add-game-choices?platform=Switch"),
            ("GET", "/collections/videogames/platform-image/Switch"),
        ]

        for method, path in requests_to_check:
            response = self.client.open(path, method=method, headers=headers)
            self.assertEqual(404, response.status_code, path)

    def test_legacy_ods_collection_routes_are_absent_from_route_catalog(self):
        """Verifie que les anciennes routes ODS sont absentes de `/api/routes`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le catalogue.
        """

        response = self.client.get("/api/routes", headers=self.get_user_auth_headers())
        routes_by_path = {route["path"] for route in response.get_json()["routes"]}

        self.assertNotIn("/collections/videogames/home", routes_by_path)
        self.assertNotIn("/collections/videogames/cache/reset", routes_by_path)
        self.assertNotIn("/collections/videogames/search", routes_by_path)
        self.assertNotIn("/collections/videogames/platforms", routes_by_path)
        self.assertNotIn("/collections/videogames/column-values", routes_by_path)
        self.assertNotIn("/collections/videogames/add-game-choices", routes_by_path)
        self.assertNotIn("/collections/videogames/platform-image/<path:platform>", routes_by_path)
        self.assertNotIn("/collections/videogames/wishlist/games", routes_by_path)

    def test_download_returns_current_user_raw_file(self):
        """Verifie le telechargement brut du fichier utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les reponses.
        """

        headers = self.get_user_auth_headers()

        response = self.client.get("/collections/videogames/download", headers=headers)
        self.assertEqual(200, response.status_code)
        self.assertIn("attachment", response.headers["Content-Disposition"])

    def test_download_returns_404_when_collection_file_is_empty_or_missing(self):
        """Verifie le telechargement avec fichier absent.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les 404 attendus.
        """

        headers = self.get_user_auth_headers()

        FakeUserCollectionQueryService.collection_file_path = ""
        self.assertEqual(404, self.client.get("/collections/videogames/download", headers=headers).status_code)

        FakeUserCollectionQueryService.collection_file_path = "/tmp/cloudcollection-missing-file.ods"
        self.assertEqual(404, self.client.get("/collections/videogames/download", headers=headers).status_code)
