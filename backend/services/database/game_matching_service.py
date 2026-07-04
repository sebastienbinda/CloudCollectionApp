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
from datetime import date, datetime

from services.collection.imports import CollectionImportGame
from services.matching import GameTitleMatchingResult, explain_game_name_matching
from services.users import UserCollectionNameNormalizer

from .game_matching_configuration import GameMatchingConfiguration
from .game_release_date_score_adjuster import GameReleaseDateScoreAdjuster

GamePlatformIndex = dict[str, list[tuple]]


@dataclass(frozen=True)
class GameMatchingCandidate:
    """Decrit le meilleur candidat de matching trouve pour un jeu importe.

    Attributes:
        game_name (str): Nom lisible du jeu existant candidat.
        score (int): Score de similarite calcule.
        decision (str): Decision explicable du matching.
        rule (str): Regle de matching appliquee.
        reason (str): Raison explicative du matching.
    """

    game_name: str
    score: int
    decision: str = ""
    rule: str = ""
    reason: str = ""


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
        release_date_score_adjuster: GameReleaseDateScoreAdjuster | None = None,
    ):
        """Initialise le service de matching des jeux.

        Args:
            configuration (GameMatchingConfiguration | None): Seuils de matching des jeux.
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur metier.
            release_date_score_adjuster (GameReleaseDateScoreAdjuster | None): Ajusteur de
                score selon les dates de sortie.

        Returns:
            None: Le constructeur ne retourne aucune valeur.

        Raises:
            ValueError: Si les seuils de matching sont invalides.
        """

        self.configuration = configuration or GameMatchingConfiguration.from_environment()
        self.configuration.validate()
        self.name_normalizer = name_normalizer or UserCollectionNameNormalizer()
        self.release_date_score_adjuster = (
            release_date_score_adjuster or GameReleaseDateScoreAdjuster()
        )

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
        return self._evaluate_high_confidence_match(
            imported_key,
            game.release_date,
            games_by_platform,
        )

    def build_platform_index(
        self,
        existing_game_ids: dict[tuple[str, str], int | tuple[int, str] | tuple[int, str, object]],
    ) -> GamePlatformIndex:
        """Indexe les jeux existants par plateforme normalisee.

        Args:
            existing_game_ids (dict[tuple[str, str], int | tuple[int, str] |
                tuple[int, str, object]]): Jeux par cle.

        Returns:
            GamePlatformIndex: Candidats fuzzy regroupes par plateforme.
        """

        games_by_platform: GamePlatformIndex = {}
        for (platform_key, game_name_key), game_reference in existing_game_ids.items():
            if not platform_key or not game_name_key:
                continue
            game_id, game_name, release_date = self._game_reference_values(
                game_reference,
                game_name_key,
            )
            games_by_platform.setdefault(platform_key, []).append(
                (game_name_key, game_id, game_name, release_date)
            )
        return games_by_platform

    def add_to_platform_index(
        self,
        game_key: tuple[str, str],
        game_id: int,
        game_name: str,
        games_by_platform: GamePlatformIndex,
        release_date: date | datetime | None = None,
    ) -> None:
        """Ajoute un jeu cree pendant l'import dans l'index par plateforme.

        Args:
            game_key (tuple[str, str]): Cle normalisee plateforme/jeu.
            game_id (int): Identifiant du jeu cree.
            game_name (str): Nom lisible du jeu cree.
            games_by_platform (GamePlatformIndex): Index a enrichir.
            release_date (date | datetime | None): Date de sortie du jeu cree.

        Returns:
            None: L'index est modifie en place.
        """

        platform_key, game_name_key = game_key
        if not platform_key or not game_name_key:
            return
        games_by_platform.setdefault(platform_key, []).append(
            (game_name_key, game_id, game_name, release_date)
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

    def calculate_name_score(self, imported_name: str, candidate_name: str) -> int:
        """Calcule le score metier entre deux noms de jeux.

        Args:
            imported_name (str): Nom de jeu importe.
            candidate_name (str): Nom de jeu candidat dans la Bibliotheque.

        Returns:
            int: Score de matching entre `0` et `100`.
        """

        return self.explain_name_score(imported_name, candidate_name).score

    def explain_name_score(
        self,
        imported_name: str,
        candidate_name: str,
    ) -> GameTitleMatchingResult:
        """Explique le score metier entre deux noms de jeux.

        Args:
            imported_name (str): Nom de jeu importe.
            candidate_name (str): Nom de jeu candidat dans la Bibliotheque.

        Returns:
            GameTitleMatchingResult: Score, decision et regle appliquee.

        Raises:
            Aucun.
        """

        imported_key = self.name_normalizer.comparison_key(imported_name) or ""
        candidate_key = self.name_normalizer.comparison_key(candidate_name) or ""
        return explain_game_name_matching(imported_key, candidate_key)

    def _evaluate_high_confidence_match(
        self,
        imported_key: tuple[str, str],
        imported_release_date: date | datetime | None,
        games_by_platform: GamePlatformIndex,
    ) -> GameMatchingResult:
        platform_key, game_name_key = imported_key
        if not platform_key or not game_name_key:
            return GameMatchingResult(None, None)
        candidates = []
        for indexed_candidate in games_by_platform.get(platform_key, []):
            (
                candidate_name_key,
                game_id,
                candidate_name,
                candidate_release_date,
            ) = self._indexed_candidate_values(indexed_candidate)
            matching_explanation = self.explain_name_score(game_name_key, candidate_name_key)
            score = self._matching_score(game_name_key, candidate_name_key)
            adjusted_score = self.release_date_score_adjuster.adjust_score(
                score,
                imported_release_date,
                candidate_release_date,
            )
            candidates.append(
                (
                    adjusted_score,
                    game_id,
                    candidate_name,
                    matching_explanation.decision.value,
                    matching_explanation.rule,
                    matching_explanation.reason,
                )
            )
        best_score = max(
            (score for score, _game_id, _candidate_name, _decision, _rule, _reason in candidates),
            default=0,
        )
        best_game_ids = {
            game_id
            for score, game_id, _candidate_name, _decision, _rule, _reason in candidates
            if score == best_score
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
        candidates: list[tuple[int, int, str, str, str, str]],
        best_score: int,
    ) -> GameMatchingCandidate | None:
        if not candidates:
            return None
        best_details = sorted(
            (
                candidate_name,
                decision,
                rule,
                reason,
            )
            for score, _game_id, candidate_name, decision, rule, reason in candidates
            if score == best_score
        )
        best_names = sorted(
            {
                candidate_name
                for score, _game_id, candidate_name, _decision, _rule, _reason in candidates
                if score == best_score
            }
        )
        _candidate_name, decision, rule, reason = best_details[0]
        return GameMatchingCandidate(" / ".join(best_names), best_score, decision, rule, reason)

    def _matching_score(self, imported_key: str, candidate_key: str) -> int:
        return explain_game_name_matching(imported_key, candidate_key).score

    def _game_reference_values(
        self,
        game_reference: int | tuple[int, str] | tuple[int, str, object],
        fallback_name: str,
    ) -> tuple[int, str, date | datetime | None]:
        if isinstance(game_reference, tuple):
            return (
                int(game_reference[0]),
                str(game_reference[1] or fallback_name),
                self._reference_release_date(game_reference),
            )
        return int(game_reference), fallback_name, None

    def _indexed_candidate_values(
        self,
        indexed_candidate: tuple,
    ) -> tuple[str, int, str, date | datetime | None]:
        if len(indexed_candidate) >= 3:
            return (
                str(indexed_candidate[0]),
                int(indexed_candidate[1]),
                str(indexed_candidate[2] or indexed_candidate[0]),
                self._indexed_release_date(indexed_candidate),
            )
        return (
            str(indexed_candidate[0]),
            int(indexed_candidate[1]),
            str(indexed_candidate[0]),
            None,
        )

    def _reference_release_date(
        self,
        game_reference: tuple[int, str] | tuple[int, str, object],
    ) -> date | datetime | None:
        if len(game_reference) < 3:
            return None
        return self._date_value(game_reference[2])

    def _indexed_release_date(self, indexed_candidate: tuple) -> date | datetime | None:
        if len(indexed_candidate) < 4:
            return None
        return self._date_value(indexed_candidate[3])

    def _date_value(self, value: object) -> date | datetime | None:
        if isinstance(value, (date, datetime)):
            return value
        return None
