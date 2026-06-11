#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
# Projet : CloudCollectionApp
# Date de creation : 2026-06-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : import depuis un fichier de collection utilisateur deja stocke.

from pathlib import Path

from services.collection.imports import (
    CollectionFileDescription,
    CollectionFileDescriptionValidationError,
    CollectionFileReadError,
    CollectionFileValidationError,
)
from services.database.user_collection_import_repository import (
    UserCollectionImportUserNotFoundError,
)

from .user_collection_import_service import (
    UserCollectionImportInvalidFileError,
    UserCollectionImportResult,
    UserCollectionImportService,
    UserCollectionImportUnexpectedError,
)


class StoredUserCollectionImportService(UserCollectionImportService):
    """Importe une collection depuis le fichier serveur deja conserve."""

    def import_stored_collection(
        self,
        user_id: int,
        stored_file_path: str,
        file_description: CollectionFileDescription | None,
    ) -> UserCollectionImportResult:
        """Importe une collection depuis son fichier serveur deja stocke.

        Args:
            user_id (int): Identifiant utilisateur connecte.
            stored_file_path (str): Chemin du fichier de collection conserve.
            file_description (CollectionFileDescription | None): Description valide du fichier.

        Returns:
            UserCollectionImportResult: Compteurs de l'import reussi.

        Raises:
            UserCollectionImportInvalidFileError: Si le fichier est invalide.
            UserCollectionImportUnexpectedError: Si une erreur non fonctionnelle survient.
        """

        user_lock = self._lock_for_user(user_id)
        with user_lock:
            return self._import_stored_collection_locked(
                user_id,
                Path(stored_file_path),
                file_description,
            )

    def _import_stored_collection_locked(
        self,
        user_id: int,
        stored_file_path: Path,
        file_description: CollectionFileDescription | None,
    ) -> UserCollectionImportResult:
        if file_description is None:
            raise CollectionFileDescriptionValidationError(
                ["collection_file_description est requis."]
            )
        reader = self.reader_factory.create(file_description.file_type)
        self._validate_source_file(stored_file_path, stored_file_path.name, reader)
        try:
            import_data = self.date_validator.validate(
                reader.read(str(stored_file_path), file_description)
            )
            persistence_result = self.repository.import_collection(
                user_id,
                str(stored_file_path),
                import_data,
                file_description.to_dict(),
            )
            return self._map_result(persistence_result, import_data)
        except CollectionFileDescriptionValidationError:
            raise
        except (CollectionFileReadError, CollectionFileValidationError) as exc:
            raise UserCollectionImportInvalidFileError(
                "Fichier de collection invalide.",
                self._import_invalid_file_details(exc),
            ) from exc
        except UserCollectionImportUserNotFoundError as exc:
            raise UserCollectionImportUnexpectedError("Utilisateur introuvable.") from exc
        except Exception as exc:
            raise UserCollectionImportUnexpectedError("Erreur pendant l'import.") from exc
