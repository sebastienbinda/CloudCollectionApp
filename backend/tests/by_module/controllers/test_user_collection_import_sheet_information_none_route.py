#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : test route du mode d'import multi-onglets sans information d'onglet.

try:
    from tests.support.route_test_support import (
        BaseAppRoutesTest,
        FakeUserCollectionImportService,
    )
except ModuleNotFoundError:
    from tests.support.route_test_support import (
        BaseAppRoutesTest,
        FakeUserCollectionImportService,
    )


class UserCollectionImportSheetInformationNoneRouteTest(BaseAppRoutesTest):
    """Valide le contrat HTTP du mode sans information portee par l'onglet."""

    def test_import_endpoint_accepts_missing_sheet_information_with_platform_column(self):
        """Verifie que le endpoint accepte la plateforme portee par une colonne.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut et la description transmise.
        """

        response = self.client.post(
            "/api/users/import",
            headers=self.get_user_auth_headers(),
            json={
                "file_type": "libreoffice_ods",
                "wishlist": {"mode": "none"},
                "multiple_sheets_conf": {
                    "shared_layout": {
                        "included_sheets": ["Janvier", "Fevrier"],
                        "data_range": "A1:C200",
                        "header_row": 1,
                        "column_information": {
                            "name": "A",
                            "platform": "B",
                            "studio": "C",
                        },
                    },
                },
            },
        )

        self.assertEqual(201, response.status_code)
        file_description = FakeUserCollectionImportService.last_call[1].to_dict()
        self.assertNotIn("sheet_information", file_description["multiple_sheets_conf"])
        self.assertEqual(
            "B",
            file_description["multiple_sheets_conf"]["shared_layout"]["column_information"]["platform"],
        )
