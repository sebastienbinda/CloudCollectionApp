#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-07-21
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : politique d'activation du rapport administrateur d'import.


class UserCollectionImportReportPolicy:
    """Determine si le rapport administrateur d'import doit etre construit."""

    def is_enabled(self, report_notifier: object) -> bool:
        """Indique si le notifier accepte la construction d'un rapport.

        Args:
            report_notifier (object): Notifier configure pour le service d'import.

        Returns:
            bool: `False` uniquement lorsque le notifier declare etre desactive.
        """

        is_enabled = getattr(report_notifier, "is_enabled", None)
        if callable(is_enabled):
            return bool(is_enabled())
        return True
