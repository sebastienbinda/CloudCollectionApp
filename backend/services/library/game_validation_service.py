#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-01
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : service metier de moderation admin des nouveaux jeux.

from dataclasses import dataclass
from typing import Any, Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from services.database.database_configuration import DatabaseConfiguration
from services.database.game_validation_repository import SqlAlchemyGameValidationRepository

from .game_validation_user_notifier import GameValidationUserNotifier

EngineFactory = Callable[[str], Engine]


class GameValidationError(ValueError):
    """Signale une erreur de payload pour la moderation des jeux."""


@dataclass(frozen=True)
class GameValidationBatchResult:
    """Decrit le resultat d'une moderation par lot.

    Attributes:
        requested_count (int): Nombre d'identifiants demandes apres dedoublonnage.
        processed_count (int): Nombre de jeux traites.
        impacted_user_count (int): Nombre d'utilisateurs impactes par un refus.
        notification_count (int): Nombre d'emails envoyes.
        ignored_ids (list[int]): Identifiants non traites.
    """

    requested_count: int
    processed_count: int
    impacted_user_count: int = 0
    notification_count: int = 0
    ignored_ids: list[int] | None = None

    def to_dict(self, processed_key: str) -> dict[str, Any]:
        """Convertit le resultat en payload JSON.

        Args:
            processed_key (str): Nom du compteur metier traite.

        Returns:
            dict[str, Any]: Resultat serialisable.
        """

        return {
            "requested_count": self.requested_count,
            processed_key: self.processed_count,
            "impacted_user_count": self.impacted_user_count,
            "notification_count": self.notification_count,
            "ignored_ids": list(self.ignored_ids or []),
        }


