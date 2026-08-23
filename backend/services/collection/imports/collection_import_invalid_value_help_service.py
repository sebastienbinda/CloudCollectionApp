#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : aide a la correction des valeurs d'import refusees.

from dataclasses import dataclass

from .collection_private_information_contract import (
    ALLOWED_REGIONS,
    BOOLEAN_FALSE_LABELS,
    BOOLEAN_TRUE_LABELS,
    CONDITION_LABELS_BY_VALUE,
    REGION_ALIASES_BY_VALUE,
)


@dataclass(frozen=True)
class CollectionImportInvalidValueHelp:
    """Decrit pourquoi une valeur importee a ete refusee.

    Attributes:
        field (str): Nom technique du champ refuse.
        value (str): Valeur importee refusee.
        reason (str): Explication lisible du refus.
        possible_values (list[str]): Valeurs acceptees ou exemples utiles.
    """

    field: str
    value: str
    reason: str
    possible_values: list[str]

    def to_dict(self) -> dict[str, object]:
        """Convertit l'aide en dictionnaire serialisable.

        Args:
            Aucun.

        Returns:
            dict[str, object]: Aide exploitable par l'IHM.
        """

        return {
            "field": self.field,
            "value": self.value,
            "reason": self.reason,
            "possible_values": list(self.possible_values),
        }


class CollectionImportInvalidValueHelpService:
    """Construit les aides de correction pour les valeurs d'import refusees."""

    FIELD_HELPS = {
        "release_date": {
            "reason": "La date ne respecte pas un format reconnu ou est trop ancienne.",
            "possible_values": ["1994", "1994-11-24", "24/11/1994"],
        },
        "buy_date": {
            "reason": "La date d'achat ne respecte pas un format reconnu.",
            "possible_values": ["2024-03-15", "15/03/2024"],
        },
        "purchase_price": {
            "reason": "Le prix doit etre un nombre positif avec au plus deux decimales utiles.",
            "possible_values": ["12", "12,50", "12.50"],
        },
        "grade": {
            "reason": "La note doit etre numerique et compatible avec la base de notation choisie.",
            "possible_values": ["8", "8/10", "82/100"],
        },
        "condition": {
            "reason": "La valeur ne correspond pas a un etat physique reconnu.",
            "possible_values": [],
        },
        "region": {
            "reason": "La valeur ne correspond pas a une region ou version reconnue.",
            "possible_values": [],
        },
        "has_manual": {
            "reason": "La valeur ne correspond pas a une reponse oui/non reconnue.",
            "possible_values": [],
        },
        "is_collector": {
            "reason": "La valeur ne correspond pas a une reponse oui/non reconnue.",
            "possible_values": [],
        },
        "has_steelbook": {
            "reason": "La valeur ne correspond pas a une reponse oui/non reconnue.",
            "possible_values": [],
        },
        "is_digital": {
            "reason": "La valeur ne correspond pas a une reponse oui/non reconnue.",
            "possible_values": [],
        },
    }

    BOOLEAN_FIELDS = frozenset({"has_manual", "is_collector", "has_steelbook", "is_digital"})

    def get_help(self, field: str, value: str) -> CollectionImportInvalidValueHelp:
        """Retourne l'aide de correction d'une valeur refusee.

        Args:
            field (str): Nom technique du champ refuse.
            value (str): Valeur refusee telle qu'affichee dans le resume.

        Returns:
            CollectionImportInvalidValueHelp: Aide de correction.
        """

        normalized_field = str(field or "").strip()
        normalized_value = str(value or "").strip()
        field_help = self.FIELD_HELPS.get(normalized_field)
        if field_help is None:
            return CollectionImportInvalidValueHelp(
                normalized_field,
                normalized_value,
                "La valeur ne correspond pas au format attendu pour ce champ.",
                [],
            )
        return CollectionImportInvalidValueHelp(
            normalized_field,
            normalized_value,
            str(field_help["reason"]),
            self._possible_values(normalized_field, field_help),
        )

    def _possible_values(self, field: str, field_help: dict[str, object]) -> list[str]:
        if field == "region":
            aliases = [
                alias
                for aliases_for_region in REGION_ALIASES_BY_VALUE.values()
                for alias in aliases_for_region
            ]
            return sorted(ALLOWED_REGIONS) + sorted(aliases)
        if field == "condition":
            values = [
                label
                for labels in CONDITION_LABELS_BY_VALUE.values()
                for label in labels
            ]
            return sorted(values)
        if field in self.BOOLEAN_FIELDS:
            return sorted(BOOLEAN_TRUE_LABELS) + sorted(BOOLEAN_FALSE_LABELS)
        return list(field_help.get("possible_values") or [])
