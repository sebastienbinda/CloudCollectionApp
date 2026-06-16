#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : lecteur CSV du catalogue applicatif des plateformes.

import csv
from datetime import datetime
from pathlib import Path

from .platform_catalog_entry import PlatformCatalogEntry


class PlatformCatalogCsvReader:
    """Lit le fichier CSV de reference des plateformes applicatives."""

    REQUIRED_COLUMNS = (
        "nom_machine",
        "nom_fabricant",
        "date_mise_en_vente",
        "date_retrait_vente",
    )
    UNKNOWN_VALUE = "Inconnue"
    AVAILABLE_VALUE = "En vente"

    def read(self, csv_path: Path) -> list[PlatformCatalogEntry]:
        """Lit et valide les plateformes du CSV.

        Args:
            csv_path (Path): Chemin du fichier CSV a lire.

        Returns:
            list[PlatformCatalogEntry]: Plateformes normalisees.

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
                "Colonnes CSV plateformes manquantes: "
                + ", ".join(missing_columns)
            )

    def _row_to_entry(self, row: dict[str, str], line_number: int) -> PlatformCatalogEntry:
        name = self._required_text(row, "nom_machine", line_number)
        manufacturer = self._required_text(row, "nom_fabricant", line_number)
        release_date = self._parse_date(
            row.get("date_mise_en_vente", ""),
            "date_mise_en_vente",
            line_number,
        )
        end_date = self._parse_date(
            row.get("date_retrait_vente", ""),
            "date_retrait_vente",
            line_number,
        )
        return PlatformCatalogEntry(
            name=name,
            manufacturer=manufacturer,
            release_date=release_date,
            end_date=end_date,
            description={},
        )

    def _required_text(self, row: dict[str, str], column: str, line_number: int) -> str:
        value = str(row.get(column) or "").strip()
        if not value:
            raise ValueError(f"Valeur obligatoire absente ligne {line_number}: {column}.")
        return value

    def _parse_date(
        self,
        value: str,
        column: str,
        line_number: int,
    ) -> datetime | None:
        normalized_value = str(value or "").strip()
        if normalized_value == self.UNKNOWN_VALUE:
            return None
        if normalized_value == self.AVAILABLE_VALUE:
            if column != "date_retrait_vente":
                raise ValueError(
                    f"Valeur {self.AVAILABLE_VALUE} interdite ligne {line_number}: "
                    f"{column}."
                )
            return None
        return self._parse_known_date(normalized_value, column, line_number)

    def _parse_known_date(
        self,
        value: str,
        column: str,
        line_number: int,
    ) -> datetime:
        date_formats = {
            4: "%Y",
            7: "%Y-%m",
            10: "%Y-%m-%d",
        }
        date_format = date_formats.get(len(value))
        if date_format is None:
            raise ValueError(f"Date invalide ligne {line_number}: {column}={value}.")
        try:
            return datetime.strptime(value, date_format)
        except ValueError as exc:
            raise ValueError(f"Date invalide ligne {line_number}: {column}={value}.") from exc
