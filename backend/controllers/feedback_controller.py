#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : controleur HTTP des retours beta utilisateurs.

from flask import Flask, current_app, jsonify, request

from services import AuthGuard, UserProfile
from services.feedback import GitHubFeedbackService


class FeedbackController:
    """Expose la route protegee d'envoi de retour beta vers GitHub."""

    def __init__(self, auth_guard: AuthGuard, feedback_service_factory=None):
        """Initialise le controleur des retours.

        Args:
            auth_guard (AuthGuard): Garde d'authentification applicatif.
            feedback_service_factory (Callable | None): Fabrique du service de retour.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_guard = auth_guard
        self.feedback_service_factory = feedback_service_factory or GitHubFeedbackService.from_environment

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre la route de retour beta dans Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/api/feedback",
            endpoint="submit_feedback",
            view_func=self.auth_guard.require_profile(UserProfile.USER.value)(self.submit_feedback),
            methods=["POST"],
        )

    def submit_feedback(self):
        """Cree une issue GitHub depuis un retour utilisateur connecte.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Issue creee ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict):
            return jsonify({"error": "Le format du retour est invalide."}), 400

        requester_subject = str(
            self.auth_guard.get_current_token_payload().get("sub") or ""
        ).strip().lower()
        try:
            feedback = self.feedback_service_factory().submit_feedback(payload, requester_subject)
            return jsonify({"feedback": feedback}), 201
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 503
        except Exception:
            current_app.logger.exception("Erreur pendant l'envoi d'un retour beta.")
            return jsonify({"error": "Unable to send feedback."}), 500
