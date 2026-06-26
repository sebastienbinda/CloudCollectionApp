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
from pathlib import Path
from io import BytesIO

import app as app_module
from services.library import LibraryResetAlreadyRunningError, LibraryResetJob
from services.library.admin_library_import_service import AdminLibraryImportInvalidFileError

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


class FakePlatformCatalogSyncResult:
    """Resultat factice de synchronisation du catalogue plateformes."""

    def to_dict(self):
        """Convertit le resultat factice en dictionnaire.

        Args:
            Aucun.

        Returns:
            dict: Compteurs de synchronisation factices.
        """

        return {
            "inserted_platforms": 2,
            "inserted_aliases": 3,
            "total_inserted": 5,
        }


class FakePlatformCatalogUpdateService:
    """Service factice de synchronisation du catalogue plateformes."""

    next_error = None
    update_calls = 0

    def update_from_resources(self):
        """Execute une synchronisation factice.

        Args:
            Aucun.

        Returns:
            FakePlatformCatalogSyncResult: Compteurs factices.

        Raises:
            Exception: Si une erreur configuree existe.
        """

        self.__class__.update_calls += 1
        if self.next_error:
            raise self.next_error
        return FakePlatformCatalogSyncResult()


class FakeLibraryServiceProvider:
    """Provider factice des services Bibliotheque."""

    reset_calls = 0

    def reset(self):
        """Capture l'invalidation du cache Bibliotheque.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.__class__.reset_calls += 1


class FakeAdminLibraryImportResult:
    """Resultat factice d'import CSV admin."""

    def to_dict(self):
        """Convertit le resultat factice en dictionnaire.

        Args:
            Aucun.

        Returns:
            dict: Compteurs d'import factices.
        """

        return {
            "linked_platforms": 1,
            "created_studios": 2,
            "created_games": 3,
            "warnings": {},
        }


