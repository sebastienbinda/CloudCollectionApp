#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-01
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : notification utilisateur apres refus admin de jeux.

import os
from pathlib import Path
from typing import Any

from services.email import EmailConfiguration, EmailSenderFactory, EmailTemplateRenderer


class GameValidationUserNotifier:
    """Notifie les utilisateurs impactes par le refus de jeux proposes."""

    def __init__(
        self,
        email_sender=None,
        site_url: str | None = None,
        template_path: str | Path | None = None,
        template_renderer: EmailTemplateRenderer | None = None,
    ):
        """Initialise le notifier utilisateur des refus de jeux.

        Args:
            email_sender (object | None): Expediteur email injectable.
            site_url (str | None): URL publique du site a placer dans le mail.
            template_path (str | Path | None): Chemin optionnel du template texte.
            template_renderer (EmailTemplateRenderer | None): Moteur de rendu injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.email_sender = email_sender
        self.site_url = self._normalize_site_url(site_url or self.default_site_url())
        self.template_path = Path(template_path) if template_path else self.default_template_path()
        self.template_renderer = template_renderer or EmailTemplateRenderer()

    @classmethod
    def from_environment(cls) -> "GameValidationUserNotifier":
        """Construit le notifier depuis l'environnement.

        Args:
            Aucun.

        Returns:
            GameValidationUserNotifier: Notifier configure.
        """

        return cls()

    @classmethod
    def default_template_path(cls) -> Path:
        """Retourne le chemin du template email par defaut.

        Args:
            Aucun.

        Returns:
            Path: Chemin du template stocke dans `backend/resources`.
        """

        return (
            EmailTemplateRenderer.default_resources_directory()
            / "game_validation_refusal_user_notification_template.txt"
        )

    @classmethod
    def default_site_url(cls) -> str:
        """Retourne l'URL publique du site configuree pour les liens email.

        Args:
            Aucun.

        Returns:
            str: URL publique frontend, ou backend local par defaut.
        """

        return os.getenv(
            "FRONTEND_PUBLIC_URL",
            os.getenv("BACKEND_PUBLIC_URL", "http://localhost:7777"),
        )

    def notify_refused_games(self, impacted_users: list[dict[str, Any]]) -> int:
        """Envoie un email aux utilisateurs impactes par des jeux refuses.

        Args:
            impacted_users (list[dict[str, Any]]): Utilisateurs et jeux refuses.

        Returns:
            int: Nombre d'emails envoyes.
        """

        if not impacted_users:
            return 0
        sender = self.email_sender or EmailSenderFactory.create(
            EmailConfiguration.from_environment()
        )
        sent_count = 0
        for impacted_user in impacted_users:
            recipient_email = str(impacted_user.get("user_email") or "").strip()
            if not recipient_email:
                continue
            sender.send_email(
                recipient_email=recipient_email,
                subject="Mise a jour de votre collection",
                body=self._build_email_body(impacted_user),
            )
            sent_count += 1
        return sent_count

    def _build_email_body(self, impacted_user: dict[str, Any]) -> str:
        games = impacted_user.get("games") or []
        game_lines = "\n".join(
            f"- {game['name']} ({game['platform_name']})"
            for game in games
        )
        return self.template_renderer.render(
            self.template_path,
            {
                "game_lines": game_lines,
                "collection_url": f"{self.site_url}/collection",
            },
        )

    def _normalize_site_url(self, site_url: str) -> str:
        return str(site_url or "").strip().rstrip("/") or "http://localhost:7777"
