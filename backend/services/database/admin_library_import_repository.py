#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-26
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : persistance SQL de l'import CSV admin Bibliotheque.

from dataclasses import dataclass

from services.collection.imports import CollectionImportData

from .user_collection_import_repository import SqlAlchemyUserCollectionImportRepository


@dataclass(frozen=True)
class AdminLibraryImportPersistenceResult:
    """Regroupe les compteurs SQL d'un import admin Bibliotheque.

    Attributes:
        linked_platforms (int): Nombre de plateformes du referentiel liees.
        created_studios (int): Nombre de studios crees.
        created_games (int): Nombre de jeux crees.
    """

    linked_platforms: int
    created_studios: int
    created_games: int


class SqlAlchemyAdminLibraryImportRepository(SqlAlchemyUserCollectionImportRepository):
    """Importe des jeux dans la Bibliotheque globale sans collection utilisateur."""

    def import_library(
        self,
        import_data: CollectionImportData,
    ) -> AdminLibraryImportPersistenceResult:
        """Persiste les plateformes rattachees, studios et jeux importes.

        Args:
            import_data (CollectionImportData): Donnees CSV deja lues et validees.

        Returns:
            AdminLibraryImportPersistenceResult: Compteurs de persistance.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: Si la transaction SQL echoue.
        """

        with self.engine.begin() as connection:
            self._lock_global_game_import_state(connection)
            matched_import_data = self._match_platforms(connection, import_data)
            self._synchronize_import_data(import_data, matched_import_data)
            platform_ids, linked_platforms = self._ensure_platforms(
                connection,
                matched_import_data,
            )
            studio_ids, created_studios = self._ensure_studios(connection, matched_import_data)
            _, created_games, _created_game_match_reports, _imported_game_match_reports = (
                self._ensure_games(
                    connection,
                    matched_import_data,
                    platform_ids,
                    studio_ids,
                )
            )
        self.platform_repository.invalidate_cache()
        return AdminLibraryImportPersistenceResult(
            linked_platforms=linked_platforms,
            created_studios=created_studios,
            created_games=created_games,
        )
