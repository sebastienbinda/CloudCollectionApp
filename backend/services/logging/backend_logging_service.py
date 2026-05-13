#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-13
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : configuration centralisee des journaux backend.

import logging
import os
from logging.config import dictConfig
from pathlib import Path

from .daily_size_rotating_file_handler import DailySizeRotatingFileHandler


class BackendLoggingService:
    """Configure les journaux applicatifs du backend Flask.

    La configuration ecrit les evenements sur la sortie standard pour rester
    compatible avec Docker et les plateformes d'hebergement.
    """

    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_LOG_DIR = "/app/logs"
    DEFAULT_LOG_FILE_NAME = "backend.log"
    DEFAULT_LOG_FILE_MAX_BYTES = 10 * 1024 * 1024
    DEFAULT_LOG_FILE_BACKUP_COUNT = 30
    ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    @classmethod
    def configure_from_environment(cls) -> None:
        """Configure le systeme de log depuis les variables d'environnement.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si une variable de configuration des logs est invalide.
        """

        log_level = os.getenv("BACKEND_LOG_LEVEL", cls.DEFAULT_LOG_LEVEL).upper()
        if log_level not in cls.ALLOWED_LOG_LEVELS:
            raise ValueError("BACKEND_LOG_LEVEL doit etre un niveau de log Python valide.")

        dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "standard": {
                        "format": (
                            "%(asctime)s %(levelname)s "
                            "[%(name)s] %(message)s"
                        )
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "standard",
                    }
                },
                "root": {
                    "level": log_level,
                    "handlers": ["console"],
                },
            }
        )
        if cls._is_file_logging_enabled():
            cls._add_file_handler(log_level)
        logging.getLogger(__name__).debug("Configuration des journaux backend chargee.")

    @classmethod
    def _add_file_handler(cls, log_level: str) -> None:
        """Ajoute un handler de log fichier au logger racine.

        Args:
            log_level (str): Niveau de log applique au handler.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si les limites de rotation sont invalides.
            OSError: Si le repertoire de logs ne peut pas etre cree.
        """

        log_dir = Path(os.getenv("BACKEND_LOG_DIR", cls.DEFAULT_LOG_DIR))
        log_file_name = os.getenv("BACKEND_LOG_FILE_NAME", cls.DEFAULT_LOG_FILE_NAME)
        max_bytes = cls._read_positive_int(
            "BACKEND_LOG_FILE_MAX_BYTES",
            cls.DEFAULT_LOG_FILE_MAX_BYTES,
        )
        backup_count = cls._read_positive_int(
            "BACKEND_LOG_FILE_BACKUP_COUNT",
            cls.DEFAULT_LOG_FILE_BACKUP_COUNT,
        )
        handler = DailySizeRotatingFileHandler(
            filename=str(log_dir / log_file_name),
            max_bytes=max_bytes,
            backup_count=backup_count,
        )
        handler.setLevel(log_level)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )
        logging.getLogger().addHandler(handler)

    @classmethod
    def _is_file_logging_enabled(cls) -> bool:
        """Indique si l'ecriture des logs sur disque est activee.

        Args:
            Aucun.

        Returns:
            bool: `True` si `BACKEND_LOG_FILE_ENABLED` vaut `true`.
        """

        return os.getenv("BACKEND_LOG_FILE_ENABLED", "false").strip().lower() == "true"

    @classmethod
    def _read_positive_int(cls, env_name: str, default_value: int) -> int:
        """Lit un entier positif depuis l'environnement.

        Args:
            env_name (str): Nom de la variable d'environnement.
            default_value (int): Valeur par defaut.

        Returns:
            int: Entier strictement positif.

        Raises:
            ValueError: Si la valeur n'est pas un entier strictement positif.
        """

        raw_value = os.getenv(env_name, str(default_value))
        try:
            parsed_value = int(raw_value)
        except ValueError as exc:
            raise ValueError(f"{env_name} doit etre un entier positif.") from exc
        if parsed_value <= 0:
            raise ValueError(f"{env_name} doit etre un entier positif.")
        return parsed_value
