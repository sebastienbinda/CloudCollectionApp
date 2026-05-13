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
# Description : tests unitaires de l'enregistrement utilisateur.

import unittest
from datetime import datetime

from services.auth import (
    DuplicateUserEmailError,
    EmailVerificationToken,
    PasswordPolicyError,
    PasswordHashService,
    RegisteredUser,
    UserRegistrationService,
)


class FakeUserRepository:
    """Repository utilisateur factice pour les tests d'inscription."""

    def __init__(self, existing_emails=None):
        """Initialise le repository factice.

        Args:
            existing_emails (set[str] | None): Emails consideres comme deja existants.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.existing_emails = existing_emails or set()
        self.created_email = None
        self.created_password_hash = None
        self.created_verification_token = None

    def email_exists(self, email):
        """Indique si l'email existe dans le jeu de test.

        Args:
            email (str): Email normalise a rechercher.

        Returns:
            bool: `True` si l'email est deja present.
        """

        return email in self.existing_emails

    def create_user(self, email, password_hash, creation_date, verification_token):
        """Memorise la creation utilisateur factice.

        Args:
            email (str): Email normalise.
            password_hash (str): Empreinte du mot de passe.
            creation_date (datetime): Date de creation.
            verification_token (EmailVerificationToken): Token de validation email.

        Returns:
            RegisteredUser: Utilisateur public factice.
        """

        self.created_email = email
        self.created_password_hash = password_hash
        self.created_verification_token = verification_token
        return RegisteredUser(
            id=42,
            email=email,
            creation_date=creation_date,
            is_email_verified=False,
        )


class FakeEmailVerificationService:
    """Service de validation email factice."""

    def __init__(self):
        """Initialise le service factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.sent_email = None
        self.token = EmailVerificationToken(
            raw_token="raw-token",
            token_hash="hashed-token",
            expires_at=datetime(2026, 5, 14, 12, 0, 0),
        )

    def create_token(self):
        """Retourne un token factice.

        Args:
            Aucun.

        Returns:
            EmailVerificationToken: Token determine pour le test.
        """

        return self.token

    def send_verification_email(self, email, raw_token):
        """Memorise l'envoi email factice.

        Args:
            email (str): Adresse email destinataire.
            raw_token (str): Token brut envoye.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.sent_email = {"email": email, "raw_token": raw_token}


class UserRegistrationServiceTest(unittest.TestCase):
    def test_register_user_normalizes_email_and_hashes_password(self):
        """Verifie la normalisation email et le stockage d'une empreinte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement.
        """

        repository = FakeUserRepository()
        email_verification_service = FakeEmailVerificationService()
        service = UserRegistrationService(repository, email_verification_service)

        user = service.register_user(" USER@Example.COM ", "VeryStrongPassword123!")

        self.assertEqual(42, user.id)
        self.assertEqual("user@example.com", repository.created_email)
        self.assertFalse(user.is_email_verified)
        self.assertNotEqual("VeryStrongPassword123!", repository.created_password_hash)
        self.assertTrue(repository.created_password_hash.startswith("scrypt:"))
        self.assertEqual("hashed-token", repository.created_verification_token.token_hash)
        self.assertEqual(
            {"email": "user@example.com", "raw_token": "raw-token"},
            email_verification_service.sent_email,
        )

    def test_register_user_rejects_invalid_email(self):
        """Verifie le refus d'un email invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(ValueError):
            service.register_user("invalid-email", "VeryStrongPassword123!")

    def test_register_user_rejects_short_password(self):
        """Verifie le refus d'un mot de passe trop court.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(PasswordPolicyError):
            service.register_user("user@example.com", "short")

    def test_register_user_rejects_password_without_digit(self):
        """Verifie le refus d'un mot de passe sans chiffre.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(PasswordPolicyError):
            service.register_user("user@example.com", "Password!")

    def test_register_user_rejects_password_without_special_character(self):
        """Verifie le refus d'un mot de passe sans caractere special.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(PasswordPolicyError):
            service.register_user("user@example.com", "Password1")

    def test_register_user_rejects_password_without_lowercase(self):
        """Verifie le refus d'un mot de passe sans minuscule.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(PasswordPolicyError):
            service.register_user("user@example.com", "PASSWORD1!")

    def test_register_user_rejects_password_without_uppercase(self):
        """Verifie le refus d'un mot de passe sans majuscule.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(PasswordPolicyError):
            service.register_user("user@example.com", "password1!")

    def test_register_user_rejects_duplicate_email(self):
        """Verifie le refus d'un email deja utilise.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(
            FakeUserRepository({"user@example.com"}),
            FakeEmailVerificationService(),
        )

        with self.assertRaises(DuplicateUserEmailError):
            service.register_user("user@example.com", "VeryStrongPassword123!")


class PasswordHashServiceTest(unittest.TestCase):
    def test_hash_password_returns_non_reversible_hash(self):
        """Verifie que le service retourne une empreinte scrypt salee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le format de l'empreinte.
        """

        service = PasswordHashService()

        first_hash = service.hash_password("VeryStrongPassword123!")
        second_hash = service.hash_password("VeryStrongPassword123!")

        self.assertTrue(first_hash.startswith("scrypt:"))
        self.assertNotEqual("VeryStrongPassword123!", first_hash)
        self.assertNotEqual(first_hash, second_hash)


if __name__ == "__main__":
    unittest.main()
