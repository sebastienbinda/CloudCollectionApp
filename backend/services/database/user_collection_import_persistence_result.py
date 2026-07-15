#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-07-04
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : resultats de persistance d'un import de collection utilisateur.

from dataclasses import dataclass


@dataclass(frozen=True)
class CreatedGameMatchReport:
    """Decrit un jeu cree faute de rattachement a un jeu existant.

    Attributes:
        imported_game_name (str): Nom du jeu cree depuis l'import.
        platform_name (str): Plateforme du jeu cree.
        best_existing_game_name (str): Meilleur candidat existant trouve.
        best_score (int): Score du meilleur candidat.
    """

    imported_game_name: str
    platform_name: str
    best_existing_game_name: str
    best_score: int


@dataclass(frozen=True)
class ImportedGameMatchReport:
    """Decrit le diagnostic de matching d'un jeu importe.

    Attributes:
        imported_game_name (str): Nom d'origine du jeu dans le fichier utilisateur.
        created (bool): Indique si un nouveau jeu de reference a ete cree.
        associated_game_name (str): Nom du jeu existant retenu quand il existe.
        score (int): Score final utilise pour la decision.
        decision (str): Decision du moteur de matching.
        rule (str): Regle de matching appliquee.
        reason (str): Raison explicative du matching.
    """

    imported_game_name: str
    created: bool
    associated_game_name: str
    score: int
    decision: str
    rule: str
    reason: str


@dataclass(frozen=True)
class ImportedStudioMatchReport:
    """Decrit le diagnostic de matching d'un studio importe.

    Attributes:
        imported_studio_name (str): Nom d'origine du studio dans le fichier utilisateur.
        created (bool): Indique si un nouveau studio de reference a ete cree.
        associated_studio_name (str): Nom du studio existant retenu quand il existe.
        score (int): Score de matching du meilleur candidat.
    """

    imported_studio_name: str
    created: bool
    associated_studio_name: str
    score: int


@dataclass(frozen=True)
class UserCollectionImportPersistenceResult:
    """Regroupe les compteurs de persistance d'un import de collection.

    Attributes:
        linked_platforms (int): Nombre de plateformes du referentiel liees.
        created_studios (int): Nombre de studios crees.
        created_games (int): Nombre de jeux crees.
        associated_games (int): Nombre de jeux rattaches a l'utilisateur.
        user_email (str): Adresse email de l'utilisateur importe.
        created_game_match_reports (tuple[CreatedGameMatchReport, ...]): Jeux crees
            avec leur meilleur candidat de matching.
        imported_game_match_reports (tuple[ImportedGameMatchReport, ...]): Diagnostic
            de matching pour chaque jeu importe.
        imported_studio_match_reports (tuple[ImportedStudioMatchReport, ...]): Diagnostic
            de matching pour chaque studio importe.
    """

    linked_platforms: int
    created_studios: int
    created_games: int
    associated_games: int
    user_email: str = ""
    created_game_match_reports: tuple[CreatedGameMatchReport, ...] = ()
    imported_game_match_reports: tuple[ImportedGameMatchReport, ...] = ()
    imported_studio_match_reports: tuple[ImportedStudioMatchReport, ...] = ()
