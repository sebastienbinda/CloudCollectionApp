#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du lecteur d'import de collection ODS.

import logging
import sys
import unittest
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.ods import (
    OdsCollectionImportReadError,
    OdsCollectionImportReader,
    OdsCollectionImportValidationError,
)


class FakeOdsReader:
    """Simule le lecteur ODS bas niveau pour les tests d'import."""

    def __init__(self, platform_names, dataframes_by_platform=None, error=None):
        """Initialise le lecteur ODS factice.

        Args:
            platform_names (list[str]): Onglets plateformes retournes.
            dataframes_by_platform (dict[str, pandas.DataFrame] | None): Donnees par onglet.
            error (Exception | None): Erreur a lever lors de la lecture des onglets.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.platform_names = platform_names
        self.dataframes_by_platform = dataframes_by_platform or {}
        self.error = error
        self.cache = FakeOdsCache()

    def list_platforms(self):
        """Retourne les onglets plateformes factices.

        Args:
            Aucun.

        Returns:
            list[str]: Noms d'onglets plateformes.

        Raises:
            Exception: Si le lecteur est configure avec une erreur.
        """

        if self.error:
            raise self.error
        return self.platform_names

    def read_games_dataframe(self, platform):
        """Retourne les jeux factices d'une plateforme.

        Args:
            platform (str): Nom de l'onglet plateforme.

        Returns:
            pandas.DataFrame: Jeux de la plateforme.
        """

        return self.dataframes_by_platform[platform]


class FakeOdsCache:
    """Simule le cache ODS partage par le lecteur bas niveau."""

    def __init__(self):
        """Initialise le cache factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.reset_count = 0

    def reset(self):
        """Memorise un vidage de cache.

        Args:
            Aucun.

        Returns:
            int: Nombre factice d'entrees supprimees.
        """

        self.reset_count += 1
        return 1


