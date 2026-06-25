#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du modele et du repository de partage de collection.

from datetime import datetime
import unittest

from services.database import CollectionShare, SqlAlchemyCollectionShareRepository


class FakeCollectionShareResult:
    """Simule un resultat SQLAlchemy de partage de collection."""

    def __init__(self, rows=None):
        """Initialise le resultat factice.

        Args:
            rows (list[dict] | None): Lignes retournees par la requete.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.rows = rows or []

    def mappings(self):
        """Retourne le resultat compatible avec les mappings SQLAlchemy.

        Args:
            Aucun.

        Returns:
            FakeCollectionShareResult: Resultat courant.
        """

        return self

    def one(self):
        """Retourne l'unique ligne configuree.

        Args:
            Aucun.

        Returns:
            dict: Premiere ligne configuree.

        Raises:
            IndexError: Si aucune ligne n'est configuree.
        """

        return self.rows[0]

    def first(self):
        """Retourne la premiere ligne ou aucune valeur.

        Args:
            Aucun.

        Returns:
            dict | None: Premiere ligne ou absence.
        """

        return self.rows[0] if self.rows else None

    def all(self):
        """Retourne toutes les lignes configurees.

        Args:
            Aucun.

        Returns:
            list[dict]: Lignes configurees.
        """

        return self.rows


class FakeCollectionShareConnection:
    """Capture les requetes du repository de partage."""

    def __init__(self, result_rows=None):
        """Initialise la connexion factice.

        Args:
            result_rows (list[dict] | None): Lignes du prochain resultat.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.result_rows = result_rows or []
        self.executed_statements = []

    def execute(self, statement, parameters=None):
        """Capture une requete SQL.

        Args:
            statement (object): Requete SQLAlchemy recue.
            parameters (dict | None): Parametres de requete.

        Returns:
            FakeCollectionShareResult: Resultat configure.
        """

        self.executed_statements.append((str(statement), parameters or {}))
        return FakeCollectionShareResult(self.result_rows)


