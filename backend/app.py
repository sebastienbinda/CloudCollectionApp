#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
from io import BytesIO
import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from models import CollectionTypes, Film
from services import (
    AuthGuard,
    AuthTokenService,
    BackendLoggingService,
    DatabaseConfiguration,
    DatabaseSchemaService,
    DuplicateUserEmailError,
    EmailConfiguration,
    EmailSenderFactory,
    EmailVerificationService,
    GamesService,
    InvalidEmailVerificationTokenError,
    PasswordPolicyError,
    RouteDiscoveryService,
    SqlAlchemyUserRepository,
    UserRegistrationService,
)
BackendLoggingService.configure_from_environment()
app = Flask(__name__)
CORS(app)
auth_token_service = AuthTokenService()
auth_guard = AuthGuard(auth_token_service)


def initialize_database_schema_on_startup() -> None:
    """Initialise le schema PostgreSQL configure au demarrage Flask.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.

    Raises:
        ValueError: Si la configuration de base de donnees est invalide.
        sqlalchemy.exc.SQLAlchemyError: Si PostgreSQL refuse l'initialisation.
    """

    configuration = DatabaseConfiguration.from_environment()
    if not configuration.is_database_enabled():
        app.logger.info("DATABASE_URL absent : initialisation SQL ignoree.")
        return
    DatabaseSchemaService(configuration).initialize_database_schema()
    app.logger.info("Schema PostgreSQL initialise : %s.", configuration.schema_name)


initialize_database_schema_on_startup()


COLLECTION_ITEMS = {
    CollectionTypes.Films.value: [
        Film(id=1, name="Interstellar"),
        Film(id=2, name="Inception"),
        Film(id=3, name="Le Seigneur des Anneaux"),
    ],
}
@app.post("/auth/token")
def issue_auth_token():
    """Retourne un token Bearer compatible OAuth2 pour les routes protegees.
    Args:
        Aucun.
    Form or JSON Body:
        username (str): Identifiant backend, ou `client_id` en flux client credentials.
        password (str): Mot de passe backend, ou `client_secret` en flux client credentials.
    Returns:
        tuple[flask.Response, int] | flask.Response: Token OAuth2 ou erreur JSON 401.
    """
    payload = request.get_json(silent=True) or request.form
    username = payload.get("username") or payload.get("client_id") or ""
    password = payload.get("password") or payload.get("client_secret") or ""
    try:
        token_response = auth_token_service.issue_token(username, password)
        return jsonify(token_response)
    except ValueError as exc:
        return (
            jsonify({"error": str(exc)}),
            401,
            {"WWW-Authenticate": 'Bearer realm="CloudCollectionApp"'},
        )


@app.post("/api/auth/register")
def register_user():
    """Enregistre un nouvel utilisateur applicatif protege par Bearer.

    Args:
        Aucun.

    JSON Body:
        email (str): Adresse email du compte a creer.
        password (str): Mot de passe brut a hacher avant stockage.

    Returns:
        tuple[flask.Response, int]: Donnees publiques utilisateur ou erreur JSON.
    """
    payload = request.get_json(silent=True) or {}
    email = payload.get("email", "")
    password = payload.get("password", "")
    app.logger.info("Demande d'inscription utilisateur recue.")
    try:
        user_repository = SqlAlchemyUserRepository(DatabaseConfiguration.from_environment())
        email_sender = EmailSenderFactory.create(EmailConfiguration.from_environment())
        email_verification_service = EmailVerificationService(user_repository, email_sender)
        registration_service = UserRegistrationService(
            user_repository,
            email_verification_service,
        )
        registered_user = registration_service.register_user(email=email, password=password)
        app.logger.info("Utilisateur inscrit avec succes: id=%s.", registered_user.id)
        return jsonify({"user": registered_user.to_public_dict()}), 201
    except DuplicateUserEmailError as exc:
        app.logger.warning("Inscription refusee: email deja utilise.")
        return jsonify({"error": str(exc)}), 409
    except PasswordPolicyError as exc:
        app.logger.warning("Inscription refusee: regles de mot de passe non respectees.")
        return jsonify({"error": str(exc)}), 400
    except ValueError as exc:
        app.logger.warning("Inscription refusee: %s", str(exc))
        if "DATABASE_URL" in str(exc):
            return jsonify({"error": str(exc)}), 503
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Erreur inattendue pendant l'inscription utilisateur.")
        return jsonify({"error": "Unable to register user."}), 500


