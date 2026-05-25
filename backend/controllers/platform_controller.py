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
# Description : controleur HTTP des plateformes de collection jeux video.

from io import BytesIO
from functools import wraps

from flask import Flask, jsonify, request, send_file

from models import CollectionTypes
from services import DatabaseConfiguration, GamesService, LibraryQueryParser, LibraryService


class PlatformController:
    """Enregistre les routes HTTP liees aux plateformes jeux video."""

    PUBLIC_ENDPOINTS = frozenset(
        {
            "count_library_entities",
            "list_library_platforms",
        }
    )

    def __init__(
        self,
        games_service_factory=GamesService,
        library_service_factory=None,
        library_query_parser=None,
    ):
        """Initialise le controleur des plateformes.

        Args:
            games_service_factory (Callable): Fabrique du service metier jeux video.
            library_service_factory (Callable | None): Fabrique du service Bibliotheque.
            library_query_parser (LibraryQueryParser | None): Parseur de requetes Bibliotheque.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.games_service_factory = games_service_factory
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
            "/collections/JeuxVideo/platforms",
            endpoint="list_jeux_video_platforms",
            view_func=self._as_view(self.list_jeux_video_platforms),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/collections/JeuxVideo/platform-image/<path:platform>",
            endpoint="get_jeux_video_platform_image",
            view_func=self._as_view(self.get_jeux_video_platform_image),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/collections/JeuxVideo/column-values",
            endpoint="list_jeux_video_column_values",
            view_func=self._as_view(self.list_jeux_video_column_values),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/collections/JeuxVideo/add-game-choices",
            endpoint="list_jeux_video_add_game_choices",
            view_func=self._as_view(self.list_jeux_video_add_game_choices),
            methods=["GET"],
        )
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
            return jsonify(self._create_library_service().count_entities())
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
            return jsonify(self._create_library_service().list_platforms(criteria))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 503
        except Exception as exc:
            return jsonify({"error": f"Unable to read library platforms: {exc}"}), 500

    def list_jeux_video_platforms(self):
        """Liste les plateformes disponibles dans le fichier ODS.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Plateformes JSON ou erreur JSON.
        """

        try:
            platforms = self._create_games_service().list_platforms()
            return jsonify({"type": CollectionTypes.JeuxVideo.value, "platforms": platforms})
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except Exception as exc:
            return jsonify({"error": f"Unable to read ODS file: {exc}"}), 500

    def get_jeux_video_platform_image(self, platform: str):
        """Retourne l'image embarquee dans l'onglet ODS d'une plateforme.

        Args:
            platform (str): Nom de l'onglet plateforme recherche.

        Returns:
            flask.Response | tuple[flask.Response, int]: Image ou erreur JSON.
        """

        try:
            image_bytes, mime_type, filename = self._create_games_service().get_platform_image(platform)
            response = send_file(
                BytesIO(image_bytes),
                mimetype=mime_type,
                download_name=filename,
                max_age=0,
            )
            response.headers["Cache-Control"] = "no-store, max-age=0"
            return response
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 404
        except Exception as exc:
            return jsonify({"error": f"Unable to read ODS image: {exc}"}), 500

    def list_jeux_video_column_values(self):
        """Liste les valeurs distinctes de chaque colonne pour une plateforme.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Valeurs JSON ou erreur JSON.
        """

        platform = request.args.get("platform", "Playstation").strip() or "Playstation"
        try:
            values = self._create_games_service().list_column_values(platform=platform)
            return jsonify(
                {
                    "type": CollectionTypes.JeuxVideo.value,
                    "platform": platform,
                    "values_by_column": values,
                }
            )
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Sheet '{platform}' not found in ODS file.",
                        "hint": "Use query param ?platform=<sheet_name>.",
                    }
                ),
                400,
            )
        except Exception as exc:
            return jsonify({"error": f"Unable to read ODS file: {exc}"}), 500

    def list_jeux_video_add_game_choices(self):
        """Liste les choix fusionnes pour le formulaire d'ajout.

        Args:
            Aucun.

        Returns:
            flask.Response | tuple[flask.Response, int]: Choix JSON ou erreur JSON.
        """

        platform = request.args.get("platform", "").strip()
        try:
            choices = self._create_games_service().list_add_game_choices(platform=platform)
            return jsonify({"type": CollectionTypes.JeuxVideo.value, **choices})
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": f"Unable to read ODS choices: {exc}"}), 500

    def _create_games_service(self):
        """Construit le service jeux video.

        Args:
            Aucun.

        Returns:
            GamesService: Service metier utilise par les routes.
        """

        return self.games_service_factory()

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
