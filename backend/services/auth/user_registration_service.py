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
from .duplicate_user_pseudonym_error import DuplicateUserPseudonymError
from .password_hash_service import PasswordHashService
from .user_profile import UserProfile
from services.users import UserStatus


@dataclass(frozen=True)
class RegisteredUser:
    """Represente les donnees publiques d'un utilisateur cree.

    Attributes:
        id (int): Identifiant technique de l'utilisateur.
        email (str): Adresse email normalisee.
        pseudonym (str): Pseudonyme public unique de l'utilisateur.
        creation_date (datetime): Date de creation du compte.
        is_email_verified (bool): Indique si l'adresse email a ete validee.
        profile (str): Profil applicatif attribue au compte.
        status (str): Statut fonctionnel attribue au compte.
    """

    id: int
    email: str
    pseudonym: str
    creation_date: datetime
    is_email_verified: bool
    profile: str = UserProfile.USER.value
    status: str = UserStatus.WAITING_VALIDATION.value

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
            "pseudonym": self.pseudonym,
            "creation_date": self.creation_date.isoformat(),
            "is_email_verified": self.is_email_verified,
            "profile": self.profile,
            "status": self.status,
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

    def pseudonym_exists(self, pseudonym: str) -> bool:
        """Indique si un pseudonyme est deja utilise sans tenir compte de la casse.

        Args:
            pseudonym (str): Pseudonyme normalise a rechercher.

        Returns:
            bool: `True` si le pseudonyme existe deja en base.
        """

    def create_user(
        self,
        email: str,
        pseudonym: str,
        password_hash: str,
        creation_date: datetime,
        verification_token: EmailVerificationToken,
        profile: str,
        status: str,
    ) -> RegisteredUser:
        """Persiste un nouvel utilisateur.

        Args:
            email (str): Adresse email normalisee.
            pseudonym (str): Pseudonyme public valide.
            password_hash (str): Empreinte non reversible du mot de passe.
            creation_date (datetime): Date de creation du compte.
            verification_token (EmailVerificationToken): Token de validation email a stocker.
            profile (str): Profil applicatif initial du compte.
            status (str): Statut fonctionnel initial du compte.

        Returns:
            RegisteredUser: Donnees publiques de l'utilisateur cree.

        Raises:
            DuplicateUserEmailError: Si l'email existe deja.
            DuplicateUserPseudonymError: Si le pseudonyme existe deja.
        """


class DuplicateUserEmailError(ValueError):
    """Signale qu'une adresse email est deja rattachee a un compte."""


class PasswordPolicyError(ValueError):
    """Signale qu'un mot de passe ne respecte pas les regles de securite."""


class UserRegistrationService:
    """Orchestre la validation et la creation d'un compte utilisateur."""

    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    PSEUDONYM_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,32}$")
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_POLICY_MESSAGE = (
        "Le mot de passe doit contenir au moins 8 caracteres, au moins un chiffre, "
        "un caractere special, une minuscule et une majuscule."
    )

    def __init__(
        self,
        user_repository: UserRepository,
        email_verification_service: EmailVerificationService | None,
        password_hash_service: PasswordHashService | None = None,
        admin_account_validation_enabled: bool = True,
    ):
        """Initialise le service d'enregistrement.

        Args:
            user_repository (UserRepository): Port de persistance utilisateur.
            email_verification_service (EmailVerificationService | None): Service de validation email.
            password_hash_service (PasswordHashService | None): Service de hachage injectable.
            admin_account_validation_enabled (bool): Active la validation administrateur.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.user_repository = user_repository
        self.email_verification_service = email_verification_service
        self.password_hash_service = password_hash_service or PasswordHashService()
        self.admin_account_validation_enabled = bool(admin_account_validation_enabled)

    def register_user(self, email: str, pseudonym: str, password: str) -> RegisteredUser:
        """Cree un utilisateur apres validation des donnees d'inscription.

        Args:
            email (str): Adresse email fournie par le client.
            pseudonym (str): Pseudonyme public fourni par le client.
            password (str): Mot de passe brut fourni par le client.

        Returns:
            RegisteredUser: Donnees publiques du compte cree.

        Raises:
            ValueError: Si l'email ou le mot de passe est invalide.
            DuplicateUserEmailError: Si l'email est deja utilise.
            DuplicateUserPseudonymError: Si le pseudonyme est deja utilise.
        """

        normalized_email = self._normalize_email(email)
        normalized_pseudonym = self.normalize_pseudonym(pseudonym)
        self._validate_email(normalized_email)
        self.validate_pseudonym(normalized_pseudonym)
        self._validate_password(password)

        if self.user_repository.email_exists(normalized_email):
            raise DuplicateUserEmailError("Un compte existe deja pour cet email.")
        if self.user_repository.pseudonym_exists(normalized_pseudonym):
            raise DuplicateUserPseudonymError("Ce pseudonyme est deja utilise.")

        password_hash = self.password_hash_service.hash_password(password)
        if self.email_verification_service is None:
            raise ValueError("Le service de validation email est requis pour l'inscription.")
        creation_date = datetime.now(timezone.utc).replace(tzinfo=None)
        verification_token = self.email_verification_service.create_token()
        registered_user = self.user_repository.create_user(
            email=normalized_email,
            pseudonym=normalized_pseudonym,
            password_hash=password_hash,
            creation_date=creation_date,
            verification_token=verification_token,
            profile=UserProfile.USER.value,
            status=self._initial_user_status(),
        )
        self.email_verification_service.send_verification_email(
            email=registered_user.email,
            raw_token=verification_token.raw_token,
        )
        return registered_user

    def is_pseudonym_available(self, pseudonym: str) -> bool:
        """Verifie la validite et la disponibilite d'un pseudonyme.

        Args:
            pseudonym (str): Pseudonyme fourni par le client.

        Returns:
            bool: `True` si le pseudonyme valide est disponible.

        Raises:
            ValueError: Si le format du pseudonyme est invalide.
        """

        normalized_pseudonym = self.normalize_pseudonym(pseudonym)
        self.validate_pseudonym(normalized_pseudonym)
        return not self.user_repository.pseudonym_exists(normalized_pseudonym)

    @classmethod
    def normalize_pseudonym(cls, pseudonym: str) -> str:
        """Nettoie un pseudonyme sans modifier sa casse d'affichage.

        Args:
            pseudonym (str): Pseudonyme brut.

        Returns:
            str: Pseudonyme sans espaces exterieurs.
        """

        return str(pseudonym or "").strip()

    @classmethod
    def validate_pseudonym(cls, pseudonym: str) -> None:
        """Valide le format public d'un pseudonyme.

        Args:
            pseudonym (str): Pseudonyme nettoye.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si le pseudonyme ne respecte pas le format autorise.
        """

        if not cls.PSEUDONYM_PATTERN.fullmatch(pseudonym):
            raise ValueError(
                "Le pseudonyme doit contenir entre 3 et 32 caracteres parmi les lettres, "
                "les chiffres, le tiret et le tiret bas."
            )

    def _initial_user_status(self) -> str:
        """Retourne le statut initial selon la validation administrateur.

        Args:
            Aucun.

        Returns:
            str: Statut initial du compte cree.
        """

        if self.admin_account_validation_enabled:
            return UserStatus.WAITING_VALIDATION.value
        return UserStatus.ACTIVE.value

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
