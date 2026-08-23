#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : configuration GitHub utilisee pour les retours beta.

from dataclasses import dataclass
import os

from services.security import EnvironmentSecretReader


@dataclass(frozen=True)
class GitHubFeedbackConfiguration:
    """Decrit la configuration de creation d'issues GitHub pour les retours beta."""

    repository: str
    token: str
    labels: tuple[str, ...]
    title_prefix: str

    DEFAULT_LABELS = ("feedback", "remarque")
    DEFAULT_TITLE_PREFIX = "[Retour utilisateur]"

    @classmethod
    def from_environment(cls) -> "GitHubFeedbackConfiguration":
        """Construit la configuration depuis les variables d'environnement.

        Args:
            Aucun.

        Returns:
            GitHubFeedbackConfiguration: Configuration GitHub lue et nettoyee.

        Raises:
            ValueError: Si une valeur configuree est invalide.
        """

        labels = cls._parse_labels(os.getenv("GITHUB_FEEDBACK_LABELS", "feedback,remarque"))
        configuration = cls(
            repository=(os.getenv("GITHUB_FEEDBACK_REPOSITORY") or "").strip(),
            token=(EnvironmentSecretReader.read("GITHUB_FEEDBACK_TOKEN") or "").strip(),
            labels=labels,
            title_prefix=(
                os.getenv("GITHUB_FEEDBACK_TITLE_PREFIX", cls.DEFAULT_TITLE_PREFIX).strip()
                or cls.DEFAULT_TITLE_PREFIX
            ),
        )
        configuration.validate()
        return configuration

    def validate(self) -> None:
        """Valide la coherence de la configuration GitHub.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            ValueError: Si le depot ou le token est invalide.
        """

        if "/" not in self.repository or len(self.repository.split("/")) != 2:
            raise ValueError("GITHUB_FEEDBACK_REPOSITORY doit utiliser le format owner/repository.")
        if not self.token:
            raise ValueError("GITHUB_FEEDBACK_TOKEN est requis pour creer une issue GitHub.")

    @classmethod
    def _parse_labels(cls, raw_labels: str) -> tuple[str, ...]:
        labels = tuple(
            label.strip()
            for label in str(raw_labels or "").split(",")
            if label.strip()
        )
        return labels or cls.DEFAULT_LABELS
