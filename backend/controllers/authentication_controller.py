#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-21
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : controleur HTTP d'authentification, inscription et validation email.

from flask import Flask, current_app, jsonify, request

from services import (
    AuthTokenService,
    DatabaseConfiguration,
    DuplicateUserEmailError,
    EmailConfiguration,
    EmailSenderFactory,
    EmailVerificationService,
    InvalidEmailVerificationTokenError,
    PasswordPolicyError,
    SqlAlchemyUserRepository,
    UserRegistrationService,
)


class AuthenticationController:
    """Enregistre les routes HTTP publiques d'authentification et d'inscription."""

    PUBLIC_ENDPOINTS = frozenset(
        {
            "issue_auth_token",
            "register_user",
            "verify_user_email",
        }
    )

    def __init__(
        self,
        auth_token_service: AuthTokenService,
        user_repository_class=SqlAlchemyUserRepository,
        user_registration_service_class=UserRegistrationService,
        email_sender_factory=EmailSenderFactory,
        email_configuration_class=EmailConfiguration,
        database_configuration_class=DatabaseConfiguration,
        email_verification_service_class=EmailVerificationService,
    ):
        """Initialise le controleur et ses dependances metier.

        Args:
            auth_token_service (AuthTokenService): Service d'emission des tokens Bearer.
            user_repository_class (type): Classe de persistance des utilisateurs.
            user_registration_service_class (type): Classe de service d'inscription.
            email_sender_factory (type): Fabrique d'expediteurs email.
            email_configuration_class (type): Classe de configuration email.
            database_configuration_class (type): Classe de configuration base de donnees.
            email_verification_service_class (type): Classe de service de validation email.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_token_service = auth_token_service
        self.user_repository_class = user_repository_class
        self.user_registration_service_class = user_registration_service_class
        self.email_sender_factory = email_sender_factory
        self.email_configuration_class = email_configuration_class
        self.database_configuration_class = database_configuration_class
        self.email_verification_service_class = email_verification_service_class

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes du controleur dans l'application Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/auth/token",
            endpoint="issue_auth_token",
            view_func=self.issue_auth_token,
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/auth/register",
            endpoint="register_user",
            view_func=self.register_user,
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/auth/verify-email",
            endpoint="verify_user_email",
            view_func=self.verify_user_email,
            methods=["GET", "POST"],
        )

    def get_public_endpoint_names(self) -> set[str]:
        """Retourne les endpoints publics portes par le controleur.

        Args:
            Aucun.

        Returns:
            set[str]: Noms d'endpoints Flask a exclure de la protection Bearer globale.
        """

        return set(self.PUBLIC_ENDPOINTS)

    def issue_auth_token(self):
        """Retourne un token Bearer compatible OAuth2 pour les routes protegees.

        Args:
            Aucun.

        Form or JSON Body:
            username (str): Identifiant backend, ou `client_id` en flux client credentials.
            password (str): Mot de passe backend, ou `client_secret` en flux client credentials.

        Returns:
            tuple[flask.Response, int] | flask.Response: Token OAuth2 ou erreur JSON 401.
        """

        payload = request.get_json(silent=True) or request.form
        username = payload.get("username") or payload.get("client_id") or ""
        password = payload.get("password") or payload.get("client_secret") or ""
        try:
            token_response = self.auth_token_service.issue_token(username, password)
            return jsonify(token_response)
        except ValueError as exc:
            return (
                jsonify({"error": str(exc)}),
                401,
                {"WWW-Authenticate": 'Bearer realm="CloudCollectionApp"'},
            )

    def register_user(self):
        """Enregistre un nouvel utilisateur applicatif public.

        Args:
            Aucun.

        JSON Body:
            email (str): Adresse email du compte a creer.
            password (str): Mot de passe brut a hacher avant stockage.

        Returns:
            tuple[flask.Response, int]: Donnees publiques utilisateur ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        email = payload.get("email", "")
        password = payload.get("password", "")
        current_app.logger.info("Demande d'inscription utilisateur recue.")
        try:
            user_repository = self._create_user_repository()
            email_verification_service = self._create_email_verification_service(user_repository)
            registration_service = self.user_registration_service_class(
                user_repository,
                email_verification_service,
            )
            registered_user = registration_service.register_user(email=email, password=password)
            current_app.logger.info("Utilisateur inscrit avec succes: id=%s.", registered_user.id)
            return jsonify({"user": registered_user.to_public_dict()}), 201
        except DuplicateUserEmailError as exc:
            current_app.logger.warning("Inscription refusee: email deja utilise.")
            return jsonify({"error": str(exc)}), 409
        except PasswordPolicyError as exc:
            current_app.logger.warning("Inscription refusee: regles de mot de passe non respectees.")
            return jsonify({"error": str(exc)}), 400
        except ValueError as exc:
            current_app.logger.warning("Inscription refusee: %s", str(exc))
            if "DATABASE_URL" in str(exc):
                return jsonify({"error": str(exc)}), 503
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant l'inscription utilisateur.")
            return jsonify({"error": "Unable to register user."}), 500

    def verify_user_email(self):
        """Valide l'adresse email d'un utilisateur depuis un token applicatif.

        Args:
            Aucun.

        Query Args:
            token (str): Token de validation transmis dans le lien email.

        JSON Body:
            token (str): Token de validation pour les clients API.

        Returns:
            tuple[flask.Response, int]: Donnees publiques de validation ou erreur JSON.
        """

        payload = request.get_json(silent=True) or {}
        raw_token = request.args.get("token") or payload.get("token") or ""
        current_app.logger.info("Demande de validation email recue.")
        try:
            user_repository = self._create_user_repository()
            email_verification_service = self._create_email_verification_service(user_repository)
            verified_user = email_verification_service.verify_email(raw_token)
            current_app.logger.info("Email utilisateur valide avec succes: id=%s.", verified_user.id)
            return jsonify({"user": verified_user.to_public_dict()})
        except InvalidEmailVerificationTokenError as exc:
            current_app.logger.warning("Validation email refusee: token invalide ou expire.")
            return jsonify({"error": str(exc)}), 400
        except ValueError as exc:
            current_app.logger.warning("Validation email refusee: %s", str(exc))
            if "DATABASE_URL" in str(exc):
                return jsonify({"error": str(exc)}), 503
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant la validation email.")
            return jsonify({"error": "Unable to verify email."}), 500

    def _create_user_repository(self):
        """Cree le repository utilisateur configure.

        Args:
            Aucun.

        Returns:
            object: Repository utilisateur SQLAlchemy.
        """

        configuration = self.database_configuration_class.from_environment()
        return self.user_repository_class(configuration)

    def _create_email_verification_service(self, user_repository):
        """Cree le service de validation email configure.

        Args:
            user_repository (object): Repository utilisateur partage avec l'inscription.

        Returns:
            EmailVerificationService: Service pret a valider ou envoyer les emails.
        """

        email_sender = self.email_sender_factory.create(
            self.email_configuration_class.from_environment()
        )
        return self.email_verification_service_class(user_repository, email_sender)
