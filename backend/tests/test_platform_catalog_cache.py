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
# Description : tests du cache serveur du catalogue plateformes.

import unittest

from services.database import PlatformCatalogCache, SqlAlchemyPlatformRepository
from services.users import UserCollectionNameNormalizer


class FakeRepositoryCacheConnection:
    """Connexion factice capturant les lectures SQL du catalogue plateformes."""

    def __init__(self):
        """Initialise la connexion factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.executed_statements = []

    def execute(self, statement):
        """Capture une requete SQL et retourne un resultat factice.

        Args:
            statement (object): Requete SQLAlchemy recue.

        Returns:
            FakeRepositoryCacheResult: Resultat compatible avec `mappings`.
        """

        sql = str(statement)
        self.executed_statements.append(sql)
        if 'FROM "collection".t_platform platform' in sql:
            return FakeRepositoryCacheResult([
                {
                    "id": 7,
                    "name": "Switch",
                    "release_date": None,
                    "end_date": None,
                    "manufacturer": "Nintendo",
                    "description": {},
                    "total_games": 1,
                }
            ])
        return FakeRepositoryCacheResult([])


class FakeRepositoryCacheResult:
    """Resultat SQL factice pour les lectures cachees."""

    def __init__(self, rows):
        """Initialise le resultat factice.

        Args:
            rows (list[dict]): Lignes retournees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.rows = rows

    def mappings(self):
        """Retourne les mappings factices.

        Args:
            Aucun.

        Returns:
            list[dict]: Lignes configurees.
        """

        return self.rows


class PlatformCatalogCacheTest(unittest.TestCase):
    """Valide l'expiration et l'isolation du cache plateformes."""

    def test_remember_reuses_value_until_ttl_then_reloads(self):
        """Verifie que le cache expire apres la duree configuree.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les chargements.
        """

        current_time = [100.0]
        load_calls = []
        cache = PlatformCatalogCache(ttl_seconds=10, clock=lambda: current_time[0])

        def load_rows():
            load_calls.append("load")
            return [{"id": len(load_calls), "name": "Switch"}]

        first_rows = cache.remember("cache_test", load_rows)
        first_rows[0]["name"] = "mutated"
        second_rows = cache.remember("cache_test", load_rows)
        current_time[0] = 111.0
        third_rows = cache.remember("cache_test", load_rows)

        self.assertEqual(2, len(load_calls))
        self.assertEqual("Switch", second_rows[0]["name"])
        self.assertEqual(1, second_rows[0]["id"])
        self.assertEqual(2, third_rows[0]["id"])

    def test_invalidate_removes_cached_schema(self):
        """Verifie l'invalidation explicite d'un schema.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'invalidation.
        """

        cache = PlatformCatalogCache(ttl_seconds=10)
        cache.remember("cache_test_invalidate", lambda: [{"id": 1, "name": "Switch"}])

        self.assertEqual(1, cache.invalidate("cache_test_invalidate"))
        self.assertEqual(0, cache.invalidate("cache_test_invalidate"))

    def test_platform_repository_reuses_catalog_cache_without_repeated_sql(self):
        """Verifie l'absence de requetes SQL repetees avant expiration.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les lectures SQL.
        """

        connection = FakeRepositoryCacheConnection()
        repository = SqlAlchemyPlatformRepository(
            "collection",
            UserCollectionNameNormalizer(),
            platform_catalog_cache=PlatformCatalogCache(ttl_seconds=300),
        )

        first_rows = repository.load_catalog_rows(connection)
        second_rows = repository.load_catalog_rows(connection)
        platform_selects = [
            sql
            for sql in connection.executed_statements
            if 'FROM "collection".t_platform platform' in sql
        ]

        self.assertEqual(1, len(platform_selects))
        self.assertEqual(first_rows, second_rows)


if __name__ == "__main__":
    unittest.main()
