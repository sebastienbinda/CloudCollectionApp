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
# Description : tests du resume et des notifications de validation des jeux.

import unittest
from datetime import datetime, time
from pathlib import Path

from services.database import DatabaseConfiguration
from services.database.game_validation_repository import SqlAlchemyGameValidationRepository
from services.library import (
    GameValidationDailyNotificationScheduler,
    GameValidationDailyNotificationService,
    GameValidationService,
)
from tests.support.fake_platform_matching_email_sender import FakePlatformMatchingEmailSender


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


class FakeWaitingValidationCountRepository:
    """Repository factice pour le comptage des jeux en attente."""

    def __init__(self, waiting_validation_count):
        """Initialise le compteur retourne.

        Args:
            waiting_validation_count (int): Nombre de jeux a retourner.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.waiting_validation_count = waiting_validation_count
        self.calls = 0

    def count_waiting_validation_games(self, connection):
        """Retourne le nombre de jeux en attente configure.

        Args:
            connection (object): Connexion ignoree.

        Returns:
            int: Nombre de jeux en attente configure.
        """

        self.calls += 1
        return self.waiting_validation_count


class FakeLogger:
    """Journal factice capturant les warnings."""

    def __init__(self):
        """Initialise le journal factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.warnings = []

    def warning(self, message, *args):
        """Capture un warning.

        Args:
            message (str): Message de log.
            *args: Arguments de formatage.

        Returns:
            None: Le message est memorise.
        """

        self.warnings.append(message % args if args else message)


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


