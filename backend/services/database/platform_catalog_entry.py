#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : entree normalisee du catalogue applicatif des plateformes.

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class PlatformCatalogEntry:
    """Represente une plateforme issue du catalogue CSV applicatif.

    Attributes:
        name (str): Nom public de la plateforme.
        manufacturer (str): Fabricant public de la plateforme.
        release_date (datetime | None): Date de mise en vente normalisee.
        end_date (datetime | None): Date de retrait normalisee ou absence.
        description (dict[str, Any]): Description JSON structuree.
    """

    name: str
    manufacturer: str
    release_date: datetime | None
    end_date: datetime | None
    description: dict[str, Any]
