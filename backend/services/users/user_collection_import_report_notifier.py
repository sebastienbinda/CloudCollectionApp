#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-16
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : protocole de notification du rapport d'import utilisateur.

from typing import Protocol

from .user_collection_import_report_context import UserCollectionImportReportContext


class UserCollectionImportReportNotifier(Protocol):
    """Definit l'envoi du rapport administrateur apres import."""

    def notify_import_report(self, context: UserCollectionImportReportContext) -> None:
        """Envoie le rapport de fin d'import.

        Args:
            context (UserCollectionImportReportContext): Contexte complet de l'import.

        Returns:
            None: La methode ne retourne aucune valeur.
        """
