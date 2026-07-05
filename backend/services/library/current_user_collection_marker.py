#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-07-05
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : enrichissement des jeux avec le marqueur de collection utilisateur.

from typing import Any

from sqlalchemy.engine import Connection

from .current_user_collection_game_repository import CurrentUserCollectionGameRepository


class CurrentUserCollectionMarker:
    """Ajoute le marqueur de collection utilisateur aux jeux d'une page."""

    def __init__(self, game_repository: CurrentUserCollectionGameRepository):
        """Initialise le marqueur de collection utilisateur.

        Args:
            game_repository (CurrentUserCollectionGameRepository): Repository des jeux.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.game_repository = game_repository

    def mark_games(
        self,
        connection: Connection,
        rows: list[dict[str, Any]],
        current_user_id: int | None,
    ) -> None:
        """Ajoute le marqueur collection utilisateur aux jeux de la page.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            rows (list[dict[str, Any]]): Jeux de la page courante.
            current_user_id (int | None): Utilisateur connecte optionnel.

        Returns:
            None: Les lignes sont enrichies sur place.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

        for row in rows:
            row["in_current_user_collection"] = False
        if current_user_id is None or not rows:
            return
        page_game_ids = [int(row["id"]) for row in rows]
        owned_game_ids = self.game_repository.list_current_user_collection_game_ids(
            connection,
            current_user_id,
            page_game_ids,
        )
        for row in rows:
            row["in_current_user_collection"] = int(row["id"]) in owned_game_ids
