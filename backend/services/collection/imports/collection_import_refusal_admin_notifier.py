#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
# Projet : CloudCollectionApp
# Date de creation : 2026-08-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : notification administrateur d'un import refuse apres lecture.

import os
from html import escape
from pathlib import Path

from services.email import EmailConfiguration, EmailSenderFactory, EmailTemplateRenderer

from .collection_import_refusal_context import CollectionImportRefusalContext


class CollectionImportRefusalAdminNotifier:
    """Envoie un email administrateur quand un import est refuse."""

    def __init__(
        self,
        email_sender=None,
        admin_notification_email: str | None = None,
        template_path: str | Path | None = None,
        template_renderer: EmailTemplateRenderer | None = None,
    ):
        """Initialise le notifier de refus d'import.

        Args:
            email_sender (object | None): Expediteur email injectable.
            admin_notification_email (str | None): Adresse administrateur destinataire.
            template_path (str | Path | None): Chemin optionnel du template HTML.
            template_renderer (EmailTemplateRenderer | None): Moteur de rendu injectable.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.email_sender = email_sender
        if admin_notification_email is None:
            admin_notification_email = os.getenv("ADMIN_NOTIFICATION_EMAIL", "")
        self.admin_notification_email = str(admin_notification_email or "").strip()
        self.template_path = Path(template_path) if template_path else self.default_template_path()
        self.template_renderer = template_renderer or EmailTemplateRenderer()

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
            / "collection_import_refusal_email_template.txt"
        )

    def is_enabled(self) -> bool:
        """Indique si une notification de refus peut etre envoyee.

        Args:
            Aucun.

        Returns:
            bool: `True` lorsqu'une adresse administrateur est configuree.
        """

        return bool(self.admin_notification_email)

    def notify_import_refusal(self, context: CollectionImportRefusalContext) -> None:
        """Envoie le rapport de refus d'import a l'administrateur.

        Args:
            context (CollectionImportRefusalContext): Contexte complet du refus.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        if not self.admin_notification_email:
            return
        email_sender = self.email_sender or EmailSenderFactory.create(
            EmailConfiguration.from_environment()
        )
        email_sender.send_email(
            recipient_email=self.admin_notification_email,
            subject=f"Import refuse - {context.import_kind}",
            body=self._build_email_body(context),
            content_subtype="html",
        )

    def _build_email_body(self, context: CollectionImportRefusalContext) -> str:
        warnings = context.import_data.warnings
        return self.template_renderer.render(
            self.template_path,
            {
                "import_kind": escape(context.import_kind),
                "requester_user_id": self._requester_user_id(context.requester_user_id),
                "requester_email": escape(context.requester_email or "inconnu"),
                "file_type": escape(context.file_type or "inconnu"),
                "original_filename": escape(context.original_filename or "inconnu"),
                "reason": escape(str(context.refusal.get("reason") or "")),
                "message": escape(str(context.refusal.get("message") or "")),
                "invalid_games_count": int(context.refusal.get("invalid_games_count") or 0),
                "total_games_count": int(context.refusal.get("total_games_count") or 0),
                "linked_platforms": 0,
                "created_studios": 0,
                "created_games": 0,
                "associated_games": 0,
                "wishlisted_games": 0,
                "warnings": escape(self._warnings_text(warnings)),
                "invalid_games": self._invalid_games_html(warnings.invalid_games),
            },
        )

    def _requester_user_id(self, requester_user_id: int | None) -> str:
        return escape(str(requester_user_id)) if requester_user_id is not None else "inconnu"

    def _warnings_text(self, warnings: object) -> str:
        lines = [
            "Warnings:",
            f"- Wishlist invalide: {int(getattr(warnings, 'invalid_wishlist', 0) or 0)}",
            f"- Jeux invalides: {len(getattr(warnings, 'invalid_games', []) or [])}",
            f"- Jeux ignores: {len(getattr(warnings, 'skipped_games', []) or [])}",
            f"- Plateformes a verifier: {len(getattr(warnings, 'platform_matches', []) or [])}",
        ]
        invalid_values = list(getattr(warnings, "invalid_wishlist_values_found", []) or [])
        if invalid_values:
            lines.append("- Valeurs wishlist invalides: " + ", ".join(map(str, invalid_values)))
        return "\n".join(lines)

    def _invalid_games_html(self, invalid_games: list[dict]) -> str:
        if not invalid_games:
            return "<p>Aucun jeu avec information invalide.</p>"
        rows = []
        for invalid_game in invalid_games:
            rows.append(
                "<tr>"
                f"<td>{escape(str(invalid_game.get('name') or ''))}</td>"
                f"<td>{escape(self._invalid_fields_text(invalid_game.get('invalid_fields') or []))}</td>"
                "</tr>"
            )
        return (
            '<table border="1" cellpadding="6" cellspacing="0">'
            "<thead><tr><th>Jeu</th><th>Erreurs</th></tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table>"
        )

    def _invalid_fields_text(self, invalid_fields: list[dict]) -> str:
        values = []
        for invalid_field in invalid_fields:
            field_name = str(invalid_field.get("field") or "")
            field_value = str(invalid_field.get("value") or "")
            values.append(f"{field_name}: {field_value}" if field_value else field_name)
        return ", ".join(values)
