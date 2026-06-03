#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-03
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du contrat de configuration wishlist.

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.collection.imports import (  # noqa: E402
    CollectionFileDescriptionValidationError,
    CollectionFileDescriptionValidator,
    CollectionImportField,
    WishlistDuplicatePolicy,
    WishlistImportMode,
    WishlistValueParser,
)


class WishlistImportContractTest(unittest.TestCase):
    """Valide le contrat JSON et le parsing de la wishlist."""

    def setUp(self):
        """Prepare le validateur teste.

        Args:
            Aucun.

        Returns:
            None: Le validateur est initialise.
        """

        self.validator = CollectionFileDescriptionValidator()

    def test_valid_wishlist_sheet_configuration(self):
        """Verifie une configuration avec onglet dedie wishlist."""

        payload = self._single_sheet_payload()
        payload["wishlist"] = {
            "mode": "sheet",
            "sheet_name": "Wishlist",
            "data_range": "A1:D200",
            "header_row": 1,
            "column_information": {
                "name": "A",
                "platform": "B",
                "studio": "C",
                "release_date": "D",
            },
        }

        description = self.validator.validate(payload, {"Collection", "Wishlist"})

        self.assertEqual(WishlistImportMode.SHEET, description.wishlist.mode)
        self.assertEqual("Wishlist", description.wishlist.sheet_name)
        self.assertEqual(payload, description.to_dict())

    def test_valid_wishlist_column_configuration(self):
        """Verifie une configuration avec colonne wishlist dans la collection."""

        payload = self._single_sheet_payload()
        payload["wishlist"] = {"mode": "column"}
        payload["single_sheet_conf"]["data_range"] = "A1:E200"
        payload["single_sheet_conf"]["column_information"]["wishlist"] = "E"

        description = self.validator.validate(payload)

        self.assertEqual(WishlistImportMode.COLUMN, description.wishlist.mode)
        self.assertEqual(
            "E",
            description.single_sheet_conf.column_information[CollectionImportField.WISHLIST],
        )
        self.assertEqual(payload, description.to_dict())

    def test_rejects_missing_wishlist_configuration(self):
        """Verifie que la section wishlist est obligatoire."""

        payload = self._single_sheet_payload()
        del payload["wishlist"]

        self._assert_errors(payload, ["wishlist est obligatoire."])

    def test_rejects_missing_or_unknown_wishlist_mode(self):
        """Verifie le refus d'un mode wishlist absent ou inconnu."""

        payload = self._single_sheet_payload()
        payload["wishlist"] = {}
        self._assert_errors(payload, ["wishlist.mode est obligatoire."])

        payload = self._single_sheet_payload()
        payload["wishlist"] = {"mode": "maybe"}
        self._assert_errors(payload, ["wishlist.mode inconnu."])

    def test_rejects_wishlist_sheet_without_required_configuration(self):
        """Verifie le refus d'un onglet wishlist incomplet."""

        payload = self._single_sheet_payload()
        payload["wishlist"] = {"mode": "sheet"}

        self._assert_errors(
            payload,
            [
                "wishlist.sheet_name est obligatoire en mode sheet.",
                "wishlist.data_range doit utiliser le format A1:H200.",
                "wishlist.header_row doit etre un entier.",
                "wishlist.column_information doit etre un objet.",
                "colonne obligatoire manquante: name.",
            ],
        )

    def test_rejects_wishlist_sheet_with_wishlist_column(self):
        """Verifie que le layout d'onglet dedie ne porte pas de colonne wishlist."""

        payload = self._single_sheet_payload()
        payload["wishlist"] = {
            "mode": "sheet",
            "sheet_name": "Wishlist",
            "data_range": "A1:E200",
            "header_row": 1,
            "column_information": {
                "name": "A",
                "platform": "B",
                "studio": "C",
                "release_date": "D",
                "wishlist": "E",
            },
        }

        self._assert_errors(
            payload,
            ["wishlist.column_information ne doit pas contenir wishlist en mode sheet."],
        )

    def test_rejects_wishlist_column_without_collection_mapping(self):
        """Verifie que le mode colonne exige le mapping wishlist dans la collection."""

        payload = self._single_sheet_payload()
        payload["wishlist"] = {"mode": "column"}

        self._assert_errors(
            payload,
            ["single_sheet_conf.column_information.wishlist est obligatoire en mode column."],
        )

    def test_rejects_wishlist_none_with_sheet_or_column_configuration(self):
        """Verifie que le mode none reste vide et sans colonne wishlist."""

        payload = self._single_sheet_payload()
        payload["wishlist"] = {
            "mode": "none",
            "sheet_name": "Wishlist",
        }
        self._assert_errors(
            payload,
            ["wishlist.mode none ne doit pas definir de configuration d'onglet."],
        )

        payload = self._single_sheet_payload()
        payload["single_sheet_conf"]["data_range"] = "A1:E200"
        payload["single_sheet_conf"]["column_information"]["wishlist"] = "E"
        self._assert_errors(
            payload,
            ["wishlist.mode none ne doit pas utiliser de colonne wishlist."],
        )

    def test_wishlist_value_parser_accepts_expected_boolean_values(self):
        """Verifie le parsing des valeurs booleennes wishlist attendues."""

        parser = WishlistValueParser()
        for value in ("Oui", "O", "True", "Yes", "Y"):
            result = parser.parse(value)
            self.assertTrue(result.is_valid)
            self.assertTrue(result.value)
        for value in ("Non", "N", "False", "No"):
            result = parser.parse(value)
            self.assertTrue(result.is_valid)
            self.assertFalse(result.value)

    def test_wishlist_value_parser_handles_empty_and_invalid_values(self):
        """Verifie la valeur vide et les valeurs invalides."""

        parser = WishlistValueParser()

        empty_result = parser.parse(" ")
        invalid_result = parser.parse("Peut etre")

        self.assertTrue(empty_result.is_valid)
        self.assertFalse(empty_result.value)
        self.assertFalse(invalid_result.is_valid)
        self.assertEqual("Peut etre", invalid_result.invalid_value)

    def test_wishlist_duplicate_policy_applies_confirmed_priorities(self):
        """Verifie les priorites de doublons confirmees par le contrat."""

        policy = WishlistDuplicatePolicy()

        self.assertFalse(
            policy.resolve_wishlist_value(WishlistImportMode.SHEET, False, True)
        )
        self.assertTrue(
            policy.resolve_wishlist_value(WishlistImportMode.COLUMN, False, True)
        )
        self.assertTrue(
            policy.resolve_wishlist_value(WishlistImportMode.COLUMN, True, False)
        )

    def _single_sheet_payload(self):
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

    def _assert_errors(self, payload, expected_errors):
        with self.assertRaises(CollectionFileDescriptionValidationError) as context:
            self.validator.parse_json_text(json.dumps(payload))
        for expected_error in expected_errors:
            self.assertIn(expected_error, context.exception.details)


if __name__ == "__main__":
    unittest.main()
