#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-24
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : fixtures partagees par les tests de routes Flask.

from datetime import datetime
import unittest

import app as app_module
from services.auth import (
    AuthenticatedUserCredentials,
    DuplicateUserEmailError,
    InvalidEmailVerificationTokenError,
    PasswordHashService,
    PasswordPolicyError,
    RegisteredUser,
    UserProfile,
    UserStatus,
)
from services.auth.email_verification_service import EmailVerificationService, VerifiedUser
from services.database.user_collection_import_repository import (
    UserCollectionImportPersistenceResult,
)
from services.users import UserSummary
from services.users.user_collection_import_service import UserCollectionImportResult

try:
    from tests.route_test_fakes import (
        FakeLibraryService,
        FakeUserCollectionQueryService,
    )
except ModuleNotFoundError:
    from route_test_fakes import (
        FakeLibraryService,
        FakeUserCollectionQueryService,
    )


class FakeSqlAlchemyUserRepository:
    """Repository utilisateur factice pour les tests HTTP."""

    user_password_hash = PasswordHashService().hash_password("VeryStrongPassword123!")

    def __init__(self, configuration):
        """Initialise le repository factice.

        Args:
            configuration (object): Configuration ignoree.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration

    def find_verified_user_credentials_by_email(self, email):
        """Retourne les identifiants d'un utilisateur verifie.

        Args:
            email (str): Email recherche.

        Returns:
            AuthenticatedUserCredentials | None: Utilisateur factice ou absence.
        """

        if email != "user@example.com":
            return None
        return AuthenticatedUserCredentials(
            id=7,
            email=email,
            password_hash=self.user_password_hash,
            profile=UserProfile.USER.value,
            status=UserStatus.ACTIVE.value,
        )

    def update_last_connexion_date(self, user_id, last_connexion_date):
        """Ignore la date de connexion.

        Args:
            user_id (int): Identifiant utilisateur.
            last_connexion_date (datetime): Date ignoree.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

    def find_user_id_by_email(self, email):
        """Retourne l'identifiant de l'utilisateur factice.

        Args:
            email (str): Email recherche.

        Returns:
            int | None: Identifiant utilisateur ou absence.
        """

        return 7 if email == "user@example.com" else None

    def search_users(self, criteria):
        """Retourne des utilisateurs factices filtres.

        Args:
            criteria (UserSearchCriteria): Criteres de recherche.

        Returns:
            list[UserSummary]: Utilisateurs correspondant aux criteres.
        """

        users = [
            UserSummary(7, "user@example.com", "USER", "ACTIVE", True, datetime(2026, 5, 13, 12), datetime(2026, 5, 22, 8, 30)),
            UserSummary(8, "locked@example.com", "USER", "LOCKED", True, datetime(2026, 5, 20, 12), None),
        ]
        if criteria.name:
            users = [user for user in users if criteria.name.lower() in user.email.lower()]
        if criteria.creation_date_from:
            users = [user for user in users if user.creation_date >= criteria.creation_date_from]
        if criteria.creation_date_to:
            users = [user for user in users if user.creation_date <= criteria.creation_date_to]
        if criteria.last_connexion_date_to:
            users = [user for user in users if user.last_connexion_date and user.last_connexion_date <= criteria.last_connexion_date_to]
        if criteria.status:
            users = [user for user in users if user.status == criteria.status]
        return users

    def delete_user(self, user_id):
        """Supprime l'utilisateur 7.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            bool: `True` si l'utilisateur existe.
        """

        return user_id == 7

    def lock_user(self, user_id):
        """Bloque l'utilisateur 7.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            UserSummary | None: Utilisateur bloque ou absence.
        """

        if user_id != 7:
            return None
        return UserSummary(7, "user@example.com", "USER", "LOCKED", True, datetime(2026, 5, 13, 12), datetime(2026, 5, 22, 8, 30))

    def unlock_user(self, user_id):
        """Debloque l'utilisateur 7.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            UserSummary | None: Utilisateur actif ou absence.
        """

        if user_id != 7:
            return None
        return UserSummary(7, "user@example.com", "USER", "ACTIVE", True, datetime(2026, 5, 13, 12), datetime(2026, 5, 22, 8, 30))

    def verify_email_by_token_hash(self, token_hash, verified_at):
        """Valide un token email factice.

        Args:
            token_hash (str): Empreinte du token.
            verified_at (datetime): Date de validation.

        Returns:
            VerifiedUser: Utilisateur valide.

        Raises:
            InvalidEmailVerificationTokenError: Si le token est invalide.
        """

        if token_hash == EmailVerificationService.hash_token("invalid-token"):
            raise InvalidEmailVerificationTokenError("Le token de validation est invalide ou expire.")
        return VerifiedUser(id=7, email="user@example.com", email_verified_at=verified_at)


