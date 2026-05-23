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
# Description : controleur HTTP du catalogue des routes backend.

from functools import wraps

from flask import Flask, current_app, jsonify

from services import RouteDiscoveryService


class RouteController:
    """Enregistre les routes HTTP de decouverte du backend."""

    def __init__(self, route_discovery_service_class=RouteDiscoveryService):
        """Initialise le controleur de decouverte des routes.

        Args:
            route_discovery_service_class (type): Classe de service listant les routes Flask.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.route_discovery_service_class = route_discovery_service_class

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes de decouverte dans l'application Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/api/routes",
            endpoint="list_accessible_routes",
            view_func=self._as_view(self.list_accessible_routes),
            methods=["GET"],
        )

    def list_accessible_routes(self):
        """Liste les routes backend et indique celles qui exigent un token.

        Args:
            Aucun.

        Returns:
            flask.Response: Reponse JSON contenant `routes` (list[dict]).
        """

        routes = self.route_discovery_service_class(current_app).list_routes()
        return jsonify({"routes": routes})

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
