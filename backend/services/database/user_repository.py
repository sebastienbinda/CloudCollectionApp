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

from services.auth.email_verification_service import (
    EmailVerificationToken,
    InvalidEmailVerificationTokenError,
    VerifiedUser,
)
from services.auth.user_registration_service import DuplicateUserEmailError, RegisteredUser

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
    ) -> RegisteredUser:
        """Cree un utilisateur en stockant uniquement l'empreinte du mot de passe.

        Args:
            email (str): Adresse email normalisee.
            password_hash (str): Empreinte non reversible du mot de passe.
            creation_date (datetime): Date de creation du compte.
            verification_token (EmailVerificationToken): Token de validation email a stocker.

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
                        "(email, password_hash, is_email_verified, "
                        "email_verification_token_hash, email_verification_expires_at, "
                        "creation_date) "
                        "VALUES (:email, :password_hash, false, :token_hash, "
                        ":token_expires_at, :creation_date) "
                        "RETURNING id, email, creation_date, is_email_verified"
                    ),
                    {
                        "email": email,
                        "password_hash": password_hash,
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
