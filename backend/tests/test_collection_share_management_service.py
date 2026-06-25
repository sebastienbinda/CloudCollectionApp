#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du service proprietaire de gestion des partages.

from datetime import datetime, timedelta
import unittest

from services.collection import (
    CollectionShareManagementService,
    CollectionShareNotFoundError,
    CollectionShareOwnerNotFoundError,
)
from services.database import DatabaseConfiguration


class FakeShareManagementConnectionContext:
    """Expose une connexion factice transactionnelle."""

    def __init__(self, connection):
        """Initialise le contexte.

        Args:
            connection (object): Connexion exposee.

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
            exc_type (type | None): Type d'erreur.
            exc_value (BaseException | None): Erreur eventuelle.
            traceback (object | None): Trace eventuelle.

        Returns:
            bool: Toujours faux.
        """

        return False


class FakeShareManagementEngine:
    """Simule les connexions et transactions SQLAlchemy."""

    def __init__(self):
        """Initialise le moteur factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = object()
        self.begin_count = 0
        self.connect_count = 0

    def begin(self):
        """Ouvre une transaction factice.

        Args:
            Aucun.

        Returns:
            FakeShareManagementConnectionContext: Contexte transactionnel.
        """

        self.begin_count += 1
        return FakeShareManagementConnectionContext(self.connection)

    def connect(self):
        """Ouvre une connexion de lecture factice.

        Args:
            Aucun.

        Returns:
            FakeShareManagementConnectionContext: Contexte de lecture.
        """

        self.connect_count += 1
        return FakeShareManagementConnectionContext(self.connection)


class FakeShareManagementUserRepository:
    """Resout un proprietaire factice par email."""

    def find_user_id_by_email(self, email):
        """Retourne l'identifiant du proprietaire connu.

        Args:
            email (str): Email normalise.

        Returns:
            int | None: Identifiant 7 ou absence.
        """

        return 7 if email == "user@example.com" else None


class FakeShareLinkSigner:
    """Construit un token de lien deterministe."""

    def create_share_link_token(self, share_id, expires_at):
        """Retourne un token factice sans persistance.

        Args:
            share_id (int): Identifiant du partage.
            expires_at (datetime): Expiration du partage.

        Returns:
            str: Token de test deterministe.
        """

        return f"signed-{share_id}-{expires_at.strftime('%Y%m%d%H%M')}"


class FakeShareManagementRepository:
    """Persiste des partages en memoire pour le service teste."""

    def __init__(self):
        """Initialise le stockage factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.rows = []
        self.next_id = 1

    def create_share(
        self,
        connection,
        owner_user_id,
        created_at,
        expires_at,
        allow_collection,
        allow_wishlist,
        allow_prices,
        recipient=None,
    ):
        """Ajoute un partage factice.

        Args:
            connection (object): Connexion ignoree.
            owner_user_id (int): Proprietaire.
            created_at (datetime): Creation.
            expires_at (datetime): Expiration.
            allow_collection (bool): Permission collection.
            allow_wishlist (bool): Permission wishlist.
            allow_prices (bool): Permission prix.
            recipient (str | None): Destinataire du partage.

        Returns:
            dict: Partage ajoute.
        """

        row = {
            "id": self.next_id,
            "owner_user_id": owner_user_id,
            "created_at": created_at,
            "expires_at": expires_at,
            "revoked_at": None,
            "allow_collection": allow_collection,
            "allow_wishlist": allow_wishlist,
            "allow_prices": allow_prices,
            "recipient": recipient,
        }
        self.next_id += 1
        self.rows.append(row)
        return dict(row)

    def list_shares_by_owner(self, connection, owner_user_id, current_time):
        """Liste les partages du proprietaire avec leur statut.

        Args:
            connection (object): Connexion ignoree.
            owner_user_id (int): Proprietaire filtre.
            current_time (datetime): Date de calcul.

        Returns:
            list[dict]: Partages et statuts.
        """

        results = []
        for row in self.rows:
            if row["owner_user_id"] != owner_user_id:
                continue
            status = "REVOKED" if row["revoked_at"] else (
                "EXPIRED" if row["expires_at"] <= current_time else "ACTIVE"
            )
            results.append({**row, "status": status})
        return results

    def revoke_share(self, connection, share_id, owner_user_id, revoked_at):
        """Revoque un partage factice de facon idempotente.

        Args:
            connection (object): Connexion ignoree.
            share_id (int): Partage cible.
            owner_user_id (int): Proprietaire attendu.
            revoked_at (datetime): Date de revocation.

        Returns:
            dict | None: Partage revoque ou absence.
        """

        for row in self.rows:
            if row["id"] == share_id and row["owner_user_id"] == owner_user_id:
                row["revoked_at"] = row["revoked_at"] or revoked_at
                return dict(row)
        return None


