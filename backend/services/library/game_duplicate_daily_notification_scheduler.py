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
# Description : planification quotidienne de la notification des doublons.

import logging
import os
from datetime import datetime, time, timedelta
from threading import Lock, Thread
from typing import Callable

from .game_duplicate_daily_notification_service import GameDuplicateDailyNotificationService

NowFactory = Callable[[], datetime]
SleepFunction = Callable[[float], None]


class GameDuplicateDailyNotificationScheduler:
    """Planifie la verification quotidienne des jeux signales comme doublons."""

    DEFAULT_NOTIFICATION_TIME = "04:00"
    ENV_NOTIFICATION_TIME = "GAME_DUPLICATE_DAILY_NOTIFICATION_TIME"

    def __init__(
        self,
        notification_service: GameDuplicateDailyNotificationService,
        scheduled_time: time,
        now_factory: NowFactory = datetime.now,
        sleep_function: SleepFunction | None = None,
        thread_factory=Thread,
        logger: logging.Logger | None = None,
    ):
        """Initialise le planificateur quotidien.

        Args:
            notification_service (GameDuplicateDailyNotificationService): Service metier execute.
            scheduled_time (time): Heure locale quotidienne d'execution.
            now_factory (NowFactory): Fabrique de date courante injectable.
            sleep_function (SleepFunction | None): Fonction d'attente injectable.
            thread_factory (type): Fabrique de threads injectable.
            logger (logging.Logger | None): Journal applicatif injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.notification_service = notification_service
        self.scheduled_time = scheduled_time
        self.now_factory = now_factory
        self.sleep_function = sleep_function or self._default_sleep
        self.thread_factory = thread_factory
        self.logger = logger or logging.getLogger(__name__)
        self._lock = Lock()
        self._started = False

    @classmethod
    def from_environment(cls) -> "GameDuplicateDailyNotificationScheduler":
        """Construit le planificateur depuis les variables d'environnement.

        Args:
            Aucun.

        Returns:
            GameDuplicateDailyNotificationScheduler: Planificateur configure.
        """

        configured_time = os.getenv(
            cls.ENV_NOTIFICATION_TIME,
            cls.DEFAULT_NOTIFICATION_TIME,
        )
        return cls(
            GameDuplicateDailyNotificationService.from_environment(),
            cls.parse_scheduled_time(configured_time),
        )

    @classmethod
    def parse_scheduled_time(cls, raw_value: str | None) -> time:
        """Convertit une configuration `HH:MM` en heure locale.

        Args:
            raw_value (str | None): Valeur brute de configuration.

        Returns:
            time: Heure locale interpretee, ou `04:00` par defaut.
        """

        value = str(raw_value or cls.DEFAULT_NOTIFICATION_TIME).strip()
        try:
            return datetime.strptime(value, "%H:%M").time()
        except ValueError:
            return datetime.strptime(cls.DEFAULT_NOTIFICATION_TIME, "%H:%M").time()

    def start(self) -> bool:
        """Demarre le thread de planification s'il n'est pas deja actif.

        Args:
            Aucun.

        Returns:
            bool: `True` si un thread a ete demarre.
        """

        with self._lock:
            if self._started:
                return False
            self._started = True
        thread = self.thread_factory(target=self._run_forever, daemon=True)
        thread.start()
        self.logger.info(
            "Notification quotidienne doublons planifiee a %s.",
            self.scheduled_time.strftime("%H:%M"),
        )
        return True

    def seconds_until_next_run(self, now: datetime | None = None) -> float:
        """Calcule le delai avant la prochaine execution.

        Args:
            now (datetime | None): Date courante optionnelle.

        Returns:
            float: Nombre de secondes avant la prochaine execution.
        """

        current_datetime = now or self.now_factory()
        next_run = datetime.combine(current_datetime.date(), self.scheduled_time)
        if next_run <= current_datetime:
            next_run += timedelta(days=1)
        return max(0.0, (next_run - current_datetime).total_seconds())

    def run_once(self) -> int:
        """Execute immediatement une verification des doublons.

        Args:
            Aucun.

        Returns:
            int: Nombre de doublons signales lors de la verification.
        """

        return self.notification_service.notify_if_duplicates_exist()

    def _run_forever(self) -> None:
        while True:
            self.sleep_function(self.seconds_until_next_run())
            try:
                self.run_once()
            except Exception:
                self.logger.exception("Echec de la notification quotidienne des doublons.")

    def _default_sleep(self, seconds: float) -> None:
        import time as time_module

        time_module.sleep(seconds)
