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
# Description : controleur HTTP des jeux de la Bibliotheque publique.

from functools import wraps

from flask import Flask, current_app, jsonify, request

from services import (
    AuthGuard,
    DatabaseConfiguration,
    GameDuplicateNotFoundError,
    GameDuplicatePermissionError,
    GameDuplicateService,
    LibraryQueryParser,
    LibraryService,
    SqlAlchemyUserRepository,
    UserProfile,
)
from services.auth import ExpiredAccessTokenError


class GameController:
    """Enregistre les routes HTTP liees aux jeux globaux."""

    PUBLIC_ENDPOINTS = frozenset({"get_library_game", "list_library_games"})

    def __init__(
        self,
        auth_guard: AuthGuard | None = None,
        library_service_factory=None,
        library_query_parser=None,
        duplicate_service_factory=None,
        user_repository_class=SqlAlchemyUserRepository,
        database_configuration_class=DatabaseConfiguration,
    ):
        """Initialise le controleur des jeux.

        Args:
            auth_guard (AuthGuard | None): Garde d'authentification des actions protegees.
            library_service_factory (Callable | None): Fabrique du service Bibliotheque.
            library_query_parser (LibraryQueryParser | None): Parseur de requetes Bibliotheque.
            duplicate_service_factory (Callable | None): Fabrique du service doublons.
            user_repository_class (type): Classe de repository utilisateur.
            database_configuration_class (type): Classe de configuration base.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self._library_service = None
        self._library_service_factory = None
        self.auth_guard = auth_guard
        self.library_service_factory = library_service_factory or self._create_default_library_service
        self.library_query_parser = library_query_parser or LibraryQueryParser()
        self.duplicate_service_factory = duplicate_service_factory or GameDuplicateService.from_environment
        self.user_repository_class = user_repository_class
        self.database_configuration_class = database_configuration_class

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes jeux dans l'application Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/api/library/games",
            endpoint="list_library_games",
            view_func=self._as_view(self.list_library_games),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/library/games/<int:game_id>",
            endpoint="get_library_game",
            view_func=self._as_view(self.get_library_game),
            methods=["GET"],
        )
        if self.auth_guard is not None:
            flask_app.add_url_rule(
                "/api/library/games/<int:game_id>/doublon",
                endpoint="report_library_game_duplicate",
                view_func=self.auth_guard.require_profile(UserProfile.USER.value)(
                    self.report_library_game_duplicate
                ),
                methods=["POST"],
            )

    def get_public_endpoint_names(self) -> set[str]:
        """Retourne les endpoints publics portes par le controleur.

        Args:
            Aucun.

        Returns:
            set[str]: Noms d'endpoints Flask publics.
        """

        return set(self.PUBLIC_ENDPOINTS)

    def list_library_games(self):
        """Liste les jeux publics de la Bibliotheque.

        Args:
            Aucun.

        Returns:
            flask.Response | tuple[flask.Response, int]: Jeux JSON ou erreur JSON.
        """

        try:
            requester_profile, current_user_id = self._optional_request_context()
        except ExpiredAccessTokenError as exc:
            return jsonify({"error": str(exc)}), 401
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 401

        try:
            criteria = self.library_query_parser.parse(
                "games",
                request.args,
                current_user_id=current_user_id,
                requester_profile=requester_profile,
            )
            return jsonify(self._get_library_service().list_games(criteria))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 503
        except Exception as exc:
            return jsonify({"error": f"Unable to read library games: {exc}"}), 500

    def get_library_game(self, game_id: int):
        """Retourne le detail public d'un jeu de la Bibliotheque.

        Args:
            game_id (int): Identifiant du jeu recherche.

        Returns:
            flask.Response | tuple[flask.Response, int]: Jeu JSON ou erreur JSON.
        """

        try:
            requester_profile, current_user_id = self._optional_request_context()
        except ExpiredAccessTokenError as exc:
            return jsonify({"error": str(exc)}), 401
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 401

        try:
            game = self._get_library_service().get_game(
                game_id,
                requester_profile=requester_profile,
                current_user_id=current_user_id,
            )
            if game is None:
                return jsonify({"error": "Game not found."}), 404
            return jsonify({"game": game})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 503
        except Exception as exc:
            return jsonify({"error": f"Unable to read library game: {exc}"}), 500

    def report_library_game_duplicate(self, game_id: int):
        """Signale un jeu de la Bibliotheque comme doublon.

        Args:
            game_id (int): Identifiant du jeu signale.

        Returns:
            flask.Response | tuple[flask.Response, int]: Confirmation JSON ou erreur JSON.
        """

        try:
            result = self.duplicate_service_factory().report_duplicate(
                self._current_user_id(),
                game_id,
            )
            return jsonify({
                **result,
                "message": "Merci, un administrateur verifiera ce signalement.",
            }), 200
        except GameDuplicatePermissionError as exc:
            return jsonify({"error": str(exc)}), 403
        except GameDuplicateNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur pendant le signalement de doublon jeu.")
            return jsonify({"error": "Unable to report duplicate game."}), 500

    @property
    def library_service_factory(self):
        """Retourne la fabrique du service Bibliotheque.

        Args:
            Aucun.

        Returns:
            Callable: Fabrique courante du service Bibliotheque.
        """

        return self._library_service_factory

    @library_service_factory.setter
    def library_service_factory(self, factory):
        """Remplace la fabrique du service Bibliotheque et invalide le singleton.

        Args:
            factory (Callable): Fabrique a utiliser pour construire le service.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self._library_service_factory = factory
        self._library_service = None

    def _get_library_service(self):
        """Retourne le singleton de service Bibliotheque du controleur.

        Args:
            Aucun.

        Returns:
            LibraryService: Service metier partage par les routes Bibliotheque.
        """

        if self._library_service is None:
            self._library_service = self.library_service_factory()
        return self._library_service

    def _create_default_library_service(self):
        """Construit le service Bibliotheque depuis l'environnement.

        Args:
            Aucun.

        Returns:
            LibraryService: Service Bibliotheque configure.
        """

        return LibraryService(DatabaseConfiguration.from_environment())

    def _current_user_id(self) -> int:
        """Retourne l'identifiant base de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            int: Identifiant technique utilisateur.

        Raises:
            ValueError: Si le token ne correspond pas a un utilisateur en base.
        """

        if self.auth_guard is None:
            raise ValueError("Authentification indisponible.")
        payload = self.auth_guard.get_current_token_payload()
        user_id = self.user_repository_class(
            self.database_configuration_class.from_environment()
        ).find_user_id_by_email(payload.get("sub"))
        if user_id is None:
            raise ValueError("Utilisateur introuvable.")
        return int(user_id)

    def _optional_request_context(self) -> tuple[str, int | None]:
        """Retourne le profil et l'utilisateur optionnels de la requete publique.

        Args:
            Aucun.

        Returns:
            tuple[str, int | None]: Profil demandeur et identifiant utilisateur optionnel.

        Raises:
            ValueError: Si un Bearer fourni est invalide.
            ExpiredAccessTokenError: Si un Bearer fourni est expire.
        """

        if self.auth_guard is None:
            return "PUBLIC", None
        token = self.auth_guard.extract_bearer_token()
        if not token:
            return "PUBLIC", None
        payload = self.auth_guard.get_current_token_payload()
        requester_profile = UserProfile.normalize(payload.get("profile"))
        if requester_profile is not UserProfile.USER:
            return requester_profile.value, None
        user_id = self.user_repository_class(
            self.database_configuration_class.from_environment()
        ).find_user_id_by_email(payload.get("sub"))
        if user_id is None:
            raise ValueError("Utilisateur introuvable.")
        return requester_profile.value, int(user_id)

    def _as_view(self, route_handler):
        """Transforme une methode liee en fonction Flask annotable.

        Args:
            route_handler (Callable): Methode de controleur appelee par Flask.

        Returns:
            Callable: Fonction de vue compatible avec les annotations d'authentification.
        """

        @wraps(route_handler)
        def view_function(*args, **kwargs):
            return route_handler(*args, **kwargs)

        return view_function
