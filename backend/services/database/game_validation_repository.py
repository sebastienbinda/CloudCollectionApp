#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-01
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : repository SQL de moderation admin des jeux en validation.

from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.engine import Connection

from .game_duplicate_repository import SqlAlchemyGameDuplicateRepository

GAME_STATUS_WAITING_VALIDATION = "WAITING_VALIDATION"
GAME_STATUS_ACCEPTED = "ACCEPTED"


class SqlAlchemyGameValidationRepository:
    """Persiste les validations et refus administrateur des jeux."""

    GLOBAL_GAME_IMPORT_LOCK_KEY = SqlAlchemyGameDuplicateRepository.GLOBAL_GAME_IMPORT_LOCK_KEY

    def __init__(self, schema_name: str):
        """Initialise le repository de moderation des jeux.

        Args:
            schema_name (str): Nom du schema PostgreSQL.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name

    def lock_global_game_catalog(self, connection: Connection) -> None:
        """Serialise la moderation avec les imports et corrections de jeux.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            None: Le verrou PostgreSQL est conserve jusqu'a la fin de transaction.
        """

        connection.execute(
            text("SELECT pg_advisory_xact_lock(:lock_key)"),
            {"lock_key": self.GLOBAL_GAME_IMPORT_LOCK_KEY},
        )

    def accept_waiting_games(self, connection: Connection, game_ids: list[int]) -> list[int]:
        """Valide les jeux en attente parmi les identifiants fournis.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_ids (list[int]): Identifiants candidats.

        Returns:
            list[int]: Identifiants effectivement valides.
        """

        if not game_ids:
            return []
        rows = connection.execute(
            text(
                f'UPDATE "{self.schema_name}".t_game '
                "SET status = :accepted_status "
                "WHERE id IN :game_ids AND status = :waiting_status "
                "RETURNING id"
            ).bindparams(bindparam("game_ids", expanding=True)),
            {
                "game_ids": game_ids,
                "accepted_status": GAME_STATUS_ACCEPTED,
                "waiting_status": GAME_STATUS_WAITING_VALIDATION,
            },
        ).mappings()
        return [int(row["id"]) for row in rows]

    def count_waiting_validation_games(self, connection: Connection) -> int:
        """Compte les jeux en attente de validation administrateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle ou de lecture.

        Returns:
            int: Nombre de jeux `WAITING_VALIDATION`.
        """

        return int(connection.execute(
            text(
                f'SELECT COUNT(*) FROM "{self.schema_name}".t_game '
                "WHERE status = :waiting_status"
            ),
            {"waiting_status": GAME_STATUS_WAITING_VALIDATION},
        ).scalar_one())

    def list_refusable_games(self, connection: Connection, game_ids: list[int]) -> list[dict[str, Any]]:
        """Liste les jeux en attente pouvant etre refuses.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_ids (list[int]): Identifiants candidats.

        Returns:
            list[dict[str, Any]]: Jeux avec plateforme et utilisateurs impactes.
        """

        if not game_ids:
            return []
        rows = connection.execute(
            text(
                "SELECT game.id, game.name, platform.name AS platform_name, "
                "app_user.id AS user_id, app_user.email AS user_email "
                f'FROM "{self.schema_name}".t_game game '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                f'LEFT JOIN "{self.schema_name}".t_user_collection collection '
                "ON collection.game_id = game.id "
                f'LEFT JOIN "{self.schema_name}".t_user app_user '
                "ON app_user.id = collection.user_id "
                "WHERE game.id IN :game_ids AND game.status = :waiting_status "
                "ORDER BY game.id, app_user.id"
            ).bindparams(bindparam("game_ids", expanding=True)),
            {
                "game_ids": game_ids,
                "waiting_status": GAME_STATUS_WAITING_VALIDATION,
            },
        ).mappings()
        return [dict(row) for row in rows]

    def delete_user_collection_links(self, connection: Connection, game_ids: list[int]) -> int:
        """Supprime les rattachements utilisateur aux jeux refuses.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_ids (list[int]): Identifiants des jeux refuses.

        Returns:
            int: Nombre de lignes `t_user_collection` supprimees.
        """

        if not game_ids:
            return 0
        return int(connection.execute(
            text(
                f'DELETE FROM "{self.schema_name}".t_user_collection '
                "WHERE game_id IN :game_ids"
            ).bindparams(bindparam("game_ids", expanding=True)),
            {"game_ids": game_ids},
        ).rowcount)

    def delete_games(self, connection: Connection, game_ids: list[int]) -> list[int]:
        """Supprime les jeux en attente refuses.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_ids (list[int]): Identifiants des jeux refuses.

        Returns:
            list[int]: Identifiants effectivement supprimes.
        """

        if not game_ids:
            return []
        rows = connection.execute(
            text(
                f'DELETE FROM "{self.schema_name}".t_game '
                "WHERE id IN :game_ids AND status = :waiting_status "
                "RETURNING id"
            ).bindparams(bindparam("game_ids", expanding=True)),
            {
                "game_ids": game_ids,
                "waiting_status": GAME_STATUS_WAITING_VALIDATION,
            },
        ).mappings()
        return [int(row["id"]) for row in rows]
