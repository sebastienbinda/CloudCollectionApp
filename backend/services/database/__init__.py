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
"""Exports publics du domaine database."""

from .database_configuration import DatabaseConfiguration
from .database_model_base import DatabaseModelBase
from .database_schema_service import DatabaseSchemaService
from .game import Game
from .platform import Platform
from .schema_version import SchemaVersion
from .studio import Studio
from .user import User
from .user_collection import UserCollection

__all__ = [
    "DatabaseConfiguration",
    "DatabaseModelBase",
    "DatabaseSchemaService",
    "Game",
    "Platform",
    "SchemaVersion",
    "Studio",
    "User",
    "UserCollection",
]
