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
# Description : repository SQL des studios de collection.

from sqlalchemy import text
from sqlalchemy.engine import Connection

from services.library import LibraryQueryCriteria
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer

from .library_query_sql_builder import LibraryQuerySqlBuilder


class SqlAlchemyStudioRepository:
    """Persiste les studios de collection dans `t_studio`."""

    UNKNOWN_STATUS = "UNKNOWN"
    LIBRARY_SORT_COLUMNS = {
        "name": "studio.name",
        "country": "studio.country",
        "creation_date": "studio.creation_date",
    }

    def __init__(self, schema_name: str, name_normalizer: UserCollectionNameNormalizer):
        """Initialise le repository des studios.

        Args:
            schema_name (str): Nom du schema PostgreSQL.
            name_normalizer (UserCollectionNameNormalizer): Normaliseur metier.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name
        self.name_normalizer = name_normalizer

    def load_ids_by_key(self, connection: Connection) -> dict[str, int]:
        """Charge les studios existants par cle de comparaison.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            dict[str, int]: Identifiants des studios.
        """

        return {
            self.name_normalizer.comparison_key(row["name"]): int(row["id"])
            for row in connection.execute(
                text(f'SELECT id, name FROM "{self.schema_name}".t_studio')
            ).mappings()
        }

    def insert(self, connection: Connection, studio_name: str) -> int:
        """Insere un studio avec le statut `UNKNOWN`.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            studio_name (str): Nom de studio a creer.

        Returns:
            int: Identifiant genere.
        """

        return int(connection.execute(
            text(
                f'INSERT INTO "{self.schema_name}".t_studio (name, status) '
                "VALUES (:name, :status) RETURNING id"
            ),
            {"name": studio_name, "status": self.UNKNOWN_STATUS},
        ).scalar_one())

    def count_public_library_studios(self, connection: Connection) -> int:
        """Compte tous les studios globaux de reference.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            int: Nombre total de studios globaux.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        return int(connection.execute(
            text(f'SELECT COUNT(*) FROM "{self.schema_name}".t_studio')
        ).scalar_one())

    def count_public_library_studios_by_criteria(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> int:
        """Compte les studios globaux correspondant aux criteres publics.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres de recherche Bibliotheque.

        Returns:
            int: Nombre de studios correspondant aux criteres.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, object] = {}
        where_clause = LibraryQuerySqlBuilder.build_name_filter(criteria, "studio.name", parameters)
        return int(connection.execute(
            text(
                f'SELECT COUNT(*) FROM "{self.schema_name}".t_studio studio '
                f"{where_clause}"
            ),
            parameters,
        ).scalar_one())

    def list_public_library_studios(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> list[dict[str, object]]:
        """Liste les studios globaux pages pour la Bibliotheque.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres de recherche, tri et pagination.

        Returns:
            list[dict[str, object]]: Studios publics avec compteurs de jeux.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, object] = LibraryQuerySqlBuilder.build_pagination_parameters(criteria)
        where_clause = LibraryQuerySqlBuilder.build_name_filter(criteria, "studio.name", parameters)
        order_by_clause = LibraryQuerySqlBuilder.build_order_by(criteria, self.LIBRARY_SORT_COLUMNS)
        rows = connection.execute(
            text(
                "SELECT "
                "studio.id, studio.name, studio.country, studio.city, "
                "studio.creation_date, studio.status, "
                "COUNT(DISTINCT editor_game.id) AS editor_total_games, "
                "COUNT(DISTINCT developer_game.id) AS developer_total_games "
                f'FROM "{self.schema_name}".t_studio studio '
                f'LEFT JOIN "{self.schema_name}".t_game editor_game '
                "ON editor_game.editor = studio.id "
                f'LEFT JOIN "{self.schema_name}".t_game developer_game '
                "ON developer_game.developer = studio.id "
                f"{where_clause} "
                "GROUP BY studio.id, studio.name, studio.country, studio.city, "
                "studio.creation_date, studio.status "
                f"{order_by_clause} "
                "LIMIT :limit OFFSET :offset"
            ),
            parameters,
        ).mappings()
        return [dict(row) for row in rows]
