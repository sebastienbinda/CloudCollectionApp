#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-15
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : entree normalisee du catalogue des alias de plateformes.

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformAliasCatalogEntry:
    """Represente un alias de plateforme issu du CSV applicatif.

    Attributes:
        platform_name (str): Nom canonique de plateforme cible.
        alias_name (str): Nom alternatif a rattacher.
        category (str): Type fonctionnel de l'alias.
        usage_region (str): Zone ou contexte d'usage.
        comment (str): Commentaire explicatif.
    """

    platform_name: str
    alias_name: str
    category: str
    usage_region: str
    comment: str
