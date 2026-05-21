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
import unittest
from datetime import datetime
from pathlib import Path
import app as app_module
from services.auth import (
    DuplicateUserEmailError,
    InvalidEmailVerificationTokenError,
    PasswordPolicyError,
    RegisteredUser,
)
from services.auth.email_verification_service import EmailVerificationService, VerifiedUser


class FakeSqlAlchemyUserRepository:
    def __init__(self, configuration):
        """Initialise un repository utilisateur factice.
        Args:
            configuration (DatabaseConfiguration): Configuration ignoree en test.
        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.configuration = configuration

    def verify_email_by_token_hash(self, token_hash, verified_at):
        """Valide un token factice.
        Args:
            token_hash (str): Empreinte du token.
            verified_at (datetime): Date de validation.
        Returns:
            VerifiedUser: Utilisateur valide factice.
        """

        if token_hash == EmailVerificationService.hash_token("invalid-token"):
            raise InvalidEmailVerificationTokenError("Le token de validation est invalide ou expire.")
        return VerifiedUser(id=7, email="user@example.com", email_verified_at=verified_at)


class FakeUserRegistrationService:
    def __init__(self, user_repository, email_verification_service):
        """Initialise un service d'inscription factice.
        Args:
            user_repository (object): Repository injecte par la route.
            email_verification_service (object): Service de validation email injecte par la route.
        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.user_repository = user_repository
        self.email_verification_service = email_verification_service

    def register_user(self, email, password):
        """Retourne un utilisateur factice ou leve une erreur controlee.
        Args:
            email (str): Email fourni par la route.
            password (str): Mot de passe fourni par la route.
        Returns:
            RegisteredUser: Utilisateur public factice.
        """

        if email == "duplicate@example.com":
            raise DuplicateUserEmailError("Un compte existe deja pour cet email.")
        if not email:
            raise ValueError("L'email est obligatoire.")
        if password != "VeryStrongPassword123!":
            raise PasswordPolicyError(
                "Le mot de passe doit contenir au moins 8 caracteres, au moins un chiffre, "
                "un caractere special, une minuscule et une majuscule."
            )
        return RegisteredUser(
            id=7,
            email=str(email).strip().lower(),
            creation_date=datetime(2026, 5, 13, 12, 0, 0),
            is_email_verified=False,
        )
