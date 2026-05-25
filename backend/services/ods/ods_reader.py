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
import os
from typing import Any, Optional

import pandas as pd

from .ods_cache import OdsCache
from .ods_image_reader import OdsImageReader
from .ods_xml_reader import OdsXmlReader
from services.formatting import SheetValueFormatter


class OdsReader:
    def __init__(
        self,
        ods_path: str,
        cache: OdsCache,
        xml_reader: OdsXmlReader,
        image_reader: OdsImageReader,
    ):
        """Initialise le lecteur de donnees metier depuis l'ODS.

        Args:
            ods_path (str): Chemin du fichier ODS.
            cache (OdsCache): Cache partage par le service.
            xml_reader (OdsXmlReader): Lecteur XML utilise en secours.
            image_reader (OdsImageReader): Lecteur des images embarquees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.ods_path = ods_path
        self.cache = cache
        self.xml_reader = xml_reader
        self.image_reader = image_reader

    def list_platforms(self) -> list[str]:
        """Liste les onglets ODS correspondant a des plateformes.

        Args:
            Aucun.

        Returns:
            list[str]: Noms des onglets, hors `Accueil` et `Liste de souhaits`.
        """

        return self.cache.remember("platforms", self._load_platforms)

    def get_home_stats(self) -> dict[str, Any]:
        """Lit les statistiques de l'onglet `Accueil`.

        Args:
            Aucun.

        Returns:
            dict[str, Any]: Titre, plateformes, totaux, premiere date et derniere date.
        """

        return self.cache.remember("home_stats", self._load_home_stats)

    def list_column_values(self, platform: str) -> dict[str, list[str]]:
        """Retourne les valeurs distinctes de chaque colonne d'une plateforme.

        Args:
            platform (str): Nom de l'onglet ODS a lire.

        Returns:
            dict[str, list[str]]: Dictionnaire `nom_colonne -> valeurs uniques triees`.
        """

        return self.cache.remember(
            f"column_values:{platform}",
            lambda: self._load_column_values(platform),
        )

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

    def _load_home_stats(self) -> dict[str, Any]:
        """Charge les statistiques d'accueil depuis le fichier ODS.

        Args:
            Aucun.

        Returns:
            dict[str, Any]: Statistiques d'accueil serialisables en JSON.
        """

        try:
            dataframe = pd.read_excel(self.ods_path, sheet_name="Accueil", engine="odf", header=5)
        except (TypeError, ValueError):
            return self._load_computed_home_stats()
        dataframe = dataframe.where(pd.notna(dataframe), None)
        sheet_names_by_key = {
            SheetValueFormatter.normalize_platform_name(platform): platform
            for platform in self.list_platforms()
        }
        image_paths_by_sheet = self.image_reader.list_platform_image_paths()
        platforms, totals = [], {}
        first_game_date, last_game_date = None, None

        for row in dataframe.to_dict(orient="records"):
            platform_name = SheetValueFormatter.clean_text(row.get("Plateforme"))
            if not platform_name:
                continue
            if platform_name == "Total":
                totals = self._build_home_totals(row)
                continue
            if platform_name == "Date du premier jeu":
                first_game_date = SheetValueFormatter.serialize(row.get("Prix"))
                continue
            if platform_name == "Date du dernier jeu":
                last_game_date = SheetValueFormatter.serialize(row.get("Prix"))
                continue
            platform_stats = self._build_platform_stats(
                row,
                platform_name,
                sheet_names_by_key,
                image_paths_by_sheet,
            )
            computed_stats = self._compute_platform_stats(platform_stats["sheet_name"])
            platforms.append(self._merge_platform_stats(platform_stats, computed_stats))

        computed_totals = self._compute_home_totals(platforms)
        totals = self._merge_home_totals(totals, computed_totals)
        if first_game_date is None:
            first_game_date = computed_totals["first_game_date"]
        if last_game_date is None:
            last_game_date = computed_totals["last_game_date"]

        return {
            "title": os.getenv("APP_HOME_TITLE", "Ma collection"),
            "platforms": platforms,
            "totals": totals,
            "first_game_date": first_game_date,
            "last_game_date": last_game_date,
        }

    def _load_computed_home_stats(self) -> dict[str, Any]:
        """Construit l'accueil depuis les plateformes si l'onglet Accueil est illisible.

        Args:
            Aucun.

        Returns:
            dict[str, Any]: Statistiques d'accueil recalculees sans valeurs de formules en cache.
        """

        image_paths_by_sheet = self.image_reader.list_platform_image_paths()
        platforms = []
        for platform in self.list_platforms():
            computed_stats = self._compute_platform_stats(platform)
            platforms.append(
                {
                    "name": platform,
                    "sheet_name": platform,
                    "image_url": self._build_platform_image_url(platform),
                    "has_image": platform in image_paths_by_sheet,
                    **computed_stats,
                }
            )
        computed_totals = self._compute_home_totals(platforms)
        return {
            "title": os.getenv("APP_HOME_TITLE", "Ma collection"),
            "platforms": platforms,
            "totals": {
                "games_count": computed_totals["games_count"],
                "total_price": computed_totals["total_price"],
                "average_price": computed_totals["average_price"],
            },
            "first_game_date": computed_totals["first_game_date"],
            "last_game_date": computed_totals["last_game_date"],
        }

    def _merge_home_totals(
        self,
        sheet_totals: dict[str, Any],
        computed_totals: dict[str, Any],
    ) -> dict[str, Any]:
        """Complete les totaux Accueil manquants avec les totaux recalcules.

        Args:
            sheet_totals (dict[str, Any]): Totaux lus depuis l'onglet Accueil.
            computed_totals (dict[str, Any]): Totaux recalcules depuis les plateformes.

        Returns:
            dict[str, Any]: Totaux complets pour l'API.
        """

        return {
            "games_count": sheet_totals.get("games_count") or computed_totals["games_count"],
            "total_price": sheet_totals.get("total_price") or computed_totals["total_price"],
            "average_price": sheet_totals.get("average_price") or computed_totals["average_price"],
        }

    def _build_home_totals(self, row: dict[str, Any]) -> dict[str, Any]:
        """Construit les totaux globaux de l'accueil.

        Args:
            row (dict[str, Any]): Ligne issue de l'onglet Accueil.

        Returns:
            dict[str, Any]: Totaux serialises pour JSON.
        """

        return {
            "games_count": SheetValueFormatter.serialize(row.get("Nombre de jeux")),
            "total_price": SheetValueFormatter.serialize(row.get("Prix")),
            "average_price": SheetValueFormatter.serialize(row.get("Prix moyen")),
        }

    def _build_platform_stats(
        self,
        row: dict[str, Any],
        platform_name: str,
        sheet_names_by_key: dict[str, str],
        image_paths_by_sheet: dict[str, str],
    ) -> dict[str, Any]:
        """Construit les statistiques d'une plateforme de l'accueil.

        Args:
            row (dict[str, Any]): Ligne issue de l'onglet Accueil.
            platform_name (str): Nom affiche de la plateforme.
            sheet_names_by_key (dict[str, str]): Onglets indexes par nom normalise.
            image_paths_by_sheet (dict[str, str]): Images embarquees indexees par onglet.

        Returns:
            dict[str, Any]: Statistiques plateforme serialisees pour JSON.
        """

        sheet_name = sheet_names_by_key.get(
            SheetValueFormatter.normalize_platform_name(platform_name),
            platform_name,
        )
        return {
            "name": platform_name,
            "sheet_name": sheet_name,
            "image_url": self._build_platform_image_url(sheet_name),
            "games_count": SheetValueFormatter.serialize(row.get("Nombre de jeux")),
            "total_price": SheetValueFormatter.serialize(row.get("Prix")),
            "average_price": SheetValueFormatter.serialize(row.get("Prix moyen")),
            "has_image": sheet_name in image_paths_by_sheet,
        }

    def _build_platform_image_url(self, sheet_name: str) -> str:
        """Construit l'URL versionnee de l'image d'une plateforme.

        Args:
            sheet_name (str): Nom de l'onglet plateforme.

        Returns:
            str: URL image avec un parametre de cache base sur le fichier ODS.
        """

        return f"/collections/videogames/platform-image/{sheet_name}?v={self._build_image_cache_token()}"

    def _build_image_cache_token(self) -> str:
        """Construit un jeton de cache base sur l'etat du fichier ODS.

        Args:
            Aucun.

        Returns:
            str: Jeton stable tant que le fichier ODS ne change pas.
        """

        try:
            stat_result = os.stat(self.ods_path)
            return f"{stat_result.st_mtime_ns}-{stat_result.st_size}"
        except OSError:
            return "missing"

    def _merge_platform_stats(
        self,
        sheet_stats: dict[str, Any],
        computed_stats: dict[str, Any],
    ) -> dict[str, Any]:
        """Complete les statistiques plateforme manquantes avec un recalcul.

        Args:
            sheet_stats (dict[str, Any]): Statistiques lues depuis l'onglet Accueil.
            computed_stats (dict[str, Any]): Statistiques recalculees depuis l'onglet plateforme.

        Returns:
            dict[str, Any]: Statistiques plateforme completes.
        """

        return {
            **sheet_stats,
            "games_count": sheet_stats["games_count"] or computed_stats["games_count"],
            "total_price": sheet_stats["total_price"] or computed_stats["total_price"],
            "average_price": sheet_stats["average_price"] or computed_stats["average_price"],
            "first_game_date": computed_stats["first_game_date"],
            "last_game_date": computed_stats["last_game_date"],
        }

    def _compute_home_totals(self, platforms: list[dict[str, Any]]) -> dict[str, Any]:
        """Recalcule les totaux globaux depuis les statistiques plateformes.

        Args:
            platforms (list[dict[str, Any]]): Statistiques des plateformes.

        Returns:
            dict[str, Any]: Totaux globaux recalcules.
        """

        games_count = sum(int(platform.get("games_count") or 0) for platform in platforms)
        total_price = sum(float(platform.get("total_price") or 0) for platform in platforms)
        dated_values = [
            value
            for platform in platforms
            for value in [platform.get("first_game_date"), platform.get("last_game_date")]
            if value
        ]
        return {
            "games_count": games_count,
            "total_price": round(total_price, 2),
            "average_price": round(total_price / games_count, 2) if games_count else None,
            "first_game_date": min(dated_values) if dated_values else None,
            "last_game_date": max(dated_values) if dated_values else None,
        }

    def _compute_platform_stats(self, platform: str) -> dict[str, Any]:
        """Recalcule les statistiques d'une plateforme depuis ses lignes de jeux.

        Args:
            platform (str): Nom de l'onglet plateforme.

        Returns:
            dict[str, Any]: Statistiques recalculees pour la plateforme.
        """

        dataframe = self.read_games_dataframe(platform)
        if dataframe.empty or "Nom du jeu" not in dataframe.columns:
            return self._empty_computed_stats()

        games = dataframe[dataframe["Nom du jeu"].notna()]
        games = games[games["Nom du jeu"].astype(str).str.strip() != ""]
        prices = self._numeric_series(games.get("Prix d'achat"))
        release_dates = self._date_series(games.get("Date de sortie"))
        games_count = int(len(games))
        total_price = float(prices.sum()) if not prices.empty else 0
        return {
            "games_count": games_count,
            "total_price": round(total_price, 2),
            "average_price": round(total_price / games_count, 2) if games_count else None,
            "first_game_date": release_dates.min().date().isoformat() if not release_dates.empty else None,
            "last_game_date": release_dates.max().date().isoformat() if not release_dates.empty else None,
        }

    def _empty_computed_stats(self) -> dict[str, Any]:
        """Retourne une structure de statistiques vide.

        Args:
            Aucun.

        Returns:
            dict[str, Any]: Statistiques vides avec valeurs neutres.
        """

        return {
            "games_count": 0,
            "total_price": 0,
            "average_price": None,
            "first_game_date": None,
            "last_game_date": None,
        }

    def _numeric_series(self, series: Optional[pd.Series]) -> pd.Series:
        """Convertit une colonne de valeurs en serie numerique.

        Args:
            series (Optional[pandas.Series]): Colonne brute a convertir.

        Returns:
            pandas.Series: Valeurs numeriques valides.
        """

        if series is None:
            return pd.Series(dtype="float64")
        text_series = series.astype(str).str.replace(",", ".", regex=False)
        return pd.to_numeric(text_series, errors="coerce").dropna()

    def _date_series(self, series: Optional[pd.Series]) -> pd.Series:
        """Convertit une colonne de valeurs en serie de dates.

        Args:
            series (Optional[pandas.Series]): Colonne brute a convertir.

        Returns:
            pandas.Series: Dates valides.
        """

        if series is None:
            return pd.Series(dtype="datetime64[ns]")
        return pd.to_datetime(series, errors="coerce").dropna()

    def _load_column_values(self, platform: str) -> dict[str, list[str]]:
        """Charge les valeurs distinctes de colonnes depuis les jeux caches.

        Args:
            platform (str): Nom de l'onglet ODS a lire.

        Returns:
            dict[str, list[str]]: Valeurs uniques par colonne.
        """

        dataframe = self.read_games_dataframe(platform)
        values_by_column: dict[str, list[str]] = {}
        for column in dataframe.columns:
            unique_values = sorted(
                {
                    str(value).strip()
                    for value in dataframe[column].tolist()
                    if value is not None and str(value).strip() != ""
                }
            )
            values_by_column[str(column)] = unique_values
        return values_by_column

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
