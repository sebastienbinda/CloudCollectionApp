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
# Description : handler de logs avec rotation quotidienne et par taille.

from datetime import datetime
import os
from logging.handlers import BaseRotatingHandler
from pathlib import Path
from typing import Callable


class DailySizeRotatingFileHandler(BaseRotatingHandler):
    """Ecrit les journaux sur disque avec rotation par jour et par taille."""

    def __init__(
        self,
        filename: str,
        max_bytes: int,
        backup_count: int,
        date_provider: Callable[[], datetime] | None = None,
    ):
        """Initialise le handler de fichiers tournants.

        Args:
            filename (str): Chemin du fichier de log actif.
            max_bytes (int): Taille maximale du fichier actif avant rotation.
            backup_count (int): Nombre maximal d'archives conservees.
            date_provider (Callable[[], datetime] | None): Fournisseur de date injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        super().__init__(filename, mode="a", encoding="utf-8", delay=False)
        self.max_bytes = max(0, int(max_bytes))
        self.backup_count = max(0, int(backup_count))
        self.date_provider = date_provider or datetime.now
        self.current_log_date = self._current_date_label()

    def shouldRollover(self, record) -> bool:
        """Indique si le prochain enregistrement doit declencher une rotation.

        Args:
            record (logging.LogRecord): Evenement de log a ecrire.

        Returns:
            bool: `True` si la date a change ou si la taille maximale est depassee.
        """

        if self._current_date_label() != self.current_log_date:
            return True
        if self.max_bytes <= 0:
            return False
        if self.stream is None:
            self.stream = self._open()
        message = f"{self.format(record)}\n"
        self.stream.seek(0, os.SEEK_END)
        return self.stream.tell() + len(message.encode(self.encoding or "utf-8")) > self.max_bytes

    def doRollover(self) -> None:
        """Archive le fichier courant et supprime les anciennes archives.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        if self.stream:
            self.stream.close()
            self.stream = None

        active_file_path = Path(self.baseFilename)
        if active_file_path.exists() and active_file_path.stat().st_size > 0:
            archive_path = self._next_archive_path(self.current_log_date)
            os.replace(active_file_path, archive_path)

        self.current_log_date = self._current_date_label()
        self._delete_old_archives()
        if not self.delay:
            self.stream = self._open()

    def _current_date_label(self) -> str:
        """Retourne la date courante au format de suffixe de fichier.

        Args:
            Aucun.

        Returns:
            str: Date courante au format `YYYY-MM-DD`.
        """

        return self.date_provider().strftime("%Y-%m-%d")

    def _next_archive_path(self, date_label: str) -> Path:
        """Construit le prochain chemin d'archive disponible.

        Args:
            date_label (str): Date a inscrire dans le nom d'archive.

        Returns:
            Path: Chemin d'archive libre.
        """

        active_file_path = Path(self.baseFilename)
        archive_index = 1
        while True:
            archive_path = active_file_path.with_name(
                f"{active_file_path.name}.{date_label}.{archive_index}"
            )
            if not archive_path.exists():
                return archive_path
            archive_index += 1

    def _delete_old_archives(self) -> None:
        """Supprime les archives excedant la retention configuree.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        if self.backup_count <= 0:
            return
        active_file_path = Path(self.baseFilename)
        archives = sorted(
            active_file_path.parent.glob(f"{active_file_path.name}.*.*"),
            key=lambda archive: (archive.stat().st_mtime, archive.name),
        )
        archives_to_delete = archives[: max(0, len(archives) - self.backup_count)]
        for archive_path in archives_to_delete:
            archive_path.unlink(missing_ok=True)
