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
# Description : orchestration de la gestion proprietaire des partages.

from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .collection_share_not_found_error import CollectionShareNotFoundError
from .collection_share_owner_not_found_error import CollectionShareOwnerNotFoundError


class CollectionShareManagementService:
    """Cree, liste et revoque les partages d'un proprietaire connecte."""

    MIN_DURATION_HOURS = 1
    MAX_DURATION_HOURS = 240

    def __init__(
        self,
        configuration: Any,
        repository: Any,
        user_repository: Any,
        guest_authentication_service: Any,
        frontend_public_url: str,
        engine: Engine | None = None,
        engine_factory: Callable[[str], Engine] = create_engine,
        clock: Callable[[], datetime] | None = None,
    ):
        """Initialise le service de gestion des partages.

        Args:
            configuration (Any): Configuration de base de donnees.
            repository (Any): Repository des partages.
            user_repository (Any): Repository resolvant le proprietaire.
            guest_authentication_service (Any): Service de signature des liens.
            frontend_public_url (str): Origine publique du frontend.
            engine (Engine | None): Moteur SQLAlchemy injectable.
            engine_factory (Callable[[str], Engine]): Fabrique de moteur SQLAlchemy.
            clock (Callable[[], datetime] | None): Horloge UTC injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        configuration.validate()
        self.repository = repository
        self.user_repository = user_repository
        self.guest_authentication_service = guest_authentication_service
        self.frontend_public_url = str(frontend_public_url).rstrip("/")
        self.engine = engine
        if self.engine is None and configuration.is_database_enabled():
            self.engine = engine_factory(configuration.database_url)
        self.clock = clock or self._utc_now

    def create_share(
        self,
        owner_subject: str,
        duration_hours: Any,
        allow_collection: Any,
        allow_wishlist: Any,
        allow_prices: Any,
    ) -> dict[str, Any]:
        """Cree un partage valide pour le proprietaire connecte.

        Args:
            owner_subject (str): Sujet email du Bearer proprietaire.
            duration_hours (Any): Duree demandee en heures.
            allow_collection (Any): Permission collection brute.
            allow_wishlist (Any): Permission wishlist brute.
            allow_prices (Any): Permission prix brute.

        Returns:
            dict[str, Any]: Partage serialise avec son lien signe.

        Raises:
            ValueError: Si la duree ou les permissions sont invalides.
            CollectionShareOwnerNotFoundError: Si le proprietaire est inconnu.
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse l'ecriture.
        """

        normalized_duration = self._validate_duration(duration_hours)
        permissions = self._validate_permissions(
            allow_collection,
            allow_wishlist,
            allow_prices,
        )
        engine = self._require_engine()
        owner_user_id = self._resolve_owner_user_id(owner_subject)
        created_at = self.clock()
        expires_at = created_at + timedelta(hours=normalized_duration)
        with engine.begin() as connection:
            row = self.repository.create_share(
                connection,
                owner_user_id,
                created_at,
                expires_at,
                permissions["collection"],
                permissions["wishlist"],
                permissions["prices"],
            )
        return self._serialize_share(row, "ACTIVE")

    def list_shares(self, owner_subject: str) -> list[dict[str, Any]]:
        """Liste tous les partages du proprietaire connecte.

        Args:
            owner_subject (str): Sujet email du Bearer proprietaire.

        Returns:
            list[dict[str, Any]]: Partages actifs, expires et revoques.

        Raises:
            CollectionShareOwnerNotFoundError: Si le proprietaire est inconnu.
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la lecture.
        """

        engine = self._require_engine()
        owner_user_id = self._resolve_owner_user_id(owner_subject)
        with engine.connect() as connection:
            rows = self.repository.list_shares_by_owner(
                connection,
                owner_user_id,
                self.clock(),
            )
        return [self._serialize_share(row, str(row["status"])) for row in rows]

    def revoke_share(self, owner_subject: str, share_id: int) -> dict[str, Any]:
        """Revoque idempotemment un partage du proprietaire connecte.

        Args:
            owner_subject (str): Sujet email du Bearer proprietaire.
            share_id (int): Identifiant du partage a revoquer.

        Returns:
            dict[str, Any]: Partage revoque serialise.

        Raises:
            ValueError: Si l'identifiant est invalide.
            CollectionShareOwnerNotFoundError: Si le proprietaire est inconnu.
            CollectionShareNotFoundError: Si le partage ne lui appartient pas.
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse l'ecriture.
        """

        if type(share_id) is not int or share_id <= 0:
            raise ValueError("Identifiant de partage invalide.")
        engine = self._require_engine()
        owner_user_id = self._resolve_owner_user_id(owner_subject)
        with engine.begin() as connection:
            row = self.repository.revoke_share(
                connection,
                share_id,
                owner_user_id,
                self.clock(),
            )
        if row is None:
            raise CollectionShareNotFoundError("Partage introuvable.")
        return self._serialize_share(row, "REVOKED")

    def _resolve_owner_user_id(self, owner_subject: str) -> int:
        normalized_subject = str(owner_subject or "").strip().lower()
        owner_user_id = self.user_repository.find_user_id_by_email(normalized_subject)
        if owner_user_id is None:
            raise CollectionShareOwnerNotFoundError("Proprietaire de collection introuvable.")
        return int(owner_user_id)

    def _require_engine(self) -> Engine:
        if self.engine is None or self.user_repository is None:
            raise RuntimeError("DATABASE_URL est requis pour gerer les partages.")
        return self.engine

    def _validate_duration(self, duration_hours: Any) -> int:
        if type(duration_hours) is not int:
            raise ValueError("duration_hours doit etre un entier entre 1 et 240.")
        if not self.MIN_DURATION_HOURS <= duration_hours <= self.MAX_DURATION_HOURS:
            raise ValueError("duration_hours doit etre compris entre 1 et 240.")
        return duration_hours

    def _validate_permissions(
        self,
        allow_collection: Any,
        allow_wishlist: Any,
        allow_prices: Any,
    ) -> dict[str, bool]:
        values = (allow_collection, allow_wishlist, allow_prices)
        if any(type(value) is not bool for value in values):
            raise ValueError("Les permissions de partage doivent etre booleennes.")
        if not allow_collection and not allow_wishlist:
            raise ValueError("Le partage doit autoriser la collection ou la wishlist.")
        return {
            "collection": allow_collection,
            "wishlist": allow_wishlist,
            "prices": allow_prices,
        }

    def _serialize_share(self, row: dict[str, Any], status: str) -> dict[str, Any]:
        share_token = self.guest_authentication_service.create_share_link_token(
            int(row["id"]),
            row["expires_at"],
        )
        return {
            "id": int(row["id"]),
            "created_at": self._datetime_text(row["created_at"]),
            "expires_at": self._datetime_text(row["expires_at"]),
            "revoked_at": self._optional_datetime_text(row.get("revoked_at")),
            "permissions": {
                "collection": bool(row["allow_collection"]),
                "wishlist": bool(row["allow_wishlist"]),
                "prices": bool(row["allow_prices"]),
            },
            "status": status,
            "link": f"{self.frontend_public_url}/collection/share/{share_token}",
        }

    @staticmethod
    def _datetime_text(value: datetime) -> str:
        return value.isoformat()

    @classmethod
    def _optional_datetime_text(cls, value: datetime | None) -> str | None:
        return None if value is None else cls._datetime_text(value)

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)
