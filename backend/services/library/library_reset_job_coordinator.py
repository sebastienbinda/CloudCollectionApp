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
# Description : coordination en memoire du job de reset Bibliotheque.

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock, Thread
from typing import Callable


class LibraryResetAlreadyRunningError(Exception):
    """Signale qu'un reset Bibliotheque est deja en cours."""


@dataclass(frozen=True)
class LibraryResetJob:
    """Represente le job asynchrone de reset Bibliotheque.

    Attributes:
        job_id (int): Identifiant technique du job lance.
        started_at (datetime): Date de lancement du job.
    """

    job_id: int
    started_at: datetime


class LibraryResetJobCoordinator:
    """Coordonne le lancement concurrentiel d'un reset Bibliotheque."""

    def __init__(self, thread_factory=Thread):
        """Initialise le coordinateur de reset Bibliotheque.

        Args:
            thread_factory (type): Fabrique de threads injectable en test.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.thread_factory = thread_factory
        self._lock = Lock()
        self._next_job_id = 1
        self._running_job_id = None

    def start_reset(self, reset_task: Callable[[LibraryResetJob], None] | None = None) -> LibraryResetJob:
        """Lance un reset Bibliotheque asynchrone.

        Args:
            reset_task (Callable[[LibraryResetJob], None] | None): Tache executee dans le thread.

        Returns:
            LibraryResetJob: Job cree et demarre.

        Raises:
            LibraryResetAlreadyRunningError: Si un reset est deja en cours.
        """

        with self._lock:
            if self._running_job_id is not None:
                raise LibraryResetAlreadyRunningError("Un reset de la Bibliotheque est deja en cours.")
            job = LibraryResetJob(self._next_job_id, datetime.now(timezone.utc).replace(tzinfo=None))
            self._next_job_id += 1
            self._running_job_id = job.job_id

        thread = self.thread_factory(target=self._run_job, args=(job, reset_task), daemon=True)
        thread.start()
        return job

    def is_reset_running(self) -> bool:
        """Indique si un reset Bibliotheque est en cours.

        Args:
            Aucun.

        Returns:
            bool: `True` si un job est actif.
        """

        with self._lock:
            return self._running_job_id is not None

    def _run_job(self, job: LibraryResetJob, reset_task: Callable[[LibraryResetJob], None] | None) -> None:
        """Execute la tache de reset puis libere le verrou global.

        Args:
            job (LibraryResetJob): Job a executer.
            reset_task (Callable[[LibraryResetJob], None] | None): Tache metier optionnelle.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        try:
            if reset_task is not None:
                reset_task(job)
        finally:
            with self._lock:
                if self._running_job_id == job.job_id:
                    self._running_job_id = None
