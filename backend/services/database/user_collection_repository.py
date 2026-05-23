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
# Description : repository SQL des associations utilisateur-collection.

from sqlalchemy import text
from sqlalchemy.engine import Connection


class SqlAlchemyUserCollectionRepository:
    """Persiste les associations de jeux dans `t_user_collection`."""

    def __init__(self, schema_name: str):
        """Initialise le repository d'association utilisateur-collection.

        Args:
            schema_name (str): Nom du schema PostgreSQL.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name

    def ensure_user_game_associations(
        self,
        connection: Connection,
        user_id: int,
        game_ids: list[int],
    ) -> int:
        """Cree les associations utilisateur-jeu manquantes.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur.
            game_ids (list[int]): Jeux a rattacher.

        Returns:
            int: Nombre de jeux associes apres import.
        """

        existing_game_ids = {
            int(row["game_id"])
            for row in connection.execute(
                text(
                    f'SELECT game_id FROM "{self.schema_name}".t_user_collection '
                    "WHERE user_id = :user_id"
                ),
                {"user_id": user_id},
            ).mappings()
        }
        for game_id in game_ids:
            if game_id in existing_game_ids:
                continue
            connection.execute(
                text(
                    f'INSERT INTO "{self.schema_name}".t_user_collection '
                    "(user_id, game_id, game_additional_name) VALUES (:user_id, :game_id, NULL)"
                ),
                {"user_id": user_id, "game_id": game_id},
            )
            existing_game_ids.add(game_id)
        return len(game_ids)
