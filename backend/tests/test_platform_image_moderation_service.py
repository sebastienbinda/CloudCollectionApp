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
# Description : tests de moderation des images de plateformes.

from datetime import datetime
import tempfile
import unittest
from pathlib import Path

from services.database import DatabaseConfiguration
from services.library import PlatformImageConfiguration
from services.library.platform_image_service import PlatformImageService

try:
    from tests.test_platform_image_service import FakeEngine, FakeNotifier, FakeUserRepository
except ModuleNotFoundError:
    from test_platform_image_service import FakeEngine, FakeNotifier, FakeUserRepository


class FakeModerationPlatformImageRepository:
    """Repository factice des images de moderation."""

    def __init__(self, image_path: str):
        """Initialise les images factices.

        Args:
            image_path (str): Chemin disque de l'image refusee.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.images = {
            12: {
                "id": 12,
                "platform": 1,
                "platform_name": "Switch",
                "path": image_path,
                "file_size_bytes": 262144,
                "type": "MAIN",
                "status": "WAITING_VALIDATION",
                "user_id": 7,
                "user_email": "user@example.com",
                "creation_date": datetime(2026, 6, 19, 8, 0, 0),
            },
            13: {
                "id": 13,
                "platform": 1,
                "platform_name": "Switch",
                "path": image_path,
                "file_size_bytes": 131072,
                "type": "OTHER",
                "status": "WAITING_VALIDATION",
                "user_id": 8,
                "user_email": "other@example.com",
                "creation_date": datetime(2026, 6, 19, 9, 0, 0),
            },
        }
        self.last_count_filters = None
        self.last_list_filters = None

    def count_moderation_images(self, connection, status, platform_filter):
        """Compte les images avec les filtres recus.

        Args:
            connection (object): Connexion ignoree.
            status (str): Filtre statut.
            platform_filter (str): Filtre plateforme.

        Returns:
            int: Nombre d'images factices.
        """

        self.last_count_filters = (status, platform_filter)
        return 2

    def list_moderation_images(
        self,
        connection,
        status,
        platform_filter,
        page_request,
        sort_rules,
    ):
        """Liste les images avec pagination et filtres recus.

        Args:
            connection (object): Connexion ignoree.
            status (str): Filtre statut.
            platform_filter (str): Filtre plateforme.
            page_request (LibraryPageRequest): Pagination.
            sort_rules (tuple): Tris recus.

        Returns:
            list[dict[str, object]]: Images factices.
        """

        self.last_list_filters = (status, platform_filter, page_request, sort_rules)
        return [self.images[12]]

    def get_global_storage_summary(self, connection):
        """Retourne un resume de stockage factice.

        Args:
            connection (object): Connexion ignoree.

        Returns:
            dict[str, int]: Nombre et taille totale des images.
        """

        return {
            "total_images": len(self.images),
            "total_size_bytes": sum(
                int(image.get("file_size_bytes") or 0) for image in self.images.values()
            ),
        }

    def update_image_status(self, connection, platform_id, image_id, status):
        """Modifie le statut d'une image factice.

        Args:
            connection (object): Connexion ignoree.
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.
            status (str): Statut cible.

        Returns:
            dict[str, object] | None: Image modifiee ou absence.
        """

        image = self.find_image(connection, platform_id, image_id)
        if not image:
            return None
        image["status"] = status
        return image

    def find_image(self, connection, platform_id, image_id):
        """Retourne une image factice.

        Args:
            connection (object): Connexion ignoree.
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.

        Returns:
            dict[str, object] | None: Image trouvee ou absence.
        """

        image = self.images.get(image_id)
        if image and image["platform"] == platform_id:
            return image
        return None

    def delete_image(self, connection, platform_id, image_id):
        """Supprime une image factice.

        Args:
            connection (object): Connexion ignoree.
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.

        Returns:
            bool: `True` si l'image existait.
        """

        return self.images.pop(image_id, None) is not None

    def set_image_type(self, connection, platform_id, image_id, image_type):
        """Modifie le type d'une image factice.

        Args:
            connection (object): Connexion ignoree.
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.
            image_type (str): Type cible.

        Returns:
            dict[str, object] | None: Image modifiee ou absence.
        """

        image = self.find_image(connection, platform_id, image_id)
        if not image:
            return None
        if image_type == "MAIN":
            for existing_image in self.images.values():
                if existing_image["platform"] == platform_id:
                    existing_image["type"] = "OTHER"
        image["type"] = image_type
        return image


class PlatformImageModerationServiceTest(unittest.TestCase):
    """Valide la moderation metier des images de plateformes."""

    def setUp(self):
        """Prepare le service de moderation.

        Args:
            Aucun.

        Returns:
            None: Les dependances factices sont preparees.
        """

        self.temp_directory = tempfile.TemporaryDirectory()
        self.image_path = Path(self.temp_directory.name) / "image.png"
        self.image_path.write_bytes(b"image")
        self.image_repository = FakeModerationPlatformImageRepository(str(self.image_path))
        self.service = PlatformImageService(
            DatabaseConfiguration(None, "collection", "0.1"),
            PlatformImageConfiguration(self.temp_directory.name, 10),
            image_repository=self.image_repository,
            user_repository=FakeUserRepository(),
            notifier=FakeNotifier(),
            engine=FakeEngine(),
        )

    def tearDown(self):
        """Nettoie les fichiers temporaires.

        Args:
            Aucun.

        Returns:
            None: Le repertoire temporaire est supprime.
        """

        self.temp_directory.cleanup()

    def test_list_moderation_images_uses_pagination_and_filters(self):
        """Verifie pagination, filtres et payload de liste.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la liste admin.
        """

        payload = self.service.list_moderation_images(
            {
                "page": "2",
                "size": "25",
                "status": "accepted",
                "platform": "Switch",
                "sort": "platform,asc",
            }
        )
        page_request = self.image_repository.last_list_filters[2]

        self.assertEqual("ACCEPTED", self.image_repository.last_count_filters[0])
        self.assertEqual("Switch", self.image_repository.last_count_filters[1])
        self.assertEqual(2, page_request.page)
        self.assertEqual(25, page_request.size)
        self.assertEqual(7, payload["images"][0]["user_id"])
        self.assertEqual(262144, payload["images"][0]["file_size_bytes"])
        self.assertEqual(2, payload["storage_summary"]["total_images"])
        self.assertEqual(393216, payload["storage_summary"]["total_size_bytes"])
        self.assertEqual("/api/library/platforms/1/image/12", payload["images"][0]["image_url"])
        self.assertEqual(
            "/api/library/platforms/1/image/12/moderation",
            payload["images"][0]["moderation_image_url"],
        )

    def test_update_status_accepts_image(self):
        """Verifie l'acceptation d'une image.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        payload = self.service.update_image_status(1, 12, "accepted")

        self.assertEqual("ACCEPTED", payload["image"]["status"])
        self.assertIn(12, self.image_repository.images)

    def test_update_status_refuses_image_and_deletes_file_and_sql(self):
        """Verifie le refus avec suppression disque et SQL.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les suppressions.
        """

        payload = self.service.update_image_status(1, 12, "refused")

        self.assertTrue(payload["deleted"])
        self.assertNotIn(12, self.image_repository.images)
        self.assertFalse(self.image_path.exists())

    def test_update_type_main_switches_existing_main_to_other(self):
        """Verifie la bascule automatique de l'ancienne image MAIN.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les types.
        """

        payload = self.service.update_image_type(1, 13, "MAIN")

        self.assertEqual("MAIN", payload["image"]["type"])
        self.assertEqual("OTHER", self.image_repository.images[12]["type"])
        self.assertEqual("MAIN", self.image_repository.images[13]["type"])


if __name__ == "__main__":
    unittest.main()
