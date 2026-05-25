#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-25
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du service de consultation collection utilisateur.

from datetime import datetime
import unittest

from services.collection import UserCollectionQueryParser
from services.collection.user_collection_query_service import UserCollectionQueryService
from services.database import DatabaseConfiguration


class FakeConnectionContext:
    """Contexte de connexion factice."""

    def __init__(self, connection):
        """Initialise le contexte.

        Args:
            connection (object): Connexion exposee par le contexte.

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
            bool: `False` pour propager les exceptions.
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


class FakeUserCollectionQueryRepository:
    """Repository factice de consultation collection."""

    def __init__(self):
        """Initialise le repository factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.calls = []

    def count_collection_games(self, connection, user_id):
        """Compte les jeux factices.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.

        Returns:
            int: Nombre de jeux configure.
        """

        self.calls.append(("count_collection_games", connection, user_id))
        return 42

    def find_max_platform_name(self, connection, user_id):
        """Retourne la plateforme max factice.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.

        Returns:
            str: Nom de plateforme.
        """

        self.calls.append(("find_max_platform_name", connection, user_id))
        return "Switch"

    def count_platforms_by_criteria(self, connection, user_id, criteria):
        """Compte les plateformes factices.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionPlatformQueryCriteria): Criteres recus.

        Returns:
            int: Nombre de plateformes.
        """

        self.calls.append(("count_platforms", connection, user_id, criteria))
        return 6

    def list_platforms(self, connection, user_id, criteria):
        """Liste les plateformes factices.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionPlatformQueryCriteria): Criteres recus.

        Returns:
            list[dict]: Plateformes factices.
        """

        self.calls.append(("list_platforms", connection, user_id, criteria))
        return [{"id": 1, "name": "Switch", "nb_games": 25}]

    def count_games_by_criteria(self, connection, user_id, criteria):
        """Compte les jeux factices.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionGameQueryCriteria): Criteres recus.

        Returns:
            int: Nombre de jeux.
        """

        self.calls.append(("count_games", connection, user_id, criteria))
        return 501

    def list_games(self, connection, user_id, criteria):
        """Liste les jeux factices.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionGameQueryCriteria): Criteres recus.

        Returns:
            list[dict]: Jeux factices.
        """

        self.calls.append(("list_games", connection, user_id, criteria))
        return [
            {
                "id": 11,
                "name": "Final Fantasy",
                "platform_name": "NES",
                "platform_id": 3,
                "release_date": datetime(1987, 12, 18),
                "studio_name": None,
                "studio_id": None,
            }
        ]


class EmptyUserCollectionQueryRepository(FakeUserCollectionQueryRepository):
    """Repository factice pour un utilisateur sans collection."""

    def count_collection_games(self, connection, user_id):
        """Compte une collection vide.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.

        Returns:
            int: Zero.
        """

        self.calls.append(("count_collection_games", connection, user_id))
        return 0

    def count_platforms_by_criteria(self, connection, user_id, criteria):
        """Compte les plateformes d'une collection vide.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionPlatformQueryCriteria): Criteres recus.

        Returns:
            int: Zero.
        """

        self.calls.append(("count_platforms", connection, user_id, criteria))
        return 0

    def list_platforms(self, connection, user_id, criteria):
        """Liste les plateformes d'une collection vide.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionPlatformQueryCriteria): Criteres recus.

        Returns:
            list[dict]: Liste vide.
        """

        self.calls.append(("list_platforms", connection, user_id, criteria))
        return []

    def count_games_by_criteria(self, connection, user_id, criteria):
        """Compte les jeux d'une collection vide.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionGameQueryCriteria): Criteres recus.

        Returns:
            int: Zero.
        """

        self.calls.append(("count_games", connection, user_id, criteria))
        return 0

    def list_games(self, connection, user_id, criteria):
        """Liste les jeux d'une collection vide.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionGameQueryCriteria): Criteres recus.

        Returns:
            list[dict]: Liste vide.
        """

        self.calls.append(("list_games", connection, user_id, criteria))
        return []


