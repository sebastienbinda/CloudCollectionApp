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
# Description : service objet de creation et validation des tokens Bearer OAuth2.

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from services.security import EnvSecretCipher

from .password_hash_service import PasswordHashService
from .user_profile import UserProfile


@dataclass(frozen=True)
class AuthenticatedUserCredentials:
    """Represente les informations minimales pour authentifier un utilisateur en base.

    Attributes:
        id (int): Identifiant technique de l'utilisateur.
        email (str): Email normalise utilise comme sujet du token.
        password_hash (str): Empreinte non reversible du mot de passe.
        profile (str): Profil applicatif associe a l'utilisateur.
    """

    id: int
    email: str
    password_hash: str
    profile: str = UserProfile.USER.value


@dataclass(frozen=True)
class AuthenticatedTokenIdentity:
    """Represente l'identite autorisee a recevoir un token.

    Attributes:
        subject (str): Sujet place dans le token.
        profile (str): Profil applicatif place dans le token.
    """

    subject: str
    profile: str


class AuthTokenService:
    """Gere les identifiants backend et les tokens Bearer signes.

    La classe expose un flux compatible OAuth2 simplifie pour obtenir un
    `access_token`, puis valider ce token sur les routes protegees.
    """

    DEFAULT_TOKEN_TTL_SECONDS = 3600

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        secret_key: Optional[str] = None,
        token_ttl_seconds: Optional[int] = None,
        password_hash_service: Optional[PasswordHashService] = None,
    ):
        """Initialise le service d'authentification.

        Args:
            username (Optional[str]): Identifiant autorise, sinon `AUTH_USERNAME`.
            password (Optional[str]): Mot de passe autorise, sinon l'environnement chiffre.
            secret_key (Optional[str]): Cle HMAC, sinon l'environnement chiffre.
            token_ttl_seconds (Optional[int]): Duree de vie du token en secondes.
            password_hash_service (Optional[PasswordHashService]): Service de verification injecte.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.username = username or os.getenv("AUTH_USERNAME", "admin")
        self.password = password or self._read_secret(
            encrypted_env_name="AUTH_PASSWORD_ENCRYPTED",
            plain_env_name="AUTH_PASSWORD",
            default_value="change-me",
        )
        self.secret_key = secret_key or self._read_secret(
            encrypted_env_name="AUTH_SECRET_KEY_ENCRYPTED",
            plain_env_name="AUTH_SECRET_KEY",
            default_value="cloud-collection-app-dev-secret",
        )
        self.token_ttl_seconds = token_ttl_seconds or int(
            os.getenv("AUTH_TOKEN_TTL_SECONDS", str(self.DEFAULT_TOKEN_TTL_SECONDS))
        )
        self.password_hash_service = password_hash_service or PasswordHashService()

    def issue_token(self, username: str, password: str, user_repository=None) -> dict[str, Any]:
        """Cree une reponse OAuth2 si les identifiants sont valides.

        Args:
            username (str): Identifiant utilisateur fourni par le client.
            password (str): Mot de passe fourni par le client.
            user_repository (object | None): Repository optionnel des utilisateurs en base.

        Returns:
            dict[str, Any]: Reponse contenant `access_token`, `token_type` et `expires_in`.
        """

        authenticated_identity = self.get_authenticated_identity(username, password, user_repository)
        if not authenticated_identity:
            raise ValueError("Identifiants invalides.")

        return {
            "access_token": self.create_access_token(
                authenticated_identity.subject,
                authenticated_identity.profile,
            ),
            "token_type": "Bearer",
            "expires_in": self.token_ttl_seconds,
        }

    def validate_credentials(self, username: str, password: str) -> bool:
        """Verifie les identifiants d'acces au backend.

        Args:
            username (str): Identifiant utilisateur fourni par le client.
            password (str): Mot de passe fourni par le client.

        Returns:
            bool: `True` si les identifiants correspondent a la configuration.
        """

        return secrets_equal(username, self.username) and secrets_equal(password, self.password)

    def get_authenticated_identity(
        self,
        username: str,
        password: str,
        user_repository=None,
    ) -> AuthenticatedTokenIdentity | None:
        """Retourne l'identite authentifiee via la configuration ou la base.

        Args:
            username (str): Identifiant utilisateur fourni par le client.
            password (str): Mot de passe fourni par le client.
            user_repository (object | None): Repository optionnel des utilisateurs en base.

        Returns:
            AuthenticatedTokenIdentity | None: Identite a placer dans le token, ou `None`.
        """

        if self.validate_credentials(username, password):
            return AuthenticatedTokenIdentity(subject=username, profile=UserProfile.ADMIN.value)
        database_user = None
        if user_repository:
            database_user = self.validate_registered_user_credentials(
                username,
                password,
                user_repository,
            )
        if database_user:
            return AuthenticatedTokenIdentity(
                subject=database_user.email,
                profile=UserProfile.normalize(database_user.profile).value,
            )
        return None

    def get_authenticated_subject(self, username: str, password: str, user_repository=None) -> str:
        """Retourne le sujet authentifie via la configuration ou la base.

        Args:
            username (str): Identifiant utilisateur fourni par le client.
            password (str): Mot de passe fourni par le client.
            user_repository (object | None): Repository optionnel des utilisateurs en base.

        Returns:
            str: Sujet a placer dans le token, ou chaine vide si les identifiants sont invalides.
        """

        identity = self.get_authenticated_identity(username, password, user_repository)
        return identity.subject if identity else ""

    def validate_registered_user_credentials(
        self,
        username: str,
        password: str,
        user_repository,
    ) -> AuthenticatedUserCredentials | None:
        """Retourne un utilisateur enregistre si ses identifiants sont valides.

        Args:
            username (str): Email utilisateur fourni par le client.
            password (str): Mot de passe brut fourni par le client.
            user_repository (object): Repository exposant la recherche utilisateur verifie.

        Returns:
            AuthenticatedUserCredentials | None: Utilisateur verifie ou `None`.
        """

        normalized_email = str(username or "").strip().lower()
        if not normalized_email or not password:
            return None

        database_user = user_repository.find_verified_user_credentials_by_email(normalized_email)
        if not database_user:
            return None
        if not self.password_hash_service.verify_password(database_user.password_hash, password):
            return None
        user_repository.update_last_connexion_date(
            database_user.id,
            datetime.now(timezone.utc).replace(tzinfo=None),
        )
        return database_user

    def create_access_token(self, subject: str, profile: str | None = None) -> str:
        """Cree un token Bearer signe et limite dans le temps.

        Args:
            subject (str): Sujet du token, generalement l'identifiant utilisateur.
            profile (str | None): Profil applicatif a inclure dans le token.

        Returns:
            str: Token signe au format `payload.signature`.
        """

        issued_at = int(time.time())
        payload = {
            "sub": subject,
            "profile": UserProfile.normalize(profile).value,
            "iat": issued_at,
            "exp": issued_at + self.token_ttl_seconds,
        }
        payload_segment = self._encode_json(payload)
        signature_segment = self._sign(payload_segment)
        return f"{payload_segment}.{signature_segment}"

    def validate_access_token(self, token: str) -> dict[str, Any]:
        """Valide la signature et l'expiration d'un token Bearer.

        Args:
            token (str): Token transmis dans l'en-tete `Authorization`.

        Returns:
            dict[str, Any]: Payload decode si le token est valide.
        """

        try:
            payload_segment, signature_segment = token.split(".", 1)
        except ValueError as exc:
            raise ValueError("Token invalide.") from exc

        expected_signature = self._sign(payload_segment)
        if not secrets_equal(signature_segment, expected_signature):
            raise ValueError("Token invalide.")

        payload = self._decode_json(payload_segment)
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("Token expire.")
        return payload

    def _encode_json(self, payload: dict[str, Any]) -> str:
        """Encode un dictionnaire JSON en base64 URL-safe.

        Args:
            payload (dict[str, Any]): Donnees a encoder.

        Returns:
            str: Representation base64 URL-safe sans padding.
        """

        raw_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return base64.urlsafe_b64encode(raw_json).decode("ascii").rstrip("=")

    def _decode_json(self, payload_segment: str) -> dict[str, Any]:
        """Decode un segment base64 URL-safe en dictionnaire JSON.

        Args:
            payload_segment (str): Segment du token a decoder.

        Returns:
            dict[str, Any]: Donnees JSON decodees.
        """

        padding = "=" * (-len(payload_segment) % 4)
        try:
            raw_json = base64.urlsafe_b64decode(f"{payload_segment}{padding}")
            payload = json.loads(raw_json.decode("utf-8"))
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValueError("Token invalide.") from exc
        if not isinstance(payload, dict):
            raise ValueError("Token invalide.")
        return payload

    def _sign(self, payload_segment: str) -> str:
        """Signe un segment de token avec HMAC SHA-256.

        Args:
            payload_segment (str): Segment payload du token.

        Returns:
            str: Signature base64 URL-safe sans padding.
        """

        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            payload_segment.encode("ascii"),
            hashlib.sha256,
        ).digest()
        return base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")

    def _read_secret(
        self,
        encrypted_env_name: str,
        plain_env_name: str,
        default_value: str,
    ) -> str:
        """Lit un secret chiffre depuis l'environnement avec secours en clair.

        Args:
            encrypted_env_name (str): Nom de la variable contenant le secret chiffre.
            plain_env_name (str): Nom de la variable contenant le secret en clair.
            default_value (str): Valeur par defaut si aucune variable n'est definie.

        Returns:
            str: Secret pret a etre utilise par le service.
        """

        encrypted_value = os.getenv(encrypted_env_name)
        if encrypted_value:
            encryption_key = os.getenv("AUTH_ENV_ENCRYPTION_KEY")
            if not encryption_key:
                raise ValueError("AUTH_ENV_ENCRYPTION_KEY est requis pour dechiffrer les secrets.")
            return EnvSecretCipher(encryption_key).decrypt(encrypted_value)

        return os.getenv(plain_env_name, default_value)


def secrets_equal(left: str, right: str) -> bool:
    """Compare deux chaines sans fuite de timing evidente.

    Args:
        left (str): Premiere valeur a comparer.
        right (str): Deuxieme valeur a comparer.

    Returns:
        bool: `True` si les chaines sont identiques.
    """

    return hmac.compare_digest(str(left), str(right))
