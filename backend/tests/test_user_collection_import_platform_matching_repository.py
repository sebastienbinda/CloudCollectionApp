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
# Description : tests du rattachement plateformes dans le repository d'import.

from types import SimpleNamespace
import unittest

from services.collection.imports import CollectionImportData, CollectionImportPlatform
from services.database.user_collection_import_repository import (
    SqlAlchemyUserCollectionImportRepository,
)
from services.users import UserCollectionNameNormalizer


class UserCollectionImportPlatformMatchingRepositoryTest(unittest.TestCase):
    """Valide que l'import ne cree plus de plateformes utilisateur."""

    def test_ensure_platforms_reuses_catalog_ids_without_insert(self):
        """Verifie l'absence d'insertion plateforme pendant l'import.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les identifiants retournes.
        """

        insert_calls = []
        repository = object.__new__(SqlAlchemyUserCollectionImportRepository)
        repository.name_normalizer = UserCollectionNameNormalizer()
        repository.platform_repository = SimpleNamespace(
            load_ids_by_key=lambda connection: {"switch": 7, "nes": 8},
            insert=lambda connection, name: insert_calls.append(name),
        )

        platform_ids, linked_platforms = repository._ensure_platforms(
            object(),
            CollectionImportData(
                [CollectionImportPlatform("Switch")],
                [],
                [
                    SimpleNamespace(platform_name="Switch"),
                    SimpleNamespace(platform_name="Switch"),
                    SimpleNamespace(platform_name="NES"),
                    SimpleNamespace(platform_name="Unknown"),
                ],
            ),
        )

        self.assertEqual({"switch": 7, "nes": 8}, platform_ids)
        self.assertEqual(2, linked_platforms)
        self.assertEqual([], insert_calls)


if __name__ == "__main__":
    unittest.main()
