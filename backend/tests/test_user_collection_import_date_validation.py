#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-10
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de validation des dates avant persistance d'un import.

import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from tests.test_user_collection_import_service import (
        FakeOdsCollectionImportReader,
        UserCollectionImportServiceTest,
    )
except ModuleNotFoundError:
    from test_user_collection_import_service import (
        FakeOdsCollectionImportReader,
        UserCollectionImportServiceTest,
    )

from services.collection.imports import (
    CollectionImportData,
    CollectionImportGame,
    CollectionImportPlatform,
    CollectionImportStudio,
)


class UserCollectionImportDateValidationTest(unittest.TestCase):
    """Valide la normalisation des dates d'import au niveau service."""

    def test_import_collection_replaces_unpersistable_release_date_with_none(self):
        """Verifie qu'une date hors plage lue par un reader n'atteint pas SQL.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les donnees envoyees au repository.
        """

        helper = UserCollectionImportServiceTest()
        import_data = CollectionImportData(
            platforms=[CollectionImportPlatform("Switch")],
            studios=[CollectionImportStudio("Nintendo")],
            games=[
                CollectionImportGame(
                    name="Zelda",
                    platform_name="Switch",
                    studio_name="Nintendo",
                    release_date="48113-11-21 00:00:01",
                )
            ],
        )
        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = helper._build_service(
                directory,
                reader=FakeOdsCollectionImportReader(import_data=import_data),
            )

            service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                helper._valid_description(),
            )

            persisted_data = repository.import_calls[0][2]
            self.assertIsNone(persisted_data.games[0].release_date)
            self.assertEqual(import_data, reader.import_data)

    def test_import_collection_keeps_valid_release_dates(self):
        """Verifie que les dates valides restent persistables.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la conservation des dates valides.
        """

        helper = UserCollectionImportServiceTest()
        import_data = CollectionImportData(
            platforms=[CollectionImportPlatform("Switch")],
            studios=[CollectionImportStudio("Nintendo")],
            games=[
                CollectionImportGame(
                    name="Zelda",
                    platform_name="Switch",
                    studio_name="Nintendo",
                    release_date=datetime(1986, 2, 21, 12, 30),
                ),
                CollectionImportGame(
                    name="Metroid",
                    platform_name="Switch",
                    studio_name="Nintendo",
                    release_date=date(1987, 8, 6),
                ),
            ],
        )
        with tempfile.TemporaryDirectory() as directory:
            service, repository, _reader, source_file = helper._build_service(
                directory,
                reader=FakeOdsCollectionImportReader(import_data=import_data),
            )

            service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                helper._valid_description(),
            )

            persisted_data = repository.import_calls[0][2]
            self.assertEqual(date(1986, 2, 21), persisted_data.games[0].release_date)
            self.assertEqual(date(1987, 8, 6), persisted_data.games[1].release_date)

    def test_import_collection_parses_valid_release_date_string(self):
        """Verifie qu'une date texte valide devient une date persistable.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le parsing de la date texte.
        """

        helper = UserCollectionImportServiceTest()
        import_data = CollectionImportData(
            platforms=[CollectionImportPlatform("Switch")],
            studios=[CollectionImportStudio("Nintendo")],
            games=[
                CollectionImportGame(
                    name="Zelda",
                    platform_name="Switch",
                    studio_name="Nintendo",
                    release_date="1986-02-21 00:00:00",
                )
            ],
        )
        with tempfile.TemporaryDirectory() as directory:
            service, repository, _reader, source_file = helper._build_service(
                directory,
                reader=FakeOdsCollectionImportReader(import_data=import_data),
            )

            service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                helper._valid_description(),
            )

            persisted_data = repository.import_calls[0][2]
            self.assertEqual(date(1986, 2, 21), persisted_data.games[0].release_date)

    def test_import_collection_replaces_too_old_release_date_with_none(self):
        """Verifie qu'une date de sortie anterieure aux jeux video est ignoree.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la neutralisation de la date.
        """

        helper = UserCollectionImportServiceTest()
        import_data = CollectionImportData(
            platforms=[CollectionImportPlatform("Switch")],
            studios=[CollectionImportStudio("Nintendo")],
            games=[
                CollectionImportGame(
                    name="Penny Blood",
                    platform_name="Switch",
                    studio_name="Nintendo",
                    release_date="0200-11-24",
                )
            ],
        )
        with tempfile.TemporaryDirectory() as directory:
            service, repository, _reader, source_file = helper._build_service(
                directory,
                reader=FakeOdsCollectionImportReader(import_data=import_data),
            )

            service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                helper._valid_description(),
            )

            persisted_data = repository.import_calls[0][2]
            self.assertIsNone(persisted_data.games[0].release_date)


if __name__ == "__main__":
    unittest.main()
