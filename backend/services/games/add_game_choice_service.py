#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-08
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# License : Apache 2.0
#
"""Fusion des choix du formulaire d'ajout de jeu.

Description:
    Cette classe objet fusionne les valeurs distinctes de toutes les plateformes
    de collection et de la liste de souhaits pour alimenter les champs de saisie.
"""

from typing import Any, Optional

from services.formatting import SheetValueFormatter

WISHLIST_SHEET = "Liste de souhaits"


class AddGameChoiceService:
    """Construit les choix dedoublonnes, nettoyes et tries du formulaire d'ajout."""

    def __init__(self, platform_provider, column_value_provider):
        """Initialise le service de choix d'ajout.

        Args:
            platform_provider (Callable[[], list[str]]): Fournit les plateformes collection.
            column_value_provider (Callable[[str], dict[str, list[str]]]): Fournit les valeurs d'une feuille.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.platform_provider = platform_provider
        self.column_value_provider = column_value_provider

    def list_choices(self) -> dict[str, Any]:
        """Retourne les choix fusionnes du formulaire d'ajout.

        Args:
            Aucun.

        Returns:
            dict[str, Any]: Plateformes et valeurs de colonnes dedoublonnees.
        """

        collection_platforms = self.platform_provider()
        collection_values_groups = [
            self.column_value_provider(collection_platform)
            for collection_platform in collection_platforms
        ]
        wishlist_values = self.column_value_provider(WISHLIST_SHEET)
        merged_platforms = self._sort_choices(
            self._merge_choices(
                collection_platforms,
                wishlist_values.get("Console", []),
                wishlist_values.get("Plateforme", []),
            )
        )
        return {
            "platforms": merged_platforms,
            "values_by_column": self._build_values_by_column(
                collection_values_groups,
                wishlist_values,
                merged_platforms,
            ),
        }

    def _build_values_by_column(
        self,
        collection_values_groups: list[dict[str, list[str]]],
        wishlist_values: dict[str, list[str]],
        merged_platforms: list[str],
    ) -> dict[str, list[str]]:
        """Construit les valeurs de colonnes fusionnees pour l'ajout.

        Args:
            collection_values_groups (list[dict[str, list[str]]]): Valeurs de toutes les plateformes.
            wishlist_values (dict[str, list[str]]): Valeurs de la liste de souhaits.
            merged_platforms (list[str]): Plateformes et consoles dedoublonnees.

        Returns:
            dict[str, list[str]]: Valeurs fusionnees par colonne.
        """

        column_names = set(wishlist_values.keys())
        for values_by_column in collection_values_groups:
            column_names.update(values_by_column.keys())
        merged_values = {}
        for column_name in sorted(column_names):
            merged_values[column_name] = self._sort_choices(self._merge_choices(
                *[values_by_column.get(column_name, []) for values_by_column in collection_values_groups],
                wishlist_values.get(column_name, []),
            ))
        merged_values["Plateforme"] = merged_platforms
        merged_values["Studio"] = self._sort_choices(self._merge_choices(
            *[values_by_column.get("Studio", []) for values_by_column in collection_values_groups],
            wishlist_values.get("Studio", []),
        ))
        return merged_values

    def _merge_choices(self, *choices_groups) -> list[str]:
        """Fusionne des choix en ignorant la casse, les espaces et les valeurs invalides.

        Args:
            *choices_groups (Iterable[Any]): Groupes de valeurs a fusionner.

        Returns:
            list[str]: Choix uniques dans leur ordre d'apparition.
        """

        seen_keys = set()
        merged_choices = []
        for choices in choices_groups:
            for value in choices:
                choice = self._clean_choice(value)
                choice_key = self._choice_key(choice)
                if not choice_key or choice_key in seen_keys:
                    continue
                seen_keys.add(choice_key)
                merged_choices.append(choice)
        return merged_choices

    def _clean_choice(self, value: Any) -> Optional[str]:
        """Nettoie une valeur de choix et ignore les marqueurs invalides.

        Args:
            value (Any): Valeur brute issue d'une cellule ODS.

        Returns:
            Optional[str]: Choix nettoye, ou `None` si la valeur est invalide.
        """

        choice = SheetValueFormatter.serialize(value)
        if choice is None:
            return None
        choice = SheetValueFormatter.clean_text(choice)
        if not choice or choice.casefold() in {"nan", "nat", "none", "null"}:
            return None
        if choice.casefold().startswith("err:"):
            return None
        return choice

    def _sort_choices(self, choices: list[str]) -> list[str]:
        """Trie des choix alphabetiquement sans tenir compte de la casse.

        Args:
            choices (list[str]): Choix dedoublonnes a trier.

        Returns:
            list[str]: Choix tries par ordre alphabetique.
        """

        return sorted(choices, key=lambda choice: str(choice).casefold())

    def _choice_key(self, value: Any) -> str:
        """Construit une cle de dedoublonnage pour un choix.

        Args:
            value (Any): Valeur de choix brute.

        Returns:
            str: Cle normalisee sans casse ni espaces.
        """

        return "".join(str(value or "").lower().split())
