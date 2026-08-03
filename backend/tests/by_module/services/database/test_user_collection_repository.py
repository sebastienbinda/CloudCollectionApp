#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-03
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du repository d'associations utilisateur-collection.

import unittest
from decimal import Decimal

from services.database import SqlAlchemyUserCollectionRepository, UserGameAssociation


class FakeRepositoryResult:
    """Resultat SQL factice compatible avec `mappings`."""

    def __init__(self, rows=None, scalar_value=0, rowcount=0):
        """Initialise le resultat factice.

        Args:
            rows (list[dict] | None): Lignes retournees.
            scalar_value (int): Valeur scalaire retournee.
            rowcount (int): Nombre de lignes modifiees.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.rows = rows or []
        self.scalar_value = scalar_value
        self.rowcount = rowcount

    def mappings(self):
        """Retourne les lignes configurees.

        Args:
            Aucun.

        Returns:
            list[dict]: Lignes de resultat.
        """

        return self.rows

    def scalar_one(self):
        """Retourne la valeur scalaire configuree.

        Args:
            Aucun.

        Returns:
            int: Valeur scalaire.
        """

        return self.scalar_value


class FakeRepositoryConnection:
    """Connexion SQL factice capturant les requetes executees."""

    def __init__(self, existing_wishlist_values=None, association_count=0):
        """Initialise la connexion factice.

        Args:
            existing_wishlist_values (dict[int | tuple[int, str], bool] | None): Valeurs
                wishlist existantes.
            association_count (int): Nombre d'associations retourne par COUNT.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.existing_wishlist_values = existing_wishlist_values or {}
        self.association_count = association_count
        self.executed_statements = []

    def execute(self, statement, parameters=None):
        """Capture une requete SQL.

        Args:
            statement (object): Requete SQLAlchemy recue.
            parameters (dict | None): Parametres SQL.

        Returns:
            FakeRepositoryResult: Resultat compatible avec le repository.
        """

        sql = str(statement)
        self.executed_statements.append((sql, parameters or {}))
        if "COUNT(*)" in sql:
            return FakeRepositoryResult(scalar_value=self.association_count)
        if sql.strip().startswith("DELETE"):
            return FakeRepositoryResult(rowcount=self.association_count)
        if sql.strip().startswith("SELECT"):
            return FakeRepositoryResult(
                [
                    {
                        "game_id": key[0] if isinstance(key, tuple) else key,
                        "region": key[1] if isinstance(key, tuple) else "EU-FR",
                        "wishlist": wishlist,
                    }
                    for key, wishlist in sorted(
                        self.existing_wishlist_values.items(),
                        key=lambda item: str(item[0]),
                    )
                ]
            )
        return FakeRepositoryResult()


