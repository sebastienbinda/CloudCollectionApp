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
                "end_date": None,
                "manufacturer": None,
                "description": {"screen": "portable"},
                "total_games": 12,
            }
        ]

    def find_public_library_platform(self, connection, platform_id):
        """Retourne une plateforme factice.

        Args:
            connection (object): Connexion recue.
            platform_id (int): Identifiant de plateforme.

        Returns:
            dict | None: Plateforme factice ou absence.
        """

        self.calls.append(("find", connection, platform_id))
        if platform_id != 1:
            return None
        return {
            "id": 1,
            "name": "Switch",
            "release_date": datetime(2017, 3, 3, 9, 30),
            "end_date": None,
            "manufacturer": "Nintendo",
            "description": {"screen": "portable"},
            "total_games": 12,
            "aliases": [
                {
                    "name": "Nintendo Switch",
                    "category": "official",
                    "usage_region": "Japon",
                    "comment": None,
                }
            ],
        }


class FakePlatformImageRepository:
    """Repository images factice pour la Bibliotheque."""

    def __init__(self):
        """Initialise le repository images factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.calls = []

    def list_accepted_images(self, connection, platform_id):
        """Liste les images acceptees factices.

        Args:
            connection (object): Connexion recue.
            platform_id (int): Identifiant de plateforme.

        Returns:
            list[dict]: Images acceptees.
        """

        self.calls.append(("list_accepted", connection, platform_id))
        return [
            {
                "id": 41,
                "type": "MAIN",
                "status": "ACCEPTED",
                "path": "/images/platforms/switch/main.png",
            },
            {
                "id": 42,
                "type": "OTHER",
                "status": "ACCEPTED",
                "path": "/images/platforms/switch/other.png",
            },
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

    last_count_include_waiting_validation = None
    last_find_call = None

    def count_public_library_games(self, connection, include_waiting_validation=False):
        """Compte les jeux factices.

        Args:
            connection (object): Connexion recue.
            include_waiting_validation (bool): Inclut les jeux en attente si `True`.

        Returns:
            int: Nombre de jeux.
        """

        self.__class__.last_count_include_waiting_validation = include_waiting_validation
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
                "platform_end_date": datetime(1995, 8, 14),
                "platform_common_alias": "NES",
            }
        ]

    def list_current_user_collection_game_ids(self, connection, user_id, game_ids):
        """Liste les jeux factices presents dans la collection utilisateur.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            game_ids (list[int]): Identifiants de jeux verifies.

        Returns:
            set[int]: Identifiants en collection.
        """

        if user_id != 7:
            return set()
        return {game_id for game_id in game_ids if game_id == 11}

    def list_current_user_wishlist_game_ids(self, connection, user_id, game_ids):
        """Liste les jeux factices presents dans la liste de souhaits utilisateur.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.
            game_ids (list[int]): Identifiants de jeux verifies.

        Returns:
            set[int]: Identifiants en liste de souhaits.
        """

        if user_id != 8:
            return set()
        return {game_id for game_id in game_ids if game_id == 11}

    def find_public_library_game(
        self,
        connection,
        game_id,
        include_waiting_validation=False,
        current_user_id=None,
    ):
        """Recherche un jeu factice.

        Args:
            connection (object): Connexion recue.
            game_id (int): Identifiant du jeu recherche.
            include_waiting_validation (bool): Inclut les jeux en attente si `True`.
            current_user_id (int | None): Utilisateur proprietaire optionnel.

        Returns:
            dict | None: Jeu factice ou absence.
        """

        self.__class__.last_find_call = (
            game_id,
            include_waiting_validation,
            current_user_id,
        )
        if game_id != 11:
            return None
        return {
            "id": 11,
            "name": "Final Fantasy",
            "release_date": datetime(1987, 12, 18),
            "developer": "Square",
            "editor": None,
            "platform": "NES",
            "platform_end_date": datetime(1995, 8, 14),
            "platform_common_alias": "NES",
        }


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
        self.platform_image_repository = FakePlatformImageRepository()
        self.studio_repository = FakeStudioRepository()
        self.game_repository = FakeGameRepository()
        self.service = LibraryService(
            DatabaseConfiguration(None, "collection", "0.1"),
            platform_repository=self.platform_repository,
            platform_image_repository=self.platform_image_repository,
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
        self.assertFalse(FakeGameRepository.last_count_include_waiting_validation)

    def test_count_entities_includes_waiting_games_for_admin(self):
        """Verifie que les compteurs admin incluent les jeux en attente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le flag transmis au repository.
        """

        self.service.count_entities("ADMIN")

        self.assertTrue(FakeGameRepository.last_count_include_waiting_validation)

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
                    "end_date": "",
                    "manufacturer": "",
                    "description": {"screen": "portable"},
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
                    "platform_end_date": "1995-08-14",
                    "platform_common_alias": "NES",
                    "duplicate_flag": False,
                    "in_current_user_collection": False,
                    "in_current_user_wishlist": False,
                }
            ],
            payload["games"],
        )

    def test_list_games_marks_current_user_collection_items(self):
        """Verifie le marqueur collection utilisateur hors wishlist.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le booleen expose.
        """

        criteria = self.query_parser.parse("games", {}, current_user_id=7)

        payload = self.service.list_games(criteria)

        self.assertTrue(payload["games"][0]["in_current_user_collection"])
        self.assertFalse(payload["games"][0]["in_current_user_wishlist"])

    def test_list_games_marks_current_user_wishlist_items(self):
        """Verifie le marqueur liste de souhaits utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le booleen expose.
        """

        criteria = self.query_parser.parse("games", {}, current_user_id=8)

        payload = self.service.list_games(criteria)

        self.assertFalse(payload["games"][0]["in_current_user_collection"])
        self.assertTrue(payload["games"][0]["in_current_user_wishlist"])

    def test_get_game_returns_detail_payload(self):
        """Verifie le payload detail d'un jeu public.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le jeu serialise.
        """

        game = self.service.get_game(11)

        self.assertEqual("Final Fantasy", game["name"])
        self.assertEqual("1987-12-18", game["release_date"])
        self.assertEqual("NES", game["platform"])
        self.assertEqual("1995-08-14", game["platform_end_date"])
        self.assertEqual("NES", game["platform_common_alias"])
        self.assertEqual((11, False, None), FakeGameRepository.last_find_call)

    def test_get_game_allows_admin_waiting_visibility(self):
        """Verifie que le detail jeu transmet la visibilite admin.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contexte repository.
        """

        self.service.get_game(11, requester_profile="ADMIN")

        self.assertEqual((11, True, None), FakeGameRepository.last_find_call)

    def test_get_game_allows_owner_waiting_visibility(self):
        """Verifie que le detail jeu transmet l'utilisateur proprietaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contexte repository.
        """

        self.service.get_game(11, requester_profile="USER", current_user_id=7)

        self.assertEqual((11, False, 7), FakeGameRepository.last_find_call)

    def test_get_game_returns_none_for_unknown_game(self):
        """Verifie l'absence de jeu public.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence.
        """

        self.assertIsNone(self.service.get_game(999))

    def test_get_platform_returns_detail_payload_with_aliases(self):
        """Verifie le payload detail d'une plateforme publique.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la plateforme serialisee.
        """

        platform = self.service.get_platform(1)

        self.assertEqual("Switch", platform["name"])
        self.assertEqual("2017-03-03", platform["release_date"])
        self.assertEqual("Japon", platform["aliases"][0]["usage_region"])
        self.assertEqual("", platform["aliases"][0]["comment"])
        self.assertEqual(
            [{"id": 41, "type": "MAIN"}, {"id": 42, "type": "OTHER"}],
            platform["images"],
        )

    def test_get_platform_returns_none_for_unknown_platform(self):
        """Verifie l'absence de plateforme publique.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence.
        """

        self.assertIsNone(self.service.get_platform(999))

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
