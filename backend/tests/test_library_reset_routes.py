#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du contrat HTTP de reset Bibliotheque.

from datetime import datetime

import app as app_module
from services.library import LibraryResetAlreadyRunningError, LibraryResetJob

try:
    from tests.route_test_support import BaseAppRoutesTest
except ModuleNotFoundError:
    from route_test_support import BaseAppRoutesTest


class FakeLibraryResetJobCoordinator:
    """Coordinateur de reset Bibliotheque factice."""

    next_error = None
    next_job_id = 25
    start_calls = 0

    def start_reset(self, reset_task=None):
        """Lance un reset factice.

        Args:
            reset_task (Callable | None): Tache ignoree.

        Returns:
            LibraryResetJob: Job factice cree.

        Raises:
            LibraryResetAlreadyRunningError: Si une erreur configuree existe.
        """

        self.__class__.start_calls += 1
        if self.next_error:
            raise self.next_error
        return LibraryResetJob(self.next_job_id, datetime(2026, 6, 11, 12))


class LibraryResetRoutesTest(BaseAppRoutesTest):
    """Valide la route admin de reset Bibliotheque."""

    def setUp(self):
        """Prepare le client Flask avec un coordinateur factice.

        Args:
            Aucun.

        Returns:
            None: Le client Flask est configure.
        """

        super().setUp()
        self.original_reset_job_coordinator = app_module.library_controller.reset_job_coordinator
        app_module.library_controller.reset_job_coordinator = FakeLibraryResetJobCoordinator()
        FakeLibraryResetJobCoordinator.next_error = None
        FakeLibraryResetJobCoordinator.next_job_id = 25
        FakeLibraryResetJobCoordinator.start_calls = 0

    def tearDown(self):
        """Restaure le coordinateur de reset original.

        Args:
            Aucun.

        Returns:
            None: Les dependances globales sont restaurees.
        """

        app_module.library_controller.reset_job_coordinator = self.original_reset_job_coordinator
        super().tearDown()

    def test_reset_library_requires_authentication(self):
        """Verifie que le reset Bibliotheque exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le refus HTTP.
        """

        response = self.client.post("/api/library/reset")

        self.assertEqual(403, response.status_code)
        self.assertEqual(0, FakeLibraryResetJobCoordinator.start_calls)

    def test_reset_library_rejects_user_profile(self):
        """Verifie que le reset Bibliotheque est reserve aux administrateurs.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le refus du profil USER.
        """

        response = self.client.post(
            "/api/library/reset",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(403, response.status_code)
        self.assertEqual(0, FakeLibraryResetJobCoordinator.start_calls)

    def test_reset_library_starts_job_for_admin(self):
        """Verifie le lancement nominal du job de reset.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat 202.
        """

        response = self.client.post(
            "/api/library/reset",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(202, response.status_code)
        self.assertEqual({"job_id": 25}, response.get_json())
        self.assertEqual(1, FakeLibraryResetJobCoordinator.start_calls)

    def test_reset_library_returns_conflict_when_job_is_running(self):
        """Verifie le conflit quand un reset est deja en cours.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat 409.
        """

        FakeLibraryResetJobCoordinator.next_error = LibraryResetAlreadyRunningError(
            "Un reset de la Bibliotheque est deja en cours."
        )

        response = self.client.post(
            "/api/library/reset",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(409, response.status_code)
        self.assertEqual(
            {"error": "Un reset de la Bibliotheque est deja en cours."},
            response.get_json(),
        )

    def test_routes_catalog_exposes_admin_reset_contract(self):
        """Verifie les metadonnees d'acces de la route reset.

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
        reset_route = routes_by_key[("/api/library/reset", ("POST",))]

        self.assertTrue(reset_route["requires_auth"])
        self.assertEqual(["Bearer"], reset_route["auth_schemes"])
        self.assertEqual(["ADMIN"], reset_route["required_profiles"])
