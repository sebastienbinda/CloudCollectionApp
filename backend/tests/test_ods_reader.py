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
import unittest
from unittest.mock import patch

import pandas as pd

from services.ods import OdsCache, OdsReader, OdsXmlReader


class FakeImageReader:
    def list_platform_image_paths(self):
        """Retourne les chemins d'images factices des plateformes.

        Args:
            Aucun.

        Returns:
            dict[str, str]: Images factices indexees par nom d'onglet.
        """

        return {"Switch": "Pictures/switch.png", "Playstation": "Pictures/ps.png"}


class OdsReaderFallbackTest(unittest.TestCase):
    def setUp(self):
        """Prepare un lecteur ODS avec dependances factices.

        Args:
            Aucun.

        Returns:
            None: L'instance de test est initialisee.
        """

        self.reader = OdsReader(
            ods_path="/tmp/fallback-home.ods",
            cache=OdsCache("/tmp/fallback-home.ods"),
            xml_reader=None,
            image_reader=FakeImageReader(),
        )
        self.reader.cache.reset()
        self.reader.list_platforms = lambda: ["Switch", "Playstation"]
        self.reader.read_games_dataframe = self._read_games_dataframe

    def test_home_stats_fallback_recomputes_error_values(self):
        """Verifie le fallback lorsque l'onglet Accueil retourne des erreurs.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les statistiques recalculees.
        """

        with patch.dict("services.ods.ods_reader.os.environ", {}, clear=True):
            with patch("services.ods.ods_reader.pd.read_excel", return_value=self._home_dataframe()):
                stats = self.reader.get_home_stats()

        self.assertEqual(3, stats["totals"]["games_count"])
        self.assertEqual("Ma collection", stats["title"])
        self.assertEqual(60.5, stats["totals"]["total_price"])
        self.assertEqual(20.17, stats["totals"]["average_price"])
        self.assertEqual("2019-03-01", stats["first_game_date"])
        self.assertEqual("2021-06-15", stats["last_game_date"])
        self.assertEqual(2, stats["platforms"][0]["games_count"])
        self.assertEqual(30.5, stats["platforms"][0]["total_price"])
        self.assertEqual(15.25, stats["platforms"][0]["average_price"])

    def test_home_stats_keeps_valid_sheet_values(self):
        """Verifie que le fallback ne remplace pas les valeurs Accueil valides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la priorite des valeurs de l'onglet Accueil.
        """

        dataframe = self._home_dataframe()
        dataframe = dataframe.astype(
            {"Nombre de jeux": "object", "Prix": "object", "Prix moyen": "object"}
        )
        dataframe.loc[dataframe["Plateforme"] == "Switch", "Nombre de jeux"] = 99
        dataframe.loc[dataframe["Plateforme"] == "Switch", "Prix"] = 1234
        dataframe.loc[dataframe["Plateforme"] == "Switch", "Prix moyen"] = 12.46

        with patch("services.ods.ods_reader.pd.read_excel", return_value=dataframe):
            stats = self.reader.get_home_stats()

        switch_stats = stats["platforms"][0]
        self.assertEqual(99, switch_stats["games_count"])
        self.assertEqual(1234, switch_stats["total_price"])
        self.assertEqual(12.46, switch_stats["average_price"])

    def test_home_stats_versions_platform_image_urls(self):
        """Verifie que les URLs d'images changent avec le fichier ODS.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la presence du jeton de cache.
        """

        with patch("services.ods.ods_reader.os.stat") as stat_mock:
            stat_mock.return_value.st_mtime_ns = 123456
            stat_mock.return_value.st_size = 789
            with patch("services.ods.ods_reader.pd.read_excel", return_value=self._home_dataframe()):
                stats = self.reader.get_home_stats()

        image_url = stats["platforms"][0]["image_url"]
        self.assertEqual("/collections/videogames/platform-image/Switch?v=123456-789", image_url)

    def test_home_title_can_be_configured_from_environment(self):
        """Verifie la configuration du titre d'accueil.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le titre configure.
        """

        self.reader.cache.reset()
        with patch("services.ods.ods_reader.pd.read_excel", return_value=self._home_dataframe()):
            with patch.dict("services.ods.ods_reader.os.environ", {"APP_HOME_TITLE": "Mes RPG"}):
                stats = self.reader.get_home_stats()

        self.assertEqual("Mes RPG", stats["title"])

    def test_home_stats_fallback_when_pandas_cannot_read_formulas(self):
        """Verifie le fallback si pandas echoue sur des formules sans cache.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'accueil recalcule.
        """

        self.reader.cache.reset()
        with patch.dict("services.ods.ods_reader.os.environ", {}, clear=True):
            with patch("services.ods.ods_reader.pd.read_excel", side_effect=TypeError("formula cache")):
                stats = self.reader.get_home_stats()

        self.assertEqual(3, stats["totals"]["games_count"])
        self.assertEqual(60.5, stats["totals"]["total_price"])

    def test_xml_reader_returns_none_for_formula_float_without_cached_value(self):
        """Verifie la lecture d'une formule sans resultat calcule en cache.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence de crash et la valeur vide.
        """

        value_type_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value-type"
        value_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value"
        date_value_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}date-value"
        cell = self._cell_with_attribute(value_type_attribute, "float")

        xml_reader = OdsXmlReader.__new__(OdsXmlReader)
        value = xml_reader.extract_cell_value(
            cell,
            value_type_attribute,
            value_attribute,
            date_value_attribute,
        )

        self.assertIsNone(value)

    def _home_dataframe(self):
        """Construit un DataFrame Accueil avec erreurs de formules.

        Args:
            Aucun.

        Returns:
            pandas.DataFrame: Donnees factices de l'onglet Accueil.
        """

        return pd.DataFrame(
            [
                {
                    "Plateforme": "Switch",
                    "Nombre de jeux": "Err:510",
                    "Prix": "Err:510",
                    "Prix moyen": "Err:510",
                },
                {
                    "Plateforme": "Playstation",
                    "Nombre de jeux": "Err:510",
                    "Prix": "Err:510",
                    "Prix moyen": "Err:510",
                },
                {
                    "Plateforme": "Total",
                    "Nombre de jeux": "Err:510",
                    "Prix": "Err:510",
                    "Prix moyen": "Err:510",
                },
                {"Plateforme": "Date du premier jeu", "Prix": "Err:510"},
                {"Plateforme": "Date du dernier jeu", "Prix": "Err:510"},
            ]
        )

    def _read_games_dataframe(self, platform):
        """Retourne les jeux factices d'une plateforme.

        Args:
            platform (str): Nom de l'onglet plateforme.

        Returns:
            pandas.DataFrame: Jeux factices de la plateforme.
        """

        games_by_platform = {
            "Switch": pd.DataFrame(
                [
                    {
                        "Nom du jeu": "Zelda",
                        "Prix d'achat": "10,50",
                        "Date de sortie": "2020-01-01",
                    },
                    {
                        "Nom du jeu": "Mario",
                        "Prix d'achat": 20,
                        "Date de sortie": "2021-06-15",
                    },
                ]
            ),
            "Playstation": pd.DataFrame(
                [
                    {
                        "Nom du jeu": "Gran Turismo",
                        "Prix d'achat": 30,
                        "Date de sortie": "2019-03-01",
                    }
                ]
            ),
        }
        return games_by_platform[platform]

    def _cell_with_attribute(self, attribute, value):
        """Construit une cellule XML avec un attribut.

        Args:
            attribute (str): Nom qualifie de l'attribut XML.
            value (str): Valeur d'attribut.

        Returns:
            xml.etree.ElementTree.Element: Cellule XML factice.
        """

        import xml.etree.ElementTree as ET

        return ET.Element(
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell",
            {attribute: value},
        )


if __name__ == "__main__":
    unittest.main()
