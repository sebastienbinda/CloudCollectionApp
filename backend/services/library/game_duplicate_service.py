#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : service metier de signalement et correction des doublons de jeux.

import logging
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from services.database.database_configuration import DatabaseConfiguration
from services.database.game_duplicate_repository import SqlAlchemyGameDuplicateRepository
from services.database.game_repository import SqlAlchemyGameRepository
from services.users import UserCollectionNameNormalizer

from .game_duplicate_user_notifier import GameDuplicateUserNotifier
from .library_query_contract import LibraryPageRequest, LibraryQueryCriteria, LibrarySortRule

EngineFactory = Callable[[str], Engine]


class GameDuplicateError(ValueError):
    """Signale une erreur metier pendant la gestion des doublons de jeux."""


class GameDuplicateNotFoundError(GameDuplicateError):
    """Signale l'absence d'un jeu implique dans une operation de doublon."""


class GameDuplicatePermissionError(PermissionError):
    """Signale qu'un utilisateur ne peut pas signaler ce jeu comme doublon."""


@dataclass(frozen=True)
class GameDuplicateMergeResult:
    """Decrit le resultat d'une fusion de doublon.

    Attributes:
        duplicate_game_id (int): Identifiant du jeu supprime.
        target_game_id (int): Identifiant du jeu conserve.
        remapped_user_count (int): Nombre d'utilisateurs concernes par le remapping.
        updated_collection_rows (int): Nombre de rattachements simplement remappes.
        merged_collection_rows (int): Nombre de rattachements fusionnes.
        alias_created (bool): Indique si un alias a ete cree.
        deleted_duplicate (bool): Indique si le doublon a ete supprime.
        processing_time_ms (int): Duree de traitement en millisecondes.
    """

    duplicate_game_id: int
    target_game_id: int
    remapped_user_count: int
    updated_collection_rows: int
    merged_collection_rows: int
    alias_created: bool
    deleted_duplicate: bool
    processing_time_ms: int

    def to_dict(self) -> dict[str, Any]:
        """Convertit le resultat en payload JSON.

        Args:
            Aucun.

        Returns:
            dict[str, Any]: Resultat serialisable.
        """

        return {
            "action": "merge",
            "duplicate_game_id": self.duplicate_game_id,
            "target_game_id": self.target_game_id,
            "remapped_user_count": self.remapped_user_count,
            "updated_collection_rows": self.updated_collection_rows,
            "merged_collection_rows": self.merged_collection_rows,
            "alias_created": self.alias_created,
            "deleted_duplicate": self.deleted_duplicate,
            "processing_time_ms": self.processing_time_ms,
        }


