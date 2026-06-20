#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-19
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : parsing des requetes de moderation des images de plateformes.

from dataclasses import dataclass
from typing import Any, Mapping

from .library_query_contract import LibraryPageRequest, LibrarySortRule


@dataclass(frozen=True)
class PlatformImageModerationCriteria:
    """Regroupe les criteres de liste des images a moderer.

    Attributes:
        page_request (LibraryPageRequest): Pagination normalisee.
        status (str): Statut filtre en base, ou chaine vide.
        platform (str): Nom de plateforme filtre, ou chaine vide.
        sort_rules (tuple[LibrarySortRule, ...]): Tris normalises.
    """

    page_request: LibraryPageRequest
    status: str
    platform: str
    sort_rules: tuple[LibrarySortRule, ...]


class PlatformImageModerationQueryParser:
    """Parse les parametres HTTP de moderation des images de plateformes."""

    STATUS_ALIASES = {
        "waiting_validation": "WAITING_VALIDATION",
        "accepted": "ACCEPTED",
    }
    DEFAULT_PAGE = 0
    DEFAULT_SIZE = 500
    MAX_SIZE = 500
    DEFAULT_SORT_RULE = LibrarySortRule("creation_date", "desc")
    ALLOWED_SORT_COLUMNS = {"creation_date", "platform", "status", "type"}

    def parse(self, query_parameters: Mapping[str, Any]) -> PlatformImageModerationCriteria:
        """Parse les criteres de liste de moderation.

        Args:
            query_parameters (Mapping[str, Any]): Parametres HTTP bruts.

        Returns:
            PlatformImageModerationCriteria: Criteres normalises.
        """

        page_request = LibraryPageRequest(
            page=self._parse_positive_int(self._get_first_value(query_parameters, "page"), 0),
            size=self._parse_size(self._get_first_value(query_parameters, "size")),
        )
        return PlatformImageModerationCriteria(
            page_request=page_request,
            status=self._parse_status_filter(self._get_first_value(query_parameters, "status")),
            platform=str(self._get_first_value(query_parameters, "platform") or "").strip(),
            sort_rules=tuple(
                self._parse_sort_rules(self._get_all_values(query_parameters, "sort"))
            ),
        )

    def _parse_status_filter(self, value: Any) -> str:
        raw_value = str(value or "").strip()
        if not raw_value:
            return ""
        normalized_value = raw_value.lower()
        return self.STATUS_ALIASES.get(normalized_value, raw_value.upper())

    def _parse_sort_rules(self, sort_values: list[Any]) -> list[LibrarySortRule]:
        parsed_rules = [
            self._parse_sort_rule(sort_value)
            for sort_value in sort_values
            if str(sort_value or "").strip()
        ]
        return parsed_rules or [self.DEFAULT_SORT_RULE]

    def _parse_sort_rule(self, value: Any) -> LibrarySortRule:
        raw_value = str(value or "").strip()
        column, _, direction = raw_value.partition(",")
        column = column.strip().lower()
        direction = direction.strip().lower()
        if column not in self.ALLOWED_SORT_COLUMNS:
            return self.DEFAULT_SORT_RULE
        if direction not in {"asc", "desc"}:
            direction = "asc"
        return LibrarySortRule(column, direction)

    def _parse_size(self, value: Any) -> int:
        parsed_value = self._parse_positive_int(value, self.DEFAULT_SIZE)
        if parsed_value <= 0 or parsed_value > self.MAX_SIZE:
            return self.DEFAULT_SIZE
        return parsed_value

    def _parse_positive_int(self, value: Any, default_value: int) -> int:
        try:
            parsed_value = int(value)
        except (TypeError, ValueError):
            return default_value
        return parsed_value if parsed_value >= 0 else default_value

    def _get_first_value(self, query_parameters: Mapping[str, Any], key: str) -> Any:
        if hasattr(query_parameters, "get"):
            return query_parameters.get(key)
        return None

    def _get_all_values(self, query_parameters: Mapping[str, Any], key: str) -> list[Any]:
        if hasattr(query_parameters, "getlist"):
            return list(query_parameters.getlist(key))
        value = query_parameters.get(key) if hasattr(query_parameters, "get") else None
        if value is None:
            return []
        return value if isinstance(value, list) else [value]
