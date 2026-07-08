#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-07-05
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : repository SQL des statistiques detaillees de collection.

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection


class SqlAlchemyUserCollectionStatisticsRepository:
    """Lit les agregats statistiques de la collection utilisateur."""

    def __init__(self, schema_name: str):
        """Initialise le repository de statistiques utilisateur.

        Args:
            schema_name (str): Nom du schema PostgreSQL.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            Aucun.
        """

        self.schema_name = schema_name

    def list_platform_distribution(
        self,
        connection: Connection,
        user_id: int,
    ) -> list[dict[str, Any]]:
        """Liste la repartition des jeux possedes par plateforme.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant du proprietaire de collection.

        Returns:
            list[dict[str, Any]]: Nombre de jeux par plateforme.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        rows = connection.execute(
            text(
                "SELECT platform.id AS platform_id, platform.name AS platform_name, "
                "COUNT(*) AS games_count "
                f'FROM "{self.schema_name}".t_user_collection user_collection '
                f'JOIN "{self.schema_name}".t_game game ON game.id = user_collection.game_id '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                "WHERE user_collection.user_id = :user_id "
                "AND user_collection.wishlist = FALSE "
                "GROUP BY platform.id, platform.name "
                "ORDER BY COUNT(*) DESC, platform.name ASC"
            ),
            {"user_id": user_id},
        ).mappings()
        return [dict(row) for row in rows]

    def list_release_year_distribution(
        self,
        connection: Connection,
        user_id: int,
        platform_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Liste la repartition annuelle des dates de sortie.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant du proprietaire de collection.
            platform_id (int | None): Plateforme optionnelle de filtrage.

        Returns:
            list[dict[str, Any]]: Nombre de jeux par annee de sortie.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        return self._list_year_distribution(connection, user_id, "game.release_date", platform_id)

    def list_purchase_year_distribution(
        self,
        connection: Connection,
        user_id: int,
        platform_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Liste la repartition annuelle des dates d'achat.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant du proprietaire de collection.
            platform_id (int | None): Plateforme optionnelle de filtrage.

        Returns:
            list[dict[str, Any]]: Nombre de jeux par annee d'achat.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        return self._list_year_distribution(
            connection,
            user_id,
            "user_collection.buy_date",
            platform_id,
        )

    def list_top_rated_games(
        self,
        connection: Connection,
        user_id: int,
        platform_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Liste les jeux possedes dont la note normalisee est superieure ou egale a 90.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant du proprietaire de collection.
            platform_id (int | None): Plateforme optionnelle de filtrage.

        Returns:
            list[dict[str, Any]]: Jeux les mieux notes.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        platform_filter = "AND game.platform = :platform_id " if platform_id is not None else ""
        parameters = {"user_id": user_id}
        if platform_id is not None:
            parameters["platform_id"] = platform_id
        rows = connection.execute(
            text(
                "SELECT game.id, game.name, platform.name AS platform_name, "
                "game.release_date::text AS release_date, "
                "user_collection.buy_date::text AS buy_date, "
                "user_collection.grade, user_collection.grade_normalized "
                f'FROM "{self.schema_name}".t_user_collection user_collection '
                f'JOIN "{self.schema_name}".t_game game ON game.id = user_collection.game_id '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                "WHERE user_collection.user_id = :user_id "
                "AND user_collection.wishlist = FALSE "
                f"{platform_filter}"
                "AND user_collection.grade_normalized >= 90 "
                "ORDER BY user_collection.grade_normalized DESC, "
                "game.name ASC"
            ),
            parameters,
        ).mappings()
        return [dict(row) for row in rows]

    def _list_year_distribution(
        self,
        connection: Connection,
        user_id: int,
        date_column_expression: str,
        platform_id: int | None = None,
    ) -> list[dict[str, Any]]:
        platform_filter = "AND game.platform = :platform_id " if platform_id is not None else ""
        parameters = {"user_id": user_id}
        if platform_id is not None:
            parameters["platform_id"] = platform_id
        rows = connection.execute(
            text(
                f"SELECT EXTRACT(YEAR FROM {date_column_expression})::int AS year, "
                "COUNT(*) AS games_count "
                f'FROM "{self.schema_name}".t_user_collection user_collection '
                f'JOIN "{self.schema_name}".t_game game ON game.id = user_collection.game_id '
                "WHERE user_collection.user_id = :user_id "
                "AND user_collection.wishlist = FALSE "
                f"{platform_filter}"
                f"AND {date_column_expression} IS NOT NULL "
                f"GROUP BY EXTRACT(YEAR FROM {date_column_expression})::int "
                "ORDER BY year ASC"
            ),
            parameters,
        ).mappings()
        return [dict(row) for row in rows]
