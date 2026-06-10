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

import shutil
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Protocol

from services.collection.imports import (
    CollectionFileDescription,
    CollectionFileDescriptionValidationError,
    CollectionFileReader,
    CollectionFileReaderFactory,
    CollectionFileReadError,
    CollectionFileValidationError,
    CollectionImportData,
)
from services.database.user_collection_import_repository import (
    UserCollectionImportPersistenceResult,
    UserCollectionImportUserNotFoundError,
    UserCollectionReinitializationNotFoundError,
)

from .collection_import_date_validator import CollectionImportDateValidator
from .user_collection_import_configuration import UserCollectionImportConfiguration


class UserCollectionImportError(Exception):
    """Classe de base des erreurs metier d'import de collection utilisateur."""


class UserCollectionImportInvalidFileError(UserCollectionImportError):
    """Signale qu'un fichier d'import est invalide ou illisible."""

    def __init__(self, message: str, details: list[str] | None = None):
        """Initialise l'erreur de fichier invalide.

        Args:
            message (str): Message fonctionnel principal.
            details (list[str] | None): Raisons techniques affichables.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.details = details or [message]
        super().__init__(message)


class UserCollectionImportTooLargeError(UserCollectionImportError):
    """Signale qu'un fichier d'import depasse la taille maximale autorisee."""


class UserCollectionImportTemporaryFileMissingError(UserCollectionImportError):
    """Signale que le fichier temporaire d'import est absent."""


class UserCollectionImportNotFoundError(UserCollectionImportError):
    """Signale qu'aucune collection utilisateur ne peut etre reinitialisee."""


class UserCollectionImportUnexpectedError(UserCollectionImportError):
    """Signale une erreur non fonctionnelle pendant l'import."""


class UserCollectionImportRepository(Protocol):
    """Definit les operations de persistance requises par l'import."""

    def user_has_collection(self, user_id: int) -> bool:
        """Indique si un utilisateur a deja une collection.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            bool: `True` si une collection existe deja.
        """

    def import_collection(
        self,
        user_id: int,
        collection_file_path: str,
        import_data: CollectionImportData,
        collection_file_description: dict,
    ) -> UserCollectionImportPersistenceResult:
        """Persiste les donnees importees dans une transaction.

        Args:
            user_id (int): Identifiant utilisateur.
            collection_file_path (str): Chemin final du fichier.
            import_data (CollectionImportData): Donnees lues depuis le fichier.
            collection_file_description (dict): Description valide ayant servi a l'import.

        Returns:
            UserCollectionImportPersistenceResult: Compteurs de persistance.
        """
    def reinitialize_collection(self, user_id: int) -> None:
        """Reinitialise la collection persistante d'un utilisateur.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            UserCollectionImportNotFoundError: Si aucune collection n'existe.
            UserCollectionImportUnexpectedError: Si la reinitialisation echoue.
        """


