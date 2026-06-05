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
# Description : classe utilitaire de remplacement des lignes XML d'une feuille ODS.

import xml.etree.ElementTree as ET


class OdsSheetRowReplacer:
    """Remplace les lignes `table-row` d'une feuille ODS en preservant leur position."""

    def replace(
        self,
        sheet: ET.Element,
        row_tag: str,
        row_insert_position: int,
        rows: list[ET.Element],
    ) -> None:
        """Remplace les lignes XML d'une feuille.

        Args:
            sheet (xml.etree.ElementTree.Element): Feuille ODS cible.
            row_tag (str): Balise XML des lignes.
            row_insert_position (int): Position d'insertion des lignes.
            rows (list[xml.etree.ElementTree.Element]): Lignes a inserer.

        Returns:
            None: La feuille est modifiee en place.
        """

        for child in list(sheet):
            if child.tag == row_tag:
                sheet.remove(child)
        for offset, row in enumerate(rows):
            sheet.insert(row_insert_position + offset, row)
