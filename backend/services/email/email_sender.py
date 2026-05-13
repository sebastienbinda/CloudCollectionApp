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
# Description : implementations d'envoi email applicatif.

import logging
import smtplib
from email.message import EmailMessage
from typing import Protocol

from .email_configuration import EmailConfiguration


class EmailSender(Protocol):
    """Decrit le contrat d'envoi d'un email applicatif."""

    def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        """Envoie un email texte.

        Args:
            recipient_email (str): Adresse destinataire.
            subject (str): Sujet du message.
            body (str): Corps texte du message.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            smtplib.SMTPException: Si le serveur SMTP refuse l'envoi.
            OSError: Si la connexion au serveur SMTP echoue.
        """


class ConsoleEmailSender:
    """Simule l'envoi d'email en journalisant le message en developpement."""

    def __init__(self, logger: logging.Logger | None = None):
        """Initialise l'expediteur console.

        Args:
            logger (logging.Logger | None): Journal applicatif injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.logger = logger or logging.getLogger(__name__)

    def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        """Journalise un email au lieu de l'envoyer.

        Args:
            recipient_email (str): Adresse destinataire.
            subject (str): Sujet du message.
            body (str): Corps texte du message.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.logger.info(
            "Email console pour %s | sujet=%s | corps=%s",
            recipient_email,
            subject,
            body,
        )


class SmtpEmailSender:
    """Envoie les emails via un serveur SMTP configure par environnement."""

    def __init__(self, configuration: EmailConfiguration):
        """Initialise l'expediteur SMTP.

        Args:
            configuration (EmailConfiguration): Configuration SMTP valide.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration

    def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        """Envoie un email texte via SMTP.

        Args:
            recipient_email (str): Adresse destinataire.
            subject (str): Sujet du message.
            body (str): Corps texte du message.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            smtplib.SMTPException: Si le serveur SMTP refuse l'envoi.
            OSError: Si la connexion au serveur SMTP echoue.
        """

        message = EmailMessage()
        message["From"] = self.configuration.sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.configuration.smtp_host, self.configuration.smtp_port) as smtp:
            if self.configuration.smtp_use_tls:
                smtp.starttls()
            if self.configuration.smtp_username and self.configuration.smtp_password:
                smtp.login(self.configuration.smtp_username, self.configuration.smtp_password)
            smtp.send_message(message)


class EmailSenderFactory:
    """Construit l'expediteur email adapte a la configuration."""

    @staticmethod
    def create(configuration: EmailConfiguration) -> EmailSender:
        """Cree un expediteur email.

        Args:
            configuration (EmailConfiguration): Configuration email valide.

        Returns:
            EmailSender: Expediteur console ou SMTP.
        """

        if configuration.delivery_mode == "smtp":
            return SmtpEmailSender(configuration)
        return ConsoleEmailSender()
