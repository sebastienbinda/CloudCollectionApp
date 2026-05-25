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
    PlatformController,
    RouteController,
    StudioController,
    UserCollectionImportController,
    UserController,
)
from services import (
    AuthGuard,
    AuthTokenService,
    BackendLoggingService,
    DatabaseSchemaService,
    UserCollectionImportConfiguration,
)

# 1. Configure les services transverses avant de creer l'application Flask.
BackendLoggingService.configure_from_environment()

# 2. Cree l'application HTTP et active les preflights CORS.
app = Flask(__name__)
CORS(app)
user_collection_import_configuration = UserCollectionImportConfiguration.from_environment()
app.config["MAX_CONTENT_LENGTH"] = user_collection_import_configuration.max_upload_bytes
app.config["USER_COLLECTION_WORKSPACE_PATH"] = (
    user_collection_import_configuration.workspace_path
)

# 3. Prepare le schema SQL avant d'instancier les composants applicatifs.
DatabaseSchemaService.initialize_database_schema_on_startup(app.logger)

# 4. Instancie les services et controleurs partages par les routes.
auth_token_service = AuthTokenService()
auth_guard = AuthGuard(auth_token_service)
authentication_controller = AuthenticationController(auth_token_service)
route_controller = RouteController()
user_controller = UserController(auth_guard)
user_collection_import_controller = UserCollectionImportController(auth_guard)
collection_controller = CollectionController(auth_guard)
platform_controller = PlatformController()
studio_controller = StudioController()
game_controller = GameController()

# 5. Enregistre les routes avant de les marquer avec la protection globale.
authentication_controller.register_routes(app)
route_controller.register_routes(app)
user_controller.register_routes(app)
user_collection_import_controller.register_routes(app)
collection_controller.register_routes(app)
platform_controller.register_routes(app)
studio_controller.register_routes(app)
game_controller.register_routes(app)

# 6. Protege toutes les routes non publiques apres leur enregistrement.
auth_guard.protect_all_routes(
    app,
    exempt_endpoints=(
        authentication_controller.get_public_endpoint_names()
        | platform_controller.get_public_endpoint_names()
        | studio_controller.get_public_endpoint_names()
        | game_controller.get_public_endpoint_names()
    ),
)

if __name__ == "__main__":
    # 7. Lance le serveur Flask uniquement en execution directe.
    backend_port = int(os.getenv("BACKEND_PORT", "7777"))
    app.run(debug=True, host="0.0.0.0", port=backend_port)
