#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-12
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#

import os
import unittest
from unittest.mock import patch

from services.database import DatabaseConfiguration, DatabaseModelBase


class DatabaseConfigurationTest(unittest.TestCase):
    def test_database_models_expose_initial_schema_tables(self):
        """Verifie que les modeles ORM couvrent le schema initial.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les tables ORM declarees.
        """

        self.assertEqual(
            {
                "t_schema_version",
                "t_platform",
                "t_platform_alias",
                "t_platform_image",
                "t_studio",
                "t_user",
                "t_game",
                "t_user_collection",
                "t_collection_share",
            },
            set(DatabaseModelBase.metadata.tables.keys()),
        )

    def test_user_collection_model_exposes_wishlist_column(self):
        """Verifie que le modele ORM expose la colonne wishlist.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la colonne et son defaut.
        """

        table = DatabaseModelBase.metadata.tables["t_user_collection"]

        self.assertIn("wishlist", table.columns)
        self.assertFalse(table.columns["wishlist"].nullable)
        self.assertEqual("false", str(table.columns["wishlist"].server_default.arg))

    def test_collection_share_model_exposes_recipient_column(self):
        """Verifie que le modele ORM expose le destinataire optionnel.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la colonne et sa taille.
        """

        table = DatabaseModelBase.metadata.tables["t_collection_share"]

        self.assertIn("recipient", table.columns)
        self.assertTrue(table.columns["recipient"].nullable)
        self.assertEqual(256, table.columns["recipient"].type.length)

    def test_platform_image_model_exposes_user_and_validation_columns(self):
        """Verifie que le modele ORM expose le schema des images plateformes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les colonnes et contraintes.
        """

        table = DatabaseModelBase.metadata.tables["t_platform_image"]

        self.assertIn("user_id", table.columns)
        self.assertFalse(table.columns["user_id"].nullable)
        self.assertFalse(table.columns["platform"].nullable)
        self.assertFalse(table.columns["path"].nullable)
        self.assertFalse(table.columns["type"].nullable)
        self.assertFalse(table.columns["status"].nullable)
        self.assertFalse(table.columns["file_size_bytes"].nullable)
        self.assertFalse(table.columns["creation_date"].nullable)
        self.assertIsNone(table.columns["file_size_bytes"].server_default)
        self.assertIn(
            "ck_t_platform_image_file_size_bytes",
            {constraint.name for constraint in table.constraints},
        )
        self.assertIn("ix_t_platform_image_user_id", {index.name for index in table.indexes})
        self.assertIn(
            "uq_t_platform_image_single_main",
            {index.name for index in table.indexes if index.unique},
        )

    def test_from_environment_reads_database_settings(self):
        """Verifie la lecture des variables d'environnement SQL.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la configuration construite.
        """

        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:password@database:5432/app",
                "DB_SCHEMA_NAME": "collection_schema",
                "APP_VERSION": "1.2",
            },
            clear=True,
        ):
            configuration = DatabaseConfiguration.from_environment()

        self.assertEqual(
            "postgresql+psycopg://user:password@database:5432/app",
            configuration.database_url,
        )
        self.assertEqual("collection_schema", configuration.schema_name)
        self.assertEqual("1.2", configuration.application_version)

    def test_validate_rejects_unsafe_schema_name(self):
        """Verifie le refus des noms de schema non surs.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur attendue.
        """

        configuration = DatabaseConfiguration(
            database_url="postgresql://database/app",
            schema_name="public;drop",
            application_version="1.0",
        )

        with self.assertRaises(ValueError):
            configuration.validate()

    def test_validate_rejects_long_application_version(self):
        """Verifie la contrainte de taille de `t_schema_version.version`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur attendue.
        """

        configuration = DatabaseConfiguration(
            database_url="postgresql://database/app",
            schema_name="collection",
            application_version="2026.05",
        )

        with self.assertRaises(ValueError):
            configuration.validate()


if __name__ == "__main__":
    unittest.main()
