#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : controleur HTTP d'aide a la correction d'import.

from flask import Flask, jsonify, request

from services import AuthGuard, UserProfile
from services.collection.imports import CollectionImportInvalidValueHelpService


class UserCollectionImportHelpController:
    """Enregistre les routes d'aide liees aux erreurs d'import utilisateur."""

    def __init__(
        self,
        auth_guard: AuthGuard,
        invalid_value_help_service_class=CollectionImportInvalidValueHelpService,
    ):
        """Initialise le controleur d'aide d'import.

        Args:
            auth_guard (AuthGuard): Garde d'authentification et de profil.
            invalid_value_help_service_class (type): Classe d'aide sur les valeurs refusees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_guard = auth_guard
        self.invalid_value_help_service_class = invalid_value_help_service_class

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes d'aide de collection utilisateur dans Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/api/users/import/invalid-value-help",
            endpoint="get_import_invalid_value_help",
            view_func=self.auth_guard.require_profile(UserProfile.USER.value)(
                self.get_import_invalid_value_help
            ),
            methods=["GET"],
        )

    def get_import_invalid_value_help(self):
        """Retourne l'aide de correction d'une valeur d'import refusee.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Aide JSON ou erreur.
        """

        field = str(request.args.get("field") or "").strip()
        value = str(request.args.get("value") or "").strip()
        if not field:
            return jsonify({"error": "Le parametre field est requis."}), 400
        help_result = self.invalid_value_help_service_class().get_help(field, value)
        return jsonify(help_result.to_dict()), 200
