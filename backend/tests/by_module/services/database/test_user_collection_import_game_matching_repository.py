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
# Description : tests du rattachement des jeux pendant l'import utilisateur.

from types import SimpleNamespace
import unittest

from services.collection.imports import (
    CollectionImportData,
    CollectionImportGame,
    CollectionImportPlatform,
)
from services.database.user_collection_import_repository import (
    SqlAlchemyUserCollectionImportRepository,
)
from services.users import UserCollectionNameNormalizer


class FakeGameMatchingService:
    """Service de matching factice capturant la taille de l'index fuzzy."""

    def __init__(self):
        """Initialise les compteurs du service factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.evaluated_candidate_counts = []

    def build_platform_index(self, existing_game_references):
        """Retourne l'index initial vide du referentiel.

        Args:
            existing_game_references (dict): References existantes.

        Returns:
            dict: Index par plateforme.
        """

        return {"super nintendo": []}

    def evaluate_existing_game(self, game, existing_game_ids, games_by_platform):
        """Memorise le nombre de candidats fuzzy disponibles.

        Args:
            game (CollectionImportGame): Jeu importe.
            existing_game_ids (dict): Identifiants exacts disponibles.
            games_by_platform (dict): Index fuzzy courant.

        Returns:
            SimpleNamespace: Absence de rattachement fuzzy.
        """

        self.evaluated_candidate_counts.append(
            len(games_by_platform.get("super nintendo", []))
        )
        return SimpleNamespace(existing_game_id=None, best_candidate=None)

    def add_to_platform_index(self, *args):
        """Echoue si un jeu cree est ajoute a l'index fuzzy.

        Args:
            *args (tuple): Parametres inattendus.

        Raises:
            AssertionError: Toujours, car l'import ne doit plus appeler ce chemin.
        """

        raise AssertionError("L'index fuzzy ne doit pas grossir pendant l'import.")


class UserCollectionImportGameMatchingRepositoryTest(unittest.TestCase):
    """Valide le matching des jeux pendant l'import utilisateur."""

    def test_ensure_games_keeps_fuzzy_index_limited_to_preexisting_games(self):
        """Verifie que les jeux crees ne gonflent pas l'index fuzzy du meme import.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident un cout de matching borne.
        """

        repository = object.__new__(SqlAlchemyUserCollectionImportRepository)
        repository.name_normalizer = UserCollectionNameNormalizer()
        repository.game_matching_service = FakeGameMatchingService()
        repository.game_repository = SimpleNamespace(
            load_references_by_key=lambda connection: {},
            game_key=lambda game: (
                repository.name_normalizer.comparison_key(game.platform_name),
                repository.name_normalizer.game_comparison_key(game.name),
            ),
            insert=lambda connection, game, platform_id, studio_id, status: len(game.name),
        )

        _associations, created_games, _created_reports, _imported_reports = (
            repository._ensure_games(
                object(),
                CollectionImportData(
                    platforms=[CollectionImportPlatform("Super Nintendo")],
                    studios=[],
                    games=[
                        CollectionImportGame("Chrono Trigger", "Super Nintendo", "", None),
                        CollectionImportGame("Super Metroid", "Super Nintendo", "", None),
                        CollectionImportGame("EarthBound", "Super Nintendo", "", None),
                    ],
                ),
                {"super nintendo": 7},
                {},
            )
        )

        self.assertEqual(3, created_games)
        self.assertEqual(
            [0, 0, 0],
            repository.game_matching_service.evaluated_candidate_counts,
        )
