#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-28
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : lecture centralisee des secrets depuis l'environnement ou un fichier.

import os
from pathlib import Path
from typing import Optional


class EnvironmentSecretReader:
    """Lit des valeurs sensibles depuis une variable ou un fichier de secret.

    La convention `NOM_FILE` permet aux conteneurs Docker d'utiliser des secrets
    montes dans `/run/secrets` sans exposer la valeur sensible dans
    l'environnement du processus.
    """

    @classmethod
    def read(cls, env_name: str, default_value: Optional[str] = None) -> Optional[str]:
        """Lit une valeur depuis `env_name_FILE`, puis depuis `env_name`.

        Args:
            env_name (str): Nom de la variable d'environnement fonctionnelle.
            default_value (Optional[str]): Valeur retournee quand aucune source
                n'est definie.

        Returns:
            Optional[str]: Valeur lue depuis le fichier, la variable ou le
            defaut.

        Raises:
            ValueError: Si le fichier reference par `env_name_FILE` est
                illisible.
        """

        file_path = os.getenv(f"{env_name}_FILE")
        if file_path:
            return cls._read_file(file_path, env_name)
        return os.getenv(env_name, default_value)

    @classmethod
    def _read_file(cls, file_path: str, env_name: str) -> str:
        """Lit le contenu texte d'un fichier de secret.

        Args:
            file_path (str): Chemin du fichier a lire.
            env_name (str): Nom de la variable fonctionnelle pour le message
                d'erreur.

        Returns:
            str: Contenu du fichier sans retour ligne final.

        Raises:
            ValueError: Si le fichier est absent ou illisible.
        """

        try:
            return Path(file_path).read_text(encoding="utf-8").rstrip("\r\n")
        except OSError as exc:
            raise ValueError(f"{env_name}_FILE pointe vers un fichier de secret illisible.") from exc
