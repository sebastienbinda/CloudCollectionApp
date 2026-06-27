#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/|_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de la notification quotidienne des doublons de jeux.

import unittest
from datetime import datetime, time
from pathlib import Path

from services.database import DatabaseConfiguration
from services.database.game_duplicate_repository import SqlAlchemyGameDuplicateRepository
from services.library import (
    GameDuplicateDailyNotificationScheduler,
    GameDuplicateDailyNotificationService,
)
from tests.fake_platform_matching_email_sender import FakePlatformMatchingEmailSender


class FakeConnectionContext:
    """Contexte SQL factice."""

    def __init__(self, connection):
        """Initialise le contexte.

        Args:
            connection (object): Connexion retournee.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection

    def __enter__(self):
        """Entre dans le contexte.

        Args:
            Aucun.

        Returns:
            object: Connexion factice.
        """

        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        """Sort du contexte.

        Args:
            exc_type (type | None): Type d'exception.
            exc_value (BaseException | None): Exception.
            traceback (object | None): Traceback.

        Returns:
            bool: `False` pour laisser remonter les erreurs.
        """

        return False


class FakeEngine:
    """Moteur SQL factice."""

    def __init__(self):
        """Initialise le moteur.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = object()

    def connect(self):
        """Ouvre une connexion de lecture factice.

        Args:
            Aucun.

        Returns:
            FakeConnectionContext: Contexte SQL factice.
        """

        return FakeConnectionContext(self.connection)


class FakeDuplicateCountRepository:
    """Repository factice pour le comptage des doublons."""

    def __init__(self, duplicate_count):
        """Initialise le compteur retourne.

        Args:
            duplicate_count (int): Nombre de doublons a retourner.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.duplicate_count = duplicate_count
        self.calls = 0

    def count_reported_duplicates(self, connection):
        """Retourne le nombre de doublons configure.

        Args:
            connection (object): Connexion ignoree.

        Returns:
            int: Nombre de doublons configure.
        """

        self.calls += 1
        return self.duplicate_count


class FakeSqlConnection:
    """Connexion SQL factice capturant les requetes."""

    def __init__(self, scalar_value):
        """Initialise la connexion.

        Args:
            scalar_value (int): Valeur scalaire retournee.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.scalar_value = scalar_value
        self.executed_statements = []

    def execute(self, statement, parameters=None):
        """Capture la requete executee.

        Args:
            statement (object): Requete SQLAlchemy.
            parameters (dict | None): Parametres SQL.

        Returns:
            FakeSqlResult: Resultat factice.
        """

        self.executed_statements.append((str(statement), parameters))
        return FakeSqlResult(self.scalar_value)


class FakeSqlResult:
    """Resultat SQL factice."""

    def __init__(self, scalar_value):
        """Initialise le resultat.

        Args:
            scalar_value (int): Valeur scalaire retournee.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.scalar_value = scalar_value

    def scalar_one(self):
        """Retourne la valeur scalaire.

        Args:
            Aucun.

        Returns:
            int: Valeur configuree.
        """

        return self.scalar_value


class GameDuplicateDailyNotificationTest(unittest.TestCase):
    """Valide la notification quotidienne des doublons de jeux."""

    def test_notify_if_duplicates_exist_sends_templated_email(self):
        """Verifie l'envoi du mail quand des doublons existent.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le mail.
        """

        sender = FakePlatformMatchingEmailSender()
        repository = FakeDuplicateCountRepository(3)
        service = GameDuplicateDailyNotificationService(
            DatabaseConfiguration(None, "cloudcollectionapp", "0.1"),
            repository=repository,
            engine=FakeEngine(),
            email_sender=sender,
            admin_notification_email="admin@example.com",
            site_url="https://app.example.com/",
        )

        duplicate_count = service.notify_if_duplicates_exist()

        self.assertEqual(3, duplicate_count)
        self.assertEqual(1, repository.calls)
        self.assertEqual(1, len(sender.sent_emails))
        self.assertEqual("admin@example.com", sender.sent_emails[0]["recipient_email"])
        self.assertEqual("Jeux en doublon a traiter", sender.sent_emails[0]["subject"])
        self.assertIn("3 jeu(x)", sender.sent_emails[0]["body"])
        self.assertIn("https://app.example.com", sender.sent_emails[0]["body"])
        self.assertIn(
            "https://app.example.com/bibliotheque/jeux?duplicate_flag=true",
            sender.sent_emails[0]["body"],
        )

    def test_notify_if_duplicates_exist_does_not_send_email_without_duplicate(self):
        """Verifie qu'aucun mail n'est envoye sans doublon.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence d'envoi.
        """

        sender = FakePlatformMatchingEmailSender()
        service = GameDuplicateDailyNotificationService(
            DatabaseConfiguration(None, "cloudcollectionapp", "0.1"),
            repository=FakeDuplicateCountRepository(0),
            engine=FakeEngine(),
            email_sender=sender,
            admin_notification_email="admin@example.com",
        )

        duplicate_count = service.notify_if_duplicates_exist()

        self.assertEqual(0, duplicate_count)
        self.assertEqual([], sender.sent_emails)

    def test_notify_if_duplicates_exist_uses_backend_resource_template(self):
        """Verifie que le template email vient des ressources backend.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le chemin du template.
        """

        template_path = GameDuplicateDailyNotificationService.default_template_path()

        self.assertEqual(Path("backend/resources"), Path(*template_path.parts[-3:-1]))
        self.assertTrue(template_path.exists())

    def test_scheduler_uses_default_time_when_configuration_is_invalid(self):
        """Verifie le repli sur 04:00 quand l'heure est invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'heure planifiee.
        """

        scheduled_time = GameDuplicateDailyNotificationScheduler.parse_scheduled_time("25:61")

        self.assertEqual(time(4, 0), scheduled_time)

    def test_scheduler_computes_next_run_same_day_or_next_day(self):
        """Verifie le calcul du prochain passage quotidien.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le delai.
        """

        service = GameDuplicateDailyNotificationService(
            DatabaseConfiguration(None, "cloudcollectionapp", "0.1"),
            repository=FakeDuplicateCountRepository(0),
            engine=FakeEngine(),
            email_sender=FakePlatformMatchingEmailSender(),
        )
        scheduler = GameDuplicateDailyNotificationScheduler(service, time(4, 0))

        before_run = scheduler.seconds_until_next_run(datetime(2026, 6, 27, 3, 30))
        after_run = scheduler.seconds_until_next_run(datetime(2026, 6, 27, 4, 30))

        self.assertEqual(30 * 60, before_run)
        self.assertEqual((23 * 60 + 30) * 60, after_run)

    def test_repository_counts_games_with_duplicate_flag(self):
        """Verifie la requete SQL de comptage des doublons signales.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la requete.
        """

        connection = FakeSqlConnection(5)
        repository = SqlAlchemyGameDuplicateRepository("cloudcollectionapp")

        count = repository.count_reported_duplicates(connection)

        self.assertEqual(5, count)
        self.assertIn("COUNT(*)", connection.executed_statements[0][0])
        self.assertIn("duplicate_flag = TRUE", connection.executed_statements[0][0])


if __name__ == "__main__":
    unittest.main()
