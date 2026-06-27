#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-24
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : contrat de requete backend pour la Bibliotheque publique.

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from services.users import UserCollectionNameNormalizer


class QueryParameterSource(Protocol):
    """Decrit une source de parametres HTTP compatible avec Flask."""

    def get(self, key: str, default: Any = None) -> Any:
        """Retourne la premiere valeur d'un parametre.

        Args:
            key (str): Nom du parametre recherche.
            default (Any): Valeur retournee lorsque le parametre est absent.

        Returns:
            Any: Valeur brute du parametre ou valeur par defaut.

        Raises:
            Aucun.
        """

    def getlist(self, key: str) -> list[Any]:
        """Retourne toutes les valeurs d'un parametre repetable.

        Args:
            key (str): Nom du parametre recherche.

        Returns:
            list[Any]: Valeurs brutes associees au parametre.

        Raises:
            Aucun.
        """


@dataclass(frozen=True)
class LibraryPageRequest:
    """Regroupe les parametres de pagination normalises.

    Attributes:
        page (int): Index de page commence a zero.
        size (int): Taille de page bornee par la valeur maximale autorisee.
    """

    page: int
    size: int

    @property
    def offset(self) -> int:
        """Calcule l'offset SQL correspondant a la page.

        Args:
            Aucun.

        Returns:
            int: Nombre de lignes a ignorer avant la page demandee.

        Raises:
            Aucun.
        """

        return self.page * self.size


@dataclass(frozen=True)
class LibrarySortRule:
    """Represente une regle de tri autorisee pour une requete Bibliotheque.

    Attributes:
        column (str): Nom logique de colonne autorise.
        direction (str): Sens du tri, `asc` ou `desc`.
    """

    column: str
    direction: str


@dataclass(frozen=True)
class LibraryQueryCriteria:
    """Regroupe les criteres de consultation d'une liste Bibliotheque.

    Attributes:
        page_request (LibraryPageRequest): Pagination normalisee.
        name (str): Filtre `name` brut nettoye.
        normalized_name (str): Filtre `name` sans casse ni accents.
        platform (str): Filtre `platform` brut nettoye.
        normalized_platform (str): Filtre `platform` sans casse ni accents.
        duplicate_flag (bool | None): Filtre optionnel des jeux signales doublons.
        sort_rules (tuple[LibrarySortRule, ...]): Tris autorises et normalises.
    """

    page_request: LibraryPageRequest
    name: str
    normalized_name: str
    platform: str
    normalized_platform: str
    duplicate_flag: bool | None
    sort_rules: tuple[LibrarySortRule, ...]


