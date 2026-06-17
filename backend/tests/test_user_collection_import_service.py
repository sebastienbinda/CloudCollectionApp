#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du service d'import de collection utilisateur.

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.database.user_collection_import_repository import UserCollectionImportPersistenceResult
from services.collection.imports import (
    CollectionFileDescription,
    CollectionFileType,
    CollectionImportField,
    CollectionSheetLayout,
)
from services.ods import (
    OdsCollectionImportData,
    OdsCollectionImportGame,
    OdsCollectionImportPlatform,
    OdsCollectionImportReadError,
    OdsCollectionImportStudio,
)
from services.users.user_collection_import_configuration import (
    UserCollectionImportConfiguration,
)
from services.users.user_collection_import_service import (
    UserCollectionImportInvalidFileError,
    UserCollectionImportService,
    UserCollectionImportTooLargeError,
    UserCollectionImportUnexpectedError,
)


class FakeUserCollectionImportRepository:
    """Simule le repository d'import de collection utilisateur."""

    def __init__(self, has_collection=False, result=None, import_error=None):
        """Initialise le repository factice.

        Args:
            has_collection (bool): Indique si une collection existe deja.
            result (UserCollectionImportPersistenceResult | None): Resultat retourne.
            import_error (Exception | None): Erreur levee pendant la persistance.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.has_collection = has_collection
        self.result = result or UserCollectionImportPersistenceResult(
            1,
            1,
            1,
            1,
            user_email="importer@example.com",
        )
        self.import_error = import_error
        self.import_calls = []

    def user_has_collection(self, user_id):
        """Indique si l'utilisateur a deja une collection.

        Args:
            user_id (int): Identifiant utilisateur.

        Returns:
            bool: Valeur configuree pour le test.
        """

        return self.has_collection

    def import_collection(
        self,
        user_id,
        collection_file_path,
        import_data,
        collection_file_description,
    ):
        """Memorise l'appel de persistance ou leve une erreur.

        Args:
            user_id (int): Identifiant utilisateur.
            collection_file_path (str): Chemin final du fichier.
            import_data (OdsCollectionImportData): Donnees importees.
            collection_file_description (dict): Description sauvegardee.

        Returns:
            UserCollectionImportPersistenceResult: Resultat configure.

        Raises:
            Exception: Erreur configuree pour le test.
        """

        self.import_calls.append(
            (user_id, collection_file_path, import_data, collection_file_description)
        )
        if self.import_error:
            raise self.import_error
        return self.result


class FakeOdsCollectionImportReader:
    """Simule le lecteur ODS d'import."""

    def __init__(self, import_data=None, error=None, accepted_extensions=(".ods",)):
        """Initialise le lecteur factice.

        Args:
            import_data (OdsCollectionImportData | None): Donnees retournees.
            error (Exception | None): Erreur levee pendant la lecture.
            accepted_extensions (tuple[str, ...]): Extensions acceptees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.import_data = import_data or OdsCollectionImportData(
            platforms=[OdsCollectionImportPlatform("Switch")],
            studios=[OdsCollectionImportStudio("Nintendo")],
            games=[
                OdsCollectionImportGame(
                    name="Zelda",
                    platform_name="Switch",
                    studio_name="Nintendo",
                    release_date=None,
                )
            ],
        )
        self.error = error
        self._accepted_extensions = accepted_extensions
        self.read_paths = []
        self.analyze_paths = []

    @property
    def accepted_extensions(self):
        """Retourne l'extension acceptee par le lecteur factice.

        Args:
            Aucun.

        Returns:
            tuple[str, ...]: Extension ODS.
        """

        return self._accepted_extensions

    def read(self, ods_path, file_description):
        """Lit le fichier ODS factice.

        Args:
            ods_path (str): Chemin du fichier copie.
            file_description (object): Description valide.

        Returns:
            OdsCollectionImportData: Donnees configurees.

        Raises:
            Exception: Erreur configuree pour le test.
        """

        self.read_paths.append(ods_path)
        if self.error:
            raise self.error
        return self.import_data

    def analyze_sheets(self, file_path):
        """Retourne des onglets factices.

        Args:
            file_path (str): Chemin du fichier analyse.

        Returns:
            list[str]: Onglets factices.
        """

        self.analyze_paths.append(file_path)
        if self.error:
            raise self.error
        return ["Switch", "NES"]


class FakeCollectionFileReaderFactory:
    """Simule la factory de lecteurs de collection."""

    def __init__(self, reader):
        """Initialise la factory factice.

        Args:
            reader (FakeOdsCollectionImportReader): Lecteur retourne.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.reader = reader
        self.file_types = []

    def create(self, file_type):
        """Retourne le lecteur configure.

        Args:
            file_type (CollectionFileType): Type de fichier demande.

        Returns:
            FakeOdsCollectionImportReader: Lecteur configure.
        """

        self.file_types.append(file_type)
        return self.reader


