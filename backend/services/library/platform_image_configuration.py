#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-18
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : configuration de stockage des images de plateformes.

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PlatformImageConfiguration:
    """Decrit la configuration applicative des images de plateformes.

    Attributes:
        image_directory_path (str): Chemin conteneur du repertoire d'images.
        max_upload_bytes (int): Taille maximale acceptee pour une image uploadee.
    """

    image_directory_path: str
    max_upload_bytes: int

    DEFAULT_IMAGE_DIRECTORY_PATH = "/images"
    DEFAULT_MAX_UPLOAD_BYTES = 10485760

    @classmethod
    def from_environment(cls) -> "PlatformImageConfiguration":
        """Construit la configuration des images depuis l'environnement.

        Args:
            Aucun.

        Returns:
            PlatformImageConfiguration: Configuration validee.

        Raises:
            ValueError: Si le chemin cible ou la taille maximale est invalide.
        """

        configuration = cls(
            image_directory_path=os.getenv(
                "BACKEND_IMG_DIR",
                cls.DEFAULT_IMAGE_DIRECTORY_PATH,
            ).strip(),
            max_upload_bytes=cls._read_positive_int(
                "PLATFORM_IMAGE_MAX_UPLOAD_BYTES",
                cls.DEFAULT_MAX_UPLOAD_BYTES,
            ),
        )
        configuration.validate()
        return configuration

    def validate(self) -> None:
        """Valide la coherence de la configuration d'images.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si le chemin cible ou la taille maximale est invalide.
        """

        if not self.image_directory_path.strip():
            raise ValueError("BACKEND_IMG_DIR est requis pour stocker les images.")
        if self.max_upload_bytes <= 0:
            raise ValueError("PLATFORM_IMAGE_MAX_UPLOAD_BYTES doit etre un entier positif.")

    def ensure_image_directory(self) -> Path:
        """Cree le repertoire de stockage des images si necessaire.

        Args:
            Aucun.

        Returns:
            Path: Chemin du repertoire de stockage cree ou deja existant.

        Raises:
            OSError: Si le repertoire cible ne peut pas etre cree.
        """

        image_directory = Path(self.image_directory_path)
        image_directory.mkdir(parents=True, exist_ok=True)
        return image_directory

    @classmethod
    def _read_positive_int(cls, env_name: str, default_value: int) -> int:
        """Lit un entier positif depuis une variable d'environnement.

        Args:
            env_name (str): Nom de la variable d'environnement.
            default_value (int): Valeur utilisee quand la variable est absente.

        Returns:
            int: Valeur entiere strictement positive.

        Raises:
            ValueError: Si la valeur configuree n'est pas un entier positif.
        """

        raw_value = os.getenv(env_name, str(default_value))
        try:
            parsed_value = int(raw_value)
        except ValueError as exc:
            raise ValueError(f"{env_name} doit etre un entier positif.") from exc
        if parsed_value <= 0:
            raise ValueError(f"{env_name} doit etre un entier positif.")
        return parsed_value
