#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-06
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : classe objet de validation des champs de jeu de liste de souhaits.

from datetime import datetime
from typing import Any

from services.formatting import SheetValueFormatter


class WishlistPayloadValidator:
    """Valide et normalise les champs d'un jeu de liste de souhaits."""

    required_fields = ["Nom du jeu", "Console", "Studio"]

    def validate_add_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Valide les donnees d'ajout d'un jeu wishlist.

        Args:
            payload (dict[str, Any]): Donnees wishlist brutes envoyees par le frontend.

        Returns:
            dict[str, Any]: Donnees nettoyees et pretes a ecrire dans l'ODS.
        """

        return self.validate_update_payload(payload)

    def validate_update_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Valide les donnees de modification d'un jeu wishlist.

        Args:
            payload (dict[str, Any]): Donnees wishlist brutes envoyees par le frontend.

        Returns:
            dict[str, Any]: Donnees nettoyees et pretes a ecrire dans l'ODS.
        """

        cleaned_payload = {
            "Nom du jeu": self._clean_text(payload.get("Nom du jeu")),
            "Console": self._clean_text(payload.get("Console") or payload.get("Plateforme")),
            "Studio": self._clean_text(payload.get("Studio")),
            "Date de sortie": self._clean_text(payload.get("Date de sortie")),
            "Date d'achat": self._clean_text(payload.get("Date d'achat")),
            "Lieu d'achat": self._clean_text(payload.get("Lieu d'achat")),
            "Prix d'achat": self._clean_text(payload.get("Prix d'achat") or payload.get("Prix")),
        }
        self._validate_required_fields(cleaned_payload)
        self._validate_optional_date(cleaned_payload, "Date de sortie")
        self._validate_optional_date(cleaned_payload, "Date d'achat")
        self._validate_optional_price(cleaned_payload["Prix d'achat"])
        return cleaned_payload

    def _validate_required_fields(self, payload: dict[str, Any]) -> None:
        """Valide les champs obligatoires non vides.

        Args:
            payload (dict[str, Any]): Donnees nettoyees du jeu wishlist.

        Returns:
            None: Une exception est levee si un champ obligatoire manque.
        """

        for field_name in self.required_fields:
            if payload.get(field_name) == "":
                if field_name == "Console":
                    raise ValueError("Plateforme est obligatoire.")
                raise ValueError(f"{field_name} est obligatoire.")

    def _clean_text(self, value: Any) -> str:
        """Nettoie une valeur en garantissant une chaine.

        Args:
            value (Any): Valeur brute issue du payload JSON.

        Returns:
            str: Texte nettoye, ou chaine vide si absent.
        """

        return SheetValueFormatter.clean_text(value) or ""

    def _validate_optional_date(self, payload: dict[str, Any], field_name: str) -> None:
        """Valide une date facultative au format ISO.

        Args:
            payload (dict[str, Any]): Donnees nettoyees du jeu wishlist.
            field_name (str): Nom du champ date a valider.

        Returns:
            None: Une exception est levee si le format est invalide.
        """

        value = payload.get(field_name)
        if not value:
            return
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(f"{field_name} doit respecter le format YYYY-MM-DD.") from exc

    def _validate_optional_price(self, value: str) -> None:
        """Valide un prix facultatif positif ou nul.

        Args:
            value (str): Prix d'achat a valider.

        Returns:
            None: Une exception est levee si le prix est invalide.
        """

        if not value:
            return
        try:
            parsed_value = float(value.replace(",", "."))
        except ValueError as exc:
            raise ValueError("Prix d'achat doit etre un nombre.") from exc
        if parsed_value < 0:
            raise ValueError("Prix d'achat doit etre positif ou egal a 0.")
