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
# Description : configuration de l'import de collection utilisateur.

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class UserCollectionImportConfiguration:
    """Decrit la configuration applicative d'import de collection utilisateur.

    Attributes:
        workspace_path (str): Chemin conteneur du repertoire de collections utilisateur.
        max_upload_bytes (int): Taille maximale acceptee pour un fichier importe.
    """

    workspace_path: str
    max_upload_bytes: int

    DEFAULT_WORKSPACE_PATH = "/users/workspace"
    DEFAULT_MAX_UPLOAD_BYTES = 104857600

    @classmethod
    def from_environment(
        cls,
        workspace_path: str = DEFAULT_WORKSPACE_PATH,
    ) -> "UserCollectionImportConfiguration":
        """Construit la configuration d'import depuis l'environnement.

        Args:
            workspace_path (str): Chemin conteneur fixe utilise par le backend.

        Returns:
            UserCollectionImportConfiguration: Configuration d'import validee.

        Raises:
            ValueError: Si la taille maximale d'upload est invalide.
        """

        configuration = cls(
            workspace_path=workspace_path,
            max_upload_bytes=cls._read_positive_int(
                "USER_COLLECTION_MAX_UPLOAD_BYTES",
                cls.DEFAULT_MAX_UPLOAD_BYTES,
            ),
        )
        configuration.validate()
        return configuration

    def validate(self) -> None:
        """Valide la coherence de la configuration d'import.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si le chemin cible ou la taille maximale est invalide.
        """

        if not self.workspace_path.strip():
            raise ValueError("Le chemin du workspace utilisateur est requis.")
        if self.max_upload_bytes <= 0:
            raise ValueError("USER_COLLECTION_MAX_UPLOAD_BYTES doit etre un entier positif.")

    def ensure_workspace_directory(self) -> Path:
        """Cree le repertoire de stockage des collections si necessaire.

        Args:
            Aucun.

        Returns:
            Path: Chemin du repertoire de stockage cree ou deja existant.

        Raises:
            OSError: Si le repertoire cible ne peut pas etre cree.
        """

        workspace_directory = Path(self.workspace_path)
        workspace_directory.mkdir(parents=True, exist_ok=True)
        return workspace_directory

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
