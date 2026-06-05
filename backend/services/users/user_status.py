#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-22
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : statuts fonctionnels des comptes utilisateurs.

from enum import Enum


class UserStatus(str, Enum):
    """Enumere les statuts fonctionnels autorises pour un compte utilisateur.

    Attributes:
        ACTIVE (str): Compte autorise a se connecter si l'email est verifie.
        WAITING_VALIDATION (str): Compte en attente de validation administrateur.
        LOCKED (str): Compte bloque, refuse par le flux d'authentification.
    """

    ACTIVE = "ACTIVE"
    WAITING_VALIDATION = "WAITING_VALIDATION"
    LOCKED = "LOCKED"

    @classmethod
    def normalize(cls, value: str | None) -> "UserStatus":
        """Normalise une valeur brute en statut utilisateur.

        Args:
            value (str | None): Valeur brute a convertir.

        Returns:
            UserStatus: Statut reconnu, ou `ACTIVE` par defaut.
        """

        normalized_value = str(value or cls.ACTIVE.value).strip().upper()
        try:
            return cls(normalized_value)
        except ValueError:
            return cls.ACTIVE
