#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-26
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du service d'import CSV admin Bibliotheque.

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(next(parent for parent in Path(__file__).resolve().parents if (parent / "app.py").exists())))

from services.collection.imports import (  # noqa: E402
    CollectionCsvConfiguration,
    CollectionFileDescription,
    CollectionFileDescriptionValidationError,
    CollectionFileType,
    CollectionImportData,
    CollectionImportField,
    CollectionImportGame,
    CollectionImportPlatform,
    CollectionImportStudio,
    WishlistImportConfiguration,
)
from services.database.admin_library_import_repository import (  # noqa: E402
    AdminLibraryImportPersistenceResult,
)
from services.library.admin_library_import_configuration import (  # noqa: E402
    AdminLibraryImportConfigurationError,
    AdminLibraryImportConfigurationLoader,
)
from services.library.admin_library_import_service import (  # noqa: E402
    AdminLibraryImportInvalidFileError,
    AdminLibraryImportService,
)


class FakeAdminLibraryImportReader:
    """Lecteur CSV factice pour les tests du service admin."""

    accepted_extensions = (".csv",)

    def __init__(self):
        """Initialise le lecteur factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.analyze_paths = []
        self.read_calls = []

    def analyze_sheets(self, file_path):
        """Retourne des colonnes CSV factices.

        Args:
            file_path (str): Chemin recu par le service.

        Returns:
            list[str]: Colonnes factices.
        """

        self.analyze_paths.append(file_path)
        return ["Jeu", "Plateforme", "Studio", "Sortie"]

    def read(self, file_path, description):
        """Retourne des donnees d'import factices.

        Args:
            file_path (str): Chemin CSV lu.
            description (CollectionFileDescription): Description construite.

        Returns:
            CollectionImportData: Donnees CSV factices.
        """

        self.read_calls.append((file_path, description))
        return CollectionImportData(
            platforms=[CollectionImportPlatform("Switch")],
            studios=[CollectionImportStudio("Nintendo")],
            games=[CollectionImportGame("Zelda", "Switch", "Nintendo", None)],
        )


class FakeAdminLibraryImportConfigurationLoader:
    """Chargeur de configuration factice pour les tests du service admin."""

    def __init__(self, error=None):
        """Initialise le chargeur factice.

        Args:
            error (Exception | None): Erreur a lever pendant le chargement.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.error = error
        self.columns = []

    def load_for_columns(self, columns):
        """Construit une description minimale ou leve l'erreur configuree.

        Args:
            columns (list[str]): Colonnes recues du reader.

        Returns:
            CollectionFileDescription: Description minimale factice.

        Raises:
            Exception: Si `error` est configure.
        """

        self.columns = columns
        if self.error:
            raise self.error
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


class FakeAdminLibraryImportRepository:
    """Repository factice pour capturer les imports admin."""

    def __init__(self):
        """Initialise le repository factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.import_calls = []

    def import_library(self, import_data):
        """Capture les donnees importees et retourne des compteurs.

        Args:
            import_data (CollectionImportData): Donnees recues du service.

        Returns:
            AdminLibraryImportPersistenceResult: Compteurs factices.
        """

        self.import_calls.append(import_data)
        return AdminLibraryImportPersistenceResult(
            linked_platforms=1,
            created_studios=1,
            created_games=1,
        )


class AdminLibraryImportServiceTest(unittest.TestCase):
    """Valide le service d'import CSV admin Bibliotheque."""

    def test_import_csv_file_uses_fixed_configuration_and_persists_library_only(self):
        """Verifie l'orchestration nominale de l'import admin.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les compteurs et appels.
        """

        repository = FakeAdminLibraryImportRepository()
        reader = FakeAdminLibraryImportReader()
        loader = FakeAdminLibraryImportConfigurationLoader()
        service = AdminLibraryImportService(repository, reader, loader)

        result = service.import_csv_file("/tmp/import.csv", "admin.csv")

        self.assertEqual(["/tmp/import.csv"], reader.analyze_paths)
        self.assertEqual(["Jeu", "Plateforme", "Studio", "Sortie"], loader.columns)
        self.assertEqual(1, len(reader.read_calls))
        self.assertEqual(1, len(repository.import_calls))
        self.assertEqual(1, result.created_games)
        self.assertEqual(1, result.created_studios)
        self.assertEqual(1, result.linked_platforms)
        self.assertEqual(0, result.warnings["invalid_wishlist"])

    def test_import_csv_file_rejects_non_csv_extension(self):
        """Verifie que le service refuse les extensions non CSV.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur fonctionnelle.
        """

        repository = FakeAdminLibraryImportRepository()
        reader = FakeAdminLibraryImportReader()
        service = AdminLibraryImportService(
            repository,
            reader,
            FakeAdminLibraryImportConfigurationLoader(),
        )

        with self.assertRaises(AdminLibraryImportInvalidFileError) as context:
            service.import_csv_file("/tmp/import.ods", "import.ods")

        self.assertEqual(["Seuls les fichiers CSV sont acceptes."], context.exception.details)
        self.assertEqual([], reader.analyze_paths)
        self.assertEqual([], repository.import_calls)

    def test_import_csv_file_exposes_configuration_errors(self):
        """Verifie la propagation des erreurs de configuration admin.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les details d'erreur.
        """

        repository = FakeAdminLibraryImportRepository()
        reader = FakeAdminLibraryImportReader()
        loader = FakeAdminLibraryImportConfigurationLoader(
            AdminLibraryImportConfigurationError(["mapping.name doit etre valide."])
        )
        service = AdminLibraryImportService(repository, reader, loader)

        with self.assertRaises(AdminLibraryImportInvalidFileError) as context:
            service.import_csv_file("/tmp/import.csv", "import.csv")

        self.assertEqual(["mapping.name doit etre valide."], context.exception.details)
        self.assertEqual([], repository.import_calls)


