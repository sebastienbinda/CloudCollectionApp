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
# Description : orchestration transactionnelle SQL de l'import de collection utilisateur.

from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection

from services.collection.imports import CollectionImportData
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer

from .database_configuration import DatabaseConfiguration
from .game_repository import SqlAlchemyGameRepository
from .platform_repository import SqlAlchemyPlatformRepository
from .studio_repository import SqlAlchemyStudioRepository
from .user_collection_file_repository import (
    SqlAlchemyUserCollectionFileRepository,
    UserCollectionAlreadyImportedError,
    UserCollectionImportUserNotFoundError,
)
from .user_collection_repository import SqlAlchemyUserCollectionRepository, UserGameAssociation


@dataclass(frozen=True)
class UserCollectionImportPersistenceResult:
    """Regroupe les compteurs de persistance d'un import de collection.

    Attributes:
        created_platforms (int): Nombre de plateformes creees.
        created_studios (int): Nombre de studios crees.
        created_games (int): Nombre de jeux crees.
        associated_games (int): Nombre de jeux rattaches a l'utilisateur.
    """

    created_platforms: int
    created_studios: int
    created_games: int
    associated_games: int


class SqlAlchemyUserCollectionImportRepository:
    """Coordonne les repositories d'entites dans une transaction d'import."""

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        name_normalizer: UserCollectionNameNormalizer | None = None,
    ):
        """Initialise l'orchestrateur SQL d'import de collection.

        Args:
            configuration (DatabaseConfiguration): Configuration SQLAlchemy.
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur metier.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si aucune base de donnees n'est configuree.
        """

        configuration.validate()
        if not configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour importer une collection utilisateur.")
        self.configuration = configuration
        self.name_normalizer = name_normalizer or UserCollectionNameNormalizer()
        self.engine = create_engine(configuration.database_url)
        self.user_file_repository = SqlAlchemyUserCollectionFileRepository(
            configuration.schema_name
        )
        self.platform_repository = SqlAlchemyPlatformRepository(
            configuration.schema_name,
            self.name_normalizer,
        )
        self.studio_repository = SqlAlchemyStudioRepository(
            configuration.schema_name,
            self.name_normalizer,
        )
        self.game_repository = SqlAlchemyGameRepository(
            configuration.schema_name,
            self.name_normalizer,
        )
        self.user_collection_repository = SqlAlchemyUserCollectionRepository(
            configuration.schema_name
        )

    def user_has_collection(self, user_id: int) -> bool:
        """Indique si l'utilisateur possede deja un fichier de collection.

        Args:
            user_id (int): Identifiant technique de l'utilisateur.

        Returns:
            bool: `True` si `collection_file_path` est deja renseigne.
        """

        with self.engine.connect() as connection:
            return self.user_file_repository.user_has_collection(connection, user_id)

    def import_collection(
        self,
        user_id: int,
        collection_file_path: str,
        import_data: CollectionImportData,
        collection_file_description: dict,
    ) -> UserCollectionImportPersistenceResult:
        """Importe les donnees de collection dans une transaction SQL.

        Args:
            user_id (int): Identifiant de l'utilisateur proprietaire.
            collection_file_path (str): Chemin final du fichier de collection.
            import_data (CollectionImportData): Donnees de collection deja validees.
            collection_file_description (dict): Description valide ayant servi a l'import.

        Returns:
            UserCollectionImportPersistenceResult: Compteurs de l'import.

        Raises:
            UserCollectionAlreadyImportedError: Si une collection existe deja.
            UserCollectionImportUserNotFoundError: Si l'utilisateur est absent.
        """

        with self.engine.begin() as connection:
            self.user_file_repository.lock_user_without_collection(connection, user_id)
            platform_ids, created_platforms = self._ensure_platforms(connection, import_data)
            studio_ids, created_studios = self._ensure_studios(connection, import_data)
            game_associations, created_games = self._ensure_games(
                connection,
                import_data,
                platform_ids,
                studio_ids,
            )
            associated_games = self.user_collection_repository.ensure_user_game_associations(
                connection,
                user_id,
                game_associations,
            )
            self.user_file_repository.update_collection_file(
                connection,
                user_id,
                collection_file_path,
                collection_file_description,
            )
        return UserCollectionImportPersistenceResult(
            created_platforms=created_platforms,
            created_studios=created_studios,
            created_games=created_games,
            associated_games=associated_games,
        )

    def _ensure_platforms(
        self,
        connection: Connection,
        import_data: CollectionImportData,
    ) -> tuple[dict[str, int], int]:
        """Cree les plateformes absentes et retourne leurs identifiants.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            import_data (CollectionImportData): Donnees importees.

        Returns:
            tuple[dict[str, int], int]: Identifiants par cle et nombre de creations.
        """

        platform_ids = self.platform_repository.load_ids_by_key(connection)
        created_count = 0
        for platform in import_data.platforms:
            platform_key = self.name_normalizer.comparison_key(platform.name)
            if platform_key in platform_ids:
                continue
            platform_ids[platform_key] = self.platform_repository.insert(
                connection,
                platform.name,
            )
            created_count += 1
        return platform_ids, created_count

    def _ensure_studios(
        self,
        connection: Connection,
        import_data: CollectionImportData,
    ) -> tuple[dict[str, int], int]:
        """Cree les studios absents et retourne leurs identifiants.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            import_data (CollectionImportData): Donnees importees.

        Returns:
            tuple[dict[str, int], int]: Identifiants par cle et nombre de creations.
        """

        studio_ids = self.studio_repository.load_ids_by_key(connection)
        created_count = 0
        for studio in import_data.studios:
            studio_key = self.name_normalizer.comparison_key(studio.name)
            if studio_key in studio_ids:
                continue
            studio_ids[studio_key] = self.studio_repository.insert(connection, studio.name)
            created_count += 1
        return studio_ids, created_count

    def _ensure_games(
        self,
        connection: Connection,
        import_data: CollectionImportData,
        platform_ids: dict[str, int],
        studio_ids: dict[str, int],
    ) -> tuple[list[UserGameAssociation], int]:
        """Cree les jeux absents et retourne leurs identifiants.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            import_data (CollectionImportData): Donnees importees.
            platform_ids (dict[str, int]): Plateformes par cle normalisee.
            studio_ids (dict[str, int]): Studios par cle normalisee.

        Returns:
            tuple[list[UserGameAssociation], int]: Associations importees et nombre de creations.
        """

        existing_game_ids = self.game_repository.load_ids_by_key(connection)
        game_associations: list[UserGameAssociation] = []
        created_count = 0
        for game in import_data.games:
            game_key = self.game_repository.game_key(game)
            if game_key not in existing_game_ids:
                existing_game_ids[game_key] = self.game_repository.insert(
                    connection,
                    game,
                    platform_ids[game_key[0]],
                    studio_ids.get(self.name_normalizer.comparison_key(game.studio_name)),
                )
                created_count += 1
            game_associations.append(
                UserGameAssociation(existing_game_ids[game_key], game.wishlist)
            )
        return game_associations, created_count
