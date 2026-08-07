#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-08-07
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : notification administrateur des echecs d'import.

import os
from html import escape
from pathlib import Path

from services.email import EmailConfiguration, EmailSenderFactory, EmailTemplateRenderer

from .collection_import_failure_context import CollectionImportFailureContext


class CollectionImportFailureAdminNotifier:
    """Envoie un email administrateur quand un import echoue."""

    MAX_TRACEBACK_LENGTH = 12000

    def __init__(
        self,
        email_sender=None,
        admin_notification_email: str | None = None,
        template_path: str | Path | None = None,
        template_renderer: EmailTemplateRenderer | None = None,
    ):
        """Initialise le notifier d'echec d'import.

        Args:
            email_sender (object | None): Expediteur email injectable.
            admin_notification_email (str | None): Adresse administrateur destinataire.
            template_path (str | Path | None): Chemin optionnel du template HTML.
            template_renderer (EmailTemplateRenderer | None): Moteur de rendu injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            Aucun.
        """

        self.email_sender = email_sender
        if admin_notification_email is None:
            admin_notification_email = os.getenv("ADMIN_NOTIFICATION_EMAIL", "")
        self.admin_notification_email = str(admin_notification_email or "").strip()
        self.template_path = Path(template_path) if template_path else self.default_template_path()
        self.template_renderer = template_renderer or EmailTemplateRenderer()

    @classmethod
    def from_environment(cls) -> "CollectionImportFailureAdminNotifier":
        """Construit le notifier depuis l'environnement.

        Args:
            Aucun.

        Returns:
            CollectionImportFailureAdminNotifier: Notifier configure.

        Raises:
            Aucun.
        """

        return cls(admin_notification_email=os.getenv("ADMIN_NOTIFICATION_EMAIL", ""))

    @classmethod
    def default_template_path(cls) -> Path:
        """Retourne le chemin du template email par defaut.

        Args:
            Aucun.

        Returns:
            Path: Chemin du template stocke dans `backend/resources`.

        Raises:
            Aucun.
        """

        return (
            EmailTemplateRenderer.default_resources_directory()
            / "collection_import_failure_email_template.txt"
        )

    def notify_import_failure(self, context: CollectionImportFailureContext) -> None:
        """Envoie le rapport d'echec d'import a l'administrateur.

        Args:
            context (CollectionImportFailureContext): Contexte complet de l'erreur.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            smtplib.SMTPException: Si le serveur SMTP refuse l'envoi.
            OSError: Si la connexion au serveur SMTP echoue.
        """

        if not self.admin_notification_email:
            return
        email_sender = self.email_sender or EmailSenderFactory.create(
            EmailConfiguration.from_environment()
        )
        email_sender.send_email(
            recipient_email=self.admin_notification_email,
            subject=f"Echec d'import - {context.import_kind}",
            body=self._build_email_body(context),
            content_subtype="html",
        )

    def is_enabled(self) -> bool:
        """Indique si une notification d'echec peut etre envoyee.

        Args:
            Aucun.

        Returns:
            bool: `True` lorsqu'une adresse administrateur est configuree.

        Raises:
            Aucun.
        """

        return bool(self.admin_notification_email)

    def _build_email_body(self, context: CollectionImportFailureContext) -> str:
        requester_id = (
            str(context.requester_user_id) if context.requester_user_id is not None else "inconnu"
        )
        traceback_text = str(context.traceback_text or "")
        if len(traceback_text) > self.MAX_TRACEBACK_LENGTH:
            traceback_text = traceback_text[-self.MAX_TRACEBACK_LENGTH:]
        return self.template_renderer.render(
            self.template_path,
            {
                "import_kind": escape(context.import_kind),
                "initiated_by_function": escape(context.initiated_by_function),
                "failing_function": escape(context.failing_function),
                "requester_user_id": escape(requester_id),
                "requester_email": escape(context.requester_email or "inconnu"),
                "file_type": escape(context.file_type or "inconnu"),
                "original_filename": escape(context.original_filename or "inconnu"),
                "error_type": escape(context.error_type),
                "error_message": escape(context.error_message),
                "traceback_text": escape(traceback_text),
            },
        )
