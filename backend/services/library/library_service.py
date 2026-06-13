#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-24
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : service metier de consultation publique de la Bibliotheque.

from datetime import date, datetime
from math import ceil
from typing import Any, Callable, Protocol

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine

from services.database.database_configuration import DatabaseConfiguration
from services.database.game_repository import SqlAlchemyGameRepository
from services.database.platform_repository import SqlAlchemyPlatformRepository
from services.database.studio_repository import SqlAlchemyStudioRepository
from services.users import UserCollectionNameNormalizer

from .library_query_contract import LibraryQueryCriteria

EngineFactory = Callable[[str], Engine]


class PublicLibraryPlatformRepository(Protocol):
    """Decrit les lectures publiques attendues pour les plateformes."""

    def count_public_library_platforms(self, connection: Connection) -> int:
        """Compte les plateformes globales.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            int: Nombre total de plateformes.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def count_public_library_platforms_by_criteria(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> int:
        """Compte les plateformes correspondant aux criteres.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres Bibliotheque.

        Returns:
            int: Nombre de plateformes filtrees.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def list_public_library_platforms(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> list[dict[str, Any]]:
        """Liste les plateformes correspondant aux criteres.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres Bibliotheque.

        Returns:
            list[dict[str, Any]]: Plateformes lues.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """


class PublicLibraryStudioRepository(Protocol):
    """Decrit les lectures publiques attendues pour les studios."""

    def count_public_library_studios(self, connection: Connection) -> int:
        """Compte les studios globaux.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            int: Nombre total de studios.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def count_public_library_studios_by_criteria(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> int:
        """Compte les studios correspondant aux criteres.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres Bibliotheque.

        Returns:
            int: Nombre de studios filtres.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def list_public_library_studios(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> list[dict[str, Any]]:
        """Liste les studios correspondant aux criteres.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres Bibliotheque.

        Returns:
            list[dict[str, Any]]: Studios lus.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """


class PublicLibraryGameRepository(Protocol):
    """Decrit les lectures publiques attendues pour les jeux."""

    def count_public_library_games(self, connection: Connection) -> int:
        """Compte les jeux globaux.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            int: Nombre total de jeux.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def count_public_library_games_by_criteria(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> int:
        """Compte les jeux correspondant aux criteres.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres Bibliotheque.

        Returns:
            int: Nombre de jeux filtres.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def list_public_library_games(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> list[dict[str, Any]]:
        """Liste les jeux correspondant aux criteres.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            criteria (LibraryQueryCriteria): Criteres Bibliotheque.

        Returns:
            list[dict[str, Any]]: Jeux lus.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """


class LibraryService:
    """Orchestre la consultation publique de la base globale."""

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        platform_repository: PublicLibraryPlatformRepository | None = None,
        studio_repository: PublicLibraryStudioRepository | None = None,
        game_repository: PublicLibraryGameRepository | None = None,
        engine: Engine | None = None,
        engine_factory: EngineFactory = create_engine,
        name_normalizer: UserCollectionNameNormalizer | None = None,
    ):
        """Initialise le service Bibliotheque.

        Args:
            configuration (DatabaseConfiguration): Configuration de connexion SQL.
            platform_repository (PublicLibraryPlatformRepository | None): Repository plateformes.
            studio_repository (PublicLibraryStudioRepository | None): Repository studios.
            game_repository (PublicLibraryGameRepository | None): Repository jeux.
            engine (Engine | None): Moteur SQLAlchemy injectable en test.
            engine_factory (EngineFactory): Fabrique de moteur SQLAlchemy.
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur partage.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si aucune URL de base de donnees n'est configuree.
        """

        configuration.validate()
        if engine is None and not configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour consulter la Bibliotheque.")
        self.configuration = configuration
        self.engine = engine or engine_factory(configuration.database_url)
        resolved_normalizer = name_normalizer or UserCollectionNameNormalizer()
        self.platform_repository = platform_repository or SqlAlchemyPlatformRepository(
            configuration.schema_name,
            resolved_normalizer,
        )
        self.studio_repository = studio_repository or SqlAlchemyStudioRepository(
            configuration.schema_name,
            resolved_normalizer,
        )
        self.game_repository = game_repository or SqlAlchemyGameRepository(
            configuration.schema_name,
            resolved_normalizer,
        )

    def count_entities(self) -> dict[str, int]:
        """Compte les entites globales exposees par la Bibliotheque.

        Args:
            Aucun.

        Returns:
            dict[str, int]: Compteurs `platforms`, `studios` et `games`.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une requete.
        """

        with self.engine.connect() as connection:
            return {
                "platforms": self.platform_repository.count_public_library_platforms(connection),
                "studios": self.studio_repository.count_public_library_studios(connection),
                "games": self.game_repository.count_public_library_games(connection),
            }

    def list_platforms(self, criteria: LibraryQueryCriteria) -> dict[str, Any]:
        """Liste les plateformes publiques au format API Bibliotheque.

        Args:
            criteria (LibraryQueryCriteria): Criteres de pagination, recherche et tri.

        Returns:
            dict[str, Any]: Payload contenant `page` et `platforms`.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une requete.
        """

        with self.engine.connect() as connection:
            total_elements = self.platform_repository.count_public_library_platforms_by_criteria(
                connection,
                criteria,
            )
            rows = self.platform_repository.list_public_library_platforms(connection, criteria)
        return {
            "page": self._page_payload(criteria, total_elements),
            "platforms": [self._platform_payload(row) for row in rows],
        }

    def list_studios(self, criteria: LibraryQueryCriteria) -> dict[str, Any]:
        """Liste les studios publics au format API Bibliotheque.

        Args:
            criteria (LibraryQueryCriteria): Criteres de pagination, recherche et tri.

        Returns:
            dict[str, Any]: Payload contenant `page` et `studios`.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une requete.
        """

        with self.engine.connect() as connection:
            total_elements = self.studio_repository.count_public_library_studios_by_criteria(
                connection,
                criteria,
            )
            rows = self.studio_repository.list_public_library_studios(connection, criteria)
        return {
            "page": self._page_payload(criteria, total_elements),
            "studios": [self._studio_payload(row) for row in rows],
        }

    def list_games(self, criteria: LibraryQueryCriteria) -> dict[str, Any]:
        """Liste les jeux publics au format API Bibliotheque.

        Args:
            criteria (LibraryQueryCriteria): Criteres de pagination, recherche et tri.

        Returns:
            dict[str, Any]: Payload contenant `page` et `games`.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une requete.
        """

        with self.engine.connect() as connection:
            total_elements = self.game_repository.count_public_library_games_by_criteria(
                connection,
                criteria,
            )
            rows = self.game_repository.list_public_library_games(connection, criteria)
        return {
            "page": self._page_payload(criteria, total_elements),
            "games": [self._game_payload(row) for row in rows],
        }

    def get_game(self, game_id: int) -> dict[str, Any] | None:
        """Retourne le detail public d'un jeu global.

        Args:
            game_id (int): Identifiant du jeu recherche.

        Returns:
            dict[str, Any] | None: Jeu serialisable ou absence.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une requete.
        """

        with self.engine.connect() as connection:
            row = self.game_repository.find_public_library_game(connection, game_id)
        return None if row is None else self._game_payload(row)

    def _page_payload(
        self,
        criteria: LibraryQueryCriteria,
        total_elements: int,
    ) -> dict[str, int]:
        """Construit la section de pagination du payload.

        Args:
            criteria (LibraryQueryCriteria): Criteres contenant la page demandee.
            total_elements (int): Nombre total d'elements filtres.

        Returns:
            dict[str, int]: Metadonnees de pagination.
        """

        page_size = criteria.page_request.size
        return {
            "totalElements": total_elements,
            "page": criteria.page_request.page,
            "size": page_size,
            "totalPages": ceil(total_elements / page_size) if total_elements else 0,
        }

    def _platform_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        """Normalise une plateforme pour l'API Bibliotheque.

        Args:
            row (dict[str, Any]): Ligne retournee par le repository.

        Returns:
            dict[str, Any]: Plateforme serialisable.
        """

        return {
            "id": row["id"],
            "name": self._text_value(row.get("name")),
            "release_date": self._date_value(row.get("release_date")),
            "manufacturer": self._text_value(row.get("manufacturer")),
            "description": self._description_value(row.get("description")),
            "status": self._text_value(row.get("status")),
            "total_games": self._integer_value(row.get("total_games")),
        }

    def _studio_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        """Normalise un studio pour l'API Bibliotheque.

        Args:
            row (dict[str, Any]): Ligne retournee par le repository.

        Returns:
            dict[str, Any]: Studio serialisable.
        """

        return {
            "id": row["id"],
            "name": self._text_value(row.get("name")),
            "country": self._text_value(row.get("country")),
            "city": self._text_value(row.get("city")),
            "creation_date": self._date_value(row.get("creation_date")),
            "status": self._text_value(row.get("status")),
            "editor_total_games": self._integer_value(row.get("editor_total_games")),
            "developer_total_games": self._integer_value(row.get("developer_total_games")),
        }

    def _game_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        """Normalise un jeu pour l'API Bibliotheque.

        Args:
            row (dict[str, Any]): Ligne retournee par le repository.

        Returns:
            dict[str, Any]: Jeu serialisable.
        """

        return {
            "id": row["id"],
            "name": self._text_value(row.get("name")),
            "release_date": self._date_value(row.get("release_date")),
            "developer": self._text_value(row.get("developer")),
            "editor": self._text_value(row.get("editor")),
            "status": self._text_value(row.get("status")),
            "platform": self._text_value(row.get("platform")),
        }

    def _date_value(self, value: Any) -> str:
        """Serialise une date pour l'API Bibliotheque.

        Args:
            value (Any): Valeur brute retournee par le repository.

        Returns:
            str: Date ISO ou chaine vide.
        """

        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return self._text_value(value)

    def _description_value(self, value: Any) -> Any:
        """Normalise une description JSON.

        Args:
            value (Any): Description brute.

        Returns:
            Any: Description JSON existante ou chaine vide.
        """

        return value if value is not None else ""

    def _text_value(self, value: Any) -> str:
        """Normalise une valeur textuelle.

        Args:
            value (Any): Valeur brute.

        Returns:
            str: Texte serialisable ou chaine vide.
        """

        return "" if value is None else str(value)

    def _integer_value(self, value: Any) -> int:
        """Normalise une valeur entiere.

        Args:
            value (Any): Valeur brute.

        Returns:
            int: Entier serialisable.
        """

        return int(value or 0)
