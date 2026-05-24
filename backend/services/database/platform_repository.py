#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : repository SQL des plateformes de collection.

from sqlalchemy import text
from sqlalchemy.engine import Connection

from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer


class SqlAlchemyPlatformRepository:
    """Persiste les plateformes de collection dans `t_platform`."""

    UNKNOWN_STATUS = "UNKNOWN"

    def __init__(self, schema_name: str, name_normalizer: UserCollectionNameNormalizer):
        """Initialise le repository des plateformes.

        Args:
            schema_name (str): Nom du schema PostgreSQL.
            name_normalizer (UserCollectionNameNormalizer): Normaliseur metier.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name
        self.name_normalizer = name_normalizer

    def load_ids_by_key(self, connection: Connection) -> dict[str, int]:
        """Charge les plateformes existantes par cle de comparaison.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            dict[str, int]: Identifiants des plateformes.
        """

        return {
            self.name_normalizer.comparison_key(row["name"]): int(row["id"])
            for row in connection.execute(
                text(f'SELECT id, name FROM "{self.schema_name}".t_platform')
            ).mappings()
        }

    def insert(self, connection: Connection, platform_name: str) -> int:
        """Insere une plateforme avec le statut `UNKNOWN`.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_name (str): Nom de plateforme a creer.

        Returns:
            int: Identifiant genere.
        """

        return int(connection.execute(
            text(
                f'INSERT INTO "{self.schema_name}".t_platform (name, status) '
                "VALUES (:name, :status) RETURNING id"
            ),
            {"name": platform_name, "status": self.UNKNOWN_STATUS},
        ).scalar_one())