class FakeImportReportNotifier:
    """Capture les contextes de rapport d'import."""

    def __init__(self, error=None):
        """Initialise le notifier factice.

        Args:
            error (Exception | None): Erreur optionnelle a lever.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.error = error
        self.contexts = []

    def notify_import_report(self, context):
        """Memorise le contexte de rapport ou leve l'erreur configuree.

        Args:
            context (object): Contexte complet du rapport d'import.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            Exception: Erreur configuree pour le test.
        """

        if self.error:
            raise self.error
        self.contexts.append(context)


class UserCollectionImportServiceTest(unittest.TestCase):
    """Valide le service metier d'import de collection utilisateur."""

    def test_import_collection_copies_file_and_returns_counts(self):
        """Verifie l'import nominal et les compteurs retournes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la copie et le resultat.
        """

        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = self._build_service(directory)

            result = service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                self._valid_description(),
            )

            target_file = Path(directory) / "workspace" / "7" / "7-collection.ods"
            self.assertTrue(target_file.exists())
            self.assertEqual(0o440, target_file.stat().st_mode & 0o777)
            self.assertEqual(str(target_file), reader.read_paths[0])
            self.assertEqual((1, 1, 1, 1), (
                result.linked_platforms,
                result.created_studios,
                result.created_games,
                result.associated_games,
            ))
            self.assertEqual(str(target_file), repository.import_calls[0][1])
            self.assertEqual(
                self._valid_description().to_dict(),
                repository.import_calls[0][3],
            )

    def test_import_collection_sends_report_context_after_success(self):
        """Verifie l'envoi du contexte complet apres import reussi.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contexte transmis.
        """

        with tempfile.TemporaryDirectory() as directory:
            notifier = FakeImportReportNotifier()
            service, repository, reader, source_file = self._build_service(
                directory,
                report_notifier=notifier,
            )

            result = service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                self._valid_description(),
            )

            self.assertEqual(1, len(notifier.contexts))
            context = notifier.contexts[0]
            self.assertEqual(7, context.user_id)
            self.assertEqual("importer@example.com", context.user_email)
            self.assertEqual("collection.ods", context.original_filename)
            self.assertEqual("libreoffice_ods", context.file_type)
            self.assertEqual("temporary_upload", context.source_mode)
            self.assertTrue(context.copied_to_workspace)
            self.assertEqual(result.associated_games, context.associated_games)
            self.assertEqual(result.wishlisted_games, context.wishlisted_games)
            self.assertEqual(
                self._valid_description().to_dict(),
                context.collection_file_description,
            )
            self.assertGreaterEqual(context.warnings.total_import_duration_seconds, 0)

    def test_import_collection_keeps_success_when_report_email_fails(self):
        """Verifie qu'un echec email ne transforme pas l'import en erreur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident que l'import reste reussi.
        """

        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = self._build_service(
                directory,
                report_notifier=FakeImportReportNotifier(RuntimeError("smtp")),
            )

            result = service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                self._valid_description(),
            )

            self.assertEqual(1, result.associated_games)
            self.assertEqual(1, len(repository.import_calls))
            self.assertEqual(1, len(reader.read_paths))

    def test_import_collection_accepts_existing_collection(self):
        """Verifie l'ajout depuis un nouveau fichier sur une collection existante.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'import additionnel.
        """

        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = self._build_service(
                directory,
                repository=FakeUserCollectionImportRepository(has_collection=True),
            )

            result = service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                self._valid_description(),
            )

            self.assertEqual(1, result.associated_games)
            self.assertEqual(1, len(repository.import_calls))
            self.assertEqual(1, len(reader.read_paths))

    def test_upload_import_file_accepts_existing_collection(self):
        """Verifie le depot temporaire pour ajouter a une collection existante.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la copie temporaire.
        """

        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = self._build_service(
                directory,
                repository=FakeUserCollectionImportRepository(has_collection=True),
            )

            service.upload_import_file(
                7,
                str(source_file),
                "collection.ods",
                self._valid_description().file_type,
            )

            temporary_file = Path(directory) / "workspace" / "7" / "current-import.ods"
            self.assertTrue(temporary_file.exists())
            self.assertEqual([], repository.import_calls)
            self.assertEqual([], reader.read_paths)

    def test_import_collection_rejects_invalid_file_type(self):
        """Verifie le refus d'un fichier non ODS.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de fichier invalide.
        """

        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = self._build_service(
                directory,
                source_filename="collection.txt",
            )

            with self.assertRaises(UserCollectionImportInvalidFileError):
                service.import_collection(
                    7,
                    str(source_file),
                    "collection.txt",
                    self._valid_description(),
                )

            self.assertEqual([], repository.import_calls)
            self.assertEqual([], reader.read_paths)

    def test_import_collection_rejects_too_large_file(self):
        """Verifie le refus d'un fichier trop volumineux.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de taille.
        """

        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = self._build_service(
                directory,
                max_upload_bytes=2,
                source_content=b"123",
            )

            with self.assertRaises(UserCollectionImportTooLargeError):
                service.import_collection(
                    7,
                    str(source_file),
                    "collection.ods",
                    self._valid_description(),
                )

            self.assertEqual([], repository.import_calls)
            self.assertEqual([], reader.read_paths)

    def test_import_collection_deletes_copied_file_when_ods_reader_fails(self):
        """Verifie la suppression du fichier copie si la lecture ODS echoue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le nettoyage fichier.
        """

        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = self._build_service(
                directory,
                reader=FakeOdsCollectionImportReader(error=OdsCollectionImportReadError("bad")),
            )

            with self.assertRaises(UserCollectionImportInvalidFileError):
                service.import_collection(
                    7,
                    str(source_file),
                    "collection.ods",
                    self._valid_description(),
                )

            self.assertFalse((Path(directory) / "workspace" / "7" / "7-collection.ods").exists())
            self.assertEqual([], repository.import_calls)
            self.assertEqual(1, len(reader.read_paths))

    def test_import_collection_deletes_copied_file_when_repository_rolls_back(self):
        """Verifie le nettoyage fichier si la persistance echoue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le nettoyage apres rollback SQL.
        """

        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = self._build_service(
                directory,
                repository=FakeUserCollectionImportRepository(import_error=RuntimeError("db")),
            )

            with self.assertRaises(UserCollectionImportUnexpectedError):
                service.import_collection(
                    7,
                    str(source_file),
                    "collection.ods",
                    self._valid_description(),
                )

            self.assertFalse((Path(directory) / "workspace" / "7" / "7-collection.ods").exists())
            self.assertEqual(1, len(repository.import_calls))
            self.assertEqual(1, len(reader.read_paths))

    def test_import_collection_returns_existing_game_association_counts(self):
        """Verifie les compteurs quand les jeux existent deja.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les compteurs de rattachement.
        """

        with tempfile.TemporaryDirectory() as directory:
            service, repository, reader, source_file = self._build_service(
                directory,
                repository=FakeUserCollectionImportRepository(
                    result=UserCollectionImportPersistenceResult(
                        linked_platforms=1,
                        created_studios=0,
                        created_games=0,
                        associated_games=2,
                    )
                ),
            )

            result = service.import_collection(
                7,
                str(source_file),
                "collection.ods",
                self._valid_description(),
            )

            self.assertEqual(0, result.created_games)
            self.assertEqual(1, result.linked_platforms)
            self.assertEqual(2, result.associated_games)
            self.assertEqual(1, len(repository.import_calls))
            self.assertEqual(1, len(reader.read_paths))

    def _build_service(
        self,
        directory,
        repository=None,
        reader=None,
        max_upload_bytes=104857600,
        source_filename="collection.ods",
        source_content=b"ods-content",
        report_notifier=None,
    ):
        source_file = Path(directory) / source_filename
        source_file.write_bytes(source_content)
        repository = repository or FakeUserCollectionImportRepository()
        reader = reader or FakeOdsCollectionImportReader()
        configuration = UserCollectionImportConfiguration(
            workspace_path=str(Path(directory) / "workspace"),
            max_upload_bytes=max_upload_bytes,
        )
        return (
            UserCollectionImportService(
                configuration,
                repository,
                FakeCollectionFileReaderFactory(reader),
                report_notifier=report_notifier,
            ),
            repository,
            reader,
            source_file,
        )

    def _valid_description(self):
        return CollectionFileDescription(
            file_type=CollectionFileType.LIBREOFFICE_ODS,
            single_sheet_conf=CollectionSheetLayout(
                data_range="A1:D10",
                header_row=1,
                column_information={
                    CollectionImportField.NAME: "A",
                    CollectionImportField.PLATFORM: "B",
                    CollectionImportField.STUDIO: "C",
                    CollectionImportField.RELEASE_DATE: "D",
                },
            ),
        )
