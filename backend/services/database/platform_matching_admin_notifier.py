#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : notification administrateur des matchings plateformes.

import os

from services.email import EmailConfiguration, EmailSenderFactory


class PlatformMatchingAdminNotifier:
    """Notifie l'administrateur du rapport de matching des plateformes."""

    def __init__(self, email_sender=None, admin_notification_email: str | None = None):
        """Initialise la notification de matching plateformes.

        Args:
            email_sender (object | None): Expediteur email injectable.
            admin_notification_email (str): Adresse administrateur destinataire.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.email_sender = email_sender
        if admin_notification_email is None:
            admin_notification_email = os.getenv("ADMIN_NOTIFICATION_EMAIL", "")
        self.admin_notification_email = str(admin_notification_email or "").strip()

    @classmethod
    def from_environment(cls) -> "PlatformMatchingAdminNotifier":
        """Construit le notifier depuis l'environnement.

        Args:
            Aucun.

        Returns:
            PlatformMatchingAdminNotifier: Notifier configure.

        Raises:
            ValueError: Si la configuration email est invalide.
        """

        return cls(admin_notification_email=os.getenv("ADMIN_NOTIFICATION_EMAIL", ""))

    def notify_import_report(self, warnings: object) -> None:
        """Envoie le rapport admin des mappings et warnings de plateformes.

        Args:
            warnings (object): Warnings d'import contenant les mappings plateformes.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        if not self.admin_notification_email:
            return
        platform_mappings = list(getattr(warnings, "platform_mappings", []) or [])
        manual_matches = list(getattr(warnings, "platform_matches", []) or [])
        skipped_games = list(getattr(warnings, "skipped_games", []) or [])
        invalid_games = list(getattr(warnings, "invalid_games", []) or [])
        invalid_wishlist = int(getattr(warnings, "invalid_wishlist", 0) or 0)
        total_import_duration_seconds = float(
            getattr(warnings, "total_import_duration_seconds", 0.0) or 0.0
        )
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
            return

        lines = [
            "Rapport de mapping des plateformes importees.",
            "Duree totale de l'import: {duration:.3f} seconde(s).".format(
                duration=total_import_duration_seconds,
            ),
            "",
        ]
        self._append_platform_mappings(lines, platform_mappings)
        self._append_manual_matches(lines, manual_matches)
        self._append_skipped_games(lines, skipped_games)
        self._append_invalid_games(lines, invalid_games)
        self._append_invalid_wishlist(lines, invalid_wishlist, invalid_wishlist_values)
        email_sender = self.email_sender or EmailSenderFactory.create(
            EmailConfiguration.from_environment()
        )
        email_sender.send_email(
            recipient_email=self.admin_notification_email,
            subject="Rapport de mapping des plateformes importees",
            body="\n".join(lines),
        )

    def notify_manual_matches(self, manual_matches: list[dict]) -> None:
        """Envoie un email de compatibilite pour les matchings faibles.

        Args:
            manual_matches (list[dict]): Warnings de plateformes a verifier.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        warnings = type(
            "PlatformMatchingWarnings",
            (),
            {
                "platform_mappings": [],
                "platform_matches": manual_matches,
                "skipped_games": [],
                "invalid_games": [],
                "invalid_wishlist": 0,
                "invalid_wishlist_values_found": [],
            },
        )()
        self.notify_import_report(warnings)

    def _append_platform_mappings(
        self,
        lines: list[str],
        platform_mappings: list[dict],
    ) -> None:
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
                "Alias: {alias_text}".format(
                    alias_text=alias_text,
                    **mapping,
                )
            )
        lines.append("")

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
        lines.append("")

    def _append_skipped_games(self, lines: list[str], skipped_games: list[dict]) -> None:
        if not skipped_games:
            return
        lines.append("Jeux ignores:")
        for skipped_game in skipped_games:
            lines.append(
                "- Jeu: {game_name} | Plateforme importee: {imported_platform} | "
                "Score: {score} | Raison: {reason}".format(**skipped_game)
            )
        lines.append("")

    def _append_invalid_games(self, lines: list[str], invalid_games: list[dict]) -> None:
        if not invalid_games:
            return
        lines.append("Jeux importes avec informations invalides ignorees:")
        for invalid_game in invalid_games:
            lines.append("- Jeu: {name}".format(**invalid_game))
        lines.append("")

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
