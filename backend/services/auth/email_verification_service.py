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
# Description : generation, envoi et validation des tokens de verification email.

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import os
import secrets
from typing import Protocol
from urllib.parse import urlencode

from services.email import EmailSender, EmailTemplateRenderer
from services.users import UserStatus


@dataclass(frozen=True)
class EmailVerificationToken:
    """Represente un token de verification email cree pour un utilisateur.

    Attributes:
        raw_token (str): Token brut a transmettre uniquement par email.
        token_hash (str): Empreinte SHA-256 stockable en base.
        expires_at (datetime): Date d'expiration du token.
    """

    raw_token: str
    token_hash: str
    expires_at: datetime


@dataclass(frozen=True)
class VerifiedUser:
    """Represente un utilisateur dont l'email vient d'etre valide.

    Attributes:
        id (int): Identifiant technique de l'utilisateur.
        email (str): Adresse email validee.
        email_verified_at (datetime): Date de validation de l'email.
        status (str): Statut fonctionnel du compte apres validation email.
    """

    id: int
    email: str
    email_verified_at: datetime
    status: str = UserStatus.WAITING_VALIDATION.value

    def to_public_dict(self) -> dict[str, object]:
        """Convertit l'utilisateur valide en dictionnaire JSON public.

        Args:
            Aucun.

        Returns:
            dict[str, object]: Donnees publiques de validation.
        """

        return {
            "id": self.id,
            "email": self.email,
            "email_verified_at": self.email_verified_at.isoformat(),
            "status": self.status,
        }

    @property
    def admin_validation_required(self) -> bool:
        """Indique si le compte attend encore une validation administrateur.

        Args:
            Aucun.

        Returns:
            bool: `True` si le statut reste `WAITING_VALIDATION`.
        """

        return self.status == UserStatus.WAITING_VALIDATION.value


class EmailVerificationRepository(Protocol):
    """Decrit les operations de persistance pour la verification email."""

    def verify_email_by_token_hash(
        self,
        token_hash: str,
        verified_at: datetime,
        activate_user: bool = False,
    ) -> VerifiedUser:
        """Valide un email a partir d'une empreinte de token.

        Args:
            token_hash (str): Empreinte SHA-256 du token recu.
            verified_at (datetime): Date de validation.
            activate_user (bool): Active le compte pendant la validation email.

        Returns:
            VerifiedUser: Utilisateur valide.

        Raises:
            InvalidEmailVerificationTokenError: Si le token est inconnu ou expire.
        """

    def count_users_by_status(self, status: str) -> int:
        """Compte les utilisateurs ayant un statut donne.

        Args:
            status (str): Statut fonctionnel a compter.

        Returns:
            int: Nombre d'utilisateurs correspondant au statut.
        """


class EmailVerificationAdminNotificationSender(Protocol):
    """Decrit l'envoi d'une notification administrateur apres validation email."""

    def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        """Envoie un email texte.

        Args:
            recipient_email (str): Adresse destinataire.
            subject (str): Sujet du message.
            body (str): Corps texte du message.

        Returns:
            None: La methode ne retourne aucune valeur.
        """


class InvalidEmailVerificationTokenError(ValueError):
    """Signale qu'un token de verification email est invalide ou expire."""


