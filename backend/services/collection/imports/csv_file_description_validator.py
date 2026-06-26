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
# Description : validation de la configuration d'import CSV de collection.

from typing import Any, Optional

from .collection_file_description import CollectionCsvConfiguration, CollectionImportField


class CsvFileDescriptionValidator:
    """Valide la section de mapping propre aux fichiers CSV."""

    REQUIRED_FIELDS = {
        CollectionImportField.NAME,
        CollectionImportField.PLATFORM,
    }

    def build(
        self,
        payload: Any,
        wishlist_mode: str,
        errors: list[str],
        available_column_names: Optional[set[str]] = None,
    ) -> CollectionCsvConfiguration | None:
        """Construit la configuration CSV depuis un payload JSON.

        Args:
            payload (Any): Valeur brute de la cle `mapping`.
            wishlist_mode (str): Mode wishlist deja lu.
            errors (list[str]): Liste d'erreurs de validation a enrichir.
            available_column_names (Optional[set[str]]): Colonnes detectees si connues.

        Returns:
            CollectionCsvConfiguration | None: Configuration CSV valide ou absence.
        """

        if not isinstance(payload, dict):
            errors.append("mapping doit etre un objet.")
            return None
        parsed_columns: dict[CollectionImportField, str] = {}
        normalized_available_columns = self._normalized_available_columns(available_column_names)
        for field_name, column_name in payload.items():
            field = self._parse_field(field_name, errors)
            if field is None:
                continue
            column_value = str(column_name or "").strip()
            if not column_value:
                errors.append(f"mapping.{field.value} doit etre une colonne CSV.")
                continue
            if normalized_available_columns is not None and column_value not in normalized_available_columns:
                errors.append(f"colonne CSV absente: {column_value}.")
                continue
            parsed_columns[field] = column_value
        self._validate_required_fields(parsed_columns, wishlist_mode, errors)
        return CollectionCsvConfiguration(parsed_columns)

    def _parse_field(
        self,
        field_name: str,
        errors: list[str],
    ) -> CollectionImportField | None:
        try:
            return CollectionImportField(field_name)
        except ValueError:
            errors.append(f"mapping contient un champ inconnu: {field_name}.")
            return None

    def _validate_required_fields(
        self,
        parsed_columns: dict[CollectionImportField, str],
        wishlist_mode: str,
        errors: list[str],
    ) -> None:
        required_fields = set(self.REQUIRED_FIELDS)
        if wishlist_mode == "column":
            required_fields.add(CollectionImportField.WISHLIST)
        missing_fields = sorted(
            field.value for field in required_fields.difference(parsed_columns)
        )
        for field_name in missing_fields:
            errors.append(f"colonne obligatoire manquante: {field_name}.")

    def _normalized_available_columns(
        self,
        available_column_names: Optional[set[str]],
    ) -> set[str] | None:
        if available_column_names is None:
            return None
        return {str(column_name).strip() for column_name in available_column_names}
