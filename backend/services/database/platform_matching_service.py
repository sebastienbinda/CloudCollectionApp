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
# Description : matching des plateformes importees avec le referentiel.

from difflib import SequenceMatcher

from services.collection.imports import (
    CollectionImportData,
    CollectionImportGame,
    CollectionImportPlatform,
    CollectionImportWarnings,
)
from services.users import UserCollectionNameNormalizer

from .platform_matching_configuration import PlatformMatchingConfiguration


class PlatformMatchingService:
    """Rattache les plateformes importees au catalogue applicatif existant."""

    def __init__(
        self,
        configuration: PlatformMatchingConfiguration | None = None,
        name_normalizer: UserCollectionNameNormalizer | None = None,
    ):
        """Initialise le service de matching plateformes.

        Args:
            configuration (PlatformMatchingConfiguration | None): Seuils de matching.
            name_normalizer (UserCollectionNameNormalizer | None): Normaliseur metier.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration or PlatformMatchingConfiguration.from_environment()
        self.configuration.validate()
        self.name_normalizer = name_normalizer or UserCollectionNameNormalizer()

    def match_import_data(
        self,
        import_data: CollectionImportData,
        platform_rows: list[dict[str, object]],
    ) -> CollectionImportData:
        """Remplace les plateformes importees par les plateformes du catalogue.

        Args:
            import_data (CollectionImportData): Donnees lues depuis le fichier.
            platform_rows (list[dict[str, object]]): Plateformes candidates.

        Returns:
            CollectionImportData: Donnees filtrees et rattachees.
        """

        matches_by_key = self._build_matches_by_imported_platform(import_data, platform_rows)
        warnings = self._copy_warnings(import_data.warnings)
        matched_games = []
        for game in import_data.games:
            platform_key = self._compact_key(game.platform_name)
            match = matches_by_key.get(platform_key)
            if match is None or not match["accepted"]:
                warnings.skipped_games.append(self._skipped_game_warning(game, match))
                continue
            matched_games.append(self._matched_game(game, str(match["matched_name"])))
            if match["manual_check"]:
                warnings.platform_matches.append(self._platform_match_warning(game, match))
        matched_platform_names = self._matched_platform_names(matched_games)
        return CollectionImportData(
            platforms=[CollectionImportPlatform(name) for name in matched_platform_names],
            studios=self._matched_studios(import_data, matched_games),
            games=matched_games,
            warnings=warnings,
        )

    def _build_matches_by_imported_platform(
        self,
        import_data: CollectionImportData,
        platform_rows: list[dict[str, object]],
    ) -> dict[str, dict[str, object]]:
        rows = list(platform_rows)
        return {
            self._compact_key(platform.name): self._match_platform(platform.name, rows)
            for platform in import_data.platforms
        }

    def _match_platform(
        self,
        imported_platform: str,
        platform_rows: list[dict[str, object]],
    ) -> dict[str, object]:
        imported_key = self._compact_key(imported_platform)
        scored_rows = [
            (self._matching_score(imported_key, self._compact_key(row["name"])), row)
            for row in platform_rows
        ]
        scored_rows.sort(key=lambda scored_row: scored_row[0], reverse=True)
        best_score = scored_rows[0][0] if scored_rows else 0
        best_rows = [row for score, row in scored_rows if score == best_score]
        if best_score == 0:
            return self._match_result(imported_platform, "", 0, False, False, "no_match")
        if len(best_rows) > 1:
            return self._match_result(imported_platform, "", best_score, False, False, "ambiguous")
        matched_name = str(best_rows[0]["name"])
        if best_score >= self.configuration.high_level_rating:
            return self._match_result(imported_platform, matched_name, best_score, True, False, "")
        if best_score >= self.configuration.low_level_rating:
            return self._match_result(imported_platform, matched_name, best_score, True, True, "")
        return self._match_result(imported_platform, matched_name, best_score, False, False, "low_score")

    def _matching_score(self, imported_key: str, candidate_key: str) -> int:
        if imported_key == candidate_key:
            return 100
        if not imported_key or not candidate_key:
            return 0
        return int(round(SequenceMatcher(None, imported_key, candidate_key).ratio() * 100))

    def _compact_key(self, value: object) -> str:
        comparison_key = self.name_normalizer.comparison_key(value) or ""
        return "".join(str(comparison_key).split())

    def _copy_warnings(self, warnings: CollectionImportWarnings) -> CollectionImportWarnings:
        return CollectionImportWarnings(
            invalid_wishlist=warnings.invalid_wishlist,
            invalid_wishlist_values_found=list(warnings.invalid_wishlist_values_found),
            invalid_games=list(warnings.invalid_games),
            platform_matches=list(warnings.platform_matches),
            skipped_games=list(warnings.skipped_games),
        )

    def _matched_game(self, game: CollectionImportGame, platform_name: str) -> CollectionImportGame:
        return CollectionImportGame(
            name=game.name,
            platform_name=platform_name,
            studio_name=game.studio_name,
            release_date=game.release_date,
            wishlist=game.wishlist,
        )

    def _matched_platform_names(self, games: list[CollectionImportGame]) -> list[str]:
        names_by_key = {}
        for game in games:
            names_by_key.setdefault(self._compact_key(game.platform_name), game.platform_name)
        return list(names_by_key.values())

    def _matched_studios(
        self,
        import_data: CollectionImportData,
        games: list[CollectionImportGame],
    ):
        matched_studio_keys = {
            self.name_normalizer.comparison_key(game.studio_name)
            for game in games
            if self.name_normalizer.comparison_key(game.studio_name)
        }
        return [
            studio
            for studio in import_data.studios
            if self.name_normalizer.comparison_key(studio.name) in matched_studio_keys
        ]

    def _platform_match_warning(
        self,
        game: CollectionImportGame,
        match: dict[str, object],
    ) -> dict[str, object]:
        return {
            "game_name": game.name,
            "imported_platform": match["imported_name"],
            "matched_platform": match["matched_name"],
            "score": match["score"],
        }

    def _skipped_game_warning(
        self,
        game: CollectionImportGame,
        match: dict[str, object] | None,
    ) -> dict[str, object]:
        return {
            "game_name": game.name,
            "imported_platform": game.platform_name,
            "score": 0 if match is None else match["score"],
            "reason": "no_match" if match is None else match["reason"],
        }

    def _match_result(
        self,
        imported_name: str,
        matched_name: str,
        score: int,
        accepted: bool,
        manual_check: bool,
        reason: str,
    ) -> dict[str, object]:
        return {
            "imported_name": imported_name,
            "matched_name": matched_name,
            "score": score,
            "accepted": accepted,
            "manual_check": manual_check,
            "reason": reason,
        }
