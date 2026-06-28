#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du service d'authentification des invites de partage.

from datetime import datetime, timedelta, timezone
import unittest

from services.auth import (
    AuthTokenService,
    CollectionShareGuestAuthenticationService,
    CollectionShareUnavailableError,
    UserProfile,
)
from services.database import DatabaseConfiguration


class FakeGuestAuthenticationConnectionContext:
    """Expose une connexion factice dans un contexte."""

    def __init__(self, connection):
        """Initialise le contexte factice.

        Args:
            connection (object): Connexion retournee.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection

    def __enter__(self):
        """Retourne la connexion configuree.

        Args:
            Aucun.

        Returns:
            object: Connexion factice.
        """

        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        """Ferme le contexte sans masquer les erreurs.

        Args:
            exc_type (type | None): Type d'erreur eventuel.
            exc_value (BaseException | None): Erreur eventuelle.
            traceback (object | None): Trace eventuelle.

        Returns:
            bool: Toujours faux.
        """

        return False


class FakeGuestAuthenticationEngine:
    """Simule un moteur SQLAlchemy injectable."""

    def __init__(self):
        """Initialise la connexion factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = object()

    def connect(self):
        """Ouvre un contexte de connexion factice.

        Args:
            Aucun.

        Returns:
            FakeGuestAuthenticationConnectionContext: Contexte factice.
        """

        return FakeGuestAuthenticationConnectionContext(self.connection)


class FakeGuestAuthenticationRepository:
    """Retourne un partage configurable au service GUEST."""

    def __init__(self, share):
        """Initialise le repository factice.

        Args:
            share (dict | None): Partage retourne par les lectures.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.share = share
        self.calls = []

    def find_share_with_owner(self, connection, share_id, current_time):
        """Retourne le partage configure.

        Args:
            connection (object): Connexion recue.
            share_id (int): Identifiant recherche.
            current_time (datetime): Date de validation.

        Returns:
            dict | None: Partage configure ou absence.
        """

        self.calls.append((connection, share_id, current_time))
        return self.share


class CollectionShareGuestAuthenticationServiceTest(unittest.TestCase):
    """Valide l'echange et la revocation des sessions GUEST."""

    def setUp(self):
        """Prepare un partage actif et une horloge deterministe.

        Args:
            Aucun.

        Returns:
            None: Les dependances sont initialisees.
        """

        self.now = datetime(2030, 1, 1, 10, 0, 0)
        self.expires_at = self.now + timedelta(hours=12)
        self.share = {
            "id": 8,
            "owner_user_id": 7,
            "created_at": self.now - timedelta(hours=1),
            "expires_at": self.expires_at,
            "revoked_at": None,
            "allow_collection": True,
            "allow_wishlist": False,
            "allow_prices": True,
            "wishlist_buy_status_default_filter": "yes",
            "recipient": "Alice",
            "status": "ACTIVE",
            "owner_pseudonym": "Player_One",
            "owner_status": "ACTIVE",
        }
        self.token_service = AuthTokenService(
            username="admin",
            password="secret",
            secret_key="guest-test-secret",
        )
        self.repository = FakeGuestAuthenticationRepository(self.share)
        self.service = CollectionShareGuestAuthenticationService(
            DatabaseConfiguration("postgresql://test", "collection", "0.1"),
            self.token_service,
            self.repository,
            engine=FakeGuestAuthenticationEngine(),
            clock=lambda: self.now,
        )

    def test_exchange_returns_guest_session_with_current_owner_and_permissions(self):
        """Verifie l'echange complet d'un lien actif.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la session GUEST.
        """

        link_token = self.service.create_share_link_token(8, self.expires_at)

        response = self.service.exchange_share_link_token(link_token)
        payload = self.token_service.validate_access_token(response["access_token"])

        self.assertEqual("Bearer", response["token_type"])
        self.assertEqual(12 * 3600, response["expires_in"])
        self.assertEqual(UserProfile.GUEST.value, payload["profile"])
        self.assertEqual(8, payload["collection_share_id"])
        self.assertEqual(7, payload["owner_user_id"])
        self.assertEqual("Player_One", payload["owner_pseudonym"])
        self.assertEqual(
            {"collection": True, "wishlist": False, "prices": True},
            payload["permissions"],
        )
        self.assertEqual("yes", payload["wishlist_buy_status_default_filter"])
        expected_expiration = int(self.expires_at.replace(tzinfo=timezone.utc).timestamp())
        self.assertEqual(expected_expiration, payload["exp"])

    def test_exchange_logs_recipient_for_guest_access(self):
        """Verifie le journal de l'acces invite avec le destinataire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le contenu du log.
        """

        link_token = self.service.create_share_link_token(8, self.expires_at)

        with self.assertLogs("services.auth.collection_share_guest_authentication_service", level="INFO") as logs:
            self.service.exchange_share_link_token(link_token)

        self.assertIn("share_id=8", logs.output[0])
        self.assertIn("owner_user_id=7", logs.output[0])
        self.assertIn("recipient=Alice", logs.output[0])

    def test_link_token_is_not_accepted_as_bearer(self):
        """Verifie la separation entre lien et session Bearer.

        Args:
            Aucun.

        Returns:
            None: L'assertion valide le refus du lien comme session.
        """

        link_token = self.service.create_share_link_token(8, self.expires_at)

        with self.assertRaises(ValueError):
            self.token_service.validate_access_token(link_token)

    def test_exchange_rejects_falsified_or_unknown_link(self):
        """Verifie le refus des liens non signes ou sans partage.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les refus.
        """

        with self.assertRaises(ValueError):
            self.service.exchange_share_link_token("invalid-token")

        self.repository.share = None
        link_token = self.service.create_share_link_token(99, self.expires_at)
        with self.assertRaises(CollectionShareUnavailableError):
            self.service.exchange_share_link_token(link_token)

    def test_exchange_returns_unavailable_for_expired_or_revoked_share(self):
        """Verifie les invalidations temporelle et explicite.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur metier.
        """

        expired_link = self.service.create_share_link_token(8, self.now)
        with self.assertRaises(CollectionShareUnavailableError):
            self.service.exchange_share_link_token(expired_link)

        self.repository.share = {**self.share, "status": "REVOKED"}
        active_link = self.service.create_share_link_token(8, self.expires_at)
        with self.assertRaises(CollectionShareUnavailableError):
            self.service.exchange_share_link_token(active_link)

    def test_exchange_returns_unavailable_for_locked_owner(self):
        """Verifie l'invalidation par verrouillage du proprietaire.

        Args:
            Aucun.

        Returns:
            None: L'assertion valide l'erreur metier.
        """

        self.repository.share = {**self.share, "owner_status": "LOCKED"}
        link_token = self.service.create_share_link_token(8, self.expires_at)

        with self.assertRaises(CollectionShareUnavailableError):
            self.service.exchange_share_link_token(link_token)

    def test_validate_guest_session_checks_database_on_every_call(self):
        """Verifie la relecture du partage pour chaque validation.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la revocabilite serveur.
        """

        link_token = self.service.create_share_link_token(8, self.expires_at)
        response = self.service.exchange_share_link_token(link_token)
        payload = self.token_service.validate_access_token(response["access_token"])
        initial_call_count = len(self.repository.calls)

        self.service.validate_guest_session(payload)

        self.assertEqual(initial_call_count + 1, len(self.repository.calls))
        self.repository.share = {**self.share, "status": "REVOKED"}
        with self.assertRaises(CollectionShareUnavailableError):
            self.service.validate_guest_session(payload)


if __name__ == "__main__":
    unittest.main()
