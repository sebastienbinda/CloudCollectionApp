#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
# Projet : CloudCollectionApp
# Date de creation : 2026-08-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : validation metier des associations creees pendant un import utilisateur.

from services.collection.imports import CollectionImportData
from services.database.user_collection_import_persistence_result import (
    UserCollectionImportPersistenceResult,
)

from .user_collection_import_errors import UserCollectionImportInvalidFileError


class UserCollectionImportAssociationValidator:
    """Valide que les donnees lues produisent au moins une association utilisateur."""

    def ensure_games_read(self, import_data: CollectionImportData) -> None:
        """Refuse un import dont aucun jeu importable n'a ete lu.

        Args:
            import_data (CollectionImportData): Donnees lues depuis le fichier.

        Returns:
            None: Ne retourne rien si au moins un jeu est lisible.

        Raises:
            UserCollectionImportInvalidFileError: Si aucun jeu importable n'est trouve.
        """

        if import_data.games:
            return
        raise UserCollectionImportInvalidFileError(
            "Fichier de collection invalide.",
            [
                "Aucun jeu importable n'a ete trouve dans le fichier. Verifiez que les "
                "colonnes obligatoires Nom du jeu et Plateforme sont correctement configurees."
            ],
        )

    def validate(
        self,
        import_data: CollectionImportData,
        persistence_result: UserCollectionImportPersistenceResult,
    ) -> None:
        """Refuse un import dont aucun jeu lu ne peut etre associe.

        Args:
            import_data (CollectionImportData): Donnees lues depuis le fichier.
            persistence_result (UserCollectionImportPersistenceResult): Compteurs SQL.

        Returns:
            None: Ne retourne rien si au moins un jeu est associe.

        Raises:
            UserCollectionImportInvalidFileError: Si les jeux lus sont tous ecartes.
        """

        self.ensure_games_read(import_data)
        if persistence_result.associated_games > 0:
            return

        detail = (
            "Aucun jeu n'a ete associe a la collection. Verifiez que les colonnes "
            "obligatoires Nom du jeu et Plateforme sont correctement configurees."
        )
        skipped_platforms = self._skipped_platforms(import_data)
        if skipped_platforms:
            detail = (
                f"{detail} Plateformes lues mais non reconnues: "
                f"{', '.join(skipped_platforms)}."
            )
        raise UserCollectionImportInvalidFileError(
            "Fichier de collection invalide.",
            [detail],
        )

    def _skipped_platforms(self, import_data: CollectionImportData) -> list[str]:
        platforms = {
            str(skipped_game.get("imported_platform") or "").strip()
            for skipped_game in import_data.warnings.skipped_games
            if str(skipped_game.get("imported_platform") or "").strip()
        }
        return sorted(platforms)
