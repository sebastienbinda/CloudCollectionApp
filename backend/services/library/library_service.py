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

from typing import Any, Callable, Protocol

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine

from services.database.database_configuration import DatabaseConfiguration
from services.database.game_repository import SqlAlchemyGameRepository
from services.database.platform_image_repository import SqlAlchemyPlatformImageRepository
from services.database.platform_repository import SqlAlchemyPlatformRepository
from services.database.studio_repository import SqlAlchemyStudioRepository
from services.users import UserCollectionNameNormalizer

from .current_user_collection_marker import CurrentUserCollectionMarker
from .library_query_contract import LibraryQueryCriteria
from .library_payload_serializer import LibraryPayloadSerializer

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

    def find_public_library_platform(
        self,
        connection: Connection,
        platform_id: int,
    ) -> dict[str, Any] | None:
        """Retourne une plateforme correspondant a l'identifiant.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_id (int): Identifiant de plateforme.

        Returns:
            dict[str, Any] | None: Plateforme lue ou absence.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """


class PublicLibraryPlatformImageRepository(Protocol):
    """Decrit les lectures publiques attendues pour les images de plateformes."""

    def list_accepted_images(
        self,
        connection: Connection,
        platform_id: int,
    ) -> list[dict[str, Any]]:
        """Liste les images acceptees d'une plateforme.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_id (int): Identifiant de plateforme.

        Returns:
            list[dict[str, Any]]: Images acceptees.

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

    def list_current_user_collection_game_ids(
        self,
        connection: Connection,
        user_id: int,
        game_ids: list[int],
    ) -> set[int]:
        """Liste les jeux de la page deja presents dans la collection utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur connecte.
            game_ids (list[int]): Identifiants de jeux a verifier.

        Returns:
            set[int]: Identifiants en collection hors wishlist.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def find_public_library_game(
        self,
        connection: Connection,
        game_id: int,
    ) -> dict[str, Any] | None:
        """Retourne un jeu correspondant a l'identifiant.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game_id (int): Identifiant de jeu.

        Returns:
            dict[str, Any] | None: Jeu lu ou absence.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """


class LibraryService:
    """Orchestre la consultation publique de la base globale."""

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        platform_repository: PublicLibraryPlatformRepository | None = None,
        platform_image_repository: PublicLibraryPlatformImageRepository | None = None,
        studio_repository: PublicLibraryStudioRepository | None = None,
        game_repository: PublicLibraryGameRepository | None = None,
        engine: Engine | None = None,
        engine_factory: EngineFactory = create_engine,
        name_normalizer: UserCollectionNameNormalizer | None = None,
        payload_serializer: LibraryPayloadSerializer | None = None,
    ):
        """Initialise le service Bibliotheque.

        Args:
            configuration (DatabaseConfiguration): Configuration de connexion SQL.
            platform_repository (PublicLibraryPlatformRepository | None): Repository plateformes.
            platform_image_repository (PublicLibraryPlatformImageRepository | None): Repository images.
            studio_repository (PublicLibraryStudioRepository | None): Repository studios.
            game_repository (PublicLibraryGameRepository | None): Repository jeux.
            engine (Engine | None): Moteur SQLAlchemy injectable en test.
            engine_factory (EngineFactory): Fabrique de moteur SQLAlchemy.
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur partage.
            payload_serializer (LibraryPayloadSerializer | None): Serialiseur de payloads.

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
        self.platform_image_repository = (
            platform_image_repository
            or SqlAlchemyPlatformImageRepository(configuration.schema_name)
        )
        self.studio_repository = studio_repository or SqlAlchemyStudioRepository(
            configuration.schema_name,
            resolved_normalizer,
        )
        self.game_repository = game_repository or SqlAlchemyGameRepository(
            configuration.schema_name,
            resolved_normalizer,
        )
        self.current_user_collection_marker = CurrentUserCollectionMarker(self.game_repository)
        self.payload_serializer = payload_serializer or LibraryPayloadSerializer()

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
            "page": self.payload_serializer.page_payload(criteria, total_elements),
            "platforms": [self.payload_serializer.platform_payload(row) for row in rows],
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
            "page": self.payload_serializer.page_payload(criteria, total_elements),
            "studios": [self.payload_serializer.studio_payload(row) for row in rows],
        }

    def list_games(
        self,
        criteria: LibraryQueryCriteria,
        current_user_id: int | None = None,
    ) -> dict[str, Any]:
        """Liste les jeux publics au format API Bibliotheque.

        Args:
            criteria (LibraryQueryCriteria): Criteres de pagination, recherche et tri.
            current_user_id (int | None): Utilisateur connecte optionnel.

        Returns:
            dict[str, Any]: Payload contenant `page` et `games`.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une requete.
        """

        effective_current_user_id = (
            current_user_id
            if current_user_id is not None
            else criteria.current_user_id
        )
        with self.engine.connect() as connection:
            total_elements = self.game_repository.count_public_library_games_by_criteria(
                connection,
                criteria,
            )
            rows = self.game_repository.list_public_library_games(connection, criteria)
            self.current_user_collection_marker.mark_games(
                connection,
                rows,
                effective_current_user_id,
            )
        return {
            "page": self.payload_serializer.page_payload(criteria, total_elements),
            "games": [self.payload_serializer.game_payload(row) for row in rows],
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
        return None if row is None else self.payload_serializer.game_payload(row)

    def get_platform(self, platform_id: int) -> dict[str, Any] | None:
        """Retourne le detail public d'une plateforme globale.

        Args:
            platform_id (int): Identifiant de la plateforme recherchee.

        Returns:
            dict[str, Any] | None: Plateforme serialisable ou absence.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une requete.
        """

        with self.engine.connect() as connection:
            row = self.platform_repository.find_public_library_platform(connection, platform_id)
            if row is not None:
                row = dict(row)
                row["images"] = self.platform_image_repository.list_accepted_images(
                    connection,
                    platform_id,
                )
        return None if row is None else self.payload_serializer.platform_payload(row)
