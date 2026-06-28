#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-26
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : regles transverses de validation de description d'import.

from typing import Any, Optional

from .collection_file_description import (
    CollectionCsvConfiguration,
    CollectionFileType,
    CollectionImportField,
    CollectionMultipleSheetsConfiguration,
    CollectionSheetLayout,
    WishlistImportConfiguration,
    WishlistImportMode,
)


class CollectionFileDescriptionRules:
    """Regroupe les regles de coherence communes aux descriptions d'import."""

    def validate_top_level_modes(
        self,
        file_type: Optional[CollectionFileType],
        single_sheet_conf: Any,
        multiple_sheets_conf: Any,
        csv_mapping: Any,
        errors: list[str],
    ) -> None:
        """Valide l'exclusivite des modes de configuration racine.

        Args:
            file_type (Optional[CollectionFileType]): Type de fichier parse.
            single_sheet_conf (Any): Configuration feuille unique brute.
            multiple_sheets_conf (Any): Configuration multi-onglets brute.
            csv_mapping (Any): Mapping CSV brut.
            errors (list[str]): Erreurs a enrichir.

        Returns:
            None: La methode enrichit `errors`.
        """

        ods_config_count = sum(
            config is not None for config in (single_sheet_conf, multiple_sheets_conf)
        )
        if file_type == CollectionFileType.CSV:
            if ods_config_count:
                errors.append(
                    "single_sheet_conf et multiple_sheets_conf ne sont pas autorises pour csv."
                )
            if csv_mapping is None:
                errors.append("mapping est requis pour csv.")
            return
        if csv_mapping is not None:
            errors.append("mapping n'est autorise que pour csv.")
        if single_sheet_conf is not None and multiple_sheets_conf is not None:
            errors.append("single_sheet_conf et multiple_sheets_conf sont exclusifs.")
        if single_sheet_conf is None and multiple_sheets_conf is None:
            errors.append("un mode de configuration est requis.")
        if single_sheet_conf is not None and not isinstance(single_sheet_conf, dict):
            errors.append("single_sheet_conf doit etre un objet.")
        if multiple_sheets_conf is not None and not isinstance(multiple_sheets_conf, dict):
            errors.append("multiple_sheets_conf doit etre un objet.")

    def validate_csv_wishlist_configuration(
        self,
        csv_conf: Optional[CollectionCsvConfiguration],
        wishlist_configuration: Optional[WishlistImportConfiguration],
        errors: list[str],
    ) -> None:
        """Valide la coherence wishlist d'une configuration CSV.

        Args:
            csv_conf (Optional[CollectionCsvConfiguration]): Configuration CSV construite.
            wishlist_configuration (Optional[WishlistImportConfiguration]): Wishlist construite.
            errors (list[str]): Erreurs a enrichir.

        Returns:
            None: La methode enrichit `errors`.
        """

        if csv_conf is None or wishlist_configuration is None:
            return
        if wishlist_configuration.mode == WishlistImportMode.SHEET:
            errors.append("wishlist.mode sheet n'est pas autorise pour csv.")
            return
        if (
            wishlist_configuration.mode == WishlistImportMode.NONE
            and CollectionImportField.WISHLIST in csv_conf.column_information
        ):
            errors.append("wishlist.mode none ne doit pas utiliser de colonne wishlist.")

    def uses_purchase_price(
        self,
        single_sheet: Optional[CollectionSheetLayout],
        multiple_sheets: Optional[CollectionMultipleSheetsConfiguration],
        csv_conf: Optional[CollectionCsvConfiguration] = None,
        wishlist_configuration: Optional[WishlistImportConfiguration] = None,
    ) -> bool:
        """Indique si une configuration importe un prix d'achat.

        Args:
            single_sheet (Optional[CollectionSheetLayout]): Layout simple.
            multiple_sheets (Optional[CollectionMultipleSheetsConfiguration]): Layouts multiples.
            csv_conf (Optional[CollectionCsvConfiguration]): Mapping CSV.
            wishlist_configuration (Optional[WishlistImportConfiguration]): Configuration wishlist.

        Returns:
            bool: `True` lorsqu'un prix doit etre importe.
        """

        layouts = [single_sheet]
        if multiple_sheets is not None:
            layouts.append(multiple_sheets.shared_layout)
            layouts.extend(sheet.layout for sheet in multiple_sheets.sheets or [])
        if wishlist_configuration is not None:
            layouts.append(wishlist_configuration.layout)
        if (
            csv_conf is not None
            and CollectionImportField.PURCHASE_PRICE in csv_conf.column_information
        ):
            return True
        return any(
            layout is not None
            and CollectionImportField.PURCHASE_PRICE in layout.column_information
            for layout in layouts
        )
