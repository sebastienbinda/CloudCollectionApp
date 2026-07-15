#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-07-15
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : matching des studios importes avec le referentiel.

from dataclasses import dataclass

from services.matching import matching_score
from services.users.user_collection_name_normalizer import UserCollectionNameNormalizer

from .studio_matching_configuration import StudioMatchingConfiguration


@dataclass(frozen=True)
class StudioMatchingResult:
    """Decrit le resultat de matching d'un studio importe.

    Attributes:
        matched_key (str | None): Cle du studio existant retenu.
        score (int): Score du meilleur candidat.
        accepted (bool): Indique si le candidat existant est accepte.
    """

    matched_key: str | None
    score: int
    accepted: bool


class StudioMatchingService:
    """Rattache les studios importes aux studios applicatifs existants."""

    STUDIO_SUFFIX_ALTERNATIVES = ("entertainment", "game", "games", "studio", "studios")
    STUDIO_SUFFIX_ALTERNATIVE_MIN_SCORE = 70

    def __init__(
        self,
        configuration: StudioMatchingConfiguration | None = None,
        name_normalizer: UserCollectionNameNormalizer | None = None,
    ):
        """Initialise le service de matching studios.

        Args:
            configuration (StudioMatchingConfiguration | None): Seuils de matching.
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur metier.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration or StudioMatchingConfiguration.from_environment()
        self.configuration.validate()
        self.name_normalizer = name_normalizer or UserCollectionNameNormalizer()

    def match_existing_studio_key(
        self,
        imported_studio_name: str,
        existing_studio_ids: dict[str, int],
    ) -> str | None:
        """Retourne la cle existante correspondant au studio importe.

        Args:
            imported_studio_name (str): Nom de studio lu depuis le fichier.
            existing_studio_ids (dict[str, int]): Studios existants par cle normalisee.

        Returns:
            str | None: Cle existante acceptee, ou `None` si aucune correspondance fiable.
        """

        imported_key = self._comparison_key(imported_studio_name)
        if not imported_key:
            return None
        return self.evaluate_existing_studio(imported_studio_name, existing_studio_ids).matched_key

    def evaluate_existing_studio(
        self,
        imported_studio_name: str,
        existing_studio_ids: dict[str, int],
    ) -> StudioMatchingResult:
        """Evalue le meilleur studio existant pour un studio importe.

        Args:
            imported_studio_name (str): Nom de studio lu depuis le fichier.
            existing_studio_ids (dict[str, int]): Studios existants par cle normalisee.

        Returns:
            StudioMatchingResult: Cle retenue, score et decision d'acceptation.
        """

        imported_key = self._comparison_key(imported_studio_name)
        if not imported_key:
            return StudioMatchingResult(None, 0, False)
        if imported_key in existing_studio_ids:
            return StudioMatchingResult(imported_key, 100, True)
        return self._best_unique_existing_result(imported_key, existing_studio_ids)

    def _best_unique_existing_result(
        self,
        imported_key: str,
        existing_studio_ids: dict[str, int],
    ) -> StudioMatchingResult:
        scored_keys = [
            (self._studio_matching_score(imported_key, candidate_key), candidate_key)
            for candidate_key in existing_studio_ids
        ]
        best_score = max((score for score, _candidate_key in scored_keys), default=0)
        if best_score < self.configuration.high_level_rating:
            return StudioMatchingResult(None, best_score, False)
        best_keys = [
            candidate_key
            for score, candidate_key in scored_keys
            if score == best_score
        ]
        if len(best_keys) != 1:
            return StudioMatchingResult(None, best_score, False)
        return StudioMatchingResult(best_keys[0], best_score, True)

    def _studio_matching_score(self, imported_key: str, candidate_key: str) -> int:
        imported_words = self._words(imported_key)
        candidate_words = self._words(candidate_key)
        if self._has_suffix_alternative_equivalence(imported_words, candidate_words):
            return 100
        return matching_score(imported_key, candidate_key)

    def _has_suffix_alternative_equivalence(
        self,
        imported_words: list[str],
        candidate_words: list[str],
    ) -> bool:
        imported_base_words = self._without_studio_suffix(imported_words)
        candidate_base_words = self._without_studio_suffix(candidate_words)
        if imported_base_words == imported_words and candidate_base_words == candidate_words:
            return False
        imported_base_key = " ".join(imported_base_words)
        candidate_base_key = " ".join(candidate_base_words)
        if not imported_base_key or not candidate_base_key:
            return False
        return matching_score(imported_base_key, candidate_base_key) >= (
            self.configuration.high_level_rating
        )

    def _without_studio_suffix(self, words: list[str]) -> list[str]:
        if not words or not self._is_studio_suffix_alternative(words[-1]):
            return list(words)
        return list(words[:-1])

    def _is_studio_suffix_alternative(self, word: str) -> bool:
        return any(
            matching_score(word, suffix) >= self.STUDIO_SUFFIX_ALTERNATIVE_MIN_SCORE
            for suffix in self.STUDIO_SUFFIX_ALTERNATIVES
        )

    def _comparison_key(self, value: object) -> str:
        return self.name_normalizer.comparison_key(value) or ""

    def _words(self, value: str) -> list[str]:
        return [word for word in str(value).split() if word]
