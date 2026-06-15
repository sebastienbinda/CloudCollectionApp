#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-15
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : resultat serialisable d'un import de collection utilisateur.

from dataclasses import dataclass


@dataclass(frozen=True)
class UserCollectionImportResult:
    """Regroupe les compteurs retournes apres un import reussi.

    Attributes:
        linked_platforms (int): Nombre de plateformes du referentiel liees.
        created_studios (int): Nombre de studios crees.
        created_games (int): Nombre de jeux crees.
        associated_games (int): Nombre de jeux associes a l'utilisateur.
        wishlisted_games (int): Nombre de jeux importes comme souhaits.
        warnings (dict): Avertissements fonctionnels de l'import.
    """

    linked_platforms: int
    created_studios: int
    created_games: int
    associated_games: int
    wishlisted_games: int = 0
    warnings: dict | None = None

    def to_dict(self) -> dict[str, int | dict]:
        """Convertit le resultat en dictionnaire serialisable.

        Args:
            Aucun.

        Returns:
            dict[str, int | dict]: Compteurs et warnings d'import.
        """

        return {
            "linked_platforms": self.linked_platforms,
            "created_studios": self.created_studios,
            "created_games": self.created_games,
            "associated_games": self.associated_games,
            "wishlisted_games": self.wishlisted_games,
            "warnings": self.warnings or {
                "invalid_wishlist": 0,
                "invalid_wishlist_values_found": [],
                "invalid_games": [],
                "platform_mappings": [],
                "platform_matches": [],
                "skipped_games": [],
                "total_import_duration_seconds": 0.0,
            },
        }
