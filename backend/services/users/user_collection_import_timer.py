#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-07-21
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : utilitaire de mesure des durees d'import utilisateur.

from time import perf_counter


class UserCollectionImportTimer:
    """Centralise le formatage des durees mesurees pendant l'import."""

    @staticmethod
    def elapsed_seconds(started_at: float) -> float:
        """Calcule une duree positive arrondie en secondes.

        Args:
            started_at (float): Valeur initiale retournee par `perf_counter`.

        Returns:
            float: Duree positive arrondie a trois decimales.
        """

        return round(max(0.0, perf_counter() - started_at), 3)