class GameDuplicateService:
    """Orchestre les signalements et corrections de doublons de jeux."""

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        repository: SqlAlchemyGameDuplicateRepository | None = None,
        game_repository: SqlAlchemyGameRepository | None = None,
        engine: Engine | None = None,
        engine_factory: EngineFactory = create_engine,
        name_normalizer: UserCollectionNameNormalizer | None = None,
        user_notifier: GameDuplicateUserNotifier | None = None,
        logger: logging.Logger | None = None,
    ):
        """Initialise le service de doublons de jeux.

        Args:
            configuration (DatabaseConfiguration): Configuration de connexion SQL.
            repository (SqlAlchemyGameDuplicateRepository | None): Repository injectable.
            game_repository (SqlAlchemyGameRepository | None): Repository de recherche des jeux.
            engine (Engine | None): Moteur SQLAlchemy injectable en test.
            engine_factory (EngineFactory): Fabrique de moteur SQLAlchemy.
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur de recherche.
            user_notifier (GameDuplicateUserNotifier | None): Notifier utilisateur injectable.
            logger (logging.Logger | None): Journal applicatif injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si aucune URL SQL n'est configuree.
        """

        configuration.validate()
        if engine is None and not configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour gerer les doublons.")
        self.engine = engine or engine_factory(configuration.database_url)
        self.name_normalizer = name_normalizer or UserCollectionNameNormalizer()
        self.repository = repository or SqlAlchemyGameDuplicateRepository(
            configuration.schema_name,
        )
        self.game_repository = game_repository or SqlAlchemyGameRepository(
            configuration.schema_name,
            self.name_normalizer,
        )
        self.user_notifier = user_notifier or GameDuplicateUserNotifier.from_environment()
        self.logger = logger or logging.getLogger(__name__)

    def report_duplicate(self, user_id: int, game_id: int) -> dict[str, Any]:
        """Signale un jeu de la collection utilisateur comme doublon.

        Args:
            user_id (int): Identifiant de l'utilisateur connecte.
            game_id (int): Identifiant du jeu signale.

        Returns:
            dict[str, Any]: Payload de confirmation.

        Raises:
            GameDuplicatePermissionError: Si l'utilisateur n'a pas encore de collection.
            GameDuplicateNotFoundError: Si le jeu n'existe pas.
        """

        with self.engine.begin() as connection:
            if not self.repository.game_exists(connection, game_id):
                raise GameDuplicateNotFoundError("Game not found.")
            if not self.repository.user_has_collection(connection, user_id):
                raise GameDuplicatePermissionError(
                    "Une collection importee est requise pour signaler un doublon."
                )
            self.repository.mark_game_as_duplicate(connection, game_id)
        return {"game_id": game_id, "duplicate_flag": True}

    def get_duplicate_game(self, game_id: int) -> dict[str, Any]:
        """Retourne un jeu destine a la correction de doublon.

        Args:
            game_id (int): Identifiant du jeu signale.

        Returns:
            dict[str, Any]: Jeu administrable.

        Raises:
            GameDuplicateNotFoundError: Si le jeu est absent.
        """

        with self.engine.connect() as connection:
            game = self.repository.find_game_for_duplicate_management(connection, game_id)
        if game is None:
            raise GameDuplicateNotFoundError("Game not found.")
        return self._game_payload(game)

    def search_candidates(
        self,
        duplicate_game_id: int,
        name_query: str = "",
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Recherche des candidats de fusion sur la meme plateforme.

        Args:
            duplicate_game_id (int): Identifiant du jeu signale.
            name_query (str): Filtre optionnel sur le nom.
            limit (int): Nombre maximal de candidats.

        Returns:
            list[dict[str, Any]]: Candidats serialisables.
        """

        with self.engine.connect() as connection:
            duplicate_game = self.repository.find_game_for_duplicate_management(
                connection,
                duplicate_game_id,
            )
            if duplicate_game is None:
                raise GameDuplicateNotFoundError("Game not found.")
            criteria = self._candidate_search_criteria(duplicate_game, name_query, limit)
            rows = self.game_repository.list_public_library_games(connection, criteria)
        candidates = [
            row for row in rows
            if int(row.get("id") or 0) != int(duplicate_game_id)
        ][:max(1, min(int(limit), 100))]
        return [self._game_payload(row) for row in candidates]

    def reject_duplicate(self, duplicate_game_id: int) -> dict[str, Any]:
        """Refuse un signalement de doublon.

        Args:
            duplicate_game_id (int): Identifiant du jeu signale.

        Returns:
            dict[str, Any]: Payload de confirmation.

        Raises:
            GameDuplicateNotFoundError: Si aucun signalement actif n'existe.
        """

        start_time = perf_counter()
        with self.engine.begin() as connection:
            self.repository.lock_global_game_catalog(connection)
            updated = self.repository.reject_duplicate(connection, duplicate_game_id)
        if not updated:
            raise GameDuplicateNotFoundError("Duplicate report not found.")
        return {
            "action": "reject",
            "duplicate_game_id": duplicate_game_id,
            "duplicate_flag": False,
            "processing_time_ms": self._elapsed_ms(start_time),
        }

    def merge_duplicate(
        self,
        duplicate_game_id: int,
        target_game_id: int,
        selected_values: dict[str, Any] | None = None,
        keep_duplicate_name_as_alias: bool = True,
    ) -> GameDuplicateMergeResult:
        """Fusionne un jeu signale dans un jeu conserve.

        Args:
            duplicate_game_id (int): Identifiant du jeu a supprimer.
            target_game_id (int): Identifiant du jeu conserve.
            selected_values (dict[str, Any] | None): Valeurs cible choisies.
            keep_duplicate_name_as_alias (bool): Ajoute le nom supprime comme alias.

        Returns:
            GameDuplicateMergeResult: Compteurs de fusion.

        Raises:
            GameDuplicateError: Si les deux jeux ne peuvent pas etre fusionnes.
            GameDuplicateNotFoundError: Si un jeu est absent.
        """

        start_time = perf_counter()
        if duplicate_game_id == target_game_id:
            raise GameDuplicateError("Le jeu doublon et le jeu conserve doivent etre differents.")
        impacted_users = []
        should_notify_impacted_users = False
        with self.engine.begin() as connection:
            self.repository.lock_global_game_catalog(connection)
            duplicate_game = self.repository.find_game_for_duplicate_management(
                connection,
                duplicate_game_id,
            )
            target_game = self.repository.find_game_for_duplicate_management(connection, target_game_id)
            if duplicate_game is None or target_game is None:
                raise GameDuplicateNotFoundError("Game not found.")
            if duplicate_game.get("platform") != target_game.get("platform"):
                raise GameDuplicateError("Les deux jeux doivent appartenir a la meme plateforme.")
            should_notify_impacted_users = bool(duplicate_game.get("duplicate_flag"))
            if should_notify_impacted_users:
                impacted_users = self.repository.list_users_impacted_by_merge(
                    connection,
                    duplicate_game_id,
                    target_game_id,
                )
            remapped_user_count = self.repository.count_users_with_game(
                connection,
                duplicate_game_id,
            )
            alias_created = False
            if keep_duplicate_name_as_alias:
                alias_created = self.repository.insert_game_alias(
                    connection,
                    target_game_id,
                    str(duplicate_game.get("name") or ""),
                )
            self.repository.update_game_values(connection, target_game_id, selected_values or {})
            collection_counts = self.repository.remap_user_collections(
                connection,
                duplicate_game_id,
                target_game_id,
            )
            deleted_duplicate = self.repository.delete_game(connection, duplicate_game_id)
        result = GameDuplicateMergeResult(
            duplicate_game_id=duplicate_game_id,
            target_game_id=target_game_id,
            remapped_user_count=remapped_user_count,
            updated_collection_rows=collection_counts["updated_rows"],
            merged_collection_rows=collection_counts["merged_rows"],
            alias_created=alias_created,
            deleted_duplicate=deleted_duplicate,
            processing_time_ms=self._elapsed_ms(start_time),
        )
        if should_notify_impacted_users:
            self._notify_impacted_users(impacted_users, duplicate_game, target_game)
        return result

    @classmethod
    def from_environment(cls):
        """Construit le service depuis l'environnement.

        Args:
            Aucun.

        Returns:
            GameDuplicateService: Service configure.
        """

        return cls(DatabaseConfiguration.from_environment())

    def _game_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": int(row["id"]),
            "name": str(row.get("name") or ""),
            "release_date": str(row.get("release_date") or ""),
            "developer": row.get("developer_name", row.get("developer")) or "",
            "developer_id": row.get("developer_id", row.get("developer")) or None,
            "editor": row.get("editor_name", row.get("editor")) or "",
            "editor_id": row.get("editor_id", row.get("editor")) or None,
            "platform": row.get("platform_name", row.get("platform")) or "",
            "platform_id": row.get("platform_id", row.get("platform")) or None,
            "description": row.get("description") or "",
            "duplicate_flag": bool(row.get("duplicate_flag")),
        }

    def _candidate_search_criteria(
        self,
        duplicate_game: dict[str, Any],
        name_query: str,
        limit: int,
    ) -> LibraryQueryCriteria:
        platform_name = str(duplicate_game.get("platform_name") or "")
        requested_limit = max(1, min(int(limit), 100))
        return LibraryQueryCriteria(
            page_request=LibraryPageRequest(page=0, size=requested_limit + 1),
            name=self.name_normalizer.stored_value(name_query) or "",
            normalized_name=self.name_normalizer.comparison_key(name_query) or "",
            platform=platform_name,
            normalized_platform=self.name_normalizer.comparison_key(platform_name) or "",
            duplicate_flag=None,
            sort_rules=(LibrarySortRule("name", "asc"),),
        )

    def _elapsed_ms(self, start_time: float) -> int:
        return int(round((perf_counter() - start_time) * 1000))

    def _notify_impacted_users(
        self,
        impacted_users: list[dict[str, Any]],
        duplicate_game: dict[str, Any],
        target_game: dict[str, Any],
    ) -> None:
        try:
            self.user_notifier.notify_merge(impacted_users, duplicate_game, target_game)
        except Exception:
            self.logger.exception(
                "Impossible d'envoyer la notification utilisateur de fusion de doublon."
            )