@app.get("/api/auth/verify-email")
@app.post("/api/auth/verify-email")
def verify_user_email():
    """Valide l'adresse email d'un utilisateur depuis un token applicatif.

    Args:
        Aucun.

    Query Args:
        token (str): Token de validation transmis dans le lien email.

    JSON Body:
        token (str): Token de validation pour les clients API.

    Returns:
        tuple[flask.Response, int]: Donnees publiques de validation ou erreur JSON.
    """
    payload = request.get_json(silent=True) or {}
    raw_token = request.args.get("token") or payload.get("token") or ""
    app.logger.info("Demande de validation email recue.")
    try:
        user_repository = SqlAlchemyUserRepository(DatabaseConfiguration.from_environment())
        email_sender = EmailSenderFactory.create(EmailConfiguration.from_environment())
        email_verification_service = EmailVerificationService(user_repository, email_sender)
        verified_user = email_verification_service.verify_email(raw_token)
        app.logger.info("Email utilisateur valide avec succes: id=%s.", verified_user.id)
        return jsonify({"user": verified_user.to_public_dict()})
    except InvalidEmailVerificationTokenError as exc:
        app.logger.warning("Validation email refusee: token invalide ou expire.")
        return jsonify({"error": str(exc)}), 400
    except ValueError as exc:
        app.logger.warning("Validation email refusee: %s", str(exc))
        if "DATABASE_URL" in str(exc):
            return jsonify({"error": str(exc)}), 503
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Erreur inattendue pendant la validation email.")
        return jsonify({"error": "Unable to verify email."}), 500


@app.get("/api/routes")
def list_accessible_routes():
    """Liste les routes backend et indique celles qui exigent un token.
    Args:
        Aucun.
    Returns:
        flask.Response: Reponse JSON contenant `routes` (list[dict]).
    """
    routes = RouteDiscoveryService(app).list_routes()
    return jsonify({"routes": routes})
@app.get("/collections/<collection_type>/search")
def search_collection_items(collection_type):
    """Recherche des elements dans une collection supportee.
    Args:
        collection_type (str): Type de collection dans l'URL, par exemple `JeuxVideo` ou `Films`.
    Query Args:
        q (str): Texte optionnel de recherche.
        platform (str): Onglet ODS a lire pour la collection `JeuxVideo`.
    Returns:
        tuple[flask.Response, int] | flask.Response: Liste JSON des elements trouves ou erreur JSON.
    """
    try:
        collection_enum = CollectionTypes(collection_type)
    except ValueError:
        return (
            jsonify(
                {
                    "error": "Unknown collection type.",
                    "allowed_types": [t.value for t in CollectionTypes],
                }
            ),
            400,
        )
    search_query = request.args.get("q", "").strip().lower()
    if collection_enum == CollectionTypes.JeuxVideo:
        platform = request.args.get("platform", "Playstation").strip() or "Playstation"
        try:
            items = GamesService().search(platform=platform, query=search_query)
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Sheet '{platform}' not found in ODS file.",
                        "hint": "Use query param ?platform=<sheet_name>.",
                    }
                ),
                400,
            )
        except Exception as exc:
            return jsonify({"error": f"Unable to read ODS file: {exc}"}), 500
    else:
        items = COLLECTION_ITEMS[collection_enum.value]
    if search_query and collection_enum != CollectionTypes.JeuxVideo:
        items = [
            item
            for item in items
            if search_query
            in " ".join(str(value).lower() for value in item.to_dict().values())
        ]
    if collection_enum == CollectionTypes.JeuxVideo:
        return jsonify(items)
    return jsonify({"type": collection_enum.value, "items": [item.to_dict() for item in items]})
@app.get("/collections/JeuxVideo/platforms")
def list_jeux_video_platforms():
    """Liste les plateformes disponibles dans le fichier ODS.
    Args:
        Aucun.
    Returns:
        tuple[flask.Response, int] | flask.Response: Objet JSON avec `type` (str) et `platforms` (list[str]).
    """
    try:
        platforms = GamesService().list_platforms()
        return jsonify({"type": CollectionTypes.JeuxVideo.value, "platforms": platforms})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"Unable to read ODS file: {exc}"}), 500
@app.get("/collections/JeuxVideo/home")
def get_jeux_video_home():
    """Retourne les statistiques de l'onglet `Accueil` du fichier ODS.
    Args:
        Aucun.
    Returns:
        tuple[flask.Response, int] | flask.Response: Donnees JSON du tableau de bord ou erreur JSON.
    """
    try:
        stats = GamesService().get_home_stats()
        return jsonify({"type": CollectionTypes.JeuxVideo.value, **stats})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError:
        return (
            jsonify(
                {
                    "error": "Sheet 'Accueil' not found in ODS file.",
                }
            ),
            400,
        )
    except Exception as exc:
        return jsonify({"error": f"Unable to read ODS file: {exc}"}), 500
