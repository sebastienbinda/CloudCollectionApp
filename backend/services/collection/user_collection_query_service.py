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
# Description : service metier de consultation SQL de collection utilisateur.

from datetime import date, datetime
from math import ceil
from typing import Any, Callable, Protocol

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine

from services.database.database_configuration import DatabaseConfiguration
from services.database.user_collection_query_repository import (
    SqlAlchemyUserCollectionQueryRepository,
)

from .user_collection_query_contract import (
    UserCollectionGameQueryCriteria,
    UserCollectionPlatformQueryCriteria,
)

EngineFactory = Callable[[str], Engine]


class UserCollectionQueryRepository(Protocol):
    """Decrit les lectures SQL attendues pour la collection utilisateur."""

    def count_collection_games(self, connection: Connection, user_id: int) -> int:
        """Compte les jeux rattaches a l'utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.

        Returns:
            int: Nombre de jeux.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def find_max_platform_name(self, connection: Connection, user_id: int) -> str:
        """Retourne la plateforme la plus representee.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.

        Returns:
            str: Nom de plateforme ou chaine vide.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def count_platforms_by_criteria(
        self,
        connection: Connection,
        user_id: int,
        criteria: UserCollectionPlatformQueryCriteria,
    ) -> int:
        """Compte les plateformes de l'utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionPlatformQueryCriteria): Criteres de recherche.

        Returns:
            int: Nombre de plateformes.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def list_platforms(
        self,
        connection: Connection,
        user_id: int,
        criteria: UserCollectionPlatformQueryCriteria,
    ) -> list[dict[str, Any]]:
        """Liste les plateformes de l'utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionPlatformQueryCriteria): Criteres de recherche.

        Returns:
            list[dict[str, Any]]: Plateformes lues.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def count_games_by_criteria(
        self,
        connection: Connection,
        user_id: int,
        criteria: UserCollectionGameQueryCriteria,
    ) -> int:
        """Compte les jeux de l'utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionGameQueryCriteria): Criteres de recherche.

        Returns:
            int: Nombre de jeux.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def list_games(
        self,
        connection: Connection,
        user_id: int,
        criteria: UserCollectionGameQueryCriteria,
    ) -> list[dict[str, Any]]:
        """Liste les jeux de l'utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.
            criteria (UserCollectionGameQueryCriteria): Criteres de recherche.

        Returns:
            list[dict[str, Any]]: Jeux lus.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """


class UserCollectionQueryService:
    """Orchestre la consultation SQL de la collection utilisateur."""

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        repository: UserCollectionQueryRepository | None = None,
        engine: Engine | None = None,
        engine_factory: EngineFactory = create_engine,
    ):
        """Initialise le service de consultation de collection.

        Args:
            configuration (DatabaseConfiguration): Configuration de connexion SQL.
            repository (UserCollectionQueryRepository | None): Repository injectable.
            engine (Engine | None): Moteur SQLAlchemy injectable en test.
            engine_factory (EngineFactory): Fabrique de moteur SQLAlchemy.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si aucune URL de base de donnees n'est configuree.
        """

        configuration.validate()
        if engine is None and not configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour consulter la collection.")
        self.configuration = configuration
        self.engine = engine or engine_factory(configuration.database_url)
        self.repository = repository or SqlAlchemyUserCollectionQueryRepository(
            configuration.schema_name,
        )

    def get_statistics(self, user_id: int) -> dict[str, Any]:
        """Retourne les statistiques globales de collection utilisateur.

        Args:
            user_id (int): Identifiant de l'utilisateur connecte.

        Returns:
            dict[str, Any]: Statistiques globales serialisables.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une requete.
        """

        with self.engine.connect() as connection:
            total = self.repository.count_collection_games(connection, user_id)
            max_platform = (
                self.repository.find_max_platform_name(connection, user_id)
                if total
                else ""
            )
        return {
            "total": total,
            "total_value": 0,
            "average_value": 0,
            "max_platform": max_platform,
        }

    def list_platforms(
        self,
        user_id: int,
        criteria: UserCollectionPlatformQueryCriteria,
    ) -> dict[str, Any]:
        """Liste les plateformes de collection au format API.

        Args:
            user_id (int): Identifiant de l'utilisateur connecte.
            criteria (UserCollectionPlatformQueryCriteria): Criteres de recherche.

        Returns:
            dict[str, Any]: Payload contenant `page` et `platforms`.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une requete.
        """

        with self.engine.connect() as connection:
            total_elements = self.repository.count_platforms_by_criteria(
                connection,
                user_id,
                criteria,
            )
            rows = self.repository.list_platforms(connection, user_id, criteria)
        return {
            "page": self._page_payload(criteria, total_elements),
            "platforms": [self._platform_payload(row) for row in rows],
        }

    def list_games(
        self,
        user_id: int,
        criteria: UserCollectionGameQueryCriteria,
    ) -> dict[str, Any]:
        """Liste les jeux de collection au format API.

        Args:
            user_id (int): Identifiant de l'utilisateur connecte.
            criteria (UserCollectionGameQueryCriteria): Criteres de recherche.

        Returns:
            dict[str, Any]: Payload contenant `page` et `games`.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une requete.
        """

        if criteria.has_invalid_platform_id:
            return {
                "page": self._page_payload(criteria, 0),
                "games": [],
            }
        with self.engine.connect() as connection:
            total_elements = self.repository.count_games_by_criteria(
                connection,
                user_id,
                criteria,
            )
            rows = self.repository.list_games(connection, user_id, criteria)
        return {
            "page": self._page_payload(criteria, total_elements),
            "games": [self._game_payload(row) for row in rows],
        }

    def _page_payload(
        self,
        criteria: UserCollectionPlatformQueryCriteria | UserCollectionGameQueryCriteria,
        total_elements: int,
    ) -> dict[str, int]:
        page_size = criteria.page_request.size
        return {
            "totalElements": total_elements,
            "page": criteria.page_request.page,
            "size": page_size,
            "totalPages": ceil(total_elements / page_size) if total_elements else 0,
        }

    def _platform_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": int(row["id"]),
            "name": self._text_value(row.get("name")),
            "nb_games": self._integer_value(row.get("nb_games")),
            "total_value": 0,
            "average_value": 0,
        }

    def _game_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": int(row["id"]),
            "name": self._text_value(row.get("name")),
            "platform_name": self._text_value(row.get("platform_name")),
            "platform_id": int(row["platform_id"]),
            "release_date": self._date_value(row.get("release_date")),
            "studio_name": self._text_value(row.get("studio_name")),
            "studio_id": self._optional_integer_value(row.get("studio_id")),
            "version": "",
            "buy_date": "",
            "buy_location": "",
            "grade": "",
        }

    def _date_value(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return self._text_value(value)

    def _text_value(self, value: Any) -> str:
        return "" if value is None else str(value)

    def _integer_value(self, value: Any) -> int:
        return int(value or 0)

    def _optional_integer_value(self, value: Any) -> int | None:
        return None if value is None else int(value)
