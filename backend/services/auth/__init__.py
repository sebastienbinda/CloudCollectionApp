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
# Description : exports des utilitaires d'authentification backend.

from .auth_guard import AuthGuard
from .auth_token_service import (
    AuthenticatedTokenIdentity,
    AuthenticatedUserCredentials,
    AuthTokenService,
)
from .email_verification_service import (
    EmailVerificationService,
    EmailVerificationToken,
    InvalidEmailVerificationTokenError,
    VerifiedUser,
)
from .duplicate_user_pseudonym_error import DuplicateUserPseudonymError
from .password_hash_service import PasswordHashService
from .user_registration_service import (
    DuplicateUserEmailError,
    PasswordPolicyError,
    RegisteredUser,
    UserRegistrationService,
)
from .user_profile import UserProfile
from services.users import UserStatus

__all__ = [
    "AuthGuard",
    "AuthenticatedTokenIdentity",
    "AuthenticatedUserCredentials",
    "AuthTokenService",
    "DuplicateUserEmailError",
    "DuplicateUserPseudonymError",
    "EmailVerificationService",
    "EmailVerificationToken",
    "InvalidEmailVerificationTokenError",
    "PasswordPolicyError",
    "PasswordHashService",
    "RegisteredUser",
    "UserRegistrationService",
    "UserProfile",
    "UserStatus",
    "VerifiedUser",
]
