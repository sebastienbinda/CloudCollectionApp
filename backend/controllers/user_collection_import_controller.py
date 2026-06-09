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
    CollectionFileType,
    CollectionFileReaderFactory,
)
from services.users.user_collection_import_service import (
    UserCollectionImportConflictError,
    UserCollectionImportInvalidFileError,
    UserCollectionImportNotFoundError,
    UserCollectionImportService,
    UserCollectionImportTemporaryFileMissingError,
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
        reader_factory_class=CollectionFileReaderFactory,
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
            reader_factory_class (type): Classe de factory de lecteurs.
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
        self.reader_factory_class = reader_factory_class
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
            "/api/users/import/",
            endpoint="get_current_user_import_configuration",
            view_func=self.auth_guard.require_profile(UserProfile.USER.value)(
                self.get_current_user_import_configuration
            ),
            methods=["GET"],
            strict_slashes=False,
        )
        flask_app.add_url_rule(
            "/api/users/import/file/<file_type>",
            endpoint="upload_current_user_collection_import_file",
            view_func=self.auth_guard.require_profile(UserProfile.USER.value)(
                self.upload_current_user_collection_import_file
            ),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/users/import/analyze/<file_type>",
            endpoint="analyze_current_user_collection_import_file",
            view_func=self.auth_guard.require_profile(UserProfile.USER.value)(
                self.analyze_current_user_collection_import_file
            ),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/users/import",
            endpoint="import_current_user_collection",
            view_func=self.auth_guard.require_profile(UserProfile.USER.value)(
                self.import_current_user_collection
            ),
            methods=["POST"],
        )
        flask_app.add_url_rule(
            "/api/users/collection/reinit",
            endpoint="reinitialize_current_user_collection",
            view_func=self.auth_guard.require_profile(UserProfile.USER.value)(
                self.reinitialize_current_user_collection
            ),
            methods=["POST"],
        )

    def upload_current_user_collection_import_file(self, file_type: str):
        """Depose le fichier temporaire de collection de l'utilisateur connecte.

        Args:
            file_type (str): Type de fichier cible depuis la route.

        Returns:
            tuple[flask.Response, int]: Resultat JSON ou erreur.
        """

        temporary_file_path = None
        try:
            user_id = self._current_user_id()
            collection_file = request.files.get("collection_file")
            if collection_file is None or not collection_file.filename:
                return jsonify({"error": "Le parametre collection_file est requis."}), 400
            parsed_file_type = self._parse_route_file_type(file_type)
            temporary_file_path = self._save_temporary_upload(collection_file)
            self._create_import_service().upload_import_file(
                user_id,
                str(temporary_file_path),
                collection_file.filename,
                parsed_file_type,
            )
            return jsonify({"uploaded": True}), 201
        except CollectionFileDescriptionValidationError as exc:
            return jsonify({"error": "Configuration invalide.", "details": exc.details}), 422
        except UserCollectionImportInvalidFileError as exc:
            return jsonify({"error": str(exc), "details": exc.details}), 400
        except UserCollectionImportTooLargeError as exc:
            return jsonify({"error": str(exc)}), 413
        except UserCollectionImportConflictError as exc:
            return jsonify({"error": str(exc)}), 409
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant le depot du fichier.")
            return jsonify({"error": "Unable to upload collection file."}), 500
        finally:
            if temporary_file_path is not None:
                self._delete_temporary_file(temporary_file_path)

    def analyze_current_user_collection_import_file(self, file_type: str):
        """Analyse le fichier temporaire et retourne ses onglets.

        Args:
            file_type (str): Type de fichier cible depuis la route.

        Returns:
            tuple[flask.Response, int]: Liste des onglets ou erreur.
        """

        try:
            sheets = self._create_import_service().analyze_import_file(
                self._current_user_id(),
                self._parse_route_file_type(file_type),
            )
            return jsonify({"sheets": sheets})
        except CollectionFileDescriptionValidationError as exc:
            return jsonify({"error": "Configuration invalide.", "details": exc.details}), 422
        except UserCollectionImportTemporaryFileMissingError as exc:
            return jsonify({"error": str(exc)}), 404
        except UserCollectionImportInvalidFileError as exc:
            return jsonify({"error": str(exc), "details": exc.details}), 422
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur inattendue pendant l'analyse collection.")
            return jsonify({"error": "Unable to analyze collection file."}), 500

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

    def get_current_user_import_configuration(self):
        """Retourne la derniere configuration d'import sauvegardee.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int] | flask.Response: Configuration JSON ou erreur.
        """

        try:
            configuration = self._create_import_repository().find_import_configuration(
                self._current_user_id()
            )
            if configuration is None:
                return jsonify({"error": "Configuration d'import introuvable."}), 404
            return jsonify(configuration), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            current_app.logger.exception("Erreur pendant la lecture de la configuration d'import.")
            return jsonify({"error": "Unable to read import configuration."}), 500

    def import_current_user_collection(self):
        """Importe le fichier de collection de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Resultat JSON ou erreur.
        """

        try:
            user_id = self._current_user_id()
            file_description = self._parse_collection_file_description_json()
            result = self._create_import_service().import_collection_from_temporary_file(
                user_id,
                file_description,
            )
            return jsonify(result.to_dict()), 201
        except CollectionFileDescriptionValidationError as exc:
            return jsonify({"error": "Configuration invalide.", "details": exc.details}), 422
        except UserCollectionImportTemporaryFileMissingError as exc:
            return jsonify({"error": str(exc)}), 404
        except UserCollectionImportInvalidFileError as exc:
            current_app.logger.exception(
                "Fichier de collection refuse pendant l'import utilisateur."
            )
            return jsonify({"error": str(exc), "details": exc.details}), 400
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

    def reinitialize_current_user_collection(self):
        """Reinitialise la collection de l'utilisateur connecte.

        Args:
            Aucun.

        Returns:
            tuple[flask.Response, int]: Resultat JSON ou erreur.
        """

        try:
            user_id = self._current_user_id()
            self._create_import_service().reinitialize_collection(user_id)
            return jsonify({"reinitialized": True}), 200
        except UserCollectionImportNotFoundError:
            return jsonify({"error": "Collection introuvable."}), 404
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except UserCollectionImportUnexpectedError:
            current_app.logger.exception(
                "Erreur metier inattendue pendant la reinitialisation collection."
            )
            return jsonify({"error": "Unable to reinitialize collection."}), 500
        except Exception:
            current_app.logger.exception(
                "Erreur inattendue pendant la reinitialisation collection."
            )
            return jsonify({"error": "Unable to reinitialize collection."}), 500

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

    def _parse_collection_file_description_json(self):
        """Parse et valide la description JSON du body d'import.

        Args:
            Aucun.

        Returns:
            CollectionFileDescription: Description valide du fichier importe.

        Raises:
            CollectionFileDescriptionValidationError: Si la description est invalide.
        """

        return self.file_description_validator_class().validate(request.get_json(silent=True))

    def _parse_route_file_type(self, file_type: str) -> CollectionFileType:
        """Parse le type de fichier declare dans une route d'import.

        Args:
            file_type (str): Valeur route.

        Returns:
            CollectionFileType: Type de fichier reconnu.

        Raises:
            CollectionFileDescriptionValidationError: Si le type est inconnu.
        """

        try:
            return CollectionFileType(file_type)
        except ValueError as exc:
            raise CollectionFileDescriptionValidationError(["file_type inconnu."]) from exc

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
            self.reader_factory_class(),
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
