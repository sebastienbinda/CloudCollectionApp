#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : garde-fou des quotas de stockage des images de plateformes.

from dataclasses import dataclass
from typing import Mapping

from .platform_image_configuration import PlatformImageConfiguration


@dataclass(frozen=True)
class PlatformImageStorageUsage:
    """Decrit l'occupation de stockage utilisee pour controler les quotas.

    Attributes:
        pending_image_count (int): Nombre d'images en attente pour l'utilisateur.
        pending_image_bytes (int): Taille des images en attente pour l'utilisateur.
        total_image_bytes (int): Taille totale des fichiers d'images stockee en base.
    """

    pending_image_count: int
    pending_image_bytes: int
    total_image_bytes: int


class PlatformImageStorageLimitExceededError(ValueError):
    """Signale que les quotas de stockage des images de plateformes sont depasses."""

    USER_MESSAGE = (
        "Il y a actuellement trop d'images sur le serveur. "
        "La fonctionnalite est temporairement desactivee."
    )

    def __init__(self, reason: str, metrics: Mapping[str, int]):
        """Initialise l'erreur de quota disque.

        Args:
            reason (str): Limite ayant bloque l'upload.
            metrics (Mapping[str, int]): Valeurs utiles au diagnostic admin.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        super().__init__(self.USER_MESSAGE)
        self.reason = reason
        self.metrics = dict(metrics)


class PlatformImageStorageGuard:
    """Controle les limites de stockage avant et pendant un upload d'image."""

    def __init__(self, configuration: PlatformImageConfiguration):
        """Initialise le controleur de quotas de stockage.

        Args:
            configuration (PlatformImageConfiguration): Configuration des limites.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration

    def validate_existing_usage(self, usage: PlatformImageStorageUsage) -> None:
        """Valide les quotas avant de commencer l'ecriture d'une image.

        Args:
            usage (PlatformImageStorageUsage): Occupation connue depuis la base.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            PlatformImageStorageLimitExceededError: Si une limite est deja atteinte.
        """

        self._validate_usage_thresholds(usage)

    def usage_from_mapping(self, storage_usage: Mapping[str, object]) -> PlatformImageStorageUsage:
        """Convertit les compteurs SQL en objet de controle des quotas.

        Args:
            storage_usage (Mapping[str, object]): Compteurs retournes par le repository.

        Returns:
            PlatformImageStorageUsage: Compteurs normalises pour les controles.
        """

        return PlatformImageStorageUsage(
            pending_image_count=int(storage_usage.get("pending_image_count") or 0),
            pending_image_bytes=int(storage_usage.get("pending_image_bytes") or 0),
            total_image_bytes=int(storage_usage.get("total_image_bytes") or 0),
        )

    def validate_uploaded_bytes(
        self,
        uploaded_bytes: int,
        usage: PlatformImageStorageUsage,
    ) -> None:
        """Valide les quotas avec les octets deja recus pour l'upload courant.

        Args:
            uploaded_bytes (int): Nombre d'octets deja ecrits pour le fichier courant.
            usage (PlatformImageStorageUsage): Occupation disque avant upload.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            PlatformImageStorageLimitExceededError: Si l'upload depasse une limite de stockage.
        """

        pending_bytes_after_upload = usage.pending_image_bytes + uploaded_bytes
        if pending_bytes_after_upload > self.configuration.max_pending_bytes_per_user:
            raise self._limit_error("pending_user_bytes", usage, uploaded_bytes)
        if usage.total_image_bytes + uploaded_bytes > self.configuration.max_total_bytes:
            raise self._limit_error("total_bytes", usage, uploaded_bytes)

    def _validate_usage_thresholds(self, usage: PlatformImageStorageUsage) -> None:
        if usage.pending_image_count >= self.configuration.max_pending_images_per_user:
            raise self._limit_error("pending_user_count", usage, 0)
        if usage.pending_image_bytes >= self.configuration.max_pending_bytes_per_user:
            raise self._limit_error("pending_user_bytes", usage, 0)
        if usage.total_image_bytes >= self.configuration.max_total_bytes:
            raise self._limit_error("total_bytes", usage, 0)

    def _limit_error(
        self,
        reason: str,
        usage: PlatformImageStorageUsage,
        uploaded_bytes: int,
    ) -> PlatformImageStorageLimitExceededError:
        return PlatformImageStorageLimitExceededError(
            reason,
            {
                "pending_image_count": usage.pending_image_count,
                "pending_image_bytes": usage.pending_image_bytes,
                "total_image_bytes": usage.total_image_bytes,
                "uploaded_bytes": uploaded_bytes,
                "max_pending_images_per_user": self.configuration.max_pending_images_per_user,
                "max_pending_bytes_per_user": self.configuration.max_pending_bytes_per_user,
                "max_total_bytes": self.configuration.max_total_bytes,
            },
        )
