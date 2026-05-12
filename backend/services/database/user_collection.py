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
# Description : modele ORM des jeux rattaches aux utilisateurs.

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .database_model_base import DatabaseModelBase


class UserCollection(DatabaseModelBase):
    """Represente l'association entre un utilisateur et un jeu possede.

    Attributes:
        user_id (int): Identifiant de l'utilisateur proprietaire de l'entree.
        game_id (int): Identifiant du jeu rattache a la collection.
        game_additional_name (Optional[str]): Nom complementaire du jeu dans la
            collection utilisateur.
    """

    __tablename__ = "t_user_collection"

    user_id: Mapped[int] = mapped_column(ForeignKey("t_user.id"), primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("t_game.id"), primary_key=True)
    game_additional_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
