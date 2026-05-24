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
import unittest
from io import BytesIO
from datetime import datetime
from pathlib import Path
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
from services.users import UserSummary
from services.database.user_collection_import_repository import (
    UserCollectionImportPersistenceResult,
)
from services.users.user_collection_import_service import (
    UserCollectionImportConflictError,
    UserCollectionImportInvalidFileError,
    UserCollectionImportResult,
    UserCollectionImportTooLargeError,
    UserCollectionImportUnexpectedError,
)


class FakeSqlAlchemyUserRepository:
    user_password_hash = PasswordHashService().hash_password("VeryStrongPassword123!")

    def __init__(self, configuration):
        """Initialise un repository utilisateur factice.
        Args:
            configuration (DatabaseConfiguration): Configuration ignoree en test.
        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration
        self.last_connexion_user_id = None

    def find_verified_user_credentials_by_email(self, email):
        """Retourne les identifiants d'un utilisateur verifie factice.

        Args:
            email (str): Email normalise recherche.

        Returns:
            AuthenticatedUserCredentials | None: Utilisateur verifie ou absent.
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
        """Memorise une date de derniere connexion factice.

        Args:
            user_id (int): Identifiant utilisateur.
            last_connexion_date (datetime): Date de connexion ignoree.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.last_connexion_user_id = user_id

    def find_user_id_by_email(self, email):
        """Retourne l'identifiant d'un utilisateur factice par email.

        Args:
            email (str): Email recherche.

        Returns:
            int | None: Identifiant utilisateur ou absence.
        """

        if email != "user@example.com":
            return None
        return 7

    def search_users(self, criteria):
        """Retourne des utilisateurs factices filtres par criteres.

        Args:
            criteria (UserSearchCriteria): Criteres de recherche utilisateur.

        Returns:
            list[UserSummary]: Utilisateurs factices correspondant aux filtres.
        """

        users = [
            UserSummary(
                id=7,
                email="user@example.com",
                profile=UserProfile.USER.value,
                status=UserStatus.ACTIVE.value,
                is_email_verified=True,
                creation_date=datetime(2026, 5, 13, 12, 0, 0),
                last_connexion_date=datetime(2026, 5, 22, 8, 30, 0),
            ),
            UserSummary(
                id=8,
                email="locked@example.com",
                profile=UserProfile.USER.value,
                status=UserStatus.LOCKED.value,
                is_email_verified=True,
                creation_date=datetime(2026, 5, 20, 12, 0, 0),
                last_connexion_date=None,
            ),
        ]
        if criteria.name:
            users = [user for user in users if criteria.name.lower() in user.email.lower()]
        if criteria.creation_date_from:
            users = [user for user in users if user.creation_date >= criteria.creation_date_from]
        if criteria.creation_date_to:
            users = [user for user in users if user.creation_date <= criteria.creation_date_to]
        if criteria.last_connexion_date_from:
            users = [
                user for user in users
                if user.last_connexion_date
                and user.last_connexion_date >= criteria.last_connexion_date_from
            ]
        if criteria.last_connexion_date_to:
            users = [
                user for user in users
                if user.last_connexion_date
                and user.last_connexion_date <= criteria.last_connexion_date_to
            ]
        if criteria.status:
            users = [user for user in users if user.status == criteria.status]
        return users

    def delete_user(self, user_id):
        """Supprime un utilisateur factice.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            bool: `True` pour l'utilisateur de test supprimable.
        """

        return user_id == 7

    def lock_user(self, user_id):
        """Bloque un utilisateur factice.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            UserSummary | None: Utilisateur bloque ou absent.
        """

        if user_id != 7:
            return None
        return UserSummary(
            id=7,
            email="user@example.com",
            profile=UserProfile.USER.value,
            status=UserStatus.LOCKED.value,
            is_email_verified=True,
            creation_date=datetime(2026, 5, 13, 12, 0, 0),
            last_connexion_date=datetime(2026, 5, 22, 8, 30, 0),
        )

    def unlock_user(self, user_id):
        """Debloque un utilisateur factice.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            UserSummary | None: Utilisateur debloque ou absent.
        """

        if user_id != 7:
            return None
        return UserSummary(
            id=7,
            email="user@example.com",
            profile=UserProfile.USER.value,
            status=UserStatus.ACTIVE.value,
            is_email_verified=True,
            creation_date=datetime(2026, 5, 13, 12, 0, 0),
            last_connexion_date=datetime(2026, 5, 22, 8, 30, 0),
        )

    def verify_email_by_token_hash(self, token_hash, verified_at):
        """Valide un token factice.
        Args:
            token_hash (str): Empreinte du token.
            verified_at (datetime): Date de validation.
        Returns:
            VerifiedUser: Utilisateur valide factice.
        """

        if token_hash == EmailVerificationService.hash_token("invalid-token"):
            raise InvalidEmailVerificationTokenError("Le token de validation est invalide ou expire.")
        return VerifiedUser(id=7, email="user@example.com", email_verified_at=verified_at)


class FakeDatabaseConfiguration:
    """Configuration de base factice active pour les tests de route."""

    def is_database_enabled(self):
        """Indique que la base factice est disponible.

        Args:
            Aucun.

        Returns:
            bool: Toujours `True` pour activer le repository factice.
        """

        return True

    @classmethod
    def from_environment(cls):
        """Construit la configuration factice.

        Args:
            Aucun.

        Returns:
            FakeDatabaseConfiguration: Configuration factice active.
        """

        return cls()


class FakeUserRegistrationService:
    def __init__(self, user_repository, email_verification_service):
        """Initialise un service d'inscription factice.
        Args:
            user_repository (object): Repository injecte par la route.
            email_verification_service (object): Service de validation email injecte par la route.
        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.user_repository = user_repository
        self.email_verification_service = email_verification_service

    def register_user(self, email, password):
        """Retourne un utilisateur factice ou leve une erreur controlee.
        Args:
            email (str): Email fourni par la route.
            password (str): Mot de passe fourni par la route.
        Returns:
            RegisteredUser: Utilisateur public factice.
        """

        if email == "duplicate@example.com":
            raise DuplicateUserEmailError("Un compte existe deja pour cet email.")
        if not email:
            raise ValueError("L'email est obligatoire.")
        if password != "VeryStrongPassword123!":
            raise PasswordPolicyError(
                "Le mot de passe doit contenir au moins 8 caracteres, au moins un chiffre, "
                "un caractere special, une minuscule et une majuscule."
            )
        return RegisteredUser(
            id=7,
            email=str(email).strip().lower(),
            creation_date=datetime(2026, 5, 13, 12, 0, 0),
            is_email_verified=False,
            profile=UserProfile.USER.value,
        )


