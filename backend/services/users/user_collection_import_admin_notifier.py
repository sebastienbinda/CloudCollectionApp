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
import re
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
                "error_counters": self._error_counters_html(context),
                "manual_platform_mappings": self._manual_platform_mappings_html(
                    list(getattr(context.warnings, "platform_matches", []) or []),
                ),
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
                "collection_file_description": self._collection_file_description_html(
                    context.collection_file_description
                ),
            },
        )

    def _format_duration(self, duration_seconds: object) -> str:
        return "{duration:.3f}".format(duration=float(duration_seconds or 0.0))

    def _collection_file_description_html(self, collection_file_description: dict) -> str:
        json_text = json.dumps(
            collection_file_description,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        token_pattern = re.compile(
            r'("(?:\\.|[^"\\])*")(\s*:)?'
            r"|\b(true|false|null)\b"
            r"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"
        )
        html_parts = []
        last_index = 0
        for match in token_pattern.finditer(json_text):
            html_parts.append(escape(json_text[last_index : match.start()]))
            token = match.group(0)
            if match.group(1) and match.group(2):
                html_parts.append(self._json_span(token, "#0f5e9c", "600"))
            elif match.group(1):
                html_parts.append(self._json_span(token, "#277a3f", "400"))
            elif match.group(3):
                html_parts.append(self._json_span(token, "#8a4f00", "600"))
            else:
                html_parts.append(self._json_span(token, "#7c3aed", "600"))
            last_index = match.end()
        html_parts.append(escape(json_text[last_index:]))
        return "".join(html_parts)

    def _json_span(self, token: str, color: str, font_weight: str) -> str:
        return (
            f'<span style="color:{color};font-weight:{font_weight};">'
            f"{escape(token)}</span>"
        )

    def _table_html(self, headers: list[str], rows: list[str]) -> str:
        return (
            '<table border="1" cellpadding="6" cellspacing="0" '
            'style="border-collapse:collapse;width:100%;margin:8px 0 16px 0;'
            'border:1px solid #cbd5e1;">'
            + self._table_header_html(headers)
            + "<tbody>"
            + "".join(rows)
            + "</tbody></table>"
        )

    def _table_header_html(self, headers: list[str]) -> str:
        cells = []
        for header in headers:
            cells.append(
                '<th style="background:#e8f1ff;color:#1e3a5f;'
                'border:1px solid #cbd5e1;text-align:left;">'
                f"{escape(header)}</th>"
            )
        return "<thead><tr>" + "".join(cells) + "</tr></thead>"

    def _table_row_html(self, cells: list[str], background_color: str = "") -> str:
        style = f' style="background:{background_color};"' if background_color else ""
        return f"<tr{style}>" + "".join(cells) + "</tr>"

    def _table_cell_html(self, html_value: str, extra_style: str = "") -> str:
        style = "border:1px solid #cbd5e1;vertical-align:top;"
        if extra_style:
            style += extra_style
        return f'<td style="{style}">{html_value}</td>'

    def _created_status_cell_html(self, created: bool) -> str:
        if created:
            return self._table_cell_html(
                '<strong style="color:#166534;">Oui</strong>',
                "background:#dcfce7;",
            )
        return self._table_cell_html('<span style="color:#475569;">Non</span>')

    def _error_counters_html(self, context: UserCollectionImportReportContext) -> str:
        warnings = context.warnings
        skipped_games_count = len(getattr(warnings, "skipped_games", []) or [])
        skipped_mandatory_games_count = int(
            getattr(warnings, "skipped_mandatory_games", 0) or 0
        )
        invalid_games_count = len(getattr(warnings, "invalid_games", []) or [])
        blocking_errors_count = (
            invalid_games_count + skipped_games_count + skipped_mandatory_games_count
        )
        total_games_count = (
            int(context.associated_games or 0)
            + skipped_games_count
            + skipped_mandatory_games_count
        )
        counters = [
            (
                "Jeux avec erreur bloquante",
                blocking_errors_count,
                "Total qui aurait ete utilise pour refuser le fichier.",
            ),
            (
                "Jeux lus dans le fichier",
                total_games_count,
                "Base de calcul du seuil de refus.",
            ),
            (
                "Jeux avec information invalide",
                invalid_games_count,
                "Au moins une valeur refusee dans un champ importe.",
            ),
            (
                "Jeux refuses ou ignores",
                skipped_games_count,
                "Jeux non importes, par exemple plateforme non reconnue.",
            ),
            (
                "Lignes sans nom ou plateforme obligatoire",
                skipped_mandatory_games_count,
                "Lignes non importables car une information obligatoire manque.",
            ),
            (
                "Jeux avec plateforme a valider",
                len(getattr(warnings, "platform_matches", []) or []),
                "Non bloquant: validation admin attendue.",
            ),
            (
                "Lignes wishlist ignorees",
                int(getattr(warnings, "invalid_wishlist", 0) or 0),
                "Valeur wishlist invalide ou inexploitable.",
            ),
        ]
        rows = []
        for label, count, description in counters:
            background_color = self._error_counter_background(label, int(count))
            rows.append(
                self._table_row_html(
                    [
                        self._table_cell_html(escape(label)),
                        self._table_cell_html(str(count), "font-weight:600;"),
                        self._table_cell_html(escape(description)),
                    ],
                    background_color,
                )
            )
        return self._table_html(["Compteur", "Valeur", "Explication"], rows)

    def _error_counter_background(self, label: str, count: int) -> str:
        if count <= 0:
            return ""
        if "plateforme a valider" in label:
            return "#fff7ed"
        if "erreur" in label or "refuses" in label or "obligatoire" in label:
            return "#fef2f2"
        return "#f8fafc"

    def _imported_studio_match_reports_html(self, imported_studio_match_reports: tuple) -> str:
        if not imported_studio_match_reports:
            return "<p>Aucun studio importe.</p>"
        rows = []
        for report in imported_studio_match_reports:
            created = bool(getattr(report, "created", False))
            rows.append(
                self._table_row_html(
                    [
                        self._table_cell_html(
                            self._html_value(getattr(report, "imported_studio_name", ""))
                        ),
                        self._created_status_cell_html(created),
                        self._table_cell_html(
                            self._html_value(getattr(report, "associated_studio_name", ""))
                        ),
                        self._table_cell_html(str(int(getattr(report, "score", 0) or 0))),
                    ],
                    "#ecfdf3" if created else "",
                )
            )
        return self._table_html(
            ["Nom du studio importé", "Créé", "Nom du Studio associé", "Score de matching"],
            rows,
        )

    def _imported_game_match_reports_html(self, imported_game_match_reports: tuple) -> str:
        if not imported_game_match_reports:
            return "<p>Aucun jeu importe.</p>"
        rows = []
        for report in imported_game_match_reports:
            created = bool(getattr(report, "created", False))
            decision = str(getattr(report, "decision", "") or "")
            rejected_decision = self._is_rejected_game_decision(decision)
            rows.append(
                self._table_row_html(
                    [
                        self._table_cell_html(
                            self._html_value(getattr(report, "imported_game_name", ""))
                        ),
                        self._created_status_cell_html(created),
                        self._table_cell_html(
                            self._html_value(getattr(report, "associated_game_name", ""))
                        ),
                        self._table_cell_html(str(int(getattr(report, "score", 0) or 0))),
                        self._game_decision_cell_html(decision, rejected_decision),
                        self._table_cell_html(self._html_value(getattr(report, "rule", ""))),
                        self._table_cell_html(self._html_value(getattr(report, "reason", ""))),
                    ],
                    self._imported_game_row_background(created, rejected_decision),
                )
            )
        return self._table_html(
            ["Nom", "Créé", "Jeu associé", "Score", "Decision", "Rule", "Raison"],
            rows,
        )

    def _imported_game_row_background(self, created: bool, rejected_decision: bool) -> str:
        if rejected_decision:
            return "#fef2f2"
        return "#ecfdf3" if created else ""

    def _is_rejected_game_decision(self, decision: str) -> bool:
        normalized_decision = (
            decision.lower()
            .replace("é", "e")
            .replace("è", "e")
            .replace("ê", "e")
            .replace("à", "a")
        )
        rejected_markers = (
            "refus",
            "reject",
            "rejected",
            "valeur a verifier",
            "a verifier",
            "to_check",
            "manual_check",
        )
        return any(marker in normalized_decision for marker in rejected_markers)

    def _game_decision_cell_html(self, decision: str, rejected_decision: bool) -> str:
        if not rejected_decision:
            return self._table_cell_html(self._html_value(decision))
        return self._table_cell_html(
            f'<strong style="color:#991b1b;">{self._html_value(decision)}</strong>',
            "background:#fee2e2;",
        )

    def _html_value(self, value) -> str:
        text = str(value or "")
        return escape(text) if text else "&nbsp;"

    def _manual_platform_mappings_html(self, manual_matches: list[dict]) -> str:
        if not manual_matches:
            return "<p>Aucune plateforme en attente de validation admin.</p>"
        rows = []
        for mapping in self._manual_platform_mappings(manual_matches):
            rows.append(
                self._table_row_html(
                    [
                        self._table_cell_html(escape(mapping["imported_platform"])),
                        self._table_cell_html(escape(mapping["matched_platform"])),
                        self._table_cell_html(str(mapping["games_count"]), "font-weight:600;"),
                        self._table_cell_html(escape(", ".join(mapping["game_names"]))),
                        self._table_cell_html(
                            '<strong style="color:#9a3412;">En attente de validation</strong>',
                        ),
                    ],
                    "#fff7ed",
                )
            )
        return self._table_html(
            ["Valeur dans le fichier", "Plateforme proposée", "Jeux", "Liste des jeux", "Statut"],
            rows,
        )

    def _manual_platform_mappings(self, manual_matches: list[dict]) -> list[dict]:
        mappings_by_key = {}
        for match in manual_matches:
            imported_platform = str(match.get("imported_platform") or "").strip()
            matched_platform = str(match.get("matched_platform") or "").strip()
            key = (imported_platform, matched_platform)
            mapping = mappings_by_key.get(key) or {
                "imported_platform": imported_platform or "-",
                "matched_platform": matched_platform or "-",
                "games_count": 0,
                "game_names": [],
            }
            mapping["games_count"] += 1
            mapping["game_names"].append(str(match.get("game_name") or "-"))
            mappings_by_key[key] = mapping
        return list(mappings_by_key.values())
