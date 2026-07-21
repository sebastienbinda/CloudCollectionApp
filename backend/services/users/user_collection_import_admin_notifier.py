#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-16
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : notification administrateur de fin d'import utilisateur.

import json
import os
from html import escape
from pathlib import Path

from services.email import EmailConfiguration, EmailSenderFactory, EmailTemplateRenderer

from .user_collection_import_report_context import UserCollectionImportReportContext


class UserCollectionImportAdminNotifier:
    """Envoie un rapport administrateur unique apres chaque import utilisateur."""

    def __init__(
        self,
        email_sender=None,
        admin_notification_email: str | None = None,
        template_path: str | Path | None = None,
        template_renderer: EmailTemplateRenderer | None = None,
    ):
        """Initialise le notifier administrateur.

        Args:
            email_sender (object | None): Expediteur email injectable.
            admin_notification_email (str | None): Adresse administrateur destinataire.
            template_path (str | Path | None): Chemin optionnel du template texte.
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
    def from_environment(cls) -> "UserCollectionImportAdminNotifier":
        """Construit le notifier depuis l'environnement.

        Args:
            Aucun.

        Returns:
            UserCollectionImportAdminNotifier: Notifier configure.
        """

        return cls(admin_notification_email=os.getenv("ADMIN_NOTIFICATION_EMAIL", ""))

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
            / "user_collection_import_report_email_template.txt"
        )

    def notify_import_report(self, context: UserCollectionImportReportContext) -> None:
        """Envoie le rapport de fin d'import a l'administrateur.

        Args:
            context (UserCollectionImportReportContext): Contexte complet de l'import.

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
            subject="Rapport d'import de collection utilisateur",
            body=self._build_email_body(context),
            content_subtype="html",
        )

    def is_enabled(self) -> bool:
        """Indique si un rapport administrateur peut etre envoye.

        Args:
            Aucun.

        Returns:
            bool: `True` lorsqu'une adresse administrateur est configuree.
        """

        return bool(self.admin_notification_email)

    def _build_email_body(self, context: UserCollectionImportReportContext) -> str:
        warnings_lines = []
        self._append_warnings(warnings_lines, context.warnings)
        return self.template_renderer.render(
            self.template_path,
            {
                "user_id": context.user_id,
                "user_email": escape(str(context.user_email)),
                "file_type": escape(str(context.file_type)),
                "original_filename": escape(str(context.original_filename)),
                "source_mode": escape(str(context.source_mode)),
                "copied_to_workspace": "oui" if context.copied_to_workspace else "non",
                "linked_platforms": context.linked_platforms,
                "created_studios": context.created_studios,
                "created_games": context.created_games,
                "associated_games": context.associated_games,
                "wishlisted_games": context.wishlisted_games,
                "imported_game_match_reports": self._imported_game_match_reports_html(
                    context.imported_game_match_reports,
                ),
                "imported_studio_match_reports": self._imported_studio_match_reports_html(
                    context.imported_studio_match_reports,
                ),
                "total_import_duration_seconds": "{duration:.3f}".format(
                    duration=float(
                        getattr(context.warnings, "total_import_duration_seconds", 0.0)
                        or 0.0
                    ),
                ),
                "file_read_duration_seconds": self._format_duration(
                    context.file_read_duration_seconds
                ),
                "association_calculation_duration_seconds": self._format_duration(
                    context.association_calculation_duration_seconds
                ),
                "database_query_duration_seconds": self._format_duration(
                    context.database_query_duration_seconds
                ),
                "collection_file_description": escape(
                    json.dumps(
                        context.collection_file_description,
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                ),
                "warnings": escape("\n".join(warnings_lines)),
            },
        )

    def _format_duration(self, duration_seconds: object) -> str:
        return "{duration:.3f}".format(duration=float(duration_seconds or 0.0))

    def _imported_studio_match_reports_html(self, imported_studio_match_reports: tuple) -> str:
        if not imported_studio_match_reports:
            return "<p>Aucun studio importe.</p>"
        rows = []
        for report in imported_studio_match_reports:
            rows.append(
                "<tr>"
                f"<td>{self._html_value(getattr(report, 'imported_studio_name', ''))}</td>"
                f"<td>{'Oui' if getattr(report, 'created', False) else 'Non'}</td>"
                f"<td>{self._html_value(getattr(report, 'associated_studio_name', ''))}</td>"
                f"<td>{int(getattr(report, 'score', 0) or 0)}</td>"
                "</tr>"
            )
        return (
            '<table border="1" cellpadding="6" cellspacing="0">'
            "<thead><tr>"
            "<th>Nom du studio importé</th>"
            "<th>Créé</th>"
            "<th>Nom du Studio associé</th>"
            "<th>Score de matching</th>"
            "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table>"
        )

    def _imported_game_match_reports_html(self, imported_game_match_reports: tuple) -> str:
        if not imported_game_match_reports:
            return "<p>Aucun jeu importe.</p>"
        rows = []
        for report in imported_game_match_reports:
            rows.append(
                "<tr>"
                f"<td>{self._html_value(getattr(report, 'imported_game_name', ''))}</td>"
                f"<td>{'Oui' if getattr(report, 'created', False) else 'Non'}</td>"
                f"<td>{self._html_value(getattr(report, 'associated_game_name', ''))}</td>"
                f"<td>{int(getattr(report, 'score', 0) or 0)}</td>"
                f"<td>{self._html_value(getattr(report, 'decision', ''))}</td>"
                f"<td>{self._html_value(getattr(report, 'rule', ''))}</td>"
                f"<td>{self._html_value(getattr(report, 'reason', ''))}</td>"
                "</tr>"
            )
        return (
            '<table border="1" cellpadding="6" cellspacing="0">'
            "<thead><tr>"
            "<th>Nom</th>"
            "<th>Créé</th>"
            "<th>Jeu associé</th>"
            "<th>Score</th>"
            "<th>Decision</th>"
            "<th>Rule</th>"
            "<th>Raison</th>"
            "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table>"
        )

    def _html_value(self, value) -> str:
        text = str(value or "")
        return escape(text) if text else "&nbsp;"

    def _append_warnings(self, lines: list[str], warnings: object) -> None:
        platform_mappings = list(getattr(warnings, "platform_mappings", []) or [])
        manual_matches = list(getattr(warnings, "platform_matches", []) or [])
        skipped_games = list(getattr(warnings, "skipped_games", []) or [])
        invalid_games = list(getattr(warnings, "invalid_games", []) or [])
        invalid_wishlist = int(getattr(warnings, "invalid_wishlist", 0) or 0)
        invalid_wishlist_values = list(
            getattr(warnings, "invalid_wishlist_values_found", []) or []
        )
        if not any(
            [
                platform_mappings,
                manual_matches,
                skipped_games,
                invalid_games,
                invalid_wishlist,
            ]
        ):
            lines.append("Warnings: aucun warning detecte.")
            return
        lines.append("Warnings:")
        self._append_platform_mappings(lines, platform_mappings)
        self._append_manual_matches(lines, manual_matches)
        self._append_skipped_games(lines, skipped_games)
        self._append_invalid_games(lines, invalid_games)
        self._append_invalid_wishlist(lines, invalid_wishlist, invalid_wishlist_values)

    def _append_platform_mappings(self, lines: list[str], platform_mappings: list[dict]) -> None:
        if not platform_mappings:
            return
        lines.append("Mappings plateformes:")
        for mapping in platform_mappings:
            alias_text = "oui" if mapping.get("matched_by_alias") else "non"
            matched_alias = str(mapping.get("matched_alias") or "")
            if matched_alias:
                alias_text = f"{alias_text} ({matched_alias})"
            lines.append(
                "- Plateforme lue: {imported_platform} | Plateforme rattachee: "
                "{matched_platform} | Score: {score} | Jeux: {games_count} | "
                "Alias: {alias_text}".format(alias_text=alias_text, **mapping)
            )

    def _append_manual_matches(self, lines: list[str], manual_matches: list[dict]) -> None:
        if not manual_matches:
            return
        lines.append("Warnings de verification manuelle:")
        for match in manual_matches:
            lines.append(
                "- Jeu: {game_name} | Plateforme importee: {imported_platform} | "
                "Plateforme rattachee: {matched_platform} | Score: {score}".format(
                    **match
                )
            )

    def _append_skipped_games(self, lines: list[str], skipped_games: list[dict]) -> None:
        if not skipped_games:
            return
        lines.append("Jeux ignores:")
        for skipped_game in skipped_games:
            lines.append(
                "- Jeu: {game_name} | Plateforme importee: {imported_platform} | "
                "Score: {score} | Raison: {reason}".format(**skipped_game)
            )

    def _append_invalid_games(self, lines: list[str], invalid_games: list[dict]) -> None:
        if not invalid_games:
            return
        lines.append("Jeux importes avec informations invalides ignorees:")
        for invalid_game in invalid_games:
            lines.append("- Jeu: {name}".format(**invalid_game))

    def _append_invalid_wishlist(
        self,
        lines: list[str],
        invalid_wishlist: int,
        invalid_wishlist_values: list[str],
    ) -> None:
        if invalid_wishlist <= 0:
            return
        lines.append(
            "Wishlist invalide: {count} ligne(s) ignoree(s).".format(
                count=invalid_wishlist,
            )
        )
        if invalid_wishlist_values:
            lines.append("Valeurs detectees: " + ", ".join(invalid_wishlist_values))
