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

    def count_entities(self):
        """Retourne les compteurs globaux.

        Args:
            Aucun.

        Returns:
            dict[str, int]: Compteurs factices.
        """

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
        return {"page": self._page(criteria), "games": [{"id": 3, "name": "Final Fantasy", "release_date": "1987-12-18", "developer": "Square", "editor": "", "status": "", "platform": "NES"}]}

    def get_game(self, game_id):
        """Retourne un jeu public factice.

        Args:
            game_id (int): Identifiant du jeu recherche.

        Returns:
            dict[str, object] | None: Jeu factice ou absence.
        """

        if game_id != 3:
            return None
        return {"id": 3, "name": "Final Fantasy", "release_date": "1987-12-18", "developer": "Square", "editor": "", "status": "", "platform": "NES"}

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

    def get_statistics(self, user_id):
        """Retourne les statistiques de collection factices.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            dict[str, object]: Statistiques factices.
        """

        return {
            "total": 42,
            "total_value": 0,
            "average_value": 0,
            "max_platform": "Switch",
            "collection": {
                "total": 42,
                "total_value": 0,
                "average_value": 0,
                "max_platform": "Switch",
            },
            "wishlist": {
                "total": 3,
                "total_value": 0,
                "average_value": 0,
                "max_platform": "NES",
            },
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
                    "total_value": 0,
                    "average_value": 0,
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
        return {
            "page": self._page(criteria),
            "games": [
                {
                    "id": 3,
                    "name": "Mario Kart",
                    "platform_name": "Switch",
                    "platform_id": 1,
                    "release_date": "1992-08-27",
                    "studio_name": "Nintendo",
                    "studio_id": 2,
                    "version": "",
                    "buy_date": "",
                    "buy_location": "",
                    "grade": "",
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

        if game_id != 3:
            return None
        return {
            "id": 3,
            "name": "Mario Kart",
            "platform_name": "Switch",
            "platform_id": 1,
            "release_date": "1992-08-27",
            "studio_name": "Nintendo",
            "studio_id": 2,
            "version": "",
            "buy_date": "",
            "buy_location": "",
            "grade": "",
            "wishlist": False,
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
