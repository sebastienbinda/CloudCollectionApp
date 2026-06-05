#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-22
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : controleur HTTP de gestion administrative des utilisateurs.

from datetime import datetime

from flask import Flask, current_app, jsonify, request

from services import (
    AuthGuard,
    DatabaseConfiguration,
    EmailConfiguration,
    EmailSenderFactory,
    SqlAlchemyUserRepository,
    UserManagementService,
    UserNotFoundError,
    UserProfile,
    UserSearchCriteria,
)


class UserController:
    """Enregistre les routes HTTP d'administration des utilisateurs."""

    def __init__(
        self,
        auth_guard: AuthGuard,
        user_repository_class=SqlAlchemyUserRepository,
        user_management_service_class=UserManagementService,
        database_configuration_class=DatabaseConfiguration,
        email_sender_factory=EmailSenderFactory,
        email_configuration_class=EmailConfiguration,
    ):
        """Initialise le controleur utilisateur et ses dependances.

        Args:
            auth_guard (AuthGuard): Garde d'authentification et de profil.
            user_repository_class (type): Classe de persistance des utilisateurs.
            user_management_service_class (type): Classe de service de gestion utilisateur.
            database_configuration_class (type): Classe de configuration base de donnees.
            email_sender_factory (type): Fabrique d'expediteurs email.
            email_configuration_class (type): Classe de configuration email.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_guard = auth_guard
        self.user_repository_class = user_repository_class
        self.user_management_service_class = user_management_service_class
        self.database_configuration_class = database_configuration_class
        self.email_sender_factory = email_sender_factory
        self.email_configuration_class = email_configuration_class

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes utilisateur dans l'application Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/api/users",
            endpoint="search_users",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(self.search_users),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/users/<int:user_id>",
            endpoint="delete_user",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(self.delete_user),
            methods=["DELETE"],
        )
        flask_app.add_url_rule(
            "/api/users/<int:user_id>/lock",
            endpoint="lock_user",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(self.lock_user),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/users/<int:user_id>/unlock",
            endpoint="unlock_user",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(self.unlock_user),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/users/<int:user_id>/validate",
            endpoint="validate_user",
            view_func=self.auth_guard.require_profile(UserProfile.ADMIN.value)(self.validate_user),
            methods=["POST"],
        )

    def search_users(self):
        """Recherche les utilisateurs selon les criteres de requete.

        Args:
            Aucun.

        Query Args:
            name (str): Portion d'email ou de nom de connexion.
            creation_date_from (str): Date ISO minimale de creation.
            creation_date_to (str): Date ISO maximale de creation.
            last_connexion_date_from (str): Date ISO minimale de derniere connexion.
            last_connexion_date_to (str): Date ISO maximale de derniere connexion.
            status (str): Statut exact, par exemple `ACTIVE`, `WAITING_VALIDATION` ou `LOCKED`.

        Returns:
            tuple[flask.Response, int] | flask.Response: Liste JSON des utilisateurs ou erreur.
        """

        try:
            criteria = self._build_search_criteria()
            users = self._create_user_management_service().search_users(criteria)
            return jsonify({"users": [user.to_dict() for user in users]})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant la recherche utilisateur.")
            return jsonify({"error": "Unable to search users."}), 500

    def delete_user(self, user_id: int):
        """Supprime un utilisateur.

        Args:
            user_id (int): Identifiant technique du compte a supprimer.

        Returns:
            tuple[flask.Response, int] | flask.Response: Reponse vide 204 ou erreur JSON.
        """

        try:
            self._create_user_management_service().delete_user(user_id)
            return "", 204
        except UserNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant la suppression utilisateur.")
            return jsonify({"error": "Unable to delete user."}), 500

    def lock_user(self, user_id: int):
        """Bloque un utilisateur.

        Args:
            user_id (int): Identifiant technique du compte a bloquer.

        Returns:
            tuple[flask.Response, int] | flask.Response: Utilisateur bloque ou erreur JSON.
        """

        try:
            user = self._create_user_management_service().lock_user(user_id)
            return jsonify({"user": user.to_dict()})
        except UserNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant le blocage utilisateur.")
            return jsonify({"error": "Unable to lock user."}), 500

    def unlock_user(self, user_id: int):
        """Debloque un utilisateur.

        Args:
            user_id (int): Identifiant technique du compte a debloquer.

        Returns:
            tuple[flask.Response, int] | flask.Response: Utilisateur debloque ou erreur JSON.
        """

        try:
            user = self._create_user_management_service().unlock_user(user_id)
            return jsonify({"user": user.to_dict()})
        except UserNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant le deblocage utilisateur.")
            return jsonify({"error": "Unable to unlock user."}), 500

    def validate_user(self, user_id: int):
        """Valide un utilisateur en attente.

        Args:
            user_id (int): Identifiant technique du compte a valider.

        Returns:
            tuple[flask.Response, int] | flask.Response: Utilisateur active ou erreur JSON.
        """

        try:
            user = self._create_user_management_service(
                activation_email_sender=self._create_activation_email_sender()
            ).validate_user(user_id)
            return jsonify({"user": user.to_dict()})
        except UserNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant la validation utilisateur.")
            return jsonify({"error": "Unable to validate user."}), 500

    def _build_search_criteria(self) -> UserSearchCriteria:
        """Construit les criteres de recherche depuis la requete HTTP.

        Args:
            Aucun.

        Returns:
            UserSearchCriteria: Criteres normalises.

        Raises:
            ValueError: Si une date de filtre est invalide.
        """

        return UserSearchCriteria(
            name=request.args.get("name", "").strip(),
            creation_date_from=self._parse_optional_datetime("creation_date_from"),
            creation_date_to=self._parse_optional_datetime("creation_date_to"),
            last_connexion_date_from=self._parse_optional_datetime("last_connexion_date_from"),
            last_connexion_date_to=self._parse_optional_datetime("last_connexion_date_to"),
            status=request.args.get("status", "").strip().upper(),
        )

    def _parse_optional_datetime(self, query_parameter_name: str) -> datetime | None:
        """Decode une date ISO optionnelle depuis la requete.

        Args:
            query_parameter_name (str): Nom du parametre de requete.

        Returns:
            datetime | None: Date decodee, ou `None` si absente.

        Raises:
            ValueError: Si la date n'est pas au format ISO accepte.
        """

        raw_value = request.args.get(query_parameter_name, "").strip()
        if not raw_value:
            return None
        try:
            return datetime.fromisoformat(raw_value)
        except ValueError as exc:
            raise ValueError(f"Le parametre {query_parameter_name} doit etre une date ISO.") from exc

    def _create_user_management_service(
        self,
        activation_email_sender=None,
    ) -> UserManagementService:
        """Construit le service de gestion utilisateur.

        Args:
            activation_email_sender (object | None): Expediteur email optionnel.

        Returns:
            UserManagementService: Service initialise avec le repository SQL.
        """

        return self.user_management_service_class(
            self._create_user_repository(),
            activation_email_sender,
        )

    def _create_activation_email_sender(self):
        """Construit l'expediteur email d'activation.

        Args:
            Aucun.

        Returns:
            object: Expediteur email configure.
        """

        return self.email_sender_factory.create(
            self.email_configuration_class.from_environment()
        )

    def _create_user_repository(self):
        """Construit le repository utilisateur SQL.

        Args:
            Aucun.

        Returns:
            SqlAlchemyUserRepository: Repository configure depuis l'environnement.

        Raises:
            ValueError: Si la base de donnees n'est pas configuree.
        """

        return self.user_repository_class(self.database_configuration_class.from_environment())
