#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : modeles metier generiques issus d'un fichier de collection.

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class CollectionImportPlatform:
    """Represente une plateforme importee depuis un fichier de collection.

    Attributes:
        name (str): Nom de la plateforme.
    """

    name: str


@dataclass(frozen=True)
class CollectionImportStudio:
    """Represente un studio importe depuis un fichier de collection.

    Attributes:
        name (str): Nom du studio.
    """

    name: str


@dataclass(frozen=True)
class CollectionImportGame:
    """Represente un jeu importe depuis un fichier de collection.

    Attributes:
        name (str): Nom du jeu.
        platform_name (str): Nom de la plateforme de rattachement.
        studio_name (Optional[str]): Nom du studio developpeur si renseigne.
        release_date (Optional[date]): Date de sortie valide ou `None`.
    """

    name: str
    platform_name: str
    studio_name: Optional[str]
    release_date: Optional[date]


@dataclass(frozen=True)
class CollectionImportData:
    """Regroupe les donnees metier extraites d'un fichier de collection.

    Attributes:
        platforms (list[CollectionImportPlatform]): Plateformes importables.
        studios (list[CollectionImportStudio]): Studios presents dans les jeux.
        games (list[CollectionImportGame]): Jeux presents dans le fichier.
    """

    platforms: list[CollectionImportPlatform]
    studios: list[CollectionImportStudio]
    games: list[CollectionImportGame]
