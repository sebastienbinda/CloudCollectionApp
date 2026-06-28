#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-25
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : contrat de requete backend pour la collection utilisateur.

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping

from services.library.library_query_contract import (
    LibraryPageRequest,
    LibraryQueryParser,
    LibrarySortRule,
    QueryParameterSource,
)
from services.users import UserCollectionNameNormalizer

WISHLIST_BUY_STATUS_ALL = "all"
WISHLIST_BUY_STATUS_YES = "yes"
WISHLIST_BUY_STATUS_NO = "no"
WISHLIST_BUY_STATUS_VALUES = frozenset({
    WISHLIST_BUY_STATUS_ALL,
    WISHLIST_BUY_STATUS_YES,
    WISHLIST_BUY_STATUS_NO,
})


@dataclass(frozen=True)
class UserCollectionPlatformQueryCriteria:
    """Regroupe les criteres de consultation des plateformes utilisateur.

    Attributes:
        page_request (LibraryPageRequest): Pagination normalisee.
        name (str): Filtre `name` nettoye.
        normalized_name (str): Filtre `name` sans casse ni accents.
        wishlist (bool | None): Filtre wishlist, ou aucun filtre si absent.
        sort_rules (tuple[LibrarySortRule, ...]): Tris autorises.
    """

    page_request: LibraryPageRequest
    name: str
    normalized_name: str
    wishlist: bool | None
    sort_rules: tuple[LibrarySortRule, ...]


@dataclass(frozen=True)
class UserCollectionGameQueryCriteria:
    """Regroupe les criteres de consultation des jeux utilisateur.

    Attributes:
        page_request (LibraryPageRequest): Pagination normalisee.
        name (str): Filtre `name` nettoye.
        normalized_name (str): Filtre `name` sans casse ni accents.
        studio_name (str): Filtre `studio_name` nettoye.
        normalized_studio_name (str): Filtre studio sans casse ni accents.
        platform_name (str): Filtre `platform_name` nettoye.
        normalized_platform_name (str): Filtre plateforme sans casse ni accents.
        platform_id (int | None): Identifiant exact de plateforme.
        has_invalid_platform_id (bool): Indique un identifiant plateforme invalide.
        release_date_from (date | None): Debut de plage de date de sortie.
        release_date_to (date | None): Fin de plage de date de sortie.
        wishlist (bool | None): Filtre wishlist, ou aucun filtre si absent.
        wishlist_buy_status (str): Filtre d'achat wishlist: all, yes ou no.
        sort_rules (tuple[LibrarySortRule, ...]): Tris autorises.
    """

    page_request: LibraryPageRequest
    name: str
    normalized_name: str
    studio_name: str
    normalized_studio_name: str
    platform_name: str
    normalized_platform_name: str
    platform_id: int | None
    has_invalid_platform_id: bool
    release_date_from: date | None
    release_date_to: date | None
    wishlist: bool | None
    wishlist_buy_status: str
    sort_rules: tuple[LibrarySortRule, ...]


