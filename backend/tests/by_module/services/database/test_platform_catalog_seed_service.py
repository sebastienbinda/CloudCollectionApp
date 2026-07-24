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
    PlatformCatalogSeedResult,
    PlatformCatalogSeedService,
)
from tests.support.fake_platform_catalog_connection import FakePlatformCatalogConnection
from tests.support.static_platform_catalog_reader import StaticPlatformCatalogReader


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
                "Super Nintendo",
                "Super Famicom",
                "nom_alternatif",
                "Japon",
                "Nom japonais.",
            ),
            PlatformAliasCatalogEntry(
                "Super Nintendo",
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
                    "name": "Super Nintendo",
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
        self.assertEqual("Super Famicom", alias_insert_parameters[0]["name"])
        self.assertEqual(7, alias_insert_parameters[0]["platform"])

    def test_seed_from_csv_detailed_returns_serializable_counts(self):
        """Verifie les compteurs detailles serialisables du seed catalogue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les compteurs separes.
        """

        entries = [
            PlatformCatalogEntry("Atari 7800+", "Atari", None, None, {}),
        ]
        connection = FakePlatformCatalogConnection()
        service = PlatformCatalogSeedService(
            "collection",
            csv_reader=StaticPlatformCatalogReader(entries),
        )

        result = service.seed_from_csv_detailed(
            connection,
            Path("unused.csv"),
        )

        self.assertEqual(PlatformCatalogSeedResult(1, 0), result)
        self.assertEqual(
            {
                "inserted_platforms": 1,
                "inserted_aliases": 0,
                "total_inserted": 1,
            },
            result.to_dict(),
        )


if __name__ == "__main__":
    unittest.main()
