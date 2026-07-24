#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-11
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du service de reset Bibliotheque.

from datetime import datetime
from pathlib import Path
import tempfile
import unittest

from services.database import LibraryResetImportableUser, LibraryResetPlatformImageSnapshot
from services.library import LibraryResetJob
from services.library.library_reset_service import LibraryResetService


class FakeResetRepository:
    """Repository de reset factice."""

    def __init__(self, users=None, clean_error=None, platform_image_snapshots=None):
        """Initialise le repository.

        Args:
            users (list | None): Utilisateurs retournes.
            clean_error (Exception | None): Erreur de clean.
            platform_image_snapshots (list | None): Images sauvegardees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.users = users or []
        self.clean_error = clean_error
        self.platform_image_snapshots = platform_image_snapshots or []
        self.cleaned = False
        self.list_called = False
        self.restored_snapshots = None
        self.events = []

    def clean_library_tables(self):
        """Nettoie ou leve une erreur configuree."""

        self.cleaned = True
        self.events.append("clean")
        if self.clean_error:
            raise self.clean_error
        return self.platform_image_snapshots

    def list_importable_users(self):
        """Retourne les utilisateurs configures."""

        self.list_called = True
        self.events.append("list")
        return self.users

    def restore_platform_images(self, platform_image_snapshots):
        """Memorise les images restaurees."""

        self.restored_snapshots = platform_image_snapshots
        self.events.append("restore")
        return len(platform_image_snapshots)


class FakeImportResult:
    """Resultat d'import minimal."""

    associated_games = 3


class FakeImportService:
    """Service d'import factice."""

    def __init__(self, errors_by_user=None, events=None):
        """Initialise le service.

        Args:
            errors_by_user (dict | None): Erreurs par utilisateur.
            events (list | None): Journal d'evenements partage.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.errors_by_user = errors_by_user or {}
        self.events = events
        self.calls = []

    def import_stored_collection(self, user_id, stored_file_path, file_description):
        """Memorise l'import ou leve une erreur configuree."""

        if self.events is not None:
            self.events.append(f"import:{user_id}")
        self.calls.append((user_id, stored_file_path, file_description))
        if user_id in self.errors_by_user:
            raise self.errors_by_user[user_id]
        return FakeImportResult()


class FakePlatformCatalogUpdater:
    """Service factice de reconstruction du catalogue plateformes."""

    def __init__(self, events=None, error=None):
        """Initialise le service factice.

        Args:
            events (list | None): Journal d'evenements partage.
            error (Exception | None): Erreur a lever.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.events = events
        self.error = error
        self.called = False

    def update_from_resources(self):
        """Memorise la reconstruction ou leve une erreur configuree."""

        self.called = True
        if self.events is not None:
            self.events.append("seed")
        if self.error:
            raise self.error
        return object()


class FakeEmailSender:
    """Expediteur email factice."""

    def __init__(self):
        """Initialise l'expediteur."""

        self.sent_emails = []

    def send_email(self, recipient_email, subject, body):
        """Memorise l'email."""

        self.sent_emails.append(
            {"recipient_email": recipient_email, "subject": subject, "body": body}
        )