class UserCollectionQueryParser:
    """Parse les parametres HTTP des endpoints de collection utilisateur."""

    PLATFORM_ENTITY = "collection_platforms"
    GAME_ENTITY = "collection_games"
    PLATFORM_QUERY_PARAMETERS = frozenset({"name", "wishlist", "page", "size", "sort"})
    GAME_QUERY_PARAMETERS = frozenset(
        {
            "name",
            "studio_name",
            "platform_name",
            "platform_id",
            "release_date",
            "wishlist",
            "wishlist_buy_status",
            "page",
            "size",
            "sort",
        }
    )
    PLATFORM_SORT_COLUMNS = frozenset({"name", "release_date", "end_date", "manufacturer"})
    GAME_SORT_COLUMNS = frozenset(
        {"name", "platform_name", "release_date", "studio_name", "buy_date", "grade"}
    )

    def __init__(self, name_normalizer: UserCollectionNameNormalizer | None = None):
        """Initialise le parseur de requete collection.

        Args:
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur de noms.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            Aucun.
        """

        self.name_normalizer = name_normalizer or UserCollectionNameNormalizer()
        self.base_parser = LibraryQueryParser(self.name_normalizer)

    def parse_platforms(
        self,
        query_parameters: QueryParameterSource | Mapping[str, Any],
    ) -> UserCollectionPlatformQueryCriteria:
        """Parse les criteres de consultation des plateformes utilisateur.

        Args:
            query_parameters (QueryParameterSource | Mapping[str, Any]): Parametres HTTP bruts.

        Returns:
            UserCollectionPlatformQueryCriteria: Criteres normalises.

        Raises:
            ValueError: Si un parametre ou un tri n'est pas supporte.
        """

        self._validate_query_parameters(query_parameters, self.PLATFORM_QUERY_PARAMETERS)
        page_request = LibraryPageRequest(
            page=self.base_parser._parse_page(self._get_first_value(query_parameters, "page")),
            size=self.base_parser._parse_size(self._get_first_value(query_parameters, "size")),
        )
        return UserCollectionPlatformQueryCriteria(
            page_request=page_request,
            name=self._parse_text(query_parameters, "name"),
            normalized_name=self._parse_normalized_text(query_parameters, "name"),
            wishlist=self._parse_wishlist_filter(query_parameters),
            sort_rules=self._parse_sort_rules(
                self.PLATFORM_SORT_COLUMNS,
                self._get_all_values(query_parameters, "sort"),
            ),
        )

    def parse_games(
        self,
        query_parameters: QueryParameterSource | Mapping[str, Any],
    ) -> UserCollectionGameQueryCriteria:
        """Parse les criteres de consultation des jeux utilisateur.

        Args:
            query_parameters (QueryParameterSource | Mapping[str, Any]): Parametres HTTP bruts.

        Returns:
            UserCollectionGameQueryCriteria: Criteres normalises.

        Raises:
            ValueError: Si un parametre ou un critere n'est pas supporte.
        """

        self._validate_query_parameters(query_parameters, self.GAME_QUERY_PARAMETERS)
        platform_id, has_invalid_platform_id = self._parse_platform_id(
            self._get_first_value(query_parameters, "platform_id")
        )
        release_date_from, release_date_to = self._parse_release_date_range(
            self._get_first_value(query_parameters, "release_date")
        )
        return UserCollectionGameQueryCriteria(
            page_request=LibraryPageRequest(
                page=self.base_parser._parse_page(self._get_first_value(query_parameters, "page")),
                size=self.base_parser._parse_size(self._get_first_value(query_parameters, "size")),
            ),
            name=self._parse_text(query_parameters, "name"),
            normalized_name=self._parse_normalized_text(query_parameters, "name"),
            studio_name=self._parse_text(query_parameters, "studio_name"),
            normalized_studio_name=self._parse_normalized_text(query_parameters, "studio_name"),
            platform_name=self._parse_text(query_parameters, "platform_name"),
            normalized_platform_name=self._parse_normalized_text(query_parameters, "platform_name"),
            platform_id=platform_id,
            has_invalid_platform_id=has_invalid_platform_id,
            release_date_from=release_date_from,
            release_date_to=release_date_to,
            wishlist=self._parse_wishlist_filter(query_parameters),
            wishlist_buy_status=self._parse_wishlist_buy_status_filter(query_parameters),
            sort_rules=self._parse_sort_rules(
                self.GAME_SORT_COLUMNS,
                self._get_all_values(query_parameters, "sort"),
            ),
        )

    def _parse_text(
        self,
        query_parameters: QueryParameterSource | Mapping[str, Any],
        key: str,
    ) -> str:
        """Nettoie une valeur textuelle.

        Args:
            query_parameters (QueryParameterSource | Mapping[str, Any]): Parametres bruts.
            key (str): Nom du parametre.

        Returns:
            str: Valeur nettoyee ou chaine vide.

        Raises:
            Aucun.
        """

        return self.name_normalizer.stored_value(self._get_first_value(query_parameters, key)) or ""

    def _parse_normalized_text(
        self,
        query_parameters: QueryParameterSource | Mapping[str, Any],
        key: str,
    ) -> str:
        """Normalise une valeur textuelle pour une recherche insensible aux accents.

        Args:
            query_parameters (QueryParameterSource | Mapping[str, Any]): Parametres bruts.
            key (str): Nom du parametre.

        Returns:
            str: Valeur normalisee ou chaine vide.

        Raises:
            Aucun.
        """

        return self.name_normalizer.comparison_key(self._get_first_value(query_parameters, key)) or ""

    def _parse_sort_rules(
        self,
        allowed_columns: frozenset[str],
        sort_values: list[Any],
    ) -> tuple[LibrarySortRule, ...]:
        """Parse les tris demandes selon une allowlist.

        Args:
            allowed_columns (frozenset[str]): Colonnes de tri autorisees.
            sort_values (list[Any]): Valeurs brutes du parametre `sort`.

        Returns:
            tuple[LibrarySortRule, ...]: Tris normalises.

        Raises:
            ValueError: Si une colonne ou direction de tri est invalide.
        """

        parsed_rules = []
        allowed_columns_text = ", ".join(sorted(allowed_columns))
        for sort_value in sort_values:
            if not str(sort_value or "").strip():
                continue
            parts = [part.strip() for part in str(sort_value).split(",", 1)]
            requested_column = parts[0] if parts else ""
            if requested_column not in allowed_columns:
                raise ValueError(
                    f"Unsupported sort column '{requested_column}'. "
                    f"Allowed columns: {allowed_columns_text}."
                )
            requested_direction = parts[1].lower() if len(parts) > 1 else ""
            if requested_direction not in {"asc", "desc"}:
                raise ValueError(
                    f"Unsupported sort direction '{requested_direction}' for column "
                    f"'{requested_column}'. Allowed directions: asc, desc."
                )
            parsed_rules.append(
                LibrarySortRule(
                    column=requested_column,
                    direction=requested_direction,
                )
            )
        return tuple(parsed_rules or [self.base_parser._default_sort_rule()])

    def _parse_platform_id(self, value: Any) -> tuple[int | None, bool]:
        """Parse l'identifiant de plateforme.

        Args:
            value (Any): Valeur brute du parametre `platform_id`.

        Returns:
            tuple[int | None, bool]: Identifiant normalise et indicateur d'invalidite.

        Raises:
            ValueError: Si la valeur n'est pas un identifiant positif.
        """

        if value is None or str(value).strip() == "":
            return None, False
        parsed_value = self.base_parser._parse_positive_integer(value)
        if parsed_value is None or parsed_value == 0:
            raise ValueError("Invalid platform_id. Expected a positive integer.")
        return parsed_value, False

    def _parse_release_date_range(self, value: Any) -> tuple[date | None, date | None]:
        """Parse une plage `release_date=YYYY-MM-DD..YYYY-MM-DD`.

        Args:
            value (Any): Valeur brute du parametre `release_date`.

        Returns:
            tuple[date | None, date | None]: Bornes valides ou valeurs vides.

        Raises:
            ValueError: Si la plage n'utilise pas le format attendu.
        """

        raw_value = str(value or "").strip()
        if not raw_value:
            return None, None
        if ".." not in raw_value:
            raise ValueError("Invalid release_date. Expected format: YYYY-MM-DD..YYYY-MM-DD.")
        start_value, end_value = raw_value.split("..", 1)
        return self._parse_date(start_value), self._parse_date(end_value)

    def _parse_date(self, value: str) -> date | None:
        """Parse une date ISO.

        Args:
            value (str): Valeur brute de date.

        Returns:
            date | None: Date valide ou `None`.

        Raises:
            ValueError: Si la date n'utilise pas le format ISO.
        """

        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            raise ValueError("Invalid release_date. Expected format: YYYY-MM-DD..YYYY-MM-DD.")

    def _parse_wishlist(self, value: Any) -> bool | None:
        """Parse le filtre booleen `wishlist`.

        Args:
            value (Any): Valeur brute du parametre `wishlist`.

        Returns:
            bool | None: Filtre booleen, ou `None` si le parametre est absent ou invalide.

        Raises:
            Aucun.
        """

        if value is True:
            return True
        if value is False:
            return False
        normalized_value = str(value or "").strip().lower()
        if normalized_value == "true":
            return True
        if normalized_value == "false":
            return False
        return None

    def _parse_wishlist_filter(
        self,
        query_parameters: QueryParameterSource | Mapping[str, Any],
    ) -> bool | None:
        """Parse le filtre wishlist en refusant les valeurs inconnues.

        Args:
            query_parameters (QueryParameterSource | Mapping[str, Any]): Parametres bruts.

        Returns:
            bool | None: Filtre booleen ou aucun filtre si absent.

        Raises:
            ValueError: Si la valeur n'est ni `true` ni `false`.
        """

        value = self._get_first_value(query_parameters, "wishlist")
        if value is None or str(value).strip() == "":
            return None
        parsed_value = self._parse_wishlist(value)
        if parsed_value is None:
            raise ValueError("Invalid wishlist. Expected 'true' or 'false'.")
        return parsed_value

    def _parse_wishlist_buy_status_filter(
        self,
        query_parameters: QueryParameterSource | Mapping[str, Any],
    ) -> str:
        """Parse le filtre d'achat de la wishlist.

        Args:
            query_parameters (QueryParameterSource | Mapping[str, Any]): Parametres bruts.

        Returns:
            str: Filtre normalise: `all`, `yes` ou `no`.

        Raises:
            ValueError: Si la valeur n'est pas supportee.
        """

        raw_value = self._get_first_value(query_parameters, "wishlist_buy_status")
        normalized_value = str(raw_value or "").strip().lower()
        if not normalized_value:
            return WISHLIST_BUY_STATUS_ALL
        aliases = {
            "all": WISHLIST_BUY_STATUS_ALL,
            "tous": WISHLIST_BUY_STATUS_ALL,
            "yes": WISHLIST_BUY_STATUS_YES,
            "oui": WISHLIST_BUY_STATUS_YES,
            "true": WISHLIST_BUY_STATUS_YES,
            "no": WISHLIST_BUY_STATUS_NO,
            "non": WISHLIST_BUY_STATUS_NO,
            "false": WISHLIST_BUY_STATUS_NO,
        }
        parsed_value = aliases.get(normalized_value)
        if parsed_value not in WISHLIST_BUY_STATUS_VALUES:
            raise ValueError("Invalid wishlist_buy_status. Expected 'all', 'yes' or 'no'.")
        return parsed_value

    def _validate_query_parameters(
        self,
        query_parameters: QueryParameterSource | Mapping[str, Any],
        allowed_parameters: frozenset[str],
    ) -> None:
        """Verifie que les parametres de recherche sont declares.

        Args:
            query_parameters (QueryParameterSource | Mapping[str, Any]): Parametres bruts.
            allowed_parameters (frozenset[str]): Parametres supportes.

        Returns:
            None: La validation ne retourne aucune valeur.

        Raises:
            ValueError: Si un parametre n'est pas supporte.
        """

        parameter_names = getattr(query_parameters, "keys", lambda: [])()
        for parameter_name in parameter_names:
            if parameter_name not in allowed_parameters:
                allowed_parameters_text = ", ".join(sorted(allowed_parameters))
                raise ValueError(
                    f"Unsupported query parameter '{parameter_name}'. "
                    f"Allowed parameters: {allowed_parameters_text}."
                )

    def _get_first_value(
        self,
        query_parameters: QueryParameterSource | Mapping[str, Any],
        key: str,
    ) -> Any:
        return self.base_parser._get_first_value(query_parameters, key)

    def _get_all_values(
        self,
        query_parameters: QueryParameterSource | Mapping[str, Any],
        key: str,
    ) -> list[Any]:
        return self.base_parser._get_all_values(query_parameters, key)
