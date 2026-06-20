#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-19
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : controleur HTTP des images de plateformes.

from functools import wraps

from flask import Flask, jsonify, request, send_file

from services import AuthGuard, UserProfile
from services.library.platform_image_service import (
    PlatformImageModerationError,
    PlatformImageNotFoundError,
    PlatformImagePlatformNotFoundError,
    PlatformImageService,
    PlatformImageStorageLimitExceededError,
    PlatformImageUserNotFoundError,
    PlatformImageValidationError,
)


class PlatformImageController:
    """Enregistre les routes HTTP des images de plateformes."""

    PUBLIC_ENDPOINTS = frozenset({"get_library_platform_image"})

    def __init__(self, auth_guard: AuthGuard, platform_image_service_factory=None):
        """Initialise le controleur des images de plateformes.

        Args:
            auth_guard (AuthGuard): Garde d'authentification.
            platform_image_service_factory (Callable | None): Fabrique du service image.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_guard = auth_guard
        self.platform_image_service_factory = (
            platform_image_service_factory or PlatformImageService.from_environment
        )

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes images dans l'application Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/api/library/platforms/images",
            endpoint="list_library_platform_images",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self._as_view(self.list_platform_images)
            ),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/library/platforms/<int:platform_id>/image",
            endpoint="upload_library_platform_image",
            view_func=self.auth_guard.require_profile(UserProfile.USER.value)(
                self._as_view(self.upload_platform_image)
            ),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/library/platforms/<int:platform_id>/image/<int:image_id>",
            endpoint="get_library_platform_image",
            view_func=self._as_view(self.get_platform_image),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/library/platforms/<int:platform_id>/image/<int:image_id>/moderation",
            endpoint="get_library_platform_moderation_image",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self._as_view(self.get_moderation_platform_image)
            ),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/library/platforms/<int:platform_id>/image/<int:image_id>/type/<image_type>",
            endpoint="update_library_platform_image_type",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self._as_view(self.update_platform_image_type)
            ),
            methods=["PUT"],
        )
        flask_app.add_url_rule(
            "/api/library/platforms/<int:platform_id>/image/<int:image_id>/status/<status>",
            endpoint="update_library_platform_image_status",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(
                self._as_view(self.update_platform_image_status)
            ),
            methods=["PUT"],
        )

    def get_public_endpoint_names(self) -> set[str]:
        """Retourne les endpoints publics portes par le controleur.

        Args:
            Aucun.

        Returns:
            set[str]: Noms d'endpoints Flask publics.
        """

        return set(self.PUBLIC_ENDPOINTS)

    def upload_platform_image(self, platform_id: int):
        """Depose une image utilisateur pour une plateforme.

        Args:
            platform_id (int): Identifiant de plateforme.

        Returns:
            tuple[flask.Response, int]: Image creee ou erreur JSON.
        """

        try:
            token_payload = self.auth_guard.get_current_token_payload()
            image = self.platform_image_service_factory().upload_image(
                platform_id,
                request.files.get("image"),
                str(token_payload.get("sub", "")),
            )
            return jsonify({"image": image}), 201
        except PlatformImagePlatformNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except PlatformImageUserNotFoundError as exc:
            return jsonify({"error": str(exc)}), 403
        except PlatformImageStorageLimitExceededError as exc:
            return jsonify({"error": str(exc)}), 503
        except PlatformImageValidationError as exc:
            return jsonify({"error": str(exc)}), 422

    def list_platform_images(self):
        """Liste les images de plateformes a moderer.

        Args:
            Aucun.

        Returns:
            flask.Response: Liste paginee JSON des images.
        """

        return jsonify(self.platform_image_service_factory().list_moderation_images(request.args))

    def get_platform_image(self, platform_id: int, image_id: int):
        """Retourne le contenu d'une image acceptee.

        Args:
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.

        Returns:
            flask.Response | tuple[flask.Response, int]: Image ou erreur JSON.
        """

        try:
            image_file = self.platform_image_service_factory().get_accepted_image_file(
                platform_id,
                image_id,
            )
            return send_file(image_file.path, mimetype=image_file.mimetype, max_age=0)
        except PlatformImageNotFoundError:
            return jsonify({"error": "Library platform image not found."}), 404

    def get_moderation_platform_image(self, platform_id: int, image_id: int):
        """Retourne le contenu protege d'une image a moderer.

        Args:
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.

        Returns:
            flask.Response | tuple[flask.Response, int]: Image ou erreur JSON.
        """

        try:
            image_file = self.platform_image_service_factory().get_moderation_image_file(
                platform_id,
                image_id,
            )
            return send_file(image_file.path, mimetype=image_file.mimetype, max_age=0)
        except PlatformImageNotFoundError:
            return jsonify({"error": "Library platform image not found."}), 404

    def update_platform_image_type(self, platform_id: int, image_id: int, image_type: str):
        """Modifie le type d'une image de plateforme.

        Args:
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.
            image_type (str): Type cible.

        Returns:
            tuple[flask.Response, int]: Image modifiee ou erreur JSON.
        """

        try:
            payload = self.platform_image_service_factory().update_image_type(
                platform_id,
                image_id,
                image_type,
            )
            return jsonify(payload), 200
        except (PlatformImageNotFoundError, PlatformImageModerationError) as exc:
            return jsonify({"error": str(exc)}), 404

    def update_platform_image_status(self, platform_id: int, image_id: int, status: str):
        """Modifie le statut d'une image de plateforme.

        Args:
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.
            status (str): Statut cible.

        Returns:
            tuple[flask.Response, int]: Image modifiee ou erreur JSON.
        """

        try:
            payload = self.platform_image_service_factory().update_image_status(
                platform_id,
                image_id,
                status,
            )
            return jsonify(payload), 200
        except (PlatformImageNotFoundError, PlatformImageModerationError) as exc:
            return jsonify({"error": str(exc)}), 404

    def _as_view(self, route_handler):
        """Transforme une methode liee en fonction Flask annotable.

        Args:
            route_handler (Callable): Methode de controleur appelee par Flask.

        Returns:
            Callable: Fonction de vue compatible Flask.
        """

        @wraps(route_handler)
        def view_function(*args, **kwargs):
            return route_handler(*args, **kwargs)

        return view_function
