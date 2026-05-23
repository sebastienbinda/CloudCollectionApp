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
# Description : modele ORM de version applicative du schema SQL.

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .database_model_base import DatabaseModelBase


class SchemaVersion(DatabaseModelBase):
    """Represente la version applicative inscrite apres initialisation SQL.

    Attributes:
        version (str): Version applicative courante, limitee a cinq caracteres.
        date_creation (datetime): Date de premiere creation du schema SQL.
        update_date (Optional[datetime]): Date de derniere mise a jour de la
            version applicative, absente lors de la premiere creation.
    """

    __tablename__ = "t_schema_version"

    version: Mapped[str] = mapped_column(String(5), primary_key=True)
    date_creation: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    update_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
