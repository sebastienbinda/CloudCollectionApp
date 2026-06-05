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
from pathlib import Path
import app as app_module
class FakeJeuVideoService:
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
        return [{"Nom du jeu": "Mario Kart", "Plateforme": platform, "Query": query}]
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
        self.original_service = app_module.JeuVideoService
        app_module.JeuVideoService = FakeJeuVideoService
        app_module.app.config.update(TESTING=True)
        self.client = app_module.app.test_client()
    def tearDown(self):
        """Restaure le service ODS original.
        Args:
            Aucun.
        Returns:
            None: Les modifications globales du test sont annulees.
        """
        app_module.JeuVideoService = self.original_service
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
    def test_platforms_route_returns_platforms(self):
        """Verifie l'endpoint de liste des plateformes.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la reponse HTTP.
        """
        response = self.client.get("/collections/JeuxVideo/platforms")
        self.assertEqual(200, response.status_code)
        self.assertEqual(["Switch", "Playstation"], response.get_json()["platforms"])
    def test_routes_route_lists_public_and_protected_routes(self):
        """Verifie le catalogue des routes et leurs contraintes d'authentification.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident le contrat de decouverte des routes.
        """
        response = self.client.get("/api/routes")
        routes = response.get_json()["routes"]
        routes_by_key = {
            (route["path"], tuple(route["methods"])): route
            for route in routes
        }
        self.assertEqual(200, response.status_code)
        self.assertFalse(routes_by_key[("/api/routes", ("GET",))]["requires_auth"])
        self.assertFalse(routes_by_key[("/collections/JeuxVideo/platforms", ("GET",))]["requires_auth"])
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
        response = self.client.get("/collections/JeuxVideo/add-game-choices?platform=Switch")
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
        self.assertEqual(401, response.status_code)
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
        self.assertEqual(401, response.status_code)
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
