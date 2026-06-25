#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : controleur HTTP de gestion proprietaire des partages.

from flask import Flask, current_app, jsonify, request

from services.auth import AuthGuard, UserProfile
from services.collection.collection_share_not_found_error import (
    CollectionShareNotFoundError,
)
from services.collection.collection_share_owner_not_found_error import (
    CollectionShareOwnerNotFoundError,
)


class CollectionShareController:
    """Expose les routes protegees de gestion des partages de collection."""

    def __init__(self, auth_guard: AuthGuard, management_service):
        """Initialise le controleur des partages.

        Args:
            auth_guard (AuthGuard): Garde d'authentification applicatif.
            management_service (object): Service metier de gestion des partages.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_guard = auth_guard
        self.management_service = management_service

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes de partage dans Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        protected_view = self.auth_guard.require_profile(UserProfile.USER.value)
        flask_app.add_url_rule(
            "/api/collection-shares",
            endpoint="create_collection_share",
            view_func=protected_view(self.create_share),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/collection-shares",
            endpoint="list_collection_shares",
            view_func=protected_view(self.list_shares),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/collection-shares/<int:share_id>",
            endpoint="revoke_collection_share",
            view_func=protected_view(self.revoke_share),
            methods=["DELETE"],
        )

    def create_share(self):
        """Cree un partage pour l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Partage cree ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        try:
            share = self.management_service.create_share(
                self._current_subject(),
                payload.get("duration_hours"),
                payload.get("allow_collection"),
                payload.get("allow_wishlist"),
                payload.get("allow_prices"),
            )
            return jsonify({"share": share}), 201
        except ValueError as exc:
            return self._error_response(exc)
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 503
        except Exception:
            current_app.logger.exception("Erreur pendant la creation d'un partage.")
            return jsonify({"error": "Unable to create collection share."}), 500

    def list_shares(self):
        """Liste les partages de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Liste ou erreur JSON.
        """

        try:
            return jsonify({
                "shares": self.management_service.list_shares(self._current_subject()),
            })
        except ValueError as exc:
            return self._error_response(exc)
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 503
        except Exception:
            current_app.logger.exception("Erreur pendant la liste des partages.")
            return jsonify({"error": "Unable to list collection shares."}), 500

    def revoke_share(self, share_id: int):
        """Revoque un partage de l'utilisateur connecte.

        Args:
            share_id (int): Identifiant technique du partage.

        Returns:
            tuple[flask.Response, int] | flask.Response: Partage revoque ou erreur.
        """

        try:
            share = self.management_service.revoke_share(
                self._current_subject(),
                share_id,
            )
            return jsonify({"share": share})
        except ValueError as exc:
            return self._error_response(exc)
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 503
        except Exception:
            current_app.logger.exception("Erreur pendant la revocation d'un partage.")
            return jsonify({"error": "Unable to revoke collection share."}), 500

    def _current_subject(self) -> str:
        payload = self.auth_guard.get_current_token_payload()
        return str(payload.get("sub") or "").strip().lower()

    @staticmethod
    def _error_response(error: ValueError):
        if isinstance(error, (CollectionShareNotFoundError, CollectionShareOwnerNotFoundError)):
            return jsonify({"error": str(error)}), 404
        return jsonify({"error": str(error)}), 400