class CollectionShareManagementServiceTest(unittest.TestCase):
    """Valide les regles proprietaire des partages de collection."""

    def setUp(self):
        """Prepare le service et ses dependances factices.

        Args:
            Aucun.

        Returns:
            None: Les fakes sont initialises.
        """

        self.now = datetime(2030, 1, 1, 10, 0, 0)
        self.repository = FakeShareManagementRepository()
        self.engine = FakeShareManagementEngine()
        self.service = CollectionShareManagementService(
            DatabaseConfiguration("postgresql://test", "collection", "0.1"),
            self.repository,
            FakeShareManagementUserRepository(),
            FakeShareLinkSigner(),
            "https://collection.example/",
            engine=self.engine,
            clock=lambda: self.now,
        )

    def test_create_share_accepts_duration_boundaries(self):
        """Verifie les durees minimale et maximale.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident creations et expirations.
        """

        for duration_hours in (1, 240):
            with self.subTest(duration_hours=duration_hours):
                share = self.service.create_share(
                    " USER@Example.COM ",
                    duration_hours,
                    True,
                    False,
                    True,
                    "  Alice  ",
                )
                self.assertEqual("Alice", share["recipient"])
                self.assertEqual(
                    (self.now + timedelta(hours=duration_hours)).isoformat(),
                    share["expires_at"],
                )
                self.assertEqual("ACTIVE", share["status"])
                self.assertTrue(share["link"].startswith(
                    "https://collection.example/collection/share/signed-"
                ))

    def test_create_share_rejects_invalid_durations(self):
        """Verifie le refus des durees hors contrat.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident chaque refus.
        """

        for duration_hours in (0, 241, 1.5, True, "1", None):
            with self.subTest(duration_hours=duration_hours):
                with self.assertRaises(ValueError):
                    self.service.create_share(
                        "user@example.com",
                        duration_hours,
                        True,
                        False,
                        False,
                        None,
                    )

    def test_create_share_requires_explicit_boolean_permissions(self):
        """Verifie la validation stricte des permissions.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident types et acces minimal.
        """

        invalid_permissions = (
            (1, False, False),
            (True, "false", False),
            (True, False, None),
            (False, False, True),
        )
        for permissions in invalid_permissions:
            with self.subTest(permissions=permissions):
                with self.assertRaises(ValueError):
                    self.service.create_share(
                        "user@example.com",
                        24,
                        *permissions,
                    )

    def test_create_share_normalizes_optional_recipient(self):
        """Verifie le nettoyage et la validation du destinataire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les cas optionnels et invalides.
        """

        anonymous_share = self.service.create_share(
            "user@example.com",
            24,
            True,
            False,
            False,
            "   ",
        )
        named_share = self.service.create_share(
            "user@example.com",
            24,
            True,
            False,
            False,
            "Bob",
        )

        self.assertIsNone(anonymous_share["recipient"])
        self.assertEqual("Bob", named_share["recipient"])
        with self.assertRaises(ValueError):
            self.service.create_share(
                "user@example.com",
                24,
                True,
                False,
                False,
                "x" * 257,
            )
        with self.assertRaises(ValueError):
            self.service.create_share(
                "user@example.com",
                24,
                True,
                False,
                False,
                123,
            )

    def test_list_shares_serializes_active_expired_and_revoked_rows(self):
        """Verifie la liste historique et la reconstruction des liens.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les trois statuts.
        """

        active = self.repository.create_share(
            None, 7, self.now, self.now + timedelta(hours=2), True, False, True, "Alice"
        )
        expired = self.repository.create_share(
            None,
            7,
            self.now - timedelta(hours=2),
            self.now - timedelta(hours=1),
            True,
            True,
            False,
            None,
        )
        revoked = self.repository.create_share(
            None, 7, self.now, self.now + timedelta(hours=3), False, True, False, "Bob"
        )
        self.repository.revoke_share(None, revoked["id"], 7, self.now)

        shares = self.service.list_shares("user@example.com")

        self.assertEqual(["ACTIVE", "EXPIRED", "REVOKED"], [row["status"] for row in shares])
        self.assertEqual("Alice", shares[0]["recipient"])
        self.assertIsNone(shares[1]["recipient"])
        self.assertEqual(active["id"], shares[0]["id"])
        self.assertEqual(expired["id"], shares[1]["id"])
        self.assertIn("/collection/share/signed-", shares[2]["link"])

    def test_revoke_share_is_idempotent_and_owner_scoped(self):
        """Verifie la revocation idempotente et l'isolation proprietaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident statut, date et absence.
        """

        row = self.repository.create_share(
            None, 7, self.now, self.now + timedelta(hours=2), True, False, False
        )

        first_result = self.service.revoke_share("user@example.com", row["id"])
        second_result = self.service.revoke_share("user@example.com", row["id"])

        self.assertEqual("REVOKED", first_result["status"])
        self.assertEqual(first_result["revoked_at"], second_result["revoked_at"])
        foreign_row = self.repository.create_share(
            None, 99, self.now, self.now + timedelta(hours=2), True, False, False
        )
        with self.assertRaises(CollectionShareNotFoundError):
            self.service.revoke_share("user@example.com", foreign_row["id"])

    def test_unknown_owner_is_rejected(self):
        """Verifie le refus d'un sujet Bearer sans utilisateur.

        Args:
            Aucun.

        Returns:
            None: L'assertion valide l'erreur proprietaire.
        """

        with self.assertRaises(CollectionShareOwnerNotFoundError):
            self.service.list_shares("unknown@example.com")


if __name__ == "__main__":
    unittest.main()
