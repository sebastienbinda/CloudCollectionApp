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
"""Exports publics du contrat de configuration d'import de collection."""

from .collection_file_description import (
    CollectionFileDescription,
    CollectionFileType,
    CollectionImportField,
    CollectionMultipleSheetsConfiguration,
    CollectionPerSheetConfiguration,
    CollectionSheetLayout,
)
from .collection_file_description_validator import (
    CollectionFileDescriptionValidationError,
    CollectionFileDescriptionValidator,
)

__all__ = [
    "CollectionFileDescription",
    "CollectionFileDescriptionValidationError",
    "CollectionFileDescriptionValidator",
    "CollectionFileType",
    "CollectionImportField",
    "CollectionMultipleSheetsConfiguration",
    "CollectionPerSheetConfiguration",
    "CollectionSheetLayout",
]
