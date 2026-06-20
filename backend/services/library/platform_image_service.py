#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-19
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : service metier des images de plateformes.

from dataclasses import dataclass
from datetime import datetime, timezone
import mimetypes
from pathlib import Path
import re
from math import ceil
from typing import Any, Mapping
import unicodedata

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from werkzeug.datastructures import FileStorage

from services.database.database_configuration import DatabaseConfiguration
from services.database.platform_image_repository import SqlAlchemyPlatformImageRepository
from services.database.user_repository import SqlAlchemyUserRepository
from services.library.library_query_contract import LibraryPageRequest

from .platform_image_moderation_query import PlatformImageModerationQueryParser
from .platform_image_admin_notifier import PlatformImageAdminNotifier
from .platform_image_configuration import PlatformImageConfiguration
from .platform_image_storage_guard import (
    PlatformImageStorageGuard,
    PlatformImageStorageLimitExceededError,
    PlatformImageStorageUsage,
)


class PlatformImageValidationError(ValueError):
    """Signale une image invalide pour l'upload."""


class PlatformImagePlatformNotFoundError(ValueError):
    """Signale une plateforme inconnue."""


class PlatformImageNotFoundError(ValueError):
    """Signale une image publique absente ou inaccessible."""


class PlatformImageUserNotFoundError(ValueError):
    """Signale un utilisateur connecte absent de la base."""


class PlatformImageModerationError(ValueError):
    """Signale une action de moderation invalide ou impossible."""


@dataclass(frozen=True)
class PlatformImageFile:
    """Decrit un fichier image public pret a etre servi.

    Attributes:
        path (str): Chemin absolu du fichier image.
        mimetype (str): Type MIME a retourner.
    """

    path: str
    mimetype: str


