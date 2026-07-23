#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-07-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : lecteur bas niveau des classeurs Excel XLSX.

import pandas as pd


class ExcelSpreadsheetReader:
    """Lit les onglets et plages d'un classeur Excel XLSX."""

    def __init__(self, excel_path: str):
        """Initialise le lecteur Excel.

        Args:
            excel_path (str): Chemin du fichier `.xlsx`.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.excel_path = excel_path
        self._excel_file = None
        self._cache: dict[str, object] = {}

    def list_sheets(self) -> list[str]:
        """Liste les onglets presents dans le classeur.

        Args:
            Aucun.

        Returns:
            list[str]: Noms d'onglets dans l'ordre du classeur.
        """

        return self._remember("sheets", lambda: list(self._excel_file_handle().sheet_names))

    def read_sheet_dataframe(
        self,
        sheet_name: str,
        data_range: str,
        header_row: int,
        selected_columns: str | None = None,
    ) -> pd.DataFrame:
        """Lit une feuille Excel selon la plage configuree.

        Args:
            sheet_name (str): Nom de l'onglet a lire.
            data_range (str): Plage tableur inclusive, par exemple `A1:H200`.
            header_row (int): Ligne d'en-tete en index tableur commencant a `1`.
            selected_columns (str | None): Colonnes tableur a charger, par exemple `A,C,F`.

        Returns:
            pandas.DataFrame: Donnees de la feuille avec valeurs vides a `None`.
        """

        return self._remember(
            f"sheet:{sheet_name}:{data_range}:{header_row}:{selected_columns or '*'}",
            lambda: self._load_sheet_dataframe(
                sheet_name,
                data_range,
                header_row,
                selected_columns,
            ),
        )

    def close(self) -> None:
        """Ferme le handle pandas conserve pendant l'import.

        Args:
            Aucun.

        Returns:
            None: La methode libere le classeur si disponible.
        """

        if self._excel_file is not None:
            close = getattr(self._excel_file, "close", None)
            if callable(close):
                close()
        self._excel_file = None
        self._cache.clear()

    def _remember(self, key: str, loader):
        if key not in self._cache:
            self._cache[key] = loader()
        return self._cache[key]

    def _excel_file_handle(self):
        if self._excel_file is None:
            self._excel_file = pd.ExcelFile(self.excel_path, engine="openpyxl")
        return self._excel_file

    def _load_sheet_dataframe(
        self,
        sheet_name: str,
        data_range: str,
        header_row: int,
        selected_columns: str | None,
    ) -> pd.DataFrame:
        read_options = {
            "sheet_name": sheet_name,
            "engine": "openpyxl",
            "header": header_row - 1,
            "usecols": selected_columns or self._usecols_from_range(data_range),
            "nrows": self._data_row_count(data_range, header_row),
        }
        try:
            dataframe = pd.read_excel(self._excel_file_handle(), **read_options)
        except ValueError as exc:
            if selected_columns is None or not self._is_out_of_bounds_usecols_error(exc):
                raise
            read_options.pop("usecols")
            complete_dataframe = pd.read_excel(self._excel_file_handle(), **read_options)
            dataframe = self._select_columns_with_empty_fallback(
                complete_dataframe,
                selected_columns,
            )
        return dataframe.where(pd.notna(dataframe), None)

    def _is_out_of_bounds_usecols_error(self, error: ValueError) -> bool:
        return "out-of-bounds" in str(error).lower() and "usecols" in str(error).lower()

    def _select_columns_with_empty_fallback(
        self,
        dataframe: pd.DataFrame,
        selected_columns: str,
    ) -> pd.DataFrame:
        columns = [column.strip().upper() for column in selected_columns.split(",")]
        selected_series = []
        for column in columns:
            column_index = self._column_to_index(column)
            if column_index < len(dataframe.columns):
                selected_series.append(dataframe.iloc[:, column_index])
            else:
                selected_series.append(pd.Series(None, index=dataframe.index, dtype=object))
        selected_dataframe = pd.concat(selected_series, axis=1)
        selected_dataframe.columns = columns
        return selected_dataframe

    def _column_to_index(self, column: str) -> int:
        return sum(
            (ord(character) - ord("A") + 1) * (26 ** position)
            for position, character in enumerate(reversed(column))
        ) - 1

    def _usecols_from_range(self, data_range: str) -> str:
        start_cell, end_cell = data_range.upper().split(":", 1)
        start_column = "".join(character for character in start_cell if character.isalpha())
        end_column = "".join(character for character in end_cell if character.isalpha())
        return f"{start_column}:{end_column}"

    def _data_row_count(self, data_range: str, header_row: int) -> int:
        end_cell = data_range.upper().split(":", 1)[1]
        end_row = int("".join(character for character in end_cell if character.isdigit()))
        return max(end_row - header_row, 0)