class UserCollectionRepositoryTest(unittest.TestCase):
    """Valide la persistance des associations utilisateur-jeu."""

    def setUp(self):
        """Prepare le repository teste.

        Args:
            Aucun.

        Returns:
            None: Le repository est initialise.
        """

        self.repository = SqlAlchemyUserCollectionRepository("collection")

    def test_creates_association_with_wishlist_false_by_default(self):
        """Verifie l'insertion par defaut avec wishlist=false."""

        connection = FakeRepositoryConnection()

        count = self.repository.ensure_user_game_associations(connection, 7, [42])

        insert_sql, parameter_batch = connection.executed_statements[1]
        parameters = parameter_batch[0]
        self.assertEqual(1, count)
        self.assertIn("wishlist", insert_sql)
        self.assertEqual(7, parameters["user_id"])
        self.assertEqual(42, parameters["game_id"])
        self.assertEqual("EU-FR", parameters["region"])
        self.assertFalse(parameters["wishlist"])
        self.assertIsNone(parameters["purchase_price"])

    def test_reads_existing_wishlist_values(self):
        """Verifie la lecture des valeurs wishlist existantes."""

        connection = FakeRepositoryConnection(existing_wishlist_values={42: True, 43: False})

        values = self.repository.find_user_game_wishlist_values(connection, 7)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual({(42, "EU-FR"): True, (43, "EU-FR"): False}, values)
        self.assertIn("SELECT game_id, region, wishlist", sql)
        self.assertEqual({"user_id": 7}, parameters)

    def test_creates_association_with_wishlist_true(self):
        """Verifie l'insertion d'un souhait."""

        connection = FakeRepositoryConnection()

        count = self.repository.ensure_user_game_associations(
            connection,
            7,
            [UserGameAssociation(42, True)],
        )

        _, parameter_batch = connection.executed_statements[1]
        parameters = parameter_batch[0]
        self.assertEqual(1, count)
        self.assertEqual(7, parameters["user_id"])
        self.assertEqual(42, parameters["game_id"])
        self.assertTrue(parameters["wishlist"])

    def test_does_not_duplicate_existing_user_game_association(self):
        """Verifie qu'une association existante n'est pas reinseree."""

        connection = FakeRepositoryConnection(existing_wishlist_values={(42, "EU-FR"): False})

        count = self.repository.ensure_user_game_associations(
            connection,
            7,
            [UserGameAssociation(42, True)],
        )

        self.assertEqual(1, count)
        self.assertEqual(2, len(connection.executed_statements))
        self.assertIn("SELECT game_id, region, wishlist", connection.executed_statements[0][0])
        self.assertIn("UPDATE", connection.executed_statements[1][0])

    def test_creates_distinct_association_for_existing_game_with_different_region(self):
        """Verifie qu'une autre region cree un nouvel exemplaire utilisateur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'insertion distincte.
        """

        connection = FakeRepositoryConnection(existing_wishlist_values={(42, "US"): False})

        count = self.repository.ensure_user_game_associations(
            connection,
            7,
            [UserGameAssociation(42, True, region="EU-FR")],
        )

        insert_sql, parameter_batch = connection.executed_statements[1]
        self.assertEqual(1, count)
        self.assertIn("INSERT INTO", insert_sql)
        self.assertEqual("EU-FR", parameter_batch[0]["region"])

    def test_updates_only_non_null_private_information_for_existing_association(self):
        """Verifie l'upsert non destructif des informations privees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident SQL et parametres.
        """

        connection = FakeRepositoryConnection(existing_wishlist_values={(42, "EU-FR"): False})
        association = UserGameAssociation(
            game_id=42,
            purchase_price=Decimal("120.25"),
            price_unit="EUR",
            region="EU-FR",
            has_manual=False,
        )

        self.repository.ensure_user_game_associations(connection, 7, [association])

        sql, parameter_batch = connection.executed_statements[1]
        parameters = parameter_batch[0]
        self.assertIn("purchase_price = COALESCE(:purchase_price, purchase_price)", sql)
        self.assertIn("AND region = :region", sql)
        self.assertEqual(Decimal("120.25"), parameters["purchase_price"])
        self.assertEqual("EUR", parameters["price_unit"])
        self.assertEqual("EU-FR", parameters["region"])
        self.assertFalse(parameters["has_manual"])
        self.assertIsNone(parameters["description"])

    def test_batches_new_and_existing_association_persistence(self):
        """Verifie le regroupement SQL des insertions et mises a jour.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les lots de parametres transmis.
        """

        connection = FakeRepositoryConnection(existing_wishlist_values={(42, "EU-FR"): False})

        count = self.repository.ensure_user_game_associations(
            connection,
            7,
            [
                UserGameAssociation(42, purchase_price=Decimal("5.00")),
                UserGameAssociation(43, True),
                UserGameAssociation(44, False),
            ],
        )

        self.assertEqual(3, count)
        self.assertEqual(3, len(connection.executed_statements))
        insert_sql, insert_batch = connection.executed_statements[1]
        update_sql, update_batch = connection.executed_statements[2]
        self.assertIn("INSERT INTO", insert_sql)
        self.assertEqual([43, 44], [parameters["game_id"] for parameters in insert_batch])
        self.assertIn("UPDATE", update_sql)
        self.assertEqual([42], [parameters["game_id"] for parameters in update_batch])

    def test_limits_insert_and_update_batch_sizes(self):
        """Verifie que les lots SQL respectent la taille maximale configuree.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le decoupage des insertions et mises a jour.
        """

        self.repository.ASSOCIATION_BATCH_SIZE = 2
        connection = FakeRepositoryConnection(
            existing_wishlist_values={
                (42, "EU-FR"): False,
                (43, "EU-FR"): False,
                (44, "EU-FR"): False,
                (45, "EU-FR"): False,
                (46, "EU-FR"): False,
            }
        )

        self.repository.ensure_user_game_associations(
            connection,
            7,
            [
                UserGameAssociation(42),
                UserGameAssociation(43),
                UserGameAssociation(44),
                UserGameAssociation(45),
                UserGameAssociation(46),
                UserGameAssociation(47),
                UserGameAssociation(48),
                UserGameAssociation(49),
                UserGameAssociation(50),
                UserGameAssociation(51),
            ],
        )

        insert_batches = [
            parameters
            for sql, parameters in connection.executed_statements
            if "INSERT INTO" in sql
        ]
        update_batches = [
            parameters
            for sql, parameters in connection.executed_statements
            if "UPDATE" in sql
        ]
        self.assertEqual([[47, 48], [49, 50], [51]], self._game_ids(insert_batches))
        self.assertEqual([[42, 43], [44, 45], [46]], self._game_ids(update_batches))

    def test_counts_user_game_associations(self):
        """Verifie le comptage des associations utilisateur."""

        connection = FakeRepositoryConnection(association_count=3)

        count = self.repository.count_user_game_associations(connection, 7)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(3, count)
        self.assertIn("SELECT COUNT(*)", sql)
        self.assertEqual({"user_id": 7}, parameters)

    def test_deletes_user_game_associations(self):
        """Verifie la suppression des associations utilisateur."""

        connection = FakeRepositoryConnection(association_count=2)

        deleted_count = self.repository.delete_user_game_associations(connection, 7)

        sql, parameters = connection.executed_statements[0]
        self.assertEqual(2, deleted_count)
        self.assertIn("DELETE FROM", sql)
        self.assertEqual({"user_id": 7}, parameters)

    def _game_ids(self, batches):
        """Extrait les identifiants de jeux depuis des lots de parametres.

        Args:
            batches (list[list[dict]]): Lots de parametres SQL captures.

        Returns:
            list[list[int]]: Identifiants de jeux par lot.
        """

        return [
            [parameters["game_id"] for parameters in batch]
            for batch in batches
        ]


if __name__ == "__main__":
    unittest.main()
