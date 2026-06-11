#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : persistance SQL du reset global de la Bibliotheque.

from dataclasses import dataclass
from datetime import datetime

from typing import Callable

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .database_configuration import DatabaseConfiguration


@dataclass(frozen=True)
class LibraryResetImportableUser:
    """Represente un utilisateur dont le fichier peut reconstruire la Bibliotheque.

    Attributes:
        id (int): Identifiant technique utilisateur.
        email (str): Adresse email utilisateur.
        collection_file_path (str): Chemin du fichier stocke.
        collection_file_description (dict | None): Configuration d'import sauvegardee.
        profile (str): Profil applicatif.
        status (str): Statut fonctionnel.
        creation_date (datetime): Date de creation utilisateur.
    """

    id: int
    email: str
    collection_file_path: str
    collection_file_description: dict | None
    profile: str
    status: str
    creation_date: datetime


EngineFactory = Callable[[str], Engine]


class SqlAlchemyLibraryResetRepository:
    """Execute les operations SQL necessaires au reset Bibliotheque."""

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        engine: Engine | None = None,
        engine_factory: EngineFactory = create_engine,
    ):
        """Initialise le repository de reset Bibliotheque.

        Args:
            configuration (DatabaseConfiguration): Configuration SQLAlchemy.
            engine (Engine | None): Moteur SQLAlchemy injectable en test.
            engine_factory (EngineFactory): Fabrique de moteur SQLAlchemy.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si aucune base de donnees n'est configuree.
        """

        configuration.validate()
        if not configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour reinitialiser la Bibliotheque.")
        self.configuration = configuration
        self.engine = engine or engine_factory(configuration.database_url)

    def clean_library_tables(self) -> None:
        """Vide les tables reconstruites par le reset Bibliotheque.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse une suppression.
        """

        schema_name = self.configuration.schema_name
        table_names = ("t_user_collection", "t_game", "t_studio", "t_platform")
        with self.engine.begin() as connection:
            for table_name in table_names:
                connection.execute(text(f'DELETE FROM "{schema_name}".{table_name}'))

    def list_importable_users(self) -> list[LibraryResetImportableUser]:
        """Liste les utilisateurs dont un fichier de collection est reference.

        Args:
            Aucun.

        Returns:
            list[LibraryResetImportableUser]: Utilisateurs ordonnes par date de creation.
        """

        schema_name = self.configuration.schema_name
        with self.engine.connect() as connection:
            rows = connection.execute(
                text(
                    f'SELECT id, email, collection_file_path, collection_file_description, '
                    f'profile, status, creation_date FROM "{schema_name}".t_user '
                    "WHERE collection_file_path IS NOT NULL "
                    "ORDER BY creation_date ASC, id ASC"
                )
            ).mappings().all()
        return [
            LibraryResetImportableUser(
                id=int(row["id"]),
                email=str(row["email"]),
                collection_file_path=str(row["collection_file_path"]),
                collection_file_description=row["collection_file_description"],
                profile=str(row["profile"]),
                status=str(row["status"]),
                creation_date=row["creation_date"],
            )
            for row in rows
        ]