class UserCollectionQueryServiceTest(unittest.TestCase):
    """Valide le service de consultation de collection utilisateur."""

    def setUp(self):
        """Prepare le service teste.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.engine = FakeEngine()
        self.repository = FakeUserCollectionQueryRepository()
        self.service = UserCollectionQueryService(
            DatabaseConfiguration(None, "collection", "0.1"),
            repository=self.repository,
            engine=self.engine,
        )
        self.query_parser = UserCollectionQueryParser()

    def test_get_statistics_returns_contract_payload(self):
        """Verifie le contrat des statistiques globales.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        payload = self.service.get_statistics(7)

        self.assertEqual(
            {"total": 42, "total_value": 0, "average_value": 0, "max_platform": "Switch"},
            payload,
        )
        self.assertEqual(1, self.engine.connect_count)

    def test_empty_collection_returns_standard_empty_payloads(self):
        """Verifie les reponses vides pour un utilisateur sans collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les contrats vides.
        """

        service = UserCollectionQueryService(
            DatabaseConfiguration(None, "collection", "0.1"),
            repository=EmptyUserCollectionQueryRepository(),
            engine=FakeEngine(),
        )

        statistics = service.get_statistics(7)
        platforms = service.list_platforms(7, self.query_parser.parse_platforms({}))
        games = service.list_games(7, self.query_parser.parse_games({}))

        self.assertEqual(
            {"total": 0, "total_value": 0, "average_value": 0, "max_platform": ""},
            statistics,
        )
        self.assertEqual(
            {"page": {"totalElements": 0, "page": 0, "size": 500, "totalPages": 0}, "platforms": []},
            platforms,
        )
        self.assertEqual(
            {"page": {"totalElements": 0, "page": 0, "size": 500, "totalPages": 0}, "games": []},
            games,
        )

    def test_list_platforms_returns_paginated_contract_payload(self):
        """Verifie le contrat pagine des plateformes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        criteria = self.query_parser.parse_platforms({"page": "1", "size": "5"})

        payload = self.service.list_platforms(7, criteria)

        self.assertEqual({"totalElements": 6, "page": 1, "size": 5, "totalPages": 2}, payload["page"])
        self.assertEqual(
            [
                {
                    "id": 1,
                    "name": "Switch",
                    "nb_games": 25,
                    "total_value": 0,
                    "average_value": 0,
                }
            ],
            payload["platforms"],
        )

    def test_list_games_returns_paginated_contract_payload(self):
        """Verifie le contrat pagine des jeux.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        criteria = self.query_parser.parse_games({"size": "500"})

        payload = self.service.list_games(7, criteria)

        self.assertEqual(501, payload["page"]["totalElements"])
        self.assertEqual(2, payload["page"]["totalPages"])
        self.assertEqual(
            [
                {
                    "id": 11,
                    "name": "Final Fantasy",
                    "platform_name": "NES",
                    "platform_id": 3,
                    "release_date": "1987-12-18",
                    "studio_name": "",
                    "studio_id": None,
                    "version": "",
                    "buy_date": "",
                    "buy_location": "",
                    "grade": "",
                }
            ],
            payload["games"],
        )

    def test_list_games_returns_empty_payload_for_invalid_platform_id(self):
        """Verifie le retour vide pour un identifiant plateforme invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le court-circuit.
        """

        criteria = self.query_parser.parse_games({"platform_id": "abc"})

        payload = self.service.list_games(7, criteria)

        self.assertEqual({"totalElements": 0, "page": 0, "size": 500, "totalPages": 0}, payload["page"])
        self.assertEqual([], payload["games"])
        self.assertEqual(0, self.engine.connect_count)

    def test_parser_normalizes_filters_sort_and_date_range(self):
        """Verifie le parsing des filtres specifiques collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les criteres.
        """

        criteria = self.query_parser.parse_games(
            {
                "name": " École ",
                "studio_name": " Dév ",
                "platform_name": " NéS ",
                "platform_id": "12",
                "release_date": "1980-01-01..1990-12-31",
                "sort": ["platform_name,desc", "unknown,asc"],
            }
        )

        self.assertEqual("ecole", criteria.normalized_name)
        self.assertEqual("dev", criteria.normalized_studio_name)
        self.assertEqual("nes", criteria.normalized_platform_name)
        self.assertEqual(12, criteria.platform_id)
        self.assertFalse(criteria.has_invalid_platform_id)
        self.assertEqual("1980-01-01", criteria.release_date_from.isoformat())
        self.assertEqual("1990-12-31", criteria.release_date_to.isoformat())
        self.assertEqual(("platform_name", "desc"), (criteria.sort_rules[0].column, criteria.sort_rules[0].direction))
        self.assertEqual(("name", "asc"), (criteria.sort_rules[1].column, criteria.sort_rules[1].direction))

    def test_constructor_rejects_missing_database_url_without_injected_engine(self):
        """Verifie qu'un moteur est requis sans configuration SQL.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur attendue.
        """

        with self.assertRaises(ValueError):
            UserCollectionQueryService(DatabaseConfiguration(None, "collection", "0.1"))


if __name__ == "__main__":
    unittest.main()
