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

from services.users.user_collection_import_service import (
    UserCollectionImportConflictError,
    UserCollectionImportInvalidFileError,
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

        self.assertEqual({"has_collection": False}, self.client.get("/api/users/me/collection", headers=headers).get_json())
        FakeUserCollectionImportRepository.has_collection = True
        self.assertEqual({"has_collection": True}, self.client.get("/api/users/me/collection", headers=headers).get_json())

    def test_import_current_user_collection_returns_counts(self):
        """Verifie l'import nominal d'une collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les compteurs.
        """

        response = self.client.post(
            "/api/users/import",
            headers=self.get_user_auth_headers(),
            data={"collection_file": (BytesIO(b"ods"), "collection.ods")},
            content_type="multipart/form-data",
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual(4, response.get_json()["associated_games"])
        self.assertEqual(7, FakeUserCollectionImportService.last_call[0])

    def test_import_current_user_collection_requires_file(self):
        """Verifie le refus sans fichier.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident 400.
        """

        response = self.client.post("/api/users/import", headers=self.get_user_auth_headers())

        self.assertEqual(400, response.status_code)

    def test_import_current_user_collection_maps_domain_errors(self):
        """Verifie le mapping des erreurs d'import.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les statuts HTTP.
        """

        cases = [
            (UserCollectionImportConflictError("Collection deja importee."), 409),
            (UserCollectionImportInvalidFileError("Fichier invalide."), 400),
            (UserCollectionImportTooLargeError("Fichier trop volumineux."), 413),
            (UserCollectionImportUnexpectedError("boom"), 500),
        ]
        for error, expected_status in cases:
            FakeUserCollectionImportService.next_error = error
            response = self.client.post(
                "/api/users/import",
                headers=self.get_user_auth_headers(),
                data={"collection_file": (BytesIO(b"ods"), "collection.ods")},
                content_type="multipart/form-data",
            )
            self.assertEqual(expected_status, response.status_code)
