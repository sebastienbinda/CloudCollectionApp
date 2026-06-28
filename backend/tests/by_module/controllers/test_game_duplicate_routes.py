#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests des routes HTTP de gestion des doublons de jeux.

import app as app_module

try:
    from tests.support.route_test_support import BaseAppRoutesTest
except ModuleNotFoundError:
    from tests.support.route_test_support import BaseAppRoutesTest


class FakeDuplicateMergeResult:
    """Resultat de fusion factice."""

    def to_dict(self):
        """Convertit le resultat en dictionnaire.

        Args:
            Aucun.

        Returns:
            dict: Payload de fusion.
        """

        return {"action": "merge", "remapped_user_count": 2, "processing_time_ms": 1}


class FakeGameDuplicateRouteService:
    """Service doublon factice pour les routes."""

    report_calls = []
    reject_calls = []
    merge_calls = []

    def report_duplicate(self, user_id, game_id):
        """Capture le signalement.

        Args:
            user_id (int): Identifiant utilisateur.
            game_id (int): Identifiant du jeu.

        Returns:
            dict: Confirmation factice.
        """

        self.__class__.report_calls.append((user_id, game_id))
        return {"game_id": game_id, "duplicate_flag": True}

    def get_duplicate_game(self, game_id):
        """Retourne un jeu signale factice.

        Args:
            game_id (int): Identifiant du jeu.

        Returns:
            dict: Jeu factice.
        """

        return {"id": game_id, "name": "Sonic the edgedog", "duplicate_flag": True}

    def search_candidates(self, duplicate_game_id, name_query="", limit=50):
        """Retourne les candidats factices.

        Args:
            duplicate_game_id (int): Identifiant du doublon.
            name_query (str): Filtre recu.
            limit (int): Limite recue.

        Returns:
            list[dict]: Candidats factices.
        """

        return [{"id": 2, "name": "Sonic"}]

    def reject_duplicate(self, duplicate_game_id):
        """Capture le refus.

        Args:
            duplicate_game_id (int): Identifiant du doublon.

        Returns:
            dict: Resultat factice.
        """

        self.__class__.reject_calls.append(duplicate_game_id)
        return {"action": "reject", "duplicate_game_id": duplicate_game_id}

    def merge_duplicate(
        self,
        duplicate_game_id,
        target_game_id,
        selected_values=None,
        keep_duplicate_name_as_alias=True,
    ):
        """Capture la fusion.

        Args:
            duplicate_game_id (int): Jeu supprime.
            target_game_id (int): Jeu conserve.
            selected_values (dict | None): Valeurs choisies.
            keep_duplicate_name_as_alias (bool): Conservation en alias.

        Returns:
            FakeDuplicateMergeResult: Resultat factice.
        """

        self.__class__.merge_calls.append(
            (duplicate_game_id, target_game_id, selected_values, keep_duplicate_name_as_alias)
        )
        return FakeDuplicateMergeResult()


class GameDuplicateRoutesTest(BaseAppRoutesTest):
    """Valide les routes de signalement et correction de doublons."""

    def setUp(self):
        """Prepare les fakes de routes.

        Args:
            Aucun.

        Returns:
            None: Les services sont injectes.
        """

        super().setUp()
        self.original_library_duplicate_service_factory = (
            app_module.library_controller.duplicate_service_factory
        )
        app_module.game_controller.duplicate_service_factory = FakeGameDuplicateRouteService
        app_module.library_controller.duplicate_service_factory = FakeGameDuplicateRouteService
        FakeGameDuplicateRouteService.report_calls = []
        FakeGameDuplicateRouteService.reject_calls = []
        FakeGameDuplicateRouteService.merge_calls = []

    def tearDown(self):
        """Restaure le service de doublons admin.

        Args:
            Aucun.

        Returns:
            None: Les dependances sont restaurees.
        """

        app_module.library_controller.duplicate_service_factory = (
            self.original_library_duplicate_service_factory
        )
        super().tearDown()

    def test_report_duplicate_requires_user_authentication(self):
        """Verifie que le signalement refuse les appels anonymes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut HTTP.
        """

        response = self.client.post("/api/library/games/3/doublon")

        self.assertEqual(403, response.status_code)

    def test_report_duplicate_uses_authenticated_user(self):
        """Verifie le signalement par un utilisateur connecte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'appel service.
        """

        response = self.client.post(
            "/api/library/games/3/doublon",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual([(7, 3)], FakeGameDuplicateRouteService.report_calls)
        self.assertTrue(response.get_json()["duplicate_flag"])

    def test_admin_duplicate_routes_reject_user_profile(self):
        """Verifie que les corrections sont reservees aux administrateurs.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut HTTP.
        """

        response = self.client.post(
            "/api/library/games/doublon",
            headers=self.get_user_auth_headers(),
            json={"action": "reject", "duplicate_game_id": 3},
        )

        self.assertEqual(403, response.status_code)

    def test_admin_can_reject_duplicate(self):
        """Verifie le refus administrateur d'un doublon.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'appel service.
        """

        response = self.client.post(
            "/api/library/games/doublon",
            headers=self.get_admin_auth_headers(),
            json={"action": "reject", "duplicate_game_id": 3},
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual([3], FakeGameDuplicateRouteService.reject_calls)
        self.assertEqual("reject", response.get_json()["result"]["action"])

    def test_admin_can_merge_duplicate(self):
        """Verifie la fusion administrateur d'un doublon.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'appel service.
        """

        response = self.client.post(
            "/api/library/games/doublon",
            headers=self.get_admin_auth_headers(),
            json={
                "action": "merge",
                "duplicate_game_id": 3,
                "target_game_id": 2,
                "selected_values": {"release_date": "1991-06-23"},
                "keep_duplicate_name_as_alias": True,
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [(3, 2, {"release_date": "1991-06-23"}, True)],
            FakeGameDuplicateRouteService.merge_calls,
        )
        self.assertEqual(2, response.get_json()["result"]["remapped_user_count"])


if __name__ == "__main__":
    unittest.main()
