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
import pandas as pd

from .ods_cache import OdsCache


class OdsReader:
    def __init__(
        self,
        ods_path: str,
        cache: OdsCache,
    ):
        """Initialise le lecteur ODS bas niveau dedie a l'import utilisateur.

        Args:
            ods_path (str): Chemin du fichier ODS.
            cache (OdsCache): Cache partage par le service.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.ods_path = ods_path
        self.cache = cache

    def list_sheets(self) -> list[str]:
        """Liste tous les onglets presents dans le fichier ODS.

        Args:
            Aucun.

        Returns:
            list[str]: Noms des onglets dans l'ordre du fichier.
        """

        return self.cache.remember("sheets", self._load_sheets)

    def read_sheet_dataframe(
        self,
        sheet_name: str,
        data_range: str,
        header_row: int,
        selected_columns: str | None = None,
    ) -> pd.DataFrame:
        """Lit une feuille ODS selon une plage et une ligne d'en-tete.

        Args:
            sheet_name (str): Nom de l'onglet a lire.
            data_range (str): Plage tableur inclusive, par exemple `A1:H200`.
            header_row (int): Ligne d'en-tete en index tableur commencant a `1`.
            selected_columns (str | None): Colonnes tableur a charger, par exemple `A,C,F`.

        Returns:
            pandas.DataFrame: Donnees de la feuille avec valeurs vides a `None`.
        """

        return self.cache.remember(
            f"sheet_dataframe:{sheet_name}:{data_range}:{header_row}:{selected_columns or '*'}",
            lambda: self._load_sheet_dataframe(
                sheet_name,
                data_range,
                header_row,
                selected_columns,
            ),
        )

    def _load_sheets(self) -> list[str]:
        """Charge les noms d'onglets depuis le fichier ODS.

        Args:
            Aucun.

        Returns:
            list[str]: Tous les noms d'onglets.
        """

        excel_file = pd.ExcelFile(self.ods_path, engine="odf")
        return list(excel_file.sheet_names)

    def _load_sheet_dataframe(
        self,
        sheet_name: str,
        data_range: str,
        header_row: int,
        selected_columns: str | None = None,
    ) -> pd.DataFrame:
        """Charge une feuille ODS avec les parametres configurables.

        Args:
            sheet_name (str): Nom de l'onglet.
            data_range (str): Plage tableur inclusive.
            header_row (int): Ligne d'en-tete commencant a `1`.
            selected_columns (str | None): Colonnes tableur a charger.

        Returns:
            pandas.DataFrame: Donnees lues depuis l'onglet.
        """

        read_options = {
            "sheet_name": sheet_name,
            "engine": "odf",
            "header": header_row - 1,
            "usecols": selected_columns or self._usecols_from_range(data_range),
            "nrows": self._data_row_count(data_range, header_row),
        }
        try:
            dataframe = pd.read_excel(self.ods_path, **read_options)
        except ValueError as exc:
            if selected_columns is None or not self._is_out_of_bounds_usecols_error(exc):
                raise
            read_options.pop("usecols")
            complete_dataframe = pd.read_excel(self.ods_path, **read_options)
            dataframe = self._select_columns_with_empty_fallback(
                complete_dataframe,
                selected_columns,
            )
        return dataframe.where(pd.notna(dataframe), None)

    def _is_out_of_bounds_usecols_error(self, error: ValueError) -> bool:
        """Detecte l'erreur pandas produite par des colonnes terminales absentes.

        Args:
            error (ValueError): Erreur de lecture pandas recue.

        Returns:
            bool: `True` lorsque les indices `usecols` depassent les colonnes materialisees.
        """

        return "out-of-bounds" in str(error).lower() and "usecols" in str(error).lower()

    def _select_columns_with_empty_fallback(
        self,
        dataframe: pd.DataFrame,
        selected_columns: str,
    ) -> pd.DataFrame:
        """Selectionne les colonnes demandees et complete celles absentes par `None`.

        Args:
            dataframe (pandas.DataFrame): Onglet complet lu sans filtre de colonnes.
            selected_columns (str): Colonnes tableur separees par des virgules.

        Returns:
            pandas.DataFrame: Colonnes demandees dans leur ordre, y compris les colonnes vides.
        """

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
        """Convertit une reference de colonne tableur en index base zero.

        Args:
            column (str): Reference alphabetique, par exemple `O`.

        Returns:
            int: Index de colonne base zero.
        """

        return sum(
            (ord(character) - ord("A") + 1) * (26 ** position)
            for position, character in enumerate(reversed(column))
        ) - 1

    def _usecols_from_range(self, data_range: str) -> str:
        """Extrait les colonnes utilisables par pandas depuis une plage.

        Args:
            data_range (str): Plage tableur inclusive.

        Returns:
            str: Plage de colonnes, par exemple `A:H`.
        """

        start_cell, end_cell = data_range.upper().split(":", 1)
        start_column = "".join(character for character in start_cell if character.isalpha())
        end_column = "".join(character for character in end_cell if character.isalpha())
        return f"{start_column}:{end_column}"

    def _data_row_count(self, data_range: str, header_row: int) -> int:
        """Calcule le nombre de lignes de donnees a lire apres l'en-tete.

        Args:
            data_range (str): Plage tableur inclusive.
            header_row (int): Ligne d'en-tete.

        Returns:
            int: Nombre maximal de lignes de donnees.
        """

        end_cell = data_range.upper().split(":", 1)[1]
        end_row = int("".join(character for character in end_cell if character.isdigit()))
        return max(end_row - header_row, 0)
