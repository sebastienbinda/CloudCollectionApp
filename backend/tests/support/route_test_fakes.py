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
# Description : faux services de routes Flask.

from pathlib import Path


class FakeLibraryService:
    """Service Bibliotheque factice."""

    last_platforms_criteria = None
    last_studios_criteria = None
    last_games_criteria = None
    last_entities_requester_profile = None
    last_game_detail_context = None

    def count_entities(self, requester_profile="PUBLIC"):
        """Retourne les compteurs globaux.

        Args:
            requester_profile (str): Profil du demandeur.

        Returns:
            dict[str, int]: Compteurs factices.
        """

        self.__class__.last_entities_requester_profile = requester_profile
        return {"platforms": 2, "studios": 3, "games": 4}

    def list_platforms(self, criteria):
        """Liste les plateformes publiques.

        Args:
            criteria (LibraryQueryCriteria): Criteres recus.

        Returns:
            dict[str, object]: Payload plateformes.
        """

        self.__class__.last_platforms_criteria = criteria
        return {
            "page": self._page(criteria),
            "platforms": [
                {
                    "id": 1,
                    "name": "Switch",
                    "release_date": "2017-03-03",
                    "end_date": "",
                    "manufacturer": "Nintendo",
                    "description": "",
                    "total_games": 12,
                }
            ],
        }

    def get_platform(self, platform_id):
        """Retourne une plateforme publique factice.

        Args:
            platform_id (int): Identifiant de la plateforme recherchee.

        Returns:
            dict[str, object] | None: Plateforme factice ou absence.
        """

        if platform_id != 1:
            return None
        return {
            "id": 1,
            "name": "Switch",
            "release_date": "2017-03-03",
            "end_date": "",
            "manufacturer": "Nintendo",
            "description": "",
            "total_games": 12,
            "aliases": [
                {
                    "name": "Nintendo Switch",
                    "category": "official",
                    "usage_region": "Japon",
                    "comment": "",
                }
            ],
            "images": [{"id": 41, "type": "MAIN"}],
        }

    def list_studios(self, criteria):
        """Liste les studios publics.

        Args:
            criteria (LibraryQueryCriteria): Criteres recus.

        Returns:
            dict[str, object]: Payload studios.
        """

        self.__class__.last_studios_criteria = criteria
        return {"page": self._page(criteria), "studios": [{"id": 2, "name": "Square", "country": "Japan", "city": "Tokyo", "creation_date": "", "status": "ACTIVE", "editor_total_games": 5, "developer_total_games": 7}]}

    def list_games(self, criteria):
        """Liste les jeux publics.

        Args:
            criteria (LibraryQueryCriteria): Criteres recus.

        Returns:
            dict[str, object]: Payload jeux.
        """

        self.__class__.last_games_criteria = criteria
        return {
            "page": self._page(criteria),
            "games": [
                {
                    "id": 3,
                    "name": "Final Fantasy",
                    "release_date": "1987-12-18",
                    "developer": "Square",
                    "editor": "",
                    "status": "",
                    "platform": "NES",
                    "platform_end_date": "1995-08-14",
                    "platform_common_alias": "NES",
                    "duplicate_flag": False,
                    "in_current_user_collection": criteria.current_user_id == 7,
                }
            ],
        }

    def get_game(self, game_id, requester_profile="PUBLIC", current_user_id=None):
        """Retourne un jeu public factice.

        Args:
            game_id (int): Identifiant du jeu recherche.
            requester_profile (str): Profil du demandeur.
            current_user_id (int | None): Identifiant utilisateur optionnel.

        Returns:
            dict[str, object] | None: Jeu factice ou absence.
        """

        if game_id != 3:
            return None
        self.__class__.last_game_detail_context = (requester_profile, current_user_id)
        return {"id": 3, "name": "Final Fantasy", "release_date": "1987-12-18", "developer": "Square", "editor": "", "status": "", "platform": "NES", "platform_end_date": "1995-08-14", "platform_common_alias": "NES", "duplicate_flag": True}

    def _page(self, criteria):
        """Construit une page factice.

        Args:
            criteria (LibraryQueryCriteria): Criteres recus.

        Returns:
            dict[str, int]: Page factice.
        """

        return {"totalElements": 1, "page": criteria.page_request.page, "size": criteria.page_request.size, "totalPages": 1}


