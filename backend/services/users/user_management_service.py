#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-22
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : logique metier de recherche et d'administration des utilisateurs.

from dataclasses import dataclass
from datetime import datetime
import os
from typing import Protocol

from .user_status import UserStatus


@dataclass(frozen=True)
class UserSearchCriteria:
    """Regroupe les criteres de recherche d'utilisateurs.

    Attributes:
        name (str): Portion d'email ou de nom de connexion recherchee.
        creation_date_from (datetime | None): Date minimale de creation.
        creation_date_to (datetime | None): Date maximale de creation.
        last_connexion_date_from (datetime | None): Date minimale de derniere connexion.
        last_connexion_date_to (datetime | None): Date maximale de derniere connexion.
        status (str): Statut fonctionnel recherche, ou chaine vide.
    """

    name: str = ""
    creation_date_from: datetime | None = None
    creation_date_to: datetime | None = None
    last_connexion_date_from: datetime | None = None
    last_connexion_date_to: datetime | None = None
    status: str = ""


@dataclass(frozen=True)
class UserSummary:
    """Represente les donnees publiques d'administration d'un utilisateur.

    Attributes:
        id (int): Identifiant technique de l'utilisateur.
        email (str): Adresse email de connexion.
        profile (str): Profil applicatif associe au compte.
        status (str): Statut fonctionnel du compte.
        is_email_verified (bool): Indique si l'email est verifie.
        creation_date (datetime): Date de creation du compte.
        last_connexion_date (datetime | None): Date de derniere connexion.
    """

    id: int
    email: str
    profile: str
    status: str
    is_email_verified: bool
    creation_date: datetime
    last_connexion_date: datetime | None = None

    def to_dict(self) -> dict[str, object]:
        """Convertit l'utilisateur en dictionnaire JSON sans secret.

        Args:
            Aucun.

        Returns:
            dict[str, object]: Donnees utilisateur exposees au controleur.
        """

        return {
            "id": self.id,
            "email": self.email,
            "profile": self.profile,
            "status": self.status,
            "is_email_verified": self.is_email_verified,
            "creation_date": self.creation_date.isoformat(),
            "last_connexion_date": self.last_connexion_date.isoformat()
            if self.last_connexion_date
            else None,
        }


class UserAdministrationRepository(Protocol):
    """Decrit les operations de persistance pour l'administration utilisateur."""

    def search_users(self, criteria: UserSearchCriteria) -> list[UserSummary]:
        """Recherche les utilisateurs selon des criteres optionnels.

        Args:
            criteria (UserSearchCriteria): Criteres de filtrage.

        Returns:
            list[UserSummary]: Utilisateurs correspondant aux criteres.
        """

    def delete_user(self, user_id: int) -> bool:
        """Supprime un utilisateur.

        Args:
            user_id (int): Identifiant technique du compte.

        Returns:
            bool: `True` si un utilisateur a ete supprime.
        """

    def lock_user(self, user_id: int) -> UserSummary | None:
        """Bloque un utilisateur.

        Args:
            user_id (int): Identifiant technique du compte.

        Returns:
            UserSummary | None: Utilisateur bloque, ou `None` si absent.
        """

    def unlock_user(self, user_id: int) -> UserSummary | None:
        """Debloque un utilisateur.

        Args:
            user_id (int): Identifiant technique du compte.

        Returns:
            UserSummary | None: Utilisateur debloque, ou `None` si absent.
        """

    def validate_user(self, user_id: int) -> UserSummary | None:
        """Valide un utilisateur en attente.

        Args:
            user_id (int): Identifiant technique du compte.

        Returns:
            UserSummary | None: Utilisateur active, ou `None` si absent.
        """


class UserActivationEmailSender(Protocol):
    """Decrit l'envoi d'un email d'activation de compte."""

    def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        """Envoie un email texte.

        Args:
            recipient_email (str): Adresse destinataire.
            subject (str): Sujet du message.
            body (str): Corps texte du message.

        Returns:
            None: La methode ne retourne aucune valeur.
        """


class UserNotFoundError(ValueError):
    """Signale qu'aucun utilisateur ne correspond a l'identifiant demande."""


