#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-10
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : validation generique des dates issues d'un import de collection.

from dataclasses import replace
from datetime import date, datetime

from .collection_import_models import CollectionImportData


class CollectionImportDateValidator:
    """Valide les dates d'un import avant leur persistance SQL."""

    MINIMUM_RELEASE_YEAR = 1950

    def validate(self, import_data: CollectionImportData) -> CollectionImportData:
        """Retourne des donnees d'import avec des dates persistables.

        Args:
            import_data (CollectionImportData): Donnees lues par un reader de collection.

        Returns:
            CollectionImportData: Donnees avec les dates invalides remplacees par `None`.

        Raises:
            Aucun: Les dates invalides sont ignorees fonctionnellement.
        """

        return replace(
            import_data,
            games=[
                replace(game, release_date=self._valid_release_date(game.release_date))
                for game in import_data.games
            ],
        )

    def validate_release_date(self, value) -> date | None:
        """Retourne une date persistable ou `None`.

        Args:
            value (object): Valeur brute de date issue d'un import.

        Returns:
            date | None: Date valide pour PostgreSQL ou absence de date.

        Raises:
            Aucun: Les valeurs invalides sont ignorees fonctionnellement.
        """

        if value is None:
            return None
        if isinstance(value, datetime):
            try:
                return self._valid_date(value.date())
            except (OverflowError, ValueError):
                return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return self._valid_date(value)
        if isinstance(value, str):
            return self._parse_string_date(value)
        return None

    def _valid_release_date(self, value) -> date | None:
        return self.validate_release_date(value)

    def _parse_string_date(self, value: str) -> date | None:
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        try:
            return self._valid_date(datetime.fromisoformat(cleaned_value).date())
        except ValueError:
            return None

    def _valid_date(self, value: date) -> date | None:
        if value.year < self.MINIMUM_RELEASE_YEAR:
            return None
        return value
