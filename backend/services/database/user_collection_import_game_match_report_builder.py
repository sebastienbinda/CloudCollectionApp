#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-07-04
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : construction des diagnostics de matching d'import utilisateur.

from .user_collection_import_persistence_result import (
    CreatedGameMatchReport,
    ImportedGameMatchReport,
)


class UserCollectionImportGameMatchReportBuilder:
    """Construit les rapports de matching des jeux importes.

    Returns:
        UserCollectionImportGameMatchReportBuilder: Builder stateless reutilisable.

    Raises:
        Aucun.
    """

    @staticmethod
    def build_created_game_match_report(game, best_candidate) -> CreatedGameMatchReport:
        """Construit le diagnostic historique d'un jeu cree.

        Args:
            game (object): Jeu importe.
            best_candidate (object | None): Meilleur candidat existant.

        Returns:
            CreatedGameMatchReport: Diagnostic de creation.

        Raises:
            Aucun.
        """

        return CreatedGameMatchReport(
            imported_game_name=game.name,
            platform_name=game.platform_name,
            best_existing_game_name=(
                best_candidate.game_name if best_candidate is not None else ""
            ),
            best_score=best_candidate.score if best_candidate is not None else 0,
        )

    @staticmethod
    def build_imported_game_match_report(
        game,
        created: bool,
        exact_game_reference,
        best_candidate,
    ) -> ImportedGameMatchReport:
        """Construit le diagnostic complet d'un jeu importe.

        Args:
            game (object): Jeu importe.
            created (bool): Indique si un jeu de reference a ete cree.
            exact_game_reference (object | None): Reference exacte deja existante.
            best_candidate (object | None): Meilleur candidat fuzzy.

        Returns:
            ImportedGameMatchReport: Ligne de diagnostic pour le rapport admin.

        Raises:
            Aucun.
        """

        if exact_game_reference is not None:
            return ImportedGameMatchReport(
                imported_game_name=game.name,
                created=False,
                associated_game_name=(
                    UserCollectionImportGameMatchReportBuilder._game_reference_name(
                        exact_game_reference,
                        game.name,
                    )
                ),
                score=100,
                decision="accepted",
                rule="exact_normalized_key",
                reason="Cle plateforme/jeu normalisee deja presente.",
            )
        return ImportedGameMatchReport(
            imported_game_name=game.name,
            created=created,
            associated_game_name=(
                "" if created or best_candidate is None else best_candidate.game_name
            ),
            score=best_candidate.score if best_candidate is not None else 0,
            decision=getattr(best_candidate, "decision", "") or "rejected",
            rule=getattr(best_candidate, "rule", "") or "no_candidate",
            reason=getattr(best_candidate, "reason", "") or "Aucun candidat existant.",
        )

    @staticmethod
    def _game_reference_name(game_reference, fallback_name: str) -> str:
        if isinstance(game_reference, tuple) and len(game_reference) >= 2:
            return str(game_reference[1] or fallback_name)
        return fallback_name
