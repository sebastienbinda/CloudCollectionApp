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
from datetime import date, datetime
from typing import Any, Optional


class SheetValueFormatter:
    @staticmethod
    def clean_text(value: Any) -> Optional[str]:
        """Nettoie une valeur de formulaire en texte optionnel.

        Args:
            value (Any): Valeur brute issue du payload JSON.

        Returns:
            Optional[str]: Texte sans espaces en bordure, ou `None` si vide.
        """

        if value is None:
            return None
        if isinstance(value, float) and value != value:
            return None
        text = str(value).strip()
        if text.lower() in {"nan", "nat", "none", "null"}:
            return None
        if text.lower().startswith("err:"):
            return None
        return text or None

    @staticmethod
    def serialize(value: Any) -> Any:
        """Serialise une valeur issue du tableur pour JSON.

        Args:
            value (Any): Valeur pandas, Python native, date ou cellule vide.

        Returns:
            Any: Valeur compatible JSON, avec dates ISO et `NaN` converti en `None`.
        """

        if SheetValueFormatter.clean_text(value) is None:
            return None
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if hasattr(value, "item"):
            return value.item()
        return value

    @staticmethod
    def normalize_platform_name(value: str) -> str:
        """Normalise un nom de plateforme pour une comparaison souple.

        Args:
            value (str): Nom de plateforme brut.

        Returns:
            str: Nom en minuscules sans espaces.
        """

        return "".join(str(value).lower().split())