class FakeUserCollectionQueryService:
    """Service de consultation collection factice."""

    last_platforms_criteria = None
    last_games_criteria = None
    collection_file_path = str(Path(__file__))
    last_user_id = None
    last_statistics_scope = None

    def get_statistics(self, user_id, include_collection=True, include_wishlist=True):
        """Retourne les statistiques de collection factices.

        Args:
            user_id (int): Identifiant utilisateur.
            include_collection (bool): Autorise les statistiques collection.
            include_wishlist (bool): Autorise les statistiques wishlist.

        Returns:
            dict[str, object]: Statistiques factices.
        """

        self.__class__.last_user_id = user_id
        self.__class__.last_statistics_scope = (include_collection, include_wishlist)
        collection = {
            "total": 42,
            "total_value": 1234.5,
            "average_value": 29.39,
            "max_platform": "Switch",
            "first_game_date": "1986-02-21",
            "last_game_date": "2017-03-03",
        } if include_collection else self._empty_statistics()
        wishlist = {
            "total": 3,
            "total_value": 150,
            "average_value": 50,
            "max_platform": "NES",
            "first_game_date": "1987-12-18",
            "last_game_date": "1990-04-27",
        } if include_wishlist else self._empty_statistics()
        return {
            **collection,
            "collection": collection,
            "wishlist": wishlist,
        }

    def list_platforms(self, user_id, criteria):
        """Liste les plateformes de collection factices.

        Args:
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionPlatformQueryCriteria): Criteres recus.

        Returns:
            dict[str, object]: Payload plateformes.
        """

        self.__class__.last_platforms_criteria = criteria
        self.__class__.last_user_id = user_id
        return {
            "page": self._page(criteria),
            "platforms": [
                {
                    "id": 1,
                    "name": "Switch",
                    "release_date": "2017-03-03",
                    "end_date": "",
                    "manufacturer": "Nintendo",
                    "description": {"generation": "8"},
                    "nb_games": 25,
                    "total_games": 25,
                    "total_value": 1499.75,
                    "average_value": 59.99,
                }
            ],
        }

    def list_games(self, user_id, criteria):
        """Liste les jeux de collection factices.

        Args:
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionGameQueryCriteria): Criteres recus.

        Returns:
            dict[str, object]: Payload jeux.
        """

        self.__class__.last_games_criteria = criteria
        self.__class__.last_user_id = user_id
        return {
            "page": self._page(criteria),
            "games": [
                {
                    "id": 3,
                    "name": "Mario Kart",
                    "platform_name": "Switch",
                    "platform_id": 1,
                    "platform_end_date": "",
                    "platform_common_alias": "Switch",
                    "release_date": "1992-08-27",
                    "duplicate_flag": False,
                    "studio_name": "Nintendo",
                    "studio_id": 2,
                    "version": "",
                    "buy_date": "",
                    "buy_location": "",
                    "grade": "",
                    "purchase_price": 59.99,
                    "price_unit": "EUR",
                    "wishlist": criteria.wishlist is True,
                }
            ],
        }

    def get_collection_file_path(self, user_id):
        """Retourne le chemin de fichier configure.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            str: Chemin du fichier.
        """

        return self.__class__.collection_file_path

    def get_game(self, user_id, game_id):
        """Retourne un jeu de collection factice.

        Args:
            user_id (int): Identifiant utilisateur.
            game_id (int): Identifiant du jeu recherche.

        Returns:
            dict[str, object] | None: Jeu factice ou absence.
        """

        if game_id not in (3, 4):
            return None
        self.__class__.last_user_id = user_id
        return {
            "id": game_id,
            "name": "Mario Kart",
            "platform_name": "Switch",
            "platform_id": 1,
            "platform_end_date": "",
            "platform_common_alias": "Switch",
            "release_date": "1992-08-27",
            "studio_name": "Nintendo",
            "studio_id": 2,
            "version": "",
            "buy_date": "",
            "buy_location": "",
            "grade": "",
            "purchase_price": 59.99,
            "price_unit": "EUR",
            "wishlist": game_id == 4,
        }

    @staticmethod
    def _empty_statistics():
        """Retourne une categorie de statistiques vide.

        Args:
            Aucun.

        Returns:
            dict[str, object]: Statistiques sans donnees.
        """

        return {
            "total": 0,
            "total_value": 0,
            "average_value": 0,
            "max_platform": "",
            "first_game_date": "",
            "last_game_date": "",
        }

    def _page(self, criteria):
        """Construit une page factice.

        Args:
            criteria (object): Criteres recus.

        Returns:
            dict[str, int]: Page factice.
        """

        return {
            "totalElements": 1,
            "page": criteria.page_request.page,
            "size": criteria.page_request.size,
            "totalPages": 1,
        }


class FakeUserCollectionStatisticsService:
    """Service de statistiques detaillees factice."""

    last_user_id = None
    last_platform_id = None

    def get_statistics(self, user_id, platform_id=None):
        """Retourne les statistiques detaillees factices.

        Args:
            user_id (int): Identifiant utilisateur.
            platform_id (int | None): Plateforme filtree.

        Returns:
            dict[str, object]: Statistiques detaillees factices.
        """

        self.__class__.last_user_id = user_id
        self.__class__.last_platform_id = platform_id
        return {
            "total_games": 2,
            "platform_distribution": [
                {
                    "platform_id": 1,
                    "platform_name": "Switch",
                    "games_count": 2,
                    "ratio": 100,
                }
            ],
            "release_year_distribution": [
                {"year": 1992, "games_count": 1},
                {"year": 2017, "games_count": 1},
            ],
            "purchase_year_distribution": [
                {"year": 2024, "games_count": 2},
            ],
            "top_rated_games": [
                {
                    "id": 3,
                    "name": "Mario Kart",
                    "platform_name": "Switch",
                    "release_date": "1992-08-27",
                    "buy_date": "2024-03-10",
                    "grade": "9.5",
                    "grade_normalized": 95,
                }
            ],
        }
