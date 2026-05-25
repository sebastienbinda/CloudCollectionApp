#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : controleur HTTP de la liste de souhaits jeux video.

from flask import Flask, jsonify, request

from models import CollectionTypes
from services import AuthGuard, GamesService


class UserWishListController:
    """Enregistre les routes HTTP de gestion de liste de souhaits jeux video."""

    def __init__(self, auth_guard: AuthGuard, games_service_factory=GamesService):
        """Initialise le controleur de liste de souhaits.

        Args:
            auth_guard (AuthGuard): Garde d'authentification des routes protegees.
            games_service_factory (Callable): Fabrique du service metier jeux video.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_guard = auth_guard
        self.games_service_factory = games_service_factory

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes wishlist dans l'application Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/collections/videogames/wishlist/games",
            endpoint="delete_video_games_wishlist_game",
            view_func=self.auth_guard.require_token(self.delete_video_games_wishlist_game),
            methods=["DELETE"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/wishlist/games",
            endpoint="add_video_games_wishlist_game",
            view_func=self.auth_guard.require_token(self.add_video_games_wishlist_game),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/wishlist/games",
            endpoint="update_video_games_wishlist_game",
            view_func=self.auth_guard.require_token(self.update_video_games_wishlist_game),
            methods=["PUT"],
        )

    def delete_video_games_wishlist_game(self):
        """Supprime un jeu dans l'onglet ODS `Liste de souhaits`.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Jeu supprime ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        try:
            item = self._create_games_service().delete_wishlist_game(payload)
            return jsonify({"type": CollectionTypes.VideoGames.value, "item": item})
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500

    def add_video_games_wishlist_game(self):
        """Ajoute un jeu dans l'onglet ODS `Liste de souhaits`.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Jeu ajoute ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        try:
            item = self._create_games_service().add_wishlist_game(payload)
            return jsonify({"type": CollectionTypes.VideoGames.value, "item": item}), 201
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500

    def update_video_games_wishlist_game(self):
        """Modifie un jeu dans l'onglet ODS `Liste de souhaits`.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Jeu modifie ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        try:
            item = self._create_games_service().update_wishlist_game(payload)
            return jsonify({"type": CollectionTypes.VideoGames.value, "item": item})
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500

    def _create_games_service(self):
        """Construit le service jeux video.

        Args:
            Aucun.

        Returns:
            GamesService: Service metier utilise par les routes.
        """

        return self.games_service_factory()