class FakeDatabaseConfiguration:
    """Configuration de base factice."""

    def is_database_enabled(self):
        """Indique que la base est disponible.

        Args:
            Aucun.

        Returns:
            bool: Toujours `True`.
        """

        return True

    @classmethod
    def from_environment(cls):
        """Construit la configuration factice.

        Args:
            Aucun.

        Returns:
            FakeDatabaseConfiguration: Configuration active.
        """

        return cls()


class FakeUserRegistrationService:
    """Service d'inscription factice."""

    def __init__(self, user_repository, email_verification_service):
        """Initialise le service factice.

        Args:
            user_repository (object): Repository injecte.
            email_verification_service (object): Service email injecte.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

    def register_user(self, email, password):
        """Inscrit un utilisateur factice.

        Args:
            email (str): Email fourni.
            password (str): Mot de passe fourni.

        Returns:
            RegisteredUser: Utilisateur cree.

        Raises:
            DuplicateUserEmailError: Si l'email est reserve.
            PasswordPolicyError: Si le mot de passe est invalide.
            ValueError: Si l'email manque.
        """

        if email == "duplicate@example.com":
            raise DuplicateUserEmailError("Un compte existe deja pour cet email.")
        if not email:
            raise ValueError("L'email est obligatoire.")
        if password != "VeryStrongPassword123!":
            raise PasswordPolicyError("Le mot de passe doit contenir au moins 8 caracteres, au moins un chiffre, un caractere special, une minuscule et une majuscule.")
        return RegisteredUser(7, str(email).strip().lower(), datetime(2026, 5, 13, 12), False, "USER")


class FakeUserCollectionImportRepository:
    """Repository de collection utilisateur factice."""

    has_collection = False

    def __init__(self, configuration):
        """Initialise le repository.

        Args:
            configuration (object): Configuration ignoree.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

    def user_has_collection(self, user_id):
        """Indique si une collection existe.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            bool: Valeur configuree.
        """

        return self.has_collection

    def import_collection(self, user_id, collection_file_path, import_data):
        """Retourne des compteurs de persistance.

        Args:
            user_id (int): Identifiant utilisateur.
            collection_file_path (str): Chemin final.
            import_data (object): Donnees ignorees.

        Returns:
            UserCollectionImportPersistenceResult: Compteurs factices.
        """

        return UserCollectionImportPersistenceResult(1, 2, 3, 4)


