#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-08-07
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : orchestration non bloquante des notifications d'echec d'import.

from pathlib import Path
import traceback

from .collection_import_failure_context import CollectionImportFailureContext


class CollectionImportFailureNotificationService:
    """Construit et envoie les notifications administrateur d'echec d'import."""

    def notify_failure(
        self,
        failure_notifier: object,
        logger: object,
        error: Exception,
        import_kind: str,
        initiated_by_function: str,
        requester_user_id: int | None,
        requester_email: str,
        file_type: str,
        original_filename: str,
    ) -> None:
        """Envoie une notification d'echec sans perturber l'erreur d'origine.

        Args:
            failure_notifier (object): Notifier expose par la configuration d'import.
            logger (object): Logger utilise si l'envoi echoue.
            error (Exception): Erreur d'import observee.
            import_kind (str): Type fonctionnel d'import concerne.
            initiated_by_function (str): Fonction applicative initiatrice.
            requester_user_id (int | None): Identifiant du demandeur si disponible.
            requester_email (str): Email ou sujet d'authentification du demandeur.
            file_type (str): Type de fichier concerne.
            original_filename (str): Nom de fichier transmis par le client.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            Aucun.
        """

        notify_import_failure = getattr(failure_notifier, "notify_import_failure", None)
        if not callable(notify_import_failure):
            return
        try:
            notify_import_failure(
                CollectionImportFailureContext(
                    import_kind=import_kind,
                    initiated_by_function=initiated_by_function,
                    failing_function=self.failing_function_name(error),
                    requester_user_id=requester_user_id,
                    requester_email=str(requester_email or ""),
                    file_type=file_type,
                    original_filename=str(original_filename or ""),
                    error_type=type(error).__name__,
                    error_message=str(error),
                    traceback_text="".join(
                        traceback.format_exception(type(error), error, error.__traceback__)
                    ),
                )
            )
        except Exception:
            logger.exception("Impossible d'envoyer le rapport d'echec d'import.")

    def failing_function_name(self, error: Exception) -> str:
        """Retourne le nom de fonction le plus proche de l'exception.

        Args:
            error (Exception): Erreur dont le traceback doit etre inspecte.

        Returns:
            str: Nom court `fichier.py:function`, ou chaine vide.

        Raises:
            Aucun.
        """

        traceback_entries = traceback.extract_tb(error.__traceback__)
        if not traceback_entries:
            return ""
        last_entry = traceback_entries[-1]
        return f"{Path(last_entry.filename).name}:{last_entry.name}"
