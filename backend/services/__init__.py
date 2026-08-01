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
    CollectionShareGuestAuthenticationService,
    CollectionShareUnavailableError,
    DuplicateUserEmailError,
    DuplicateUserPseudonymError,
    EmailVerificationService,
    InvalidEmailVerificationTokenError,
    PasswordPolicyError,
    UserRegistrationService,
    UserProfile,
)
from .database import (
    DatabaseConfiguration,
    DatabaseSchemaService,
    SqlAlchemyCollectionShareRepository,
    SqlAlchemyUserRepository,
)
from .email import EmailConfiguration, EmailSenderFactory
from .library.library_query_contract import (
    LibraryPageRequest,
    LibraryQueryCriteria,
    LibraryQueryParser,
    LibrarySortRule,
)
from .library.game_duplicate_service import (
    GameDuplicateError,
    GameDuplicateNotFoundError,
    GameDuplicatePermissionError,
    GameDuplicateService,
)
from .library.game_duplicate_daily_notification_scheduler import (
    GameDuplicateDailyNotificationScheduler,
)
from .library.game_validation_daily_notification_scheduler import (
    GameValidationDailyNotificationScheduler,
)
from .library.library_reset_job_coordinator import (
    LibraryResetAlreadyRunningError,
    LibraryResetJob,
    LibraryResetJobCoordinator,
)
from .library.platform_image_configuration import PlatformImageConfiguration
from .library.platform_image_service import PlatformImageService
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
    "CollectionShareGuestAuthenticationService",
    "CollectionShareUnavailableError",
    "BackendLoggingService",
    "DatabaseConfiguration",
    "DatabaseSchemaService",
    "DuplicateUserEmailError",
    "DuplicateUserPseudonymError",
    "EmailConfiguration",
    "EmailSenderFactory",
    "EmailVerificationService",
    "InvalidEmailVerificationTokenError",
    "LibraryPageRequest",
    "GameDuplicateError",
    "GameDuplicateNotFoundError",
    "GameDuplicatePermissionError",
    "GameDuplicateService",
    "GameDuplicateDailyNotificationScheduler",
    "GameValidationDailyNotificationScheduler",
    "LibraryQueryCriteria",
    "LibraryQueryParser",
    "LibraryResetAlreadyRunningError",
    "LibraryResetJob",
    "LibraryResetJobCoordinator",
    "LibraryService",
    "LibraryServiceProvider",
    "LibrarySortRule",
    "PlatformImageConfiguration",
    "PlatformImageService",
    "PasswordPolicyError",
    "RouteDiscoveryService",
    "SqlAlchemyCollectionShareRepository",
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
