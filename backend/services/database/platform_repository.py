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
# Description : repository SQL des plateformes de collection.

from sqlalchemy import text
from sqlalchemy.engine import Connection

from services.library.library_query_contract import LibraryQueryCriteria
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer

from .library_query_sql_builder import LibraryQuerySqlBuilder


class SqlAlchemyPlatformRepository:
    """Persiste les plateformes de collection dans `t_platform`."""

    UNKNOWN_STATUS = "UNKNOWN"
    LIBRARY_SORT_COLUMNS = {
        "name": "platform.name",
        "release_date": "platform.release_date",
        "manufacturer": "platform.manufacturer",
    }

    def __init__(self, schema_name: str, name_normalizer: UserCollectionNameNormalizer):
        """Initialise le repository des plateformes.

        Args:
            schema_name (str): Nom du schema PostgreSQL.
            name_normalizer (UserCollectionNameNormalizer): Normaliseur metier.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name
        self.name_normalizer = name_normalizer

    def load_ids_by_key(self, connection: Connection) -> dict[str, int]:
        """Charge les plateformes existantes par cle de comparaison.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            dict[str, int]: Identifiants des plateformes.
        """

        return {
            self.name_normalizer.comparison_key(row["name"]): int(row["id"])
            for row in connection.execute(
                text(f'SELECT id, name FROM "{self.schema_name}".t_platform')
            ).mappings()
        }

    def insert(self, connection: Connection, platform_name: str) -> int:
        """Insere une plateforme avec le statut `UNKNOWN`.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_name (str): Nom de plateforme a creer.

        Returns:
            int: Identifiant genere.
        """

        return int(connection.execute(
            text(
                f'INSERT INTO "{self.schema_name}".t_platform (name, status) '
                "VALUES (:name, :status) RETURNING id"
            ),
            {"name": platform_name, "status": self.UNKNOWN_STATUS},
        ).scalar_one())

    def count_public_library_platforms(self, connection: Connection) -> int:
        """Compte toutes les plateformes globales de reference.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            int: Nombre total de plateformes globales.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        return int(connection.execute(
            text(f'SELECT COUNT(*) FROM "{self.schema_name}".t_platform')
        ).scalar_one())

    def count_public_library_platforms_by_criteria(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> int:
        """Compte les plateformes globales correspondant aux criteres publics.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres de recherche Bibliotheque.

        Returns:
            int: Nombre de plateformes correspondant aux criteres.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, object] = {}
        where_clause = LibraryQuerySqlBuilder.build_name_filter(
            criteria,
            "platform.name",
            parameters,
        )
        return int(connection.execute(
            text(
                f'SELECT COUNT(*) FROM "{self.schema_name}".t_platform platform '
                f"{where_clause}"
            ),
            parameters,
        ).scalar_one())

    def list_public_library_platforms(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> list[dict[str, object]]:
        """Liste les plateformes globales paginees pour la Bibliotheque.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres de recherche, tri et pagination.

        Returns:
            list[dict[str, object]]: Plateformes publiques avec compteur de jeux.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, object] = LibraryQuerySqlBuilder.build_pagination_parameters(criteria)
        where_clause = LibraryQuerySqlBuilder.build_name_filter(criteria, "platform.name", parameters)
        order_by_clause = LibraryQuerySqlBuilder.build_order_by(criteria, self.LIBRARY_SORT_COLUMNS)
        rows = connection.execute(
            text(
                "SELECT "
                "platform.id, platform.name, platform.release_date, platform.manufacturer, "
                "platform.description, platform.status, COUNT(game.id) AS total_games "
                f'FROM "{self.schema_name}".t_platform platform '
                f'LEFT JOIN "{self.schema_name}".t_game game ON game.platform = platform.id '
                f"{where_clause} "
                "GROUP BY platform.id, platform.name, platform.release_date, "
                "platform.manufacturer, platform.description, platform.status "
                f"{order_by_clause} "
                "LIMIT :limit OFFSET :offset"
            ),
            parameters,
        ).mappings()
        return [dict(row) for row in rows]