class EmailVerificationService:
    """Gere le cycle de vie des validations d'adresse email."""

    DEFAULT_TOKEN_TTL_HOURS = 24

    def __init__(
        self,
        repository: EmailVerificationRepository,
        email_sender: EmailSender,
        backend_public_url: str | None = None,
        frontend_public_url: str | None = None,
        token_ttl_hours: int | None = None,
        admin_notification_sender: EmailVerificationAdminNotificationSender | None = None,
        admin_notification_email: str = "",
        admin_account_validation_enabled: bool = True,
        template_renderer: EmailTemplateRenderer | None = None,
    ):
        """Initialise le service de verification email.

        Args:
            repository (EmailVerificationRepository): Persistance des validations email.
            email_sender (EmailSender): Service d'envoi du mail de validation.
            backend_public_url (str | None): URL publique du backend pour construire le lien.
            frontend_public_url (str | None): URL publique frontend pour le lien admin.
            token_ttl_hours (int | None): Duree de validite du token en heures.
            admin_notification_sender (EmailVerificationAdminNotificationSender | None):
                Expediteur de notification administrateur.
            admin_notification_email (str): Adresse administrateur destinataire.
            admin_account_validation_enabled (bool): Active la validation administrateur.
            template_renderer (EmailTemplateRenderer | None): Moteur de rendu injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.repository = repository
        self.email_sender = email_sender
        self.backend_public_url = (
            backend_public_url
            or os.getenv("BACKEND_PUBLIC_URL", "http://localhost:7777")
        ).rstrip("/")
        self.frontend_public_url = (
            frontend_public_url
            or os.getenv("FRONTEND_PUBLIC_URL", self.backend_public_url)
        ).rstrip("/")
        self.token_ttl_hours = token_ttl_hours or int(
            os.getenv("EMAIL_VERIFICATION_TOKEN_TTL_HOURS", str(self.DEFAULT_TOKEN_TTL_HOURS))
        )
        self.admin_notification_sender = admin_notification_sender
        self.admin_notification_email = str(admin_notification_email or "").strip()
        self.admin_account_validation_enabled = bool(admin_account_validation_enabled)
        self.template_renderer = template_renderer or EmailTemplateRenderer()

    def create_token(self) -> EmailVerificationToken:
        """Cree un token brut et son empreinte stockable.

        Args:
            Aucun.

        Returns:
            EmailVerificationToken: Token brut, empreinte et date d'expiration.
        """

        raw_token = secrets.token_urlsafe(48)
        return EmailVerificationToken(
            raw_token=raw_token,
            token_hash=self.hash_token(raw_token),
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None)
            + timedelta(hours=self.token_ttl_hours),
        )

    def send_verification_email(self, email: str, raw_token: str) -> None:
        """Envoie le lien de validation a l'utilisateur.

        Args:
            email (str): Adresse email destinataire.
            raw_token (str): Token brut a placer dans le lien.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            smtplib.SMTPException: Si le serveur SMTP refuse l'envoi.
            OSError: Si la connexion au serveur SMTP echoue.
        """

        verification_link = self.build_verification_link(raw_token)
        self.email_sender.send_email(
            recipient_email=email,
            subject="Validation de votre compte CloudCollectionApp",
            body=self.template_renderer.render(
                self.default_verification_template_path(),
                {
                    "verification_link": verification_link,
                    "validation_detail": self._verification_detail(),
                },
            ),
        )

    def verify_email(self, raw_token: str) -> VerifiedUser:
        """Valide une adresse email a partir du token recu.

        Args:
            raw_token (str): Token brut transmis par le lien de validation.

        Returns:
            VerifiedUser: Utilisateur dont l'email est valide.

        Raises:
            InvalidEmailVerificationTokenError: Si le token est absent, inconnu ou expire.
        """

        if not raw_token:
            raise InvalidEmailVerificationTokenError("Le token de validation est obligatoire.")
        verified_user = self.repository.verify_email_by_token_hash(
            token_hash=self.hash_token(raw_token),
            verified_at=datetime.now(timezone.utc).replace(tzinfo=None),
            activate_user=not self.admin_account_validation_enabled,
        )
        self._send_admin_notification(verified_user)
        return verified_user

    def build_verification_link(self, raw_token: str) -> str:
        """Construit le lien HTTP de validation email.

        Args:
            raw_token (str): Token brut a encoder dans l'URL.

        Returns:
            str: URL publique de validation.
        """

        query_string = urlencode({"token": raw_token})
        return f"{self.backend_public_url}/api/auth/verify-email?{query_string}"

    def _verification_detail(self) -> str:
        if self.admin_account_validation_enabled:
            return (
                "Cette validation est obligatoire avant que votre inscription puisse "
                "etre examinee par un administrateur. Apres validation de votre adresse "
                "email, votre compte restera en attente jusqu'a son activation par un "
                "administrateur."
            )
        return (
            "Apres validation de votre adresse email, votre compte sera actif et vous "
            "pourrez vous connecter."
        )

    def _send_admin_notification(self, verified_user: VerifiedUser) -> None:
        if not self.admin_notification_sender or not self.admin_notification_email:
            return
        waiting_status = UserStatus.WAITING_VALIDATION.value
        validation_link = f"{self.frontend_public_url}/users?status={waiting_status}"
        waiting_users_count = self.repository.count_users_by_status(waiting_status)
        self.admin_notification_sender.send_email(
            recipient_email=self.admin_notification_email,
            subject="Adresse email utilisateur validee",
            body=self.template_renderer.render(
                self.default_admin_notification_template_path(),
                {
                    "user_email": verified_user.email,
                    "user_id": verified_user.id,
                    "admin_validation_enabled": (
                        "oui" if self.admin_account_validation_enabled else "non"
                    ),
                    "user_status": verified_user.status,
                    "waiting_users_count": waiting_users_count,
                    "validation_link": validation_link,
                },
            ),
        )

    @classmethod
    def default_verification_template_path(cls):
        """Retourne le template du mail de verification utilisateur.

        Args:
            Aucun.

        Returns:
            Path: Chemin du template de verification email.
        """

        return EmailTemplateRenderer.default_resources_directory() / "user_email_verification_template.txt"

    @classmethod
    def default_admin_notification_template_path(cls):
        """Retourne le template du mail administrateur apres validation email.

        Args:
            Aucun.

        Returns:
            Path: Chemin du template de notification administrateur.
        """

        return EmailTemplateRenderer.default_resources_directory() / "admin_user_email_validated_template.txt"

    @staticmethod
    def hash_token(raw_token: str) -> str:
        """Calcule l'empreinte SHA-256 d'un token de validation.

        Args:
            raw_token (str): Token brut.

        Returns:
            str: Empreinte hexadecimale du token.
        """

        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
