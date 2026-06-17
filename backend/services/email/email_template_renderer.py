#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-17
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : rendu des templates email stockes dans les ressources backend.

from pathlib import Path
from string import Template


class EmailTemplateRenderer:
    """Rend des emails texte depuis des templates de ressources backend."""

    @classmethod
    def default_resources_directory(cls) -> Path:
        """Retourne le repertoire de ressources backend.

        Args:
            Aucun.

        Returns:
            Path: Chemin absolu vers `backend/resources`.
        """

        return Path(__file__).resolve().parents[2] / "resources"

    def render(self, template_path: str | Path, values: dict[str, object]) -> str:
        """Rend un template texte avec les valeurs fournies.

        Args:
            template_path (str | Path): Chemin du template a lire.
            values (dict[str, object]): Valeurs injectees dans le template.

        Returns:
            str: Corps email rendu.

        Raises:
            OSError: Si le template ne peut pas etre lu.
        """

        template = Path(template_path).read_text(encoding="utf-8")
        return Template(template).safe_substitute(values)
