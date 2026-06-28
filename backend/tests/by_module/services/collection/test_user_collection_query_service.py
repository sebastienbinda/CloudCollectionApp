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
from decimal import Decimal
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

    def count_collection_games(self, connection, user_id, wishlist=None):
        """Compte les jeux factices.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            wishlist (bool | None): Filtre wishlist recu.

        Returns:
            int: Nombre de jeux configure.
        """

        self.calls.append(("count_collection_games", connection, user_id, wishlist))
        return 3 if wishlist is True else 42

    def find_max_platform_name(self, connection, user_id, wishlist=None):
        """Retourne la plateforme max factice.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            wishlist (bool | None): Filtre wishlist recu.

        Returns:
            str: Nom de plateforme.
        """

        self.calls.append(("find_max_platform_name", connection, user_id, wishlist))
        return "NES" if wishlist is True else "Switch"

    def find_price_statistics(self, connection, user_id, wishlist=None):
        """Retourne les statistiques de prix factices.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            wishlist (bool | None): Filtre wishlist recu.

        Returns:
            dict: Somme et moyenne configurees.
        """

        self.calls.append(("find_price_statistics", connection, user_id, wishlist))
        if wishlist is True:
            return {"total_value": Decimal("19.99"), "average_value": Decimal("9.995")}
        return {"total_value": Decimal("125.50"), "average_value": Decimal("41.8333")}

    def find_collection_file_path(self, connection, user_id):
        """Retourne un chemin de fichier factice.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.

        Returns:
            str: Chemin de collection.
        """

        self.calls.append(("find_collection_file_path", connection, user_id))
        return "/users/workspace/7/7-collection.ods"

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
        return [
            {
                "id": 1,
                "name": "Switch",
                "release_date": datetime(2017, 3, 3, 9, 0),
                "end_date": None,
                "manufacturer": "Nintendo",
                "description": {"generation": "8"},
                "nb_games": 25,
                "total_games": 25,
                "total_value": Decimal("120.75"),
                "average_value": Decimal("6.355"),
            }
        ]

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
                "wishlist": True,
                "purchase_price": Decimal("2.25"),
                "price_unit": "EUR",
                "buy_location": "Paris",
                "buy_date": datetime(2026, 6, 1),
                "grade": "Rare",
                "condition": 3,
                "has_manual": True,
                "is_collector": False,
                "has_steelbook": True,
                "is_digital": False,
                "region": "EU-FR",
                "description": "Edition francaise",
            }
        ]

    def find_game(self, connection, user_id, game_id):
        """Recherche un jeu de collection factice.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            game_id (int): Identifiant du jeu recherche.

        Returns:
            dict | None: Jeu factice ou absence.
        """

        self.calls.append(("find_game", connection, user_id, game_id))
        if game_id != 11:
            return None
        return {
            "id": 11,
            "name": "Final Fantasy",
            "platform_name": "NES",
            "platform_id": 3,
            "release_date": datetime(1987, 12, 18),
            "studio_name": None,
            "studio_id": None,
            "wishlist": True,
        }


