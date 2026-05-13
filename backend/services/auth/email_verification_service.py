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

from services.email import EmailSender


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
    """

    id: int
    email: str
    email_verified_at: datetime

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
        }


class EmailVerificationRepository(Protocol):
    """Decrit les operations de persistance pour la verification email."""

    def verify_email_by_token_hash(
        self,
        token_hash: str,
        verified_at: datetime,
    ) -> VerifiedUser:
        """Valide un email a partir d'une empreinte de token.

        Args:
            token_hash (str): Empreinte SHA-256 du token recu.
            verified_at (datetime): Date de validation.

        Returns:
            VerifiedUser: Utilisateur valide.

        Raises:
            InvalidEmailVerificationTokenError: Si le token est inconnu ou expire.
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
        token_ttl_hours: int | None = None,
    ):
        """Initialise le service de verification email.

        Args:
            repository (EmailVerificationRepository): Persistance des validations email.
            email_sender (EmailSender): Service d'envoi du mail de validation.
            backend_public_url (str | None): URL publique du backend pour construire le lien.
            token_ttl_hours (int | None): Duree de validite du token en heures.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.repository = repository
        self.email_sender = email_sender
        self.backend_public_url = (
            backend_public_url
            or os.getenv("BACKEND_PUBLIC_URL", "http://localhost:7777")
        ).rstrip("/")
        self.token_ttl_hours = token_ttl_hours or int(
            os.getenv("EMAIL_VERIFICATION_TOKEN_TTL_HOURS", str(self.DEFAULT_TOKEN_TTL_HOURS))
        )

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
            body=(
                "Bonjour,\n\n"
                "Veuillez valider votre adresse email avec le lien suivant :\n"
                f"{verification_link}\n\n"
                "Si vous n'etes pas a l'origine de cette demande, ignorez cet email."
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
        return self.repository.verify_email_by_token_hash(
            token_hash=self.hash_token(raw_token),
            verified_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

    def build_verification_link(self, raw_token: str) -> str:
        """Construit le lien HTTP de validation email.

        Args:
            raw_token (str): Token brut a encoder dans l'URL.

        Returns:
            str: URL publique de validation.
        """

        query_string = urlencode({"token": raw_token})
        return f"{self.backend_public_url}/api/auth/verify-email?{query_string}"

    @staticmethod
    def hash_token(raw_token: str) -> str:
        """Calcule l'empreinte SHA-256 d'un token de validation.

        Args:
            raw_token (str): Token brut.

        Returns:
            str: Empreinte hexadecimale du token.
        """

        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
