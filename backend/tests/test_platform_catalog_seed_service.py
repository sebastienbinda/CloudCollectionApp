#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du seed du catalogue plateformes.

from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import unittest

from services.database import (
    PlatformAliasCatalogEntry,
    PlatformCatalogEntry,
    PlatformCatalogSeedService,
)
from tests.fake_platform_catalog_connection import FakePlatformCatalogConnection
from tests.static_platform_catalog_reader import StaticPlatformCatalogReader


class PlatformCatalogSeedServiceTest(unittest.TestCase):
    """Valide le seed idempotent du catalogue plateformes."""

    def test_seed_inserts_missing_platforms_only(self):
        """Verifie que le seed ignore les plateformes deja presentes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les insertions.
        """

        entries = [
            PlatformCatalogEntry("Atari 7800", "Atari", None, None, {}),
            PlatformCatalogEntry("Atari 7800+", "Atari", None, None, {}),
            PlatformCatalogEntry("Switch", "Nintendo", datetime(2017, 3, 3), None, {}),
        ]
        connection = FakePlatformCatalogConnection(existing_rows=[{"name": "Switch"}])
        service = PlatformCatalogSeedService(
            "collection",
            csv_reader=StaticPlatformCatalogReader(entries),
        )

        inserted_count = service.seed_from_csv(connection, Path("unused.csv"))

        insert_parameters = [
            parameters
            for statement, parameters in connection.executed_statements
            if statement.startswith("INSERT INTO")
        ]
        self.assertEqual(2, inserted_count)
        self.assertEqual(
            ["Atari 7800", "Atari 7800+"],
            [parameters["name"] for parameters in insert_parameters],
        )

    def test_catalog_key_keeps_plus_suffix_distinct(self):
        """Verifie que la cle de seed ne fusionne pas les suffixes `+`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la distinction.
        """

        service = PlatformCatalogSeedService("collection")

        self.assertNotEqual(
            service.catalog_key("Atari 7800"),
            service.catalog_key("Atari 7800+"),
        )

    def test_seed_inserts_missing_aliases_only(self):
        """Verifie que le seed alias rattache les noms alternatifs au catalogue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les insertions.
        """

        aliases = [
            PlatformAliasCatalogEntry(
                "Super Nintendo Entertainment System / Super Famicom",
                "Super Nintendo",
                "nom_court",
                "France",
                "Nom courant.",
            ),
            PlatformAliasCatalogEntry(
                "Super Nintendo Entertainment System / Super Famicom",
                "SNES",
                "abreviation",
                "Occident",
                "Abreviation.",
            ),
        ]
        connection = FakePlatformCatalogConnection(
            existing_rows=[
                {
                    "id": 7,
                    "name": "Super Nintendo Entertainment System / Super Famicom",
                    "platform": 7,
                },
                {"id": 7, "platform": 7, "name": "SNES"},
            ]
        )
        service = PlatformCatalogSeedService(
            "collection",
            csv_reader=StaticPlatformCatalogReader([]),
            alias_csv_reader=SimpleNamespace(read=lambda path: aliases),
        )

        inserted_count = service.seed_from_csv(
            connection,
            Path("unused.csv"),
            Path("unused_alias.csv"),
        )

        alias_insert_parameters = [
            parameters
            for statement, parameters in connection.executed_statements
            if "t_platform_alias" in statement and statement.startswith("INSERT INTO")
        ]
        self.assertEqual(1, inserted_count)
        self.assertEqual("Super Nintendo", alias_insert_parameters[0]["name"])
        self.assertEqual(7, alias_insert_parameters[0]["platform"])


if __name__ == "__main__":
    unittest.main()
