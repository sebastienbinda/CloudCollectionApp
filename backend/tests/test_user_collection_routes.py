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
# Description : tests des routes de collection utilisateur.

from io import BytesIO

from services.collection.imports import CollectionFileDescriptionValidationError
from services.users.user_collection_import_service import (
    UserCollectionImportInvalidFileError,
    UserCollectionImportNotFoundError,
    UserCollectionImportTemporaryFileMissingError,
    UserCollectionImportTooLargeError,
    UserCollectionImportUnexpectedError,
)

try:
    from tests.route_test_support import (
        BaseAppRoutesTest,
        FakeUserCollectionImportRepository,
        FakeUserCollectionImportService,
    )
except ModuleNotFoundError:
    from route_test_support import (
        BaseAppRoutesTest,
        FakeUserCollectionImportRepository,
        FakeUserCollectionImportService,
    )


class UserCollectionRoutesTest(BaseAppRoutesTest):
    """Valide les routes d'import et statut de collection utilisateur."""

    def test_current_user_collection_status_requires_authentication(self):
        """Verifie que le statut collection exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 403.
        """

        self.assertEqual(403, self.client.get("/api/users/me/collection").status_code)

    def test_current_user_collection_status_returns_false_and_true(self):
        """Verifie les deux statuts de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les payloads.
        """

        headers = self.get_user_auth_headers()

        self.assertEqual(
            {"has_collection": False},
            self.client.get("/api/users/me/collection", headers=headers).get_json(),
        )
        FakeUserCollectionImportRepository.has_collection = True
        self.assertEqual(
            {"has_collection": True},
            self.client.get("/api/users/me/collection", headers=headers).get_json(),
        )

    def test_current_user_import_configuration_requires_authentication(self):
        """Verifie que la recuperation de configuration exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 403.
        """

        self.assertEqual(403, self.client.get("/api/users/import/").status_code)

    def test_current_user_import_configuration_returns_saved_configuration(self):
        """Verifie la recuperation nominale de la configuration sauvegardee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut et le payload.
        """

        saved_configuration = self._valid_description()
        FakeUserCollectionImportRepository.import_configuration = saved_configuration

        response = self.client.get(
            "/api/users/import/",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(saved_configuration, response.get_json())

    def test_current_user_import_configuration_returns_not_found_without_configuration(self):
        """Verifie le 404 sans configuration sauvegardee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut et le message.
        """

        response = self.client.get(
            "/api/users/import/",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(404, response.status_code)
        self.assertEqual({"error": "Configuration d'import introuvable."}, response.get_json())

    def test_upload_current_user_collection_import_file_returns_created(self):
        """Verifie le depot temporaire nominal d'une collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut et l'appel service.
        """

        response = self.client.post(
            "/api/users/import/file/libreoffice_ods",
            headers=self.get_user_auth_headers(),
            data={"collection_file": (BytesIO(b"ods"), "collection.ods")},
            content_type="multipart/form-data",
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual({"uploaded": True}, response.get_json())
        self.assertEqual(7, FakeUserCollectionImportService.last_call[0])
        self.assertEqual("collection.ods", FakeUserCollectionImportService.last_call[2])

    def test_analyze_current_user_collection_import_file_returns_sheets(self):
        """Verifie l'analyse nominale du fichier temporaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les onglets retournes.
        """

        response = self.client.post(
            "/api/users/import/analyze/libreoffice_ods",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual({"sheets": ["Switch", "NES"]}, response.get_json())
        self.assertEqual(7, FakeUserCollectionImportService.last_call[0])

    def test_import_current_user_collection_returns_counts(self):
        """Verifie l'import nominal d'une collection depuis le fichier temporaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les compteurs.
        """

        response = self.client.post(
            "/api/users/import",
            headers=self.get_user_auth_headers(),
            json=self._valid_description(),
        )

        self.assertEqual(201, response.status_code)
        payload = response.get_json()
        self.assertEqual(1, payload["linked_platforms"])
        self.assertNotIn("created_platforms", payload)
        self.assertEqual(4, payload["associated_games"])
        self.assertEqual(0, payload["wishlisted_games"])
        self.assertEqual(
            {
                "invalid_wishlist": 0,
                "invalid_wishlist_values_found": [],
                "invalid_games": [],
                "platform_matches": [],
                "skipped_games": [],
            },
            payload["warnings"],
        )
        self.assertEqual(7, FakeUserCollectionImportService.last_call[0])
        self.assertIsNotNone(FakeUserCollectionImportService.last_call[1])

    def test_reinitialize_current_user_collection_requires_authentication(self):
        """Verifie que la reinitialisation collection exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 403.
        """

        response = self.client.post("/api/users/collection/reinit")

        self.assertEqual(403, response.status_code)

    def test_reinitialize_current_user_collection_returns_success(self):
        """Verifie la reinitialisation nominale de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut, le payload et l'utilisateur.
        """

        response = self.client.post(
            "/api/users/collection/reinit",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual({"reinitialized": True}, response.get_json())
        self.assertEqual((7,), FakeUserCollectionImportService.last_call)

    def test_reinitialize_current_user_collection_maps_not_found(self):
        """Verifie le mapping 404 quand aucune collection n'existe.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat d'erreur.
        """

        FakeUserCollectionImportService.next_error = UserCollectionImportNotFoundError(
            "Collection introuvable."
        )

        response = self.client.post(
            "/api/users/collection/reinit",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(404, response.status_code)
        self.assertEqual({"error": "Collection introuvable."}, response.get_json())

    def test_reinitialize_current_user_collection_maps_unexpected_error(self):
        """Verifie le mapping 500 d'une erreur inattendue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat d'erreur.
        """

        FakeUserCollectionImportService.next_error = UserCollectionImportUnexpectedError(
            "boom"
        )

        response = self.client.post(
            "/api/users/collection/reinit",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(500, response.status_code)
        self.assertEqual(
            {"error": "Unable to reinitialize collection."},
            response.get_json(),
        )

    def test_import_current_user_collection_accepts_multiple_sheet_modes(self):
        """Verifie les modes multi-onglets valides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les statuts HTTP.
        """

        for description in [self._valid_shared_layout_description(), self._valid_sheets_description()]:
            response = self.client.post(
                "/api/users/import",
                headers=self.get_user_auth_headers(),
                json=description,
            )
            self.assertEqual(201, response.status_code)

    def test_upload_current_user_collection_import_file_requires_file(self):
        """Verifie le refus sans fichier.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 400.
        """

        response = self.client.post(
            "/api/users/import/file/libreoffice_ods",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(400, response.status_code)

    def test_import_current_user_collection_requires_file_description(self):
        """Verifie le refus sans body JSON.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 422 et les details.
        """

        response = self.client.post("/api/users/import", headers=self.get_user_auth_headers())

        self.assertEqual(422, response.status_code)
        self.assertEqual("Configuration invalide.", response.get_json()["error"])
        self.assertTrue(response.get_json()["details"])

    def test_import_current_user_collection_rejects_invalid_json_description(self):
        """Verifie le refus d'une description JSON invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 422 et les details.
        """

        response = self.client.post(
            "/api/users/import",
            headers=self.get_user_auth_headers(),
            data="{invalid-json",
            content_type="application/json",
        )

        self.assertEqual(422, response.status_code)
        self.assertEqual(["JSON invalide."], response.get_json()["details"])

    def test_import_current_user_collection_maps_validation_error(self):
        """Verifie le mapping 422 d'une erreur de validation de configuration.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le format d'erreur.
        """

        FakeUserCollectionImportService.next_error = CollectionFileDescriptionValidationError(
            ["file_type inconnu."]
        )
        response = self.client.post(
            "/api/users/import",
            headers=self.get_user_auth_headers(),
            json=self._valid_description(),
        )

        self.assertEqual(422, response.status_code)
        self.assertEqual(
            {"error": "Configuration invalide.", "details": ["file_type inconnu."]},
            response.get_json(),
        )

    def test_import_current_user_collection_maps_domain_errors(self):
        """Verifie le mapping des erreurs d'import.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les statuts HTTP.
        """

        cases = [
            (UserCollectionImportInvalidFileError("Fichier invalide."), 400),
            (UserCollectionImportTemporaryFileMissingError("Fichier temporaire introuvable."), 404),
            (UserCollectionImportTooLargeError("Fichier trop volumineux."), 413),
            (UserCollectionImportUnexpectedError("boom"), 500),
        ]
        for error, expected_status in cases:
            FakeUserCollectionImportService.next_error = error
            response = self.client.post(
                "/api/users/import",
                headers=self.get_user_auth_headers(),
                json=self._valid_description(),
            )
            self.assertEqual(expected_status, response.status_code)
            if expected_status == 400:
                self.assertIn("details", response.get_json())

    def test_upload_current_user_collection_import_file_maps_domain_errors(self):
        """Verifie le mapping des erreurs du depot temporaire."""

        cases = [
            (UserCollectionImportInvalidFileError("Fichier invalide."), 400),
            (UserCollectionImportTooLargeError("Fichier trop volumineux."), 413),
        ]
        for error, expected_status in cases:
            FakeUserCollectionImportService.next_error = error
            response = self.client.post(
                "/api/users/import/file/libreoffice_ods",
                headers=self.get_user_auth_headers(),
                data={"collection_file": (BytesIO(b"ods"), "collection.ods")},
                content_type="multipart/form-data",
            )
            self.assertEqual(expected_status, response.status_code)

    def test_analyze_current_user_collection_import_file_maps_errors(self):
        """Verifie le mapping des erreurs de l'analyse."""

        cases = [
            (UserCollectionImportTemporaryFileMissingError("Fichier temporaire introuvable."), 404),
            (UserCollectionImportInvalidFileError("Fichier invalide."), 422),
        ]
        for error, expected_status in cases:
            FakeUserCollectionImportService.next_error = error
            response = self.client.post(
                "/api/users/import/analyze/libreoffice_ods",
                headers=self.get_user_auth_headers(),
            )
            self.assertEqual(expected_status, response.status_code)

    def _valid_description(self):
        """Construit une description de fichier valide pour les routes.

        Args:
            Aucun.

        Returns:
            dict: Description JSON compatible avec le contrat d'import.
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

    def _valid_shared_layout_description(self):
        """Construit une description multi-onglets a layout partage.

        Args:
            Aucun.

        Returns:
            dict: Description JSON compatible.
        """

        return {
            "file_type": "libreoffice_ods",
            "wishlist": {"mode": "none"},
            "multiple_sheets_conf": {
                "sheet_information": "platform",
                "shared_layout": {
                    "data_range": "A1:D200",
                    "header_row": 1,
                    "column_information": {
                        "name": "A",
                        "studio": "C",
                        "release_date": "D",
                    },
                },
            },
        }

    def _valid_sheets_description(self):
        """Construit une description multi-onglets avec layout par onglet.

        Args:
            Aucun.

        Returns:
            dict: Description JSON compatible.
        """

        return {
            "file_type": "libreoffice_ods",
            "wishlist": {"mode": "none"},
            "multiple_sheets_conf": {
                "sheets": [
                    {
                        "sheet_name": "Switch",
                        "sheet_information": "platform",
                        "data_range": "A1:D200",
                        "header_row": 1,
                        "column_information": {
                            "name": "A",
                            "studio": "C",
                            "release_date": "D",
                        },
                    }
                ]
            },
        }
