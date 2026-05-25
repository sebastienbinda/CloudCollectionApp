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
# Description : controleur HTTP de la collection utilisateur de jeux video.

from functools import wraps

from flask import Flask, jsonify, request, send_file

from models import CollectionTypes
from services import AuthGuard, GamesService


class UserGamesCollectionController:
    """Enregistre les routes HTTP de consultation et gestion de collection jeux video."""

    def __init__(self, auth_guard: AuthGuard, games_service_factory=GamesService):
        """Initialise le controleur de collection jeux video.

        Args:
            auth_guard (AuthGuard): Garde d'authentification des routes protegees.
            games_service_factory (Callable): Fabrique du service metier jeux video.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_guard = auth_guard
        self.games_service_factory = games_service_factory

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes de collection dans l'application Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/collections/videogames/search",
            endpoint="search_collection_items",
            view_func=self._as_view(self.search_collection_items),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/home",
            endpoint="get_video_games_home",
            view_func=self._as_view(self.get_video_games_home),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/cache/reset",
            endpoint="reset_video_games_cache",
            view_func=self.auth_guard.require_token(self.reset_video_games_cache),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/download",
            endpoint="download_video_games_ods",
            view_func=self.auth_guard.require_token(self.download_video_games_ods),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/games/search",
            endpoint="search_video_games",
            view_func=self._as_view(self.search_video_games),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/games",
            endpoint="add_video_game",
            view_func=self.auth_guard.require_token(self.add_video_game),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/games",
            endpoint="delete_video_game",
            view_func=self.auth_guard.require_token(self.delete_video_game),
            methods=["DELETE"],
        )
        flask_app.add_url_rule(
            "/collections/videogames/games",
            endpoint="update_video_game",
            view_func=self.auth_guard.require_token(self.update_video_game),
            methods=["PUT"],
        )

    def search_collection_items(self):
        """Recherche des jeux video sur une plateforme ODS.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Liste JSON ou erreur JSON.
        """

        search_query = request.args.get("q", "").strip().lower()
        return self._search_video_games_items(search_query)

    def get_video_games_home(self):
        """Retourne les statistiques de l'onglet `Accueil` du fichier ODS.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Donnees JSON ou erreur JSON.
        """

        try:
            stats = self._create_games_service().get_home_stats()
            return jsonify({"type": CollectionTypes.VideoGames.value, **stats})
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError:
            return jsonify({"error": "Sheet 'Accueil' not found in ODS file."}), 400
        except Exception as exc:
            return jsonify({"error": f"Unable to read ODS file: {exc}"}), 500

    def reset_video_games_cache(self):
        """Vide le cache backend des donnees lues depuis le fichier ODS.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Statut JSON ou erreur JSON.
        """

        try:
            removed_entries = self._create_games_service().reset_cache()
            return jsonify(
                {
                    "type": CollectionTypes.VideoGames.value,
                    "message": "Cache ODS reinitialise.",
                    "removed_entries": removed_entries,
                }
            )
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except Exception as exc:
            return jsonify({"error": f"Unable to reset ODS cache: {exc}"}), 500

    def download_video_games_ods(self):
        """Telecharge le fichier ODS de la collection jeux video.

        Args:
            Aucun.

        Returns:
            flask.Response | tuple[flask.Response, int]: Fichier ODS ou erreur JSON.
        """

        try:
            ods_path, filename = self._create_games_service().get_ods_download()
            return send_file(
                ods_path,
                mimetype="application/vnd.oasis.opendocument.spreadsheet",
                as_attachment=True,
                download_name=filename,
            )
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except Exception as exc:
            return jsonify({"error": f"Unable to download ODS file: {exc}"}), 500

    def search_video_games(self):
        """Recherche un jeu par nom dans toutes les plateformes.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Resultats JSON ou erreur JSON.
        """

        search_query = request.args.get("q", "").strip()
        parsed_limit = self._parse_limit(request.args.get("limit", "50").strip())
        try:
            items = self._create_games_service().search_by_game_name(
                query=search_query,
                limit=parsed_limit,
            )
            return jsonify(
                {
                    "type": CollectionTypes.VideoGames.value,
                    "query": search_query,
                    "count": len(items),
                    "items": items,
                }
            )
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except Exception as exc:
            return jsonify({"error": f"Unable to search ODS file: {exc}"}), 500

    def add_video_game(self):
        """Ajoute un jeu dans l'onglet ODS correspondant a sa plateforme.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Jeu ajoute ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        try:
            item = self._create_games_service().add_game(payload)
            return jsonify({"type": CollectionTypes.VideoGames.value, "item": item}), 201
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500

    def delete_video_game(self):
        """Supprime un jeu dans l'onglet ODS de sa plateforme.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Jeu supprime ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        try:
            item = self._create_games_service().delete_game(payload)
            return jsonify({"type": CollectionTypes.VideoGames.value, "item": item})
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500

    def update_video_game(self):
        """Modifie un jeu dans l'onglet ODS de sa plateforme.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Jeu modifie ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        try:
            item = self._create_games_service().update_game(payload)
            return jsonify({"type": CollectionTypes.VideoGames.value, "item": item})
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500

    def _search_video_games_items(self, search_query: str):
        """Recherche les jeux video sur une plateforme ODS.

        Args:
            search_query (str): Texte de recherche normalise.

        Returns:
            tuple[flask.Response, int] | flask.Response: Resultats JSON ou erreur JSON.
        """

        platform = request.args.get("platform", "Playstation").strip() or "Playstation"
        try:
            items = self._create_games_service().search(platform=platform, query=search_query)
            return jsonify(items)
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

    def _parse_limit(self, raw_limit: str) -> int:
        """Decode la limite de resultats de recherche.

        Args:
            raw_limit (str): Valeur brute recue depuis la query string.

        Returns:
            int: Limite bornee entre 1 et 100.
        """

        try:
            return max(1, min(int(raw_limit), 100))
        except ValueError:
            return 50

    def _create_games_service(self):
        """Construit le service jeux video.

        Args:
            Aucun.

        Returns:
            GamesService: Service metier utilise par les routes.
        """

        return self.games_service_factory()

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