class FakeGamesService:
    def __init__(self):
        """Initialise un service JeuxVideo factice.
        Args:
            Aucun.
        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """
    def list_platforms(self):
        """Retourne les plateformes factices.
        Args:
            Aucun.
        Returns:
            list[str]: Plateformes disponibles.
        """
        return ["Switch", "Playstation"]
    def reset_cache(self):
        """Retourne un nombre factice d'entrees supprimees.
        Args:
            Aucun.
        Returns:
            int: Nombre d'entrees supprimees.
        """
        return 2
    def get_ods_download(self):
        """Retourne un fichier ODS factice a telecharger.
        Args:
            Aucun.
        Returns:
            tuple[str, str]: Chemin et nom de fichier factices.
        """
        return str(Path(__file__)), "JeuxVideo-test.ods"
    def search(self, platform, query=""):
        """Retourne les jeux factices d'une plateforme.
        Args:
            platform (str): Plateforme demandee.
            query (str): Recherche optionnelle.
        Returns:
            list[dict[str, str]]: Jeux factices.
        """
        return [
            {
                "Nom du jeu": "Mario Kart",
                "Plateforme": platform,
                "Query": query,
                "Prix d'achat": 45,
            }
        ]
    def search_by_game_name(self, query, limit=50):
        """Retourne les jeux factices trouves par nom.
        Args:
            query (str): Texte recherche.
            limit (int): Nombre maximal de resultats.
        Returns:
            list[dict[str, object]]: Jeux factices trouves.
        """
        return [
            {
                "Nom du jeu": "Mario Kart",
                "Plateforme": "Switch",
                "Query": query,
                "Prix d'achat": 45,
            }
        ][:limit]
    def get_home_stats(self):
        """Retourne des statistiques d'accueil factices.
        Args:
            Aucun.
        Returns:
            dict[str, object]: Statistiques factices avec prix.
        """
        return {
            "title": "Jeux Video",
            "totals": {"games_count": 1, "total_price": 45, "average_price": 45},
            "platforms": [
                {
                    "name": "Switch",
                    "sheet_name": "Switch",
                    "games_count": 1,
                    "total_price": 45,
                    "average_price": 45,
                }
            ],
        }
    def list_column_values(self, platform):
        """Retourne les valeurs distinctes factices d'une plateforme.
        Args:
            platform (str): Plateforme demandee.
        Returns:
            dict[str, list[object]]: Valeurs distinctes factices.
        """
        return {"Nom du jeu": ["Mario Kart"], "Prix d'achat": [45]}
    def add_game(self, payload):
        """Retourne le jeu ajoute sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees du jeu.
        Returns:
            dict[str, str]: Jeu ajoute.
        """
        if not payload.get("Nom du jeu"):
            raise ValueError("Le nom du jeu est obligatoire.")
        return {"Plateforme": payload.get("platform"), "Nom du jeu": payload.get("Nom du jeu")}
    def delete_wishlist_game(self, payload):
        """Retourne le jeu wishlist supprime sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees du jeu.
        Returns:
            dict[str, str]: Jeu supprime.
        """
        if not payload.get("Console"):
            raise ValueError("La console est obligatoire.")
        return {"Nom du jeu": payload.get("Nom du jeu"), "Console": payload.get("Console")}
    def add_wishlist_game(self, payload):
        """Retourne le jeu wishlist ajoute sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees du jeu wishlist.
        Returns:
            dict[str, str]: Jeu ajoute.
        """
        if not payload.get("Studio"):
            raise ValueError("Studio est obligatoire.")
        return {"Nom du jeu": payload.get("Nom du jeu"), "Console": payload.get("Console")}
    def update_wishlist_game(self, payload):
        """Retourne le jeu wishlist modifie sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees de modification.
        Returns:
            dict[str, str]: Jeu wishlist modifie.
        """
        updated = payload.get("updated") or {}
        if not updated.get("Studio"):
            raise ValueError("Studio est obligatoire.")
        return {"Nom du jeu": updated.get("Nom du jeu"), "Console": updated.get("Console")}
    def delete_game(self, payload):
        """Retourne le jeu supprime sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees du jeu.
        Returns:
            dict[str, str]: Jeu supprime.
        """
        if not payload.get("Nom du jeu"):
            raise ValueError("Le nom du jeu est obligatoire.")
        return {"Plateforme": payload.get("platform"), "Nom du jeu": payload.get("Nom du jeu")}
    def update_game(self, payload):
        """Retourne le jeu modifie sans modifier de fichier.
        Args:
            payload (dict[str, str]): Donnees de modification.
        Returns:
            dict[str, str]: Jeu modifie.
        """
        updated = payload.get("updated") or {}
        if not updated.get("Nom du jeu"):
            raise ValueError("Nom du jeu est obligatoire.")
        return {"Plateforme": payload.get("platform"), **updated}
    def list_add_game_choices(self, platform=""):
        """Retourne des choix fusionnes factices.
        Args:
            platform (str): Plateforme de reference.
        Returns:
            dict[str, object]: Choix du formulaire d'ajout.
        """
        return {"platforms": ["Switch", "Xbox"], "values_by_column": {"Plateforme": ["Switch", "Xbox"]}}
