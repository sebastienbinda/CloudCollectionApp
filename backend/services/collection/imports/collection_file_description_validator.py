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
# Description : validation du contrat JSON d'import de collection.

import json
from typing import Any, Optional

from .collection_file_description import (
    CollectionFileDescription,
    CollectionFileType,
    CollectionImportField,
    CollectionMultipleSheetsConfiguration,
    CollectionPerSheetConfiguration,
    CollectionSheetLayout,
    WishlistImportConfiguration,
)
from .collection_file_description_rules import CollectionFileDescriptionRules
from .wishlist_import_configuration_validator import WishlistImportConfigurationValidator
from .spreadsheet_cell_reference import SpreadsheetCellReferenceParser
from .collection_private_information_contract import ALLOWED_PRICE_UNITS
from .csv_file_description_validator import CsvFileDescriptionValidator


class CollectionFileDescriptionValidationError(ValueError):
    """Signale une description de fichier de collection invalide."""

    def __init__(self, details: list[str]):
        """Initialise l'erreur de validation.

        Args:
            details (list[str]): Messages explicites de validation.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.details = details
        super().__init__("Configuration invalide.")


class CollectionFileDescriptionValidator:
    """Valide et construit le DTO de description d'un fichier de collection."""

    REQUIRED_FIELDS = {
        CollectionImportField.NAME,
        CollectionImportField.PLATFORM,
    }

    def __init__(
        self,
        cell_reference_parser: Optional[SpreadsheetCellReferenceParser] = None,
        wishlist_validator: Optional[WishlistImportConfigurationValidator] = None,
        csv_validator: Optional[CsvFileDescriptionValidator] = None,
        rules: Optional[CollectionFileDescriptionRules] = None,
    ):
        """Initialise le validateur de description.

        Args:
            cell_reference_parser (Optional[SpreadsheetCellReferenceParser]): Parser tableur.
            wishlist_validator (Optional[WishlistImportConfigurationValidator]): Validateur wishlist.
            csv_validator (Optional[CsvFileDescriptionValidator]): Validateur CSV.
            rules (Optional[CollectionFileDescriptionRules]): Regles de coherence.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.cell_reference_parser = cell_reference_parser or SpreadsheetCellReferenceParser()
        self.wishlist_validator = wishlist_validator or WishlistImportConfigurationValidator()
        self.csv_validator = csv_validator or CsvFileDescriptionValidator()
        self.rules = rules or CollectionFileDescriptionRules()

    def parse_json_text(
        self,
        json_text: str | None,
        available_sheet_names: Optional[set[str]] = None,
    ) -> CollectionFileDescription:
        """Parse et valide le champ texte multipart.

        Args:
            json_text (str | None): JSON UTF-8 recu dans `collection_file_description`.
            available_sheet_names (Optional[set[str]]): Onglets reels connus si disponibles.

        Returns:
            CollectionFileDescription: Description valide construite.

        Raises:
            CollectionFileDescriptionValidationError: Si le JSON ou son contenu est invalide.
        """

        if json_text is None or not str(json_text).strip():
            raise CollectionFileDescriptionValidationError(
                ["collection_file_description est requis."]
            )
        try:
            payload = json.loads(json_text)
        except json.JSONDecodeError as exc:
            raise CollectionFileDescriptionValidationError(["JSON invalide."]) from exc
        return self.validate(payload, available_sheet_names)

    def validate(
        self,
        payload: Any,
        available_sheet_names: Optional[set[str]] = None,
    ) -> CollectionFileDescription:
        """Valide un payload deja decode et construit son DTO.

        Args:
            payload (Any): Objet JSON decode.
            available_sheet_names (Optional[set[str]]): Onglets reels connus si disponibles.

        Returns:
            CollectionFileDescription: Description valide construite.

        Raises:
            CollectionFileDescriptionValidationError: Si le payload est invalide.
        """

        errors: list[str] = []
        if not isinstance(payload, dict):
            raise CollectionFileDescriptionValidationError(["JSON invalide."])

        file_type = self._parse_file_type(payload.get("file_type"), errors)
        wishlist_payload = payload.get("wishlist")
        single_sheet_conf = payload.get("single_sheet_conf")
        multiple_sheets_conf = payload.get("multiple_sheets_conf")
        csv_mapping = payload.get("mapping")
        self.rules.validate_top_level_modes(
            file_type,
            single_sheet_conf,
            multiple_sheets_conf,
            csv_mapping,
            errors,
        )
        wishlist_configuration = self.wishlist_validator.build(
            wishlist_payload,
            errors,
            available_sheet_names,
            self._build_layout,
        )

        single_sheet = None
        multiple_sheets = None
        csv_conf = None
        if isinstance(single_sheet_conf, dict):
            single_sheet = self._build_layout(
                single_sheet_conf,
                None,
                "single_sheet_conf",
                errors,
                allow_included_sheets=False,
            )
        if isinstance(multiple_sheets_conf, dict):
            multiple_sheets = self._build_multiple_sheets(
                multiple_sheets_conf,
                errors,
                available_sheet_names,
            )
        if file_type == CollectionFileType.CSV:
            csv_conf = self.csv_validator.build(
                csv_mapping,
                str((wishlist_payload or {}).get("mode") or ""),
                errors,
                available_sheet_names,
            )
        self.wishlist_validator.validate_collection_configuration(
            wishlist_configuration,
            wishlist_payload,
            single_sheet,
            multiple_sheets,
            errors,
        )
        self.rules.validate_csv_wishlist_configuration(csv_conf, wishlist_configuration, errors)
        price_unit = self._parse_price_unit(payload.get("price_unit"), errors)
        if (
            self.rules.uses_purchase_price(
                single_sheet,
                multiple_sheets,
                csv_conf,
                wishlist_configuration,
            )
            and price_unit is None
        ):
            errors.append("price_unit est requis quand purchase_price est configure.")

        if errors:
            raise CollectionFileDescriptionValidationError(errors)
        return CollectionFileDescription(
            file_type=file_type or CollectionFileType.LIBREOFFICE_ODS,
            wishlist=wishlist_configuration or WishlistImportConfiguration.none(),
            single_sheet_conf=single_sheet,
            multiple_sheets_conf=multiple_sheets,
            csv_conf=csv_conf,
            price_unit=price_unit,
        )

    def _parse_price_unit(self, value: Any, errors: list[str]) -> Optional[str]:
        """Valide l'unite monetaire globale optionnelle.

        Args:
            value (Any): Valeur brute du payload.
            errors (list[str]): Erreurs a enrichir.

        Returns:
            Optional[str]: Code ISO valide ou absence.
        """

        if value is None or not str(value).strip():
            return None
        price_unit = str(value).strip().upper()
        if price_unit not in ALLOWED_PRICE_UNITS:
            errors.append("price_unit inconnu.")
            return None
        return price_unit

    def _parse_file_type(
        self,
        value: Any,
        errors: list[str],
    ) -> Optional[CollectionFileType]:
        try:
            return CollectionFileType(value)
        except ValueError:
            errors.append("file_type inconnu.")
            return None

    def _build_multiple_sheets(
        self,
        payload: dict[str, Any],
        errors: list[str],
        available_sheet_names: Optional[set[str]],
    ) -> CollectionMultipleSheetsConfiguration:
        shared_layout_payload = payload.get("shared_layout")
        sheets_payload = payload.get("sheets")
        if shared_layout_payload is not None and sheets_payload is not None:
            errors.append("shared_layout et sheets sont exclusifs.")
        if shared_layout_payload is None and sheets_payload is None:
            errors.append("multiple_sheets_conf doit definir shared_layout ou sheets.")

        shared_sheet_information = self._parse_sheet_information(
            payload.get("sheet_information"),
            "multiple_sheets_conf.sheet_information",
            errors,
        )
        shared_layout = None
        if isinstance(shared_layout_payload, dict):
            shared_layout = self._build_layout(
                shared_layout_payload,
                shared_sheet_information,
                "multiple_sheets_conf.shared_layout",
                errors,
                allow_included_sheets=True,
            )
            self._validate_included_sheets(
                shared_layout.included_sheets if shared_layout else None,
                available_sheet_names,
                errors,
            )
            self._validate_excluded_sheets(
                shared_layout.excluded_sheets if shared_layout else None,
                available_sheet_names,
                errors,
            )
        elif shared_layout_payload is not None:
            errors.append("multiple_sheets_conf.shared_layout doit etre un objet.")

        sheets = None
        if isinstance(sheets_payload, list):
            sheets = [
                self._build_sheet_configuration(item, index, errors)
                for index, item in enumerate(sheets_payload)
            ]
        elif sheets_payload is not None:
            errors.append("multiple_sheets_conf.sheets doit etre une liste.")
        return CollectionMultipleSheetsConfiguration(
            sheet_information=shared_sheet_information,
            shared_layout=shared_layout,
            sheets=sheets,
        )

    def _build_sheet_configuration(
        self,
        payload: Any,
        index: int,
        errors: list[str],
    ) -> CollectionPerSheetConfiguration:
        path = f"multiple_sheets_conf.sheets[{index}]"
        if not isinstance(payload, dict):
            errors.append(f"{path} doit etre un objet.")
            payload = {}
        sheet_name = str(payload.get("sheet_name") or "").strip()
        if not sheet_name:
            errors.append(f"{path}.sheet_name est obligatoire.")
        sheet_information = self._parse_sheet_information(
            payload.get("sheet_information"),
            f"{path}.sheet_information",
            errors,
        )
        layout = self._build_layout(
            payload,
            sheet_information,
            path,
            errors,
            allow_included_sheets=False,
        )
        return CollectionPerSheetConfiguration(sheet_name, sheet_information, layout)

    def _build_layout(
        self,
        payload: dict[str, Any],
        sheet_information: Optional[CollectionImportField],
        path: str,
        errors: list[str],
        allow_included_sheets: bool,
    ) -> CollectionSheetLayout:
        data_range = str(payload.get("data_range") or "").strip().upper()
        header_row = payload.get("header_row")
        column_information = payload.get("column_information")
        range_bounds = self._parse_data_range(data_range, path, errors)
        if not isinstance(header_row, int):
            errors.append(f"{path}.header_row doit etre un entier.")
            header_row = 0
        if not isinstance(column_information, dict):
            errors.append(f"{path}.column_information doit etre un objet.")
            column_information = {}

        parsed_columns = self._parse_columns(
            column_information,
            sheet_information,
            path,
            errors,
        )
        if range_bounds is not None:
            start_col, start_row, end_col, end_row = range_bounds
            if not start_row <= header_row <= end_row:
                errors.append("header_row hors data_range.")
            self._validate_columns_in_range(parsed_columns, start_col, end_col, errors)
        included_sheets = self._parse_included_sheets(
            payload.get("included_sheets"),
            path,
            errors,
            allow_included_sheets,
        )
        excluded_sheets = self._parse_excluded_sheets(
            payload.get("excluded_sheets"),
            path,
            errors,
            allow_included_sheets,
        )
        if included_sheets is not None and excluded_sheets is not None:
            errors.append(f"{path}.included_sheets et excluded_sheets sont exclusifs.")
        return CollectionSheetLayout(
            data_range,
            header_row,
            parsed_columns,
            included_sheets,
            excluded_sheets,
        )

    def _parse_sheet_information(
        self,
        value: Any,
        path: str,
        errors: list[str],
    ) -> Optional[CollectionImportField]:
        if value is None:
            return None
        try:
            field = CollectionImportField(value)
        except ValueError:
            errors.append(f"{path} inconnu.")
            return None
        if field == CollectionImportField.WISHLIST:
            errors.append(f"{path} inconnu.")
            return None
        return field

    def _parse_data_range(
        self,
        value: str,
        path: str,
        errors: list[str],
    ) -> Optional[tuple[int, int, int, int]]:
        bounds = self.cell_reference_parser.parse_range(value)
        if bounds is None:
            errors.append(f"{path}.data_range doit utiliser le format A1:H200.")
            return None
        return bounds

    def _parse_columns(
        self,
        column_information: dict[str, Any],
        sheet_information: Optional[CollectionImportField],
        path: str,
        errors: list[str],
    ) -> dict[CollectionImportField, str]:
        parsed_columns: dict[CollectionImportField, str] = {}
        for field_name, column_name in column_information.items():
            try:
                field = CollectionImportField(field_name)
            except ValueError:
                errors.append(f"{path}.column_information contient un champ inconnu: {field_name}.")
                continue
            if sheet_information == field:
                errors.append("sheet_information est aussi present dans column_information.")
            column_value = str(column_name or "").strip().upper()
            if not self.cell_reference_parser.is_column_name(column_value):
                errors.append(f"{path}.column_information.{field.value} doit etre une colonne.")
                continue
            parsed_columns[field] = column_value
        missing_fields = sorted(
            field.value
            for field in self.REQUIRED_FIELDS.difference(parsed_columns)
            if field != sheet_information
        )
        for field_name in missing_fields:
            errors.append(f"colonne obligatoire manquante: {field_name}.")
        return parsed_columns

    def _validate_columns_in_range(
        self,
        parsed_columns: dict[CollectionImportField, str],
        start_col: int,
        end_col: int,
        errors: list[str],
    ) -> None:
        for field, column_name in parsed_columns.items():
            column_index = self.cell_reference_parser.column_to_index(column_name)
            if not start_col <= column_index <= end_col:
                errors.append(f"colonne hors data_range: {field.value}.")

    def _parse_included_sheets(
        self,
        value: Any,
        path: str,
        errors: list[str],
        allow_included_sheets: bool,
    ) -> Optional[list[str]]:
        if value is None:
            return None
        if not allow_included_sheets:
            errors.append(f"{path}.included_sheets n'est pas autorise.")
            return None
        if not isinstance(value, list):
            errors.append(f"{path}.included_sheets doit etre une liste.")
            return None
        sheet_names = [str(sheet_name).strip() for sheet_name in value]
        empty_names = [sheet_name for sheet_name in sheet_names if not sheet_name]
        if empty_names:
            errors.append(f"{path}.included_sheets contient un onglet vide.")
        return [sheet_name for sheet_name in sheet_names if sheet_name]

    def _parse_excluded_sheets(
        self,
        value: Any,
        path: str,
        errors: list[str],
        allow_excluded_sheets: bool,
    ) -> Optional[list[str]]:
        if value is None:
            return None
        if not allow_excluded_sheets:
            errors.append(f"{path}.excluded_sheets n'est pas autorise.")
            return None
        if not isinstance(value, list):
            errors.append(f"{path}.excluded_sheets doit etre une liste.")
            return None
        sheet_names = [str(sheet_name).strip() for sheet_name in value]
        if any(not sheet_name for sheet_name in sheet_names):
            errors.append(f"{path}.excluded_sheets contient un onglet vide.")
        return [sheet_name for sheet_name in sheet_names if sheet_name]

    def _validate_included_sheets(
        self,
        included_sheets: Optional[list[str]],
        available_sheet_names: Optional[set[str]],
        errors: list[str],
    ) -> None:
        if included_sheets is None or available_sheet_names is None:
            return
        missing_sheets = sorted(set(included_sheets).difference(available_sheet_names))
        for sheet_name in missing_sheets:
            errors.append(f"onglet absent du fichier: {sheet_name}.")

    def _validate_excluded_sheets(
        self,
        excluded_sheets: Optional[list[str]],
        available_sheet_names: Optional[set[str]],
        errors: list[str],
    ) -> None:
        if excluded_sheets is None or available_sheet_names is None:
            return
        missing_sheets = sorted(set(excluded_sheets).difference(available_sheet_names))
        for sheet_name in missing_sheets:
            errors.append(f"onglet absent du fichier: {sheet_name}.")
