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
# Description : controleur HTTP des plateformes de la Bibliotheque publique.

from functools import wraps

from flask import Flask, jsonify, request

from services import DatabaseConfiguration, LibraryQueryParser, LibraryService


class PlatformController:
    """Enregistre les routes HTTP publiques liees aux plateformes."""

    PUBLIC_ENDPOINTS = frozenset(
        {
            "count_library_entities",
            "get_library_platform",
            "list_library_platforms",
        }
    )

    def __init__(
        self,
        library_service_factory=None,
        library_query_parser=None,
    ):
        """Initialise le controleur des plateformes.

        Args:
            library_service_factory (Callable | None): Fabrique du service Bibliotheque.
            library_query_parser (LibraryQueryParser | None): Parseur de requetes Bibliotheque.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self._library_service = None
        self._library_service_factory = None
        self.library_service_factory = library_service_factory or self._create_default_library_service
        self.library_query_parser = library_query_parser or LibraryQueryParser()

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes plateforme dans l'application Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/api/library/entities",
            endpoint="count_library_entities",
            view_func=self._as_view(self.count_library_entities),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/library/platforms",
            endpoint="list_library_platforms",
            view_func=self._as_view(self.list_library_platforms),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/library/platforms/<int:platform_id>",
            endpoint="get_library_platform",
            view_func=self._as_view(self.get_library_platform),
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

    def count_library_entities(self):
        """Retourne les compteurs globaux de la Bibliotheque publique.

        Args:
            Aucun.

        Returns:
            flask.Response | tuple[flask.Response, int]: Compteurs JSON ou erreur JSON.
        """

        try:
            return jsonify(self._get_library_service().count_entities())
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 503
        except Exception as exc:
            return jsonify({"error": f"Unable to read library entities: {exc}"}), 500

    def list_library_platforms(self):
        """Liste les plateformes publiques de la Bibliotheque.

        Args:
            Aucun.

        Returns:
            flask.Response | tuple[flask.Response, int]: Plateformes JSON ou erreur JSON.
        """

        try:
            criteria = self.library_query_parser.parse("platforms", request.args)
            return jsonify(self._get_library_service().list_platforms(criteria))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 503
        except Exception as exc:
            return jsonify({"error": f"Unable to read library platforms: {exc}"}), 500

    def get_library_platform(self, platform_id: int):
        """Retourne le detail public d'une plateforme de la Bibliotheque.

        Args:
            platform_id (int): Identifiant de la plateforme recherchee.

        Returns:
            flask.Response | tuple[flask.Response, int]: Plateforme JSON ou erreur JSON.
        """

        try:
            platform = self._get_library_service().get_platform(platform_id)
            if platform is None:
                return jsonify({"error": "Library platform not found."}), 404
            return jsonify({"platform": platform})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 503
        except Exception as exc:
            return jsonify({"error": f"Unable to read library platform: {exc}"}), 500

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
