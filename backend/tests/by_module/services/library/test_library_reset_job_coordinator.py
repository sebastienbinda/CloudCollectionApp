#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du coordinateur de job reset Bibliotheque.

import unittest

from services.library import LibraryResetAlreadyRunningError, LibraryResetJobCoordinator


class RecordingThread:
    """Thread factice qui memorise la tache sans l'executer automatiquement."""

    instances = []

    def __init__(self, target, args=(), daemon=False):
        """Initialise le thread factice.

        Args:
            target (Callable): Fonction a executer.
            args (tuple): Arguments de la fonction.
            daemon (bool): Indicateur daemon recu du coordinateur.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.target = target
        self.args = args
        self.daemon = daemon
        self.started = False
        self.__class__.instances.append(self)

    def start(self):
        """Marque le thread comme demarre sans executer la tache.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.started = True

    def run_target(self):
        """Execute la tache memorisee.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.target(*self.args)


class LibraryResetJobCoordinatorTest(unittest.TestCase):
    """Valide le verrou global du coordinateur de reset."""

    def setUp(self):
        """Reinitialise les threads factices.

        Args:
            Aucun.

        Returns:
            None: Les instances memorisees sont videes.
        """

        RecordingThread.instances = []

    def test_start_reset_creates_async_job(self):
        """Verifie la creation d'un job asynchrone.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le job cree.
        """

        coordinator = LibraryResetJobCoordinator(thread_factory=RecordingThread)

        job = coordinator.start_reset()

        self.assertEqual(1, job.job_id)
        self.assertTrue(coordinator.is_reset_running())
        self.assertEqual(1, len(RecordingThread.instances))
        self.assertTrue(RecordingThread.instances[0].started)
        self.assertTrue(RecordingThread.instances[0].daemon)

    def test_start_reset_rejects_concurrent_job(self):
        """Verifie le refus d'un second reset concurrent.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'exception metier.
        """

        coordinator = LibraryResetJobCoordinator(thread_factory=RecordingThread)
        coordinator.start_reset()

        with self.assertRaises(LibraryResetAlreadyRunningError):
            coordinator.start_reset()

    def test_running_flag_is_released_after_job_execution(self):
        """Verifie la liberation du verrou apres execution.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la fin du job.
        """

        executed_job_ids = []
        coordinator = LibraryResetJobCoordinator(thread_factory=RecordingThread)
        job = coordinator.start_reset(lambda current_job: executed_job_ids.append(current_job.job_id))

        RecordingThread.instances[0].run_target()
        next_job = coordinator.start_reset()

        self.assertEqual([job.job_id], executed_job_ids)
        self.assertEqual(2, next_job.job_id)


if __name__ == "__main__":
    unittest.main()
