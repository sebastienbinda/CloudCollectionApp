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
# Description : contrat de lecture des jeux presents dans la collection utilisateur.

from typing import Protocol

from sqlalchemy.engine import Connection


class CurrentUserCollectionGameRepository(Protocol):
    """Decrit la lecture des jeux presents dans la collection utilisateur."""

    def list_current_user_collection_game_ids(
        self,
        connection: Connection,
        user_id: int,
        game_ids: list[int],
    ) -> set[int]:
        """Liste les jeux de la page deja presents dans la collection utilisateur.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur connecte.
            game_ids (list[int]): Identifiants de jeux a verifier.

        Returns:
            set[int]: Identifiants en collection hors wishlist.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """

    def list_current_user_wishlist_game_ids(
        self,
        connection: Connection,
        user_id: int,
        game_ids: list[int],
    ) -> set[int]:
        """Liste les jeux de la page deja presents dans la liste de souhaits.

        Args:
            connection (Connection): Connexion SQL transactionnelle.
            user_id (int): Identifiant utilisateur connecte.
            game_ids (list[int]): Identifiants de jeux a verifier.

        Returns:
            set[int]: Identifiants en liste de souhaits.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse la requete.
        """