class AdminLibraryImportConfigurationLoaderTest(unittest.TestCase):
    """Valide la conversion de la configuration JSON fixe."""

    def test_load_for_columns_converts_indexes_to_csv_headers(self):
        """Verifie la conversion des index configures en noms de colonnes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le mapping transmis au validateur.
        """

        with tempfile.TemporaryDirectory() as directory:
            configuration_path = Path(directory) / "admin_import_conf.json"
            configuration_path.write_text(
                '{"file_type":"csv","mapping":{"name":1,"platform":2,"studio":3,"release_date":4}}',
                encoding="utf-8",
            )
            validator = SimpleNamespace(
                validate=lambda payload, columns: SimpleNamespace(payload=payload, columns=columns)
            )
            loader = AdminLibraryImportConfigurationLoader(configuration_path, validator)

            description = loader.load_for_columns(["Jeu", "Plateforme", "Studio", "Sortie"])

            self.assertEqual({"Jeu", "Plateforme", "Studio", "Sortie"}, description.columns)
            self.assertEqual(
                {
                    "file_type": "csv",
                    "wishlist": {"mode": "none"},
                    "mapping": {
                        "name": "Jeu",
                        "platform": "Plateforme",
                        "studio": "Studio",
                        "release_date": "Sortie",
                    },
                },
                description.payload,
            )

    def test_load_for_columns_rejects_missing_csv_column(self):
        """Verifie le refus quand la configuration pointe une colonne absente.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les details.
        """

        with tempfile.TemporaryDirectory() as directory:
            configuration_path = Path(directory) / "admin_import_conf.json"
            configuration_path.write_text(
                '{"file_type":"csv","mapping":{"name":1,"platform":2,"studio":3,"release_date":4}}',
                encoding="utf-8",
            )
            loader = AdminLibraryImportConfigurationLoader(configuration_path)

            with self.assertRaises(AdminLibraryImportConfigurationError) as context:
                loader.load_for_columns(["Jeu", "Plateforme"])

        self.assertEqual(
            [
                "mapping.studio cible une colonne CSV absente.",
                "mapping.release_date cible une colonne CSV absente.",
            ],
            context.exception.details,
        )

    def test_load_for_columns_rejects_invalid_field_index(self):
        """Verifie le refus d'un index de colonne invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les details.
        """

        with tempfile.TemporaryDirectory() as directory:
            configuration_path = Path(directory) / "admin_import_conf.json"
            configuration_path.write_text(
                '{"file_type":"csv","mapping":{"name":0,"platform":2}}',
                encoding="utf-8",
            )
            loader = AdminLibraryImportConfigurationLoader(configuration_path)

            with self.assertRaises(AdminLibraryImportConfigurationError) as context:
                loader.load_for_columns(["Jeu", "Plateforme"])

        self.assertEqual(["mapping.name doit etre un index entier positif."], context.exception.details)

    def test_load_for_columns_exposes_validator_errors(self):
        """Verifie que les erreurs du validateur commun restent visibles.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la propagation.
        """

        with tempfile.TemporaryDirectory() as directory:
            configuration_path = Path(directory) / "admin_import_conf.json"
            configuration_path.write_text(
                '{"file_type":"csv","mapping":{"name":1,"platform":2}}',
                encoding="utf-8",
            )
            validator = SimpleNamespace(
                validate=lambda payload, columns: (_ for _ in ()).throw(
                    CollectionFileDescriptionValidationError(["mapping invalide."])
                )
            )
            loader = AdminLibraryImportConfigurationLoader(configuration_path, validator)

            with self.assertRaises(CollectionFileDescriptionValidationError) as context:
                loader.load_for_columns(["Jeu", "Plateforme"])

        self.assertEqual(["mapping invalide."], context.exception.details)


if __name__ == "__main__":
    unittest.main()
