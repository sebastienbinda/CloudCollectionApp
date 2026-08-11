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
# Description : contexte de notification administrateur d'un import refuse.

from dataclasses import dataclass

from .collection_import_models import CollectionImportData


@dataclass(frozen=True)
class CollectionImportRefusalContext:
    """Regroupe les informations envoyees quand un import est refuse.

    Attributes:
        import_kind (str): Type fonctionnel d'import.
        requester_user_id (int | None): Identifiant utilisateur demandeur si connu.
        requester_email (str): Email ou sujet d'authentification du demandeur.
        file_type (str): Type de fichier importe.
        original_filename (str): Nom original du fichier.
        refusal (dict): Decision de refus serialisable.
        import_data (CollectionImportData): Donnees lues et warnings de l'import.
    """

    import_kind: str
    requester_user_id: int | None
    requester_email: str
    file_type: str
    original_filename: str
    refusal: dict
    import_data: CollectionImportData
