#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
from dataclasses import dataclass


@dataclass
class Film:
    """Represente un film simple expose par l'API d'exemple.

    Attributes:
        id (int): Identifiant unique du film.
        name (str): Nom lisible du film.
    """

    id: int
    name: str

    def to_dict(self) -> dict[str, object]:
        """Convertit le film en dictionnaire serialisable en JSON.

        Args:
            Aucun.

        Returns:
            dict[str, int | str]: Dictionnaire contenant `id` et `name`.
        """

        return {"id": self.id, "name": self.name}
