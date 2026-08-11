#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | |__|  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : gestion des fichiers temporaires et conserves pendant l'import utilisateur.

import shutil
from pathlib import Path

from services.collection.imports import CollectionFileReader

from .user_collection_import_configuration import UserCollectionImportConfiguration
from .user_collection_import_errors import (
    UserCollectionImportInvalidFileError,
    UserCollectionImportTemporaryFileMissingError,
    UserCollectionImportTooLargeError,
    UserCollectionImportUnexpectedError,
)


class UserCollectionImportFileManager:
    """Centralise les operations de fichiers du workflow d'import utilisateur."""

    def __init__(self, configuration: UserCollectionImportConfiguration):
        """Initialise le gestionnaire de fichiers d'import.

        Args:
            configuration (UserCollectionImportConfiguration): Configuration des chemins et tailles.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration

    def validate_source_file(
        self,
        source_file_path: Path,
        original_filename: str | None,
        reader: CollectionFileReader,
    ) -> None:
        """Valide l'extension et la taille du fichier source.

        Args:
            source_file_path (Path): Chemin du fichier a controler.
            original_filename (str | None): Nom original transmis par le navigateur.
            reader (CollectionFileReader): Lecteur attendu pour le type de fichier.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            UserCollectionImportInvalidFileError: Si l'extension ou la lecture est invalide.
            UserCollectionImportTooLargeError: Si la taille maximale est depassee.
        """

        checked_filename = original_filename or source_file_path.name
        if not self.has_accepted_extension(checked_filename, reader.accepted_extensions):
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

    def copy_file(self, source_file_path: Path, target_file_path: Path) -> Path:
        """Copie un fichier d'import et applique les droits attendus.

        Args:
            source_file_path (Path): Fichier source.
            target_file_path (Path): Destination finale.

        Returns:
            Path: Chemin du fichier copie.

        Raises:
            UserCollectionImportUnexpectedFileError: Si la copie echoue.
        """

        try:
            target_file_path.parent.mkdir(parents=True, exist_ok=True)
            target_file_path.unlink(missing_ok=True)
            shutil.copyfile(source_file_path, target_file_path)
            target_file_path.chmod(0o750)
        except OSError as exc:
            self.delete_copied_file(target_file_path)
            raise UserCollectionImportUnexpectedError(
                "Impossible de copier le fichier."
            ) from exc
        return target_file_path

    def target_file_path(
        self,
        user_id: int,
        original_filename: str | None,
        reader: CollectionFileReader,
    ) -> Path:
        """Construit le chemin du fichier conserve pour l'utilisateur.

        Args:
            user_id (int): Identifiant utilisateur.
            original_filename (str | None): Nom original du fichier.
            reader (CollectionFileReader): Lecteur attendu.

        Returns:
            Path: Chemin cible dans le workspace utilisateur.
        """

        workspace_directory = self.configuration.ensure_workspace_directory()
        extension = self.validated_extension(original_filename, reader.accepted_extensions)
        return workspace_directory / str(user_id) / f"{user_id}-collection{extension}"

    def temporary_file_path(self, user_id: int, reader: CollectionFileReader) -> Path:
        """Construit le chemin du fichier temporaire d'import.

        Args:
            user_id (int): Identifiant utilisateur.
            reader (CollectionFileReader): Lecteur attendu.

        Returns:
            Path: Chemin du fichier temporaire.
        """

        workspace_directory = self.configuration.ensure_workspace_directory()
        return workspace_directory / str(user_id) / f"current-import{reader.accepted_extensions[0]}"

    def ensure_temporary_file_exists(self, temporary_file_path: Path) -> None:
        """Verifie que le fichier temporaire d'import existe.

        Args:
            temporary_file_path (Path): Chemin temporaire attendu.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            UserCollectionImportTemporaryFileMissingError: Si le fichier est absent.
        """

        if not temporary_file_path.exists():
            raise UserCollectionImportTemporaryFileMissingError(
                "Fichier temporaire introuvable."
            )

    def has_accepted_extension(
        self,
        filename: str,
        accepted_extensions: tuple[str, ...],
    ) -> bool:
        """Indique si un nom de fichier utilise une extension acceptee.

        Args:
            filename (str): Nom a verifier.
            accepted_extensions (tuple[str, ...]): Extensions autorisees.

        Returns:
            bool: `True` quand une extension attendue est trouvee.
        """

        return self.validated_extension(filename, accepted_extensions) is not None

    def validated_extension(
        self,
        filename: str | None,
        accepted_extensions: tuple[str, ...],
    ) -> str | None:
        """Retourne l'extension acceptee trouvee dans un nom de fichier.

        Args:
            filename (str | None): Nom a verifier.
            accepted_extensions (tuple[str, ...]): Extensions autorisees.

        Returns:
            str | None: Extension acceptee ou `None`.
        """

        checked_filename = str(filename or "").lower().strip()
        for extension in accepted_extensions:
            if checked_filename.endswith(extension):
                return extension
        return None

    def delete_copied_file(self, copied_file_path: Path | None) -> None:
        """Supprime un fichier copie si son chemin existe.

        Args:
            copied_file_path (Path | None): Chemin a supprimer.

        Returns:
            None: La methode ignore les erreurs de suppression.
        """

        if copied_file_path is None:
            return
        try:
            copied_file_path.unlink(missing_ok=True)
        except OSError:
            pass
