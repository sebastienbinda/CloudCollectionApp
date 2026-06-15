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
# Description : lecteur CSV du catalogue applicatif des alias de plateformes.

import csv
from pathlib import Path

from .platform_alias_catalog_entry import PlatformAliasCatalogEntry


class PlatformAliasCatalogCsvReader:
    """Lit le fichier CSV de reference des alias de plateformes."""

    REQUIRED_COLUMNS = (
        "nom_machine",
        "nom_alternatif",
        "categorie",
        "zone_ou_usage",
        "commentaire",
    )

    def read(self, csv_path: Path) -> list[PlatformAliasCatalogEntry]:
        """Lit et valide les alias du CSV.

        Args:
            csv_path (Path): Chemin du fichier CSV a lire.

        Returns:
            list[PlatformAliasCatalogEntry]: Alias normalises.

        Raises:
            ValueError: Si le fichier est invalide ou incomplet.
            OSError: Si le fichier ne peut pas etre lu.
        """

        with csv_path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            self._validate_columns(reader.fieldnames)
            return [
                self._row_to_entry(row, line_number)
                for line_number, row in enumerate(reader, start=2)
            ]

    def _validate_columns(self, fieldnames: list[str] | None) -> None:
        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in (fieldnames or [])
        ]
        if missing_columns:
            raise ValueError(
                "Colonnes CSV alias plateformes manquantes: "
                + ", ".join(missing_columns)
            )

    def _row_to_entry(
        self,
        row: dict[str, str],
        line_number: int,
    ) -> PlatformAliasCatalogEntry:
        return PlatformAliasCatalogEntry(
            platform_name=self._required_text(row, "nom_machine", line_number),
            alias_name=self._required_text(row, "nom_alternatif", line_number),
            category=self._clean_text(row.get("categorie", "")),
            usage_region=self._clean_text(row.get("zone_ou_usage", "")),
            comment=self._clean_text(row.get("commentaire", "")),
        )

    def _required_text(self, row: dict[str, str], column: str, line_number: int) -> str:
        value = self._clean_text(row.get(column, ""))
        if not value:
            raise ValueError(f"Valeur obligatoire absente ligne {line_number}: {column}.")
        return value

    def _clean_text(self, value: str) -> str:
        return str(value or "").strip()
