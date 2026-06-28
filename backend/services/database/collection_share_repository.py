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
# Description : repository SQL des partages temporaires de collection.

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.engine import Connection


class SqlAlchemyCollectionShareRepository:
    """Persiste et lit les partages temporaires de collection."""

    def __init__(self, schema_name: str):
        """Initialise le repository de partage de collection.

        Args:
            schema_name (str): Nom du schema PostgreSQL.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name

    def create_share(
        self,
        connection: Connection,
        owner_user_id: int,
        created_at: datetime,
        expires_at: datetime,
        allow_collection: bool,
        allow_wishlist: bool,
        allow_prices: bool,
        wishlist_buy_status_default_filter: str = "all",
        recipient: str | None = None,
    ) -> dict[str, object]:
        """Cree un partage rattache a un proprietaire.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            owner_user_id (int): Identifiant du proprietaire.
            created_at (datetime): Date de creation.
            expires_at (datetime): Date d'expiration.
            allow_collection (bool): Autorisation collection.
            allow_wishlist (bool): Autorisation liste de souhaits.
            allow_prices (bool): Autorisation prix.
            wishlist_buy_status_default_filter (str): Filtre d'achat wishlist par defaut.
            recipient (str | None): Destinataire lisible du partage.

        Returns:
            dict[str, object]: Partage cree.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse l'insertion.
        """

        row = connection.execute(
            text(
                f'INSERT INTO "{self.schema_name}".t_collection_share '
                "(owner_user_id, created_at, expires_at, revoked_at, "
                "allow_collection, allow_wishlist, allow_prices, "
                "wishlist_buy_status_default_filter, recipient) "
                "VALUES (:owner_user_id, :created_at, :expires_at, NULL, "
                ":allow_collection, :allow_wishlist, :allow_prices, "
                ":wishlist_buy_status_default_filter, :recipient) "
                f"RETURNING {self._share_columns()}"
            ),
            {
                "owner_user_id": owner_user_id,
                "created_at": created_at,
                "expires_at": expires_at,
                "allow_collection": allow_collection,
                "allow_wishlist": allow_wishlist,
                "allow_prices": allow_prices,
                "wishlist_buy_status_default_filter": wishlist_buy_status_default_filter,
                "recipient": recipient,
            },
        ).mappings().one()
        return dict(row)

    def find_share(
        self,
        connection: Connection,
        share_id: int,
        current_time: datetime,
    ) -> dict[str, object] | None:
        """Recherche un partage par son identifiant technique.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            share_id (int): Identifiant du partage.
            current_time (datetime): Date utilisee pour calculer le statut.

        Returns:
            dict[str, object] | None: Partage trouve avec son statut ou absence.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la lecture.
        """

        row = connection.execute(
            text(
                f"SELECT {self._share_columns()}, {self._status_expression()} AS status "
                f'FROM "{self.schema_name}".t_collection_share '
                "WHERE id = :share_id"
            ),
            {"share_id": share_id, "current_time": current_time},
        ).mappings().first()
        return dict(row) if row else None

    def find_share_with_owner(
        self,
        connection: Connection,
        share_id: int,
        current_time: datetime,
    ) -> dict[str, object] | None:
        """Recherche un partage avec le statut courant de son proprietaire.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            share_id (int): Identifiant du partage.
            current_time (datetime): Date utilisee pour calculer le statut.

        Returns:
            dict[str, object] | None: Partage et proprietaire ou absence.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la lecture.
        """

        row = connection.execute(
            text(
                f"SELECT {self._qualified_share_columns()}, "
                f"{self._qualified_status_expression()} AS status, "
                "app_user.pseudonym AS owner_pseudonym, "
                "app_user.status AS owner_status "
                f'FROM "{self.schema_name}".t_collection_share collection_share '
                f'JOIN "{self.schema_name}".t_user app_user '
                "ON app_user.id = collection_share.owner_user_id "
                "WHERE collection_share.id = :share_id"
            ),
            {"share_id": share_id, "current_time": current_time},
        ).mappings().first()
        return dict(row) if row else None

    def list_shares_by_owner(
        self,
        connection: Connection,
        owner_user_id: int,
        current_time: datetime,
    ) -> list[dict[str, object]]:
        """Liste tous les partages d'un proprietaire sans purger l'historique.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            owner_user_id (int): Identifiant du proprietaire.
            current_time (datetime): Date utilisee pour calculer les statuts.

        Returns:
            list[dict[str, object]]: Partages actifs, expires et revoques.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la lecture.
        """

        rows = connection.execute(
            text(
                f"SELECT {self._share_columns()}, {self._status_expression()} AS status "
                f'FROM "{self.schema_name}".t_collection_share '
                "WHERE owner_user_id = :owner_user_id "
                "ORDER BY created_at DESC, id DESC"
            ),
            {"owner_user_id": owner_user_id, "current_time": current_time},
        ).mappings().all()
        return [dict(row) for row in rows]

    def revoke_share(
        self,
        connection: Connection,
        share_id: int,
        owner_user_id: int,
        revoked_at: datetime,
    ) -> dict[str, object] | None:
        """Revoque de facon idempotente un partage appartenant au proprietaire.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            share_id (int): Identifiant du partage.
            owner_user_id (int): Identifiant du proprietaire.
            revoked_at (datetime): Date de revocation demandee.

        Returns:
            dict[str, object] | None: Partage revoque ou absence.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la mise a jour.
        """

        row = connection.execute(
            text(
                f'UPDATE "{self.schema_name}".t_collection_share '
                "SET revoked_at = COALESCE(revoked_at, :revoked_at) "
                "WHERE id = :share_id AND owner_user_id = :owner_user_id "
                f"RETURNING {self._share_columns()}"
            ),
            {
                "share_id": share_id,
                "owner_user_id": owner_user_id,
                "revoked_at": revoked_at,
            },
        ).mappings().first()
        return dict(row) if row else None

    @staticmethod
    def _share_columns() -> str:
        return (
            "id, owner_user_id, created_at, expires_at, revoked_at, "
            "allow_collection, allow_wishlist, allow_prices, "
            "wishlist_buy_status_default_filter, recipient"
        )

    @staticmethod
    def _status_expression() -> str:
        return (
            "CASE WHEN revoked_at IS NOT NULL THEN 'REVOKED' "
            "WHEN expires_at <= :current_time THEN 'EXPIRED' ELSE 'ACTIVE' END"
        )

    @staticmethod
    def _qualified_share_columns() -> str:
        return ", ".join(
            f"collection_share.{column_name}"
            for column_name in (
                "id",
                "owner_user_id",
                "created_at",
                "expires_at",
                "revoked_at",
                "allow_collection",
                "allow_wishlist",
                "allow_prices",
                "wishlist_buy_status_default_filter",
                "recipient",
            )
        )

    @staticmethod
    def _qualified_status_expression() -> str:
        return (
            "CASE WHEN collection_share.revoked_at IS NOT NULL THEN 'REVOKED' "
            "WHEN collection_share.expires_at <= :current_time THEN 'EXPIRED' "
            "ELSE 'ACTIVE' END"
        )
