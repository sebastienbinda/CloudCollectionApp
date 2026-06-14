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

from services.library.library_query_contract import LibraryQueryCriteria, LibrarySortRule
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer

from .platform_catalog_cache import PlatformCatalogCache


class SqlAlchemyPlatformRepository:
    """Persiste les plateformes de collection dans `t_platform`."""

    def __init__(
        self,
        schema_name: str,
        name_normalizer: UserCollectionNameNormalizer,
        platform_catalog_cache: PlatformCatalogCache | None = None,
    ):
        """Initialise le repository des plateformes.

        Args:
            schema_name (str): Nom du schema PostgreSQL.
            name_normalizer (UserCollectionNameNormalizer): Normaliseur metier.
            platform_catalog_cache (PlatformCatalogCache | None): Cache serveur.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name
        self.name_normalizer = name_normalizer
        self.platform_catalog_cache = platform_catalog_cache or PlatformCatalogCache()

    def load_ids_by_key(self, connection: Connection) -> dict[str, int]:
        """Charge les plateformes existantes par cle de comparaison.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            dict[str, int]: Identifiants des plateformes.
        """

        return {
            self.name_normalizer.comparison_key(row["name"]): int(row["id"])
            for row in self._cached_platform_rows(connection)
        }

    def load_catalog_rows(self, connection: Connection) -> list[dict[str, object]]:
        """Charge les plateformes du catalogue applicatif depuis le cache.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            list[dict[str, object]]: Plateformes candidates au matching.
        """

        return self._cached_platform_rows(connection)

    def insert(self, connection: Connection, platform_name: str) -> int:
        """Insere une plateforme minimale.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_name (str): Nom de plateforme a creer.

        Returns:
            int: Identifiant genere.
        """

        platform_id = int(connection.execute(
            text(
                f'INSERT INTO "{self.schema_name}".t_platform (name) '
                "VALUES (:name) RETURNING id"
            ),
            {"name": platform_name},
        ).scalar_one())
        self.platform_catalog_cache.invalidate(self.schema_name)
        return platform_id

    def count_public_library_platforms(self, connection: Connection) -> int:
        """Compte toutes les plateformes globales de reference.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            int: Nombre total de plateformes globales.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        return len(self._cached_platform_rows(connection))

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

        rows = self._filter_platform_rows(self._cached_platform_rows(connection), criteria)
        return len(rows)

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

        rows = self._filter_platform_rows(self._cached_platform_rows(connection), criteria)
        rows = self._sort_platform_rows(rows, criteria)
        offset = criteria.page_request.offset
        limit = criteria.page_request.size
        return rows[offset:offset + limit]

    def _cached_platform_rows(self, connection: Connection) -> list[dict[str, object]]:
        return self.platform_catalog_cache.remember(
            self.schema_name,
            lambda: self._load_platform_rows(connection),
        )

    def _load_platform_rows(self, connection: Connection) -> list[dict[str, object]]:
        rows = connection.execute(
            text(
                "SELECT "
                "platform.id, platform.name, platform.release_date, platform.end_date, "
                "platform.manufacturer, platform.description, COUNT(game.id) AS total_games "
                f'FROM "{self.schema_name}".t_platform platform '
                f'LEFT JOIN "{self.schema_name}".t_game game ON game.platform = platform.id '
                "GROUP BY platform.id, platform.name, platform.release_date, "
                "platform.end_date, platform.manufacturer, platform.description"
            )
        ).mappings()
        return [dict(row) for row in rows]

    def _filter_platform_rows(
        self,
        rows: list[dict[str, object]],
        criteria: LibraryQueryCriteria,
    ) -> list[dict[str, object]]:
        if not criteria.normalized_name:
            return rows
        return [
            row
            for row in rows
            if criteria.normalized_name in self.name_normalizer.comparison_key(row["name"])
        ]

    def _sort_platform_rows(
        self,
        rows: list[dict[str, object]],
        criteria: LibraryQueryCriteria,
    ) -> list[dict[str, object]]:
        sorted_rows = list(rows)
        sort_rules = list(criteria.sort_rules)
        if not any(sort_rule.column == "name" for sort_rule in sort_rules):
            sort_rules.append(LibrarySortRule("name", "asc"))
        for sort_rule in reversed(sort_rules):
            sorted_rows.sort(
                key=lambda row, column=sort_rule.column: self._sort_value(row.get(column)),
                reverse=sort_rule.direction == "desc",
            )
        return sorted_rows

    def _sort_value(self, value: object) -> tuple[bool, object]:
        if isinstance(value, str):
            return value == "", value.lower()
        return value is None, value
