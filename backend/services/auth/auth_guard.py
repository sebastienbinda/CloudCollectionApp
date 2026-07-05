#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-05
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : garde d'authentification pour proteger les routes Flask mutantes.

from functools import wraps
from typing import Callable

from flask import Flask, current_app, g, jsonify, request

from .auth_token_service import AuthTokenService
from .collection_share_unavailable_error import CollectionShareUnavailableError
from .expired_access_token_error import ExpiredAccessTokenError
from .user_profile import UserProfile


class AuthGuard:
    """Applique la validation Bearer OAuth2 aux endpoints Flask proteges."""

    EXEMPT_METHODS = {"OPTIONS"}
    DEFAULT_REQUIRED_PROFILE = UserProfile.USER.value

    def __init__(self, token_service: AuthTokenService, guest_session_validator=None):
        """Initialise le garde d'authentification.

        Args:
            token_service (AuthTokenService): Service utilise pour valider les tokens.
            guest_session_validator (object | None): Validateur revocable des sessions GUEST.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.token_service = token_service
        self.guest_session_validator = guest_session_validator

    def protect_all_routes(self, flask_app: Flask, exempt_endpoints: set[str] | None = None) -> None:
        """Protege globalement les endpoints Flask avec un token Bearer.

        Args:
            flask_app (Flask): Application Flask dont les routes doivent etre protegees.
            exempt_endpoints (set[str] | None): Noms d'endpoints Flask a laisser publics.

        Returns:
            None: Enregistre un controle avant requete et marque les routes protegees.
        """

        exempt_endpoint_names = exempt_endpoints or set()
        self._mark_protected_routes(flask_app, exempt_endpoint_names)

        @flask_app.before_request
        def require_token_before_request():
            """Valide le token Bearer avant chaque route non exemptee.

            Args:
                Aucun.

            Returns:
                None | tuple: `None` si la requete est autorisee, sinon une erreur JSON.
            """

            if self._is_request_exempt(exempt_endpoint_names):
                return None
            return self.validate_current_request()

    def require_token(self, route_handler: Callable) -> Callable:
        """Retourne un decorateur qui exige un token Bearer valide.

        Args:
            route_handler (Callable): Fonction Flask a proteger.

        Returns:
            Callable: Fonction enveloppee avec verification d'authentification.
        """

        @wraps(route_handler)
        def wrapped_route(*args, **kwargs):
            """Valide le header `Authorization` avant d'appeler la route.

            Args:
                *args (tuple): Arguments positionnels transmis par Flask.
                **kwargs (dict): Arguments nommes transmis par Flask.

            Returns:
                Any: Reponse de la route originale ou erreur JSON 401.
            """

            validation_error = self.validate_current_request()
            if validation_error:
                return validation_error
            return route_handler(*args, **kwargs)

        wrapped_route.requires_auth = True
        wrapped_route.required_profiles = UserProfile.expand_hierarchy(
            self.DEFAULT_REQUIRED_PROFILE,
        )
        return wrapped_route

    def require_profile(self, minimum_profile: str) -> Callable:
        """Retourne un decorateur exigeant un profil minimal.

        Args:
            minimum_profile (str): Profil minimal requis pour la route.

        Returns:
            Callable: Decorateur Flask appliquant le profil minimal.
        """

        def decorator(route_handler: Callable) -> Callable:
            wrapped_route = self.require_token(route_handler)
            wrapped_route.required_profiles = UserProfile.expand_hierarchy(minimum_profile)
            return wrapped_route

        return decorator

    def require_profiles(self, allowed_profiles: list[str] | tuple[str, ...]) -> Callable:
        """Retourne un decorateur autorisant explicitement plusieurs profils.

        Args:
            allowed_profiles (list[str] | tuple[str, ...]): Profils exacts autorises.

        Returns:
            Callable: Decorateur Flask appliquant la liste de profils.
        """

        normalized_profiles = list(dict.fromkeys(
            UserProfile.normalize(profile).value for profile in allowed_profiles
        ))

        def decorator(route_handler: Callable) -> Callable:
            wrapped_route = self.require_token(route_handler)
            wrapped_route.required_profiles = normalized_profiles
            return wrapped_route

        return decorator

    def validate_current_request(self):
        """Valide le header `Authorization` de la requete Flask courante.

        Args:
            Aucun.

        Returns:
            None | tuple: `None` si le token est valide, sinon une reponse d'erreur JSON.
        """

        payload = getattr(g, "auth_token_payload", None)
        if payload is None:
            token = self._extract_bearer_token()
            if not token:
                return self._forbidden_response("Token Bearer manquant.")
            try:
                payload = self.token_service.validate_access_token(token)
                self._validate_guest_session(payload)
            except ExpiredAccessTokenError as exc:
                if UserProfile.normalize(exc.payload.get("profile")) is UserProfile.GUEST:
                    return self._guest_unavailable_response()
                return self._unauthorized_response(str(exc))
            except CollectionShareUnavailableError:
                return self._guest_unavailable_response()
            except ValueError as exc:
                return self._unauthorized_response(str(exc))
            g.auth_token_payload = payload
        if not self._is_profile_allowed(payload.get("profile")):
            return self._forbidden_response("Profil utilisateur insuffisant.")
        return None

    def get_current_token_payload(self) -> dict:
        """Retourne le payload du token Bearer courant.

        Args:
            Aucun.

        Returns:
            dict: Payload du token valide.

        Raises:
            ValueError: Si le token est absent, invalide ou expire.
        """

        cached_payload = getattr(g, "auth_token_payload", None)
        if cached_payload is not None:
            return cached_payload
        token = self._extract_bearer_token()
        if not token:
            raise ValueError("Token Bearer manquant.")
        payload = self.token_service.validate_access_token(token)
        self._validate_guest_session(payload)
        g.auth_token_payload = payload
        return payload

    def _validate_guest_session(self, payload: dict) -> None:
        if UserProfile.normalize(payload.get("profile")) is not UserProfile.GUEST:
            return
        if self.guest_session_validator is None:
            raise ValueError("Session invitee indisponible.")
        self.guest_session_validator.validate_guest_session(payload)

    def _mark_protected_routes(self, flask_app: Flask, exempt_endpoints: set[str]) -> None:
        """Marque les vues Flask protegees pour la decouverte des routes.

        Args:
            flask_app (Flask): Application Flask a inspecter.
            exempt_endpoints (set[str]): Endpoints a laisser sans marque d'authentification.

        Returns:
            None: Modifie les attributs des fonctions de vue.
        """

        for endpoint_name, route_handler in flask_app.view_functions.items():
            if endpoint_name == "static" or endpoint_name in exempt_endpoints:
                continue
            route_handler.requires_auth = True
            if not hasattr(route_handler, "required_profiles"):
                route_handler.required_profiles = UserProfile.expand_hierarchy(
                    self.DEFAULT_REQUIRED_PROFILE,
                )

    def _is_profile_allowed(self, actual_profile: str | None) -> bool:
        """Indique si le profil du token est autorise pour la route courante.

        Args:
            actual_profile (str | None): Profil porte par le token valide.

        Returns:
            bool: `True` si le profil satisfait la route courante.
        """

        endpoint_name = request.endpoint or ""
        if not endpoint_name:
            return False
        handler = current_app.view_functions.get(endpoint_name)
        if handler is None:
            return True
        required_profiles = getattr(
            handler,
            "required_profiles",
            UserProfile.expand_hierarchy(self.DEFAULT_REQUIRED_PROFILE),
        )
        return UserProfile.can_access(actual_profile, required_profiles)

    def _is_request_exempt(self, exempt_endpoints: set[str]) -> bool:
        """Indique si la requete courante doit eviter le controle global.

        Args:
            exempt_endpoints (set[str]): Endpoints Flask autorises sans token.

        Returns:
            bool: `True` pour les preflight CORS, les fichiers statiques ou les endpoints publics.
        """

        if request.method in self.EXEMPT_METHODS:
            return True
        endpoint_name = request.endpoint or ""
        if not endpoint_name:
            return True
        return endpoint_name == "static" or endpoint_name in exempt_endpoints

    def _extract_bearer_token(self) -> str:
        """Extrait le token Bearer depuis l'en-tete HTTP.

        Args:
            Aucun.

        Returns:
            str: Token extrait, ou chaine vide si absent.
        """

        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            return ""
        return token.strip()

    def extract_bearer_token(self) -> str:
        """Retourne le token Bearer brut de la requete courante.

        Args:
            Aucun.

        Returns:
            str: Token extrait, ou chaine vide si aucun Bearer n'est present.
        """

        return self._extract_bearer_token()

    def _unauthorized_response(self, message: str):
        """Construit une reponse HTTP 401 compatible OAuth2 Bearer.

        Args:
            message (str): Message d'erreur a retourner au client.

        Returns:
            tuple[flask.Response, int, dict[str, str]]: Reponse JSON 401 avec challenge Bearer.
        """

        return (
            jsonify({"error": message}),
            401,
            {"WWW-Authenticate": 'Bearer realm="CloudCollectionApp"'},
        )

    def _forbidden_response(self, message: str):
        """Construit une reponse HTTP 403 pour les requetes sans token.

        Args:
            message (str): Message d'erreur a retourner au client.

        Returns:
            tuple[flask.Response, int]: Reponse JSON 403.
        """

        return jsonify({"error": message}), 403

    def _guest_unavailable_response(self):
        """Construit la reponse specifique d'invalidation d'un partage GUEST.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Reponse JSON HTTP 411.
        """

        return jsonify({
            "error": "Partage expire ou revoque.",
            "error_code": "COLLECTION_SHARE_UNAVAILABLE",
        }), 411