class OdsCollectionImportReaderTest(unittest.TestCase):
    """Valide la lecture ODS dediee a l'import de collection utilisateur."""

    def test_read_returns_business_structure_for_valid_file(self):
        """Verifie la structure metier retournee pour un fichier valide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident plateformes, studios et jeux.
        """

        fake_reader = FakeOdsReader(
            ["Switch", "PC"],
            {
                "Switch": self._dataframe(
                    [
                        {
                            "Nom du jeu": " Zelda ",
                            "Studio": " Nintendo ",
                            "Date de sortie": "2017-03-03",
                        },
                        {
                            "Nom du jeu": "Mario",
                            "Studio": "Retro",
                            "Date de sortie": date(2023, 10, 20),
                        },
                    ]
                ),
                "PC": self._dataframe(
                    [
                        {
                            "Nom du jeu": "Baldur's Gate 3",
                            "Studio": "Larian",
                            "Date de sortie": "2023-08-03",
                        }
                    ]
                ),
            },
        )
        service = self._service_for_reader(fake_reader)

        import_data = service.read("/tmp/collection.ods")

        self.assertEqual(1, fake_reader.cache.reset_count)
        self.assertEqual(["Switch", "PC"], [platform.name for platform in import_data.platforms])
        self.assertEqual(
            ["Nintendo", "Retro", "Larian"],
            [studio.name for studio in import_data.studios],
        )
        self.assertEqual(3, len(import_data.games))
        self.assertEqual("Zelda", import_data.games[0].name)
        self.assertEqual("Switch", import_data.games[0].platform_name)
        self.assertEqual("Nintendo", import_data.games[0].studio_name)
        self.assertEqual(date(2017, 3, 3), import_data.games[0].release_date)

    def test_read_rejects_unreadable_file(self):
        """Verifie le refus d'un fichier ODS illisible.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de lecture.
        """

        service = self._service_for_reader(FakeOdsReader([], error=OSError("boom")))

        with self.assertRaises(OdsCollectionImportReadError):
            service.read("/tmp/broken.ods")

    def test_read_rejects_file_without_importable_platform_sheet(self):
        """Verifie le refus d'un fichier sans onglet plateforme.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de validation.
        """

        service = self._service_for_reader(FakeOdsReader([]))

        with self.assertRaises(OdsCollectionImportValidationError) as context:
            service.read("/tmp/empty.ods")

        self.assertIn("aucun onglet plateforme", str(context.exception))

    def test_read_rejects_platform_sheet_with_missing_columns(self):
        """Verifie le refus d'une feuille plateforme sans colonnes attendues.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de validation.
        """

        service = self._service_for_reader(
            FakeOdsReader(
                ["Switch"],
                {
                    "Switch": pd.DataFrame(
                        [{"Nom du jeu": "Zelda", "Date de sortie": "2017-03-03"}]
                    )
                },
            )
        )

        with self.assertRaises(OdsCollectionImportValidationError) as context:
            service.read("/tmp/missing-column.ods")

        self.assertIn("Studio", str(context.exception))

    def test_read_keeps_empty_release_date_as_none(self):
        """Verifie qu'une date de sortie vide devient `None`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la date nulle.
        """

        service = self._service_for_reader(
            FakeOdsReader(
                ["Switch"],
                {
                    "Switch": self._dataframe(
                        [{"Nom du jeu": "Zelda", "Studio": "Nintendo", "Date de sortie": ""}]
                    )
                },
            )
        )

        import_data = service.read("/tmp/empty-date.ods")

        self.assertIsNone(import_data.games[0].release_date)

    def test_read_warns_and_keeps_invalid_release_date_as_none(self):
        """Verifie qu'une date de sortie invalide devient `None` avec warning.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'avertissement et la date nulle.
        """

        logger = logging.getLogger("tests.ods_import_reader")
        service = self._service_for_reader(
            FakeOdsReader(
                ["Switch"],
                {
                    "Switch": self._dataframe(
                        [
                            {
                                "Nom du jeu": "Zelda",
                                "Studio": "Nintendo",
                                "Date de sortie": "pas-une-date",
                            }
                        ]
                    )
                },
            ),
            logger=logger,
        )

        with self.assertLogs(logger, level="WARNING") as logs:
            import_data = service.read("/tmp/invalid-date.ods")

        self.assertIsNone(import_data.games[0].release_date)
        self.assertIn("Date de sortie invalide", logs.output[0])

    def test_read_warns_and_keeps_out_of_range_release_date_as_none(self):
        """Verifie qu'une date hors plage PostgreSQL/Python devient `None`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'avertissement et la date nulle.
        """

        logger = logging.getLogger("tests.ods_import_reader.out_of_range_date")
        service = self._service_for_reader(
            FakeOdsReader(
                ["Switch"],
                {
                    "Switch": self._dataframe(
                        [
                            {
                                "Nom du jeu": "Zelda",
                                "Studio": "Nintendo",
                                "Date de sortie": "48113-11-21 00:00:01",
                            }
                        ]
                    )
                },
            ),
            logger=logger,
        )

        with self.assertLogs(logger, level="WARNING") as logs:
            import_data = service.read("/tmp/out-of-range-date.ods")

        self.assertIsNone(import_data.games[0].release_date)
        self.assertIn("Date de sortie invalide", logs.output[0])

    def test_read_ignores_duplicate_platforms_with_warning(self):
        """Verifie la deduplication des plateformes du fichier.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la premiere occurrence conservee.
        """

        logger = logging.getLogger("tests.ods_import_reader.platform_duplicates")
        fake_reader = FakeOdsReader(
            ["Switch", " switch ", "PC"],
            {
                "Switch": self._dataframe(
                    [{"Nom du jeu": "Zelda", "Studio": "Nintendo", "Date de sortie": ""}]
                ),
                "PC": self._dataframe(
                    [{"Nom du jeu": "Doom", "Studio": "id Software", "Date de sortie": ""}]
                ),
            },
        )
        service = self._service_for_reader(fake_reader, logger=logger)

        with self.assertLogs(logger, level="WARNING") as logs:
            import_data = service.read("/tmp/platform-duplicates.ods")

        self.assertEqual(["Switch", "PC"], [platform.name for platform in import_data.platforms])
        self.assertEqual(["Zelda", "Doom"], [game.name for game in import_data.games])
        self.assertIn("Plateforme dupliquee ignoree", logs.output[0])

    def test_read_ignores_duplicate_studios_with_warning(self):
        """Verifie la deduplication des studios du fichier.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les studios uniques.
        """

        logger = logging.getLogger("tests.ods_import_reader.studio_duplicates")
        service = self._service_for_reader(
            FakeOdsReader(
                ["Switch"],
                {
                    "Switch": self._dataframe(
                        [
                            {"Nom du jeu": "Zelda", "Studio": "École", "Date de sortie": ""},
                            {"Nom du jeu": "Mario", "Studio": "ecole", "Date de sortie": ""},
                        ]
                    )
                },
            ),
            logger=logger,
        )

        with self.assertLogs(logger, level="WARNING") as logs:
            import_data = service.read("/tmp/studio-duplicates.ods")

        self.assertEqual(["École"], [studio.name for studio in import_data.studios])
        self.assertEqual(["Zelda", "Mario"], [game.name for game in import_data.games])
        self.assertIn("Studio duplique ignore", logs.output[0])

    def test_read_ignores_duplicate_games_with_warning(self):
        """Verifie la deduplication des jeux du fichier.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le premier jeu conserve.
        """

        logger = logging.getLogger("tests.ods_import_reader.game_duplicates")
        service = self._service_for_reader(
            FakeOdsReader(
                ["Switch"],
                {
                    "Switch": self._dataframe(
                        [
                            {"Nom du jeu": "École", "Studio": "Studio A", "Date de sortie": ""},
                            {"Nom du jeu": " ecole ", "Studio": "Studio B", "Date de sortie": ""},
                        ]
                    )
                },
            ),
            logger=logger,
        )

        with self.assertLogs(logger, level="WARNING") as logs:
            import_data = service.read("/tmp/game-duplicates.ods")

        self.assertEqual(["École"], [game.name for game in import_data.games])
        self.assertEqual(["Studio A"], [studio.name for studio in import_data.studios])
        self.assertIn("Jeu duplique ignore", logs.output[0])

    def _service_for_reader(self, fake_reader, logger=None):
        """Construit le service d'import avec un lecteur factice.

        Args:
            fake_reader (FakeOdsReader): Lecteur ODS factice a utiliser.
            logger (logging.Logger | None): Logger optionnel du service.

        Returns:
            OdsCollectionImportReader: Service configure pour le test.
        """

        return OdsCollectionImportReader(
            reader_factory=lambda ods_path: fake_reader,
            logger=logger,
        )

    def _dataframe(self, rows):
        """Construit un DataFrame de jeux avec les colonnes attendues.

        Args:
            rows (list[dict]): Lignes de jeux factices.

        Returns:
            pandas.DataFrame: Donnees de jeux factices.
        """

        return pd.DataFrame(rows, columns=["Nom du jeu", "Studio", "Date de sortie"])


if __name__ == "__main__":
    unittest.main()
