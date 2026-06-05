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
# Description : classe objet de validation des champs de jeu avant modification ODS.

from datetime import datetime
from typing import Any

from services.formatting import SheetValueFormatter


class GamePayloadValidator:
    """Valide et normalise les champs d'un jeu de plateforme."""

    required_update_fields = ["Nom du jeu", "Date d'achat", "Prix d'achat", "Lieu d'achat"]

    def validate_add_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Valide les donnees d'ajout d'un jeu.

        Args:
            payload (dict[str, Any]): Donnees de jeu brutes envoyees par le frontend.

        Returns:
            dict[str, Any]: Donnees nettoyees et pretes a ecrire dans l'ODS.
        """

        return self.validate_update_payload(payload)

    def validate_update_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Valide les donnees de modification d'un jeu.

        Args:
            payload (dict[str, Any]): Donnees de jeu brutes envoyees par le frontend.

        Returns:
            dict[str, Any]: Donnees nettoyees et pretes a ecrire dans l'ODS.
        """

        cleaned_payload = {
            "Nom du jeu": self._clean_text(payload.get("Nom du jeu")),
            "Studio": self._clean_text(payload.get("Studio")),
            "Date de sortie": self._clean_text(payload.get("Date de sortie")),
            "Date d'achat": self._clean_text(payload.get("Date d'achat")),
            "Lieu d'achat": self._clean_text(payload.get("Lieu d'achat")),
            "Note": self._clean_text(payload.get("Note")),
            "Prix d'achat": self._clean_text(payload.get("Prix d'achat")),
            "Version": self._clean_text(payload.get("Version")),
        }
        self._validate_required_fields(cleaned_payload)
        self._validate_optional_date(cleaned_payload, "Date de sortie")
        self._validate_required_date(cleaned_payload, "Date d'achat")
        self._validate_price(cleaned_payload["Prix d'achat"])
        self._validate_note(cleaned_payload["Note"])
        return cleaned_payload

    def _clean_text(self, value: Any) -> str:
        """Nettoie une valeur en garantissant une chaine.

        Args:
            value (Any): Valeur brute issue du payload JSON.

        Returns:
            str: Texte nettoye, ou chaine vide si absent.
        """

        return SheetValueFormatter.clean_text(value) or ""

    def _validate_required_fields(self, payload: dict[str, Any]) -> None:
        """Valide les champs obligatoires non vides.

        Args:
            payload (dict[str, Any]): Donnees nettoyees du jeu.

        Returns:
            None: Une exception est levee si un champ obligatoire manque.
        """

        for field_name in self.required_update_fields:
            if payload.get(field_name) == "":
                raise ValueError(f"{field_name} est obligatoire.")

    def _validate_optional_date(self, payload: dict[str, Any], field_name: str) -> None:
        """Valide une date facultative au format ISO.

        Args:
            payload (dict[str, Any]): Donnees nettoyees du jeu.
            field_name (str): Nom du champ date a valider.

        Returns:
            None: Une exception est levee si le format est invalide.
        """

        value = payload.get(field_name)
        if value:
            self._validate_iso_date(value, field_name)

    def _validate_required_date(self, payload: dict[str, Any], field_name: str) -> None:
        """Valide une date obligatoire au format ISO.

        Args:
            payload (dict[str, Any]): Donnees nettoyees du jeu.
            field_name (str): Nom du champ date a valider.

        Returns:
            None: Une exception est levee si le format est invalide.
        """

        self._validate_iso_date(payload.get(field_name), field_name)

    def _validate_iso_date(self, value: str, field_name: str) -> None:
        """Valide une chaine date `YYYY-MM-DD`.

        Args:
            value (str): Valeur date a controler.
            field_name (str): Nom du champ pour le message d'erreur.

        Returns:
            None: Une exception est levee si le format est invalide.
        """

        try:
            datetime.strptime(value, "%Y-%m-%d")
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} doit respecter le format YYYY-MM-DD.") from exc

    def _validate_price(self, value: str) -> None:
        """Valide un prix numerique positif ou nul.

        Args:
            value (str): Prix d'achat a valider.

        Returns:
            None: Une exception est levee si le prix est invalide.
        """

        try:
            parsed_value = float(value.replace(",", "."))
        except (AttributeError, ValueError) as exc:
            raise ValueError("Prix d'achat doit etre un nombre.") from exc
        if parsed_value < 0:
            raise ValueError("Prix d'achat doit etre positif ou egal a 0.")

    def _validate_note(self, value: str) -> None:
        """Valide une note facultative au format numerique ou `x/10`.

        Args:
            value (str): Note saisie par l'utilisateur.

        Returns:
            None: Une exception est levee si la note est invalide.
        """

        if not value:
            return
        score_value = value.split("/", 1)[0].replace(",", ".")
        try:
            float(score_value)
        except ValueError as exc:
            raise ValueError("Note doit etre un nombre ou un format comme 8/10.") from exc
