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
from .ods_xml_reader import OdsXmlReader


class OdsReader:
    def __init__(
        self,
        ods_path: str,
        cache: OdsCache,
        xml_reader: OdsXmlReader,
    ):
        """Initialise le lecteur ODS bas niveau dedie a l'import utilisateur.

        Args:
            ods_path (str): Chemin du fichier ODS.
            cache (OdsCache): Cache partage par le service.
            xml_reader (OdsXmlReader): Lecteur XML utilise en secours.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.ods_path = ods_path
        self.cache = cache
        self.xml_reader = xml_reader

    def list_platforms(self) -> list[str]:
        """Liste les onglets ODS correspondant a des plateformes.

        Args:
            Aucun.

        Returns:
            list[str]: Noms des onglets, hors `Accueil` et `Liste de souhaits`.
        """

        return self.cache.remember("platforms", self._load_platforms)

    def list_sheets(self) -> list[str]:
        """Liste tous les onglets presents dans le fichier ODS.

        Args:
            Aucun.

        Returns:
            list[str]: Noms des onglets dans l'ordre du fichier.
        """

        return self.cache.remember("sheets", self._load_sheets)

    def read_games_dataframe(self, platform: str) -> pd.DataFrame:
        """Lit les jeux d'une plateforme dans un DataFrame.

        Args:
            platform (str): Nom de l'onglet ODS a lire.

        Returns:
            pandas.DataFrame: Lignes de jeux avec colonnes normalisees.
        """

        return self.cache.remember(
            f"games_dataframe:{platform}",
            lambda: self._load_games_dataframe(platform),
        )

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

    def _load_platforms(self) -> list[str]:
        """Charge les plateformes depuis le fichier ODS.

        Args:
            Aucun.

        Returns:
            list[str]: Noms des onglets de plateformes.
        """

        excluded_sheets = {"Accueil", "Liste de souhaits"}
        return [sheet for sheet in self._load_sheets() if sheet not in excluded_sheets]

    def _load_sheets(self) -> list[str]:
        """Charge les noms d'onglets depuis le fichier ODS.

        Args:
            Aucun.

        Returns:
            list[str]: Tous les noms d'onglets.
        """

        excel_file = pd.ExcelFile(self.ods_path, engine="odf")
        return list(excel_file.sheet_names)

    def _load_games_dataframe(self, platform: str) -> pd.DataFrame:
        """Charge les jeux d'une plateforme depuis le fichier ODS.

        Args:
            platform (str): Nom de l'onglet ODS a lire.

        Returns:
            pandas.DataFrame: Jeux lus depuis l'onglet demande.
        """

        try:
            dataframe = pd.read_excel(
                self.ods_path,
                sheet_name=platform,
                engine="odf",
                header=5,
                usecols="F:M",
            )
            dataframe = dataframe.where(pd.notna(dataframe), None)
        except (TypeError, ValueError):
            if platform not in self.list_platforms():
                raise
            dataframe = self.xml_reader.read_games_dataframe_from_xml(platform)
        return self._normalize_games_dataframe_columns(dataframe)

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

        dataframe = pd.read_excel(
            self.ods_path,
            sheet_name=sheet_name,
            engine="odf",
            header=header_row - 1,
            usecols=selected_columns or self._usecols_from_range(data_range),
            nrows=self._data_row_count(data_range, header_row),
        )
        return dataframe.where(pd.notna(dataframe), None)

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

    def _normalize_games_dataframe_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Normalise les noms de colonnes contenant des apostrophes typographiques.

        Args:
            dataframe (pandas.DataFrame): Tableau de jeux lu depuis l'ODS.

        Returns:
            pandas.DataFrame: Tableau avec les noms de colonnes harmonises.
        """

        return dataframe.rename(
            columns={
                "Date d’achat": "Date d'achat",
                "Lieu d’achat": "Lieu d'achat",
                "Prix d’achat": "Prix d'achat",
            }
        )
