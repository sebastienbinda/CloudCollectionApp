#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
# Projet : CloudCollectionApp
# Date de creation : 2026-08-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : orchestration non bloquante des notifications d'import refuse.

from .collection_import_models import CollectionImportData
from .collection_import_refusal_context import CollectionImportRefusalContext


class CollectionImportRefusalNotificationService:
    """Construit et envoie les notifications administrateur de refus d'import."""

    def notify_refusal(
        self,
        refusal_notifier: object,
        logger: object,
        import_kind: str,
        requester_user_id: int | None,
        requester_email: str,
        file_type: str,
        original_filename: str,
        refusal: dict,
        import_data: CollectionImportData,
    ) -> None:
        """Envoie une notification de refus sans perturber la reponse d'import.

        Args:
            refusal_notifier (object): Notifier expose par la configuration d'import.
            logger (object): Logger utilise si l'envoi echoue.
            import_kind (str): Type fonctionnel d'import concerne.
            requester_user_id (int | None): Identifiant du demandeur si disponible.
            requester_email (str): Email ou sujet d'authentification du demandeur.
            file_type (str): Type de fichier concerne.
            original_filename (str): Nom de fichier transmis par le client.
            refusal (dict): Decision de refus serialisable.
            import_data (CollectionImportData): Donnees lues et warnings.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        notify_import_refusal = getattr(refusal_notifier, "notify_import_refusal", None)
        if not callable(notify_import_refusal):
            return
        try:
            notify_import_refusal(
                CollectionImportRefusalContext(
                    import_kind=import_kind,
                    requester_user_id=requester_user_id,
                    requester_email=str(requester_email or ""),
                    file_type=str(file_type or ""),
                    original_filename=str(original_filename or ""),
                    refusal=refusal,
                    import_data=import_data,
                )
            )
        except Exception:
            logger.exception("Impossible d'envoyer le rapport de refus d'import.")
