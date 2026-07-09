#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-25
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : repository SQL de consultation de collection utilisateur.

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

from services.collection.user_collection_query_contract import (
    UserCollectionGameQueryCriteria,
    UserCollectionPlatformQueryCriteria,
    WISHLIST_BUY_STATUS_NO,
    WISHLIST_BUY_STATUS_YES,
)
from services.library.library_query_contract import LibrarySortRule

from .library_query_sql_builder import LibraryQuerySqlBuilder
from .platform_alias_sql_selector import PlatformAliasSqlSelector


class SqlAlchemyUserCollectionQueryRepository:
    """Lit la collection utilisateur depuis les tables SQL."""

    PLATFORM_SORT_COLUMNS = {
        "name": "platform.name",
        "release_date": "platform.release_date",
        "end_date": "platform.end_date",
        "manufacturer": "platform.manufacturer",
    }

    def _platform_common_alias_select(self) -> str:
        return PlatformAliasSqlSelector.common_alias_subquery(
            self.schema_name,
            "platform.id",
        ) + " AS platform_common_alias, "
    GAME_SORT_COLUMNS = {
        "name": "game.name",
        "platform_name": "platform.name",
        "release_date": "game.release_date",
        "studio_name": "studio.name",
        "buy_date": "user_collection.buy_date",
        "grade": "user_collection.grade",
    }

    def __init__(self, schema_name: str):
        """Initialise le repository de consultation de collection.

        Args:
            schema_name (str): Nom du schema PostgreSQL.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            Aucun.
        """

        self.schema_name = schema_name

    def count_collection_games(
        self,
        connection: Connection,
        user_id: int,
        wishlist: bool | None = None,
    ) -> int:
        """Compte les jeux de la collection d'un utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant de l'utilisateur connecte.
            wishlist (bool | None): Filtre wishlist optionnel.

        Returns:
            int: Nombre de jeux rattaches a l'utilisateur.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, Any] = {"user_id": user_id}
        where_clause = self._build_user_collection_where_clause(parameters, wishlist)
        return int(connection.execute(
            text(
                f'SELECT COUNT(*) FROM "{self.schema_name}".t_user_collection user_collection '
                f"{where_clause}"
            ),
            parameters,
        ).scalar_one())

    def find_collection_file_path(self, connection: Connection, user_id: int) -> str:
        """Recherche le chemin du fichier de collection utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant de l'utilisateur connecte.

        Returns:
            str: Chemin du fichier ou chaine vide si absent.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        collection_file_path = connection.execute(
            text(
                f'SELECT collection_file_path FROM "{self.schema_name}".t_user '
                "WHERE id = :user_id"
            ),
            {"user_id": user_id},
        ).scalar_one_or_none()
        return "" if collection_file_path is None else str(collection_file_path)

    def find_max_platform_name(
        self,
        connection: Connection,
        user_id: int,
        wishlist: bool | None = None,
    ) -> str:
        """Recherche la plateforme la plus representee dans la collection.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant de l'utilisateur connecte.
            wishlist (bool | None): Filtre wishlist optionnel.

        Returns:
            str: Nom de plateforme ou chaine vide si la collection est vide.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, Any] = {"user_id": user_id}
        where_clause = self._build_user_collection_where_clause(parameters, wishlist)
        row = connection.execute(
            text(
                "SELECT platform.name "
                f'FROM "{self.schema_name}".t_user_collection user_collection '
                f'JOIN "{self.schema_name}".t_game game ON game.id = user_collection.game_id '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                f"{where_clause} "
                "GROUP BY platform.id, platform.name "
                "ORDER BY COUNT(game.id) DESC, platform.name ASC "
                "LIMIT 1"
            ),
            parameters,
        ).scalar_one_or_none()
        return "" if row is None else str(row)

    def find_price_statistics(
        self,
        connection: Connection,
        user_id: int,
        wishlist: bool | None = None,
    ) -> dict[str, Any]:
        """Calcule les statistiques de prix de la collection utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant de l'utilisateur connecte.
            wishlist (bool | None): Filtre wishlist optionnel.

        Returns:
            dict[str, Any]: Somme et moyenne des prix renseignes.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, Any] = {"user_id": user_id}
        where_clause = self._build_user_collection_where_clause(parameters, wishlist)
        rows = connection.execute(
            text(
                "SELECT "
                "COALESCE(SUM(user_collection.purchase_price), 0) AS total_value, "
                "COALESCE(AVG(user_collection.purchase_price), 0) AS average_value "
                f'FROM "{self.schema_name}".t_user_collection user_collection '
                f"{where_clause}"
            ),
            parameters,
        ).mappings()
        return dict(next(iter(rows)))

    def count_platforms_by_criteria(
        self,
        connection: Connection,
        user_id: int,
        criteria: UserCollectionPlatformQueryCriteria,
    ) -> int:
        """Compte les plateformes de l'utilisateur correspondant aux criteres.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant de l'utilisateur connecte.
            criteria (UserCollectionPlatformQueryCriteria): Criteres de recherche.

        Returns:
            int: Nombre de plateformes filtrees.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, Any] = {"user_id": user_id}
        where_clause = self._build_platform_where_clause(criteria, parameters)
        return int(connection.execute(
            text(
                "SELECT COUNT(DISTINCT platform.id) "
                f'FROM "{self.schema_name}".t_user_collection user_collection '
                f'JOIN "{self.schema_name}".t_game game ON game.id = user_collection.game_id '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                f"{where_clause}"
            ),
            parameters,
        ).scalar_one())

    def list_platforms(
        self,
        connection: Connection,
        user_id: int,
        criteria: UserCollectionPlatformQueryCriteria,
    ) -> list[dict[str, Any]]:
        """Liste les plateformes de l'utilisateur correspondant aux criteres.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant de l'utilisateur connecte.
            criteria (UserCollectionPlatformQueryCriteria): Criteres de recherche.

        Returns:
            list[dict[str, Any]]: Plateformes et statistiques de collection.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, Any] = {
            "user_id": user_id,
            **LibraryQuerySqlBuilder.build_pagination_parameters(criteria),
        }
        where_clause = self._build_platform_where_clause(criteria, parameters)
        rows = connection.execute(
            text(
                "SELECT "
                "platform.id, platform.name, platform.release_date::text AS release_date, "
                "platform.end_date::text AS end_date, platform.manufacturer, "
                "platform.description, COUNT(game.id) AS nb_games, COUNT(game.id) AS total_games, "
                "COALESCE(SUM(user_collection.purchase_price), 0) AS total_value, "
                "COALESCE(AVG(user_collection.purchase_price), 0) AS average_value "
                f'FROM "{self.schema_name}".t_user_collection user_collection '
                f'JOIN "{self.schema_name}".t_game game ON game.id = user_collection.game_id '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                f"{where_clause} "
                "GROUP BY "
                "platform.id, platform.name, platform.release_date, platform.end_date, "
                "platform.manufacturer, platform.description "
                f"{self._build_order_by(criteria.sort_rules, self.PLATFORM_SORT_COLUMNS)} "
                "LIMIT :limit OFFSET :offset"
            ),
            parameters,
        ).mappings()
        return [dict(row) for row in rows]

    def count_games_by_criteria(
        self,
        connection: Connection,
        user_id: int,
        criteria: UserCollectionGameQueryCriteria,
    ) -> int:
        """Compte les jeux de l'utilisateur correspondant aux criteres.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant de l'utilisateur connecte.
            criteria (UserCollectionGameQueryCriteria): Criteres de recherche.

        Returns:
            int: Nombre de jeux filtres.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, Any] = {"user_id": user_id}
        where_clause = self._build_game_where_clause(criteria, parameters)
        return int(connection.execute(
            text(
                "SELECT COUNT(*) "
                f'FROM "{self.schema_name}".t_user_collection user_collection '
                f'JOIN "{self.schema_name}".t_game game ON game.id = user_collection.game_id '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                f'LEFT JOIN "{self.schema_name}".t_studio studio ON studio.id = game.developer '
                f"{where_clause}"
            ),
            parameters,
        ).scalar_one())

    def list_games(
        self,
        connection: Connection,
        user_id: int,
        criteria: UserCollectionGameQueryCriteria,
    ) -> list[dict[str, Any]]:
        """Liste les jeux de l'utilisateur correspondant aux criteres.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant de l'utilisateur connecte.
            criteria (UserCollectionGameQueryCriteria): Criteres de recherche.

        Returns:
            list[dict[str, Any]]: Jeux de collection avec plateforme et studio.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, Any] = {
            "user_id": user_id,
            **LibraryQuerySqlBuilder.build_pagination_parameters(criteria),
        }
        where_clause = self._build_game_where_clause(criteria, parameters)
        rows = connection.execute(
            text(
                "SELECT "
                "game.id, game.name, game.release_date::text AS release_date, "
                "game.duplicate_flag, "
                "platform.id AS platform_id, platform.name AS platform_name, "
                "platform.end_date::text AS platform_end_date, "
                f"{self._platform_common_alias_select()}"
                "studio.id AS studio_id, studio.name AS studio_name, "
                "user_collection.wishlist, user_collection.purchase_price, "
                "user_collection.price_unit, user_collection.buy_location, "
                "user_collection.buy_date::text AS buy_date, user_collection.grade, "
                "user_collection.condition, user_collection.has_manual, "
                "user_collection.is_collector, user_collection.has_steelbook, "
                "user_collection.is_digital, user_collection.region, "
                "user_collection.description "
                f'FROM "{self.schema_name}".t_user_collection user_collection '
                f'JOIN "{self.schema_name}".t_game game ON game.id = user_collection.game_id '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                f'LEFT JOIN "{self.schema_name}".t_studio studio ON studio.id = game.developer '
                f"{where_clause} "
                f"{self._build_order_by(criteria.sort_rules, self.GAME_SORT_COLUMNS)} "
                "LIMIT :limit OFFSET :offset"
            ),
            parameters,
        ).mappings()
        return [dict(row) for row in rows]

    def find_game(
        self,
        connection: Connection,
        user_id: int,
        game_id: int,
    ) -> dict[str, Any] | None:
        """Recherche un jeu rattache a la collection de l'utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant de l'utilisateur connecte.
            game_id (int): Identifiant du jeu recherche.

        Returns:
            dict[str, Any] | None: Jeu trouve ou absence.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        row = connection.execute(
            text(
                "SELECT "
                "game.id, game.name, game.release_date::text AS release_date, "
                "game.duplicate_flag, "
                "platform.id AS platform_id, platform.name AS platform_name, "
                "platform.end_date::text AS platform_end_date, "
                f"{self._platform_common_alias_select()}"
                "studio.id AS studio_id, studio.name AS studio_name, "
                "user_collection.wishlist, user_collection.purchase_price, "
                "user_collection.price_unit, user_collection.buy_location, "
                "user_collection.buy_date::text AS buy_date, user_collection.grade, "
                "user_collection.condition, user_collection.has_manual, "
                "user_collection.is_collector, user_collection.has_steelbook, "
                "user_collection.is_digital, user_collection.region, "
                "user_collection.description "
                f'FROM "{self.schema_name}".t_user_collection user_collection '
                f'JOIN "{self.schema_name}".t_game game ON game.id = user_collection.game_id '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                f'LEFT JOIN "{self.schema_name}".t_studio studio ON studio.id = game.developer '
                "WHERE user_collection.user_id = :user_id AND game.id = :game_id"
            ),
            {"user_id": user_id, "game_id": game_id},
        ).mappings().first()
        return None if row is None else dict(row)

    def _build_user_collection_where_clause(
        self,
        parameters: dict[str, Any],
        wishlist: bool | None,
    ) -> str:
        filters = ["user_collection.user_id = :user_id"]
        if wishlist is not None:
            filters.append("user_collection.wishlist = :wishlist")
            parameters["wishlist"] = wishlist
        return "WHERE " + " AND ".join(filters)

    def _build_platform_where_clause(
        self,
        criteria: UserCollectionPlatformQueryCriteria,
        parameters: dict[str, Any],
    ) -> str:
        filters = ["user_collection.user_id = :user_id"]
        self._append_text_filter(
            filters,
            parameters,
            "platform.name",
            criteria.normalized_name,
            "platform_name_pattern",
        )
        if criteria.wishlist is not None:
            filters.append("user_collection.wishlist = :wishlist")
            parameters["wishlist"] = criteria.wishlist
        return "WHERE " + " AND ".join(filters)

    @staticmethod
    def _wishlist_buy_information_expression() -> str:
        return (
            "(user_collection.buy_date IS NOT NULL "
            "OR NULLIF(TRIM(user_collection.buy_location), '') IS NOT NULL "
            "OR user_collection.purchase_price IS NOT NULL)"
        )

    def _build_game_where_clause(
        self,
        criteria: UserCollectionGameQueryCriteria,
        parameters: dict[str, Any],
    ) -> str:
        filters = ["user_collection.user_id = :user_id"]
        self._append_text_filter(filters, parameters, "game.name", criteria.normalized_name, "name_pattern")
        self._append_text_filter(
            filters,
            parameters,
            "studio.name",
            criteria.normalized_studio_name,
            "studio_name_pattern",
        )
        self._append_text_filter(
            filters,
            parameters,
            "platform.name",
            criteria.normalized_platform_name,
            "platform_name_pattern",
        )
        if criteria.platform_id is not None:
            filters.append("platform.id = :platform_id")
            parameters["platform_id"] = criteria.platform_id
        if criteria.release_date_from is not None:
            filters.append("game.release_date >= :release_date_from")
            parameters["release_date_from"] = criteria.release_date_from
        if criteria.release_date_to is not None:
            filters.append("game.release_date <= :release_date_to")
            parameters["release_date_to"] = criteria.release_date_to
        if criteria.wishlist is not None:
            filters.append("user_collection.wishlist = :wishlist")
            parameters["wishlist"] = criteria.wishlist
        if criteria.wishlist_buy_status == WISHLIST_BUY_STATUS_YES:
            filters.append(self._wishlist_buy_information_expression())
        elif criteria.wishlist_buy_status == WISHLIST_BUY_STATUS_NO:
            filters.append(f"NOT ({self._wishlist_buy_information_expression()})")
        return "WHERE " + " AND ".join(filters)

    def _append_text_filter(
        self,
        filters: list[str],
        parameters: dict[str, Any],
        column_expression: str,
        normalized_value: str,
        parameter_name: str,
    ) -> None:
        if not normalized_value:
            return
        parameters[parameter_name] = f"%{normalized_value}%"
        parameters["accented_characters"] = LibraryQuerySqlBuilder.ACCENTED_CHARACTERS
        parameters["plain_characters"] = LibraryQuerySqlBuilder.PLAIN_CHARACTERS
        filters.append(
            "TRANSLATE(LOWER("
            f"{column_expression}"
            "), :accented_characters, :plain_characters) "
            f"LIKE :{parameter_name}"
        )

    def _build_order_by(
        self,
        sort_rules: tuple[LibrarySortRule, ...],
        allowed_columns: dict[str, str],
    ) -> str:
        expressions = []
        for sort_rule in sort_rules:
            column_expression = allowed_columns.get(sort_rule.column, allowed_columns["name"])
            direction = "DESC" if sort_rule.direction == "desc" else "ASC"
            expressions.append(f"{column_expression} {direction}")
        if not any(expression.startswith(f"{allowed_columns['name']} ") for expression in expressions):
            expressions.append(f"{allowed_columns['name']} ASC")
        return "ORDER BY " + ", ".join(expressions)
