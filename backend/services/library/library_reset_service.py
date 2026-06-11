#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : orchestration metier du reset global de la Bibliotheque.

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from services.collection.imports import (
    CollectionFileDescriptionValidationError,
    CollectionFileDescriptionValidator,
)
from services.database.database_configuration import DatabaseConfiguration
from services.database.library_reset_repository import (
    LibraryResetImportableUser,
    SqlAlchemyLibraryResetRepository,
)
from services.database.user_collection_import_repository import (
    SqlAlchemyUserCollectionImportRepository,
)
from services.email import EmailConfiguration, EmailSenderFactory
from services.users import UserCollectionImportConfiguration
from services.users.stored_user_collection_import_service import StoredUserCollectionImportService
from services.collection.imports import CollectionFileReaderFactory

from .library_reset_job_coordinator import LibraryResetJob


class LibraryResetRepository(Protocol):
    """Decrit les operations de persistance du reset Bibliotheque."""

    def clean_library_tables(self) -> None:
        """Vide les tables globales reconstruites par l'import.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

    def list_importable_users(self) -> list[LibraryResetImportableUser]:
        """Liste les utilisateurs sources du reset.

        Args:
            Aucun.

        Returns:
            list[LibraryResetImportableUser]: Utilisateurs a traiter.
        """


class LibraryResetEmailSender(Protocol):
    """Decrit l'envoi du rapport final de reset."""

    def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        """Envoie le rapport de reset.

        Args:
            recipient_email (str): Destinataire administrateur.
            subject (str): Sujet du message.
            body (str): Corps texte.

        Returns:
            None: La methode ne retourne aucune valeur.
        """


@dataclass
class LibraryResetUserResult:
    """Represente le resultat de traitement d'un utilisateur.

    Attributes:
        user_id (int): Identifiant utilisateur.
        email (str): Adresse email utilisateur.
        message (str): Detail du resultat.
    """

    user_id: int
    email: str
    message: str


@dataclass
class LibraryResetContext:
    """Regroupe le contexte memoire d'un job de reset Bibliotheque.

    Attributes:
        job_id (int): Identifiant du job.
        successful_users (list[LibraryResetUserResult]): Utilisateurs importes.
        failed_users (list[LibraryResetUserResult]): Utilisateurs en erreur.
        global_error (str): Erreur globale eventuelle.
    """

    job_id: int
    successful_users: list[LibraryResetUserResult] = field(default_factory=list)
    failed_users: list[LibraryResetUserResult] = field(default_factory=list)
    global_error: str = ""

    def has_errors(self) -> bool:
        """Indique si le reset contient au moins une erreur.

        Args:
            Aucun.

        Returns:
            bool: `True` si une erreur globale ou utilisateur existe.
        """

        return bool(self.global_error or self.failed_users)


