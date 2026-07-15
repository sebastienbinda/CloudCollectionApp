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

import logging
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

from services.collection.imports import CollectionImportData
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer

from .database_configuration import DatabaseConfiguration
from .game_matching_service import GameMatchingService
from .game_repository import SqlAlchemyGameRepository
from .platform_matching_service import PlatformMatchingService
from .platform_repository import SqlAlchemyPlatformRepository
from .studio_matching_service import StudioMatchingService
from .studio_repository import SqlAlchemyStudioRepository
from .user_collection_import_game_match_report_builder import (
    UserCollectionImportGameMatchReportBuilder,
)
from .user_collection_import_persistence_result import (
    CreatedGameMatchReport,
    ImportedStudioMatchReport,
    ImportedGameMatchReport,
    UserCollectionImportPersistenceResult,
)
from .user_collection_file_repository import (
    SqlAlchemyUserCollectionFileRepository,
    UserCollectionImportUserNotFoundError,
)
from .user_collection_repository import SqlAlchemyUserCollectionRepository, UserGameAssociation


class UserCollectionReinitializationNotFoundError(Exception):
    """Signale qu'aucune collection utilisateur ne peut etre reinitialisee."""


class _UserCollectionFileRemover:
    """Supprime le fichier de collection stocke sur disque."""

    def __init__(self, logger=None):
        """Initialise le suppresseur de fichier.

        Args:
            logger (logging.Logger | None): Logger applicatif.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.logger = logger or logging.getLogger(__name__)

    def delete_collection_file(self, collection_file_path: str) -> None:
        """Supprime le fichier de collection si son chemin est renseigne.

        Args:
            collection_file_path (str): Chemin du fichier a supprimer.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            OSError: Si le fichier existe mais ne peut pas etre supprime.
        """

        if not collection_file_path:
            return
        resolved_path = Path(collection_file_path)
        try:
            resolved_path.unlink()
        except FileNotFoundError:
            self.logger.warning("Fichier de collection absent pendant la reinitialisation.")


class SqlAlchemyUserCollectionImportRepository:
    """Coordonne les repositories d'entites dans une transaction d'import."""

    GLOBAL_GAME_IMPORT_LOCK_KEY = 4_282_026_062_701

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        name_normalizer: UserCollectionNameNormalizer | None = None,
        collection_file_remover=None,
        platform_matching_service: PlatformMatchingService | None = None,
        studio_matching_service: StudioMatchingService | None = None,
        game_matching_service: GameMatchingService | None = None,
    ):
        """Initialise l'orchestrateur SQL d'import de collection.

        Args:
            configuration (DatabaseConfiguration): Configuration SQLAlchemy.
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur metier.
            collection_file_remover (object | None): Suppresseur de fichier injecte.
            platform_matching_service (PlatformMatchingService | None): Matching plateformes.
            studio_matching_service (StudioMatchingService | None): Matching studios.
            game_matching_service (GameMatchingService | None): Matching jeux existants.

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
        self.collection_file_remover = collection_file_remover or _UserCollectionFileRemover()
        self.platform_matching_service = (
            platform_matching_service
            or PlatformMatchingService(name_normalizer=self.name_normalizer)
        )
        self.studio_matching_service = (
            studio_matching_service
            or StudioMatchingService(name_normalizer=self.name_normalizer)
        )
        self.game_matching_service = (
            game_matching_service
            or GameMatchingService(name_normalizer=self.name_normalizer)
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

    def find_import_configuration(self, user_id: int) -> dict | None:
        """Retourne la derniere configuration d'import sauvegardee.

        Args:
            user_id (int): Identifiant technique de l'utilisateur.

        Returns:
            dict | None: Configuration d'import sauvegardee ou absence.
        """

        with self.engine.connect() as connection:
            return self.user_file_repository.find_collection_file_description(connection, user_id)

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
            UserCollectionImportUserNotFoundError: Si l'utilisateur est absent.
        """

        with self.engine.begin() as connection:
            self.user_file_repository.lock_user_collection_state(connection, user_id)
            self._lock_global_game_import_state(connection)
            user_email = self.user_file_repository.find_user_email(connection, user_id)
            matched_import_data = self._match_platforms(connection, import_data)
            self._synchronize_import_data(import_data, matched_import_data)
            platform_ids, linked_platforms = self._ensure_platforms(
                connection,
                matched_import_data,
            )
            studio_ids, created_studios, imported_studio_match_reports = self._ensure_studios(
                connection,
                matched_import_data,
            )
            (
                game_associations,
                created_games,
                created_game_match_reports,
                imported_game_match_reports,
            ) = self._ensure_games(
                connection,
                matched_import_data,
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
        self.platform_repository.invalidate_cache()
        return UserCollectionImportPersistenceResult(
            linked_platforms=linked_platforms,
            created_studios=created_studios,
            created_games=created_games,
            associated_games=associated_games,
            user_email=user_email,
            created_game_match_reports=tuple(created_game_match_reports),
            imported_game_match_reports=tuple(imported_game_match_reports),
            imported_studio_match_reports=tuple(imported_studio_match_reports),
        )

    def _lock_global_game_import_state(self, connection: Connection) -> None:
        """Serialise le matching et la creation des jeux globaux pendant l'import.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            None: Le verrou est conserve jusqu'a la fin de la transaction.
        """

        connection.execute(
            text("SELECT pg_advisory_xact_lock(:lock_key)"),
            {"lock_key": self.GLOBAL_GAME_IMPORT_LOCK_KEY},
        )

    def _synchronize_import_data(
        self,
        import_data: CollectionImportData,
        matched_import_data: CollectionImportData,
    ) -> None:
        """Expose les donnees filtrees au service appelant apres matching.

        Args:
            import_data (CollectionImportData): Donnees initiales lues par le reader.
            matched_import_data (CollectionImportData): Donnees rattachees au catalogue.

        Returns:
            None: La methode met a jour l'objet transmis par l'appelant.
        """

        object.__setattr__(import_data, "platforms", matched_import_data.platforms)
        object.__setattr__(import_data, "studios", matched_import_data.studios)
        object.__setattr__(import_data, "games", matched_import_data.games)
        object.__setattr__(import_data, "warnings", matched_import_data.warnings)

    def _match_platforms(
        self,
        connection: Connection,
        import_data: CollectionImportData,
    ) -> CollectionImportData:
        platform_rows = self.platform_repository.load_catalog_rows(connection)
        matched_import_data = self.platform_matching_service.match_import_data(
            import_data,
            platform_rows,
        )
        return matched_import_data

    def reinitialize_collection(self, user_id: int) -> None:
        """Reinitialise la collection d'un utilisateur dans une transaction SQL.

        Args:
            user_id (int): Identifiant de l'utilisateur proprietaire.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            UserCollectionReinitializationNotFoundError: Si aucune collection n'existe.
            UserCollectionImportUserNotFoundError: Si l'utilisateur est absent.
            OSError: Si le fichier existant ne peut pas etre supprime.
        """

        with self.engine.begin() as connection:
            collection_file_path = self.user_file_repository.lock_user_collection_state(
                connection,
                user_id,
            )
            association_count = (
                self.user_collection_repository.count_user_game_associations(
                    connection,
                    user_id,
                )
            )
            if not collection_file_path and association_count == 0:
                raise UserCollectionReinitializationNotFoundError(
                    "Collection introuvable."
                )
            self.user_collection_repository.delete_user_game_associations(
                connection,
                user_id,
            )
            self.user_file_repository.clear_collection_file(connection, user_id)
            self.collection_file_remover.delete_collection_file(collection_file_path)

    def _ensure_platforms(
        self,
        connection: Connection,
        import_data: CollectionImportData,
    ) -> tuple[dict[str, int], int]:
        """Retourne les plateformes du referentiel liees a l'import.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            import_data (CollectionImportData): Donnees importees.

        Returns:
            tuple[dict[str, int], int]: Identifiants par cle et nombre de plateformes liees.
        """

        platform_ids = self.platform_repository.load_ids_by_key(connection)
        linked_keys = {
            self.name_normalizer.comparison_key(game.platform_name)
            for game in import_data.games
            if self.name_normalizer.comparison_key(game.platform_name)
        }
        return platform_ids, len(linked_keys.intersection(platform_ids))

    def _ensure_studios(
        self,
        connection: Connection,
        import_data: CollectionImportData,
    ) -> tuple[dict[str, int], int, list[ImportedStudioMatchReport]]:
        """Cree les studios absents et retourne leurs identifiants.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            import_data (CollectionImportData): Donnees importees.

        Returns:
            tuple[dict[str, int], int, list[ImportedStudioMatchReport]]: Identifiants
                par cle, nombre de creations et diagnostics de matching.
        """

        studio_ids = self.studio_repository.load_ids_by_key(connection)
        studio_names = self._load_studio_names_by_key(connection, studio_ids)
        studio_matching_service = getattr(
            self,
            "studio_matching_service",
            StudioMatchingService(name_normalizer=self.name_normalizer),
        )
        created_count = 0
        imported_studio_match_reports = []
        for studio in import_data.studios:
            studio_key = self.name_normalizer.comparison_key(studio.name)
            matching_result = studio_matching_service.evaluate_existing_studio(
                studio.name,
                studio_ids,
            )
            matched_studio_key = matching_result.matched_key
            if matched_studio_key is not None:
                if studio_key not in studio_ids:
                    studio_ids[studio_key] = studio_ids[matched_studio_key]
                    studio_names[studio_key] = studio_names.get(matched_studio_key, "")
                imported_studio_match_reports.append(
                    ImportedStudioMatchReport(
                        studio.name,
                        False,
                        studio_names.get(matched_studio_key, ""),
                        matching_result.score,
                    )
                )
                continue
            studio_ids[studio_key] = self.studio_repository.insert(connection, studio.name)
            studio_names[studio_key] = studio.name
            created_count += 1
            imported_studio_match_reports.append(
                ImportedStudioMatchReport(studio.name, True, "", matching_result.score)
            )
        return studio_ids, created_count, imported_studio_match_reports

    def _load_studio_names_by_key(
        self,
        connection: Connection,
        studio_ids: dict[str, int],
    ) -> dict[str, str]:
        """Charge les noms de studios existants quand le repository les expose.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            studio_ids (dict[str, int]): Identifiants de studios par cle.

        Returns:
            dict[str, str]: Noms de studios par cle normalisee.
        """

        if hasattr(self.studio_repository, "load_names_by_key"):
            return self.studio_repository.load_names_by_key(connection)
        return {studio_key: studio_key for studio_key in studio_ids}

    def _ensure_games(
        self,
        connection: Connection,
        import_data: CollectionImportData,
        platform_ids: dict[str, int],
        studio_ids: dict[str, int],
    ) -> tuple[
        list[UserGameAssociation],
        int,
        list[CreatedGameMatchReport],
        list[ImportedGameMatchReport],
    ]:
        """Cree les jeux absents et retourne leurs identifiants.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            import_data (CollectionImportData): Donnees importees.
            platform_ids (dict[str, int]): Plateformes par cle normalisee.
            studio_ids (dict[str, int]): Studios par cle normalisee.

        Returns:
            tuple[list[UserGameAssociation], int, list[CreatedGameMatchReport],
                list[ImportedGameMatchReport]]: Associations, nombre de creations,
                details des jeux crees et diagnostics par jeu importe.
        """

        existing_game_references = self.game_repository.load_references_by_key(connection)
        existing_game_ids = {
            game_key: game_reference[0]
            for game_key, game_reference in existing_game_references.items()
        }
        games_by_platform = self.game_matching_service.build_platform_index(
            existing_game_references
        )
        game_associations: list[UserGameAssociation] = []
        created_game_match_reports: list[CreatedGameMatchReport] = []
        imported_game_match_reports: list[ImportedGameMatchReport] = []
        created_count = 0
        for game in import_data.games:
            game_key = self.game_repository.game_key(game)
            exact_game_reference = existing_game_references.get(game_key)
            matching_result = self.game_matching_service.evaluate_existing_game(
                game,
                existing_game_ids,
                games_by_platform,
            )
            existing_game_id = matching_result.existing_game_id
            created = False
            if existing_game_id is None:
                created = True
                created_game_match_reports.append(
                    UserCollectionImportGameMatchReportBuilder.build_created_game_match_report(
                        game,
                        matching_result.best_candidate,
                    )
                )
                existing_game_ids[game_key] = self.game_repository.insert(
                    connection,
                    game,
                    platform_ids[game_key[0]],
                    studio_ids.get(self.name_normalizer.comparison_key(game.studio_name)),
                )
                existing_game_id = existing_game_ids[game_key]
                self.game_matching_service.add_to_platform_index(
                    game_key,
                    existing_game_id,
                    game.name,
                    games_by_platform,
                    game.release_date,
                )
                created_count += 1
            imported_game_match_reports.append(
                UserCollectionImportGameMatchReportBuilder.build_imported_game_match_report(
                    game,
                    created,
                    exact_game_reference,
                    matching_result.best_candidate,
                )
            )
            game_associations.append(
                UserGameAssociation(
                    game_id=existing_game_id,
                    wishlist=game.wishlist,
                    purchase_price=game.purchase_price,
                    price_unit=game.price_unit,
                    buy_location=game.buy_location,
                    buy_date=game.buy_date,
                    grade=game.grade,
                    grade_normalized=game.grade_normalized,
                    condition=game.condition,
                    has_manual=game.has_manual,
                    is_collector=game.is_collector,
                    has_steelbook=game.has_steelbook,
                    is_digital=game.is_digital,
                    region=game.region,
                    description=game.description,
                )
            )
        return (
            game_associations,
            created_count,
            created_game_match_reports,
            imported_game_match_reports,
        )
