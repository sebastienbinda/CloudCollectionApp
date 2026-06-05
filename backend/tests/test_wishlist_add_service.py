#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-08
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# License : Apache 2.0
#
"""Tests d'ajout de jeux dans la liste de souhaits.

Description:
    Ce module valide le service objet qui nettoie les champs wishlist avant
    d'appeler l'ecriture ODS.
"""

import unittest

from services.jeux_video import JeuVideoService
from services.validation import WishlistPayloadValidator


class FakeWishlistWriter:
    """Ecrivain factice capturant les jeux wishlist ajoutes."""

    def __init__(self):
        """Initialise l'ecrivain factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.added_wishlist_games = []

    def add_wishlist_game(self, game):
        """Capture le jeu wishlist ajoute.

        Args:
            game (dict[str, object]): Jeu wishlist nettoye.

        Returns:
            None: Les donnees sont conservees en memoire.
        """

        self.added_wishlist_games.append(game)


class FakeCache:
    """Cache factice comptant les invalidations."""

    def __init__(self):
        """Initialise le cache factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.reset_count = 0

    def reset(self):
        """Compte une demande de reset.

        Args:
            Aucun.

        Returns:
            int: Nombre de resets effectues.
        """

        self.reset_count += 1
        return self.reset_count


class WishlistAddServiceTest(unittest.TestCase):
    """Tests unitaires du service d'ajout wishlist."""

    def setUp(self):
        """Prepare un service sans acces fichier.

        Args:
            Aucun.

        Returns:
            None: Les dependances ODS sont remplacees par des fakes.
        """

        self.service = JeuVideoService.__new__(JeuVideoService)
        self.service.writer = FakeWishlistWriter()
        self.service.cache = FakeCache()
        self.service.wishlist_validator = WishlistPayloadValidator()

    def test_add_wishlist_game_writes_clean_payload_and_resets_cache(self):
        """Verifie l'ajout wishlist et l'invalidation du cache.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        item = self.service.add_wishlist_game(
            {"Nom du jeu": " Chrono Trigger HD ", "Console": " Switch 2 ", "Studio": " Square "}
        )

        self.assertEqual("Chrono Trigger HD", item["Nom du jeu"])
        self.assertEqual("Switch 2", item["Console"])
        self.assertEqual(1, self.service.cache.reset_count)
        self.assertEqual("Square", self.service.writer.added_wishlist_games[0]["Studio"])

    def test_add_wishlist_game_rejects_missing_required_field(self):
        """Verifie la validation obligatoire avant ecriture wishlist.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le refus du payload incomplet.
        """

        with self.assertRaises(ValueError):
            self.service.add_wishlist_game({"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"})


if __name__ == "__main__":
    unittest.main()
