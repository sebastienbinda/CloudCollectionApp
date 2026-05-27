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
# Description : controleur HTTP d'import de collection utilisateur.

from pathlib import Path
from tempfile import NamedTemporaryFile

from flask import Flask, current_app, jsonify, request

from services import (
    AuthGuard,
    DatabaseConfiguration,
    SqlAlchemyUserRepository,
    UserCollectionImportConfiguration,
    UserProfile,
)
from services.database import SqlAlchemyUserCollectionImportRepository
from services.collection.imports import (
    CollectionFileDescriptionValidationError,
    CollectionFileDescriptionValidator,
)
from services.ods import OdsCollectionImportReader
from services.users.user_collection_import_service import (
    UserCollectionImportConflictError,
    UserCollectionImportInvalidFileError,
    UserCollectionImportService,
    UserCollectionImportTooLargeError,
    UserCollectionImportUnexpectedError,
)


class UserCollectionImportController:
    """Enregistre les routes HTTP self-service de collection utilisateur."""

    def __init__(
        self,
        auth_guard: AuthGuard,
        user_repository_class=SqlAlchemyUserRepository,
        import_repository_class=SqlAlchemyUserCollectionImportRepository,
        import_service_class=UserCollectionImportService,
        ods_reader_class=OdsCollectionImportReader,
        file_description_validator_class=CollectionFileDescriptionValidator,
        import_configuration_class=UserCollectionImportConfiguration,
        database_configuration_class=DatabaseConfiguration,
    ):
        """Initialise le controleur d'import de collection.

        Args:
            auth_guard (AuthGuard): Garde d'authentification et de profil.
            user_repository_class (type): Classe de repository utilisateur.
            import_repository_class (type): Classe de repository d'import.
            import_service_class (type): Classe du service metier d'import.
            ods_reader_class (type): Classe du lecteur ODS d'import.
            file_description_validator_class (type): Classe de validation de description.
            import_configuration_class (type): Classe de configuration d'import.
            database_configuration_class (type): Classe de configuration base.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.auth_guard = auth_guard
        self.user_repository_class = user_repository_class
        self.import_repository_class = import_repository_class
        self.import_service_class = import_service_class
        self.ods_reader_class = ods_reader_class
        self.file_description_validator_class = file_description_validator_class
        self.import_configuration_class = import_configuration_class
        self.database_configuration_class = database_configuration_class

    def register_routes(self, flask_app: Flask) -> None:
        """Enregistre les routes de collection utilisateur dans Flask.

        Args:
            flask_app (Flask): Application Flask cible.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        flask_app.add_url_rule(
            "/api/users/me/collection",
            endpoint="get_current_user_collection_status",
            view_func=self.auth_guard.require_profile(UserProfile.USER.value)(
                self.get_current_user_collection_status
            ),
            methods=["GET"],
        )
        flask_app.add_url_rule(
            "/api/users/import",
            endpoint="import_current_user_collection",
            view_func=self.auth_guard.require_profile(UserProfile.USER.value)(
                self.import_current_user_collection
            ),
            methods=["POST"],
        )

    def get_current_user_collection_status(self):
        """Retourne l'existence d'une collection pour l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Statut JSON ou erreur.
        """

        try:
            user_id = self._current_user_id()
            has_collection = self._create_import_repository().user_has_collection(user_id)
            return jsonify({"has_collection": has_collection})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur pendant la lecture du statut collection.")
            return jsonify({"error": "Unable to read collection status."}), 500

    def import_current_user_collection(self):
        """Importe le fichier de collection de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Resultat JSON ou erreur.
        """

        temporary_file_path = None
        try:
            user_id = self._current_user_id()
            collection_file = request.files.get("collection_file")
            if collection_file is None or not collection_file.filename:
                return jsonify({"error": "Le parametre collection_file est requis."}), 400
            self._parse_collection_file_description()
            temporary_file_path = self._save_temporary_upload(collection_file)
            result = self._create_import_service().import_collection(
                user_id,
                str(temporary_file_path),
                collection_file.filename,
            )
            return jsonify(result.to_dict()), 201
        except CollectionFileDescriptionValidationError as exc:
            return jsonify({"error": "Configuration invalide.", "details": exc.details}), 422
        except UserCollectionImportInvalidFileError as exc:
            return jsonify({"error": str(exc)}), 400
        except UserCollectionImportTooLargeError as exc:
            return jsonify({"error": str(exc)}), 413
        except UserCollectionImportConflictError as exc:
            return jsonify({"error": str(exc)}), 409
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except UserCollectionImportUnexpectedError:
            current_app.logger.exception("Erreur metier inattendue pendant l'import collection.")
            return jsonify({"error": "Unable to import collection."}), 500
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant l'import collection.")
            return jsonify({"error": "Unable to import collection."}), 500
        finally:
            if temporary_file_path is not None:
                self._delete_temporary_file(temporary_file_path)

    def _current_user_id(self) -> int:
        """Retourne l'identifiant base de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            int: Identifiant technique utilisateur.

        Raises:
            ValueError: Si le token ne correspond pas a un utilisateur en base.
        """

        payload = self.auth_guard.get_current_token_payload()
        subject = str(payload.get("sub") or "").strip().lower()
        if not subject:
            raise ValueError("Utilisateur connecte invalide.")
        user_id = self._create_user_repository().find_user_id_by_email(subject)
        if user_id is None:
            raise ValueError("Utilisateur connecte introuvable.")
        return user_id

    def _save_temporary_upload(self, collection_file) -> Path:
        """Sauvegarde l'upload multipart dans un fichier temporaire.

        Args:
            collection_file (FileStorage): Fichier recu par Flask.

        Returns:
            Path: Chemin du fichier temporaire sauvegarde.
        """

        with NamedTemporaryFile(prefix="collection-import-", suffix=".ods", delete=False) as file:
            temporary_file_path = Path(file.name)
        collection_file.save(temporary_file_path)
        return temporary_file_path

    def _parse_collection_file_description(self):
        """Parse et valide la description JSON du fichier de collection.

        Args:
            Aucun.

        Returns:
            CollectionFileDescription: Description valide du fichier importe.

        Raises:
            CollectionFileDescriptionValidationError: Si la description est invalide.
        """

        return self.file_description_validator_class().parse_json_text(
            request.form.get("collection_file_description")
        )

    def _delete_temporary_file(self, temporary_file_path: Path) -> None:
        """Supprime le fichier temporaire d'upload.

        Args:
            temporary_file_path (Path): Fichier temporaire a supprimer.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        try:
            temporary_file_path.unlink(missing_ok=True)
        except OSError:
            pass

    def _create_import_service(self):
        """Construit le service metier d'import.

        Args:
            Aucun.

        Returns:
            UserCollectionImportService: Service configure.
        """

        return self.import_service_class(
            self.import_configuration_class.from_environment(),
            self._create_import_repository(),
            self.ods_reader_class(),
        )

    def _create_import_repository(self):
        """Construit le repository transactionnel d'import.

        Args:
            Aucun.

        Returns:
            SqlAlchemyUserCollectionImportRepository: Repository configure.
        """

        return self.import_repository_class(self.database_configuration_class.from_environment())

    def _create_user_repository(self):
        """Construit le repository utilisateur.

        Args:
            Aucun.

        Returns:
            SqlAlchemyUserRepository: Repository configure.
        """

        return self.user_repository_class(self.database_configuration_class.from_environment())
