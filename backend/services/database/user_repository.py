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
# Description : persistance SQL des inscriptions utilisateur.

from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from services.auth.auth_token_service import AuthenticatedUserCredentials
from services.auth.email_verification_service import (
    EmailVerificationToken,
    InvalidEmailVerificationTokenError,
    VerifiedUser,
)
from services.auth.user_registration_service import DuplicateUserEmailError, RegisteredUser
from services.auth.user_profile import UserProfile
from services.users import UserSearchCriteria, UserStatus, UserSummary

from .database_configuration import DatabaseConfiguration


class SqlAlchemyUserRepository:
    """Persiste les utilisateurs dans PostgreSQL via SQLAlchemy Core."""

    def __init__(self, configuration: DatabaseConfiguration):
        """Initialise le repository utilisateur.

        Args:
            configuration (DatabaseConfiguration): Configuration de connexion PostgreSQL.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si aucune base de donnees n'est configuree.
        """

        configuration.validate()
        if not configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour enregistrer un utilisateur.")
        self.configuration = configuration
        self.engine = create_engine(configuration.database_url)

    def email_exists(self, email: str) -> bool:
        """Indique si une adresse email existe deja.

        Args:
            email (str): Adresse email normalisee.

        Returns:
            bool: `True` si l'adresse est deja presente en base.
        """

        schema_name = self.configuration.schema_name
        with self.engine.connect() as connection:
            existing_count = connection.execute(
                text(f'SELECT COUNT(*) FROM "{schema_name}".t_user WHERE email = :email'),
                {"email": email},
            ).scalar_one()
        return int(existing_count) > 0

    def create_user(
        self,
        email: str,
        password_hash: str,
        creation_date: datetime,
        verification_token: EmailVerificationToken,
        profile: str = UserProfile.USER.value,
    ) -> RegisteredUser:
        """Cree un utilisateur en stockant uniquement l'empreinte du mot de passe.

        Args:
            email (str): Adresse email normalisee.
            password_hash (str): Empreinte non reversible du mot de passe.
            creation_date (datetime): Date de creation du compte.
            verification_token (EmailVerificationToken): Token de validation email a stocker.
            profile (str): Profil applicatif initial du compte.

        Returns:
            RegisteredUser: Donnees publiques de l'utilisateur cree.

        Raises:
            DuplicateUserEmailError: Si la contrainte unique email est violee.
        """

        schema_name = self.configuration.schema_name
        try:
            with self.engine.begin() as connection:
                row = connection.execute(
                    text(
                        f'INSERT INTO "{schema_name}".t_user '
                        "(email, password_hash, profile, status, is_email_verified, "
                        "email_verification_token_hash, email_verification_expires_at, "
                        "creation_date) "
                        "VALUES (:email, :password_hash, :profile, :status, false, :token_hash, "
                        ":token_expires_at, :creation_date) "
                        "RETURNING id, email, creation_date, is_email_verified, profile, status"
                    ),
                    {
                        "email": email,
                        "password_hash": password_hash,
                        "profile": UserProfile.normalize(profile).value,
                        "status": UserStatus.ACTIVE.value,
                        "token_hash": verification_token.token_hash,
                        "token_expires_at": verification_token.expires_at,
                        "creation_date": creation_date,
                    },
                ).mappings().one()
        except IntegrityError as exc:
            raise DuplicateUserEmailError("Un compte existe deja pour cet email.") from exc

        return RegisteredUser(
            id=int(row["id"]),
            email=str(row["email"]),
            creation_date=row["creation_date"],
            is_email_verified=bool(row["is_email_verified"]),
            profile=str(row["profile"]),
            status=str(row["status"]),
        )

    def find_verified_user_credentials_by_email(
        self,
        email: str,
    ) -> AuthenticatedUserCredentials | None:
        """Retourne les identifiants d'un utilisateur verifie par email.

        Args:
            email (str): Adresse email normalisee a rechercher.

        Returns:
            AuthenticatedUserCredentials | None: Donnees d'authentification si le compte est verifie.
        """

        schema_name = self.configuration.schema_name
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    f'SELECT id, email, password_hash, profile, status FROM "{schema_name}".t_user '
                    "WHERE email = :email AND is_email_verified = true"
                ),
                {"email": email},
            ).mappings().first()

        if not row:
            return None

        return AuthenticatedUserCredentials(
            id=int(row["id"]),
            email=str(row["email"]),
            password_hash=str(row["password_hash"]),
            profile=str(row["profile"]),
            status=str(row["status"]),
        )

    def search_users(self, criteria: UserSearchCriteria) -> list[UserSummary]:
        """Recherche les utilisateurs selon des criteres optionnels.

        Args:
            criteria (UserSearchCriteria): Criteres de filtrage utilisateur.

        Returns:
            list[UserSummary]: Utilisateurs correspondant aux criteres.
        """

        schema_name = self.configuration.schema_name
        where_clauses = []
        parameters = {}
        if criteria.name:
            where_clauses.append("LOWER(email) LIKE :name")
            parameters["name"] = f"%{criteria.name.strip().lower()}%"
        if criteria.creation_date_from:
            where_clauses.append("creation_date >= :creation_date_from")
            parameters["creation_date_from"] = criteria.creation_date_from
        if criteria.creation_date_to:
            where_clauses.append("creation_date <= :creation_date_to")
            parameters["creation_date_to"] = criteria.creation_date_to
        if criteria.last_connexion_date_from:
            where_clauses.append("last_connexion_date >= :last_connexion_date_from")
            parameters["last_connexion_date_from"] = criteria.last_connexion_date_from
        if criteria.last_connexion_date_to:
            where_clauses.append("last_connexion_date <= :last_connexion_date_to")
            parameters["last_connexion_date_to"] = criteria.last_connexion_date_to
        if criteria.status:
            where_clauses.append("status = :status")
            parameters["status"] = UserStatus.normalize(criteria.status).value
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        with self.engine.connect() as connection:
            rows = connection.execute(
                text(
                    f'SELECT id, email, profile, status, is_email_verified, creation_date, '
                    f'last_connexion_date FROM "{schema_name}".t_user '
                    f"{where_sql} ORDER BY creation_date DESC, id DESC"
                ),
                parameters,
            ).mappings().all()
        return [self._map_user_summary(row) for row in rows]

    def delete_user(self, user_id: int) -> bool:
        """Supprime un utilisateur et ses rattachements de collection.

        Args:
            user_id (int): Identifiant technique du compte a supprimer.

        Returns:
            bool: `True` si un compte a ete supprime.
        """

        schema_name = self.configuration.schema_name
        with self.engine.begin() as connection:
            connection.execute(
                text(f'DELETE FROM "{schema_name}".t_user_collection WHERE user_id = :user_id'),
                {"user_id": user_id},
            )
            result = connection.execute(
                text(f'DELETE FROM "{schema_name}".t_user WHERE id = :user_id'),
                {"user_id": user_id},
            )
        return result.rowcount > 0

    def lock_user(self, user_id: int) -> UserSummary | None:
        """Passe un utilisateur au statut `LOCKED`.

        Args:
            user_id (int): Identifiant technique du compte a bloquer.

        Returns:
            UserSummary | None: Utilisateur bloque, ou `None` si absent.
        """

        schema_name = self.configuration.schema_name
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    f'UPDATE "{schema_name}".t_user '
                    "SET status = :status "
                    "WHERE id = :user_id "
                    "RETURNING id, email, profile, status, is_email_verified, "
                    "creation_date, last_connexion_date"
                ),
                {"user_id": user_id, "status": UserStatus.LOCKED.value},
            ).mappings().first()
        return self._map_user_summary(row) if row else None

    def unlock_user(self, user_id: int) -> UserSummary | None:
        """Passe un utilisateur au statut `ACTIVE`.

        Args:
            user_id (int): Identifiant technique du compte a debloquer.

        Returns:
            UserSummary | None: Utilisateur debloque, ou `None` si absent.
        """

        schema_name = self.configuration.schema_name
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    f'UPDATE "{schema_name}".t_user '
                    "SET status = :status "
                    "WHERE id = :user_id "
                    "RETURNING id, email, profile, status, is_email_verified, "
                    "creation_date, last_connexion_date"
                ),
                {"user_id": user_id, "status": UserStatus.ACTIVE.value},
            ).mappings().first()
        return self._map_user_summary(row) if row else None

    def update_last_connexion_date(
        self,
        user_id: int,
        last_connexion_date: datetime,
    ) -> None:
        """Met a jour la date de derniere connexion d'un utilisateur.

        Args:
            user_id (int): Identifiant technique de l'utilisateur.
            last_connexion_date (datetime): Date de connexion a enregistrer.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        schema_name = self.configuration.schema_name
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    f'UPDATE "{schema_name}".t_user '
                    "SET last_connexion_date = :last_connexion_date "
                    "WHERE id = :user_id"
                ),
                {"user_id": user_id, "last_connexion_date": last_connexion_date},
            )

    def verify_email_by_token_hash(
        self,
        token_hash: str,
        verified_at: datetime,
    ) -> VerifiedUser:
        """Valide l'adresse email associee a une empreinte de token.

        Args:
            token_hash (str): Empreinte SHA-256 du token recu.
            verified_at (datetime): Date de validation.

        Returns:
            VerifiedUser: Donnees publiques de l'utilisateur valide.

        Raises:
            InvalidEmailVerificationTokenError: Si le token est inconnu ou expire.
        """

        schema_name = self.configuration.schema_name
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    f'UPDATE "{schema_name}".t_user '
                    "SET is_email_verified = true, "
                    "email_verified_at = :verified_at, "
                    "email_verification_token_hash = NULL, "
                    "email_verification_expires_at = NULL "
                    "WHERE email_verification_token_hash = :token_hash "
                    "AND email_verification_expires_at >= :verified_at "
                    "RETURNING id, email, email_verified_at"
                ),
                {"token_hash": token_hash, "verified_at": verified_at},
            ).mappings().first()

        if not row:
            raise InvalidEmailVerificationTokenError("Le token de validation est invalide ou expire.")

        return VerifiedUser(
            id=int(row["id"]),
            email=str(row["email"]),
            email_verified_at=row["email_verified_at"],
        )

    def _map_user_summary(self, row) -> UserSummary:
        """Convertit une ligne SQL utilisateur en objet public.

        Args:
            row (Mapping): Ligne SQLAlchemy mappee.

        Returns:
            UserSummary: Donnees utilisateur sans secret.
        """

        return UserSummary(
            id=int(row["id"]),
            email=str(row["email"]),
            profile=str(row["profile"]),
            status=str(row["status"]),
            is_email_verified=bool(row["is_email_verified"]),
            creation_date=row["creation_date"],
            last_connexion_date=row["last_connexion_date"],
        )
