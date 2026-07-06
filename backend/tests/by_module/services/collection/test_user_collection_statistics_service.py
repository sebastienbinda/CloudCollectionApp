#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-07-05
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du service de statistiques detaillees.

import unittest

from services.collection.user_collection_statistics_service import UserCollectionStatisticsService
from services.database import DatabaseConfiguration


class FakeConnectionContext:
    """Contexte de connexion factice."""

    def __init__(self, connection):
        """Initialise le contexte.

        Args:
            connection (object): Connexion retournee par le contexte.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection

    def __enter__(self):
        """Retourne la connexion factice.

        Args:
            Aucun.

        Returns:
            object: Connexion configuree.
        """

        return self.connection

    def __exit__(self, exc_type, exc, traceback):
        """Ferme le contexte factice.

        Args:
            exc_type (type | None): Type d'exception.
            exc (Exception | None): Exception levee.
            traceback (object | None): Traceback associe.

        Returns:
            bool: `False` pour ne pas masquer les exceptions.
        """

        return False


class FakeEngine:
    """Moteur SQLAlchemy factice."""

    def __init__(self):
        """Initialise le moteur factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = object()
        self.connect_count = 0

    def connect(self):
        """Retourne un contexte de connexion factice.

        Args:
            Aucun.

        Returns:
            FakeConnectionContext: Contexte compatible avec `with`.
        """

        self.connect_count += 1
        return FakeConnectionContext(self.connection)


class FakeStatisticsRepository:
    """Repository de statistiques factice."""

    def list_platform_distribution(self, connection, user_id):
        """Retourne la repartition par plateforme.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.

        Returns:
            list[dict]: Plateformes factices.
        """

        return [
            {"platform_id": 1, "platform_name": "Switch", "games_count": 3},
            {"platform_id": 2, "platform_name": "NES", "games_count": 1},
        ]

    def list_release_year_distribution(self, connection, user_id):
        """Retourne les annees de sortie factices.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.

        Returns:
            list[dict]: Annees de sortie.
        """

        return [{"year": 1992, "games_count": 1}]

    def list_purchase_year_distribution(self, connection, user_id):
        """Retourne les annees d'achat factices.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.

        Returns:
            list[dict]: Annees d'achat.
        """

        return [{"year": 2024, "games_count": 4}]

    def list_top_rated_games(self, connection, user_id):
        """Retourne les jeux les mieux notes factices.

        Args:
            connection (object): Connexion recue.
            user_id (int): Identifiant utilisateur.

        Returns:
            list[dict]: Jeux factices.
        """

        return [
            {
                "id": 3,
                "name": "Mario Kart",
                "platform_name": "Switch",
                "release_date": "1992-08-27",
                "buy_date": "2024-03-10",
                "grade": "9.5",
            }
        ]


class UserCollectionStatisticsServiceTest(unittest.TestCase):
    """Valide le service de statistiques detaillees."""

    def test_get_statistics_returns_detailed_payload(self):
        """Verifie le contrat des statistiques detaillees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        engine = FakeEngine()
        service = UserCollectionStatisticsService(
            DatabaseConfiguration(None, "collection", "0.1"),
            repository=FakeStatisticsRepository(),
            engine=engine,
        )

        payload = service.get_statistics(7)

        self.assertEqual(1, engine.connect_count)
        self.assertEqual(4, payload["total_games"])
        self.assertEqual(75, payload["platform_distribution"][0]["ratio"])
        self.assertEqual(25, payload["platform_distribution"][1]["ratio"])
        self.assertEqual(1992, payload["release_year_distribution"][0]["year"])
        self.assertEqual(2024, payload["purchase_year_distribution"][0]["year"])
        self.assertEqual("Mario Kart", payload["top_rated_games"][0]["name"])


if __name__ == "__main__":
    unittest.main()
