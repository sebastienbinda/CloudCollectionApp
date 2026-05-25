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


class FakeGamesService:
    """Service VideoGames factice."""

    def list_platforms(self):
        """Retourne les plateformes.

        Args:
            Aucun.

        Returns:
            list[str]: Plateformes factices.
        """

        return ["Switch", "Playstation"]

    def reset_cache(self):
        """Reinitialise le cache factice.

        Args:
            Aucun.

        Returns:
            int: Nombre d'entrees supprimees.
        """

        return 2

    def get_ods_download(self):
        """Retourne un fichier de test.

        Args:
            Aucun.

        Returns:
            tuple[str, str]: Chemin et nom du fichier.
        """

        return str(Path(__file__)), "VideoGames-test.ods"

    def search(self, platform, query=""):
        """Recherche les jeux d'une plateforme.

        Args:
            platform (str): Plateforme demandee.
            query (str): Recherche optionnelle.

        Returns:
            list[dict[str, object]]: Jeux factices.
        """

        return [{"Nom du jeu": "Mario Kart", "Plateforme": platform, "Query": query, "Prix d'achat": 45}]

    def search_by_game_name(self, query, limit=50):
        """Recherche un jeu par nom.

        Args:
            query (str): Texte recherche.
            limit (int): Limite de resultats.

        Returns:
            list[dict[str, object]]: Jeux trouves.
        """

        return [{"Nom du jeu": "Mario Kart", "Plateforme": "Switch", "Query": query, "Prix d'achat": 45}][:limit]

    def get_home_stats(self):
        """Retourne les statistiques d'accueil.

        Args:
            Aucun.

        Returns:
            dict[str, object]: Statistiques factices.
        """

        return {"title": "Jeux Video", "totals": {"games_count": 1, "total_price": 45, "average_price": 45}, "platforms": [{"name": "Switch", "sheet_name": "Switch", "games_count": 1, "total_price": 45, "average_price": 45}]}

    def list_column_values(self, platform):
        """Retourne les valeurs distinctes.

        Args:
            platform (str): Plateforme demandee.

        Returns:
            dict[str, list[object]]: Valeurs distinctes.
        """

        return {"Nom du jeu": ["Mario Kart"], "Prix d'achat": [45]}

    def add_game(self, payload):
        """Ajoute un jeu factice.

        Args:
            payload (dict[str, str]): Donnees du jeu.

        Returns:
            dict[str, str]: Jeu ajoute.

        Raises:
            ValueError: Si le nom manque.
        """

        if not payload.get("Nom du jeu"):
            raise ValueError("Le nom du jeu est obligatoire.")
        return {"Plateforme": payload.get("platform"), "Nom du jeu": payload.get("Nom du jeu")}

    def delete_game(self, payload):
        """Supprime un jeu factice.

        Args:
            payload (dict[str, str]): Donnees du jeu.

        Returns:
            dict[str, str]: Jeu supprime.

        Raises:
            ValueError: Si le nom manque.
        """

        if not payload.get("Nom du jeu"):
            raise ValueError("Le nom du jeu est obligatoire.")
        return {"Plateforme": payload.get("platform"), "Nom du jeu": payload.get("Nom du jeu")}

    def update_game(self, payload):
        """Modifie un jeu factice.

        Args:
            payload (dict[str, object]): Donnees de modification.

        Returns:
            dict[str, object]: Jeu modifie.

        Raises:
            ValueError: Si le nom manque.
        """

        updated = payload.get("updated") or {}
        if not updated.get("Nom du jeu"):
            raise ValueError("Nom du jeu est obligatoire.")
        return {"Plateforme": payload.get("platform"), **updated}

    def list_add_game_choices(self, platform=""):
        """Retourne les choix d'ajout factices.

        Args:
            platform (str): Plateforme demandee.

        Returns:
            dict[str, object]: Choix factices.
        """

        return {"platforms": ["Switch", "Xbox"], "values_by_column": {"Plateforme": ["Switch", "Xbox"]}}


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
        return {"page": self._page(criteria), "platforms": [{"id": 1, "name": "Switch", "release_date": "2017-03-03", "manufacturer": "Nintendo", "description": "", "status": "ACTIVE", "total_games": 12}]}

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
                    "nb_games": 25,
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