class GameValidationService:
    """Orchestre la validation et le refus admin des jeux en attente."""

    BATCH_SIZE = 500

    def __init__(
        self,
        configuration: DatabaseConfiguration,
        repository: SqlAlchemyGameValidationRepository | None = None,
        engine: Engine | None = None,
        engine_factory: EngineFactory = create_engine,
        user_notifier: GameValidationUserNotifier | None = None,
    ):
        """Initialise le service de moderation des jeux.

        Args:
            configuration (DatabaseConfiguration): Configuration de connexion SQL.
            repository (SqlAlchemyGameValidationRepository | None): Repository injectable.
            engine (Engine | None): Moteur SQLAlchemy injectable en test.
            engine_factory (EngineFactory): Fabrique de moteur SQLAlchemy.
            user_notifier (GameValidationUserNotifier | None): Notifier utilisateur injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si aucune URL SQL n'est configuree.
        """

        configuration.validate()
        if engine is None and not configuration.is_database_enabled():
            raise ValueError("DATABASE_URL est requis pour moderer les jeux.")
        self.engine = engine or engine_factory(configuration.database_url)
        self.repository = repository or SqlAlchemyGameValidationRepository(
            configuration.schema_name,
        )
        self.user_notifier = user_notifier or GameValidationUserNotifier.from_environment()

    @classmethod
    def from_environment(cls):
        """Construit le service depuis l'environnement.

        Args:
            Aucun.

        Returns:
            GameValidationService: Service configure.
        """

        return cls(DatabaseConfiguration.from_environment())

    def accept_games(self, raw_game_ids: Any) -> GameValidationBatchResult:
        """Valide les jeux en attente demandes.

        Args:
            raw_game_ids (Any): Liste brute d'identifiants de jeux.

        Returns:
            GameValidationBatchResult: Compteurs de validation.

        Raises:
            GameValidationError: Si la liste d'identifiants est invalide.
        """

        game_ids = self._parse_game_ids(raw_game_ids)
        accepted_ids: list[int] = []
        with self.engine.begin() as connection:
            self.repository.lock_global_game_catalog(connection)
            for chunk in self._chunks(game_ids):
                accepted_ids.extend(self.repository.accept_waiting_games(connection, chunk))
        return GameValidationBatchResult(
            requested_count=len(game_ids),
            processed_count=len(accepted_ids),
            ignored_ids=self._ignored_ids(game_ids, accepted_ids),
        )

    def refuse_games(self, raw_game_ids: Any) -> GameValidationBatchResult:
        """Refuse les jeux en attente demandes et notifie les utilisateurs impactes.

        Args:
            raw_game_ids (Any): Liste brute d'identifiants de jeux.

        Returns:
            GameValidationBatchResult: Compteurs de refus.

        Raises:
            GameValidationError: Si la liste d'identifiants est invalide.
        """

        game_ids = self._parse_game_ids(raw_game_ids)
        refusable_games: list[dict[str, Any]] = []
        deleted_ids: list[int] = []
        deleted_collection_links = 0
        with self.engine.begin() as connection:
            self.repository.lock_global_game_catalog(connection)
            for chunk in self._chunks(game_ids):
                chunk_refusable_games = self.repository.list_refusable_games(connection, chunk)
                chunk_game_ids = self._unique_ids(row["id"] for row in chunk_refusable_games)
                deleted_collection_links += self.repository.delete_user_collection_links(
                    connection,
                    chunk_game_ids,
                )
                deleted_ids.extend(self.repository.delete_games(connection, chunk_game_ids))
                refusable_games.extend(chunk_refusable_games)
        impacted_users = self._impacted_users(refusable_games, deleted_ids)
        notification_count = self.user_notifier.notify_refused_games(impacted_users)
        return GameValidationBatchResult(
            requested_count=len(game_ids),
            processed_count=len(deleted_ids),
            impacted_user_count=len(impacted_users),
            notification_count=notification_count,
            ignored_ids=self._ignored_ids(game_ids, deleted_ids),
        )

    def _parse_game_ids(self, raw_game_ids: Any) -> list[int]:
        if not isinstance(raw_game_ids, list):
            raise GameValidationError("game_ids doit etre une liste d'identifiants.")
        game_ids = []
        for raw_game_id in raw_game_ids:
            try:
                game_id = int(raw_game_id)
            except (TypeError, ValueError) as exc:
                raise GameValidationError("game_ids doit contenir uniquement des entiers.") from exc
            if game_id <= 0:
                raise GameValidationError("game_ids doit contenir uniquement des entiers positifs.")
            game_ids.append(game_id)
        if not game_ids:
            raise GameValidationError("game_ids doit contenir au moins un identifiant.")
        return self._unique_ids(game_ids)

    def _chunks(self, game_ids: list[int]):
        for start_index in range(0, len(game_ids), self.BATCH_SIZE):
            yield game_ids[start_index:start_index + self.BATCH_SIZE]

    def _unique_ids(self, game_ids) -> list[int]:
        unique_game_ids: list[int] = []
        seen_game_ids = set()
        for game_id in game_ids:
            normalized_game_id = int(game_id)
            if normalized_game_id in seen_game_ids:
                continue
            seen_game_ids.add(normalized_game_id)
            unique_game_ids.append(normalized_game_id)
        return unique_game_ids

    def _ignored_ids(self, requested_ids: list[int], processed_ids: list[int]) -> list[int]:
        processed_set = {int(game_id) for game_id in processed_ids}
        return [game_id for game_id in requested_ids if game_id not in processed_set]

    def _impacted_users(
        self,
        refusable_games: list[dict[str, Any]],
        deleted_ids: list[int],
    ) -> list[dict[str, Any]]:
        deleted_id_set = {int(game_id) for game_id in deleted_ids}
        users_by_id: dict[int, dict[str, Any]] = {}
        for row in refusable_games:
            user_id = row.get("user_id")
            if user_id is None or int(row["id"]) not in deleted_id_set:
                continue
            normalized_user_id = int(user_id)
            impacted_user = users_by_id.setdefault(
                normalized_user_id,
                {
                    "user_id": normalized_user_id,
                    "user_email": str(row.get("user_email") or ""),
                    "games": [],
                },
            )
            impacted_user["games"].append({
                "id": int(row["id"]),
                "name": str(row.get("name") or ""),
                "platform_name": str(row.get("platform_name") or ""),
            })
        return list(users_by_id.values())