@app.post("/collections/JeuxVideo/cache/reset")
@auth_guard.require_token
def reset_jeux_video_cache():
    """Vide le cache backend des donnees lues depuis le fichier ODS.
    Args:
        Aucun.
    Returns:
        tuple[flask.Response, int] | flask.Response: Statut JSON avec le nombre d'entrees supprimees.
    """
    try:
        removed_entries = GamesService().reset_cache()
        return jsonify(
            {
                "type": CollectionTypes.JeuxVideo.value,
                "message": "Cache ODS reinitialise.",
                "removed_entries": removed_entries,
            }
        )
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"Unable to reset ODS cache: {exc}"}), 500
@app.get("/collections/JeuxVideo/ods/download")
@auth_guard.require_token
def download_jeux_video_ods():
    """Telecharge le fichier ODS de la collection jeux video.
    Args:
        Aucun.
    Returns:
        flask.Response | tuple[flask.Response, int]: Fichier ODS ou erreur JSON.
    """
    try:
        ods_path, filename = GamesService().get_ods_download()
        return send_file(
            ods_path,
            mimetype="application/vnd.oasis.opendocument.spreadsheet",
            as_attachment=True,
            download_name=filename,
        )
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"Unable to download ODS file: {exc}"}), 500
@app.get("/collections/JeuxVideo/game-search")
def search_jeux_video_games():
    """Recherche un jeu par nom dans toutes les plateformes.
    Args:
        Aucun.
    Query Args:
        q (str): Texte recherche dans le nom du jeu.
        limit (str): Nombre maximal de resultats, converti en int entre 1 et 100.
    Returns:
        tuple[flask.Response, int] | flask.Response: Objet JSON avec `items` (list[dict]) ou erreur JSON.
    """
    search_query = request.args.get("q", "").strip()
    limit = request.args.get("limit", "50").strip()
    try:
        parsed_limit = max(1, min(int(limit), 100))
    except ValueError:
        parsed_limit = 50
    try:
        items = GamesService().search_by_game_name(
            query=search_query,
            limit=parsed_limit,
        )
        return jsonify(
            {
                "type": CollectionTypes.JeuxVideo.value,
                "query": search_query,
                "count": len(items),
                "items": items,
            }
        )
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"Unable to search ODS file: {exc}"}), 500
@app.post("/collections/JeuxVideo/games")
@auth_guard.require_token
def add_jeux_video_game():
    """Ajoute un jeu dans l'onglet ODS correspondant a sa plateforme.
    Args:
        Aucun.
    JSON Body:
        dict[str, Any]: Donnees du jeu, dont `platform` (str) et `Nom du jeu` (str).
    Returns:
        tuple[flask.Response, int]: Objet JSON avec le jeu ajoute et statut 201, ou erreur JSON.
    """
    payload = request.get_json(silent=True) or {}
    try:
        item = GamesService().add_game(payload)
        return jsonify({"type": CollectionTypes.JeuxVideo.value, "item": item}), 201
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500
@app.delete("/collections/JeuxVideo/games")
@auth_guard.require_token
def delete_jeux_video_game():
    """Supprime un jeu dans l'onglet ODS de sa plateforme.
    Args:
        Aucun.
    JSON Body:
        dict[str, Any]: Donnees du jeu, dont `platform` (str) et `Nom du jeu` (str).
    Returns:
        tuple[flask.Response, int]: Objet JSON avec le jeu supprime ou erreur JSON.
    """
    payload = request.get_json(silent=True) or {}
    try:
        item = GamesService().delete_game(payload)
        return jsonify({"type": CollectionTypes.JeuxVideo.value, "item": item})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500
@app.put("/collections/JeuxVideo/games")
@auth_guard.require_token
def update_jeux_video_game():
    """Modifie un jeu dans l'onglet ODS de sa plateforme.
    Args:
        Aucun.
    JSON Body:
        dict[str, Any]: Donnees contenant `platform`, `original` et `updated`.
    Returns:
        tuple[flask.Response, int]: Objet JSON avec le jeu modifie ou erreur JSON.
    """
    payload = request.get_json(silent=True) or {}
    try:
        item = GamesService().update_game(payload)
        return jsonify({"type": CollectionTypes.JeuxVideo.value, "item": item})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500
