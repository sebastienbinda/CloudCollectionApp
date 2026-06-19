#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-19
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du service metier des images de plateformes.

from io import BytesIO
import tempfile
import unittest
from pathlib import Path

from werkzeug.datastructures import FileStorage

from services.database import DatabaseConfiguration
from services.library import PlatformImageConfiguration
from services.library.platform_image_service import (
    PlatformImageNotFoundError,
    PlatformImagePlatformNotFoundError,
    PlatformImageService,
    PlatformImageUserNotFoundError,
    PlatformImageValidationError,
)


class FakeConnectionContext:
    """Contexte de connexion factice."""

    def __init__(self, connection):
        """Initialise le contexte.

        Args:
            connection (object): Connexion retournee.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection

    def __enter__(self):
        """Entre dans le contexte.

        Args:
            Aucun.

        Returns:
            object: Connexion factice.
        """

        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        """Sort du contexte.

        Args:
            exc_type (type | None): Type d'exception.
            exc_value (BaseException | None): Exception.
            traceback (object | None): Traceback.

        Returns:
            bool: `False` pour propager les exceptions.
        """

        return False


class FakeEngine:
    """Moteur SQL factice."""

    def __init__(self):
        """Initialise le moteur factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = object()

    def begin(self):
        """Ouvre une transaction factice.

        Args:
            Aucun.

        Returns:
            FakeConnectionContext: Contexte transactionnel.
        """

        return FakeConnectionContext(self.connection)

    def connect(self):
        """Ouvre une connexion factice.

        Args:
            Aucun.

        Returns:
            FakeConnectionContext: Contexte de connexion.
        """

        return FakeConnectionContext(self.connection)


class FakePlatformImageRepository:
    """Repository image factice."""

    def __init__(self):
        """Initialise le repository factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.platform_name = "Nintendo Switch"
        self.accepted_image = None
        self.created_images = []

    def find_platform_name(self, connection, platform_id):
        """Retourne une plateforme factice.

        Args:
            connection (object): Connexion ignoree.
            platform_id (int): Identifiant de plateforme.

        Returns:
            str | None: Nom de plateforme ou absence.
        """

        return self.platform_name if platform_id == 1 else None

    def create_waiting_image(self, connection, platform_id, path, user_id, creation_date):
        """Insere une image factice.

        Args:
            connection (object): Connexion ignoree.
            platform_id (int): Identifiant de plateforme.
            path (str): Chemin absolu stocke.
            user_id (int): Identifiant utilisateur.
            creation_date (datetime): Date de creation.

        Returns:
            dict[str, object]: Image inseree.
        """

        image = {
            "id": 4,
            "platform": platform_id,
            "path": path,
            "type": "OTHER",
            "status": "WAITING_VALIDATION",
            "user_id": user_id,
            "creation_date": creation_date,
        }
        self.created_images.append(image)
        return image

    def find_accepted_image(self, connection, platform_id, image_id):
        """Retourne l'image acceptee configuree.

        Args:
            connection (object): Connexion ignoree.
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.

        Returns:
            dict[str, object] | None: Image acceptee ou absence.
        """

        if self.accepted_image and platform_id == 1 and image_id == 4:
            return self.accepted_image
        return None


class FakeUserRepository:
    """Repository utilisateur factice."""

    def __init__(self, user_id=7):
        """Initialise le repository utilisateur factice.

        Args:
            user_id (int | None): Identifiant a retourner.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.user_id = user_id
        self.last_email = None

    def find_user_id_by_email(self, email):
        """Retourne l'identifiant utilisateur configure.

        Args:
            email (str): Email recherche.

        Returns:
            int | None: Identifiant utilisateur ou absence.
        """

        self.last_email = email
        return self.user_id


class FakeNotifier:
    """Notifier factice des images."""

    def __init__(self):
        """Initialise le notifier factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.calls = []

    def notify_image_created(self, platform_name, image_id, user_email):
        """Memorise la notification.

        Args:
            platform_name (str): Nom de plateforme.
            image_id (int): Identifiant d'image.
            user_email (str): Email utilisateur.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.calls.append((platform_name, image_id, user_email))


