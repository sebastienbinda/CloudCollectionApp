#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-24
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du service metier Bibliotheque.

from datetime import datetime
import unittest

from services.database import DatabaseConfiguration
from services.library import LibraryQueryParser
from services.library.library_service import LibraryService
from services.library.library_service_provider import LibraryServiceProvider


class FakeConnectionContext:
    """Contexte de connexion factice."""

    def __init__(self, connection):
        """Initialise le contexte de connexion.

        Args:
            connection (object): Connexion retournee par le contexte.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection

    def __enter__(self):
        """Entre dans le contexte.

        Args:
            Aucun.

        Returns:
            object: Connexion configuree.
        """

        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        """Sort du contexte.

        Args:
            exc_type (type | None): Type d'exception eventuelle.
            exc_value (BaseException | None): Exception eventuelle.
            traceback (object | None): Traceback eventuel.

        Returns:
            bool: `False` pour ne pas masquer les exceptions.
        """

        return False


class FakeEngine:
    """Moteur SQLAlchemy factice."""

    def __init__(self):
        """Initialise le moteur factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = object()
        self.connect_count = 0

    def connect(self):
        """Ouvre une connexion factice.

        Args:
            Aucun.

        Returns:
            FakeConnectionContext: Contexte de connexion.
        """

        self.connect_count += 1
        return FakeConnectionContext(self.connection)


