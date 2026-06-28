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
# Description : tests des routes mutantes jeux.

try:
    from tests.support.route_test_support import BaseAppRoutesTest
except ModuleNotFoundError:
    from tests.support.route_test_support import BaseAppRoutesTest


class GameMutationRoutesTest(BaseAppRoutesTest):
    """Valide les routes mutantes jeux."""

    def test_add_game_route_requires_valid_token(self):
        """Verifie l'authentification de l'ajout de jeu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 401.
        """

        response = self.client.post("/collections/videogames/games", headers={"Authorization": "Bearer invalid-token"}, json={"platform": "Switch", "Nom du jeu": "Mario"})

        self.assertEqual(401, response.status_code)

    def test_add_delete_update_game_routes_return_not_implemented(self):
        """Verifie les mutations futures de jeux de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les payloads.
        """

        headers = self.get_auth_headers()

        self.assertEqual(501, self.client.post("/collections/videogames/games", headers=headers, json={"platform": "Switch", "Nom du jeu": "Mario"}).status_code)
        self.assertEqual(501, self.client.delete("/collections/videogames/games", headers=headers, json={"platform": "Switch", "Nom du jeu": "Mario"}).status_code)
        self.assertEqual(501, self.client.put("/collections/videogames/games", headers=headers, json={"platform": "Switch", "updated": {"Nom du jeu": "Mario 2"}}).status_code)

    def test_wishlist_mutation_routes_are_not_registered(self):
        """Verifie que les mutations wishlist sont supprimees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les payloads.
        """

        headers = self.get_auth_headers()

        self.assertEqual(404, self.client.post("/collections/videogames/wishlist/games", headers=headers, json={"Nom du jeu": "Chrono", "Console": "Switch", "Studio": "Square"}).status_code)
        self.assertEqual(404, self.client.delete("/collections/videogames/wishlist/games", headers=headers, json={"Nom du jeu": "Chrono", "Console": "Switch"}).status_code)
        self.assertEqual(404, self.client.put("/collections/videogames/wishlist/games", headers=headers, json={"updated": {"Nom du jeu": "Chrono", "Console": "Switch", "Studio": "Square"}}).status_code)
