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

from services.database.user_collection_import_repository import (
    UserCollectionAlreadyImportedError,
    UserCollectionImportPersistenceResult,
    UserCollectionImportUserNotFoundError,
)
from services.ods import (
    OdsCollectionImportData,
    OdsCollectionImportReadError,
    OdsCollectionImportReader,
    OdsCollectionImportValidationError,
)

from .user_collection_import_configuration import UserCollectionImportConfiguration


class UserCollectionImportError(Exception):
    """Classe de base des erreurs metier d'import de collection utilisateur."""


class UserCollectionImportConflictError(UserCollectionImportError):
    """Signale qu'une collection utilisateur est deja importee."""


class UserCollectionImportInvalidFileError(UserCollectionImportError):
    """Signale qu'un fichier d'import est invalide ou illisible."""


class UserCollectionImportTooLargeError(UserCollectionImportError):
    """Signale qu'un fichier d'import depasse la taille maximale autorisee."""


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
        import_data: OdsCollectionImportData,
    ) -> UserCollectionImportPersistenceResult:
        """Persiste les donnees importees dans une transaction.

        Args:
            user_id (int): Identifiant utilisateur.
            collection_file_path (str): Chemin final du fichier.
            import_data (OdsCollectionImportData): Donnees lues depuis l'ODS.

        Returns:
            UserCollectionImportPersistenceResult: Compteurs de persistance.
        """


@dataclass(frozen=True)
class UserCollectionImportResult:
    """Regroupe les compteurs retournes apres un import reussi.

    Attributes:
        created_platforms (int): Nombre de plateformes creees.
        created_studios (int): Nombre de studios crees.
        created_games (int): Nombre de jeux crees.
        associated_games (int): Nombre de jeux associes a l'utilisateur.
    """

    created_platforms: int
    created_studios: int
    created_games: int
    associated_games: int

    def to_dict(self) -> dict[str, int]:
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
        }


