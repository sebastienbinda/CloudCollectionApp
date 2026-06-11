#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du verrouillage des imports pendant un reset Bibliotheque.

from io import BytesIO

import app as app_module

try:
    from tests.route_test_support import BaseAppRoutesTest, FakeUserCollectionImportService
except ModuleNotFoundError:
    from route_test_support import BaseAppRoutesTest, FakeUserCollectionImportService


class FakeRunningLibraryResetCoordinator:
    """Coordinateur factice indiquant qu'un reset Bibliotheque est actif."""

    def is_reset_running(self) -> bool:
        """Indique qu'un reset est en cours.

        Args:
            Aucun.

        Returns:
            bool: Toujours `True` pour bloquer les imports en test.
        """

        return True


class UserCollectionImportLockingRoutesTest(BaseAppRoutesTest):
    """Valide le blocage des routes d'import pendant un reset Bibliotheque."""

    def setUp(self):
        """Prepare le controleur d'import avec un reset Bibliotheque actif.

        Args:
            Aucun.

        Returns:
            None: Le coordinateur factice est installe.
        """

        super().setUp()
        self.original_reset_job_coordinator = (
            app_module.user_collection_import_controller.reset_job_coordinator
        )
        app_module.user_collection_import_controller.reset_job_coordinator = (
            FakeRunningLibraryResetCoordinator()
        )

    def tearDown(self):
        """Restaure le coordinateur de reset original.

        Args:
            Aucun.

        Returns:
            None: Les dependances globales sont restaurees.
        """

        app_module.user_collection_import_controller.reset_job_coordinator = (
            self.original_reset_job_coordinator
        )
        super().tearDown()

    def test_import_endpoints_return_forbidden_while_library_reset_is_running(self):
        """Verifie le blocage des routes d'import pendant le reset.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les statuts et messages.
        """

        expected_payload = {
            "error": app_module.user_collection_import_controller.RESET_IN_PROGRESS_ERROR
        }
        headers = self.get_user_auth_headers()
        endpoints = [
            ("get", "/api/users/import/", {}),
            (
                "post",
                "/api/users/import/file/libreoffice_ods",
                {
                    "data": {"collection_file": (BytesIO(b"ods"), "collection.ods")},
                    "content_type": "multipart/form-data",
                },
            ),
            ("post", "/api/users/import/analyze/libreoffice_ods", {}),
            ("post", "/api/users/import", {"json": self._valid_description()}),
            ("post", "/api/users/collection/reinit", {}),
        ]

        for method_name, url, request_kwargs in endpoints:
            response = getattr(self.client, method_name)(
                url,
                headers=headers,
                **request_kwargs,
            )
            self.assertEqual(403, response.status_code, url)
            self.assertEqual(expected_payload, response.get_json(), url)

        self.assertIsNone(FakeUserCollectionImportService.last_call)

    def test_authentication_stays_prioritary_while_library_reset_is_running(self):
        """Verifie que le reset ne contourne pas les regles d'authentification.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le message d'authentification.
        """

        response = self.client.get("/api/users/import/")

        self.assertEqual(403, response.status_code)
        self.assertEqual({"error": "Token Bearer manquant."}, response.get_json())

    def _valid_description(self):
        """Construit une description de fichier valide.

        Args:
            Aucun.

        Returns:
            dict: Description JSON compatible avec l'import utilisateur.
        """

        return {
            "file_type": "libreoffice_ods",
            "wishlist": {"mode": "none"},
            "single_sheet_conf": {
                "data_range": "A1:H200",
                "header_row": 1,
                "column_information": {
                    "name": "A",
                    "platform": "B",
                    "studio": "C",
                    "release_date": "D",
                },
            },
        }
