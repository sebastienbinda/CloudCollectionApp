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

from flask import Flask, jsonify, request

from services import DatabaseConfiguration, LibraryQueryParser, LibraryService


class GameController:
    """Enregistre les routes HTTP liees aux jeux globaux."""

    PUBLIC_ENDPOINTS = frozenset({"list_library_games"})

    def __init__(self, library_service_factory=None, library_query_parser=None):
        """Initialise le controleur des jeux.

        Args:
            library_service_factory (Callable | None): Fabrique du service Bibliotheque.
            library_query_parser (LibraryQueryParser | None): Parseur de requetes Bibliotheque.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.library_service_factory = library_service_factory or self._create_default_library_service
        self.library_query_parser = library_query_parser or LibraryQueryParser()

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
            criteria = self.library_query_parser.parse("games", request.args)
            return jsonify(self._create_library_service().list_games(criteria))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 503
        except Exception as exc:
            return jsonify({"error": f"Unable to read library games: {exc}"}), 500

    def _create_library_service(self):
        """Construit le service Bibliotheque.

        Args:
            Aucun.

        Returns:
            LibraryService: Service metier utilise par les routes Bibliotheque.
        """

        return self.library_service_factory()

    def _create_default_library_service(self):
        """Construit le service Bibliotheque depuis l'environnement.

        Args:
            Aucun.

        Returns:
            LibraryService: Service Bibliotheque configure.
        """

        return LibraryService(DatabaseConfiguration.from_environment())

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
