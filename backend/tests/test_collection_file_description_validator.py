#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du contrat JSON de configuration d'import.

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.collection.imports import (  # noqa: E402
    CollectionFileDescriptionValidationError,
    CollectionFileDescriptionValidator,
    CollectionFileType,
    CollectionImportField,
)


class CollectionFileDescriptionValidatorTest(unittest.TestCase):
    """Valide le parsing et les erreurs du contrat d'import configurable."""

    def setUp(self):
        """Prepare le validateur teste.

        Args:
            Aucun.

        Returns:
            None: Le validateur est initialise.
        """

        self.validator = CollectionFileDescriptionValidator()

    def test_valid_single_sheet_configuration(self):
        """Verifie une configuration feuille unique valide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le DTO.
        """

        description = self.validator.validate(self._single_sheet_payload())

        self.assertEqual(CollectionFileType.LIBREOFFICE_ODS, description.file_type)
        self.assertIsNotNone(description.single_sheet_conf)
        self.assertEqual(
            "A",
            description.single_sheet_conf.column_information[CollectionImportField.NAME],
        )
        self.assertEqual(self._single_sheet_payload(), description.to_dict())

    def test_valid_shared_layout_configuration(self):
        """Verifie une configuration multi-onglets avec layout partage.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le DTO.
        """

        payload = {
            "file_type": "libreoffice_ods",
            "wishlist": {"mode": "none"},
            "multiple_sheets_conf": {
                "sheet_information": "platform",
                "shared_layout": {
                    "included_sheets": ["Switch", "NES"],
                    "data_range": "A1:H200",
                    "header_row": 1,
                    "column_information": {
                        "name": "A",
                        "studio": "C",
                        "release_date": "D",
                    },
                },
            },
        }

        description = self.validator.validate(payload, {"Switch", "NES"})

        self.assertIsNotNone(description.multiple_sheets_conf.shared_layout)
        self.assertEqual(
            CollectionImportField.PLATFORM,
            description.multiple_sheets_conf.sheet_information,
        )

    def test_valid_shared_layout_configuration_with_excluded_sheets(self):
        """Verifie une configuration multi-onglets avec exclusions."""

        payload = {
            "file_type": "libreoffice_ods",
            "wishlist": {"mode": "none"},
            "multiple_sheets_conf": {
                "sheet_information": "platform",
                "shared_layout": {
                    "excluded_sheets": ["Accueil", "Liste de souhaits"],
                    "data_range": "A1:H200",
                    "header_row": 1,
                    "column_information": {
                        "name": "A",
                        "studio": "C",
                        "release_date": "D",
                    },
                },
            },
        }

        description = self.validator.validate(payload, {"Switch", "Accueil", "Liste de souhaits"})

        self.assertEqual(
            ["Accueil", "Liste de souhaits"],
            description.multiple_sheets_conf.shared_layout.excluded_sheets,
        )
        self.assertEqual(payload, description.to_dict())

    def test_valid_per_sheet_configuration(self):
        """Verifie une configuration multi-onglets avec layout par onglet.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le DTO.
        """

        payload = {
            "file_type": "libreoffice_ods",
            "wishlist": {"mode": "none"},
            "multiple_sheets_conf": {
                "sheets": [
                    {
                        "sheet_name": "Playstation",
                        "sheet_information": "platform",
                        "data_range": "A1:H200",
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

        description = self.validator.validate(payload)

        self.assertEqual(
            "Playstation",
            description.multiple_sheets_conf.sheets[0].sheet_name,
        )

    def test_parse_json_text_rejects_missing_and_invalid_json(self):
        """Verifie les erreurs de champ absent et JSON invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les details.
        """

        self._assert_errors(None, ["collection_file_description est requis."])
        with self.assertRaises(CollectionFileDescriptionValidationError) as context:
            self.validator.parse_json_text("{bad")
        self.assertEqual(["JSON invalide."], context.exception.details)

    def test_rejects_unknown_file_type(self):
        """Verifie le refus d'un type de fichier inconnu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        payload = self._single_sheet_payload()
        payload["file_type"] = "excel_xlsx"

        self._assert_errors(payload, ["file_type inconnu."])

    def test_rejects_mode_conflicts(self):
        """Verifie le refus des modes concurrents.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les erreurs d'exclusivite.
        """

        payload = self._single_sheet_payload()
        payload["multiple_sheets_conf"] = {"shared_layout": payload["single_sheet_conf"]}
        self._assert_errors(
            payload,
            ["single_sheet_conf et multiple_sheets_conf sont exclusifs."],
        )

        payload = {"file_type": "libreoffice_ods"}
        self._assert_errors(payload, ["un mode de configuration est requis."])

        payload = {
            "file_type": "libreoffice_ods",
            "multiple_sheets_conf": {
                "shared_layout": self._single_sheet_payload()["single_sheet_conf"],
                "sheets": [],
            },
        }
        self._assert_errors(payload, ["shared_layout et sheets sont exclusifs."])

    def test_rejects_missing_required_column(self):
        """Verifie le refus d'une colonne obligatoire absente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        payload = self._single_sheet_payload()
        del payload["single_sheet_conf"]["column_information"]["name"]

        self._assert_errors(payload, ["colonne obligatoire manquante: name."])

    def test_rejects_column_out_of_range(self):
        """Verifie le refus d'une colonne hors plage.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        payload = self._single_sheet_payload()
        payload["single_sheet_conf"]["data_range"] = "A1:C200"
        payload["single_sheet_conf"]["column_information"]["release_date"] = "D"

        self._assert_errors(payload, ["colonne hors data_range: release_date."])

    def test_rejects_header_row_out_of_range(self):
        """Verifie le refus d'une ligne d'en-tete hors plage.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        payload = self._single_sheet_payload()
        payload["single_sheet_conf"]["data_range"] = "A2:H200"
        payload["single_sheet_conf"]["header_row"] = 1

        self._assert_errors(payload, ["header_row hors data_range."])

    def test_rejects_unknown_sheet_information(self):
        """Verifie le refus d'une information d'onglet inconnue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        payload = {
            "file_type": "libreoffice_ods",
            "multiple_sheets_conf": {
                "sheet_information": "unknown",
                "shared_layout": self._single_sheet_payload()["single_sheet_conf"],
            },
        }

        self._assert_errors(
            payload,
            ["multiple_sheets_conf.sheet_information inconnu."],
        )

    def test_rejects_sheet_information_also_present_as_column(self):
        """Verifie le refus d'un champ porte aussi declare en colonne.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        payload = {
            "file_type": "libreoffice_ods",
            "multiple_sheets_conf": {
                "sheet_information": "platform",
                "shared_layout": self._single_sheet_payload()["single_sheet_conf"],
            },
        }

        self._assert_errors(
            payload,
            ["sheet_information est aussi present dans column_information."],
        )

    def test_rejects_missing_included_sheet_when_available_sheets_are_known(self):
        """Verifie le refus d'un onglet inclus absent du fichier.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        payload = {
            "file_type": "libreoffice_ods",
            "multiple_sheets_conf": {
                "sheet_information": "platform",
                "shared_layout": {
                    "included_sheets": ["Switch", "Missing"],
                    "data_range": "A1:H200",
                    "header_row": 1,
                    "column_information": {
                        "name": "A",
                        "studio": "C",
                        "release_date": "D",
                    },
                },
            },
        }

        self._assert_errors(
            payload,
            ["onglet absent du fichier: Missing."],
            available_sheet_names={"Switch"},
        )

    def test_rejects_missing_excluded_sheet_when_available_sheets_are_known(self):
        """Verifie le refus d'un onglet exclu absent du fichier."""

        payload = {
            "file_type": "libreoffice_ods",
            "multiple_sheets_conf": {
                "sheet_information": "platform",
                "shared_layout": {
                    "excluded_sheets": ["Missing"],
                    "data_range": "A1:H200",
                    "header_row": 1,
                    "column_information": {
                        "name": "A",
                        "studio": "C",
                        "release_date": "D",
                    },
                },
            },
        }

        self._assert_errors(
            payload,
            ["onglet absent du fichier: Missing."],
            available_sheet_names={"Switch"},
        )

    def test_rejects_included_and_excluded_sheets_together(self):
        """Verifie le refus d'une selection et exclusion simultanees."""

        payload = {
            "file_type": "libreoffice_ods",
            "multiple_sheets_conf": {
                "sheet_information": "platform",
                "shared_layout": {
                    "included_sheets": ["Switch"],
                    "excluded_sheets": ["NES"],
                    "data_range": "A1:H200",
                    "header_row": 1,
                    "column_information": {
                        "name": "A",
                        "studio": "C",
                        "release_date": "D",
                    },
                },
            },
        }

        self._assert_errors(
            payload,
            ["multiple_sheets_conf.shared_layout.included_sheets et excluded_sheets sont exclusifs."],
        )

    def test_rejects_missing_or_empty_sheet_name(self):
        """Verifie le refus d'un onglet declare sans nom.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        payload = {
            "file_type": "libreoffice_ods",
            "multiple_sheets_conf": {
                "sheets": [
                    {
                        "sheet_name": " ",
                        "sheet_information": "platform",
                        "data_range": "A1:H200",
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

        self._assert_errors(
            payload,
            ["multiple_sheets_conf.sheets[0].sheet_name est obligatoire."],
        )

    def _single_sheet_payload(self):
        """Construit une configuration feuille unique valide.

        Args:
            Aucun.

        Returns:
            dict: Payload JSON compatible avec le contrat.
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

    def _assert_errors(
        self,
        payload,
        expected_errors,
        available_sheet_names=None,
    ):
        """Verifie qu'un payload produit au moins les erreurs attendues.

        Args:
            payload (dict | None): Payload a valider.
            expected_errors (list[str]): Erreurs attendues.
            available_sheet_names (set[str] | None): Onglets disponibles.

        Returns:
            None: Les assertions valident les erreurs.
        """

        with self.assertRaises(CollectionFileDescriptionValidationError) as context:
            if payload is None:
                self.validator.parse_json_text(None)
            else:
                json_text = json.dumps(payload)
                self.validator.parse_json_text(json_text, available_sheet_names)
        for expected_error in expected_errors:
            self.assertIn(expected_error, context.exception.details)


if __name__ == "__main__":
    unittest.main()
