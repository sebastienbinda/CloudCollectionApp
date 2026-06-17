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
# Description : tests unitaires de la verification d'adresse email.

import unittest
from datetime import datetime

from services.auth import (
    EmailVerificationService,
    InvalidEmailVerificationTokenError,
    VerifiedUser,
)
from services.users import UserStatus


class FakeEmailVerificationRepository:
    """Repository factice pour la validation email."""

    def __init__(self):
        """Initialise le repository factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.verified_token_hash = None
        self.counted_status = None

    def verify_email_by_token_hash(self, token_hash, verified_at, activate_user=False):
        """Valide un token factice.

        Args:
            token_hash (str): Empreinte du token.
            verified_at (datetime): Date de validation.
            activate_user (bool): Active le compte pendant la validation email.

        Returns:
            VerifiedUser: Utilisateur valide factice.
        """

        self.verified_token_hash = token_hash
        status = UserStatus.ACTIVE.value if activate_user else UserStatus.WAITING_VALIDATION.value
        return VerifiedUser(
            id=12,
            email="user@example.com",
            email_verified_at=verified_at,
            status=status,
        )

    def count_users_by_status(self, status):
        """Retourne un nombre factice d'utilisateurs pour un statut.

        Args:
            status (str): Statut fonctionnel a compter.

        Returns:
            int: Nombre d'utilisateurs factice.
        """

        self.counted_status = status
        return 4


class FakeEmailSender:
    """Expediteur email factice."""

    def __init__(self):
        """Initialise l'expediteur factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.sent_email = None

    def send_email(self, recipient_email, subject, body):
        """Memorise l'email envoye.

        Args:
            recipient_email (str): Adresse destinataire.
            subject (str): Sujet du message.
            body (str): Corps texte du message.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.sent_email = {
            "recipient_email": recipient_email,
            "subject": subject,
            "body": body,
        }


class EmailVerificationServiceTest(unittest.TestCase):
    def test_create_token_returns_raw_token_and_hash(self):
        """Verifie la creation du token brut et de son empreinte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le token.
        """

        service = EmailVerificationService(
            FakeEmailVerificationRepository(),
            FakeEmailSender(),
            token_ttl_hours=24,
        )

        token = service.create_token()

        self.assertTrue(token.raw_token)
        self.assertEqual(64, len(token.token_hash))
        self.assertNotEqual(token.raw_token, token.token_hash)

    def test_send_verification_email_includes_backend_link(self):
        """Verifie que l'email contient le lien de validation backend.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contenu de l'email.
        """

        email_sender = FakeEmailSender()
        service = EmailVerificationService(
            FakeEmailVerificationRepository(),
            email_sender,
            backend_public_url="https://api.example.com",
        )

        service.send_verification_email("user@example.com", "raw-token")

        self.assertEqual("user@example.com", email_sender.sent_email["recipient_email"])
        self.assertEqual(
            EmailVerificationService.default_verification_template_path().read_text(
                encoding="utf-8"
            ).splitlines()[0],
            email_sender.sent_email["body"].splitlines()[0],
        )
        self.assertIn(
            "Merci de vous etre inscrit sur CloudCollectionApp.",
            email_sender.sent_email["body"],
        )
        self.assertIn(
            "organiser votre collection de jeux video",
            email_sender.sent_email["body"],
        )
        self.assertIn(
            "votre compte restera en attente jusqu'a son activation par un administrateur",
            email_sender.sent_email["body"],
        )
        self.assertIn(
            "https://api.example.com/api/auth/verify-email?token=raw-token",
            email_sender.sent_email["body"],
        )

    def test_verify_email_hashes_token_before_repository_lookup(self):
        """Verifie que seul le hash du token est transmis au repository.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'empreinte transmise.
        """

        repository = FakeEmailVerificationRepository()
        service = EmailVerificationService(repository, FakeEmailSender())

        user = service.verify_email("raw-token")

        self.assertEqual(12, user.id)
        self.assertEqual(UserStatus.WAITING_VALIDATION.value, user.status)
        self.assertEqual(
            EmailVerificationService.hash_token("raw-token"),
            repository.verified_token_hash,
        )

    def test_verify_email_notifies_admin_after_email_validation(self):
        """Verifie la notification administrateur apres validation email.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le mail administrateur.
        """

        repository = FakeEmailVerificationRepository()
        admin_sender = FakeEmailSender()
        service = EmailVerificationService(
            repository,
            FakeEmailSender(),
            frontend_public_url="https://cloud.example.com",
            admin_notification_sender=admin_sender,
            admin_notification_email="admin@example.com",
        )

        service.verify_email("raw-token")

        self.assertEqual("admin@example.com", admin_sender.sent_email["recipient_email"])
        self.assertEqual("Adresse email utilisateur validee", admin_sender.sent_email["subject"])
        self.assertIn("user@example.com", admin_sender.sent_email["body"])
        self.assertEqual(UserStatus.WAITING_VALIDATION.value, repository.counted_status)
        self.assertIn("Nombre total d'utilisateurs en attente : 4", admin_sender.sent_email["body"])
        self.assertIn(
            "https://cloud.example.com/users?status=WAITING_VALIDATION",
            admin_sender.sent_email["body"],
        )

    def test_verify_email_notifies_admin_when_admin_validation_is_disabled(self):
        """Verifie que l'admin reste notifie sans validation administrateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le corps du mail.
        """

        repository = FakeEmailVerificationRepository()
        admin_sender = FakeEmailSender()
        service = EmailVerificationService(
            repository,
            FakeEmailSender(),
            admin_notification_sender=admin_sender,
            admin_notification_email="admin@example.com",
            admin_account_validation_enabled=False,
        )

        verified_user = service.verify_email("raw-token")

        self.assertIn("Validation administrateur active : non", admin_sender.sent_email["body"])
        self.assertEqual(UserStatus.ACTIVE.value, verified_user.status)

    def test_verify_email_rejects_empty_token(self):
        """Verifie le refus d'un token absent.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = EmailVerificationService(FakeEmailVerificationRepository(), FakeEmailSender())

        with self.assertRaises(InvalidEmailVerificationTokenError):
            service.verify_email("")


if __name__ == "__main__":
    unittest.main()
