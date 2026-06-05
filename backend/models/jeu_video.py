#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional, Union


@dataclass
class JeuVideo:
    """Represente une ligne de jeu video normalisee depuis le fichier ODS.

    Attributes:
        nom_du_jeu (Optional[str]): Titre du jeu.
        studio (Optional[str]): Studio ou editeur du jeu.
        date_de_sortie (Optional[Union[date, datetime, str]]): Date de sortie brute ou normalisee.
        date_d_achat (Optional[Union[date, datetime, str]]): Date d'achat brute ou normalisee.
        lieu_d_achat (Optional[str]): Magasin, site ou lieu d'achat.
        note (Optional[str]): Note personnelle du jeu.
        prix_d_achat (Optional[Union[float, int, str]]): Prix d'achat lu dans l'ODS.
        version (Optional[str]): Version ou region du jeu.
    """

    nom_du_jeu: Optional[str]
    studio: Optional[str]
    date_de_sortie: Optional[Union[date, datetime, str]]
    date_d_achat: Optional[Union[date, datetime, str]]
    lieu_d_achat: Optional[str]
    note: Optional[str]
    prix_d_achat: Optional[Union[float, int, str]]
    version: Optional[str]

    @classmethod
    def from_sheet_row(cls, row: dict[str, Any]) -> "JeuVideo":
        """Construit un objet `JeuVideo` a partir d'une ligne ODS.

        Args:
            row (dict[str, Any]): Ligne issue de pandas ou du parseur XML, indexee par nom de colonne.

        Returns:
            JeuVideo: Instance normalisee avec les variantes d'apostrophes harmonisees.
        """

        return cls(
            nom_du_jeu=_clean_value(row.get("Nom du jeu")),
            studio=_clean_value(row.get("Studio")),
            date_de_sortie=_clean_value(row.get("Date de sortie")),
            date_d_achat=_clean_value(row.get("Date d'achat") or row.get("Date d’achat")),
            lieu_d_achat=_clean_value(
                row.get("Lieu d'achat") or row.get("Lieu d’achat")
            ),
            note=_clean_value(row.get("Note")),
            prix_d_achat=_clean_value(
                row.get("Prix d'achat") or row.get("Prix d’achat")
            ),
            version=_clean_value(row.get("Version")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convertit le jeu video en dictionnaire compatible JSON.

        Args:
            Aucun.

        Returns:
            dict[str, Any]: Donnees du jeu avec les noms de colonnes attendus par le frontend.
        """

        return {
            "Nom du jeu": self.nom_du_jeu,
            "Studio": self.studio,
            "Date de sortie": _serialize_value(self.date_de_sortie),
            "Date d'achat": _serialize_value(self.date_d_achat),
            "Lieu d'achat": self.lieu_d_achat,
            "Note": self.note,
            "Prix d'achat": _serialize_value(self.prix_d_achat),
            "Version": self.version,
        }


def _clean_value(value: Any) -> Any:
    """Nettoie une valeur brute lue depuis le tableur.

    Args:
        value (Any): Valeur issue du fichier ODS, potentiellement `None` ou `NaN`.

    Returns:
        Any: `None` pour les valeurs vides/NaN, sinon la valeur d'origine.
    """

    if value is None:
        return None
    if isinstance(value, float) and value != value:
        return None
    return value


def _serialize_value(value: Any) -> Any:
    """Serialise une valeur Python pour une reponse JSON.

    Args:
        value (Any): Valeur interne, notamment date, datetime, nombre ou texte.

    Returns:
        Any: Date convertie en chaine ISO 8601, ou valeur d'origine.
    """

    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value
