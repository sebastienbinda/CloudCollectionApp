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
            "/collections/JeuxVideo/platforms",
            "/collections/JeuxVideo/search?platform=Switch",
            "/collections/JeuxVideo/game-search?q=mario",
            "/collections/JeuxVideo/home",
            "/collections/JeuxVideo/column-values?platform=Switch",
            "/collections/JeuxVideo/cache/reset",
            "/collections/JeuxVideo/ods/download",
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

        self.assertEqual(["Switch", "Playstation"], self.client.get("/collections/JeuxVideo/platforms", headers=headers).get_json()["platforms"])
        self.assertEqual(45, self.client.get("/collections/JeuxVideo/search?platform=Switch", headers=headers).get_json()[0]["Prix d'achat"])
        self.assertEqual(45, self.client.get("/collections/JeuxVideo/home", headers=headers).get_json()["totals"]["total_price"])
        self.assertEqual([45], self.client.get("/collections/JeuxVideo/column-values?platform=Switch", headers=headers).get_json()["values_by_column"]["Prix d'achat"])
        self.assertEqual("Mario Kart", self.client.get("/collections/JeuxVideo/game-search?q=mario", headers=headers).get_json()["items"][0]["Nom du jeu"])

    def test_cache_reset_add_game_choices_and_download(self):
        """Verifie les routes utilitaires de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les reponses.
        """

        headers = self.get_auth_headers()

        self.assertEqual(2, self.client.post("/collections/JeuxVideo/cache/reset", headers=headers).get_json()["removed_entries"])
        self.assertIn("Switch", self.client.get("/collections/JeuxVideo/add-game-choices?platform=Switch", headers=headers).get_json()["platforms"])
        response = self.client.get("/collections/JeuxVideo/ods/download", headers=headers)
        self.assertEqual(200, response.status_code)
        self.assertIn("attachment", response.headers["Content-Disposition"])