class FakeThread:
    """Thread factice capturant le demarrage du scheduler."""

    created_threads = []

    def __init__(self, target=None, daemon=False):
        """Initialise le thread factice.

        Args:
            target (Callable | None): Fonction cible.
            daemon (bool): Indique si le thread est daemon.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.target = target
        self.daemon = daemon
        self.started = False
        self.__class__.created_threads.append(self)

    def start(self):
        """Memorise le demarrage du thread.

        Args:
            Aucun.

        Returns:
            None: Le thread factice ne lance aucun traitement.
        """

        self.started = True


class GameValidationDailyNotificationTest(unittest.TestCase):
    """Valide le resume et la notification quotidienne des jeux a valider."""

    def test_summary_returns_zero_counter(self):
        """Verifie le resume sans jeux en attente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        service = GameValidationService(
            DatabaseConfiguration(None, "cloudcollectionapp", "0.1"),
            repository=FakeWaitingValidationCountRepository(0),
            engine=FakeEngine(),
        )

        summary = service.get_summary()

        self.assertEqual(0, summary["waiting_validation_count"])
        self.assertFalse(summary["has_waiting_validation"])

    def test_summary_returns_positive_counter(self):
        """Verifie le resume avec jeux en attente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        service = GameValidationService(
            DatabaseConfiguration(None, "cloudcollectionapp", "0.1"),
            repository=FakeWaitingValidationCountRepository(4),
            engine=FakeEngine(),
        )

        summary = service.get_summary()

        self.assertEqual(4, summary["waiting_validation_count"])
        self.assertTrue(summary["has_waiting_validation"])

    def test_notify_if_waiting_games_exist_sends_templated_email(self):
        """Verifie l'envoi du mail quand des jeux sont en attente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le mail.
        """

        sender = FakePlatformMatchingEmailSender()
        repository = FakeWaitingValidationCountRepository(3)
        service = GameValidationDailyNotificationService(
            DatabaseConfiguration(None, "cloudcollectionapp", "0.1"),
            repository=repository,
            engine=FakeEngine(),
            email_sender=sender,
            admin_notification_email="admin@example.com",
            site_url="https://app.example.com/",
        )

        waiting_validation_count = service.notify_if_waiting_games_exist()

        self.assertEqual(3, waiting_validation_count)
        self.assertEqual(1, repository.calls)
        self.assertEqual(1, len(sender.sent_emails))
        self.assertEqual("admin@example.com", sender.sent_emails[0]["recipient_email"])
        self.assertEqual("Jeux en attente de validation", sender.sent_emails[0]["subject"])
        self.assertIn("3 jeu(x)", sender.sent_emails[0]["body"])
        self.assertIn(
            "https://app.example.com/bibliotheque/jeux?status=WAITING_VALIDATION",
            sender.sent_emails[0]["body"],
        )

    def test_notify_if_waiting_games_exist_does_not_send_email_without_pending_game(self):
        """Verifie qu'aucun mail n'est envoye sans jeu en attente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence d'envoi.
        """

        sender = FakePlatformMatchingEmailSender()
        service = GameValidationDailyNotificationService(
            DatabaseConfiguration(None, "cloudcollectionapp", "0.1"),
            repository=FakeWaitingValidationCountRepository(0),
            engine=FakeEngine(),
            email_sender=sender,
            admin_notification_email="admin@example.com",
        )

        waiting_validation_count = service.notify_if_waiting_games_exist()

        self.assertEqual(0, waiting_validation_count)
        self.assertEqual([], sender.sent_emails)

    def test_notify_if_waiting_games_exist_logs_warning_without_admin_email(self):
        """Verifie le warning quand aucun email admin n'est configure.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le log et l'absence d'envoi.
        """

        sender = FakePlatformMatchingEmailSender()
        logger = FakeLogger()
        service = GameValidationDailyNotificationService(
            DatabaseConfiguration(None, "cloudcollectionapp", "0.1"),
            repository=FakeWaitingValidationCountRepository(2),
            engine=FakeEngine(),
            email_sender=sender,
            admin_notification_email="",
            logger=logger,
        )

        waiting_validation_count = service.notify_if_waiting_games_exist()

        self.assertEqual(2, waiting_validation_count)
        self.assertEqual([], sender.sent_emails)
        self.assertIn("ADMIN_NOTIFICATION_EMAIL absent", logger.warnings[0])

    def test_template_path_uses_backend_resource(self):
        """Verifie que le template email vient des ressources backend.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le chemin du template.
        """

        template_path = GameValidationDailyNotificationService.default_template_path()

        self.assertEqual(Path("backend/resources"), Path(*template_path.parts[-3:-1]))
        self.assertTrue(template_path.exists())

    def test_scheduler_uses_default_time_when_configuration_is_invalid(self):
        """Verifie le repli sur 04:15 quand l'heure est invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'heure planifiee.
        """

        scheduled_time = GameValidationDailyNotificationScheduler.parse_scheduled_time("25:61")

        self.assertEqual(time(4, 15), scheduled_time)

    def test_scheduler_computes_next_run_same_day_or_next_day(self):
        """Verifie le calcul du prochain passage quotidien.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le delai.
        """

        service = GameValidationDailyNotificationService(
            DatabaseConfiguration(None, "cloudcollectionapp", "0.1"),
            repository=FakeWaitingValidationCountRepository(0),
            engine=FakeEngine(),
            email_sender=FakePlatformMatchingEmailSender(),
        )
        scheduler = GameValidationDailyNotificationScheduler(service, time(4, 15))

        before_run = scheduler.seconds_until_next_run(datetime(2026, 8, 1, 3, 45))
        after_run = scheduler.seconds_until_next_run(datetime(2026, 8, 1, 4, 45))

        self.assertEqual(30 * 60, before_run)
        self.assertEqual((23 * 60 + 30) * 60, after_run)

    def test_scheduler_starts_once(self):
        """Verifie que le scheduler initialise un seul thread.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'initialisation idempotente.
        """

        FakeThread.created_threads = []
        service = GameValidationDailyNotificationService(
            DatabaseConfiguration(None, "cloudcollectionapp", "0.1"),
            repository=FakeWaitingValidationCountRepository(0),
            engine=FakeEngine(),
            email_sender=FakePlatformMatchingEmailSender(),
        )
        scheduler = GameValidationDailyNotificationScheduler(
            service,
            time(4, 15),
            thread_factory=FakeThread,
        )

        first_start = scheduler.start()
        second_start = scheduler.start()

        self.assertTrue(first_start)
        self.assertFalse(second_start)
        self.assertEqual(1, len(FakeThread.created_threads))
        self.assertTrue(FakeThread.created_threads[0].daemon)
        self.assertTrue(FakeThread.created_threads[0].started)

    def test_repository_counts_games_waiting_validation(self):
        """Verifie la requete SQL de comptage des jeux a valider.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la requete.
        """

        connection = FakeSqlConnection(5)
        repository = SqlAlchemyGameValidationRepository("cloudcollectionapp")

        count = repository.count_waiting_validation_games(connection)

        self.assertEqual(5, count)
        self.assertIn("COUNT(*)", connection.executed_statements[0][0])
        self.assertIn("status = :waiting_status", connection.executed_statements[0][0])
        self.assertEqual(
            "WAITING_VALIDATION",
            connection.executed_statements[0][1]["waiting_status"],
        )


if __name__ == "__main__":
    unittest.main()
