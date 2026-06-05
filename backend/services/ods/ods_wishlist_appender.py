#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-08
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# License : Apache 2.0
#
"""Ajout de lignes dans la liste de souhaits ODS.

Description:
    Cette classe objet construit un `content.xml` avec un nouveau jeu ajoute
    dans l'onglet `Liste de souhaits`, sans allonger l'ecrivain ODS principal.
"""

import copy
from typing import Any, Optional
import xml.etree.ElementTree as ET

from .ods_namespaces import OdsNamespaces


class OdsWishlistAppender:
    """Construit le contenu ODS necessaire a l'ajout d'un jeu wishlist."""

    def __init__(self, archive_reader, xml_reader, row_editor, row_replacer):
        """Initialise l'ajouteur de ligne wishlist.

        Args:
            archive_reader (OdsArchiveReader): Lecteur des fichiers internes ODS.
            xml_reader (OdsXmlReader): Lecteur XML partage.
            row_editor (OdsWishlistRowEditor): Editeur des cellules wishlist.
            row_replacer (OdsSheetRowReplacer): Remplaceur de lignes ODS.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.archive_reader = archive_reader
        self.xml_reader = xml_reader
        self.row_editor = row_editor
        self.row_replacer = row_replacer
        self.namespaces = OdsNamespaces.values

    def build_content(self, game: dict[str, Any]) -> bytes:
        """Construit un nouveau `content.xml` avec un jeu wishlist ajoute.

        Args:
            game (dict[str, Any]): Donnees wishlist validees.

        Returns:
            bytes: Contenu XML encode en UTF-8 a reinjecter dans l'archive ODS.
        """

        root = ET.fromstring(self.archive_reader.read_file("content.xml"))
        sheet = self.xml_reader.find_sheet(root, "Liste de souhaits")
        row_tag = f"{{{self.namespaces['table']}}}table-row"
        repeated_rows_attribute = f"{{{self.namespaces['table']}}}number-rows-repeated"
        direct_children = list(sheet)
        row_insert_position = next(
            (index for index, child in enumerate(direct_children) if child.tag == row_tag),
            len(direct_children),
        )
        expanded_rows = self._expanded_rows(direct_children, row_tag, repeated_rows_attribute)
        template_row = self._find_template_row(expanded_rows)
        target_row_index = self._find_next_available_row_index(expanded_rows)
        if target_row_index is None:
            target_row_index = len(expanded_rows)
            expanded_rows.append(ET.Element(row_tag))
        target_row = copy.deepcopy(expanded_rows[target_row_index])
        self.row_editor.set_wishlist_row_values(target_row, template_row, game)
        expanded_rows[target_row_index] = target_row
        self.row_replacer.replace(sheet, row_tag, row_insert_position, expanded_rows)
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def _expanded_rows(
        self,
        direct_children: list[ET.Element],
        row_tag: str,
        repeated_rows_attribute: str,
    ) -> list[ET.Element]:
        """Expanse les lignes repetees d'une feuille ODS.

        Args:
            direct_children (list[xml.etree.ElementTree.Element]): Enfants directs de la feuille.
            row_tag (str): Balise XML des lignes.
            repeated_rows_attribute (str): Attribut ODS de repetition de lignes.

        Returns:
            list[xml.etree.ElementTree.Element]: Lignes clonees sans repetition.
        """

        expanded_rows = []
        for child in direct_children:
            if child.tag != row_tag:
                continue
            repeated_rows = int(child.attrib.get(repeated_rows_attribute, "1"))
            for _ in range(repeated_rows):
                expanded_row = copy.deepcopy(child)
                expanded_row.attrib.pop(repeated_rows_attribute, None)
                expanded_rows.append(expanded_row)
        return expanded_rows

    def _find_template_row(self, rows: list[ET.Element]) -> ET.Element:
        """Trouve une ligne modele pour conserver les styles wishlist.

        Args:
            rows (list[xml.etree.ElementTree.Element]): Lignes XML expansees.

        Returns:
            xml.etree.ElementTree.Element: Ligne modele clonee.
        """

        filled_rows = [
            row for row in rows
            if any(self.row_editor._wishlist_row_values(row))
        ]
        if filled_rows:
            return copy.deepcopy(filled_rows[-1])
        if rows:
            return copy.deepcopy(rows[-1])
        raise ValueError("Impossible de trouver une ligne modele dans la liste de souhaits.")

    def _find_next_available_row_index(self, rows: list[ET.Element]) -> Optional[int]:
        """Trouve une ligne wishlist libre.

        Args:
            rows (list[xml.etree.ElementTree.Element]): Lignes XML expansees.

        Returns:
            Optional[int]: Index libre trouve, sinon `None`.
        """

        for index, row in enumerate(rows):
            if index < 6:
                continue
            if not any(self.row_editor._wishlist_row_values(row)):
                return index
        return None
