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

from sqlalchemy import text
from sqlalchemy.engine import Connection


@dataclass(frozen=True)
class UserGameAssociation:
    """Represente une association utilisateur-jeu a persister.

    Attributes:
        game_id (int): Identifiant du jeu rattache.
        wishlist (bool): Indique si le jeu est un souhait.
    """

    game_id: int
    wishlist: bool = False


class SqlAlchemyUserCollectionRepository:
    """Persiste les associations de jeux dans `t_user_collection`."""

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
        for association in normalized_associations:
            if association.game_id in existing_game_ids:
                continue
            connection.execute(
                text(
                    f'INSERT INTO "{self.schema_name}".t_user_collection '
                    "(user_id, game_id, game_additional_name, wishlist) "
                    "VALUES (:user_id, :game_id, NULL, :wishlist)"
                ),
                {
                    "user_id": user_id,
                    "game_id": association.game_id,
                    "wishlist": association.wishlist,
                },
            )
            existing_game_ids.add(association.game_id)
        return len(normalized_associations)

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
