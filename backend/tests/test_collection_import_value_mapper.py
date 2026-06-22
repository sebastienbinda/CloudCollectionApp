#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du service generique de mapping des valeurs importees.

from datetime import date
from decimal import Decimal
import unittest

from services.collection.imports import CollectionImportField, WishlistImportMode
from services.collection.imports.collection_private_information_contract import (
    ALLOWED_REGIONS,
    CONDITION_LABELS_BY_VALUE,
    REGION_ALIASES_BY_VALUE,
)
from services.collection.imports import (
    CollectionImportValueMapper,
    ConditionMatchingConfiguration,
    RegionMatchingConfiguration,
)


class CollectionImportValueMapperTest(unittest.TestCase):
    """Valide la normalisation des informations privees importees."""

    def setUp(self):
        """Prepare le parser et les warnings.

        Args:
            Aucun.

        Returns:
            None: Initialise les dependances de test.
        """

        self.mapper = CollectionImportValueMapper(
            RegionMatchingConfiguration(60),
            ConditionMatchingConfiguration(60),
        )
        self.warnings = {"invalid_games": []}

    def test_parses_all_supported_private_information(self):
        """Verifie les types, enumerations et unite de prix valides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les valeurs normalisees.
        """

        values = {
            CollectionImportField.PURCHASE_PRICE: "129",
            CollectionImportField.BUY_LOCATION: " Paris ",
            CollectionImportField.BUY_DATE: "2026-06-01",
            CollectionImportField.GRADE: "Rare",
            CollectionImportField.CONDITION: "Très bon",
            CollectionImportField.HAS_MANUAL: "Non",
            CollectionImportField.IS_COLLECTOR: "Oui",
            CollectionImportField.HAS_STEELBOOK: True,
            CollectionImportField.IS_DIGITAL: "false",
            CollectionImportField.REGION: "eu-fr",
            CollectionImportField.DESCRIPTION: " Edition complete ",
        }

        result = self.mapper.map_private_values(values, "Zelda", self.warnings, "EUR")

        self.assertEqual(Decimal("129.00"), result["purchase_price"])
        self.assertEqual("EUR", result["price_unit"])
        self.assertEqual(date(2026, 6, 1), result["buy_date"])
        self.assertEqual(3, result["condition"])
        self.assertFalse(result["has_manual"])
        self.assertTrue(result["is_collector"])
        self.assertEqual("EU-FR", result["region"])
        self.assertEqual([], self.warnings["invalid_games"])

    def test_maps_release_dates_without_reader_specific_context(self):
        """Verifie que le mapping de date est reutilisable par tout lecteur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident date correcte et warning generique.
        """

        valid_date = self.mapper.map_release_date(
            "2000-01-01",
            "Zelda",
            self.warnings,
        )
        invalid_date = self.mapper.map_release_date(
            "1949-12-31",
            "Mario",
            self.warnings,
        )

        self.assertEqual(date(2000, 1, 1), valid_date)
        self.assertIsNone(invalid_date)
        self.assertEqual(
            "release_date",
            self.warnings["invalid_games"][0]["invalid_fields"][0]["field"],
        )

    def test_maps_names_and_wishlist_without_reader_specific_context(self):
        """Verifie les mappings generiques de nom et wishlist.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les valeurs et warnings generiques.
        """

        warnings = {"invalid_wishlist": 0, "invalid_values": []}

        game_name = self.mapper.map_name("  Édition Zelda  ")
        wishlist = self.mapper.map_wishlist(
            "Yes",
            WishlistImportMode.COLUMN,
            None,
            game_name,
            warnings,
        )

        self.assertEqual("Édition Zelda", game_name)
        self.assertEqual("edition zelda", self.mapper.comparison_key(game_name))
        self.assertTrue(wishlist)
        self.assertEqual(0, warnings["invalid_wishlist"])

    def test_empty_values_stay_null_and_invalid_values_create_warnings(self):
        """Verifie les valeurs nullable et les warnings non bloquants.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les valeurs invalides.
        """

        values = {
            CollectionImportField.PURCHASE_PRICE: "prix inconnu",
            CollectionImportField.CONDITION: "zzzzzz",
            CollectionImportField.HAS_MANUAL: "Peut-etre",
            CollectionImportField.REGION: "MARS",
            CollectionImportField.DESCRIPTION: "",
        }

        result = self.mapper.map_private_values(values, "Zelda", self.warnings, "USD")

        self.assertIsNone(result["purchase_price"])
        self.assertIsNone(result["price_unit"])
        self.assertIsNone(result["description"])
        invalid_fields = self.warnings["invalid_games"][0]["invalid_fields"]
        self.assertEqual(
            {"purchase_price", "condition", "has_manual", "region"},
            {item["field"] for item in invalid_fields},
        )

    def test_purchase_price_accepts_and_truncates_decimal_values(self):
        """Verifie l'acceptation et la troncature inferieure des prix positifs.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la borne minimale du prix.
        """

        negative_warnings = {"invalid_games": []}
        negative_result = self.mapper.map_private_values(
            {CollectionImportField.PURCHASE_PRICE: "-1"},
            "Zelda",
            negative_warnings,
            "EUR",
        )
        decimal_warnings = {"invalid_games": []}
        decimal_result = self.mapper.map_private_values(
            {CollectionImportField.PURCHASE_PRICE: "2,25"},
            "Mario",
            decimal_warnings,
            "EUR",
        )
        precision_warnings = {"invalid_games": []}
        precision_result = self.mapper.map_private_values(
            {CollectionImportField.PURCHASE_PRICE: "2,259"},
            "Luigi",
            precision_warnings,
            "EUR",
        )

        self.assertIsNone(negative_result["purchase_price"])
        self.assertIsNone(negative_result["price_unit"])
        self.assertEqual(
            "purchase_price",
            negative_warnings["invalid_games"][0]["invalid_fields"][0]["field"],
        )
        self.assertEqual(Decimal("2.25"), decimal_result["purchase_price"])
        self.assertEqual("EUR", decimal_result["price_unit"])
        self.assertEqual([], decimal_warnings["invalid_games"])
        self.assertEqual(Decimal("2.25"), precision_result["purchase_price"])
        self.assertEqual("EUR", precision_result["price_unit"])
        self.assertEqual([], precision_warnings["invalid_games"])

    def test_region_matching_accepts_typo_at_limit_and_rejects_below_limit(self):
        """Verifie le seuil configurable applique au score de region.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident acceptation et refus.
        """

        values = {CollectionImportField.REGION: "EU-F"}

        accepted = CollectionImportValueMapper(
            RegionMatchingConfiguration(60)
        ).map_private_values(values, "Zelda", {"invalid_games": []}, None)
        rejected_warnings = {"invalid_games": []}
        rejected = CollectionImportValueMapper(
            RegionMatchingConfiguration(95)
        ).map_private_values(values, "Zelda", rejected_warnings, None)

        self.assertEqual("EU-FR", accepted["region"])
        self.assertIsNone(rejected["region"])
        self.assertEqual("region", rejected_warnings["invalid_games"][0]["invalid_fields"][0]["field"])

    def test_region_matching_maps_exact_aliases_to_controlled_regions(self):
        """Verifie les alias explicites correspondant aux regions controlees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'alias independamment du seuil de similarite.
        """

        expected_regions_by_alias = {
            "NTSC - US": "US",
            "US - NTSC": "US",
            "FR": "EU-FR",
            "PAL - FR": "EU-FR",
            "PAL - EUR": "EU-FR",
            "EUR - PAL": "EU-FR",
            "UK": "EU-UK",
            "PAL - UK": "EU-UK",
            "DE": "EU-DE",
            "PAL - DE": "EU-DE",
            "ES": "EU-ES",
            "PAL - ES": "EU-ES",
            "IT": "EU-IT",
            "PAL - IT": "EU-IT",
        }
        mapper = CollectionImportValueMapper(RegionMatchingConfiguration(100))

        for alias, expected_region in expected_regions_by_alias.items():
            with self.subTest(alias=alias):
                warnings = {"invalid_games": []}
                result = mapper.map_private_values(
                    {CollectionImportField.REGION: alias},
                    "Zelda",
                    warnings,
                    None,
                )

                self.assertEqual(expected_region, result["region"])
                self.assertEqual([], warnings["invalid_games"])

    def test_every_declared_region_alias_maps_without_similarity_fallback(self):
        """Verifie que chaque alias declare est resolu meme au seuil maximal.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident tous les alias declares.
        """

        mapper = CollectionImportValueMapper(RegionMatchingConfiguration(100))

        for expected_region, aliases in REGION_ALIASES_BY_VALUE.items():
            for alias in aliases:
                with self.subTest(expected_region=expected_region, alias=alias):
                    warnings = {"invalid_games": []}
                    result = mapper.map_private_values(
                        {CollectionImportField.REGION: alias},
                        "Zelda",
                        warnings,
                        None,
                    )

                    self.assertIn(expected_region, ALLOWED_REGIONS)
                    self.assertEqual(expected_region, result["region"])
                    self.assertEqual([], warnings["invalid_games"])

    def test_condition_matching_supports_english_and_configurable_limit(self):
        """Verifie les alias anglais et le seuil configurable des etats.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident matching et warning.
        """

        values = {CollectionImportField.CONDITION: "very god"}
        accepted = CollectionImportValueMapper(
            RegionMatchingConfiguration(60),
            ConditionMatchingConfiguration(60),
        ).map_private_values(values, "Zelda", {"invalid_games": []}, None)
        rejected_warnings = {"invalid_games": []}
        rejected = CollectionImportValueMapper(
            RegionMatchingConfiguration(60),
            ConditionMatchingConfiguration(95),
        ).map_private_values(values, "Zelda", rejected_warnings, None)

        self.assertEqual(3, accepted["condition"])
        self.assertIsNone(rejected["condition"])
        self.assertEqual(
            "condition",
            rejected_warnings["invalid_games"][0]["invalid_fields"][0]["field"],
        )

    def test_condition_matching_accepts_every_confirmed_french_and_english_alias(self):
        """Verifie tous les synonymes confirmes pour chaque etat.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le mapping exhaustif.
        """

        for expected_condition, aliases in CONDITION_LABELS_BY_VALUE.items():
            for alias in aliases:
                with self.subTest(expected_condition=expected_condition, alias=alias):
                    warnings = {"invalid_games": []}
                    result = self.mapper.map_private_values(
                        {CollectionImportField.CONDITION: alias},
                        "Zelda",
                        warnings,
                        None,
                    )
                    self.assertEqual(expected_condition, result["condition"])
                    self.assertEqual([], warnings["invalid_games"])

    def test_condition_matching_maps_used_and_occasion_to_correct(self):
        """Verifie la precision metier pour les jeux d'occasion.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'etat Correct.
        """

        for value in ("used", "occasion"):
            with self.subTest(value=value):
                result = self.mapper.map_private_values(
                    {CollectionImportField.CONDITION: value},
                    "Zelda",
                    {"invalid_games": []},
                    None,
                )
                self.assertEqual(1, result["condition"])

    def test_condition_matching_explicitly_excludes_content_descriptions(self):
        """Verifie que les descriptions de contenu ne deviennent pas un etat.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les warnings non bloquants.
        """

        for value in ("complet", "complete", "loose", "loos", "CIB"):
            with self.subTest(value=value):
                warnings = {"invalid_games": []}
                result = self.mapper.map_private_values(
                    {CollectionImportField.CONDITION: value},
                    "Zelda",
                    warnings,
                    None,
                )
                self.assertIsNone(result["condition"])
                self.assertEqual(
                    "condition",
                    warnings["invalid_games"][0]["invalid_fields"][0]["field"],
                )

    def test_condition_matching_rejects_non_string_without_rejecting_values(self):
        """Verifie qu'un etat non textuel devient un warning nullable.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat non bloquant.
        """

        warnings = {"invalid_games": []}

        result = self.mapper.map_private_values(
            {CollectionImportField.CONDITION: 3},
            "Zelda",
            warnings,
            None,
        )

        self.assertIsNone(result["condition"])
        self.assertEqual("condition", warnings["invalid_games"][0]["invalid_fields"][0]["field"])

    def test_boolean_columns_share_confirmed_text_mapping(self):
        """Verifie les valeurs textuelles communes aux quatre booleens.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident vrais, faux et cellules vides.
        """

        values = {
            CollectionImportField.HAS_MANUAL: "Ouii",
            CollectionImportField.IS_COLLECTOR: "No n",
            CollectionImportField.HAS_STEELBOOK: "Présent",
            CollectionImportField.IS_DIGITAL: "No",
        }

        result = self.mapper.map_private_values(values, "Zelda", self.warnings, None)

        self.assertTrue(result["has_manual"])
        self.assertFalse(result["is_collector"])
        self.assertTrue(result["has_steelbook"])
        self.assertFalse(result["is_digital"])
        self.assertEqual([], self.warnings["invalid_games"])

    def test_unknown_boolean_is_null_with_warning_and_empty_is_silent(self):
        """Verifie le warning non bloquant et la cellule vide nullable.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les deux comportements.
        """

        warnings = {"invalid_games": []}
        result = self.mapper.map_private_values(
            {
                CollectionImportField.HAS_MANUAL: "peut-etre",
                CollectionImportField.IS_COLLECTOR: "   ",
            },
            "Zelda",
            warnings,
            None,
        )

        self.assertIsNone(result["has_manual"])
        self.assertIsNone(result["is_collector"])
        self.assertEqual(1, len(warnings["invalid_games"][0]["invalid_fields"]))
        self.assertEqual("has_manual", warnings["invalid_games"][0]["invalid_fields"][0]["field"])


if __name__ == "__main__":
    unittest.main()
