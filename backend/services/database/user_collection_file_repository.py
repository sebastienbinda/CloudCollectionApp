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
# Description : repository SQL du chemin de collection utilisateur.

from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Connection


class UserCollectionAlreadyImportedError(Exception):
    """Signale qu'un utilisateur possede deja un fichier de collection."""


class UserCollectionImportUserNotFoundError(Exception):
    """Signale que l'utilisateur cible de l'import n'existe pas."""


class SqlAlchemyUserCollectionFileRepository:
    """Persiste le chemin de fichier de collection dans `t_user`."""

    def __init__(self, schema_name: str):
        """Initialise le repository du fichier de collection utilisateur.

        Args:
            schema_name (str): Nom du schema PostgreSQL.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name

    def user_has_collection(self, connection: Connection, user_id: int) -> bool:
        """Indique si l'utilisateur possede deja un fichier de collection.

        Args:
            connection (Connection): Connexion SQL.
            user_id (int): Identifiant technique de l'utilisateur.

        Returns:
            bool: `True` si `collection_file_path` est deja renseigne.
        """

        collection_file_path = connection.execute(
            text(
                f'SELECT collection_file_path FROM "{self.schema_name}".t_user '
                "WHERE id = :user_id"
            ),
            {"user_id": user_id},
        ).scalar_one_or_none()
        return bool(collection_file_path)

    def lock_user_without_collection(self, connection: Connection, user_id: int) -> None:
        """Verrouille l'utilisateur et verifie l'absence de collection.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            UserCollectionAlreadyImportedError: Si une collection existe deja.
            UserCollectionImportUserNotFoundError: Si l'utilisateur est absent.
        """

        row = connection.execute(
            text(
                f'SELECT collection_file_path FROM "{self.schema_name}".t_user '
                "WHERE id = :user_id FOR UPDATE"
            ),
            {"user_id": user_id},
        ).mappings().first()
        if not row:
            raise UserCollectionImportUserNotFoundError("Utilisateur introuvable.")
        if row["collection_file_path"]:
            raise UserCollectionAlreadyImportedError("Collection deja importee.")

    def update_collection_file(
        self,
        connection: Connection,
        user_id: int,
        collection_file_path: str,
        collection_file_description: dict,
    ) -> None:
        """Renseigne le fichier et sa description en fin de transaction.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.
            collection_file_path (str): Chemin final du fichier.
            collection_file_description (dict): Description JSON valide du fichier.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        connection.execute(
            text(
                f'UPDATE "{self.schema_name}".t_user '
                "SET collection_file_path = :collection_file_path, "
                "collection_file_description = :collection_file_description "
                "WHERE id = :user_id"
            ).bindparams(bindparam("collection_file_description", type_=JSONB)),
            {
                "user_id": user_id,
                "collection_file_path": collection_file_path,
                "collection_file_description": collection_file_description,
            },
        )

    def update_collection_file_path(
        self,
        connection: Connection,
        user_id: int,
        collection_file_path: str,
    ) -> None:
        """Renseigne seulement le chemin de collection utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.
            collection_file_path (str): Chemin final du fichier.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.update_collection_file(connection, user_id, collection_file_path, {})
