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
# Description : contexte serialisable du rapport administrateur d'import utilisateur.

from dataclasses import dataclass


@dataclass(frozen=True)
class UserCollectionImportReportContext:
    """Regroupe les informations envoyees dans le rapport d'import administrateur.

    Attributes:
        user_id (int): Identifiant de l'utilisateur importe.
        user_email (str): Adresse email de l'utilisateur importe.
        file_type (str): Type de fichier traite.
        original_filename (str): Nom de fichier fourni ou conserve.
        source_mode (str): Mode de source utilise par l'import.
        copied_to_workspace (bool): Indique si le fichier a ete copie avant lecture.
        linked_platforms (int): Nombre de plateformes rattachees.
        created_studios (int): Nombre de studios crees.
        created_games (int): Nombre de jeux crees.
        associated_games (int): Nombre de jeux associes a l'utilisateur.
        wishlisted_games (int): Nombre de jeux importes en liste de souhaits.
        warnings (object): Avertissements et metadonnees de l'import.
        collection_file_description (dict): Configuration valide utilisee.
        created_game_match_reports (tuple): Jeux crees avec meilleur candidat existant.
    """

    user_id: int
    user_email: str
    file_type: str
    original_filename: str
    source_mode: str
    copied_to_workspace: bool
    linked_platforms: int
    created_studios: int
    created_games: int
    associated_games: int
    wishlisted_games: int
    warnings: object
    collection_file_description: dict
    created_game_match_reports: tuple = ()
