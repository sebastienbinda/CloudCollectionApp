#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : controleur HTTP des actions admin Bibliotheque.

from flask import Flask, current_app, jsonify

from services import AuthGuard, UserProfile
from services.library import LibraryResetAlreadyRunningError, LibraryResetJobCoordinator
from services.library.library_reset_service import LibraryResetService


class LibraryController:
    """Enregistre les routes HTTP admin liees a la Bibliotheque."""

    def __init__(
        self,
        auth_guard: AuthGuard,
        reset_job_coordinator: LibraryResetJobCoordinator | None = None,
        reset_service_factory=None,
    ):
        """Initialise le controleur admin Bibliotheque.

        Args:
            auth_guard (AuthGuard): Garde d'authentification et de profil.
            reset_job_coordinator (LibraryResetJobCoordinator | None): Coordinateur de reset.
            reset_service_factory (Callable | None): Fabrique du service de reset.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_guard = auth_guard
        self.reset_job_coordinator = reset_job_coordinator or LibraryResetJobCoordinator()
        self.reset_service_factory = reset_service_factory or LibraryResetService.from_environment

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes admin Bibliotheque dans Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/api/library/reset",
            endpoint="reset_library",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(self.reset_library),
            methods=["POST"],
        )

    def reset_library(self):
        """Lance un job asynchrone de reset Bibliotheque.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Identifiant du job ou erreur JSON.
        """

        try:
            job = self.reset_job_coordinator.start_reset(self._run_reset_job)
            return jsonify({"job_id": job.job_id}), 202
        except LibraryResetAlreadyRunningError:
            return jsonify({"error": "Un reset de la Bibliotheque est deja en cours."}), 409
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant le lancement du reset Bibliotheque.")
            return jsonify({"error": "Unable to start library reset."}), 500

    def _run_reset_job(self, job):
        """Execute le service de reset dans le thread de job.

        Args:
            job (LibraryResetJob): Job lance par le coordinateur.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.reset_service_factory().run_reset(job)
