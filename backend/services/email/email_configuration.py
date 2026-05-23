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
# Description : configuration d'envoi email du backend.

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EmailConfiguration:
    """Decrit la configuration necessaire a l'envoi d'emails.

    Attributes:
        delivery_mode (str): Mode d'envoi, `console` ou `smtp`.
        sender_email (str): Adresse expediteur des emails applicatifs.
        smtp_host (Optional[str]): Hote SMTP en mode `smtp`.
        smtp_port (int): Port SMTP.
        smtp_username (Optional[str]): Identifiant SMTP optionnel.
        smtp_password (Optional[str]): Mot de passe SMTP optionnel.
        smtp_use_tls (bool): Active STARTTLS en mode SMTP.
    """

    delivery_mode: str
    sender_email: str
    smtp_host: Optional[str]
    smtp_port: int
    smtp_username: Optional[str]
    smtp_password: Optional[str]
    smtp_use_tls: bool

    DEFAULT_SENDER_EMAIL = "noreply@cloudcollectionapp.local"

    @classmethod
    def from_environment(cls) -> "EmailConfiguration":
        """Construit la configuration email depuis l'environnement.

        Args:
            Aucun.

        Returns:
            EmailConfiguration: Configuration email validee.

        Raises:
            ValueError: Si le mode d'envoi ou la configuration SMTP est invalide.
        """

        configuration = cls(
            delivery_mode=os.getenv("EMAIL_DELIVERY_MODE", "console").strip().lower(),
            sender_email=os.getenv("SMTP_FROM_EMAIL", cls.DEFAULT_SENDER_EMAIL).strip(),
            smtp_host=(os.getenv("SMTP_HOST") or "").strip() or None,
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_username=(os.getenv("SMTP_USERNAME") or "").strip() or None,
            smtp_password=os.getenv("SMTP_PASSWORD") or None,
            smtp_use_tls=os.getenv("SMTP_USE_TLS", "true").strip().lower() == "true",
        )
        configuration.validate()
        return configuration

    def validate(self) -> None:
        """Valide la coherence de la configuration email.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si une valeur de configuration est invalide.
        """

        if self.delivery_mode not in {"console", "smtp"}:
            raise ValueError("EMAIL_DELIVERY_MODE doit valoir 'console' ou 'smtp'.")
        if not self.sender_email:
            raise ValueError("SMTP_FROM_EMAIL est requis pour envoyer un email.")
        if self.delivery_mode == "smtp" and not self.smtp_host:
            raise ValueError("SMTP_HOST est requis lorsque EMAIL_DELIVERY_MODE vaut 'smtp'.")
        if self.smtp_port <= 0:
            raise ValueError("SMTP_PORT doit etre un entier positif.")
