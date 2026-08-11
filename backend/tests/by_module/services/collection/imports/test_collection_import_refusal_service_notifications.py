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
# Description : tests des notifications de refus envoyees par les services d'import.

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.collection.imports import (  # noqa: E402
    CollectionCsvConfiguration,
    CollectionFileDescription,
    CollectionFileType,
    CollectionImportData,
    CollectionImportField,
    CollectionImportGame,
    CollectionImportPlatform,
    CollectionImportWarnings,
    WishlistImportConfiguration,
)
from services.database.admin_library_import_repository import (  # noqa: E402
    AdminLibraryImportPersistenceResult,
)
from services.database.user_collection_import_persistence_result import (  # noqa: E402
    UserCollectionImportPersistenceResult,
)
from services.library.admin_library_import_service import AdminLibraryImportService  # noqa: E402
from services.users.user_collection_import_configuration import (  # noqa: E402
    UserCollectionImportConfiguration,
)
from services.users.user_collection_import_service import UserCollectionImportService  # noqa: E402


class FakeImportRefusalNotifier:
    """Capture les notifications de refus d'import."""

    def __init__(self):
        """Initialise le notifier factice."""

        self.contexts = []

    def notify_import_refusal(self, context):
        """Memorise le contexte de refus."""

        self.contexts.append(context)


class FakeCollectionReader:
    """Retourne des donnees d'import factices en erreur."""

    accepted_extensions = (".csv",)

    def __init__(self, import_data):
        """Initialise le lecteur avec ses donnees."""

        self.import_data = import_data

    def analyze_sheets(self, file_path):
        """Retourne des colonnes CSV factices."""

        return ["Jeu", "Plateforme"]

    def read(self, file_path, description):
        """Retourne les donnees configurees."""

        return self.import_data


class FakeReaderFactory:
    """Retourne toujours le lecteur configure."""

    def __init__(self, reader):
        """Initialise la factory de lecteur."""

        self.reader = reader

    def create(self, file_type):
        """Retourne le lecteur configure."""

        return self.reader


class FakeUserRepository:
    """Capture les appels de persistance utilisateur."""

    def __init__(self):
        """Initialise le repository factice."""

        self.import_calls = []

    def import_collection(
        self,
        user_id,
        collection_file_path,
        import_data,
        collection_file_description,
        initial_game_validation_status,
    ):
        """Capture l'appel de persistance."""

        self.import_calls.append(import_data)
        return UserCollectionImportPersistenceResult(1, 1, 1, 1)


class FakeAdminRepository:
    """Capture les appels de persistance admin."""

    def __init__(self):
        """Initialise le repository factice."""

        self.import_calls = []

    def import_library(self, import_data):
        """Capture l'appel de persistance."""

        self.import_calls.append(import_data)
        return AdminLibraryImportPersistenceResult(1, 1, 1)


class FakeAdminConfigurationLoader:
    """Retourne une description CSV minimale."""

    def load_for_columns(self, columns):
        """Construit une description CSV valide."""

        return CollectionFileDescription(
            file_type=CollectionFileType.CSV,
            wishlist=WishlistImportConfiguration.none(),
            csv_conf=CollectionCsvConfiguration(
                {
                    CollectionImportField.NAME: "Jeu",
                    CollectionImportField.PLATFORM: "Plateforme",
                }
            ),
        )


class CollectionImportRefusalServiceNotificationsTest(unittest.TestCase):
    """Valide les notifications de refus emises par les services."""

    def test_user_import_refusal_notifies_admin(self):
        """Verifie le contexte du mail de refus utilisateur."""

        import_data = self._refused_import_data()
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "collection.csv"
            source_file.write_text("Jeu,Plateforme\n", encoding="utf-8")
            notifier = FakeImportRefusalNotifier()
            repository = FakeUserRepository()
            service = UserCollectionImportService(
                UserCollectionImportConfiguration(
                    str(Path(directory) / "workspace"),
                    UserCollectionImportConfiguration.DEFAULT_MAX_UPLOAD_BYTES,
                ),
                repository,
                FakeReaderFactory(FakeCollectionReader(import_data)),
                refusal_notifier=notifier,
            )

            service.import_collection(
                7,
                str(source_file),
                "collection.csv",
                CollectionFileDescription(
                    file_type=CollectionFileType.CSV,
                    wishlist=WishlistImportConfiguration.none(),
                    csv_conf=CollectionCsvConfiguration(
                        {
                            CollectionImportField.NAME: "A",
                            CollectionImportField.PLATFORM: "B",
                        }
                    ),
                ),
                requester_email="user@example.com",
            )

        self.assertEqual([], repository.import_calls)
        self.assertEqual(1, len(notifier.contexts))
        context = notifier.contexts[0]
        self.assertEqual("collection_utilisateur", context.import_kind)
        self.assertEqual(7, context.requester_user_id)
        self.assertEqual("user@example.com", context.requester_email)
        self.assertEqual("collection.csv", context.original_filename)
        self.assertEqual("too_many_invalid_games", context.refusal["reason"])
        self.assertEqual(import_data.warnings, context.import_data.warnings)

    def test_admin_import_refusal_notifies_admin(self):
        """Verifie le contexte du mail de refus admin CSV."""

        import_data = self._refused_import_data()
        repository = FakeAdminRepository()
        notifier = FakeImportRefusalNotifier()
        service = AdminLibraryImportService(
            repository,
            FakeCollectionReader(import_data),
            FakeAdminConfigurationLoader(),
            refusal_notifier=notifier,
        )

        service.import_csv_file(
            "/tmp/admin.csv",
            "admin.csv",
            requester_email="admin@example.com",
        )

        self.assertEqual([], repository.import_calls)
        self.assertEqual(1, len(notifier.contexts))
        context = notifier.contexts[0]
        self.assertEqual("bibliotheque_admin_csv", context.import_kind)
        self.assertIsNone(context.requester_user_id)
        self.assertEqual("admin@example.com", context.requester_email)
        self.assertEqual("admin.csv", context.original_filename)
        self.assertEqual("too_many_invalid_games", context.refusal["reason"])
        self.assertEqual(import_data.warnings, context.import_data.warnings)

    def _refused_import_data(self):
        return CollectionImportData(
            platforms=[CollectionImportPlatform("Switch")],
            studios=[],
            games=[
                CollectionImportGame("Zelda", "Switch", None, None),
                CollectionImportGame("Mario", "Switch", None, None),
                CollectionImportGame("Metroid", "Switch", None, None),
            ],
            warnings=CollectionImportWarnings(
                invalid_games=[
                    {"name": "Zelda", "invalid_fields": [{"field": "release_date"}]},
                    {"name": "Mario", "invalid_fields": [{"field": "release_date"}]},
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
