#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/|_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : notification utilisateur apres fusion administrative d'un doublon.

import os
from pathlib import Path
from typing import Any

from services.email import EmailConfiguration, EmailSenderFactory, EmailTemplateRenderer


class GameDuplicateUserNotifier:
    """Notifie les utilisateurs impactes par une fusion de doublon flague."""

    def __init__(
        self,
        email_sender=None,
        site_url: str | None = None,
        template_path: str | Path | None = None,
        template_renderer: EmailTemplateRenderer | None = None,
    ):
        """Initialise le notifier utilisateur des fusions de doublons.

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
    def from_environment(cls) -> "GameDuplicateUserNotifier":
        """Construit le notifier depuis l'environnement.

        Args:
            Aucun.

        Returns:
            GameDuplicateUserNotifier: Notifier configure.
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
            / "game_duplicate_user_merge_notification_template.txt"
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

    def notify_merge(
        self,
        impacted_users: list[dict[str, Any]],
        duplicate_game: dict[str, Any],
        target_game: dict[str, Any],
    ) -> int:
        """Envoie un mail aux utilisateurs impactes par la fusion.

        Args:
            impacted_users (list[dict[str, Any]]): Utilisateurs impactes.
            duplicate_game (dict[str, Any]): Jeu supprime par la fusion.
            target_game (dict[str, Any]): Jeu conserve par la fusion.

        Returns:
            int: Nombre de mails envoyes.
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
                body=self._build_email_body(impacted_user, duplicate_game, target_game),
            )
            sent_count += 1
        return sent_count

    def _build_email_body(
        self,
        impacted_user: dict[str, Any],
        duplicate_game: dict[str, Any],
        target_game: dict[str, Any],
    ) -> str:
        had_target_game = bool(impacted_user.get("had_target_game"))
        impact_description = (
            "Vous possediez deja le jeu conserve. Les deux entrees de votre collection "
            "ont ete fusionnees en une seule entree."
            if had_target_game
            else "L'entree rattachee au doublon a ete remplacee par le jeu conserve."
        )
        target_game_id = int(target_game.get("id") or 0)
        return self.template_renderer.render(
            self.template_path,
            {
                "duplicate_game_name": str(duplicate_game.get("name") or ""),
                "target_game_name": str(target_game.get("name") or ""),
                "platform_name": str(target_game.get("platform_name") or ""),
                "impact_description": impact_description,
                "collection_url": f"{self.site_url}/collection",
                "target_game_url": f"{self.site_url}/collection/jeux/{target_game_id}",
            },
        )

    def _normalize_site_url(self, site_url: str) -> str:
        return str(site_url or "").strip().rstrip("/") or "http://localhost:7777"
