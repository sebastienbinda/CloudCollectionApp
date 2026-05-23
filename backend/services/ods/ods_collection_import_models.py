#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : modeles metier de lecture d'import de collection ODS.

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class OdsCollectionImportPlatform:
    """Represente une plateforme lue depuis un onglet ODS importable.

    Attributes:
        name (str): Nom de la plateforme issue du nom d'onglet.
    """

    name: str


@dataclass(frozen=True)
class OdsCollectionImportStudio:
    """Represente un studio lu depuis une ligne de jeu ODS.

    Attributes:
        name (str): Nom du studio.
    """

    name: str


@dataclass(frozen=True)
class OdsCollectionImportGame:
    """Represente un jeu lu depuis une feuille de plateforme ODS.

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
class OdsCollectionImportData:
    """Regroupe les donnees metier extraites d'un fichier ODS de collection.

    Attributes:
        platforms (list[OdsCollectionImportPlatform]): Plateformes importables.
        studios (list[OdsCollectionImportStudio]): Studios presents dans les jeux.
        games (list[OdsCollectionImportGame]): Jeux presents dans les onglets plateforme.
    """

    platforms: list[OdsCollectionImportPlatform]
    studios: list[OdsCollectionImportStudio]
    games: list[OdsCollectionImportGame]
