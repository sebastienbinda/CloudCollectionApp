#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-07-15
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : configuration des seuils de matching des studios.

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class StudioMatchingConfiguration:
    """Configure les seuils de matching des studios importes.

    Attributes:
        low_level_rating (int): Score minimal informatif coherent avec les plateformes.
        high_level_rating (int): Score minimal de rattachement automatique.
    """

    low_level_rating: int = 25
    high_level_rating: int = 87

    @classmethod
    def from_environment(cls) -> "StudioMatchingConfiguration":
        """Construit la configuration depuis les variables d'environnement.

        Args:
            Aucun.

        Returns:
            StudioMatchingConfiguration: Configuration validee.

        Raises:
            ValueError: Si une variable de seuil est invalide.
        """

        configuration = cls(
            low_level_rating=cls._parse_rating("STUDIO_MATCHING_LOW_LVL_RATING", 25),
            high_level_rating=cls._parse_rating("STUDIO_MATCHING_HIGH_LEVEL_RATING", 87),
        )
        configuration.validate()
        return configuration

    def validate(self) -> None:
        """Valide les bornes et l'ordre des seuils.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si les seuils sont incoherents.
        """

        if not 0 <= self.low_level_rating <= 100:
            raise ValueError("STUDIO_MATCHING_LOW_LVL_RATING doit etre entre 0 et 100.")
        if not 0 <= self.high_level_rating <= 100:
            raise ValueError("STUDIO_MATCHING_HIGH_LEVEL_RATING doit etre entre 0 et 100.")
        if self.low_level_rating >= self.high_level_rating:
            raise ValueError(
                "STUDIO_MATCHING_LOW_LVL_RATING doit etre strictement inferieur a "
                "STUDIO_MATCHING_HIGH_LEVEL_RATING."
            )

    @staticmethod
    def _parse_rating(environment_key: str, default_value: int) -> int:
        raw_value = os.getenv(environment_key, str(default_value)).strip()
        try:
            return int(raw_value)
        except ValueError as exc:
            raise ValueError(f"{environment_key} doit etre numerique.") from exc