class AppRoutesTest(unittest.TestCase):
    def setUp(self):
        """Remplace le service ODS par un service factice.
        Args:
            Aucun.
        Returns:
            None: Le client Flask est prepare pour chaque test.
        """
        self.original_service = app_module.GamesService
        self.original_user_repository = app_module.authentication_controller.user_repository_class
        self.original_registration_service = (
            app_module.authentication_controller.user_registration_service_class
        )
        app_module.GamesService = FakeGamesService
        app_module.authentication_controller.user_repository_class = FakeSqlAlchemyUserRepository
        app_module.authentication_controller.user_registration_service_class = (
            FakeUserRegistrationService
        )
        app_module.app.config.update(TESTING=True)
        self.client = app_module.app.test_client()
    def tearDown(self):
        """Restaure le service ODS original.
        Args:
            Aucun.
        Returns:
            None: Les modifications globales du test sont annulees.
        """
        app_module.GamesService = self.original_service
        app_module.authentication_controller.user_repository_class = self.original_user_repository
        app_module.authentication_controller.user_registration_service_class = (
            self.original_registration_service
        )
    def get_auth_headers(self):
        """Construit un header Bearer valide pour les routes protegees.
        Args:
            Aucun.
        Returns:
            dict[str, str]: En-tetes HTTP contenant le token d'authentification.
        """
        token = app_module.auth_token_service.create_access_token("admin")
        return {"Authorization": f"Bearer {token}"}
    def test_auth_token_route_returns_bearer_token(self):
        """Verifie la generation d'un token OAuth2 Bearer.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/auth/token",
            json={"username": "admin", "password": "change-me"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Bearer", response.get_json()["token_type"])
        self.assertTrue(response.get_json()["access_token"])
    def test_auth_token_route_rejects_invalid_credentials(self):
        """Verifie le refus des identifiants invalides.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/auth/token",
            json={"username": "admin", "password": "bad-password"},
        )
        self.assertEqual(401, response.status_code)
        self.assertIn("invalides", response.get_json()["error"])
    def test_routes_route_requires_authentication(self):
        """Verifie que le catalogue des routes exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/api/routes")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_register_user_route_returns_public_user(self):
        """Verifie la creation publique d'un utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/api/auth/register",
            json={"email": " USER@Example.COM ", "password": "VeryStrongPassword123!"},
        )
        data = response.get_json()
        self.assertEqual(201, response.status_code)
        self.assertEqual(7, data["user"]["id"])
        self.assertEqual("user@example.com", data["user"]["email"])
        self.assertFalse(data["user"]["is_email_verified"])
        self.assertNotIn("password", data["user"])
        self.assertNotIn("password_hash", data["user"])
    def test_register_user_route_rejects_duplicate_email(self):
        """Verifie la reponse HTTP pour un email deja utilise.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident le statut 409.
        """
        response = self.client.post(
            "/api/auth/register",
            json={"email": "duplicate@example.com", "password": "VeryStrongPassword123!"},
        )
        self.assertEqual(409, response.status_code)
        self.assertIn("existe deja", response.get_json()["error"])
    def test_register_user_route_rejects_invalid_payload(self):
        """Verifie la reponse HTTP pour une inscription invalide.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident le statut 400.
        """
        response = self.client.post(
            "/api/auth/register",
            json={"email": "user@example.com", "password": "short"},
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("8 caracteres", response.get_json()["error"])
        self.assertIn("un chiffre", response.get_json()["error"])
        self.assertIn("un caractere special", response.get_json()["error"])
        self.assertIn("une minuscule", response.get_json()["error"])
        self.assertIn("une majuscule", response.get_json()["error"])
    def test_verify_email_route_returns_verified_user(self):
        """Verifie la validation publique d'email depuis un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/api/auth/verify-email?token=valid-token")
        data = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual(7, data["user"]["id"])
        self.assertEqual("user@example.com", data["user"]["email"])
        self.assertIn("email_verified_at", data["user"])
    def test_verify_email_route_rejects_missing_token(self):
        """Verifie le refus d'une validation sans token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/api/auth/verify-email")
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
    def test_verify_email_route_rejects_invalid_token(self):
        """Verifie le refus d'un token invalide.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post("/api/auth/verify-email", json={"token": "invalid-token"})
        self.assertEqual(400, response.status_code)
        self.assertIn("invalide", response.get_json()["error"])
    def test_platforms_route_requires_authentication(self):
        """Verifie que la liste des plateformes exige un token.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/platforms")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_platforms_route_returns_platforms(self):
        """Verifie l'endpoint de liste des plateformes.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get(
            "/collections/JeuxVideo/platforms",
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(["Switch", "Playstation"], response.get_json()["platforms"])
    def test_search_route_requires_authentication(self):
        """Verifie que la recherche exige un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/search?platform=Switch")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_search_route_keeps_prices_with_authentication(self):
        """Verifie que la recherche authentifiee retourne les prix.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la presence des prix.
        """
        response = self.client.get(
            "/collections/JeuxVideo/search?platform=Switch",
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(45, response.get_json()[0]["Prix d'achat"])
    def test_game_search_route_requires_authentication(self):
        """Verifie que la recherche globale exige un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/game-search?q=mario")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_home_route_requires_authentication(self):
        """Verifie que l'accueil exige un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/home")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_home_route_keeps_price_statistics_with_authentication(self):
        """Verifie que l'accueil authentifie retourne les statistiques de prix.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident les champs presents.
        """
        response = self.client.get(
            "/collections/JeuxVideo/home",
            headers=self.get_auth_headers(),
        )
        data = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual(45, data["totals"]["total_price"])
        self.assertEqual(45, data["platforms"][0]["average_price"])
    def test_column_values_route_requires_authentication(self):
        """Verifie que les valeurs de filtre exigent un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/column-values?platform=Switch")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_column_values_route_keeps_price_values_with_authentication(self):
        """Verifie que les valeurs de filtre authentifiees retournent les prix.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la presence des prix.
        """
        response = self.client.get(
            "/collections/JeuxVideo/column-values?platform=Switch",
            headers=self.get_auth_headers(),
        )
        data = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual([45], data["values_by_column"]["Prix d'achat"])
    def test_routes_route_lists_protected_routes(self):
        """Verifie le catalogue des routes et leurs contraintes d'authentification.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident le contrat de decouverte des routes.
        """
        response = self.client.get("/api/routes", headers=self.get_auth_headers())
        routes = response.get_json()["routes"]
        routes_by_key = {
            (route["path"], tuple(route["methods"])): route
            for route in routes
        }
        self.assertEqual(200, response.status_code)
        self.assertFalse(routes_by_key[("/auth/token", ("POST",))]["requires_auth"])
        self.assertFalse(routes_by_key[("/api/auth/register", ("POST",))]["requires_auth"])
        self.assertFalse(
            routes_by_key[("/api/auth/verify-email", ("GET", "POST"))]["requires_auth"]
        )
        self.assertTrue(routes_by_key[("/api/routes", ("GET",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/collections/JeuxVideo/platforms", ("GET",))]["requires_auth"])
        self.assertTrue(routes_by_key[("/collections/JeuxVideo/games", ("POST",))]["requires_auth"])
        self.assertTrue(
            routes_by_key[("/collections/JeuxVideo/wishlist/games", ("POST",))]["requires_auth"]
        )
        self.assertEqual(
            ["Bearer"],
            routes_by_key[("/collections/JeuxVideo/games", ("POST",))]["auth_schemes"],
        )
    def test_cache_reset_route_returns_removed_entries(self):
        """Verifie l'endpoint de reset du cache.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/cache/reset",
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.get_json()["removed_entries"])
    def test_add_game_choices_route_returns_merged_choices(self):
        """Verifie l'endpoint des choix fusionnes du formulaire d'ajout.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get(
            "/collections/JeuxVideo/add-game-choices?platform=Switch",
            headers=self.get_auth_headers(),
        )
        data = response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual(["Switch", "Xbox"], data["platforms"])
    def test_cache_reset_route_requires_authentication(self):
        """Verifie que le reset du cache exige un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post("/collections/JeuxVideo/cache/reset")
        self.assertEqual(403, response.status_code)
        self.assertIn("Bearer", response.get_json()["error"])
    def test_ods_download_route_returns_attachment(self):
        """Verifie l'endpoint de telechargement du fichier ODS.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get(
            "/collections/JeuxVideo/ods/download",
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("attachment", response.headers["Content-Disposition"])
        response.close()
    def test_ods_download_route_requires_authentication(self):
        """Verifie que le telechargement ODS exige un token.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/ods/download")
        self.assertEqual(403, response.status_code)
    def test_add_game_route_returns_created_item(self):
        """Verifie l'endpoint d'ajout d'un jeu.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch", "Nom du jeu": "Metroid"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual("Metroid", response.get_json()["item"]["Nom du jeu"])
    def test_add_game_route_rejects_invalid_token(self):
        """Verifie que l'ajout d'un jeu refuse un token invalide.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch", "Nom du jeu": "Metroid"},
            headers={"Authorization": "Bearer invalid-token"},
        )
        self.assertEqual(401, response.status_code)
        self.assertIn("invalide", response.get_json()["error"])
    def test_add_game_route_returns_validation_error(self):
        """Verifie la propagation des erreurs de validation.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
    def test_delete_wishlist_game_route_returns_deleted_item(self):
        """Verifie l'endpoint de suppression wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.delete(
            "/collections/JeuxVideo/wishlist/games",
            json={"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Switch 2", response.get_json()["item"]["Console"])
    def test_add_wishlist_game_route_returns_created_item(self):
        """Verifie l'endpoint d'ajout wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/wishlist/games",
            json={"Nom du jeu": "Chrono Trigger", "Console": "Switch 2", "Studio": "Square"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual("Switch 2", response.get_json()["item"]["Console"])
    def test_add_wishlist_game_route_returns_validation_error(self):
        """Verifie les erreurs de validation de l'ajout wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.post(
            "/collections/JeuxVideo/wishlist/games",
            json={"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
    def test_delete_game_route_returns_deleted_item(self):
        """Verifie l'endpoint de suppression d'un jeu de plateforme.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.delete(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch", "Nom du jeu": "Metroid"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Metroid", response.get_json()["item"]["Nom du jeu"])
    def test_delete_game_route_returns_validation_error(self):
        """Verifie les erreurs de validation de suppression d'un jeu.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.delete(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
    def test_update_game_route_returns_updated_item(self):
        """Verifie l'endpoint de modification d'un jeu de plateforme.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.put(
            "/collections/JeuxVideo/games",
            json={
                "platform": "Switch",
                "original": {"Nom du jeu": "Metroid"},
                "updated": {"Nom du jeu": "Metroid Prime"},
            },
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Metroid Prime", response.get_json()["item"]["Nom du jeu"])
    def test_update_game_route_returns_validation_error(self):
        """Verifie les erreurs de validation de modification d'un jeu.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.put(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch", "original": {"Nom du jeu": "Metroid"}, "updated": {}},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
    def test_delete_wishlist_game_route_returns_validation_error(self):
        """Verifie les erreurs de validation de suppression wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.delete(
            "/collections/JeuxVideo/wishlist/games",
            json={"Nom du jeu": "Chrono Trigger"},
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
    def test_update_wishlist_game_route_returns_updated_item(self):
        """Verifie l'endpoint de modification wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.put(
            "/collections/JeuxVideo/wishlist/games",
            json={
                "original": {"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"},
                "updated": {"Nom du jeu": "Chrono Trigger", "Console": "Switch 2", "Studio": "Square"},
            },
            headers=self.get_auth_headers(),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Switch 2", response.get_json()["item"]["Console"])
    def test_update_wishlist_game_route_returns_validation_error(self):
        """Verifie les erreurs de validation de modification wishlist.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.put(
            "/collections/JeuxVideo/wishlist/games",
            json={
                "original": {"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"},
                "updated": {"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"},
            },
            headers=self.get_auth_headers(),
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])
if __name__ == "__main__":
    unittest.main()
