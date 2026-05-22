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
# Description : profils applicatifs et hierarchie d'acces des routes backend.

from enum import Enum


class UserProfile(str, Enum):
    """Enumere les profils applicatifs autorises.

    Attributes:
        USER (str): Profil standard attribue aux utilisateurs inscrits.
        ADMIN (str): Profil administrateur reserve aux identifiants configures.
    """

    USER = "USER"
    ADMIN = "ADMIN"

    @classmethod
    def normalize(cls, value: str | None) -> "UserProfile":
        """Normalise une valeur brute en profil applicatif.

        Args:
            value (str | None): Valeur issue de la base, du token ou du code appelant.

        Returns:
            UserProfile: Profil reconnu, ou `USER` par defaut.
        """

        normalized_value = str(value or cls.USER.value).strip().upper()
        try:
            return cls(normalized_value)
        except ValueError:
            return cls.USER

    @classmethod
    def can_access(
        cls,
        actual_profile: str | None,
        required_profiles: list[str] | tuple[str, ...],
    ) -> bool:
        """Verifie si un profil satisfait les profils exiges par une route.

        Args:
            actual_profile (str | None): Profil porte par le token courant.
            required_profiles (list[str] | tuple[str, ...]): Profils autorises par la route.

        Returns:
            bool: `True` si le profil courant est autorise.
        """

        actual = cls.normalize(actual_profile)
        allowed_values = {cls.normalize(profile).value for profile in required_profiles}
        if actual is cls.ADMIN:
            allowed_values.add(cls.ADMIN.value)
            allowed_values.add(cls.USER.value)
        return actual.value in allowed_values

    @classmethod
    def expand_hierarchy(cls, minimum_profile: str | None) -> list[str]:
        """Retourne les profils autorises pour un profil minimal.

        Args:
            minimum_profile (str | None): Profil minimal attendu par une route.

        Returns:
            list[str]: Profils autorises en tenant compte de la hierarchie.
        """

        profile = cls.normalize(minimum_profile)
        if profile is cls.USER:
            return [cls.USER.value, cls.ADMIN.value]
        return [cls.ADMIN.value]
