#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : mapping generique des valeurs de jeux importees.

from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_DOWN
import logging
import unicodedata
from typing import Any

import pandas as pd

from .collection_file_description import CollectionImportField
from .collection_file_description import WishlistImportMode
from .collection_import_date_validator import CollectionImportDateValidator
from .collection_private_information_contract import (
    ALLOWED_REGIONS,
    BOOLEAN_MATCH_LIMIT,
    BOOLEAN_FALSE_LABELS,
    BOOLEAN_TRUE_LABELS,
    CONDITION_EXCLUDED_LABELS,
    CONDITION_LABELS_BY_VALUE,
    REGION_ALIASES_BY_VALUE,
)
from services.formatting import SheetValueFormatter
from services.matching import matching_score

from .region_matching_configuration import RegionMatchingConfiguration
from .condition_matching_configuration import ConditionMatchingConfiguration
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer
from .wishlist_value_parser import WishlistValueParser


class CollectionImportValueMapper:
    """Convertit les valeurs brutes d'un lecteur en valeurs metier importables."""

    BOOLEAN_FIELDS = (
        CollectionImportField.HAS_MANUAL,
        CollectionImportField.IS_COLLECTOR,
        CollectionImportField.HAS_STEELBOOK,
        CollectionImportField.IS_DIGITAL,
    )

    def __init__(
        self,
        region_matching_configuration: RegionMatchingConfiguration | None = None,
        condition_matching_configuration: ConditionMatchingConfiguration | None = None,
        date_validator: CollectionImportDateValidator | None = None,
        name_normalizer: UserCollectionNameNormalizer | None = None,
        wishlist_value_parser: WishlistValueParser | None = None,
        logger: logging.Logger | None = None,
    ):
        """Initialise le parser avec le seuil de matching des regions.

        Args:
            region_matching_configuration (RegionMatchingConfiguration | None): Seuil injectable.
            condition_matching_configuration (ConditionMatchingConfiguration | None): Seuil etat.
            date_validator (CollectionImportDateValidator | None): Validateur de dates generique.
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur de noms.
            wishlist_value_parser (WishlistValueParser | None): Parser wishlist generique.
            logger (logging.Logger | None): Logger applicatif optionnel.

        Returns:
            None: Initialise le parser.

        Raises:
            ValueError: Si `REGION_MATCH_LIMIT` est invalide.
        """

        self.region_matching_configuration = (
            region_matching_configuration or RegionMatchingConfiguration.from_environment()
        )
        self.condition_matching_configuration = (
            condition_matching_configuration or ConditionMatchingConfiguration.from_environment()
        )
        self.date_validator = date_validator or CollectionImportDateValidator()
        self.name_normalizer = name_normalizer or UserCollectionNameNormalizer()
        self.wishlist_value_parser = wishlist_value_parser or WishlistValueParser()
        self.logger = logger or logging.getLogger(__name__)

    def map_name(self, value: Any) -> str | None:
        """Mappe un nom brut vers sa valeur metier nettoyee.

        Args:
            value (Any): Valeur brute fournie par un lecteur.

        Returns:
            str | None: Nom trimme ou absence.
        """

        return self.name_normalizer.stored_value(value)

    def comparison_key(self, value: Any) -> str | None:
        """Construit la cle generique de comparaison d'un nom importe.

        Args:
            value (Any): Valeur brute ou deja nettoyee.

        Returns:
            str | None: Cle minuscule sans accents ou absence.
        """

        return self.name_normalizer.comparison_key(value)

    def map_wishlist(
        self,
        value: Any,
        mode: WishlistImportMode,
        forced_value: bool | None,
        game_name: str,
        warnings: dict[str, Any],
        source_context: str = "",
    ) -> bool | None:
        """Mappe une valeur wishlist brute selon le mode d'import.

        Args:
            value (Any): Valeur brute fournie par le lecteur.
            mode (WishlistImportMode): Mode wishlist configure.
            forced_value (bool | None): Valeur imposee par une source dediee.
            game_name (str): Nom du jeu utilise dans les logs.
            warnings (dict[str, Any]): Warnings d'import a enrichir.
            source_context (str): Contexte technique optionnel pour les logs.

        Returns:
            bool | None: Valeur mappee ou absence lorsque la ligne doit etre ignoree.
        """

        if forced_value is not None:
            return forced_value
        if mode != WishlistImportMode.COLUMN:
            return False
        result = self.wishlist_value_parser.parse(value)
        if result.is_valid:
            return result.value
        warnings["invalid_wishlist"] += 1
        if result.invalid_value not in warnings["invalid_values"]:
            warnings["invalid_values"].append(result.invalid_value)
        self.logger.warning(
            "Valeur wishlist invalide ignoree: jeu=%s, valeur=%s%s",
            game_name,
            result.invalid_value,
            f", {source_context}" if source_context else "",
        )
        return None

    def map_private_values(
        self,
        values: dict[CollectionImportField, Any],
        game_name: str,
        warnings: dict[str, Any],
        price_unit: str | None,
    ) -> dict[str, Any]:
        """Mappe les valeurs privees et enregistre les valeurs invalides.

        Args:
            values (dict[CollectionImportField, Any]): Valeurs brutes par champ.
            game_name (str): Nom du jeu utilise dans les warnings.
            warnings (dict[str, Any]): Warnings d'import a enrichir.
            price_unit (str | None): Unite globale configuree pour le fichier.

        Returns:
            dict[str, Any]: Valeurs privees normalisees.
        """

        parsed = {
            "purchase_price": self._parse_non_negative_decimal(
                values.get(CollectionImportField.PURCHASE_PRICE),
                game_name,
                "purchase_price",
                warnings,
            ),
            "buy_location": self._text(values.get(CollectionImportField.BUY_LOCATION)),
            "buy_date": self._parse_date(
                values.get(CollectionImportField.BUY_DATE), game_name, "buy_date", warnings
            ),
            "grade": self._text(values.get(CollectionImportField.GRADE)),
            "condition": self._parse_condition(
                values.get(CollectionImportField.CONDITION), game_name, warnings
            ),
            "region": self._parse_region(
                values.get(CollectionImportField.REGION), game_name, warnings
            ),
            "description": self._text(values.get(CollectionImportField.DESCRIPTION)),
        }
        for field in self.BOOLEAN_FIELDS:
            parsed[field.value] = self._parse_boolean(
                values.get(field), game_name, field.value, warnings
            )
        parsed["price_unit"] = price_unit if parsed["purchase_price"] is not None else None
        return parsed

    def map_release_date(
        self,
        value: Any,
        game_name: str,
        warnings: dict[str, Any],
        source_context: str = "",
    ) -> date | None:
        """Mappe une date de sortie brute vers une date persistable.

        Args:
            value (Any): Valeur brute fournie par un lecteur de collection.
            game_name (str): Nom du jeu utilise dans les warnings.
            warnings (dict[str, Any]): Warnings d'import a enrichir.
            source_context (str): Contexte technique optionnel pour les logs.

        Returns:
            date | None: Date valide ou absence.
        """

        if self._is_empty(value):
            return None
        parsed_value = value
        if not isinstance(value, (date, datetime)):
            try:
                parsed_value = pd.to_datetime(value, errors="coerce")
            except (OverflowError, ValueError, TypeError):
                return self._invalid_release_date(value, game_name, warnings, source_context)
            if pd.isna(parsed_value):
                return self._invalid_release_date(value, game_name, warnings, source_context)
        valid_date = self.date_validator.validate_release_date(parsed_value)
        if valid_date is not None:
            return valid_date
        return self._invalid_release_date(value, game_name, warnings, source_context)

    def _invalid_release_date(
        self,
        value: Any,
        game_name: str,
        warnings: dict[str, Any],
        source_context: str,
    ) -> None:
        self._record_invalid(game_name, "release_date", value, warnings)
        self.logger.warning(
            "Date de sortie invalide ignoree: jeu=%s, valeur=%s%s",
            game_name,
            value,
            f", {source_context}" if source_context else "",
        )
        return None

    def _parse_non_negative_decimal(
        self, value: Any, game_name: str, field: str, warnings: dict[str, Any]
    ) -> Decimal | None:
        if self._is_empty(value):
            return None
        try:
            parsed = Decimal(str(value).strip().replace(" ", "").replace(",", "."))
            if not parsed.is_finite() or parsed < 0:
                raise ValueError
            normalized = parsed.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            if normalized > Decimal("9999999999.99"):
                raise ValueError
            return normalized
        except (InvalidOperation, TypeError, ValueError):
            self._record_invalid(game_name, field, value, warnings)
            return None

    def _parse_date(
        self, value: Any, game_name: str, field: str, warnings: dict[str, Any]
    ) -> date | None:
        if self._is_empty(value):
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        try:
            parsed = pd.to_datetime(value, errors="coerce")
            if pd.isna(parsed):
                raise ValueError
            return parsed.date()
        except (TypeError, ValueError, OverflowError, AttributeError):
            self._record_invalid(game_name, field, value, warnings)
            return None

    def _parse_condition(
        self, value: Any, game_name: str, warnings: dict[str, Any]
    ) -> int | None:
        if self._is_empty(value):
            return None
        if not isinstance(value, str):
            self._record_invalid(game_name, "condition", value, warnings)
            return None
        imported_key = self._compact_key(value)
        excluded_keys = {self._compact_key(label) for label in CONDITION_EXCLUDED_LABELS}
        if imported_key in excluded_keys:
            self._record_invalid(game_name, "condition", value, warnings)
            return None
        scored_conditions = []
        for condition, labels in CONDITION_LABELS_BY_VALUE.items():
            best_score = max(
                self._matching_score(imported_key, self._compact_key(label))
                for label in labels
            )
            scored_conditions.append((best_score, condition))
        best_score = max((score for score, _ in scored_conditions), default=0)
        best_conditions = [
            condition for score, condition in scored_conditions if score == best_score
        ]
        if (
            best_score >= self.condition_matching_configuration.match_limit
            and len(best_conditions) == 1
        ):
            return best_conditions[0]
        self._record_invalid(game_name, "condition", value, warnings)
        return None

    def _parse_boolean(
        self, value: Any, game_name: str, field: str, warnings: dict[str, Any]
    ) -> bool | None:
        if self._is_empty(value):
            return None
        if isinstance(value, bool):
            return value
        if not isinstance(value, str):
            self._record_invalid(game_name, field, value, warnings)
            return None
        imported_key = self._compact_key(value)
        true_keys = {self._compact_key(label) for label in BOOLEAN_TRUE_LABELS}
        false_keys = {self._compact_key(label) for label in BOOLEAN_FALSE_LABELS}
        if imported_key in true_keys:
            return True
        if imported_key in false_keys:
            return False
        scored_values = [
            (max(self._matching_score(imported_key, key) for key in true_keys), True),
            (max(self._matching_score(imported_key, key) for key in false_keys), False),
        ]
        best_score = max(score for score, _ in scored_values)
        best_values = [result for score, result in scored_values if score == best_score]
        if best_score >= BOOLEAN_MATCH_LIMIT and len(best_values) == 1:
            return best_values[0]
        self._record_invalid(game_name, field, value, warnings)
        return None

    def _parse_region(
        self, value: Any, game_name: str, warnings: dict[str, Any]
    ) -> str | None:
        imported_region = self._text(value)
        if imported_region is None:
            return None
        imported_key = self._compact_key(imported_region)
        aliased_region = self._find_region_by_exact_alias(imported_key)
        if aliased_region is not None:
            return aliased_region
        scored_regions = sorted(
            (
                (self._matching_score(imported_key, self._compact_key(region)), region)
                for region in ALLOWED_REGIONS
            ),
            reverse=True,
        )
        best_score = scored_regions[0][0] if scored_regions else 0
        best_regions = [region for score, region in scored_regions if score == best_score]
        if (
            best_score >= self.region_matching_configuration.match_limit
            and len(best_regions) == 1
        ):
            return best_regions[0]
        self._record_invalid(game_name, "region", value, warnings)
        return None

    def _find_region_by_exact_alias(self, imported_key: str) -> str | None:
        """Recherche une region par alias normalise exact.

        Args:
            imported_key (str): Valeur de region importee, normalisee et compactee.

        Returns:
            str | None: Code de region controle correspondant ou absence.
        """

        for region, aliases in REGION_ALIASES_BY_VALUE.items():
            if imported_key in {self._compact_key(alias) for alias in aliases}:
                return region
        return None

    def _matching_score(self, imported_key: str, candidate_key: str) -> int:
        return matching_score(imported_key, candidate_key)

    def _compact_key(self, value: Any) -> str:
        return "".join(self._normalized_text(value).split())

    def _record_invalid(
        self, game_name: str, field: str, value: Any, warnings: dict[str, Any]
    ) -> None:
        games = warnings.setdefault("invalid_games", [])
        game_warning = next((item for item in games if item["name"] == game_name), None)
        if game_warning is None:
            game_warning = {"name": game_name, "invalid_fields": []}
            games.append(game_warning)
        game_warning["invalid_fields"].append({"field": field, "value": str(value)})

    def _is_empty(self, value: Any) -> bool:
        return SheetValueFormatter.clean_text(value) is None

    def _text(self, value: Any) -> str | None:
        return SheetValueFormatter.clean_text(value)

    def _normalized_text(self, value: Any) -> str:
        text = self._text(value) or ""
        return "".join(
            character
            for character in unicodedata.normalize("NFKD", text.lower())
            if not unicodedata.combining(character)
        )
