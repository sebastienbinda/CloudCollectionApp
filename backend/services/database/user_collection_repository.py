#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : repository SQL des associations utilisateur-collection.

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.engine import Connection


@dataclass(frozen=True)
class UserGameAssociation:
    """Represente une association utilisateur-jeu a persister.

    Attributes:
        game_id (int): Identifiant du jeu rattache.
        wishlist (bool): Indique si le jeu est un souhait.
        purchase_price (Decimal | None): Prix d'achat decimal optionnel.
    """

    game_id: int
    wishlist: bool = False
    purchase_price: Decimal | None = None
    price_unit: str | None = None
    buy_location: str | None = None
    buy_date: date | None = None
    grade: str | None = None
    grade_normalized: int | None = None
    condition: int | None = None
    has_manual: bool | None = None
    is_collector: bool | None = None
    has_steelbook: bool | None = None
    is_digital: bool | None = None
    region: str | None = None
    description: str | None = None


class SqlAlchemyUserCollectionRepository:
    """Persiste les associations de jeux dans `t_user_collection`."""

    ASSOCIATION_BATCH_SIZE = 500

    def __init__(self, schema_name: str):
        """Initialise le repository d'association utilisateur-collection.

        Args:
            schema_name (str): Nom du schema PostgreSQL.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name

    def find_user_game_wishlist_values(
        self,
        connection: Connection,
        user_id: int,
    ) -> dict[int, bool]:
        """Lit les valeurs wishlist des jeux deja associes a un utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.

        Returns:
            dict[int, bool]: Valeur wishlist par identifiant de jeu.
        """

        return {
            int(row["game_id"]): bool(row["wishlist"])
            for row in connection.execute(
                text(
                    f'SELECT game_id, wishlist FROM "{self.schema_name}".t_user_collection '
                    "WHERE user_id = :user_id"
                ),
                {"user_id": user_id},
            ).mappings()
        }

    def ensure_user_game_associations(
        self,
        connection: Connection,
        user_id: int,
        game_associations: list[int | UserGameAssociation],
    ) -> int:
        """Cree les associations utilisateur-jeu manquantes.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.
            game_associations (list[int | UserGameAssociation]): Jeux a rattacher.

        Returns:
            int: Nombre de jeux associes apres import.
        """

        normalized_associations = self._normalize_associations(game_associations)
        existing_wishlist_values = self.find_user_game_wishlist_values(connection, user_id)
        existing_game_ids = set(existing_wishlist_values.keys())
        insert_associations = []
        update_associations = []
        for association in normalized_associations:
            if association.game_id in existing_game_ids:
                update_associations.append(association)
                continue
            insert_associations.append(association)
            existing_game_ids.add(association.game_id)
        self._insert_missing_associations(connection, user_id, insert_associations)
        self._update_private_information(connection, user_id, update_associations)
        return len(normalized_associations)

    def _insert_missing_associations(
        self,
        connection: Connection,
        user_id: int,
        associations: list[UserGameAssociation],
    ) -> None:
        """Insere les associations absentes en une execution groupee.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.
            associations (list[UserGameAssociation]): Associations nouvelles.

        Returns:
            None: Les associations sont persistees quand la liste n'est pas vide.
        """

        if not associations:
            return
        insert_statement = text(
            f'INSERT INTO "{self.schema_name}".t_user_collection '
            "(user_id, game_id, game_additional_name, wishlist, purchase_price, "
            "price_unit, buy_location, buy_date, grade, grade_normalized, "
            "condition, has_manual, "
            "is_collector, has_steelbook, is_digital, region, description) "
            "VALUES (:user_id, :game_id, NULL, :wishlist, :purchase_price, "
            ":price_unit, :buy_location, :buy_date, :grade, :grade_normalized, "
            ":condition, :has_manual, "
            ":is_collector, :has_steelbook, :is_digital, :region, :description)"
        )
        for association_batch in self._association_batches(associations):
            connection.execute(
                insert_statement,
                [
                    self._association_parameters(user_id, association)
                    for association in association_batch
                ],
            )

    def _update_private_information(
        self,
        connection: Connection,
        user_id: int,
        associations: list[UserGameAssociation],
    ) -> None:
        """Met a jour en groupe les informations privees non nulles.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.
            associations (list[UserGameAssociation]): Valeurs importees.

        Returns:
            None: Met a jour les associations existantes quand la liste n'est pas vide.
        """

        if not associations:
            return
        assignments = ", ".join(
            f"{field} = COALESCE(:{field}, {field})"
            for field in self._private_field_names()
        )
        update_statement = text(
            f'UPDATE "{self.schema_name}".t_user_collection SET {assignments} '
            "WHERE user_id = :user_id AND game_id = :game_id"
        )
        for association_batch in self._association_batches(associations):
            connection.execute(
                update_statement,
                [
                    self._association_parameters(user_id, association)
                    for association in association_batch
                ],
            )

    def _association_batches(
        self,
        associations: list[UserGameAssociation],
    ) -> list[list[UserGameAssociation]]:
        """Decoupe les associations en lots bornes pour les executions SQL.

        Args:
            associations (list[UserGameAssociation]): Associations a persister.

        Returns:
            list[list[UserGameAssociation]]: Lots successifs de taille limitee.
        """

        return [
            associations[index:index + self.ASSOCIATION_BATCH_SIZE]
            for index in range(0, len(associations), self.ASSOCIATION_BATCH_SIZE)
        ]

    def _association_parameters(
        self,
        user_id: int,
        association: UserGameAssociation,
    ) -> dict[str, object]:
        """Construit les parametres SQL d'une association.

        Args:
            user_id (int): Identifiant utilisateur.
            association (UserGameAssociation): Association importee.

        Returns:
            dict[str, object]: Parametres SQL nommes.
        """

        parameters = {
            "user_id": user_id,
            "game_id": association.game_id,
            "wishlist": association.wishlist,
        }
        parameters.update({field: getattr(association, field) for field in self._private_field_names()})
        return parameters

    @staticmethod
    def _private_field_names() -> tuple[str, ...]:
        """Retourne les noms persistants des informations privees.

        Args:
            Aucun.

        Returns:
            tuple[str, ...]: Noms de colonnes SQL.
        """

        return (
            "purchase_price", "price_unit", "buy_location", "buy_date", "grade",
            "grade_normalized", "condition", "has_manual", "is_collector",
            "has_steelbook", "is_digital", "region", "description",
        )

    def count_user_game_associations(self, connection: Connection, user_id: int) -> int:
        """Compte les associations de collection d'un utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.

        Returns:
            int: Nombre d'associations utilisateur-jeu.
        """

        return int(
            connection.execute(
                text(
                    f'SELECT COUNT(*) FROM "{self.schema_name}".t_user_collection '
                    "WHERE user_id = :user_id"
                ),
                {"user_id": user_id},
            ).scalar_one()
        )

    def delete_user_game_associations(self, connection: Connection, user_id: int) -> int:
        """Supprime les associations de collection d'un utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.

        Returns:
            int: Nombre de lignes supprimees.
        """

        result = connection.execute(
            text(
                f'DELETE FROM "{self.schema_name}".t_user_collection '
                "WHERE user_id = :user_id"
            ),
            {"user_id": user_id},
        )
        return int(result.rowcount or 0)

    def _normalize_associations(
        self,
        game_associations: list[int | UserGameAssociation],
    ) -> list[UserGameAssociation]:
        """Normalise les associations en conservant `wishlist=false` par defaut.

        Args:
            game_associations (list[int | UserGameAssociation]): Associations source.

        Returns:
            list[UserGameAssociation]: Associations normalisees.
        """

        return [
            association
            if isinstance(association, UserGameAssociation)
            else UserGameAssociation(int(association), False)
            for association in game_associations
        ]
