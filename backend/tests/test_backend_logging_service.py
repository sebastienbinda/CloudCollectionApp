#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-13
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du systeme de rotation des logs backend.

from datetime import datetime
import logging
from pathlib import Path
import tempfile
import unittest

from services.logging import DailySizeRotatingFileHandler


class MutableDateProvider:
    """Fournit une date modifiable aux tests de rotation quotidienne."""

    def __init__(self, current_datetime: datetime):
        """Initialise le fournisseur de date.

        Args:
            current_datetime (datetime): Date initiale retournee par le fournisseur.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.current_datetime = current_datetime

    def __call__(self) -> datetime:
        """Retourne la date courante du test.

        Args:
            Aucun.

        Returns:
            datetime: Date configuree pour le test.
        """

        return self.current_datetime


class DailySizeRotatingFileHandlerTest(unittest.TestCase):
    def test_handler_rotates_when_file_exceeds_max_bytes(self):
        """Verifie la rotation lorsque le fichier actif depasse la taille maximale.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la creation d'une archive.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            logger, handler = self._create_logger(temp_dir, max_bytes=40, backup_count=5)

            logger.info("premiere ligne assez longue")
            logger.info("deuxieme ligne assez longue")
            handler.close()

            log_dir = Path(temp_dir)
            self.assertTrue((log_dir / "backend.log").exists())
            self.assertTrue(list(log_dir.glob("backend.log.2026-05-13.*")))

    def test_handler_rotates_when_day_changes(self):
        """Verifie la rotation lorsque la date courante change.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le suffixe de date archive.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            date_provider = MutableDateProvider(datetime(2026, 5, 13, 12, 0, 0))
            logger, handler = self._create_logger(
                temp_dir,
                max_bytes=1024,
                backup_count=5,
                date_provider=date_provider,
            )

            logger.info("ligne du premier jour")
            date_provider.current_datetime = datetime(2026, 5, 14, 12, 0, 0)
            logger.info("ligne du second jour")
            handler.close()

            self.assertTrue(list(Path(temp_dir).glob("backend.log.2026-05-13.*")))

    def test_handler_keeps_only_configured_archive_count(self):
        """Verifie la purge des archives excedant la retention.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le nombre d'archives conservees.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            logger, handler = self._create_logger(temp_dir, max_bytes=30, backup_count=2)

            for index in range(6):
                logger.info("ligne longue numero %s", index)
            handler.close()

            archives = list(Path(temp_dir).glob("backend.log.2026-05-13.*"))
            self.assertLessEqual(len(archives), 2)

    def _create_logger(
        self,
        temp_dir: str,
        max_bytes: int,
        backup_count: int,
        date_provider: MutableDateProvider | None = None,
    ):
        """Construit un logger isole pour tester le handler.

        Args:
            temp_dir (str): Repertoire temporaire des fichiers de log.
            max_bytes (int): Taille maximale avant rotation.
            backup_count (int): Nombre d'archives conservees.
            date_provider (MutableDateProvider | None): Date injectable.

        Returns:
            tuple[logging.Logger, DailySizeRotatingFileHandler]: Logger et handler testes.
        """

        logger = logging.getLogger(f"test-logger-{id(temp_dir)}")
        logger.handlers = []
        logger.propagate = False
        logger.setLevel(logging.INFO)
        handler = DailySizeRotatingFileHandler(
            filename=str(Path(temp_dir) / "backend.log"),
            max_bytes=max_bytes,
            backup_count=backup_count,
            date_provider=date_provider or MutableDateProvider(datetime(2026, 5, 13, 12, 0, 0)),
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        return logger, handler


if __name__ == "__main__":
    unittest.main()
