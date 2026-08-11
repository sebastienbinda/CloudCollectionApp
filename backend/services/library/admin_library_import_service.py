#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-26
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : service metier d'import CSV admin Bibliotheque.

from dataclasses import dataclass
import logging
from pathlib import Path

from services.collection.imports import (
    CollectionFileDescriptionValidationError,
    CollectionFileReadError,
    CollectionFileValidationError,
    CollectionImportFailureAdminNotifier,
    CollectionImportFailureNotificationService,
    CollectionImportDateValidator,
    CollectionImportRefusalAdminNotifier,
    CollectionImportRefusalNotificationService,
    CollectionImportRefusalPolicy,
)
from services.csv.csv_collection_import_reader import CsvCollectionImportReader
from services.database.admin_library_import_repository import (
    SqlAlchemyAdminLibraryImportRepository,
)
from services.database.database_configuration import DatabaseConfiguration

from .admin_library_import_configuration import (
    AdminLibraryImportConfigurationError,
    AdminLibraryImportConfigurationLoader,
)


class AdminLibraryImportInvalidFileError(ValueError):
    """Signale qu'un fichier CSV admin ne peut pas etre importe."""

    def __init__(self, details: list[str]):
        """Initialise l'erreur d'import admin.

        Args:
            details (list[str]): Messages d'erreur exploitables par l'IHM.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.details = details
        super().__init__("Fichier CSV admin invalide.")


@dataclass(frozen=True)
class AdminLibraryImportResult:
    """Regroupe les compteurs exposes par l'import CSV admin.

    Attributes:
        linked_platforms (int): Nombre de plateformes rattachees au referentiel.
        created_studios (int): Nombre de studios crees.
        created_games (int): Nombre de jeux crees.
        warnings (dict): Avertissements produits pendant la lecture et le matching.
        refusal (dict | None): Decision de refus global du fichier.
    """

    linked_platforms: int
    created_studios: int
    created_games: int
    warnings: dict
    refusal: dict | None = None

    def to_dict(self) -> dict:
        """Convertit le resultat en payload JSON.

        Args:
            Aucun.

        Returns:
            dict: Resultat serialisable pour l'API admin.
        """

        return {
            "linked_platforms": self.linked_platforms,
            "created_studios": self.created_studios,
            "created_games": self.created_games,
            "warnings": dict(self.warnings),
            "refusal": self.refusal or {
                "refused": False,
                "reason": "",
                "invalid_games_count": 0,
                "total_games_count": 0,
                "message": "",
            },
        }


class AdminLibraryImportService:
    """Orchestre l'import CSV admin dans la Bibliotheque globale."""

    def __init__(
        self,
        repository,
        reader: CsvCollectionImportReader | None = None,
        configuration_loader: AdminLibraryImportConfigurationLoader | None = None,
        date_validator: CollectionImportDateValidator | None = None,
        failure_notifier=None,
        refusal_notifier=None,
        logger=None,
    ):
        """Initialise le service d'import admin.

        Args:
            repository (object): Repository de persistance Bibliotheque.
            reader (CsvCollectionImportReader | None): Lecteur CSV injectable.
            configuration_loader (AdminLibraryImportConfigurationLoader | None): Chargeur JSON.
            date_validator (CollectionImportDateValidator | None): Validateur de dates.
            failure_notifier (object | None): Notifier admin des echecs d'import.
            refusal_notifier (object | None): Notifier admin des refus d'import.
            logger (object | None): Logger injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.repository = repository
        self.reader = reader or CsvCollectionImportReader()
        self.configuration_loader = configuration_loader or AdminLibraryImportConfigurationLoader()
        self.date_validator = date_validator or CollectionImportDateValidator()
        self.failure_notifier = failure_notifier or CollectionImportFailureAdminNotifier()
        self.refusal_notifier = refusal_notifier or CollectionImportRefusalAdminNotifier()
        self.failure_notification_service = CollectionImportFailureNotificationService()
        self.refusal_notification_service = CollectionImportRefusalNotificationService()
        self.refusal_policy = CollectionImportRefusalPolicy()
        self.logger = logger or logging.getLogger(__name__)

    @classmethod
    def from_environment(cls) -> "AdminLibraryImportService":
        """Construit le service depuis la configuration d'environnement.

        Args:
            Aucun.

        Returns:
            AdminLibraryImportService: Service configure pour PostgreSQL.

        Raises:
            ValueError: Si la base de donnees n'est pas configuree.
        """

        return cls(
            SqlAlchemyAdminLibraryImportRepository(DatabaseConfiguration.from_environment())
        )

    def import_csv_file(
        self,
        csv_file_path: str,
        original_filename: str = "",
        requester_email: str = "",
    ) -> AdminLibraryImportResult:
        """Importe un CSV admin dans la Bibliotheque globale.

        Args:
            csv_file_path (str): Chemin temporaire du fichier televerse.
            original_filename (str): Nom original transmis par le navigateur.
            requester_email (str): Email ou sujet d'authentification du demandeur admin.

        Returns:
            AdminLibraryImportResult: Compteurs et warnings d'import.

        Raises:
            AdminLibraryImportInvalidFileError: Si le fichier ou la configuration est invalide.
            sqlalchemy.exc.SQLAlchemyError: Si la persistance echoue.
        """

        try:
            self._validate_extension(original_filename or csv_file_path)
            columns = self.reader.analyze_sheets(csv_file_path)
            description = self.configuration_loader.load_for_columns(columns)
            import_data = self.reader.read(csv_file_path, description)
            import_data = self.date_validator.validate(import_data)
            refusal = self.refusal_policy.evaluate(import_data)
            if refusal.refused:
                refusal_payload = refusal.to_dict()
                self.refusal_notification_service.notify_refusal(
                    self.refusal_notifier,
                    self.logger,
                    "bibliotheque_admin_csv",
                    None,
                    requester_email,
                    "csv",
                    original_filename or Path(csv_file_path).name,
                    refusal_payload,
                    import_data,
                )
                return AdminLibraryImportResult(
                    linked_platforms=0,
                    created_studios=0,
                    created_games=0,
                    warnings=import_data.warnings.to_dict(),
                    refusal=refusal_payload,
                )
            persistence_result = self.repository.import_library(import_data)
        except AdminLibraryImportInvalidFileError as exc:
            self._notify_import_failure(exc, csv_file_path, original_filename, requester_email)
            raise
        except AdminLibraryImportConfigurationError as exc:
            converted_error = AdminLibraryImportInvalidFileError(exc.details)
            self._notify_import_failure(
                converted_error,
                csv_file_path,
                original_filename,
                requester_email,
            )
            raise converted_error from exc
        except CollectionFileDescriptionValidationError as exc:
            converted_error = AdminLibraryImportInvalidFileError(exc.details)
            self._notify_import_failure(
                converted_error,
                csv_file_path,
                original_filename,
                requester_email,
            )
            raise converted_error from exc
        except CollectionFileValidationError as exc:
            converted_error = AdminLibraryImportInvalidFileError([str(exc)])
            self._notify_import_failure(
                converted_error,
                csv_file_path,
                original_filename,
                requester_email,
            )
            raise converted_error from exc
        except CollectionFileReadError as exc:
            converted_error = AdminLibraryImportInvalidFileError([str(exc)])
            self._notify_import_failure(
                converted_error,
                csv_file_path,
                original_filename,
                requester_email,
            )
            raise converted_error from exc
        except Exception as exc:
            self._notify_import_failure(exc, csv_file_path, original_filename, requester_email)
            raise
        return AdminLibraryImportResult(
            linked_platforms=persistence_result.linked_platforms,
            created_studios=persistence_result.created_studios,
            created_games=persistence_result.created_games,
            warnings=import_data.warnings.to_dict(),
            refusal={
                "refused": False,
                "reason": "",
                "invalid_games_count": len(import_data.warnings.invalid_games),
                "total_games_count": len(import_data.games),
                "message": "",
            },
        )

    def _validate_extension(self, filename: str) -> None:
        extension = Path(filename or "").suffix.lower()
        if extension not in self.reader.accepted_extensions:
            raise AdminLibraryImportInvalidFileError(["Seuls les fichiers CSV sont acceptes."])

    def _notify_import_failure(
        self,
        error: Exception,
        csv_file_path: str,
        original_filename: str,
        requester_email: str,
    ) -> None:
        self.failure_notification_service.notify_failure(
            self.failure_notifier,
            self.logger,
            error,
            "bibliotheque_admin_csv",
            "AdminLibraryImportService.import_csv_file",
            None,
            requester_email,
            "csv",
            str(original_filename or Path(csv_file_path).name),
        )