class PlatformImageServiceTest(unittest.TestCase):
    """Valide le service des images de plateformes."""

    def setUp(self):
        """Prepare les dependances de test.

        Args:
            Aucun.

        Returns:
            None: Les fakes sont prepares.
        """

        self.temp_directory = tempfile.TemporaryDirectory()
        self.image_repository = FakePlatformImageRepository()
        self.user_repository = FakeUserRepository()
        self.notifier = FakeNotifier()
        self.service = PlatformImageService(
            DatabaseConfiguration(None, "collection", "0.1"),
            PlatformImageConfiguration(self.temp_directory.name, 10),
            image_repository=self.image_repository,
            user_repository=self.user_repository,
            notifier=self.notifier,
            engine=FakeEngine(),
        )

    def tearDown(self):
        """Nettoie le repertoire temporaire.

        Args:
            Aucun.

        Returns:
            None: Les fichiers temporaires sont supprimes.
        """

        self.temp_directory.cleanup()

    def image_file(self, content=b"image", filename="console.png", mimetype="image/png"):
        """Construit un fichier upload factice.

        Args:
            content (bytes): Contenu du fichier.
            filename (str): Nom original.
            mimetype (str): Type MIME.

        Returns:
            FileStorage: Fichier multipart factice.
        """

        return FileStorage(stream=BytesIO(content), filename=filename, content_type=mimetype)

    def test_upload_copies_file_and_inserts_waiting_image_with_token_user(self):
        """Verifie la copie disque et l'insertion SQL.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le workflow.
        """

        image = self.service.upload_image(1, self.image_file(), "USER@EXAMPLE.COM")

        created_image = self.image_repository.created_images[0]
        self.assertEqual(4, image["id"])
        self.assertEqual("WAITING_VALIDATION", image["status"])
        self.assertEqual(7, created_image["user_id"])
        self.assertEqual("user@example.com", self.user_repository.last_email)
        self.assertTrue(Path(created_image["path"]).is_file())
        self.assertEqual([("Nintendo Switch", 4, "user@example.com")], self.notifier.calls)

    def test_upload_adds_counter_on_filename_collision(self):
        """Verifie l'ajout d'un compteur en cas de collision.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le nom final.
        """

        first_image = self.service.upload_image(1, self.image_file(b"first"), "user@example.com")
        second_image = self.service.upload_image(1, self.image_file(b"second"), "user@example.com")

        first_path = Path(self.image_repository.created_images[0]["path"])
        second_path = Path(self.image_repository.created_images[1]["path"])
        self.assertEqual(4, first_image["id"])
        self.assertEqual(4, second_image["id"])
        self.assertEqual("console.png", first_path.name)
        self.assertEqual("console-1.png", second_path.name)

    def test_upload_rejects_unknown_platform(self):
        """Verifie le refus d'une plateforme inconnue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        with self.assertRaises(PlatformImagePlatformNotFoundError):
            self.service.upload_image(99, self.image_file(), "user@example.com")

    def test_upload_rejects_missing_database_user(self):
        """Verifie le refus si le sujet du token n'existe pas en base.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        self.service.user_repository = FakeUserRepository(user_id=None)

        with self.assertRaises(PlatformImageUserNotFoundError):
            self.service.upload_image(1, self.image_file(), "unknown@example.com")

    def test_upload_rejects_too_large_image(self):
        """Verifie le refus d'une image trop volumineuse.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur.
        """

        with self.assertRaises(PlatformImageValidationError):
            self.service.upload_image(1, self.image_file(b"01234567890"), "user@example.com")

        self.assertEqual([], self.image_repository.created_images)

    def test_upload_rejects_invalid_extension_or_mime(self):
        """Verifie le refus d'une extension ou d'un MIME invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les erreurs.
        """

        with self.assertRaises(PlatformImageValidationError):
            self.service.upload_image(1, self.image_file(filename="file.txt"), "user@example.com")
        with self.assertRaises(PlatformImageValidationError):
            self.service.upload_image(
                1,
                self.image_file(filename="file.png", mimetype="text/plain"),
                "user@example.com",
            )

    def test_get_accepted_image_returns_public_file(self):
        """Verifie la lecture publique d'une image acceptee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le fichier public.
        """

        image_path = Path(self.temp_directory.name) / "accepted.png"
        image_path.write_bytes(b"ok")
        self.image_repository.accepted_image = {"path": str(image_path)}

        image_file = self.service.get_accepted_image_file(1, 4)

        self.assertEqual(str(image_path), image_file.path)
        self.assertEqual("image/png", image_file.mimetype)

    def test_get_accepted_image_rejects_waiting_or_missing_file(self):
        """Verifie le refus public d'une image non acceptee ou illisible.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur 404 metier.
        """

        with self.assertRaises(PlatformImageNotFoundError):
            self.service.get_accepted_image_file(1, 4)
        self.image_repository.accepted_image = {"path": str(Path(self.temp_directory.name) / "missing.png")}
        with self.assertRaises(PlatformImageNotFoundError):
            self.service.get_accepted_image_file(1, 4)


if __name__ == "__main__":
    unittest.main()
