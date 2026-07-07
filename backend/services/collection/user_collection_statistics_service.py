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
# Description : service metier des statistiques detaillees de collection.

from typing import Any, Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from services.database.database_configuration import DatabaseConfiguration
from services.database.user_collection_statistics_repository import (
    SqlAlchemyUserCollectionStatisticsRepository,
)

EngineFactory = Callable[[str], Engine]


class UserCollectionStatisticsService:
    """Orchestre les statistiques detaillees de collection utilisateur."""

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        repository: Any | None = None,
        engine: Engine | None = None,
        engine_factory: EngineFactory = create_engine,
    ):
        """Initialise le service de statistiques de collection.

        Args:
            configuration (DatabaseConfiguration): Configuration de connexion SQL.
            repository (Any | None): Repository injectable en test.
            engine (Engine | None): Moteur SQLAlchemy injectable en test.
            engine_factory (EngineFactory): Fabrique de moteur SQLAlchemy.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si aucune URL de base de donnees n'est configuree.
        """

        configuration.validate()
        if engine is None and not configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour consulter les statistiques.")
        self.engine = engine or engine_factory(configuration.database_url)
        self.repository = repository or SqlAlchemyUserCollectionStatisticsRepository(
            configuration.schema_name,
        )

    def get_statistics(self, user_id: int, platform_id: int | None = None) -> dict[str, Any]:
        """Retourne les statistiques detaillees de la collection possedee.

        Args:
            user_id (int): Identifiant du proprietaire de collection.
            platform_id (int | None): Plateforme optionnelle filtrant les distributions temporelles.

        Returns:
            dict[str, Any]: Statistiques detaillees serialisables.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une requete.
        """

        with self.engine.connect() as connection:
            platforms = self.repository.list_platform_distribution(connection, user_id)
            release_years = self.repository.list_release_year_distribution(
                connection,
                user_id,
                platform_id,
            )
            purchase_years = self.repository.list_purchase_year_distribution(
                connection,
                user_id,
                platform_id,
            )
            top_rated_games = self.repository.list_top_rated_games(connection, user_id)
        total_games = sum(int(row.get("games_count") or 0) for row in platforms)
        return {
            "total_games": total_games,
            "platform_distribution": self._platform_distribution_payload(platforms, total_games),
            "release_year_distribution": self._year_distribution_payload(release_years),
            "purchase_year_distribution": self._year_distribution_payload(purchase_years),
            "top_rated_games": self._top_rated_games_payload(top_rated_games),
        }

    def _platform_distribution_payload(
        self,
        rows: list[dict[str, Any]],
        total_games: int,
    ) -> list[dict[str, Any]]:
        return [
            {
                "platform_id": int(row["platform_id"]),
                "platform_name": str(row.get("platform_name") or ""),
                "games_count": int(row.get("games_count") or 0),
                "ratio": self._ratio(row.get("games_count"), total_games),
            }
            for row in rows
        ]

    def _year_distribution_payload(self, rows: list[dict[str, Any]]) -> list[dict[str, int]]:
        return [
            {
                "year": int(row["year"]),
                "games_count": int(row.get("games_count") or 0),
            }
            for row in rows
        ]

    def _top_rated_games_payload(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "id": int(row["id"]),
                "name": str(row.get("name") or ""),
                "platform_name": str(row.get("platform_name") or ""),
                "release_date": str(row.get("release_date") or ""),
                "buy_date": str(row.get("buy_date") or ""),
                "grade": str(row.get("grade") or ""),
            }
            for row in rows
        ]

    @staticmethod
    def _ratio(games_count: Any, total_games: int) -> float:
        if total_games <= 0:
            return 0
        return round((int(games_count or 0) / total_games) * 100, 2)
