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
# Description : repository SQL des jeux de collection.

from sqlalchemy import text
from sqlalchemy.engine import Connection

from services.library.library_query_contract import LibraryQueryCriteria
from services.collection.imports import CollectionImportGame
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer
from services.collection.imports import CollectionImportDateValidator

from .library_query_sql_builder import LibraryQuerySqlBuilder


class SqlAlchemyGameRepository:
    """Persiste les jeux de collection dans `t_game`."""

    LIBRARY_SORT_COLUMNS = {
        "name": "game.name",
        "release_date": "game.release_date",
        "developer": "developer_studio.name",
        "platform": "platform.name",
    }

    def __init__(self, schema_name: str, name_normalizer: UserCollectionNameNormalizer):
        """Initialise le repository des jeux.

        Args:
            schema_name (str): Nom du schema PostgreSQL.
            name_normalizer (UserCollectionNameNormalizer): Normaliseur metier.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name
        self.name_normalizer = name_normalizer
        self.date_validator = CollectionImportDateValidator()

    def load_references_by_key(
        self,
        connection: Connection,
    ) -> dict[tuple[str, str], tuple[int, str]]:
        """Charge les jeux existants par cle avec leur nom d'origine.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            dict[tuple[str, str], tuple[int, str]]: Identifiants et noms des jeux.
        """

        rows = connection.execute(
            text(
                f'SELECT game.id, game.name, platform.name AS platform_name '
                f'FROM "{self.schema_name}".t_game game '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform'
            )
        ).mappings()
        references = {
            (
                self.name_normalizer.comparison_key(row["platform_name"]),
                self.name_normalizer.comparison_key(row["name"]),
            ): (int(row["id"]), str(row["name"] or ""))
            for row in rows
        }
        alias_rows = connection.execute(
            text(
                f'SELECT game.id, game.name, alias.name AS alias_name, '
                "platform.name AS platform_name "
                f'FROM "{self.schema_name}".t_game_alias alias '
                f'JOIN "{self.schema_name}".t_game game ON game.id = alias.game_id '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform'
            )
        ).mappings()
        for row in alias_rows:
            references.setdefault(
                (
                    self.name_normalizer.comparison_key(row["platform_name"]),
                    self.name_normalizer.comparison_key(row["alias_name"]),
                ),
                (int(row["id"]), str(row["name"] or "")),
            )
        return references

    def load_ids_by_key(self, connection: Connection) -> dict[tuple[str, str], int]:
        """Charge les jeux existants par cle plateforme/nom.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            dict[tuple[str, str], int]: Identifiants des jeux.
        """

        return {
            game_key: game_reference[0]
            for game_key, game_reference in self.load_references_by_key(connection).items()
        }

    def insert(
        self,
        connection: Connection,
        game: CollectionImportGame,
        platform_id: int,
        studio_id: int | None,
    ) -> int:
        """Insere un jeu absent.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game (CollectionImportGame): Jeu a creer.
            platform_id (int): Identifiant de plateforme.
            studio_id (int | None): Identifiant du studio developpeur.

        Returns:
            int: Identifiant genere.
        """

        return int(connection.execute(
            text(
                f'INSERT INTO "{self.schema_name}".t_game '
                "(name, release_date, developer, editor, platform, description, duplicate_flag) "
                "VALUES (:name, :release_date, :developer, NULL, :platform, NULL, FALSE) "
                "RETURNING id"
            ),
            {
                "name": game.name,
                "release_date": self.date_validator.validate_release_date(game.release_date),
                "developer": studio_id,
                "platform": platform_id,
            },
        ).scalar_one())

    def game_key(self, game: CollectionImportGame) -> tuple[str, str]:
        """Construit la cle fonctionnelle d'un jeu.

        Args:
            game (CollectionImportGame): Jeu importe.

        Returns:
            tuple[str, str]: Cle plateforme/nom.
        """

        return (
            self.name_normalizer.comparison_key(game.platform_name),
            self.name_normalizer.comparison_key(game.name),
        )

    def count_public_library_games(self, connection: Connection) -> int:
        """Compte tous les jeux globaux de reference.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            int: Nombre total de jeux globaux.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        return int(connection.execute(
            text(f'SELECT COUNT(*) FROM "{self.schema_name}".t_game')
        ).scalar_one())

    def count_public_library_games_by_criteria(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> int:
        """Compte les jeux globaux correspondant aux criteres publics.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres de recherche Bibliotheque.

        Returns:
            int: Nombre de jeux correspondant aux criteres.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, object] = {}
        where_clause = self._build_library_games_where_clause(criteria, parameters)
        return int(connection.execute(
            text(
                f'SELECT COUNT(*) FROM "{self.schema_name}".t_game game '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                f"{where_clause}"
            ),
            parameters,
        ).scalar_one())

    def list_public_library_games(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> list[dict[str, object]]:
        """Liste les jeux globaux pages pour la Bibliotheque.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres de recherche, tri et pagination.

        Returns:
            list[dict[str, object]]: Jeux publics avec noms de studios et plateforme.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        parameters: dict[str, object] = LibraryQuerySqlBuilder.build_pagination_parameters(criteria)
        where_clause = self._build_library_games_where_clause(criteria, parameters)
        order_by_clause = LibraryQuerySqlBuilder.build_order_by(criteria, self.LIBRARY_SORT_COLUMNS)
        rows = connection.execute(
            text(
                "SELECT "
                "game.id, game.name, game.release_date, game.description, game.duplicate_flag, "
                "game.developer AS developer_id, developer_studio.name AS developer, "
                "game.editor AS editor_id, editor_studio.name AS editor, "
                "game.platform AS platform_id, platform.name AS platform "
                f'FROM "{self.schema_name}".t_game game '
                f'LEFT JOIN "{self.schema_name}".t_studio developer_studio '
                "ON developer_studio.id = game.developer "
                f'LEFT JOIN "{self.schema_name}".t_studio editor_studio '
                "ON editor_studio.id = game.editor "
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                f"{where_clause} "
                f"{order_by_clause} "
                "LIMIT :limit OFFSET :offset"
            ),
            parameters,
        ).mappings()
        return [dict(row) for row in rows]

    def find_public_library_game(
        self,
        connection: Connection,
        game_id: int,
    ) -> dict[str, object] | None:
        """Recherche un jeu global par identifiant.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_id (int): Identifiant du jeu recherche.

        Returns:
            dict[str, object] | None: Jeu public trouve ou absence.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        row = connection.execute(
            text(
                "SELECT "
                "game.id, game.name, game.release_date, game.description, game.duplicate_flag, "
                "developer_studio.name AS developer, editor_studio.name AS editor, "
                "platform.name AS platform "
                f'FROM "{self.schema_name}".t_game game '
                f'LEFT JOIN "{self.schema_name}".t_studio developer_studio '
                "ON developer_studio.id = game.developer "
                f'LEFT JOIN "{self.schema_name}".t_studio editor_studio '
                "ON editor_studio.id = game.editor "
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform '
                "WHERE game.id = :game_id"
            ),
            {"game_id": game_id},
        ).mappings().first()
        return None if row is None else dict(row)

    def _build_library_games_where_clause(
        self,
        criteria: LibraryQueryCriteria,
        parameters: dict[str, object],
    ) -> str:
        """Construit les filtres publics applicables aux jeux Bibliotheque.

        Args:
            criteria (LibraryQueryCriteria): Criteres de recherche Bibliotheque.
            parameters (dict[str, object]): Parametres SQL a enrichir.

        Returns:
            str: Clause SQL `WHERE`, ou chaine vide sans filtre.
        """

        filters = []
        name_clause = LibraryQuerySqlBuilder.build_name_filter(
            criteria,
            "game.name",
            parameters,
        )
        if name_clause:
            filters.append(name_clause.removeprefix("WHERE "))

        if criteria.normalized_platform:
            parameters["platform_key"] = criteria.normalized_platform.replace(" ", "")
            parameters["accented_characters"] = LibraryQuerySqlBuilder.ACCENTED_CHARACTERS
            parameters["plain_characters"] = LibraryQuerySqlBuilder.PLAIN_CHARACTERS
            filters.append(
                "REPLACE(TRANSLATE(LOWER(platform.name), :accented_characters, "
                ":plain_characters), ' ', '') = :platform_key"
            )

        return f"WHERE {' AND '.join(filters)}" if filters else ""
