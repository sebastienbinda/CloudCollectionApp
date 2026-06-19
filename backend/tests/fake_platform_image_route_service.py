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
# Description : faux service de routes pour les images de plateformes.


class FakePlatformImageRouteService:
    """Service factice des images de plateformes pour les tests HTTP."""

    next_upload_error = None
    next_public_error = None
    next_moderation_error = None
    last_upload_call = None
    last_public_call = None
    last_list_query = None
    last_type_call = None
    last_status_call = None

    def upload_image(self, platform_id, uploaded_file, user_email):
        """Retourne une image creee ou leve l'erreur configuree.

        Args:
            platform_id (int): Identifiant de plateforme.
            uploaded_file (object): Fichier recu.
            user_email (str): Email issu du token.

        Returns:
            dict[str, object]: Image factice.
        """

        self.__class__.last_upload_call = (platform_id, uploaded_file, user_email)
        if self.next_upload_error:
            raise self.next_upload_error
        return {
            "id": 12,
            "platform_id": platform_id,
            "type": "OTHER",
            "status": "WAITING_VALIDATION",
            "user_id": 7,
        }

    def get_accepted_image_file(self, platform_id, image_id):
        """Retourne une image publique ou leve l'erreur configuree.

        Args:
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.

        Returns:
            PlatformImageFile: Fichier public factice.
        """

        from services.library import PlatformImageFile

        self.__class__.last_public_call = (platform_id, image_id)
        if self.next_public_error:
            raise self.next_public_error
        return PlatformImageFile(path=__file__, mimetype="image/png")

    def list_moderation_images(self, query_parameters):
        """Retourne une liste de moderation factice.

        Args:
            query_parameters (object): Parametres HTTP recus.

        Returns:
            dict[str, object]: Payload pagine factice.
        """

        self.__class__.last_list_query = query_parameters
        return {
            "images": [
                {
                    "id": 12,
                    "platform_id": 1,
                    "platform_name": "Switch",
                    "type": "OTHER",
                    "status": "WAITING_VALIDATION",
                    "user_id": 7,
                    "user_email": "user@example.com",
                    "creation_date": "2026-06-19T08:00:00",
                    "image_url": "/api/library/platforms/1/image/12",
                }
            ],
            "page": {"page": 2, "size": 25, "totalElements": 1, "totalPages": 1},
        }

    def update_image_type(self, platform_id, image_id, image_type):
        """Modifie le type d'image factice.

        Args:
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.
            image_type (str): Type demande.

        Returns:
            dict[str, object]: Image modifiee factice.
        """

        self.__class__.last_type_call = (platform_id, image_id, image_type)
        if self.next_moderation_error:
            raise self.next_moderation_error
        return {"image": {"id": image_id, "platform_id": platform_id, "type": image_type.upper()}}

    def update_image_status(self, platform_id, image_id, status):
        """Modifie le statut d'image factice.

        Args:
            platform_id (int): Identifiant de plateforme.
            image_id (int): Identifiant d'image.
            status (str): Statut demande.

        Returns:
            dict[str, object]: Image modifiee factice.
        """

        self.__class__.last_status_call = (platform_id, image_id, status)
        if self.next_moderation_error:
            raise self.next_moderation_error
        return {"image": {"id": image_id, "platform_id": platform_id}, "deleted": status == "refused"}