class LibraryQueryParser:
    """Parse les parametres HTTP des endpoints Bibliotheque publique."""

    DEFAULT_PAGE = 0
    DEFAULT_SIZE = 500
    MAX_SIZE = 500
    DEFAULT_SORT_COLUMN = "name"
    DEFAULT_SORT_DIRECTION = "asc"
    ALLOWED_SORT_COLUMNS = {
        "platforms": frozenset({"name", "release_date", "end_date", "manufacturer"}),
        "studios": frozenset({"name", "country", "creation_date"}),
        "games": frozenset({"name", "release_date", "developer", "platform"}),
    }

    def __init__(self, name_normalizer: UserCollectionNameNormalizer | None = None):
        """Initialise le parseur de requete Bibliotheque.

        Args:
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur de noms.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            Aucun.
        """

        self.name_normalizer = name_normalizer or UserCollectionNameNormalizer()

    def parse(
        self,
        entity_name: str,
        query_parameters: QueryParameterSource | Mapping[str, Any],
    ) -> LibraryQueryCriteria:
        """Parse les criteres de consultation pour une entite Bibliotheque.

        Args:
            entity_name (str): Nom logique de l'entite, par exemple `platforms`.
            query_parameters (QueryParameterSource | Mapping[str, Any]): Parametres HTTP bruts.

        Returns:
            LibraryQueryCriteria: Criteres normalises et securises.

        Raises:
            Aucun.
        """

        return LibraryQueryCriteria(
            page_request=LibraryPageRequest(
                page=self._parse_page(self._get_first_value(query_parameters, "page")),
                size=self._parse_size(self._get_first_value(query_parameters, "size")),
            ),
            name=self._parse_name(self._get_first_value(query_parameters, "name")),
            normalized_name=self._parse_normalized_name(
                self._get_first_value(query_parameters, "name")
            ),
            platform=self._parse_name(self._get_first_value(query_parameters, "platform")),
            normalized_platform=self._parse_normalized_name(
                self._get_first_value(query_parameters, "platform")
            ),
            duplicate_flag=self._parse_duplicate_flag(
                self._get_first_value(query_parameters, "duplicate_flag")
            ),
            sort_rules=tuple(
                self._parse_sort_rules(
                    entity_name,
                    self._get_all_values(query_parameters, "sort"),
                )
            ),
        )

    def _parse_page(self, value: Any) -> int:
        """Parse le numero de page.

        Args:
            value (Any): Valeur brute du parametre `page`.

        Returns:
            int: Page normalisee, avec fallback a `0`.
        """

        parsed_value = self._parse_positive_integer(value)
        if parsed_value is None:
            return self.DEFAULT_PAGE
        return parsed_value

    def _parse_size(self, value: Any) -> int:
        """Parse la taille de page.

        Args:
            value (Any): Valeur brute du parametre `size`.

        Returns:
            int: Taille normalisee, avec fallback a `500`.
        """

        parsed_value = self._parse_positive_integer(value)
        if parsed_value is None or parsed_value == 0 or parsed_value > self.MAX_SIZE:
            return self.DEFAULT_SIZE
        return parsed_value

    def _parse_name(self, value: Any) -> str:
        """Nettoie le filtre de nom brut.

        Args:
            value (Any): Valeur brute du parametre `name`.

        Returns:
            str: Nom nettoye ou chaine vide.
        """

        stored_value = self.name_normalizer.stored_value(value)
        return stored_value or ""

    def _parse_normalized_name(self, value: Any) -> str:
        """Normalise le filtre de nom pour une recherche sans casse ni accents.

        Args:
            value (Any): Valeur brute du parametre `name`.

        Returns:
            str: Nom normalise ou chaine vide.
        """

        comparison_key = self.name_normalizer.comparison_key(value)
        return comparison_key or ""

    def _parse_duplicate_flag(self, value: Any) -> bool | None:
        """Parse le filtre de signalement doublon.

        Args:
            value (Any): Valeur brute du parametre `duplicate_flag`.

        Returns:
            bool | None: Valeur booleenne demandee ou absence de filtre.
        """

        normalized_value = str(value or "").strip().lower()
        if normalized_value in {"true", "1", "yes", "oui"}:
            return True
        if normalized_value in {"false", "0", "no", "non"}:
            return False
        return None

    def _parse_sort_rules(
        self,
        entity_name: str,
        sort_values: list[Any],
    ) -> list[LibrarySortRule]:
        """Parse les parametres de tri repetables.

        Args:
            entity_name (str): Nom logique de l'entite cible.
            sort_values (list[Any]): Valeurs brutes des parametres `sort`.

        Returns:
            list[LibrarySortRule]: Regles de tri autorisees.
        """

        parsed_rules = [
            self._parse_sort_rule(entity_name, sort_value)
            for sort_value in sort_values
            if self._has_text(sort_value)
        ]
        return parsed_rules or [self._default_sort_rule()]

    def _parse_sort_rule(self, entity_name: str, value: Any) -> LibrarySortRule:
        """Parse une valeur `sort` individuelle.

        Args:
            entity_name (str): Nom logique de l'entite cible.
            value (Any): Valeur brute au format `colonne,sens`.

        Returns:
            LibrarySortRule: Regle autorisee ou tri par defaut.
        """

        parts = [part.strip() for part in str(value).split(",", 1)]
        requested_column = parts[0] if parts else ""
        if requested_column not in self.ALLOWED_SORT_COLUMNS.get(entity_name, frozenset()):
            return self._default_sort_rule()

        requested_direction = parts[1].lower() if len(parts) > 1 else ""
        direction = (
            requested_direction
            if requested_direction in {"asc", "desc"}
            else self.DEFAULT_SORT_DIRECTION
        )
        return LibrarySortRule(column=requested_column, direction=direction)

    def _default_sort_rule(self) -> LibrarySortRule:
        """Construit la regle de tri par defaut.

        Args:
            Aucun.

        Returns:
            LibrarySortRule: Tri `name,asc`.
        """

        return LibrarySortRule(
            column=self.DEFAULT_SORT_COLUMN,
            direction=self.DEFAULT_SORT_DIRECTION,
        )

    def _parse_positive_integer(self, value: Any) -> int | None:
        """Convertit une valeur en entier positif ou nul.

        Args:
            value (Any): Valeur brute a convertir.

        Returns:
            int | None: Entier positif ou nul, sinon `None`.
        """

        try:
            parsed_value = int(value)
        except (TypeError, ValueError):
            return None
        if parsed_value < 0:
            return None
        return parsed_value

    def _get_first_value(
        self,
        query_parameters: QueryParameterSource | Mapping[str, Any],
        key: str,
    ) -> Any:
        """Lit la premiere valeur d'un parametre.

        Args:
            query_parameters (QueryParameterSource | Mapping[str, Any]): Parametres bruts.
            key (str): Nom du parametre.

        Returns:
            Any: Premiere valeur trouvee ou `None`.
        """

        return query_parameters.get(key)

    def _get_all_values(
        self,
        query_parameters: QueryParameterSource | Mapping[str, Any],
        key: str,
    ) -> list[Any]:
        """Lit toutes les valeurs d'un parametre repetable.

        Args:
            query_parameters (QueryParameterSource | Mapping[str, Any]): Parametres bruts.
            key (str): Nom du parametre.

        Returns:
            list[Any]: Valeurs associees au parametre.
        """

        if hasattr(query_parameters, "getlist"):
            return list(query_parameters.getlist(key))
        value = query_parameters.get(key)
        if value is None:
            return []
        if isinstance(value, list | tuple):
            return list(value)
        return [value]

    def _has_text(self, value: Any) -> bool:
        """Indique si une valeur contient du texte apres nettoyage.

        Args:
            value (Any): Valeur brute a verifier.

        Returns:
            bool: `True` si la valeur contient du texte.
        """

        return bool(str(value or "").strip())
