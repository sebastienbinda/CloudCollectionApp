#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
# Projet : CloudCollectionApp
# Date de creation : 2026-05-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : fournisseur singleton du service Bibliotheque.

from threading import Lock
from typing import Callable

from services.database.database_configuration import DatabaseConfiguration

from .library_service import LibraryService


class LibraryServiceProvider:
    """Fournit une instance singleton de `LibraryService`.

    Attributes:
        service_factory (Callable[[], LibraryService]): Fabrique utilisee pour
            construire le service lors du premier appel.
    """

    def __init__(self, service_factory: Callable[[], LibraryService] | None = None):
        """Initialise le fournisseur singleton.

        Args:
            service_factory (Callable[[], LibraryService] | None): Fabrique injectable du service.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.service_factory = service_factory or self._create_default_service
        self._service: LibraryService | None = None
        self._lock = Lock()

    def __call__(self) -> LibraryService:
        """Retourne le singleton via une interface de fabrique.

        Args:
            Aucun.

        Returns:
            LibraryService: Instance partagee du service Bibliotheque.
        """

        return self.get_service()

    def get_service(self) -> LibraryService:
        """Retourne le service Bibliotheque partage.

        Args:
            Aucun.

        Returns:
            LibraryService: Instance partagee creee au premier appel.
        """

        if self._service is None:
            with self._lock:
                if self._service is None:
                    self._service = self.service_factory()
        return self._service

    def reset(self) -> None:
        """Vide l'instance singleton memorisee.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        with self._lock:
            self._service = None

    def _create_default_service(self) -> LibraryService:
        """Construit le service Bibliotheque par defaut.

        Args:
            Aucun.

        Returns:
            LibraryService: Service configure depuis l'environnement.
        """

        return LibraryService(DatabaseConfiguration.from_environment())
