#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-04
# Auteurs : Codex et Binda Sébastien
# License : Apache 2.0
#
"""Edition des lignes de jeux dans le XML ODS.

Description:
    Cette classe encapsule les operations sur les colonnes F a M du tableau des jeux
    afin de ne pas modifier les colonnes hors perimetre.
"""

import copy
from datetime import datetime
from typing import Any, Optional
import xml.etree.ElementTree as ET

from .ods_namespaces import OdsNamespaces


class OdsGameRowEditor:
    """Edite les cellules d'une ligne de jeu sans toucher les autres colonnes."""

    game_columns = [
        "Nom du jeu",
        "Studio",
        "Date de sortie",
        "Date d'achat",
        "Lieu d'achat",
        "Note",
        "Prix d'achat",
        "Version",
    ]

    def __init__(self, xml_reader):
        """Initialise l'editeur de lignes de jeux.

        Args:
            xml_reader (OdsXmlReader): Lecteur XML capable d'expanser et lire les cellules.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.xml_reader = xml_reader
        self.namespaces = OdsNamespaces.values

    def find_next_available_game_row_index(
        self,
        rows: list[ET.Element],
        start_index: int,
    ) -> Optional[int]:
        """Trouve la prochaine ligne libre dans les colonnes du tableau des jeux.

        Args:
            rows (list[xml.etree.ElementTree.Element]): Lignes XML deja expansees.
            start_index (int): Index de depart de la recherche.

        Returns:
            Optional[int]: Index d'une ligne dont les colonnes F a M sont vides, sinon `None`.
        """

        for index in range(start_index, len(rows)):
            cells = self.xml_reader.expanded_cells(rows[index])
            game_cells = cells[5:13] if len(cells) > 5 else []
            if not any(self.xml_reader.cell_text_value(cell) for cell in game_cells):
                return index
        return None

    def find_game_row_index(
        self,
        rows: list[ET.Element],
        game: dict[str, Any],
    ) -> Optional[int]:
        """Trouve la ligne de plateforme correspondant au jeu cible.

        Args:
            rows (list[xml.etree.ElementTree.Element]): Lignes XML deja expansees.
            game (dict[str, Any]): Valeurs de jeu utilisees pour identifier la ligne.

        Returns:
            Optional[int]: Index de la ligne trouvee, sinon `None`.
        """

        expected_values = [self._normalized_text(game.get(column)) for column in self.game_columns]
        expected_name = expected_values[0]
        if not expected_name:
            return None

        name_matches = []
        for index, row in enumerate(rows):
            row_values = self._game_row_values(row)
            if row_values[0] != expected_name:
                continue
            name_matches.append(index)
            if self._matches_expected_values(row_values, expected_values):
                return index
        if len(name_matches) == 1:
            return name_matches[0]
        return None

    def set_game_row_values(
        self,
        row: ET.Element,
        template_row: ET.Element,
        game: dict[str, Any],
    ) -> None:
        """Remplit les cellules de jeu sans modifier les colonnes hors table.

        Args:
            row (xml.etree.ElementTree.Element): Ligne XML cible a completer.
            template_row (xml.etree.ElementTree.Element): Ligne modele pour les styles F a M.
            game (dict[str, Any]): Donnees du jeu a placer dans les colonnes F a M.

        Returns:
            None: La ligne XML est modifiee en place.
        """

        cells, game_cells = self._build_row_cells_preserving_unrelated_columns(row, template_row)
        values_by_index = {
            0: ("string", game["Nom du jeu"]),
            1: ("string", game["Studio"]),
            2: ("date", game["Date de sortie"]),
            3: ("date", game["Date d'achat"]),
            4: ("string", game["Lieu d'achat"]),
            5: ("string", game["Note"]),
            6: ("float", game["Prix d'achat"]),
            7: ("string", game["Version"]),
        }
        for index, (value_type, value) in values_by_index.items():
            self._set_cell_value(game_cells[index], value_type, value)

        self._replace_row_cells(row, cells)

    def clear_game_row_values(self, row: ET.Element) -> None:
        """Vide uniquement les cellules F a M d'une ligne de jeu.

        Args:
            row (xml.etree.ElementTree.Element): Ligne XML cible a nettoyer.

        Returns:
            None: Les cellules de jeu sont videes en place.
        """

        cells, game_cells = self._build_row_cells_preserving_unrelated_columns(row, row)
        for cell in game_cells:
            self._set_cell_value(cell, "string", "")

        self._replace_row_cells(row, cells)

    def _game_row_values(self, row: ET.Element) -> list[str]:
        """Retourne les valeurs normalisees des colonnes F a M d'une ligne.

        Args:
            row (xml.etree.ElementTree.Element): Ligne XML a lire.

        Returns:
            list[str]: Valeurs normalisees du tableau des jeux.
        """

        cells = self.xml_reader.expanded_cells(row)
        return [
            self._normalized_text(self.xml_reader.cell_text_value(cells[column_index]))
            if len(cells) > column_index
            else ""
            for column_index in range(5, 13)
        ]

    def _matches_expected_values(self, row_values: list[str], expected_values: list[str]) -> bool:
        """Indique si les valeurs non vides attendues correspondent a la ligne.

        Args:
            row_values (list[str]): Valeurs lues dans la ligne.
            expected_values (list[str]): Valeurs attendues depuis le payload.

        Returns:
            bool: `True` si toutes les valeurs attendues non vides correspondent.
        """

        return all(
            not value or row_values[value_index] == value
            for value_index, value in enumerate(expected_values)
        )

    def _build_row_cells_preserving_unrelated_columns(
        self,
        row: ET.Element,
        template_row: ET.Element,
    ) -> tuple[list[ET.Element], list[ET.Element]]:
        """Construit les cellules en preservant les colonnes hors table de jeux.

        Args:
            row (xml.etree.ElementTree.Element): Ligne cible contenant les cellules a conserver.
            template_row (xml.etree.ElementTree.Element): Ligne modele contenant les styles de jeu.

        Returns:
            tuple[list[xml.etree.ElementTree.Element], list[xml.etree.ElementTree.Element]]:
                Cellules de ligne et cellules de jeu a renseigner.
        """

        first_game_column = 5
        last_game_column = 12
        template_cells = self.xml_reader.expanded_cells(template_row)
        while len(template_cells) <= last_game_column:
            template_cells.append(ET.Element(f"{{{self.namespaces['table']}}}table-cell"))

        prefix_cells, prefix_size = self._copy_cell_range(row, 0, first_game_column - 1)
        while prefix_size < first_game_column:
            prefix_cells.append(ET.Element(f"{{{self.namespaces['table']}}}table-cell"))
            prefix_size += 1

        game_cells = [
            copy.deepcopy(template_cells[index])
            for index in range(first_game_column, last_game_column + 1)
        ]
        suffix_cells, _ = self._copy_cell_range(row, last_game_column + 1, None)
        return prefix_cells + game_cells + suffix_cells, game_cells

    def _copy_cell_range(
        self,
        row: ET.Element,
        first_column: int,
        last_column: Optional[int],
    ) -> tuple[list[ET.Element], int]:
        """Copie une plage de cellules ODS en conservant les repetitions possibles.

        Args:
            row (xml.etree.ElementTree.Element): Ligne source contenant les cellules a copier.
            first_column (int): Index zero-based de la premiere colonne a copier.
            last_column (Optional[int]): Index zero-based de la derniere colonne a copier, ou `None`.

        Returns:
            tuple[list[xml.etree.ElementTree.Element], int]: Cellules copiees et nombre de colonnes couvertes.
        """

        repeated_columns_attribute = f"{{{self.namespaces['table']}}}number-columns-repeated"
        selected_cells = []
        selected_size = 0
        current_column = 0
        for cell in list(row):
            if not cell.tag.endswith("table-cell"):
                continue
            repeated_columns = int(cell.attrib.get(repeated_columns_attribute, "1"))
            cell_start = current_column
            cell_end = current_column + repeated_columns - 1
            range_end = cell_end if last_column is None else min(cell_end, last_column)
            selected_start = max(cell_start, first_column)
            if selected_start <= range_end:
                selected_cell = self._copy_cell_with_repeat(cell, range_end - selected_start + 1)
                selected_cells.append(selected_cell)
                selected_size += range_end - selected_start + 1
            current_column += repeated_columns
            if last_column is not None and current_column > last_column:
                break
        return selected_cells, selected_size

    def _copy_cell_with_repeat(self, cell: ET.Element, repeat: int) -> ET.Element:
        """Copie une cellule et ajuste son attribut de repetition.

        Args:
            cell (xml.etree.ElementTree.Element): Cellule source.
            repeat (int): Nombre de colonnes que la copie doit couvrir.

        Returns:
            xml.etree.ElementTree.Element: Cellule copiee avec repetition ajustee.
        """

        repeated_columns_attribute = f"{{{self.namespaces['table']}}}number-columns-repeated"
        copied_cell = copy.deepcopy(cell)
        if repeat > 1:
            copied_cell.attrib[repeated_columns_attribute] = str(repeat)
        else:
            copied_cell.attrib.pop(repeated_columns_attribute, None)
        return copied_cell

    def _replace_row_cells(self, row: ET.Element, cells: list[ET.Element]) -> None:
        """Remplace les cellules XML d'une ligne.

        Args:
            row (xml.etree.ElementTree.Element): Ligne a modifier.
            cells (list[xml.etree.ElementTree.Element]): Nouvelles cellules a poser.

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
            cell (xml.etree.ElementTree.Element): Cellule a modifier.
            value_type (str): Type attendu, par exemple `string`, `date` ou `float`.
            value (Any): Valeur brute a ecrire.

        Returns:
            None: La cellule XML est modifiee en place.
        """

        office_value_type = f"{{{self.namespaces['office']}}}value-type"
        office_value = f"{{{self.namespaces['office']}}}value"
        office_date_value = f"{{{self.namespaces['office']}}}date-value"
        calcext_value_type = f"{{{self.namespaces['calcext']}}}value-type"
        table_formula = f"{{{self.namespaces['table']}}}formula"

        for attribute in [office_value_type, office_value, office_date_value, calcext_value_type, table_formula]:
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
        """Normalise une valeur pour comparer deux cellules ODS.

        Args:
            value (Any): Valeur brute issue du payload ou du XML.

        Returns:
            str: Texte minuscule sans espaces exterieurs.
        """

        return "" if value is None else str(value).strip().lower()

    def _is_iso_date(self, value: str) -> bool:
        """Indique si une chaine respecte le format date ISO `YYYY-MM-DD`.

        Args:
            value (str): Texte a valider.

        Returns:
            bool: `True` si le texte est une date ISO valide, sinon `False`.
        """

        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _is_number(self, value: str) -> bool:
        """Indique si une chaine represente un nombre.

        Args:
            value (str): Texte a valider, avec virgule ou point decimal accepte.

        Returns:
            bool: `True` si le texte est convertible en float, sinon `False`.
        """

        try:
            float(value.replace(",", "."))
            return True
        except ValueError:
            return False
