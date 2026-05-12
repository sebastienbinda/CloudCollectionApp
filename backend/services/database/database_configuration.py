#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-12
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : configuration de connexion et de schema pour la base PostgreSQL.

import os
import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DatabaseConfiguration:
    """Decrit la configuration backend necessaire a l'initialisation SQL.

    La configuration reste volontairement minimale : l'URL de connexion, le
    schema PostgreSQL cible et la version applicative a inscrire dans la table
    `t_schema_version`.

    Attributes:
        database_url (Optional[str]): URL SQLAlchemy de connexion a PostgreSQL.
        schema_name (str): Nom du schema PostgreSQL gere par l'application.
        application_version (str): Version applicative inscrite dans
            `t_schema_version`.
    """

    database_url: Optional[str]
    schema_name: str
    application_version: str

    DEFAULT_SCHEMA_NAME = "cloudcollectionapp"
    DEFAULT_APPLICATION_VERSION = "0.1"
    SCHEMA_NAME_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")
    MAX_APPLICATION_VERSION_LENGTH = 5

    @classmethod
    def from_environment(cls) -> "DatabaseConfiguration":
        """Construit la configuration depuis les variables d'environnement.

        Args:
            Aucun.

        Returns:
            DatabaseConfiguration: Configuration lue depuis l'environnement.

        Raises:
            ValueError: Si `DB_SCHEMA_NAME` ou `APP_VERSION` est invalide.
        """

        configuration = cls(
            database_url=cls._normalize_database_url(os.getenv("DATABASE_URL") or None),
            schema_name=os.getenv("DB_SCHEMA_NAME", cls.DEFAULT_SCHEMA_NAME),
            application_version=os.getenv("APP_VERSION", cls.DEFAULT_APPLICATION_VERSION),
        )
        configuration.validate()
        return configuration

    def is_database_enabled(self) -> bool:
        """Indique si une URL de base de donnees est configuree.

        Args:
            Aucun.

        Returns:
            bool: `True` si `DATABASE_URL` contient une valeur exploitable.
        """

        return bool(self.database_url)

    def validate(self) -> None:
        """Valide les valeurs de configuration sensibles.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si le nom du schema ou la version applicative est invalide.
        """

        if not self.SCHEMA_NAME_PATTERN.match(self.schema_name):
            raise ValueError(
                "DB_SCHEMA_NAME doit commencer par une lettre minuscule ou '_' et ne contenir "
                "que des lettres minuscules, chiffres ou '_'."
            )
        if self.schema_name.lower().startswith("pg_"):
            raise ValueError("DB_SCHEMA_NAME ne doit pas utiliser le prefixe reserve 'pg_'.")
        if len(self.application_version) > self.MAX_APPLICATION_VERSION_LENGTH:
            raise ValueError("APP_VERSION ne doit pas depasser 5 caracteres.")

    @classmethod
    def _normalize_database_url(cls, database_url: Optional[str]) -> Optional[str]:
        """Adapte l'URL PostgreSQL Docker au driver SQLAlchemy installe.

        Args:
            database_url (Optional[str]): URL brute lue depuis `DATABASE_URL`.

        Returns:
            Optional[str]: URL compatible avec le driver `psycopg` v3.
        """

        if database_url and database_url.startswith("postgresql://"):
            return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return database_url
