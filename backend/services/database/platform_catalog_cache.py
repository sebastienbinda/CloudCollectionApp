#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : cache serveur du catalogue applicatif des plateformes.

import copy
import time
from threading import RLock
from typing import Any, Callable


class PlatformCatalogCache:
    """Met en cache le catalogue applicatif des plateformes avec expiration."""

    DEFAULT_TTL_SECONDS = 5 * 60 * 60
    _entries: dict[str, tuple[float, list[dict[str, Any]]]] = {}
    _lock = RLock()

    def __init__(
        self,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ):
        """Initialise le cache du catalogue plateformes.

        Args:
            ttl_seconds (int): Duree de validite du cache en secondes.
            clock (Callable[[], float]): Horloge injectable pour les tests.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.ttl_seconds = ttl_seconds
        self.clock = clock

    def remember(self, schema_name: str, loader: Callable[[], list[dict[str, Any]]]):
        """Retourne les plateformes en cache ou les charge depuis la base.

        Args:
            schema_name (str): Nom du schema PostgreSQL servant de cle de cache.
            loader (Callable[[], list[dict[str, Any]]]): Chargement en cas de miss.

        Returns:
            list[dict[str, Any]]: Copie des plateformes cachees.
        """

        with self._lock:
            now = self.clock()
            expires_at, rows = self._entries.get(schema_name, (0, []))
            if now >= expires_at:
                rows = loader()
                self._entries[schema_name] = (now + self.ttl_seconds, rows)
            return copy.deepcopy(rows)

    def invalidate(self, schema_name: str) -> int:
        """Invalide le catalogue cache pour un schema.

        Args:
            schema_name (str): Nom du schema PostgreSQL a vider.

        Returns:
            int: `1` si une entree existait, sinon `0`.
        """

        with self._lock:
            existed = schema_name in self._entries
            self._entries.pop(schema_name, None)
            return 1 if existed else 0
