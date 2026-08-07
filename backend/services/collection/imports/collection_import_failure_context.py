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
# Description : contexte de notification administrateur apres echec d'import.

from dataclasses import dataclass


@dataclass(frozen=True)
class CollectionImportFailureContext:
    """Regroupe les informations envoyees apres un echec d'import.

    Attributes:
        import_kind (str): Type fonctionnel d'import concerne.
        initiated_by_function (str): Fonction applicative qui a lance l'import.
        failing_function (str): Fonction la plus proche de l'exception levee.
        requester_user_id (int | None): Identifiant technique du demandeur si disponible.
        requester_email (str): Email ou sujet d'authentification du demandeur.
        file_type (str): Type de fichier importe si connu.
        original_filename (str): Nom original du fichier si connu.
        error_type (str): Classe de l'erreur observee.
        error_message (str): Message de l'erreur observee.
        traceback_text (str): Traceback formate de l'erreur.
    """

    import_kind: str
    initiated_by_function: str
    failing_function: str
    requester_user_id: int | None
    requester_email: str
    file_type: str
    original_filename: str
    error_type: str
    error_message: str
    traceback_text: str
