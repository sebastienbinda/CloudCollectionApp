#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-06
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : classe objet d'edition des lignes de jeux dans la liste de souhaits ODS.

import copy
from datetime import datetime
from typing import Any, Optional
import xml.etree.ElementTree as ET

from .ods_namespaces import OdsNamespaces


class OdsWishlistRowEditor:
    """Edite les cellules F a L d'une ligne de la liste de souhaits."""

    wishlist_columns = [
        "Nom du jeu",
        "Console",
        "Studio",
        "Date de sortie",
        "Date d'achat",
        "Lieu d'achat",
        "Prix d'achat",
    ]

    def __init__(self, xml_reader):
        """Initialise l'editeur wishlist.

        Args:
            xml_reader (OdsXmlReader): Lecteur XML partage.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.xml_reader = xml_reader
        self.namespaces = OdsNamespaces.values

    def find_wishlist_row_index(self, rows: list[ET.Element], game: dict[str, Any]) -> Optional[int]:
        """Trouve la ligne wishlist correspondant au nom et a la console.

        Args:
            rows (list[xml.etree.ElementTree.Element]): Lignes XML expansees.
            game (dict[str, Any]): Jeu cible contenant `Nom du jeu` et `Console`.

        Returns:
            Optional[int]: Index de ligne trouve, sinon `None`.
        """

        expected_name = self._normalized_text(game.get("Nom du jeu"))
        expected_console = self._normalized_text(game.get("Console") or game.get("Plateforme"))
        for index, row in enumerate(rows):
            values = self._wishlist_row_values(row)
            if values[0] == expected_name and values[1] == expected_console:
                return index
        return None

    def set_wishlist_row_values(self, row: ET.Element, template_row: ET.Element, game: dict[str, Any]) -> None:
        """Remplit les cellules wishlist sans modifier les colonnes hors table.

        Args:
            row (xml.etree.ElementTree.Element): Ligne XML cible.
            template_row (xml.etree.ElementTree.Element): Ligne modele pour les styles.
            game (dict[str, Any]): Donnees wishlist a placer dans F a L.

        Returns:
            None: La ligne XML est modifiee en place.
        """

        cells, wishlist_cells = self._build_row_cells(row, template_row)
        values_by_index = {
            0: ("string", game["Nom du jeu"]),
            1: ("string", game["Console"]),
            2: ("string", game["Studio"]),
            3: ("date", game["Date de sortie"]),
            4: ("date", game["Date d'achat"]),
            5: ("string", game["Lieu d'achat"]),
            6: ("float", game["Prix d'achat"]),
        }
        for index, (value_type, value) in values_by_index.items():
            self._set_cell_value(wishlist_cells[index], value_type, value)
        self._replace_row_cells(row, cells)

    def _wishlist_row_values(self, row: ET.Element) -> list[str]:
        """Retourne les valeurs normalisees des colonnes F a L.

        Args:
            row (xml.etree.ElementTree.Element): Ligne XML a lire.

        Returns:
            list[str]: Valeurs wishlist normalisees.
        """

        cells = self.xml_reader.expanded_cells(row)
        return [
            self._normalized_text(self.xml_reader.cell_text_value(cells[column_index]))
            if len(cells) > column_index
            else ""
            for column_index in range(5, 12)
        ]

    def _build_row_cells(self, row: ET.Element, template_row: ET.Element) -> tuple[list[ET.Element], list[ET.Element]]:
        """Construit les cellules en preservant les colonnes hors wishlist.

        Args:
            row (xml.etree.ElementTree.Element): Ligne cible.
            template_row (xml.etree.ElementTree.Element): Ligne modele.

        Returns:
            tuple[list[xml.etree.ElementTree.Element], list[xml.etree.ElementTree.Element]]: Cellules de ligne et wishlist.
        """

        first_column = 5
        last_column = 11
        template_cells = self.xml_reader.expanded_cells(template_row)
        while len(template_cells) <= last_column:
            template_cells.append(ET.Element(f"{{{self.namespaces['table']}}}table-cell"))
        prefix_cells = [copy.deepcopy(cell) for cell in self.xml_reader.expanded_cells(row)[:first_column]]
        while len(prefix_cells) < first_column:
            prefix_cells.append(ET.Element(f"{{{self.namespaces['table']}}}table-cell"))
        wishlist_cells = [copy.deepcopy(template_cells[index]) for index in range(first_column, last_column + 1)]
        suffix_cells = [copy.deepcopy(cell) for cell in self.xml_reader.expanded_cells(row)[last_column + 1:]]
        return prefix_cells + wishlist_cells + suffix_cells, wishlist_cells

    def _replace_row_cells(self, row: ET.Element, cells: list[ET.Element]) -> None:
        """Remplace les cellules XML d'une ligne.

        Args:
            row (xml.etree.ElementTree.Element): Ligne a modifier.
            cells (list[xml.etree.ElementTree.Element]): Nouvelles cellules.

        Returns:
            None: La ligne est modifiee en place.
        """

        for child in list(row):
            row.remove(child)
        for cell in cells:
            row.append(cell)

    def _set_cell_value(self, cell: ET.Element, value_type: str, value: Any) -> None:
        """Ecrit une valeur dans une cellule XML ODS.

        Args:
            cell (xml.etree.ElementTree.Element): Cellule cible.
            value_type (str): Type `string`, `date` ou `float`.
            value (Any): Valeur brute a ecrire.

        Returns:
            None: La cellule XML est modifiee en place.
        """

        office_value_type = f"{{{self.namespaces['office']}}}value-type"
        office_value = f"{{{self.namespaces['office']}}}value"
        office_date_value = f"{{{self.namespaces['office']}}}date-value"
        calcext_value_type = f"{{{self.namespaces['calcext']}}}value-type"
        for attribute in [office_value_type, office_value, office_date_value, calcext_value_type]:
            cell.attrib.pop(attribute, None)
        for child in list(cell):
            cell.remove(child)
        text_value = "" if value is None else str(value).strip()
        if not text_value:
            return
        if value_type == "date" and self._is_iso_date(text_value):
            cell.attrib[office_value_type] = "date"
            cell.attrib[office_date_value] = text_value
            cell.attrib[calcext_value_type] = "date"
        elif value_type == "float" and self._is_number(text_value):
            cell.attrib[office_value_type] = "float"
            cell.attrib[office_value] = text_value.replace(",", ".")
            cell.attrib[calcext_value_type] = "float"
        else:
            cell.attrib[office_value_type] = "string"
            cell.attrib[calcext_value_type] = "string"
        paragraph = ET.SubElement(cell, f"{{{self.namespaces['text']}}}p")
        paragraph.text = text_value

    def _normalized_text(self, value: Any) -> str:
        """Normalise une valeur pour comparaison.

        Args:
            value (Any): Valeur brute.

        Returns:
            str: Texte minuscule nettoye.
        """

        return "" if value is None else str(value).strip().lower()

    def _is_iso_date(self, value: str) -> bool:
        """Indique si une chaine respecte le format date ISO.

        Args:
            value (str): Texte a valider.

        Returns:
            bool: `True` si la date est valide.
        """

        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _is_number(self, value: str) -> bool:
        """Indique si une chaine represente un nombre.

        Args:
            value (str): Texte a convertir.

        Returns:
            bool: `True` si la valeur est numerique.
        """

        try:
            float(value.replace(",", "."))
            return True
        except ValueError:
            return False
