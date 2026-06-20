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
from time import perf_counter

from flask import Flask, Response, g, request

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
    HTTP_LOGGER_NAME = "backend.http"
    MAX_ERROR_MESSAGE_LENGTH = 500

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
    def register_http_request_logging(cls, flask_app: Flask) -> None:
        """Enregistre la journalisation de toutes les requetes HTTP Flask.

        Args:
            flask_app (Flask): Application dont les appels REST doivent etre traces.

        Returns:
            None: Enregistre les traitements avant et apres requete.

        Raises:
            RuntimeError: Si Flask refuse l'enregistrement apres la premiere requete.
        """

        http_logger = logging.getLogger(cls.HTTP_LOGGER_NAME)

        @flask_app.before_request
        def record_http_request_start_time() -> None:
            """Memorise l'instant de reception de la requete courante.

            Args:
                Aucun.

            Returns:
                None: Stocke l'instant dans le contexte Flask.
            """

            g.http_request_started_at = perf_counter()

        @flask_app.after_request
        def log_http_response(response: Response) -> Response:
            """Trace la reponse HTTP avec un niveau adapte au statut.

            Args:
                response (Response): Reponse Flask produite par l'application.

            Returns:
                Response: Reponse originale sans modification.
            """

            started_at = getattr(g, "http_request_started_at", perf_counter())
            duration_ms = round(max(0.0, perf_counter() - started_at) * 1000, 3)
            log_level = logging.ERROR if response.status_code >= 400 else logging.INFO
            http_logger.log(
                log_level,
                "REST method=%s path=%s endpoint=%s status=%s duration_ms=%s remote_addr=%s%s",
                request.method,
                request.path,
                request.endpoint or "unmatched",
                response.status_code,
                duration_ms,
                request.remote_addr or "unknown",
                cls._format_http_error(response),
            )
            return response

        @flask_app.teardown_request
        def log_unhandled_http_exception(exception: BaseException | None) -> None:
            """Trace une exception HTTP non convertie en reponse Flask.

            Args:
                exception (BaseException | None): Exception levee pendant la requete.

            Returns:
                None: Ecrit uniquement dans le journal.
            """

            if exception is not None:
                http_logger.error(
                    "REST exception method=%s path=%s endpoint=%s",
                    request.method,
                    request.path,
                    request.endpoint or "unmatched",
                    exc_info=(type(exception), exception, exception.__traceback__),
                )

    @classmethod
    def _format_http_error(cls, response: Response) -> str:
        """Extrait un message JSON borne pour une reponse HTTP en erreur.

        Args:
            response (Response): Reponse Flask a inspecter.

        Returns:
            str: Suffixe de log vide ou contenant le message fonctionnel.
        """

        if response.status_code < 400 or not response.is_json:
            return ""
        payload = response.get_json(silent=True)
        if not isinstance(payload, dict) or not payload.get("error"):
            return ""
        error_message = str(payload["error"]).replace("\n", " ").replace("\r", " ")
        return f" error={error_message[:cls.MAX_ERROR_MESSAGE_LENGTH]!r}"

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
