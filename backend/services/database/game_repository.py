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
# Description : repository SQL des jeux de collection.

from sqlalchemy import text
from sqlalchemy.engine import Connection

from services.ods import OdsCollectionImportGame
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer


class SqlAlchemyGameRepository:
    """Persiste les jeux de collection dans `t_game`."""

    def __init__(self, schema_name: str, name_normalizer: UserCollectionNameNormalizer):
        """Initialise le repository des jeux.

        Args:
            schema_name (str): Nom du schema PostgreSQL.
            name_normalizer (UserCollectionNameNormalizer): Normaliseur metier.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.schema_name = schema_name
        self.name_normalizer = name_normalizer

    def load_ids_by_key(self, connection: Connection) -> dict[tuple[str, str], int]:
        """Charge les jeux existants par cle plateforme/nom.

        Args:
            connection (Connection): Connexion SQL transactionnelle.

        Returns:
            dict[tuple[str, str], int]: Identifiants des jeux.
        """

        rows = connection.execute(
            text(
                f'SELECT game.id, game.name, platform.name AS platform_name '
                f'FROM "{self.schema_name}".t_game game '
                f'JOIN "{self.schema_name}".t_platform platform ON platform.id = game.platform'
            )
        ).mappings()
        return {
            (
                self.name_normalizer.comparison_key(row["platform_name"]),
                self.name_normalizer.comparison_key(row["name"]),
            ): int(row["id"])
            for row in rows
        }

    def insert(
        self,
        connection: Connection,
        game: OdsCollectionImportGame,
        platform_id: int,
        studio_id: int | None,
    ) -> int:
        """Insere un jeu absent.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            game (OdsCollectionImportGame): Jeu a creer.
            platform_id (int): Identifiant de plateforme.
            studio_id (int | None): Identifiant du studio developpeur.

        Returns:
            int: Identifiant genere.
        """

        return int(connection.execute(
            text(
                f'INSERT INTO "{self.schema_name}".t_game '
                "(name, release_date, developper, editor, platform, description) "
                "VALUES (:name, :release_date, :developper, NULL, :platform, NULL) RETURNING id"
            ),
            {
                "name": game.name,
                "release_date": game.release_date,
                "developper": studio_id,
                "platform": platform_id,
            },
        ).scalar_one())

    def game_key(self, game: OdsCollectionImportGame) -> tuple[str, str]:
        """Construit la cle fonctionnelle d'un jeu.

        Args:
            game (OdsCollectionImportGame): Jeu importe.

        Returns:
            tuple[str, str]: Cle plateforme/nom.
        """

        return (
            self.name_normalizer.comparison_key(game.platform_name),
            self.name_normalizer.comparison_key(game.name),
        )
