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
    DuplicateUserPseudonymError,
    EmailVerificationToken,
    PasswordPolicyError,
    PasswordHashService,
    RegisteredUser,
    UserRegistrationService,
    UserProfile,
    UserStatus,
)


class FakeUserRepository:
    """Repository utilisateur factice pour les tests d'inscription."""

    def __init__(self, existing_emails=None, existing_pseudonyms=None, waiting_users_count=3):
        """Initialise le repository factice.

        Args:
            existing_emails (set[str] | None): Emails consideres comme deja existants.
            existing_pseudonyms (set[str] | None): Pseudonymes deja existants en minuscules.
            waiting_users_count (int): Nombre d'utilisateurs en attente retourne.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.existing_emails = existing_emails or set()
        self.existing_pseudonyms = existing_pseudonyms or set()
        self.created_email = None
        self.created_pseudonym = None
        self.created_password_hash = None
        self.created_verification_token = None
        self.created_profile = None
        self.waiting_users_count = waiting_users_count
        self.counted_status = None

    def email_exists(self, email):
        """Indique si l'email existe dans le jeu de test.

        Args:
            email (str): Email normalise a rechercher.

        Returns:
            bool: `True` si l'email est deja present.
        """

        return email in self.existing_emails

    def pseudonym_exists(self, pseudonym):
        """Indique si le pseudonyme existe sans tenir compte de la casse.

        Args:
            pseudonym (str): Pseudonyme a rechercher.

        Returns:
            bool: `True` si le pseudonyme est deja present.
        """

        return pseudonym.lower() in self.existing_pseudonyms

    def create_user(
        self, email, pseudonym, password_hash, creation_date, verification_token, profile, status
    ):
        """Memorise la creation utilisateur factice.

        Args:
            email (str): Email normalise.
            pseudonym (str): Pseudonyme public.
            password_hash (str): Empreinte du mot de passe.
            creation_date (datetime): Date de creation.
            verification_token (EmailVerificationToken): Token de validation email.
            profile (str): Profil initial de l'utilisateur.
            status (str): Statut initial de l'utilisateur.

        Returns:
            RegisteredUser: Utilisateur public factice.
        """

        self.created_email = email
        self.created_pseudonym = pseudonym
        self.created_password_hash = password_hash
        self.created_verification_token = verification_token
        self.created_profile = profile
        self.created_status = status
        return RegisteredUser(
            id=42,
            email=email,
            pseudonym=pseudonym,
            creation_date=creation_date,
            is_email_verified=False,
            profile=profile,
            status=status,
        )

    def count_users_by_status(self, status):
        """Retourne le nombre factice d'utilisateurs pour un statut.

        Args:
            status (str): Statut fonctionnel a compter.

        Returns:
            int: Nombre d'utilisateurs configure pour le test.
        """

        self.counted_status = status
        return self.waiting_users_count


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

        user = service.register_user(
            " USER@Example.COM ", " Player_One ", "VeryStrongPassword123!"
        )

        self.assertEqual(42, user.id)
        self.assertEqual("user@example.com", repository.created_email)
        self.assertEqual("Player_One", repository.created_pseudonym)
        self.assertEqual("Player_One", user.pseudonym)
        self.assertFalse(user.is_email_verified)
        self.assertEqual(UserProfile.USER.value, user.profile)
        self.assertEqual(UserStatus.WAITING_VALIDATION.value, user.status)
        self.assertEqual(UserProfile.USER.value, repository.created_profile)
        self.assertEqual(UserStatus.WAITING_VALIDATION.value, repository.created_status)
        self.assertNotEqual("VeryStrongPassword123!", repository.created_password_hash)
        self.assertTrue(repository.created_password_hash.startswith("scrypt:"))
        self.assertEqual("hashed-token", repository.created_verification_token.token_hash)
        self.assertEqual(
            {"email": "user@example.com", "raw_token": "raw-token"},
            email_verification_service.sent_email,
        )

    def test_register_user_sets_active_status_when_admin_validation_is_disabled(self):
        """Verifie le statut initial sans validation administrateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut cree.
        """

        repository = FakeUserRepository()
        service = UserRegistrationService(
            repository,
            FakeEmailVerificationService(),
            admin_account_validation_enabled=False,
        )

        user = service.register_user("user@example.com", "Player_One", "VeryStrongPassword123!")

        self.assertEqual(UserStatus.ACTIVE.value, user.status)
        self.assertEqual(UserStatus.ACTIVE.value, repository.created_status)

    def test_register_user_rejects_invalid_email(self):
        """Verifie le refus d'un email invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(ValueError):
            service.register_user("invalid-email", "Player_One", "VeryStrongPassword123!")

    def test_register_user_rejects_short_password(self):
        """Verifie le refus d'un mot de passe trop court.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(PasswordPolicyError):
            service.register_user("user@example.com", "Player_One", "short")

    def test_register_user_rejects_password_without_digit(self):
        """Verifie le refus d'un mot de passe sans chiffre.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(PasswordPolicyError):
            service.register_user("user@example.com", "Player_One", "Password!")

    def test_register_user_rejects_password_without_special_character(self):
        """Verifie le refus d'un mot de passe sans caractere special.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(PasswordPolicyError):
            service.register_user("user@example.com", "Player_One", "Password1")

    def test_register_user_rejects_password_without_lowercase(self):
        """Verifie le refus d'un mot de passe sans minuscule.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(PasswordPolicyError):
            service.register_user("user@example.com", "Player_One", "PASSWORD1!")

    def test_register_user_rejects_password_without_uppercase(self):
        """Verifie le refus d'un mot de passe sans majuscule.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        service = UserRegistrationService(FakeUserRepository(), FakeEmailVerificationService())

        with self.assertRaises(PasswordPolicyError):
            service.register_user("user@example.com", "Player_One", "password1!")

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
            service.register_user("user@example.com", "Player_One", "VeryStrongPassword123!")

    def test_register_user_rejects_duplicate_pseudonym_without_case_sensitivity(self):
        """Verifie le refus d'un pseudonyme deja utilise avec une autre casse.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur metier.
        """

        repository = FakeUserRepository(existing_pseudonyms={"player_one"})
        service = UserRegistrationService(repository, FakeEmailVerificationService())

        with self.assertRaises(DuplicateUserPseudonymError):
            service.register_user(
                "other@example.com", "Player_One", "VeryStrongPassword123!"
            )

    def test_pseudonym_availability_validates_format_and_case_insensitive_uniqueness(self):
        """Verifie le format et la disponibilite publique d'un pseudonyme.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident disponibilite et refus.
        """

        repository = FakeUserRepository(existing_pseudonyms={"reserved"})
        service = UserRegistrationService(repository, FakeEmailVerificationService())

        self.assertTrue(service.is_pseudonym_available(" Player_One "))
        self.assertFalse(service.is_pseudonym_available("Reserved"))
        with self.assertRaises(ValueError):
            service.is_pseudonym_available("ab")
        with self.assertRaises(ValueError):
            service.is_pseudonym_available("pseudo interdit")


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

    def test_verify_password_accepts_matching_password(self):
        """Verifie la validation d'un mot de passe avec son empreinte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la comparaison securisee.
        """

        service = PasswordHashService()
        password_hash = service.hash_password("VeryStrongPassword123!")

        self.assertTrue(service.verify_password(password_hash, "VeryStrongPassword123!"))
        self.assertFalse(service.verify_password(password_hash, "WrongPassword123!"))


if __name__ == "__main__":
    unittest.main()
