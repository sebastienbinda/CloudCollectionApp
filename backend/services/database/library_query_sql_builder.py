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
# Description : construction SQL securisee des requetes Bibliotheque.

from typing import Any

from services.library import LibraryQueryCriteria


class LibraryQuerySqlBuilder:
    """Construit les fragments SQL reutilises par les repositories Bibliotheque."""

    ACCENTED_CHARACTERS = (
        "àáâãäåāăąçćčďèéêëēĕėęěìíîïĩīĭįłñńňòóôõöøōŏőŕř"
        "śšşťùúûüũūŭůűųýÿźżž"
    )
    PLAIN_CHARACTERS = (
        "aaaaaaaaacccdeeeeeeeeeiiiiiiiilnnnooooooooorrssstuuuuuuuuuuyyzzz"
    )

    @classmethod
    def build_name_filter(
        cls,
        criteria: LibraryQueryCriteria,
        column_expression: str,
        parameters: dict[str, Any],
    ) -> str:
        """Construit le filtre SQL `name` sans casse ni accents.

        Args:
            criteria (LibraryQueryCriteria): Criteres de consultation normalises.
            column_expression (str): Expression SQL de la colonne nommee.
            parameters (dict[str, Any]): Parametres SQL a enrichir.

        Returns:
            str: Clause SQL commencant par `WHERE`, ou chaine vide.

        Raises:
            Aucun.
        """

        if not criteria.normalized_name:
            return ""
        parameters["name_pattern"] = f"%{criteria.normalized_name}%"
        parameters["accented_characters"] = cls.ACCENTED_CHARACTERS
        parameters["plain_characters"] = cls.PLAIN_CHARACTERS
        return (
            "WHERE TRANSLATE(LOWER("
            f"{column_expression}"
            "), :accented_characters, :plain_characters) LIKE :name_pattern"
        )

    @classmethod
    def build_order_by(
        cls,
        criteria: LibraryQueryCriteria,
        allowed_columns: dict[str, str],
    ) -> str:
        """Construit une clause `ORDER BY` depuis une allowlist.

        Args:
            criteria (LibraryQueryCriteria): Criteres contenant les tris demandes.
            allowed_columns (dict[str, str]): Expressions SQL autorisees par nom logique.

        Returns:
            str: Clause `ORDER BY` complete.

        Raises:
            Aucun.
        """

        expressions = []
        for sort_rule in criteria.sort_rules:
            column_expression = allowed_columns.get(sort_rule.column, allowed_columns["name"])
            direction = "DESC" if sort_rule.direction == "desc" else "ASC"
            expressions.append(f"{column_expression} {direction}")
        if not any(expression.startswith(f"{allowed_columns['name']} ") for expression in expressions):
            expressions.append(f"{allowed_columns['name']} ASC")
        return "ORDER BY " + ", ".join(expressions)

    @classmethod
    def build_pagination_parameters(cls, criteria: LibraryQueryCriteria) -> dict[str, int]:
        """Construit les parametres SQL de pagination.

        Args:
            criteria (LibraryQueryCriteria): Criteres contenant la pagination.

        Returns:
            dict[str, int]: Parametres `limit` et `offset`.

        Raises:
            Aucun.
        """

        return {
            "limit": criteria.page_request.size,
            "offset": criteria.page_request.offset,
        }