@dataclass(frozen=True)
class UserCollectionImportResult:
    """Regroupe les compteurs retournes apres un import reussi.

    Attributes:
        created_platforms (int): Nombre de plateformes creees.
        created_studios (int): Nombre de studios crees.
        created_games (int): Nombre de jeux crees.
        associated_games (int): Nombre de jeux associes a l'utilisateur.
        wishlisted_games (int): Nombre de jeux importes comme souhaits.
        warnings (dict): Avertissements fonctionnels de l'import.
    """

    created_platforms: int
    created_studios: int
    created_games: int
    associated_games: int
    wishlisted_games: int = 0
    warnings: dict | None = None

    def to_dict(self) -> dict[str, int | dict]:
        """Convertit le resultat en dictionnaire serialisable.

        Args:
            Aucun.

        Returns:
            dict[str, int]: Compteurs d'import.
        """

        return {
            "created_platforms": self.created_platforms,
            "created_studios": self.created_studios,
            "created_games": self.created_games,
            "associated_games": self.associated_games,
            "wishlisted_games": self.wishlisted_games,
            "warnings": self.warnings or {
                "invalid_wishlist": 0,
                "invalid_wishlist_values_found": [],
                "invalid_games": [],
            },
        }


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
    ):
        """Initialise le service d'import de collection.

        Args:
            configuration (UserCollectionImportConfiguration): Configuration d'import.
            repository (UserCollectionImportRepository): Persistance transactionnelle.
            reader_factory (CollectionFileReaderFactory): Factory de lecteurs.
            date_validator (CollectionImportDateValidator | None): Validateur des dates lues.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration
        self.repository = repository
        self.reader_factory = reader_factory
        self.date_validator = date_validator or CollectionImportDateValidator()

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
            self._validate_source_file(source_path, original_filename, reader)
            self._copy_file(source_path, self._temporary_file_path(user_id, reader))

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
        temporary_file_path = self._temporary_file_path(user_id, reader)
        self._ensure_temporary_file_exists(temporary_file_path)
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
    ) -> UserCollectionImportResult:
        """Importe la collection depuis le fichier temporaire utilisateur.

        Args:
            user_id (int): Identifiant utilisateur connecte.
            file_description (CollectionFileDescription | None): Description valide du fichier.

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
        temporary_file_path = self._temporary_file_path(user_id, reader)
        self._ensure_temporary_file_exists(temporary_file_path)
        result = self.import_collection(
            user_id,
            str(temporary_file_path),
            temporary_file_path.name,
            file_description,
        )
        self._delete_copied_file(temporary_file_path)
        return result

    def import_collection(
        self,
        user_id: int,
        source_file_path: str,
        original_filename: str | None = None,
        file_description: CollectionFileDescription | None = None,
    ) -> UserCollectionImportResult:
        """Importe le fichier de collection d'un utilisateur.

        Args:
            user_id (int): Identifiant utilisateur connecte.
            source_file_path (str): Chemin du fichier temporaire uploade.
            original_filename (str | None): Nom original du fichier uploade.
            file_description (CollectionFileDescription | None): Description valide du fichier.

        Returns:
            UserCollectionImportResult: Compteurs de l'import reussi.

        Raises:
            UserCollectionImportInvalidFileError: Si le fichier est invalide.
            UserCollectionImportTooLargeError: Si le fichier est trop volumineux.
            UserCollectionImportUnexpectedError: Si une erreur non fonctionnelle survient.
        """

        user_lock = self._lock_for_user(user_id)
        with user_lock:
            return self._import_collection_locked(
                user_id,
                Path(source_file_path),
                original_filename,
                file_description,
            )

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
    ) -> UserCollectionImportResult:
        if file_description is None:
            raise CollectionFileDescriptionValidationError(
                ["collection_file_description est requis."]
            )
        reader = self.reader_factory.create(file_description.file_type)
        self._validate_source_file(source_file_path, original_filename, reader)
        target_file_path = self._target_file_path(
            user_id,
            original_filename or source_file_path.name,
            reader,
        )
        copied_file_path = self._copy_file(source_file_path, target_file_path)
        try:
            import_data = self.date_validator.validate(
                reader.read(str(copied_file_path), file_description)
            )
            persistence_result = self.repository.import_collection(
                user_id,
                str(copied_file_path),
                import_data,
                file_description.to_dict(),
            )
            return self._map_result(persistence_result, import_data)
        except CollectionFileDescriptionValidationError:
            self._delete_copied_file(copied_file_path)
            raise
        except (CollectionFileReadError, CollectionFileValidationError) as exc:
            self._delete_copied_file(copied_file_path)
            raise UserCollectionImportInvalidFileError(
                "Fichier de collection invalide.",
                self._import_invalid_file_details(exc),
            ) from exc
        except UserCollectionImportUserNotFoundError as exc:
            self._delete_copied_file(copied_file_path)
            raise UserCollectionImportUnexpectedError("Utilisateur introuvable.") from exc
        except Exception as exc:
            self._delete_copied_file(copied_file_path)
            raise UserCollectionImportUnexpectedError("Erreur pendant l'import.") from exc

    def _validate_source_file(
        self,
        source_file_path: Path,
        original_filename: str | None,
        reader: CollectionFileReader,
    ) -> None:
        checked_filename = original_filename or source_file_path.name
        if not self._has_accepted_extension(checked_filename, reader.accepted_extensions):
            accepted_extensions = ", ".join(reader.accepted_extensions)
            raise UserCollectionImportInvalidFileError(
                f"Le fichier doit utiliser une extension acceptee: {accepted_extensions}."
            )
        try:
            file_size = source_file_path.stat().st_size
        except OSError as exc:
            raise UserCollectionImportInvalidFileError("Le fichier source est illisible.") from exc
        if file_size > self.configuration.max_upload_bytes:
            raise UserCollectionImportTooLargeError("Le fichier depasse la taille maximale.")

    def _copy_file(self, source_file_path: Path, target_file_path: Path) -> Path:
        try:
            target_file_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file_path, target_file_path)
            target_file_path.chmod(0o440)
        except OSError as exc:
            self._delete_copied_file(target_file_path)
            raise UserCollectionImportUnexpectedError("Impossible de copier le fichier.") from exc
        return target_file_path

    def _target_file_path(
        self,
        user_id: int,
        original_filename: str | None,
        reader: CollectionFileReader,
    ) -> Path:
        workspace_directory = self.configuration.ensure_workspace_directory()
        extension = self._validated_extension(original_filename, reader.accepted_extensions)
        return workspace_directory / str(user_id) / f"{user_id}-collection{extension}"

    def _temporary_file_path(self, user_id: int, reader: CollectionFileReader) -> Path:
        workspace_directory = self.configuration.ensure_workspace_directory()
        return workspace_directory / str(user_id) / f"current-import{reader.accepted_extensions[0]}"

    def _ensure_temporary_file_exists(self, temporary_file_path: Path) -> None:
        if not temporary_file_path.exists():
            raise UserCollectionImportTemporaryFileMissingError(
                "Fichier temporaire introuvable."
            )

    def _has_accepted_extension(
        self,
        filename: str,
        accepted_extensions: tuple[str, ...],
    ) -> bool:
        return self._validated_extension(filename, accepted_extensions) is not None

    def _validated_extension(
        self,
        filename: str | None,
        accepted_extensions: tuple[str, ...],
    ) -> str | None:
        checked_filename = str(filename or "").lower().strip()
        for extension in accepted_extensions:
            if checked_filename.endswith(extension):
                return extension
        return None

    def _delete_copied_file(self, copied_file_path: Path) -> None:
        try:
            copied_file_path.unlink(missing_ok=True)
        except OSError:
            pass

    def _import_invalid_file_details(self, error: Exception) -> list[str]:
        messages = [str(error).strip()]
        cause = getattr(error, "__cause__", None)
        if cause is not None:
            cause_message = str(cause).strip()
            if cause_message:
                messages.append(cause_message)
        return [message for message in messages if message]

    def _map_result(
        self,
        persistence_result: UserCollectionImportPersistenceResult,
        import_data: CollectionImportData,
    ) -> UserCollectionImportResult:
        return UserCollectionImportResult(
            created_platforms=persistence_result.created_platforms,
            created_studios=persistence_result.created_studios,
            created_games=persistence_result.created_games,
            associated_games=persistence_result.associated_games,
            wishlisted_games=sum(1 for game in import_data.games if game.wishlist),
            warnings=import_data.warnings.to_dict(),
        )

    @classmethod
    def _lock_for_user(cls, user_id: int) -> Lock:
        with cls._locks_guard:
            if user_id not in cls._locks_by_user_id:
                cls._locks_by_user_id[user_id] = Lock()
            return cls._locks_by_user_id[user_id]
