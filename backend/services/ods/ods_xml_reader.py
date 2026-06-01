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
import copy
from typing import Any, Optional
import xml.etree.ElementTree as ET

from .ods_archive_reader import OdsArchiveReader
from .ods_cache import OdsCache
from .ods_namespaces import OdsNamespaces


class OdsXmlReader:
    def __init__(self, archive_reader: OdsArchiveReader, cache: OdsCache):
        """Initialise le lecteur XML interne de l'ODS.

        Args:
            archive_reader (OdsArchiveReader): Lecteur des fichiers internes ODS.
            cache (OdsCache): Cache partage par le service.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.archive_reader = archive_reader
        self.cache = cache
        self.namespaces = OdsNamespaces.values

    def find_sheet(self, root: ET.Element, sheet_name: str) -> ET.Element:
        """Recherche un onglet dans l'arbre XML de l'ODS.

        Args:
            root (xml.etree.ElementTree.Element): Racine XML de `content.xml`.
            sheet_name (str): Nom exact de l'onglet recherche.

        Returns:
            xml.etree.ElementTree.Element: Element XML de l'onglet.

        Raises:
            ValueError: Si l'onglet n'existe pas.
        """

        table_name_attribute = f"{{{self.namespaces['table']}}}name"
        sheet = next(
            (
                table
                for table in root.findall(".//table:table", self.namespaces)
                if table.attrib.get(table_name_attribute) == sheet_name
            ),
            None,
        )
        if sheet is None:
            raise ValueError(f"Sheet '{sheet_name}' not found in ODS file.")
        return sheet

    def expanded_cells(self, row: ET.Element) -> list[ET.Element]:
        """Developpe les cellules repetees d'une ligne ODS.

        Args:
            row (xml.etree.ElementTree.Element): Ligne XML contenant des cellules ODS.

        Returns:
            list[xml.etree.ElementTree.Element]: Cellules individuelles sans repetition.
        """

        repeated_columns_attribute = f"{{{self.namespaces['table']}}}number-columns-repeated"
        cells = []
        for cell in list(row):
            if not cell.tag.endswith("table-cell"):
                continue
            repeated_columns = int(cell.attrib.get(repeated_columns_attribute, "1"))
            for _ in range(repeated_columns):
                expanded_cell = copy.deepcopy(cell)
                expanded_cell.attrib.pop(repeated_columns_attribute, None)
                cells.append(expanded_cell)
        return cells

    def row_text_values(self, row: ET.Element) -> list[str]:
        """Extrait tous les textes non vides d'une ligne XML ODS.

        Args:
            row (xml.etree.ElementTree.Element): Ligne XML a inspecter.

        Returns:
            list[str]: Textes des cellules non vides.
        """

        return [
            value
            for value in (self.cell_text_value(cell) for cell in self.expanded_cells(row))
            if value
        ]

    def cell_text_value(self, cell: ET.Element) -> Optional[str]:
        """Extrait le texte visible d'une cellule ODS.

        Args:
            cell (xml.etree.ElementTree.Element): Cellule XML a lire.

        Returns:
            Optional[str]: Texte concatene des paragraphes, ou `None` si vide.
        """

        text_parts = []
        for paragraph in cell.findall(".//text:p", self.namespaces):
            text_parts.append("".join(paragraph.itertext()))
        text = "\n".join(part for part in text_parts if part).strip()
        return text or None

    def read_sheet_rows(self, sheet_name: str) -> list[list[Any]]:
        """Lit toutes les lignes d'un onglet depuis le XML interne de l'ODS.

        Args:
            sheet_name (str): Nom exact de l'onglet a extraire.

        Returns:
            list[list[Any]]: Lignes de cellules avec repetitions ODS developpees.
        """

        return self.cache.remember(
            f"sheet_rows:{sheet_name}",
            lambda: self._read_uncached_sheet_rows(sheet_name),
        )

    def _read_uncached_sheet_rows(self, sheet_name: str) -> list[list[Any]]:
        """Lit les lignes XML d'un onglet sans passer par le cache.

        Args:
            sheet_name (str): Nom exact de l'onglet a extraire.

        Returns:
            list[list[Any]]: Lignes de cellules de l'onglet demande.
        """

        table_name_attribute = f"{{{self.namespaces['table']}}}name"
        repeated_rows_attribute = f"{{{self.namespaces['table']}}}number-rows-repeated"
        repeated_columns_attribute = f"{{{self.namespaces['table']}}}number-columns-repeated"
        value_type_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value-type"
        value_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value"
        date_value_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}date-value"

        root = ET.fromstring(self.archive_reader.read_file("content.xml"))
        sheet = next(
            (
                table
                for table in root.findall(".//table:table", self.namespaces)
                if table.attrib.get(table_name_attribute) == sheet_name
            ),
            None,
        )
        if sheet is None:
            raise ValueError(f"Sheet '{sheet_name}' not found in ODS file.")

        rows = []
        for table_row in sheet.findall("table:table-row", self.namespaces):
            repeated_rows = int(table_row.attrib.get(repeated_rows_attribute, "1"))
            row_values = []
            for cell in list(table_row):
                if not cell.tag.endswith("table-cell"):
                    continue
                repeated_columns = int(cell.attrib.get(repeated_columns_attribute, "1"))
                value = self.extract_cell_value(
                    cell,
                    value_type_attribute,
                    value_attribute,
                    date_value_attribute,
                )
                row_values.extend([value] * repeated_columns)
            for _ in range(repeated_rows):
                rows.append(list(row_values))
        return rows

    def extract_cell_value(
        self,
        cell: ET.Element,
        value_type_attribute: str,
        value_attribute: str,
        date_value_attribute: str,
    ) -> Any:
        """Extrait une valeur Python depuis une cellule XML ODS.

        Args:
            cell (xml.etree.ElementTree.Element): Cellule XML source.
            value_type_attribute (str): Nom qualifie de l'attribut `office:value-type`.
            value_attribute (str): Nom qualifie de l'attribut numerique `office:value`.
            date_value_attribute (str): Nom qualifie de l'attribut date `office:date-value`.

        Returns:
            Any: int, float, str ou `None` selon le contenu de la cellule.
        """

        value_type = cell.attrib.get(value_type_attribute)
        if value_type == "float" and value_attribute in cell.attrib:
            value = float(cell.attrib[value_attribute])
            return int(value) if value.is_integer() else value
        if value_type == "float":
            return None
        if value_type == "date" and date_value_attribute in cell.attrib:
            return cell.attrib[date_value_attribute]
        if value_type == "date":
            return None
        return self.cell_text_value(cell)
