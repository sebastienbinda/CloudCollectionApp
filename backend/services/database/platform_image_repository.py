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

from services.library.library_query_contract import LibraryPageRequest, LibrarySortRule


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

    def count_moderation_images(
        self,
        connection: Connection,
        status: str,
        platform_filter: str,
    ) -> int:
        """Compte les images correspondant aux filtres de moderation.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            status (str): Statut filtre, ou chaine vide.
            platform_filter (str): Filtre nom de plateforme, ou chaine vide.

        Returns:
            int: Nombre d'images filtrees.
        """

        where_sql, parameters = self._moderation_where_clause(status, platform_filter)
        count = connection.execute(
            text(
                "SELECT COUNT(*) "
                f'FROM "{self.schema_name}".t_platform_image image '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = image.platform '
                f'JOIN "{self.schema_name}".t_user app_user ON app_user.id = image.user_id '
                f"{where_sql}"
            ),
            parameters,
        ).scalar_one()
        return int(count)

    def list_moderation_images(
        self,
        connection: Connection,
        status: str,
        platform_filter: str,
        page_request: LibraryPageRequest,
        sort_rules: tuple[LibrarySortRule, ...],
    ) -> list[dict[str, object]]:
        """Liste les images candidates a la moderation administrateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            status (str): Statut filtre, ou chaine vide.
            platform_filter (str): Filtre nom de plateforme, ou chaine vide.
            page_request (LibraryPageRequest): Pagination normalisee.
            sort_rules (tuple[LibrarySortRule, ...]): Tri normalise.

        Returns:
            list[dict[str, object]]: Images de moderation.
        """

        where_sql, parameters = self._moderation_where_clause(status, platform_filter)
        parameters.update({"limit": page_request.size, "offset": page_request.offset})
        rows = connection.execute(
            text(
                "SELECT image.id, image.platform, platform.name AS platform_name, "
                "image.path, image.type, image.status, image.user_id, "
                "app_user.email AS user_email, image.creation_date "
                f'FROM "{self.schema_name}".t_platform_image image '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = image.platform '
                f'JOIN "{self.schema_name}".t_user app_user ON app_user.id = image.user_id '
                f"{where_sql} "
                f"{self._order_by_clause(sort_rules)} "
                "LIMIT :limit OFFSET :offset"
            ),
            parameters,
        ).mappings().all()
        return [dict(row) for row in rows]

    def find_image(
        self,
        connection: Connection,
        platform_id: int,
        image_id: int,
    ) -> dict[str, object] | None:
        """Retourne une image associee a une plateforme.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.

        Returns:
            dict[str, object] | None: Image trouvee ou absence.
        """

        row = connection.execute(
            text(
                "SELECT id, platform, path, type, status, user_id, creation_date "
                f'FROM "{self.schema_name}".t_platform_image '
                "WHERE platform = :platform_id AND id = :image_id"
            ),
            {"platform_id": platform_id, "image_id": image_id},
        ).mappings().first()
        return dict(row) if row else None

    def update_image_status(
        self,
        connection: Connection,
        platform_id: int,
        image_id: int,
        status: str,
    ) -> dict[str, object] | None:
        """Modifie le statut d'une image.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.
            status (str): Nouveau statut stocke.

        Returns:
            dict[str, object] | None: Image modifiee ou absence.
        """

        row = connection.execute(
            text(
                f'UPDATE "{self.schema_name}".t_platform_image '
                "SET status = :status "
                "WHERE platform = :platform_id AND id = :image_id "
                "RETURNING id, platform, path, type, status, user_id, creation_date"
            ),
            {"platform_id": platform_id, "image_id": image_id, "status": status},
        ).mappings().first()
        return dict(row) if row else None

    def delete_image(self, connection: Connection, platform_id: int, image_id: int) -> bool:
        """Supprime une image de la base.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.

        Returns:
            bool: `True` si une ligne a ete supprimee.
        """

        result = connection.execute(
            text(
                f'DELETE FROM "{self.schema_name}".t_platform_image '
                "WHERE platform = :platform_id AND id = :image_id"
            ),
            {"platform_id": platform_id, "image_id": image_id},
        )
        return result.rowcount > 0

    def set_image_type(
        self,
        connection: Connection,
        platform_id: int,
        image_id: int,
        image_type: str,
    ) -> dict[str, object] | None:
        """Modifie le type d'une image.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.
            image_type (str): Nouveau type stocke.

        Returns:
            dict[str, object] | None: Image modifiee ou absence.
        """

        if image_type == "MAIN":
            connection.execute(
                text(
                    f'UPDATE "{self.schema_name}".t_platform_image '
                    "SET type = 'OTHER' "
                    "WHERE platform = :platform_id AND id <> :image_id AND type = 'MAIN'"
                ),
                {"platform_id": platform_id, "image_id": image_id},
            )
        row = connection.execute(
            text(
                f'UPDATE "{self.schema_name}".t_platform_image '
                "SET type = :image_type "
                "WHERE platform = :platform_id AND id = :image_id "
                "RETURNING id, platform, path, type, status, user_id, creation_date"
            ),
            {
                "platform_id": platform_id,
                "image_id": image_id,
                "image_type": image_type,
            },
        ).mappings().first()
        return dict(row) if row else None

    def _moderation_where_clause(
        self,
        status: str,
        platform_filter: str,
    ) -> tuple[str, dict[str, object]]:
        where_clauses = []
        parameters: dict[str, object] = {}
        if status:
            where_clauses.append("image.status = :status")
            parameters["status"] = status
        if platform_filter:
            where_clauses.append("LOWER(platform.name) LIKE :platform_filter")
            parameters["platform_filter"] = f"%{platform_filter.lower()}%"
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        return where_sql, parameters

    def _order_by_clause(self, sort_rules: tuple[LibrarySortRule, ...]) -> str:
        allowed_columns = {
            "creation_date": "image.creation_date",
            "platform": "platform.name",
            "status": "image.status",
            "type": "image.type",
        }
        clauses = []
        for sort_rule in sort_rules:
            column_sql = allowed_columns.get(sort_rule.column, "image.creation_date")
            direction = "DESC" if sort_rule.direction == "desc" else "ASC"
            clauses.append(f"{column_sql} {direction}")
        clauses.append("image.id DESC")
        return "ORDER BY " + ", ".join(clauses)