class LibraryResetService:
    """Reconstruit la Bibliotheque depuis les fichiers utilisateurs."""

    def __init__(
        self,
        reset_repository: LibraryResetRepository,
        import_service_factory,
        file_description_validator: CollectionFileDescriptionValidator | None = None,
        email_sender: LibraryResetEmailSender | None = None,
        admin_notification_email: str = "",
        logger=None,
    ):
        """Initialise le service de reset Bibliotheque.

        Args:
            reset_repository (LibraryResetRepository): Repository de reset.
            import_service_factory (Callable): Fabrique du service d'import utilisateur.
            file_description_validator (CollectionFileDescriptionValidator | None): Validateur.
            email_sender (LibraryResetEmailSender | None): Expediteur email optionnel.
            admin_notification_email (str): Destinataire du rapport final.
            logger (logging.Logger | None): Logger injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.reset_repository = reset_repository
        self.import_service_factory = import_service_factory
        self.file_description_validator = file_description_validator or CollectionFileDescriptionValidator()
        self.email_sender = email_sender
        self.admin_notification_email = str(admin_notification_email or "").strip()
        self.logger = logger or logging.getLogger(__name__)

    @classmethod
    def from_environment(cls) -> "LibraryResetService":
        """Construit le service depuis la configuration d'environnement.

        Args:
            Aucun.

        Returns:
            LibraryResetService: Service pret a executer un reset.
        """

        database_configuration = DatabaseConfiguration.from_environment()
        return cls(
            reset_repository=SqlAlchemyLibraryResetRepository(database_configuration),
            import_service_factory=lambda: StoredUserCollectionImportService(
                UserCollectionImportConfiguration.from_environment(),
                SqlAlchemyUserCollectionImportRepository(database_configuration),
                CollectionFileReaderFactory(),
            ),
            email_sender=EmailSenderFactory.create(EmailConfiguration.from_environment()),
            admin_notification_email=os.getenv("ADMIN_NOTIFICATION_EMAIL", ""),
        )

    def run_reset(self, job: LibraryResetJob) -> LibraryResetContext:
        """Execute le reset Bibliotheque pour un job.

        Args:
            job (LibraryResetJob): Job courant.

        Returns:
            LibraryResetContext: Contexte memoire du reset.
        """

        context = LibraryResetContext(job_id=job.job_id)
        try:
            self.reset_repository.clean_library_tables()
        except Exception as exc:
            context.global_error = f"Echec du nettoyage de la base: {exc}"
            self.logger.exception("Echec du nettoyage de la base pendant le reset Bibliotheque.")
            self._send_final_email(context)
            return context

        for user in self.reset_repository.list_importable_users():
            self._import_user_collection(user, context)
        self._send_final_email(context)
        return context

    def _import_user_collection(
        self,
        user: LibraryResetImportableUser,
        context: LibraryResetContext,
    ) -> None:
        """Importe le fichier d'un utilisateur dans le contexte courant.

        Args:
            user (LibraryResetImportableUser): Utilisateur source.
            context (LibraryResetContext): Contexte a enrichir.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        file_path = Path(user.collection_file_path)
        if not file_path.is_file():
            self._add_user_error(context, user, "Fichier de collection introuvable ou illisible.")
            return
        if not isinstance(user.collection_file_description, dict) or not user.collection_file_description:
            self._add_user_error(context, user, "Configuration d'import absente.")
            return
        try:
            file_description = self.file_description_validator.validate(
                user.collection_file_description
            )
            result = self.import_service_factory().import_stored_collection(
                user.id,
                str(file_path),
                file_description,
            )
            context.successful_users.append(
                LibraryResetUserResult(
                    user.id,
                    user.email,
                    f"{result.associated_games} jeux associes.",
                )
            )
        except CollectionFileDescriptionValidationError as exc:
            self._add_user_error(context, user, f"Configuration invalide: {', '.join(exc.details)}")
        except Exception as exc:
            self._add_user_error(context, user, f"Echec d'import: {exc}")

    def _add_user_error(
        self,
        context: LibraryResetContext,
        user: LibraryResetImportableUser,
        message: str,
    ) -> None:
        """Ajoute une erreur utilisateur au contexte et aux logs.

        Args:
            context (LibraryResetContext): Contexte a enrichir.
            user (LibraryResetImportableUser): Utilisateur concerne.
            message (str): Message d'erreur.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.logger.error(
            "Reset Bibliotheque: utilisateur id=%s email=%s ignore: %s",
            user.id,
            user.email,
            message,
        )
        context.failed_users.append(LibraryResetUserResult(user.id, user.email, message))

    def _send_final_email(self, context: LibraryResetContext) -> None:
        """Envoie le rapport final du reset a l'administrateur.

        Args:
            context (LibraryResetContext): Contexte final du job.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        if not self.email_sender or not self.admin_notification_email:
            return
        subject = (
            "Reset Bibliotheque termine avec erreurs"
            if context.has_errors()
            else "Reset Bibliotheque termine"
        )
        try:
            self.email_sender.send_email(
                self.admin_notification_email,
                subject,
                self._build_email_body(context),
            )
        except Exception:
            self.logger.exception("Impossible d'envoyer le rapport de reset Bibliotheque.")

    def _build_email_body(self, context: LibraryResetContext) -> str:
        """Construit le corps texte du rapport final.

        Args:
            context (LibraryResetContext): Contexte final du job.

        Returns:
            str: Corps email.
        """

        lines = [
            f"Reset Bibliotheque job #{context.job_id}",
            "",
            f"Succes utilisateurs : {len(context.successful_users)}",
            f"Erreurs utilisateurs : {len(context.failed_users)}",
        ]
        if context.global_error:
            lines.extend(["", f"Erreur globale : {context.global_error}"])
        if context.successful_users:
            lines.append("")
            lines.append("Succes :")
            lines.extend(self._format_user_results(context.successful_users))
        if context.failed_users:
            lines.append("")
            lines.append("Erreurs :")
            lines.extend(self._format_user_results(context.failed_users))
        return "\n".join(lines)

    def _format_user_results(self, results: list[LibraryResetUserResult]) -> list[str]:
        """Formate une liste de resultats utilisateur.

        Args:
            results (list[LibraryResetUserResult]): Resultats a formater.

        Returns:
            list[str]: Lignes du rapport.
        """

        return [
            f"- utilisateur {result.user_id} ({result.email}) : {result.message}"
            for result in results
        ]
