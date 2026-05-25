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
except ModuleNotFoundError:
    from route_test_support import BaseAppRoutesTest


class CollectionRoutesTest(BaseAppRoutesTest):
    """Valide les routes protegees de lecture et outils collection."""

    def test_read_routes_require_authentication(self):
        """Verifie que les routes de lecture ODS exigent un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 403.
        """

        for path in [
            "/collections/videogames/platforms",
            "/collections/videogames/search?platform=Switch",
            "/collections/videogames/games/search?q=mario",
            "/collections/videogames/home",
            "/collections/videogames/column-values?platform=Switch",
            "/collections/videogames/cache/reset",
            "/collections/videogames/download",
        ]:
            self.assertEqual(403, self.client.get(path).status_code)

    def test_platforms_search_home_and_column_values_return_data(self):
        """Verifie les routes de lecture authentifiees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les payloads.
        """

        headers = self.get_auth_headers()

        self.assertEqual(["Switch", "Playstation"], self.client.get("/collections/videogames/platforms", headers=headers).get_json()["platforms"])
        self.assertEqual(45, self.client.get("/collections/videogames/search?platform=Switch", headers=headers).get_json()[0]["Prix d'achat"])
        self.assertEqual(45, self.client.get("/collections/videogames/home", headers=headers).get_json()["totals"]["total_price"])
        self.assertEqual([45], self.client.get("/collections/videogames/column-values?platform=Switch", headers=headers).get_json()["values_by_column"]["Prix d'achat"])
        self.assertEqual("Mario Kart", self.client.get("/collections/videogames/games/search?q=mario", headers=headers).get_json()["items"][0]["Nom du jeu"])

    def test_legacy_collection_type_search_route_is_not_registered(self):
        """Verifie que l'ancien chemin typé de collection n'est plus expose.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la suppression de l'ancien format de route.
        """

        legacy_collection_type = "Jeux" + "Video"
        legacy_path = f"/collections/{legacy_collection_type}/search"
        response = self.client.get(legacy_path, headers=self.get_auth_headers())

        self.assertEqual(403, response.status_code)

    def test_cache_reset_add_game_choices_and_download(self):
        """Verifie les routes utilitaires de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les reponses.
        """

        headers = self.get_auth_headers()

        self.assertEqual(2, self.client.post("/collections/videogames/cache/reset", headers=headers).get_json()["removed_entries"])
        self.assertIn("Switch", self.client.get("/collections/videogames/add-game-choices?platform=Switch", headers=headers).get_json()["platforms"])
        response = self.client.get("/collections/videogames/download", headers=headers)
        self.assertEqual(200, response.status_code)
        self.assertIn("attachment", response.headers["Content-Disposition"])
