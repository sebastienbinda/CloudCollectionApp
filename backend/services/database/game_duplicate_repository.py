#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/|_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : repository SQL de gestion des doublons de jeux.

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection


class SqlAlchemyGameDuplicateRepository:
    """Persiste les signalements, refus et fusions de doublons de jeux."""

    GAME_UPDATE_COLUMNS = frozenset({"name", "release_date", "developer", "editor", "description"})
    GLOBAL_GAME_IMPORT_LOCK_KEY = 4_282_026_062_701

    def __init__(self, schema_name: str):
        """Initialise le repository de doublons de jeux.

        Args:
            schema_name (str): Nom du schema PostgreSQL.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name

    def lock_global_game_catalog(self, connection: Connection) -> None:
        """Serialise une correction de doublon avec les imports de jeux globaux.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            None: Le verrou PostgreSQL est conserve jusqu'a la fin de la transaction.
        """

        connection.execute(
            text("SELECT pg_advisory_xact_lock(:lock_key)"),
            {"lock_key": self.GLOBAL_GAME_IMPORT_LOCK_KEY},
        )

    def user_has_game(self, connection: Connection, user_id: int, game_id: int) -> bool:
        """Indique si un utilisateur possede un jeu dans sa collection.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.
            game_id (int): Identifiant du jeu.

        Returns:
            bool: `True` si le rattachement existe.
        """

        row = connection.execute(
            text(
                f'SELECT 1 FROM "{self.schema_name}".t_user_collection '
                "WHERE user_id = :user_id AND game_id = :game_id"
            ),
            {"user_id": user_id, "game_id": game_id},
        ).first()
        return row is not None

    def mark_game_as_duplicate(self, connection: Connection, game_id: int) -> bool:
        """Active le signalement de doublon sur un jeu.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_id (int): Identifiant du jeu signale.

        Returns:
            bool: `True` si un jeu a ete mis a jour.
        """

        return connection.execute(
            text(
                f'UPDATE "{self.schema_name}".t_game '
                "SET duplicate_flag = TRUE WHERE id = :game_id"
            ),
            {"game_id": game_id},
        ).rowcount > 0

    def count_reported_duplicates(self, connection: Connection) -> int:
        """Compte les jeux actuellement signales comme doublons.

        Args:
            connection (Connection): Connexion SQL transactionnelle ou de lecture.

        Returns:
            int: Nombre de jeux avec `duplicate_flag` actif.
        """

        return int(connection.execute(
            text(
                f'SELECT COUNT(*) FROM "{self.schema_name}".t_game '
                "WHERE duplicate_flag = TRUE"
            ),
        ).scalar_one())

    def reject_duplicate(self, connection: Connection, game_id: int) -> bool:
        """Refuse un signalement de doublon.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_id (int): Identifiant du jeu a remettre a l'etat normal.

        Returns:
            bool: `True` si un jeu a ete mis a jour.
        """

        return connection.execute(
            text(
                f'UPDATE "{self.schema_name}".t_game '
                "SET duplicate_flag = FALSE WHERE id = :game_id AND duplicate_flag = TRUE"
            ),
            {"game_id": game_id},
        ).rowcount > 0

    def find_game_for_duplicate_management(
        self,
        connection: Connection,
        game_id: int,
    ) -> dict[str, Any] | None:
        """Recherche un jeu avec ses attributs administrables.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_id (int): Identifiant du jeu.

        Returns:
            dict[str, Any] | None: Jeu trouve ou absence.
        """

        row = connection.execute(
            text(
                "SELECT "
                "game.id, game.name, game.release_date::text AS release_date, "
                "game.developer, developer_studio.name AS developer_name, "
                "game.editor, editor_studio.name AS editor_name, "
                "game.platform, platform.name AS platform_name, "
                "game.description, game.duplicate_flag "
                f'FROM "{self.schema_name}".t_game game '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                f'LEFT JOIN "{self.schema_name}".t_studio developer_studio '
                "ON developer_studio.id = game.developer "
                f'LEFT JOIN "{self.schema_name}".t_studio editor_studio '
                "ON editor_studio.id = game.editor "
                "WHERE game.id = :game_id"
            ),
            {"game_id": game_id},
        ).mappings().first()
        return None if row is None else dict(row)

    def count_users_with_game(self, connection: Connection, game_id: int) -> int:
        """Compte les utilisateurs rattaches a un jeu.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_id (int): Identifiant du jeu.

        Returns:
            int: Nombre d'utilisateurs distincts.
        """

        return int(connection.execute(
            text(
                f'SELECT COUNT(DISTINCT user_id) FROM "{self.schema_name}".t_user_collection '
                "WHERE game_id = :game_id"
            ),
            {"game_id": game_id},
        ).scalar_one())

    def remap_user_collections(
        self,
        connection: Connection,
        duplicate_game_id: int,
        target_game_id: int,
    ) -> dict[str, int]:
        """Remappe les collections utilisateur du doublon vers le jeu conserve.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            duplicate_game_id (int): Identifiant du jeu a supprimer.
            target_game_id (int): Identifiant du jeu conserve.

        Returns:
            dict[str, int]: Compteurs de lignes mises a jour et fusionnees.
        """

        merged_rows = connection.execute(
            text(
                f'UPDATE "{self.schema_name}".t_user_collection target '
                "SET "
                "wishlist = COALESCE(target.wishlist, false) "
                "OR COALESCE(duplicate.wishlist, false), "
                "purchase_price = COALESCE(target.purchase_price, duplicate.purchase_price), "
                "price_unit = COALESCE(NULLIF(target.price_unit, ''), duplicate.price_unit), "
                "buy_location = COALESCE(NULLIF(target.buy_location, ''), duplicate.buy_location), "
                "buy_date = COALESCE(target.buy_date, duplicate.buy_date), "
                "grade = COALESCE(NULLIF(target.grade, ''), duplicate.grade), "
                '"condition" = COALESCE(target."condition", duplicate."condition"), '
                "has_manual = COALESCE(target.has_manual, false) "
                "OR COALESCE(duplicate.has_manual, false), "
                "is_collector = COALESCE(target.is_collector, false) "
                "OR COALESCE(duplicate.is_collector, false), "
                "has_steelbook = COALESCE(target.has_steelbook, false) "
                "OR COALESCE(duplicate.has_steelbook, false), "
                "is_digital = COALESCE(target.is_digital, false) "
                "OR COALESCE(duplicate.is_digital, false), "
                "region = COALESCE(NULLIF(target.region, ''), duplicate.region), "
                "description = COALESCE(target.description, duplicate.description) "
                f'FROM "{self.schema_name}".t_user_collection duplicate '
                "WHERE target.user_id = duplicate.user_id "
                "AND target.game_id = :target_game_id "
                "AND duplicate.game_id = :duplicate_game_id"
            ),
            {"duplicate_game_id": duplicate_game_id, "target_game_id": target_game_id},
        ).rowcount
        connection.execute(
            text(
                f'DELETE FROM "{self.schema_name}".t_user_collection duplicate '
                f'USING "{self.schema_name}".t_user_collection target '
                "WHERE duplicate.user_id = target.user_id "
                "AND duplicate.game_id = :duplicate_game_id "
                "AND target.game_id = :target_game_id"
            ),
            {"duplicate_game_id": duplicate_game_id, "target_game_id": target_game_id},
        )
        updated_rows = connection.execute(
            text(
                f'UPDATE "{self.schema_name}".t_user_collection '
                "SET game_id = :target_game_id WHERE game_id = :duplicate_game_id"
            ),
            {"duplicate_game_id": duplicate_game_id, "target_game_id": target_game_id},
        ).rowcount
        return {"merged_rows": int(merged_rows), "updated_rows": int(updated_rows)}

    def update_game_values(
        self,
        connection: Connection,
        game_id: int,
        selected_values: dict[str, Any],
    ) -> int:
        """Met a jour les attributs administrables du jeu conserve.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_id (int): Identifiant du jeu conserve.
            selected_values (dict[str, Any]): Valeurs choisies par l'administrateur.

        Returns:
            int: Nombre de lignes mises a jour.
        """

        assignments = []
        parameters: dict[str, Any] = {"game_id": game_id}
        for column_name, value in selected_values.items():
            if column_name not in self.GAME_UPDATE_COLUMNS:
                continue
            assignments.append(f"{column_name} = :{column_name}")
            parameters[column_name] = value
        if not assignments:
            return 0
        return int(connection.execute(
            text(
                f'UPDATE "{self.schema_name}".t_game SET '
                f"{', '.join(assignments)}, duplicate_flag = FALSE WHERE id = :game_id"
            ),
            parameters,
        ).rowcount)

    def insert_game_alias(
        self,
        connection: Connection,
        target_game_id: int,
        alias_name: str,
    ) -> bool:
        """Ajoute le nom du doublon comme alias du jeu conserve.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            target_game_id (int): Identifiant du jeu conserve.
            alias_name (str): Alias a ajouter.

        Returns:
            bool: `True` si l'alias a ete cree.
        """

        inserted_id = connection.execute(
            text(
                f'INSERT INTO "{self.schema_name}".t_game_alias '
                "(game_id, name, creation_date) "
                "VALUES (:game_id, :name, :creation_date) "
                "ON CONFLICT ON CONSTRAINT uq_t_game_alias_game_name DO NOTHING "
                "RETURNING id"
            ),
            {
                "game_id": target_game_id,
                "name": alias_name,
                "creation_date": datetime.now(timezone.utc).replace(tzinfo=None),
            },
        ).scalar_one_or_none()
        return inserted_id is not None

    def delete_game(self, connection: Connection, game_id: int) -> bool:
        """Supprime un jeu de reference.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_id (int): Identifiant du jeu a supprimer.

        Returns:
            bool: `True` si le jeu a ete supprime.
        """

        return connection.execute(
            text(f'DELETE FROM "{self.schema_name}".t_game WHERE id = :game_id'),
            {"game_id": game_id},
        ).rowcount > 0
