#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de la route HTTP de retours beta.

import app as app_module

try:
    from tests.support.route_test_support import BaseAppRoutesTest
except ModuleNotFoundError:
    from tests.support.route_test_support import BaseAppRoutesTest


class FakeFeedbackRouteService:
    """Service de retour factice pour les tests HTTP."""

    last_call = None
    next_error = None

    def submit_feedback(self, payload, requester_subject):
        """Memorise l'appel et retourne une issue factice.

        Args:
            payload (dict): Payload recu.
            requester_subject (str): Sujet authentifie.

        Returns:
            dict: Issue factice.

        Raises:
            Exception: Erreur configuree pour le test.
        """

        self.__class__.last_call = (payload, requester_subject)
        if self.next_error:
            raise self.next_error
        return {"issue_number": 7, "issue_url": "https://github.com/acme/app/issues/7"}


class FeedbackRoutesTest(BaseAppRoutesTest):
    """Valide le contrat HTTP d'envoi de retour beta."""

    def setUp(self):
        """Prepare les fakes de route.

        Args:
            Aucun.

        Returns:
            None: Le client Flask est configure.
        """

        super().setUp()
        self.original_feedback_service_factory = app_module.feedback_controller.feedback_service_factory
        app_module.feedback_controller.feedback_service_factory = FakeFeedbackRouteService
        FakeFeedbackRouteService.last_call = None
        FakeFeedbackRouteService.next_error = None

    def tearDown(self):
        """Restaure la fabrique de service.

        Args:
            Aucun.

        Returns:
            None: Les fakes sont retires.
        """

        app_module.feedback_controller.feedback_service_factory = self.original_feedback_service_factory
        super().tearDown()

    def test_submit_feedback_requires_authentication(self):
        """Verifie que la route est protegee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        response = self.client.post("/api/feedback", json={"message": "Retour utilisateur."})

        self.assertEqual(403, response.status_code)

    def test_submit_feedback_creates_issue_for_user(self):
        """Verifie la creation d'un retour avec le sujet connecte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le payload.
        """

        response = self.client.post(
            "/api/feedback",
            json={"category": "idea", "message": "Ajouter un mode sombre serait utile."},
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual(7, response.get_json()["feedback"]["issue_number"])
        self.assertEqual("user@example.com", FakeFeedbackRouteService.last_call[1])

    def test_submit_feedback_returns_400_for_invalid_payload(self):
        """Verifie la conversion des erreurs de validation.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        FakeFeedbackRouteService.next_error = ValueError("Le retour est invalide.")

        response = self.client.post(
            "/api/feedback",
            json={"message": "Court"},
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(400, response.status_code)

    def test_submit_feedback_returns_400_for_non_object_payload(self):
        """Verifie le rejet d'un JSON qui n'est pas un objet.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        response = self.client.post(
            "/api/feedback",
            json=["message invalide"],
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(400, response.status_code)
        self.assertIsNone(FakeFeedbackRouteService.last_call)

    def test_submit_feedback_returns_503_when_github_is_unavailable(self):
        """Verifie la conversion des erreurs GitHub.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le statut.
        """

        FakeFeedbackRouteService.next_error = RuntimeError("GitHub indisponible.")

        response = self.client.post(
            "/api/feedback",
            json={"message": "Le formulaire fonctionne mal sur mobile."},
            headers=self.get_user_auth_headers(),
        )

        self.assertEqual(503, response.status_code)


if __name__ == "__main__":
    unittest.main()
