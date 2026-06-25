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
# Description : creation et validation des sessions invitees de partage.

from datetime import datetime, timezone
from typing import Any, Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from services.users import UserStatus

from .auth_token_service import AuthTokenService
from .collection_share_unavailable_error import CollectionShareUnavailableError
from .user_profile import UserProfile


class CollectionShareGuestAuthenticationService:
    """Echange un lien signe et controle les sessions GUEST revocables."""

    def __init__(
        self,
        configuration: Any,
        token_service: AuthTokenService,
        repository: Any,
        engine: Engine | None = None,
        engine_factory: Callable[[str], Engine] = create_engine,
        clock: Callable[[], datetime] | None = None,
    ):
        """Initialise le service d'authentification invitee.

        Args:
            configuration (Any): Configuration de base de donnees.
            token_service (AuthTokenService): Service central de signature.
            repository (Any): Repository des partages de collection.
            engine (Engine | None): Moteur SQLAlchemy injectable en test.
            engine_factory (Callable[[str], Engine]): Fabrique de moteur SQLAlchemy.
            clock (Callable[[], datetime] | None): Horloge UTC injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration
        self.token_service = token_service
        self.repository = repository
        self.engine = engine
        if self.engine is None and configuration.is_database_enabled():
            self.engine = engine_factory(configuration.database_url)
        self.clock = clock or self._utc_now

    def create_share_link_token(self, share_id: int, expires_at: datetime) -> str:
        """Cree un token de lien signe et inutilisable comme Bearer.

        Args:
            share_id (int): Identifiant du partage persiste.
            expires_at (datetime): Date d'expiration du partage.

        Returns:
            str: Token signe a placer dans le lien HTTP.

        Raises:
            ValueError: Si l'identifiant ou la date est invalide.
        """

        if share_id <= 0:
            raise ValueError("Identifiant de partage invalide.")
        expiration_timestamp = self._timestamp(expires_at)
        return self.token_service.create_access_token(
            subject=f"collection-share:{share_id}",
            profile=UserProfile.GUEST.value,
            expires_at=expiration_timestamp,
            additional_claims={
                "token_kind": AuthTokenService.COLLECTION_SHARE_LINK_TOKEN_KIND,
                "collection_share_id": share_id,
            },
        )

    def exchange_share_link_token(self, raw_token: str) -> dict[str, Any]:
        """Echange un token de lien valide contre une session Bearer GUEST.

        Args:
            raw_token (str): Token signe extrait du lien de partage.

        Returns:
            dict[str, Any]: Reponse OAuth2 contenant la session GUEST.

        Raises:
            ValueError: Si le token de lien est invalide.
            CollectionShareUnavailableError: Si le partage n'est plus actif.
            RuntimeError: Si la base de donnees est indisponible.
        """

        payload = self.token_service.decode_signed_token(raw_token, validate_expiration=False)
        if payload.get("token_kind") != AuthTokenService.COLLECTION_SHARE_LINK_TOKEN_KIND:
            raise ValueError("Token de partage invalide.")
        share_id = self._positive_identifier(payload.get("collection_share_id"))
        now = self.clock()
        if int(payload.get("exp", 0)) <= self._timestamp(now):
            raise CollectionShareUnavailableError("Partage expire ou revoque.")
        share = self._find_active_share(share_id, now)
        expires_at = share["expires_at"]
        expires_in = max(0, int((expires_at - now).total_seconds()))
        access_token = self.token_service.create_access_token(
            subject=f"guest-share:{share_id}",
            profile=UserProfile.GUEST.value,
            display_name=str(share["owner_pseudonym"]),
            expires_at=self._timestamp(expires_at),
            additional_claims=self._guest_claims(share),
        )
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
        }

    def validate_guest_session(self, payload: dict[str, Any]) -> None:
        """Verifie en base qu'une session GUEST reste rattachee a un partage actif.

        Args:
            payload (dict[str, Any]): Payload Bearer deja signe et decode.

        Returns:
            None: La methode ne retourne aucune valeur si la session reste valide.

        Raises:
            ValueError: Si les claims GUEST sont invalides.
            CollectionShareUnavailableError: Si le partage n'est plus actif.
            RuntimeError: Si la base de donnees est indisponible.
        """

        if UserProfile.normalize(payload.get("profile")) is not UserProfile.GUEST:
            return
        share_id = self._positive_identifier(payload.get("collection_share_id"))
        share = self._find_active_share(share_id, self.clock())
        if int(payload.get("owner_user_id", 0)) != int(share["owner_user_id"]):
            raise ValueError("Session invitee invalide.")

    def _find_active_share(self, share_id: int, current_time: datetime) -> dict[str, Any]:
        if self.engine is None:
            raise RuntimeError("DATABASE_URL est requis pour valider un partage.")
        with self.engine.connect() as connection:
            share = self.repository.find_share_with_owner(connection, share_id, current_time)
        if not share or share.get("status") != "ACTIVE":
            raise CollectionShareUnavailableError("Partage expire ou revoque.")
        if str(share.get("owner_status")) != UserStatus.ACTIVE.value:
            raise CollectionShareUnavailableError("Partage expire ou revoque.")
        return share

    @staticmethod
    def _guest_claims(share: dict[str, Any]) -> dict[str, Any]:
        return {
            "collection_share_id": int(share["id"]),
            "owner_user_id": int(share["owner_user_id"]),
            "owner_pseudonym": str(share["owner_pseudonym"]),
            "permissions": {
                "collection": bool(share["allow_collection"]),
                "wishlist": bool(share["allow_wishlist"]),
                "prices": bool(share["allow_prices"]),
            },
        }

    @staticmethod
    def _positive_identifier(value: Any) -> int:
        try:
            identifier = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Token de partage invalide.") from exc
        if identifier <= 0:
            raise ValueError("Token de partage invalide.")
        return identifier

    @staticmethod
    def _timestamp(value: datetime) -> int:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return int(value.timestamp())

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)
