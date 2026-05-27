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
# Description : DTOs du contrat de configuration d'import de collection.

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CollectionImportField(str, Enum):
    """Enumere les champs metier importables depuis un fichier de collection."""

    NAME = "name"
    PLATFORM = "platform"
    STUDIO = "studio"
    RELEASE_DATE = "release_date"


class CollectionFileType(str, Enum):
    """Enumere les formats de fichiers de collection pris en charge."""

    LIBREOFFICE_ODS = "libreoffice_ods"


@dataclass(frozen=True)
class CollectionSheetLayout:
    """Represente la disposition tabulaire commune a une ou plusieurs feuilles.

    Attributes:
        data_range (str): Plage tableur inclusive au format `A1:H200`.
        header_row (int): Ligne d'en-tete avec index tableur commencant a `1`.
        column_information (dict[CollectionImportField, str]): Colonnes par champ.
        included_sheets (Optional[list[str]]): Onglets inclus pour un layout partage.
    """

    data_range: str
    header_row: int
    column_information: dict[CollectionImportField, str]
    included_sheets: Optional[list[str]] = None


@dataclass(frozen=True)
class CollectionPerSheetConfiguration:
    """Represente la configuration specifique d'un onglet declare.

    Attributes:
        sheet_name (str): Nom non vide de l'onglet a importer.
        sheet_information (Optional[CollectionImportField]): Champ porte par le nom d'onglet.
        layout (CollectionSheetLayout): Disposition des donnees de l'onglet.
    """

    sheet_name: str
    sheet_information: Optional[CollectionImportField]
    layout: CollectionSheetLayout


@dataclass(frozen=True)
class CollectionMultipleSheetsConfiguration:
    """Represente une configuration d'import multi-onglets.

    Attributes:
        sheet_information (Optional[CollectionImportField]): Champ porte par le nom d'onglet.
        shared_layout (Optional[CollectionSheetLayout]): Layout commun aux onglets.
        sheets (Optional[list[CollectionPerSheetConfiguration]]): Layouts declares par onglet.
    """

    sheet_information: Optional[CollectionImportField] = None
    shared_layout: Optional[CollectionSheetLayout] = None
    sheets: Optional[list[CollectionPerSheetConfiguration]] = None


@dataclass(frozen=True)
class CollectionFileDescription:
    """Represente la description valide d'un fichier de collection.

    Attributes:
        file_type (CollectionFileType): Type de fichier cible.
        single_sheet_conf (Optional[CollectionSheetLayout]): Configuration feuille unique.
        multiple_sheets_conf (Optional[CollectionMultipleSheetsConfiguration]): Configuration multi-onglets.
    """

    file_type: CollectionFileType
    single_sheet_conf: Optional[CollectionSheetLayout] = None
    multiple_sheets_conf: Optional[CollectionMultipleSheetsConfiguration] = None
