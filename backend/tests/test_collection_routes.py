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
            "/collections/videogames/platforms/search?name=École&page=2&size=25&sort=name,desc",
            headers=headers,
        ).get_json()
        games = self.client.get(
            "/collections/videogames/games/search?name=mario&platform_id=1&sort=studio_name,desc",
            headers=headers,
        ).get_json()

        self.assertEqual(42, statistics["total"])
        self.assertEqual("Switch", statistics["max_platform"])
        self.assertEqual("Switch", platforms["platforms"][0]["name"])
        self.assertEqual(25, platforms["platforms"][0]["nb_games"])
        self.assertEqual("Mario Kart", games["games"][0]["name"])
        self.assertEqual(1, games["games"][0]["platform_id"])
        self.assertEqual("ecole", FakeUserCollectionQueryService.last_platforms_criteria.normalized_name)
        self.assertEqual(("studio_name", "desc"), (
            FakeUserCollectionQueryService.last_games_criteria.sort_rules[0].column,
            FakeUserCollectionQueryService.last_games_criteria.sort_rules[0].direction,
        ))

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

        self.assertEqual(403, response.status_code)

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
