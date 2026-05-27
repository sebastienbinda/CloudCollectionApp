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
# Description : controleur HTTP de consultation SQL de collection utilisateur.

from pathlib import Path

from flask import Flask, current_app, jsonify, request, send_file

from services import AuthGuard, DatabaseConfiguration, SqlAlchemyUserRepository, UserProfile
from services.collection import UserCollectionQueryParser
from services.collection.user_collection_query_service import UserCollectionQueryService


class CollectionController:
    """Enregistre les routes HTTP de collection utilisateur."""

    def __init__(
        self,
        auth_guard: AuthGuard,
        collection_query_service_factory=None,
        collection_query_parser=None,
        user_repository_class=SqlAlchemyUserRepository,
        database_configuration_class=DatabaseConfiguration,
    ):
        """Initialise le controleur de collection.

        Args:
            auth_guard (AuthGuard): Garde d'authentification et de profil.
            collection_query_service_factory (Callable | None): Fabrique du service de lecture SQL.
            collection_query_parser (UserCollectionQueryParser | None): Parseur des criteres.
            user_repository_class (type): Classe de repository utilisateur.
            database_configuration_class (type): Classe de configuration base.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_guard = auth_guard
        self.collection_query_service_factory = (
            collection_query_service_factory or self._create_default_collection_query_service
        )
        self.collection_query_parser = collection_query_parser or UserCollectionQueryParser()
        self.user_repository_class = user_repository_class
        self.database_configuration_class = database_configuration_class

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes de collection dans l'application Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        protected_view = self.auth_guard.require_profile(UserProfile.USER.value)
        flask_app.add_url_rule(
            "/collections/videogames",
            endpoint="get_collection_video_games_statistics",
            view_func=protected_view(self.get_video_games_statistics),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/platforms/search",
            endpoint="search_collection_video_game_platforms",
            view_func=protected_view(self.search_video_game_platforms),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/games/search",
            endpoint="search_collection_video_games",
            view_func=protected_view(self.search_video_games),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/download",
            endpoint="download_collection_video_games_ods",
            view_func=protected_view(self.download_video_games_ods),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/games",
            endpoint="add_collection_video_game",
            view_func=protected_view(self.not_implemented_game_action),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/games",
            endpoint="delete_collection_video_game",
            view_func=protected_view(self.not_implemented_game_action),
            methods=["DELETE"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/games",
            endpoint="update_collection_video_game",
            view_func=protected_view(self.not_implemented_game_action),
            methods=["PUT"],
        )

    def get_video_games_statistics(self):
        """Retourne les statistiques globales de collection.

        Args:
            Aucun.

        Returns:
            flask.Response | tuple[flask.Response, int]: Statistiques JSON ou erreur JSON.
        """

        try:
            return jsonify(self._create_collection_query_service().get_statistics(
                self._current_user_id()
            ))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur pendant la lecture des statistiques collection.")
            return jsonify({"error": "Unable to read collection statistics."}), 500

    def search_video_game_platforms(self):
        """Liste les plateformes de collection de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            flask.Response | tuple[flask.Response, int]: Plateformes JSON ou erreur JSON.
        """

        try:
            criteria = self.collection_query_parser.parse_platforms(request.args)
            return jsonify(self._create_collection_query_service().list_platforms(
                self._current_user_id(),
                criteria,
            ))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur pendant la lecture des plateformes collection.")
            return jsonify({"error": "Unable to read collection platforms."}), 500

    def search_video_games(self):
        """Liste les jeux de collection de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            flask.Response | tuple[flask.Response, int]: Jeux JSON ou erreur JSON.
        """

        try:
            criteria = self.collection_query_parser.parse_games(request.args)
            return jsonify(self._create_collection_query_service().list_games(
                self._current_user_id(),
                criteria,
            ))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur pendant la lecture des jeux collection.")
            return jsonify({"error": "Unable to read collection games."}), 500

    def download_video_games_ods(self):
        """Telecharge le fichier ODS brut de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            flask.Response | tuple[flask.Response, int]: Fichier ODS ou erreur JSON.
        """

        try:
            collection_file_path = self._create_collection_query_service().get_collection_file_path(
                self._current_user_id()
            )
            if not collection_file_path:
                return jsonify({"error": "Collection file not found."}), 404
            resolved_path = Path(collection_file_path)
            if not resolved_path.is_file():
                return jsonify({"error": "Collection file not found."}), 404
            return send_file(
                resolved_path,
                mimetype="application/vnd.oasis.opendocument.spreadsheet",
                as_attachment=True,
                download_name=resolved_path.name,
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur pendant le telechargement collection.")
            return jsonify({"error": "Unable to download collection file."}), 500

    def not_implemented_game_action(self):
        """Retourne le statut des actions jeux prevues pour une evolution future.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Reponse `501 Not Implemented`.
        """

        return jsonify({"error": "Not implemented."}), 501

    def _current_user_id(self) -> int:
        """Retourne l'identifiant base de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            int: Identifiant technique utilisateur.

        Raises:
            ValueError: Si le token ne correspond pas a un utilisateur en base.
        """

        payload = self.auth_guard.get_current_token_payload()
        subject = str(payload.get("sub") or "").strip().lower()
        if not subject:
            raise ValueError("Utilisateur connecte invalide.")
        user_id = self._create_user_repository().find_user_id_by_email(subject)
        if user_id is None:
            raise ValueError("Utilisateur connecte introuvable.")
        return user_id

    def _create_collection_query_service(self):
        """Construit le service de consultation de collection.

        Args:
            Aucun.

        Returns:
            UserCollectionQueryService: Service de consultation configure.
        """

        return self.collection_query_service_factory()

    def _create_default_collection_query_service(self):
        """Construit le service de consultation depuis l'environnement.

        Args:
            Aucun.

        Returns:
            UserCollectionQueryService: Service de consultation configure.
        """

        return UserCollectionQueryService(self.database_configuration_class.from_environment())

    def _create_user_repository(self):
        """Construit le repository utilisateur.

        Args:
            Aucun.

        Returns:
            SqlAlchemyUserRepository: Repository configure.
        """

        return self.user_repository_class(self.database_configuration_class.from_environment())
