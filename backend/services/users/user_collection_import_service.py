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
# Description : service metier d'import de collection utilisateur.

import logging
from time import perf_counter
from pathlib import Path
from threading import Lock

from services.collection.imports import (
    CollectionFileDescription,
    CollectionFileDescriptionValidationError,
    CollectionImportFailureAdminNotifier,
    CollectionImportFailureNotificationService,
    CollectionFileReaderFactory,
    CollectionFileReadError,
    CollectionFileValidationError,
    CollectionImportData,
    CollectionImportRefusalAdminNotifier,
    CollectionImportRefusalNotificationService,
    CollectionImportRefusalPolicy,
)
from services.database.user_collection_import_persistence_result import (
    UserCollectionImportPersistenceResult,
)
from services.database.game_repository import GAME_STATUS_WAITING_VALIDATION
from services.database.user_collection_import_repository import (
    UserCollectionImportUserNotFoundError,
    UserCollectionReinitializationNotFoundError,
)

from .user_collection_import_admin_notifier import UserCollectionImportAdminNotifier
from services.collection.imports import CollectionImportDateValidator
from .user_collection_import_configuration import UserCollectionImportConfiguration
from .user_collection_import_errors import (
    UserCollectionImportError,
    UserCollectionImportInvalidFileError,
    UserCollectionImportNotFoundError,
    UserCollectionImportTemporaryFileMissingError,
    UserCollectionImportTooLargeError,
    UserCollectionImportUnexpectedError,
)
from .user_collection_import_file_manager import UserCollectionImportFileManager
from .user_collection_import_association_validator import UserCollectionImportAssociationValidator
from .user_collection_import_report_notifier import UserCollectionImportReportNotifier
from .user_collection_import_repository_protocol import UserCollectionImportRepository
from .user_collection_import_report_context import UserCollectionImportReportContext
from .user_collection_import_report_policy import UserCollectionImportReportPolicy
from .user_collection_import_result import UserCollectionImportResult
from .user_collection_import_timer import UserCollectionImportTimer


