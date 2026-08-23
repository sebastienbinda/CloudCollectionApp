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
# Description : service de creation d'issues GitHub depuis les retours beta.

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .github_feedback_configuration import GitHubFeedbackConfiguration


class GitHubFeedbackService:
    """Cree une issue GitHub a partir d'un retour utilisateur authentifie."""

    CATEGORY_LABELS = {
        "bug": "Bug",
        "idea": "Idee",
        "usability": "Utilisation",
        "other": "Retour",
    }
    MAX_TITLE_LENGTH = 120
    MAX_MESSAGE_LENGTH = 4000
    MIN_MESSAGE_LENGTH = 10

    def __init__(self, configuration: GitHubFeedbackConfiguration, http_post=None):
        """Initialise le service de retour beta.

        Args:
            configuration (GitHubFeedbackConfiguration): Configuration GitHub.
            http_post (Callable | None): Fonction HTTP injectable pour les tests.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration
        self.http_post = http_post or self._post_json

    @classmethod
    def from_environment(cls) -> "GitHubFeedbackService":
        """Construit le service depuis l'environnement.

        Args:
            Aucun.

        Returns:
            GitHubFeedbackService: Service configure.

        Raises:
            RuntimeError: Si la configuration est invalide.
        """

        try:
            return cls(GitHubFeedbackConfiguration.from_environment())
        except ValueError as exc:
            raise RuntimeError("Le service de retours beta n'est pas configure.") from exc

    def submit_feedback(self, payload: dict, requester_subject: str) -> dict:
        """Valide un retour utilisateur et cree l'issue GitHub correspondante.

        Args:
            payload (dict): Donnees du formulaire de retour.
            requester_subject (str): Sujet authentifie ayant envoye le retour.

        Returns:
            dict: Numero et URL publique de l'issue creee.

        Raises:
            ValueError: Si les donnees utilisateur sont invalides.
            RuntimeError: Si GitHub refuse ou ne peut pas traiter la creation.
        """

        feedback = self._normalize_payload(payload)
        github_payload = {
            "title": self._build_issue_title(feedback),
            "body": self._build_issue_body(feedback, requester_subject),
        }
        if self.configuration.labels:
            github_payload["labels"] = list(self.configuration.labels)

        issue = self.http_post(self._issues_url(), github_payload, self.configuration.token)
        return {
            "issue_number": int(issue.get("number", 0)),
            "issue_url": str(issue.get("html_url") or ""),
        }

    def _normalize_payload(self, payload: dict) -> dict:
        title = str(payload.get("title") or "").strip()
        category = str(payload.get("category") or "other").strip().lower()
        message = str(payload.get("message") or "").strip()
        page_url = str(payload.get("page_url") or "").strip()
        user_agent = str(payload.get("user_agent") or "").strip()

        if category not in self.CATEGORY_LABELS:
            raise ValueError("Le type de retour est invalide.")
        if len(message) < self.MIN_MESSAGE_LENGTH:
            raise ValueError("Le retour doit contenir au moins 10 caracteres.")
        if len(message) > self.MAX_MESSAGE_LENGTH:
            raise ValueError("Le retour est trop long.")
        if len(title) > self.MAX_TITLE_LENGTH:
            raise ValueError("Le titre du retour est trop long.")

        return {
            "title": title,
            "category": category,
            "message": message,
            "page_url": page_url[:500],
            "user_agent": user_agent[:500],
        }

    def _build_issue_title(self, feedback: dict) -> str:
        title = feedback["title"] or feedback["message"].splitlines()[0]
        normalized_title = " ".join(title.split())[: self.MAX_TITLE_LENGTH]
        category_label = self.CATEGORY_LABELS[feedback["category"]]
        return f"{self.configuration.title_prefix} {category_label} - {normalized_title}"

    def _build_issue_body(self, feedback: dict, requester_subject: str) -> str:
        return "\n".join([
            "## Retour utilisateur",
            "",
            feedback["message"],
            "",
            "## Contexte",
            "",
            f"- Type : {self.CATEGORY_LABELS[feedback['category']]}",
            f"- Utilisateur applicatif : {requester_subject or 'inconnu'}",
            f"- Page : {feedback['page_url'] or 'non fournie'}",
            f"- Navigateur : {feedback['user_agent'] or 'non fourni'}",
        ])

    def _issues_url(self) -> str:
        return f"https://api.github.com/repos/{self.configuration.repository}/issues"

    @staticmethod
    def _post_json(url: str, payload: dict, token: str) -> dict:
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "CloudCollectionApp",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError("GitHub a refuse la creation du retour.") from exc
        except (OSError, URLError, json.JSONDecodeError) as exc:
            raise RuntimeError("Le service GitHub est temporairement indisponible.") from exc