class UserManagementService:
    """Orchestre la recherche et les actions d'administration des utilisateurs."""

    def __init__(
        self,
        user_repository: UserAdministrationRepository,
        activation_email_sender: UserActivationEmailSender | None = None,
        frontend_public_url: str | None = None,
    ):
        """Initialise le service de gestion utilisateur.

        Args:
            user_repository (UserAdministrationRepository): Port de persistance utilisateur.
            activation_email_sender (UserActivationEmailSender | None): Expediteur email optionnel.
            frontend_public_url (str | None): URL publique frontend pour le lien de connexion.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.user_repository = user_repository
        self.activation_email_sender = activation_email_sender
        self.frontend_public_url = (
            frontend_public_url
            or os.getenv("FRONTEND_PUBLIC_URL")
            or os.getenv("BACKEND_PUBLIC_URL", "http://localhost:7777")
        ).rstrip("/")

    def search_users(self, criteria: UserSearchCriteria) -> list[UserSummary]:
        """Recherche les utilisateurs avec les criteres fournis.

        Args:
            criteria (UserSearchCriteria): Criteres de recherche.

        Returns:
            list[UserSummary]: Utilisateurs trouves.

        Raises:
            ValueError: Si le statut demande n'est pas reconnu.
        """

        if criteria.status:
            self._validate_status(criteria.status)
        return self.user_repository.search_users(criteria)

    def delete_user(self, user_id: int) -> None:
        """Supprime un utilisateur existant.

        Args:
            user_id (int): Identifiant technique du compte.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si l'identifiant est invalide.
            UserNotFoundError: Si aucun compte ne correspond.
        """

        normalized_user_id = self._validate_user_id(user_id)
        if not self.user_repository.delete_user(normalized_user_id):
            raise UserNotFoundError("Utilisateur introuvable.")

    def lock_user(self, user_id: int) -> UserSummary:
        """Bloque un utilisateur existant.

        Args:
            user_id (int): Identifiant technique du compte.

        Returns:
            UserSummary: Utilisateur apres passage au statut `LOCKED`.

        Raises:
            ValueError: Si l'identifiant est invalide.
            UserNotFoundError: Si aucun compte ne correspond.
        """

        normalized_user_id = self._validate_user_id(user_id)
        locked_user = self.user_repository.lock_user(normalized_user_id)
        if not locked_user:
            raise UserNotFoundError("Utilisateur introuvable.")
        return locked_user

    def unlock_user(self, user_id: int) -> UserSummary:
        """Debloque un utilisateur existant.

        Args:
            user_id (int): Identifiant technique du compte.

        Returns:
            UserSummary: Utilisateur apres passage au statut `ACTIVE`.

        Raises:
            ValueError: Si l'identifiant est invalide.
            UserNotFoundError: Si aucun compte ne correspond.
        """

        normalized_user_id = self._validate_user_id(user_id)
        unlocked_user = self.user_repository.unlock_user(normalized_user_id)
        if not unlocked_user:
            raise UserNotFoundError("Utilisateur introuvable.")
        return unlocked_user

    def validate_user(self, user_id: int) -> UserSummary:
        """Valide un utilisateur en attente et notifie le titulaire du compte.

        Args:
            user_id (int): Identifiant technique du compte.

        Returns:
            UserSummary: Utilisateur apres passage au statut `ACTIVE`.

        Raises:
            ValueError: Si l'identifiant est invalide.
            UserNotFoundError: Si aucun compte ne correspond.
        """

        normalized_user_id = self._validate_user_id(user_id)
        validated_user = self.user_repository.validate_user(normalized_user_id)
        if not validated_user:
            raise UserNotFoundError("Utilisateur introuvable.")
        self._send_activation_email(validated_user)
        return validated_user

    def _send_activation_email(self, user: UserSummary) -> None:
        """Envoie l'email d'activation si un expediteur est configure.

        Args:
            user (UserSummary): Utilisateur valide a notifier.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        if not self.activation_email_sender:
            return
        login_link = f"{self.frontend_public_url}/auth"
        self.activation_email_sender.send_email(
            recipient_email=user.email,
            subject="Votre compte CloudCollectionApp est active",
            body=(
                "Bonjour,\n\n"
                "Votre compte CloudCollectionApp a ete valide par un administrateur.\n\n"
                "Vous pouvez maintenant vous connecter avec votre adresse email depuis le lien "
                "suivant :\n"
                f"{login_link}\n\n"
                "Si vous n'etes pas a l'origine de cette demande, contactez l'administrateur."
            ),
        )

    def _validate_user_id(self, user_id: int) -> int:
        """Valide un identifiant utilisateur.

        Args:
            user_id (int): Identifiant brut recu par le controleur.

        Returns:
            int: Identifiant strictement positif.

        Raises:
            ValueError: Si l'identifiant est invalide.
        """

        try:
            normalized_user_id = int(user_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("L'identifiant utilisateur est invalide.") from exc
        if normalized_user_id <= 0:
            raise ValueError("L'identifiant utilisateur est invalide.")
        return normalized_user_id

    def _validate_status(self, status: str) -> None:
        """Valide un statut de recherche.

        Args:
            status (str): Statut brut demande.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si le statut n'est pas autorise.
        """

        normalized_status = str(status or "").strip().upper()
        if normalized_status not in {item.value for item in UserStatus}:
            raise ValueError("Le statut utilisateur est invalide.")