class UserCollectionImportService:
    """Orchestre l'import complet d'une collection utilisateur."""

    _locks_by_user_id: dict[int, Lock] = {}
    _locks_guard = Lock()

    def __init__(
        self,
        configuration: UserCollectionImportConfiguration,
        repository: UserCollectionImportRepository,
        reader_factory: CollectionFileReaderFactory,
        date_validator: CollectionImportDateValidator | None = None,
        report_notifier: UserCollectionImportReportNotifier | None = None,
        failure_notifier=None,
        refusal_notifier=None,
        logger=None,
    ):
        """Initialise le service d'import de collection.

        Args:
            configuration (UserCollectionImportConfiguration): Configuration d'import.
            repository (UserCollectionImportRepository): Persistance transactionnelle.
            reader_factory (CollectionFileReaderFactory): Factory de lecteurs.
            date_validator (CollectionImportDateValidator | None): Validateur des dates lues.
            report_notifier (UserCollectionImportReportNotifier | None): Notifier admin.
            failure_notifier (object | None): Notifier admin des echecs d'import.
            refusal_notifier (object | None): Notifier admin des refus d'import.
            logger (object | None): Logger injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration
        self.repository = repository
        self.reader_factory = reader_factory
        self.file_manager = UserCollectionImportFileManager(configuration)
        self.date_validator = date_validator or CollectionImportDateValidator()
        self.report_notifier = report_notifier or UserCollectionImportAdminNotifier()
        self.failure_notifier = failure_notifier or CollectionImportFailureAdminNotifier()
        self.refusal_notifier = refusal_notifier or CollectionImportRefusalAdminNotifier()
        self.failure_notification_service = CollectionImportFailureNotificationService()
        self.refusal_notification_service = CollectionImportRefusalNotificationService()
        self.report_policy = UserCollectionImportReportPolicy()
        self.refusal_policy = CollectionImportRefusalPolicy()
        self.association_validator = UserCollectionImportAssociationValidator()
        self.logger = logger or logging.getLogger(__name__)

    def upload_import_file(
        self,
        user_id: int,
        source_file_path: str,
        original_filename: str | None,
        file_type,
    ) -> None:
        """Copie le fichier d'import temporaire d'un utilisateur.

        Args:
            user_id (int): Identifiant utilisateur connecte.
            source_file_path (str): Chemin du fichier temporaire uploade.
            original_filename (str | None): Nom original du fichier uploade.
            file_type (CollectionFileType): Type de fichier selectionne.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            UserCollectionImportInvalidFileError: Si le fichier est invalide.
            UserCollectionImportTooLargeError: Si le fichier est trop volumineux.
        """

        user_lock = self._lock_for_user(user_id)
        with user_lock:
            reader = self.reader_factory.create(file_type)
            source_path = Path(source_file_path)
            self.file_manager.validate_source_file(source_path, original_filename, reader)
            self.file_manager.copy_file(
                source_path,
                self.file_manager.temporary_file_path(user_id, reader),
            )

    def analyze_import_file(self, user_id: int, file_type) -> list[str]:
        """Analyse le fichier temporaire et retourne ses onglets.

        Args:
            user_id (int): Identifiant utilisateur connecte.
            file_type (CollectionFileType): Type de fichier selectionne.

        Returns:
            list[str]: Noms d'onglets disponibles.

        Raises:
            UserCollectionImportTemporaryFileMissingError: Si le fichier temporaire est absent.
            UserCollectionImportInvalidFileError: Si le fichier ne correspond pas au type.
        """

        reader = self.reader_factory.create(file_type)
        temporary_file_path = self.file_manager.temporary_file_path(user_id, reader)
        self.file_manager.ensure_temporary_file_exists(temporary_file_path)
        try:
            return reader.analyze_sheets(str(temporary_file_path))
        except (CollectionFileReadError, CollectionFileValidationError) as exc:
            raise UserCollectionImportInvalidFileError(
                "Fichier de collection invalide.",
                self._import_invalid_file_details(exc),
            ) from exc

    def import_collection_from_temporary_file(
        self,
        user_id: int,
        file_description: CollectionFileDescription | None,
        requester_email: str = "",
    ) -> UserCollectionImportResult:
        """Importe la collection depuis le fichier temporaire utilisateur.

        Args:
            user_id (int): Identifiant utilisateur connecte.
            file_description (CollectionFileDescription | None): Description valide du fichier.
            requester_email (str): Email du demandeur authentifie.

        Returns:
            UserCollectionImportResult: Compteurs de l'import reussi.

        Raises:
            UserCollectionImportTemporaryFileMissingError: Si le fichier temporaire est absent.
            UserCollectionImportError: Si l'import echoue.
        """

        if file_description is None:
            raise CollectionFileDescriptionValidationError(
                ["collection_file_description est requis."]
            )
        reader = self.reader_factory.create(file_description.file_type)
        temporary_file_path = self.file_manager.temporary_file_path(user_id, reader)
        self.file_manager.ensure_temporary_file_exists(temporary_file_path)
        result = self.import_collection(
            user_id,
            str(temporary_file_path),
            temporary_file_path.name,
            file_description,
            requester_email=requester_email,
            initiated_by_function=(
                "UserCollectionImportService.import_collection_from_temporary_file"
            ),
        )
        self.file_manager.delete_copied_file(temporary_file_path)
        return result

    def import_collection(
        self,
        user_id: int,
        source_file_path: str,
        original_filename: str | None = None,
        file_description: CollectionFileDescription | None = None,
        requester_email: str = "",
        initiated_by_function: str = "UserCollectionImportService.import_collection",
    ) -> UserCollectionImportResult:
        """Importe le fichier de collection d'un utilisateur.

        Args:
            user_id (int): Identifiant utilisateur connecte.
            source_file_path (str): Chemin du fichier temporaire uploade.
            original_filename (str | None): Nom original du fichier uploade.
            file_description (CollectionFileDescription | None): Description valide du fichier.
            requester_email (str): Email du demandeur authentifie.
            initiated_by_function (str): Fonction applicative qui lance l'import.

        Returns:
            UserCollectionImportResult: Compteurs de l'import reussi.

        Raises:
            UserCollectionImportInvalidFileError: Si le fichier est invalide.
            UserCollectionImportTooLargeError: Si le fichier est trop volumineux.
            UserCollectionImportUnexpectedError: Si une erreur non fonctionnelle survient.
        """

        user_lock = self._lock_for_user(user_id)
        with user_lock:
            try:
                return self._import_collection_locked(
                    user_id,
                    Path(source_file_path),
                    original_filename,
                    file_description,
                    requester_email,
                )
            except Exception as exc:
                self.failure_notification_service.notify_failure(
                    self.failure_notifier,
                    self.logger,
                    exc,
                    "collection_utilisateur",
                    initiated_by_function,
                    user_id,
                    requester_email,
                    self._failure_file_type(file_description),
                    original_filename or Path(source_file_path).name,
                )
                raise

    def reinitialize_collection(self, user_id: int) -> None:
        """Reinitialise la collection importee d'un utilisateur.

        Args:
            user_id (int): Identifiant utilisateur connecte.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        user_lock = self._lock_for_user(user_id)
        with user_lock:
            try:
                self.repository.reinitialize_collection(user_id)
            except UserCollectionImportNotFoundError:
                raise
            except UserCollectionReinitializationNotFoundError as exc:
                raise UserCollectionImportNotFoundError("Collection introuvable.") from exc
            except Exception as exc:
                raise UserCollectionImportUnexpectedError(
                    "Erreur pendant la reinitialisation collection."
                ) from exc

    def _import_collection_locked(
        self,
        user_id: int,
        source_file_path: Path,
        original_filename: str | None,
        file_description: CollectionFileDescription | None,
        requester_email: str = "",
    ) -> UserCollectionImportResult:
        if file_description is None:
            raise CollectionFileDescriptionValidationError(
                ["collection_file_description est requis."]
            )
        return self._import_collection_file(
            user_id,
            source_file_path,
            original_filename,
            file_description,
            True,
            GAME_STATUS_WAITING_VALIDATION,
            requester_email,
        )

    def _import_collection_file(
        self, user_id: int, source_file_path: Path, original_filename: str | None,
        file_description: CollectionFileDescription, copy_to_workspace: bool,
        initial_game_validation_status: str, requester_email: str = "",
    ) -> UserCollectionImportResult:
        import_started_at = perf_counter()
        reader = self.reader_factory.create(file_description.file_type)
        self.file_manager.validate_source_file(source_file_path, original_filename, reader)
        import_file_path = source_file_path
        copied_file_path = None
        if copy_to_workspace:
            target_file_path = self.file_manager.target_file_path(
                user_id,
                original_filename or source_file_path.name,
                reader,
            )
            copied_file_path = self.file_manager.copy_file(source_file_path, target_file_path)
            import_file_path = copied_file_path
        try:
            file_read_started_at = perf_counter()
            import_data = reader.read(str(import_file_path), file_description)
            file_read_duration_seconds = UserCollectionImportTimer.elapsed_seconds(
                file_read_started_at
            )
            import_data = self.date_validator.validate(import_data)
            import_data = self.repository.prepare_import_data_for_policy(import_data)
            self._set_total_import_duration(import_data, import_started_at)
            refusal = self.refusal_policy.evaluate(import_data)
            if refusal.refused:
                self.file_manager.delete_copied_file(copied_file_path)
                refusal_payload = refusal.to_dict()
                self.refusal_notification_service.notify_refusal(
                    self.refusal_notifier,
                    self.logger,
                    "collection_utilisateur",
                    user_id,
                    requester_email,
                    str(file_description.file_type.value),
                    original_filename or source_file_path.name,
                    refusal_payload,
                    import_data,
                )
                return self._map_refused_result(import_data, refusal_payload)
            self.association_validator.ensure_games_read(import_data)
            persistence_result = self.repository.import_collection(
                user_id,
                str(import_file_path),
                import_data,
                file_description.to_dict(),
                initial_game_validation_status,
            )
            self.association_validator.validate(import_data, persistence_result)
            result = self._map_result(persistence_result, import_data)
            if self.report_policy.is_enabled(self.report_notifier):
                self._notify_import_report(
                    self._build_import_report_context(
                        user_id,
                        original_filename or source_file_path.name,
                        file_description,
                        copy_to_workspace,
                        persistence_result,
                        import_data,
                        result,
                        file_read_duration_seconds,
                    )
                )
            return result
        except CollectionFileDescriptionValidationError:
            self.file_manager.delete_copied_file(copied_file_path)
            raise
        except (CollectionFileReadError, CollectionFileValidationError) as exc:
            self.file_manager.delete_copied_file(copied_file_path)
            raise UserCollectionImportInvalidFileError(
                "Fichier de collection invalide.",
                self._import_invalid_file_details(exc),
            ) from exc
        except UserCollectionImportInvalidFileError:
            self.file_manager.delete_copied_file(copied_file_path)
            raise
        except UserCollectionImportUserNotFoundError as exc:
            self.file_manager.delete_copied_file(copied_file_path)
            raise UserCollectionImportUnexpectedError("Utilisateur introuvable.") from exc
        except Exception as exc:
            self.file_manager.delete_copied_file(copied_file_path)
            raise UserCollectionImportUnexpectedError("Erreur pendant l'import.") from exc

    def _import_invalid_file_details(self, error: Exception) -> list[str]:
        messages = [str(error).strip()]
        cause = getattr(error, "__cause__", None)
        if cause is not None:
            cause_message = str(cause).strip()
            if cause_message:
                messages.append(cause_message)
        return [message for message in messages if message]

    def _map_result(self, persistence_result: UserCollectionImportPersistenceResult,
                    import_data: CollectionImportData) -> UserCollectionImportResult:
        return UserCollectionImportResult(
            linked_platforms=persistence_result.linked_platforms,
            created_studios=persistence_result.created_studios,
            created_games=persistence_result.created_games,
            associated_games=persistence_result.associated_games,
            wishlisted_games=sum(1 for game in import_data.games if game.wishlist),
            warnings=import_data.warnings.to_dict(),
            refusal={
                "refused": False,
                "reason": "",
                "invalid_games_count": (
                    refusal := self.refusal_policy.evaluate(import_data)
                ).invalid_games_count,
                "total_games_count": refusal.total_games_count,
                "message": "",
            },
        )

    def _map_refused_result(
        self,
        import_data: CollectionImportData,
        refusal: dict,
    ) -> UserCollectionImportResult:
        return UserCollectionImportResult(
            linked_platforms=0,
            created_studios=0,
            created_games=0,
            associated_games=0,
            wishlisted_games=0,
            warnings=import_data.warnings.to_dict(),
            refusal=refusal,
        )

    def _build_import_report_context(
        self,
        user_id: int,
        original_filename: str,
        file_description: CollectionFileDescription,
        copy_to_workspace: bool,
        persistence_result: UserCollectionImportPersistenceResult,
        import_data: CollectionImportData,
        result: UserCollectionImportResult,
        file_read_duration_seconds: float = 0.0,
    ) -> UserCollectionImportReportContext:
        return UserCollectionImportReportContext(
            user_id=user_id,
            user_email=str(getattr(persistence_result, "user_email", "") or ""),
            file_type=str(file_description.file_type.value),
            original_filename=original_filename,
            source_mode="temporary_upload" if copy_to_workspace else "stored_file",
            copied_to_workspace=copy_to_workspace,
            linked_platforms=persistence_result.linked_platforms,
            created_studios=persistence_result.created_studios,
            created_games=persistence_result.created_games,
            associated_games=persistence_result.associated_games,
            wishlisted_games=result.wishlisted_games,
            warnings=import_data.warnings,
            collection_file_description=file_description.to_dict(),
            created_game_match_reports=persistence_result.created_game_match_reports,
            imported_game_match_reports=persistence_result.imported_game_match_reports,
            imported_studio_match_reports=persistence_result.imported_studio_match_reports,
            file_read_duration_seconds=file_read_duration_seconds,
            association_calculation_duration_seconds=(
                persistence_result.association_calculation_duration_seconds
            ),
            database_query_duration_seconds=persistence_result.database_query_duration_seconds,
        )

    def _notify_import_report(self, context: UserCollectionImportReportContext) -> None:
        try:
            self.report_notifier.notify_import_report(context)
        except Exception:
            self.logger.exception("Impossible d'envoyer le rapport d'import utilisateur.")

    def _failure_file_type(self, file_description: CollectionFileDescription | None) -> str:
        if file_description is None:
            return ""
        return str(file_description.file_type.value)

    def _set_total_import_duration(
        self,
        import_data: CollectionImportData,
        import_started_at: float,
    ) -> None:
        duration_seconds = UserCollectionImportTimer.elapsed_seconds(import_started_at)
        object.__setattr__(
            import_data.warnings,
            "total_import_duration_seconds",
            duration_seconds,
        )

    @classmethod
    def _lock_for_user(cls, user_id: int) -> Lock:
        with cls._locks_guard:
            if user_id not in cls._locks_by_user_id:
                cls._locks_by_user_id[user_id] = Lock()
            return cls._locks_by_user_id[user_id]