class UserCollectionImportService:
    """Orchestre l'import complet d'une collection utilisateur."""

    _locks_by_user_id: dict[int, Lock] = {}
    _locks_guard = Lock()

    def __init__(
        self,
        configuration: UserCollectionImportConfiguration,
        repository: UserCollectionImportRepository,
        ods_reader: OdsCollectionImportReader,
    ):
        """Initialise le service d'import de collection.

        Args:
            configuration (UserCollectionImportConfiguration): Configuration d'import.
            repository (UserCollectionImportRepository): Persistance transactionnelle.
            ods_reader (OdsCollectionImportReader): Lecteur ODS dedie a l'import.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration
        self.repository = repository
        self.ods_reader = ods_reader

    def import_collection(
        self,
        user_id: int,
        source_file_path: str,
        original_filename: str | None = None,
    ) -> UserCollectionImportResult:
        """Importe le fichier de collection d'un utilisateur.

        Args:
            user_id (int): Identifiant utilisateur connecte.
            source_file_path (str): Chemin du fichier temporaire uploade.
            original_filename (str | None): Nom original du fichier uploade.

        Returns:
            UserCollectionImportResult: Compteurs de l'import reussi.

        Raises:
            UserCollectionImportConflictError: Si la collection existe deja.
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
            )

    def _import_collection_locked(
        self,
        user_id: int,
        source_file_path: Path,
        original_filename: str | None,
    ) -> UserCollectionImportResult:
        """Execute l'import une fois le verrou utilisateur acquis.

        Args:
            user_id (int): Identifiant utilisateur.
            source_file_path (Path): Chemin du fichier source.
            original_filename (str | None): Nom original optionnel.

        Returns:
            UserCollectionImportResult: Compteurs de l'import.

        Raises:
            UserCollectionImportError: Si l'import echoue.
        """

        self._ensure_user_has_no_collection(user_id)
        self._validate_source_file(source_file_path, original_filename)
        target_file_path = self._target_file_path(user_id)
        copied_file_path = self._copy_file(source_file_path, target_file_path)
        try:
            import_data = self.ods_reader.read(str(copied_file_path))
            persistence_result = self.repository.import_collection(
                user_id,
                str(copied_file_path),
                import_data,
            )
            return self._map_result(persistence_result)
        except (OdsCollectionImportReadError, OdsCollectionImportValidationError) as exc:
            self._delete_copied_file(copied_file_path)
            raise UserCollectionImportInvalidFileError("Fichier de collection invalide.") from exc
        except UserCollectionAlreadyImportedError as exc:
            self._delete_copied_file(copied_file_path)
            raise UserCollectionImportConflictError("Collection deja importee.") from exc
        except UserCollectionImportUserNotFoundError as exc:
            self._delete_copied_file(copied_file_path)
            raise UserCollectionImportUnexpectedError("Utilisateur introuvable.") from exc
        except Exception as exc:
            self._delete_copied_file(copied_file_path)
            raise UserCollectionImportUnexpectedError("Erreur pendant l'import.") from exc

    def _ensure_user_has_no_collection(self, user_id: int) -> None:
        """Verifie que l'utilisateur n'a pas deja de collection.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            UserCollectionImportConflictError: Si une collection existe deja.
        """

        if self.repository.user_has_collection(user_id):
            raise UserCollectionImportConflictError("Collection deja importee.")

    def _validate_source_file(
        self,
        source_file_path: Path,
        original_filename: str | None,
    ) -> None:
        """Valide le type et la taille du fichier source.

        Args:
            source_file_path (Path): Fichier source.
            original_filename (str | None): Nom original optionnel.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            UserCollectionImportInvalidFileError: Si le fichier n'est pas un ODS.
            UserCollectionImportTooLargeError: Si le fichier est trop volumineux.
        """

        checked_filename = original_filename or source_file_path.name
        if checked_filename.lower().strip().endswith(".ods") is False:
            raise UserCollectionImportInvalidFileError("Le fichier doit etre au format ODS.")
        try:
            file_size = source_file_path.stat().st_size
        except OSError as exc:
            raise UserCollectionImportInvalidFileError("Le fichier source est illisible.") from exc
        if file_size > self.configuration.max_upload_bytes:
            raise UserCollectionImportTooLargeError("Le fichier depasse la taille maximale.")

    def _copy_file(self, source_file_path: Path, target_file_path: Path) -> Path:
        """Copie le fichier source vers le workspace utilisateur.

        Args:
            source_file_path (Path): Fichier source.
            target_file_path (Path): Chemin cible.

        Returns:
            Path: Chemin du fichier copie.

        Raises:
            UserCollectionImportUnexpectedError: Si la copie echoue.
        """

        try:
            target_file_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file_path, target_file_path)
            target_file_path.chmod(0o440)
        except OSError as exc:
            self._delete_copied_file(target_file_path)
            raise UserCollectionImportUnexpectedError("Impossible de copier le fichier.") from exc
        return target_file_path

    def _target_file_path(self, user_id: int) -> Path:
        """Construit le chemin final du fichier de collection utilisateur.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            Path: Chemin `/users/workspace/<user_id>/<user_id>-collection.ods`.
        """

        workspace_directory = self.configuration.ensure_workspace_directory()
        return workspace_directory / str(user_id) / f"{user_id}-collection.ods"

    def _delete_copied_file(self, copied_file_path: Path) -> None:
        """Supprime le fichier copie si l'import echoue.

        Args:
            copied_file_path (Path): Fichier a supprimer.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        try:
            copied_file_path.unlink(missing_ok=True)
        except OSError:
            pass

    def _map_result(
        self,
        persistence_result: UserCollectionImportPersistenceResult,
    ) -> UserCollectionImportResult:
        """Convertit le resultat de persistance en resultat service.

        Args:
            persistence_result (UserCollectionImportPersistenceResult): Compteurs SQL.

        Returns:
            UserCollectionImportResult: Compteurs exposes par le service.
        """

        return UserCollectionImportResult(
            created_platforms=persistence_result.created_platforms,
            created_studios=persistence_result.created_studios,
            created_games=persistence_result.created_games,
            associated_games=persistence_result.associated_games,
        )

    @classmethod
    def _lock_for_user(cls, user_id: int) -> Lock:
        """Retourne le verrou applicatif associe a un utilisateur.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            Lock: Verrou partage pour l'utilisateur.
        """

        with cls._locks_guard:
            if user_id not in cls._locks_by_user_id:
                cls._locks_by_user_id[user_id] = Lock()
            return cls._locks_by_user_id[user_id]
