#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-05
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : service objet listant les routes Flask et leur besoin d'authentification.

from flask import Flask


class RouteDiscoveryService:
    """Construit un catalogue JSON des endpoints exposes par le backend."""

    IGNORED_METHODS = {"HEAD", "OPTIONS"}

    def __init__(self, flask_app: Flask):
        """Initialise le service de decouverte de routes.

        Args:
            flask_app (Flask): Application Flask contenant la table de routage.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.flask_app = flask_app

    def list_routes(self) -> list[dict]:
        """Liste les routes applicatives accessibles par le frontend.

        Args:
            Aucun.

        Returns:
            list[dict]: Routes triees avec chemin, endpoint, methodes et statut d'authentification.
        """

        routes = []
        for rule in self.flask_app.url_map.iter_rules():
            if rule.endpoint == "static":
                continue
            routes.append(self._build_route_entry(rule))
        return sorted(routes, key=lambda route: (route["path"], route["endpoint"]))

    def _build_route_entry(self, rule) -> dict:
        """Construit une entree serialisable pour une route Flask.

        Args:
            rule (werkzeug.routing.Rule): Regle Flask inspectee.

        Returns:
            dict: Description de la route et de ses contraintes d'acces.
        """

        route_handler = self.flask_app.view_functions[rule.endpoint]
        requires_auth = bool(getattr(route_handler, "requires_auth", False))
        required_profiles = list(getattr(route_handler, "required_profiles", []))
        methods = sorted(method for method in rule.methods if method not in self.IGNORED_METHODS)
        return {
            "path": rule.rule,
            "endpoint": rule.endpoint,
            "methods": methods,
            "requires_auth": requires_auth,
            "access": "bearer_token" if requires_auth else "public",
            "auth_schemes": ["Bearer"] if requires_auth else [],
            "required_profiles": required_profiles if requires_auth else [],
        }
