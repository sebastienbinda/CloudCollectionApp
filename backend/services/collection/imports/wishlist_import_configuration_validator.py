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
# Description : validation de la configuration wishlist d'import.

from typing import Any, Callable, Optional

from .collection_file_description import (
    CollectionImportField,
    CollectionMultipleSheetsConfiguration,
    CollectionSheetLayout,
    WishlistImportConfiguration,
    WishlistImportMode,
)

LayoutBuilder = Callable[
    [dict[str, Any], Optional[CollectionImportField], str, list[str], bool],
    CollectionSheetLayout,
]


class WishlistImportConfigurationValidator:
    """Valide la section wishlist du contrat de configuration d'import."""

    def build(
        self,
        payload: Any,
        errors: list[str],
        available_sheet_names: Optional[set[str]],
        layout_builder: LayoutBuilder,
    ) -> Optional[WishlistImportConfiguration]:
        """Construit la configuration wishlist depuis le payload JSON.

        Args:
            payload (Any): Section `wishlist` brute du payload.
            errors (list[str]): Liste d'erreurs de validation a enrichir.
            available_sheet_names (Optional[set[str]]): Onglets reels connus.
            layout_builder (LayoutBuilder): Fonction de construction d'un layout.

        Returns:
            Optional[WishlistImportConfiguration]: Configuration wishlist validee ou partielle.

        Raises:
            Aucun.
        """

        if payload is None:
            errors.append("wishlist est obligatoire.")
            return None
        if not isinstance(payload, dict):
            errors.append("wishlist doit etre un objet.")
            return None
        mode = self._parse_mode(payload.get("mode"), errors)
        if mode is None:
            return None
        if mode != WishlistImportMode.SHEET:
            return WishlistImportConfiguration(mode)

        sheet_name = str(payload.get("sheet_name") or "").strip()
        if not sheet_name:
            errors.append("wishlist.sheet_name est obligatoire en mode sheet.")
        elif available_sheet_names is not None and sheet_name not in available_sheet_names:
            errors.append(f"onglet absent du fichier: {sheet_name}.")
        layout = layout_builder(payload, None, "wishlist", errors, False)
        return WishlistImportConfiguration(mode, sheet_name, layout)

    def validate_collection_configuration(
        self,
        wishlist_configuration: Optional[WishlistImportConfiguration],
        wishlist_payload: Any,
        single_sheet: Optional[CollectionSheetLayout],
        multiple_sheets: Optional[CollectionMultipleSheetsConfiguration],
        errors: list[str],
    ) -> None:
        """Valide la coherence entre wishlist et layouts de collection.

        Args:
            wishlist_configuration (Optional[WishlistImportConfiguration]): Configuration wishlist.
            wishlist_payload (Any): Section `wishlist` brute du payload.
            single_sheet (Optional[CollectionSheetLayout]): Layout feuille unique.
            multiple_sheets (Optional[CollectionMultipleSheetsConfiguration]): Layouts multi-onglets.
            errors (list[str]): Liste d'erreurs de validation a enrichir.

        Returns:
            None: La methode enrichit `errors`.

        Raises:
            Aucun.
        """

        if wishlist_configuration is None or not isinstance(wishlist_payload, dict):
            return
        if wishlist_configuration.mode == WishlistImportMode.NONE:
            self._validate_none_payload(wishlist_payload, errors)
            self._validate_collection_layouts_do_not_define_wishlist(
                single_sheet,
                multiple_sheets,
                "wishlist.mode none ne doit pas utiliser de colonne wishlist.",
                errors,
            )
            return
        if wishlist_configuration.mode == WishlistImportMode.SHEET:
            self._validate_sheet_payload(wishlist_payload, wishlist_configuration, errors)
            self._validate_collection_layouts_do_not_define_wishlist(
                single_sheet,
                multiple_sheets,
                "wishlist.mode sheet ne doit pas utiliser de colonne wishlist dans la collection.",
                errors,
            )
            return
        self._validate_column_payload(wishlist_payload, errors)
        self._validate_collection_layouts_define_wishlist(single_sheet, multiple_sheets, errors)

    def _parse_mode(self, value: Any, errors: list[str]) -> Optional[WishlistImportMode]:
        if value is None or str(value).strip() == "":
            errors.append("wishlist.mode est obligatoire.")
            return None
        try:
            return WishlistImportMode(value)
        except ValueError:
            errors.append("wishlist.mode inconnu.")
            return None

    def _validate_none_payload(self, payload: dict[str, Any], errors: list[str]) -> None:
        if set(payload.keys()).difference({"mode"}):
            errors.append("wishlist.mode none ne doit pas definir de configuration d'onglet.")

    def _validate_sheet_payload(
        self,
        payload: dict[str, Any],
        configuration: WishlistImportConfiguration,
        errors: list[str],
    ) -> None:
        allowed_keys = {"mode", "sheet_name", "data_range", "header_row", "column_information"}
        if set(payload.keys()).difference(allowed_keys):
            errors.append("wishlist.mode sheet contient une configuration non autorisee.")
        if (
            configuration.layout is not None
            and CollectionImportField.WISHLIST in configuration.layout.column_information
        ):
            errors.append("wishlist.column_information ne doit pas contenir wishlist en mode sheet.")

    def _validate_column_payload(self, payload: dict[str, Any], errors: list[str]) -> None:
        if set(payload.keys()).difference({"mode"}):
            errors.append("wishlist.mode column ne doit pas definir de configuration d'onglet.")

    def _validate_collection_layouts_do_not_define_wishlist(
        self,
        single_sheet: Optional[CollectionSheetLayout],
        multiple_sheets: Optional[CollectionMultipleSheetsConfiguration],
        message: str,
        errors: list[str],
    ) -> None:
        for _, layout in self._named_collection_layouts(single_sheet, multiple_sheets):
            if CollectionImportField.WISHLIST in layout.column_information:
                errors.append(message)

    def _validate_collection_layouts_define_wishlist(
        self,
        single_sheet: Optional[CollectionSheetLayout],
        multiple_sheets: Optional[CollectionMultipleSheetsConfiguration],
        errors: list[str],
    ) -> None:
        for path, layout in self._named_collection_layouts(single_sheet, multiple_sheets):
            if CollectionImportField.WISHLIST not in layout.column_information:
                errors.append(f"{path}.column_information.wishlist est obligatoire en mode column.")

    def _named_collection_layouts(
        self,
        single_sheet: Optional[CollectionSheetLayout],
        multiple_sheets: Optional[CollectionMultipleSheetsConfiguration],
    ) -> list[tuple[str, CollectionSheetLayout]]:
        if single_sheet is not None:
            return [("single_sheet_conf", single_sheet)]
        if multiple_sheets is None:
            return []
        if multiple_sheets.shared_layout is not None:
            return [("multiple_sheets_conf.shared_layout", multiple_sheets.shared_layout)]
        return [
            (f"multiple_sheets_conf.sheets[{index}]", sheet.layout)
            for index, sheet in enumerate(multiple_sheets.sheets or [])
        ]