class FakeUserCollectionImportRepository:
    """Repository factice de collection utilisateur pour les routes."""

    has_collection = False

    def __init__(self, configuration):
        """Initialise le repository factice.

        Args:
            configuration (object): Configuration ignoree.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration

    def user_has_collection(self, user_id):
        """Indique si une collection existe deja.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            bool: Valeur configuree pour le test.
        """

        return self.has_collection

    def import_collection(self, user_id, collection_file_path, import_data):
        """Retourne un resultat de persistance factice.

        Args:
            user_id (int): Identifiant utilisateur.
            collection_file_path (str): Chemin final.
            import_data (object): Donnees ignorees.

        Returns:
            UserCollectionImportPersistenceResult: Resultat factice.
        """

        return UserCollectionImportPersistenceResult(1, 2, 3, 4)


class FakeUserCollectionImportService:
    """Service factice d'import de collection pour les routes."""

    next_error = None
    last_call = None

    def __init__(self, configuration, repository, ods_reader):
        """Initialise le service factice.

        Args:
            configuration (object): Configuration ignoree.
            repository (object): Repository ignore.
            ods_reader (object): Lecteur ignore.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration
        self.repository = repository
        self.ods_reader = ods_reader

    def import_collection(self, user_id, source_file_path, original_filename=None):
        """Retourne un resultat ou leve l'erreur configuree.

        Args:
            user_id (int): Identifiant utilisateur.
            source_file_path (str): Fichier temporaire recu.
            original_filename (str | None): Nom original.

        Returns:
            UserCollectionImportResult: Resultat factice.

        Raises:
            Exception: Erreur configuree.
        """

        self.__class__.last_call = (user_id, source_file_path, original_filename)
        if self.next_error:
            raise self.next_error
        return UserCollectionImportResult(1, 2, 3, 4)


class FakeOdsCollectionImportReader:
    """Lecteur ODS factice pour construire le service de route."""

    def __init__(self):
        """Initialise le lecteur factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """
class FakeGamesService:
    def __init__(self):
        """Initialise un service JeuxVideo factice.
        Args:
            Aucun.
        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """
    def list_platforms(self):
        """Retourne les plateformes factices.
        Args:
            Aucun.
        Returns:
            list[str]: Plateformes disponibles.
        """
        return ["Switch", "Playstation"]
    def reset_cache(self):
        """Retourne un nombre factice d'entrees supprimees.
        Args:
            Aucun.
        Returns:
            int: Nombre d'entrees supprimees.
        """
        return 2
    def get_ods_download(self):
        """Retourne un fichier ODS factice a telecharger.
        Args:
            Aucun.
        Returns:
            tuple[str, str]: Chemin et nom de fichier factices.
        """
        return str(Path(__file__)), "JeuxVideo-test.ods"
    def search(self, platform, query=""):
        """Retourne les jeux factices d'une plateforme.
        Args:
            platform (str): Plateforme demandee.
            query (str): Recherche optionnelle.
        Returns:
            list[dict[str, str]]: Jeux factices.
        """
        return [
            {
                "Nom du jeu": "Mario Kart",
                "Plateforme": platform,
                "Query": query,
                "Prix d'achat": 45,
            }
        ]
    def search_by_game_name(self, query, limit=50):
        """Retourne les jeux factices trouves par nom.
        Args:
            query (str): Texte recherche.
            limit (int): Nombre maximal de resultats.
        Returns:
            list[dict[str, object]]: Jeux factices trouves.
        """
        return [
            {
                "Nom du jeu": "Mario Kart",
                "Plateforme": "Switch",
                "Query": query,
                "Prix d'achat": 45,
            }
        ][:limit]
    def get_home_stats(self):
        """Retourne des statistiques d'accueil factices.
        Args:
            Aucun.
        Returns:
            dict[str, object]: Statistiques factices avec prix.
        """
        return {
            "title": "Jeux Video",
            "totals": {"games_count": 1, "total_price": 45, "average_price": 45},
            "platforms": [
                {
                    "name": "Switch",
                    "sheet_name": "Switch",
                    "games_count": 1,
                    "total_price": 45,
                    "average_price": 45,
                }
            ],
        }
    def list_column_values(self, platform):
        """Retourne les valeurs distinctes factices d'une plateforme.
        Args:
            platform (str): Plateforme demandee.
        Returns:
            dict[str, list[object]]: Valeurs distinctes factices.
        """
        return {"Nom du jeu": ["Mario Kart"], "Prix d'achat": [45]}
    def add_game(self, payload):
        """Retourne le jeu ajoute sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees du jeu.
        Returns:
            dict[str, str]: Jeu ajoute.
        """
        if not payload.get("Nom du jeu"):
            raise ValueError("Le nom du jeu est obligatoire.")
        return {"Plateforme": payload.get("platform"), "Nom du jeu": payload.get("Nom du jeu")}
    def delete_wishlist_game(self, payload):
        """Retourne le jeu wishlist supprime sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees du jeu.
        Returns:
            dict[str, str]: Jeu supprime.
        """
        if not payload.get("Console"):
            raise ValueError("La console est obligatoire.")
        return {"Nom du jeu": payload.get("Nom du jeu"), "Console": payload.get("Console")}
    def add_wishlist_game(self, payload):
        """Retourne le jeu wishlist ajoute sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees du jeu wishlist.
        Returns:
            dict[str, str]: Jeu ajoute.
        """
        if not payload.get("Studio"):
            raise ValueError("Studio est obligatoire.")
        return {"Nom du jeu": payload.get("Nom du jeu"), "Console": payload.get("Console")}
    def update_wishlist_game(self, payload):
        """Retourne le jeu wishlist modifie sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees de modification.
        Returns:
            dict[str, str]: Jeu wishlist modifie.
        """
        updated = payload.get("updated") or {}
        if not updated.get("Studio"):
            raise ValueError("Studio est obligatoire.")
        return {"Nom du jeu": updated.get("Nom du jeu"), "Console": updated.get("Console")}
    def delete_game(self, payload):
        """Retourne le jeu supprime sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees du jeu.
        Returns:
            dict[str, str]: Jeu supprime.
        """
        if not payload.get("Nom du jeu"):
            raise ValueError("Le nom du jeu est obligatoire.")
        return {"Plateforme": payload.get("platform"), "Nom du jeu": payload.get("Nom du jeu")}
    def update_game(self, payload):
        """Retourne le jeu modifie sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees de modification.
        Returns:
            dict[str, str]: Jeu modifie.
        """
        updated = payload.get("updated") or {}
        if not updated.get("Nom du jeu"):
            raise ValueError("Nom du jeu est obligatoire.")
        return {"Plateforme": payload.get("platform"), **updated}
    def list_add_game_choices(self, platform=""):
        """Retourne des choix fusionnes factices.
        Args:
            platform (str): Plateforme de reference.
        Returns:
            dict[str, object]: Choix du formulaire d'ajout.
        """
        return {"platforms": ["Switch", "Xbox"], "values_by_column": {"Plateforme": ["Switch", "Xbox"]}}
class AppRoutesTest(unittest.TestCase):
    def setUp(self):
        """Remplace le service ODS par un service factice.
        Args:
            Aucun.
        Returns:
            None: Le client Flask est prepare pour chaque test.
        """
        self.original_service = app_module.GamesService
        self.original_user_repository = app_module.authentication_controller.user_repository_class
        self.original_user_controller_repository = app_module.user_controller.user_repository_class
        self.original_user_controller_database_configuration = (
            app_module.user_controller.database_configuration_class
        )
        self.original_collection_user_repository = (
            app_module.user_collection_import_controller.user_repository_class
        )
        self.original_collection_import_repository = (
            app_module.user_collection_import_controller.import_repository_class
        )
        self.original_collection_import_service = (
            app_module.user_collection_import_controller.import_service_class
        )
        self.original_collection_ods_reader = (
            app_module.user_collection_import_controller.ods_reader_class
        )
        self.original_collection_database_configuration = (
            app_module.user_collection_import_controller.database_configuration_class
        )
        self.original_registration_service = (
            app_module.authentication_controller.user_registration_service_class
        )
        self.original_database_configuration = (
            app_module.authentication_controller.database_configuration_class
        )
        app_module.GamesService = FakeGamesService
        app_module.authentication_controller.user_repository_class = FakeSqlAlchemyUserRepository
        app_module.user_controller.user_repository_class = FakeSqlAlchemyUserRepository
        app_module.user_controller.database_configuration_class = FakeDatabaseConfiguration
        app_module.user_collection_import_controller.user_repository_class = (
            FakeSqlAlchemyUserRepository
        )
        app_module.user_collection_import_controller.import_repository_class = (
            FakeUserCollectionImportRepository
        )
        app_module.user_collection_import_controller.import_service_class = (
            FakeUserCollectionImportService
        )
        app_module.user_collection_import_controller.ods_reader_class = FakeOdsCollectionImportReader
        app_module.user_collection_import_controller.database_configuration_class = (
            FakeDatabaseConfiguration
        )
        FakeUserCollectionImportRepository.has_collection = False
        FakeUserCollectionImportService.next_error = None
        FakeUserCollectionImportService.last_call = None
        app_module.authentication_controller.user_registration_service_class = (
            FakeUserRegistrationService
        )
        app_module.authentication_controller.database_configuration_class = FakeDatabaseConfiguration
        app_module.app.config.update(TESTING=True)
        self.client = app_module.app.test_client()
    def tearDown(self):
        """Restaure le service ODS original.
        Args:
            Aucun.
        Returns:
            None: Les modifications globales du test sont annulees.
        """
        app_module.GamesService = self.original_service
        app_module.authentication_controller.user_repository_class = self.original_user_repository
        app_module.user_controller.user_repository_class = self.original_user_controller_repository
        app_module.user_controller.database_configuration_class = (
            self.original_user_controller_database_configuration
        )
        app_module.user_collection_import_controller.user_repository_class = (
            self.original_collection_user_repository
        )
        app_module.user_collection_import_controller.import_repository_class = (
            self.original_collection_import_repository
        )
        app_module.user_collection_import_controller.import_service_class = (
            self.original_collection_import_service
        )
        app_module.user_collection_import_controller.ods_reader_class = (
            self.original_collection_ods_reader
        )
        app_module.user_collection_import_controller.database_configuration_class = (
            self.original_collection_database_configuration
        )
        app_module.authentication_controller.user_registration_service_class = (
            self.original_registration_service
        )
        app_module.authentication_controller.database_configuration_class = (
            self.original_database_configuration
        )
    def get_auth_headers(self):
        """Construit un header Bearer valide pour les routes protegees.
        Args:
            Aucun.
        Returns:
            dict[str, str]: En-tetes HTTP contenant le token d'authentification.
        """
        token = app_module.auth_token_service.create_access_token("admin")
        return {"Authorization": f"Bearer {token}"}

    def get_admin_auth_headers(self):
        """Construit un header Bearer administrateur valide.

        Args:
            Aucun.

        Returns:
            dict[str, str]: En-tetes HTTP contenant un token ADMIN.
        """

        token = app_module.auth_token_service.create_access_token(
            "admin",
            UserProfile.ADMIN.value,
        )
        return {"Authorization": f"Bearer {token}"}

    def get_user_auth_headers(self):
        """Construit un header Bearer USER valide pour l'utilisateur factice.

        Args:
            Aucun.

        Returns:
            dict[str, str]: En-tetes HTTP contenant un token USER.
        """

        token = app_module.auth_token_service.create_access_token(
            "user@example.com",
            UserProfile.USER.value,
        )
        return {"Authorization": f"Bearer {token}"}
    def test_auth_token_route_returns_bearer_token(self):
        """Verifie la generation d'un token OAuth2 Bearer.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/auth/token",
            json={"username": "admin", "password": "change-me"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Bearer", response.get_json()["token_type"])
        self.assertTrue(response.get_json()["access_token"])
        payload = app_module.auth_token_service.validate_access_token(
            response.get_json()["access_token"],
        )
        self.assertEqual(UserProfile.ADMIN.value, payload["profile"])
    def test_auth_token_route_rejects_invalid_credentials(self):
        """Verifie le refus des identifiants invalides.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/auth/token",
            json={"username": "admin", "password": "bad-password"},
        )
        self.assertEqual(401, response.status_code)
        self.assertIn("invalides", response.get_json()["error"])
    def test_auth_token_route_accepts_verified_registered_user(self):
        """Verifie la generation de token pour un utilisateur en base verifie.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP et le sujet du token.
        """
        response = self.client.post(
            "/auth/token",
            json={"username": "USER@Example.COM", "password": "VeryStrongPassword123!"},
        )
        data = response.get_json()
        payload = app_module.auth_token_service.validate_access_token(data["access_token"])
        self.assertEqual(200, response.status_code)
        self.assertEqual("Bearer", data["token_type"])
        self.assertEqual("user@example.com", payload["sub"])
        self.assertEqual(UserProfile.USER.value, payload["profile"])

    def test_user_search_route_requires_authentication(self):
        """Verifie que la recherche utilisateur exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.get("/api/users")

        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])

    def test_user_search_route_requires_admin_profile(self):
        """Verifie que la recherche utilisateur exige le profil administrateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.get("/api/users", headers=self.get_auth_headers())

        self.assertEqual(403, response.status_code)
        self.assertIn("Profil", response.get_json()["error"])

    def test_user_search_route_filters_users(self):
        """Verifie les filtres de recherche utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les utilisateurs retournes.
        """

        response = self.client.get(
            "/api/users?name=user&creation_date_from=2026-05-01T00:00:00"
            "&last_connexion_date_to=2026-05-23T00:00:00&status=ACTIVE",
            headers=self.get_admin_auth_headers(),
        )
        data = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(data["users"]))
        self.assertEqual("user@example.com", data["users"][0]["email"])
        self.assertEqual(UserStatus.ACTIVE.value, data["users"][0]["status"])
        self.assertNotIn("password", data["users"][0])
        self.assertNotIn("password_hash", data["users"][0])

    def test_user_search_route_rejects_invalid_status(self):
        """Verifie le refus d'un statut de recherche invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.get(
            "/api/users?status=DISABLED",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("statut", response.get_json()["error"])

    def test_user_search_route_rejects_invalid_date(self):
        """Verifie le refus d'une date de recherche invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.get(
            "/api/users?creation_date_from=not-a-date",
            headers=self.get_admin_auth_headers(),
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("date ISO", response.get_json()["error"])

    def test_delete_user_route_deletes_user(self):
        """Verifie la suppression d'un utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.delete("/api/users/7", headers=self.get_admin_auth_headers())

        self.assertEqual(204, response.status_code)

    def test_delete_user_route_returns_not_found(self):
        """Verifie la suppression d'un utilisateur absent.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.delete("/api/users/404", headers=self.get_admin_auth_headers())

        self.assertEqual(404, response.status_code)
        self.assertIn("introuvable", response.get_json()["error"])

    def test_lock_user_route_locks_user(self):
        """Verifie le blocage d'un utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut retourne.
        """

        response = self.client.post("/api/users/7/lock", headers=self.get_admin_auth_headers())
        data = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertEqual(7, data["user"]["id"])
        self.assertEqual(UserStatus.LOCKED.value, data["user"]["status"])

    def test_lock_user_route_returns_not_found(self):
        """Verifie le blocage d'un utilisateur absent.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.post("/api/users/404/lock", headers=self.get_admin_auth_headers())

        self.assertEqual(404, response.status_code)
        self.assertIn("introuvable", response.get_json()["error"])

    def test_unlock_user_route_unlocks_user(self):
        """Verifie le deblocage d'un utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut retourne.
        """

        response = self.client.post("/api/users/7/unlock", headers=self.get_admin_auth_headers())
        data = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertEqual(7, data["user"]["id"])
        self.assertEqual(UserStatus.ACTIVE.value, data["user"]["status"])

    def test_unlock_user_route_returns_not_found(self):
        """Verifie le deblocage d'un utilisateur absent.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.post("/api/users/404/unlock", headers=self.get_admin_auth_headers())

        self.assertEqual(404, response.status_code)
        self.assertIn("introuvable", response.get_json()["error"])

    def test_routes_route_requires_authentication(self):
        """Verifie que le catalogue des routes exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/api/routes")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_register_user_route_returns_public_user(self):
        """Verifie la creation publique d'un utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/api/auth/register",
            json={"email": " USER@Example.COM ", "password": "VeryStrongPassword123!"},
        )
        data = response.get_json()
        self.assertEqual(201, response.status_code)
        self.assertEqual(7, data["user"]["id"])
        self.assertEqual("user@example.com", data["user"]["email"])
        self.assertFalse(data["user"]["is_email_verified"])
        self.assertEqual(UserProfile.USER.value, data["user"]["profile"])
        self.assertNotIn("password", data["user"])
        self.assertNotIn("password_hash", data["user"])
    def test_register_user_route_rejects_duplicate_email(self):
        """Verifie la reponse HTTP pour un email deja utilise.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident le statut 409.
        """
        response = self.client.post(
            "/api/auth/register",
            json={"email": "duplicate@example.com", "password": "VeryStrongPassword123!"},
        )
        self.assertEqual(409, response.status_code)
        self.assertIn("existe deja", response.get_json()["error"])
    def test_register_user_route_rejects_invalid_payload(self):
        """Verifie la reponse HTTP pour une inscription invalide.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident le statut 400.
        """
        response = self.client.post(
            "/api/auth/register",
            json={"email": "user@example.com", "password": "short"},
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("8 caracteres", response.get_json()["error"])
        self.assertIn("un chiffre", response.get_json()["error"])
        self.assertIn("un caractere special", response.get_json()["error"])
        self.assertIn("une minuscule", response.get_json()["error"])
        self.assertIn("une majuscule", response.get_json()["error"])
    def test_verify_email_route_returns_verified_user(self):
        """Verifie la page publique de validation email depuis un lien.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/api/auth/verify-email?token=valid-token")
        self.assertEqual(200, response.status_code)
        self.assertIn("text/html", response.content_type)
        self.assertIn("Compte valide", response.get_data(as_text=True))
        self.assertIn("desormais operationnel", response.get_data(as_text=True))
        self.assertIn('href="/auth"', response.get_data(as_text=True))
    def test_verify_email_route_post_returns_verified_user_json(self):
        """Verifie la validation email API en JSON.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP JSON.
        """
        response = self.client.post("/api/auth/verify-email", json={"token": "valid-token"})
        data = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual(7, data["user"]["id"])
        self.assertEqual("user@example.com", data["user"]["email"])
        self.assertIn("email_verified_at", data["user"])
    def test_verify_email_route_rejects_missing_token(self):
        """Verifie le refus d'une validation sans token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/api/auth/verify-email")
        self.assertEqual(400, response.status_code)
        self.assertIn("text/html", response.content_type)
        self.assertIn("Validation impossible", response.get_data(as_text=True))
        self.assertIn("obligatoire", response.get_data(as_text=True))
    def test_verify_email_route_rejects_invalid_token(self):
        """Verifie le refus d'un token invalide.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post("/api/auth/verify-email", json={"token": "invalid-token"})
        self.assertEqual(400, response.status_code)
        self.assertIn("invalide", response.get_json()["error"])
    def test_platforms_route_requires_authentication(self):
        """Verifie que la liste des plateformes exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/platforms")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_platforms_route_returns_platforms(self):
        """Verifie l'endpoint de liste des plateformes.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get(
            "/collections/JeuxVideo/platforms",
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(["Switch", "Playstation"], response.get_json()["platforms"])
    def test_search_route_requires_authentication(self):
        """Verifie que la recherche exige un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/search?platform=Switch")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_search_route_keeps_prices_with_authentication(self):
        """Verifie que la recherche authentifiee retourne les prix.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la presence des prix.
        """
        response = self.client.get(
            "/collections/JeuxVideo/search?platform=Switch",
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(45, response.get_json()[0]["Prix d'achat"])
    def test_game_search_route_requires_authentication(self):
        """Verifie que la recherche globale exige un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/game-search?q=mario")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_home_route_requires_authentication(self):
        """Verifie que l'accueil exige un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/home")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_home_route_keeps_price_statistics_with_authentication(self):
        """Verifie que l'accueil authentifie retourne les statistiques de prix.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident les champs presents.
        """
        response = self.client.get(
            "/collections/JeuxVideo/home",
            headers=self.get_auth_headers(),
        )
        data = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual(45, data["totals"]["total_price"])
        self.assertEqual(45, data["platforms"][0]["average_price"])
    def test_column_values_route_requires_authentication(self):
        """Verifie que les valeurs de filtre exigent un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/column-values?platform=Switch")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_column_values_route_keeps_price_values_with_authentication(self):
        """Verifie que les valeurs de filtre authentifiees retournent les prix.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la presence des prix.
        """
        response = self.client.get(
            "/collections/JeuxVideo/column-values?platform=Switch",
            headers=self.get_auth_headers(),
        )
        data = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual([45], data["values_by_column"]["Prix d'achat"])
    def test_routes_route_lists_protected_routes(self):
        """Verifie le catalogue des routes et leurs contraintes d'authentification.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident le contrat de decouverte des routes.
        """
        response = self.client.get("/api/routes", headers=self.get_auth_headers())
        routes = response.get_json()["routes"]
        routes_by_key = {
            (route["path"], tuple(route["methods"])): route
            for route in routes
        }
        self.assertEqual(200, response.status_code)
        self.assertFalse(routes_by_key[("/auth/token", ("POST",))]["requires_auth"])
        self.assertFalse(routes_by_key[("/api/auth/register", ("POST",))]["requires_auth"])
        self.assertFalse(
            routes_by_key[("/api/auth/verify-email", ("GET", "POST"))]["requires_auth"]
        )
        self.assertTrue(routes_by_key[("/api/routes", ("GET",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/api/users", ("GET",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/api/users/<int:user_id>", ("DELETE",))]["requires_auth"])
        self.assertTrue(
            routes_by_key[("/api/users/<int:user_id>/lock", ("POST",))]["requires_auth"]
        )
        self.assertTrue(
            routes_by_key[("/api/users/<int:user_id>/unlock", ("POST",))]["requires_auth"]
        )
        self.assertTrue(routes_by_key[("/api/users/me/collection", ("GET",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/api/users/import", ("POST",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/collections/JeuxVideo/platforms", ("GET",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/collections/JeuxVideo/games", ("POST",))]["requires_auth"])
        self.assertTrue(
            routes_by_key[("/collections/JeuxVideo/wishlist/games", ("POST",))]["requires_auth"]
        )
        self.assertEqual(
            ["Bearer"],
            routes_by_key[("/collections/JeuxVideo/games", ("POST",))]["auth_schemes"],
        )
        self.assertEqual(
            [UserProfile.USER.value, UserProfile.ADMIN.value],
            routes_by_key[("/collections/JeuxVideo/games", ("POST",))]["required_profiles"],
        )
        self.assertEqual(
            [UserProfile.ADMIN.value],
            routes_by_key[("/api/users", ("GET",))]["required_profiles"],
        )
        self.assertEqual(
            [UserProfile.ADMIN.value],
            routes_by_key[("/api/users/<int:user_id>/unlock", ("POST",))]["required_profiles"],
        )
        self.assertEqual(
            [UserProfile.USER.value, UserProfile.ADMIN.value],
            routes_by_key[("/api/users/me/collection", ("GET",))]["required_profiles"],
        )
        self.assertEqual(
            [UserProfile.USER.value, UserProfile.ADMIN.value],
            routes_by_key[("/api/users/import", ("POST",))]["required_profiles"],
        )

    def test_current_user_collection_status_returns_false(self):
        """Verifie le statut collection absent de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse JSON.
        """

        response = self.client.get(
            "/api/users/me/collection",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual({"has_collection": False}, response.get_json())

    def test_current_user_collection_status_returns_true(self):
        """Verifie le statut collection present de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse JSON.
        """

        FakeUserCollectionImportRepository.has_collection = True

        response = self.client.get(
            "/api/users/me/collection",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual({"has_collection": True}, response.get_json())

    def test_current_user_collection_status_requires_authentication(self):
        """Verifie que le statut collection exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le code 403.
        """

        response = self.client.get("/api/users/me/collection")

        self.assertEqual(403, response.status_code)

    def test_import_current_user_collection_returns_counts(self):
        """Verifie l'import multipart nominal de collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le code 201 et les compteurs.
        """

        response = self.client.post(
            "/api/users/import",
            data={"collection_file": (BytesIO(b"ods"), "collection.ods")},
            content_type="multipart/form-data",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual(
            {
                "created_platforms": 1,
                "created_studios": 2,
                "created_games": 3,
                "associated_games": 4,
            },
            response.get_json(),
        )
        self.assertEqual(7, FakeUserCollectionImportService.last_call[0])
        self.assertEqual("collection.ods", FakeUserCollectionImportService.last_call[2])

    def test_import_current_user_collection_requires_file(self):
        """Verifie le refus d'un import sans fichier multipart.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le code 400.
        """

        response = self.client.post(
            "/api/users/import",
            data={},
            content_type="multipart/form-data",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("collection_file", response.get_json()["error"])

    def test_import_current_user_collection_maps_conflict(self):
        """Verifie le mapping 409 d'une collection deja importee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le code 409.
        """

        FakeUserCollectionImportService.next_error = UserCollectionImportConflictError("conflit")

        response = self.client.post(
            "/api/users/import",
            data={"collection_file": (BytesIO(b"ods"), "collection.ods")},
            content_type="multipart/form-data",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(409, response.status_code)

    def test_import_current_user_collection_maps_invalid_file(self):
        """Verifie le mapping 400 d'un fichier invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le code 400.
        """

        FakeUserCollectionImportService.next_error = UserCollectionImportInvalidFileError("bad")

        response = self.client.post(
            "/api/users/import",
            data={"collection_file": (BytesIO(b"ods"), "collection.ods")},
            content_type="multipart/form-data",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(400, response.status_code)

    def test_import_current_user_collection_maps_too_large_file(self):
        """Verifie le mapping 413 d'un fichier trop volumineux.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le code 413.
        """

        FakeUserCollectionImportService.next_error = UserCollectionImportTooLargeError("large")

        response = self.client.post(
            "/api/users/import",
            data={"collection_file": (BytesIO(b"ods"), "collection.ods")},
            content_type="multipart/form-data",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(413, response.status_code)

    def test_import_current_user_collection_maps_unexpected_error(self):
        """Verifie le mapping 500 d'une erreur inattendue d'import.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le code 500.
        """

        FakeUserCollectionImportService.next_error = UserCollectionImportUnexpectedError("boom")

        response = self.client.post(
            "/api/users/import",
            data={"collection_file": (BytesIO(b"ods"), "collection.ods")},
            content_type="multipart/form-data",
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(500, response.status_code)
    def test_cache_reset_route_returns_removed_entries(self):
        """Verifie l'endpoint de reset du cache.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/cache/reset",
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.get_json()["removed_entries"])
    def test_add_game_choices_route_returns_merged_choices(self):
        """Verifie l'endpoint des choix fusionnes du formulaire d'ajout.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get(
            "/collections/JeuxVideo/add-game-choices?platform=Switch",
            headers=self.get_auth_headers(),
        )
        data = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual(["Switch", "Xbox"], data["platforms"])
    def test_cache_reset_route_requires_authentication(self):
        """Verifie que le reset du cache exige un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post("/collections/JeuxVideo/cache/reset")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_ods_download_route_returns_attachment(self):
        """Verifie l'endpoint de telechargement du fichier ODS.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get(
            "/collections/JeuxVideo/ods/download",
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("attachment", response.headers["Content-Disposition"])
        response.close()
    def test_ods_download_route_requires_authentication(self):
        """Verifie que le telechargement ODS exige un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/ods/download")
        self.assertEqual(403, response.status_code)
    def test_add_game_route_returns_created_item(self):
        """Verifie l'endpoint d'ajout d'un jeu.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch", "Nom du jeu": "Metroid"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual("Metroid", response.get_json()["item"]["Nom du jeu"])
    def test_add_game_route_rejects_invalid_token(self):
        """Verifie que l'ajout d'un jeu refuse un token invalide.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch", "Nom du jeu": "Metroid"},
            headers={"Authorization": "Bearer invalid-token"},
        )
        self.assertEqual(401, response.status_code)
        self.assertIn("invalide", response.get_json()["error"])
    def test_add_game_route_returns_validation_error(self):
        """Verifie la propagation des erreurs de validation.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
    def test_delete_wishlist_game_route_returns_deleted_item(self):
        """Verifie l'endpoint de suppression wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.delete(
            "/collections/JeuxVideo/wishlist/games",
            json={"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Switch 2", response.get_json()["item"]["Console"])
    def test_add_wishlist_game_route_returns_created_item(self):
        """Verifie l'endpoint d'ajout wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/wishlist/games",
            json={"Nom du jeu": "Chrono Trigger", "Console": "Switch 2", "Studio": "Square"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual("Switch 2", response.get_json()["item"]["Console"])
    def test_add_wishlist_game_route_returns_validation_error(self):
        """Verifie les erreurs de validation de l'ajout wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/wishlist/games",
            json={"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
    def test_delete_game_route_returns_deleted_item(self):
        """Verifie l'endpoint de suppression d'un jeu de plateforme.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.delete(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch", "Nom du jeu": "Metroid"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Metroid", response.get_json()["item"]["Nom du jeu"])
    def test_delete_game_route_returns_validation_error(self):
        """Verifie les erreurs de validation de suppression d'un jeu.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.delete(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
    def test_update_game_route_returns_updated_item(self):
        """Verifie l'endpoint de modification d'un jeu de plateforme.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.put(
            "/collections/JeuxVideo/games",
            json={
                "platform": "Switch",
                "original": {"Nom du jeu": "Metroid"},
                "updated": {"Nom du jeu": "Metroid Prime"},
            },
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Metroid Prime", response.get_json()["item"]["Nom du jeu"])
    def test_update_game_route_returns_validation_error(self):
        """Verifie les erreurs de validation de modification d'un jeu.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.put(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch", "original": {"Nom du jeu": "Metroid"}, "updated": {}},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
    def test_delete_wishlist_game_route_returns_validation_error(self):
        """Verifie les erreurs de validation de suppression wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.delete(
            "/collections/JeuxVideo/wishlist/games",
            json={"Nom du jeu": "Chrono Trigger"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
    def test_update_wishlist_game_route_returns_updated_item(self):
        """Verifie l'endpoint de modification wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.put(
            "/collections/JeuxVideo/wishlist/games",
            json={
                "original": {"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"},
                "updated": {"Nom du jeu": "Chrono Trigger", "Console": "Switch 2", "Studio": "Square"},
            },
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Switch 2", response.get_json()["item"]["Console"])
    def test_update_wishlist_game_route_returns_validation_error(self):
        """Verifie les erreurs de validation de modification wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.put(
            "/collections/JeuxVideo/wishlist/games",
            json={
                "original": {"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"},
                "updated": {"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"},
            },
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
if __name__ == "__main__":
    unittest.main()