class FakeUserCollectionImportService:
    """Service d'import factice."""

    next_error = None
    last_call = None

    def __init__(self, configuration, repository, ods_reader):
        """Initialise le service.

        Args:
            configuration (object): Configuration ignoree.
            repository (object): Repository ignore.
            ods_reader (object): Lecteur ignore.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

    def import_collection(self, user_id, source_file_path, original_filename=None):
        """Importe une collection factice.

        Args:
            user_id (int): Identifiant utilisateur.
            source_file_path (str): Chemin temporaire.
            original_filename (str | None): Nom original.

        Returns:
            UserCollectionImportResult: Compteurs factices.

        Raises:
            Exception: Erreur configuree.
        """

        self.__class__.last_call = (user_id, source_file_path, original_filename)
        if self.next_error:
            raise self.next_error
        return UserCollectionImportResult(1, 2, 3, 4)


class FakeOdsCollectionImportReader:
    """Lecteur ODS factice."""


class BaseAppRoutesTest(unittest.TestCase):
    """Base commune des tests de routes Flask."""

    def setUp(self):
        """Remplace les dependances globales par des fakes.

        Args:
            Aucun.

        Returns:
            None: Le client Flask est prepare.
        """

        self.original_user_repository = app_module.authentication_controller.user_repository_class
        self.original_user_controller_repository = app_module.user_controller.user_repository_class
        self.original_user_controller_database_configuration = app_module.user_controller.database_configuration_class
        self.original_collection_user_repository = app_module.user_collection_import_controller.user_repository_class
        self.original_collection_import_repository = app_module.user_collection_import_controller.import_repository_class
        self.original_collection_import_service = app_module.user_collection_import_controller.import_service_class
        self.original_collection_ods_reader = app_module.user_collection_import_controller.ods_reader_class
        self.original_collection_database_configuration = app_module.user_collection_import_controller.database_configuration_class
        self.original_collection_query_service_factory = app_module.collection_controller.collection_query_service_factory
        self.original_collection_user_repository_class = app_module.collection_controller.user_repository_class
        self.original_collection_database_configuration_class = app_module.collection_controller.database_configuration_class
        self.original_registration_service = app_module.authentication_controller.user_registration_service_class
        self.original_database_configuration = app_module.authentication_controller.database_configuration_class
        self.original_platform_library_service_factory = app_module.platform_controller.library_service_factory
        self.original_studio_library_service_factory = app_module.studio_controller.library_service_factory
        self.original_game_library_service_factory = app_module.game_controller.library_service_factory
        app_module.authentication_controller.user_repository_class = FakeSqlAlchemyUserRepository
        app_module.user_controller.user_repository_class = FakeSqlAlchemyUserRepository
        app_module.user_controller.database_configuration_class = FakeDatabaseConfiguration
        app_module.user_collection_import_controller.user_repository_class = FakeSqlAlchemyUserRepository
        app_module.user_collection_import_controller.import_repository_class = FakeUserCollectionImportRepository
        app_module.user_collection_import_controller.import_service_class = FakeUserCollectionImportService
        app_module.user_collection_import_controller.ods_reader_class = FakeOdsCollectionImportReader
        app_module.user_collection_import_controller.database_configuration_class = FakeDatabaseConfiguration
        app_module.collection_controller.collection_query_service_factory = FakeUserCollectionQueryService
        app_module.collection_controller.user_repository_class = FakeSqlAlchemyUserRepository
        app_module.collection_controller.database_configuration_class = FakeDatabaseConfiguration
        app_module.authentication_controller.user_registration_service_class = FakeUserRegistrationService
        app_module.authentication_controller.database_configuration_class = FakeDatabaseConfiguration
        app_module.platform_controller.library_service_factory = FakeLibraryService
        app_module.studio_controller.library_service_factory = FakeLibraryService
        app_module.game_controller.library_service_factory = FakeLibraryService
        FakeUserCollectionImportRepository.has_collection = False
        FakeUserCollectionImportService.next_error = None
        FakeUserCollectionImportService.last_call = None
        FakeLibraryService.last_platforms_criteria = None
        FakeLibraryService.last_studios_criteria = None
        FakeLibraryService.last_games_criteria = None
        FakeUserCollectionQueryService.last_platforms_criteria = None
        FakeUserCollectionQueryService.last_games_criteria = None
        FakeUserCollectionQueryService.collection_file_path = __file__
        app_module.app.config.update(TESTING=True)
        self.client = app_module.app.test_client()

    def tearDown(self):
        """Restaure les dependances globales.

        Args:
            Aucun.

        Returns:
            None: Les fakes sont retires.
        """

        app_module.authentication_controller.user_repository_class = self.original_user_repository
        app_module.user_controller.user_repository_class = self.original_user_controller_repository
        app_module.user_controller.database_configuration_class = self.original_user_controller_database_configuration
        app_module.user_collection_import_controller.user_repository_class = self.original_collection_user_repository
        app_module.user_collection_import_controller.import_repository_class = self.original_collection_import_repository
        app_module.user_collection_import_controller.import_service_class = self.original_collection_import_service
        app_module.user_collection_import_controller.ods_reader_class = self.original_collection_ods_reader
        app_module.user_collection_import_controller.database_configuration_class = self.original_collection_database_configuration
        app_module.collection_controller.collection_query_service_factory = self.original_collection_query_service_factory
        app_module.collection_controller.user_repository_class = self.original_collection_user_repository_class
        app_module.collection_controller.database_configuration_class = self.original_collection_database_configuration_class
        app_module.authentication_controller.user_registration_service_class = self.original_registration_service
        app_module.authentication_controller.database_configuration_class = self.original_database_configuration
        app_module.platform_controller.library_service_factory = self.original_platform_library_service_factory
        app_module.studio_controller.library_service_factory = self.original_studio_library_service_factory
        app_module.game_controller.library_service_factory = self.original_game_library_service_factory

    def get_auth_headers(self):
        """Construit un header Bearer valide.

        Args:
            Aucun.

        Returns:
            dict[str, str]: En-tetes ADMIN.
        """

        token = app_module.auth_token_service.create_access_token("admin")
        return {"Authorization": f"Bearer {token}"}

    def get_admin_auth_headers(self):
        """Construit un header Bearer administrateur.

        Args:
            Aucun.

        Returns:
            dict[str, str]: En-tetes ADMIN.
        """

        token = app_module.auth_token_service.create_access_token("admin", "ADMIN")
        return {"Authorization": f"Bearer {token}"}

    def get_user_auth_headers(self):
        """Construit un header Bearer utilisateur.

        Args:
            Aucun.

        Returns:
            dict[str, str]: En-tetes USER.
        """

        token = app_module.auth_token_service.create_access_token("user@example.com", "USER")
        return {"Authorization": f"Bearer {token}"}