class LibraryResetServiceTest(unittest.TestCase):
    """Valide l'orchestration du reset Bibliotheque."""

    def test_run_reset_stops_when_clean_fails(self):
        """Verifie l'arret du reset si le clean base echoue."""

        email_sender = FakeEmailSender()
        import_service = FakeImportService()
        repository = FakeResetRepository(clean_error=RuntimeError("db"))
        service = LibraryResetService(
            repository,
            lambda: import_service,
            email_sender=email_sender,
            admin_notification_email="admin@example.com",
        )

        context = service.run_reset(LibraryResetJob(4, datetime(2026, 6, 11, 12)))

        self.assertTrue(repository.cleaned)
        self.assertFalse(repository.list_called)
        self.assertEqual("Echec du nettoyage de la base: db", context.global_error)
        self.assertEqual([], import_service.calls)
        self.assertIn("Erreur globale", email_sender.sent_emails[0]["body"])

    def test_run_reset_imports_users_and_reports_partial_errors(self):
        """Verifie les succes, erreurs utilisateur et email final."""

        with tempfile.TemporaryDirectory() as temp_dir:
            valid_file = Path(temp_dir) / "7-collection.ods"
            valid_file.write_text("content", encoding="utf-8")
            invalid_config_file = Path(temp_dir) / "8-collection.ods"
            invalid_config_file.write_text("content", encoding="utf-8")
            users = [
                self._user(7, str(valid_file), self._valid_description()),
                self._user(8, str(invalid_config_file), {}),
                self._user(9, str(Path(temp_dir) / "missing.ods"), self._valid_description()),
            ]
            import_service = FakeImportService()
            email_sender = FakeEmailSender()
            service = LibraryResetService(
                FakeResetRepository(users),
                lambda: import_service,
                email_sender=email_sender,
                admin_notification_email="admin@example.com",
            )

            context = service.run_reset(LibraryResetJob(5, datetime(2026, 6, 11, 12)))

        self.assertEqual([7], [result.user_id for result in context.successful_users])
        self.assertEqual([8, 9], [result.user_id for result in context.failed_users])
        self.assertEqual(1, len(import_service.calls))
        self.assertEqual([], service.reset_repository.restored_snapshots)
        self.assertEqual("admin@example.com", email_sender.sent_emails[0]["recipient_email"])
        self.assertIn("Reset Bibliotheque termine avec erreurs", email_sender.sent_emails[0]["subject"])
        self.assertIn("utilisateur 7", email_sender.sent_emails[0]["body"])
        self.assertIn("utilisateur 8", email_sender.sent_emails[0]["body"])

    def test_run_reset_continues_after_user_import_failure(self):
        """Verifie qu'un echec d'import utilisateur ne bloque pas le suivant."""

        with tempfile.TemporaryDirectory() as temp_dir:
            first_file = Path(temp_dir) / "7-collection.ods"
            first_file.write_text("content", encoding="utf-8")
            second_file = Path(temp_dir) / "8-collection.ods"
            second_file.write_text("content", encoding="utf-8")
            users = [
                self._user(7, str(first_file), self._valid_description()),
                self._user(8, str(second_file), self._valid_description()),
            ]
            import_service = FakeImportService(errors_by_user={7: RuntimeError("import")})
            service = LibraryResetService(FakeResetRepository(users), lambda: import_service)

            context = service.run_reset(LibraryResetJob(6, datetime(2026, 6, 11, 12)))

        self.assertEqual([8], [result.user_id for result in context.successful_users])
        self.assertEqual([7], [result.user_id for result in context.failed_users])
        self.assertEqual([7, 8], [call[0] for call in import_service.calls])

    def test_run_reset_restores_platform_images_after_user_imports(self):
        """Verifie le seed catalogue puis la restauration apres les imports.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'orchestration.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            events = []
            valid_file = Path(temp_dir) / "7-collection.ods"
            valid_file.write_text("content", encoding="utf-8")
            snapshot = LibraryResetPlatformImageSnapshot(
                "Switch",
                "/images/switch.png",
                42,
                "MAIN",
                "ACCEPTED",
                7,
                datetime(2026, 6, 1, 12),
            )
            repository = FakeResetRepository(
                [self._user(7, str(valid_file), self._valid_description())],
                platform_image_snapshots=[snapshot],
            )
            repository.events = events
            import_service = FakeImportService(events=events)
            service = LibraryResetService(
                repository,
                lambda: import_service,
                platform_catalog_updater=FakePlatformCatalogUpdater(events),
            )

            context = service.run_reset(LibraryResetJob(7, datetime(2026, 6, 11, 12)))

        self.assertEqual([7], [result.user_id for result in context.successful_users])
        self.assertEqual([snapshot], repository.restored_snapshots)
        self.assertEqual(["clean", "seed", "list", "import:7", "restore"], events)

    def test_run_reset_stops_when_platform_catalog_seed_fails(self):
        """Verifie que les imports ne demarrent pas sans catalogue plateformes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'arret du reset.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            valid_file = Path(temp_dir) / "7-collection.ods"
            valid_file.write_text("content", encoding="utf-8")
            import_service = FakeImportService()
            repository = FakeResetRepository(
                [self._user(7, str(valid_file), self._valid_description())],
            )
            service = LibraryResetService(
                repository,
                lambda: import_service,
                platform_catalog_updater=FakePlatformCatalogUpdater(error=RuntimeError("csv")),
            )

            context = service.run_reset(LibraryResetJob(8, datetime(2026, 6, 11, 12)))

        self.assertEqual(
            "Echec de reconstruction du catalogue plateformes: csv",
            context.global_error,
        )
        self.assertFalse(repository.list_called)
        self.assertEqual([], import_service.calls)
        self.assertIsNone(repository.restored_snapshots)

    def _user(self, user_id, file_path, description):
        """Construit un utilisateur importable factice."""

        return LibraryResetImportableUser(
            id=user_id,
            email=f"user{user_id}@example.com",
            collection_file_path=file_path,
            collection_file_description=description,
            profile="USER",
            status="ACTIVE",
            creation_date=datetime(2026, 5, user_id, 12),
        )

    def _valid_description(self):
        """Retourne une configuration d'import valide minimale."""

        return {
            "file_type": "libreoffice_ods",
            "wishlist": {"mode": "none"},
            "single_sheet_conf": {
                "sheet_name": "Collection",
                "data_range": "A1:D5",
                "header_row": 1,
                "column_information": {
                    "name": "A",
                    "platform": "B",
                    "studio": "C",
                    "release_date": "D",
                },
            },
        }


if __name__ == "__main__":
    unittest.main()