@app.delete("/collections/JeuxVideo/wishlist/games")
@auth_guard.require_token
def delete_jeux_video_wishlist_game():
    """Supprime un jeu dans l'onglet ODS `Liste de souhaits`.
    Args:
        Aucun.
    JSON Body:
        dict[str, Any]: Donnees du jeu, dont `Nom du jeu` (str) et `Console` (str).
    Returns:
        tuple[flask.Response, int]: Objet JSON avec le jeu supprime ou erreur JSON.
    """
    payload = request.get_json(silent=True) or {}
    try:
        item = GamesService().delete_wishlist_game(payload)
        return jsonify({"type": CollectionTypes.JeuxVideo.value, "item": item})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500
@app.post("/collections/JeuxVideo/wishlist/games")
@auth_guard.require_token
def add_jeux_video_wishlist_game():
    """Ajoute un jeu dans l'onglet ODS `Liste de souhaits`.
    Args:
        Aucun.
    JSON Body:
        dict[str, Any]: Donnees du jeu, dont `Nom du jeu`, `Console` et `Studio`.
    Returns:
        tuple[flask.Response, int]: Objet JSON avec le jeu ajoute et statut 201, ou erreur JSON.
    """
    payload = request.get_json(silent=True) or {}
    try:
        item = GamesService().add_wishlist_game(payload)
        return jsonify({"type": CollectionTypes.JeuxVideo.value, "item": item}), 201
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500
@app.put("/collections/JeuxVideo/wishlist/games")
@auth_guard.require_token
def update_jeux_video_wishlist_game():
    """Modifie un jeu dans l'onglet ODS `Liste de souhaits`.
    Args:
        Aucun.
    JSON Body:
        dict[str, Any]: Donnees contenant `original` et `updated`.
    Returns:
        tuple[flask.Response, int]: Objet JSON avec le jeu modifie ou erreur JSON.
    """
    payload = request.get_json(silent=True) or {}
    try:
        item = GamesService().update_wishlist_game(payload)
        return jsonify({"type": CollectionTypes.JeuxVideo.value, "item": item})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500
@app.get("/collections/JeuxVideo/platform-image/<path:platform>")
def get_jeux_video_platform_image(platform):
    """Retourne l'image embarquee dans l'onglet ODS d'une plateforme.
    Args:
        platform (str): Nom de l'onglet plateforme recherche dans le fichier ODS.
    Returns:
        flask.Response | tuple[flask.Response, int]: Flux image avec son MIME type, ou erreur JSON.
    """
    try:
        image_bytes, mime_type, filename = GamesService().get_platform_image(platform)
        response = send_file(
            BytesIO(image_bytes),
            mimetype=mime_type,
            download_name=filename,
            max_age=0,
        )
        response.headers["Cache-Control"] = "no-store, max-age=0"
        return response
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": f"Unable to read ODS image: {exc}"}), 500
@app.get("/collections/JeuxVideo/column-values")
def list_jeux_video_column_values():
    """Liste les valeurs distinctes de chaque colonne pour une plateforme.
    Args:
        Aucun.
    Query Args:
        platform (str): Nom de l'onglet ODS a analyser.
    Returns:
        tuple[flask.Response, int] | flask.Response: Objet JSON avec `values_by_column` ou erreur JSON.
    """
    platform = request.args.get("platform", "Playstation").strip() or "Playstation"
    try:
        values = GamesService().list_column_values(platform=platform)
        return jsonify(
            {
                "type": CollectionTypes.JeuxVideo.value,
                "platform": platform,
                "values_by_column": values,
            }
        )
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError:
        return (
            jsonify(
                {
                    "error": f"Sheet '{platform}' not found in ODS file.",
                    "hint": "Use query param ?platform=<sheet_name>.",
                }
            ),
            400,
        )
    except Exception as exc:
        return jsonify({"error": f"Unable to read ODS file: {exc}"}), 500
@app.get("/collections/JeuxVideo/add-game-choices")
def list_jeux_video_add_game_choices():
    """Liste les choix fusionnes pour le formulaire d'ajout.
    Args:
        Aucun.
    Query Args:
        platform (str): Plateforme collection de reference pour les suggestions.
    Returns:
        flask.Response | tuple[flask.Response, int]: Objet JSON avec les choix fusionnes.
    """
    platform = request.args.get("platform", "").strip()
    try:
        choices = GamesService().list_add_game_choices(platform=platform)
        return jsonify({"type": CollectionTypes.JeuxVideo.value, **choices})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Unable to read ODS choices: {exc}"}), 500


auth_guard.protect_all_routes(app, exempt_endpoints={"issue_auth_token"})


if __name__ == "__main__":
    backend_port = int(os.getenv("BACKEND_PORT", "7777"))
    app.run(debug=True, host="0.0.0.0", port=backend_port)
