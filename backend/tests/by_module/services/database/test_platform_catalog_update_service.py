#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-16
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du service d'actualisation du catalogue plateformes.

from pathlib import Path
import unittest

from services.database import (
    DatabaseConfiguration,
    PlatformCatalogSeedResult,
    PlatformCatalogUpdateService,
)


class FakeTransaction:
    """Transaction factice indiquant si le commit est termine."""

    def __init__(self, engine):
        """Initialise la transaction factice.

        Args:
            engine (FakeEngine): Moteur dont l'etat de commit est mis a jour.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.engine = engine

    def __enter__(self):
        """Entre dans la transaction factice.

        Args:
            Aucun.

        Returns:
            object: Connexion factice.
        """

        return object()

    def __exit__(self, exc_type, exc_value, traceback):
        """Marque la transaction comme terminee.

        Args:
            exc_type (type | None): Type d'exception eventuelle.
            exc_value (BaseException | None): Exception eventuelle.
            traceback (object | None): Traceback eventuel.

        Returns:
            bool: `False` pour ne pas masquer les exceptions.
        """

        self.engine.transaction_closed = True
        return False


class FakeEngine:
    """Moteur factice exposant un contexte transactionnel."""

    def __init__(self):
        """Initialise le moteur factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.transaction_closed = False

    def begin(self):
        """Ouvre une transaction factice.

        Args:
            Aucun.

        Returns:
            FakeTransaction: Transaction factice.
        """

        return FakeTransaction(self)


class FakeSeedService:
    """Seed factice du catalogue plateformes."""

    def seed_from_csv_detailed(self, connection, csv_path, alias_csv_path):
        """Retourne un resultat de seed factice.

        Args:
            connection (object): Connexion ignoree.
            csv_path (Path): Chemin du CSV plateformes.
            alias_csv_path (Path): Chemin du CSV alias.

        Returns:
            PlatformCatalogSeedResult: Resultat factice.
        """

        self.csv_path = csv_path
        self.alias_csv_path = alias_csv_path
        return PlatformCatalogSeedResult(inserted_platforms=1, inserted_aliases=2)


class FakePlatformCatalogCache:
    """Cache factice capturant l'invalidation du catalogue plateformes."""

    def __init__(self, engine):
        """Initialise le cache factice.

        Args:
            engine (FakeEngine): Moteur observe pour verifier l'ordre.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.engine = engine
        self.invalidated_schema_name = None
        self.invalidated_after_transaction = False

    def invalidate(self, schema_name):
        """Capture l'invalidation.

        Args:
            schema_name (str): Schema invalide.

        Returns:
            int: Nombre d'entrees invalidees.
        """

        self.invalidated_schema_name = schema_name
        self.invalidated_after_transaction = self.engine.transaction_closed
        return 1


class PlatformCatalogUpdateServiceTest(unittest.TestCase):
    """Valide l'actualisation admin du catalogue plateformes."""

    def test_update_from_resources_invalidates_cache_after_transaction(self):
        """Verifie que le cache est invalide apres commit.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'ordre d'invalidation.
        """

        engine = FakeEngine()
        seed_service = FakeSeedService()
        platform_catalog_cache = FakePlatformCatalogCache(engine)
        configuration = DatabaseConfiguration(
            database_url="postgresql://example",
            schema_name="collection",
            application_version="0.1",
        )
        service = PlatformCatalogUpdateService(
            configuration,
            seed_service=seed_service,
            platform_catalog_cache=platform_catalog_cache,
            resources_directory=Path("/tmp/resources"),
            engine_factory=lambda database_url: engine,
        )

        result = service.update_from_resources()

        self.assertEqual(PlatformCatalogSeedResult(1, 2), result)
        self.assertEqual("platform_catalog.csv", seed_service.csv_path.name)
        self.assertEqual("platform_alias_catalog.csv", seed_service.alias_csv_path.name)
        self.assertEqual("collection", platform_catalog_cache.invalidated_schema_name)
        self.assertTrue(platform_catalog_cache.invalidated_after_transaction)


if __name__ == "__main__":
    unittest.main()