class EmptyUserCollectionQueryRepository(FakeUserCollectionQueryRepository):
    """Repository factice pour un utilisateur sans collection."""

    def count_collection_games(self, connection, user_id, wishlist=None):
        """Compte une collection vide.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            wishlist (bool | None): Filtre wishlist recu.

        Returns:
            int: Zero.
        """

        self.calls.append(("count_collection_games", connection, user_id, wishlist))
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
            {
                "total": 42,
                "total_value": 125.5,
                "average_value": 41.83,
                "max_platform": "Switch",
                "collection": {
                    "total": 42,
                    "total_value": 125.5,
                    "average_value": 41.83,
                    "max_platform": "Switch",
                },
                "wishlist": {
                    "total": 3,
                    "total_value": 19.99,
                    "average_value": 10.0,
                    "max_platform": "NES",
                },
            },
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
            {
                "total": 0,
                "total_value": 0,
                "average_value": 0,
                "max_platform": "",
                "collection": {
                    "total": 0,
                    "total_value": 0,
                    "average_value": 0,
                    "max_platform": "",
                },
                "wishlist": {
                    "total": 0,
                    "total_value": 0,
                    "average_value": 0,
                    "max_platform": "",
                },
            },
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
                    "release_date": "2017-03-03",
                    "end_date": "",
                    "manufacturer": "Nintendo",
                    "description": {"generation": "8"},
                    "nb_games": 25,
                    "total_games": 25,
                    "total_value": 120.75,
                    "average_value": 6.36,
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
                    "version": "EU-FR",
                    "purchase_price": 2.25,
                    "price_unit": "EUR",
                    "buy_date": "2026-06-01",
                    "buy_location": "Paris",
                    "grade": "Rare",
                    "condition": 3,
                    "has_manual": True,
                    "is_collector": False,
                    "has_steelbook": True,
                    "is_digital": False,
                    "region": "EU-FR",
                    "description": "Edition francaise",
                    "wishlist": True,
                }
            ],
            payload["games"],
        )

    def test_get_game_returns_collection_detail_payload(self):
        """Verifie le payload detail d'un jeu de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le jeu serialise.
        """

        game = self.service.get_game(7, 11)

        self.assertEqual("Final Fantasy", game["name"])
        self.assertEqual("NES", game["platform_name"])
        self.assertTrue(game["wishlist"])

    def test_get_game_returns_none_for_unknown_collection_game(self):
        """Verifie l'absence de jeu dans la collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence.
        """

        self.assertIsNone(self.service.get_game(7, 999))

    def test_parser_rejects_invalid_platform_id(self):
        """Verifie le refus explicite d'un identifiant plateforme invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le message d'erreur.
        """

        with self.assertRaisesRegex(ValueError, "Invalid platform_id"):
            self.query_parser.parse_games({"platform_id": "abc"})

    def test_get_collection_file_path_uses_repository(self):
        """Verifie la lecture du chemin de fichier utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le chemin retourne.
        """

        self.assertEqual("/users/workspace/7/7-collection.ods", self.service.get_collection_file_path(7))
        self.assertIn(("find_collection_file_path", self.engine.connection, 7), self.repository.calls)

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
                "sort": ["platform_name,desc", "name,asc"],
            }
        )

        self.assertEqual("ecole", criteria.normalized_name)
        self.assertEqual("dev", criteria.normalized_studio_name)
        self.assertEqual("nes", criteria.normalized_platform_name)
        self.assertEqual(12, criteria.platform_id)
        self.assertIsNone(criteria.wishlist)
        self.assertFalse(criteria.has_invalid_platform_id)
        self.assertEqual("1980-01-01", criteria.release_date_from.isoformat())
        self.assertEqual("1990-12-31", criteria.release_date_to.isoformat())
        self.assertEqual(("platform_name", "desc"), (criteria.sort_rules[0].column, criteria.sort_rules[0].direction))
        self.assertEqual(("name", "asc"), (criteria.sort_rules[1].column, criteria.sort_rules[1].direction))

    def test_parser_rejects_unsupported_game_sort_column(self):
        """Verifie le refus explicite d'une colonne de tri jeux inconnue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le message d'erreur.
        """

        with self.assertRaisesRegex(ValueError, "Unsupported sort column 'unknown'"):
            self.query_parser.parse_games({"sort": ["unknown,asc"]})

    def test_parser_rejects_unsupported_sort_direction(self):
        """Verifie le refus explicite d'un sens de tri invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le message d'erreur.
        """

        with self.assertRaisesRegex(ValueError, "Unsupported sort direction 'up'"):
            self.query_parser.parse_games({"sort": ["name,up"]})

    def test_parser_rejects_invalid_release_date_range(self):
        """Verifie le refus explicite d'une plage de dates invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le message d'erreur.
        """

        with self.assertRaisesRegex(ValueError, "Invalid release_date"):
            self.query_parser.parse_games({"release_date": "1980-01-01"})

        with self.assertRaisesRegex(ValueError, "Invalid release_date"):
            self.query_parser.parse_games({"release_date": "not-a-date..1990-12-31"})

    def test_parser_rejects_unsupported_game_query_parameter(self):
        """Verifie le refus explicite d'un critere de recherche inconnu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le message d'erreur.
        """

        with self.assertRaisesRegex(ValueError, "Unsupported query parameter 'unknown_filter'"):
            self.query_parser.parse_games({"unknown_filter": "x"})

    def test_parser_reads_only_boolean_wishlist_filter_values(self):
        """Verifie le parsing du filtre wishlist.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les valeurs booleennes.
        """

        self.assertFalse(self.query_parser.parse_games({"wishlist": "false"}).wishlist)
        self.assertTrue(self.query_parser.parse_games({"wishlist": "true"}).wishlist)
        self.assertFalse(self.query_parser.parse_games({"wishlist": False}).wishlist)
        self.assertTrue(self.query_parser.parse_games({"wishlist": True}).wishlist)
        self.assertIsNone(self.query_parser.parse_games({}).wishlist)
        for invalid_value in ["0", "1", "oui", "maybe"]:
            with self.assertRaisesRegex(ValueError, "Invalid wishlist"):
                self.query_parser.parse_games({"wishlist": invalid_value})

    def test_parser_reads_platform_wishlist_filter(self):
        """Verifie le parsing wishlist des plateformes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le filtre plateforme.
        """

        self.assertFalse(self.query_parser.parse_platforms({"wishlist": "false"}).wishlist)
        self.assertTrue(self.query_parser.parse_platforms({"wishlist": "true"}).wishlist)
        self.assertIsNone(self.query_parser.parse_platforms({}).wishlist)
        with self.assertRaisesRegex(ValueError, "Invalid wishlist"):
            self.query_parser.parse_platforms({"wishlist": "1"})

    def test_parser_accepts_platform_catalog_sort_columns(self):
        """Verifie les tris catalogue autorises pour les plateformes collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les colonnes de tri.
        """

        for column in ["name", "release_date", "end_date", "manufacturer"]:
            criteria = self.query_parser.parse_platforms({"sort": f"{column},desc"})
            self.assertEqual((column, "desc"), (
                criteria.sort_rules[0].column,
                criteria.sort_rules[0].direction,
            ))

    def test_parser_rejects_unsupported_platform_query_parameter(self):
        """Verifie le refus explicite d'un critere plateforme inconnu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le message d'erreur.
        """

        with self.assertRaisesRegex(ValueError, "Unsupported query parameter 'platform_id'"):
            self.query_parser.parse_platforms({"platform_id": "12"})

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
