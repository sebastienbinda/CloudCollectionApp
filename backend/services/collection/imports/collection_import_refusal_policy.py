#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : politique de refus global d'un fichier de collection importe.

from dataclasses import dataclass

from .collection_import_models import CollectionImportData


@dataclass(frozen=True)
class CollectionImportRefusal:
    """Decrit le refus global eventuel d'un fichier importe.

    Attributes:
        refused (bool): Indique si l'import complet est refuse.
        reason (str): Raison fonctionnelle stable du refus.
        invalid_games_count (int): Nombre de jeux contenant au moins une erreur.
        total_games_count (int): Nombre total de jeux lus dans le fichier.
        message (str): Message fonctionnel exploitable par l'interface.
    """

    refused: bool
    reason: str = ""
    invalid_games_count: int = 0
    total_games_count: int = 0
    message: str = ""

    def to_dict(self) -> dict[str, object]:
        """Convertit le refus en dictionnaire serialisable.

        Args:
            Aucun.

        Returns:
            dict[str, object]: Informations de refus exposees par l'API.
        """

        return {
            "refused": self.refused,
            "reason": self.reason,
            "invalid_games_count": self.invalid_games_count,
            "total_games_count": self.total_games_count,
            "message": self.message,
        }


class CollectionImportRefusalPolicy:
    """Refuse un import quand trop de jeux lus contiennent des erreurs."""

    REFUSAL_REASON_TOO_MANY_INVALID_GAMES = "too_many_invalid_games"

    def evaluate(self, import_data: CollectionImportData) -> CollectionImportRefusal:
        """Evalue si l'import complet doit etre refuse.

        Args:
            import_data (CollectionImportData): Donnees lues et validees.

        Returns:
            CollectionImportRefusal: Decision de refus global.
        """

        total_games_count = len(import_data.games)
        invalid_games_count = len(import_data.warnings.invalid_games)
        if total_games_count > 0 and invalid_games_count * 2 > total_games_count:
            return CollectionImportRefusal(
                refused=True,
                reason=self.REFUSAL_REASON_TOO_MANY_INVALID_GAMES,
                invalid_games_count=invalid_games_count,
                total_games_count=total_games_count,
                message=(
                    "Import refuse car "
                    f"{invalid_games_count}/{total_games_count} jeux contiennent au moins une erreur."
                ),
            )
        return CollectionImportRefusal(
            refused=False,
            invalid_games_count=invalid_games_count,
            total_games_count=total_games_count,
        )
