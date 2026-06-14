#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : notification administrateur des matchings plateformes faibles.

import os

from services.email import EmailConfiguration, EmailSenderFactory


class PlatformMatchingAdminNotifier:
    """Notifie l'administrateur des plateformes rattachees avec score faible."""

    def __init__(self, email_sender=None, admin_notification_email: str | None = None):
        """Initialise la notification de matching plateformes.

        Args:
            email_sender (object | None): Expediteur email injectable.
            admin_notification_email (str): Adresse administrateur destinataire.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.email_sender = email_sender
        if admin_notification_email is None:
            admin_notification_email = os.getenv("ADMIN_NOTIFICATION_EMAIL", "")
        self.admin_notification_email = str(admin_notification_email or "").strip()

    @classmethod
    def from_environment(cls) -> "PlatformMatchingAdminNotifier":
        """Construit le notifier depuis l'environnement.

        Args:
            Aucun.

        Returns:
            PlatformMatchingAdminNotifier: Notifier configure.

        Raises:
            ValueError: Si la configuration email est invalide.
        """

        return cls(admin_notification_email=os.getenv("ADMIN_NOTIFICATION_EMAIL", ""))

    def notify_manual_matches(self, manual_matches: list[dict]) -> None:
        """Envoie un email si des matchings faibles doivent etre verifies.

        Args:
            manual_matches (list[dict]): Warnings de plateformes a verifier.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        if not manual_matches or not self.admin_notification_email:
            return
        lines = [
            "Des plateformes importees demandent une verification manuelle.",
            "",
        ]
        for match in manual_matches:
            lines.append(
                "- Jeu: {game_name} | Plateforme importee: {imported_platform} | "
                "Plateforme rattachee: {matched_platform} | Score: {score}".format(
                    **match
                )
            )
        email_sender = self.email_sender or EmailSenderFactory.create(
            EmailConfiguration.from_environment()
        )
        email_sender.send_email(
            recipient_email=self.admin_notification_email,
            subject="Verification manuelle de plateformes importees",
            body="\n".join(lines),
        )
