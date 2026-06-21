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

from dataclasses import replace

from services.collection.imports import (
    CollectionImportData,
    CollectionImportGame,
    CollectionImportPlatform,
    CollectionImportWarnings,
)
from services.users import UserCollectionNameNormalizer
from services.matching import matching_score

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
        warnings.platform_mappings.extend(
            self._platform_mapping_warnings(import_data, matches_by_key)
        )
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
        direct_match = self._best_match_from_candidates(
            self._direct_match_candidates(imported_key, platform_rows)
        )
        if direct_match["score"] >= self.configuration.high_level_rating:
            return self._finalize_match(imported_platform, direct_match)

        alias_match = self._best_match_from_candidates(
            self._alias_match_candidates(imported_key, platform_rows)
        )
        best_match = alias_match if alias_match["score"] > direct_match["score"] else direct_match
        return self._finalize_match(imported_platform, best_match)

    def _direct_match_candidates(
        self,
        imported_key: str,
        platform_rows: list[dict[str, object]],
    ) -> list[tuple[int, dict[str, object], str]]:
        return [
            (self._matching_score(imported_key, self._compact_key(row["name"])), row, "")
            for row in platform_rows
        ]

    def _alias_match_candidates(
        self,
        imported_key: str,
        platform_rows: list[dict[str, object]],
    ) -> list[tuple[int, dict[str, object], str]]:
        candidates = []
        for row in platform_rows:
            alias_matches = [
                (self._matching_score(imported_key, self._compact_key(alias_name)), alias_name)
                for alias_name in self._alias_names(row)
            ]
            if alias_matches:
                best_score, best_alias = max(alias_matches, key=lambda alias_match: alias_match[0])
                candidates.append((best_score, row, str(best_alias)))
        return candidates

    def _best_match_from_candidates(
        self,
        candidates: list[tuple[int, dict[str, object], str]],
    ) -> dict[str, object]:
        scored_rows = sorted(candidates, key=lambda scored_row: scored_row[0], reverse=True)
        best_score = scored_rows[0][0] if scored_rows else 0
        best_rows_by_name = {
            str(row["name"]): {"row": row, "alias": alias_name}
            for score, row, alias_name in scored_rows
            if score == best_score
        }
        return {
            "score": best_score,
            "rows": [value["row"] for value in best_rows_by_name.values()],
            "alias": next(
                (value["alias"] for value in best_rows_by_name.values() if value["alias"]),
                "",
            ),
        }

    def _finalize_match(
        self,
        imported_platform: str,
        best_match: dict[str, object],
    ) -> dict[str, object]:
        best_score = int(best_match["score"])
        best_rows = list(best_match["rows"])
        if best_score == 0:
            return self._match_result(imported_platform, "", 0, False, False, "no_match")
        if len(best_rows) > 1:
            return self._match_result(imported_platform, "", best_score, False, False, "ambiguous")
        matched_name = str(best_rows[0]["name"])
        matched_alias = str(best_match.get("alias") or "")
        if best_score >= self.configuration.high_level_rating:
            return self._match_result(
                imported_platform,
                matched_name,
                best_score,
                True,
                False,
                "",
                bool(matched_alias),
                matched_alias,
            )
        if best_score >= self.configuration.low_level_rating:
            return self._match_result(
                imported_platform,
                matched_name,
                best_score,
                True,
                True,
                "",
                bool(matched_alias),
                matched_alias,
            )
        return self._match_result(
            imported_platform,
            matched_name,
            best_score,
            False,
            False,
            "low_score",
            bool(matched_alias),
            matched_alias,
        )

    def _alias_names(self, row: dict[str, object]) -> list[object]:
        aliases = row.get("aliases") or []
        return [
            alias.get("name")
            for alias in aliases
            if isinstance(alias, dict) and alias.get("name")
        ]

    def _matching_score(self, imported_key: str, candidate_key: str) -> int:
        return matching_score(imported_key, candidate_key)

    def _compact_key(self, value: object) -> str:
        comparison_key = self.name_normalizer.comparison_key(value) or ""
        return "".join(str(comparison_key).split())

    def _copy_warnings(self, warnings: CollectionImportWarnings) -> CollectionImportWarnings:
        return CollectionImportWarnings(
            invalid_wishlist=warnings.invalid_wishlist,
            invalid_wishlist_values_found=list(warnings.invalid_wishlist_values_found),
            invalid_games=list(warnings.invalid_games),
            platform_mappings=list(warnings.platform_mappings),
            platform_matches=list(warnings.platform_matches),
            skipped_games=list(warnings.skipped_games),
        )

    def _matched_game(self, game: CollectionImportGame, platform_name: str) -> CollectionImportGame:
        return replace(game, platform_name=platform_name)

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

    def _platform_mapping_warnings(
        self,
        import_data: CollectionImportData,
        matches_by_key: dict[str, dict[str, object]],
    ) -> list[dict[str, object]]:
        game_counts_by_platform_key = self._game_counts_by_imported_platform(import_data.games)
        platform_mappings = []
        seen_keys = set()
        for platform in import_data.platforms:
            platform_key = self._compact_key(platform.name)
            if platform_key in seen_keys:
                continue
            seen_keys.add(platform_key)
            match = matches_by_key.get(platform_key)
            platform_mappings.append(
                {
                    "imported_platform": platform.name,
                    "matched_platform": "" if match is None else match["matched_name"],
                    "score": 0 if match is None else match["score"],
                    "games_count": game_counts_by_platform_key.get(platform_key, 0),
                    "matched_by_alias": False if match is None else match["matched_by_alias"],
                    "matched_alias": "" if match is None else match["matched_alias"],
                    "accepted": False if match is None else match["accepted"],
                    "manual_check": False if match is None else match["manual_check"],
                    "reason": "no_match" if match is None else match["reason"],
                }
            )
        return platform_mappings

    def _game_counts_by_imported_platform(
        self,
        games: list[CollectionImportGame],
    ) -> dict[str, int]:
        game_counts_by_platform_key = {}
        for game in games:
            platform_key = self._compact_key(game.platform_name)
            game_counts_by_platform_key[platform_key] = (
                game_counts_by_platform_key.get(platform_key, 0) + 1
            )
        return game_counts_by_platform_key

    def _match_result(
        self,
        imported_name: str,
        matched_name: str,
        score: int,
        accepted: bool,
        manual_check: bool,
        reason: str,
        matched_by_alias: bool = False,
        matched_alias: str = "",
    ) -> dict[str, object]:
        return {
            "imported_name": imported_name,
            "matched_name": matched_name,
            "score": score,
            "accepted": accepted,
            "manual_check": manual_check,
            "reason": reason,
            "matched_by_alias": matched_by_alias,
            "matched_alias": matched_alias,
        }
