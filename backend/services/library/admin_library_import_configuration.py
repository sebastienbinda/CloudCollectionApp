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
# Description : chargement de la configuration fixe d'import CSV admin.

import json
from pathlib import Path
from typing import Any

from services.collection.imports import (
    CollectionFileDescription,
    CollectionFileDescriptionValidationError,
    CollectionFileDescriptionValidator,
)


class AdminLibraryImportConfigurationError(ValueError):
    """Signale une configuration d'import admin invalide."""

    def __init__(self, details: list[str]):
        """Initialise l'erreur de configuration admin.

        Args:
            details (list[str]): Messages de validation lisibles.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.details = details
        super().__init__("Configuration d'import admin invalide.")


class AdminLibraryImportConfigurationLoader:
    """Charge la configuration fixe d'import CSV admin depuis les ressources."""

    REQUIRED_FIELDS = {"name", "platform"}
    ALLOWED_FIELDS = {"name", "platform", "studio", "release_date"}

    def __init__(
        self,
        configuration_path: Path | None = None,
        validator: CollectionFileDescriptionValidator | None = None,
    ):
        """Initialise le chargeur de configuration admin.

        Args:
            configuration_path (Path | None): Chemin JSON optionnel.
            validator (CollectionFileDescriptionValidator | None): Validateur DTO injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration_path = configuration_path or self.default_configuration_path()
        self.validator = validator or CollectionFileDescriptionValidator()

    @classmethod
    def default_configuration_path(cls) -> Path:
        """Retourne le chemin de la configuration embarquee.

        Args:
            Aucun.

        Returns:
            Path: Chemin `backend/resources/admin_import_conf.json`.
        """

        return Path(__file__).resolve().parents[2] / "resources" / "admin_import_conf.json"

    def load_for_columns(self, columns: list[str]) -> CollectionFileDescription:
        """Construit une description CSV depuis les colonnes du fichier.

        Args:
            columns (list[str]): Noms d'en-tetes CSV disponibles dans l'ordre.

        Returns:
            CollectionFileDescription: Description valide pour le reader CSV commun.

        Raises:
            AdminLibraryImportConfigurationError: Si le JSON fixe est invalide.
            CollectionFileDescriptionValidationError: Si la description convertie est invalide.
        """

        payload = self._load_payload()
        self._validate_payload(payload)
        converted_payload = self._build_reader_payload(payload["mapping"], columns)
        try:
            return self.validator.validate(converted_payload, set(columns))
        except CollectionFileDescriptionValidationError:
            raise

    def _load_payload(self) -> dict[str, Any]:
        try:
            with self.configuration_path.open(encoding="utf-8") as configuration_file:
                payload = json.load(configuration_file)
        except FileNotFoundError as exc:
            raise AdminLibraryImportConfigurationError(
                ["resources/admin_import_conf.json est introuvable."]
            ) from exc
        except json.JSONDecodeError as exc:
            raise AdminLibraryImportConfigurationError(
                ["resources/admin_import_conf.json contient un JSON invalide."]
            ) from exc
        if not isinstance(payload, dict):
            raise AdminLibraryImportConfigurationError(
                ["resources/admin_import_conf.json doit contenir un objet JSON."]
            )
        return payload

    def _validate_payload(self, payload: dict[str, Any]) -> None:
        errors: list[str] = []
        if payload.get("file_type") != "csv":
            errors.append("file_type doit valoir csv.")
        mapping = payload.get("mapping")
        if not isinstance(mapping, dict):
            errors.append("mapping est requis.")
        else:
            fields = set(mapping)
            unknown_fields = sorted(fields.difference(self.ALLOWED_FIELDS))
            missing_fields = sorted(self.REQUIRED_FIELDS.difference(fields))
            if unknown_fields:
                errors.append(f"mapping contient des champs inconnus: {', '.join(unknown_fields)}.")
            if missing_fields:
                errors.append(f"mapping doit definir: {', '.join(missing_fields)}.")
            for field_name, column_index in mapping.items():
                if not isinstance(column_index, int) or column_index < 1:
                    errors.append(f"mapping.{field_name} doit etre un index entier positif.")
        if errors:
            raise AdminLibraryImportConfigurationError(errors)

    def _build_reader_payload(self, mapping: dict[str, int], columns: list[str]) -> dict[str, Any]:
        converted_mapping: dict[str, str] = {}
        errors: list[str] = []
        for field_name, column_index in mapping.items():
            if column_index > len(columns):
                errors.append(f"mapping.{field_name} cible une colonne CSV absente.")
                continue
            converted_mapping[field_name] = columns[column_index - 1]
        if errors:
            raise AdminLibraryImportConfigurationError(errors)
        return {
            "file_type": "csv",
            "wishlist": {"mode": "none"},
            "mapping": converted_mapping,
        }
