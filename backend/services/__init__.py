#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
"""Exports publics des services backend."""

from .auth import (
    AuthGuard,
    AuthTokenService,
    DuplicateUserEmailError,
    EmailVerificationService,
    InvalidEmailVerificationTokenError,
    PasswordPolicyError,
    UserRegistrationService,
    UserProfile,
)
from .database import DatabaseConfiguration, DatabaseSchemaService, SqlAlchemyUserRepository
from .email import EmailConfiguration, EmailSenderFactory
from .library.library_query_contract import (
    LibraryPageRequest,
    LibraryQueryCriteria,
    LibraryQueryParser,
    LibrarySortRule,
)
from .library.library_reset_job_coordinator import (
    LibraryResetAlreadyRunningError,
    LibraryResetJob,
    LibraryResetJobCoordinator,
)
from .library.library_service import (
    LibraryService,
)
from .library.library_service_provider import LibraryServiceProvider
from .logging import BackendLoggingService
from .routing import RouteDiscoveryService
from .users import (
    UserCollectionImportConfiguration,
    UserCollectionNameNormalizer,
    UserManagementService,
    UserNotFoundError,
    UserSearchCriteria,
    UserStatus,
    UserSummary,
)

__all__ = [
    "AuthGuard",
    "AuthTokenService",
    "BackendLoggingService",
    "DatabaseConfiguration",
    "DatabaseSchemaService",
    "DuplicateUserEmailError",
    "EmailConfiguration",
    "EmailSenderFactory",
    "EmailVerificationService",
    "InvalidEmailVerificationTokenError",
    "LibraryPageRequest",
    "LibraryQueryCriteria",
    "LibraryQueryParser",
    "LibraryResetAlreadyRunningError",
    "LibraryResetJob",
    "LibraryResetJobCoordinator",
    "LibraryService",
    "LibraryServiceProvider",
    "LibrarySortRule",
    "PasswordPolicyError",
    "RouteDiscoveryService",
    "SqlAlchemyUserRepository",
    "UserRegistrationService",
    "UserProfile",
    "UserCollectionImportConfiguration",
    "UserCollectionNameNormalizer",
    "UserManagementService",
    "UserNotFoundError",
    "UserSearchCriteria",
    "UserStatus",
    "UserSummary",
]
