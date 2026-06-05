#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-05
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du service d'authentification par token Bearer.

import unittest

from services.auth import (
    AuthenticatedUserCredentials,
    AuthTokenService,
    PasswordHashService,
    UserProfile,
    UserStatus,
)


class FakeUserRepository:
    """Repository utilisateur factice pour les tests d'authentification."""

    def __init__(self, password_hash, status=UserStatus.ACTIVE.value):
        """Initialise les identifiants utilisateur factices.

        Args:
            password_hash (str): Empreinte du mot de passe attendu.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.password_hash = password_hash
        self.status = status
        self.last_connexion_user_id = None

    def find_verified_user_credentials_by_email(self, email):
        """Retourne un utilisateur verifie factice.

        Args:
            email (str): Email normalise recherche.

        Returns:
            AuthenticatedUserCredentials | None: Utilisateur trouve ou absent.
        """

        if email != "user@example.com":
            return None
        return AuthenticatedUserCredentials(
            id=7,
            email=email,
            password_hash=self.password_hash,
            profile=UserProfile.USER.value,
            status=self.status,
        )

    def update_last_connexion_date(self, user_id, last_connexion_date):
        """Memorise la derniere connexion factice.

        Args:
            user_id (int): Identifiant utilisateur.
            last_connexion_date (datetime): Date de connexion ignoree.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.last_connexion_user_id = user_id


class AuthTokenServiceTest(unittest.TestCase):
    def setUp(self):
        """Prepare un service d'authentification deterministe.

        Args:
            Aucun.

        Returns:
            None: Le service est stocke pour chaque test.
        """

        self.service = AuthTokenService(
            username="admin",
            password="secret",
            secret_key="unit-test-secret",
            token_ttl_seconds=3600,
        )

    def test_issue_token_returns_oauth2_payload(self):
        """Verifie le format de la reponse OAuth2.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le token genere.
        """

        token_response = self.service.issue_token("admin", "secret")

        self.assertEqual("Bearer", token_response["token_type"])
        self.assertEqual(3600, token_response["expires_in"])
        self.assertIn(".", token_response["access_token"])

    def test_validate_access_token_returns_payload(self):
        """Verifie qu'un token signe valide retourne son payload.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le sujet du token.
        """

        token = self.service.create_access_token("admin")

        payload = self.service.validate_access_token(token)

        self.assertEqual("admin", payload["sub"])
        self.assertEqual(UserProfile.USER.value, payload["profile"])

    def test_issue_token_adds_admin_profile_for_configured_user(self):
        """Verifie que l'utilisateur configure recoit le profil administrateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le profil du token.
        """

        token_response = self.service.issue_token("admin", "secret")

        payload = self.service.validate_access_token(token_response["access_token"])

        self.assertEqual("admin", payload["sub"])
        self.assertEqual(UserProfile.ADMIN.value, payload["profile"])

    def test_user_profile_hierarchy_allows_admin_on_user_routes(self):
        """Verifie la hierarchie de profils applicatifs.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les droits herites.
        """

        user_route_profiles = UserProfile.expand_hierarchy(UserProfile.USER.value)
        admin_route_profiles = UserProfile.expand_hierarchy(UserProfile.ADMIN.value)

        self.assertTrue(UserProfile.can_access(UserProfile.ADMIN.value, user_route_profiles))
        self.assertTrue(UserProfile.can_access(UserProfile.USER.value, user_route_profiles))
        self.assertFalse(UserProfile.can_access(UserProfile.USER.value, admin_route_profiles))

    def test_issue_token_rejects_invalid_credentials(self):
        """Verifie le refus d'identifiants invalides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur levee.
        """

        with self.assertRaises(ValueError):
            self.service.issue_token("admin", "bad-password")

    def test_issue_token_accepts_verified_database_user(self):
        """Verifie l'emission de token pour un utilisateur verifie en base.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le token et la trace de connexion.
        """

        password_hash = PasswordHashService().hash_password("VeryStrongPassword123!")
        repository = FakeUserRepository(password_hash)

        token_response = self.service.issue_token(
            " USER@Example.COM ",
            "VeryStrongPassword123!",
            repository,
        )
        payload = self.service.validate_access_token(token_response["access_token"])

        self.assertEqual("user@example.com", payload["sub"])
        self.assertEqual(UserProfile.USER.value, payload["profile"])
        self.assertEqual(7, repository.last_connexion_user_id)

    def test_issue_token_rejects_unverified_or_unknown_database_user(self):
        """Verifie le refus si aucun compte verifie ne correspond.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur levee.
        """

        password_hash = PasswordHashService().hash_password("VeryStrongPassword123!")
        repository = FakeUserRepository(password_hash)

        with self.assertRaises(ValueError):
            self.service.issue_token("unknown@example.com", "VeryStrongPassword123!", repository)

    def test_issue_token_rejects_locked_database_user(self):
        """Verifie le refus d'un utilisateur bloque.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur et l'absence de trace connexion.
        """

        password_hash = PasswordHashService().hash_password("VeryStrongPassword123!")
        repository = FakeUserRepository(password_hash, status=UserStatus.LOCKED.value)

        with self.assertRaises(ValueError):
            self.service.issue_token("user@example.com", "VeryStrongPassword123!", repository)

        self.assertIsNone(repository.last_connexion_user_id)

    def test_issue_token_rejects_waiting_validation_database_user_with_clear_message(self):
        """Verifie le refus explicite d'un utilisateur en attente de validation.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur et l'absence de connexion.
        """

        password_hash = PasswordHashService().hash_password("VeryStrongPassword123!")
        repository = FakeUserRepository(password_hash, status=UserStatus.WAITING_VALIDATION.value)

        with self.assertRaises(ValueError) as context:
            self.service.issue_token("user@example.com", "VeryStrongPassword123!", repository)

        self.assertEqual(AuthTokenService.WAITING_VALIDATION_MESSAGE, str(context.exception))
        self.assertIsNone(repository.last_connexion_user_id)

    def test_validate_access_token_rejects_invalid_signature(self):
        """Verifie le refus d'un token modifie.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de signature.
        """

        token = self.service.create_access_token("admin")
        payload_segment, _ = token.split(".", 1)

        with self.assertRaises(ValueError):
            self.service.validate_access_token(f"{payload_segment}.bad-signature")

    def test_validate_access_token_rejects_expired_token(self):
        """Verifie le refus d'un token expire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur d'expiration.
        """

        expired_service = AuthTokenService(
            username="admin",
            password="secret",
            secret_key="unit-test-secret",
            token_ttl_seconds=-1,
        )
        token = expired_service.create_access_token("admin")

        with self.assertRaises(ValueError):
            expired_service.validate_access_token(token)


if __name__ == "__main__":
    unittest.main()