class FakePlatformRepository:
    """Repository plateformes factice pour la Bibliotheque."""

    def __init__(self):
        """Initialise le repository factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.calls = []

    def count_public_library_platforms(self, connection):
        """Compte les plateformes factices.

        Args:
            connection (object): Connexion recue.

        Returns:
            int: Nombre de plateformes.
        """

        self.calls.append(("count_all", connection))
        return 2

    def count_public_library_platforms_by_criteria(self, connection, criteria):
        """Compte les plateformes filtrees factices.

        Args:
            connection (object): Connexion recue.
            criteria (LibraryQueryCriteria): Criteres recus.

        Returns:
            int: Nombre de plateformes filtrees.
        """

        self.calls.append(("count_filtered", connection, criteria))
        return 6

    def list_public_library_platforms(self, connection, criteria):
        """Liste les plateformes factices.

        Args:
            connection (object): Connexion recue.
            criteria (LibraryQueryCriteria): Criteres recus.

        Returns:
            list[dict]: Plateformes factices.
        """

        self.calls.append(("list", connection, criteria))
        return [
            {
                "id": 1,
                "name": "Switch",
                "release_date": datetime(2017, 3, 3, 9, 30),
                "manufacturer": None,
                "description": {"screen": "portable"},
                "status": "ACTIVE",
                "total_games": 12,
            }
        ]


class FakeStudioRepository:
    """Repository studios factice pour la Bibliotheque."""

    def count_public_library_studios(self, connection):
        """Compte les studios factices.

        Args:
            connection (object): Connexion recue.

        Returns:
            int: Nombre de studios.
        """

        return 3

    def count_public_library_studios_by_criteria(self, connection, criteria):
        """Compte les studios filtres factices.

        Args:
            connection (object): Connexion recue.
            criteria (LibraryQueryCriteria): Criteres recus.

        Returns:
            int: Nombre de studios filtres.
        """

        return 1

    def list_public_library_studios(self, connection, criteria):
        """Liste les studios factices.

        Args:
            connection (object): Connexion recue.
            criteria (LibraryQueryCriteria): Criteres recus.

        Returns:
            list[dict]: Studios factices.
        """

        return [
            {
                "id": 7,
                "name": "Square",
                "country": "Japan",
                "city": None,
                "creation_date": None,
                "status": "ACTIVE",
                "editor_total_games": 4,
                "developer_total_games": 5,
            }
        ]


class FakeGameRepository:
    """Repository jeux factice pour la Bibliotheque."""

    def count_public_library_games(self, connection):
        """Compte les jeux factices.

        Args:
            connection (object): Connexion recue.

        Returns:
            int: Nombre de jeux.
        """

        return 9

    def count_public_library_games_by_criteria(self, connection, criteria):
        """Compte les jeux filtres factices.

        Args:
            connection (object): Connexion recue.
            criteria (LibraryQueryCriteria): Criteres recus.

        Returns:
            int: Nombre de jeux filtres.
        """

        return 501

    def list_public_library_games(self, connection, criteria):
        """Liste les jeux factices.

        Args:
            connection (object): Connexion recue.
            criteria (LibraryQueryCriteria): Criteres recus.

        Returns:
            list[dict]: Jeux factices.
        """

        return [
            {
                "id": 11,
                "name": "Final Fantasy",
                "release_date": datetime(1987, 12, 18),
                "developer": "Square",
                "editor": None,
                "platform": "NES",
            }
        ]


class LibraryServiceTest(unittest.TestCase):
    """Valide le service de consultation publique Bibliotheque."""

    def setUp(self):
        """Prepare le service teste.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.engine = FakeEngine()
        self.platform_repository = FakePlatformRepository()
        self.studio_repository = FakeStudioRepository()
        self.game_repository = FakeGameRepository()
        self.service = LibraryService(
            DatabaseConfiguration(None, "collection", "0.1"),
            platform_repository=self.platform_repository,
            studio_repository=self.studio_repository,
            game_repository=self.game_repository,
            engine=self.engine,
        )
        self.query_parser = LibraryQueryParser()

    def test_count_entities_returns_global_reference_counts(self):
        """Verifie le payload de comptage global.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les compteurs.
        """

        payload = self.service.count_entities()

        self.assertEqual({"platforms": 2, "studios": 3, "games": 9}, payload)
        self.assertEqual(1, self.engine.connect_count)

    def test_library_service_provider_reuses_singleton_instance(self):
        """Verifie que le fournisseur Bibliotheque construit une seule instance.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le singleton et son reset.
        """

        created_services = []

        def create_service():
            service = object()
            created_services.append(service)
            return service

        provider = LibraryServiceProvider(create_service)

        first_service = provider.get_service()
        second_service = provider()
        provider.reset()
        third_service = provider.get_service()

        self.assertIs(first_service, second_service)
        self.assertIsNot(first_service, third_service)
        self.assertEqual(2, len(created_services))

    def test_list_platforms_returns_contract_payload(self):
        """Verifie le payload pagine des plateformes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat JSON.
        """

        criteria = self.query_parser.parse("platforms", {"page": "1", "size": "5"})

        payload = self.service.list_platforms(criteria)

        self.assertEqual(
            {
                "totalElements": 6,
                "page": 1,
                "size": 5,
                "totalPages": 2,
            },
            payload["page"],
        )
        self.assertEqual(
            [
                {
                    "id": 1,
                    "name": "Switch",
                    "release_date": "2017-03-03",
                    "manufacturer": "",
                    "description": {"screen": "portable"},
                    "status": "ACTIVE",
                    "total_games": 12,
                }
            ],
            payload["platforms"],
        )

    def test_list_studios_returns_contract_payload(self):
        """Verifie le payload pagine des studios.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat JSON.
        """

        criteria = self.query_parser.parse("studios", {})

        payload = self.service.list_studios(criteria)

        self.assertEqual(1, payload["page"]["totalElements"])
        self.assertEqual(1, payload["page"]["totalPages"])
        self.assertEqual(
            [
                {
                    "id": 7,
                    "name": "Square",
                    "country": "Japan",
                    "city": "",
                    "creation_date": "",
                    "status": "ACTIVE",
                    "editor_total_games": 4,
                    "developer_total_games": 5,
                }
            ],
            payload["studios"],
        )

    def test_list_games_returns_contract_payload(self):
        """Verifie le payload pagine des jeux.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contrat JSON.
        """

        criteria = self.query_parser.parse("games", {"size": "500"})

        payload = self.service.list_games(criteria)

        self.assertEqual(501, payload["page"]["totalElements"])
        self.assertEqual(2, payload["page"]["totalPages"])
        self.assertEqual(
            [
                {
                    "id": 11,
                    "name": "Final Fantasy",
                    "release_date": "1987-12-18",
                    "developer": "Square",
                    "editor": "",
                    "status": "",
                    "platform": "NES",
                }
            ],
            payload["games"],
        )

    def test_constructor_rejects_missing_database_url_without_injected_engine(self):
        """Verifie qu'un moteur est requis sans configuration SQL.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur attendue.
        """

        with self.assertRaises(ValueError):
            LibraryService(DatabaseConfiguration(None, "collection", "0.1"))


if __name__ == "__main__":
    unittest.main()
