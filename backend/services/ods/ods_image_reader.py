#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
import os
from mimetypes import guess_type
from typing import Optional
import xml.etree.ElementTree as ET

from .ods_archive_reader import OdsArchiveReader
from .ods_cache import OdsCache
from .ods_namespaces import OdsNamespaces
from services.formatting import SheetValueFormatter


class OdsImageReader:
    def __init__(self, archive_reader: OdsArchiveReader, cache: OdsCache):
        """Initialise le lecteur d'images embarquees dans l'ODS.

        Args:
            archive_reader (OdsArchiveReader): Lecteur des fichiers internes ODS.
            cache (OdsCache): Cache partage par le service.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.archive_reader = archive_reader
        self.cache = cache
        self.namespaces = OdsNamespaces.values

    def get_platform_image(self, platform: str) -> tuple[bytes, str, str]:
        """Retourne l'image embarquee dans l'onglet d'une plateforme.

        Args:
            platform (str): Nom exact ou normalise de la plateforme recherchee.

        Returns:
            tuple[bytes, str, str]: Contenu binaire, MIME type et nom de fichier de l'image.
        """

        image_path = self._find_platform_image_path(platform)
        if not image_path:
            raise ValueError(f"No image found for platform '{platform}'.")

        image_bytes = self.archive_reader.read_file(image_path)
        mime_type = guess_type(image_path)[0] or "application/octet-stream"
        filename = os.path.basename(image_path)
        return image_bytes, mime_type, filename

    def list_platform_image_paths(self) -> dict[str, str]:
        """Liste les chemins des images embarquees par onglet ODS.

        Args:
            Aucun.

        Returns:
            dict[str, str]: Dictionnaire `nom_onglet -> chemin_image_dans_archive`.
        """

        return self.cache.remember("platform_image_paths", self._load_image_paths)

    def _find_platform_image_path(self, platform: str) -> Optional[str]:
        """Recherche le chemin d'image associe a une plateforme.

        Args:
            platform (str): Nom exact ou normalise de la plateforme recherchee.

        Returns:
            Optional[str]: Chemin d'image interne, ou `None` si absent.
        """

        image_paths_by_sheet = self.list_platform_image_paths()
        image_path = image_paths_by_sheet.get(platform)
        if image_path:
            return image_path

        normalized_platform = SheetValueFormatter.normalize_platform_name(platform)
        return next(
            (
                path
                for sheet_name, path in image_paths_by_sheet.items()
                if SheetValueFormatter.normalize_platform_name(sheet_name) == normalized_platform
            ),
            None,
        )

    def _load_image_paths(self) -> dict[str, str]:
        """Charge les chemins des images embarquees depuis le XML ODS.

        Args:
            Aucun.

        Returns:
            dict[str, str]: Chemins d'images indexes par onglet.
        """

        table_name_attribute = f"{{{self.namespaces['table']}}}name"
        href_attribute = f"{{{self.namespaces['xlink']}}}href"
        image_paths: dict[str, str] = {}

        content = self.archive_reader.read_file("content.xml")
        root = ET.fromstring(content)
        for table in root.findall(".//table:table", self.namespaces):
            sheet_name = table.attrib.get(table_name_attribute)
            if not sheet_name:
                continue

            image_path = next(
                (
                    image.attrib.get(href_attribute)
                    for image in table.findall(".//draw:image", self.namespaces)
                    if (image.attrib.get(href_attribute) or "").startswith("Pictures/")
                ),
                None,
            )
            if image_path:
                image_paths[sheet_name] = image_path
        return image_paths
