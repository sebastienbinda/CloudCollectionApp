#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-19
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : repository SQL des images de plateformes.

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.engine import Connection


class SqlAlchemyPlatformImageRepository:
    """Persiste et lit les images associees aux plateformes."""

    def __init__(self, schema_name: str):
        """Initialise le repository d'images de plateformes.

        Args:
            schema_name (str): Nom du schema PostgreSQL.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name

    def platform_exists(self, connection: Connection, platform_id: int) -> bool:
        """Indique si une plateforme existe.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_id (int): Identifiant de plateforme.

        Returns:
            bool: `True` si la plateforme existe.
        """

        count = connection.execute(
            text(f'SELECT COUNT(*) FROM "{self.schema_name}".t_platform WHERE id = :platform_id'),
            {"platform_id": platform_id},
        ).scalar_one()
        return int(count) > 0

    def find_platform_name(self, connection: Connection, platform_id: int) -> str | None:
        """Retourne le nom d'une plateforme.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_id (int): Identifiant de plateforme.

        Returns:
            str | None: Nom de plateforme ou absence.
        """

        value = connection.execute(
            text(f'SELECT name FROM "{self.schema_name}".t_platform WHERE id = :platform_id'),
            {"platform_id": platform_id},
        ).scalar_one_or_none()
        return str(value) if value is not None else None

    def create_waiting_image(
        self,
        connection: Connection,
        platform_id: int,
        path: str,
        user_id: int,
        creation_date: datetime,
    ) -> dict[str, object]:
        """Insere une image en attente de validation.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_id (int): Identifiant de plateforme.
            path (str): Chemin absolu du fichier stocke.
            user_id (int): Identifiant utilisateur issu du token.
            creation_date (datetime): Date de creation de l'image.

        Returns:
            dict[str, object]: Ligne inseree.
        """

        row = connection.execute(
            text(
                f'INSERT INTO "{self.schema_name}".t_platform_image '
                "(platform, path, type, status, user_id, creation_date) "
                "VALUES (:platform, :path, 'OTHER', 'WAITING_VALIDATION', "
                ":user_id, :creation_date) "
                "RETURNING id, platform, path, type, status, user_id, creation_date"
            ),
            {
                "platform": platform_id,
                "path": path,
                "user_id": user_id,
                "creation_date": creation_date,
            },
        ).mappings().one()
        return dict(row)

    def list_accepted_images(
        self,
        connection: Connection,
        platform_id: int,
    ) -> list[dict[str, object]]:
        """Liste les images acceptees d'une plateforme.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_id (int): Identifiant de plateforme.

        Returns:
            list[dict[str, object]]: Images acceptees triees par type puis creation.
        """

        rows = connection.execute(
            text(
                "SELECT id, platform, path, type, status, user_id, creation_date "
                f'FROM "{self.schema_name}".t_platform_image '
                "WHERE platform = :platform_id AND status = 'ACCEPTED' "
                "ORDER BY CASE WHEN type = 'MAIN' THEN 0 ELSE 1 END, creation_date, id"
            ),
            {"platform_id": platform_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def find_accepted_image(
        self,
        connection: Connection,
        platform_id: int,
        image_id: int,
    ) -> dict[str, object] | None:
        """Retourne une image acceptee precise.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.

        Returns:
            dict[str, object] | None: Image acceptee ou absence.
        """

        row = connection.execute(
            text(
                "SELECT id, platform, path, type, status, user_id, creation_date "
                f'FROM "{self.schema_name}".t_platform_image '
                "WHERE platform = :platform_id AND id = :image_id AND status = 'ACCEPTED'"
            ),
            {"platform_id": platform_id, "image_id": image_id},
        ).mappings().first()
        return dict(row) if row else None