class CollectionShareRepositoryTest(unittest.TestCase):
    """Valide le modele et la persistance des partages de collection."""

    def setUp(self):
        """Prepare le repository teste.

        Args:
            Aucun.

        Returns:
            None: La methode initialise les dates et le repository.
        """

        self.repository = SqlAlchemyCollectionShareRepository("collection")
        self.created_at = datetime(2026, 6, 23, 10, 0, 0)
        self.expires_at = datetime(2026, 6, 24, 10, 0, 0)

    def test_model_declares_expected_columns_constraints_and_index(self):
        """Verifie le contrat ORM sans stockage de token brut.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les metadonnees SQLAlchemy.
        """

        table = CollectionShare.__table__
        column_names = set(table.columns.keys())
        index_names = {index.name for index in table.indexes}
        constraint_names = {constraint.name for constraint in table.constraints}

        self.assertEqual(
            {
                "id",
                "owner_user_id",
                "created_at",
                "expires_at",
                "revoked_at",
                "recipient",
                "allow_collection",
                "allow_wishlist",
                "allow_prices",
            },
            column_names,
        )
        self.assertNotIn("token", column_names)
        self.assertIn("ix_t_collection_share_owner_user_id", index_names)
        self.assertIn("ck_t_collection_share_expiration", constraint_names)
        owner_foreign_key = next(iter(table.c.owner_user_id.foreign_keys))
        self.assertEqual("CASCADE", owner_foreign_key.ondelete)

    def test_create_share_inserts_permissions_without_raw_token(self):
        """Verifie l'insertion d'un partage sans secret persiste.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident SQL, parametres et resultat.
        """

        expected_row = self._share_row(share_id=5)
        connection = FakeCollectionShareConnection([expected_row])

        created_share = self.repository.create_share(
            connection,
            owner_user_id=12,
            created_at=self.created_at,
            expires_at=self.expires_at,
            allow_collection=True,
            allow_wishlist=False,
            allow_prices=True,
            recipient="Famille",
        )

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(expected_row, created_share)
        self.assertIn("INSERT INTO", sql)
        self.assertIn("t_collection_share", sql)
        self.assertNotIn("token", sql.lower())
        self.assertNotIn("token", parameters)
        self.assertEqual("Famille", parameters["recipient"])
        self.assertEqual(12, parameters["owner_user_id"])
        self.assertTrue(parameters["allow_collection"])
        self.assertFalse(parameters["allow_wishlist"])
        self.assertTrue(parameters["allow_prices"])

    def test_find_share_calculates_status_from_dates(self):
        """Verifie la recherche par identifiant et le calcul du statut.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le SQL de statut.
        """

        row = {**self._share_row(share_id=5), "status": "EXPIRED"}
        connection = FakeCollectionShareConnection([row])

        found_share = self.repository.find_share(connection, 5, self.expires_at)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(row, found_share)
        self.assertIn("WHERE id = :share_id", sql)
        self.assertIn("revoked_at IS NOT NULL THEN 'REVOKED'", sql)
        self.assertIn("expires_at <= :current_time THEN 'EXPIRED'", sql)
        self.assertEqual({"share_id": 5, "current_time": self.expires_at}, parameters)

    def test_list_shares_is_isolated_by_owner_and_keeps_all_statuses(self):
        """Verifie la liste historique limitee au proprietaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident filtre, ordre et statuts.
        """

        rows = [
            {**self._share_row(share_id=7), "status": "ACTIVE"},
            {**self._share_row(share_id=6), "status": "EXPIRED"},
            {**self._share_row(share_id=5), "status": "REVOKED"},
        ]
        connection = FakeCollectionShareConnection(rows)

        shares = self.repository.list_shares_by_owner(connection, 12, self.created_at)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(rows, shares)
        self.assertIn("WHERE owner_user_id = :owner_user_id", sql)
        self.assertNotIn("DELETE", sql)
        self.assertIn("ORDER BY created_at DESC, id DESC", sql)
        self.assertEqual({"owner_user_id": 12, "current_time": self.created_at}, parameters)

    def test_find_share_with_owner_reads_current_identity_and_status(self):
        """Verifie la lecture jointe necessaire a la validation GUEST.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la jointure utilisateur.
        """

        row = {
            **self._share_row(share_id=5),
            "status": "ACTIVE",
            "owner_pseudonym": "Player_One",
            "owner_status": "ACTIVE",
        }
        connection = FakeCollectionShareConnection([row])

        found_share = self.repository.find_share_with_owner(
            connection,
            5,
            self.created_at,
        )

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(row, found_share)
        self.assertIn("JOIN \"collection\".t_user app_user", sql)
        self.assertIn("app_user.pseudonym AS owner_pseudonym", sql)
        self.assertIn("app_user.status AS owner_status", sql)
        self.assertEqual({"share_id": 5, "current_time": self.created_at}, parameters)

    def test_revoke_share_is_idempotent_and_owner_scoped(self):
        """Verifie la revocation idempotente reservee au proprietaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le SQL et son isolation.
        """

        revoked_at = datetime(2026, 6, 23, 11, 0, 0)
        row = {**self._share_row(share_id=5), "revoked_at": revoked_at}
        connection = FakeCollectionShareConnection([row])

        revoked_share = self.repository.revoke_share(connection, 5, 12, revoked_at)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(row, revoked_share)
        self.assertIn("SET revoked_at = COALESCE(revoked_at, :revoked_at)", sql)
        self.assertIn("id = :share_id AND owner_user_id = :owner_user_id", sql)
        self.assertEqual(5, parameters["share_id"])
        self.assertEqual(12, parameters["owner_user_id"])

    def test_revoke_share_returns_none_for_another_owner(self):
        """Verifie l'absence de resultat pour un proprietaire different.

        Args:
            Aucun.

        Returns:
            None: L'assertion valide l'isolation du partage.
        """

        connection = FakeCollectionShareConnection()

        revoked_share = self.repository.revoke_share(
            connection,
            share_id=5,
            owner_user_id=99,
            revoked_at=self.created_at,
        )

        self.assertIsNone(revoked_share)

    def _share_row(self, share_id):
        return {
            "id": share_id,
            "owner_user_id": 12,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "revoked_at": None,
            "recipient": "Famille",
            "allow_collection": True,
            "allow_wishlist": False,
            "allow_prices": True,
        }


if __name__ == "__main__":
    unittest.main()
