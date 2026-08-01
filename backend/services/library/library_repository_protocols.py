#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-01
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : protocoles des repositories de consultation Bibliotheque.

from typing import Any, Protocol

from sqlalchemy.engine import Connection

from .library_query_contract import LibraryQueryCriteria


class PublicLibraryPlatformRepository(Protocol):
    """Decrit les lectures publiques attendues pour les plateformes."""

    def count_public_library_platforms(self, connection: Connection) -> int:
        """Compte les plateformes globales."""

    def count_public_library_platforms_by_criteria(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> int:
        """Compte les plateformes correspondant aux criteres."""

    def list_public_library_platforms(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> list[dict[str, Any]]:
        """Liste les plateformes correspondant aux criteres."""

    def find_public_library_platform(
        self,
        connection: Connection,
        platform_id: int,
    ) -> dict[str, Any] | None:
        """Retourne une plateforme correspondant a l'identifiant."""


class PublicLibraryPlatformImageRepository(Protocol):
    """Decrit les lectures publiques attendues pour les images de plateformes."""

    def list_accepted_images(
        self,
        connection: Connection,
        platform_id: int,
    ) -> list[dict[str, Any]]:
        """Liste les images acceptees d'une plateforme."""


class PublicLibraryStudioRepository(Protocol):
    """Decrit les lectures publiques attendues pour les studios."""

    def count_public_library_studios(self, connection: Connection) -> int:
        """Compte les studios globaux."""

    def count_public_library_studios_by_criteria(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> int:
        """Compte les studios correspondant aux criteres."""

    def list_public_library_studios(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> list[dict[str, Any]]:
        """Liste les studios correspondant aux criteres."""


class PublicLibraryGameRepository(Protocol):
    """Decrit les lectures publiques attendues pour les jeux."""

    def count_public_library_games(
        self,
        connection: Connection,
        include_waiting_validation: bool = False,
    ) -> int:
        """Compte les jeux globaux."""

    def count_public_library_games_by_criteria(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> int:
        """Compte les jeux correspondant aux criteres."""

    def list_public_library_games(
        self,
        connection: Connection,
        criteria: LibraryQueryCriteria,
    ) -> list[dict[str, Any]]:
        """Liste les jeux correspondant aux criteres."""

    def list_current_user_collection_game_ids(
        self,
        connection: Connection,
        user_id: int,
        game_ids: list[int],
    ) -> set[int]:
        """Liste les jeux presents dans la collection utilisateur."""

    def list_current_user_wishlist_game_ids(
        self,
        connection: Connection,
        user_id: int,
        game_ids: list[int],
    ) -> set[int]:
        """Liste les jeux presents dans la liste de souhaits utilisateur."""

    def find_public_library_game(
        self,
        connection: Connection,
        game_id: int,
        include_waiting_validation: bool = False,
        current_user_id: int | None = None,
    ) -> dict[str, Any] | None:
        """Retourne un jeu correspondant a l'identifiant."""
