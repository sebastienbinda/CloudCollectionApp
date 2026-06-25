#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-25
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Exports publics du domaine collection utilisateur."""

from .collection_share_management_service import CollectionShareManagementService
from .collection_share_not_found_error import CollectionShareNotFoundError
from .collection_share_owner_not_found_error import CollectionShareOwnerNotFoundError
from .guest_collection_access_policy import CollectionAccessContext, GuestCollectionAccessPolicy
from .user_collection_query_contract import (
    UserCollectionGameQueryCriteria,
    UserCollectionPlatformQueryCriteria,
    UserCollectionQueryParser,
)

__all__ = [
    "CollectionShareManagementService",
    "CollectionShareNotFoundError",
    "CollectionShareOwnerNotFoundError",
    "UserCollectionGameQueryCriteria",
    "UserCollectionPlatformQueryCriteria",
    "UserCollectionQueryParser",
]
