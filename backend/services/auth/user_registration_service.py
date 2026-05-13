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
# Description : logique metier d'enregistrement des utilisateurs.

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Protocol

from .email_verification_service import EmailVerificationService, EmailVerificationToken
from .password_hash_service import PasswordHashService


@dataclass(frozen=True)
class RegisteredUser:
    """Represente les donnees publiques d'un utilisateur cree.

    Attributes:
        id (int): Identifiant technique de l'utilisateur.
        email (str): Adresse email normalisee.
        creation_date (datetime): Date de creation du compte.
        is_email_verified (bool): Indique si l'adresse email a ete validee.
    """

    id: int
    email: str
    creation_date: datetime
    is_email_verified: bool

    def to_public_dict(self) -> dict[str, object]:
        """Convertit l'utilisateur en dictionnaire JSON public.

        Args:
            Aucun.

        Returns:
            dict[str, object]: Donnees publiques sans mot de passe ni empreinte.
        """

        return {
            "id": self.id,
            "email": self.email,
            "creation_date": self.creation_date.isoformat(),
            "is_email_verified": self.is_email_verified,
        }


class UserRepository(Protocol):
    """Decrit le contrat de persistance des utilisateurs.

    Les implementations doivent stocker uniquement l'empreinte du mot de passe,
    jamais le mot de passe brut.
    """

    def email_exists(self, email: str) -> bool:
        """Indique si un email est deja utilise.

        Args:
            email (str): Adresse email normalisee.

        Returns:
            bool: `True` si l'email existe deja en base.
        """

    def create_user(
        self,
        email: str,
        password_hash: str,
        creation_date: datetime,
        verification_token: EmailVerificationToken,
    ) -> RegisteredUser:
        """Persiste un nouvel utilisateur.

        Args:
            email (str): Adresse email normalisee.
            password_hash (str): Empreinte non reversible du mot de passe.
            creation_date (datetime): Date de creation du compte.
            verification_token (EmailVerificationToken): Token de validation email a stocker.

        Returns:
            RegisteredUser: Donnees publiques de l'utilisateur cree.

        Raises:
            DuplicateUserEmailError: Si l'email existe deja.
        """


class DuplicateUserEmailError(ValueError):
    """Signale qu'une adresse email est deja rattachee a un compte."""


class PasswordPolicyError(ValueError):
    """Signale qu'un mot de passe ne respecte pas les regles de securite."""


class UserRegistrationService:
    """Orchestre la validation et la creation d'un compte utilisateur."""

    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_POLICY_MESSAGE = (
        "Le mot de passe doit contenir au moins 8 caracteres, au moins un chiffre, "
        "un caractere special, une minuscule et une majuscule."
    )

    def __init__(
        self,
        user_repository: UserRepository,
        email_verification_service: EmailVerificationService,
        password_hash_service: PasswordHashService | None = None,
    ):
        """Initialise le service d'enregistrement.

        Args:
            user_repository (UserRepository): Port de persistance utilisateur.
            email_verification_service (EmailVerificationService): Service de validation email.
            password_hash_service (PasswordHashService | None): Service de hachage injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.user_repository = user_repository
        self.email_verification_service = email_verification_service
        self.password_hash_service = password_hash_service or PasswordHashService()

    def register_user(self, email: str, password: str) -> RegisteredUser:
        """Cree un utilisateur apres validation des donnees d'inscription.

        Args:
            email (str): Adresse email fournie par le client.
            password (str): Mot de passe brut fourni par le client.

        Returns:
            RegisteredUser: Donnees publiques du compte cree.

        Raises:
            ValueError: Si l'email ou le mot de passe est invalide.
            DuplicateUserEmailError: Si l'email est deja utilise.
        """

        normalized_email = self._normalize_email(email)
        self._validate_email(normalized_email)
        self._validate_password(password)

        if self.user_repository.email_exists(normalized_email):
            raise DuplicateUserEmailError("Un compte existe deja pour cet email.")

        password_hash = self.password_hash_service.hash_password(password)
        creation_date = datetime.now(timezone.utc).replace(tzinfo=None)
        verification_token = self.email_verification_service.create_token()
        registered_user = self.user_repository.create_user(
            email=normalized_email,
            password_hash=password_hash,
            creation_date=creation_date,
            verification_token=verification_token,
        )
        self.email_verification_service.send_verification_email(
            email=registered_user.email,
            raw_token=verification_token.raw_token,
        )
        return registered_user

    def _normalize_email(self, email: str) -> str:
        """Normalise une adresse email pour eviter les doublons triviaux.

        Args:
            email (str): Adresse email brute.

        Returns:
            str: Adresse email nettoyee et en minuscules.
        """

        return str(email or "").strip().lower()

    def _validate_email(self, email: str) -> None:
        """Valide le format de l'adresse email.

        Args:
            email (str): Adresse email normalisee.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si l'adresse email est invalide.
        """

        if not email:
            raise ValueError("L'email est obligatoire.")
        if len(email) > 256:
            raise ValueError("L'email ne doit pas depasser 256 caracteres.")
        if not self.EMAIL_PATTERN.match(email):
            raise ValueError("L'email est invalide.")

    def _validate_password(self, password: str) -> None:
        """Valide la politique minimale de mot de passe.

        Args:
            password (str): Mot de passe brut.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si le mot de passe ne respecte pas la politique.
        """

        if not password:
            raise PasswordPolicyError(self.PASSWORD_POLICY_MESSAGE)
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise PasswordPolicyError(self.PASSWORD_POLICY_MESSAGE)
        if not re.search(r"\d", password):
            raise PasswordPolicyError(self.PASSWORD_POLICY_MESSAGE)
        if not re.search(r"[A-Z]", password):
            raise PasswordPolicyError(self.PASSWORD_POLICY_MESSAGE)
        if not re.search(r"[a-z]", password):
            raise PasswordPolicyError(self.PASSWORD_POLICY_MESSAGE)
        if not re.search(r"[^A-Za-z0-9]", password):
            raise PasswordPolicyError(self.PASSWORD_POLICY_MESSAGE)
