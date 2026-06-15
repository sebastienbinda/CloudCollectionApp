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
# Description : serialisation des payloads publics de la Bibliotheque.

from datetime import date, datetime
from math import ceil
from typing import Any

from .library_query_contract import LibraryQueryCriteria


class LibraryPayloadSerializer:
    """Normalise les lignes SQL en payloads publics Bibliotheque."""

    def page_payload(
        self,
        criteria: LibraryQueryCriteria,
        total_elements: int,
    ) -> dict[str, int]:
        """Construit la section de pagination du payload.

        Args:
            criteria (LibraryQueryCriteria): Criteres contenant la page demandee.
            total_elements (int): Nombre total d'elements filtres.

        Returns:
            dict[str, int]: Metadonnees de pagination.
        """

        page_size = criteria.page_request.size
        return {
            "totalElements": total_elements,
            "page": criteria.page_request.page,
            "size": page_size,
            "totalPages": ceil(total_elements / page_size) if total_elements else 0,
        }

    def platform_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        """Normalise une plateforme pour l'API Bibliotheque.

        Args:
            row (dict[str, Any]): Ligne retournee par le repository.

        Returns:
            dict[str, Any]: Plateforme serialisable.
        """

        payload = {
            "id": row["id"],
            "name": self.text_value(row.get("name")),
            "release_date": self.date_value(row.get("release_date")),
            "end_date": self.date_value(row.get("end_date")),
            "manufacturer": self.text_value(row.get("manufacturer")),
            "description": self.description_value(row.get("description")),
            "total_games": self.integer_value(row.get("total_games")),
        }
        if "aliases" in row:
            payload["aliases"] = [
                self.platform_alias_payload(alias)
                for alias in row.get("aliases") or []
            ]
        return payload

    def platform_alias_payload(self, row: dict[str, Any]) -> dict[str, str]:
        """Normalise un alias de plateforme pour l'API Bibliotheque.

        Args:
            row (dict[str, Any]): Ligne d'alias retournee par le repository.

        Returns:
            dict[str, str]: Alias serialisable.
        """

        return {
            "name": self.text_value(row.get("name")),
            "category": self.text_value(row.get("category")),
            "usage_region": self.text_value(row.get("usage_region")),
            "comment": self.text_value(row.get("comment")),
        }

    def studio_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        """Normalise un studio pour l'API Bibliotheque.

        Args:
            row (dict[str, Any]): Ligne retournee par le repository.

        Returns:
            dict[str, Any]: Studio serialisable.
        """

        return {
            "id": row["id"],
            "name": self.text_value(row.get("name")),
            "country": self.text_value(row.get("country")),
            "city": self.text_value(row.get("city")),
            "creation_date": self.date_value(row.get("creation_date")),
            "status": self.text_value(row.get("status")),
            "editor_total_games": self.integer_value(row.get("editor_total_games")),
            "developer_total_games": self.integer_value(row.get("developer_total_games")),
        }

    def game_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        """Normalise un jeu pour l'API Bibliotheque.

        Args:
            row (dict[str, Any]): Ligne retournee par le repository.

        Returns:
            dict[str, Any]: Jeu serialisable.
        """

        return {
            "id": row["id"],
            "name": self.text_value(row.get("name")),
            "release_date": self.date_value(row.get("release_date")),
            "developer": self.text_value(row.get("developer")),
            "editor": self.text_value(row.get("editor")),
            "status": self.text_value(row.get("status")),
            "platform": self.text_value(row.get("platform")),
        }

    def date_value(self, value: Any) -> str:
        """Serialise une date pour l'API Bibliotheque.

        Args:
            value (Any): Valeur brute retournee par le repository.

        Returns:
            str: Date ISO ou chaine vide.
        """

        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return self.text_value(value)

    def description_value(self, value: Any) -> Any:
        """Normalise une description JSON.

        Args:
            value (Any): Description brute.

        Returns:
            Any: Description JSON existante ou chaine vide.
        """

        return value if value is not None else ""

    def text_value(self, value: Any) -> str:
        """Normalise une valeur textuelle.

        Args:
            value (Any): Valeur brute.

        Returns:
            str: Texte serialisable ou chaine vide.
        """

        return "" if value is None else str(value)

    def integer_value(self, value: Any) -> int:
        """Normalise une valeur entiere.

        Args:
            value (Any): Valeur brute.

        Returns:
            int: Entier serialisable.
        """

        return int(value or 0)