class PlatformImageService:
    """Orchestre l'upload et la lecture publique des images de plateformes."""

    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }
    MODERATION_STATUSES = {"WAITING_VALIDATION", "ACCEPTED"}
    MODERATION_TYPES = {"MAIN", "OTHER"}

    def __init__(
        self,
        database_configuration: DatabaseConfiguration,
        image_configuration: PlatformImageConfiguration,
        image_repository: SqlAlchemyPlatformImageRepository | None = None,
        user_repository: SqlAlchemyUserRepository | None = None,
        notifier: PlatformImageAdminNotifier | None = None,
        moderation_query_parser: PlatformImageModerationQueryParser | None = None,
        engine: Engine | None = None,
        engine_factory=create_engine,
    ):
        """Initialise le service d'images de plateformes.

        Args:
            database_configuration (DatabaseConfiguration): Configuration SQL.
            image_configuration (PlatformImageConfiguration): Configuration image.
            image_repository (SqlAlchemyPlatformImageRepository | None): Repository images.
            user_repository (SqlAlchemyUserRepository | None): Repository utilisateurs.
            notifier (PlatformImageAdminNotifier | None): Notifier administrateur.
            moderation_query_parser (PlatformImageModerationQueryParser | None): Parseur admin.
            engine (Engine | None): Moteur SQL injectable.
            engine_factory (Callable): Fabrique de moteur SQLAlchemy.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si la configuration SQL ou image est invalide.
        """

        database_configuration.validate()
        image_configuration.validate()
        if engine is None and not database_configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour gerer les images de plateformes.")
        self.database_configuration = database_configuration
        self.image_configuration = image_configuration
        self.engine = engine or engine_factory(database_configuration.database_url)
        self.image_repository = image_repository or SqlAlchemyPlatformImageRepository(
            database_configuration.schema_name
        )
        self.user_repository = user_repository or SqlAlchemyUserRepository(database_configuration)
        self.notifier = notifier or PlatformImageAdminNotifier.from_environment()
        self.moderation_query_parser = (
            moderation_query_parser or PlatformImageModerationQueryParser()
        )
        self.storage_guard = PlatformImageStorageGuard(image_configuration)

    @classmethod
    def from_environment(cls) -> "PlatformImageService":
        """Construit le service depuis l'environnement.

        Args:
            Aucun.

        Returns:
            PlatformImageService: Service configure.
        """

        return cls(
            DatabaseConfiguration.from_environment(),
            PlatformImageConfiguration.from_environment(),
        )

    def upload_image(
        self,
        platform_id: int,
        uploaded_file: FileStorage | None,
        user_email: str,
    ) -> dict[str, object]:
        """Valide, copie et enregistre une image proposee.

        Args:
            platform_id (int): Identifiant de plateforme.
            uploaded_file (FileStorage | None): Fichier multipart recu.
            user_email (str): Sujet du token utilisateur valide.

        Returns:
            dict[str, object]: Image creee serialisee.

        Raises:
            PlatformImageValidationError: Si le fichier est absent ou invalide.
            PlatformImageStorageLimitExceededError: Si les limites disque sont depassees.
            PlatformImagePlatformNotFoundError: Si la plateforme est inconnue.
            PlatformImageUserNotFoundError: Si l'utilisateur du token est inconnu.
            OSError: Si la copie disque echoue.
        """

        original_filename = self._validate_uploaded_file(uploaded_file)
        normalized_user_email = str(user_email or "").strip().lower()
        user_id = self.user_repository.find_user_id_by_email(normalized_user_email)
        if user_id is None:
            raise PlatformImageUserNotFoundError("Utilisateur connecte introuvable.")
        with self.engine.begin() as connection:
            platform_name = self.image_repository.find_platform_name(connection, platform_id)
            if platform_name is None:
                raise PlatformImagePlatformNotFoundError("Plateforme inconnue.")
            storage_root = self.image_configuration.ensure_image_directory()
            storage_usage = self.storage_guard.usage_from_mapping(
                self.image_repository.get_storage_usage(connection, user_id)
            )
            try:
                self.storage_guard.validate_existing_usage(storage_usage)
                target_path, file_size_bytes = self._copy_file(
                    platform_id,
                    platform_name,
                    original_filename,
                    uploaded_file,
                    storage_root,
                    storage_usage,
                )
            except PlatformImageStorageLimitExceededError as exc:
                self.notifier.notify_upload_disabled(
                    normalized_user_email,
                    exc.reason,
                    exc.metrics,
                )
                raise
            try:
                image = self.image_repository.create_waiting_image(
                    connection,
                    platform_id,
                    str(target_path),
                    file_size_bytes,
                    user_id,
                    datetime.now(timezone.utc).replace(tzinfo=None),
                )
            except Exception:
                target_path.unlink(missing_ok=True)
                raise
        self.notifier.notify_image_created(platform_name, int(image["id"]), normalized_user_email)
        return self._image_payload(image)

    def get_accepted_image_file(self, platform_id: int, image_id: int) -> PlatformImageFile:
        """Retourne le fichier d'une image acceptee.

        Args:
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.

        Returns:
            PlatformImageFile: Fichier public a servir.

        Raises:
            PlatformImageNotFoundError: Si l'image est absente, refusee ou illisible.
        """

        with self.engine.connect() as connection:
            image = self.image_repository.find_accepted_image(connection, platform_id, image_id)
        if image is None:
            raise PlatformImageNotFoundError("Image acceptee introuvable.")
        path = Path(str(image["path"]))
        if not path.is_file():
            raise PlatformImageNotFoundError("Image acceptee inaccessible.")
        mimetype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return PlatformImageFile(path=str(path), mimetype=mimetype)

    def get_moderation_image_file(self, platform_id: int, image_id: int) -> PlatformImageFile:
        """Retourne le fichier d'une image pour la moderation admin.

        Args:
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.

        Returns:
            PlatformImageFile: Fichier protege a servir.

        Raises:
            PlatformImageNotFoundError: Si l'image est absente ou illisible.
        """

        with self.engine.connect() as connection:
            image = self.image_repository.find_image(connection, platform_id, image_id)
        if image is None:
            raise PlatformImageNotFoundError("Image de plateforme introuvable.")
        path = Path(str(image["path"]))
        if not path.is_file():
            raise PlatformImageNotFoundError("Image de plateforme inaccessible.")
        mimetype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return PlatformImageFile(path=str(path), mimetype=mimetype)

    def list_moderation_images(
        self,
        query_parameters: Mapping[str, Any],
    ) -> dict[str, object]:
        """Liste les images de plateformes a moderer.

        Args:
            query_parameters (Mapping[str, Any]): Parametres HTTP de pagination et filtres.

        Returns:
            dict[str, object]: Payload pagine contenant `images`, `page` et le stockage.
        """

        criteria = self.moderation_query_parser.parse(query_parameters)
        with self.engine.connect() as connection:
            total_elements = self.image_repository.count_moderation_images(
                connection,
                criteria.status,
                criteria.platform,
            )
            rows = self.image_repository.list_moderation_images(
                connection,
                criteria.status,
                criteria.platform,
                criteria.page_request,
                criteria.sort_rules,
            )
            storage_summary = self.image_repository.get_global_storage_summary(connection)
        return {
            "images": [self._moderation_image_payload(row) for row in rows],
            "page": self._page_payload(criteria.page_request, total_elements),
            "storage_summary": {
                "total_images": int(storage_summary.get("total_images") or 0),
                "total_size_bytes": int(storage_summary.get("total_size_bytes") or 0),
            },
        }

    def update_image_status(
        self,
        platform_id: int,
        image_id: int,
        status: str,
    ) -> dict[str, object]:
        """Accepte ou refuse une image de plateforme.

        Args:
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.
            status (str): Statut demande, `accepted` ou `refused`.

        Returns:
            dict[str, object]: Resultat de moderation.

        Raises:
            PlatformImageNotFoundError: Si l'image ou la plateforme est inconnue.
            PlatformImageModerationError: Si le statut demande est invalide.
        """

        normalized_status = str(status or "").strip().lower()
        if normalized_status == "accepted":
            with self.engine.begin() as connection:
                image = self.image_repository.update_image_status(
                    connection,
                    platform_id,
                    image_id,
                    "ACCEPTED",
                )
            if image is None:
                raise PlatformImageNotFoundError("Image de plateforme introuvable.")
            return {"image": self._image_payload(image)}
        if normalized_status == "refused":
            return self._refuse_image(platform_id, image_id)
        raise PlatformImageModerationError("Statut de moderation invalide.")

    def update_image_type(
        self,
        platform_id: int,
        image_id: int,
        image_type: str,
    ) -> dict[str, object]:
        """Modifie le type d'une image de plateforme.

        Args:
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.
            image_type (str): Type demande, `MAIN` ou `OTHER`.

        Returns:
            dict[str, object]: Image modifiee.

        Raises:
            PlatformImageNotFoundError: Si l'image ou la plateforme est inconnue.
            PlatformImageModerationError: Si le type demande est invalide.
        """

        normalized_type = str(image_type or "").strip().upper()
        if normalized_type not in self.MODERATION_TYPES:
            raise PlatformImageModerationError("Type d'image invalide.")
        with self.engine.begin() as connection:
            image = self.image_repository.set_image_type(
                connection,
                platform_id,
                image_id,
                normalized_type,
            )
        if image is None:
            raise PlatformImageNotFoundError("Image de plateforme introuvable.")
        return {"image": self._image_payload(image)}

    def _validate_uploaded_file(self, uploaded_file: FileStorage | None) -> str:
        if uploaded_file is None or not uploaded_file.filename:
            raise PlatformImageValidationError("Le champ multipart image est requis.")
        original_filename = Path(uploaded_file.filename).name
        extension = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else ""
        if extension not in self.ALLOWED_EXTENSIONS:
            raise PlatformImageValidationError("Extension d'image invalide.")
        if uploaded_file.mimetype not in self.ALLOWED_MIME_TYPES:
            raise PlatformImageValidationError("MIME d'image invalide.")
        return original_filename

    def _copy_file(
        self,
        platform_id: int,
        platform_name: str,
        original_filename: str,
        uploaded_file: FileStorage,
        storage_root: Path,
        storage_usage: PlatformImageStorageUsage,
    ) -> tuple[Path, int]:
        platform_directory = storage_root / "platforms" / self._slugify(platform_name, platform_id)
        platform_directory.mkdir(parents=True, exist_ok=True)
        target_path = self._resolve_available_path(platform_directory, original_filename)
        bytes_written = 0
        with target_path.open("wb") as target_file:
            while True:
                chunk = uploaded_file.stream.read(1024 * 1024)
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > self.image_configuration.max_upload_bytes:
                    target_file.close()
                    target_path.unlink(missing_ok=True)
                    raise PlatformImageValidationError("Image trop volumineuse.")
                try:
                    self.storage_guard.validate_uploaded_bytes(bytes_written, storage_usage)
                except PlatformImageStorageLimitExceededError:
                    target_file.close()
                    target_path.unlink(missing_ok=True)
                    raise
                target_file.write(chunk)
        if bytes_written == 0:
            target_path.unlink(missing_ok=True)
            raise PlatformImageValidationError("Image vide.")
        return target_path, bytes_written

    def _resolve_available_path(self, directory: Path, original_filename: str) -> Path:
        candidate = directory / original_filename
        if not candidate.exists():
            return candidate
        stem = candidate.stem
        suffix = candidate.suffix
        counter = 1
        while True:
            numbered_candidate = directory / f"{stem}-{counter}{suffix}"
            if not numbered_candidate.exists():
                return numbered_candidate
            counter += 1

    def _slugify(self, platform_name: str, platform_id: int) -> str:
        normalized = unicodedata.normalize("NFKD", platform_name)
        ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
        slug = re.sub(r"-+", "-", slug)
        return slug or f"platform-{platform_id}"

    def _refuse_image(self, platform_id: int, image_id: int) -> dict[str, object]:
        with self.engine.begin() as connection:
            image = self.image_repository.find_image(connection, platform_id, image_id)
            if image is None:
                raise PlatformImageNotFoundError("Image de plateforme introuvable.")
            self.image_repository.delete_image(connection, platform_id, image_id)
        Path(str(image["path"])).unlink(missing_ok=True)
        return {
            "image": self._image_payload(image),
            "deleted": True,
        }

    def _page_payload(
        self,
        page_request: LibraryPageRequest,
        total_elements: int,
    ) -> dict[str, int]:
        page_size = page_request.size
        return {
            "totalElements": total_elements,
            "page": page_request.page,
            "size": page_size,
            "totalPages": ceil(total_elements / page_size) if total_elements else 0,
        }

    def _image_payload(self, image: dict[str, object]) -> dict[str, object]:
        return {
            "id": int(image["id"]),
            "platform_id": int(image["platform"]),
            "file_size_bytes": int(image.get("file_size_bytes") or 0),
            "type": str(image["type"]),
            "status": str(image["status"]),
            "user_id": int(image["user_id"]),
        }

    def _moderation_image_payload(self, image: dict[str, object]) -> dict[str, object]:
        payload = self._image_payload(image)
        payload.update(
            {
                "platform_name": str(image.get("platform_name") or ""),
                "user_email": str(image.get("user_email") or ""),
                "creation_date": self._date_value(image.get("creation_date")),
                "image_url": (
                    f"/api/library/platforms/{int(image['platform'])}/image/{int(image['id'])}"
                ),
                "moderation_image_url": (
                    f"/api/library/platforms/{int(image['platform'])}/image/"
                    f"{int(image['id'])}/moderation"
                ),
            }
        )
        return payload

    def _date_value(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        return "" if value is None else str(value)
