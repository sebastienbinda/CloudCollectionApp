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
# Description : notification administrateur des images de plateformes proposees.

import logging
import os

from services.email import EmailConfiguration, EmailSenderFactory


class PlatformImageAdminNotifier:
    """Notifie l'administrateur apres une proposition d'image de plateforme."""

    def __init__(
        self,
        email_sender=None,
        admin_notification_email: str | None = None,
        logger: logging.Logger | None = None,
    ):
        """Initialise le notifier d'images de plateformes.

        Args:
            email_sender (object | None): Expediteur email injectable.
            admin_notification_email (str | None): Adresse administrateur.
            logger (logging.Logger | None): Journal applicatif injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.email_sender = email_sender
        if admin_notification_email is None:
            admin_notification_email = os.getenv("ADMIN_NOTIFICATION_EMAIL", "")
        self.admin_notification_email = str(admin_notification_email or "").strip()
        self.logger = logger or logging.getLogger(__name__)

    @classmethod
    def from_environment(cls) -> "PlatformImageAdminNotifier":
        """Construit le notifier depuis l'environnement.

        Args:
            Aucun.

        Returns:
            PlatformImageAdminNotifier: Notifier configure.

        Raises:
            ValueError: Si la configuration email est invalide.
        """

        return cls(admin_notification_email=os.getenv("ADMIN_NOTIFICATION_EMAIL", ""))

    def notify_image_created(self, platform_name: str, image_id: int, user_email: str) -> None:
        """Envoie une notification apres creation d'image.

        Args:
            platform_name (str): Nom de la plateforme concernee.
            image_id (int): Identifiant de l'image creee.
            user_email (str): Email de l'utilisateur proposant l'image.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        if not self.admin_notification_email:
            self.logger.warning(
                "ADMIN_NOTIFICATION_EMAIL absent: notification image plateforme ignoree."
            )
            return
        sender = self.email_sender or EmailSenderFactory.create(
            EmailConfiguration.from_environment()
        )
        sender.send_email(
            recipient_email=self.admin_notification_email,
            subject="Nouvelle image de plateforme a valider",
            body=(
                "Une nouvelle image de plateforme est en attente de validation.\n\n"
                f"Plateforme: {platform_name}\n"
                f"Image: {image_id}\n"
                f"Utilisateur: {user_email}\n"
            ),
        )

    def notify_upload_disabled(
        self,
        user_email: str,
        reason: str,
        metrics: dict[str, int],
    ) -> None:
        """Envoie une notification quand les quotas disque bloquent l'upload.

        Args:
            user_email (str): Email de l'utilisateur ayant tente l'upload.
            reason (str): Limite ayant provoque le blocage.
            metrics (dict[str, int]): Valeurs de quotas et d'usage.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        if not self.admin_notification_email:
            self.logger.warning(
                "ADMIN_NOTIFICATION_EMAIL absent: alerte quota image plateforme ignoree."
            )
            return
        sender = self.email_sender or EmailSenderFactory.create(
            EmailConfiguration.from_environment()
        )
        metric_lines = "\n".join(
            f"{metric_name}: {metric_value}"
            for metric_name, metric_value in sorted(metrics.items())
        )
        try:
            sender.send_email(
                recipient_email=self.admin_notification_email,
                subject="Uploads d'images de plateformes temporairement bloques",
                body=(
                    "Une limite de stockage des images de plateformes a ete atteinte.\n\n"
                    f"Utilisateur: {user_email}\n"
                    f"Limite: {reason}\n"
                    f"{metric_lines}\n"
                ),
            )
        except Exception:
            self.logger.exception("Impossible d'envoyer l'alerte quota image plateforme.")
