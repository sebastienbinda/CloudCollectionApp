#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : point d'entree Flask du backend CloudCollectionApp.

import os

from flask import Flask
from flask_cors import CORS

from controllers import (
    AuthenticationController,
    CollectionController,
    GameController,
    LibraryController,
    PlatformController,
    PlatformImageController,
    RouteController,
    StudioController,
    UserCollectionImportController,
    UserController,
)
from services import (
    AuthGuard,
    AuthTokenService,
    BackendLoggingService,
    CollectionShareGuestAuthenticationService,
    DatabaseConfiguration,
    DatabaseSchemaService,
    LibraryResetJobCoordinator,
    LibraryServiceProvider,
    PlatformImageConfiguration,
    SqlAlchemyCollectionShareRepository,
    UserCollectionImportConfiguration,
)

# 1. Configure les services transverses avant de creer l'application Flask.
BackendLoggingService.configure_from_environment()

# 2. Cree l'application HTTP et active les preflights CORS.
app = Flask(__name__)
CORS(app)
BackendLoggingService.register_http_request_logging(app)
user_collection_import_configuration = UserCollectionImportConfiguration.from_environment()
platform_image_configuration = PlatformImageConfiguration.from_environment()
try:
    platform_image_configuration.ensure_image_directory()
except OSError as exc:
    app.logger.warning("Repertoire d'images de plateformes indisponible au demarrage: %s", exc)
app.config["MAX_CONTENT_LENGTH"] = max(
    user_collection_import_configuration.max_upload_bytes,
    platform_image_configuration.max_upload_bytes,
)
app.config["USER_COLLECTION_WORKSPACE_PATH"] = (
    user_collection_import_configuration.workspace_path
)

# 3. Prepare le schema SQL avant d'instancier les composants applicatifs.
DatabaseSchemaService.initialize_database_schema_on_startup(app.logger)

# 4. Instancie les services et controleurs partages par les routes.
auth_token_service = AuthTokenService()
database_configuration = DatabaseConfiguration.from_environment()
collection_share_repository = SqlAlchemyCollectionShareRepository(
    database_configuration.schema_name,
)
collection_share_authentication_service = CollectionShareGuestAuthenticationService(
    database_configuration,
    auth_token_service,
    collection_share_repository,
)
auth_guard = AuthGuard(auth_token_service, collection_share_authentication_service)
authentication_controller = AuthenticationController(
    auth_token_service,
    collection_share_authentication_service,
)
route_controller = RouteController(auth_guard)
user_controller = UserController(auth_guard)
collection_controller = CollectionController(auth_guard)
library_reset_job_coordinator = LibraryResetJobCoordinator()
user_collection_import_controller = UserCollectionImportController(
    auth_guard,
    reset_job_coordinator=library_reset_job_coordinator,
)
library_service_provider = LibraryServiceProvider()
library_controller = LibraryController(
    auth_guard,
    library_reset_job_coordinator,
    library_service_provider=library_service_provider,
)
platform_controller = PlatformController(library_service_factory=library_service_provider)
platform_image_controller = PlatformImageController(auth_guard)
studio_controller = StudioController(library_service_factory=library_service_provider)
game_controller = GameController(library_service_factory=library_service_provider)

# 5. Enregistre les routes avant de les marquer avec la protection globale.
authentication_controller.register_routes(app)
route_controller.register_routes(app)
user_controller.register_routes(app)
user_collection_import_controller.register_routes(app)
collection_controller.register_routes(app)
library_controller.register_routes(app)
platform_controller.register_routes(app)
platform_image_controller.register_routes(app)
studio_controller.register_routes(app)
game_controller.register_routes(app)

# 6. Protege toutes les routes non publiques apres leur enregistrement.
auth_guard.protect_all_routes(
    app,
    exempt_endpoints=(
        authentication_controller.get_public_endpoint_names()
        | platform_controller.get_public_endpoint_names()
        | platform_image_controller.get_public_endpoint_names()
        | studio_controller.get_public_endpoint_names()
        | game_controller.get_public_endpoint_names()
    ),
)

if __name__ == "__main__":
    # 7. Lance le serveur Flask uniquement en execution directe.
    backend_port = int(os.getenv("BACKEND_PORT", "7777"))
    app.run(debug=True, host="0.0.0.0", port=backend_port)