class FakeAdminLibraryImportService:
    """Service factice d'import CSV admin."""

    next_error = None
    import_calls = []
    path_existed_during_call = False

    def import_csv_file(self, csv_file_path, original_filename=""):
        """Capture l'import CSV admin.

        Args:
            csv_file_path (str): Chemin temporaire recu.
            original_filename (str): Nom original recu.

        Returns:
            FakeAdminLibraryImportResult: Resultat factice.

        Raises:
            Exception: Si une erreur configuree existe.
        """

        self.__class__.import_calls.append((csv_file_path, original_filename))
        self.__class__.path_existed_during_call = Path(csv_file_path).exists()
        if self.next_error:
            raise self.next_error
        return FakeAdminLibraryImportResult()


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
        self.original_platform_catalog_update_service_factory = (
            app_module.library_controller.platform_catalog_update_service_factory
        )
        self.original_admin_import_service_factory = (
            app_module.library_controller.admin_import_service_factory
        )
        self.original_library_service_provider = app_module.library_controller.library_service_provider
        app_module.library_controller.reset_job_coordinator = FakeLibraryResetJobCoordinator()
        app_module.library_controller.platform_catalog_update_service_factory = (
            FakePlatformCatalogUpdateService
        )
        app_module.library_controller.admin_import_service_factory = FakeAdminLibraryImportService
        app_module.library_controller.library_service_provider = FakeLibraryServiceProvider()
        FakeLibraryResetJobCoordinator.next_error = None
        FakeLibraryResetJobCoordinator.next_job_id = 25
        FakeLibraryResetJobCoordinator.start_calls = 0
        FakePlatformCatalogUpdateService.next_error = None
        FakePlatformCatalogUpdateService.update_calls = 0
        FakeAdminLibraryImportService.next_error = None
        FakeAdminLibraryImportService.import_calls = []
        FakeAdminLibraryImportService.path_existed_during_call = False
        FakeLibraryServiceProvider.reset_calls = 0

    def tearDown(self):
        """Restaure le coordinateur de reset original.

        Args:
            Aucun.

        Returns:
            None: Les dependances globales sont restaurees.
        """

        app_module.library_controller.reset_job_coordinator = self.original_reset_job_coordinator
        app_module.library_controller.platform_catalog_update_service_factory = (
            self.original_platform_catalog_update_service_factory
        )
        app_module.library_controller.admin_import_service_factory = (
            self.original_admin_import_service_factory
        )
        app_module.library_controller.library_service_provider = self.original_library_service_provider
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
        """Verifie les metadonnees d'acces des routes admin Bibliotheque.

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
        sync_route = routes_by_key[("/api/library/platform-catalog/sync", ("POST",))]
        self.assertTrue(sync_route["requires_auth"])
        self.assertEqual(["Bearer"], sync_route["auth_schemes"])
        self.assertEqual(["ADMIN"], sync_route["required_profiles"])
        import_route = routes_by_key[("/api/library/import/csv", ("POST",))]
        self.assertTrue(import_route["requires_auth"])
        self.assertEqual(["Bearer"], import_route["auth_schemes"])
        self.assertEqual(["ADMIN"], import_route["required_profiles"])

    def test_sync_platform_catalog_requires_authentication(self):
        """Verifie que la synchronisation catalogue exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le refus HTTP.
        """

        response = self.client.post("/api/library/platform-catalog/sync")

        self.assertEqual(403, response.status_code)
        self.assertEqual(0, FakePlatformCatalogUpdateService.update_calls)
        self.assertEqual(0, FakeLibraryServiceProvider.reset_calls)

    def test_sync_platform_catalog_rejects_user_profile(self):
        """Verifie que la synchronisation catalogue est reservee aux admins.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le refus du profil USER.
        """

        response = self.client.post(
            "/api/library/platform-catalog/sync",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(403, response.status_code)
        self.assertEqual(0, FakePlatformCatalogUpdateService.update_calls)
        self.assertEqual(0, FakeLibraryServiceProvider.reset_calls)

    def test_sync_platform_catalog_adds_missing_rows_for_admin(self):
        """Verifie le contrat nominal de synchronisation catalogue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat 200.
        """

        response = self.client.post(
            "/api/library/platform-catalog/sync",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {
                "inserted_platforms": 2,
                "inserted_aliases": 3,
                "total_inserted": 5,
            },
            response.get_json(),
        )
        self.assertEqual(1, FakePlatformCatalogUpdateService.update_calls)
        self.assertEqual(1, FakeLibraryServiceProvider.reset_calls)

    def test_sync_platform_catalog_returns_error_when_service_fails(self):
        """Verifie le contrat d'erreur de la synchronisation catalogue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat 500.
        """

        FakePlatformCatalogUpdateService.next_error = RuntimeError("boom")

        response = self.client.post(
            "/api/library/platform-catalog/sync",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(500, response.status_code)
        self.assertEqual(
            {"error": "Unable to sync platform catalog."},
            response.get_json(),
        )
        self.assertEqual(1, FakePlatformCatalogUpdateService.update_calls)
        self.assertEqual(0, FakeLibraryServiceProvider.reset_calls)

    def test_import_library_csv_requires_authentication(self):
        """Verifie que l'import CSV admin exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le refus HTTP.
        """

        response = self.client.post("/api/library/import/csv")

        self.assertEqual(403, response.status_code)
        self.assertEqual([], FakeAdminLibraryImportService.import_calls)

    def test_import_library_csv_rejects_user_profile(self):
        """Verifie que l'import CSV admin est reserve aux admins.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le refus du profil USER.
        """

        response = self.client.post(
            "/api/library/import/csv",
            headers=self.get_user_auth_headers(),
            data={"library_file": (BytesIO(b"name,platform\nZelda,Switch\n"), "admin.csv")},
        )

        self.assertEqual(403, response.status_code)
        self.assertEqual([], FakeAdminLibraryImportService.import_calls)

    def test_import_library_csv_adds_games_for_admin_and_deletes_temporary_file(self):
        """Verifie le contrat nominal de l'import CSV admin.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse et le nettoyage temporaire.
        """

        response = self.client.post(
            "/api/library/import/csv",
            headers=self.get_admin_auth_headers(),
            data={"library_file": (BytesIO(b"name,platform\nZelda,Switch\n"), "admin.csv")},
        )

        temporary_path, original_filename = FakeAdminLibraryImportService.import_calls[0]
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            {
                "linked_platforms": 1,
                "created_studios": 2,
                "created_games": 3,
                "warnings": {},
            },
            response.get_json(),
        )
        self.assertEqual("admin.csv", original_filename)
        self.assertTrue(FakeAdminLibraryImportService.path_existed_during_call)
        self.assertFalse(Path(temporary_path).exists())
        self.assertEqual(1, FakeLibraryServiceProvider.reset_calls)

    def test_import_library_csv_returns_bad_request_without_file(self):
        """Verifie le refus sans fichier multipart.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat 400.
        """

        response = self.client.post(
            "/api/library/import/csv",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual({"error": "library_file est requis."}, response.get_json())
        self.assertEqual([], FakeAdminLibraryImportService.import_calls)

    def test_import_library_csv_returns_bad_request_when_service_rejects_file(self):
        """Verifie la reponse quand le service refuse le CSV.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les details d'erreur.
        """

        FakeAdminLibraryImportService.next_error = AdminLibraryImportInvalidFileError(
            ["Seuls les fichiers CSV sont acceptes."]
        )

        response = self.client.post(
            "/api/library/import/csv",
            headers=self.get_admin_auth_headers(),
            data={"library_file": (BytesIO(b"bad"), "admin.txt")},
        )

        temporary_path, _ = FakeAdminLibraryImportService.import_calls[0]
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            {
                "error": "Fichier CSV admin invalide.",
                "details": ["Seuls les fichiers CSV sont acceptes."],
            },
            response.get_json(),
        )
        self.assertFalse(Path(temporary_path).exists())
        self.assertEqual(0, FakeLibraryServiceProvider.reset_calls)
