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
# Description : messages d'erreur contextualises pour l'import ODS.

from typing import Any

from services.collection.imports import CollectionSheetLayout


class OdsImportErrorContext:
    """Construit les messages d'erreur contextualises de l'import ODS."""

    def sheet_message(
        self,
        message: str,
        sheet_name: str,
        layout: CollectionSheetLayout,
    ) -> str:
        """Construit un message contextualise par onglet.

        Args:
            message (str): Message principal.
            sheet_name (str): Onglet concerne.
            layout (CollectionSheetLayout): Layout configure.

        Returns:
            str: Message avec onglet, plage, ligne d'en-tete et colonnes.
        """

        return (
            f"{message}. Onglet: {sheet_name}. Plage: {layout.data_range}. "
            f"Ligne d'en-tete: {layout.header_row}. Colonnes: {self.column_context(layout)}."
        )

    def row_message(
        self,
        sheet_name: str,
        row_number: int,
        layout: CollectionSheetLayout,
    ) -> str:
        """Construit un message contextualise par ligne.

        Args:
            sheet_name (str): Onglet concerne.
            row_number (int): Ligne tableur concernee.
            layout (CollectionSheetLayout): Layout configure.

        Returns:
            str: Message avec onglet, ligne et colonnes.
        """

        return (
            f"Ligne de collection invalide. Onglet: {sheet_name}. Ligne: {row_number}. "
            f"Colonnes: {self.column_context(layout)}."
        )

    def column_context(self, layout: CollectionSheetLayout) -> str:
        """Retourne les colonnes configurees sous forme lisible.

        Args:
            layout (CollectionSheetLayout): Layout configure.

        Returns:
            str: Colonnes `champ=colonne`.
        """

        return ", ".join(
            f"{field.value}={column_name}"
            for field, column_name in layout.column_information.items()
        )

    def spreadsheet_row_number(self, layout: CollectionSheetLayout, row_index: Any) -> int:
        """Convertit un index DataFrame en ligne tableur approximative.

        Args:
            layout (CollectionSheetLayout): Layout configure.
            row_index (Any): Index de ligne pandas.

        Returns:
            int: Numero de ligne tableur.
        """

        try:
            return layout.header_row + int(row_index) + 1
        except (TypeError, ValueError):
            return layout.header_row + 1
