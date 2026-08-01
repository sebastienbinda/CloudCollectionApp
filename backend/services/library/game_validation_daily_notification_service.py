#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-01
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : notification quotidienne des jeux en attente de validation.

import logging
import os
from pathlib import Path
from typing import Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from services.database.database_configuration import DatabaseConfiguration
from services.database.game_validation_repository import SqlAlchemyGameValidationRepository
from services.email import EmailConfiguration, EmailSenderFactory, EmailTemplateRenderer

EngineFactory = Callable[[str], Engine]


class GameValidationDailyNotificationService:
    """Compte les jeux en attente et notifie l'administrateur si besoin."""

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        repository: SqlAlchemyGameValidationRepository | None = None,
        engine: Engine | None = None,
        engine_factory: EngineFactory = create_engine,
        email_sender=None,
        admin_notification_email: str | None = None,
        site_url: str | None = None,
        template_path: str | Path | None = None,
        template_renderer: EmailTemplateRenderer | None = None,
        logger: logging.Logger | None = None,
    ):
        """Initialise le service de notification quotidienne de validation.

        Args:
            configuration (DatabaseConfiguration): Configuration SQL du backend.
            repository (SqlAlchemyGameValidationRepository | None): Repository injectable.
            engine (Engine | None): Moteur SQLAlchemy injectable en test.
            engine_factory (EngineFactory): Fabrique de moteur SQLAlchemy.
            email_sender (object | None): Expediteur email injectable.
            admin_notification_email (str | None): Adresse administrateur destinataire.
            site_url (str | None): URL publique du site a placer dans le mail.
            template_path (str | Path | None): Chemin optionnel du template texte.
            template_renderer (EmailTemplateRenderer | None): Moteur de rendu injectable.
            logger (logging.Logger | None): Journal applicatif injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si aucune URL SQL n'est configuree.
        """

        configuration.validate()
        if engine is None and not configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour notifier les jeux a valider.")
        self.engine = engine or engine_factory(configuration.database_url)
        self.repository = repository or SqlAlchemyGameValidationRepository(
            configuration.schema_name,
        )
        self.email_sender = email_sender
        if admin_notification_email is None:
            admin_notification_email = os.getenv("ADMIN_NOTIFICATION_EMAIL", "")
        self.admin_notification_email = str(admin_notification_email or "").strip()
        self.site_url = self._normalize_site_url(site_url or self.default_site_url())
        self.template_path = Path(template_path) if template_path else self.default_template_path()
        self.template_renderer = template_renderer or EmailTemplateRenderer()
        self.logger = logger or logging.getLogger(__name__)

    @classmethod
    def from_environment(cls) -> "GameValidationDailyNotificationService":
        """Construit le service depuis les variables d'environnement.

        Args:
            Aucun.

        Returns:
            GameValidationDailyNotificationService: Service configure.
        """

        return cls(DatabaseConfiguration.from_environment())

    @classmethod
    def default_template_path(cls) -> Path:
        """Retourne le chemin du template email par defaut.

        Args:
            Aucun.

        Returns:
            Path: Chemin du template stocke dans `backend/resources`.
        """

        return (
            EmailTemplateRenderer.default_resources_directory()
            / "game_validation_daily_notification_template.txt"
        )

    @classmethod
    def default_site_url(cls) -> str:
        """Retourne l'URL publique du site configuree pour les liens email.

        Args:
            Aucun.

        Returns:
            str: URL publique frontend, ou backend local par defaut.
        """

        return os.getenv(
            "FRONTEND_PUBLIC_URL",
            os.getenv("BACKEND_PUBLIC_URL", "http://localhost:7777"),
        )

    def notify_if_waiting_games_exist(self) -> int:
        """Envoie un email administrateur si des jeux sont a valider.

        Args:
            Aucun.

        Returns:
            int: Nombre de jeux en attente lors de la verification.
        """

        waiting_validation_count = self._count_waiting_validation_games()
        if waiting_validation_count <= 0:
            return waiting_validation_count
        if not self.admin_notification_email:
            self.logger.warning(
                "ADMIN_NOTIFICATION_EMAIL absent: notification quotidienne jeux a valider ignoree."
            )
            return waiting_validation_count
        sender = self.email_sender or EmailSenderFactory.create(
            EmailConfiguration.from_environment()
        )
        sender.send_email(
            recipient_email=self.admin_notification_email,
            subject="Jeux en attente de validation",
            body=self._build_email_body(waiting_validation_count),
        )
        return waiting_validation_count

    def _count_waiting_validation_games(self) -> int:
        with self.engine.connect() as connection:
            return self.repository.count_waiting_validation_games(connection)

    def _build_email_body(self, waiting_validation_count: int) -> str:
        library_games_url = f"{self.site_url}/bibliotheque/jeux?status=WAITING_VALIDATION"
        return self.template_renderer.render(
            self.template_path,
            {
                "waiting_validation_count": waiting_validation_count,
                "site_url": self.site_url,
                "library_games_url": library_games_url,
            },
        )

    def _normalize_site_url(self, site_url: str) -> str:
        return str(site_url or "").strip().rstrip("/") or "http://localhost:7777"
