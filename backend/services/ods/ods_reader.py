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

    def _load_platforms(self) -> list[str]:
        """Charge les plateformes depuis le fichier ODS.

        Args:
            Aucun.

        Returns:
            list[str]: Noms des onglets de plateformes.
        """

        excel_file = pd.ExcelFile(self.ods_path, engine="odf")
        excluded_sheets = {"Accueil", "Liste de souhaits"}
        return [sheet for sheet in excel_file.sheet_names if sheet not in excluded_sheets]

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
