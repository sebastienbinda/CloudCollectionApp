#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : matching centralise des jeux importes avec le referentiel.

from dataclasses import dataclass

from services.collection.imports import CollectionImportGame
from services.matching import matching_score
from services.users import UserCollectionNameNormalizer

from .game_matching_configuration import GameMatchingConfiguration

GamePlatformIndex = dict[str, list[tuple]]


@dataclass(frozen=True)
class GameMatchingCandidate:
    """Decrit le meilleur candidat de matching trouve pour un jeu importe.

    Attributes:
        game_name (str): Nom lisible du jeu existant candidat.
        score (int): Score de similarite calcule.
    """

    game_name: str
    score: int


@dataclass(frozen=True)
class GameMatchingResult:
    """Regroupe la decision de rattachement et son meilleur candidat.

    Attributes:
        existing_game_id (int | None): Identifiant retenu ou absence de rattachement.
        best_candidate (GameMatchingCandidate | None): Meilleur candidat evalue.
    """

    existing_game_id: int | None
    best_candidate: GameMatchingCandidate | None


class GameMatchingService:
    """Rattache un jeu importe a un jeu existant de la meme plateforme."""

    def __init__(
        self,
        configuration: GameMatchingConfiguration | None = None,
        name_normalizer: UserCollectionNameNormalizer | None = None,
    ):
        """Initialise le service de matching des jeux.

        Args:
            configuration (GameMatchingConfiguration | None): Seuils de matching des jeux.
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur metier.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si les seuils de matching sont invalides.
        """

        self.configuration = configuration or GameMatchingConfiguration.from_environment()
        self.configuration.validate()
        self.name_normalizer = name_normalizer or UserCollectionNameNormalizer()

    def find_existing_game_id(
        self,
        game: CollectionImportGame,
        existing_game_ids: dict[tuple[str, str], int],
        games_by_platform: GamePlatformIndex,
    ) -> int | None:
        """Recherche un jeu existant par cle exacte puis par score unique.

        Args:
            game (CollectionImportGame): Jeu importe a rattacher.
            existing_game_ids (dict[tuple[str, str], int]): Identifiants par cle plateforme/jeu.
            games_by_platform (GamePlatformIndex): Jeux existants indexes par plateforme.

        Returns:
            int | None: Identifiant du jeu existant retenu, ou `None`.
        """

        return self.evaluate_existing_game(
            game,
            existing_game_ids,
            games_by_platform,
        ).existing_game_id

    def evaluate_existing_game(
        self,
        game: CollectionImportGame,
        existing_game_ids: dict[tuple[str, str], int],
        games_by_platform: GamePlatformIndex,
    ) -> GameMatchingResult:
        """Evalue le rattachement d'un jeu et conserve le meilleur candidat.

        Args:
            game (CollectionImportGame): Jeu importe a rattacher.
            existing_game_ids (dict[tuple[str, str], int]): Identifiants par cle plateforme/jeu.
            games_by_platform (GamePlatformIndex): Jeux existants indexes par plateforme.

        Returns:
            GameMatchingResult: Decision de rattachement et meilleur candidat.
        """

        imported_key = self.game_key(game)
        exact_match_id = existing_game_ids.get(imported_key)
        if exact_match_id is not None:
            return GameMatchingResult(exact_match_id, None)
        return self._evaluate_high_confidence_match(imported_key, games_by_platform)

    def build_platform_index(
        self,
        existing_game_ids: dict[tuple[str, str], int | tuple[int, str]],
    ) -> GamePlatformIndex:
        """Indexe les jeux existants par plateforme normalisee.

        Args:
            existing_game_ids (dict[tuple[str, str], int | tuple[int, str]]): Jeux par cle.

        Returns:
            GamePlatformIndex: Candidats fuzzy regroupes par plateforme.
        """

        games_by_platform: GamePlatformIndex = {}
        for (platform_key, game_name_key), game_reference in existing_game_ids.items():
            if not platform_key or not game_name_key:
                continue
            game_id, game_name = self._game_reference_values(game_reference, game_name_key)
            games_by_platform.setdefault(platform_key, []).append(
                (game_name_key, game_id, game_name)
            )
        return games_by_platform

    def add_to_platform_index(
        self,
        game_key: tuple[str, str],
        game_id: int,
        game_name: str,
        games_by_platform: GamePlatformIndex,
    ) -> None:
        """Ajoute un jeu cree pendant l'import dans l'index par plateforme.

        Args:
            game_key (tuple[str, str]): Cle normalisee plateforme/jeu.
            game_id (int): Identifiant du jeu cree.
            game_name (str): Nom lisible du jeu cree.
            games_by_platform (GamePlatformIndex): Index a enrichir.

        Returns:
            None: L'index est modifie en place.
        """

        platform_key, game_name_key = game_key
        if not platform_key or not game_name_key:
            return
        games_by_platform.setdefault(platform_key, []).append(
            (game_name_key, game_id, game_name)
        )

    def game_key(self, game: CollectionImportGame) -> tuple[str, str]:
        """Construit la cle normalisee d'un jeu importe.

        Args:
            game (CollectionImportGame): Jeu importe.

        Returns:
            tuple[str, str]: Cle plateforme/nom normalisee.
        """

        return (
            self.name_normalizer.comparison_key(game.platform_name) or "",
            self.name_normalizer.comparison_key(game.name) or "",
        )

    def _evaluate_high_confidence_match(
        self,
        imported_key: tuple[str, str],
        games_by_platform: GamePlatformIndex,
    ) -> GameMatchingResult:
        platform_key, game_name_key = imported_key
        if not platform_key or not game_name_key:
            return GameMatchingResult(None, None)
        candidates = []
        for indexed_candidate in games_by_platform.get(platform_key, []):
            candidate_name_key, game_id, candidate_name = self._indexed_candidate_values(
                indexed_candidate
            )
            candidates.append(
                (
                    self._matching_score(game_name_key, candidate_name_key),
                    game_id,
                    candidate_name,
                )
            )
        best_score = max((score for score, _game_id, _candidate_name in candidates), default=0)
        best_game_ids = {
            game_id for score, game_id, _candidate_name in candidates if score == best_score
        }
        best_candidate = self._best_candidate(candidates, best_score)
        if best_score < self.configuration.low_level_rating:
            return GameMatchingResult(None, best_candidate)
        if (
            best_score >= self.configuration.high_level_rating
            and len(best_game_ids) == 1
        ):
            return GameMatchingResult(next(iter(best_game_ids)), best_candidate)
        return GameMatchingResult(None, best_candidate)

    def _best_candidate(
        self,
        candidates: list[tuple[int, int, str]],
        best_score: int,
    ) -> GameMatchingCandidate | None:
        if not candidates:
            return None
        best_names = sorted(
            {
                candidate_name
                for score, _game_id, candidate_name in candidates
                if score == best_score
            }
        )
        return GameMatchingCandidate(" / ".join(best_names), best_score)

    def _matching_score(self, imported_key: str, candidate_key: str) -> int:
        return matching_score(imported_key, candidate_key)

    def _game_reference_values(
        self,
        game_reference: int | tuple[int, str],
        fallback_name: str,
    ) -> tuple[int, str]:
        if isinstance(game_reference, tuple):
            return int(game_reference[0]), str(game_reference[1] or fallback_name)
        return int(game_reference), fallback_name

    def _indexed_candidate_values(self, indexed_candidate: tuple) -> tuple[str, int, str]:
        if len(indexed_candidate) >= 3:
            return (
                str(indexed_candidate[0]),
                int(indexed_candidate[1]),
                str(indexed_candidate[2] or indexed_candidate[0]),
            )
        return (
            str(indexed_candidate[0]),
            int(indexed_candidate[1]),
            str(indexed_candidate[0]),
        )
