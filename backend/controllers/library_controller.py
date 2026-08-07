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

from pathlib import Path
from tempfile import NamedTemporaryFile

from flask import Flask, current_app, jsonify, request

from services import AuthGuard, UserProfile
from services.database.platform_catalog_update_service import PlatformCatalogUpdateService
from services.library import LibraryResetAlreadyRunningError, LibraryResetJobCoordinator
from services.library import (
    GameDuplicateError,
    GameDuplicateNotFoundError,
    GameDuplicateService,
    GameValidationError,
    GameValidationService,
)
from services.library.admin_library_import_service import (
    AdminLibraryImportInvalidFileError,
    AdminLibraryImportService,
)
from services.library.library_reset_service import LibraryResetService


class LibraryController:
    """Enregistre les routes HTTP admin liees a la Bibliotheque."""

    def __init__(
        self,
        auth_guard: AuthGuard,
        reset_job_coordinator: LibraryResetJobCoordinator | None = None,
        reset_service_factory=None,
        platform_catalog_update_service_factory=None,
        admin_import_service_factory=None,
        duplicate_service_factory=None,
        game_validation_service_factory=None,
        library_service_provider=None,
    ):
        """Initialise le controleur admin Bibliotheque.

        Args:
            auth_guard (AuthGuard): Garde d'authentification et de profil.
            reset_job_coordinator (LibraryResetJobCoordinator | None): Coordinateur de reset.
            reset_service_factory (Callable | None): Fabrique du service de reset.
            platform_catalog_update_service_factory (Callable | None): Fabrique du service
                d'actualisation des plateformes.
            admin_import_service_factory (Callable | None): Fabrique du service d'import CSV
                admin Bibliotheque.
            duplicate_service_factory (Callable | None): Fabrique du service doublons.
            game_validation_service_factory (Callable | None): Fabrique du service de moderation
                des jeux.
            library_service_provider (LibraryServiceProvider | None): Cache de services
                Bibliotheque a invalider apres actualisation.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_guard = auth_guard
        self.reset_job_coordinator = reset_job_coordinator or LibraryResetJobCoordinator()
        self.reset_service_factory = reset_service_factory or LibraryResetService.from_environment
        self.platform_catalog_update_service_factory = (
            platform_catalog_update_service_factory
            or PlatformCatalogUpdateService.from_environment
        )
        self.admin_import_service_factory = (
            admin_import_service_factory
            or AdminLibraryImportService.from_environment
        )
        self.duplicate_service_factory = duplicate_service_factory or GameDuplicateService.from_environment
        self.game_validation_service_factory = (
            game_validation_service_factory or GameValidationService.from_environment
        )
        self.library_service_provider = library_service_provider

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
        flask_app.add_url_rule(
            "/api/library/platform-catalog/sync",
            endpoint="sync_platform_catalog",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self.sync_platform_catalog
            ),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/library/import/csv",
            endpoint="import_library_csv",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self.import_library_csv
            ),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/library/games/<int:game_id>/doublon",
            endpoint="get_library_game_duplicate_admin",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self.get_library_game_duplicate_admin
            ),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/library/games/<int:game_id>/doublon/candidates",
            endpoint="list_library_game_duplicate_candidates",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self.list_library_game_duplicate_candidates
            ),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/library/games/doublon",
            endpoint="manage_library_game_duplicate",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self.manage_library_game_duplicate
            ),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/library/games/validation",
            endpoint="validate_library_games",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self.validate_library_games
            ),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/library/games/validation/summary",
            endpoint="get_library_game_validation_summary",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self.get_library_game_validation_summary
            ),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/library/games/refusal",
            endpoint="refuse_library_games",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self.refuse_library_games
            ),
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

    def sync_platform_catalog(self):
        """Actualise le catalogue plateformes depuis les ressources CSV.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Compteurs d'insertions ou erreur JSON.
        """

        try:
            result = self.platform_catalog_update_service_factory().update_from_resources()
            self._reset_library_service_provider()
            return jsonify(result.to_dict()), 200
        except Exception:
            current_app.logger.exception(
                "Erreur inattendue pendant l'actualisation du catalogue plateformes."
            )
            return jsonify({"error": "Unable to sync platform catalog."}), 500

    def import_library_csv(self):
        """Importe un CSV admin dans la Bibliotheque globale.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Compteurs d'import ou erreur JSON.
        """

        uploaded_file = request.files.get("library_file")
        if uploaded_file is None or not uploaded_file.filename:
            return jsonify({"error": "library_file est requis."}), 400

        temporary_path = ""
        try:
            suffix = Path(uploaded_file.filename).suffix or ".csv"
            with NamedTemporaryFile(delete=False, suffix=suffix) as temporary_file:
                uploaded_file.save(temporary_file)
                temporary_path = temporary_file.name
            result = self.admin_import_service_factory().import_csv_file(
                temporary_path,
                uploaded_file.filename,
                requester_email=self._current_requester_email(),
            )
            self._reset_library_service_provider()
            return jsonify(result.to_dict()), 201
        except AdminLibraryImportInvalidFileError as exc:
            return jsonify({"error": "Fichier CSV admin invalide.", "details": exc.details}), 400
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant l'import CSV admin.")
            return jsonify({"error": "Unable to import admin CSV."}), 500
        finally:
            self._delete_temporary_file(temporary_path)

    def get_library_game_duplicate_admin(self, game_id: int):
        """Retourne le jeu signale pour l'ecran admin de correction.

        Args:
            game_id (int): Identifiant du jeu signale.

        Returns:
            tuple[flask.Response, int]: Jeu JSON ou erreur JSON.
        """

        try:
            return jsonify({"game": self.duplicate_service_factory().get_duplicate_game(game_id)}), 200
        except GameDuplicateNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except Exception:
            current_app.logger.exception("Erreur pendant la lecture admin doublon jeu.")
            return jsonify({"error": "Unable to read duplicate game."}), 500

    def list_library_game_duplicate_candidates(self, game_id: int):
        """Liste les candidats de fusion admin pour un doublon.

        Args:
            game_id (int): Identifiant du jeu signale.

        Returns:
            tuple[flask.Response, int]: Candidats JSON ou erreur JSON.
        """

        try:
            candidates = self.duplicate_service_factory().search_candidates(
                game_id,
                request.args.get("name", ""),
                int(request.args.get("limit", "50")),
            )
            return jsonify({"candidates": candidates}), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur pendant la recherche candidats doublon.")
            return jsonify({"error": "Unable to search duplicate candidates."}), 500

    def manage_library_game_duplicate(self):
        """Execute une correction admin de doublon de jeu.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Resultat JSON ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        try:
            action = str(payload.get("action") or "").strip().lower()
            duplicate_game_id = int(payload.get("duplicate_game_id"))
            duplicate_service = self.duplicate_service_factory()
            if action == "reject":
                result = duplicate_service.reject_duplicate(duplicate_game_id)
            elif action == "merge":
                result = duplicate_service.merge_duplicate(
                    duplicate_game_id,
                    int(payload.get("target_game_id")),
                    payload.get("selected_values") or {},
                    bool(payload.get("keep_duplicate_name_as_alias", True)),
                ).to_dict()
            else:
                return jsonify({"error": "Action doublon inconnue."}), 400
            self._reset_library_service_provider()
            return jsonify({"result": result}), 200
        except GameDuplicateNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except (TypeError, ValueError, GameDuplicateError) as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur pendant la correction admin doublon.")
            return jsonify({"error": "Unable to manage duplicate game."}), 500

    def validate_library_games(self):
        """Valide des jeux en attente dans la Bibliotheque.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Compteurs JSON ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        try:
            result = self.game_validation_service_factory().accept_games(
                payload.get("game_ids"),
            )
            self._reset_library_service_provider()
            return jsonify({"result": result.to_dict("validated_count")}), 200
        except GameValidationError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur pendant la validation admin de jeux.")
            return jsonify({"error": "Unable to validate games."}), 500

    def get_library_game_validation_summary(self):
        """Retourne le resume admin des jeux en attente de validation.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Resume JSON ou erreur JSON.
        """

        try:
            summary = self.game_validation_service_factory().get_summary()
            return jsonify({"summary": summary}), 200
        except Exception:
            current_app.logger.exception("Erreur pendant le resume admin validation jeux.")
            return jsonify({"error": "Unable to read game validation summary."}), 500

    def refuse_library_games(self):
        """Refuse des jeux en attente dans la Bibliotheque.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Compteurs JSON ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        try:
            result = self.game_validation_service_factory().refuse_games(
                payload.get("game_ids"),
            )
            self._reset_library_service_provider()
            return jsonify({"result": result.to_dict("refused_count")}), 200
        except GameValidationError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur pendant le refus admin de jeux.")
            return jsonify({"error": "Unable to refuse games."}), 500

    def _run_reset_job(self, job):
        """Execute le service de reset dans le thread de job.

        Args:
            job (LibraryResetJob): Job lance par le coordinateur.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.reset_service_factory().run_reset(job)

    def _reset_library_service_provider(self) -> None:
        if self.library_service_provider is not None:
            self.library_service_provider.reset()

    def _current_requester_email(self) -> str:
        """Retourne le sujet authentifie de la requete courante.

        Args:
            Aucun.

        Returns:
            str: Email ou sujet du token Bearer courant.
        """

        payload = self.auth_guard.get_current_token_payload()
        return str(payload.get("sub") or "").strip().lower()

    def _delete_temporary_file(self, file_path: str) -> None:
        if not file_path:
            return
        try:
            Path(file_path).unlink()
        except FileNotFoundError:
            return
        except OSError:
            current_app.logger.warning("Impossible de supprimer le CSV temporaire admin.")
